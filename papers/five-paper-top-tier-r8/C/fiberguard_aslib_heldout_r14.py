#!/usr/bin/env python3
"""Prospectively frozen held-out FiberGuard transfer audit for SAT12-ALL."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any, Iterable

import numpy as np
import yaml

import fiberguard_aslib_sat12_all_r11 as r11

SCHEMA = "ORION.FiberGuard.ASlibHeldout.R14.v1"
TERMINAL_PREFIX = "FIBERGUARD_ASLIB_HELDOUT_R14"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SCENARIO = "SAT12-ALL"
CV_BLOB = "63d3922abaae67e690f31a74c7daa1be6981fb70"
STATUS_LEVELS = ("ok", "presolved", "timeout", "memout", "crash", "other")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def percentile_higher(values: np.ndarray, probability: float) -> float:
    ordered = np.sort(np.asarray(values, dtype=float))
    index = min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1)
    return float(ordered[index])


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol["schema"] != "ORION.FiberGuard.ASlibHeldout.Protocol.R14.v1":
        raise ValueError("unexpected protocol schema")
    if protocol["parent_commit"] != "6c23a3fe4ccf415bc3a73794878d72583ed48eb2":
        raise ValueError("unexpected protocol parent")
    upstream = protocol["upstream"]
    if upstream["commit"] != ASLIB_COMMIT or upstream["scenario"] != SCENARIO:
        raise ValueError("unexpected upstream subject")
    if upstream["files"]["cv.arff"] != CV_BLOB:
        raise ValueError("unexpected cv blob")
    if protocol["official_cv"]["repetition"] != 1:
        raise ValueError("only prospectively frozen repetition 1 is admissible")
    if protocol["family_split"]["folds"] != 5:
        raise ValueError("only prospectively frozen five-fold family split is admissible")
    if protocol["frozen_control_steps"] != ["Pre", "lobjois"]:
        raise ValueError("frozen R11 representation control drift")
    if protocol["knn_baseline"]["k"] != 16:
        raise ValueError("kNN hyperparameter drift")


def validate_cv_blob(path: Path) -> dict[str, Any]:
    actual = r11.git_blob_sha(path)
    if actual != CV_BLOB:
        raise ValueError(f"cv blob mismatch: {actual} != {CV_BLOB}")
    return {
        "git_blob_sha1": actual,
        "sha256": r11.sha256_file(path),
        "bytes": path.stat().st_size,
    }


def load_official_cv(path: Path, instances: list[str], repetition: int) -> dict[str, int]:
    attrs, rows = r11.read_arff(path)
    required = ["instance_id", "repetition", "fold"]
    index = {name: attrs.index(name) for name in required}
    allowed = set(instances)
    assignment: dict[str, int] = {}
    for row in rows:
        if int(float(row[index["repetition"]])) != repetition:
            continue
        instance = row[index["instance_id"]]
        if instance not in allowed:
            continue
        fold = int(float(row[index["fold"]]))
        if instance in assignment:
            raise ValueError(f"duplicate CV assignment for {instance}")
        assignment[instance] = fold
    if set(assignment) != allowed:
        raise ValueError(f"official CV misses {len(allowed - set(assignment))} instances")
    folds = sorted(set(assignment.values()))
    if folds != list(range(1, 11)):
        raise ValueError(f"unexpected official folds: {folds}")
    return assignment


def family_key(instance: str) -> str:
    parts = [part for part in instance.split("/") if part]
    return "/".join(parts[:3]) if len(parts) >= 3 else "/".join(parts)


def balanced_family_assignment(instances: list[str], fold_count: int) -> tuple[dict[str, int], dict[str, Any]]:
    groups: dict[str, list[str]] = collections.defaultdict(list)
    for instance in instances:
        groups[family_key(instance)].append(instance)
    ordered = sorted(
        groups.items(),
        key=lambda item: (
            -len(item[1]),
            hashlib.sha256(item[0].encode()).hexdigest(),
            item[0],
        ),
    )
    fold_sizes = [0] * fold_count
    fold_families: list[list[str]] = [[] for _ in range(fold_count)]
    assignment: dict[str, int] = {}
    for family, members in ordered:
        fold = min(range(fold_count), key=lambda value: (fold_sizes[value], value))
        fold_sizes[fold] += len(members)
        fold_families[fold].append(family)
        for instance in members:
            assignment[instance] = fold + 1
    return assignment, {
        "family_count": len(groups),
        "largest_family": max(map(len, groups.values())),
        "fold_instance_counts": fold_sizes,
        "fold_family_counts": [len(row) for row in fold_families],
        "zero_family_overlap": len({family for rows in fold_families for family in rows}) == len(groups),
    }


def make_signature_ids(
    selected: tuple[str, ...],
    instances: list[str],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
) -> np.ndarray:
    ids: dict[tuple[Any, ...], int] = {}
    output = np.empty(len(instances), dtype=np.int32)
    for index, instance in enumerate(instances):
        signature = r11.step_signature(
            instance, selected, feature_steps, feature_values, feature_status
        )
        output[index] = ids.setdefault(signature, len(ids))
    return output


def make_acquisition(
    selected: tuple[str, ...],
    instances: list[str],
    feature_costs: dict[str, dict[str, float | str]],
    feature_status: dict[str, dict[str, float | str]],
    feature_cutoff: float,
) -> np.ndarray:
    return np.asarray(
        [
            r11.feature_cost(
                instance, selected, feature_costs, feature_status, feature_cutoff
            )
            for instance in instances
        ],
        dtype=float,
    )


def fit_exact_policy(
    group_ids: np.ndarray,
    acquisition: np.ndarray,
    regret: np.ndarray,
    train: np.ndarray,
) -> dict[str, Any]:
    group_count = int(group_ids.max()) + 1
    maxima = np.full((group_count, regret.shape[1]), -np.inf, dtype=float)
    train_loss = acquisition[train, None] + regret[train]
    np.maximum.at(maxima, group_ids[train], train_loss)
    active = np.isfinite(maxima[:, 0])
    solver_by_group = np.zeros(group_count, dtype=np.int32)
    solver_by_group[active] = np.argmin(maxima[active], axis=1)
    group_values = np.min(maxima[active], axis=1)
    train_solvers = solver_by_group[group_ids[train]]
    realized = acquisition[train] + regret[train, train_solvers]
    fallback = int(np.argmin(np.max(regret[train], axis=0)))
    return {
        "active": active,
        "solver_by_group": solver_by_group,
        "fallback": fallback,
        "train_robust": float(np.max(group_values)),
        "train_mean": float(np.mean(realized)),
    }


def deploy_exact_policy(
    fit: dict[str, Any],
    group_ids: np.ndarray,
    acquisition: np.ndarray,
    regret: np.ndarray,
    runtimes: np.ndarray,
    test: np.ndarray,
) -> dict[str, np.ndarray]:
    groups = group_ids[test]
    seen = fit["active"][groups]
    solvers = np.full(len(test), fit["fallback"], dtype=np.int32)
    solvers[seen] = fit["solver_by_group"][groups[seen]]
    return {
        "loss": acquisition[test] + regret[test, solvers],
        "runtime": runtimes[test, solvers],
        "feature_cost": acquisition[test],
        "seen": seen.astype(bool),
    }


def select_training_representation(
    representations: list[tuple[str, ...]],
    cache: dict[tuple[str, ...], tuple[np.ndarray, np.ndarray]],
    regret: np.ndarray,
    train: np.ndarray,
) -> tuple[tuple[str, ...], dict[str, Any]]:
    best_steps: tuple[str, ...] | None = None
    best_fit: dict[str, Any] | None = None
    best_key: tuple[Any, ...] | None = None
    for selected in representations:
        group_ids, acquisition = cache[selected]
        fit = fit_exact_policy(group_ids, acquisition, regret, train)
        key = (fit["train_robust"], fit["train_mean"], len(selected), selected)
        if best_key is None or key < best_key:
            best_key = key
            best_steps = selected
            best_fit = fit
    assert best_steps is not None and best_fit is not None
    return best_steps, best_fit


def feature_matrix(
    selected: tuple[str, ...],
    instances: list[str],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
) -> tuple[np.ndarray, np.ndarray]:
    names: list[str] = []
    for step in selected:
        provides = feature_steps.get(step, {}).get("provides", []) or []
        if isinstance(provides, str):
            provides = [provides]
        names.extend(provides)
    numeric = np.full((len(instances), len(names)), np.nan, dtype=float)
    for row, instance in enumerate(instances):
        for column, name in enumerate(names):
            value = feature_values.get(instance, {}).get(name, "?")
            if value != "?":
                numeric[row, column] = float(value)
    statuses = np.zeros((len(instances), len(selected) * len(STATUS_LEVELS)), dtype=float)
    status_index = {name: index for index, name in enumerate(STATUS_LEVELS)}
    for row, instance in enumerate(instances):
        for step_index, step in enumerate(selected):
            value = str(feature_status.get(instance, {}).get(step, "other"))
            value = value if value in status_index else "other"
            statuses[row, step_index * len(STATUS_LEVELS) + status_index[value]] = 1.0
    return numeric, statuses


def transform_for_knn(
    numeric: np.ndarray,
    statuses: np.ndarray,
    train: np.ndarray,
    test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    train_numeric = numeric[train].copy()
    test_numeric = numeric[test].copy()
    missing_train = np.isnan(train_numeric).astype(float)
    missing_test = np.isnan(test_numeric).astype(float)
    if train_numeric.shape[1]:
        medians = np.nanmedian(train_numeric, axis=0)
        medians = np.where(np.isfinite(medians), medians, 0.0)
        train_numeric = np.where(np.isnan(train_numeric), medians, train_numeric)
        test_numeric = np.where(np.isnan(test_numeric), medians, test_numeric)
        means = np.mean(train_numeric, axis=0)
        scales = np.std(train_numeric, axis=0)
        scales = np.where(scales > 0, scales, 1.0)
        train_numeric = (train_numeric - means) / scales
        test_numeric = (test_numeric - means) / scales
    train_matrix = np.concatenate((train_numeric, missing_train, statuses[train]), axis=1)
    test_matrix = np.concatenate((test_numeric, missing_test, statuses[test]), axis=1)
    return train_matrix, test_matrix


def knn_policy(
    numeric: np.ndarray,
    statuses: np.ndarray,
    acquisition: np.ndarray,
    regret: np.ndarray,
    runtimes: np.ndarray,
    train: np.ndarray,
    test: np.ndarray,
    k: int,
) -> dict[str, np.ndarray]:
    train_matrix, test_matrix = transform_for_knn(numeric, statuses, train, test)
    selected_solvers: list[np.ndarray] = []
    k_eff = min(k, len(train))
    batch_size = 64
    for start in range(0, len(test), batch_size):
        batch = test_matrix[start : start + batch_size]
        distances = np.sum((batch[:, None, :] - train_matrix[None, :, :]) ** 2, axis=2)
        neighbors = np.argsort(distances, axis=1, kind="stable")[:, :k_eff]
        predicted = np.mean(regret[train][neighbors], axis=1)
        selected_solvers.append(np.argmin(predicted, axis=1).astype(np.int32))
    solvers = np.concatenate(selected_solvers)
    return {
        "loss": acquisition[test] + regret[test, solvers],
        "runtime": runtimes[test, solvers],
        "feature_cost": acquisition[test],
        "seen": np.ones(len(test), dtype=bool),
    }


def summarize_arm(
    loss: np.ndarray,
    runtime: np.ndarray,
    feature_cost: np.ndarray,
    seen: np.ndarray,
    oracle: np.ndarray,
    par10: float,
) -> dict[str, Any]:
    catastrophic = (runtime >= par10 - 1e-9) & (oracle < par10 - 1e-9)
    return {
        "mean_total_excess": float(np.mean(loss)),
        "median_total_excess": float(np.median(loss)),
        "p95_total_excess": percentile_higher(loss, 0.95),
        "maximum_total_excess": float(np.max(loss)),
        "mean_feature_cost": float(np.mean(feature_cost)),
        "maximum_feature_cost": float(np.max(feature_cost)),
        "catastrophic_wrong_action_count": int(np.sum(catastrophic)),
        "catastrophic_wrong_action_rate": float(np.mean(catastrophic)),
        "exact_signature_seen_count": int(np.sum(seen)),
        "exact_signature_seen_coverage": float(np.mean(seen)),
    }


def strong_panel_gate(summary: dict[str, dict[str, Any]]) -> bool:
    primary = summary["training_selected_exact"]
    comparators = (
        summary["no_feature_robust"],
        summary["all_features_exact"],
        summary["knn_frozen_representation"],
    )
    return (
        all(primary["mean_total_excess"] < row["mean_total_excess"] - 1e-12 for row in comparators)
        and all(primary["p95_total_excess"] <= row["p95_total_excess"] + 1e-12 for row in comparators)
        and primary["maximum_total_excess"] <= summary["no_feature_robust"]["maximum_total_excess"] + 1e-12
        and primary["catastrophic_wrong_action_rate"] <= summary["no_feature_robust"]["catastrophic_wrong_action_rate"] + 1e-12
    )


def evaluate_panel(
    name: str,
    assignment: dict[str, int],
    instances: list[str],
    algorithms: list[str],
    representations: list[tuple[str, ...]],
    cache: dict[tuple[str, ...], tuple[np.ndarray, np.ndarray]],
    frozen_steps: tuple[str, ...],
    full_steps: tuple[str, ...],
    regret: np.ndarray,
    runtimes: np.ndarray,
    oracle: np.ndarray,
    numeric_frozen: np.ndarray,
    status_frozen: np.ndarray,
    k: int,
    par10: float,
) -> dict[str, Any]:
    fold_values = sorted(set(assignment.values()))
    fold_array = np.asarray([assignment[instance] for instance in instances], dtype=np.int32)
    arms = (
        "single_best_solver",
        "no_feature_robust",
        "all_features_exact",
        "frozen_representation_exact",
        "training_selected_exact",
        "knn_frozen_representation",
    )
    accumulated: dict[str, dict[str, np.ndarray]] = {
        arm: {
            "loss": np.full(len(instances), np.nan),
            "runtime": np.full(len(instances), np.nan),
            "feature_cost": np.full(len(instances), np.nan),
            "seen": np.zeros(len(instances), dtype=bool),
        }
        for arm in arms
    }
    selected_counter: collections.Counter[tuple[str, ...]] = collections.Counter()
    fold_rows: list[dict[str, Any]] = []

    for fold in fold_values:
        test = np.flatnonzero(fold_array == fold)
        train = np.flatnonzero(fold_array != fold)
        if not len(test) or not len(train):
            raise ValueError(f"empty train/test split in {name} fold {fold}")

        sbs = int(np.argmin(np.mean(runtimes[train], axis=0)))
        sbs_output = {
            "loss": regret[test, sbs],
            "runtime": runtimes[test, sbs],
            "feature_cost": np.zeros(len(test)),
            "seen": np.ones(len(test), dtype=bool),
        }

        no_steps: tuple[str, ...] = ()
        no_fit = fit_exact_policy(*cache[no_steps], regret, train)
        no_output = deploy_exact_policy(no_fit, *cache[no_steps], regret, runtimes, test)

        full_fit = fit_exact_policy(*cache[full_steps], regret, train)
        full_output = deploy_exact_policy(full_fit, *cache[full_steps], regret, runtimes, test)

        frozen_fit = fit_exact_policy(*cache[frozen_steps], regret, train)
        frozen_output = deploy_exact_policy(frozen_fit, *cache[frozen_steps], regret, runtimes, test)

        selected_steps, selected_fit = select_training_representation(
            representations, cache, regret, train
        )
        selected_counter[selected_steps] += 1
        selected_output = deploy_exact_policy(
            selected_fit, *cache[selected_steps], regret, runtimes, test
        )

        knn_output = knn_policy(
            numeric_frozen,
            status_frozen,
            cache[frozen_steps][1],
            regret,
            runtimes,
            train,
            test,
            k,
        )

        outputs = {
            "single_best_solver": sbs_output,
            "no_feature_robust": no_output,
            "all_features_exact": full_output,
            "frozen_representation_exact": frozen_output,
            "training_selected_exact": selected_output,
            "knn_frozen_representation": knn_output,
        }
        for arm, output in outputs.items():
            for key in ("loss", "runtime", "feature_cost", "seen"):
                accumulated[arm][key][test] = output[key]

        fold_rows.append(
            {
                "fold": int(fold),
                "train_count": len(train),
                "test_count": len(test),
                "training_selected_steps": list(selected_steps),
                "training_selected_train_robust": selected_fit["train_robust"],
                "training_selected_train_mean": selected_fit["train_mean"],
                "training_selected_test_mean": float(np.mean(selected_output["loss"])),
                "training_selected_test_maximum": float(np.max(selected_output["loss"])),
                "training_selected_seen_coverage": float(np.mean(selected_output["seen"])),
            }
        )

    summary: dict[str, dict[str, Any]] = {}
    for arm in arms:
        row = accumulated[arm]
        if np.isnan(row["loss"]).any():
            raise AssertionError(f"panel {name} arm {arm} did not predict every instance")
        summary[arm] = summarize_arm(
            row["loss"], row["runtime"], row["feature_cost"], row["seen"], oracle, par10
        )
    return {
        "name": name,
        "fold_count": len(fold_values),
        "instance_count": len(instances),
        "arms": summary,
        "training_selected_representation_histogram": [
            {"steps": list(steps), "fold_count": count}
            for steps, count in sorted(selected_counter.items(), key=lambda item: (-item[1], item[0]))
        ],
        "folds": fold_rows,
        "strong_transfer_gate": strong_panel_gate(summary),
    }


def run(root: Path, protocol_path: Path, protocol_commit: str) -> dict[str, Any]:
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    validate_protocol(protocol)

    upstream = r11.validate_upstream(root)
    scenario_root = root / SCENARIO
    cv_audit = validate_cv_blob(scenario_root / "cv.arff")
    description = yaml.safe_load((scenario_root / "description.txt").read_text())
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time", cutoff)
    feature_cutoff = cutoff if feature_cutoff_raw in {None, "?"} else float(feature_cutoff_raw)
    feature_steps = dict(description["feature_steps"])
    steps = sorted(feature_steps)

    runtimes_by_instance, algorithms, algorithm_audit = r11.load_algorithm_runs(
        scenario_root / "algorithm_runs.arff", cutoff
    )
    feature_values, feature_names = r11.load_feature_values(scenario_root / "feature_values.arff")
    feature_costs, cost_steps = r11.load_step_table(scenario_root / "feature_costs.arff", numeric=True)
    feature_status, status_steps = r11.load_step_table(
        scenario_root / "feature_runstatus.arff", numeric=False
    )
    if set(cost_steps) != set(steps) or set(status_steps) != set(steps):
        raise ValueError("feature step mismatch")

    instances = sorted(set(runtimes_by_instance) & set(feature_values) & set(feature_costs))
    if set(instances) != set(runtimes_by_instance):
        raise ValueError("feature data does not cover the complete solver matrix")
    runtimes = np.asarray(
        [[runtimes_by_instance[instance][algorithm] for algorithm in algorithms] for instance in instances],
        dtype=float,
    )
    oracle = np.min(runtimes, axis=1)
    regret = runtimes - oracle[:, None]

    representations = r11.enumerate_dependency_closed_sets(steps, feature_steps)
    frozen_steps = r11.dependency_closure(protocol["frozen_control_steps"], feature_steps)
    full_steps = r11.dependency_closure(steps, feature_steps)
    if frozen_steps != ("Pre", "lobjois"):
        raise ValueError(f"frozen representation closure drift: {frozen_steps}")

    cache: dict[tuple[str, ...], tuple[np.ndarray, np.ndarray]] = {}
    for selected in representations:
        cache[selected] = (
            make_signature_ids(
                selected, instances, feature_steps, feature_values, feature_status
            ),
            make_acquisition(
                selected, instances, feature_costs, feature_status, feature_cutoff
            ),
        )

    numeric_frozen, status_frozen = feature_matrix(
        frozen_steps, instances, feature_steps, feature_values, feature_status
    )

    official_assignment = load_official_cv(
        scenario_root / "cv.arff", instances, protocol["official_cv"]["repetition"]
    )
    family_assignment, family_audit = balanced_family_assignment(
        instances, protocol["family_split"]["folds"]
    )

    official = evaluate_panel(
        "official_cv_repetition_1",
        official_assignment,
        instances,
        algorithms,
        representations,
        cache,
        frozen_steps,
        full_steps,
        regret,
        runtimes,
        oracle,
        numeric_frozen,
        status_frozen,
        protocol["knn_baseline"]["k"],
        10.0 * cutoff,
    )
    family = evaluate_panel(
        "balanced_leave_source_family_out",
        family_assignment,
        instances,
        algorithms,
        representations,
        cache,
        frozen_steps,
        full_steps,
        regret,
        runtimes,
        oracle,
        numeric_frozen,
        status_frozen,
        protocol["knn_baseline"]["k"],
        10.0 * cutoff,
    )

    if official["strong_transfer_gate"] and family["strong_transfer_gate"]:
        terminal = f"{TERMINAL_PREFIX}_PASS_BOTH_OFFICIAL_AND_FAMILY"
    elif official["strong_transfer_gate"]:
        terminal = f"{TERMINAL_PREFIX}_OFFICIAL_ONLY__FAMILY_SHIFT_FAIL"
    else:
        primary = official["arms"]["training_selected_exact"]
        no_feature = official["arms"]["no_feature_robust"]
        if primary["mean_total_excess"] < no_feature["mean_total_excess"]:
            terminal = f"{TERMINAL_PREFIX}_PARTIAL_MEAN_ONLY"
        else:
            terminal = f"{TERMINAL_PREFIX}_NO_EXACT_TRANSFER"

    return {
        "schema": SCHEMA,
        "terminal": terminal,
        "prospective_binding": {
            "protocol_parent_commit": protocol["parent_commit"],
            "protocol_execution_commit": protocol_commit,
            "protocol_sha256": sha256_bytes(protocol_bytes),
            "result_absent_from_protocol_inputs": True,
        },
        "upstream": {
            "repository": "https://github.com/coseal/aslib_data.git",
            "commit": ASLIB_COMMIT,
            "scenario": SCENARIO,
            "files": {**upstream, "cv.arff": cv_audit},
        },
        "convention": {
            "algorithm_cutoff_time": cutoff,
            "par10": 10.0 * cutoff,
            "feature_cutoff_fallback": feature_cutoff,
            "total_excess_baseline": "statewise virtual-best-solver runtime with zero feature acquisition",
            "unseen_exact_signature_fallback": "training-only global robust action",
        },
        "corpus": {
            "instance_count": len(instances),
            "algorithm_count": len(algorithms),
            "feature_count": len(feature_names),
            "feature_step_count": len(steps),
            "candidate_representation_count": len(representations),
            "algorithm_audit": algorithm_audit,
        },
        "split_audit": {
            "official_cv_repetition": protocol["official_cv"]["repetition"],
            "official_fold_counts": dict(sorted(collections.Counter(official_assignment.values()).items())),
            "family": family_audit,
        },
        "panels": {
            "official_cv": official,
            "leave_family_out": family,
        },
        "controls": {
            "all_candidate_representations_training_only": True,
            "frozen_R11_control_not_retuned": frozen_steps == ("Pre", "lobjois"),
            "official_cv_complete": set(official_assignment) == set(instances),
            "family_cv_complete": set(family_assignment) == set(instances),
            "family_overlap_zero": family_audit["zero_family_overlap"],
            "same_oracle_baseline_all_arms": True,
            "test_runtimes_not_used_for_training_selection": True,
        },
        "authority": {
            "prospectively_frozen_before_heldout_execution": True,
            "heldout_transfer_within_pinned_ASlib_scenario": True,
            "cross_scenario_transfer": False,
            "external_independence": False,
            "strong_learned_baseline_complete": False,
            "adaptive_R12_R13_policy_executed": False,
            "production_deployment_value": False,
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def compact_summary(result: dict[str, Any], result_sha256: str) -> dict[str, Any]:
    panels = {}
    for name, panel in result["panels"].items():
        panels[name] = {
            "strong_transfer_gate": panel["strong_transfer_gate"],
            "arms": panel["arms"],
            "training_selected_representation_histogram": panel[
                "training_selected_representation_histogram"
            ],
        }
    return {
        "schema": result["schema"],
        "terminal": result["terminal"],
        "protocol_execution_commit": result["prospective_binding"]["protocol_execution_commit"],
        "protocol_sha256": result["prospective_binding"]["protocol_sha256"],
        "full_result_sha256": result_sha256,
        "corpus": result["corpus"],
        "split_audit": result["split_audit"],
        "panels": panels,
        "controls": result["controls"],
        "authority": result["authority"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--protocol-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--comment-output", type=Path, required=True)
    args = parser.parse_args()

    result = run(args.aslib_root, args.protocol, args.protocol_commit)
    payload = canonical_json(result) + "\n"
    result_sha256 = sha256_bytes(payload.encode())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")

    summary = compact_summary(result, result_sha256)
    comment = (
        "## FiberGuard R14 prospective held-out terminal\n\n"
        f"Protocol execution commit: `{args.protocol_commit}`\n\n"
        f"Terminal: `{result['terminal']}`\n\n"
        f"Full result SHA-256: `{result_sha256}`\n\n"
        "```json\n"
        + json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False)
        + "\n```\n"
    )
    args.comment_output.write_text(comment, encoding="utf-8")
    print(
        result["terminal"],
        f"protocol_commit={args.protocol_commit}",
        f"result_sha256={result_sha256}",
        f"official_gate={result['panels']['official_cv']['strong_transfer_gate']}",
        f"family_gate={result['panels']['leave_family_out']['strong_transfer_gate']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
