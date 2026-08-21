"""Run-level operator coverage.

The regression this file exists for: the P1-U R6 campaign ran 48 episodes whose
ablation arm never executed ``DIAGNOSE``, and nothing noticed. Static execution
coverage said ready, and the campaign's own trace assertion listed four operators,
none of them the missing one.
"""

from __future__ import annotations

import pytest

from orion.engine.cycle import CycleOperator
from orion_research_harness.operator_coverage import (
    CYCLE_OPERATORS,
    OperatorNotExercised,
    compare_operator_coverage,
    require_operators_exercised,
    run_operator_coverage,
)

# The exact sequence every R6 episode produced, verbatim from the reproduction.
R6_SEQUENCE = [
    "RECURSE", "FRAME", "SEARCH", "ABSORB", "RECONSTRUCT", "DETECT",
    "RECURSE", "SATURATE_BOUNDED",
    "SEARCH", "ABSORB", "RECONSTRUCT", "DETECT", "RECURSE", "SATURATE_BOUNDED",
]

FULL_SEQUENCE = [
    "RECURSE", "FRAME", "SEARCH", "ABSORB", "RECONSTRUCT", "DETECT",
    "DIAGNOSE", "REFRAME", "REOPEN", "RECURSE", "SATURATE_BOUNDED",
]


def test_cycle_operator_list_matches_the_engine() -> None:
    """A new engine operator must fail here, not silently drop out of coverage."""

    assert set(CYCLE_OPERATORS) == {member.value for member in CycleOperator}
    assert len(CYCLE_OPERATORS) == len(set(CYCLE_OPERATORS))


def test_the_r6_sequence_reports_diagnose_as_never_executed() -> None:
    report = run_operator_coverage(R6_SEQUENCE)
    assert "DIAGNOSE" in report["never_executed"]
    assert "REFRAME" in report["never_executed"]
    assert "REOPEN" in report["never_executed"]
    assert report["executed"] == [
        "FRAME", "SEARCH", "ABSORB", "RECONSTRUCT", "DETECT",
        "RECURSE", "SATURATE_BOUNDED",
    ]
    assert report["execution_counts"]["DETECT"] == 2
    assert report["grants_completeness"] is False


def test_requiring_diagnose_on_the_r6_sequence_raises_and_names_it() -> None:
    """The one line that would have caught it on episode 1."""

    with pytest.raises(OperatorNotExercised) as error:
        require_operators_exercised(
            R6_SEQUENCE, {"DIAGNOSE"}, label="ORION_NATIVE_BASE"
        )
    message = str(error.value)
    assert "ORION_NATIVE_BASE" in message
    assert "DIAGNOSE" in message
    assert "cannot be scored" in message


def test_a_full_sequence_satisfies_the_requirement() -> None:
    coverage = require_operators_exercised(FULL_SEQUENCE, {"DIAGNOSE", "REFRAME"})
    assert coverage["never_executed"] == []


def test_requiring_an_unknown_operator_is_a_caller_error() -> None:
    with pytest.raises(OperatorNotExercised, match="not cycle operators"):
        require_operators_exercised(FULL_SEQUENCE, {"DIAGNOSE", "TELEPORT"})


def test_coverage_accepts_an_outcome_mapping_and_enum_members() -> None:
    outcome = {"schema": "ORION.HarnessSolveOutcome.v1", "operator_sequence": R6_SEQUENCE}
    assert run_operator_coverage(outcome)["never_executed"] == ["DIAGNOSE", "REFRAME", "REOPEN"]

    as_enums = [CycleOperator(name) for name in FULL_SEQUENCE]
    assert run_operator_coverage(as_enums)["never_executed"] == []


def test_an_empty_run_executes_nothing_rather_than_erroring() -> None:
    report = run_operator_coverage([])
    assert report["executed"] == []
    assert report["never_executed"] == list(CYCLE_OPERATORS)


def test_unknown_operators_in_a_trace_are_surfaced_not_dropped() -> None:
    report = run_operator_coverage(["FRAME", "WOBBLE"])
    assert report["unknown_operators"] == ["WOBBLE"]
    assert "FRAME" in report["executed"]


def test_comparing_arms_shows_an_ablation_is_not_an_ablation() -> None:
    """Two arms with identical operator sets differ only in parameters."""

    comparison = compare_operator_coverage(
        [("BASE", R6_SEQUENCE), ("ARD", R6_SEQUENCE)]
    )
    assert comparison["identical_operator_sets"] is True
    assert comparison["executed_by_some"] == []

    informative = compare_operator_coverage(
        [("BASE", R6_SEQUENCE), ("ARD", FULL_SEQUENCE)]
    )
    assert informative["identical_operator_sets"] is False
    assert "DIAGNOSE" in informative["executed_by_some"]
