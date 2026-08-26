#!/usr/bin/env python3
"""Prospective FiberGuard versus learned-selector comparator on untouched ASlib data."""
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

import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

SCHEMA = "ORION.FiberGuard.LearnedComparator.R16.v1"
TERMINAL = "FIBERGUARD_LEARNED_COMPARATOR_R16_PASS"
SOURCE_PARENT = "4aac9b030c7e143b739caf42262718924b9a9005"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
FOLD_COUNT = 10
MIN_SUPPORT = 2
TAIL_FRACTION = 0.05
STATUS_CATEGORIES = ("ok", "presolved", "timeout", "memout", "crash", "other", "missing")
FOREST_PARAMETERS: dict[str, Any] = {
    "n_estimators": 96,
    "max_depth": 18,
    "min_samples_leaf": 2,
    "max_features": "sqrt",
    "bootstrap": True,
    "n_jobs": 1,
}

REGISTRY: dict[str, dict[str, str]] = {
    "BNSL-2016": {
        "description.txt": "e193c8a46d2b3b9fadfe1cb27bef16db8540bc29",
        "algorithm_runs.arff": "33adc274ba3bd7d62875a5ee017d9b4b147e6ee8",
        "cv.arff": "b53e47f5d081cfa8901ff652daf40b9c5ecd0a87",
        "feature_costs.arff": "09afa0572cc46269bfe03cfc2f008d5b95d2bf40",
        "feature_runstatus.arff": "90e494a307c44f3978ca33c5a02e66d2fe4726f3",
        "feature_values.arff": "5d981d99a76395ad9828d0ff51f60ecb5fb7965f",
    },
    "MIP-2016": {
        "description.txt": "0148a3489bdb7afdf2b7fdc46c52e0cdd8cd741c",
        "algorithm_runs.arff": "7b079046b38162f8f726c2e3d462684665532a92",
        "cv.arff": "a596ee50c3105c6fb45ad2347dc4ab956a9bcd45",
        "feature_costs.arff": "c49eb3c464afe8b8dfce5f04cd0450508354a865",
        "feature_runstatus.arff": "efc70f485ed47a4cd9fef8751f139b46f5482708",
        "feature_values.arff": "139e81684591d6d2a27eba6a805810fd02c8e6de",
    },
    "TSP-LION2015": {
        "description.txt": "923b7e0cb7cf354af398875f536717e21a8c7388",
        "algorithm_runs.arff": "7ec9db6394c52a2b62d1c44fcd84df47b10ba7b9",
        "cv.arff": "9d9bee231caaa9cfa017cb176999a36f04d163e5",
        "feature_costs.arff": "d6649105f201e9155f5646ff5191e46a824a0ee3",
        "feature_runstatus.arff": "259e00133d47da914d9cc9f7435f9c97a4346bb9",
        "feature_values.arff": "8c62bc84e319d721691d7b1ef1326f1d08437641",
    },
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def deterministic_seed(*parts: object) -> int:
    payload = "R16|" + "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:4], "big")


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


def normalize_status(value: object) -> str:
    raw = str(value).strip().lower()
    if raw in {"", "?", "none", "nan"}:
        return "missing"
    if raw in STATUS_CATEGORIES:
        return raw
    return "other"


def upper_tail_mean(values: Iterable[float]) -> float:
    ordered = sorted((float(value) for value in values), reverse=True)
    if not ordered:
        raise ValueError("empty tail")
    count = max(1, math.ceil(TAIL_FRACTION * len(ordered)))
    return statistics.fmean(ordered[:count])


def feature_names_for_steps(
    selected: tuple[int, ...],
    steps: Sequence[str],
    feature_steps: dict[str, dict[str, Any]],
) -> tuple[str, ...]:
    names: set[str] = set()
    for step_index in selected:
        provided = feature_steps[steps[step_index]].get("provides", []) or []
        if isinstance(provided, str):
            provided = [provided]
        names.update(provided)
    return tuple(sorted(names))


def build_train_test_matrix(
    selected: tuple[int, ...],
    train: Sequence[int],
    test: Sequence[int],
    steps: Sequence[str],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
    instance_names: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Build a deterministic train-only-imputed matrix for one step set."""
    features = feature_names_for_steps(selected, steps, feature_steps)
    train_rows: list[list[float]] = [[] for _ in train]
    test_rows: list[list[float]] = [[] for _ in test]
    column_receipts: list[dict[str, Any]] = []

    for feature in features:
        train_raw = [feature_values[instance_names[index]].get(feature, "?") for index in train]
        test_raw = [feature_values[instance_names[index]].get(feature, "?") for index in test]
        numeric_train: list[float] = []
        numeric_mode = True
        for raw in train_raw:
            if raw == "?":
                continue
            try:
                value = float(raw)
            except ValueError:
                numeric_mode = False
                break
            if math.isfinite(value):
                numeric_train.append(value)
        if numeric_mode:
            median = float(statistics.median(numeric_train)) if numeric_train else 0.0
            for row, raw in zip(train_rows, train_raw):
                missing = raw == "?"
                try:
                    value = float(raw) if not missing else median
                    missing = missing or not math.isfinite(value)
                except ValueError:
                    value = median
                    missing = True
                row.extend((median if missing else value, float(missing)))
            for row, raw in zip(test_rows, test_raw):
                missing = raw == "?"
                try:
                    value = float(raw) if not missing else median
                    missing = missing or not math.isfinite(value)
                except ValueError:
                    value = median
                    missing = True
                row.extend((median if missing else value, float(missing)))
            column_receipts.append(
                {
                    "feature": feature,
                    "kind": "numeric_plus_missing_indicator",
                    "training_median": format(median, ".17g"),
                    "training_nonmissing": len(numeric_train),
                }
            )
        else:
            categories = tuple(sorted({raw for raw in train_raw if raw != "?"}))
            columns = (*categories, "__UNKNOWN__", "__MISSING__")
            for row, raw in zip(train_rows, train_raw):
                category = "__MISSING__" if raw == "?" else raw
                row.extend(float(category == column) for column in columns)
            for row, raw in zip(test_rows, test_raw):
                category = "__MISSING__" if raw == "?" else raw
                if category not in categories and category != "__MISSING__":
                    category = "__UNKNOWN__"
                row.extend(float(category == column) for column in columns)
            column_receipts.append(
                {
                    "feature": feature,
                    "kind": "training_category_one_hot",
                    "categories": list(categories),
                }
            )

    for step_index in selected:
        step = steps[step_index]
        for row, index in zip(train_rows, train):
            status = normalize_status(feature_status.get(instance_names[index], {}).get(step, "?"))
            row.extend(float(status == category) for category in STATUS_CATEGORIES)
        for row, index in zip(test_rows, test):
            status = normalize_status(feature_status.get(instance_names[index], {}).get(step, "?"))
            row.extend(float(status == category) for category in STATUS_CATEGORIES)
        column_receipts.append(
            {
                "step": step,
                "kind": "fixed_runstatus_one_hot",
                "categories": list(STATUS_CATEGORIES),
            }
        )

    dimension = len(train_rows[0]) if train_rows else 0
    if any(len(row) != dimension for row in train_rows + test_rows):
        raise AssertionError("matrix rows have inconsistent dimensions")
    train_matrix = np.asarray(train_rows, dtype=np.float32).reshape(len(train), dimension)
    test_matrix = np.asarray(test_rows, dtype=np.float32).reshape(len(test), dimension)
    receipt = {
        "selected_step_indices": list(selected),
        "selected_steps": [steps[index] for index in selected],
        "provided_feature_count": len(features),
        "matrix_dimension": dimension,
        "column_contract_sha256": sha256_bytes(canonical_json(column_receipts).encode()),
        "training_matrix_sha256": sha256_bytes(train_matrix.tobytes()),
        "test_matrix_sha256": sha256_bytes(test_matrix.tobytes()),
    }
    return train_matrix, test_matrix, receipt


def forest_kwargs(seed: int) -> dict[str, Any]:
    return {**FOREST_PARAMETERS, "random_state": seed}


def learned_actions(
    scenario: str,
    split: str,
    fold: int,
    arm_prefix: str,
    selected: tuple[int, ...],
    train: Sequence[int],
    test: Sequence[int],
    runtimes: np.ndarray,
    algorithm_names: Sequence[str],
    steps: Sequence[str],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
    instance_names: Sequence[str],
    fallback_action: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    if not selected:
        constant = np.full(len(test), fallback_action, dtype=np.int64)
        return constant, constant.copy(), {
            "empty_representation": True,
            "matrix_dimension": 0,
            "regressor_count": 0,
            "classifier_classes": [algorithm_names[fallback_action]],
            "model_contract_sha256": sha256_bytes(
                canonical_json(
                    {
                        "arm_prefix": arm_prefix,
                        "fallback": algorithm_names[fallback_action],
                        "forest_parameters": FOREST_PARAMETERS,
                    }
                ).encode()
            ),
        }

    x_train, x_test, matrix_receipt = build_train_test_matrix(
        selected,
        train,
        test,
        steps,
        feature_steps,
        feature_values,
        feature_status,
        instance_names,
    )
    predicted_log_runtime = np.empty((len(test), len(algorithm_names)), dtype=np.float64)
    regression_seeds: list[int] = []
    for action, algorithm in enumerate(algorithm_names):
        seed = deterministic_seed(scenario, split, fold, arm_prefix, "regression", algorithm)
        regression_seeds.append(seed)
        model = RandomForestRegressor(**forest_kwargs(seed))
        target = np.log1p(runtimes[np.asarray(train), action])
        model.fit(x_train, target)
        predicted_log_runtime[:, action] = model.predict(x_test)
    regression_action = np.argmin(predicted_log_runtime, axis=1).astype(np.int64)

    oracle_label = np.argmin(runtimes[np.asarray(train), :], axis=1).astype(np.int64)
    classes = np.unique(oracle_label)
    classifier_seed = deterministic_seed(scenario, split, fold, arm_prefix, "classification")
    if len(classes) == 1:
        classification_action = np.full(len(test), int(classes[0]), dtype=np.int64)
    else:
        classifier = RandomForestClassifier(
            **forest_kwargs(classifier_seed),
            class_weight="balanced_subsample",
        )
        classifier.fit(x_train, oracle_label)
        classification_action = classifier.predict(x_test).astype(np.int64)

    model_contract = {
        "scenario": scenario,
        "split": split,
        "fold": fold,
        "arm_prefix": arm_prefix,
        "forest_parameters": FOREST_PARAMETERS,
        "regression_target": "log1p(PAR10 runtime)",
        "regression_seeds": regression_seeds,
        "classification_target": "lexically first virtual-best solver index",
        "classifier_seed": classifier_seed,
        "classifier_classes": [algorithm_names[int(value)] for value in classes],
        "matrix": matrix_receipt,
    }
    return regression_action, classification_action, {
        **matrix_receipt,
        "empty_representation": False,
        "regressor_count": len(algorithm_names),
        "classifier_classes": model_contract["classifier_classes"],
        "model_contract_sha256": sha256_bytes(canonical_json(model_contract).encode()),
    }


def action_rows(
    members: Sequence[int],
    fold: int,
    arm: str,
    selected: tuple[int, ...],
    actions: Sequence[int],
    acquisition: Sequence[float],
    regret: Sequence[Sequence[float]],
    timeout: Sequence[Sequence[bool]],
    algorithm_names: Sequence[str],
    instance_names: Sequence[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for local, instance in enumerate(members):
        action = int(actions[local])
        rows.append(
            {
                "instance": instance_names[instance],
                "fold": fold,
                "arm": arm,
                "steps": list(selected),
                "algorithm": algorithm_names[action],
                "feature_cost": acquisition[instance],
                "selected_solver_timeout": bool(timeout[instance][action]),
                "total_excess": acquisition[instance] + regret[instance][action],
            }
        )
    return rows


def fiberguard_rows(
    members: Sequence[int],
    fold: int,
    selected: tuple[int, ...],
    atoms: Sequence[Sequence[tuple[Any, ...]]],
    policy: dict[str, Any],
    acquisition: Sequence[float],
    regret: Sequence[Sequence[float]],
    timeout: Sequence[Sequence[bool]],
    algorithm_names: Sequence[str],
    instance_names: Sequence[str],
) -> list[dict[str, Any]]:
    actions: list[int] = []
    for instance in members:
        key = tuple(atoms[instance][step] for step in selected)
        actions.append(int(policy["actions"].get(key, policy["fallback_action"])))
    return action_rows(
        members,
        fold,
        "fiberguard_selected",
        selected,
        actions,
        acquisition,
        regret,
        timeout,
        algorithm_names,
        instance_names,
    )


def summarize(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    losses = sorted(float(row["total_excess"]) for row in rows)
    if not losses:
        raise ValueError("empty arm")
    p95 = losses[min(len(losses) - 1, math.ceil(0.95 * len(losses)) - 1)]
    timeout_count = sum(bool(row["selected_solver_timeout"]) for row in rows)
    return {
        "instance_count": len(rows),
        "selected_solver_timeout_count": timeout_count,
        "selected_solver_timeout_rate": timeout_count / len(rows),
        "worst_5_percent_mean_total_excess": upper_tail_mean(losses),
        "mean_total_excess": statistics.fmean(losses),
        "median_total_excess": statistics.median(losses),
        "p95_total_excess": p95,
        "robust_total_excess": max(losses),
        "mean_feature_cost": statistics.fmean(float(row["feature_cost"]) for row in rows),
        "maximum_feature_cost": max(float(row["feature_cost"]) for row in rows),
    }


def dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left["selected_solver_timeout_rate"] <= right["selected_solver_timeout_rate"]
        and left["worst_5_percent_mean_total_excess"]
        < right["worst_5_percent_mean_total_excess"]
        and left["mean_total_excess"] < right["mean_total_excess"]
    )


def scenario_terminal(splits: Sequence[dict[str, Any]]) -> str:
    fg_dominates_both = all(
        dominates(split["arms"]["fiberguard_selected"], split["arms"]["rf_regression_same_steps"])
        and dominates(
            split["arms"]["fiberguard_selected"],
            split["arms"]["rf_classification_same_steps"],
        )
        for split in splits
    )
    regression_dominates = all(
        dominates(split["arms"]["rf_regression_same_steps"], split["arms"]["fiberguard_selected"])
        for split in splits
    )
    classification_dominates = all(
        dominates(
            split["arms"]["rf_classification_same_steps"],
            split["arms"]["fiberguard_selected"],
        )
        for split in splits
    )
    if fg_dominates_both:
        return "C_FIBERGUARD_DOMINATES_BOTH_SAME_REPRESENTATION_RF"
    if regression_dominates and classification_dominates:
        return "C_BOTH_RF_FORMULATIONS_DOMINATE_FIBERGUARD"
    if regression_dominates:
        return "C_RF_REGRESSION_DOMINATES_FIBERGUARD"
    if classification_dominates:
        return "C_RF_CLASSIFICATION_DOMINATES_FIBERGUARD"
    return "C_LEARNED_AND_FIBERGUARD_MIXED_NO_DOMINANCE"


def load_scenario(root: Path, scenario: str) -> dict[str, Any]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import yaml
    import fiberguard_multidomain_r15 as r15
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
    from fiberguard_multidomain_r15_schema_repair import load_algorithm_runs_with_timeout

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
    runtimes = np.asarray(
        [[runtime_dict[name][algorithm] for algorithm in algorithm_names] for name in instance_names],
        dtype=np.float64,
    )
    timeout = [
        [bool(timeout_dict[name][algorithm]) for algorithm in algorithm_names]
        for name in instance_names
    ]
    oracle = np.min(runtimes, axis=1)
    regret = (runtimes - oracle[:, None]).tolist()
    step_cost = [
        [
            feature_cost(name, (step,), feature_costs, feature_status, feature_cutoff)
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
    source_folds = r15.source_cv_folds(scenario_root / "cv.arff", instance_names, read_arff)
    hash_folds, hash_receipt = r15.balanced_hash_folds(instance_names)
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
        "runtimes": runtimes,
        "candidates": candidates,
        "source_folds": source_folds,
        "hash_folds": hash_folds,
        "hash_receipt": hash_receipt,
        "helpers": (build_step_atoms, acquisition_vector, fit_policy, robust_action, r15.select_policy),
    }


def run_split(split_name: str, folds: dict[str, int], data: dict[str, Any]) -> dict[str, Any]:
    import fiberguard_multidomain_r15 as r15

    build_step_atoms, acquisition_vector, fit_policy, robust_action, select_policy = data["helpers"]
    instance_names = data["instance_names"]
    all_indices = tuple(range(len(instance_names)))
    full = tuple(range(len(data["steps"])))
    predictions: list[dict[str, Any]] = []
    fold_receipts: list[dict[str, Any]] = []

    for fold in range(1, FOLD_COUNT + 1):
        test = tuple(index for index, name in enumerate(instance_names) if folds[name] == fold)
        test_set = set(test)
        train = tuple(index for index in all_indices if index not in test_set)
        if not train or not test:
            raise ValueError(f"empty {data['scenario']} {split_name} fold {fold}")
        zero = [0.0] * len(instance_names)
        fallback_action, fallback_value = robust_action(
            train, zero, data["regret"], data["algorithm_names"]
        )
        atoms, thresholds = build_step_atoms(
            all_indices,
            train,
            instance_names,
            data["steps"],
            data["feature_steps"],
            data["feature_values"],
            data["feature_status"],
            "quartile",
        )
        selected, policy, acquisition, objective = select_policy(
            train,
            data["candidates"],
            atoms,
            data["step_cost"],
            data["regret"],
            data["timeout"],
            data["algorithm_names"],
            fallback_action,
            instance_names,
            fit_policy,
            acquisition_vector,
            "catastrophe_tail",
        )
        predictions.extend(
            action_rows(
                test,
                fold,
                "no_features",
                (),
                [fallback_action] * len(test),
                zero,
                data["regret"],
                data["timeout"],
                data["algorithm_names"],
                instance_names,
            )
        )
        predictions.extend(
            fiberguard_rows(
                test,
                fold,
                selected,
                atoms,
                policy,
                acquisition,
                data["regret"],
                data["timeout"],
                data["algorithm_names"],
                instance_names,
            )
        )

        matrix_receipts: dict[str, Any] = {}
        for prefix, learned_steps in (("same_steps", selected), ("all_steps", full)):
            regression, classification, receipt = learned_actions(
                data["scenario"],
                split_name,
                fold,
                prefix,
                learned_steps,
                train,
                test,
                data["runtimes"],
                data["algorithm_names"],
                data["steps"],
                data["feature_steps"],
                data["feature_values"],
                data["feature_status"],
                instance_names,
                fallback_action,
            )
            learned_acquisition = acquisition_vector(learned_steps, data["step_cost"])
            predictions.extend(
                action_rows(
                    test,
                    fold,
                    f"rf_regression_{prefix}",
                    learned_steps,
                    regression,
                    learned_acquisition,
                    data["regret"],
                    data["timeout"],
                    data["algorithm_names"],
                    instance_names,
                )
            )
            predictions.extend(
                action_rows(
                    test,
                    fold,
                    f"rf_classification_{prefix}",
                    learned_steps,
                    classification,
                    learned_acquisition,
                    data["regret"],
                    data["timeout"],
                    data["algorithm_names"],
                    instance_names,
                )
            )
            matrix_receipts[prefix] = receipt

        fold_receipts.append(
            {
                "fold": fold,
                "train_count": len(train),
                "test_count": len(test),
                "fallback_algorithm": data["algorithm_names"][fallback_action],
                "fallback_training_robust_regret": fallback_value,
                "fiberguard_selected_steps": [data["steps"][index] for index in selected],
                "fiberguard_training_objective": list(objective),
                "fiberguard_policy_sha256": policy["policy_sha256"],
                "quartile_threshold_sha256": sha256_bytes(canonical_json(thresholds).encode()),
                "learned_model_receipts": matrix_receipts,
            }
        )

    by_arm: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in predictions:
        by_arm[row["arm"]].append(row)
    expected_arms = {
        "no_features",
        "fiberguard_selected",
        "rf_regression_same_steps",
        "rf_classification_same_steps",
        "rf_regression_all_steps",
        "rf_classification_all_steps",
    }
    if set(by_arm) != expected_arms:
        raise AssertionError(("arm mismatch", set(by_arm), expected_arms))
    if any(len(rows) != len(instance_names) for rows in by_arm.values()):
        raise AssertionError("every arm must have one out-of-fold prediction per instance")
    summaries = {arm: summarize(rows) for arm, rows in sorted(by_arm.items())}
    return {
        "split": split_name,
        "fold_count": FOLD_COUNT,
        "fold_receipts": fold_receipts,
        "arms": summaries,
        "prediction_sha256": sha256_bytes(canonical_json(predictions).encode()),
        "predictions": predictions,
    }


def run(root: Path) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    terminal_histogram: collections.Counter[str] = collections.Counter()
    for scenario in REGISTRY:
        data = load_scenario(root, scenario)
        splits = [
            run_split("source_cv_repetition1", data["source_folds"], data),
            run_split("balanced_hash", data["hash_folds"], data),
        ]
        terminal = scenario_terminal(splits)
        terminal_histogram[terminal] += 1
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
                    "algorithm_cutoff": data["cutoff"],
                    "feature_cutoff_fallback": data["feature_cutoff"],
                    "algorithm_status_counts": data["status_counts"],
                    "hash_split_receipt": data["hash_receipt"],
                },
                "splits": splits,
                "scenario_terminal": terminal,
            }
        )
    return {
        "schema": SCHEMA,
        "terminal": TERMINAL,
        "source_parent": SOURCE_PARENT,
        "upstream": {
            "repository": "https://github.com/coseal/aslib_data.git",
            "commit": ASLIB_COMMIT,
            "scenario_registry": list(REGISTRY),
        },
        "model_contract": {
            "scikit_learn_version": "1.5.2",
            "forest_parameters": FOREST_PARAMETERS,
            "regression_target": "log1p(PAR10 runtime), one forest per solver",
            "classification_target": "lexically first virtual-best solver",
            "classification_class_weight": "balanced_subsample",
            "numeric_imputation": "outer-training median plus missing indicator",
            "categorical_encoding": "outer-training categories plus unknown/missing one-hot",
            "runstatus_encoding": list(STATUS_CATEGORIES),
            "no_hyperparameter_search": True,
        },
        "comparison_contract": {
            "same_representation_cost_matched": True,
            "dominance": "timeout no worse, worst-5%-mean strictly lower, mean strictly lower",
            "source_cv_repetition": 1,
            "control_split": "balanced SHA256(instance_id) round-robin",
            "tail_fraction": TAIL_FRACTION,
            "same_oracle_baseline": "statewise virtual-best PAR10 runtime with zero feature cost",
        },
        "scenarios": scenarios,
        "portfolio": {
            "scenario_count": len(scenarios),
            "terminal_histogram": dict(sorted(terminal_histogram.items())),
        },
        "controls": {
            "registry_fixed_before_outcomes": True,
            "all_blob_bindings_verified": True,
            "every_arm_one_out_of_fold_prediction_per_instance": all(
                all(
                    all(arm["instance_count"] == scenario["corpus"]["instance_count"] for arm in split["arms"].values())
                    for split in scenario["splits"]
                )
                for scenario in scenarios
            ),
            "same_steps_arms_share_fiberguard_representation": True,
            "all_models_use_train_only_imputation": True,
            "all_models_have_deterministic_random_states": True,
        },
        "authority": {
            "prospective_untouched_comparator_evidence": True,
            "same_owner_implementation": True,
            "strongest_configured_or_censor_aware_selector": False,
            "domain_expert_family_independence": False,
            "external_replay": False,
            "production_value": False,
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def self_test() -> dict[str, bool]:
    assert deterministic_seed("a", 1) == deterministic_seed("a", 1)
    assert deterministic_seed("a", 1) != deterministic_seed("a", 2)
    names = ("train-a", "train-b", "test")
    values = {
        "train-a": {"f": "1"},
        "train-b": {"f": "3"},
        "test": {"f": "1000"},
    }
    statuses = {name: {"s": "ok"} for name in names}
    x_train, x_test, receipt = build_train_test_matrix(
        (0,),
        (0, 1),
        (2,),
        ("s",),
        {"s": {"provides": ["f"]}},
        values,
        statuses,
        names,
    )
    assert x_train[:, 0].tolist() == [1.0, 3.0]
    assert x_test[:, 0].tolist() == [1000.0]
    assert receipt["matrix_dimension"] == 9
    better = {
        "selected_solver_timeout_rate": 0.1,
        "worst_5_percent_mean_total_excess": 5,
        "mean_total_excess": 2,
    }
    worse = {
        "selected_solver_timeout_rate": 0.2,
        "worst_5_percent_mean_total_excess": 6,
        "mean_total_excess": 3,
    }
    assert dominates(better, worse)
    assert not dominates(worse, better)
    return {
        "deterministic_seed": True,
        "train_only_matrix_contract": True,
        "dominance_contract": True,
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
        f"sha256={sha256_bytes(payload.encode())}",
        f"terminal_histogram={canonical_json(result['portfolio']['terminal_histogram'])}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
