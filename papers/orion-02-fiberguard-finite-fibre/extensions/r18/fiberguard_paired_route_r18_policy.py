"""Model fitting, conformal routing, and gate evaluation for R18 recovery."""
from __future__ import annotations

import math
from typing import Any, Iterable

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor

STATUS_LEVELS = ("ok", "presolved", "timeout", "memout", "crash", "other")


def canonical_model_specs(protocol: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    candidates = protocol["model_candidates"]
    rows: list[dict[str, Any]] = []
    for neighbors in candidates["knn"]["neighbors"]:
        rows.append(
            {
                "family": "knn",
                "neighbors": int(neighbors),
                "weights": str(candidates["knn"]["weights"]),
            }
        )
    for leaf in candidates["extra_trees"]["min_samples_leaf"]:
        for max_features in candidates["extra_trees"]["max_features"]:
            rows.append(
                {
                    "family": "extra_trees",
                    "n_estimators": int(candidates["extra_trees"]["n_estimators"]),
                    "min_samples_leaf": int(leaf),
                    "max_features": float(max_features),
                    "random_state": int(candidates["extra_trees"]["random_state"]),
                    "n_jobs": int(candidates["extra_trees"]["n_jobs"]),
                }
            )
    for leaf in candidates["random_forest"]["min_samples_leaf"]:
        for max_features in candidates["random_forest"]["max_features"]:
            rows.append(
                {
                    "family": "random_forest",
                    "n_estimators": int(candidates["random_forest"]["n_estimators"]),
                    "min_samples_leaf": int(leaf),
                    "max_features": float(max_features),
                    "random_state": int(candidates["random_forest"]["random_state"]),
                    "n_jobs": int(candidates["random_forest"]["n_jobs"]),
                }
            )
    if len(rows) != 11:
        raise AssertionError(f"frozen R18 model denominator changed: {len(rows)}")
    return tuple(rows)


def model_key(spec: dict[str, Any]) -> str:
    parts = [str(spec["family"])]
    for key in sorted(name for name in spec if name != "family"):
        parts.append(f"{key}={spec[key]}")
    return "|".join(parts)


def _fit_transform(
    raw: np.ndarray,
    runstatus: np.ndarray,
    train_idx: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    train_raw = raw[train_idx]
    with np.errstate(all="ignore"):
        medians = np.nanmedian(train_raw, axis=0)
    all_missing = ~np.isfinite(medians)
    medians = np.where(np.isfinite(medians), medians, 0.0)
    missing = ~np.isfinite(raw)
    imputed = np.where(missing, medians[None, :], raw)
    train_imputed = imputed[train_idx]
    mean = np.mean(train_imputed, axis=0)
    scale = np.std(train_imputed, axis=0)
    scale = np.where(scale < 1e-12, 1.0, scale)
    numeric = (imputed - mean[None, :]) / scale[None, :]
    missing_bits = missing.astype(float)
    status_bits = np.column_stack(
        [(runstatus == status).astype(float) for status in STATUS_LEVELS]
    )
    design = np.concatenate([numeric, missing_bits, status_bits], axis=1)
    return design, {
        "raw_dimension": int(raw.shape[1]),
        "design_dimension": int(design.shape[1]),
        "all_missing_training_features": int(np.sum(all_missing)),
    }


def outer_fold_indices(folds: np.ndarray, test_fold: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    calibration_fold = 1 + (test_fold % 10)
    test_idx = np.flatnonzero(folds == test_fold)
    calibration_idx = np.flatnonzero(folds == calibration_fold)
    train_idx = np.flatnonzero((folds != test_fold) & (folds != calibration_fold))
    if min(len(test_idx), len(calibration_idx), len(train_idx)) == 0:
        raise ValueError(f"empty R18 nested split at test fold {test_fold}")
    return train_idx, calibration_idx, test_idx


def _build_model(spec: dict[str, Any], train_size: int):
    family = spec["family"]
    if family == "knn":
        return KNeighborsRegressor(
            n_neighbors=min(int(spec["neighbors"]), train_size),
            weights=str(spec["weights"]),
            metric="minkowski",
            p=2,
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
    raise ValueError(f"unknown model family: {family}")


def fit_predict_regret(
    spec: dict[str, Any],
    X_train: np.ndarray,
    regret_train: np.ndarray,
    X_calibration: np.ndarray,
    X_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    model = _build_model(spec, len(X_train))
    model.fit(X_train, regret_train)
    cal = np.maximum(np.asarray(model.predict(X_calibration), dtype=float), 0.0)
    test = np.maximum(np.asarray(model.predict(X_test), dtype=float), 0.0)
    if cal.ndim == 1:
        cal = cal[:, None]
    if test.ndim == 1:
        test = test[:, None]
    return cal, test


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    values = np.sort(np.asarray(scores, dtype=float))
    n = len(values)
    if n == 0:
        return float("inf")
    rank = int(math.ceil((n + 1) * (1.0 - float(alpha))))
    if rank > n:
        return float("inf")
    return float(values[rank - 1])


def _route_from_predictions(
    mode: str,
    alpha: float,
    calibration: dict[str, np.ndarray],
    test: dict[str, np.ndarray],
) -> dict[str, Any]:
    L_cal = calibration["L"]
    F_cal = calibration["F"]
    Lhat_cal = calibration["Lhat"]
    Fhat_cal = calibration["Fhat"]
    L_test = test["L"]
    F_test = test["F"]
    Lhat_test = test["Lhat"]
    Fhat_test = test["Fhat"]
    if mode == "paired_upper":
        cal_score = np.maximum(L_cal - Lhat_cal, F_cal - Fhat_cal)
        test_score = np.maximum(L_test - Lhat_test, F_test - Fhat_test)
        q = conformal_quantile(cal_score, alpha)
        fallback = (Fhat_test + q) < (Lhat_test + q)
    elif mode == "interval_no_harm":
        cal_score = np.maximum(np.abs(L_cal - Lhat_cal), np.abs(F_cal - Fhat_cal))
        test_score = np.maximum(np.abs(L_test - Lhat_test), np.abs(F_test - Fhat_test))
        q = conformal_quantile(cal_score, alpha)
        fallback = (Fhat_test + q) <= np.maximum(0.0, Lhat_test - q)
    elif mode == "direct_difference":
        cal_score = np.abs((F_cal - L_cal) - (Fhat_cal - Lhat_cal))
        test_score = np.abs((F_test - L_test) - (Fhat_test - Lhat_test))
        q = conformal_quantile(cal_score, alpha)
        fallback = (Fhat_test - Lhat_test + q) <= 0.0
    else:
        raise ValueError(f"unknown route mode: {mode}")
    return {
        "fallback": np.asarray(fallback, dtype=bool),
        "violation": np.asarray(test_score > q, dtype=bool),
        "q": q,
        "calibration_size": int(len(cal_score)),
    }


def _one_sided_route(
    alpha: float,
    calibration: dict[str, np.ndarray],
    test: dict[str, np.ndarray],
) -> dict[str, Any]:
    score_cal = calibration["L"] - calibration["Lhat"]
    score_test = test["L"] - test["Lhat"]
    q = conformal_quantile(score_cal, alpha)
    fallback = (test["Lhat"] + q) > test["Fhat"]
    return {
        "fallback": np.asarray(fallback, dtype=bool),
        "violation": np.asarray(score_test > q, dtype=bool),
        "q": q,
        "calibration_size": int(len(score_cal)),
    }


def _metrics(
    data: dict[str, Any],
    actions: np.ndarray,
    *,
    pay_feature: bool,
    route_changed: np.ndarray | None = None,
    violation: np.ndarray | None = None,
) -> dict[str, Any]:
    rows = np.arange(len(actions))
    terminal = data["cost"][rows, actions]
    oracle = np.min(data["cost"], axis=1)
    total = terminal + (data["feature_cost"] if pay_feature else 0.0)
    statuses = data["runstatus"][rows, actions]
    catastrophic = np.isclose(terminal, data["par10"], rtol=1e-9, atol=1e-9)
    result = {
        "n": int(len(actions)),
        "mean_total_cost": float(np.mean(total)),
        "median_total_cost": float(np.median(total)),
        "p95_total_cost": float(np.quantile(total, 0.95, method="higher")),
        "mean_total_excess": float(np.mean(total - oracle)),
        "solve_rate": float(np.mean(statuses == "ok")),
        "timeout_rate": float(np.mean(statuses == "timeout")),
        "non_ok_rate": float(np.mean(statuses != "ok")),
        "catastrophic_rate": float(np.mean(catastrophic)),
        "mean_feature_cost": float(np.mean(data["feature_cost"])) if pay_feature else 0.0,
        "p95_definition": "empirical order statistic via numpy.quantile(method='higher')",
    }
    if route_changed is not None:
        result["route_change_coverage"] = float(np.mean(route_changed))
    if violation is not None:
        result["certificate_failure_rate"] = float(np.mean(violation))
    return result


def build_scenario_predictions(
    data: dict[str, Any],
    model_specs: Iterable[dict[str, Any]],
    reference_specs: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    specs = tuple(model_specs)
    refs = tuple(reference_specs)
    n = len(data["instances"])
    regret = data["cost"] - np.min(data["cost"], axis=1, keepdims=True)
    fallback_actions = np.empty(n, dtype=int)
    models: dict[str, dict[str, Any]] = {
        model_key(spec): {
            "spec": spec,
            "learned_action": np.empty(n, dtype=int),
            "Lhat": np.empty(n, dtype=float),
            "Fhat": np.empty(n, dtype=float),
            "folds": {},
        }
        for spec in specs + refs
    }
    transform_audit: dict[str, Any] = {}
    for test_fold in range(1, 11):
        train_idx, cal_idx, test_idx = outer_fold_indices(data["fold"], test_fold)
        design, audit = _fit_transform(data["raw_features"], data["feature_runstatus"], train_idx)
        transform_audit[str(test_fold)] = {
            **audit,
            "proper_training": int(len(train_idx)),
            "calibration": int(len(cal_idx)),
            "test": int(len(test_idx)),
            "calibration_fold": 1 + (test_fold % 10),
        }
        robust_max = np.max(regret[train_idx], axis=0)
        fallback = int(np.argmin(robust_max))
        fallback_actions[test_idx] = fallback
        for spec in specs + refs:
            key = model_key(spec)
            cal_pred, test_pred = fit_predict_regret(
                spec,
                design[train_idx],
                regret[train_idx],
                design[cal_idx],
                design[test_idx],
            )
            cal_action = np.argmin(cal_pred, axis=1)
            test_action = np.argmin(test_pred, axis=1)
            cal_L = regret[cal_idx, cal_action]
            test_L = regret[test_idx, test_action]
            cal_F = regret[cal_idx, fallback]
            test_F = regret[test_idx, fallback]
            cal_Lhat = cal_pred[np.arange(len(cal_idx)), cal_action]
            test_Lhat = test_pred[np.arange(len(test_idx)), test_action]
            cal_Fhat = cal_pred[:, fallback]
            test_Fhat = test_pred[:, fallback]
            models[key]["learned_action"][test_idx] = test_action
            models[key]["Lhat"][test_idx] = test_Lhat
            models[key]["Fhat"][test_idx] = test_Fhat
            models[key]["folds"][test_fold] = {
                "test_idx": test_idx,
                "fallback_action": fallback,
                "calibration": {
                    "L": cal_L,
                    "F": cal_F,
                    "Lhat": cal_Lhat,
                    "Fhat": cal_Fhat,
                },
                "test": {
                    "L": test_L,
                    "F": test_F,
                    "Lhat": test_Lhat,
                    "Fhat": test_Fhat,
                },
            }
    return {
        "regret": regret,
        "fallback_action": fallback_actions,
        "models": models,
        "transform_audit": transform_audit,
    }


def route_candidate(
    data: dict[str, Any],
    predictions: dict[str, Any],
    spec: dict[str, Any],
    alpha: float,
    mode: str,
) -> dict[str, Any]:
    key = model_key(spec)
    model = predictions["models"][key]
    actions = np.asarray(model["learned_action"], dtype=int).copy()
    changed = np.zeros(len(actions), dtype=bool)
    violation = np.zeros(len(actions), dtype=bool)
    quantiles: dict[str, Any] = {}
    for fold, fold_data in model["folds"].items():
        route = _route_from_predictions(
            mode, alpha, fold_data["calibration"], fold_data["test"]
        )
        idx = fold_data["test_idx"]
        actions[idx[route["fallback"]]] = int(fold_data["fallback_action"])
        changed[idx] = route["fallback"]
        violation[idx] = route["violation"]
        quantiles[str(fold)] = {
            "q": None if not math.isfinite(route["q"]) else float(route["q"]),
            "infinite": not math.isfinite(route["q"]),
            "calibration_size": route["calibration_size"],
        }
    return {
        "actions": actions,
        "route_changed": changed,
        "violation": violation,
        "quantiles": quantiles,
        "metrics": _metrics(
            data,
            actions,
            pay_feature=True,
            route_changed=changed,
            violation=violation,
        ),
    }


def one_sided_candidate(
    data: dict[str, Any],
    predictions: dict[str, Any],
    spec: dict[str, Any],
    alpha: float,
) -> dict[str, Any]:
    key = model_key(spec)
    model = predictions["models"][key]
    actions = np.asarray(model["learned_action"], dtype=int).copy()
    changed = np.zeros(len(actions), dtype=bool)
    violation = np.zeros(len(actions), dtype=bool)
    for fold, fold_data in model["folds"].items():
        route = _one_sided_route(alpha, fold_data["calibration"], fold_data["test"])
        idx = fold_data["test_idx"]
        actions[idx[route["fallback"]]] = int(fold_data["fallback_action"])
        changed[idx] = route["fallback"]
        violation[idx] = route["violation"]
    return {
        "actions": actions,
        "route_changed": changed,
        "violation": violation,
        "metrics": _metrics(
            data,
            actions,
            pay_feature=True,
            route_changed=changed,
            violation=violation,
        ),
    }


def full_model_metrics(data: dict[str, Any], predictions: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    return _metrics(
        data,
        np.asarray(predictions["models"][model_key(spec)]["learned_action"], dtype=int),
        pay_feature=True,
    )


def fallback_metrics(data: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
    return _metrics(
        data,
        np.asarray(predictions["fallback_action"], dtype=int),
        pay_feature=False,
    )


def oracle_contextual_route(
    data: dict[str, Any], predictions: dict[str, Any], spec: dict[str, Any]
) -> dict[str, Any]:
    learned = np.asarray(predictions["models"][model_key(spec)]["learned_action"], dtype=int)
    fallback = np.asarray(predictions["fallback_action"], dtype=int)
    rows = np.arange(len(learned))
    choose_fallback = data["cost"][rows, fallback] < data["cost"][rows, learned]
    actions = learned.copy()
    actions[choose_fallback] = fallback[choose_fallback]
    return {
        "actions": actions,
        "route_changed": choose_fallback,
        "metrics": _metrics(
            data,
            actions,
            pay_feature=True,
            route_changed=choose_fallback,
        ),
    }


def candidate_feasible(
    route: dict[str, Any],
    full: dict[str, Any],
    fallback: dict[str, Any],
    alpha: float,
    protocol: dict[str, Any],
) -> tuple[bool, tuple[str, ...]]:
    gate = protocol["development_selection"]["feasible_constraints"]
    m = route["metrics"]
    failures: list[str] = []
    if m["route_change_coverage"] < float(gate["route_change_coverage_minimum"]):
        failures.append("COVERAGE")
    if not m["mean_total_cost"] < full["mean_total_cost"]:
        failures.append("MEAN_VS_FULL")
    if not m["mean_total_cost"] < fallback["mean_total_cost"]:
        failures.append("MEAN_VS_FALLBACK")
    if m["catastrophic_rate"] > full["catastrophic_rate"] + 1e-12:
        failures.append("CATASTROPHIC")
    if m["p95_total_cost"] > full["p95_total_cost"] + 1e-12:
        failures.append("P95")
    if m["certificate_failure_rate"] > alpha + float(
        gate["empirical_certificate_failure_no_larger_than_alpha_plus"]
    ) + 1e-12:
        failures.append("CERTIFICATE_FAILURE")
    return not failures, tuple(failures)


def panel_gate(
    route: dict[str, Any],
    full: dict[str, Any],
    fallback: dict[str, Any],
    alpha: float,
    protocol: dict[str, Any],
) -> dict[str, Any]:
    gate = protocol["panel_gate"]
    m = route["metrics"]
    checks = {
        "full_model_beats_no_feature_fallback": full["mean_total_cost"] < fallback["mean_total_cost"],
        "route_beats_full_model": m["mean_total_cost"] < full["mean_total_cost"],
        "catastrophic_no_worse": m["catastrophic_rate"] <= full["catastrophic_rate"] + 1e-12,
        "p95_no_worse": m["p95_total_cost"] <= full["p95_total_cost"] + 1e-12,
        "coverage": m["route_change_coverage"] >= float(gate["route_change_coverage_minimum"]),
        "certificate_failure": m["certificate_failure_rate"] <= alpha + float(
            gate["empirical_certificate_failure_no_larger_than_alpha_plus"]
        ) + 1e-12,
    }
    return {"pass": all(checks.values()), "checks": checks}


def development_objective(
    route: dict[str, Any],
    spec: dict[str, Any],
    alpha: float,
    mode: str,
) -> tuple[Any, ...]:
    m = route["metrics"]
    return (
        m["mean_total_cost"],
        m["catastrophic_rate"],
        m["p95_total_cost"],
        -m["route_change_coverage"],
        model_key(spec),
        float(alpha),
        str(mode),
    )


def self_test() -> dict[str, Any]:
    scores = np.asarray([0.0, 1.0, 2.0, 3.0])
    if conformal_quantile(scores, 0.5) != 2.0:
        raise AssertionError("conformal rank drift")
    calibration = {
        "L": np.asarray([1.0, 3.0]),
        "F": np.asarray([2.0, 1.0]),
        "Lhat": np.asarray([1.0, 2.0]),
        "Fhat": np.asarray([2.0, 2.0]),
    }
    test = {
        "L": np.asarray([2.0]),
        "F": np.asarray([1.0]),
        "Lhat": np.asarray([2.0]),
        "Fhat": np.asarray([1.0]),
    }
    for mode in ("paired_upper", "interval_no_harm", "direct_difference"):
        route = _route_from_predictions(mode, 0.5, calibration, test)
        if route["fallback"].shape != (1,) or route["violation"].shape != (1,):
            raise AssertionError(f"route shape drift: {mode}")
    return {"status": "GREEN"}
