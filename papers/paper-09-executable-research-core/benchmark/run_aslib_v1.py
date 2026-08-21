#!/usr/bin/env python3
"""Run the frozen P9 discriminator on ASlib SAT11-HAND-ALGO.

The protocol and input hashes were committed before this program accessed any
outcome. Generated JSON and Markdown are written from the same in-memory result.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "ASLIB_SAT11_PROTOCOL_V1.json"
DATA_DIR = HERE / "aslib_sat11_hand_algo"
RESULT_DIR = HERE.parent / "results"
JSON_PATH = RESULT_DIR / "ASLIB_SAT11_HAND_ALGO_V1.json"
MARKDOWN_PATH = RESULT_DIR / "ASLIB_SAT11_HAND_ALGO_V1.md"
SEED = 20260818
BOOTSTRAPS = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_arff(path: Path) -> tuple[list[str], list[list[str]]]:
    """Read the simple dense ARFF dialect used by this frozen ASlib scenario."""
    attributes: list[str] = []
    rows: list[list[str]] = []
    in_data = False
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("%"):
                continue
            lower = line.lower()
            if not in_data and lower.startswith("@attribute"):
                pieces = line.split(None, 2)
                if len(pieces) < 3:
                    raise ValueError(f"malformed attribute in {path}: {line}")
                attributes.append(pieces[1].strip("'\""))
            elif lower == "@data":
                in_data = True
            elif in_data:
                row = next(csv.reader([line], skipinitialspace=True))
                if len(row) != len(attributes):
                    raise ValueError(
                        f"{path.name}: expected {len(attributes)} fields, got {len(row)}"
                    )
                rows.append(row)
    if not attributes or not rows:
        raise ValueError(f"empty or unsupported ARFF file: {path}")
    return attributes, rows


def numeric(value: str) -> float:
    return math.nan if value == "?" else float(value)


def load_scenario(protocol: dict[str, Any]) -> dict[str, Any]:
    for name, expected in protocol["source"]["files"].items():
        actual = sha256(DATA_DIR / name)
        if actual != expected:
            raise ValueError(f"input digest mismatch for {name}: {actual} != {expected}")

    feature_names, feature_rows = read_arff(DATA_DIR / "feature_values.arff")
    run_names, run_rows = read_arff(DATA_DIR / "algorithm_runs.arff")
    cv_names, cv_rows = read_arff(DATA_DIR / "cv.arff")

    if feature_names[:2] != ["instance_id", "repetition"]:
        raise ValueError("unexpected feature key columns")
    if run_names != ["instance_id", "repetition", "algorithm", "runtime", "runstatus"]:
        raise ValueError("unexpected algorithm-run schema")
    if cv_names != ["instance_id", "repetition", "fold"]:
        raise ValueError("unexpected CV schema")

    feature_by_key: dict[tuple[str, int], list[float]] = {}
    for row in feature_rows:
        key = (row[0], int(float(row[1])))
        if key in feature_by_key:
            raise ValueError(f"duplicate feature key: {key}")
        feature_by_key[key] = [numeric(value) for value in row[2:]]

    folds: dict[tuple[str, int], int] = {}
    ordered_keys: list[tuple[str, int]] = []
    for row in cv_rows:
        key = (row[0], int(float(row[1])))
        if key in folds:
            raise ValueError(f"duplicate CV key: {key}")
        folds[key] = int(float(row[2]))
        ordered_keys.append(key)

    algorithms = sorted({row[2] for row in run_rows})
    algorithm_index = {algorithm: index for index, algorithm in enumerate(algorithms)}
    run_by_key: dict[tuple[str, int], dict[str, tuple[float, bool]]] = {}
    for row in run_rows:
        key = (row[0], int(float(row[1])))
        algorithm = row[2]
        bucket = run_by_key.setdefault(key, {})
        if algorithm in bucket:
            raise ValueError(f"duplicate run key: {key} / {algorithm}")
        bucket[algorithm] = (float(row[3]), row[4].strip() == "ok")

    cv_keys = set(ordered_keys)
    if set(feature_by_key) != cv_keys or set(run_by_key) != cv_keys:
        raise ValueError("feature, run, and CV instance keys do not match exactly")
    for key, runs in run_by_key.items():
        if set(runs) != set(algorithms):
            raise ValueError(f"incomplete solver portfolio for {key}")

    cutoff = float(protocol["cutoff_seconds"])
    par10 = cutoff * 10.0
    x = np.asarray([feature_by_key[key] for key in ordered_keys], dtype=float)
    runtime = np.empty((len(ordered_keys), len(algorithms)), dtype=float)
    solved = np.empty_like(runtime, dtype=bool)
    for row_index, key in enumerate(ordered_keys):
        for algorithm, column_index in algorithm_index.items():
            observed_runtime, ok = run_by_key[key][algorithm]
            runtime[row_index, column_index] = observed_runtime if ok else par10
            solved[row_index, column_index] = ok

    return {
        "keys": ordered_keys,
        "instance_ids": np.asarray([key[0] for key in ordered_keys]),
        "folds": np.asarray([folds[key] for key in ordered_keys], dtype=int),
        "feature_names": feature_names[2:],
        "algorithms": algorithms,
        "x": x,
        "runtime": runtime,
        "solved": solved,
    }


def impute(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    with np.errstate(all="ignore"):
        medians = np.nanmedian(train, axis=0)
    medians = np.where(np.isnan(medians), 0.0, medians)
    return (
        np.where(np.isnan(train), medians, train),
        np.where(np.isnan(test), medians, test),
    )


def fit_router(
    x_train: np.ndarray,
    runtime_train: np.ndarray,
    solved_train: np.ndarray,
    x_test: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    predicted_runtime = np.empty((len(x_test), runtime_train.shape[1]), dtype=float)
    predicted_solve = np.empty_like(predicted_runtime)
    for solver_index in range(runtime_train.shape[1]):
        regression = RandomForestRegressor(
            n_estimators=300,
            max_features="sqrt",
            min_samples_leaf=2,
            random_state=SEED + solver_index,
            n_jobs=1,
        )
        regression.fit(x_train, np.log1p(runtime_train[:, solver_index]))
        predicted_runtime[:, solver_index] = np.expm1(regression.predict(x_test))

        target = solved_train[:, solver_index].astype(int)
        if target.min() == target.max():
            predicted_solve[:, solver_index] = float(target[0])
        else:
            classifier = RandomForestClassifier(
                n_estimators=300,
                max_features="sqrt",
                min_samples_leaf=2,
                random_state=SEED + solver_index,
                n_jobs=1,
            )
            classifier.fit(x_train, target)
            ok_column = int(np.flatnonzero(classifier.classes_ == 1)[0])
            predicted_solve[:, solver_index] = classifier.predict_proba(x_test)[:, ok_column]

    selected = np.argmin(predicted_runtime, axis=1)
    max_solve_probability = np.max(predicted_solve, axis=1)
    return selected, max_solve_probability


def inner_fold(instance_id: str) -> int:
    digest = hashlib.sha256(f"{instance_id}:p9-inner".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 5


def select_threshold(
    instance_ids: np.ndarray,
    x: np.ndarray,
    runtime: np.ndarray,
    solved: np.ndarray,
) -> tuple[float, dict[str, Any]]:
    assignments = np.asarray([inner_fold(item) for item in instance_ids], dtype=int)
    router_solved = np.empty(len(x), dtype=bool)
    max_probability = np.empty(len(x), dtype=float)
    vbs_unsolved = ~np.any(solved, axis=1)

    for fold in range(5):
        validation = assignments == fold
        training = ~validation
        if not validation.any() or not training.any():
            raise ValueError(f"empty deterministic inner fold {fold}")
        x_train, x_validation = impute(x[training], x[validation])
        selected, probabilities = fit_router(
            x_train, runtime[training], solved[training], x_validation
        )
        validation_rows = np.flatnonzero(validation)
        router_solved[validation_rows] = solved[validation_rows, selected]
        max_probability[validation_rows] = probabilities

    router_solve_count = int(router_solved.sum())
    unsolved_count = int(vbs_unsolved.sum())
    candidates: list[dict[str, Any]] = []
    for threshold in [float(item) for item in range(1, 10)]:
        threshold /= 10.0
        attempt = max_probability >= threshold
        retained = (
            float(np.sum(router_solved & attempt) / router_solve_count)
            if router_solve_count
            else 1.0
        )
        avoided = (
            float(np.sum(vbs_unsolved & ~attempt) / unsolved_count)
            if unsolved_count
            else 0.0
        )
        candidates.append(
            {
                "threshold": threshold,
                "rf_solved_retained": retained,
                "vbs_unsolved_attempt_reduction": avoided,
                "qualifies": retained >= 0.95,
            }
        )

    qualifying = [item for item in candidates if item["qualifies"]]
    if qualifying:
        best = sorted(
            qualifying,
            key=lambda item: (-item["vbs_unsolved_attempt_reduction"], item["threshold"]),
        )[0]
        constraint_miss = False
    else:
        best = candidates[0]
        constraint_miss = True
    return float(best["threshold"]), {
        "selected": best,
        "constraint_miss": constraint_miss,
        "candidates": candidates,
    }


def system_metrics(
    par10_cost: np.ndarray,
    solved: np.ndarray,
    attempt: np.ndarray,
    vbs_unsolved: np.ndarray,
    vbs_cost: np.ndarray,
) -> dict[str, float | None]:
    abstain = ~attempt

    def safe_ratio(numerator: int, denominator: int) -> float | None:
        return float(numerator / denominator) if denominator else None

    return {
        "mean_par10": float(np.mean(par10_cost)),
        "solve_rate": float(np.mean(solved)),
        "attempt_coverage": float(np.mean(attempt)),
        "attempt_rate_vbs_unsolved": safe_ratio(
            int(np.sum(attempt & vbs_unsolved)), int(vbs_unsolved.sum())
        ),
        "abstention_precision_vbs_unsolved": safe_ratio(
            int(np.sum(abstain & vbs_unsolved)), int(abstain.sum())
        ),
        "abstention_recall_vbs_unsolved": safe_ratio(
            int(np.sum(abstain & vbs_unsolved)), int(vbs_unsolved.sum())
        ),
        "mean_par10_regret_vs_vbs": float(np.mean(par10_cost - vbs_cost)),
    }


def percentile_ci(samples: np.ndarray) -> list[float]:
    return [float(item) for item in np.quantile(samples, [0.025, 0.975])]


def bootstrap_intervals(
    systems: dict[str, dict[str, np.ndarray]],
    vbs_unsolved: np.ndarray,
    vbs_cost: np.ndarray,
) -> dict[str, dict[str, list[float] | None]]:
    rng = np.random.default_rng(SEED)
    indices = rng.integers(0, len(vbs_cost), size=(BOOTSTRAPS, len(vbs_cost)))
    unsolved_sample = vbs_unsolved[indices]
    unsolved_denominator = np.sum(unsolved_sample, axis=1)
    intervals: dict[str, dict[str, list[float] | None]] = {}
    for name, system in systems.items():
        cost = system["cost"][indices]
        solved = system["solved"][indices]
        attempt = system["attempt"][indices]
        abstain = ~attempt
        abstain_denominator = np.sum(abstain, axis=1)

        attempt_unsolved = np.sum(attempt & unsolved_sample, axis=1)
        abstain_unsolved = np.sum(abstain & unsolved_sample, axis=1)
        attempt_rate = np.divide(
            attempt_unsolved,
            unsolved_denominator,
            out=np.full(BOOTSTRAPS, np.nan),
            where=unsolved_denominator > 0,
        )
        precision = np.divide(
            abstain_unsolved,
            abstain_denominator,
            out=np.full(BOOTSTRAPS, np.nan),
            where=abstain_denominator > 0,
        )
        recall = np.divide(
            abstain_unsolved,
            unsolved_denominator,
            out=np.full(BOOTSTRAPS, np.nan),
            where=unsolved_denominator > 0,
        )

        def finite_ci(values: np.ndarray) -> list[float] | None:
            finite = values[np.isfinite(values)]
            return percentile_ci(finite) if finite.size else None

        intervals[name] = {
            "mean_par10": percentile_ci(np.mean(cost, axis=1)),
            "solve_rate": percentile_ci(np.mean(solved, axis=1)),
            "attempt_coverage": percentile_ci(np.mean(attempt, axis=1)),
            "attempt_rate_vbs_unsolved": finite_ci(attempt_rate),
            "abstention_precision_vbs_unsolved": finite_ci(precision),
            "abstention_recall_vbs_unsolved": finite_ci(recall),
            "mean_par10_regret_vs_vbs": percentile_ci(
                np.mean(cost - vbs_cost[indices], axis=1)
            ),
        }
    return intervals


def evaluate(data: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    x = data["x"]
    runtime = data["runtime"]
    solved = data["solved"]
    folds = data["folds"]
    par10 = float(protocol["cutoff_seconds"]) * 10.0
    n_instances = len(x)

    vbs_solver = np.argmin(runtime, axis=1)
    vbs_cost = runtime[np.arange(n_instances), vbs_solver]
    vbs_solved = np.any(solved, axis=1)
    vbs_unsolved = ~vbs_solved

    systems = {
        name: {
            "cost": np.full(n_instances, par10, dtype=float),
            "solved": np.zeros(n_instances, dtype=bool),
            "attempt": np.ones(n_instances, dtype=bool),
        }
        for name in ["SBS", "VBS", "RF_ROUTER", "FAILURE_AWARE_RF", "FAILURE_MEMORY_KNN"]
    }
    systems["VBS"] = {
        "cost": vbs_cost.copy(),
        "solved": vbs_solved.copy(),
        "attempt": np.ones(n_instances, dtype=bool),
    }
    fold_receipts: list[dict[str, Any]] = []

    for fold in sorted(np.unique(folds)):
        test = folds == fold
        train = ~test
        train_rows = np.flatnonzero(train)
        test_rows = np.flatnonzero(test)
        x_train, x_test = impute(x[train], x[test])

        sbs_solver = int(np.argmin(np.mean(runtime[train], axis=0)))
        systems["SBS"]["cost"][test_rows] = runtime[test_rows, sbs_solver]
        systems["SBS"]["solved"][test_rows] = solved[test_rows, sbs_solver]

        selected, max_probability = fit_router(
            x_train, runtime[train], solved[train], x_test
        )
        router_cost = runtime[test_rows, selected]
        router_solved = solved[test_rows, selected]
        systems["RF_ROUTER"]["cost"][test_rows] = router_cost
        systems["RF_ROUTER"]["solved"][test_rows] = router_solved

        threshold, selection_receipt = select_threshold(
            data["instance_ids"][train], x[train], runtime[train], solved[train]
        )
        failure_attempt = max_probability >= threshold
        systems["FAILURE_AWARE_RF"]["cost"][test_rows] = np.where(
            failure_attempt, router_cost, par10
        )
        systems["FAILURE_AWARE_RF"]["solved"][test_rows] = (
            failure_attempt & router_solved
        )
        systems["FAILURE_AWARE_RF"]["attempt"][test_rows] = failure_attempt

        scaler = StandardScaler().fit(x_train)
        train_scaled = scaler.transform(x_train)
        test_scaled = scaler.transform(x_test)
        neighbours = NearestNeighbors(n_neighbors=5, algorithm="brute").fit(train_scaled)
        neighbour_rows = neighbours.kneighbors(test_scaled, return_distance=False)
        train_vbs_unsolved = ~np.any(solved[train_rows], axis=1)
        memory_attempt = ~np.all(train_vbs_unsolved[neighbour_rows], axis=1)
        systems["FAILURE_MEMORY_KNN"]["cost"][test_rows] = np.where(
            memory_attempt, router_cost, par10
        )
        systems["FAILURE_MEMORY_KNN"]["solved"][test_rows] = memory_attempt & router_solved
        systems["FAILURE_MEMORY_KNN"]["attempt"][test_rows] = memory_attempt

        fold_receipts.append(
            {
                "outer_fold": int(fold),
                "train_instances": int(train.sum()),
                "test_instances": int(test.sum()),
                "sbs_solver": data["algorithms"][sbs_solver],
                "failure_aware_threshold": threshold,
                "threshold_selection": selection_receipt,
            }
        )

    metrics = {
        name: system_metrics(
            system["cost"], system["solved"], system["attempt"], vbs_unsolved, vbs_cost
        )
        for name, system in systems.items()
    }
    intervals = bootstrap_intervals(systems, vbs_unsolved, vbs_cost)

    unsolved_rows = np.flatnonzero(vbs_unsolved)
    primary_difference = (
        systems["RF_ROUTER"]["attempt"][unsolved_rows].astype(float)
        - systems["FAILURE_AWARE_RF"]["attempt"][unsolved_rows].astype(float)
    )
    primary_rng = np.random.default_rng(SEED + 1)
    primary_samples = primary_difference[
        primary_rng.integers(
            0, len(primary_difference), size=(BOOTSTRAPS, len(primary_difference))
        )
    ].mean(axis=1)
    primary_estimate = float(np.mean(primary_difference))
    primary_ci = percentile_ci(primary_samples)

    rf_solved_count = int(systems["RF_ROUTER"]["solved"].sum())
    retained_solved_count = int(systems["FAILURE_AWARE_RF"]["solved"].sum())
    retention = float(retained_solved_count / rf_solved_count) if rf_solved_count else 1.0
    numerical_gate = (
        primary_estimate >= 0.20
        and primary_ci[0] > 0.0
        and retention >= 0.95
    )

    return {
        "schema": "P9AslibSat11Result.v1",
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "source_commit": protocol["source"]["commit"],
        "input_sha256": protocol["source"]["files"],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "population": {
            "instances": n_instances,
            "features": len(data["feature_names"]),
            "algorithms": len(data["algorithms"]),
            "outer_folds": int(len(np.unique(folds))),
            "vbs_unsolved_instances": int(vbs_unsolved.sum()),
        },
        "algorithms": data["algorithms"],
        "fold_receipts": fold_receipts,
        "metrics": metrics,
        "bootstrap_95_percent_intervals": intervals,
        "primary_comparison": {
            "metric": "absolute reduction in attempt rate on VBS-unsolved instances: FAILURE_AWARE_RF versus RF_ROUTER",
            "estimate": primary_estimate,
            "paired_bootstrap_95_percent_interval": primary_ci,
            "resamples": BOOTSTRAPS,
            "rf_solved_instances": rf_solved_count,
            "failure_aware_rf_solved_instances": retained_solved_count,
            "rf_solved_retention": retention,
        },
        "numerical_standalone_gate": {
            "passes": numerical_gate,
            "required_attempt_reduction": 0.20,
            "required_rf_solved_retention": 0.95,
            "requires_interval_excluding_zero": True,
            "note": "The protocol also requires a literature/ownership residual; this numerical result alone cannot keep P9 standalone.",
        },
        "disposition": "PENDING_NEAREST_WORK_AND_OWNERSHIP_REVIEW",
    }


def display(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def render_markdown(result: dict[str, Any]) -> str:
    rows = []
    for name, metric in result["metrics"].items():
        rows.append(
            "| "
            + " | ".join(
                [
                    name,
                    display(metric["mean_par10"]),
                    display(metric["solve_rate"]),
                    display(metric["attempt_coverage"]),
                    display(metric["attempt_rate_vbs_unsolved"]),
                    display(metric["abstention_precision_vbs_unsolved"]),
                    display(metric["abstention_recall_vbs_unsolved"]),
                    display(metric["mean_par10_regret_vs_vbs"]),
                ]
            )
            + " |"
        )
    primary = result["primary_comparison"]
    gate = result["numerical_standalone_gate"]
    return "\n".join(
        [
            "# P9 public discriminator result: ASlib SAT11-HAND-ALGO",
            "",
            "> Generated by `benchmark/run_aslib_v1.py` from the frozen protocol and exact",
            "> public input digests. The JSON file is the machine-readable source of truth.",
            "",
            "## Population",
            "",
            f"- instances: {result['population']['instances']}",
            f"- numeric features: {result['population']['features']}",
            f"- portfolio algorithms: {result['population']['algorithms']}",
            f"- scenario-provided outer folds: {result['population']['outer_folds']}",
            f"- VBS-unsolved instances: {result['population']['vbs_unsolved_instances']}",
            "",
            "## Pooled outer-fold metrics",
            "",
            "| System | Mean PAR10 | Solve rate | Attempt coverage | Attempt rate on VBS-unsolved | Abstention precision | Abstention recall | PAR10 regret vs VBS |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
            *rows,
            "",
            "## Pre-registered numerical gate",
            "",
            f"The failure-aware system reduced attempts on VBS-unsolved instances by **{primary['estimate']:.4f}**",
            f"(paired instance bootstrap 95% interval {primary['paired_bootstrap_95_percent_interval']}).",
            f"It retained **{primary['rf_solved_retention']:.4f}** of RF_ROUTER's solved instances.",
            f"The numerical gate therefore **{'passes' if gate['passes'] else 'does not pass'}**.",
            "",
            "This is not yet a standalone-paper decision. The frozen rule also requires a residual",
            "that survives nearest-work and paper-ownership pressure.",
            "",
            "## Interpretation boundary",
            "",
            "This is one bounded public scenario. It does not establish ASlib-wide, SAT-portfolio,",
            "meta-learning, selective-prediction, LLM-routing, or general operational superiority.",
            "Abstention is a routing terminal, not authority to act.",
            "",
        ]
    )


def main() -> None:
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    data = load_scenario(protocol)
    result = evaluate(data, protocol)
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_PATH.write_text(render_markdown(result), encoding="utf-8")
    print(f"wrote {JSON_PATH}")
    print(f"wrote {MARKDOWN_PATH}")
    print(json.dumps(result["primary_comparison"], indent=2, sort_keys=True))
    print(json.dumps(result["numerical_standalone_gate"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
