#!/usr/bin/env python3
"""Synthetic hostile verification for the Runner V2 cost amendment.

All values are deterministic synthetic nonbenchmark metadata.  The validation
opens no archive, task, candidate body, evaluator body, outcome, or credential.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE_PATH = ROOT / "sab_runner_v2_cost_amendment.py"
RECEIPT_PATH = ROOT / "SYNTHETIC_VALIDATION_RECEIPT_V2.json"


def load_module():
    spec = importlib.util.spec_from_file_location("sab_runner_v2_cost_amendment", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load amendment module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


amendment = load_module()


def synthetic_hash(label: str) -> str:
    return hashlib.sha256(f"synthetic-nonbenchmark:{label}".encode()).hexdigest()


def canonical_hash(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def synthetic_plan() -> dict:
    budget = {
        "total_input_token_cap": 4096,
        "total_output_token_cap": 2048,
        "tool_call_cap": 8,
        "wall_time_seconds_cap": 10.0,
        "local_execution_seconds_cap": 5.0,
        "final_candidates_per_attempt": 1,
    }
    metric = amendment._metric_object()
    measurement = {
        **amendment.TIMING_CONSTANTS,
        "exclusive_gpu_count_by_arm": {arm: "1" for arm in amendment.ARMS},
    }
    route = dict(amendment.ROUTE_PROFILE)
    return {
        "schema_version": amendment.RUN_PLAN_SCHEMA,
        "split": amendment.PRODUCTION_SPLIT,
        "task_ids": list(amendment.TASK_IDS),
        "arms": list(amendment.ARMS),
        "attempts_per_task_arm": len(amendment.ATTEMPTS),
        "bindings": {
            "model_id": "synthetic-open-weight-model",
            "provider": "synthetic-local-vllm",
            "tokenizer_revision": "synthetic-tokenizer-revision",
            "prompt_bundle_sha256_by_arm": {
                arm: synthetic_hash(f"prompt:{arm}") for arm in amendment.ARMS
            },
            "seed_schedule": {"1": 101, "2": 202, "3": 303},
            "provider_seed_capability": "CONFIRMED",
            "model_parameters_sha256": synthetic_hash("model-parameters"),
            "tool_policy_sha256": synthetic_hash("tool-policy"),
            "generation_runtime_manifest_sha256": synthetic_hash("runtime"),
            "credential_route_sha256": synthetic_hash("owner-route-without-secret"),
            "credential_route_status": "BOUND_OWNER_CONTROLLED",
        },
        "budget_by_arm": {arm: copy.deepcopy(budget) for arm in amendment.ARMS},
        "cost_accounting": amendment.COST_ACCOUNTING,
        "amendment_scope": (
            "ALLOCATED_ACCELERATOR_SECONDS_ONLY__BILLED_USD_REMAINS_UNCHANGED_RUNNER_V1"
        ),
        "base_runner_contract_sha256": amendment.V1_CONTRACT_SHA256,
        "base_runner_module_sha256": amendment.V1_MODULE_SHA256,
        "analysis_contract_sha256": amendment.ANALYSIS_CONTRACT_SHA256,
        "route_profile": route,
        "route_profile_binding_sha256": canonical_hash(route),
        "cost_gate_metric": metric,
        "cost_gate_metric_binding_sha256": canonical_hash(metric),
        "cost_measurement_binding": measurement,
        "cost_measurement_binding_sha256": canonical_hash(measurement),
    }


def synthetic_ledger(plan: dict, run_plan_sha256: str) -> dict:
    elapsed_by_arm = {"RR": 2_000_000_000, "OS": 1_500_000_000, "NR": 1_250_000_000}
    records = []
    index = 0
    for task_id in amendment.TASK_IDS:
        for arm in amendment.ARMS:
            for attempt in amendment.ATTEMPTS:
                start = 10_000_000_000 + index * 3_000_000_000
                elapsed = elapsed_by_arm[arm]
                records.append(
                    {
                        "task_id": task_id,
                        "arm_id": arm,
                        "attempt": attempt,
                        "seed": plan["bindings"]["seed_schedule"][str(attempt)],
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "tool_calls": 1,
                        "wall_time_seconds": 3.0,
                        "local_execution_wall_time_seconds": 1.0,
                        "billed_cost_usd": None,
                        "failure": None,
                        "raw_output_sha256": synthetic_hash(f"raw:{task_id}:{arm}:{attempt}"),
                        "candidate_program_sha256": synthetic_hash(
                            f"candidate:{task_id}:{arm}:{attempt}"
                        ),
                        "generation_cost_quantity": amendment._ns_to_accelerator_seconds(elapsed),
                        "generation_billed_cost_usd": None,
                        "generation_billed_cost_status": "CANNOT_CHECK",
                        "cost_metric_id": amendment.METRIC_ID,
                        "cost_gate_metric_binding_sha256": plan[
                            "cost_gate_metric_binding_sha256"
                        ],
                        "exclusive_gpu_count": "1",
                        "timing_provenance_sha256": plan[
                            "cost_measurement_binding_sha256"
                        ],
                        "monotonic_start_ns": str(start),
                        "monotonic_end_ns": str(start + elapsed),
                        "monotonic_elapsed_ns": str(elapsed),
                        "accelerator_allocation_status": "EXCLUSIVE_NO_OVERLAP_CONFIRMED",
                    }
                )
                index += 1
    return {
        "schema_version": amendment.LEDGER_SCHEMA,
        "split": amendment.PRODUCTION_SPLIT,
        "run_plan_sha256": run_plan_sha256,
        "cost_gate_metric": copy.deepcopy(plan["cost_gate_metric"]),
        "cost_gate_metric_binding_sha256": plan["cost_gate_metric_binding_sha256"],
        "cost_measurement_binding_sha256": plan["cost_measurement_binding_sha256"],
        "cost_accounting": amendment.COST_ACCOUNTING,
        "records": records,
    }


class RunnerV2CostAmendmentSyntheticTests(unittest.TestCase):
    """Hostile tests over synthetic 102 x 3 x 3 metadata only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = synthetic_plan()
        cls.run_plan_sha256 = synthetic_hash("run-plan-bytes-placeholder")
        cls.ledger = synthetic_ledger(cls.plan, cls.run_plan_sha256)

    def assert_reject(self, callable_, fragment: str) -> None:
        with self.assertRaises(amendment.ContractError) as caught:
            callable_()
        self.assertIn(fragment.lower(), str(caught.exception).lower())

    def validate_plan(self, plan: dict) -> None:
        amendment._validate_run_plan(plan, expected_task_ids=amendment.TASK_IDS)

    def validate_ledger(self, ledger: dict, plan: dict | None = None):
        plan = plan or self.plan
        return amendment._validate_candidate_ledger(
            ledger,
            plan,
            expected_task_ids=amendment.TASK_IDS,
            expected_run_plan_sha256=self.run_plan_sha256,
        )

    def test_01_upstream_and_amendment_hashes_are_frozen(self) -> None:
        analysis = amendment._load_and_verify_upstream_contracts()
        self.assertEqual(
            analysis["outcome_ledger_contract"]["cost_gate_metric_binding"][
                "supported_metrics"
            ][amendment.METRIC_ID]["allocation_rule"],
            amendment.ALLOCATION_RULE,
        )

    def test_02_valid_plan_delegates_unchanged_v1_invariants(self) -> None:
        validated = amendment.validate_run_plan(copy.deepcopy(self.plan))
        self.assertEqual(validated["arms"], ["RR", "OS", "NR"])

    def test_03_valid_complete_918_ledger_passes(self) -> None:
        by_tuple, billed, totals = self.validate_ledger(copy.deepcopy(self.ledger))
        self.assertEqual(len(by_tuple), 918)
        self.assertEqual(billed, {"RR": 0, "OS": 0, "NR": 0})
        self.assertGreater(totals["OS"], 0)
        self.assertGreater(totals["NR"], 0)

    def test_04_billed_usd_cannot_check_remains_null_not_zero(self) -> None:
        by_tuple, _, _ = self.validate_ledger(copy.deepcopy(self.ledger))
        projection = amendment._build_projection(
            by_tuple,
            self.plan,
            expected_task_ids=amendment.TASK_IDS,
            candidate_ledger_sha256=synthetic_hash("ledger"),
            run_plan_sha256=self.run_plan_sha256,
        )
        self.assertTrue(
            all(
                attempt["generation_billed_cost_usd"] is None
                for task in projection["records"]
                for attempt in task["attempt_records"]
            )
        )

    def test_05_authoritative_billed_usd_is_retained_separately(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["generation_billed_cost_status"] = "AVAILABLE"
        ledger["records"][0]["billed_cost_usd"] = "0.01"
        ledger["records"][0]["generation_billed_cost_usd"] = "0.01"
        by_tuple, billed, _ = self.validate_ledger(ledger)
        self.assertEqual(billed["RR"], 1)
        self.assertEqual(by_tuple[("1", "RR", 1)]["generation_cost_quantity"], "2")
        self.assertEqual(by_tuple[("1", "RR", 1)]["generation_billed_cost_usd"], "0.01")

    def test_06_missing_billed_usd_cannot_be_imputed_as_zero(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["billed_cost_usd"] = "0"
        ledger["records"][0]["generation_billed_cost_usd"] = "0"
        self.assert_reject(lambda: self.validate_ledger(ledger), "zero imputation")

    def test_07_billed_availability_requires_both_byte_equal_copies(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        record = ledger["records"][0]
        record["generation_billed_cost_status"] = "AVAILABLE"
        record["billed_cost_usd"] = "0.01"
        record["generation_billed_cost_usd"] = "0.010"
        self.assert_reject(lambda: self.validate_ledger(ledger), "canonical")

    def test_08_billed_usd_metric_is_rejected_not_shadowed(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cost_gate_metric"] = {
            "metric_id": "BILLED_USD",
            "unit": "USD",
            "allocation_rule": "SUM_PROVIDER_BILLED_USD_FOR_ALL_ATTEMPTS_NO_SELECTION",
            "binding_phase": amendment.BINDING_PHASE,
        }
        plan["cost_gate_metric_binding_sha256"] = canonical_hash(plan["cost_gate_metric"])
        self.assert_reject(lambda: self.validate_plan(plan), "unchanged Runner V1")

    def test_09_metric_unit_allocation_and_phase_drift_reject(self) -> None:
        for field, value in (
            ("unit", "GPU-second"),
            ("allocation_rule", "SUM_WALL_TIME"),
            ("binding_phase", "AFTER_OUTCOMES"),
        ):
            plan = copy.deepcopy(self.plan)
            plan["cost_gate_metric"][field] = value
            plan["cost_gate_metric_binding_sha256"] = canonical_hash(plan["cost_gate_metric"])
            self.assert_reject(lambda plan=plan: self.validate_plan(plan), "drift")

    def test_10_metric_binding_digest_mismatch_rejects(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["cost_gate_metric_binding_sha256"] = synthetic_hash("wrong-metric-binding")
        self.assert_reject(lambda: self.validate_plan(plan), "binding")

    def test_11_route_drift_rejects_even_when_rehashed(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["route_profile"]["site"] = "SYNTHETIC_OTHER_SITE"
        plan["route_profile_binding_sha256"] = canonical_hash(plan["route_profile"])
        self.assert_reject(lambda: self.validate_plan(plan), "route_profile")

    def test_12_gpu_counts_must_be_positive_canonical_and_equal_across_arms(self) -> None:
        mutations = (("NR", "2"), ("OS", "0"), ("RR", "01"), ("RR", 1))
        for arm, value in mutations:
            plan = copy.deepcopy(self.plan)
            plan["cost_measurement_binding"]["exclusive_gpu_count_by_arm"][arm] = value
            plan["cost_measurement_binding_sha256"] = canonical_hash(
                plan["cost_measurement_binding"]
            )
            self.assert_reject(lambda plan=plan: self.validate_plan(plan), "gpu")

    def test_13_exact_monotonic_provenance_constants_cannot_drift(self) -> None:
        for field, value in (
            ("clock_id", "CLOCK_MONOTONIC"),
            ("clock_api", "time"),
            ("start_boundary", "AFTER_GENERATION"),
            ("overlap_rule", "SHARED_GPU"),
        ):
            plan = copy.deepcopy(self.plan)
            plan["cost_measurement_binding"][field] = value
            plan["cost_measurement_binding_sha256"] = canonical_hash(
                plan["cost_measurement_binding"]
            )
            self.assert_reject(lambda plan=plan, field=field: self.validate_plan(plan), field)

    def test_14_record_metric_identity_and_binding_must_match_all_918(self) -> None:
        for field, value in (
            ("cost_metric_id", "BILLED_USD"),
            ("cost_gate_metric_binding_sha256", synthetic_hash("fallback")),
        ):
            ledger = copy.deepcopy(self.ledger)
            ledger["records"][917][field] = value
            self.assert_reject(lambda ledger=ledger: self.validate_ledger(ledger), "drift")

    def test_15_record_timing_provenance_hash_drift_rejects(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][411]["timing_provenance_sha256"] = synthetic_hash("wrong-clock")
        self.assert_reject(lambda: self.validate_ledger(ledger), "provenance drift")

    def test_16_record_gpu_count_must_match_frozen_plan(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["exclusive_gpu_count"] = "2"
        ledger["records"][0]["generation_cost_quantity"] = "4"
        self.assert_reject(lambda: self.validate_ledger(ledger), "gpu count drift")

    def test_17_noncanonical_monotonic_numbers_reject(self) -> None:
        hostile = ("01", "+1", "-1", "1.0", "1e3", 1, True)
        for value in hostile:
            ledger = copy.deepcopy(self.ledger)
            ledger["records"][0]["monotonic_start_ns"] = value
            self.assert_reject(lambda ledger=ledger: self.validate_ledger(ledger), "canonical")

    def test_18_monotonic_end_before_start_rejects(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        record = ledger["records"][0]
        record["monotonic_end_ns"] = str(int(record["monotonic_start_ns"]) - 1)
        self.assert_reject(lambda: self.validate_ledger(ledger), "precedes")

    def test_19_monotonic_elapsed_must_equal_end_minus_start(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["monotonic_elapsed_ns"] = "1999999999"
        self.assert_reject(lambda: self.validate_ledger(ledger), "end-minus-start")

    def test_20_primary_quantity_must_equal_exact_gpu_times_elapsed(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["generation_cost_quantity"] = "2.000000001"
        self.assert_reject(lambda: self.validate_ledger(ledger), "exact gpu-count")

    def test_21_negative_exponent_float_and_redundant_cost_forms_reject(self) -> None:
        hostile = ("-2", "+2", "02", "2.0", "2e0", 2, 2.0, True)
        for value in hostile:
            ledger = copy.deepcopy(self.ledger)
            ledger["records"][0]["generation_cost_quantity"] = value
            self.assert_reject(lambda ledger=ledger: self.validate_ledger(ledger), "canonical")

    def test_22_extra_fallback_field_is_rejected(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        ledger["records"][0]["fallback_billed_usd"] = "0"
        self.assert_reject(lambda: self.validate_ledger(ledger), "fields mismatch")

    def test_23_missing_duplicate_and_extra_tuples_reject(self) -> None:
        missing = copy.deepcopy(self.ledger)
        missing["records"].pop()
        duplicate = copy.deepcopy(self.ledger)
        duplicate["records"][-1] = copy.deepcopy(duplicate["records"][0])
        extra = copy.deepcopy(self.ledger)
        extra["records"].append(copy.deepcopy(extra["records"][0]))
        for ledger in (missing, duplicate, extra):
            self.assert_reject(lambda ledger=ledger: self.validate_ledger(ledger), "tuple")

    def test_24_zero_os_total_rejects_unknown_strongest_denominator(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        for record in ledger["records"]:
            if record["arm_id"] == "OS":
                record["monotonic_end_ns"] = record["monotonic_start_ns"]
                record["monotonic_elapsed_ns"] = "0"
                record["generation_cost_quantity"] = "0"
        self.assert_reject(lambda: self.validate_ledger(ledger), "denominator")

    def test_25_zero_nr_total_rejects_unknown_strongest_denominator(self) -> None:
        ledger = copy.deepcopy(self.ledger)
        for record in ledger["records"]:
            if record["arm_id"] == "NR":
                record["monotonic_end_ns"] = record["monotonic_start_ns"]
                record["monotonic_elapsed_ns"] = "0"
                record["generation_cost_quantity"] = "0"
        self.assert_reject(lambda: self.validate_ledger(ledger), "denominator")

    def test_26_unequal_v1_budgets_remain_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["budget_by_arm"]["NR"]["wall_time_seconds_cap"] = 11.0
        self.assert_reject(lambda: self.validate_plan(plan), "v1 run-plan invariant")

    def test_27_usage_caps_and_candidate_failures_retain_v1_semantics(self) -> None:
        over = copy.deepcopy(self.ledger)
        over["records"][0]["input_tokens"] = 4097
        self.assert_reject(lambda: self.validate_ledger(over), "exceeds")

        failed = copy.deepcopy(self.ledger)
        record = failed["records"][0]
        record["failure"] = {
            "status": "CANNOT_CHECK",
            "stage": "GENERATION",
            "code": "SYNTHETIC_FAILURE",
            "detail_sha256": synthetic_hash("synthetic-failure-detail"),
        }
        record["raw_output_sha256"] = None
        record["candidate_program_sha256"] = None
        by_tuple, _, totals = self.validate_ledger(failed)
        self.assertIsNone(by_tuple[("1", "RR", 1)]["candidate_program_sha256"])
        self.assertGreater(totals["RR"], 0)

    def test_28_duplicate_json_members_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"split":"validation","split":"verified"}\n', encoding="utf-8")
            self.assert_reject(lambda: amendment._load_json(path, "hostile"), "strict")

    def test_29_projection_matches_frozen_analysis_generation_fields_exactly(self) -> None:
        by_tuple, _, _ = self.validate_ledger(copy.deepcopy(self.ledger))
        projection = amendment._build_projection(
            by_tuple,
            self.plan,
            expected_task_ids=amendment.TASK_IDS,
            candidate_ledger_sha256=synthetic_hash("candidate-ledger"),
            run_plan_sha256=self.run_plan_sha256,
        )
        analysis = amendment._load_and_verify_upstream_contracts()
        amendment._validate_projection_against_analysis_contract(projection, analysis)
        self.assertEqual(set(projection), amendment.PROJECTION_TOP_LEVEL_FIELDS)
        self.assertEqual(len(projection["records"]), 102)
        self.assertEqual(
            sum(len(task["attempt_records"]) for task in projection["records"]), 918
        )
        self.assertEqual(
            set(projection["records"][0]["attempt_records"][0]),
            amendment.PROJECTION_ATTEMPT_FIELDS,
        )

    def test_30_projection_contains_no_outcome_or_evaluator_fields(self) -> None:
        by_tuple, _, _ = self.validate_ledger(copy.deepcopy(self.ledger))
        projection = amendment._build_projection(
            by_tuple,
            self.plan,
            expected_task_ids=amendment.TASK_IDS,
            candidate_ledger_sha256=synthetic_hash("candidate-ledger"),
            run_plan_sha256=self.run_plan_sha256,
        )
        serialized = json.dumps(projection, sort_keys=True)
        for forbidden in (
            "success_rate",
            "valid_program",
            "official_evaluator_status",
            "official_evaluator_record_sha256",
            "official_evaluator_billed_cost_usd",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_31_full_production_seal_and_cli_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan_path = root / "synthetic-plan.json"
            ledger_path = root / "synthetic-ledger.json"
            output_ledger = root / "synthetic-cost-projection.json"
            output_receipt = root / "synthetic-cost-receipt.json"
            plan_path.write_text(json.dumps(self.plan, indent=2) + "\n", encoding="utf-8")
            run_plan_sha256 = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            ledger = synthetic_ledger(self.plan, run_plan_sha256)
            ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()) as stdout:
                status = amendment.main(
                    [
                        "--run-plan",
                        str(plan_path),
                        "--candidate-ledger",
                        str(ledger_path),
                        "--output-ledger",
                        str(output_ledger),
                        "--output-receipt",
                        str(output_receipt),
                    ]
                )
            self.assertEqual(status, 0)
            projection = amendment._load_json(output_ledger, "synthetic projection")
            receipt = amendment._load_json(output_receipt, "synthetic receipt")
            self.assertEqual(receipt["candidate_record_count"], 918)
            self.assertEqual(receipt["official_outcomes_opened"], False)
            self.assertEqual(receipt["official_evaluator_invoked"], False)
            self.assertEqual(receipt["arm_generation_cost_totals"]["RR"], "612")
            self.assertEqual(receipt["arm_generation_cost_totals"]["OS"], "459")
            self.assertEqual(receipt["arm_generation_cost_totals"]["NR"], "382.5")
            self.assertEqual(
                receipt["emitted_cost_projection_file_sha256"],
                hashlib.sha256(output_ledger.read_bytes()).hexdigest(),
            )
            self.assertEqual(projection["cost_gate_metric"], amendment._metric_object())
            self.assertIn("ALLOCATED_ACCELERATOR_COST_LEDGER_SEALED", stdout.getvalue())

    def test_32_source_has_no_execution_or_outcome_analysis_imports(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("import docker", source)
        self.assertNotIn("run_evaluation", source)
        self.assertNotIn("success_rate", source)
        self.assertIn("official_evaluator_invoked", source)
        self.assertIn("official_outcomes_opened", source)


def write_receipt(result: unittest.TestResult) -> None:
    receipt = {
        "schema_version": "orion.p1.scienceagentbench.runner-v2-cost-amendment-synthetic-validation.v1",
        "contract_sha256": amendment.AMENDMENT_CONTRACT_SHA256,
        "base_runner_contract_sha256": amendment.V1_CONTRACT_SHA256,
        "base_runner_module_sha256": amendment.V1_MODULE_SHA256,
        "analysis_contract_sha256": amendment.ANALYSIS_CONTRACT_SHA256,
        "fixtures": "SYNTHETIC_NONBENCHMARK_METADATA_ONLY",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "hostile_boundaries": [
            "upstream hash drift",
            "BILLED_USD shadowing or fallback",
            "metric unit/allocation/binding-phase/hash drift",
            "route and exact monotonic provenance drift",
            "unequal, zero, or noncanonical GPU counts",
            "per-attempt metric/provenance/GPU drift across 918 records",
            "noncanonical or negative cost/timing numbers",
            "end-before-start, elapsed mismatch, derived-cost mismatch",
            "nullable billed USD zero imputation or status/value mismatch",
            "missing/duplicate/extra tuple sets and selected-only accounting",
            "zero OS or NR prospective comparator total",
            "Runner V1 budget/cap/failure invariant regression",
            "duplicate JSON members",
            "Analysis Freeze V1 projection field drift",
            "execution-capability or outcome/evaluator field leakage"
        ],
        "production_shape_validated": {
            "task_records": 102,
            "arms": ["RR", "OS", "NR"],
            "attempts_per_task_arm": 3,
            "candidate_records": 918,
            "projection_attempt_records": 918
        },
        "billed_usd_route": "UNCHANGED_RUNNER_V1__NOT_REIMPLEMENTED",
        "missing_billed_usd_imputed_as_zero": False,
        "post_outcome_metric_fallback_allowed": False,
        "strongest_comparator_zero_denominator_allowed": False,
        "official_tasks_run": 0,
        "official_outcomes_opened": 0,
        "official_evaluator_invoked": False,
        "benchmark_archive_opened": False,
        "candidate_bodies_opened": False,
        "credentials_opened": False,
        "manuscript_or_pdf_opened": False,
        "ci_or_pytest_run": False,
        "scientific_authority_delta": "NONE",
        "terminal": (
            "P1_SAB_RUNNER_V2_ALLOCATED_COST_SYNTHETIC_HOSTILE_VALIDATION_PASS__"
            "OFFICIAL_RUN_AND_OUTCOMES_CANNOT_CHECK__ZERO_TASKS_RUN__ZERO_OUTCOMES_OPENED"
        ),
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        RunnerV2CostAmendmentSyntheticTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    write_receipt(result)
    print(
        "P1_SAB_RUNNER_V2_ALLOCATED_COST_SYNTHETIC_HOSTILE_VALIDATION_PASS "
        f"tests={result.testsRun} official_tasks=0 official_outcomes=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
