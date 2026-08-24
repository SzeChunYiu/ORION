#!/usr/bin/env python3
"""Synthetic, nonbenchmark hostile validation for SAB analysis freeze V1."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import sab_outcome_analysis_v1 as analysis


ROOT = Path(__file__).resolve().parent
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
HEX_D = "d" * 64
HEX_E = "e" * 64


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def synthetic_hash(label: str) -> str:
    return sha256_bytes(f"synthetic-nonbenchmark::{label}".encode("utf-8"))


def frozen_tasks() -> tuple[tuple[str, ...], dict[str, str], tuple[str, ...]]:
    return analysis._production_bindings()


def _discipline_solved_sets(ratios: dict[str, float]) -> dict[str, set[str]]:
    task_ids, task_to_discipline, discipline_order = frozen_tasks()
    solved: dict[str, set[str]] = {arm: set() for arm in analysis.ARMS}
    for discipline in discipline_order:
        ids = sorted(
            [task_id for task_id in task_ids if task_to_discipline[task_id] == discipline],
            key=lambda value: int(value),
        )
        for arm in analysis.ARMS:
            count = math.ceil(len(ids) * ratios[arm])
            solved[arm].update(ids[:count])
    return solved


def synthetic_ledger(
    *,
    ratios: dict[str, float] | None = None,
    generation_costs: dict[str, str] | None = None,
    cost_metric_id: str = "BILLED_USD",
    generation_billed_costs: dict[str, str | None] | None = None,
) -> dict:
    """Build 102 synthetic task receipts shaped like the production contract.

    No task text, program, evaluator body, official hash, credential, archive, or
    historical outcome is read.  Every digest is derived from an explicit
    ``synthetic-nonbenchmark`` label.
    """

    ratios = ratios or {"RR": 0.80, "OS": 0.55, "NR": 0.45}
    generation_costs = generation_costs or {"RR": "0.012", "OS": "0.010", "NR": "0.011"}
    generation_billed_costs = generation_billed_costs or (
        generation_costs
        if cost_metric_id == "BILLED_USD"
        else {"RR": None, "OS": None, "NR": None}
    )
    metric_definition = analysis.COST_METRICS[cost_metric_id]
    cost_metric = {
        "metric_id": cost_metric_id,
        "unit": metric_definition["unit"],
        "allocation_rule": metric_definition["allocation_rule"],
        "binding_phase": analysis.COST_BINDING_PHASE,
    }
    task_ids, task_to_discipline, _ = frozen_tasks()
    solved = _discipline_solved_sets(ratios)
    records = []
    for task_id in task_ids:
        attempts = []
        for arm in analysis.ARMS:
            for attempt in analysis.ATTEMPTS:
                is_solved = task_id in solved[arm] and attempt == 1
                attempts.append(
                    {
                        "arm_id": arm,
                        "attempt": attempt,
                        "candidate_program_sha256": synthetic_hash(
                            f"candidate:{task_id}:{arm}:{attempt}"
                        ),
                        "official_evaluator_record_sha256": synthetic_hash(
                            f"evaluator-record:{task_id}:{arm}:{attempt}"
                        ),
                        "official_evaluator_status": "OK",
                        "valid_program": 1,
                        "success_rate": "1" if is_solved else "0",
                        "generation_cost_quantity": generation_costs[arm],
                        "generation_billed_cost_usd": generation_billed_costs[arm],
                        "official_evaluator_billed_cost_usd": "0.001",
                        "failure": None,
                    }
                )
        records.append(
            {
                "task_id": task_id,
                "discipline": task_to_discipline[task_id],
                "official_task_record_sha256": synthetic_hash(f"task-record:{task_id}"),
                "attempt_records": attempts,
            }
        )
    return {
        "schema_version": analysis.OUTCOME_SCHEMA,
        "dataset": analysis.DATASET,
        "dataset_revision": analysis.DATASET_REVISION,
        "split": analysis.SPLIT,
        "verified_parquet_sha256": analysis.VERIFIED_PARQUET_SHA256,
        "official_source_commit": analysis.OFFICIAL_SOURCE_COMMIT,
        "candidate_seal_sha256": HEX_A,
        "run_plan_sha256": HEX_B,
        "generation_ledger_sha256": HEX_C,
        "evaluator_runtime_manifest_sha256": HEX_D,
        "official_evaluator_identity_sha256": HEX_E,
        "cost_gate_metric": cost_metric,
        "cost_gate_metric_binding_sha256": analysis._canonical_object_sha256(cost_metric),
        "cost_accounting": "ALL_ATTEMPTS_NO_SELECTION",
        "records": records,
    }


def positive_fake_bootstrap() -> dict:
    interval = {
        "lower": "0.010000000000",
        "upper": "0.200000000000",
        "lower_numerator": 1,
        "lower_denominator": 100,
        "upper_numerator": 1,
        "upper_denominator": 5,
        "lower_strictly_greater_than_zero": True,
    }
    return {
        "replicates": 100_000,
        "rng_algorithm": "MT19937_REFERENCE_UINT32_V1",
        "rng_seed_decimal": 20_260_824,
        "stratum_order": list(frozen_tasks()[2]),
        "quantile_rule": "NEAREST_RANK_CEIL_Q_TIMES_B",
        "lower_zero_index": 2499,
        "upper_zero_index": 97499,
        "replicate_contrast_numerators_sha256": synthetic_hash("patched-bootstrap"),
        "RR_minus_OS": copy.deepcopy(interval),
        "RR_minus_NR": copy.deepcopy(interval),
    }


class AnalysisFreezeSyntheticTests(unittest.TestCase):
    """All fixtures are generated synthetic nonbenchmark receipts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_ledger = synthetic_ledger()
        cls.full_bootstrap_result = analysis.analyze_ledger(
            cls.valid_ledger, synthetic_hash("complete-ledger")
        )

    def analyze_without_bootstrap(self, ledger: dict) -> dict:
        with mock.patch.object(
            analysis, "_paired_stratified_bootstrap", return_value=positive_fake_bootstrap()
        ):
            return analysis.analyze_ledger(ledger, synthetic_hash("hostile-ledger"))

    def test_frozen_contract_hash_population_and_counts(self) -> None:
        contract = analysis._load_frozen_contract()
        self.assertEqual(sha256_file(analysis.CONTRACT_PATH), analysis.CONTRACT_SHA256)
        population = contract["production_population"]
        self.assertEqual(population["task_ids"], [str(index) for index in range(1, 103)])
        self.assertEqual(population["official_task_record_count"], 102)
        self.assertEqual(population["nested_official_attempt_record_count"], 918)
        self.assertEqual(sum(population["discipline_counts"].values()), 102)
        task_ids, mapping, order = frozen_tasks()
        self.assertEqual(set(task_ids), set(mapping))
        self.assertEqual(tuple(population["discipline_order"]), order)

    def test_mt19937_reference_known_answer(self) -> None:
        rng = analysis.MT19937Reference(5489)
        self.assertEqual(
            [rng.uint32() for _ in range(5)],
            [3499211612, 581869302, 3890346734, 3586334585, 545404204],
        )

    def test_full_100k_paired_stratified_bootstrap_passes_synthetic_fixture(self) -> None:
        result = self.full_bootstrap_result
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["gate_evaluable"])
        self.assertEqual(result["population"]["observed_task_records"], 102)
        bootstrap = result["gate_components"]["paired_stratified_bootstrap"]
        self.assertEqual(bootstrap["replicates"], 100_000)
        self.assertEqual(bootstrap["rng_seed_decimal"], 20_260_824)
        self.assertEqual(bootstrap["lower_zero_index"], 2499)
        self.assertEqual(bootstrap["upper_zero_index"], 97499)
        self.assertRegex(bootstrap["replicate_contrast_numerators_sha256"], r"^[0-9a-f]{64}$")
        self.assertTrue(bootstrap["RR_minus_OS"]["lower_strictly_greater_than_zero"])
        self.assertTrue(bootstrap["RR_minus_NR"]["lower_strictly_greater_than_zero"])

    def test_strongest_comparator_and_all_attempt_generation_cost(self) -> None:
        result = self.full_bootstrap_result
        self.assertEqual(result["estimands"]["strongest_comparator"], "OS")
        cost = result["gate_components"]["generation_cost"]
        self.assertEqual(cost["accounting"], "ALL_ATTEMPTS_NO_SELECTION")
        self.assertEqual(cost["metric"]["metric_id"], "BILLED_USD")
        self.assertEqual(cost["total_quantity_by_arm"], {"RR": "3.672", "OS": "3.06", "NR": "3.366"})
        self.assertEqual(cost["RR_to_strongest_comparator_ratio"], "1.200000000000")
        separate = result["gate_components"]["official_evaluator_cost_separate"]
        self.assertFalse(separate["included_in_generation_ratio"])
        self.assertEqual(separate["total_available_usd_all_arms"], "0.918")

    def test_prospectively_bound_accelerator_seconds_supports_missing_billed_usd(self) -> None:
        ledger = synthetic_ledger(
            cost_metric_id="ALLOCATED_ACCELERATOR_SECONDS",
            generation_costs={"RR": "120", "OS": "100", "NR": "110"},
        )
        result = self.analyze_without_bootstrap(ledger)
        cost = result["gate_components"]["generation_cost"]
        billed = result["gate_components"]["generation_billed_usd_separate"]
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(cost["metric"]["unit"], "accelerator-second")
        self.assertEqual(cost["RR_to_strongest_comparator_ratio"], "1.200000000000")
        self.assertEqual(billed["missing_attempts_by_arm"], {"RR": 306, "OS": 306, "NR": 306})
        self.assertFalse(billed["missing_is_zero"])
        self.assertFalse(billed["gate_primary"])

    def test_strongest_comparator_tie_breaks_to_os(self) -> None:
        ledger = synthetic_ledger(ratios={"RR": 0.80, "OS": 0.55, "NR": 0.55})
        result = self.analyze_without_bootstrap(ledger)
        self.assertEqual(result["estimands"]["strongest_comparator"], "OS")
        self.assertEqual(
            result["estimands"]["strongest_comparator_tie_break"],
            "OS_BY_FROZEN_ARM_ORDER",
        )

    def test_strongest_comparator_can_be_nr(self) -> None:
        ledger = synthetic_ledger(ratios={"RR": 0.80, "OS": 0.45, "NR": 0.55})
        result = self.analyze_without_bootstrap(ledger)
        self.assertEqual(result["estimands"]["strongest_comparator"], "NR")
        self.assertEqual(result["gate_components"]["generation_cost"]["strongest_comparator"], "NR")

    def test_gain_below_point_zero_eight_fails_gate(self) -> None:
        ledger = synthetic_ledger(ratios={"RR": 0.60, "OS": 0.55, "NR": 0.45})
        result = self.analyze_without_bootstrap(ledger)
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["gate_components"]["point_gain"]["pass"])
        self.assertEqual(result["gate_components"]["point_gain"]["threshold"], "0.08")

    def test_discipline_loss_below_minus_point_zero_five_fails_gate(self) -> None:
        ledger = synthetic_ledger()
        target = "Computational Chemistry"
        for task_record in ledger["records"]:
            if task_record["discipline"] != target:
                continue
            for row in task_record["attempt_records"]:
                if row["arm_id"] == "OS" and row["attempt"] == 1:
                    row["success_rate"] = "1"
        result = self.analyze_without_bootstrap(ledger)
        report = result["gate_components"]["discipline_noninferiority"]
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(report["pass"])
        self.assertFalse(report["disciplines"][target]["contrast_pass"]["RR_minus_OS"])
        self.assertEqual(report["threshold"], "-0.05")

    def test_cost_ratio_above_one_point_five_fails_gate(self) -> None:
        ledger = synthetic_ledger(
            generation_costs={"RR": "0.016", "OS": "0.010", "NR": "0.011"}
        )
        result = self.analyze_without_bootstrap(ledger)
        cost = result["gate_components"]["generation_cost"]
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(cost["RR_to_strongest_comparator_ratio"], "1.600000000000")
        self.assertFalse(cost["pass"])
        self.assertEqual(cost["threshold"], "1.5")

    def test_zero_strongest_comparator_cost_is_cannot_check(self) -> None:
        ledger = synthetic_ledger(
            generation_costs={"RR": "0", "OS": "0", "NR": "0"}
        )
        with mock.patch.object(analysis, "_paired_stratified_bootstrap") as bootstrap:
            result = analysis.analyze_ledger(ledger, synthetic_hash("zero-cost"))
        bootstrap.assert_not_called()
        self.assertEqual(result["status"], "CANNOT_CHECK")
        self.assertIsNone(result["estimands"])
        self.assertEqual(result["cannot_check_reasons"][0]["code"], "CANNOT_CHECK_COST_DENOMINATOR_ZERO")

    def test_missing_task_is_cannot_check_before_metrics(self) -> None:
        ledger = copy.deepcopy(self.valid_ledger)
        ledger["records"].pop()
        with mock.patch.object(analysis, "_paired_stratified_bootstrap") as bootstrap:
            result = analysis.analyze_ledger(ledger, synthetic_hash("missing-task"))
        bootstrap.assert_not_called()
        self.assertEqual(result["status"], "CANNOT_CHECK")
        self.assertIsNone(result["estimands"])
        self.assertTrue(any(reason["code"] == "OFFICIAL_TASK_SET_MISMATCH" for reason in result["cannot_check_reasons"]))

    def test_missing_and_duplicate_attempts_are_cannot_check(self) -> None:
        for mutation in ("missing", "duplicate"):
            with self.subTest(mutation=mutation):
                ledger = copy.deepcopy(self.valid_ledger)
                attempts = ledger["records"][0]["attempt_records"]
                if mutation == "missing":
                    attempts.pop()
                else:
                    attempts[-1] = copy.deepcopy(attempts[0])
                result = analysis.analyze_ledger(ledger, synthetic_hash(mutation))
                self.assertEqual(result["status"], "CANNOT_CHECK")
                self.assertIsNone(result["gate_components"])

    def test_wrong_split_and_discipline_are_cannot_check(self) -> None:
        cases = []
        wrong_split = copy.deepcopy(self.valid_ledger)
        wrong_split["split"] = "validation"
        cases.append(wrong_split)
        wrong_discipline = copy.deepcopy(self.valid_ledger)
        wrong_discipline["records"][0]["discipline"] = "SYNTHETIC"
        cases.append(wrong_discipline)
        for ledger in cases:
            with self.subTest():
                result = analysis.analyze_ledger(ledger, synthetic_hash("identity-mismatch"))
                self.assertEqual(result["status"], "CANNOT_CHECK")
                self.assertIsNone(result["estimands"])

    def test_evaluator_failure_stays_cannot_check_not_solved_zero(self) -> None:
        ledger = copy.deepcopy(self.valid_ledger)
        row = ledger["records"][0]["attempt_records"][0]
        row.update(
            {
                "official_evaluator_record_sha256": None,
                "official_evaluator_status": "CANNOT_CHECK",
                "valid_program": None,
                "success_rate": None,
                "official_evaluator_billed_cost_usd": None,
                "failure": {
                    "status": "CANNOT_CHECK",
                    "stage": "OFFICIAL_EVALUATOR",
                    "code": "SYNTHETIC_RUNTIME_FAILURE",
                    "detail_sha256": synthetic_hash("runtime-failure"),
                },
            }
        )
        result = analysis.analyze_ledger(ledger, synthetic_hash("evaluator-failure"))
        self.assertEqual(result["status"], "CANNOT_CHECK")
        self.assertIsNone(result["estimands"])
        self.assertTrue(any(reason["code"] == "OFFICIAL_EVALUATOR_CANNOT_CHECK" for reason in result["cannot_check_reasons"]))

    def test_partial_outcome_and_numeric_string_coercions_are_rejected(self) -> None:
        mutations = []
        numeric_success = copy.deepcopy(self.valid_ledger)
        numeric_success["records"][0]["attempt_records"][0]["success_rate"] = 1
        mutations.append(numeric_success)
        exponent_cost = copy.deepcopy(self.valid_ledger)
        exponent_cost["records"][0]["attempt_records"][0]["generation_billed_cost_usd"] = "1e-3"
        mutations.append(exponent_cost)
        boolean_valid = copy.deepcopy(self.valid_ledger)
        boolean_valid["records"][0]["attempt_records"][0]["valid_program"] = True
        mutations.append(boolean_valid)
        missing_field = copy.deepcopy(self.valid_ledger)
        del missing_field["records"][0]["attempt_records"][0]["success_rate"]
        mutations.append(missing_field)
        for ledger in mutations:
            with self.subTest():
                result = analysis.analyze_ledger(ledger, synthetic_hash("coercion"))
                self.assertEqual(result["status"], "CANNOT_CHECK")
                self.assertIsNone(result["gate_components"])

    def test_extra_outcome_fields_and_bad_hashes_are_rejected(self) -> None:
        extra = copy.deepcopy(self.valid_ledger)
        extra["records"][0]["attempt_records"][0]["selected_best_attempt"] = True
        bad_hash = copy.deepcopy(self.valid_ledger)
        bad_hash["candidate_seal_sha256"] = "not-a-hash"
        for ledger in (extra, bad_hash):
            result = analysis.analyze_ledger(ledger, synthetic_hash("bad-schema"))
            self.assertEqual(result["status"], "CANNOT_CHECK")
            self.assertIsNone(result["estimands"])

    def test_cost_metric_binding_drift_and_missing_primary_billed_usd_are_rejected(self) -> None:
        drift = copy.deepcopy(self.valid_ledger)
        drift["cost_gate_metric"]["unit"] = "seconds"
        missing_billed = copy.deepcopy(self.valid_ledger)
        missing_billed["records"][0]["attempt_records"][0][
            "generation_billed_cost_usd"
        ] = None
        nonstring_identity = copy.deepcopy(self.valid_ledger)
        nonstring_identity["cost_gate_metric"]["metric_id"] = []
        for ledger in (drift, missing_billed, nonstring_identity):
            result = analysis.analyze_ledger(ledger, synthetic_hash("cost-identity"))
            self.assertEqual(result["status"], "CANNOT_CHECK")
            self.assertIsNone(result["gate_components"])

    def test_unreadable_and_malformed_json_paths_emit_cannot_check(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sab-analysis-synthetic-") as tmp:
            root = Path(tmp)
            missing = analysis.analyze_path(root / "missing.json")
            malformed_path = root / "malformed.json"
            malformed_path.write_bytes(b"{synthetic-nonbenchmark")
            malformed = analysis.analyze_path(malformed_path)
        self.assertEqual(missing["status"], "CANNOT_CHECK")
        self.assertEqual(malformed["status"], "CANNOT_CHECK")
        self.assertEqual(missing["cannot_check_reasons"][0]["code"], "LEDGER_READ_FAILURE")
        self.assertEqual(malformed["cannot_check_reasons"][0]["code"], "LEDGER_PARSE_FAILURE")

    def test_analyzer_has_no_network_subprocess_random_or_scientific_import(self) -> None:
        source = (ROOT / "sab_outcome_analysis_v1.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        forbidden = {
            "requests", "urllib", "httpx", "socket", "subprocess", "os", "random",
            "numpy", "scipy", "pandas", "docker", "openai", "anthropic", "evaluation",
        }
        self.assertFalse(imported & forbidden, imported & forbidden)
        self.assertNotIn("--seed", source)
        self.assertNotIn("--replicates", source)
        self.assertIn('parser.add_argument("--outcome-ledger"', source)
        self.assertIn('parser.add_argument("--output"', source)


def build_receipt(result: unittest.result.TestResult) -> dict:
    return {
        "schema_version": "orion.p1.scienceagentbench.synthetic-analysis-validation-receipt.v1",
        "receipt_id": "P1_SAB_OUTCOME_ANALYSIS_SYNTHETIC_VALIDATION_20260824_V1",
        "authority": "SYNTHETIC_NONBENCHMARK_ANALYSIS_CONTRACT_VALIDATION_ONLY__NO_OFFICIAL_OUTCOME_OR_SCIENTIFIC_AUTHORITY",
        "validated_on": "2026-08-24",
        "validator": "validate_analysis_freeze_v1.py",
        "validator_sha256": sha256_file(ROOT / "validate_analysis_freeze_v1.py"),
        "analyzer": "sab_outcome_analysis_v1.py",
        "analyzer_sha256": sha256_file(ROOT / "sab_outcome_analysis_v1.py"),
        "contract": "ANALYSIS_CONTRACT_V1.json",
        "contract_sha256": sha256_file(ROOT / "ANALYSIS_CONTRACT_V1.json"),
        "synthetic_tests_run": result.testsRun,
        "synthetic_tests_failed": len(result.failures),
        "synthetic_tests_errored": len(result.errors),
        "bootstrap_replicates_executed_by_complete_fixture": 100_000,
        "bootstrap_rng_algorithm": "MT19937_REFERENCE_UINT32_V1",
        "bootstrap_rng_seed_decimal": 20_260_824,
        "official_task_records_opened": 0,
        "official_outcomes_opened": False,
        "official_evaluator_invoked": False,
        "benchmark_archive_opened": False,
        "benchmark_task_text_opened": False,
        "candidate_or_program_bodies_opened": False,
        "gold_evaluator_rubric_or_judge_bodies_opened": False,
        "credentials_opened": False,
        "network_used_by_validation": False,
        "fixtures": "GENERATED_SYNTHETIC_NONBENCHMARK_ONLY__NOT_COMMITTED",
        "cost_gate_metric_identities_tested": [
            "BILLED_USD",
            "ALLOCATED_ACCELERATOR_SECONDS",
        ],
        "missing_billed_usd_treated_as_zero": False,
        "post_outcome_cost_metric_fallback_allowed": False,
        "missing_and_evaluator_failures_preserved_as_cannot_check": True,
        "terminal": "P1_SAB_OUTCOME_ANALYSIS_FREEZE_SYNTHETIC_HOSTILE_VALIDATION_PASS__OFFICIAL_OUTCOMES_CANNOT_CHECK__ZERO_OFFICIAL_RECORDS_OPENED",
        "scientific_authority_delta": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AnalysisFreezeSyntheticTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    if args.write_receipt is not None:
        receipt = build_receipt(result)
        args.write_receipt.write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
