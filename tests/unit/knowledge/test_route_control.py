import pytest

from orion.core.search import SearchRouteKind
from orion.knowledge.route_control import (
    FrozenRouteControlPolicy,
    RouteAttempt,
    RouteControlAction,
    RouteControlState,
    RouteReopenTrigger,
    decide_route,
    should_reopen,
)


POLICY = FrozenRouteControlPolicy(
    policy_id="route-control-v0-flat-1-switch-2",
    reformulate_after_zero_novelty=1,
    switch_after_zero_novelty=2,
)


def _attempt(
    attempt_id: str,
    *,
    retrieved: tuple[str, ...] = (),
    novel: tuple[str, ...] = (),
    cost: float = 1.0,
    failures: tuple[str, ...] = (),
    exhausted: bool = False,
) -> RouteAttempt:
    return RouteAttempt(
        attempt_id=attempt_id,
        query_id=f"query:{attempt_id}",
        retrieved_digests=retrieved,
        novel_digests=novel,
        cost_units=cost,
        execution_failure_signatures=failures,
        backend_exhausted=exhausted,
    )


def _state(
    *attempts: RouteAttempt,
    budget: float = 10.0,
    alternatives: tuple[SearchRouteKind, ...] = (),
) -> RouteControlState:
    return RouteControlState(
        route_id="route:parent-discipline",
        route_kind=SearchRouteKind.PARENT_DISCIPLINE,
        attempts=attempts,
        budget_units=budget,
        alternative_route_kinds=alternatives,
    )


def test_untried_and_productive_routes_continue():
    untried = decide_route(_state(), POLICY)
    assert untried.action is RouteControlAction.CONTINUE
    assert untried.marginal_novelty is None

    productive = decide_route(
        _state(_attempt("a1", retrieved=("d1", "d2"), novel=("d2",))),
        POLICY,
    )
    assert productive.action is RouteControlAction.CONTINUE
    assert productive.marginal_novelty == 0.5
    assert productive.last_novel_digests == ("d2",)
    assert not productive.certifies_task_saturation


def test_one_zero_novelty_attempt_reformulates():
    decision = decide_route(
        _state(_attempt("a1", retrieved=("d1",), novel=())),
        POLICY,
    )
    assert decision.action is RouteControlAction.REFORMULATE
    assert decision.reasons == ("zero_novelty_streak:1",)
    assert not decision.certifies_task_saturation


def test_repeated_zero_novelty_switches_only_when_an_alternative_exists():
    history = (
        _attempt("a1", retrieved=("d1",), novel=()),
        _attempt("a2", retrieved=("d1",), novel=()),
    )
    switched = decide_route(
        _state(*history, alternatives=(SearchRouteKind.ADVERSARIAL_OMISSION,)),
        POLICY,
    )
    assert switched.action is RouteControlAction.SWITCH
    assert RouteReopenTrigger.ALTERNATIVE_ROUTE_MATERIAL_FINDING in switched.reopen_triggers

    no_alternative = decide_route(_state(*history), POLICY)
    assert no_alternative.action is RouteControlAction.REFORMULATE
    assert not no_alternative.certifies_task_saturation


def test_execution_failure_suspends_and_preserves_failure_signature():
    decision = decide_route(
        _state(_attempt("a1", failures=("backend:429",))),
        POLICY,
    )
    assert decision.action is RouteControlAction.SUSPEND
    assert decision.failure_signatures == ("backend:429",)
    assert RouteReopenTrigger.BACKEND_RECOVERY in decision.reopen_triggers
    assert should_reopen(decision, (RouteReopenTrigger.BACKEND_RECOVERY,))
    assert not should_reopen(decision, (RouteReopenTrigger.BUDGET_INCREASE,))


def test_explicit_backend_exhaustion_stops_only_the_route_and_can_reopen():
    decision = decide_route(
        _state(_attempt("a1", retrieved=("d1",), novel=(), exhausted=True)),
        POLICY,
    )
    assert decision.action is RouteControlAction.STOP
    assert decision.reasons == ("backend_reported_route_exhausted",)
    assert not decision.certifies_task_saturation
    assert should_reopen(decision, (RouteReopenTrigger.BACKEND_REFRESH,))
    assert should_reopen(decision, (RouteReopenTrigger.MATERIAL_FRAME_CHANGE,))


def test_budget_exhaustion_stops_only_the_route_and_can_reopen():
    decision = decide_route(
        _state(
            _attempt("a1", retrieved=("d1",), novel=("d1",), cost=2.0),
            budget=2.0,
        ),
        POLICY,
    )
    assert decision.action is RouteControlAction.STOP
    assert decision.reasons == ("route_budget_exhausted",)
    assert decision.remaining_budget_units == 0.0
    assert not decision.certifies_task_saturation
    assert should_reopen(decision, (RouteReopenTrigger.BUDGET_INCREASE,))


def test_productive_attempt_resets_the_zero_novelty_streak():
    state = _state(
        _attempt("a1", retrieved=("d1",), novel=()),
        _attempt("a2", retrieved=("d2",), novel=("d2",)),
        _attempt("a3", retrieved=("d2",), novel=()),
        alternatives=(SearchRouteKind.ADVERSARIAL_OMISSION,),
    )
    assert state.consecutive_zero_novelty == 1
    assert decide_route(state, POLICY).action is RouteControlAction.REFORMULATE


def test_route_attempt_and_policy_refuse_invalid_state():
    with pytest.raises(ValueError, match="subset"):
        _attempt("a1", retrieved=("d1",), novel=("d2",))

    with pytest.raises(ValueError, match="switch threshold"):
        FrozenRouteControlPolicy(
            policy_id="bad",
            reformulate_after_zero_novelty=2,
            switch_after_zero_novelty=1,
        )

    with pytest.raises(ValueError, match="distinct route states"):
        _attempt("a2", failures=("backend:500",), exhausted=True)
