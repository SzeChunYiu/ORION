"""Digest-bound ASlib loader for the outcome-exposed R18 recovery.

The implementation follows only PAIRED_ROUTE_PROTOCOL_R18.json and the pinned
ASlib bytes. It deliberately does not read the withdrawn R18 result prose.
"""
from __future__ import annotations

import collections
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

import fiberguard_aslib_sat12_all_r11 as r11
import fiberguard_paired_route_r18_sources as sources

STATUS_ORDER = ("ok", "presolved", "timeout", "memout", "crash", "other")


def _false_like(value: Any) -> bool:
    return value is False or str(value).strip().lower() in {"false", "no", "0"}


def _mode(values: Iterable[str]) -> str:
    counter = collections.Counter(values)
    if not counter:
        raise ValueError("empty status collection")
    return min(counter, key=lambda value: (-counter[value], value))


def _median(values: Iterable[float]) -> float:
    rows = sorted(float(value) for value in values)
    if not rows:
        raise ValueError("empty numeric collection")
    n = len(rows)
    if n % 2:
        return rows[n // 2]
    return (rows[n // 2 - 1] + rows[n // 2]) / 2.0


def _normalize_status(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in STATUS_ORDER:
        return lowered
    if lowered in {"not_applicable", "other"}:
        return "other"
    return "other"


def _parse_algorithm_runs(
    path: Path,
    *,
    measure: str,
    cutoff: float,
) -> tuple[
    dict[str, dict[str, float]],
    dict[str, dict[str, str]],
    tuple[str, ...],
    dict[str, Any],
]:
    attrs, rows = r11.read_arff(path)
    required = ("instance_id", "repetition", "algorithm", measure, "runstatus")
    missing = [name for name in required if name not in attrs]
    if missing:
        raise ValueError(f"algorithm-runs attributes missing: {missing}")
    index = {name: attrs.index(name) for name in required}
    grouped: dict[tuple[str, str], list[tuple[float, str]]] = collections.defaultdict(list)
    algorithms: set[str] = set()
    raw_status_counts: collections.Counter[str] = collections.Counter()
    par10 = 10.0 * cutoff
    declared_par10 = measure.lower() == "par10"
    for row in rows:
        instance = row[index["instance_id"]]
        algorithm = row[index["algorithm"]]
        status = _normalize_status(row[index["runstatus"]])
        value = float(row[index[measure]])
        raw_status_counts[status] += 1
        if declared_par10:
            if status != "ok" and abs(value - par10) > 1e-7 * max(1.0, par10):
                raise ValueError(
                    f"declared PAR10 non-ok value drift for {instance}/{algorithm}: "
                    f"{value} != {par10}"
                )
            penalized = value
        else:
            penalized = value if status == "ok" else par10
        grouped[(instance, algorithm)].append((penalized, status))
        algorithms.add(algorithm)

    ordered_algorithms = tuple(sorted(algorithms))
    costs: dict[str, dict[str, float]] = collections.defaultdict(dict)
    statuses: dict[str, dict[str, str]] = collections.defaultdict(dict)
    repetitions: collections.Counter[int] = collections.Counter()
    for (instance, algorithm), values in grouped.items():
        costs[instance][algorithm] = _median(value for value, _ in values)
        statuses[instance][algorithm] = _mode(status for _, status in values)
        repetitions[len(values)] += 1

    incomplete = [
        instance
        for instance, mapping in costs.items()
        if set(mapping) != set(ordered_algorithms)
    ]
    if incomplete:
        raise ValueError(f"incomplete algorithm matrix for {len(incomplete)} instances")
    return (
        dict(costs),
        dict(statuses),
        ordered_algorithms,
        {
            "declared_measure": measure,
            "cutoff": cutoff,
            "par10": par10,
            "raw_status_counts": dict(sorted(raw_status_counts.items())),
            "repetitions_per_instance_algorithm": dict(sorted(repetitions.items())),
        },
    )


def _parse_feature_values(
    path: Path,
) -> tuple[dict[str, dict[str, float]], tuple[str, ...]]:
    attrs, rows = r11.read_arff(path)
    if attrs[:2] != ["instance_id", "repetition"]:
        raise ValueError("unexpected feature-values prefix")
    features = tuple(attrs[2:])
    grouped: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for row in rows:
        instance = row[0]
        for feature, value in zip(features, row[2:]):
            grouped[(instance, feature)].append(value)
    result: dict[str, dict[str, float]] = collections.defaultdict(dict)
    for (instance, feature), values in grouped.items():
        numeric = [float(value) for value in values if value != "?"]
        result[instance][feature] = (
            float("nan") if len(numeric) != len(values) else float(np.mean(numeric))
        )
    return dict(result), features


def _parse_step_table(
    path: Path,
    *,
    numeric: bool,
) -> tuple[dict[str, dict[str, float | str]], tuple[str, ...]]:
    attrs, rows = r11.read_arff(path)
    if attrs[:2] != ["instance_id", "repetition"]:
        raise ValueError(f"unexpected step-table prefix in {path}")
    steps = tuple(attrs[2:])
    grouped: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for row in rows:
        instance = row[0]
        for step, value in zip(steps, row[2:]):
            grouped[(instance, step)].append(value)
    result: dict[str, dict[str, float | str]] = collections.defaultdict(dict)
    for (instance, step), values in grouped.items():
        if numeric:
            numbers = [float(value) for value in values if value != "?"]
            result[instance][step] = _median(numbers) if numbers else float("nan")
        else:
            result[instance][step] = _mode(_normalize_status(value) for value in values)
    return dict(result), steps


def _parse_cv(path: Path, *, repetition: int) -> dict[str, int]:
    attrs, rows = r11.read_arff(path)
    required = ("instance_id", "repetition", "fold")
    missing = [name for name in required if name not in attrs]
    if missing:
        raise ValueError(f"cv attributes missing: {missing}")
    index = {name: attrs.index(name) for name in required}
    result: dict[str, int] = {}
    for row in rows:
        if int(float(row[index["repetition"]])) != repetition:
            continue
        instance = row[index["instance_id"]]
        fold = int(float(row[index["fold"]]))
        if instance in result and result[instance] != fold:
            raise ValueError(f"multiple folds for {instance} in repetition {repetition}")
        result[instance] = fold
    if not result:
        raise ValueError(f"no cv rows for repetition {repetition}")
    return result


def load_scenario(
    aslib_root: Path,
    scenario_spec: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    """Load one scenario exactly under the frozen R18 contract."""
    scenario = str(scenario_spec["name"])
    step = str(scenario_spec["acquisition_step"])
    root = aslib_root / scenario
    source_audit = sources.verify_files(root, scenario_spec["files"])
    description = yaml.safe_load((root / "description.txt").read_text(encoding="utf-8"))
    measures = description.get("performance_measures") or []
    maximizes = description.get("maximize") or []
    if isinstance(measures, str):
        measures = [measures]
    if isinstance(maximizes, (str, bool)):
        maximizes = [maximizes]
    if len(measures) != 1 or len(maximizes) != 1 or not _false_like(maximizes[0]):
        raise ValueError(f"CANNOT_CHECK_DECLARED_MEASURE: {scenario}")
    measure = str(measures[0])
    if measure not in {"runtime", "PAR10"}:
        raise ValueError(f"CANNOT_CHECK_DECLARED_MEASURE: {scenario}/{measure}")
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time")
    feature_cutoff = (
        float(feature_cutoff_raw)
        if feature_cutoff_raw not in {None, "?", ""}
        else None
    )
    feature_steps = description.get("feature_steps") or {}
    if step not in feature_steps:
        raise ValueError(f"acquisition step {step!r} absent in {scenario}")
    provides = feature_steps[step].get("provides") or []
    if isinstance(provides, str):
        provides = [provides]
    provides = tuple(str(name) for name in provides)
    if not provides:
        raise ValueError(f"acquisition step {step!r} provides no features")

    costs_by_instance, statuses_by_instance, algorithms, run_audit = _parse_algorithm_runs(
        root / "algorithm_runs.arff", measure=measure, cutoff=cutoff
    )
    feature_values, feature_names = _parse_feature_values(root / "feature_values.arff")
    feature_costs, cost_steps = _parse_step_table(root / "feature_costs.arff", numeric=True)
    feature_status, status_steps = _parse_step_table(
        root / "feature_runstatus.arff", numeric=False
    )
    cv = _parse_cv(
        root / "cv.arff",
        repetition=int(protocol["split"]["official_cv_repetition"]),
    )
    if step not in cost_steps or step not in status_steps:
        raise ValueError(f"CANNOT_CHECK_FEATURE_COST: step {step} missing in {scenario}")
    missing_features = [name for name in provides if name not in feature_names]
    if missing_features:
        raise ValueError(f"provided features absent in {scenario}: {missing_features}")

    instances = tuple(
        sorted(
            set(costs_by_instance)
            & set(feature_values)
            & set(feature_costs)
            & set(feature_status)
            & set(cv)
        )
    )
    denominator_union = (
        set(costs_by_instance)
        | set(feature_values)
        | set(feature_costs)
        | set(feature_status)
        | set(cv)
    )
    if set(instances) != denominator_union:
        missing_counts = {
            "algorithm": len(denominator_union - set(costs_by_instance)),
            "feature_values": len(denominator_union - set(feature_values)),
            "feature_costs": len(denominator_union - set(feature_costs)),
            "feature_status": len(denominator_union - set(feature_status)),
            "cv": len(denominator_union - set(cv)),
        }
        raise ValueError(f"incomplete scenario intersection {scenario}: {missing_counts}")
    folds = np.asarray([cv[instance] for instance in instances], dtype=int)
    expected_folds = set(range(1, int(protocol["split"]["expected_folds"]) + 1))
    if set(int(value) for value in np.unique(folds)) != expected_folds:
        raise ValueError(f"official fold denominator drift in {scenario}")

    cost_matrix = np.asarray(
        [
            [costs_by_instance[instance][algorithm] for algorithm in algorithms]
            for instance in instances
        ],
        dtype=float,
    )
    status_matrix = np.asarray(
        [
            [statuses_by_instance[instance][algorithm] for algorithm in algorithms]
            for instance in instances
        ],
        dtype=object,
    )
    feature_matrix = np.asarray(
        [
            [feature_values[instance].get(feature, float("nan")) for feature in provides]
            for instance in instances
        ],
        dtype=float,
    )
    acquisition: list[float] = []
    step_statuses: list[str] = []
    for instance in instances:
        status = _normalize_status(str(feature_status[instance].get(step, "other")))
        value = feature_costs[instance].get(step, float("nan"))
        numeric = float(value) if isinstance(value, (float, int)) else float("nan")
        if not math.isfinite(numeric):
            if status == "ok" or feature_cutoff is None:
                raise ValueError(
                    f"CANNOT_CHECK_FEATURE_COST: {scenario}/{instance}/{step}/{status}"
                )
            numeric = feature_cutoff
        if numeric < 0:
            raise ValueError(f"negative feature cost in {scenario}/{instance}")
        acquisition.append(numeric)
        step_statuses.append(status)

    return {
        "scenario": scenario,
        "acquisition_step": step,
        "instances": instances,
        "algorithms": algorithms,
        "feature_names": provides,
        "raw_features": feature_matrix,
        "feature_runstatus": np.asarray(step_statuses, dtype=object),
        "feature_cost": np.asarray(acquisition, dtype=float),
        "cost": cost_matrix,
        "runstatus": status_matrix,
        "timeout": status_matrix == "timeout",
        "non_ok": status_matrix != "ok",
        "fold": folds,
        "cutoff": cutoff,
        "par10": 10.0 * cutoff,
        "measure": measure,
        "source_audit": source_audit,
        "run_audit": run_audit,
        "feature_cutoff": feature_cutoff,
    }


def self_test() -> dict[str, Any]:
    if not _false_like(False) or not _false_like("no") or _false_like(True):
        raise AssertionError("false-like parser drift")
    if _normalize_status("not_applicable") != "other":
        raise AssertionError("status normalization drift")
    if _mode(["timeout", "ok"]) != "ok":
        raise AssertionError("deterministic status tie drift")
    if _median([1.0, 3.0]) != 2.0:
        raise AssertionError("median drift")
    return {"status": "GREEN"}
