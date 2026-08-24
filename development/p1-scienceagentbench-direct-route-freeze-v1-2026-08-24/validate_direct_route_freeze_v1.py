#!/usr/bin/env python3
"""Synthetic hostile validation for additive DIRECT_ROUTE_FREEZE_V1.

The suite uses invented packet objects and an injected in-memory completion
client.  It opens no benchmark task, protected archive, candidate body,
secret, outcome, manuscript, or PDF and invokes no provider, model, scheduler,
CI, or pytest path.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
DRIVER_PATH = ROOT / "direct_route_generation_driver_v1.py"
CONTRACT_PATH = ROOT / "DIRECT_ROUTE_FREEZE_CONTRACT_V1.json"
PROMPT_PATH = ROOT / "DIRECT_ROUTE_PROMPT_BUNDLE_V1.json"
RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"

UPSTREAM_HASHES = {
    "development/p1-scienceagentbench-runner-v1-2026-08-24/RUNNER_CONTRACT_V1.json": "e191540f131b3e7e33b0c040900bea94336dbd0d704b247b547a5c361b6e242f",
    "development/p1-scienceagentbench-runner-v1-2026-08-24/sab_verified_runner_v1.py": "15d6f511be9b3b1dbac408cc41812b0f72e1dd7aa700983035438efb8ed416df",
    "development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/RUNNER_V2_COST_AMENDMENT_CONTRACT.json": "806a497798ed162af06130ec9bc12a1edf6153dc4adb690886c1c1d87f67dc0e",
    "development/p1-scienceagentbench-runner-v2-cost-amendment-2026-08-24/sab_runner_v2_cost_amendment.py": "14c7d42b0b5add7c9bc4ae8608f74b422c638d0e795ef26996dcef4a87afe8ae",
    "development/p1-scienceagentbench-analysis-freeze-v1-2026-08-24/ANALYSIS_CONTRACT_V1.json": "0cae220a5b2f73156eda63a01f769dfdecbf8ad1fa16bd0995e3f906cff391d4",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/LUNARC_GENERATION_ADAPTER_CONTRACT_V1.json": "ae8fe86e4052b65f12176980fb03a653c1ab4b5b4f99c146d0db401563d93883",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py": "e46434fd37872a4ca7abce35375043bca2035fce52e3f36d611b1a03b98aefb9",
    "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/run_lunarc_attempt_v1.sh": "1d4655350c1a037cd4e51ee11e15e21491c5bfd7cea125948beb2e152c73b582",
}

REPAIRED_HASHES = {
    "development/p1-scienceagentbench-lunarc-longseed-mechanism-v1-2026-08-24/FROZEN_LONGSEED_MECHANISM_PROTOCOL_V1.json": "a939165b0e4b74662a3e991bf8029ce7c0d2bce22ca07dde6f7efd74bc6db944",
    "development/p1-scienceagentbench-lunarc-longseed-mechanism-v1-2026-08-24/LONGSEED_MECHANISM_RECEIPT_V1.json": "111a9a9390782bd3253f82c5ba2a2a074cc940b94660292888b3239dd2af6c84",
    "development/p1-scienceagentbench-lunarc-longseed-mechanism-v1-2026-08-24/PROMPT_PROVENANCE_V1.json": "12de378f4f020e4baa23a71f689ab290f340dbdec239bebe4e52360127e999c9",
    "development/p1-scienceagentbench-lunarc-longseed-structured-v1-2026-08-24/FROZEN_LONGSEED_STRUCTURED_PROTOCOL_V1.json": "8636ae1ca5e0bfc64e1244d05290da92bfd2c712070fda3084828de8506d8928",
    "development/p1-scienceagentbench-lunarc-longseed-structured-v1-2026-08-24/LONGSEED_STRUCTURED_RECEIPT_V1.json": "f41111109054a7cc5c136195a47f8a0b6a163d51bd914b49bf1dfa5616ae4114",
    "development/p1-scienceagentbench-lunarc-longseed-structured-v1-2026-08-24/FROZEN_OUTPUT_SCHEMA_V1.json": "7b9ffda6c9daa1f39a1350959590112c5c663c6373a81e1e3fbffa23f0649498",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, allow_nan=False, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


driver = load_module(DRIVER_PATH, "orion_direct_route_driver_v1")
adapter = load_module(
    REPO_ROOT
    / "development/p1-scienceagentbench-lunarc-generation-adapter-v1-2026-08-24/sab_lunarc_generation_adapter_v1.py",
    "orion_generation_adapter_for_direct_route_tests",
)
v2 = adapter.load_v2_module()


def synthetic_hash(label: str) -> str:
    return hashlib.sha256(f"synthetic-direct-route:{label}".encode()).hexdigest()


def synthetic_owner_selection() -> dict[str, Any]:
    budget = {
        "total_input_token_cap": 24000,
        "total_output_token_cap": 1024,
        "tool_call_cap": 0,
        "wall_time_seconds_cap": 240.0,
        "local_execution_seconds_cap": 30.0,
        "final_candidates_per_attempt": 1,
    }
    return {
        "status": "OWNER_FROZEN_BEFORE_TASK_OR_OUTCOME_OPENING",
        "basis": "SYNTHETIC_NONBENCHMARK_CONSTANTS_ONLY",
        "selected_before_task_or_outcome_opening": True,
        "protected_prompt_sizes_used": False,
        "context_window_tokens": 32768,
        "budget_by_arm": {arm: copy.deepcopy(budget) for arm in ("RR", "OS", "NR")},
        "phase_output_caps_by_arm": {
            "RR": {"RR_PHASE0": 256, "RR_PHASE1": 768},
            "OS": {"OS_PHASE1": 1024},
            "NR": {"NR_PHASE0": 256, "NR_PHASE1": 768},
        },
    }


def synthetic_plan(contract: dict[str, Any], prompt: dict[str, Any]) -> dict[str, Any]:
    selection = contract["budget_owner_selection_interface"]
    metric = v2._metric_object()
    measurement = {
        **v2.TIMING_CONSTANTS,
        "exclusive_gpu_count_by_arm": {arm: "1" for arm in v2.ARMS},
    }
    route_profile = dict(v2.ROUTE_PROFILE)
    route = contract["route_descriptor"]
    runtime = contract["model_runtime_binding"]
    sampling = contract["sampling"]
    tool_policy = contract["tool_policy"]
    prompt_hash = hashlib.sha256(PROMPT_PATH.read_bytes()).hexdigest()
    return {
        "schema_version": v2.RUN_PLAN_SCHEMA,
        "split": v2.PRODUCTION_SPLIT,
        "task_ids": list(v2.TASK_IDS),
        "arms": list(v2.ARMS),
        "attempts_per_task_arm": len(v2.ATTEMPTS),
        "bindings": {
            "model_id": runtime["model_sha256"],
            "provider": "local-llama-server",
            "tokenizer_revision": contract["tokenizer_binding"]["source_revision"],
            "prompt_bundle_sha256_by_arm": {arm: prompt_hash for arm in v2.ARMS},
            "seed_schedule": copy.deepcopy(contract["seed_schedule"]),
            "provider_seed_capability": "CONFIRMED",
            "model_parameters_sha256": hashlib.sha256(canonical_bytes(sampling)).hexdigest(),
            "tool_policy_sha256": hashlib.sha256(canonical_bytes(tool_policy)).hexdigest(),
            "generation_runtime_manifest_sha256": hashlib.sha256(
                canonical_bytes(runtime)
            ).hexdigest(),
            "credential_route_sha256": hashlib.sha256(canonical_bytes(route)).hexdigest(),
            "credential_route_status": "BOUND_OWNER_CONTROLLED",
        },
        "budget_by_arm": copy.deepcopy(selection["budget_by_arm"]),
        "cost_accounting": v2.COST_ACCOUNTING,
        "amendment_scope": "ALLOCATED_ACCELERATOR_SECONDS_ONLY__BILLED_USD_REMAINS_UNCHANGED_RUNNER_V1",
        "base_runner_contract_sha256": v2.V1_CONTRACT_SHA256,
        "base_runner_module_sha256": v2.V1_MODULE_SHA256,
        "analysis_contract_sha256": v2.ANALYSIS_CONTRACT_SHA256,
        "route_profile": route_profile,
        "route_profile_binding_sha256": hashlib.sha256(canonical_bytes(route_profile)).hexdigest(),
        "cost_gate_metric": metric,
        "cost_gate_metric_binding_sha256": hashlib.sha256(canonical_bytes(metric)).hexdigest(),
        "cost_measurement_binding": measurement,
        "cost_measurement_binding_sha256": hashlib.sha256(canonical_bytes(measurement)).hexdigest(),
    }


class SyntheticClient:
    def __init__(self, *, sentinel: str = "") -> None:
        self.requests: list[dict[str, Any]] = []
        self.sentinel = sentinel

    def complete(self, body: dict[str, Any]) -> dict[str, Any]:
        self.requests.append(copy.deepcopy(body))
        schema = body["json_schema"]
        kinds = schema.get("properties", {}).get("kind", {})
        if "enum" in kinds:
            kind = "RR_TYPED_STATE" if "RR phase 0" in body["prompt"] else "NR_GENERIC_PLAN"
            value = {
                "kind": kind,
                "assumptions": [self.sentinel or "synthetic assumption"],
                "unresolved_inputs": [],
                "intended_analysis": ["synthetic analysis"],
                "invariants": ["outcome blind"],
                "output_contract": "FINAL_PROGRAM JSON",
            }
        else:
            value = {"kind": "FINAL_PROGRAM", "program": "print('synthetic')"}
        content = canonical_bytes(value).decode("utf-8")
        return {
            "content": content,
            "timings": {"cache_n": 0, "prompt_n": 100, "predicted_n": 12},
            "tokens_predicted": 12,
            "truncated": False,
        }


class DirectRouteFreezeSyntheticTests(unittest.TestCase):
    def api(self, name: str):
        value = getattr(driver, name, None)
        self.assertTrue(callable(value), f"driver API missing: {name}")
        return value

    def packet(self) -> tuple[dict[str, Any], dict[str, Any]]:
        self.assertTrue(CONTRACT_PATH.is_file(), "contract packet is missing")
        self.assertTrue(PROMPT_PATH.is_file(), "prompt bundle is missing")
        return json.loads(CONTRACT_PATH.read_text()), json.loads(PROMPT_PATH.read_text())

    def execute(
        self,
        arm: str,
        client: SyntheticClient | Any | None = None,
        *,
        clock_values: tuple[int, int] = (10_000_000_000, 12_000_000_000),
    ):
        contract, prompt = self.packet()
        plan = synthetic_plan(contract, prompt)
        chosen_client = client or SyntheticClient()
        ticks = iter(clock_values)
        receipt = self.api("execute_attempt")(
            plan=plan,
            contract=contract,
            prompt_bundle=prompt,
            owner_selection=contract["budget_owner_selection_interface"],
            runtime_binding=contract["model_runtime_binding"],
            adapter_module=adapter,
            client=chosen_client,
            raw_clock=lambda: next(ticks),
            task_id=v2.TASK_IDS[0],
            arm_id=arm,
            attempt=1,
            masked_packet={"synthetic": "masked"},
            recovered_packet={"synthetic": "recovered"},
            run_plan_sha256=synthetic_hash("run-plan-bytes"),
            slurm_job_identity={
                "cluster": "lunarc",
                "job_id": "4000001",
                "array_job_id": None,
                "array_task_id": None,
            },
            slurm_in_job_snapshot_sha256=synthetic_hash("in-job-snapshot"),
        )
        return receipt, chosen_client, contract, prompt

    def assert_contract_error(self, operation, fragment: str) -> None:
        error = getattr(driver, "ContractError", None)
        self.assertTrue(isinstance(error, type), "driver ContractError is missing")
        with self.assertRaises(error) as caught:
            operation()
        self.assertIn(fragment, str(caught.exception))

    def test_01_exact_upstream_and_repaired_bindings(self) -> None:
        contract, _ = self.packet()
        declared = {
            entry["path"]: entry["sha256"] for entry in contract["upstream_bindings"]
        }
        repaired = {
            entry["path"]: entry["sha256"]
            for entry in contract["repaired_pr1159_bindings"]["files"]
        }
        self.assertEqual(declared, UPSTREAM_HASHES)
        self.assertEqual(repaired, REPAIRED_HASHES)
        self.assertEqual(contract["repaired_pr1159_bindings"]["merge_commit"], "53cc59353b82a3908dd8066de268d326bec3908f")
        for relative, expected in {**UPSTREAM_HASHES, **REPAIRED_HASHES}.items():
            self.assertEqual(sha256_file(REPO_ROOT / relative), expected)
        prompt = json.loads(PROMPT_PATH.read_text())
        self.api("validate_packet_contract")(contract, prompt)
        mutated = copy.deepcopy(prompt)
        mutated["templates"]["OS_PHASE1"]["text"] += "synthetic mutation\n"
        self.assert_contract_error(
            lambda: self.api("validate_packet_contract")(contract, mutated), "on-disk"
        )

    def test_02_phase_schemas_have_exact_canonical_bindings(self) -> None:
        _, prompt = self.packet()
        expected = {
            "phase0_state": (567, "11299b5be0c855c1453ef99a14d1637b5c11230409efd68f50fde3394341cba1"),
            "final_program": (239, "428e793d1f94a5b9e56731a8dd96a28b7e089aaad63d6a2be722d3ed7b266c2c"),
        }
        for name, (size, digest) in expected.items():
            raw = canonical_bytes(prompt["output_schemas"][name])
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (size, digest))
            self.assertEqual(
                prompt["output_schema_canonical_bindings"][name],
                {"canonical_bytes": size, "canonical_sha256": digest},
            )

    def test_03_owner_selection_requires_equal_budgets_and_phase_caps(self) -> None:
        validate = self.api("validate_owner_selection")
        selected = synthetic_owner_selection()
        self.assertEqual(validate(selected)["context_window_tokens"], 32768)
        unequal = copy.deepcopy(selected)
        unequal["budget_by_arm"]["OS"]["wall_time_seconds_cap"] = 241.0
        self.assert_contract_error(lambda: validate(unequal), "byte-equal")
        overflow = copy.deepcopy(selected)
        overflow["phase_output_caps_by_arm"]["RR"]["RR_PHASE1"] = 769
        self.assert_contract_error(lambda: validate(overflow), "sum")

    def test_04_owner_selection_rejects_protected_size_claims(self) -> None:
        selected = synthetic_owner_selection()
        selected["protected_prompt_sizes_used"] = True
        self.assert_contract_error(
            lambda: self.api("validate_owner_selection")(selected), "protected prompt sizes"
        )
        selected = synthetic_owner_selection()
        selected["selected_before_task_or_outcome_opening"] = False
        self.assert_contract_error(
            lambda: self.api("validate_owner_selection")(selected), "before"
        )

    def test_05_paired_seed_schedule_and_zero_tool_policy_are_frozen(self) -> None:
        contract, _ = self.packet()
        self.assertEqual(contract["seed_schedule"], {"1": 101, "2": 202, "3": 303})
        self.assertEqual(
            contract["tool_policy"],
            {"tool_call_cap": 0, "external_provider_calls": 0, "final_candidates_per_attempt": 1},
        )
        self.assertEqual(contract["attempt_retention"], "ALL_ATTEMPTS_NO_SELECTION")

    def test_06_route_is_literal_loopback_and_has_no_secret_or_proxy_route(self) -> None:
        contract, _ = self.packet()
        route = contract["route_descriptor"]
        self.assertEqual(route["base_url"], "http://127.0.0.1:8080")
        self.assertEqual(route["credential_mode"], "NONE_REQUIRED")
        self.assertEqual(route["headers"], {"Content-Type": "application/json"})
        self.assertEqual(route["proxies"], {})
        self.assertFalse(route["redirects_allowed"])
        self.assertFalse(route["model_pull_or_download_allowed_during_attempt"])
        self.assertEqual(route["kernel_egress_absence"], "CANNOT_CHECK")
        self.api("validate_runtime_binding")(contract["model_runtime_binding"], contract)

    def test_07_completion_request_has_exact_fields_and_json_schema(self) -> None:
        _, prompt = self.packet()
        body = self.api("build_completion_body")(
            "synthetic prompt\n", prompt["output_schemas"]["final_program"], 101, 128
        )
        self.assertEqual(
            set(body),
            {
                "prompt", "seed", "cache_prompt", "temperature", "top_k", "top_p",
                "min_p", "repeat_penalty", "n_predict", "stream", "return_tokens",
                "json_schema",
            },
        )
        self.assertIs(body["json_schema"], prompt["output_schemas"]["final_program"])
        self.assertFalse(body["cache_prompt"])
        self.assertEqual(body["seed"], 101)

    def test_08_strict_raw_json_rejects_prefix_suffix_duplicates_and_wrong_schema(self) -> None:
        _, prompt = self.packet()
        parse = self.api("parse_phase_content")
        good = '{"kind":"FINAL_PROGRAM","program":"print(1)"}'
        self.assertEqual(parse(good, prompt["output_schemas"]["final_program"])["kind"], "FINAL_PROGRAM")
        for bad in (
            "prefix " + good,
            good + " suffix",
            '{"kind":"FINAL_PROGRAM","kind":"FINAL_PROGRAM","program":"x"}',
            '{"kind":"FINAL_PROGRAM","program":""}',
            '{"kind":"FINAL_PROGRAM","program":"x","extra":1}',
        ):
            self.assert_contract_error(lambda bad=bad: parse(bad, prompt["output_schemas"]["final_program"]), "raw JSON")

    def test_09_rr_seals_canonical_state_and_inserts_state_and_hash(self) -> None:
        receipt, client, _, _ = self.execute("RR")
        self.assertEqual(len(client.requests), 2)
        state = json.loads(client.requests[0]["json_schema"] and SyntheticClient().complete(client.requests[0])["content"])
        sealed = canonical_bytes(state).decode("utf-8")
        digest = hashlib.sha256(sealed.encode()).hexdigest()
        self.assertIn(sealed, client.requests[1]["prompt"])
        self.assertIn(digest, client.requests[1]["prompt"])
        self.assertEqual(receipt["phase_sequence"], ["RR_PHASE0", "RR_PHASE1"])

    def test_10_os_is_exactly_one_shot_without_phase_zero(self) -> None:
        receipt, client, _, _ = self.execute("OS")
        self.assertEqual(len(client.requests), 1)
        self.assertNotIn("phase-0 state", client.requests[0]["prompt"].lower())
        self.assertEqual(receipt["phase_sequence"], ["OS_PHASE1"])

    def test_11_nr_phase_zero_sentinel_is_absent_from_reset_phase(self) -> None:
        sentinel = "NR_SYNTHETIC_SENTINEL_MUST_NOT_CROSS_RESET"
        receipt, client, _, _ = self.execute("NR", SyntheticClient(sentinel=sentinel))
        self.assertEqual(len(client.requests), 2)
        self.assertIn(sentinel, client.requests[0]["prompt"] + client.complete(client.requests[0])["content"])
        self.assertNotIn(sentinel, client.requests[1]["prompt"])
        self.assertEqual(receipt["phase_sequence"], ["NR_PHASE0", "NR_PHASE1"])

    def test_12_context_overflow_cache_reuse_and_truncation_fail_closed(self) -> None:
        validate = self.api("validate_completion_response")
        base = {
            "content": '{"kind":"FINAL_PROGRAM","program":"x"}',
            "timings": {"cache_n": 0, "prompt_n": 32000, "predicted_n": 8},
            "tokens_predicted": 8,
            "truncated": False,
        }
        validate(base, 768, 32768)
        for mutation, fragment in (
            (("timings", "cache_n", 1), "cache_n"),
            (("timings", "prompt_n", 32001), "context"),
            ((None, "truncated", True), "truncation"),
        ):
            bad = copy.deepcopy(base)
            parent, key, value = mutation
            (bad if parent is None else bad[parent])[key] = value
            self.assert_contract_error(lambda bad=bad: validate(bad, 768, 32768), fragment)

    def test_13_adapter_capture_remains_scheduler_finalization_pending(self) -> None:
        receipt, _, _, _ = self.execute("RR")
        self.assertEqual(receipt["status"], "TIMING_CAPTURED__ALLOCATION_FINALIZATION_PENDING")
        self.assertEqual(receipt["allocation_status"], "CANNOT_CHECK_PENDING_SCHEDULER_FINALIZATION")
        self.assertFalse(receipt["candidate_bodies_opened"])
        self.assertFalse(receipt["official_evaluator_invoked"])
        self.assertFalse(receipt["official_outcomes_opened"])

    def test_14_claim_boundary_never_promotes_semantic_choice(self) -> None:
        contract, _ = self.packet()
        self.assertEqual(
            contract["claim_boundary"],
            {
                "provider_seed_capability": "CONFIRMED",
                "semantic_choice_sensitivity": "NOT_ESTABLISHED",
                "candidate_semantic_diversity_gate_enabled": False,
                "attempt_retention": "ALL_ATTEMPTS_NO_SELECTION",
                "production_admissibility": "CANNOT_CHECK",
                "scientific_authority_delta": "NONE",
            },
        )

    def test_15_owner_prospective_budget_is_frozen_without_task_fit_claim(self) -> None:
        contract, _ = self.packet()
        owner = contract["budget_owner_selection_interface"]
        self.assertEqual(owner["status"], "OWNER_PROSPECTIVE_BUDGET_FROZEN_BEFORE_TASK_OR_OUTCOME_OPENING")
        budget = {
            "total_input_token_cap": 57344,
            "total_output_token_cap": 8192,
            "tool_call_cap": 0,
            "wall_time_seconds_cap": 1800.0,
            "local_execution_seconds_cap": 30.0,
            "final_candidates_per_attempt": 1,
        }
        self.assertEqual(owner["budget_by_arm"], {arm: budget for arm in ("RR", "OS", "NR")})
        self.assertEqual(
            owner["phase_output_caps_by_arm"],
            {
                "RR": {"RR_PHASE0": 1024, "RR_PHASE1": 7168},
                "OS": {"OS_PHASE1": 8192},
                "NR": {"NR_PHASE0": 1024, "NR_PHASE1": 7168},
            },
        )
        self.assertEqual(owner["task_fit_status"], "CANNOT_CHECK_BEFORE_TASK_OPENING")
        plan = synthetic_plan(contract, json.loads(PROMPT_PATH.read_text()))
        plan["budget_by_arm"] = copy.deepcopy(owner["budget_by_arm"])
        adapter.validate_plan(plan)
        incompatible = copy.deepcopy(owner)
        for arm in ("RR", "OS", "NR"):
            incompatible["budget_by_arm"][arm]["local_execution_seconds_cap"] = 0.0
        self.assert_contract_error(
            lambda: self.api("validate_owner_selection")(incompatible), "positive"
        )
        alternative = synthetic_owner_selection()
        alternative_plan = copy.deepcopy(plan)
        alternative_plan["budget_by_arm"] = copy.deepcopy(alternative["budget_by_arm"])
        self.assert_contract_error(
            lambda: self.api("validate_direct_plan")(
                alternative_plan,
                contract,
                json.loads(PROMPT_PATH.read_text()),
                alternative,
            ),
            "frozen owner",
        )
        self.assertFalse(contract["production_execution_authority"])

    def test_16_driver_has_no_process_secret_or_nonloopback_transport_route(self) -> None:
        source = DRIVER_PATH.read_text()
        for forbidden in (
            "import subprocess", "from subprocess", "os.environ", "getenv(",
            "Authorization", "Cookie", "X-API-Key", "requests.", "urlopen(",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("shell=True", source)
        self.assertIn("127.0.0.1", source)

    def test_17_synthetic_receipt_binds_final_core_artifacts(self) -> None:
        self.assertTrue(RECEIPT_PATH.is_file(), "synthetic receipt is missing")
        receipt = json.loads(RECEIPT_PATH.read_text())
        self.assertEqual(receipt["status"], "PASS_SYNTHETIC_HOSTILE_VALIDATION")
        self.assertEqual(receipt["official_tasks_opened"], 0)
        self.assertEqual(receipt["official_outcomes_opened"], 0)
        self.assertEqual(receipt["semantic_choice_sensitivity"], "NOT_ESTABLISHED")
        expected = {
            "DIRECT_ROUTE_FREEZE_CONTRACT_V1.json": sha256_file(CONTRACT_PATH),
            "DIRECT_ROUTE_PROMPT_BUNDLE_V1.json": sha256_file(PROMPT_PATH),
            "direct_route_generation_driver_v1.py": sha256_file(DRIVER_PATH),
        }
        self.assertEqual(receipt["artifact_sha256"], expected)

    def test_18_real_loopback_client_uses_capture_clock_for_actual_wall_time(self) -> None:
        response_body = canonical_bytes(
            {
                "content": '{"kind":"FINAL_PROGRAM","program":"print(1)"}',
                "timings": {"cache_n": 0, "prompt_n": 100, "predicted_n": 12},
                "tokens_predicted": 12,
                "truncated": False,
            }
        )
        calls: list[tuple[Any, ...]] = []

        class FakeResponse:
            status = 200

            def read(self) -> bytes:
                return response_body

        class FakeConnection:
            def __init__(self, host: str, port: int, timeout: float) -> None:
                calls.append(("connect", host, port, timeout))

            def request(self, method: str, path: str, **kwargs: Any) -> None:
                calls.append(("request", method, path, kwargs))

            def getresponse(self) -> FakeResponse:
                return FakeResponse()

            def close(self) -> None:
                calls.append(("close",))

        with mock.patch.object(driver.http.client, "HTTPConnection", FakeConnection):
            receipt, _, _, _ = self.execute(
                "OS",
                driver.LoopbackCompletionClient(),
                clock_values=(10_000_000_000, 12_500_000_000),
            )
        self.assertEqual(receipt["monotonic_elapsed_ns"], "2500000000")
        self.assertEqual(receipt["base_candidate_record"]["wall_time_seconds"], 2.5)
        self.assertEqual(calls[0][0], "connect")
        self.assertEqual(calls[1][1:3], ("POST", "/completion"))

        with self.assertRaises(driver.ContractError) as caught:
            self.execute(
                "OS",
                SyntheticClient(),
                clock_values=(0, 1_800_000_000_001),
            )
        self.assertIn("wall", str(caught.exception))

    def test_19_local_execution_zero_is_validated_actual_no_execution_usage(self) -> None:
        validate = self.api("validate_no_local_execution_usage")
        contract, _ = self.packet()
        self.assertEqual(
            contract["budget_owner_selection_interface"]["local_execution_usage_semantics"],
            "ACTUAL_TOOL_OR_CANDIDATE_PROGRAM_EXECUTION_ONLY__DIRECT_GENERATION_ROUTE_HAS_ZERO_EVENTS",
        )
        self.assertEqual(
            validate(
                tool_calls=0,
                candidate_execution_count=0,
                local_execution_wall_time_seconds=0.0,
            ),
            0.0,
        )
        for kwargs in (
            {"tool_calls": 1, "candidate_execution_count": 0, "local_execution_wall_time_seconds": 0.0},
            {"tool_calls": 0, "candidate_execution_count": 1, "local_execution_wall_time_seconds": 0.0},
            {"tool_calls": 0, "candidate_execution_count": 0, "local_execution_wall_time_seconds": 0.1},
        ):
            self.assert_contract_error(lambda kwargs=kwargs: validate(**kwargs), "local execution")
        receipt, _, _, _ = self.execute("RR")
        base = receipt["base_candidate_record"]
        self.assertEqual(base["tool_calls"], 0)
        self.assertEqual(base["local_execution_wall_time_seconds"], 0.0)

    def test_20_new_output_is_exclusive_no_follow_and_never_overwrites_aliases(self) -> None:
        write_new = self.api("write_new_canonical_json")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_bytes(b"sentinel-input\n")
            before = source.read_bytes()

            existing = root / "existing.json"
            existing.write_bytes(b"sentinel-existing\n")
            self.assert_contract_error(lambda: write_new(existing, {"x": 1}), "already exists")
            self.assertEqual(existing.read_bytes(), b"sentinel-existing\n")

            symlink_output = root / "symlink-output.json"
            symlink_output.symlink_to(source)
            self.assert_contract_error(lambda: write_new(symlink_output, {"x": 1}), "already exists")
            self.assertEqual(source.read_bytes(), before)

            hardlink_output = root / "hardlink-output.json"
            os.link(source, hardlink_output)
            self.assert_contract_error(lambda: write_new(hardlink_output, {"x": 1}), "already exists")
            self.assertEqual(source.read_bytes(), before)

            real_parent = root / "real-parent"
            real_parent.mkdir()
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            self.assert_contract_error(
                lambda: write_new(linked_parent / "new.json", {"x": 1}), "symlink"
            )
            self.assertFalse((real_parent / "new.json").exists())

            fresh = root / "fresh.json"
            digest = write_new(fresh, {"x": 1})
            self.assertEqual(digest, hashlib.sha256(b'{"x":1}\n').hexdigest())
            self.assertEqual(fresh.read_bytes(), b'{"x":1}\n')

    def test_21_cli_paths_reject_lexical_resolved_hardlink_and_casefold_aliases(self) -> None:
        validate = self.api("validate_cli_paths")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            first = root / "CaseInput.json"
            second = root / "second.json"
            first.write_text("first")
            second.write_text("second")
            upstream = {"contract": CONTRACT_PATH.resolve(), "adapter": driver.ADAPTER_PATH.resolve()}
            validate({"first": first, "second": second}, {"output": root / "fresh.json"}, upstream)
            frozen_upstream = driver._static_upstream_paths()
            self.assertEqual(len(frozen_upstream), 17)
            self.assertEqual(len(set(frozen_upstream.values())), 17)
            self.assertTrue(all(path.is_file() for path in frozen_upstream.values()))
            self.assert_contract_error(
                lambda: validate({"first": first}, {"output": CONTRACT_PATH.resolve()}, frozen_upstream),
                "alias",
            )

            cases = [
                ({"first": first}, {"output": first}, "alias"),
                ({"first": first}, {"output": root / "caseinput.JSON"}, "alias"),
                ({"first": Path("relative.json")}, {"output": root / "fresh.json"}, "absolute"),
            ]
            for inputs, outputs, fragment in cases:
                self.assert_contract_error(
                    lambda inputs=inputs, outputs=outputs: validate(inputs, outputs, upstream),
                    fragment,
                )

            hardlink = root / "hardlink.json"
            os.link(first, hardlink)
            self.assert_contract_error(
                lambda: validate({"first": first, "hardlink": hardlink}, {"output": root / "fresh2.json"}, upstream),
                "device/inode",
            )

            real_parent = root / "real-parent"
            real_parent.mkdir()
            target = real_parent / "target.json"
            target.write_text("target")
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            self.assert_contract_error(
                lambda: validate({"target": target}, {"output": linked_parent / "target.json"}, upstream),
                "alias",
            )

    def test_22_failed_exclusive_write_rolls_back_only_created_output(self) -> None:
        write_new = self.api("write_new_canonical_json")
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory) / "failed.json"
            with mock.patch.object(driver.os, "write", side_effect=OSError("synthetic write failure")):
                self.assert_contract_error(lambda: write_new(output, {"x": 1}), "write")
            self.assertFalse(output.exists())

    def test_23_cli_alias_failure_preserves_every_input_byte(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            files = {}
            for name in (
                "run-plan.json",
                "owner.json",
                "runtime.json",
                "masked.json",
                "recovered.json",
                "job.json",
            ):
                path = root / name
                path.write_bytes(("sentinel:" + name + "\n").encode())
                files[name] = path
            before = {name: path.read_bytes() for name, path in files.items()}
            argv = [
                "--run-plan", str(files["run-plan.json"]),
                "--owner-selection", str(files["owner.json"]),
                "--runtime-binding", str(files["runtime.json"]),
                "--masked-packet", str(files["masked.json"]),
                "--recovered-packet", str(files["recovered.json"]),
                "--task-id", "1",
                "--arm-id", "OS",
                "--attempt", "1",
                "--run-plan-sha256", synthetic_hash("plan"),
                "--slurm-job-identity", str(files["job.json"]),
                "--slurm-in-job-snapshot-sha256", synthetic_hash("snapshot"),
                "--output", str(files["run-plan.json"]),
            ]
            with self.assertRaises(driver.ContractError) as caught:
                driver.main(argv)
            self.assertIn("alias", str(caught.exception))
            self.assertEqual(
                {name: path.read_bytes() for name, path in files.items()}, before
            )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DirectRouteFreezeSyntheticTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    print(
        "P1_SAB_DIRECT_ROUTE_FREEZE_V1_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} official_tasks=0 official_outcomes=0 "
        "semantic_choice=NOT_ESTABLISHED production_admissibility=CANNOT_CHECK"
    )
