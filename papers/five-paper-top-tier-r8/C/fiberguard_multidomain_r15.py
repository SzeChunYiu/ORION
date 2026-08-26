#!/usr/bin/env python3
"""Prospective multi-domain FiberGuard tail/timeout transfer audit.

The scenario registry and objective are frozen before algorithm/feature outcome
files from the three R15 scenarios are read. Generic CV, quantization and
lexicographic empirical risk are donor mechanisms; this audit tests exact
same-oracle solver-decision value across three non-SAT ASlib domains.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.FiberGuard.MultiDomain.R15.v1"
TERMINAL = "FIBERGUARD_MULTIDOMAIN_R15_PASS"
SOURCE_PARENT = "002117dbf8a90bc1ef26ba0148e856fbc41fdc6d"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
FOLD_COUNT = 10
MIN_SUPPORT = 2
TAIL_FRACTION = 0.05

REGISTRY: dict[str, dict[str, str]] = {
    "ASP-POTASSCO": {
        "description.txt": "10cf3733c628eaa0dab60a3cef13a88dd639d72e",
        "algorithm_runs.arff": "3aacc83ac6b870b9ac52e209d9989c8161c18c17",
        "cv.arff": "2c62b456a455c9aedcb15beee0be045866463228",
        "feature_costs.arff": "f9e4a8ed429627361066d539cd50451b0ddc16af",
        "feature_runstatus.arff": "219bb090549bf2dbda82b385d3ff986b23b9d51f",
        "feature_values.arff": "77d7b3e06b7f5c1e718dbfa471f97abe7c98bb10",
    },
    "CSP-Minizinc-Time-2016": {
        "description.txt": "c4131c095682fe776d21fd05f001e96de66ffd1c",
        "algorithm_runs.arff": "96957f2e5010aad21dbb475dffd0a2d23f532d04",
        "cv.arff": "4372a490cc67eaa18641bfaf63539f0f1a529ce9",
        "feature_costs.arff": "8bcd8c6e2638648ce8dec369fedd980d0e418bad",
        "feature_runstatus.arff": "536f31d5c9120e92382d8dabffb8075c5f57f552",
        "feature_values.arff": "d48ea61ec21533dddd2a4f88fdd6da9e66eb1733",
    },
    "GRAPHS-2015": {
        "description.txt": "ee98eec74659ed5fe6e354e48b34f4ba9e26c52a",
        "algorithm_runs.arff": "69a3670c150366da4f04d280de9a936e9a0d017b",
        "cv.arff": "82aa8f02c47dce6b2e5908c72170533c27c855db",
        "feature_costs.arff": "5785e525f31f1094ddd707c435273e39e8336ee9",
        "feature_runstatus.arff": "d14b49e4d9ae01e4cce0f0084252af72cbc16b19",
        "feature_values.arff": "cda576a683a700ce25af0868fa9facb2d97f51a0",
    },
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def validate_registry(root: Path, scenario: str) -> dict[str, dict[str, Any]]:
    receipt: dict[str, dict[str, Any]] = {}
    for name, expected in REGISTRY[scenario].items():
        path = root / scenario / name
        observed = git_blob_sha(path)
        if observed != expected:
            raise ValueError(f"{scenario}/{name} blob mismatch: {observed} != {expected}")
        receipt[name] = {
            "git_blob_sha1": observed,
            "sha256": sha256_bytes(path.read_bytes()),
            "bytes": path.stat().st_size,
        }
    return receipt


def load_algorithm_runs_with_timeout(path: Path, cutoff: float, read_arff, median, most_common_status):
    attrs, rows = read_arff(path)
    required = ["instance_id", "repetition", "algorithm", "runtime", "runstatus"]
    index = {name: attrs.index(name) for name in required}
    grouped: dict[tuple[str, str], list[tuple[float, str]]] = collections.defaultdict(list)
    algorithms: set[str] = set()
    for row in rows:
        instance = row[index["instance_id"]]
        algorithm = row[index["algorithm"]]
        grouped[(instance, algorithm)].append(
            (float(row[index["runtime"]]), row[index["runstatus"]])
        )
        algorithms.add(algorithm)
    names = sorted(algorithms)
    runtimes: dict[str, dict[str, float]] = collections.defaultdict(dict)
    timeout: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    status_counts: collections.Counter[str] = collections.Counter()
    for (instance, algorithm), values in grouped.items():
        status = most_common_status(status for _, status in values)
        runtime = median([value for value, _ in values])
        status_counts[status] += 1
        timeout[instance][algorithm] = status != "ok"
        runtimes[instance][algorithm] = runtime if status == "ok" else 10.0 * cutoff
    incomplete = [
        instance for instance, row in runtimes.items() if set(row) != set(names)
    ]
    if incomplete:
        raise ValueError(f"incomplete algorithm matrix for {len(incomplete)} instances")
    return dict(runtimes), dict(timeout), names, dict(sorted(status_counts.items()))


def source_cv_folds(path: Path, instances: Sequence[str], read_arff) -> dict[str, int]:
    attrs, rows = read_arff(path)
    if attrs != ["instance_id", "repetition", "fold"]:
        raise ValueError(f"unexpected cv schema: {attrs}")
    result: dict[str, int] = {}
    for instance, repetition, fold in rows:
        if int(float(repetition)) != 1:
            continue
        fold_id = int(float(fold))
        if not 1 <= fold_id <= FOLD_COUNT:
            raise ValueError(f"invalid fold {fold_id}")
        if instance in result:
            raise ValueError(f"duplicate repetition-1 cv row: {instance}")
        result[instance] = fold_id
    if set(result) != set(instances):
        raise ValueError(
            f"repetition-1 cv coverage mismatch: {len(result)} != {len(instances)}"
        )
    return result


def balanced_hash_folds(instances: Sequence[str]) -> tuple[dict[str, int], dict[str, Any]]:
    ordered = sorted(instances, key=lambda name: (sha256_bytes(name.encode()), name))
    mapping = {name: index % FOLD_COUNT + 1 for index, name in enumerate(ordered)}
    loads = collections.Counter(mapping.values())
    return mapping, {
        "method": "SHA256(instance_id), then round-robin across ten folds",
        "fold_loads": [loads[index] for index in range(1, FOLD_COUNT + 1)],
        "assignment_sha256": sha256_bytes(canonical_json(mapping).encode()),
    }


def upper_tail_mean(values: Iterable[float], fraction: float = TAIL_FRACTION) -> float:
    ordered = sorted((float(value) for value in values), reverse=True)
    if not ordered:
        raise ValueError("empty tail")
    count = max(1, math.ceil(fraction * len(ordered)))
    return statistics.fmean(ordered[:count])


def policy_rows(
    members: Sequence[int],
    selected: tuple[int, ...],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
    acquisition: Sequence[float],
    regret: Sequence[Sequence[float]],
    timeout: Sequence[Sequence[bool]],
    algorithm_names: Sequence[str],
    policy: dict[str, Any],
    instance_names: Sequence[str],
    fold: int,
    arm: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for instance in members:
        key = tuple(atoms[instance][step] for step in selected)
        action = policy["actions"].get(key, policy["fallback_action"])
        used = key in policy["actions"]
        rows.append(
            {
                "instance": instance_names[instance],
                "fold": fold,
                "arm": arm,
                "steps": list(selected),
                "algorithm": algorithm_names[action],
                "feature_cost": acquisition[instance],
                "total_excess": acquisition[instance] + regret[instance][action],
                "selected_solver_timeout": timeout[instance][action],
                "signature_seen": key in policy["support"],
                "cell_policy_used": used,
                "training_cell_support": policy["support"].get(key, 0),
            }
        )
    return rows


def training_objective(rows: Sequence[dict[str, Any]], kind: str) -> tuple[Any, ...]:
    losses = [row["total_excess"] for row in rows]
    timeout_count = sum(bool(row["selected_solver_timeout"]) for row in rows)
    if kind == "robust":
        return (max(losses), statistics.fmean(losses))
    if kind == "catastrophe_tail":
        return (
            timeout_count,
            upper_tail_mean(losses),
            statistics.fmean(losses),
            max(losses),
        )
    raise ValueError(kind)


def select_policy(
    train: Sequence[int],
    candidates: Sequence[tuple[int, ...]],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
    step_cost: Sequence[Sequence[float]],
    regret: Sequence[Sequence[float]],
    timeout: Sequence[Sequence[bool]],
    algorithm_names: Sequence[str],
    fallback_action: int,
    instance_names: Sequence[str],
    fit_policy,
    acquisition_vector,
    kind: str,
) -> tuple[tuple[int, ...], dict[str, Any], list[float], tuple[Any, ...]]:
    best: tuple[tuple[Any, ...], tuple[int, ...], dict[str, Any], list[float]] | None = None
    for selected in candidates:
        acquisition = acquisition_vector(selected, step_cost)
        policy = fit_policy(
            train,
            selected,
            atoms,
            acquisition,
            regret,
            algorithm_names,
            fallback_action,
            MIN_SUPPORT,
        )
        rows = policy_rows(
            train,
            selected,
            atoms,
            acquisition,
            regret,
            timeout,
            algorithm_names,
            policy,
            instance_names,
            0,
            "training",
        )
        objective = training_objective(rows, kind)
        key = (*objective, len(selected), selected)
        candidate = (key, selected, policy, acquisition)
        if best is None or candidate[0] < best[0]:
            best = candidate
    assert best is not None
    objective_len = 2 if kind == "robust" else 4
    return best[1], best[2], best[3], best[0][:objective_len]


def summarize(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    losses = sorted(float(row["total_excess"]) for row in rows)
    p95 = losses[min(len(losses) - 1, math.ceil(0.95 * len(losses)) - 1)]
    timeouts = sum(bool(row["selected_solver_timeout"]) for row in rows)
    return {
        "instance_count": len(rows),
        "selected_solver_timeout_count": timeouts,
        "selected_solver_timeout_rate": timeouts / len(rows),
        "robust_total_excess": max(losses),
        "worst_5_percent_mean_total_excess": upper_tail_mean(losses),
        "mean_total_excess": statistics.fmean(losses),
        "median_total_excess": statistics.median(losses),
        "p95_total_excess": p95,
        "mean_feature_cost": statistics.fmean(float(row["feature_cost"]) for row in rows),
        "maximum_feature_cost": max(float(row["feature_cost"]) for row in rows),
        "signature_seen_rate": sum(bool(row["signature_seen"]) for row in rows) / len(rows),
        "cell_policy_used_rate": sum(bool(row["cell_policy_used"]) for row in rows) / len(rows),
        "fallback_count": sum(not bool(row["cell_policy_used"]) for row in rows),
    }


def gate(primary: dict[str, Any], coarse: dict[str, Any], full: dict[str, Any]) -> dict[str, bool]:
    return {
        "timeout_rate_not_worse_than_both_extremes": primary["selected_solver_timeout_rate"]
        <= min(coarse["selected_solver_timeout_rate"], full["selected_solver_timeout_rate"]),
        "worst_5_percent_mean_strictly_better_than_both_extremes": primary[
            "worst_5_percent_mean_total_excess"
        ] < min(
            coarse["worst_5_percent_mean_total_excess"],
            full["worst_5_percent_mean_total_excess"],
        ),
        "mean_strictly_better_than_both_extremes": primary["mean_total_excess"]
        < min(coarse["mean_total_excess"], full["mean_total_excess"]),
    }


def run_split(
    split_name: str,
    folds: dict[str, int],
    instance_names: Sequence[str],
    steps: Sequence[str],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
    step_cost: Sequence[Sequence[float]],
    regret: Sequence[Sequence[float]],
    timeout: Sequence[Sequence[bool]],
    algorithm_names: Sequence[str],
    candidates: Sequence[tuple[int, ...]],
    build_step_atoms,
    acquisition_vector,
    fit_policy,
    robust_action,
) -> dict[str, Any]:
    all_indices = tuple(range(len(instance_names)))
    full = tuple(range(len(steps)))
    predictions: list[dict[str, Any]] = []
    fold_receipts: list[dict[str, Any]] = []
    for fold in range(1, FOLD_COUNT + 1):
        test = tuple(index for index, name in enumerate(instance_names) if folds[name] == fold)
        test_set = set(test)
        train = tuple(index for index in all_indices if index not in test_set)
        if not train or not test:
            raise ValueError(f"empty {split_name} fold {fold}")
        zero = [0.0] * len(instance_names)
        fallback, fallback_value = robust_action(train, zero, regret, algorithm_names)
        atoms, thresholds = build_step_atoms(
            all_indices,
            train,
            instance_names,
            steps,
            feature_steps,
            feature_values,
            feature_status,
            "quartile",
        )

        chosen: dict[str, tuple[tuple[int, ...], dict[str, Any], list[float], tuple[Any, ...]]] = {}
        for name, selected in (("no_features", ()), ("all_features", full)):
            acquisition = acquisition_vector(selected, step_cost)
            policy = fit_policy(
                train,
                selected,
                atoms,
                acquisition,
                regret,
                algorithm_names,
                fallback,
                MIN_SUPPORT,
            )
            train_rows = policy_rows(
                train, selected, atoms, acquisition, regret, timeout,
                algorithm_names, policy, instance_names, 0, "training"
            )
            chosen[name] = (
                selected,
                policy,
                acquisition,
                training_objective(train_rows, "catastrophe_tail"),
            )

        for kind, arm in (
            ("robust", "robust_selected"),
            ("catastrophe_tail", "catastrophe_tail_selected"),
        ):
            chosen[arm] = select_policy(
                train, candidates, atoms, step_cost, regret, timeout,
                algorithm_names, fallback, instance_names, fit_policy,
                acquisition_vector, kind
            )

        arm_receipts: dict[str, Any] = {}
        for arm, (selected, policy, acquisition, objective) in chosen.items():
            predictions.extend(
                policy_rows(
                    test, selected, atoms, acquisition, regret, timeout,
                    algorithm_names, policy, instance_names, fold, arm
                )
            )
            arm_receipts[arm] = {
                "steps": [steps[index] for index in selected],
                "training_objective": list(objective),
                "policy_sha256": policy["policy_sha256"],
                "training_fibre_count": policy["fibre_count"],
                "training_eligible_fibre_count": policy["eligible_fibre_count"],
            }
        fold_receipts.append(
            {
                "fold": fold,
                "train_count": len(train),
                "test_count": len(test),
                "fallback_algorithm": algorithm_names[fallback],
                "fallback_training_robust_regret": fallback_value,
                "quartile_threshold_sha256": sha256_bytes(canonical_json(thresholds).encode()),
                "arms": arm_receipts,
            }
        )

    by_arm: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in predictions:
        by_arm[row["arm"]].append(row)
    summaries = {arm: summarize(rows) for arm, rows in sorted(by_arm.items())}
    primary_gate = gate(
        summaries["catastrophe_tail_selected"],
        summaries["no_features"],
        summaries["all_features"],
    )
    return {
        "split": split_name,
        "fold_count": FOLD_COUNT,
        "fold_receipts": fold_receipts,
        "arms": summaries,
        "primary_gate": primary_gate,
        "primary_gate_passed": all(primary_gate.values()),
        "prediction_sha256": sha256_bytes(canonical_json(predictions).encode()),
        "predictions": predictions,
    }


def load_scenario(root: Path, scenario: str):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import yaml
    from fiberguard_aslib_sat12_all_r11 import (
        dependency_closure,
        enumerate_dependency_closed_sets,
        feature_cost,
        load_feature_values,
        load_step_table,
        median,
        most_common_status,
        read_arff,
    )
    from fiberguard_aslib_transfer_r14 import (
        acquisition_vector,
        build_step_atoms,
        fit_policy,
        robust_action,
    )

    receipt = validate_registry(root, scenario)
    scenario_root = root / scenario
    description = yaml.safe_load((scenario_root / "description.txt").read_text())
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time", cutoff)
    feature_cutoff = cutoff if feature_cutoff_raw in {None, "?"} else float(feature_cutoff_raw)
    feature_steps = dict(description["feature_steps"])
    steps = sorted(feature_steps)

    runtime_dict, timeout_dict, algorithm_names, status_counts = load_algorithm_runs_with_timeout(
        scenario_root / "algorithm_runs.arff", cutoff, read_arff, median, most_common_status
    )
    feature_values, feature_names = load_feature_values(scenario_root / "feature_values.arff")
    feature_costs, cost_steps = load_step_table(scenario_root / "feature_costs.arff", numeric=True)
    feature_status, status_steps = load_step_table(
        scenario_root / "feature_runstatus.arff", numeric=False
    )
    if set(cost_steps) != set(steps) or set(status_steps) != set(steps):
        raise ValueError(f"{scenario} step mismatch")
    instance_names = sorted(runtime_dict)
    if set(instance_names) != set(feature_values) or set(instance_names) != set(feature_costs):
        raise ValueError(f"{scenario} instance mismatch")

    runtimes = [
        [runtime_dict[name][algorithm] for algorithm in algorithm_names]
        for name in instance_names
    ]
    timeout = [
        [timeout_dict[name][algorithm] for algorithm in algorithm_names]
        for name in instance_names
    ]
    oracle = [min(row) for row in runtimes]
    regret = [
        [runtime - oracle[index] for runtime in row]
        for index, row in enumerate(runtimes)
    ]
    step_cost = [
        [
            feature_cost(
                name, (step,), feature_costs, feature_status, feature_cutoff
            )
            for step in steps
        ]
        for name in instance_names
    ]
    named_candidates = enumerate_dependency_closed_sets(steps, feature_steps)
    step_index = {step: index for index, step in enumerate(steps)}
    candidates = [tuple(step_index[step] for step in selected) for selected in named_candidates]
    if not all(
        tuple(sorted(dependency_closure(selected, feature_steps))) == tuple(sorted(selected))
        for selected in named_candidates
    ):
        raise AssertionError("dependency closure failure")
    source_folds = source_cv_folds(scenario_root / "cv.arff", instance_names, read_arff)
    hash_folds, hash_receipt = balanced_hash_folds(instance_names)
    return {
        "scenario": scenario,
        "receipt": receipt,
        "cutoff": cutoff,
        "feature_cutoff": feature_cutoff,
        "feature_steps": feature_steps,
        "steps": steps,
        "feature_values": feature_values,
        "feature_status": feature_status,
        "instance_names": instance_names,
        "algorithm_names": algorithm_names,
        "feature_names": feature_names,
        "status_counts": status_counts,
        "step_cost": step_cost,
        "regret": regret,
        "timeout": timeout,
        "candidates": candidates,
        "source_folds": source_folds,
        "hash_folds": hash_folds,
        "hash_receipt": hash_receipt,
        "helpers": (build_step_atoms, acquisition_vector, fit_policy, robust_action),
    }


def run(root: Path) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    domain_passes = 0
    for scenario in REGISTRY:
        data = load_scenario(root, scenario)
        helpers = data.pop("helpers")
        build_step_atoms, acquisition_vector, fit_policy, robust_action = helpers
        common = (
            data["instance_names"], data["steps"], data["feature_steps"],
            data["feature_values"], data["feature_status"], data["step_cost"],
            data["regret"], data["timeout"], data["algorithm_names"],
            data["candidates"], build_step_atoms, acquisition_vector,
            fit_policy, robust_action,
        )
        splits = [
            run_split("source_cv_repetition1", data["source_folds"], *common),
            run_split("balanced_hash", data["hash_folds"], *common),
        ]
        scenario_pass = all(split["primary_gate_passed"] for split in splits)
        domain_passes += int(scenario_pass)
        scenarios.append(
            {
                "scenario": scenario,
                "upstream_files": data["receipt"],
                "corpus": {
                    "instance_count": len(data["instance_names"]),
                    "algorithm_count": len(data["algorithm_names"]),
                    "feature_count": len(data["feature_names"]),
                    "feature_step_count": len(data["steps"]),
                    "feature_steps": data["steps"],
                    "candidate_representation_count": len(data["candidates"]),
                    "algorithm_status_counts": data["status_counts"],
                    "algorithm_cutoff": data["cutoff"],
                    "feature_cutoff_fallback": data["feature_cutoff"],
                    "hash_split_receipt": data["hash_receipt"],
                },
                "splits": splits,
                "scenario_primary_gate_passed": scenario_pass,
            }
        )

    scientific_terminal = {
        3: "C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_ALL_THREE",
        2: "C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_TWO_OF_THREE",
        1: "C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_ONE_OF_THREE",
        0: "C_MULTIDOMAIN_CATASTROPHE_TAIL_VALUE_NONE",
    }[domain_passes]
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "scientific_terminal": scientific_terminal,
        "source_parent": SOURCE_PARENT,
        "upstream": {
            "repository": "https://github.com/coseal/aslib_data.git",
            "commit": ASLIB_COMMIT,
            "scenario_registry": list(REGISTRY),
        },
        "protocol": {
            "source_cv_repetition": 1,
            "outcome_blind_control_split": "balanced SHA256(instance_id) round-robin",
            "quantization": "outer-training nearest-rank quartiles; missingness/status explicit",
            "minimum_training_cell_support": MIN_SUPPORT,
            "fallback": "outer-training no-feature robust action",
            "tail_fraction": TAIL_FRACTION,
            "tail_statistic": "mean of worst ceil(0.05*n) total-excess rows",
            "primary_training_objective": [
                "selected-solver timeout count",
                "worst-5%-mean total excess",
                "mean total excess",
                "robust total excess",
                "number of feature steps",
                "lexical step tuple",
            ],
            "primary_gate": "timeout rate no worse and both worst-5%-mean and mean strictly better than no-features and all-features on both splits",
            "same_oracle_baseline": "statewise virtual-best solver PAR10 runtime with zero feature cost",
        },
        "scenarios": scenarios,
        "portfolio": {
            "scenario_pass_count": domain_passes,
            "scenario_count": len(scenarios),
        },
        "controls": {
            "registry_fixed_before_outcome": True,
            "all_scenarios_non_SAT": True,
            "all_blob_bindings_verified": True,
            "all_splits_cover_every_instance_once_per_arm": all(
                all(
                    all(arm["instance_count"] == scenario["corpus"]["instance_count"] for arm in split["arms"].values())
                    for split in scenario["splits"]
                )
                for scenario in scenarios
            ),
        },
        "authority": {
            "multi_domain_out_of_fold_finite_evidence": True,
            "domain_registry_chosen_before_outcomes": True,
            "hash_split_is_family_ground_truth": False,
            "tail_statistic_is_distribution_free_bound": False,
            "learned_selector_claim": False,
            "external_replay": False,
            "production_value": False,
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def self_test() -> dict[str, bool]:
    folds, receipt = balanced_hash_folds([f"x{i}" for i in range(23)])
    assert sorted(collections.Counter(folds.values()).values()) == [2] * 7 + [3] * 3
    assert receipt["fold_loads"] == [3, 3, 3, 2, 2, 2, 2, 2, 2, 2]
    assert upper_tail_mean(range(1, 21)) == 20
    assert upper_tail_mean(range(1, 21), 0.1) == 19.5
    primary = {
        "selected_solver_timeout_rate": 0.1,
        "worst_5_percent_mean_total_excess": 5,
        "mean_total_excess": 2,
    }
    coarse = {
        "selected_solver_timeout_rate": 0.2,
        "worst_5_percent_mean_total_excess": 6,
        "mean_total_excess": 3,
    }
    full = {
        "selected_solver_timeout_rate": 0.1,
        "worst_5_percent_mean_total_excess": 7,
        "mean_total_excess": 4,
    }
    assert all(gate(primary, coarse, full).values())
    return {
        "balanced_hash_split": True,
        "upper_tail_mean": True,
        "lexicographic_gate": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(canonical_json(self_test()))
        return 0
    if args.aslib_root is None or args.output is None:
        parser.error("--aslib-root and --output are required")
    result = run(args.aslib_root)
    payload = canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(
        TERMINAL,
        f"scientific_terminal={result['scientific_terminal']}",
        f"scenario_passes={result['portfolio']['scenario_pass_count']}/{result['portfolio']['scenario_count']}",
        f"sha256={sha256_bytes(payload.encode())}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
