"""Deterministic descriptive analysis for the frozen P2 offline companion.

The frozen statistical plan makes the authority boundary explicit: the offline
suite has 20 tasks, below ``TIER_D_minimum_inferential`` (97), so this module
never emits a promoted p-value/CI verdict.  It collapses the three predeclared
repeats inside task, reports descriptive paired effects and preserves every
failure/CANNOT_CHECK outcome.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import fmean
from typing import Any, Iterable

from .cases import DiscoveryTask
from .corpus import DiscoveryWorld, sha256_digest
from .offline_systems import ALL_SYSTEMS, BASELINES, ORION_FULL, OfflineDiscoverySystem
from .runner import RunOutcome, execute

DEFAULT_SEEDS = (20260816, 20260817, 20260818)
MINIMUM_INFERENTIAL_N = 97


@dataclass(frozen=True)
class OfflineArchive:
    outcomes: tuple[RunOutcome, ...]
    summary: dict[str, Any]


def _mean(values: Iterable[float]) -> float:
    items = tuple(values)
    return fmean(items) if items else 0.0


def _round(value: float) -> float:
    return round(float(value), 6)


def _collapse_system(
    outcomes: tuple[RunOutcome, ...],
    tasks_by_id: dict[str, DiscoveryTask],
) -> tuple[dict[str, Any], dict[str, dict[str, float]]]:
    by_task: dict[str, list[RunOutcome]] = defaultdict(list)
    for outcome in outcomes:
        by_task[outcome.record["task_id"]].append(outcome)

    collapsed: dict[str, dict[str, float]] = {}
    status_by_task: dict[str, str] = {}
    failure_by_task: dict[str, str] = {}
    case_by_task: dict[str, str] = {}
    for task_id, repeats in sorted(by_task.items()):
        metrics = repeats[0].record["metrics"]
        collapsed[task_id] = {
            name: _mean(float(item.record["metrics"][name]) for item in repeats)
            for name in metrics
        }
        statuses = {item.record["status"] for item in repeats}
        failures = {item.record.get("failure_class") or "NONE" for item in repeats}
        if len(statuses) != 1 or len(failures) != 1:
            raise ValueError(f"non-deterministic repeat verdict for {task_id}: {statuses} / {failures}")
        status_by_task[task_id] = next(iter(statuses))
        failure_by_task[task_id] = next(iter(failures))
        case_by_task[task_id] = tasks_by_id[task_id].case_family.value

    n = len(collapsed)
    status_counts = Counter(status_by_task.values())
    failure_counts = Counter(failure_by_task.values())
    aggregate = {
        "n_tasks": n,
        "mean_complete_gold_recall": _round(
            _mean(item["complete_gold_recall"] for item in collapsed.values())
        ),
        "mean_precision": _round(_mean(item["precision"] for item in collapsed.values())),
        "premature_task_closure_rate": _round(
            _mean(item["premature_task_closure"] for item in collapsed.values())
        ),
        "mean_duplicate_processing_rate": _round(
            _mean(item["duplicate_processing_rate"] for item in collapsed.values())
        ),
        "mean_legitimate_reread_count": _round(
            _mean(item["legitimate_reread_count"] for item in collapsed.values())
        ),
        "mean_routes_used": _round(_mean(item["routes_used"] for item in collapsed.values())),
        "mean_route_pair_overlap": _round(
            _mean(item["mean_route_pair_overlap"] for item in collapsed.values())
        ),
        "mean_marginal_relevant_gain_after_first_route": _round(
            _mean(item["marginal_relevant_gain_after_first_route"] for item in collapsed.values())
        ),
        "pass_rate": _round(status_counts.get("PASS", 0) / n),
        "fail_rate": _round(status_counts.get("FAIL", 0) / n),
        "cannot_check_rate": _round(status_counts.get("CANNOT_CHECK", 0) / n),
        "invalid_rate": _round(status_counts.get("INVALID", 0) / n),
        "status_counts": dict(sorted(status_counts.items())),
        "failure_counts": dict(sorted(failure_counts.items())),
    }

    by_case: dict[str, dict[str, Any]] = {}
    for case in sorted(set(case_by_task.values())):
        ids = [task_id for task_id, value in case_by_task.items() if value == case]
        by_case[case] = {
            "n_tasks": len(ids),
            "mean_complete_gold_recall": _round(
                _mean(collapsed[task_id]["complete_gold_recall"] for task_id in ids)
            ),
            "premature_task_closure_rate": _round(
                _mean(collapsed[task_id]["premature_task_closure"] for task_id in ids)
            ),
            "mean_duplicate_processing_rate": _round(
                _mean(collapsed[task_id]["duplicate_processing_rate"] for task_id in ids)
            ),
            "mean_legitimate_reread_count": _round(
                _mean(collapsed[task_id]["legitimate_reread_count"] for task_id in ids)
            ),
        }
    aggregate["by_case_family"] = by_case
    return aggregate, collapsed


def run_offline_companion(
    world: DiscoveryWorld,
    tasks: tuple[DiscoveryTask, ...],
    *,
    run_manifest_hash: str,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    systems: tuple[OfflineDiscoverySystem, ...] = ALL_SYSTEMS,
) -> OfflineArchive:
    if len(tasks) >= MINIMUM_INFERENTIAL_N:
        raise ValueError("offline analysis authority must be revisited before inferential use")

    # Hash-stable scientific artifacts: the synthetic world has no provider
    # latency, so wall-clock is defined as zero here rather than leaking runner
    # scheduling noise into content hashes. CI runtime is reported separately.
    clock = lambda: 0.0
    outcomes = tuple(
        execute(
            system,
            world,
            task,
            seed=seed,
            run_manifest_hash=run_manifest_hash,
            clock=clock,
        )
        for system in systems
        for task in sorted(tasks, key=lambda item: item.task_id)
        for seed in seeds
    )
    tasks_by_id = {task.task_id: task for task in tasks}

    aggregates: dict[str, Any] = {}
    collapsed_by_system: dict[str, dict[str, dict[str, float]]] = {}
    for system in systems:
        subset = tuple(item for item in outcomes if item.record["system_id"] == system.system_id)
        aggregate, collapsed = _collapse_system(subset, tasks_by_id)
        aggregates[system.system_id] = aggregate
        collapsed_by_system[system.system_id] = collapsed

    strongest = max(
        BASELINES,
        key=lambda system: (
            aggregates[system.system_id]["mean_complete_gold_recall"],
            -aggregates[system.system_id]["premature_task_closure_rate"],
            system.system_id,
        ),
    )
    comparator = aggregates[strongest.system_id]
    orion = aggregates[ORION_FULL.system_id]

    all_records = [item.record for item in outcomes]
    record_digest = sha256_digest(all_records)
    raw_artifact_digest = sha256_digest(
        [item.record["raw_artifact_hash"] for item in outcomes]
    )

    summary = {
        "schema_version": "orion.p2.offline-results-summary.v1",
        "analysis_authority": "DESCRIPTIVE_ONLY",
        "authority_reason": (
            f"n={len(tasks)} is below frozen TIER_D_minimum_inferential "
            f"n={MINIMUM_INFERENTIAL_N}; no offline primary may be promoted"
        ),
        "n_tasks": len(tasks),
        "n_repeats": len(seeds),
        "seeds": list(seeds),
        "n_systems": len(systems),
        "n_result_records": len(outcomes),
        "record_digest_sha256": record_digest,
        "raw_artifact_hash_list_digest_sha256": raw_artifact_digest,
        "strongest_confirmatory_baseline": strongest.system_id,
        "orion_minus_strongest_baseline_recall": _round(
            orion["mean_complete_gold_recall"]
            - comparator["mean_complete_gold_recall"]
        ),
        "orion_minus_strongest_baseline_premature_closure": _round(
            orion["premature_task_closure_rate"]
            - comparator["premature_task_closure_rate"]
        ),
        "systems": aggregates,
        "confirmatory_baseline_ids": [item.system_id for item in BASELINES],
        "exploratory_system_ids": [
            item.system_id
            for item in systems
            if item.system_id not in {ORION_FULL.system_id, *(x.system_id for x in BASELINES)}
            and not item.system_id.startswith("no_")
            and item.system_id not in {
                "route_stop_can_close_task",
                "coverage_diagnostic_controls_stopping",
            }
        ],
    }
    return OfflineArchive(outcomes=outcomes, summary=summary)


__all__ = [
    "DEFAULT_SEEDS",
    "MINIMUM_INFERENTIAL_N",
    "OfflineArchive",
    "run_offline_companion",
]
