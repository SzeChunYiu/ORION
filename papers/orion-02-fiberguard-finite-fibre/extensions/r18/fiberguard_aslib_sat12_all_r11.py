#!/usr/bin/env python3
"""Exact FiberGuard action-regret audit on a pinned ASlib SAT12-ALL corpus.

This program is deliberately corpus-complete, not a generalization claim.  It
uses the benchmark's own algorithm runtimes and feature-step acquisition costs
and computes exact robust static selector values for every dependency-closed
feature-step set.

Operational loss uses the standard ASlib PAR10 convention for non-ok solver
runs.  Feature acquisition costs remain the recorded ASlib step runtime.  Both
are therefore expressed in seconds / PAR10 seconds-equivalent under the frozen
benchmark convention.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Any, Iterable

import yaml

SCHEMA = "ORION.FiberGuard.ASlibSAT12ALL.R11.v1"
ASLIB_REPO = "https://github.com/coseal/aslib_data.git"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SCENARIO = "SAT12-ALL"
EXPECTED_BLOBS = {
    "description.txt": "2c3662ac80c9cc4eba2857c2d9a69209cb200b94",
    "algorithm_runs.arff": "4e27dcc3c40c76e8c754a66d465b156731a85080",
    "feature_values.arff": "a0da43a740da5faf28dae1892ecdcef42cb53f61",
    "feature_costs.arff": "4b0e5685712363ebb50d0dc5bd8e7c9532a6b2ea",
    "feature_runstatus.arff": "cfec4e2bf2d48b5868c40bd521be3a914311c0fe",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


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
    attrs: list[str] = []
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
                    attrs.append(_attribute_name(stripped))
                elif lower == "@data":
                    in_data = True
                continue
            row = next(csv.reader([raw], skipinitialspace=True))
            if len(row) != len(attrs):
                raise ValueError(
                    f"row width {len(row)} does not match {len(attrs)} attributes in {path}"
                )
            rows.append([value.strip() for value in row])
    if not attrs or not in_data:
        raise ValueError(f"invalid ARFF file: {path}")
    return attrs, rows


def most_common_status(values: Iterable[str]) -> str:
    counter = collections.Counter(values)
    if not counter:
        raise ValueError("empty status list")
    # Match the ASlibScenario convention: most frequent status.  Ties are
    # broken deterministically rather than depending on input row order.
    return min(counter, key=lambda value: (-counter[value], value))


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median of empty list")
    return float(statistics.median(values))


def load_algorithm_runs(
    path: Path, cutoff: float
) -> tuple[dict[str, dict[str, float]], list[str], dict[str, Any]]:
    attrs, rows = read_arff(path)
    required = ["instance_id", "repetition", "algorithm", "runtime", "runstatus"]
    index = {name: attrs.index(name) for name in required}
    grouped: dict[tuple[str, str], list[tuple[float, str]]] = collections.defaultdict(list)
    algorithms: set[str] = set()
    for row in rows:
        instance = row[index["instance_id"]]
        algorithm = row[index["algorithm"]]
        runtime = float(row[index["runtime"]])
        status = row[index["runstatus"]]
        grouped[(instance, algorithm)].append((runtime, status))
        algorithms.add(algorithm)

    algos = sorted(algorithms)
    by_instance: dict[str, dict[str, float]] = collections.defaultdict(dict)
    status_counts: collections.Counter[str] = collections.Counter()
    repetition_counts: collections.Counter[int] = collections.Counter()
    for (instance, algorithm), values in grouped.items():
        runtime = median([value for value, _ in values])
        status = most_common_status(status for _, status in values)
        status_counts[status] += 1
        repetition_counts[len(values)] += 1
        # Standard ASlib runtime convention: non-ok -> PAR10.
        by_instance[instance][algorithm] = runtime if status == "ok" else 10.0 * cutoff

    incomplete = [
        instance
        for instance, mapping in by_instance.items()
        if set(mapping) != set(algos)
    ]
    if incomplete:
        raise ValueError(f"algorithm matrix incomplete for {len(incomplete)} instances")

    audit = {
        "algorithm_count": len(algos),
        "algorithm_measurement_status_counts": dict(sorted(status_counts.items())),
        "repetitions_per_instance_algorithm": dict(sorted(repetition_counts.items())),
        "par10_cutoff": 10.0 * cutoff,
    }
    return dict(by_instance), algos, audit


def load_feature_values(path: Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    attrs, rows = read_arff(path)
    if attrs[:2] != ["instance_id", "repetition"]:
        raise ValueError("unexpected feature-values prefix")
    feature_names = attrs[2:]
    grouped: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for row in rows:
        instance = row[0]
        for name, value in zip(feature_names, row[2:]):
            grouped[(instance, name)].append(value)

    by_instance: dict[str, dict[str, str]] = collections.defaultdict(dict)
    for (instance, name), values in grouped.items():
        numeric = [float(value) for value in values if value != "?"]
        if len(numeric) != len(values):
            # Preserve missingness as an observed representation symbol.
            by_instance[instance][name] = "?"
        else:
            mean = math.fsum(numeric) / len(numeric)
            by_instance[instance][name] = format(mean, ".17g")
    return dict(by_instance), feature_names


def load_step_table(
    path: Path, *, numeric: bool
) -> tuple[dict[str, dict[str, float | str]], list[str]]:
    attrs, rows = read_arff(path)
    if attrs[:2] != ["instance_id", "repetition"]:
        raise ValueError(f"unexpected step-table prefix in {path}")
    steps = attrs[2:]
    grouped: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for row in rows:
        instance = row[0]
        for step, value in zip(steps, row[2:]):
            grouped[(instance, step)].append(value)

    by_instance: dict[str, dict[str, float | str]] = collections.defaultdict(dict)
    for (instance, step), values in grouped.items():
        if numeric:
            numbers = [float(value) for value in values if value != "?"]
            by_instance[instance][step] = median(numbers) if numbers else math.nan
        else:
            by_instance[instance][step] = most_common_status(values)
    return dict(by_instance), steps


def dependency_closure(
    selected: Iterable[str], feature_steps: dict[str, dict[str, Any]]
) -> tuple[str, ...]:
    closure = set(selected)
    changed = True
    while changed:
        changed = False
        for step in tuple(closure):
            requirements = feature_steps.get(step, {}).get("requires", []) or []
            if isinstance(requirements, str):
                requirements = [requirements]
            for required in requirements:
                if required not in closure:
                    closure.add(required)
                    changed = True
    return tuple(sorted(closure))


def enumerate_dependency_closed_sets(
    steps: list[str], feature_steps: dict[str, dict[str, Any]]
) -> list[tuple[str, ...]]:
    result: set[tuple[str, ...]] = {()}
    for mask in range(1 << len(steps)):
        chosen = [steps[i] for i in range(len(steps)) if (mask >> i) & 1]
        result.add(dependency_closure(chosen, feature_steps))
    return sorted(result, key=lambda row: (len(row), row))


def step_signature(
    instance: str,
    selected: tuple[str, ...],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
) -> tuple[Any, ...]:
    signature: list[Any] = []
    for step in selected:
        status = str(feature_status.get(instance, {}).get(step, "other"))
        signature.extend((step, status))
        provides = feature_steps.get(step, {}).get("provides", []) or []
        if isinstance(provides, str):
            provides = [provides]
        for feature in provides:
            signature.extend((feature, feature_values.get(instance, {}).get(feature, "?")))
    return tuple(signature)


def feature_cost(
    instance: str,
    selected: tuple[str, ...],
    feature_costs: dict[str, dict[str, float | str]],
    feature_status: dict[str, dict[str, float | str]],
    feature_cutoff: float,
) -> float:
    total = 0.0
    for step in selected:
        value = feature_costs.get(instance, {}).get(step, math.nan)
        status = str(feature_status.get(instance, {}).get(step, "other"))
        if isinstance(value, float) and math.isfinite(value):
            total += value
        elif status != "ok":
            total += feature_cutoff
        else:
            raise ValueError(f"missing numeric cost for successful step {step!r} on {instance!r}")
    return total


def robust_fibre_choice(
    instances: list[str],
    algorithms: list[str],
    runtimes: dict[str, dict[str, float]],
    oracle: dict[str, float],
    acquisition: dict[str, float],
) -> tuple[float, str, dict[str, float]]:
    losses: dict[str, float] = {}
    for algorithm in algorithms:
        losses[algorithm] = max(
            acquisition[instance] + runtimes[instance][algorithm] - oracle[instance]
            for instance in instances
        )
    best = min(algorithms, key=lambda algorithm: (losses[algorithm], algorithm))
    return losses[best], best, losses


def compressed_witness(
    instances: list[str],
    algorithms: list[str],
    runtimes: dict[str, dict[str, float]],
    oracle: dict[str, float],
    acquisition: dict[str, float],
) -> dict[str, Any]:
    worst_for_action: dict[str, tuple[float, str]] = {}
    for algorithm in algorithms:
        candidates = [
            (
                acquisition[instance] + runtimes[instance][algorithm] - oracle[instance],
                instance,
            )
            for instance in instances
        ]
        worst_for_action[algorithm] = max(candidates, key=lambda row: (row[0], row[1]))
    witnesses = sorted({instance for _, instance in worst_for_action.values()})
    full_value, _, _ = robust_fibre_choice(
        instances, algorithms, runtimes, oracle, acquisition
    )
    witness_value, _, _ = robust_fibre_choice(
        witnesses, algorithms, runtimes, oracle, acquisition
    )
    if abs(full_value - witness_value) > 1e-9:
        raise AssertionError("deterministic witness compression failed")
    return {
        "full_fibre_size": len(instances),
        "witness_size": len(witnesses),
        "action_count": len(algorithms),
        "value": full_value,
        "witness_instances": witnesses,
    }


def evaluate_representation(
    selected: tuple[str, ...],
    instances: list[str],
    algorithms: list[str],
    runtimes: dict[str, dict[str, float]],
    oracle: dict[str, float],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_costs: dict[str, dict[str, float | str]],
    feature_status: dict[str, dict[str, float | str]],
    feature_cutoff: float,
) -> dict[str, Any]:
    acquisition = {
        instance: feature_cost(
            instance, selected, feature_costs, feature_status, feature_cutoff
        )
        for instance in instances
    }
    fibres: dict[tuple[Any, ...], list[str]] = collections.defaultdict(list)
    for instance in instances:
        fibres[
            step_signature(
                instance, selected, feature_steps, feature_values, feature_status
            )
        ].append(instance)

    worst_total = -1.0
    worst_action_only = -1.0
    chosen: dict[tuple[Any, ...], str] = {}
    worst_key: tuple[Any, ...] | None = None
    per_instance_excess: dict[str, float] = {}

    zero_acquisition = {instance: 0.0 for instance in instances}
    for key, members in fibres.items():
        total_value, action, _ = robust_fibre_choice(
            members, algorithms, runtimes, oracle, acquisition
        )
        action_value, _, _ = robust_fibre_choice(
            members, algorithms, runtimes, oracle, zero_acquisition
        )
        if (total_value, repr(key)) > (worst_total, repr(worst_key)):
            worst_total = total_value
            worst_key = key
        worst_action_only = max(worst_action_only, action_value)
        chosen[key] = action
        for instance in members:
            per_instance_excess[instance] = (
                acquisition[instance]
                + runtimes[instance][action]
                - oracle[instance]
            )

    assert worst_key is not None
    worst_members = fibres[worst_key]
    witness = compressed_witness(
        worst_members, algorithms, runtimes, oracle, acquisition
    )

    values = sorted(per_instance_excess.values())
    mean_feature_cost = statistics.fmean(acquisition.values())
    p95_index = min(len(values) - 1, math.ceil(0.95 * len(values)) - 1)
    return {
        "steps": list(selected),
        "fibre_count": len(fibres),
        "maximum_fibre_size": max(map(len, fibres.values())),
        "robust_action_only_regret": worst_action_only,
        "robust_total_excess_cost": worst_total,
        "mean_total_excess_cost": statistics.fmean(values),
        "median_total_excess_cost": statistics.median(values),
        "p95_total_excess_cost": values[p95_index],
        "mean_feature_cost": mean_feature_cost,
        "maximum_feature_cost": max(acquisition.values(), default=0.0),
        "worst_fibre_witness": witness,
    }


def pareto_frontier(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Two-axis descriptive frontier: mean feature cost vs robust action-only regret.
    frontier: list[dict[str, Any]] = []
    for row in rows:
        dominated = False
        for other in rows:
            if other is row:
                continue
            if (
                other["mean_feature_cost"] <= row["mean_feature_cost"] + 1e-12
                and other["robust_action_only_regret"]
                <= row["robust_action_only_regret"] + 1e-12
                and (
                    other["mean_feature_cost"] < row["mean_feature_cost"] - 1e-12
                    or other["robust_action_only_regret"]
                    < row["robust_action_only_regret"] - 1e-12
                )
            ):
                dominated = True
                break
        if not dominated:
            frontier.append(row)
    return sorted(
        frontier,
        key=lambda row: (
            row["mean_feature_cost"],
            row["robust_action_only_regret"],
            len(row["steps"]),
            row["steps"],
        ),
    )


def validate_upstream(root: Path) -> dict[str, Any]:
    scenario_root = root / SCENARIO
    rows = {}
    for name, expected_blob in EXPECTED_BLOBS.items():
        path = scenario_root / name
        if not path.exists():
            raise FileNotFoundError(path)
        actual_blob = git_blob_sha(path)
        if actual_blob != expected_blob:
            raise ValueError(
                f"upstream blob mismatch for {name}: {actual_blob} != {expected_blob}"
            )
        rows[name] = {
            "git_blob_sha1": actual_blob,
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return rows


def run(root: Path) -> dict[str, Any]:
    upstream = validate_upstream(root)
    scenario_root = root / SCENARIO
    description = yaml.safe_load((scenario_root / "description.txt").read_text())
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time", cutoff)
    feature_cutoff = cutoff if feature_cutoff_raw in {None, "?"} else float(feature_cutoff_raw)
    feature_steps = dict(description["feature_steps"])
    steps = sorted(feature_steps)

    runtimes, algorithms, algorithm_audit = load_algorithm_runs(
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
        raise ValueError("feature step mismatch across description/cost/status tables")

    instances = sorted(set(runtimes) & set(feature_values) & set(feature_costs))
    if set(instances) != set(runtimes):
        missing = sorted(set(runtimes) - set(instances))
        raise ValueError(f"missing feature data for {len(missing)} algorithm-run instances")

    oracle = {
        instance: min(runtimes[instance].values())
        for instance in instances
    }
    sbs = min(
        algorithms,
        key=lambda algorithm: (
            statistics.fmean(runtimes[instance][algorithm] for instance in instances),
            algorithm,
        ),
    )
    sbs_mean = statistics.fmean(runtimes[instance][sbs] for instance in instances)
    oracle_mean = statistics.fmean(oracle.values())

    closed_sets = enumerate_dependency_closed_sets(steps, feature_steps)
    evaluations = [
        evaluate_representation(
            selected,
            instances,
            algorithms,
            runtimes,
            oracle,
            feature_steps,
            feature_values,
            feature_costs,
            feature_status,
            feature_cutoff,
        )
        for selected in closed_sets
    ]

    best_total = min(
        evaluations,
        key=lambda row: (
            row["robust_total_excess_cost"],
            row["mean_total_excess_cost"],
            len(row["steps"]),
            row["steps"],
        ),
    )
    coarse = next(row for row in evaluations if row["steps"] == [])
    full_steps = list(dependency_closure(steps, feature_steps))
    full = next(row for row in evaluations if row["steps"] == full_steps)

    return {
        "schema": SCHEMA,
        "authority": {
            "corpus_complete_for_pinned_ASlib_scenario": True,
            "uses_ASlib_recorded_algorithm_and_feature_cost_data": True,
            "external_replay": False,
            "unseen_instance_generalization": False,
            "learned_selector_claim": False,
            "grants_journal_authority": False,
        },
        "upstream": {
            "repository": ASLIB_REPO,
            "commit": ASLIB_COMMIT,
            "scenario": SCENARIO,
            "files": upstream,
        },
        "convention": {
            "algorithm_cutoff_time": cutoff,
            "non_ok_algorithm_penalty": "PAR10",
            "par10_value": 10.0 * cutoff,
            "feature_cutoff_fallback": feature_cutoff,
            "total_excess_baseline": "statewise virtual-best-solver runtime with zero feature acquisition",
        },
        "corpus": {
            "instance_count": len(instances),
            "algorithm_count": len(algorithms),
            "feature_count": len(feature_names),
            "feature_step_count": len(steps),
            "feature_steps": steps,
            "dependency_closed_representation_count": len(closed_sets),
            "algorithm_audit": algorithm_audit,
        },
        "portfolio": {
            "single_best_solver": sbs,
            "single_best_solver_mean_PAR10": sbs_mean,
            "virtual_best_solver_mean_PAR10": oracle_mean,
            "oracle_gap_mean_PAR10": sbs_mean - oracle_mean,
        },
        "registered_baselines": {
            "no_feature_global_selector": coarse,
            "all_feature_steps": full,
        },
        "fiberguard_best_static": best_total,
        "descriptive_pareto_frontier": pareto_frontier(evaluations),
        "all_representations": sorted(
            evaluations,
            key=lambda row: (
                row["robust_total_excess_cost"],
                row["mean_total_excess_cost"],
                len(row["steps"]),
                row["steps"],
            ),
        ),
        "controls": {
            "all_dependency_closed_sets_evaluated": len(evaluations) == len(closed_sets),
            "worst_fibre_witness_bound_holds": all(
                row["worst_fibre_witness"]["witness_size"] <= len(algorithms)
                for row in evaluations
            ),
            "best_static_not_worse_than_every_registered_representation": (
                best_total["robust_total_excess_cost"]
                <= min(row["robust_total_excess_cost"] for row in evaluations) + 1e-12
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.aslib_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canonical_json(result) + "\n", encoding="utf-8")
    print(
        "FIBERGUARD_ASLIB_SAT12_ALL_PASS",
        f"instances={result['corpus']['instance_count']}",
        f"algorithms={result['corpus']['algorithm_count']}",
        f"representations={result['corpus']['dependency_closed_representation_count']}",
        f"best_steps={result['fiberguard_best_static']['steps']}",
        f"best_robust_total_excess={result['fiberguard_best_static']['robust_total_excess_cost']:.6g}",
    )


if __name__ == "__main__":
    main()
