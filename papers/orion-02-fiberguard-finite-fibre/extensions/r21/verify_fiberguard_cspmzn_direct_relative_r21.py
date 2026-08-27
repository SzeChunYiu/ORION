#!/usr/bin/env python3
"""Independent structural/result checker for ORION-02 R21 CSP-MZN."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
from typing import Any, Sequence

import numpy as np

SCHEMA = "ORION.FiberGuard.CSPMZNDirectRelative.R21.v1"
TERMINAL = "C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SCENARIO = "CSP-MZN-2013"
TOL = 1e-9
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED_TEXT = "ORION02_R21_CSPMZN_DIRECT_RELATIVE_BOOTSTRAP_V1"

EXPECTED_SOURCE_BLOBS = {
    "README.md": "bbae808cc2f718b15b379b30ef6a9909933fc3d5",
    f"{SCENARIO}/readme.txt": "55180a18d255fd01bf8c504794c85e1361e0b4de",
    f"{SCENARIO}/description.txt": "fef9553ae42035d065325c4cf938ea77c4a55b11",
    f"{SCENARIO}/algorithm_runs.arff": "874d8f4693b0c83bc82be55a77e4b3ef3ef5a0ea",
    f"{SCENARIO}/cv.arff": "9cfeda3e75d6d6ac4aa1bfb11b1a9dabf06f658e",
    f"{SCENARIO}/feature_costs.arff": "428ee0a211c9c35fd1962609428d586535215a4a",
    f"{SCENARIO}/feature_runstatus.arff": "cb802dd046d9bafe21f0580cce1c70121332d828",
    f"{SCENARIO}/feature_values.arff": "d98002d161b994d17b8155ca2e643cc29f17aec3",
}

PRESERVED_RECORD_SHA256 = {
    "papers/orion-02-fiberguard-finite-fibre/extensions/r11/"
    "FIBERGUARD_ASLIB_SAT12_ALL_R11_RESULTS_SUMMARY.json": (
        "8f944b219e4687b7629f5de93ce18c773d7d1ddb75cda938dd46b04eca6991a0"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r14/"
    "FIBERGUARD_ASLIB_HELDOUT_R14_RESULTS_SUMMARY.json": (
        "cba9a4c3f9fb6043e66972397826e825e1dc02b6fcaaa2620ff2040b38b50ee4"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r15/"
    "FIBERGUARD_MULTIDOMAIN_R15_RESULTS_SUMMARY.json": (
        "ec0f24f43133d5dddcdb0fe92ab60d011721f281e9006d45299337ae015ed2a3"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r16/"
    "FIBERGUARD_CROSS_SCENARIO_R16_RESULTS_SUMMARY.json": (
        "064628624c76dbfd3bf86b42e5108ef5aa793a3b41ef5dc8e09faa89c2df6c3e"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r17/FALLBACK_ALIGNMENT_R17_RESULTS.json": (
        "f4e8d00a8fe8f65b7fa2245d9f9ca60fa79d4b436731b8f170769d28fff7280f"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18-relative/"
    "RELATIVE_ROUTE_EXTENSION_R18_RESULTS.json": (
        "0092b67ba718daa5c977ad9fe248acd568fc94b558bb23ac42c6640a0ece8355"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18/"
    "FIBERGUARD_PAIRED_ROUTE_R18_RECOVERY_RESULTS.json": (
        "e5a4bb3c913405ec10be0cd8db3e8091deb3a3f14a855f2a5402770071e336b9"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r18/R18_RECOVERY_CUSTODY_V2.json": (
        "9b30cbd81991deba0b16f57b633409e7213f6f15c1c0ff87f980da8bc7660188"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r19/JOINT_ROUTE_R19_RESULTS.json": (
        "a6d29aca32a574886c22239e18adf14a8440776ffeea833f53d2e188b6d83f93"
    ),
    "papers/orion-02-fiberguard-finite-fibre/experiments/results/"
    "CERTIFIED_NEIGHBORHOOD_RESULT_V1.json": (
        "c6a7fa151c53f3e0397fc8351b951967028c5cc4bd08af63435122ddb315f97e"
    ),
    "papers/orion-02-fiberguard-finite-fibre/experiments/results/"
    "CERTIFIED_NEIGHBORHOOD_CONFORMAL_RECOVERY_RESULT_V2.json": (
        "0f5fb813ac9baa25efbba795b18452af36eeb47a3878f7181b9f063ac08a5c21"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r20/"
    "FIBERGUARD_BNSL_ADAPTIVE_R20_RESULTS.json": (
        "c843a0cb1c0a5a13863f27518e721cf8786334fba21a088f8ca4350ec947c49e"
    ),
    "papers/orion-02-fiberguard-finite-fibre/extensions/r20/BNSL_R20_CUSTODY_V1.json": (
        "c06e707dfb7b5a79935cd2ed716dadd38eca1609bab9706ff2358ed4005d6738"
    ),
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def nearest_rank(values: Sequence[float], probability: float) -> float:
    ordered = sorted(float(value) for value in values)
    return ordered[max(1, math.ceil(probability * len(ordered))) - 1]


def summary(values: Sequence[float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": nearest_rank(values, 0.95),
        "maximum": max(values),
    }


def close(left: float, right: float, *, tolerance: float = 1e-9) -> bool:
    return math.isclose(float(left), float(right), abs_tol=tolerance, rel_tol=1e-12)


def paired_bootstrap(differences: np.ndarray) -> dict[str, Any]:
    seed = int.from_bytes(hashlib.sha256(BOOTSTRAP_SEED_TEXT.encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    samples: list[np.ndarray] = []
    completed = 0
    while completed < BOOTSTRAP_REPLICATES:
        batch = min(500, BOOTSTRAP_REPLICATES - completed)
        indices = rng.integers(0, len(differences), size=(batch, len(differences)))
        samples.append(np.mean(differences[indices], axis=1))
        completed += batch
    values = np.concatenate(samples)
    return {
        "method": "paired_instance_cluster_percentile",
        "replicates": BOOTSTRAP_REPLICATES,
        "seed_text": BOOTSTRAP_SEED_TEXT,
        "seed_u64": seed,
        "lower_95": nearest_rank(values.tolist(), 0.025),
        "upper_95": nearest_rank(values.tolist(), 0.975),
    }


def verify_source(subject_repo: Path, result: dict[str, Any]) -> None:
    head = subprocess.check_output(
        ["git", "-C", str(subject_repo), "rev-parse", "HEAD"], text=True
    ).strip()
    assert head == ASLIB_COMMIT
    assert result["upstream"]["commit"] == ASLIB_COMMIT
    assert result["upstream"]["scenario"] == SCENARIO
    for relative, expected_blob in EXPECTED_SOURCE_BLOBS.items():
        path = subject_repo / relative
        receipt = result["upstream"]["files"][relative]
        assert path.is_file()
        assert git_blob_sha(path) == expected_blob == receipt["git_blob_sha1"]
        assert path.stat().st_size == receipt["bytes"]
        assert sha256_file(path) == receipt["sha256"]
    assert result["upstream"]["permission"]["statement"] == "GPLv3"
    assert result["upstream"]["permission"]["data_vendored_in_orion"] is False


def verify_preserved_records(repo_root: Path) -> None:
    for relative, expected in PRESERVED_RECORD_SHA256.items():
        path = repo_root / relative
        assert path.is_file(), relative
        assert sha256_file(path) == expected, relative


def verify_result(result_path: Path, repo_root: Path, subject_repo: Path) -> None:
    raw = result_path.read_bytes()
    result = json.loads(raw)
    assert raw == (canonical_json(result) + "\n").encode()
    assert result["schema"] == SCHEMA
    assert result["terminal"] == TERMINAL
    assert result["protocol"]["round"] == 2
    assert result["protocol"]["legal_pair_count_per_fold"] == 44
    assert result["protocol"]["learned_profile_count"] == 4
    assert result["protocol"]["fallback_profile_count"] == 11
    assert result["protocol"]["primary_comparator"] == "point_relative"
    assert result["corpus"]["instances"] == 4642
    assert len(result["corpus"]["algorithms"]) == 11
    assert result["corpus"]["steps"] == ["dynamic", "static"]
    assert result["corpus"]["instance_set_equality"] is True

    verify_source(subject_repo, result)
    verify_preserved_records(repo_root)

    folds = result["folds"]
    assert len(folds) == 10
    assert {fold["test_fold"] for fold in folds} == set(range(1, 11))
    for fold in folds:
        test_fold = fold["test_fold"]
        assert fold["legal_pair_count"] == 44
        assert fold["roles"]["test_fold"] == test_fold
        assert fold["roles"]["calibration_fold"] == (test_fold % 10) + 1
        assert fold["roles"]["pair_selection_fold"] == ((test_fold + 1) % 10) + 1
        assert fold["roles"]["route_fit_fold"] == ((test_fold + 2) % 10) + 1
        assert len(fold["roles"]["model_train_folds"]) == 6
        assert sum(fold["role_counts"].values()) == 4642
        assert fold["conformal"]["alpha"] == 0.10

    profiles = result["pair_selection_profiles"]
    assert len(profiles) == 440
    for test_fold in range(1, 11):
        subset = [row for row in profiles if row["test_fold"] == test_fold]
        assert len(subset) == 44
        assert sum(row["selected"] for row in subset) == 1
        identities = {(row["learned_profile"], row["fallback_solver"]) for row in subset}
        assert len(identities) == 44

    rows = result["out_of_fold"]["rows"]
    assert len(rows) == 4642 == result["out_of_fold"]["row_count"]
    assert len({row["instance_id"] for row in rows}) == len(rows)
    assert {row["test_fold"] for row in rows} == set(range(1, 11))
    arm_names = set(rows[0]["losses"])
    expected_arms = {
        "always_fallback",
        "always_learned",
        "direct_relative_certified",
        "oracle_route",
        "point_relative",
        "post_acquisition_same_route",
        "random_rate_matched",
        "uncertainty_only",
    }
    assert arm_names == expected_arms
    for row in rows:
        assert (
            set(row["choices"])
            == set(row["losses"])
            == set(row["timeouts"])
            == set(row["acquisition"])
            == expected_arms
        )
        delta = row["fallback_loss"] - row["learned_loss"]
        assert close(delta, row["actual_delta_fallback_minus_learned"])
        covers = row["interval_lower"] - TOL <= delta <= row["interval_upper"] + TOL
        assert covers == row["interval_covers_delta"]
        sign_error = row["choices"]["direct_relative_certified"] == "learned" and delta < -TOL
        assert sign_error == row["certified_learned_sign_error"]
        direct_is_learned = row["choices"]["direct_relative_certified"] == "learned"
        post_is_learned = row["choices"]["post_acquisition_same_route"] == "learned"
        assert direct_is_learned == post_is_learned
        timing_gap = (
            row["losses"]["post_acquisition_same_route"]
            - row["losses"]["direct_relative_certified"]
        )
        expected_gap = (
            0.0 if direct_is_learned else row["learned_acquisition"] - row["fallback_acquisition"]
        )
        assert close(timing_gap, expected_gap)

    for arm in sorted(expected_arms):
        values = [row["losses"][arm] for row in rows]
        computed = summary(values)
        recorded = result["out_of_fold"]["arms"][arm]
        for metric, value in computed.items():
            assert close(value, recorded[metric]), (arm, metric)
        timeout_count = sum(row["timeouts"][arm] for row in rows)
        learned_count = sum(row["choices"][arm] == "learned" for row in rows)
        mean_acquisition = statistics.fmean(row["acquisition"][arm] for row in rows)
        assert timeout_count == recorded["timeout_count"]
        assert learned_count == recorded["learned_count"]
        assert close(mean_acquisition, recorded["mean_acquisition"])
        assert close(timeout_count / len(rows), recorded["timeout_rate"])

    differences = np.array(
        [
            row["losses"]["direct_relative_certified"] - row["losses"]["point_relative"]
            for row in rows
        ],
        dtype=np.float64,
    )
    paired = result["out_of_fold"]["paired_primary_minus_point"]
    assert close(float(np.mean(differences)), paired["mean_difference"])
    recomputed_bootstrap = paired_bootstrap(differences)
    for key in ("method", "replicates", "seed_text", "seed_u64"):
        assert recomputed_bootstrap[key] == paired["bootstrap_95"][key]
    for key in ("lower_95", "upper_95"):
        assert close(recomputed_bootstrap[key], paired["bootstrap_95"][key])

    interval = result["out_of_fold"]["paired_interval"]
    coverage = statistics.fmean(row["interval_covers_delta"] for row in rows)
    certified = [row for row in rows if row["choices"]["direct_relative_certified"] == "learned"]
    sign_error_rate = statistics.fmean(row["certified_learned_sign_error"] for row in certified)
    assert len(certified) == interval["certified_learned_count"]
    assert close(len(certified) / len(rows), interval["certified_learned_fraction"])
    assert close(coverage, interval["empirical_coverage"])
    assert close(sign_error_rate, interval["certified_learned_sign_error_rate"])

    primary = result["out_of_fold"]["arms"]["direct_relative_certified"]
    comparator = result["out_of_fold"]["arms"]["point_relative"]
    difference = primary["mean"] - comparator["mean"]
    relative_reduction = (comparator["mean"] - primary["mean"]) / comparator["mean"]
    material = (
        relative_reduction >= 0.05
        and paired["bootstrap_95"]["upper_95"] < 0
        and primary["timeout_count"] <= comparator["timeout_count"]
        and coverage >= 0.90
        and sign_error_rate <= 0.10
    )
    if len(certified) / len(rows) < 0.01:
        expected_terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_NO_CERTIFIED_LEARNED_COVERAGE"
    elif material:
        expected_terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_JOINT_ROUTE_VALUE"
    elif difference < -TOL:
        expected_terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_STRICT_BUT_NOT_MATERIAL"
    elif abs(difference) <= TOL:
        expected_terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_NULL"
    else:
        expected_terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE"
    assert expected_terminal == result["terminal"] == TERMINAL

    controls = result["hostile_controls"]
    assert controls["complete_cartesian_pairs_evaluated_each_fold"] is True
    assert controls["product_and_nested_pair_enumerations_identical"] is True
    assert controls["diagonal_only_pairing_never_used_as_authority"] is True
    assert controls["route_measurable_on_pre_acquisition_information"] is True
    assert controls["pre_post_timing_identity_exact"] is True
    assert controls["common_oracle_subtraction_preserves_pair_sign"] is True
    assert controls["shuffled_relative_labels_authorized"] is False
    assert controls["shuffled_relative_predictions_differ"] is True
    assert controls["one_out_of_fold_loss_per_instance_per_arm"] is True
    assert controls["same_marginals_different_joint_value"] == {
        "full_legal_pair_value": "0",
        "diagonal_only_value": "50",
        "preserved": True,
    }
    assert controls["acquisition_timing_reversal"] == {
        "pre_acquisition_value": "5",
        "post_acquisition_value": "10",
        "preserved": True,
    }

    custody_path = result_path.with_name("FIBERGUARD_CSPMZN_DIRECT_RELATIVE_R21_CUSTODY.json")
    custody = json.loads(custody_path.read_text(encoding="utf-8"))
    assert custody["terminal"] == TERMINAL
    assert custody["corrected_execution"]["result_sha256"] == sha256_bytes(raw)
    assert custody["corrected_execution"]["result_bytes"] == len(raw)
    assert custody["corrected_execution"]["byte_identical_complete_runs"] == 2
    executor_path = result_path.with_name("fiberguard_cspmzn_direct_relative_r21.py")
    protocol_path = result_path.with_name("FIBERGUARD_CSPMZN_DIRECT_RELATIVE_R21_PROTOCOL.md")
    assert custody["corrected_execution"]["executor_sha256"] == sha256_file(executor_path)
    assert custody["corrected_execution"]["protocol_sha256"] == sha256_file(protocol_path)

    tsp_failure = json.loads(
        result_path.with_name(
            "FIBERGUARD_TSP_DIRECT_RELATIVE_R21_PREREQUISITE_FAILURE.json"
        ).read_text(encoding="utf-8")
    )
    assert tsp_failure["terminal"] == "CANNOT_CHECK_TSP_DIRECT_RELATIVE_SOURCE_OR_RESOURCE"
    assert tsp_failure["authority"]["grants_round_2_scientific_adjudication"] is False
    assert tsp_failure["missing_cost_audit"]["affected_instance_step_cells"] == 21

    authority = result["authority"]
    assert authority["production_value"] is False
    assert authority["external_independent_replay"] is False
    assert authority["novelty_authority"] is False
    assert authority["journal_authority"] is False
    assert authority["submission_authorized"] is False
    assert authority["R11_R14_R15_R16_R18_R19_CNBR_CNBR2_BNSL_records_modified"] is False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--subject-repo", type=Path, required=True)
    args = parser.parse_args()
    verify_result(args.result, args.repo_root, args.subject_repo)
    print("ORION02_R21_CSPMZN_INDEPENDENT_VERIFICATION_PASS")
    print(TERMINAL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
