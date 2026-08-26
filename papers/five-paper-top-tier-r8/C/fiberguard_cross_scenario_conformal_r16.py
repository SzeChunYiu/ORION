#!/usr/bin/env python3
"""Prospective cross-scenario conformal FiberGuard audit for SAT portfolios."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor

import fiberguard_aslib_sat12_all_r11 as r11

SCHEMA = "ORION.FiberGuard.CrossScenarioConformal.R16.v1"
TERMINAL_PREFIX = "FIBERGUARD_R16"
STATUS_LEVELS = ("ok", "presolved", "timeout", "memout", "crash", "other")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def percentile_higher(values: np.ndarray, probability: float) -> float:
    ordered = np.sort(np.asarray(values, dtype=float))
    index = min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1)
    return float(ordered[index])


def normalize_feature(name: str) -> str:
    value = name
    if value.upper().startswith("BASE-"):
        value = value[5:]
    return "".join(character for character in value.upper() if character.isalnum())


def validate_protocol(protocol: dict[str, Any]) -> None:
    if protocol["schema"] != "ORION.FiberGuard.CrossScenarioConformal.Protocol.R16.v1":
        raise ValueError("unexpected protocol schema")
    if protocol["parent_commit"] != "e431e9f187667431858f42e236bd74e57f658c31":
        raise ValueError("unexpected protocol parent")
    upstream = protocol["upstream"]
    if upstream["commit"] != "551b22beef8df17de59286b4822ef720e0aa4d6f":
        raise ValueError("unexpected ASlib commit")
    if protocol["split"]["official_cv_repetition"] != 1:
        raise ValueError("only official CV repetition 1 is admissible")
    if protocol["split"]["expected_folds"] != 10:
        raise ValueError("expected ten folds")
    if protocol["authority"]["SAT12_ALL_may_not_select_any_R16_parameter"] is not True:
        raise ValueError("SAT12 exclusion must remain hard")


def load_cv(path: Path, instances: list[str], repetition: int) -> dict[str, int]:
    attrs, rows = r11.read_arff(path)
    required = ("instance_id", "repetition", "fold")
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
        raise ValueError(f"CV misses {len(allowed - set(assignment))} admitted instances")
    if sorted(set(assignment.values())) != list(range(1, 11)):
        raise ValueError("unexpected CV fold set")
    return assignment


def verify_files(root: Path, expected: dict[str, str]) -> dict[str, Any]:
    audit: dict[str, Any] = {}
    for name, expected_blob in expected.items():
        path = root / name
        actual = r11.git_blob_sha(path)
        if actual != expected_blob:
            raise ValueError(f"blob mismatch for {path}: {actual} != {expected_blob}")
        audit[name] = {
            "git_blob_sha1": actual,
            "sha256": r11.sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return audit


def step_feature_map(
    description: dict[str, Any], step: str
) -> dict[str, str]:
    steps = dict(description["feature_steps"])
    if step not in steps:
        raise ValueError(f"missing declared step {step}")
    provides = steps[step].get("provides", []) or []
    if isinstance(provides, str):
        provides = [provides]
    mapping: dict[str, str] = {}
    for original in provides:
        canonical = normalize_feature(original)
        if canonical in mapping and mapping[canonical] != original:
            raise ValueError(
                f"canonical feature collision: {mapping[canonical]!r}, {original!r}"
            )
        mapping[canonical] = original
    return mapping


def load_scenario(root: Path, spec: dict[str, Any], repetition: int) -> dict[str, Any]:
    name = spec["name"]
    scenario_root = root / name
    source_audit = verify_files(scenario_root, spec["files"])
    description = yaml.safe_load((scenario_root / "description.txt").read_text())
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time", cutoff)
    feature_cutoff = cutoff if feature_cutoff_raw in {None, "?"} else float(feature_cutoff_raw)
    step = spec["acquisition_step"]
    feature_map = step_feature_map(description, step)

    runtimes_by_instance, algorithms, algorithm_audit = r11.load_algorithm_runs(
        scenario_root / "algorithm_runs.arff", cutoff
    )
    feature_values, feature_names = r11.load_feature_values(
        scenario_root / "feature_values.arff"
    )
    feature_costs, cost_steps = r11.load_step_table(
        scenario_root / "feature_costs.arff", numeric=True
    )
    feature_status, status_steps = r11.load_step_table(
        scenario_root / "feature_runstatus.arff", numeric=False
    )
    if step not in cost_steps or step not in status_steps:
        raise ValueError(f"paid step {step} missing from feature cost/status tables")

    instances = sorted(
        set(runtimes_by_instance)
        & set(feature_values)
        & set(feature_costs)
        & set(feature_status)
    )
    if set(instances) != set(runtimes_by_instance):
        raise ValueError(f"feature data do not cover complete solver matrix for {name}")

    runtimes = np.asarray(
        [
            [runtimes_by_instance[instance][algorithm] for algorithm in algorithms]
            for instance in instances
        ],
        dtype=float,
    )
    oracle = np.min(runtimes, axis=1)
    regret = runtimes - oracle[:, None]
    acquisition = np.asarray(
        [
            r11.feature_cost(
                instance,
                (step,),
                feature_costs,
                feature_status,
                feature_cutoff,
            )
            for instance in instances
        ],
        dtype=float,
    )
    status = np.asarray(
        [str(feature_status.get(instance, {}).get(step, "other")) for instance in instances],
        dtype=object,
    )
    cv = load_cv(scenario_root / "cv.arff", instances, repetition)
    fold = np.asarray([cv[instance] for instance in instances], dtype=np.int32)
    return {
        "name": name,
        "instances": instances,
        "algorithms": algorithms,
        "runtimes": runtimes,
        "oracle": oracle,
        "regret": regret,
        "acquisition": acquisition,
        "status": status,
        "feature_values": feature_values,
        "feature_names": feature_names,
        "feature_map": feature_map,
        "fold": fold,
        "cutoff": cutoff,
        "par10": 10.0 * cutoff,
        "source_audit": source_audit,
        "algorithm_audit": algorithm_audit,
    }


def common_feature_schema(
    scenarios: list[dict[str, Any]], minimum: int
) -> list[str]:
    common = set(scenarios[0]["feature_map"])
    for scenario in scenarios[1:]:
        common &= set(scenario["feature_map"])
    ordered = sorted(common)
    if len(ordered) < minimum:
        raise ValueError(f"only {len(ordered)} portable features; need {minimum}")
    return ordered


def raw_feature_matrix(
    scenario: dict[str, Any], common: list[str]
) -> np.ndarray:
    matrix = np.full((len(scenario["instances"]), len(common)), np.nan, dtype=float)
    for row, instance in enumerate(scenario["instances"]):
        values = scenario["feature_values"].get(instance, {})
        for column, canonical in enumerate(common):
            original = scenario["feature_map"][canonical]
            value = values.get(original, "?")
            if value != "?":
                matrix[row, column] = float(value)
    return matrix


def status_matrix(values: np.ndarray) -> np.ndarray:
    mapping = {name: index for index, name in enumerate(STATUS_LEVELS)}
    output = np.zeros((len(values), len(STATUS_LEVELS)), dtype=float)
    for row, raw in enumerate(values):
        value = str(raw)
        value = value if value in mapping else "other"
        output[row, mapping[value]] = 1.0
    return output


def preprocess(
    raw: np.ndarray,
    status: np.ndarray,
    train: np.ndarray,
    *targets: np.ndarray,
) -> tuple[np.ndarray, ...]:
    train_numeric = raw[train].copy()
    median = np.nanmedian(train_numeric, axis=0)
    median = np.where(np.isfinite(median), median, 0.0)
    train_imputed = np.where(np.isnan(train_numeric), median, train_numeric)
    mean = np.mean(train_imputed, axis=0)
    scale = np.std(train_imputed, axis=0)
    scale = np.where(scale > 0, scale, 1.0)

    def transform(index: np.ndarray) -> np.ndarray:
        numeric = raw[index].copy()
        missing = np.isnan(numeric).astype(float)
        numeric = np.where(np.isnan(numeric), median, numeric)
        numeric = (numeric - mean) / scale
        return np.concatenate((numeric, missing, status[index]), axis=1)

    return tuple(transform(index) for index in (train,) + targets)


def model_specs(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    candidates = protocol["model_candidates"]
    for neighbors in candidates["knn"]["neighbors"]:
        output.append(
            {
                "family": "knn",
                "neighbors": int(neighbors),
                "weights": candidates["knn"]["weights"],
            }
        )
    extra = candidates["extra_trees"]
    for leaf in extra["min_samples_leaf"]:
        for max_features in extra["max_features"]:
            output.append(
                {
                    "family": "extra_trees",
                    "n_estimators": int(extra["n_estimators"]),
                    "min_samples_leaf": int(leaf),
                    "max_features": float(max_features),
                    "random_state": int(extra["random_state"]),
                    "n_jobs": int(extra["n_jobs"]),
                }
            )
    forest = candidates["random_forest"]
    for leaf in forest["min_samples_leaf"]:
        for max_features in forest["max_features"]:
            output.append(
                {
                    "family": "random_forest",
                    "n_estimators": int(forest["n_estimators"]),
                    "min_samples_leaf": int(leaf),
                    "max_features": float(max_features),
                    "random_state": int(forest["random_state"]),
                    "n_jobs": int(forest["n_jobs"]),
                }
            )
    return sorted(output, key=config_key)


def config_key(spec: dict[str, Any]) -> tuple[Any, ...]:
    return (
        spec["family"],
        tuple((key, canonical_json(value)) for key, value in sorted(spec.items()) if key != "family"),
    )


def build_model(spec: dict[str, Any], training_count: int):
    family = spec["family"]
    if family == "knn":
        return KNeighborsRegressor(
            n_neighbors=min(int(spec["neighbors"]), training_count),
            weights=spec["weights"],
            metric="euclidean",
            n_jobs=1,
        )
    if family == "extra_trees":
        return ExtraTreesRegressor(
            n_estimators=int(spec["n_estimators"]),
            min_samples_leaf=int(spec["min_samples_leaf"]),
            max_features=float(spec["max_features"]),
            random_state=int(spec["random_state"]),
            n_jobs=int(spec["n_jobs"]),
        )
    if family == "random_forest":
        return RandomForestRegressor(
            n_estimators=int(spec["n_estimators"]),
            min_samples_leaf=int(spec["min_samples_leaf"]),
            max_features=float(spec["max_features"]),
            random_state=int(spec["random_state"]),
            n_jobs=int(spec["n_jobs"]),
        )
    raise ValueError(f"unknown model family {family}")


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    ordered = np.sort(np.asarray(scores, dtype=float))
    rank = math.ceil((len(ordered) + 1) * (1.0 - alpha))
    if rank > len(ordered):
        return math.inf
    return float(ordered[rank - 1])


def nested_predictions(
    scenario: dict[str, Any],
    raw: np.ndarray,
    encoded_status: np.ndarray,
    spec: dict[str, Any],
    alphas: list[float],
) -> dict[str, Any]:
    n = len(scenario["instances"])
    proposal_solver = np.full(n, -1, dtype=np.int32)
    predicted_selected = np.full(n, np.nan)
    proposal_regret = np.full(n, np.nan)
    proposal_runtime = np.full(n, np.nan)
    fallback_solver = np.full(n, -1, dtype=np.int32)
    fallback_regret = np.full(n, np.nan)
    fallback_runtime = np.full(n, np.nan)
    sbs_regret = np.full(n, np.nan)
    sbs_runtime = np.full(n, np.nan)
    quantile = {alpha: np.full(n, np.nan) for alpha in alphas}
    fold_rows: list[dict[str, Any]] = []

    for test_fold in range(1, 11):
        calibration_fold = 1 + (test_fold % 10)
        test = np.flatnonzero(scenario["fold"] == test_fold)
        calibration = np.flatnonzero(scenario["fold"] == calibration_fold)
        training = np.flatnonzero(
            (scenario["fold"] != test_fold)
            & (scenario["fold"] != calibration_fold)
        )
        if not len(test) or not len(calibration) or not len(training):
            raise ValueError(f"empty nested split in {scenario['name']} fold {test_fold}")
        train_x, cal_x, test_x = preprocess(
            raw, encoded_status, training, calibration, test
        )
        model = build_model(spec, len(training))
        model.fit(train_x, scenario["regret"][training])
        cal_prediction = np.maximum(0.0, np.asarray(model.predict(cal_x), dtype=float))
        test_prediction = np.maximum(0.0, np.asarray(model.predict(test_x), dtype=float))
        if cal_prediction.ndim == 1:
            cal_prediction = cal_prediction[:, None]
            test_prediction = test_prediction[:, None]
        cal_action = np.argmin(cal_prediction, axis=1).astype(np.int32)
        test_action = np.argmin(test_prediction, axis=1).astype(np.int32)
        cal_selected_prediction = cal_prediction[np.arange(len(calibration)), cal_action]
        test_selected_prediction = test_prediction[np.arange(len(test)), test_action]
        cal_selected_regret = scenario["regret"][calibration, cal_action]
        scores = cal_selected_regret - cal_selected_prediction

        robust = int(np.argmin(np.max(scenario["regret"][training], axis=0)))
        sbs = int(np.argmin(np.mean(scenario["runtimes"][training], axis=0)))

        proposal_solver[test] = test_action
        predicted_selected[test] = test_selected_prediction
        proposal_regret[test] = scenario["regret"][test, test_action]
        proposal_runtime[test] = scenario["runtimes"][test, test_action]
        fallback_solver[test] = robust
        fallback_regret[test] = scenario["regret"][test, robust]
        fallback_runtime[test] = scenario["runtimes"][test, robust]
        sbs_regret[test] = scenario["regret"][test, sbs]
        sbs_runtime[test] = scenario["runtimes"][test, sbs]
        fold_quantile = {}
        for alpha in alphas:
            value = conformal_quantile(scores, alpha)
            quantile[alpha][test] = value
            fold_quantile[str(alpha)] = value
        fold_rows.append(
            {
                "test_fold": test_fold,
                "calibration_fold": calibration_fold,
                "proper_training_count": len(training),
                "calibration_count": len(calibration),
                "test_count": len(test),
                "robust_fallback_solver": scenario["algorithms"][robust],
                "single_best_solver": scenario["algorithms"][sbs],
                "conformal_quantiles": fold_quantile,
            }
        )

    arrays = (
        proposal_solver,
        predicted_selected,
        proposal_regret,
        proposal_runtime,
        fallback_solver,
        fallback_regret,
        fallback_runtime,
        sbs_regret,
        sbs_runtime,
    )
    if any(np.isnan(array).any() for array in arrays[1:]):
        raise AssertionError("nested prediction did not cover every instance")
    if (proposal_solver < 0).any() or (fallback_solver < 0).any():
        raise AssertionError("solver assignment missing")
    return {
        "proposal_solver": proposal_solver,
        "predicted_selected": predicted_selected,
        "proposal_regret": proposal_regret,
        "proposal_runtime": proposal_runtime,
        "fallback_solver": fallback_solver,
        "fallback_regret": fallback_regret,
        "fallback_runtime": fallback_runtime,
        "sbs_regret": sbs_regret,
        "sbs_runtime": sbs_runtime,
        "quantile": quantile,
        "folds": fold_rows,
    }


def metric_summary(
    loss: np.ndarray,
    runtime: np.ndarray,
    feature_cost: np.ndarray,
    scenario: dict[str, Any],
    deploy: np.ndarray | None = None,
    false_certificate: np.ndarray | None = None,
) -> dict[str, Any]:
    catastrophic = (runtime >= scenario["par10"] - 1e-9) & (
        scenario["oracle"] < scenario["par10"] - 1e-9
    )
    output: dict[str, Any] = {
        "mean_total_excess": float(np.mean(loss)),
        "median_total_excess": float(np.median(loss)),
        "p95_total_excess": percentile_higher(loss, 0.95),
        "maximum_total_excess": float(np.max(loss)),
        "mean_feature_cost": float(np.mean(feature_cost)),
        "maximum_feature_cost": float(np.max(feature_cost)),
        "catastrophic_wrong_action_count": int(np.sum(catastrophic)),
        "catastrophic_wrong_action_rate": float(np.mean(catastrophic)),
    }
    if deploy is not None:
        coverage = float(np.mean(deploy))
        output["deployment_count"] = int(np.sum(deploy))
        output["deployment_coverage"] = coverage
    if false_certificate is not None:
        output["joint_false_certificate_count"] = int(np.sum(false_certificate))
        output["joint_false_certificate_rate"] = float(np.mean(false_certificate))
        if deploy is not None and np.any(deploy):
            output["conditional_false_certificate_rate"] = float(
                np.sum(false_certificate) / np.sum(deploy)
            )
        else:
            output["conditional_false_certificate_rate"] = None
    return output


def full_model_summary(
    scenario: dict[str, Any], predictions: dict[str, Any]
) -> dict[str, Any]:
    cost = scenario["acquisition"]
    return metric_summary(
        cost + predictions["proposal_regret"],
        predictions["proposal_runtime"],
        cost,
        scenario,
    )


def fallback_summary(
    scenario: dict[str, Any], predictions: dict[str, Any]
) -> dict[str, Any]:
    zeros = np.zeros(len(scenario["instances"]))
    return metric_summary(
        predictions["fallback_regret"],
        predictions["fallback_runtime"],
        zeros,
        scenario,
    )


def sbs_summary(
    scenario: dict[str, Any], predictions: dict[str, Any]
) -> dict[str, Any]:
    zeros = np.zeros(len(scenario["instances"]))
    return metric_summary(
        predictions["sbs_regret"],
        predictions["sbs_runtime"],
        zeros,
        scenario,
    )


def selective_summary(
    scenario: dict[str, Any],
    predictions: dict[str, Any],
    alpha: float,
    epsilon_fraction: float,
) -> dict[str, Any]:
    epsilon = epsilon_fraction * scenario["cutoff"]
    upper = np.maximum(
        0.0,
        predictions["predicted_selected"] + predictions["quantile"][alpha],
    )
    deploy = upper <= epsilon
    selected_regret = np.where(
        deploy, predictions["proposal_regret"], predictions["fallback_regret"]
    )
    selected_runtime = np.where(
        deploy, predictions["proposal_runtime"], predictions["fallback_runtime"]
    )
    false_certificate = deploy & (predictions["proposal_regret"] > epsilon + 1e-12)
    output = metric_summary(
        scenario["acquisition"] + selected_regret,
        selected_runtime,
        scenario["acquisition"],
        scenario,
        deploy,
        false_certificate,
    )
    output.update(
        {
            "alpha": alpha,
            "epsilon_fraction": epsilon_fraction,
            "epsilon": epsilon,
            "maximum_finite_upper_bound": float(
                np.max(upper[np.isfinite(upper)])
            )
            if np.isfinite(upper).any()
            else None,
            "infinite_upper_bound_count": int(np.sum(~np.isfinite(upper))),
        }
    )
    return output


def frozen_reference_specs(protocol: dict[str, Any]) -> dict[str, dict[str, Any]]:
    knn = dict(protocol["frozen_reference_baselines"]["knn"])
    knn["family"] = "knn"
    extra = dict(protocol["frozen_reference_baselines"]["extra_trees"])
    extra["family"] = "extra_trees"
    return {"frozen_knn": knn, "frozen_extra_trees": extra}


def development_search(
    scenario: dict[str, Any],
    raw: np.ndarray,
    encoded_status: np.ndarray,
    protocol: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    alphas = [float(value) for value in protocol["certificate_candidates"]["alpha"]]
    epsilons = [
        float(value)
        for value in protocol["certificate_candidates"]["epsilon_cutoff_fraction"]
    ]
    fallback: dict[str, Any] | None = None
    candidates: list[dict[str, Any]] = []
    predictions_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for spec in model_specs(protocol):
        predictions = nested_predictions(
            scenario, raw, encoded_status, spec, alphas
        )
        predictions_by_key[config_key(spec)] = predictions
        full = full_model_summary(scenario, predictions)
        if fallback is None:
            fallback = fallback_summary(scenario, predictions)
        for alpha in alphas:
            for epsilon_fraction in epsilons:
                selective = selective_summary(
                    scenario, predictions, alpha, epsilon_fraction
                )
                feasible = (
                    selective["deployment_coverage"] >= 0.1
                    and selective["mean_total_excess"]
                    <= fallback["mean_total_excess"] + 1e-12
                    and selective["p95_total_excess"]
                    <= fallback["p95_total_excess"] + 1e-12
                    and selective["catastrophic_wrong_action_rate"]
                    < full["catastrophic_wrong_action_rate"] - 1e-12
                )
                objective = (
                    selective["mean_total_excess"],
                    selective["catastrophic_wrong_action_rate"],
                    selective["p95_total_excess"],
                    -selective["deployment_coverage"],
                    config_key(spec),
                    alpha,
                    epsilon_fraction,
                )
                candidates.append(
                    {
                        "spec": spec,
                        "alpha": alpha,
                        "epsilon_fraction": epsilon_fraction,
                        "feasible": feasible,
                        "objective": objective,
                        "full": full,
                        "selective": selective,
                    }
                )
    feasible_rows = [row for row in candidates if row["feasible"]]
    selected = min(feasible_rows or candidates, key=lambda row: row["objective"])
    selected_predictions = predictions_by_key[config_key(selected["spec"])]
    assert fallback is not None
    return selected, {
        "candidate_count": len(candidates),
        "feasible_candidate_count": len(feasible_rows),
        "development_gate": bool(feasible_rows),
        "selected_spec": selected["spec"],
        "selected_alpha": selected["alpha"],
        "selected_epsilon_fraction": selected["epsilon_fraction"],
        "selected_full": selected["full"],
        "selected_selective": selected["selective"],
        "fallback": fallback,
        "single_best_solver": sbs_summary(scenario, selected_predictions),
        "folds": selected_predictions["folds"],
    }


def evaluate_scenario(
    scenario: dict[str, Any],
    raw: np.ndarray,
    encoded_status: np.ndarray,
    selected: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    alpha = float(selected["alpha"])
    epsilon_fraction = float(selected["epsilon_fraction"])
    chosen_predictions = nested_predictions(
        scenario, raw, encoded_status, selected["spec"], [alpha]
    )
    references = {}
    for name, spec in frozen_reference_specs(protocol).items():
        predictions = nested_predictions(scenario, raw, encoded_status, spec, [alpha])
        references[name] = full_model_summary(scenario, predictions)
    full = full_model_summary(scenario, chosen_predictions)
    selective = selective_summary(
        scenario, chosen_predictions, alpha, epsilon_fraction
    )
    fallback = fallback_summary(scenario, chosen_predictions)
    sbs = sbs_summary(scenario, chosen_predictions)
    gain = fallback["mean_total_excess"] - full["mean_total_excess"]
    gate = (
        gain > 1e-12
        and selective["mean_total_excess"]
        <= full["mean_total_excess"] + 0.1 * gain + 1e-12
        and selective["catastrophic_wrong_action_rate"]
        < full["catastrophic_wrong_action_rate"] - 1e-12
        and selective["p95_total_excess"]
        <= fallback["p95_total_excess"] + 1e-12
        and selective["deployment_coverage"] >= 0.1
        and selective["joint_false_certificate_rate"] <= alpha + 0.02 + 1e-12
    )
    return {
        "gate": gate,
        "selected_spec": selected["spec"],
        "alpha": alpha,
        "epsilon_fraction": epsilon_fraction,
        "single_best_solver": sbs,
        "robust_fallback": fallback,
        "selected_full_model": full,
        "selected_selective_model": selective,
        "frozen_reference_models": references,
        "folds": chosen_predictions["folds"],
    }


def compact_panel(panel: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "gate",
        "selected_spec",
        "alpha",
        "epsilon_fraction",
        "single_best_solver",
        "robust_fallback",
        "selected_full_model",
        "selected_selective_model",
        "frozen_reference_models",
    )
    return {key: panel[key] for key in keys}


def run(
    root: Path,
    protocol_path: Path,
    protocol_commit: str,
    script_path: Path,
) -> dict[str, Any]:
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    validate_protocol(protocol)
    repetition = int(protocol["split"]["official_cv_repetition"])
    scenario_specs = protocol["scenarios"]
    development = load_scenario(root, scenario_specs["development"], repetition)
    validation = load_scenario(root, scenario_specs["validation"], repetition)
    test = load_scenario(root, scenario_specs["test"], repetition)
    scenarios = [development, validation, test]
    common = common_feature_schema(
        scenarios,
        int(protocol["portable_representation"]["minimum_common_features"]),
    )
    matrices = {scenario["name"]: raw_feature_matrix(scenario, common) for scenario in scenarios}
    statuses = {scenario["name"]: status_matrix(scenario["status"]) for scenario in scenarios}

    selected, development_result = development_search(
        development,
        matrices[development["name"]],
        statuses[development["name"]],
        protocol,
    )
    validation_result = evaluate_scenario(
        validation,
        matrices[validation["name"]],
        statuses[validation["name"]],
        selected,
        protocol,
    )
    test_result = evaluate_scenario(
        test,
        matrices[test["name"]],
        statuses[test["name"]],
        selected,
        protocol,
    )

    if development_result["development_gate"] and validation_result["gate"] and test_result["gate"]:
        terminal = f"{TERMINAL_PREFIX}_CROSS_SCENARIO_CERTIFICATE_PASS_VALIDATION_AND_TEST"
    elif development_result["development_gate"] and validation_result["gate"]:
        terminal = f"{TERMINAL_PREFIX}_VALIDATION_PASS__UNTOUCHED_TEST_FAIL"
    elif development_result["development_gate"]:
        terminal = f"{TERMINAL_PREFIX}_DEVELOPMENT_ONLY__VALIDATION_FAIL"
    else:
        terminal = f"{TERMINAL_PREFIX}_NO_PORTABLE_CERTIFICATE_VALUE"

    scenario_result = {}
    for scenario in scenarios:
        scenario_result[scenario["name"]] = {
            "instance_count": len(scenario["instances"]),
            "algorithm_count": len(scenario["algorithms"]),
            "feature_count": len(scenario["feature_names"]),
            "common_portable_feature_count": len(common),
            "cutoff": scenario["cutoff"],
            "par10": scenario["par10"],
            "source_audit": scenario["source_audit"],
            "algorithm_audit": scenario["algorithm_audit"],
            "fold_counts": dict(
                sorted(collections.Counter(scenario["fold"].tolist()).items())
            ),
        }

    return {
        "schema": SCHEMA,
        "terminal": terminal,
        "prospective_binding": {
            "protocol_parent_commit": protocol["parent_commit"],
            "protocol_execution_commit": protocol_commit,
            "protocol_sha256": sha256_bytes(protocol_bytes),
            "implementation_sha256": r11.sha256_file(script_path),
            "result_absent_from_protocol_inputs": True,
        },
        "upstream": protocol["upstream"],
        "portable_representation": {
            "common_feature_count": len(common),
            "common_features": common,
            "canonical_collision_count": 0,
        },
        "scenarios": scenario_result,
        "development": development_result,
        "validation": validation_result,
        "test": test_result,
        "controls": {
            "SAT12_not_used_for_R16_selection": True,
            "development_only_selects_configuration": True,
            "validation_does_not_retune": True,
            "test_does_not_retune": True,
            "different_solver_portfolios_refit_within_scenario": True,
            "one_common_statewise_oracle_per_scenario": True,
            "feature_cost_paid_by_all_learned_and_selective_arms": True,
            "official_nested_folds_complete": True,
            "conditional_and_marginal_certificate_rates_separate": True,
        },
        "authority": {
            "method_configuration_transfers_across_three_pinned_scenarios": True,
            "split_conformal_guarantee": "MARGINAL_UNDER_EXCHANGEABILITY",
            "worst_case_fibre_safety": False,
            "family_shift_validity": False,
            "strongest_algorithm_selection_baseline_complete": False,
            "external_independence": False,
            "production_deployment_value": False,
            "novelty": "CANNOT_CHECK",
            "grants_journal_authority": False,
        },
    }


def compact_summary(result: dict[str, Any], digest: str) -> dict[str, Any]:
    return {
        "schema": result["schema"],
        "terminal": result["terminal"],
        "protocol_execution_commit": result["prospective_binding"]["protocol_execution_commit"],
        "protocol_sha256": result["prospective_binding"]["protocol_sha256"],
        "full_result_sha256": digest,
        "portable_representation": result["portable_representation"],
        "development": {
            "development_gate": result["development"]["development_gate"],
            "candidate_count": result["development"]["candidate_count"],
            "feasible_candidate_count": result["development"]["feasible_candidate_count"],
            "selected_spec": result["development"]["selected_spec"],
            "selected_alpha": result["development"]["selected_alpha"],
            "selected_epsilon_fraction": result["development"]["selected_epsilon_fraction"],
            "selected_full": result["development"]["selected_full"],
            "selected_selective": result["development"]["selected_selective"],
            "fallback": result["development"]["fallback"],
        },
        "validation": compact_panel(result["validation"]),
        "test": compact_panel(result["test"]),
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

    result = run(
        args.aslib_root,
        args.protocol,
        args.protocol_commit,
        Path(__file__),
    )
    payload = canonical_json(result) + "\n"
    digest = sha256_bytes(payload.encode())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    summary = compact_summary(result, digest)
    comment = (
        "## FiberGuard R16 prospective cross-scenario terminal\n\n"
        f"Protocol execution commit: `{args.protocol_commit}`\n\n"
        f"Terminal: `{result['terminal']}`\n\n"
        f"Full result SHA-256: `{digest}`\n\n"
        "```json\n"
        + json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False)
        + "\n```\n"
    )
    args.comment_output.write_text(comment, encoding="utf-8")
    print(
        result["terminal"],
        f"protocol_commit={args.protocol_commit}",
        f"result_sha256={digest}",
        f"development_gate={result['development']['development_gate']}",
        f"validation_gate={result['validation']['gate']}",
        f"test_gate={result['test']['gate']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
