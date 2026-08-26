#!/usr/bin/env python3
"""Prospective held-out FiberGuard transfer audit on pinned ASlib SAT12-ALL.

The protocol is outcome-blind at commit time. It uses source-supplied CV folds
and a deterministic path-prefix group split. Feature representations and
solver policies are fit from training outcomes only; held-out runtimes are used
only for final fold evaluation.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any, Iterable, Sequence

SCHEMA = "ORION.FiberGuard.ASlibTransfer.R14.v1"
TERMINAL = "FIBERGUARD_ASLIB_TRANSFER_R14_PASS"
SOURCE_PARENT = "6c23a3fe4ccf415bc3a73794878d72583ed48eb2"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SCENARIO = "SAT12-ALL"
CV_BLOB = "63d3922abaae67e690f31a74c7daa1be6981fb70"
FOLD_COUNT = 10
PREFIX_COMPONENTS = 4
PRIMARY_MIN_SUPPORT = 2
R11_FROZEN_STEPS = ("Pre", "lobjois")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def load_cv(path: Path, instances: Sequence[str], read_arff) -> dict[str, int]:
    attrs, rows = read_arff(path)
    if attrs != ["instance_id", "repetition", "fold"]:
        raise ValueError(f"unexpected cv schema: {attrs}")
    mapping: dict[str, int] = {}
    repetitions: set[int] = set()
    for instance, repetition, fold in rows:
        rep = int(float(repetition))
        fold_id = int(float(fold))
        repetitions.add(rep)
        if rep != 1:
            raise ValueError("R14 freezes the source-supplied repetition 1 only")
        if not 1 <= fold_id <= FOLD_COUNT:
            raise ValueError(f"invalid fold {fold_id}")
        if instance in mapping:
            raise ValueError(f"duplicate cv row for {instance}")
        mapping[instance] = fold_id
    if repetitions != {1}:
        raise ValueError(f"unexpected repetitions: {repetitions}")
    if set(mapping) != set(instances):
        raise ValueError(
            f"cv/instance mismatch: cv={len(mapping)} instances={len(instances)}"
        )
    return mapping


def prefix_group(instance: str) -> str:
    parts = instance.split("/")
    return "/".join(parts[: min(PREFIX_COMPONENTS, len(parts))])


def balanced_prefix_folds(instances: Sequence[str]) -> tuple[dict[str, int], dict[str, Any]]:
    """Outcome-blind, group-disjoint greedy assignment to ten balanced folds."""
    groups: dict[str, list[str]] = collections.defaultdict(list)
    for instance in instances:
        groups[prefix_group(instance)].append(instance)
    ordered = sorted(
        groups,
        key=lambda group: (
            -len(groups[group]),
            sha256_bytes(group.encode()),
            group,
        ),
    )
    loads = [0] * FOLD_COUNT
    group_fold: dict[str, int] = {}
    for group in ordered:
        fold_index = min(range(FOLD_COUNT), key=lambda index: (loads[index], index))
        group_fold[group] = fold_index + 1
        loads[fold_index] += len(groups[group])
    mapping = {
        instance: group_fold[prefix_group(instance)] for instance in instances
    }
    return mapping, {
        "prefix_components": PREFIX_COMPONENTS,
        "group_count": len(groups),
        "fold_loads": loads,
        "largest_group": max(map(len, groups.values())),
        "group_assignment_sha256": sha256_bytes(canonical_json(group_fold).encode()),
    }


def leakage_audit(folds: dict[str, int]) -> dict[str, int]:
    group_folds: dict[str, set[int]] = collections.defaultdict(set)
    group_instances: dict[str, int] = collections.Counter()
    for instance, fold in folds.items():
        group = prefix_group(instance)
        group_folds[group].add(fold)
        group_instances[group] += 1
    shared = {group for group, values in group_folds.items() if len(values) > 1}
    return {
        "prefix_group_count": len(group_folds),
        "prefix_groups_crossing_folds": len(shared),
        "instances_in_crossing_prefix_groups": sum(group_instances[group] for group in shared),
    }


def nearest_rank_thresholds(values: Iterable[float]) -> tuple[float, ...]:
    ordered = sorted(values)
    if not ordered:
        return ()
    thresholds: list[float] = []
    for numerator in (1, 2, 3):
        rank = math.ceil(numerator * len(ordered) / 4)
        thresholds.append(ordered[max(0, rank - 1)])
    return tuple(thresholds)


def build_step_atoms(
    all_instances: Sequence[int],
    train_instances: Sequence[int],
    instance_names: Sequence[str],
    steps: Sequence[str],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
    mode: str,
) -> tuple[list[list[tuple[Any, ...]]], dict[str, list[float]]]:
    if mode not in {"exact", "quartile"}:
        raise ValueError(mode)
    provided = sorted(
        {
            feature
            for step in steps
            for feature in (feature_steps[step].get("provides", []) or [])
        }
    )
    thresholds: dict[str, tuple[float, ...]] = {}
    if mode == "quartile":
        for feature in provided:
            numeric = [
                float(feature_values[instance_names[index]][feature])
                for index in train_instances
                if feature_values[instance_names[index]].get(feature, "?") != "?"
            ]
            thresholds[feature] = nearest_rank_thresholds(numeric)

    atoms: list[list[tuple[Any, ...]]] = [
        [()] * len(steps) for _ in all_instances
    ]
    for index in all_instances:
        name = instance_names[index]
        for step_index, step in enumerate(steps):
            status = str(feature_status.get(name, {}).get(step, "other"))
            values: list[Any] = []
            features = feature_steps[step].get("provides", []) or []
            if isinstance(features, str):
                features = [features]
            for feature in features:
                raw = feature_values.get(name, {}).get(feature, "?")
                if raw == "?":
                    values.append("?")
                elif mode == "exact":
                    values.append(raw)
                else:
                    values.append(bisect.bisect_right(thresholds[feature], float(raw)))
            atoms[index][step_index] = (status, *values)
    threshold_receipt = {
        feature: list(values) for feature, values in sorted(thresholds.items())
    }
    return atoms, threshold_receipt


def robust_action(
    members: Sequence[int],
    acquisition: Sequence[float],
    regret: Sequence[Sequence[float]],
    algorithm_names: Sequence[str],
) -> tuple[int, float]:
    if not members:
        raise ValueError("empty fibre")
    best_action = 0
    best_value = math.inf
    for action, name in enumerate(algorithm_names):
        value = max(acquisition[index] + regret[index][action] for index in members)
        if (value, name) < (best_value, algorithm_names[best_action]):
            best_action = action
            best_value = value
    return best_action, best_value


def signature(
    instance: int,
    selected: tuple[int, ...],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
) -> tuple[Any, ...]:
    return tuple(atoms[instance][step] for step in selected)


def acquisition_vector(
    selected: tuple[int, ...], step_cost: Sequence[Sequence[float]]
) -> list[float]:
    return [sum(row[step] for step in selected) for row in step_cost]


def fit_policy(
    train: Sequence[int],
    selected: tuple[int, ...],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
    acquisition: Sequence[float],
    regret: Sequence[Sequence[float]],
    algorithm_names: Sequence[str],
    fallback_action: int,
    minimum_support: int,
) -> dict[str, Any]:
    fibres: dict[tuple[Any, ...], list[int]] = collections.defaultdict(list)
    for instance in train:
        fibres[signature(instance, selected, atoms)].append(instance)

    actions: dict[tuple[Any, ...], int] = {}
    support: dict[tuple[Any, ...], int] = {}
    robust_value = 0.0
    for key, members in fibres.items():
        support[key] = len(members)
        if len(members) < minimum_support:
            action = fallback_action
            value = max(
                acquisition[index] + regret[index][action] for index in members
            )
        else:
            action, value = robust_action(
                members, acquisition, regret, algorithm_names
            )
            actions[key] = action
        robust_value = max(robust_value, value)

    digest_rows = sorted(
        (
            repr(key),
            algorithm_names[actions.get(key, fallback_action)],
            support[key],
            key in actions,
        )
        for key in fibres
    )
    return {
        "actions": actions,
        "support": support,
        "fallback_action": fallback_action,
        "robust_training_total_excess": robust_value,
        "fibre_count": len(fibres),
        "eligible_fibre_count": len(actions),
        "policy_sha256": sha256_bytes(canonical_json(digest_rows).encode()),
    }


def evaluate_policy(
    test: Sequence[int],
    fold: int,
    arm: str,
    selected: tuple[int, ...],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
    acquisition: Sequence[float],
    regret: Sequence[Sequence[float]],
    runtimes: Sequence[Sequence[float]],
    oracle: Sequence[float],
    algorithm_names: Sequence[str],
    policy: dict[str, Any],
    minimum_support: int,
    instance_names: Sequence[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for instance in test:
        key = signature(instance, selected, atoms)
        eligible = key in policy["actions"]
        action = policy["actions"].get(key, policy["fallback_action"])
        train_support = policy["support"].get(key, 0)
        rows.append(
            {
                "instance": instance_names[instance],
                "fold": fold,
                "arm": arm,
                "steps": [int(step) for step in selected],
                "minimum_support": minimum_support,
                "signature_seen": key in policy["support"],
                "cell_policy_used": eligible,
                "training_cell_support": train_support,
                "algorithm": algorithm_names[action],
                "algorithm_runtime_PAR10": runtimes[instance][action],
                "oracle_runtime_PAR10": oracle[instance],
                "feature_cost": acquisition[instance],
                "total_excess": acquisition[instance] + regret[instance][action],
            }
        )
    return rows


def summarize_predictions(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("empty predictions")
    excess = sorted(float(row["total_excess"]) for row in rows)
    costs = [float(row["feature_cost"]) for row in rows]
    p95_index = min(len(excess) - 1, math.ceil(0.95 * len(excess)) - 1)
    seen = sum(bool(row["signature_seen"]) for row in rows)
    used = sum(bool(row["cell_policy_used"]) for row in rows)
    return {
        "instance_count": len(rows),
        "robust_total_excess": max(excess),
        "mean_total_excess": statistics.fmean(excess),
        "median_total_excess": statistics.median(excess),
        "p95_total_excess": excess[p95_index],
        "mean_feature_cost": statistics.fmean(costs),
        "maximum_feature_cost": max(costs),
        "signature_seen_count": seen,
        "signature_seen_rate": seen / len(rows),
        "cell_policy_used_count": used,
        "cell_policy_used_rate": used / len(rows),
        "fallback_count": len(rows) - used,
    }


def select_representation(
    train: Sequence[int],
    closed_sets: Sequence[tuple[int, ...]],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
    step_cost: Sequence[Sequence[float]],
    regret: Sequence[Sequence[float]],
    algorithm_names: Sequence[str],
    fallback_action: int,
) -> tuple[tuple[int, ...], dict[str, Any], list[float]]:
    best: tuple[tuple[Any, ...], tuple[int, ...], dict[str, Any], list[float]] | None = None
    for selected in closed_sets:
        acquisition = acquisition_vector(selected, step_cost)
        policy = fit_policy(
            train,
            selected,
            atoms,
            acquisition,
            regret,
            algorithm_names,
            fallback_action,
            PRIMARY_MIN_SUPPORT,
        )
        key = (
            policy["robust_training_total_excess"],
            len(selected),
            selected,
        )
        candidate = (key, selected, policy, acquisition)
        if best is None or candidate[0] < best[0]:
            best = candidate
    assert best is not None
    return best[1], best[2], best[3]


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
    runtimes: Sequence[Sequence[float]],
    oracle: Sequence[float],
    algorithm_names: Sequence[str],
    closed_sets: Sequence[tuple[int, ...]],
) -> dict[str, Any]:
    all_indices = tuple(range(len(instance_names)))
    step_index = {step: index for index, step in enumerate(steps)}
    r11_selected = tuple(step_index[step] for step in R11_FROZEN_STEPS)
    full_selected = tuple(range(len(steps)))
    predictions: list[dict[str, Any]] = []
    fold_receipts: list[dict[str, Any]] = []

    for fold in range(1, FOLD_COUNT + 1):
        test = tuple(index for index, name in enumerate(instance_names) if folds[name] == fold)
        test_set = set(test)
        train = tuple(index for index in all_indices if index not in test_set)
        if not test or not train:
            raise ValueError(f"empty train/test partition in {split_name} fold {fold}")

        zero = [0.0] * len(instance_names)
        fallback_action, fallback_train_value = robust_action(
            train, zero, regret, algorithm_names
        )
        exact_atoms, _ = build_step_atoms(
            all_indices,
            train,
            instance_names,
            steps,
            feature_steps,
            feature_values,
            feature_status,
            "exact",
        )
        quartile_atoms, thresholds = build_step_atoms(
            all_indices,
            train,
            instance_names,
            steps,
            feature_steps,
            feature_values,
            feature_status,
            "quartile",
        )
        threshold_digest = sha256_bytes(canonical_json(thresholds).encode())

        arm_specs: list[tuple[str, tuple[int, ...], Any, int]] = [
            ("no_features", (), exact_atoms, 1),
            ("r11_pre_lobjois_exact", r11_selected, exact_atoms, 1),
            ("r11_pre_lobjois_quartile_support2", r11_selected, quartile_atoms, 2),
            ("all_features_quartile_support2", full_selected, quartile_atoms, 2),
        ]
        fold_arm_receipts: dict[str, Any] = {}
        for arm, selected, atoms, minimum_support in arm_specs:
            acquisition = acquisition_vector(selected, step_cost)
            policy = fit_policy(
                train,
                selected,
                atoms,
                acquisition,
                regret,
                algorithm_names,
                fallback_action,
                minimum_support,
            )
            predictions.extend(
                evaluate_policy(
                    test,
                    fold,
                    arm,
                    selected,
                    atoms,
                    acquisition,
                    regret,
                    runtimes,
                    oracle,
                    algorithm_names,
                    policy,
                    minimum_support,
                    instance_names,
                )
            )
            fold_arm_receipts[arm] = {
                "steps": [steps[index] for index in selected],
                "minimum_support": minimum_support,
                "policy_sha256": policy["policy_sha256"],
                "robust_training_total_excess": policy["robust_training_total_excess"],
                "fibre_count": policy["fibre_count"],
                "eligible_fibre_count": policy["eligible_fibre_count"],
            }

        selected, policy, acquisition = select_representation(
            train,
            closed_sets,
            quartile_atoms,
            step_cost,
            regret,
            algorithm_names,
            fallback_action,
        )
        arm = "training_selected_quartile_support2"
        predictions.extend(
            evaluate_policy(
                test,
                fold,
                arm,
                selected,
                quartile_atoms,
                acquisition,
                regret,
                runtimes,
                oracle,
                algorithm_names,
                policy,
                PRIMARY_MIN_SUPPORT,
                instance_names,
            )
        )
        fold_arm_receipts[arm] = {
            "steps": [steps[index] for index in selected],
            "minimum_support": PRIMARY_MIN_SUPPORT,
            "policy_sha256": policy["policy_sha256"],
            "robust_training_total_excess": policy["robust_training_total_excess"],
            "fibre_count": policy["fibre_count"],
            "eligible_fibre_count": policy["eligible_fibre_count"],
        }
        fold_receipts.append(
            {
                "fold": fold,
                "train_count": len(train),
                "test_count": len(test),
                "fallback_algorithm": algorithm_names[fallback_action],
                "fallback_training_robust_regret": fallback_train_value,
                "quartile_threshold_sha256": threshold_digest,
                "quartile_thresholds": thresholds,
                "arms": fold_arm_receipts,
            }
        )

    by_arm: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in predictions:
        by_arm[row["arm"]].append(row)
    if any(len(rows) != len(instance_names) for rows in by_arm.values()):
        raise AssertionError("each arm must make exactly one out-of-fold prediction per instance")
    return {
        "split": split_name,
        "fold_count": FOLD_COUNT,
        "leakage_audit": leakage_audit(folds),
        "fold_receipts": fold_receipts,
        "arms": {
            arm: summarize_predictions(rows) for arm, rows in sorted(by_arm.items())
        },
        "prediction_sha256": sha256_bytes(canonical_json(predictions).encode()),
        "predictions": predictions,
    }


def synthetic_self_test() -> dict[str, bool]:
    names = [f"root/family/{index // 2}/shared/x{index}" for index in range(8)]
    folds, audit = balanced_prefix_folds(names)
    assert set(folds.values()) <= set(range(1, 11))
    assert audit["group_count"] == 4
    assert leakage_audit(folds)["prefix_groups_crossing_folds"] == 0
    assert nearest_rank_thresholds([1, 2, 3, 4]) == (1, 2, 3)

    regret = [[0, 5], [5, 0], [1, 1]]
    acquisition = [0, 0, 0]
    action, value = robust_action((0, 1), acquisition, regret, ("a", "b"))
    assert action == 0 and value == 5

    atoms = [[("x",)], [("x",)], [("y",)]]
    policy = fit_policy(
        (0, 1),
        (0,),
        atoms,
        acquisition,
        regret,
        ("a", "b"),
        0,
        2,
    )
    assert policy["eligible_fibre_count"] == 1
    assert policy["robust_training_total_excess"] == 5
    return {
        "balanced_group_assignment": True,
        "quartile_nearest_rank": True,
        "robust_action": True,
        "support_gate": True,
    }


def run(aslib_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import yaml
    from fiberguard_aslib_sat12_all_r11 import (
        dependency_closure,
        enumerate_dependency_closed_sets,
        feature_cost,
        load_algorithm_runs,
        load_feature_values,
        load_step_table,
        read_arff,
        validate_upstream,
    )

    scenario_root = aslib_root / SCENARIO
    upstream = validate_upstream(aslib_root)
    cv_path = scenario_root / "cv.arff"
    if git_blob_sha(cv_path) != CV_BLOB:
        raise ValueError("cv.arff blob mismatch")
    upstream["cv.arff"] = {
        "git_blob_sha1": CV_BLOB,
        "sha256": sha256_bytes(cv_path.read_bytes()),
        "bytes": cv_path.stat().st_size,
    }

    description = yaml.safe_load((scenario_root / "description.txt").read_text())
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time", cutoff)
    feature_cutoff = cutoff if feature_cutoff_raw in {None, "?"} else float(feature_cutoff_raw)
    feature_steps = dict(description["feature_steps"])
    steps = sorted(feature_steps)

    runtimes_dict, algorithm_names, algorithm_audit = load_algorithm_runs(
        scenario_root / "algorithm_runs.arff", cutoff
    )
    feature_values, feature_names = load_feature_values(
        scenario_root / "feature_values.arff"
    )
    feature_costs, cost_steps = load_step_table(
        scenario_root / "feature_costs.arff", numeric=True
    )
    feature_status, status_steps = load_step_table(
        scenario_root / "feature_runstatus.arff", numeric=False
    )
    if set(cost_steps) != set(steps) or set(status_steps) != set(steps):
        raise ValueError("step mismatch")

    instance_names = sorted(runtimes_dict)
    if set(instance_names) != set(feature_values) or set(instance_names) != set(feature_costs):
        raise ValueError("instance mismatch across ASlib tables")
    official_folds = load_cv(cv_path, instance_names, read_arff)
    prefix_folds, prefix_receipt = balanced_prefix_folds(instance_names)

    runtimes = [
        [runtimes_dict[name][algorithm] for algorithm in algorithm_names]
        for name in instance_names
    ]
    oracle = [min(row) for row in runtimes]
    regret = [
        [value - oracle[index] for value in row]
        for index, row in enumerate(runtimes)
    ]
    step_cost = [
        [
            feature_cost(
                name,
                (step,),
                feature_costs,
                feature_status,
                feature_cutoff,
            )
            for step in steps
        ]
        for name in instance_names
    ]
    closed_sets_named = enumerate_dependency_closed_sets(steps, feature_steps)
    step_index = {step: index for index, step in enumerate(steps)}
    closed_sets = [tuple(step_index[step] for step in selected) for selected in closed_sets_named]

    split_results = [
        run_split(
            "source_cv_repetition1",
            official_folds,
            instance_names,
            steps,
            feature_steps,
            feature_values,
            feature_status,
            step_cost,
            regret,
            runtimes,
            oracle,
            algorithm_names,
            closed_sets,
        ),
        run_split(
            "balanced_prefix_group",
            prefix_folds,
            instance_names,
            steps,
            feature_steps,
            feature_values,
            feature_status,
            step_cost,
            regret,
            runtimes,
            oracle,
            algorithm_names,
            closed_sets,
        ),
    ]

    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_parent": SOURCE_PARENT,
        "authority": {
            "source_supplied_held_out_folds": True,
            "outcome_blind_prefix_group_split": True,
            "primary_training_selected_arm_uses_training_outcomes_only": True,
            "r11_pre_lobjois_is_post_selection_control_not_transfer_authority": True,
            "held_out_runtime_used_only_for_final_fold_evaluation": True,
            "family_independence": False,
            "prefix_group_is_family_ground_truth": False,
            "external_replay": False,
            "learned_selector_claim": False,
            "production_value": False,
            "grants_journal_authority": False,
        },
        "upstream": {
            "repository": "https://github.com/coseal/aslib_data.git",
            "commit": ASLIB_COMMIT,
            "scenario": SCENARIO,
            "files": upstream,
        },
        "protocol": {
            "official_cv_repetition": 1,
            "fold_count": FOLD_COUNT,
            "prefix_components": PREFIX_COMPONENTS,
            "prefix_group_assignment": "largest-group-first greedy to the currently lightest fold; hash/name tie break; no outcomes",
            "quantization": "outer-training nearest-rank quartiles with missingness explicit",
            "primary_minimum_training_cell_support": PRIMARY_MIN_SUPPORT,
            "unseen_or_low_support_fallback": "outer-training no-feature robust action",
            "training_selection_objective": "minimum outer-training robust total excess, then fewer steps, then lexical step tuple",
            "candidate_representation_count": len(closed_sets),
            "r11_frozen_control_steps": list(R11_FROZEN_STEPS),
            "common_oracle_baseline": "statewise virtual-best solver PAR10 runtime with zero feature acquisition",
        },
        "corpus": {
            "instance_count": len(instance_names),
            "algorithm_count": len(algorithm_names),
            "feature_count": len(feature_names),
            "feature_step_count": len(steps),
            "algorithm_audit": algorithm_audit,
            "prefix_split_receipt": prefix_receipt,
        },
        "splits": split_results,
        "self_test": synthetic_self_test(),
        "controls": {
            "official_cv_covers_every_instance_once": set(official_folds) == set(instance_names),
            "prefix_groups_do_not_cross_prefix_folds": leakage_audit(prefix_folds)["prefix_groups_crossing_folds"] == 0,
            "all_candidate_representations_dependency_closed": all(
                tuple(sorted(dependency_closure(selected, feature_steps))) == tuple(sorted(selected))
                for selected in closed_sets_named
            ),
            "every_arm_has_one_out_of_fold_prediction_per_instance": all(
                all(summary["instance_count"] == len(instance_names) for summary in split["arms"].values())
                for split in split_results
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(canonical_json(synthetic_self_test()))
        return 0
    if args.aslib_root is None or args.output is None:
        parser.error("--aslib-root and --output are required unless --self-test is used")
    result = run(args.aslib_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(result) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    print(
        TERMINAL,
        f"sha256={sha256_bytes(payload.encode())}",
        f"instances={result['corpus']['instance_count']}",
        f"representations={result['protocol']['candidate_representation_count']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
