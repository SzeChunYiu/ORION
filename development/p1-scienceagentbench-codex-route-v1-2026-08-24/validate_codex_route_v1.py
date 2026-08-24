#!/usr/bin/env python3
"""Static and synthetic validation for the blocked Codex CLI SAB route."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import codex_route_adapter_v1 as adapter  # noqa: E402


def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def digest(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def jsonl(
    *,
    thread_id: str = "synthetic-thread-1",
    item_text: str = '{"kind":"FINAL_PROGRAM","program":"print(4.0)"}',
    usage: dict | None = None,
    extra_items: list[dict] | None = None,
) -> bytes:
    if usage is None:
        usage = {
            "input_tokens": 100,
            "cached_input_tokens": 0,
            "cache_write_input_tokens": 0,
            "output_tokens": 20,
            "reasoning_output_tokens": 0,
        }
    rows = [
        {"type": "thread.started", "thread_id": thread_id},
        {"type": "turn.started"},
    ]
    rows.extend(extra_items or [])
    rows.extend(
        [
            {
                "type": "item.completed",
                "item": {"id": "item-final", "type": "agent_message", "text": item_text},
            },
            {"type": "turn.completed", "usage": usage},
        ]
    )
    return ("\n".join(json.dumps(row, separators=(",", ":")) for row in rows) + "\n").encode()


class AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = load("PROMPT_BUNDLE_V1.json")
        self.fixture = load("SYNTHETIC_FIXTURE_V1.json")
        self.caps = load("RUN_PLAN_CANDIDATE_V1.json")[
            "matched_acceptance_budget_by_arm"
        ]["RR"]

    def assert_contract_error(self, action, contains: str) -> None:
        with self.assertRaises(adapter.ContractError) as raised:
            action()
        self.assertIn(contains, str(raised.exception))

    def test_all_templates_render_without_unreplaced_markers(self) -> None:
        state_hash = "a" * 64
        for name in self.bundle["templates"]:
            with self.subTest(name=name):
                rendered = adapter.render_template(
                    self.bundle,
                    name,
                    self.fixture,
                    attempt_ordinal=1,
                    phase0_state_sha256=state_hash,
                )
                self.assertTrue(rendered.endswith(b"\n"))
                self.assertNotIn(b"{{", rendered)
                self.assertNotIn(b"}}", rendered)

    def test_renderer_rejects_bad_attempt_and_missing_state_hash(self) -> None:
        self.assert_contract_error(
            lambda: adapter.render_template(
                self.bundle, "OS_PHASE1", self.fixture, attempt_ordinal=0
            ),
            "attempt ordinal",
        )
        self.assert_contract_error(
            lambda: adapter.render_template(
                self.bundle, "RR_PHASE1", self.fixture, attempt_ordinal=1
            ),
            "phase-0 state",
        )

    def test_renderer_rejects_official_or_outcome_fixture_fields(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["official_task_content"] = True
        self.assert_contract_error(
            lambda: adapter.render_template(
                self.bundle, "OS_PHASE1", fixture, attempt_ordinal=1
            ),
            "synthetic",
        )
        fixture = copy.deepcopy(self.fixture)
        fixture["recovered_packet"]["evaluator_feedback"] = "forbidden"
        self.assert_contract_error(
            lambda: adapter.render_template(
                self.bundle, "OS_PHASE1", fixture, attempt_ordinal=1
            ),
            "forbidden",
        )

    def test_parse_jsonl_preserves_usage_hashes_and_null_cost(self) -> None:
        raw = jsonl()
        receipt = adapter.parse_jsonl(
            raw,
            phase="OS_PHASE1",
            schema=self.bundle["output_schemas"]["final_program"],
            wall_time_seconds=1.5,
            caps=self.caps,
        )
        self.assertEqual(receipt["input_tokens"], 100)
        self.assertEqual(receipt["output_tokens"], 20)
        self.assertEqual(receipt["tool_calls"], 0)
        self.assertIsNone(receipt["billed_cost_usd"])
        self.assertEqual(receipt["billed_cost_status"], "CANNOT_CHECK_NOT_EMITTED")
        self.assertEqual(receipt["raw_jsonl_sha256"], hashlib.sha256(raw).hexdigest())

    def test_parse_jsonl_rejects_failure_missing_or_duplicate_terminal(self) -> None:
        failure = (
            json.dumps({"type": "thread.started", "thread_id": "x"})
            + "\n"
            + json.dumps({"type": "turn.failed", "error": {"message": "x"}})
            + "\n"
        ).encode()
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                failure,
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=1.0,
                caps=self.caps,
            ),
            "failed",
        )
        rows = jsonl().decode().splitlines()
        duplicate = ("\n".join(rows + [rows[-1]]) + "\n").encode()
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                duplicate,
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=1.0,
                caps=self.caps,
            ),
            "terminal usage",
        )

    def test_parse_jsonl_rejects_error_item_and_unknown_item_type(self) -> None:
        for item_type in ("error", "mystery"):
            raw = jsonl(
                extra_items=[
                    {
                        "type": "item.completed",
                        "item": {"id": "extra", "type": item_type, "message": "x"},
                    }
                ]
            )
            with self.subTest(item_type=item_type):
                self.assert_contract_error(
                    lambda raw=raw: adapter.parse_jsonl(
                        raw,
                        phase="OS_PHASE1",
                        schema=self.bundle["output_schemas"]["final_program"],
                        wall_time_seconds=1.0,
                        caps=self.caps,
                    ),
                    "item type",
                )

    def test_parse_jsonl_counts_tools_and_applies_caps(self) -> None:
        raw = jsonl(
            extra_items=[
                {
                    "type": "item.completed",
                    "item": {"id": "tool", "type": "command_execution", "status": "completed"},
                }
            ]
        )
        receipt = adapter.parse_jsonl(
            raw,
            phase="OS_PHASE1",
            schema=self.bundle["output_schemas"]["final_program"],
            wall_time_seconds=1.0,
            caps=self.caps,
        )
        self.assertEqual(receipt["tool_calls"], 1)
        caps = dict(self.caps)
        caps["tool_call_cap"] = 0
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                raw,
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=1.0,
                caps=caps,
            ),
            "tool_call_cap",
        )

    def test_parse_jsonl_rejects_failed_tool_item(self) -> None:
        raw = jsonl(
            extra_items=[
                {
                    "type": "item.completed",
                    "item": {
                        "id": "tool-failed",
                        "type": "command_execution",
                        "status": "failed",
                    },
                }
            ]
        )
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                raw,
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=1.0,
                caps=self.caps,
            ),
            "tool item failed",
        )

    def test_parse_jsonl_rejects_bad_usage_time_schema_and_invented_cost(self) -> None:
        for field, value in (
            ("input_tokens", -1),
            ("output_tokens", "20"),
            ("cached_input_tokens", True),
        ):
            usage = {
                "input_tokens": 100,
                "cached_input_tokens": 0,
                "cache_write_input_tokens": 0,
                "output_tokens": 20,
                "reasoning_output_tokens": 0,
            }
            usage[field] = value
            with self.subTest(field=field):
                self.assert_contract_error(
                    lambda usage=usage: adapter.parse_jsonl(
                        jsonl(usage=usage),
                        phase="OS_PHASE1",
                        schema=self.bundle["output_schemas"]["final_program"],
                        wall_time_seconds=1.0,
                        caps=self.caps,
                    ),
                    field,
                )
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                jsonl(),
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=math.inf,
                caps=self.caps,
            ),
            "wall_time",
        )
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                jsonl(item_text='{"kind":"WRONG","program":"x"}'),
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=1.0,
                caps=self.caps,
            ),
            "schema",
        )
        self.assert_contract_error(
            lambda: adapter.parse_jsonl(
                jsonl(),
                phase="OS_PHASE1",
                schema=self.bundle["output_schemas"]["final_program"],
                wall_time_seconds=1.0,
                caps=self.caps,
                billed_cost_usd=0.0,
            ),
            "billed cost",
        )

    def test_aggregate_enforces_rr_os_nr_thread_semantics(self) -> None:
        final_schema = self.bundle["output_schemas"]["final_program"]
        state_schema = self.bundle["output_schemas"]["phase0_state"]
        rr0 = adapter.parse_jsonl(
            jsonl(
                thread_id="rr",
                item_text=json.dumps(
                    {
                        "kind": "RR_TYPED_STATE",
                        "assumptions": [],
                        "unresolved_inputs": [],
                        "intended_analysis": [],
                        "invariants": [],
                        "output_contract": "json",
                    }
                ),
            ),
            phase="RR_PHASE0",
            schema=state_schema,
            wall_time_seconds=1.0,
            caps=self.caps,
        )
        rr1 = adapter.parse_jsonl(
            jsonl(thread_id="rr"),
            phase="RR_PHASE1",
            schema=final_schema,
            wall_time_seconds=1.0,
            caps=self.caps,
        )
        receipt = adapter.aggregate_arm_attempt("RR", 1, [rr0, rr1], self.caps)
        self.assertEqual(receipt["transport_status"], "PASS")
        self.assertEqual(receipt["runner_status"], "CANNOT_CHECK_BILLED_COST")
        self.assertEqual(receipt["final_candidates"], 1)
        self.assertEqual(receipt["local_execution_seconds"], 0.0)
        self.assertEqual(
            receipt["local_execution_status"],
            "NOT_RUN_SYNTHETIC_GENERATION_TRANSPORT_ONLY",
        )
        bad = copy.deepcopy(rr1)
        bad["thread_id"] = "other"
        self.assert_contract_error(
            lambda: adapter.aggregate_arm_attempt("RR", 1, [rr0, bad], self.caps),
            "same thread",
        )
        self.assert_contract_error(
            lambda: adapter.aggregate_arm_attempt("OS", 1, [rr0, rr1], self.caps),
            "OS",
        )
        nr0 = copy.deepcopy(rr0)
        nr0["phase"] = "NR_PHASE0"
        nr0["output_kind"] = "NR_GENERIC_PLAN"
        nr1 = copy.deepcopy(rr1)
        nr1["phase"] = "NR_PHASE1"
        nr1["thread_id"] = "nr-fresh"
        adapter.aggregate_arm_attempt("NR", 1, [nr0, nr1], self.caps)
        nr1["thread_id"] = nr0["thread_id"]
        self.assert_contract_error(
            lambda: adapter.aggregate_arm_attempt("NR", 1, [nr0, nr1], self.caps),
            "distinct",
        )

    def test_run_plan_remains_blocked_and_budgets_match(self) -> None:
        plan = load("RUN_PLAN_CANDIDATE_V1.json")
        adapter.validate_run_plan_candidate(plan)
        bad = copy.deepcopy(plan)
        bad["runner_admissible"] = True
        self.assert_contract_error(
            lambda: adapter.validate_run_plan_candidate(bad), "runner_admissible"
        )
        bad = copy.deepcopy(plan)
        bad["matched_acceptance_budget_by_arm"]["NR"]["tool_call_cap"] += 1
        self.assert_contract_error(
            lambda: adapter.validate_run_plan_candidate(bad), "matched"
        )
        bad = copy.deepcopy(plan)
        for caps in bad["matched_acceptance_budget_by_arm"].values():
            caps["final_candidates_per_attempt"] = 2
        self.assert_contract_error(
            lambda: adapter.validate_run_plan_candidate(bad), "one final candidate"
        )

    def test_exact_clean_codex_argv_has_no_seed_or_dangerous_flags(self) -> None:
        argv = adapter.build_phase_argv(
            phase="OS_PHASE1",
            codex_home=Path("/external/clean-codex-home"),
            cwd=Path("/external/synthetic-task"),
            prompt_path=Path("/external/prompts/os.txt"),
            schema_path=Path("/external/schemas/final.json"),
            last_message_path=Path("/external/raw/os-last.json"),
        )
        joined = " ".join(argv)
        self.assertIn("--ignore-user-config", argv)
        self.assertIn("--strict-config", argv)
        self.assertIn("read-only", argv)
        self.assertIn('model_provider="openai"', argv)
        for feature in ("plugins", "remote_plugin", "skill_search"):
            with self.subTest(disabled_feature=feature):
                self.assertIn(feature, argv)
                self.assertEqual(argv[argv.index(feature) - 1], "--disable")
        self.assertNotIn("seed", joined.lower())
        self.assertNotIn("dangerously", joined.lower())

    def test_module_has_no_network_library_or_credential_reader(self) -> None:
        source = (ROOT / "codex_route_adapter_v1.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported & {"requests", "urllib", "httpx", "socket"})
        lowered = source.lower()
        self.assertNotIn("auth.json", lowered)
        self.assertNotIn("api_key", lowered)


def validate_committed_artifacts() -> None:
    preflight = load("CODEX_ROUTE_PREFLIGHT_V1.json")
    prompts = load("PROMPT_BUNDLE_V1.json")
    plan = load("RUN_PLAN_CANDIDATE_V1.json")
    receipt = load("SYNTHETIC_ARM_RECEIPTS_V1.json")
    adapter.validate_prompt_bundle(prompts)
    adapter.validate_run_plan_candidate(plan)
    assert plan["prompt_bundle"]["sha256"] == digest("PROMPT_BUNDLE_V1.json")
    assert preflight["prompt_bundle_sha256"] == digest("PROMPT_BUNDLE_V1.json")
    assert receipt["prompt_bundle_sha256"] == digest("PROMPT_BUNDLE_V1.json")
    assert receipt["fixture_sha256"] == digest("SYNTHETIC_FIXTURE_V1.json")
    descriptor_bytes = (
        json.dumps(
            preflight["credential_route_descriptor"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")
    descriptor_hash = hashlib.sha256(descriptor_bytes).hexdigest()
    assert preflight["credential_route_descriptor_bytes"] == len(descriptor_bytes)
    assert preflight["credential_route_descriptor_sha256"] == descriptor_hash
    assert plan["client_route"]["credential_route_descriptor_sha256"] == descriptor_hash
    assert plan["client_route"]["optional_context_features_disabled"] == [
        "plugins",
        "remote_plugin",
        "skill_search",
    ]
    assert preflight["execution_route"]["optional_context_features_disabled"] == [
        "plugins",
        "remote_plugin",
        "skill_search",
    ]
    assert [row["arm_id"] for row in receipt["arm_attempt_receipts"]] == [
        "RR",
        "OS",
        "NR",
    ]
    assert all(row["attempt"] == 1 for row in receipt["arm_attempt_receipts"])
    assert all(row["transport_status"] == "PASS" for row in receipt["arm_attempt_receipts"])
    assert all(
        row["runner_status"] == "CANNOT_CHECK_BILLED_COST"
        for row in receipt["arm_attempt_receipts"]
    )
    assert [len(row["phase_receipts"]) for row in receipt["arm_attempt_receipts"]] == [
        2,
        1,
        2,
    ]
    thread_hashes = []
    for row in receipt["arm_attempt_receipts"]:
        phases = row["phase_receipts"]
        assert row["billed_cost_usd"] is None
        assert row["tool_calls"] == 0
        assert row["final_candidates"] == 1
        assert row["local_execution_seconds"] == 0.0
        assert row["local_execution_status"] == (
            "NOT_RUN_SYNTHETIC_GENERATION_TRANSPORT_ONLY"
        )
        assert row["input_tokens"] == sum(phase["input_tokens"] for phase in phases)
        assert row["output_tokens"] == sum(phase["output_tokens"] for phase in phases)
        for phase in phases:
            assert "thread_id" not in phase
            assert len(phase["thread_id_sha256"]) == 64
            assert phase["thread_id_bytes"] == 36
            assert phase["stderr_bytes"] == 0
            assert phase["tool_calls"] == 0
            assert phase["billed_cost_usd"] is None
            assert phase["model_output_sha256"] == phase["last_message_file_sha256"]
            thread_hashes.append(phase["thread_id_sha256"])
    assert thread_hashes[0] == thread_hashes[1]
    assert thread_hashes[3] != thread_hashes[4]
    assert len(set(thread_hashes)) == 4
    assert receipt["raw_thread_ids_committed"] is False
    assert receipt["raw_jsonl_committed"] is False
    assert receipt["model_outputs_committed"] is False
    assert receipt["generated_programs_executed"] is False
    assert receipt["official_tasks_run"] == 0
    assert receipt["official_data_opened"] is False
    assert receipt["outcomes_opened"] is False
    assert receipt["scientific_authority_delta"] == "NONE"
    assert preflight["runner_admissible"] is False
    assert preflight["scientific_authority_delta"] == "NONE"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-only", action="store_true")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AdapterTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if not args.unit_only:
        validate_committed_artifacts()
    print(
        "P1_SAB_CODEX_ROUTE_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} runner_admissible=false official_tasks_run=0 outcomes_opened=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
