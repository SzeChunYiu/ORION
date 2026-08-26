"""Complete-gold route-stop FP/FN oracle replay for the frozen P2 companion.

Implements O1 from ``protocol/MEASUREMENT_PLAN_V1.md`` evaluator-side.  Candidate
systems never receive protected gold or route reachability.  Deterministic
repeats are checked for identical route/stop traces and collapsed within task.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .cases import DiscoveryTask
from .corpus import DiscoveryRoute, sha256_digest
from .offline_analysis import achieved_precision_tier
from .runner import RunOutcome
from .systems import StopScope


def _trace_signature(outcome: RunOutcome) -> tuple[Any, ...]:
    return (
        tuple(
            (event.index, event.route_id, event.transport_status, event.retrieved_merged_source_ids)
            for event in outcome.trace.route_trials
        ),
        tuple(
            (item.index, item.scope, item.route_id, item.reason, item.declared)
            for item in outcome.trace.stop_decisions
        ),
    )


def _representatives(
    outcomes: tuple[RunOutcome, ...], system_id: str
) -> dict[str, RunOutcome]:
    grouped: dict[str, list[RunOutcome]] = defaultdict(list)
    for outcome in outcomes:
        if outcome.record["system_id"] == system_id:
            grouped[outcome.record["task_id"]].append(outcome)
    representatives: dict[str, RunOutcome] = {}
    for task_id, repeats in sorted(grouped.items()):
        if len({_trace_signature(item) for item in repeats}) != 1:
            raise ValueError(
                f"{system_id}/{task_id}: route/stop trace changed across deterministic repeats"
            )
        representatives[task_id] = min(repeats, key=lambda item: item.record["seed"])
    return representatives


@dataclass(frozen=True)
class RouteOracleReplay:
    route: str
    stop_events: int
    false_positive_stops: int
    exhaustion_reached: bool
    exhaustion_index: int | None
    attempts_after_exhaustion: int
    false_negative: bool


def _found_before(outcome: RunOutcome, index: int) -> set[str]:
    found: set[str] = set()
    for event in outcome.trace.route_trials:
        if event.index >= index:
            break
        found.update(event.retrieved_merged_source_ids)
    return found


def _calls_before(outcome: RunOutcome, index: int) -> int:
    return sum(1 for event in outcome.trace.route_trials if event.index < index)


def replay_task_route(
    task: DiscoveryTask, outcome: RunOutcome, route: DiscoveryRoute
) -> RouteOracleReplay:
    """Replay frozen O1 for one route on one complete-gold task."""

    route_gold = set(task.protected_gold.reachable_via(route)) & set(
        task.protected_gold.gold_content_identities
    )
    route_stops = [
        item
        for item in outcome.trace.stop_decisions
        if item.scope == StopScope.ROUTE.value and item.route_id == route.value
    ]
    false_positive_stops = 0
    for decision in route_stops:
        residual = route_gold - _found_before(outcome, decision.index)
        remaining_budget = max(
            0, task.budget.max_route_calls - _calls_before(outcome, decision.index)
        )
        if residual and remaining_budget >= 1:
            false_positive_stops += 1

    found: set[str] = set()
    exhaustion_index: int | None = 0 if not route_gold else None
    for event in outcome.trace.route_trials:
        found.update(event.retrieved_merged_source_ids)
        if exhaustion_index is None and not (route_gold - found):
            exhaustion_index = event.index

    attempts_after = 0
    if exhaustion_index is not None:
        attempts_after = sum(
            1
            for event in outcome.trace.route_trials
            if event.route_id == route.value and event.index > exhaustion_index
        )

    return RouteOracleReplay(
        route=route.value,
        stop_events=len(route_stops),
        false_positive_stops=false_positive_stops,
        exhaustion_reached=exhaustion_index is not None,
        exhaustion_index=exhaustion_index,
        attempts_after_exhaustion=attempts_after,
        false_negative=exhaustion_index is not None and attempts_after > 1,
    )


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def _system_projection(
    tasks_by_id: dict[str, DiscoveryTask], representatives: dict[str, RunOutcome]
) -> dict[str, Any]:
    replays: list[RouteOracleReplay] = []
    by_route: dict[str, list[RouteOracleReplay]] = defaultdict(list)
    for task_id, outcome in sorted(representatives.items()):
        for route in DiscoveryRoute:
            replay = replay_task_route(tasks_by_id[task_id], outcome, route)
            replays.append(replay)
            by_route[route.value].append(replay)

    stop_events = sum(item.stop_events for item in replays)
    false_positives = sum(item.false_positive_stops for item in replays)
    exhausted = sum(item.exhaustion_reached for item in replays)
    false_negatives = sum(item.false_negative for item in replays)
    return {
        "route_stop_events": stop_events,
        "route_stop_false_positive_count": false_positives,
        "route_stop_false_positive_rate": _rate(false_positives, stop_events),
        "routes_reaching_oracle_exhaustion": exhausted,
        "route_stop_false_negative_count": false_negatives,
        "route_stop_false_negative_rate": _rate(false_negatives, exhausted),
        "attempts_after_exhaustion_total": sum(
            item.attempts_after_exhaustion for item in replays
        ),
        "by_route": {
            route.value: {
                "route_stop_events": sum(item.stop_events for item in by_route[route.value]),
                "route_stop_false_positive_count": sum(
                    item.false_positive_stops for item in by_route[route.value]
                ),
                "routes_reaching_oracle_exhaustion": sum(
                    item.exhaustion_reached for item in by_route[route.value]
                ),
                "route_stop_false_negative_count": sum(
                    item.false_negative for item in by_route[route.value]
                ),
                "attempts_after_exhaustion_total": sum(
                    item.attempts_after_exhaustion for item in by_route[route.value]
                ),
            }
            for route in DiscoveryRoute
        },
    }


def _aggregate_only(system: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in system.items() if key != "by_route"}


def build_route_stop_projection(
    tasks: tuple[DiscoveryTask, ...], outcomes: tuple[RunOutcome, ...]
) -> dict[str, Any]:
    """Build the compact publication projection for O1 across all frozen systems."""

    tasks_by_id = {task.task_id: task for task in tasks}
    systems = sorted({outcome.record["system_id"] for outcome in outcomes})
    full: dict[str, dict[str, Any]] = {}
    for system_id in systems:
        representatives = _representatives(outcomes, system_id)
        if set(representatives) != set(tasks_by_id):
            raise ValueError(f"{system_id}: missing frozen task outcomes")
        full[system_id] = _system_projection(tasks_by_id, representatives)

    return {
        "schema_version": "orion.p2.offline-route-stop-oracle.v1",
        # Same derivation as the archive summary: the label tracks the achieved
        # precision tier of the frozen N instead of pinning a superseded campaign.
        "analysis_authority": achieved_precision_tier(len(tasks_by_id))["achieved_tier"],
        "oracle": "O1",
        "n_tasks": len(tasks_by_id),
        "repeat_handling": "collapsed_within_task_after_deterministic_trace_check",
        "false_positive_definition": (
            "declared route stop with >=1 previously-unfound reachable gold identity "
            "and >=1 remaining route-call budget unit"
        ),
        "false_negative_definition": (
            "more than one further attempt on a route after oracle exhaustion; "
            "one confirming attempt is allowed"
        ),
        "source_record_digest_sha256": sha256_digest([item.record for item in outcomes]),
        "source_raw_artifact_hash_list_digest_sha256": sha256_digest(
            [item.record["raw_artifact_hash"] for item in outcomes]
        ),
        "systems": {name: _aggregate_only(values) for name, values in full.items()},
        "orion_full_by_route": full["orion_full"]["by_route"],
        "interpretation": (
            "route-stop and task-stop are distinct: the censored restricted-route case "
            "is an O1 route-stop false positive, while its unresolved O4 obligation "
            "prevents ORION from asserting task completeness"
        ),
    }


__all__ = ["RouteOracleReplay", "build_route_stop_projection", "replay_task_route"]
