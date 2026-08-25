"""Evaluator-side mechanism projections for the frozen P2 offline companion.

The publication summary intentionally keeps only aggregate metrics. Figures P2-3,
P2-4 and P2-5 require richer structure: query-order discovery trajectories,
per-route first relevant contributions and pairwise content overlap. This module
reconstructs those quantities from host-owned traces and protected gold after a
run has finished. Candidate systems never import this module and never receive
``ProtectedGold``.

The three frozen repeats are deterministic stability repeats, not independent
statistical units. Every projection therefore collapses repeats within task after
asserting that route traces are identical across seeds.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from statistics import fmean
from typing import Any

from orion.core.search import SearchRouteKind
from orion.knowledge.routes import RouteCapture, assess_pair

from .cases import DiscoveryTask
from .corpus import DiscoveryRoute, ROUTE_SPEC_BY_ROUTE, sha256_digest
from .offline_analysis import achieved_precision_tier
from .offline_systems import ORION_FULL
from .runner import RunOutcome

STRONGEST_CONFIRMATORY_BASELINE_ID = "protocol_driven_systematic_review"


def _round(value: float) -> float:
    return round(float(value), 6)


def _pair_key(left: DiscoveryRoute, right: DiscoveryRoute) -> tuple[str, str]:
    """Canonical unordered route-pair key used for both write and read paths."""

    return tuple(sorted((left.value, right.value)))


def _route_signature(outcome: RunOutcome) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            event.index,
            event.route_id,
            event.probe,
            event.backend_identity,
            event.query_derivation_identity,
            event.transport_status,
            event.retrieved_doc_ids,
            event.retrieved_merged_source_ids,
            event.novel_merged_source_ids,
            event.note,
        )
        for event in outcome.trace.route_trials
    )


def _representatives(
    outcomes: tuple[RunOutcome, ...], system_id: str
) -> dict[str, RunOutcome]:
    by_task: dict[str, list[RunOutcome]] = defaultdict(list)
    for outcome in outcomes:
        if outcome.record["system_id"] == system_id:
            by_task[outcome.record["task_id"]].append(outcome)

    representatives: dict[str, RunOutcome] = {}
    for task_id, repeats in sorted(by_task.items()):
        if not repeats:
            continue
        signatures = {_route_signature(item) for item in repeats}
        if len(signatures) != 1:
            raise ValueError(
                f"{system_id}/{task_id}: route trace changed across deterministic repeats"
            )
        metrics = {
            tuple(sorted((name, float(value)) for name, value in item.record["metrics"].items()))
            for item in repeats
        }
        if len(metrics) != 1:
            raise ValueError(
                f"{system_id}/{task_id}: metrics changed across deterministic repeats"
            )
        representatives[task_id] = min(repeats, key=lambda item: item.record["seed"])
    return representatives


def _capture_for_route(outcome: RunOutcome, route: DiscoveryRoute) -> RouteCapture:
    spec = ROUTE_SPEC_BY_ROUTE[route]
    captured: set[str] = set()
    for event in outcome.trace.route_trials:
        if event.route_id == route.value:
            captured.update(event.retrieved_merged_source_ids)
    return RouteCapture(
        route_kind=SearchRouteKind(spec.orion_route_kind),
        backend=spec.backend_identity,
        query_derivation=spec.query_derivation_identity,
        captured=frozenset(captured),
    )


def _trajectory(
    outcome: RunOutcome, task: DiscoveryTask, max_queries: int
) -> tuple[int, ...]:
    gold = set(task.protected_gold.gold_content_identities)
    seen: set[str] = set()
    counts = [0]
    for event in outcome.trace.route_trials:
        seen.update(set(event.retrieved_merged_source_ids) & gold)
        counts.append(len(seen))
    while len(counts) <= max_queries:
        counts.append(counts[-1])
    return tuple(counts[: max_queries + 1])


def _mean_trajectory(
    representatives: dict[str, RunOutcome],
    tasks_by_id: dict[str, DiscoveryTask],
    max_queries: int,
) -> list[dict[str, float]]:
    trajectories = {
        task_id: _trajectory(outcome, tasks_by_id[task_id], max_queries)
        for task_id, outcome in representatives.items()
    }
    points: list[dict[str, float]] = []
    for query_count in range(max_queries + 1):
        counts = [values[query_count] for values in trajectories.values()]
        recalls = [
            values[query_count]
            / max(1, len(tasks_by_id[task_id].protected_gold.gold_content_identities))
            for task_id, values in trajectories.items()
        ]
        points.append(
            {
                "queries": query_count,
                "mean_unique_relevant": _round(fmean(counts)),
                "mean_complete_gold_recall": _round(fmean(recalls)),
            }
        )
    return points


def _route_contributions(
    representatives: dict[str, RunOutcome], tasks_by_id: dict[str, DiscoveryTask]
) -> dict[str, dict[str, Any]]:
    per_route: dict[str, list[int]] = {route.value: [] for route in DiscoveryRoute}
    for task_id, outcome in representatives.items():
        gold = set(tasks_by_id[task_id].protected_gold.gold_content_identities)
        seen: set[str] = set()
        contribution = {route.value: 0 for route in DiscoveryRoute}
        for event in outcome.trace.route_trials:
            relevant = set(event.retrieved_merged_source_ids) & gold
            novel = relevant - seen
            contribution[event.route_id] += len(novel)
            seen.update(relevant)
        for route in DiscoveryRoute:
            per_route[route.value].append(contribution[route.value])

    lexical = DiscoveryRoute.LEXICAL
    lexical_capture = _capture_template(lexical)
    result: dict[str, dict[str, Any]] = {}
    for route in DiscoveryRoute:
        if route is lexical:
            verdict = "REFERENCE"
        else:
            verdict = assess_pair(lexical_capture, _capture_template(route)).verdict.value
        result[route.value] = {
            "mean_first_relevant_contribution": _round(fmean(per_route[route.value])),
            "independence_vs_lexical": verdict,
        }
    return result


def _capture_template(route: DiscoveryRoute) -> RouteCapture:
    spec = ROUTE_SPEC_BY_ROUTE[route]
    return RouteCapture(
        route_kind=SearchRouteKind(spec.orion_route_kind),
        backend=spec.backend_identity,
        query_derivation=spec.query_derivation_identity,
        captured=frozenset(),
    )


def _overlap_projection(
    representatives: dict[str, RunOutcome]
) -> dict[str, dict[str, dict[str, Any]]]:
    routes = tuple(DiscoveryRoute)
    values: dict[tuple[str, str], list[float]] = defaultdict(list)
    for outcome in representatives.values():
        captures = {route: _capture_for_route(outcome, route) for route in routes}
        for left, right in combinations(routes, 2):
            a = captures[left].captured
            b = captures[right].captured
            union = a | b
            jaccard = (len(a & b) / len(union)) if union else 0.0
            values[_pair_key(left, right)].append(jaccard)

    matrix: dict[str, dict[str, dict[str, Any]]] = {}
    for left in routes:
        row: dict[str, dict[str, Any]] = {}
        for right in routes:
            if left is right:
                row[right.value] = {
                    "mean_content_jaccard": 1.0,
                    "independence_verdict": "SAME_ROUTE",
                }
                continue
            pair_values = values[_pair_key(left, right)]
            if not pair_values:
                raise ValueError(f"missing overlap observations for {left.value}/{right.value}")
            verdict = assess_pair(_capture_template(left), _capture_template(right)).verdict.value
            row[right.value] = {
                "mean_content_jaccard": _round(fmean(pair_values)),
                "independence_verdict": verdict,
            }
        matrix[left.value] = row
    return matrix


def build_offline_mechanism_projection(
    tasks: tuple[DiscoveryTask, ...], outcomes: tuple[RunOutcome, ...]
) -> dict[str, Any]:
    """Build the immutable publication projection behind P2-3/P2-4/P2-5."""

    tasks_by_id = {task.task_id: task for task in tasks}
    orion = _representatives(outcomes, ORION_FULL.system_id)
    baseline = _representatives(outcomes, STRONGEST_CONFIRMATORY_BASELINE_ID)
    if set(orion) != set(tasks_by_id) or set(baseline) != set(tasks_by_id):
        raise ValueError("mechanism projection requires every frozen task for both systems")

    max_queries = max(
        max(len(item.trace.route_trials) for item in orion.values()),
        max(len(item.trace.route_trials) for item in baseline.values()),
    )
    return {
        "schema_version": "orion.p2.offline-mechanisms.v1",
        # Same derivation as the archive summary: the label tracks the achieved
        # precision tier of the frozen N (20-task DESCRIPTIVE_ONLY era ->
        # 390-task TIER_B_committed) instead of pinning a superseded campaign.
        "analysis_authority": achieved_precision_tier(len(tasks_by_id))["achieved_tier"],
        "n_tasks": len(tasks_by_id),
        "repeat_handling": "collapsed_within_task_after_deterministic_trace_check",
        "source_record_digest_sha256": sha256_digest([item.record for item in outcomes]),
        "source_raw_artifact_hash_list_digest_sha256": sha256_digest(
            [item.record["raw_artifact_hash"] for item in outcomes]
        ),
        "trajectory_systems": {
            ORION_FULL.system_id: _mean_trajectory(orion, tasks_by_id, max_queries),
            STRONGEST_CONFIRMATORY_BASELINE_ID: _mean_trajectory(
                baseline, tasks_by_id, max_queries
            ),
        },
        "orion_route_first_relevant_contribution": _route_contributions(
            orion, tasks_by_id
        ),
        "orion_content_overlap_matrix": _overlap_projection(orion),
        "notes": {
            "p2_3": "x-axis is frozen search-query count; synthetic wall-clock is intentionally zero and is not plotted",
            "p2_4": "marginal contribution means first relevant content identities discovered on each route in campaign order; independence annotation is pairwise versus LEXICAL reference",
            "p2_5": "overlap is mean task-level Jaccard over content identities; verdicts are structural earned-independence checks on backend/query-derivation identity",
        },
    }


__all__ = [
    "STRONGEST_CONFIRMATORY_BASELINE_ID",
    "build_offline_mechanism_projection",
]
