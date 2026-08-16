from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.search import SearchRouteKind


class RouteControlAction(str, Enum):
    CONTINUE = "CONTINUE"
    REFORMULATE = "REFORMULATE"
    SWITCH = "SWITCH"
    SUSPEND = "SUSPEND"
    STOP = "STOP"


class RouteReopenTrigger(str, Enum):
    MATERIAL_FRAME_CHANGE = "MATERIAL_FRAME_CHANGE"
    BACKEND_RECOVERY = "BACKEND_RECOVERY"
    BACKEND_REFRESH = "BACKEND_REFRESH"
    BUDGET_INCREASE = "BUDGET_INCREASE"
    ALTERNATIVE_ROUTE_MATERIAL_FINDING = "ALTERNATIVE_ROUTE_MATERIAL_FINDING"


@dataclass(frozen=True)
class FrozenRouteControlPolicy:
    """Named route-local heuristic; never a task-saturation authority."""

    policy_id: str
    reformulate_after_zero_novelty: int
    switch_after_zero_novelty: int

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("route-control policy id is required")
        if self.reformulate_after_zero_novelty < 1:
            raise ValueError("reformulation threshold must be positive")
        if self.switch_after_zero_novelty < self.reformulate_after_zero_novelty:
            raise ValueError("switch threshold cannot precede reformulation threshold")


@dataclass(frozen=True)
class RouteAttempt:
    attempt_id: str
    query_id: str
    retrieved_digests: tuple[str, ...]
    novel_digests: tuple[str, ...]
    cost_units: float
    execution_failure_signatures: tuple[str, ...] = ()
    backend_exhausted: bool = False

    def __post_init__(self) -> None:
        if not self.attempt_id.strip() or not self.query_id.strip():
            raise ValueError("route attempt and query identity are required")
        if self.cost_units < 0:
            raise ValueError("route attempt cost cannot be negative")
        if any(not item.strip() for item in self.retrieved_digests + self.novel_digests):
            raise ValueError("route evidence digests must be non-empty")
        if not set(self.novel_digests).issubset(self.retrieved_digests):
            raise ValueError("novel route evidence must be a subset of retrieved evidence")
        if self.backend_exhausted and self.execution_failure_signatures:
            raise ValueError("backend exhaustion and execution failure are distinct route states")

    @property
    def marginal_novelty(self) -> float:
        if not self.retrieved_digests:
            return 0.0
        return len(set(self.novel_digests)) / len(set(self.retrieved_digests))

    @property
    def successful_zero_novelty(self) -> bool:
        return not self.execution_failure_signatures and not self.backend_exhausted and not self.novel_digests


@dataclass(frozen=True)
class RouteControlState:
    route_id: str
    route_kind: SearchRouteKind
    attempts: tuple[RouteAttempt, ...]
    budget_units: float
    alternative_route_kinds: tuple[SearchRouteKind, ...] = ()

    def __post_init__(self) -> None:
        if not self.route_id.strip():
            raise ValueError("route id is required")
        if self.budget_units < 0:
            raise ValueError("route budget cannot be negative")
        if any(item is self.route_kind for item in self.alternative_route_kinds):
            raise ValueError("the active route cannot be its own alternative")
        attempt_ids = [item.attempt_id for item in self.attempts]
        if len(attempt_ids) != len(set(attempt_ids)):
            raise ValueError("route attempt ids must be unique")

    @property
    def spent_cost_units(self) -> float:
        return sum(item.cost_units for item in self.attempts)

    @property
    def remaining_budget_units(self) -> float:
        return max(0.0, self.budget_units - self.spent_cost_units)

    @property
    def consecutive_zero_novelty(self) -> int:
        count = 0
        for attempt in reversed(self.attempts):
            if not attempt.successful_zero_novelty:
                break
            count += 1
        return count

    @property
    def failure_signatures(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(signature for attempt in self.attempts for signature in attempt.execution_failure_signatures))


@dataclass(frozen=True)
class RouteControlDecision:
    route_id: str
    route_kind: SearchRouteKind
    policy_id: str
    action: RouteControlAction
    reasons: tuple[str, ...]
    spent_cost_units: float
    remaining_budget_units: float
    marginal_novelty: float | None
    last_retrieved_digests: tuple[str, ...]
    last_novel_digests: tuple[str, ...]
    failure_signatures: tuple[str, ...]
    reopen_triggers: tuple[RouteReopenTrigger, ...]

    @property
    def certifies_task_saturation(self) -> bool:
        return False


def decide_route(state: RouteControlState, policy: FrozenRouteControlPolicy) -> RouteControlDecision:
    if not state.attempts:
        return RouteControlDecision(
            state.route_id, state.route_kind, policy.policy_id, RouteControlAction.CONTINUE,
            ("route_untried",), 0.0, state.budget_units, None, (), (), (), (),
        )

    last = state.attempts[-1]
    common = dict(
        route_id=state.route_id,
        route_kind=state.route_kind,
        policy_id=policy.policy_id,
        spent_cost_units=state.spent_cost_units,
        remaining_budget_units=state.remaining_budget_units,
        marginal_novelty=last.marginal_novelty,
        last_retrieved_digests=last.retrieved_digests,
        last_novel_digests=last.novel_digests,
        failure_signatures=state.failure_signatures,
    )
    if state.remaining_budget_units <= 0:
        return RouteControlDecision(**common, action=RouteControlAction.STOP, reasons=("route_budget_exhausted",), reopen_triggers=(RouteReopenTrigger.BUDGET_INCREASE, RouteReopenTrigger.MATERIAL_FRAME_CHANGE))
    if last.backend_exhausted:
        return RouteControlDecision(**common, action=RouteControlAction.STOP, reasons=("backend_reported_route_exhausted",), reopen_triggers=(RouteReopenTrigger.BACKEND_REFRESH, RouteReopenTrigger.MATERIAL_FRAME_CHANGE))
    if last.execution_failure_signatures:
        return RouteControlDecision(**common, action=RouteControlAction.SUSPEND, reasons=("route_execution_failed", *last.execution_failure_signatures), reopen_triggers=(RouteReopenTrigger.BACKEND_RECOVERY, RouteReopenTrigger.MATERIAL_FRAME_CHANGE))

    flat = state.consecutive_zero_novelty
    if flat >= policy.switch_after_zero_novelty and state.alternative_route_kinds:
        alternatives = ",".join(item.value for item in state.alternative_route_kinds)
        return RouteControlDecision(**common, action=RouteControlAction.SWITCH, reasons=(f"zero_novelty_streak:{flat}", f"alternatives:{alternatives}"), reopen_triggers=(RouteReopenTrigger.ALTERNATIVE_ROUTE_MATERIAL_FINDING, RouteReopenTrigger.MATERIAL_FRAME_CHANGE))
    if flat >= policy.reformulate_after_zero_novelty:
        return RouteControlDecision(**common, action=RouteControlAction.REFORMULATE, reasons=(f"zero_novelty_streak:{flat}",), reopen_triggers=())
    return RouteControlDecision(**common, action=RouteControlAction.CONTINUE, reasons=("route_still_productive",), reopen_triggers=())


def should_reopen(decision: RouteControlDecision, observed_triggers: tuple[RouteReopenTrigger, ...]) -> bool:
    return bool(set(decision.reopen_triggers).intersection(observed_triggers))


__all__ = [
    "FrozenRouteControlPolicy", "RouteAttempt", "RouteControlAction", "RouteControlDecision",
    "RouteControlState", "RouteReopenTrigger", "decide_route", "should_reopen",
]
