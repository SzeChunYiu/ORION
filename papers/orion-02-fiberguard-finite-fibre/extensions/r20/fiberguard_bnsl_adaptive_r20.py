#!/usr/bin/env python3
"""Prospectively frozen FiberGuard R20 BNSL-2016 adaptive discriminator.

Protocol: FIBERGUARD_BNSL_ADAPTIVE_R20_PROTOCOL.md
Scientific scope: exact corpus-complete closed-world decision value only.
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

SCHEMA = "ORION.FiberGuard.BNSLAdaptive.R20.v1"
ASLIB_REPO = "https://github.com/coseal/aslib_data.git"
ASLIB_COMMIT = "551b22beef8df17de59286b4822ef720e0aa4d6f"
SCENARIO = "BNSL-2016"
EXPECTED_BLOBS = {
    "description.txt": "e193c8a46d2b3b9fadfe1cb27bef16db8540bc29",
    "algorithm_runs.arff": "33adc274ba3bd7d62875a5ee017d9b4b147e6ee8",
    "feature_values.arff": "5d981d99a76395ad9828d0ff51f60ecb5fb7965f",
    "feature_costs.arff": "09afa0572cc46269bfe03cfc2f008d5b95d2bf40",
    "feature_runstatus.arff": "90e494a307c44f3978ca33c5a02e66d2fe4726f3",
}
TOL = 1e-9


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


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
                    f"row width {len(row)} != {len(attrs)} in {path.name}: {raw[:120]!r}"
                )
            rows.append([value.strip() for value in row])
    if not attrs or not in_data:
        raise ValueError(f"invalid ARFF file: {path}")
    return attrs, rows


def most_common_status(values: Iterable[str]) -> str:
    counter = collections.Counter(values)
    if not counter:
        raise ValueError("empty status list")
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
        by_instance[instance][algorithm] = runtime if status == "ok" else 10.0 * cutoff

    incomplete = [
        instance for instance, mapping in by_instance.items() if set(mapping) != set(algos)
    ]
    if incomplete:
        raise ValueError(f"incomplete algorithm matrix for {len(incomplete)} instances")

    audit = {
        "algorithm_count": len(algos),
        "measurement_status_counts": dict(sorted(status_counts.items())),
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
            by_instance[instance][name] = "?"
        else:
            by_instance[instance][name] = format(math.fsum(numeric) / len(numeric), ".17g")
    return dict(by_instance), feature_names


def load_step_table(
    path: Path, *, numeric: bool
) -> tuple[dict[str, dict[str, float | str]], list[str]]:
    attrs, rows = read_arff(path)
    if attrs[:2] != ["instance_id", "repetition"]:
        raise ValueError(f"unexpected step-table prefix in {path.name}")
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
            raise ValueError(
                f"missing finite cost for successful step {step!r} on {instance!r}"
            )
    return total


def acquisition_map(
    instances: list[str],
    selected: tuple[str, ...],
    feature_costs: dict[str, dict[str, float | str]],
    feature_status: dict[str, dict[str, float | str]],
    feature_cutoff: float,
) -> dict[str, float]:
    return {
        instance: feature_cost(
            instance, selected, feature_costs, feature_status, feature_cutoff
        )
        for instance in instances
    }


def robust_choice(
    members: list[str],
    algorithms: list[str],
    runtimes: dict[str, dict[str, float]],
    oracle: dict[str, float],
    acquisition: dict[str, float],
) -> tuple[float, str]:
    losses = {
        algorithm: max(
            acquisition[x] + runtimes[x][algorithm] - oracle[x] for x in members
        )
        for algorithm in algorithms
    }
    best = min(algorithms, key=lambda a: (losses[a], a))
    return losses[best], best


def fibres_for(
    instances: list[str],
    selected: tuple[str, ...],
    feature_steps: dict[str, dict[str, Any]],
    feature_values: dict[str, dict[str, str]],
    feature_status: dict[str, dict[str, float | str]],
) -> dict[tuple[Any, ...], list[str]]:
    fibres: dict[tuple[Any, ...], list[str]] = collections.defaultdict(list)
    for instance in instances:
        key = step_signature(
            instance, selected, feature_steps, feature_values, feature_status
        )
        fibres[key].append(instance)
    return dict(fibres)


def realized_summary(values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(values.values())
    p95_index = min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "mean_total_excess_cost": statistics.fmean(ordered),
        "median_total_excess_cost": statistics.median(ordered),
        "p95_total_excess_cost": ordered[p95_index],
        "maximum_total_excess_cost": max(ordered),
    }


def evaluate_static(
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
    acquisition = acquisition_map(
        instances, selected, feature_costs, feature_status, feature_cutoff
    )
    fibres = fibres_for(
        instances, selected, feature_steps, feature_values, feature_status
    )
    realized: dict[str, float] = {}
    worst = -1.0
    for key in sorted(fibres, key=repr):
        members = fibres[key]
        value, action = robust_choice(members, algorithms, runtimes, oracle, acquisition)
        worst = max(worst, value)
        for x in members:
            realized[x] = acquisition[x] + runtimes[x][action] - oracle[x]
    zero_acq = {x: 0.0 for x in instances}
    action_only = -1.0
    for members in fibres.values():
        value, _ = robust_choice(members, algorithms, runtimes, oracle, zero_acq)
        action_only = max(action_only, value)
    return {
        "steps": list(selected),
        "fibre_count": len(fibres),
        "maximum_fibre_size": max(map(len, fibres.values())),
        "robust_action_only_regret": action_only,
        "robust_total_excess_cost": worst,
        "mean_feature_cost": statistics.fmean(acquisition.values()),
        "maximum_feature_cost": max(acquisition.values()),
        **realized_summary(realized),
    }


def choose_j0(
    closed_sets: list[tuple[str, ...]],
    instances: list[str],
    feature_costs: dict[str, dict[str, float | str]],
    feature_status: dict[str, dict[str, float | str]],
    feature_cutoff: float,
) -> tuple[str, ...]:
    free: list[tuple[str, ...]] = []
    for selected in closed_sets:
        costs = acquisition_map(
            instances, selected, feature_costs, feature_status, feature_cutoff
        )
        if all(abs(value) <= TOL for value in costs.values()):
            free.append(selected)
    if not free:
        return ()
    return min(free, key=lambda row: (-len(row), row))


def evaluate_one_step_adaptive(
    j0: tuple[str, ...],
    steps: list[str],
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
    initial = fibres_for(instances, j0, feature_steps, feature_values, feature_status)
    acq_cache: dict[tuple[str, ...], dict[str, float]] = {}

    def acq(selected: tuple[str, ...]) -> dict[str, float]:
        if selected not in acq_cache:
            acq_cache[selected] = acquisition_map(
                instances, selected, feature_costs, feature_status, feature_cutoff
            )
        return acq_cache[selected]

    j0_acq = acq(j0)
    refine_sets = {
        q: dependency_closure(tuple(j0) + (q,), feature_steps)
        for q in steps
        if q not in j0
    }

    root_records = []
    realized: dict[str, float] = {}
    chosen_counts: collections.Counter[str] = collections.Counter()
    act_only_worst = -1.0

    for parent_key in sorted(initial, key=repr):
        members = initial[parent_key]
        act_value, act_solver = robust_choice(
            members, algorithms, runtimes, oracle, j0_acq
        )
        act_only_worst = max(act_only_worst, act_value)
        candidates: list[tuple[float, int, str, Any]] = [
            (act_value, 0, "ACT", {"solver": act_solver})
        ]

        for q in sorted(refine_sets):
            selected = refine_sets[q]
            selected_acq = acq(selected)
            children: dict[tuple[Any, ...], list[str]] = collections.defaultdict(list)
            for x in members:
                child_key = step_signature(
                    x, selected, feature_steps, feature_values, feature_status
                )
                children[child_key].append(x)
            child_actions: dict[tuple[Any, ...], str] = {}
            child_values: dict[tuple[Any, ...], float] = {}
            refine_value = -1.0
            for child_key in sorted(children, key=repr):
                value, solver = robust_choice(
                    children[child_key], algorithms, runtimes, oracle, selected_acq
                )
                child_actions[child_key] = solver
                child_values[child_key] = value
                refine_value = max(refine_value, value)
            candidates.append(
                (
                    refine_value,
                    1,
                    q,
                    {
                        "selected": selected,
                        "children": children,
                        "child_actions": child_actions,
                        "child_values": child_values,
                    },
                )
            )

        value, kind_rank, choice, payload = min(
            candidates, key=lambda row: (row[0], row[1], row[2])
        )
        chosen_counts[choice] += 1
        if choice == "ACT":
            solver = payload["solver"]
            for x in members:
                realized[x] = j0_acq[x] + runtimes[x][solver] - oracle[x]
        else:
            selected = payload["selected"]
            selected_acq = acq(selected)
            children = payload["children"]
            child_actions = payload["child_actions"]
            for child_key, child_members in children.items():
                solver = child_actions[child_key]
                for x in child_members:
                    realized[x] = (
                        selected_acq[x] + runtimes[x][solver] - oracle[x]
                    )
        root_records.append(
            {
                "parent_fibre_size": len(members),
                "choice": choice,
                "value": value,
            }
        )

    robust = max(realized.values())
    controls = {
        "act_only_worst_matches_J0_static_value": act_only_worst,
        "all_instances_receive_exactly_one_realized_loss": len(realized) == len(instances),
        "refinement_children_subset_parent_by_construction": True,
    }
    return {
        "J0": list(j0),
        "initial_fibre_count": len(initial),
        "maximum_initial_fibre_size": max(map(len, initial.values())),
        "available_refinements": {q: list(s) for q, s in sorted(refine_sets.items())},
        "choice_counts": dict(sorted(chosen_counts.items())),
        "robust_total_excess_cost": robust,
        **realized_summary(realized),
        "root_records": root_records,
        "controls": controls,
    }


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


def terminal_for(adaptive: dict[str, Any], best_static: dict[str, Any]) -> str:
    va = float(adaptive["robust_total_excess_cost"])
    vs = float(best_static["robust_total_excess_cost"])
    ma = float(adaptive["mean_total_excess_cost"])
    ms = float(best_static["mean_total_excess_cost"])
    if va <= 0.90 * vs + TOL and ma <= ms + TOL:
        return "C_R20_BNSL_ADAPTIVE_MATERIAL_VALUE"
    if va < vs - TOL:
        return "C_R20_BNSL_ADAPTIVE_STRICT_VALUE"
    if abs(va - vs) <= TOL:
        return "C_R20_BNSL_ADAPTIVE_NULL"
    return "C_R20_BNSL_ADAPTIVE_ADVERSE"


def run(root: Path) -> dict[str, Any]:
    # This is intentionally the first operation: content identity is checked
    # before any scientific outcome file is parsed.
    upstream = validate_upstream(root)
    scenario_root = root / SCENARIO
    description = yaml.safe_load((scenario_root / "description.txt").read_text())
    cutoff = float(description["algorithm_cutoff_time"])
    feature_cutoff_raw = description.get("features_cutoff_time", cutoff)
    feature_cutoff = cutoff if feature_cutoff_raw in {None, "?"} else float(feature_cutoff_raw)
    feature_steps = dict(description["feature_steps"])
    steps = sorted(feature_steps)
    if len(steps) != 7:
        raise ValueError(f"frozen protocol expected 7 feature steps, got {len(steps)}")

    # Acquisition tables are loaded before target outcomes to preserve the
    # registered J0 construction dependency.
    feature_costs, cost_steps = load_step_table(
        scenario_root / "feature_costs.arff", numeric=True
    )
    feature_status, status_steps = load_step_table(
        scenario_root / "feature_runstatus.arff", numeric=False
    )

    # Scientific outcomes begin here, after all source and acquisition gates.
    runtimes, algorithms, algorithm_audit = load_algorithm_runs(
        scenario_root / "algorithm_runs.arff", cutoff
    )
    feature_values, feature_names = load_feature_values(
        scenario_root / "feature_values.arff"
    )

    if set(cost_steps) != set(steps) or set(status_steps) != set(steps):
        raise ValueError("feature-step mismatch across frozen tables")
    if len(algorithms) != 8:
        raise ValueError(f"frozen protocol expected 8 algorithms, got {len(algorithms)}")

    sets = [set(runtimes), set(feature_values), set(feature_costs), set(feature_status)]
    if any(s != sets[0] for s in sets[1:]):
        sizes = [len(s) for s in sets]
        raise ValueError(f"instance denominators disagree across tables: {sizes}")
    instances = sorted(sets[0])
    if not instances:
        raise ValueError("empty BNSL denominator")

    oracle = {x: min(runtimes[x].values()) for x in instances}
    sbs = min(
        algorithms,
        key=lambda a: (
            statistics.fmean(runtimes[x][a] for x in instances),
            a,
        ),
    )
    sbs_mean = statistics.fmean(runtimes[x][sbs] for x in instances)
    vbs_mean = statistics.fmean(oracle.values())

    closed_sets = enumerate_dependency_closed_sets(steps, feature_steps)
    j0 = choose_j0(
        closed_sets, instances, feature_costs, feature_status, feature_cutoff
    )

    static_rows = [
        evaluate_static(
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
    best_static = min(
        static_rows,
        key=lambda row: (
            row["robust_total_excess_cost"],
            row["mean_total_excess_cost"],
            len(row["steps"]),
            row["steps"],
        ),
    )
    no_feature = next(row for row in static_rows if row["steps"] == [])
    full_steps = list(dependency_closure(steps, feature_steps))
    all_feature = next(row for row in static_rows if row["steps"] == full_steps)
    j0_row = next(row for row in static_rows if row["steps"] == list(j0))

    restricted_sets = {
        j0,
        *(
            dependency_closure(tuple(j0) + (q,), feature_steps)
            for q in steps
            if q not in j0
        ),
    }
    restricted_rows = [row for row in static_rows if tuple(row["steps"]) in restricted_sets]
    best_restricted = min(
        restricted_rows,
        key=lambda row: (
            row["robust_total_excess_cost"],
            row["mean_total_excess_cost"],
            len(row["steps"]),
            row["steps"],
        ),
    )

    adaptive = evaluate_one_step_adaptive(
        j0,
        steps,
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

    if abs(
        float(adaptive["controls"]["act_only_worst_matches_J0_static_value"])
        - float(j0_row["robust_total_excess_cost"])
    ) > TOL:
        raise AssertionError("ACT-only adaptive control disagrees with J0 static value")
    if float(adaptive["robust_total_excess_cost"]) > float(
        best_restricted["robust_total_excess_cost"]
    ) + TOL:
        raise AssertionError(
            "adaptive policy failed to contain the best registered J0+one-probe static policy"
        )

    terminal = terminal_for(adaptive, best_static)

    result = {
        "schema": SCHEMA,
        "terminal": terminal,
        "authority": {
            "corpus_complete_for_pinned_BNSL_scenario": True,
            "uses_ASlib_recorded_algorithm_and_feature_cost_data": True,
            "prospectively_frozen_before_solver_outcome_access": True,
            "external_independent_replay": False,
            "unseen_instance_generalization": False,
            "learned_selector_claim": False,
            "production_value": False,
            "novelty_authority": False,
            "grants_journal_authority": False,
        },
        "upstream": {
            "repository": ASLIB_REPO,
            "commit": ASLIB_COMMIT,
            "scenario": SCENARIO,
            "files": upstream,
        },
        "convention": {
            "algorithm_cutoff": cutoff,
            "PAR10": 10.0 * cutoff,
            "feature_cutoff_fallback": feature_cutoff,
            "oracle_baseline": "statewise VBS with zero feature acquisition",
            "adaptive_depth": "J0 then at most one additional registered step closure",
        },
        "corpus": {
            "instance_count": len(instances),
            "algorithm_count": len(algorithms),
            "feature_count": len(feature_names),
            "feature_step_count": len(steps),
            "feature_steps": steps,
            "dependency_closed_static_count": len(closed_sets),
            "algorithm_audit": algorithm_audit,
        },
        "portfolio": {
            "SBS": sbs,
            "SBS_mean_PAR10": sbs_mean,
            "VBS_mean_PAR10": vbs_mean,
            "mean_oracle_gap_PAR10": sbs_mean - vbs_mean,
        },
        "registered_baselines": {
            "no_features": no_feature,
            "all_features": all_feature,
            "J0_act_only": j0_row,
            "best_J0_plus_one_static_probe": best_restricted,
        },
        "best_static": best_static,
        "adaptive_one_step": adaptive,
        "adaptive_minus_static": {
            "robust_difference": float(adaptive["robust_total_excess_cost"])
            - float(best_static["robust_total_excess_cost"]),
            "robust_ratio": (
                float(adaptive["robust_total_excess_cost"])
                / float(best_static["robust_total_excess_cost"])
                if float(best_static["robust_total_excess_cost"]) != 0.0
                else None
            ),
            "mean_difference": float(adaptive["mean_total_excess_cost"])
            - float(best_static["mean_total_excess_cost"]),
        },
        "controls": {
            "source_blobs_checked_before_outcome_parse": True,
            "J0_constructed_from_acquisition_tables_only": True,
            "ACT_control_matches_J0_static": True,
            "adaptive_weakly_dominates_registered_J0_plus_one_static_family": True,
            "all_static_dependency_closed_sets_evaluated": len(static_rows)
            == len(closed_sets),
            "no_hidden_instance_identity_observation": True,
            "state_dependent_costs_added_before_max": True,
        },
        "all_static_representations": sorted(
            static_rows,
            key=lambda row: (
                row["robust_total_excess_cost"],
                row["mean_total_excess_cost"],
                len(row["steps"]),
                row["steps"],
            ),
        ),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aslib-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = run(args.aslib_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(canonical_json(result) + "\n")
    print(
        result["terminal"],
        f"instances={result['corpus']['instance_count']}",
        f"static={result['best_static']['robust_total_excess_cost']:.12g}",
        f"adaptive={result['adaptive_one_step']['robust_total_excess_cost']:.12g}",
        f"ratio={result['adaptive_minus_static']['robust_ratio']}",
        f"J0={result['adaptive_one_step']['J0']}",
    )


if __name__ == "__main__":
    main()
