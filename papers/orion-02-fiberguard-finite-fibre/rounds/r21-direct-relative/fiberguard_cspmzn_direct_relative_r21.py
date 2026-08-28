#!/usr/bin/env python3
"""Frozen ORION-02 R21 CSP-MZN direct-relative joint-route experiment.

The scientific contract is FIBERGUARD_CSPMZN_DIRECT_RELATIVE_R21_PROTOCOL.md.
This executor intentionally fails closed on source, schema, split, or cost drift.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics
import subprocess
from typing import Any, Iterable, Sequence

import numpy as np
import yaml

SCHEMA = "ORION.FiberGuard.CSPMZNDirectRelative.R21.v1"
ASLIB_REPO = "https://github.com/coseal/aslib_data.git"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SCENARIO = "CSP-MZN-2013"
ALGORITHM_CUTOFF = 1800.0
PAR10 = 18000.0
FEATURE_CUTOFF = 900.0
ALPHA = 0.10
TOL = 1e-9
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED_TEXT = "ORION02_R21_CSPMZN_DIRECT_RELATIVE_BOOTSTRAP_V1"

EXPECTED_BLOBS = {
    "README.md": "bbae808cc2f718b15b379b30ef6a9909933fc3d5",
    f"{SCENARIO}/readme.txt": "55180a18d255fd01bf8c504794c85e1361e0b4de",
    f"{SCENARIO}/description.txt": "fef9553ae42035d065325c4cf938ea77c4a55b11",
    f"{SCENARIO}/algorithm_runs.arff": "874d8f4693b0c83bc82be55a77e4b3ef3ef5a0ea",
    f"{SCENARIO}/cv.arff": "9cfeda3e75d6d6ac4aa1bfb11b1a9dabf06f658e",
    f"{SCENARIO}/feature_costs.arff": "428ee0a211c9c35fd1962609428d586535215a4a",
    f"{SCENARIO}/feature_runstatus.arff": "cb802dd046d9bafe21f0580cce1c70121332d828",
    f"{SCENARIO}/feature_values.arff": "d98002d161b994d17b8155ca2e643cc29f17aec3",
}
EXPECTED_SIZES = {
    "README.md": 3035,
    f"{SCENARIO}/readme.txt": 2824,
    f"{SCENARIO}/description.txt": 6476,
    f"{SCENARIO}/algorithm_runs.arff": 3716780,
    f"{SCENARIO}/cv.arff": 249492,
    f"{SCENARIO}/feature_costs.arff": 288054,
    f"{SCENARIO}/feature_runstatus.arff": 267637,
    f"{SCENARIO}/feature_values.arff": 4302207,
}
EXPECTED_STEPS = ("dynamic", "static")
K_VALUES = (1, 3, 5, 9)
ROUTE_K = 9


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode())


def finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"nonfinite numeric value: {value!r}")
    return number


def _attribute_name(line: str) -> str:
    rest = line.strip()[len("@attribute") :].strip()
    if not rest:
        raise ValueError(f"malformed attribute line: {line!r}")
    if rest[0] in {"'", '"'}:
        quote = rest[0]
        end = rest.find(quote, 1)
        if end < 0:
            raise ValueError(f"unterminated quoted attribute: {line!r}")
        return rest[1:end]
    return rest.split(None, 1)[0]


def read_arff(path: Path) -> tuple[list[str], list[list[str]]]:
    attributes: list[str] = []
    rows: list[list[str]] = []
    in_data = False
    with path.open("r", encoding="utf-8", newline="") as handle:
        for raw in handle:
            stripped = raw.strip()
            if not stripped or stripped.startswith("%"):
                continue
            lower = stripped.lower()
            if not in_data:
                if lower.startswith("@attribute"):
                    attributes.append(_attribute_name(stripped))
                elif lower == "@data":
                    in_data = True
                continue
            if stripped.startswith("{"):
                raise ValueError(f"sparse ARFF rows are outside the frozen parser: {path}")
            row = next(csv.reader([raw], skipinitialspace=True))
            if len(row) != len(attributes):
                raise ValueError(
                    f"row width {len(row)} != {len(attributes)} in {path.name}: {raw[:120]!r}"
                )
            rows.append([value.strip() for value in row])
    if not attributes or not in_data or not rows:
        raise ValueError(f"invalid or empty ARFF: {path}")
    return attributes, rows


def most_common_status(values: Iterable[str]) -> str:
    counts = collections.Counter(values)
    if not counts:
        raise ValueError("empty status list")
    return min(counts, key=lambda value: (-counts[value], value))


def verify_subject(repo: Path) -> dict[str, Any]:
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    if head != ASLIB_COMMIT:
        raise ValueError(f"subject HEAD {head} != {ASLIB_COMMIT}")
    files: dict[str, Any] = {}
    for relative, expected_blob in EXPECTED_BLOBS.items():
        path = repo / relative
        if not path.is_file():
            raise ValueError(f"missing required subject file: {relative}")
        blob = git_blob_sha(path)
        size = path.stat().st_size
        if blob != expected_blob:
            raise ValueError(f"Git blob mismatch for {relative}: {blob}")
        if size != EXPECTED_SIZES[relative]:
            raise ValueError(f"byte-count mismatch for {relative}: {size}")
        files[relative] = {
            "bytes": size,
            "git_blob_sha1": blob,
            "sha256": sha256_file(path),
        }
    licence_text = (repo / "README.md").read_text(encoding="utf-8")
    if "# License\n\nGPLv3" not in licence_text:
        raise ValueError("pinned README no longer supplies the registered GPLv3 statement")
    return {
        "repository": ASLIB_REPO,
        "commit": head,
        "scenario": SCENARIO,
        "permission": {
            "statement": "GPLv3",
            "source_path": "README.md",
            "source_blob": EXPECTED_BLOBS["README.md"],
            "data_vendored_in_orion": False,
        },
        "files": files,
    }


def load_description(path: Path) -> tuple[list[str], dict[str, list[str]]]:
    description = yaml.safe_load(path.read_text(encoding="utf-8"))
    if description.get("scenario_id") != SCENARIO:
        raise ValueError("scenario_id drift")
    if float(description.get("algorithm_cutoff_time")) != ALGORITHM_CUTOFF:
        raise ValueError("algorithm cutoff drift")
    algorithms = sorted(description.get("metainfo_algorithms", {}))
    if len(algorithms) != 11:
        raise ValueError(f"expected eleven declared solvers, found {algorithms}")
    if float(description.get("features_cutoff_time")) != FEATURE_CUTOFF:
        raise ValueError("feature cutoff drift")
    steps_raw = description.get("feature_steps", {})
    if tuple(sorted(steps_raw)) != EXPECTED_STEPS:
        raise ValueError(f"feature-step registry drift: {sorted(steps_raw)}")
    step_features: dict[str, list[str]] = {}
    for step in EXPECTED_STEPS:
        provides = steps_raw[step].get("provides", [])
        if not isinstance(provides, list) or not provides:
            raise ValueError(f"invalid provides list for {step}")
        step_features[step] = [str(value) for value in provides]
    return algorithms, step_features


def load_algorithm_runs(
    path: Path, expected_algorithms: Sequence[str]
) -> tuple[
    dict[str, dict[str, float]],
    dict[str, dict[str, bool]],
    dict[str, Any],
]:
    attributes, rows = read_arff(path)
    required = ("instance_id", "repetition", "algorithm", "runtime", "runstatus")
    if any(name not in attributes for name in required):
        raise ValueError(f"algorithm table lacks required columns: {attributes}")
    index = {name: attributes.index(name) for name in required}
    grouped: dict[tuple[str, str], list[tuple[float, str, str]]] = collections.defaultdict(list)
    for row in rows:
        instance = row[index["instance_id"]]
        algorithm = row[index["algorithm"]]
        if algorithm not in expected_algorithms:
            raise ValueError(f"undeclared solver in algorithm table: {algorithm}")
        grouped[(instance, algorithm)].append(
            (
                finite_float(row[index["runtime"]]),
                row[index["runstatus"]],
                row[index["repetition"]],
            )
        )
    runtimes: dict[str, dict[str, float]] = collections.defaultdict(dict)
    timeouts: dict[str, dict[str, bool]] = collections.defaultdict(dict)
    repetition_histogram: collections.Counter[int] = collections.Counter()
    aggregated_status: collections.Counter[str] = collections.Counter()
    raw_status: collections.Counter[str] = collections.Counter()
    for (instance, algorithm), values in grouped.items():
        repetitions = [rep for _, _, rep in values]
        if not values or len(repetitions) != len(set(repetitions)):
            raise ValueError(
                f"missing or duplicate repetitions for {(instance, algorithm)}: "
                f"{len(values)}/{len(set(repetitions))}"
            )
        repetition_histogram[len(values)] += 1
        raw_status.update(status for _, status, _ in values)
        status = most_common_status(status for _, status, _ in values)
        aggregated_status[status] += 1
        successful = status == "ok"
        runtimes[instance][algorithm] = (
            float(statistics.median(runtime for runtime, _, _ in values)) if successful else PAR10
        )
        timeouts[instance][algorithm] = not successful
    expected = set(expected_algorithms)
    incomplete = [x for x, mapping in runtimes.items() if set(mapping) != expected]
    if incomplete:
        raise ValueError(f"incomplete algorithm matrix for {len(incomplete)} instances")
    return (
        dict(runtimes),
        dict(timeouts),
        {
            "instances": len(runtimes),
            "algorithms": list(expected_algorithms),
            "raw_rows": len(rows),
            "raw_status_counts": dict(sorted(raw_status.items())),
            "repetitions_per_instance_algorithm": {
                str(key): value for key, value in sorted(repetition_histogram.items())
            },
            "aggregated_status_counts": dict(sorted(aggregated_status.items())),
            "aggregation": "median_runtime__most_common_status__non_ok_PAR10",
            "par10": PAR10,
        },
    )


def load_feature_values(
    path: Path,
) -> tuple[dict[str, dict[str, float | None]], list[str], dict[str, Any]]:
    attributes, rows = read_arff(path)
    if attributes[:2] != ["instance_id", "repetition"]:
        raise ValueError("unexpected feature-values prefix")
    feature_names = attributes[2:]
    if len(feature_names) != len(set(feature_names)):
        raise ValueError("duplicate feature-value column")
    grouped: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    repetitions: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        instance = row[0]
        repetitions[instance].add(row[1])
        for name, value in zip(feature_names, row[2:]):
            grouped[(instance, name)].append(value)
    values: dict[str, dict[str, float | None]] = collections.defaultdict(dict)
    missing_cells = 0
    repetition_histogram: collections.Counter[int] = collections.Counter(
        len(items) for items in repetitions.values()
    )
    for (instance, name), raw_values in grouped.items():
        if any(value == "?" for value in raw_values):
            values[instance][name] = None
            missing_cells += 1
        else:
            values[instance][name] = float(
                statistics.median(finite_float(value) for value in raw_values)
            )
    return (
        dict(values),
        feature_names,
        {
            "instances": len(values),
            "features": len(feature_names),
            "raw_rows": len(rows),
            "missing_aggregated_cells": missing_cells,
            "repetitions_per_instance": {
                str(key): value for key, value in sorted(repetition_histogram.items())
            },
            "aggregation": "median_all_finite_repetitions__any_missing_remains_missing",
        },
    )


def load_step_table(
    path: Path, *, numeric: bool
) -> tuple[dict[str, dict[str, float | str | None]], list[str], dict[str, Any]]:
    attributes, rows = read_arff(path)
    if attributes[:2] != ["instance_id", "repetition"]:
        raise ValueError(f"unexpected step-table prefix in {path.name}")
    steps = attributes[2:]
    if tuple(sorted(steps)) != EXPECTED_STEPS:
        raise ValueError(f"step-table registry drift in {path.name}: {steps}")
    grouped: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for row in rows:
        for step, value in zip(steps, row[2:]):
            grouped[(row[0], step)].append(value)
    values: dict[str, dict[str, float | str | None]] = collections.defaultdict(dict)
    missing = 0
    for (instance, step), raw_values in grouped.items():
        if numeric:
            numbers = [finite_float(value) for value in raw_values if value != "?"]
            value: float | str | None = float(statistics.median(numbers)) if numbers else None
            if value is None:
                missing += 1
        else:
            value = most_common_status(raw_values)
        values[instance][step] = value
    return (
        dict(values),
        steps,
        {
            "instances": len(values),
            "steps": steps,
            "raw_rows": len(rows),
            "missing_aggregated_cells": missing,
            "aggregation": "median_finite" if numeric else "most_common_lexical_tie",
        },
    )


def load_cv(path: Path) -> tuple[dict[str, int], dict[str, Any]]:
    attributes, rows = read_arff(path)
    required = ("instance_id", "repetition", "fold")
    if any(name not in attributes for name in required):
        raise ValueError(f"CV table lacks required columns: {attributes}")
    index = {name: attributes.index(name) for name in required}
    mapping: dict[str, int] = {}
    duplicates: list[str] = []
    for row in rows:
        if int(float(row[index["repetition"]])) != 1:
            continue
        instance = row[index["instance_id"]]
        fold = int(float(row[index["fold"]]))
        if instance in mapping:
            duplicates.append(instance)
        mapping[instance] = fold
    if duplicates:
        raise ValueError(f"duplicate repetition-1 CV rows: {duplicates[:5]}")
    if set(mapping.values()) != set(range(1, 11)):
        raise ValueError(f"CV folds are not exactly 1..10: {sorted(set(mapping.values()))}")
    fold_counts = collections.Counter(mapping.values())
    return mapping, {
        "repetition": 1,
        "instances": len(mapping),
        "fold_counts": {str(k): v for k, v in sorted(fold_counts.items())},
    }


def representation_registry() -> list[tuple[str, ...]]:
    return [("dynamic", "static")]


def profile_name(steps: Sequence[str], k: int) -> str:
    return "+".join(steps) + f"__knn{k}"


def status_available(
    instance: str,
    feature: str,
    selected_steps: Sequence[str],
    step_features: dict[str, list[str]],
    step_status: dict[str, dict[str, float | str | None]],
) -> bool:
    providers = [step for step in selected_steps if feature in step_features[step]]
    return any(str(step_status[instance][step]) == "ok" for step in providers)


def raw_matrix(
    instances: Sequence[str],
    selected_steps: Sequence[str],
    step_features: dict[str, list[str]],
    feature_values: dict[str, dict[str, float | None]],
    step_status: dict[str, dict[str, float | str | None]],
) -> tuple[np.ndarray, list[str]]:
    features = sorted({name for step in selected_steps for name in step_features[step]})
    matrix = np.full((len(instances), len(features)), np.nan, dtype=np.float64)
    for row_index, instance in enumerate(instances):
        for column, feature in enumerate(features):
            if status_available(instance, feature, selected_steps, step_features, step_status):
                value = feature_values[instance].get(feature)
                if value is not None:
                    matrix[row_index, column] = float(value)
    return matrix, features


def fit_transform_matrices(
    train_ids: Sequence[str],
    query_groups: dict[str, Sequence[str]],
    selected_steps: Sequence[str],
    step_features: dict[str, list[str]],
    feature_values: dict[str, dict[str, float | None]],
    step_status: dict[str, dict[str, float | str | None]],
) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, Any]]:
    train_raw, features = raw_matrix(
        train_ids, selected_steps, step_features, feature_values, step_status
    )
    if np.any(np.all(np.isnan(train_raw), axis=0)):
        absent = [features[i] for i in np.where(np.all(np.isnan(train_raw), axis=0))[0]]
        raise ValueError(f"all-missing training features: {absent[:10]}")
    medians = np.nanmedian(train_raw, axis=0)
    q25 = np.nanquantile(train_raw, 0.25, axis=0, method="linear")
    q75 = np.nanquantile(train_raw, 0.75, axis=0, method="linear")
    scales = q75 - q25
    scales[~np.isfinite(scales) | (scales == 0)] = 1.0

    def transform(raw: np.ndarray) -> np.ndarray:
        missing = np.isnan(raw)
        imputed = np.where(missing, medians, raw)
        numeric = (imputed - medians) / scales
        return np.concatenate((numeric, missing.astype(np.float64)), axis=1)

    train = transform(train_raw)
    queries: dict[str, np.ndarray] = {}
    missing_counts: dict[str, int] = {"train": int(np.isnan(train_raw).sum())}
    for group, ids in query_groups.items():
        raw, query_features = raw_matrix(
            ids, selected_steps, step_features, feature_values, step_status
        )
        if query_features != features:
            raise AssertionError("feature ordering drift")
        queries[group] = transform(raw)
        missing_counts[group] = int(np.isnan(raw).sum())
    return (
        train,
        queries,
        {
            "features": len(features),
            "transformed_dimensions": train.shape[1],
            "feature_name_digest": digest_json(features),
            "training_parameter_digest": digest_json(
                {
                    "median": [format(value, ".17g") for value in medians],
                    "iqr": [format(value, ".17g") for value in scales],
                }
            ),
            "missing_cells": missing_counts,
        },
    )


def neighbour_order(
    train: np.ndarray, queries: np.ndarray, *, maximum_k: int
) -> tuple[np.ndarray, np.ndarray]:
    if train.shape[0] < maximum_k:
        raise ValueError(f"only {train.shape[0]} training rows for k={maximum_k}")
    exact_rows: dict[bytes, list[int]] = {}
    for index, row in enumerate(train):
        exact_rows.setdefault(row.tobytes(), []).append(index)
    order_chunks: list[np.ndarray] = []
    distance_chunks: list[np.ndarray] = []
    train_norm = np.sum(train * train, axis=1)
    for start in range(0, queries.shape[0], 128):
        query = queries[start : start + 128]
        distances = (
            np.sum(query * query, axis=1)[:, None] + train_norm[None, :] - 2.0 * (query @ train.T)
        )
        np.maximum(distances, 0.0, out=distances)
        for row_index, row in enumerate(query):
            matches = exact_rows.get(row.tobytes())
            if matches:
                distances[row_index, matches] = 0.0
        order = np.argsort(distances, axis=1, kind="stable")[:, :maximum_k]
        ordered_distances = np.take_along_axis(distances, order, axis=1)
        order_chunks.append(order)
        distance_chunks.append(ordered_distances)
    return np.concatenate(order_chunks), np.concatenate(distance_chunks)


def learned_predictions(
    train_ids: Sequence[str],
    query_ids: dict[str, Sequence[str]],
    train_matrix: np.ndarray,
    query_matrices: dict[str, np.ndarray],
    algorithms: Sequence[str],
    runtimes: dict[str, dict[str, float]],
) -> dict[int, dict[str, np.ndarray]]:
    train_runtime = np.array(
        [[runtimes[x][algorithm] for algorithm in algorithms] for x in train_ids],
        dtype=np.float64,
    )
    output: dict[int, dict[str, np.ndarray]] = {k: {} for k in K_VALUES}
    for group, matrix in query_matrices.items():
        order, _ = neighbour_order(train_matrix, matrix, maximum_k=max(K_VALUES))
        for k in K_VALUES:
            means = np.mean(train_runtime[order[:, :k]], axis=1)
            output[k][group] = np.argmin(means, axis=1)
        if len(query_ids[group]) != matrix.shape[0]:
            raise AssertionError("query identity/matrix mismatch")
    return output


def cost_for(
    instance: str,
    steps: Sequence[str],
    step_costs: dict[str, dict[str, float | str | None]],
    step_status: dict[str, dict[str, float | str | None]],
) -> float:
    costs: list[float] = []
    for step in steps:
        value = step_costs[instance][step]
        status = str(step_status[instance][step])
        if isinstance(value, float) and math.isfinite(value) and value >= 0:
            costs.append(value)
        elif status != "ok":
            costs.append(FEATURE_CUTOFF)
        else:
            raise ValueError(f"missing cost for successful {instance}/{step}: {value!r}")
    return math.fsum(costs)


def nearest_rank(values: Sequence[float], probability: float) -> float:
    ordered = sorted(float(value) for value in values)
    rank = max(1, math.ceil(probability * len(ordered)))
    return ordered[min(len(ordered), rank) - 1]


def summary(values: Sequence[float]) -> dict[str, float]:
    if not values:
        raise ValueError("cannot summarize an empty vector")
    return {
        "mean": float(statistics.fmean(values)),
        "median": float(statistics.median(values)),
        "p95": nearest_rank(values, 0.95),
        "maximum": float(max(values)),
    }


def selection_tuple(
    losses: np.ndarray,
    timeout_flags: np.ndarray,
    acquisition: np.ndarray,
    learned_name: str,
    fallback_name: str,
) -> tuple[Any, ...]:
    metrics = summary(losses.tolist())
    return (
        int(np.sum(timeout_flags)),
        metrics["mean"],
        metrics["p95"],
        metrics["maximum"],
        float(np.mean(acquisition)),
        learned_name,
        fallback_name,
    )


def paired_bootstrap(differences: np.ndarray) -> dict[str, Any]:
    seed = int.from_bytes(hashlib.sha256(BOOTSTRAP_SEED_TEXT.encode()).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    means: list[np.ndarray] = []
    n = len(differences)
    for _ in range(0, BOOTSTRAP_REPLICATES, 500):
        batch = min(500, BOOTSTRAP_REPLICATES - sum(len(item) for item in means))
        indices = rng.integers(0, n, size=(batch, n))
        means.append(np.mean(differences[indices], axis=1))
    samples = np.concatenate(means)
    samples.sort()
    return {
        "method": "paired_instance_cluster_percentile",
        "replicates": BOOTSTRAP_REPLICATES,
        "seed_text": BOOTSTRAP_SEED_TEXT,
        "seed_u64": seed,
        "lower_95": nearest_rank(samples.tolist(), 0.025),
        "upper_95": nearest_rank(samples.tolist(), 0.975),
    }


def r19_hostile_controls(r19_core_path: Path) -> dict[str, Any]:
    import importlib.util

    spec = importlib.util.spec_from_file_location("orion02_r19_core", r19_core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R19 core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    learned = ((0, 100), (100, 0))
    fallback = ((0, 100), (100, 0))
    full = module.enumerate_joint_route_profiles(learned, fallback, (0, 1), (0, 0), timing="pre")
    diagonal = module.enumerate_joint_route_profiles(
        learned, fallback, (0, 1), (0, 0), timing="pre", legal_pairs=((0, 0), (1, 1))
    )
    full_value = module.solve_zero_sum_profiles(full)["value"]
    diagonal_value = module.solve_zero_sum_profiles(diagonal)["value"]
    timing_learned = ((0,),)
    timing_fallback = ((5,),)
    pre_profiles = module.enumerate_joint_route_profiles(
        timing_learned, timing_fallback, (0,), (10,), timing="pre"
    )
    post_profiles = module.enumerate_joint_route_profiles(
        timing_learned, timing_fallback, (0,), (10,), timing="post"
    )
    pre_value = module.deterministic_value(pre_profiles)
    post_value = module.deterministic_value(post_profiles)
    if str(full_value) != "0" or str(diagonal_value) != "50":
        raise AssertionError("R19 same-marginals hostile fixture drift")
    if str(pre_value) != "5" or str(post_value) != "10":
        raise AssertionError("R19 timing hostile fixture drift")
    return {
        "same_marginals_different_joint_value": {
            "full_legal_pair_value": str(full_value),
            "diagonal_only_value": str(diagonal_value),
            "preserved": True,
        },
        "acquisition_timing_reversal": {
            "pre_acquisition_value": str(pre_value),
            "post_acquisition_value": str(post_value),
            "preserved": True,
        },
    }


def fold_role(test_fold: int, offset: int) -> int:
    return ((test_fold - 1 + offset) % 10) + 1


def execute(subject_repo: Path) -> dict[str, Any]:
    upstream = verify_subject(subject_repo)
    scenario = subject_repo / SCENARIO
    algorithms, step_features = load_description(scenario / "description.txt")
    runtimes, timeouts, algorithm_audit = load_algorithm_runs(
        scenario / "algorithm_runs.arff", algorithms
    )
    feature_values, feature_names, feature_audit = load_feature_values(
        scenario / "feature_values.arff"
    )
    step_costs, _, cost_audit = load_step_table(scenario / "feature_costs.arff", numeric=True)
    step_status, _, status_audit = load_step_table(
        scenario / "feature_runstatus.arff", numeric=False
    )
    cv, cv_audit = load_cv(scenario / "cv.arff")

    instance_sets = {
        "algorithm_runs": set(runtimes),
        "feature_values": set(feature_values),
        "feature_costs": set(step_costs),
        "feature_runstatus": set(step_status),
        "cv_repetition_1": set(cv),
    }
    first_set = next(iter(instance_sets.values()))
    if not all(value == first_set for value in instance_sets.values()):
        counts = {name: len(value) for name, value in instance_sets.items()}
        raise ValueError(f"subject instance sets differ: {counts}")
    instances = sorted(first_set)
    if not instances:
        raise ValueError("empty admitted subject")
    if set(feature_names) != {
        feature for features in step_features.values() for feature in features
    }:
        raise ValueError("description/feature-value registry mismatch")

    oracle = {x: min(runtimes[x].values()) for x in instances}
    representations = representation_registry()
    learned_names = [profile_name(steps, k) for steps in representations for k in K_VALUES]
    legal_pairs_product = list(itertools.product(learned_names, algorithms))
    legal_pairs_nested = [
        (learned, fallback) for learned in learned_names for fallback in algorithms
    ]
    if legal_pairs_product != legal_pairs_nested or len(legal_pairs_product) != 44:
        raise AssertionError("legal Cartesian joint grammar drift")
    legal_pair_digest = digest_json(legal_pairs_product)

    rows_out: list[dict[str, Any]] = []
    folds_out: list[dict[str, Any]] = []
    all_pair_records: list[dict[str, Any]] = []
    transform_digests: list[dict[str, Any]] = []
    full_pairing_selected_every_fold = True
    route_measurable = True
    exact_timing_identity = True
    common_oracle_signs = True
    shuffled_never_authorized = True

    for test_fold in range(1, 11):
        calibration_fold = fold_role(test_fold, 1)
        pair_selection_fold = fold_role(test_fold, 2)
        route_fit_fold = fold_role(test_fold, 3)
        groups = {
            "test": sorted(x for x in instances if cv[x] == test_fold),
            "calibration": sorted(x for x in instances if cv[x] == calibration_fold),
            "pair_select": sorted(x for x in instances if cv[x] == pair_selection_fold),
            "route_fit": sorted(x for x in instances if cv[x] == route_fit_fold),
        }
        excluded = {test_fold, calibration_fold, pair_selection_fold, route_fit_fold}
        train_ids = sorted(x for x in instances if cv[x] not in excluded)
        if any(not value for value in groups.values()) or not train_ids:
            raise ValueError(f"empty split role for outer fold {test_fold}")
        if set().union(*map(set, groups.values()), set(train_ids)) != set(instances):
            raise AssertionError("fold-role coverage mismatch")
        role_sets = [set(train_ids), *(set(value) for value in groups.values())]
        if any(left & right for i, left in enumerate(role_sets) for right in role_sets[i + 1 :]):
            raise AssertionError("fold-role overlap")

        learned_losses: dict[str, dict[str, np.ndarray]] = {}
        learned_timeouts: dict[str, dict[str, np.ndarray]] = {}
        learned_costs: dict[str, dict[str, np.ndarray]] = {}
        for steps in representations:
            train_matrix, query_matrices, transform_audit = fit_transform_matrices(
                train_ids,
                groups,
                steps,
                step_features,
                feature_values,
                step_status,
            )
            predictions = learned_predictions(
                train_ids,
                groups,
                train_matrix,
                query_matrices,
                algorithms,
                runtimes,
            )
            transform_digests.append(
                {
                    "test_fold": test_fold,
                    "steps": list(steps),
                    **transform_audit,
                }
            )
            for k in K_VALUES:
                name = profile_name(steps, k)
                learned_losses[name] = {}
                learned_timeouts[name] = {}
                learned_costs[name] = {}
                for group, ids in groups.items():
                    solver_indices = predictions[k][group]
                    costs = np.array(
                        [cost_for(x, steps, step_costs, step_status) for x in ids], dtype=np.float64
                    )
                    losses = np.array(
                        [
                            costs[i] + runtimes[x][algorithms[int(solver_indices[i])]] - oracle[x]
                            for i, x in enumerate(ids)
                        ],
                        dtype=np.float64,
                    )
                    timeout_flags = np.array(
                        [
                            timeouts[x][algorithms[int(solver_indices[i])]]
                            for i, x in enumerate(ids)
                        ],
                        dtype=bool,
                    )
                    learned_losses[name][group] = losses
                    learned_timeouts[name][group] = timeout_flags
                    learned_costs[name][group] = costs

        cheap_train, cheap_queries, cheap_transform_audit = fit_transform_matrices(
            train_ids,
            groups,
            ("static",),
            step_features,
            feature_values,
            step_status,
        )
        del cheap_train
        transform_digests.append(
            {
                "test_fold": test_fold,
                "steps": ["static"],
                "route_only": True,
                **cheap_transform_audit,
            }
        )
        route_matrix = cheap_queries["route_fit"]
        route_neighbours: dict[str, np.ndarray] = {}
        route_distances: dict[str, np.ndarray] = {}
        for group in ("pair_select", "calibration", "test"):
            order, distance = neighbour_order(route_matrix, cheap_queries[group], maximum_k=ROUTE_K)
            route_neighbours[group] = order
            route_distances[group] = distance[:, 0]

        fallback_losses: dict[str, dict[str, np.ndarray]] = {}
        fallback_timeouts: dict[str, dict[str, np.ndarray]] = {}
        fallback_costs: dict[str, dict[str, np.ndarray]] = {}
        for algorithm in algorithms:
            fallback_losses[algorithm] = {}
            fallback_timeouts[algorithm] = {}
            fallback_costs[algorithm] = {}
            for group, ids in groups.items():
                costs = np.array(
                    [cost_for(x, ("static",), step_costs, step_status) for x in ids],
                    dtype=np.float64,
                )
                fallback_costs[algorithm][group] = costs
                fallback_losses[algorithm][group] = np.array(
                    [costs[i] + runtimes[x][algorithm] - oracle[x] for i, x in enumerate(ids)],
                    dtype=np.float64,
                )
                fallback_timeouts[algorithm][group] = np.array(
                    [timeouts[x][algorithm] for x in ids], dtype=bool
                )

        pair_records: list[dict[str, Any]] = []
        pair_state: dict[tuple[str, str], dict[str, Any]] = {}
        for learned_name, fallback in legal_pairs_product:
            route_delta = (
                fallback_losses[fallback]["route_fit"] - learned_losses[learned_name]["route_fit"]
            )
            predictions: dict[str, np.ndarray] = {}
            for group in ("pair_select", "calibration", "test"):
                predictions[group] = np.mean(
                    route_delta[route_neighbours[group][:, :ROUTE_K]], axis=1
                )
            group = "pair_select"
            choose_learned = predictions[group] >= 0
            losses = np.where(
                choose_learned,
                learned_losses[learned_name][group],
                fallback_losses[fallback][group],
            )
            timeout_flags = np.where(
                choose_learned,
                learned_timeouts[learned_name][group],
                fallback_timeouts[fallback][group],
            )
            acquisition = np.where(
                choose_learned,
                learned_costs[learned_name][group],
                fallback_costs[fallback][group],
            )
            key = selection_tuple(losses, timeout_flags, acquisition, learned_name, fallback)
            profile_digest = digest_json(
                {
                    "learned": [
                        format(value, ".17g") for value in learned_losses[learned_name][group]
                    ],
                    "fallback": [
                        format(value, ".17g") for value in fallback_losses[fallback][group]
                    ],
                    "point_route": [format(value, ".17g") for value in losses],
                }
            )
            record = {
                "learned_profile": learned_name,
                "fallback_solver": fallback,
                "selection_tuple": [
                    key[0],
                    key[1],
                    key[2],
                    key[3],
                    key[4],
                    key[5],
                    key[6],
                ],
                "point_learned_count": int(np.sum(choose_learned)),
                "profile_digest": profile_digest,
            }
            pair_records.append(record)
            pair_state[(learned_name, fallback)] = {
                "key": key,
                "predictions": predictions,
                "route_delta": route_delta,
            }
        if len(pair_records) != 44 or len(pair_state) != 44:
            raise AssertionError("not every legal pair was evaluated")
        selected_pair = min(pair_state, key=lambda pair: pair_state[pair]["key"])
        selected_learned, selected_fallback = selected_pair
        selected = pair_state[selected_pair]
        selected_record = next(
            record
            for record in pair_records
            if (record["learned_profile"], record["fallback_solver"]) == selected_pair
        )
        selected_record["selected"] = True
        for record in pair_records:
            record.setdefault("selected", False)

        diagonal_pairs = {
            (learned, algorithms[index % len(algorithms)])
            for index, learned in enumerate(learned_names)
        }
        diagonal_selected = min(diagonal_pairs, key=lambda pair: pair_state[pair]["key"])
        full_pairing_selected_every_fold &= selected_pair in set(legal_pairs_product)

        calibration_delta = (
            fallback_losses[selected_fallback]["calibration"]
            - learned_losses[selected_learned]["calibration"]
        )
        calibration_prediction = selected["predictions"]["calibration"]
        residuals = np.abs(calibration_delta - calibration_prediction)
        conformal_rank = math.ceil((len(residuals) + 1) * (1 - ALPHA))
        radius = (
            float(np.sort(residuals)[conformal_rank - 1])
            if conformal_rank <= len(residuals)
            else math.inf
        )
        test_prediction = selected["predictions"]["test"]
        lower = test_prediction - radius
        upper = test_prediction + radius
        direct_choose_learned = lower >= 0
        point_choose_learned = test_prediction >= 0
        calibration_distance_median = float(
            statistics.median(route_distances["calibration"].tolist())
        )
        uncertainty_choose_learned = route_distances["test"] <= calibration_distance_median
        learned_count = int(np.sum(direct_choose_learned))
        random_choose_learned = np.zeros(len(groups["test"]), dtype=bool)
        random_order = sorted(
            range(len(groups["test"])),
            key=lambda index: (
                hashlib.sha256(f"{test_fold}:{groups['test'][index]}".encode()).hexdigest(),
                groups["test"][index],
            ),
        )
        random_choose_learned[random_order[:learned_count]] = True

        learned_loss = learned_losses[selected_learned]["test"]
        fallback_loss = fallback_losses[selected_fallback]["test"]
        learned_timeout = learned_timeouts[selected_learned]["test"]
        fallback_timeout = fallback_timeouts[selected_fallback]["test"]
        learned_cost = learned_costs[selected_learned]["test"]
        fallback_cost = fallback_costs[selected_fallback]["test"]
        actual_delta = fallback_loss - learned_loss
        decisions = {
            "direct_relative_certified": direct_choose_learned,
            "always_fallback": np.zeros(len(groups["test"]), dtype=bool),
            "always_learned": np.ones(len(groups["test"]), dtype=bool),
            "point_relative": point_choose_learned,
            "uncertainty_only": uncertainty_choose_learned,
            "random_rate_matched": random_choose_learned,
            "oracle_route": learned_loss <= fallback_loss,
            "post_acquisition_same_route": direct_choose_learned.copy(),
        }
        arm_losses = {
            arm: np.where(choice, learned_loss, fallback_loss) for arm, choice in decisions.items()
        }
        arm_timeouts = {
            arm: np.where(choice, learned_timeout, fallback_timeout)
            for arm, choice in decisions.items()
        }
        arm_costs = {
            arm: np.where(choice, learned_cost, fallback_cost) for arm, choice in decisions.items()
        }
        post_loss = arm_losses["direct_relative_certified"].copy()
        post_cost = arm_costs["direct_relative_certified"].copy()
        fallback_positions = ~direct_choose_learned
        avoided_extra = learned_cost - fallback_cost
        if np.any(avoided_extra < -TOL):
            raise ValueError("learned representation costs less than pre-route representation")
        post_loss[fallback_positions] += avoided_extra[fallback_positions]
        post_cost[fallback_positions] += avoided_extra[fallback_positions]
        arm_losses["post_acquisition_same_route"] = post_loss
        arm_timeouts["post_acquisition_same_route"] = arm_timeouts[
            "direct_relative_certified"
        ].copy()
        arm_costs["post_acquisition_same_route"] = post_cost
        exact_timing_identity &= bool(
            np.allclose(
                post_loss - arm_losses["direct_relative_certified"],
                np.where(fallback_positions, avoided_extra, 0.0),
                atol=TOL,
                rtol=0,
            )
        )
        common_oracle_signs &= bool(
            np.array_equal(
                np.sign(actual_delta),
                np.sign(
                    (fallback_loss + np.array([oracle[x] for x in groups["test"]]))
                    - (learned_loss + np.array([oracle[x] for x in groups["test"]]))
                ),
            )
        )

        attained: dict[str, set[bool]] = collections.defaultdict(set)
        for index, vector in enumerate(cheap_queries["test"]):
            attained[digest_json([format(value, ".17g") for value in vector])].add(
                bool(direct_choose_learned[index])
            )
        route_measurable &= all(len(choices) == 1 for choices in attained.values())

        shuffled_delta = np.roll(selected["route_delta"], 1)
        shuffled_prediction = np.mean(shuffled_delta[route_neighbours["test"][:, :ROUTE_K]], axis=1)
        shuffled_never_authorized &= digest_json(
            [format(value, ".17g") for value in shuffled_prediction]
        ) != digest_json([format(value, ".17g") for value in test_prediction])

        fold_rows: list[dict[str, Any]] = []
        for index, instance in enumerate(groups["test"]):
            row = {
                "instance_id": instance,
                "test_fold": test_fold,
                "learned_profile": selected_learned,
                "fallback_solver": selected_fallback,
                "relative_prediction": float(test_prediction[index]),
                "interval_lower": float(lower[index]),
                "interval_upper": float(upper[index]),
                "actual_delta_fallback_minus_learned": float(actual_delta[index]),
                "learned_loss": float(learned_loss[index]),
                "fallback_loss": float(fallback_loss[index]),
                "learned_timeout": bool(learned_timeout[index]),
                "fallback_timeout": bool(fallback_timeout[index]),
                "learned_acquisition": float(learned_cost[index]),
                "fallback_acquisition": float(fallback_cost[index]),
                "interval_covers_delta": bool(
                    lower[index] - TOL <= actual_delta[index] <= upper[index] + TOL
                ),
                "certified_learned_sign_error": bool(
                    direct_choose_learned[index] and actual_delta[index] < -TOL
                ),
                "choices": {
                    arm: "learned" if bool(choice[index]) else "fallback"
                    for arm, choice in decisions.items()
                },
                "losses": {arm: float(loss[index]) for arm, loss in arm_losses.items()},
                "timeouts": {arm: bool(flags[index]) for arm, flags in arm_timeouts.items()},
                "acquisition": {arm: float(cost[index]) for arm, cost in arm_costs.items()},
            }
            fold_rows.append(row)
        rows_out.extend(fold_rows)
        all_pair_records.extend([{"test_fold": test_fold, **record} for record in pair_records])
        folds_out.append(
            {
                "test_fold": test_fold,
                "roles": {
                    "model_train_folds": sorted(set(range(1, 11)) - excluded),
                    "route_fit_fold": route_fit_fold,
                    "pair_selection_fold": pair_selection_fold,
                    "calibration_fold": calibration_fold,
                    "test_fold": test_fold,
                },
                "role_counts": {
                    "model_train": len(train_ids),
                    **{name: len(ids) for name, ids in groups.items()},
                },
                "role_membership_digest": digest_json({"model_train": train_ids, **groups}),
                "legal_pair_count": len(pair_records),
                "legal_pair_digest": legal_pair_digest,
                "selected_pair": {
                    "learned_profile": selected_learned,
                    "fallback_solver": selected_fallback,
                    "selection_tuple": list(selected["key"]),
                },
                "diagonal_only_hostile": {
                    "pair_count": len(diagonal_pairs),
                    "selected_pair": list(diagonal_selected),
                    "selected_tuple": list(pair_state[diagonal_selected]["key"]),
                    "not_used_as_authority": True,
                },
                "conformal": {
                    "alpha": ALPHA,
                    "calibration_count": len(residuals),
                    "rank": conformal_rank,
                    "radius": radius,
                },
                "test_row_digest": digest_json(fold_rows),
            }
        )

    if len(rows_out) != len(instances) or len({row["instance_id"] for row in rows_out}) != len(
        instances
    ):
        raise AssertionError("out-of-fold rows are not one-per-instance")

    arm_names = sorted(rows_out[0]["losses"])
    arms: dict[str, Any] = {}
    for arm in arm_names:
        losses = [row["losses"][arm] for row in rows_out]
        arms[arm] = {
            **summary(losses),
            "timeout_count": sum(row["timeouts"][arm] for row in rows_out),
            "timeout_rate": sum(row["timeouts"][arm] for row in rows_out) / len(rows_out),
            "learned_count": sum(row["choices"].get(arm) == "learned" for row in rows_out),
            "mean_acquisition": statistics.fmean(row["acquisition"][arm] for row in rows_out),
        }
    differences = np.array(
        [
            row["losses"]["direct_relative_certified"] - row["losses"]["point_relative"]
            for row in rows_out
        ],
        dtype=np.float64,
    )
    bootstrap = paired_bootstrap(differences)
    coverage = statistics.fmean(row["interval_covers_delta"] for row in rows_out)
    certified_rows = [
        row for row in rows_out if row["choices"]["direct_relative_certified"] == "learned"
    ]
    certified_fraction = len(certified_rows) / len(rows_out)
    sign_error = (
        statistics.fmean(row["certified_learned_sign_error"] for row in certified_rows)
        if certified_rows
        else 0.0
    )
    primary = arms["direct_relative_certified"]
    comparator = arms["point_relative"]
    difference = primary["mean"] - comparator["mean"]
    relative_reduction = (
        (comparator["mean"] - primary["mean"]) / comparator["mean"]
        if comparator["mean"] > TOL
        else None
    )
    material = (
        relative_reduction is not None
        and relative_reduction >= 0.05
        and bootstrap["upper_95"] < 0
        and primary["timeout_count"] <= comparator["timeout_count"]
        and coverage >= 0.90
        and sign_error <= 0.10
    )
    if certified_fraction < 0.01:
        terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_NO_CERTIFIED_LEARNED_COVERAGE"
    elif material:
        terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_JOINT_ROUTE_VALUE"
    elif difference < -TOL:
        terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_STRICT_BUT_NOT_MATERIAL"
    elif abs(difference) <= TOL:
        terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_NULL"
    else:
        terminal = "C_R21_CSPMZN_DIRECT_RELATIVE_ADVERSE"

    sbs = min(
        algorithms,
        key=lambda algorithm: (
            statistics.fmean(runtimes[x][algorithm] for x in instances),
            algorithm,
        ),
    )
    r19_core = Path(__file__).resolve().parents[1] / "r19" / "fiberguard_joint_route_r19_core.py"
    hostile = {
        "complete_cartesian_pairs_evaluated_each_fold": len(all_pair_records) == 440,
        "product_and_nested_pair_enumerations_identical": True,
        "legal_pair_digest": legal_pair_digest,
        "full_pairing_selected_every_fold": full_pairing_selected_every_fold,
        "diagonal_only_pairing_never_used_as_authority": True,
        "route_measurable_on_pre_acquisition_information": route_measurable,
        "pre_post_timing_identity_exact": exact_timing_identity,
        "common_oracle_subtraction_preserves_pair_sign": common_oracle_signs,
        "shuffled_relative_labels_authorized": False,
        "shuffled_relative_predictions_differ": shuffled_never_authorized,
        "one_out_of_fold_loss_per_instance_per_arm": all(
            set(row["losses"])
            == set(row["choices"])
            == set(row["timeouts"])
            == set(row["acquisition"])
            == set(arm_names)
            for row in rows_out
        ),
        **r19_hostile_controls(r19_core),
    }
    if not all(
        value is True
        for key, value in hostile.items()
        if isinstance(value, bool) and key != "shuffled_relative_labels_authorized"
    ):
        raise AssertionError(f"hostile control failed: {hostile}")

    return {
        "schema": SCHEMA,
        "terminal": terminal,
        "upstream": upstream,
        "protocol": {
            "round": 2,
            "previous_round": "BNSL-2016_NULL_PRESERVED",
            "subject_untouched_at_freeze": True,
            "mechanism": "direct_relative_joint_route_pre_optional_acquisition",
            "alpha": ALPHA,
            "learned_representations": [list(item) for item in representations],
            "learned_k": list(K_VALUES),
            "route_k": ROUTE_K,
            "learned_profile_count": len(learned_names),
            "fallback_profile_count": len(algorithms),
            "legal_pair_count_per_fold": len(legal_pairs_product),
            "primary_comparator": "point_relative",
        },
        "corpus": {
            "instances": len(instances),
            "algorithms": algorithms,
            "steps": list(EXPECTED_STEPS),
            "features": len(feature_names),
            "algorithm_audit": algorithm_audit,
            "feature_audit": feature_audit,
            "feature_cost_audit": cost_audit,
            "feature_status_audit": status_audit,
            "cv_audit": cv_audit,
            "instance_set_equality": True,
        },
        "portfolio": {
            "SBS": sbs,
            "SBS_mean_runtime": statistics.fmean(runtimes[x][sbs] for x in instances),
            "VBS_mean_runtime": statistics.fmean(oracle.values()),
        },
        "folds": folds_out,
        "pair_selection_profiles": all_pair_records,
        "transform_audits": transform_digests,
        "out_of_fold": {
            "rows": rows_out,
            "row_count": len(rows_out),
            "row_digest": digest_json(rows_out),
            "arms": arms,
            "paired_primary_minus_point": {
                "mean_difference": float(np.mean(differences)),
                "relative_mean_reduction": relative_reduction,
                "bootstrap_95": bootstrap,
            },
            "paired_interval": {
                "nominal_coverage": 1 - ALPHA,
                "empirical_coverage": coverage,
                "certified_learned_count": len(certified_rows),
                "certified_learned_fraction": certified_fraction,
                "certified_learned_sign_error_rate": sign_error,
            },
        },
        "hostile_controls": hostile,
        "authority": {
            "corpus_out_of_fold_historical_evidence": True,
            "paired_interval_authority": "MARGINAL_SPLIT_CONFORMAL_UNDER_EXCHANGEABILITY",
            "deterministic_or_pathwise_route_safety": False,
            "unseen_domain_transfer": False,
            "production_value": False,
            "external_independent_replay": False,
            "novelty_authority": False,
            "journal_authority": False,
            "submission_authorized": False,
            "R11_R14_R15_R16_R18_R19_CNBR_CNBR2_BNSL_records_modified": False,
        },
    }


def self_test() -> None:
    assert representation_registry() == [("dynamic", "static")]
    assert [fold_role(10, offset) for offset in (1, 2, 3)] == [1, 2, 3]
    assert nearest_rank([1, 2, 3, 4], 0.95) == 4
    assert len(list(itertools.product(range(4), range(11)))) == 44
    print("ORION02_R21_STATIC_SELF_TEST_PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject-repo", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--terminal-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.subject_repo is None or args.output is None:
        parser.error("--subject-repo and --output are required outside --self-test")
    try:
        result = execute(args.subject_repo)
    except (ValueError, OSError, MemoryError, subprocess.CalledProcessError) as error:
        result = {
            "schema": SCHEMA,
            "terminal": "CANNOT_CHECK_CSPMZN_DIRECT_RELATIVE_SOURCE_OR_RESOURCE",
            "failure": {
                "type": type(error).__name__,
                "message": str(error),
            },
            "upstream": {
                "repository": ASLIB_REPO,
                "commit": ASLIB_COMMIT,
                "scenario": SCENARIO,
            },
            "authority": {
                "scientific_route_result_emitted": False,
                "submission_authorized": False,
            },
        }
    payload = canonical_json(result) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    if args.terminal_output:
        args.terminal_output.parent.mkdir(parents=True, exist_ok=True)
        args.terminal_output.write_text(result["terminal"] + "\n", encoding="utf-8")
    print(result["terminal"])
    print(f"RESULT_SHA256={sha256_bytes(payload.encode())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
