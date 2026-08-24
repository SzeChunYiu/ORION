"""BudgetedSession must actually provide what DiscoverySession declares.

The protocol declared `current_extraction_schema`; no implementation provided
it, and nothing checked. Every read that recorded the schema raised
AttributeError. A protocol nothing verifies is documentation, not a contract.
"""

from __future__ import annotations

from orion.study.p2.cases import Budget
from orion.study.p2.runner import BudgetedSession, PublicIndex, SessionConfig
from orion.study.p2.systems import DiscoverySession


def _session(schema: str | None = None) -> BudgetedSession:
    kwargs = {} if schema is None else {"extraction_schema": schema}
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
            **kwargs,
        ),
    )


def test_every_protocol_member_is_implemented() -> None:
    declared = {n for n in dir(DiscoverySession) if not n.startswith("_")}
    provided = {n for n in dir(BudgetedSession) if not n.startswith("_")}
    assert declared - provided == set()


def test_the_schema_is_readable_and_host_controlled() -> None:
    assert _session().current_extraction_schema == "P2.Extraction.v1"
    assert _session("P2.Extraction.v9").current_extraction_schema == "P2.Extraction.v9"


def test_the_question_is_still_readable() -> None:
    """The member that already worked must not regress."""
    assert _session().current_extraction_question == "q"
