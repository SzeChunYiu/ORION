"""Deterministic descriptive analysis for the frozen P2 offline companion.

The frozen statistical plan makes the authority boundary explicit: the offline
suite has 20 tasks, below ``TIER_D_minimum_inferential`` (97), so this module
never emits a promoted p-value/CI verdict.  It collapses the three predeclared
repeats inside task, reports descriptive paired effects and preserves every
failure/CANNOT_CHECK outcome.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import fmean
from typing import Any, Iterable, Sequence

from .cases import DiscoveryTask
from .corpus import DiscoveryWorld, sha256_digest
from .offline_systems import ALL_SYSTEMS, BASELINES, ORION_FULL, OfflineDiscoverySystem
from .runner import RunOutcome, build_public_index, execute

DEFAULT_SEEDS = (20260816, 20260817, 20260818)
MINIMUM_INFERENTIAL_N = 97

#: The precision tiers `STATISTICAL_PLAN_V1.json` froze, strictest first, mirrored
#: here because a protocol directory is not an importable package. Every entry is a
#: proportion half-width at assumed_p 0.5 and the N it requires. `offline_complete_gold`
#: is committed to TIER_B, and its `n_is_host_owned` flag is why a shortfall is a
#: thing the world can be made to fix rather than a fact to be reported around.
PRECISION_TIERS: tuple[tuple[str, float, int], ...] = (
    ("TIER_A_full", 0.03, 1068),
    ("TIER_B_committed", 0.05, 385),
    ("TIER_C_reduced", 0.075, 171),
    ("TIER_D_minimum_inferential", 0.1, 97),
)

COMMITTED_TIER = "TIER_B_committed"
COMMITTED_REQUIRED_N = 385
COMMITTED_HALF_WIDTH = 0.05

#: Bootstrap settings mirroring `publication_stats.bootstrap_mean_ci` so an interval
#: minted here equals one minted by programme tooling over the same numbers. The
#: seed is fixed because the whole offline archive is hash-stable and an unseeded
#: resampler would be the one thing in it that moves between runs.
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20260816
BOOTSTRAP_CONFIDENCE = 0.95


def achieved_precision_tier(n_tasks: int) -> dict[str, Any]:
    """Classify an achieved N against the frozen tier table.

    The plan's `shortfall_rule` is written in one direction only — what to record
    when the corpus lands *below* 385 — so reaching the committed N is deliberately
    reported as precision and nothing more. Meeting a tier lifts the
    `DESCRIPTIVE_ONLY` label, which is one of six conditions the frozen decision
    rule requires before anything is promoted. It is not the other five, and this
    module does not evaluate them.
    """

    tier = "DESCRIPTIVE_ONLY"
    half_width: float | None = None
    for name, width, required in PRECISION_TIERS:
        if n_tasks >= required:
            tier = name
            half_width = width
            break
    return {
        "n_tasks": n_tasks,
        "achieved_tier": tier,
        "achieved_tier_half_width": half_width,
        "committed_tier": COMMITTED_TIER,
        "committed_required_n": COMMITTED_REQUIRED_N,
        "committed_half_width": COMMITTED_HALF_WIDTH,
        "committed_tier_met": n_tasks >= COMMITTED_REQUIRED_N,
        "minimum_inferential_n": MINIMUM_INFERENTIAL_N,
        "assumed_p": 0.5,
        "primary_promoted": False,
        "promotion_note": (
            "Achieved precision only. A promoted primary additionally requires the "
            "frozen decision rule in STATISTICAL_PLAN_V1.json, which this module does "
            "not evaluate and this run does not exercise."
        ),
    }


def _authority_reason(achieved: dict[str, Any]) -> str:
    n_tasks = achieved["n_tasks"]
    if achieved["achieved_tier"] == "DESCRIPTIVE_ONLY":
        return (
            f"n={n_tasks} is below frozen TIER_D_minimum_inferential "
            f"n={MINIMUM_INFERENTIAL_N}; no offline primary may be promoted"
        )
    required = next(
        required
        for name, _, required in PRECISION_TIERS
        if name == achieved["achieved_tier"]
    )
    return (
        f"n={n_tasks} meets frozen {achieved['achieved_tier']} "
        f"(required_n={required}, "
        f"half_width={achieved['achieved_tier_half_width']}, assumed_p=0.5). "
        "This is an achieved-precision label, not a promotion: the frozen decision "
        "rule is not evaluated here and no primary is promoted by this module."
    )


def _percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile, identical to `publication_stats.percentile`."""

    ordered = sorted(float(item) for item in values)
    if not ordered:
        raise ValueError("values must be non-empty")
    if len(ordered) == 1:
        return ordered[0]
    position = q * (len(ordered) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def bootstrap_mean_interval(values: Sequence[float]) -> dict[str, float]:
    """Seeded percentile bootstrap of a mean, with the achieved half-width.

    The half-width is *observed* rather than read off the tier table. The frozen
    plan is explicit that a paired difference of two [0, 1] variables can carry up
    to four times the variance of a single rate, so the planning table sizes N and
    only the bootstrap may report what precision was actually achieved.
    """

    xs = tuple(float(item) for item in values)
    if not xs:
        raise ValueError("values must be non-empty")
    rng = random.Random(BOOTSTRAP_SEED)
    boot = [fmean(rng.choices(xs, k=len(xs))) for _ in range(BOOTSTRAP_RESAMPLES)]
    alpha = (1.0 - BOOTSTRAP_CONFIDENCE) / 2.0
    low = _percentile(boot, alpha)
    high = _percentile(boot, 1.0 - alpha)
    return {
        "mean": _round(fmean(xs)),
        "ci_low": _round(low),
        "ci_high": _round(high),
        "half_width": _round((high - low) / 2.0),
        "n": len(xs),
    }


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
    achieved = achieved_precision_tier(len(tasks))

    # Hash-stable scientific artifacts: the synthetic world has no provider
    # latency, so wall-clock is defined as zero here rather than leaking runner
    # scheduling noise into content hashes. CI runtime is reported separately.
    clock = lambda: 0.0
    # The public index is a pure function of the world, so it is built once and
    # shared across every run instead of being rebuilt inside each one. At this
    # campaign's size that is the difference between minutes and hours; it cannot
    # change an outcome.
    index = build_public_index(world)
    outcomes = tuple(
        execute(
            system,
            world,
            task,
            seed=seed,
            run_manifest_hash=run_manifest_hash,
            clock=clock,
            index=index,
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

    # Paired over the shared task order, so the difference interval is a paired
    # bootstrap over per-task differences rather than two independent intervals
    # subtracted — which would misstate the precision the plan asks to be reported.
    task_order = sorted(tasks_by_id)
    orion_recall = [
        collapsed_by_system[ORION_FULL.system_id][task_id]["complete_gold_recall"]
        for task_id in task_order
    ]
    comparator_recall = [
        collapsed_by_system[strongest.system_id][task_id]["complete_gold_recall"]
        for task_id in task_order
    ]
    achieved = {
        **achieved,
        "orion_complete_gold_recall": bootstrap_mean_interval(orion_recall),
        "strongest_baseline_complete_gold_recall": bootstrap_mean_interval(
            comparator_recall
        ),
        "paired_orion_minus_strongest_baseline_recall": bootstrap_mean_interval(
            [left - right for left, right in zip(orion_recall, comparator_recall, strict=True)]
        ),
        "bootstrap": {
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
            "confidence": BOOTSTRAP_CONFIDENCE,
            "half_width_source": "observed_percentile_bootstrap",
        },
    }

    summary = {
        "schema_version": "orion.p2.offline-results-summary.v1",
        "analysis_authority": achieved["achieved_tier"],
        "authority_reason": _authority_reason(achieved),
        "achieved_precision": achieved,
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
    "BOOTSTRAP_CONFIDENCE",
    "BOOTSTRAP_RESAMPLES",
    "BOOTSTRAP_SEED",
    "COMMITTED_HALF_WIDTH",
    "COMMITTED_REQUIRED_N",
    "COMMITTED_TIER",
    "DEFAULT_SEEDS",
    "PRECISION_TIERS",
    "achieved_precision_tier",
    "bootstrap_mean_interval",
    "MINIMUM_INFERENTIAL_N",
    "OfflineArchive",
    "run_offline_companion",
]
