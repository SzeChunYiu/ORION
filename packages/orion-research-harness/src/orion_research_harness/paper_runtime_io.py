from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Mapping, Sequence

from orion.self_orion.saturation_vector import DevelopmentSaturationAxis

from .epistemic_navigation import (
    EpistemicChart,
    NavigationState,
    Obligation,
    ObligationStatus,
    RouteContract,
    RouteStopReceipt,
)
from .research_saturation import ResearchRoundEvidence


def jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _mapping(value: object, *, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be an object")
    return value


def _array(value: object, *, name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise TypeError(f"{name} must be an array")
    return value


def _strings(value: object, *, name: str) -> tuple[str, ...]:
    rows = _array(value, name=name)
    result = tuple(str(item) for item in rows)
    if any(not item.strip() for item in result):
        raise ValueError(f"{name} entries must be non-empty")
    return result


def route_contract_from_mapping(value: object) -> RouteContract:
    raw = _mapping(value, name="route_contract")
    return RouteContract(
        route_id=str(raw["route_id"]),
        route_family=str(raw["route_family"]),
        obligation_ids=_strings(raw.get("obligation_ids", ()), name="obligation_ids"),
        critical_assumption_ids=_strings(
            raw.get("critical_assumption_ids", ()), name="critical_assumption_ids"
        ),
        coverage_scope_ids=_strings(
            raw.get("coverage_scope_ids", ()), name="coverage_scope_ids"
        ),
        censoring_scope_ids=_strings(
            raw.get("censoring_scope_ids", ()), name="censoring_scope_ids"
        ),
        available=raw.get("available", True),
    )


def navigation_state_from_mapping(value: object) -> NavigationState:
    raw = _mapping(value, name="navigation_state")
    chart_raw = _mapping(raw["active_chart"], name="active_chart")
    edges: list[tuple[str, str]] = []
    for index, edge in enumerate(_array(chart_raw.get("edges", ()), name="active_chart.edges")):
        pair = _array(edge, name=f"active_chart.edges[{index}]")
        if len(pair) != 2:
            raise ValueError("chart edges must have exactly two endpoints")
        edges.append((str(pair[0]), str(pair[1])))
    chart = EpistemicChart(
        chart_id=str(chart_raw["chart_id"]),
        location_ids=_strings(chart_raw.get("location_ids", ()), name="active_chart.location_ids"),
        edges=tuple(edges),
        obligation_ids=_strings(chart_raw.get("obligation_ids", ()), name="active_chart.obligation_ids"),
    )
    routes = tuple(
        route_contract_from_mapping(item)
        for item in _array(raw.get("routes", ()), name="routes")
    )
    obligations: list[Obligation] = []
    for index, item in enumerate(_array(raw.get("obligations", ()), name="obligations")):
        row = _mapping(item, name=f"obligations[{index}]")
        obligations.append(
            Obligation(
                obligation_id=str(row["obligation_id"]),
                mandatory=row.get("mandatory", True),
                status=ObligationStatus(str(row.get("status", "OPEN"))),
                evidence_ids=_strings(row.get("evidence_ids", ()), name="obligation.evidence_ids"),
                closure_certificate_ids=_strings(
                    row.get("closure_certificate_ids", ()),
                    name="obligation.closure_certificate_ids",
                ),
            )
        )
    stops: list[RouteStopReceipt] = []
    for index, item in enumerate(
        _array(raw.get("route_stop_receipts", ()), name="route_stop_receipts")
    ):
        row = _mapping(item, name=f"route_stop_receipts[{index}]")
        stops.append(
            RouteStopReceipt(
                route_id=str(row["route_id"]),
                evidence_ids=_strings(row.get("evidence_ids", ()), name="route_stop.evidence_ids"),
                local_only=row.get("local_only", True),
            )
        )
    current = raw.get("current_location_id")
    if current is not None and not isinstance(current, str):
        raise TypeError("current_location_id must be a string or null")
    budget = raw.get("remaining_budget")
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise TypeError("remaining_budget must be an integer")
    return NavigationState(
        active_chart=chart,
        current_location_id=current,
        frontier_ids=_strings(raw.get("frontier_ids", ()), name="frontier_ids"),
        routes=routes,
        obligations=tuple(obligations),
        remaining_budget=budget,
        censored_route_ids=_strings(raw.get("censored_route_ids", ()), name="censored_route_ids"),
        visited_location_ids=_strings(raw.get("visited_location_ids", ()), name="visited_location_ids"),
        evidence_ids=_strings(raw.get("evidence_ids", ()), name="evidence_ids"),
        route_stop_receipts=tuple(stops),
        history=_strings(raw.get("history", ()), name="history"),
    )


def research_rounds_from_mapping(value: object) -> tuple[ResearchRoundEvidence, ...]:
    raw = _mapping(value, name="research_saturation_input")
    rounds: list[ResearchRoundEvidence] = []
    for index, item in enumerate(_array(raw.get("rounds", ()), name="rounds")):
        row = _mapping(item, name=f"rounds[{index}]")
        routes = tuple(
            route_contract_from_mapping(route)
            for route in _array(row.get("route_contracts", ()), name="route_contracts")
        )
        observed = tuple(
            DevelopmentSaturationAxis(str(axis))
            for axis in _strings(row.get("observed_axes", ()), name="observed_axes")
        )
        axis_raw = _mapping(row.get("axis_item_ids", {}), name="axis_item_ids")
        axis_rows: list[tuple[DevelopmentSaturationAxis, tuple[str, ...]]] = []
        for axis_name, ids in axis_raw.items():
            axis_rows.append(
                (
                    DevelopmentSaturationAxis(str(axis_name)),
                    _strings(ids, name=f"axis_item_ids.{axis_name}"),
                )
            )
        residual_axes = tuple(
            DevelopmentSaturationAxis(str(axis))
            for axis in _strings(row.get("residual_axes", ()), name="residual_axes")
        )
        rounds.append(
            ResearchRoundEvidence(
                round_id=str(row["round_id"]),
                route_contracts=routes,
                observed_axes=observed,
                axis_item_ids=tuple(axis_rows),
                residual_axes=residual_axes,
                residual_signature=_strings(
                    row.get("residual_signature", ()), name="residual_signature"
                ),
                resource_bound=row.get("resource_bound", False),
            )
        )
    return tuple(rounds)


__all__ = [
    "jsonable",
    "navigation_state_from_mapping",
    "research_rounds_from_mapping",
    "route_contract_from_mapping",
]
