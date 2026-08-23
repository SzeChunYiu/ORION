from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping, Sequence


class ObligationStatus(str, Enum):
    OPEN = "OPEN"
    SATISFIED = "SATISFIED"
    DISCHARGED = "DISCHARGED"
    CANNOT_CHECK = "CANNOT_CHECK"


class NavigationAction(str, Enum):
    ORIENT = "ORIENT"
    EXECUTE_ROUTE = "EXECUTE_ROUTE"
    REFRAME = "REFRAME"
    ROUTE_STOP = "ROUTE_STOP"
    TASK_STOP = "TASK_STOP"
    DEFER = "DEFER"
    CANNOT_CHECK = "CANNOT_CHECK"


def _nonempty(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _unique(values: Sequence[str], *, name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an array")
    rows = tuple(_nonempty(str(item), name=f"{name} entry") for item in values)
    if len(rows) != len(set(rows)):
        raise ValueError(f"{name} entries must be unique")
    return rows


@dataclass(frozen=True)
class RouteContract:
    route_id: str
    route_family: str
    obligation_ids: tuple[str, ...]
    critical_assumption_ids: tuple[str, ...]
    coverage_scope_ids: tuple[str, ...]
    censoring_scope_ids: tuple[str, ...] = ()
    available: bool = True

    def __post_init__(self) -> None:
        _nonempty(self.route_id, name="route_id")
        _nonempty(self.route_family, name="route_family")
        object.__setattr__(self, "obligation_ids", _unique(self.obligation_ids, name="obligation_ids"))
        object.__setattr__(
            self,
            "critical_assumption_ids",
            _unique(self.critical_assumption_ids, name="critical_assumption_ids"),
        )
        object.__setattr__(
            self,
            "coverage_scope_ids",
            _unique(self.coverage_scope_ids, name="coverage_scope_ids"),
        )
        object.__setattr__(
            self,
            "censoring_scope_ids",
            _unique(self.censoring_scope_ids, name="censoring_scope_ids"),
        )
        if not isinstance(self.available, bool):
            raise TypeError("available must be a boolean")

    @property
    def structurally_identified(self) -> bool:
        return bool(self.critical_assumption_ids and self.coverage_scope_ids)


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    mandatory: bool = True
    status: ObligationStatus = ObligationStatus.OPEN
    evidence_ids: tuple[str, ...] = ()
    closure_certificate_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _nonempty(self.obligation_id, name="obligation_id")
        if not isinstance(self.mandatory, bool):
            raise TypeError("mandatory must be a boolean")
        object.__setattr__(self, "evidence_ids", _unique(self.evidence_ids, name="evidence_ids"))
        object.__setattr__(
            self,
            "closure_certificate_ids",
            _unique(self.closure_certificate_ids, name="closure_certificate_ids"),
        )

    @property
    def task_closed(self) -> bool:
        if self.closure_certificate_ids:
            return True
        return self.status in {ObligationStatus.SATISFIED, ObligationStatus.DISCHARGED}


@dataclass(frozen=True)
class EpistemicChart:
    chart_id: str
    location_ids: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    obligation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _nonempty(self.chart_id, name="chart_id")
        locations = _unique(self.location_ids, name="location_ids")
        obligations = _unique(self.obligation_ids, name="obligation_ids")
        object.__setattr__(self, "location_ids", locations)
        object.__setattr__(self, "obligation_ids", obligations)
        normalized: list[tuple[str, str]] = []
        for edge in self.edges:
            if not isinstance(edge, (tuple, list)) or len(edge) != 2:
                raise TypeError("chart edges must be two-item arrays")
            left, right = str(edge[0]), str(edge[1])
            if left not in locations or right not in locations:
                raise ValueError("chart edge endpoint is outside the chart")
            normalized.append((left, right))
        if len(normalized) != len(set(normalized)):
            raise ValueError("chart edges must be unique")
        object.__setattr__(self, "edges", tuple(normalized))


@dataclass(frozen=True)
class RouteStopReceipt:
    route_id: str
    evidence_ids: tuple[str, ...]
    local_only: bool = True

    def __post_init__(self) -> None:
        _nonempty(self.route_id, name="route stop route_id")
        object.__setattr__(self, "evidence_ids", _unique(self.evidence_ids, name="route stop evidence_ids"))
        if not self.evidence_ids:
            raise ValueError("route stop requires evidence")
        if self.local_only is not True:
            raise ValueError("route-stop receipt cannot grant task-stop authority")


@dataclass(frozen=True)
class NavigationState:
    active_chart: EpistemicChart
    current_location_id: str | None
    frontier_ids: tuple[str, ...]
    routes: tuple[RouteContract, ...]
    obligations: tuple[Obligation, ...]
    remaining_budget: int
    censored_route_ids: tuple[str, ...] = ()
    visited_location_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    route_stop_receipts: tuple[RouteStopReceipt, ...] = ()
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.current_location_id is not None and self.current_location_id not in self.active_chart.location_ids:
            raise ValueError("current location is outside the active chart")
        object.__setattr__(self, "frontier_ids", _unique(self.frontier_ids, name="frontier_ids"))
        if any(item not in self.active_chart.location_ids for item in self.frontier_ids):
            raise ValueError("frontier location is outside the active chart")
        route_ids = [item.route_id for item in self.routes]
        if len(route_ids) != len(set(route_ids)):
            raise ValueError("navigation routes must have unique identities")
        obligation_ids = [item.obligation_id for item in self.obligations]
        if len(obligation_ids) != len(set(obligation_ids)):
            raise ValueError("navigation obligations must have unique identities")
        object.__setattr__(self, "censored_route_ids", _unique(self.censored_route_ids, name="censored_route_ids"))
        object.__setattr__(self, "visited_location_ids", _unique(self.visited_location_ids, name="visited_location_ids"))
        object.__setattr__(self, "evidence_ids", _unique(self.evidence_ids, name="navigation evidence_ids"))
        if isinstance(self.remaining_budget, bool) or not isinstance(self.remaining_budget, int):
            raise TypeError("remaining_budget must be an integer")
        if self.remaining_budget < 0:
            raise ValueError("remaining_budget cannot be negative")


@dataclass(frozen=True)
class NavigationDecision:
    action: NavigationAction
    route_id: str | None = None
    reason: str = ""
    open_obligation_ids: tuple[str, ...] = ()
    grants_global_task_stop_authority: bool = False


@dataclass(frozen=True)
class ReframeMorphism:
    reframe_id: str
    source_chart_id: str
    target_chart_id: str
    location_map: tuple[tuple[str, str], ...]
    obligation_map: tuple[tuple[str, str], ...]
    support_preserved_obligation_ids: tuple[str, ...] = ()
    evidence_identity_preserved: bool = True

    def __post_init__(self) -> None:
        _nonempty(self.reframe_id, name="reframe_id")
        _nonempty(self.source_chart_id, name="source_chart_id")
        _nonempty(self.target_chart_id, name="target_chart_id")
        if not isinstance(self.evidence_identity_preserved, bool):
            raise TypeError("evidence_identity_preserved must be boolean")
        for name, pairs in (("location_map", self.location_map), ("obligation_map", self.obligation_map)):
            normalized: list[tuple[str, str]] = []
            for pair in pairs:
                if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                    raise TypeError(f"{name} entries must be two-item arrays")
                left, right = str(pair[0]), str(pair[1])
                _nonempty(left, name=f"{name} source")
                _nonempty(right, name=f"{name} target")
                normalized.append((left, right))
            if len(normalized) != len(set(normalized)):
                raise ValueError(f"{name} entries must be unique")
            object.__setattr__(self, name, tuple(normalized))
        object.__setattr__(
            self,
            "support_preserved_obligation_ids",
            _unique(self.support_preserved_obligation_ids, name="support_preserved_obligation_ids"),
        )


def structurally_independent(left: RouteContract, right: RouteContract) -> bool:
    """Conservative Paper-VII sufficient condition for route independence.

    Distinct names, APIs or observed outputs do not count. Both routes must expose
    their critical failure/coverage assumptions, and those registered assumption
    sets must be disjoint. Missing assumption identity is CANNOT_CHECK -> False.
    """

    if not left.structurally_identified or not right.structurally_identified:
        return False
    if left.route_id == right.route_id:
        return False
    return not (set(left.critical_assumption_ids) & set(right.critical_assumption_ids))


def _open_mandatory(state: NavigationState) -> tuple[Obligation, ...]:
    return tuple(item for item in state.obligations if item.mandatory and not item.task_closed)


def task_stop_allowed(state: NavigationState) -> bool:
    mandatory = tuple(item for item in state.obligations if item.mandatory)
    return bool(mandatory) and all(item.task_closed for item in mandatory)


def plan_navigation(state: NavigationState) -> NavigationDecision:
    open_mandatory = _open_mandatory(state)
    if task_stop_allowed(state):
        return NavigationDecision(
            action=NavigationAction.TASK_STOP,
            reason="all mandatory obligations are satisfied, discharged, or certificate-covered",
            grants_global_task_stop_authority=True,
        )
    cannot_check = tuple(
        item.obligation_id
        for item in open_mandatory
        if item.status is ObligationStatus.CANNOT_CHECK
    )
    if cannot_check:
        return NavigationDecision(
            action=NavigationAction.CANNOT_CHECK,
            reason="mandatory obligation cannot currently be checked",
            open_obligation_ids=tuple(item.obligation_id for item in open_mandatory),
        )
    if state.remaining_budget <= 0:
        return NavigationDecision(
            action=NavigationAction.CANNOT_CHECK,
            reason="resource budget exhausted with mandatory obligations still open",
            open_obligation_ids=tuple(item.obligation_id for item in open_mandatory),
        )
    if state.current_location_id is None:
        return NavigationDecision(
            action=NavigationAction.ORIENT,
            reason="epistemic starting location/orientation is unresolved",
            open_obligation_ids=tuple(item.obligation_id for item in open_mandatory),
        )

    stopped = {item.route_id for item in state.route_stop_receipts}
    censored = set(state.censored_route_ids)
    open_ids = {item.obligation_id for item in open_mandatory}
    candidates = [
        route
        for route in state.routes
        if route.available
        and route.route_id not in stopped
        and route.route_id not in censored
        and (not route.obligation_ids or bool(open_ids & set(route.obligation_ids)))
    ]
    if candidates:
        candidates.sort(key=lambda item: (not item.structurally_identified, item.route_family, item.route_id))
        chosen = candidates[0]
        return NavigationDecision(
            action=NavigationAction.EXECUTE_ROUTE,
            route_id=chosen.route_id,
            reason="open mandatory obligation has an executable registered route",
            open_obligation_ids=tuple(item.obligation_id for item in open_mandatory),
        )
    return NavigationDecision(
        action=NavigationAction.CANNOT_CHECK,
        reason="all registered executable routes are stopped, censored, unavailable, or out of scope while mandatory obligations remain open",
        open_obligation_ids=tuple(item.obligation_id for item in open_mandatory),
    )


def record_route_stop(
    state: NavigationState,
    route_id: str,
    *,
    evidence_ids: Sequence[str],
) -> NavigationState:
    if route_id not in {item.route_id for item in state.routes}:
        raise KeyError(route_id)
    receipt = RouteStopReceipt(route_id, tuple(evidence_ids))
    existing = {item.route_id: item for item in state.route_stop_receipts}
    if route_id in existing:
        if existing[route_id] != receipt:
            raise ValueError("route already stopped with different evidence")
        return state
    return replace(
        state,
        route_stop_receipts=(*state.route_stop_receipts, receipt),
        history=(*state.history, f"ROUTE_STOP:{route_id}"),
    )


def apply_route_observation(
    state: NavigationState,
    *,
    route_id: str,
    location_id: str | None,
    evidence_ids: Sequence[str],
    satisfied_obligation_ids: Sequence[str] = (),
    discharged_obligation_ids: Sequence[str] = (),
    closure_certificate_ids_by_obligation: Mapping[str, Sequence[str]] | None = None,
) -> NavigationState:
    route = next((item for item in state.routes if item.route_id == route_id), None)
    if route is None:
        raise KeyError(route_id)
    if not route.available or route_id in set(state.censored_route_ids):
        raise ValueError("route is unavailable/censored")
    if location_id is not None and location_id not in state.active_chart.location_ids:
        raise ValueError("observation location is outside active chart")
    evidence = _unique(tuple(evidence_ids), name="route observation evidence_ids")
    satisfied = set(_unique(tuple(satisfied_obligation_ids), name="satisfied_obligation_ids"))
    discharged = set(_unique(tuple(discharged_obligation_ids), name="discharged_obligation_ids"))
    if satisfied & discharged:
        raise ValueError("an obligation cannot be both satisfied and discharged in one observation")
    if (satisfied or discharged) and not evidence:
        raise ValueError("closing an obligation through a route observation requires evidence")
    closure_map = closure_certificate_ids_by_obligation or {}
    obligations: list[Obligation] = []
    known = {item.obligation_id for item in state.obligations}
    if not (satisfied | discharged | set(closure_map)) <= known:
        raise KeyError("observation references unknown obligation")
    for obligation in state.obligations:
        status = obligation.status
        obligation_evidence = obligation.evidence_ids
        certificates = obligation.closure_certificate_ids
        if obligation.obligation_id in satisfied:
            status = ObligationStatus.SATISFIED
            obligation_evidence = tuple(dict.fromkeys((*obligation_evidence, *evidence)))
        elif obligation.obligation_id in discharged:
            status = ObligationStatus.DISCHARGED
            obligation_evidence = tuple(dict.fromkeys((*obligation_evidence, *evidence)))
        if obligation.obligation_id in closure_map:
            ids = _unique(tuple(closure_map[obligation.obligation_id]), name="closure certificate ids")
            if not ids:
                raise ValueError("closure certificate map entry cannot be empty")
            certificates = tuple(dict.fromkeys((*certificates, *ids)))
        obligations.append(
            replace(
                obligation,
                status=status,
                evidence_ids=obligation_evidence,
                closure_certificate_ids=certificates,
            )
        )
    visited = state.visited_location_ids
    if location_id is not None:
        visited = tuple(dict.fromkeys((*visited, location_id)))
    all_evidence = tuple(dict.fromkeys((*state.evidence_ids, *evidence)))
    return replace(
        state,
        current_location_id=location_id if location_id is not None else state.current_location_id,
        visited_location_ids=visited,
        evidence_ids=all_evidence,
        obligations=tuple(obligations),
        remaining_budget=max(0, state.remaining_budget - 1),
        history=(*state.history, f"ROUTE_OBSERVATION:{route_id}"),
    )


def apply_reframe(
    state: NavigationState,
    target_chart: EpistemicChart,
    morphism: ReframeMorphism,
) -> NavigationState:
    if morphism.source_chart_id != state.active_chart.chart_id:
        raise ValueError("reframe source chart mismatch")
    if morphism.target_chart_id != target_chart.chart_id:
        raise ValueError("reframe target chart mismatch")
    location_map = dict(morphism.location_map)
    obligation_map = dict(morphism.obligation_map)
    if len(location_map) != len(morphism.location_map):
        raise ValueError("reframe location map must be functional")
    if len(obligation_map) != len(morphism.obligation_map):
        raise ValueError("reframe obligation map must be functional")
    if any(target not in target_chart.location_ids for target in location_map.values()):
        raise ValueError("reframe maps to unknown target location")
    if any(target not in target_chart.obligation_ids for target in obligation_map.values()):
        raise ValueError("reframe maps to unknown target obligation")
    preserved = set(morphism.support_preserved_obligation_ids)
    obligations: list[Obligation] = []
    produced: set[str] = set()
    for old in state.obligations:
        mapped = obligation_map.get(old.obligation_id)
        if mapped is None:
            obligations.append(
                replace(
                    old,
                    status=ObligationStatus.CANNOT_CHECK if old.mandatory else ObligationStatus.OPEN,
                    closure_certificate_ids=(),
                )
            )
            continue
        produced.add(mapped)
        if old.task_closed and old.obligation_id in preserved:
            status = old.status
            certificates = old.closure_certificate_ids
        elif old.task_closed:
            status = ObligationStatus.OPEN
            certificates = ()
        else:
            status = old.status
            certificates = () if old.status is ObligationStatus.CANNOT_CHECK else old.closure_certificate_ids
        obligations.append(
            Obligation(
                mapped,
                mandatory=old.mandatory,
                status=status,
                evidence_ids=old.evidence_ids,
                closure_certificate_ids=certificates,
            )
        )
    for obligation_id in target_chart.obligation_ids:
        if obligation_id not in produced and obligation_id not in {item.obligation_id for item in obligations}:
            obligations.append(Obligation(obligation_id, mandatory=True))

    mapped_routes: list[RouteContract] = []
    for route in state.routes:
        mapped_obligations = tuple(
            obligation_map.get(item, item)
            for item in route.obligation_ids
            if obligation_map.get(item, item) in target_chart.obligation_ids
        )
        mapped_routes.append(replace(route, obligation_ids=tuple(dict.fromkeys(mapped_obligations))))

    current = None
    if state.current_location_id is not None:
        current = location_map.get(state.current_location_id)
    evidence = state.evidence_ids if morphism.evidence_identity_preserved else ()
    return NavigationState(
        active_chart=target_chart,
        current_location_id=current,
        frontier_ids=(),
        routes=tuple(mapped_routes),
        obligations=tuple(obligations),
        remaining_budget=state.remaining_budget,
        censored_route_ids=state.censored_route_ids,
        visited_location_ids=tuple(
            dict.fromkeys(
                location_map[item]
                for item in state.visited_location_ids
                if item in location_map
            )
        ),
        evidence_ids=evidence,
        route_stop_receipts=(),
        history=(*state.history, f"REFRAME:{morphism.reframe_id}"),
    )


__all__ = [
    "EpistemicChart",
    "NavigationAction",
    "NavigationDecision",
    "NavigationState",
    "Obligation",
    "ObligationStatus",
    "ReframeMorphism",
    "RouteContract",
    "RouteStopReceipt",
    "apply_reframe",
    "apply_route_observation",
    "plan_navigation",
    "record_route_stop",
    "structurally_independent",
    "task_stop_allowed",
]
