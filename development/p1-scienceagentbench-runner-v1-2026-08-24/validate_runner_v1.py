#!/usr/bin/env python3
"""Synthetic, network-free hostile validation for the SAB verified runner V1."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import inspect
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

import sab_verified_runner_v1 as runner  # noqa: E402


SYNTHETIC_IDS = ("1", "2")
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
HEX_D = "d" * 64
HEX_E = "e" * 64


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def synthetic_mask(parquet_hash: str, ids: tuple[str, ...] = SYNTHETIC_IDS) -> dict:
    descriptors = {
        name: {
            "state": "VISIBLE_FROM_PHASE_0"
            if name in {"task_inst", "output_fname"}
            else "MASK_THEN_EXACT_RECOVER",
            "value_type": "string",
            "canonical_json_bytes": 2,
            "canonical_json_sha256": sha256_bytes(f'"{name}"'.encode()),
        }
        for name in (
            "task_inst",
            "output_fname",
            "domain_knowledge",
            "dataset_folder_tree",
            "dataset_preview",
        )
    }
    return {
        "schema_version": "orion.p1.scienceagentbench.mask-manifest.v1",
        "source": {
            "dataset": "synthetic/nonbenchmark",
            "split": "verified",
            "verified_parquet_sha256": parquet_hash,
        },
        "records": [
            {
                "instance_id": task_id,
                "domain": "SYNTHETIC",
                "license_partition": "SYNTHETIC_NONBENCHMARK",
                "fields": copy.deepcopy(descriptors),
                "binding_sha256": sha256_bytes(task_id.encode()),
            }
            for task_id in ids
        ],
        "outcomes_opened": False,
        "scientific_authority_delta": "NONE",
    }


def valid_plan(ids: tuple[str, ...] = SYNTHETIC_IDS) -> dict:
    budget = {
        "total_input_token_cap": 1000,
        "total_output_token_cap": 500,
        "tool_call_cap": 4,
        "wall_time_seconds_cap": 60.0,
        "local_execution_seconds_cap": 30.0,
        "final_candidates_per_attempt": 1,
    }
    return {
        "schema_version": "orion.p1.scienceagentbench.run-plan.v1",
        "split": "verified",
        "task_ids": list(ids),
        "arms": ["RR", "OS", "NR"],
        "attempts_per_task_arm": 3,
        "bindings": {
            "model_id": "synthetic-model-v1",
            "provider": "synthetic-provider",
            "tokenizer_revision": "synthetic-tokenizer-v1",
            "prompt_bundle_sha256_by_arm": {
                "RR": HEX_A,
                "OS": HEX_B,
                "NR": HEX_C,
            },
            "seed_schedule": {"1": 101, "2": 202, "3": 303},
            "provider_seed_capability": "CONFIRMED",
            "model_parameters_sha256": HEX_D,
            "tool_policy_sha256": HEX_E,
            "generation_runtime_manifest_sha256": HEX_A,
            "credential_route_sha256": HEX_B,
            "credential_route_status": "BOUND_OWNER_CONTROLLED",
        },
        "budget_by_arm": {arm: copy.deepcopy(budget) for arm in runner.ARMS},
        "cost_accounting": "ALL_ATTEMPTS_NO_SELECTION",
    }


def valid_ledger(plan_hash: str, ids: tuple[str, ...] = SYNTHETIC_IDS) -> dict:
    records = []
    for task_id in ids:
        for arm in runner.ARMS:
            for attempt in runner.ATTEMPTS:
                records.append(
                    {
                        "task_id": task_id,
                        "arm_id": arm,
                        "attempt": attempt,
                        "seed": {1: 101, 2: 202, 3: 303}[attempt],
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "tool_calls": 1,
                        "wall_time_seconds": 2.5,
                        "local_execution_wall_time_seconds": 1.0,
                        "billed_cost_usd": 0.01,
                        "failure": None,
                        "raw_output_sha256": HEX_C,
                        "candidate_program_sha256": HEX_D,
                    }
                )
    return {
        "schema_version": "orion.p1.scienceagentbench.candidate-ledger.v1",
        "split": "verified",
        "run_plan_sha256": plan_hash,
        "cost_accounting": "ALL_ATTEMPTS_NO_SELECTION",
        "records": records,
    }


class SyntheticBundle:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.parquet = root / "synthetic-verified.parquet"
        self.mask = root / "synthetic-mask.json"
        self.plan = root / "synthetic-plan.json"
        self.ledger = root / "synthetic-ledger.json"
        self.parquet.write_bytes(b"synthetic nonbenchmark parquet stand-in\n")
        self.parquet_hash = sha256_file(self.parquet)
        write_json(self.mask, synthetic_mask(self.parquet_hash))
        self.mask_hash = sha256_file(self.mask)
        write_json(self.plan, valid_plan())
        self.plan_hash = sha256_file(self.plan)
        write_json(self.ledger, valid_ledger(self.plan_hash))

    def seal(self, *, split: str | None = "verified") -> dict:
        return runner._create_candidate_seal(
            split,
            self.parquet,
            self.mask,
            self.plan,
            self.ledger,
            expected_parquet_sha256=self.parquet_hash,
            expected_mask_sha256=self.mask_hash,
            expected_task_ids=SYNTHETIC_IDS,
        )


class RunnerSyntheticTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="sab-runner-synthetic-")
        self.bundle = SyntheticBundle(Path(self.tmp.name))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def assert_contract_error(self, action, contains: str) -> None:
        with self.assertRaises(runner.ContractError) as raised:
            action()
        self.assertIn(contains, str(raised.exception))

    def rewrite_mask(self, value: dict) -> None:
        write_json(self.bundle.mask, value)
        self.bundle.mask_hash = sha256_file(self.bundle.mask)

    def rewrite_plan(self, value: dict, *, rebind_ledger: bool = True) -> None:
        write_json(self.bundle.plan, value)
        self.bundle.plan_hash = sha256_file(self.bundle.plan)
        if rebind_ledger:
            ledger = json.loads(self.bundle.ledger.read_text())
            ledger["run_plan_sha256"] = self.bundle.plan_hash
            write_json(self.bundle.ledger, ledger)

    def rewrite_ledger(self, value: dict) -> None:
        write_json(self.bundle.ledger, value)

    def test_valid_bundle_seals_all_synthetic_tuples(self) -> None:
        seal = self.bundle.seal()
        self.assertEqual(
            seal["status"],
            "COMPLETE_CANDIDATE_LEDGER_SEALED__EVALUATOR_NOT_INVOKED",
        )
        self.assertEqual(seal["candidate_record_count"], 18)
        self.assertFalse(seal["official_evaluator_invoked"])
        self.assertFalse(seal["evaluator_outcomes_opened"])
        self.assertEqual(seal["scientific_authority_delta"], "NONE")

    def test_omitted_and_validation_splits_fail_closed(self) -> None:
        self.assert_contract_error(lambda: self.bundle.seal(split=None), "split")
        self.assert_contract_error(
            lambda: self.bundle.seal(split="validation"), "verified"
        )

    def test_wrong_parquet_hash_fails_closed(self) -> None:
        self.bundle.parquet.write_bytes(b"changed")
        self.assert_contract_error(self.bundle.seal, "Parquet SHA-256")

    def test_missing_parquet_fails_closed(self) -> None:
        self.bundle.parquet.unlink()
        self.assert_contract_error(self.bundle.seal, "does not exist")

    def test_wrong_mask_hash_fails_closed(self) -> None:
        mask = json.loads(self.bundle.mask.read_text())
        mask["synthetic_tamper"] = True
        write_json(self.bundle.mask, mask)
        self.assert_contract_error(self.bundle.seal, "mask-manifest SHA-256")

    def test_mask_parquet_binding_mismatch_fails_closed(self) -> None:
        mask = json.loads(self.bundle.mask.read_text())
        mask["source"]["verified_parquet_sha256"] = HEX_A
        self.rewrite_mask(mask)
        self.assert_contract_error(self.bundle.seal, "Parquet binding")

    def test_missing_duplicate_extra_and_noncanonical_ids_fail_closed(self) -> None:
        for bad_ids in (("1",), ("1", "1"), ("1", "2", "3"), ("01", "2")):
            with self.subTest(ids=bad_ids):
                mask = synthetic_mask(self.bundle.parquet_hash, bad_ids)
                self.rewrite_mask(mask)
                self.assert_contract_error(self.bundle.seal, "task IDs")

    def test_missing_arm_fails_closed(self) -> None:
        plan = valid_plan()
        plan["arms"] = ["RR", "OS"]
        self.rewrite_plan(plan)
        self.assert_contract_error(self.bundle.seal, "arms")

    def test_mismatched_budget_cap_fails_closed(self) -> None:
        plan = valid_plan()
        plan["budget_by_arm"]["NR"]["wall_time_seconds_cap"] = 61.0
        self.rewrite_plan(plan)
        self.assert_contract_error(self.bundle.seal, "matched")

    def test_unbound_runtime_values_fail_closed(self) -> None:
        for value in (None, "", "AUTHOR_INPUT_NEEDED", "CANNOT_CHECK_RUNTIME"):
            with self.subTest(value=value):
                plan = valid_plan()
                plan["bindings"]["model_id"] = value
                self.rewrite_plan(plan)
                self.assert_contract_error(self.bundle.seal, "model_id")

    def test_unconfirmed_seed_and_credential_routes_fail_closed(self) -> None:
        plan = valid_plan()
        plan["bindings"]["provider_seed_capability"] = "CANNOT_CHECK"
        self.rewrite_plan(plan)
        self.assert_contract_error(self.bundle.seal, "provider_seed_capability")
        plan = valid_plan()
        plan["bindings"]["credential_route_status"] = "UNBOUND"
        self.rewrite_plan(plan)
        self.assert_contract_error(self.bundle.seal, "credential_route_status")

    def test_missing_duplicate_and_extra_candidate_tuples_fail_closed(self) -> None:
        base = valid_ledger(self.bundle.plan_hash)
        cases = []
        missing = copy.deepcopy(base)
        missing["records"].pop()
        cases.append(missing)
        duplicate = copy.deepcopy(base)
        duplicate["records"][-1] = copy.deepcopy(duplicate["records"][0])
        cases.append(duplicate)
        extra = copy.deepcopy(base)
        row = copy.deepcopy(extra["records"][0])
        row["task_id"] = "3"
        extra["records"].append(row)
        cases.append(extra)
        for ledger in cases:
            with self.subTest(records=len(ledger["records"])):
                self.rewrite_ledger(ledger)
                self.assert_contract_error(self.bundle.seal, "candidate tuples")

    def test_wrong_attempt_and_seed_fail_closed(self) -> None:
        ledger = valid_ledger(self.bundle.plan_hash)
        ledger["records"][0]["attempt"] = 0
        self.rewrite_ledger(ledger)
        self.assert_contract_error(self.bundle.seal, "attempt")
        ledger = valid_ledger(self.bundle.plan_hash)
        ledger["records"][0]["seed"] = 999
        self.rewrite_ledger(ledger)
        self.assert_contract_error(self.bundle.seal, "seed")

    def test_missing_or_null_success_hash_fails_closed(self) -> None:
        ledger = valid_ledger(self.bundle.plan_hash)
        del ledger["records"][0]["raw_output_sha256"]
        self.rewrite_ledger(ledger)
        self.assert_contract_error(self.bundle.seal, "fields mismatch")
        ledger = valid_ledger(self.bundle.plan_hash)
        ledger["records"][0]["raw_output_sha256"] = None
        self.rewrite_ledger(ledger)
        self.assert_contract_error(self.bundle.seal, "successful record")

    def test_failure_record_preserves_nulls_and_cannot_check(self) -> None:
        ledger = valid_ledger(self.bundle.plan_hash)
        row = ledger["records"][0]
        row.update(
            {
                "input_tokens": None,
                "output_tokens": None,
                "tool_calls": None,
                "wall_time_seconds": None,
                "local_execution_wall_time_seconds": None,
                "billed_cost_usd": None,
                "failure": {
                    "status": "CANNOT_CHECK",
                    "stage": "GENERATION",
                    "code": "SYNTHETIC_RUNTIME_FAILURE",
                    "detail_sha256": None,
                },
                "raw_output_sha256": None,
                "candidate_program_sha256": None,
            }
        )
        self.rewrite_ledger(ledger)
        seal = self.bundle.seal()
        self.assertEqual(seal["cannot_check_record_count"], 1)
        self.assertNotIn("solved", seal)

    def test_solved_and_evaluator_feedback_fields_fail_closed(self) -> None:
        for key in ("solved", "evaluator_feedback", "official_score"):
            with self.subTest(key=key):
                ledger = valid_ledger(self.bundle.plan_hash)
                ledger["records"][0][key] = 0
                self.rewrite_ledger(ledger)
                self.assert_contract_error(self.bundle.seal, key)

    def test_invalid_measurements_fail_closed(self) -> None:
        for field, value in (
            ("input_tokens", "100"),
            ("tool_calls", True),
            ("wall_time_seconds", math.inf),
            ("billed_cost_usd", -0.01),
        ):
            with self.subTest(field=field, value=value):
                ledger = valid_ledger(self.bundle.plan_hash)
                ledger["records"][0][field] = value
                self.rewrite_ledger(ledger)
                self.assert_contract_error(self.bundle.seal, field)

    def test_candidate_usage_over_budget_fails_closed(self) -> None:
        for field, value in (
            ("input_tokens", 1001),
            ("output_tokens", 501),
            ("tool_calls", 5),
            ("wall_time_seconds", 60.1),
            ("local_execution_wall_time_seconds", 30.1),
        ):
            with self.subTest(field=field, value=value):
                ledger = valid_ledger(self.bundle.plan_hash)
                ledger["records"][0][field] = value
                self.rewrite_ledger(ledger)
                self.assert_contract_error(self.bundle.seal, "exceeds matched cap")

    def test_best_attempt_only_cost_mode_fails_closed(self) -> None:
        ledger = valid_ledger(self.bundle.plan_hash)
        ledger["cost_accounting"] = "BEST_ATTEMPT_ONLY"
        self.rewrite_ledger(ledger)
        self.assert_contract_error(self.bundle.seal, "ALL_ATTEMPTS_NO_SELECTION")

    def test_run_plan_digest_mismatch_fails_closed(self) -> None:
        plan = valid_plan()
        plan["bindings"]["model_id"] = "synthetic-model-v2"
        self.rewrite_plan(plan, rebind_ledger=False)
        self.assert_contract_error(self.bundle.seal, "run-plan SHA-256")

    def test_verified_evaluator_command_is_inert_and_exact(self) -> None:
        seal = self.bundle.seal()
        receipt = runner._build_evaluator_command_receipt(
            seal,
            official_repo_root=Path("/external/ScienceAgentBench-pinned"),
            benchmark_path=Path("/external/benchmark_verified"),
            pred_program_path=Path("/external/pred_programs/RR/attempt-1"),
            log_fname=Path("/external/logs/RR-attempt-1.jsonl"),
            arm_id="RR",
            attempt=1,
            run_id="rr-a1",
            split="verified",
            expected_task_ids=SYNTHETIC_IDS,
            expected_parquet_sha256=self.bundle.parquet_hash,
            expected_mask_sha256=self.bundle.mask_hash,
        )
        argv = receipt["argv"]
        self.assertEqual(argv.count("--split"), 1)
        self.assertEqual(argv[argv.index("--split") + 1], "verified")
        self.assertFalse(receipt["execution_allowed"])
        self.assertFalse(receipt["official_evaluator_invoked"])
        self.assertEqual(receipt["runtime_status"], "CANNOT_CHECK")
        self.assertEqual(receipt["official_source_commit"], runner.OFFICIAL_SOURCE_COMMIT)

    def test_unsealed_or_wrong_constant_receipts_cannot_emit(self) -> None:
        seal = self.bundle.seal()
        for key, value in (
            ("status", "PARTIAL"),
            ("candidate_record_count", 17),
            ("verified_parquet_sha256", HEX_A),
            ("mask_manifest_sha256", HEX_B),
            ("official_evaluator_invoked", True),
        ):
            with self.subTest(key=key):
                bad = copy.deepcopy(seal)
                bad[key] = value
                self.assert_contract_error(
                    lambda bad=bad: runner._build_evaluator_command_receipt(
                        bad,
                        official_repo_root=Path("/external/ScienceAgentBench-pinned"),
                        benchmark_path=Path("/external/benchmark_verified"),
                        pred_program_path=Path("/external/pred_programs/RR/attempt-1"),
                        log_fname=Path("/external/logs/RR-attempt-1.jsonl"),
                        arm_id="RR",
                        attempt=1,
                        run_id="rr-a1",
                        split="verified",
                        expected_task_ids=SYNTHETIC_IDS,
                        expected_parquet_sha256=self.bundle.parquet_hash,
                        expected_mask_sha256=self.bundle.mask_hash,
                    ),
                    key,
                )

    def test_evaluator_argv_missing_duplicate_or_conflicting_split_fails(self) -> None:
        base = [
            "python",
            "-m",
            "evaluation.harness.run_evaluation",
            "--benchmark_path",
            "/external/benchmark_verified",
            "--pred_program_path",
            "/external/pred_programs",
            "--log_fname",
            "/external/log.jsonl",
            "--run_id",
            "x",
        ]
        cases = (
            base,
            base + ["--split", "validation"],
            base + ["--split", "verified", "--split", "verified"],
            base + ["--split=verified"],
            base + ["--split", "verified", "--split=validation"],
        )
        for argv in cases:
            with self.subTest(argv=argv[-4:]):
                self.assert_contract_error(
                    lambda argv=argv: runner.validate_evaluator_argv(argv), "split"
                )

    def test_forbidden_paths_fail_closed(self) -> None:
        seal = self.bundle.seal()
        for path in (
            "/external/gold_programs",
            "/external/eval_programs",
            "/external/scoring_rubrics",
            "/external/evaluator_feedback",
            "/external/official_results",
        ):
            with self.subTest(path=path):
                self.assert_contract_error(
                    lambda path=path: runner._build_evaluator_command_receipt(
                        seal,
                        official_repo_root=Path("/external/ScienceAgentBench-pinned"),
                        benchmark_path=Path(path),
                        pred_program_path=Path("/external/pred_programs/RR/attempt-1"),
                        log_fname=Path("/external/logs/RR-attempt-1.jsonl"),
                        arm_id="RR",
                        attempt=1,
                        run_id="rr-a1",
                        split="verified",
                        expected_task_ids=SYNTHETIC_IDS,
                        expected_parquet_sha256=self.bundle.parquet_hash,
                        expected_mask_sha256=self.bundle.mask_hash,
                    ),
                    "forbidden path",
                )

    def test_production_api_exposes_no_constant_overrides(self) -> None:
        self.assertEqual(
            set(inspect.signature(runner.validate_input_binding).parameters),
            {"split", "parquet_path", "mask_manifest_path"},
        )
        self.assertEqual(
            set(inspect.signature(runner.create_candidate_seal).parameters),
            {
                "split",
                "parquet_path",
                "mask_manifest_path",
                "run_plan_path",
                "candidate_ledger_path",
            },
        )
        parser = runner.build_parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        self.assertFalse(any("expected" in option for option in option_strings))

    def test_cli_requires_explicit_verified_split(self) -> None:
        parser = runner.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["validate-bindings"])
        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "validate-bindings",
                    "--split",
                    "validation",
                    "--parquet",
                    "x",
                    "--mask-manifest",
                    "y",
                    "--run-plan",
                    "z",
                    "--output",
                    "o",
                ]
            )

    def test_module_has_no_execution_network_or_provider_imports(self) -> None:
        source = (ROOT / "sab_verified_runner_v1.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        banned_roots = {
            "subprocess",
            "socket",
            "urllib",
            "requests",
            "httpx",
            "docker",
            "pandas",
            "pyarrow",
            "openai",
            "anthropic",
        }
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertFalse(imported & banned_roots)
        forbidden_calls = {"system", "popen", "spawn", "execv", "execve"}
        called = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertFalse(called & forbidden_calls)

    def test_contract_and_preflight_bindings_match_production_constants(self) -> None:
        contract = json.loads((ROOT / "RUNNER_CONTRACT_V1.json").read_text())
        constants = contract["production_constants"]
        self.assertEqual(constants["split"], runner.PRODUCTION_SPLIT)
        self.assertEqual(
            constants["verified_parquet_sha256"], runner.PRODUCTION_PARQUET_SHA256
        )
        self.assertEqual(
            constants["mask_manifest_sha256"],
            runner.PRODUCTION_MASK_MANIFEST_SHA256,
        )
        self.assertEqual(
            constants["official_source_commit"], runner.OFFICIAL_SOURCE_COMMIT
        )
        preflight_mask = REPO_ROOT / constants["mask_manifest_path"]
        self.assertEqual(sha256_file(preflight_mask), runner.PRODUCTION_MASK_MANIFEST_SHA256)


def expected_receipt(tests_run: int) -> dict:
    return {
        "schema_version": "orion.p1.scienceagentbench.synthetic-runner-validation-receipt.v1",
        "receipt_id": "P1_SAB_VERIFIED_RUNNER_SYNTHETIC_VALIDATION_20260824_V1",
        "authority": "SYNTHETIC_NONBENCHMARK_CONTRACT_VALIDATION_ONLY__NO_BENCHMARK_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "validated_on": "2026-08-24",
        "validator": "validate_runner_v1.py",
        "validator_sha256": sha256_file(ROOT / "validate_runner_v1.py"),
        "runner": "sab_verified_runner_v1.py",
        "runner_sha256": sha256_file(ROOT / "sab_verified_runner_v1.py"),
        "contract": "RUNNER_CONTRACT_V1.json",
        "contract_sha256": sha256_file(ROOT / "RUNNER_CONTRACT_V1.json"),
        "preflight_mask_manifest_sha256_verified": runner.PRODUCTION_MASK_MANIFEST_SHA256,
        "synthetic_tests_run": tests_run,
        "synthetic_tests_failed": 0,
        "synthetic_tests_errored": 0,
        "official_parquet_opened": False,
        "official_task_text_opened": False,
        "benchmark_archive_opened": False,
        "gold_program_bodies_opened": False,
        "evaluation_program_bodies_opened": False,
        "rubric_bodies_opened": False,
        "result_bodies_opened": False,
        "official_evaluator_invoked": False,
        "network_used_by_validation": False,
        "production_constants_overrideable_from_cli": False,
        "null_and_cannot_check_preserved": True,
        "evaluator_command_emission_only": True,
        "terminal": "P1_SAB_VERIFIED_RUNNER_SYNTHETIC_HOSTILE_VALIDATION_PASS__OFFICIAL_RUNTIME_AND_OWNER_BINDINGS_CANNOT_CHECK__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED",
        "scientific_authority_delta": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RunnerSyntheticTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1

    receipt = expected_receipt(result.testsRun)
    receipt_path = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V1.json"
    if args.write_receipt:
        write_json(receipt_path, receipt)
    else:
        if not receipt_path.is_file():
            raise AssertionError("synthetic validation receipt is missing")
        observed = json.loads(receipt_path.read_text(encoding="utf-8"))
        if observed != receipt:
            raise AssertionError(
                "synthetic validation receipt is stale; rerun with --write-receipt"
            )

    print(
        "P1_SAB_VERIFIED_RUNNER_SYNTHETIC_VALIDATION_PASS "
        f"tests={result.testsRun} official_tasks_run=0 outcomes_opened=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
