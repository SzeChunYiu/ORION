"""The route- and task-stop paths must actually record a stop.

Both `BudgetedSession` stop paths were left on the pre-#1078 `StopDecision`
vocabulary when that refactor landed, so every call raised TypeError. P2's
premature-stopping measurement reads these records, which means it could not
be taken at all. These tests fail on the unmigrated code.
"""

from __future__ import annotations

import pytest

from orion.study.p2.cases import Budget
from orion.study.p2.runner import BudgetedSession, PublicIndex, SessionConfig
from orion.study.p2.systems import StopScope


def _session() -> BudgetedSession:
    return BudgetedSession(
        PublicIndex(records=(), postings=()),
        SessionConfig(
            task_id="t",
            availability=(),
            budget=Budget(
                max_route_calls=4,
                max_reads=4,
                max_tool_calls=4,
                max_model_tokens=1,
                max_wallclock_seconds=60.0,
            ),
            extraction_questions=("q",),
            extraction_shift_after_reads=None,
        ),
    )


def test_declaring_a_route_stop_records_one() -> None:
    session = _session()
    session.declare_route_stop("LEXICAL", "route went flat")
    assert len(session.stop_decisions) == 1
    decision = session.stop_decisions[0]
    assert decision.scope == StopScope.ROUTE.value
    assert decision.route_id == "LEXICAL"
    assert decision.reason == "route went flat"
    assert decision.declared is False


def test_task_stop_carries_the_completeness_claim() -> None:
    session = _session()
    session.record_task_stop(reason="done", claimed_complete=True)
    decision = session.stop_decisions[-1]
    assert decision.scope == StopScope.TASK.value
    assert decision.route_id == ""
    assert decision.declared is True


def test_route_stop_carries_the_attempt_count_it_was_taken_after() -> None:
    """Abandoning a route after real attempts is not abandoning it cold.

    Without the attempt index the oracle cannot separate the two, and
    prematurity stops being scoreable.
    """
    session = _session()
    session.declare_route_stop("SEMANTIC", "nothing new")
    assert session.stop_decisions[-1].attempt_index == 0


def test_stop_decisions_serialise() -> None:
    session = _session()
    session.declare_route_stop("LEXICAL", "flat")
    session.record_task_stop(reason="closing", claimed_complete=False)
    for decision in session.stop_decisions:
        payload = decision.as_json()
        assert set(payload) == {
            "index",
            "scope",
            "route_id",
            "attempt_index",
            "reason",
            "declared",
        }


def test_indices_are_distinct_and_ordered() -> None:
    session = _session()
    session.declare_route_stop("LEXICAL", "a")
    session.declare_route_stop("SEMANTIC", "b")
    indices = [d.index for d in session.stop_decisions]
    assert indices == sorted(indices)
    assert len(set(indices)) == len(indices)
