"""A premise a check was handed must not read as a premise the check decided.

The fixtures are two miniature "theorems" over the same four-case space. One
decides its premise from the case; the other takes it as a parameter and asserts
the matching terminal for whichever value it is given --- which is the shape of
P7's transport theorem, reduced until the arithmetic is checkable by eye.
"""

from __future__ import annotations

import pytest

from orion.programme.decided_premises import (
    CaseAdmissibility,
    DecidedResult,
    DecisionConstraint,
    DecisionReason,
    Premise,
    UndecidedPremise,
    case_label,
    decision_outcome,
    measure_decision_constraint,
    require_decided,
    sample_assignments_accepted,
)
from orion.programme.records import Outcome

CASES = tuple({"left": left, "right": right} for left in (False, True) for right in (False, True))

DECIDED = Premise(
    premise_id="agrees",
    claim_ref="fixture C1",
    decision_obligation="whether the two coordinates of the case agree",
    decided_from=("left", "right"),
    domain=(False, True),
)

SUPPLIED = Premise(
    premise_id="ambiguous",
    claim_ref="fixture C2",
    decision_obligation="whether the admissible completions disagree on the obligation",
    decided_from=("left", "right"),
    domain=(False, True),
)

UNMODELLED = Premise(
    premise_id="ambiguous",
    claim_ref="fixture C2",
    decision_obligation="whether the admissible completions disagree on the obligation",
    decided_from=("admissible_completions",),
    domain=(False, True),
)

DEFINITION = "the four enumerated cases; each may exclude a value of the premise"


def _deciding_replay(assignment):
    """A check that pins the premise: it asserts the premise equals a case property."""

    for case in CASES:
        assert bool(assignment(case)) == (case["left"] == case["right"])
    return True


def _supplying_replay(assignment):
    """A check that asserts the terminal matching whichever value it is handed.

    Every value of the premise satisfies it, which is exactly what makes the
    case count uninformative about the premise.
    """

    for case in CASES:
        expected = "REOPEN" if assignment(case) else "CANNOT_CHECK"
        terminal = "REOPEN" if assignment(case) else "CANNOT_CHECK"
        assert terminal == expected
        assert case["left"] in (False, True)
    return True


def _measure(premise, replay, *, baseline=lambda case: True, cases=CASES):
    return measure_decision_constraint(
        premise,
        check_id="fixture_check",
        cases=cases,
        replay=replay,
        baseline=baseline,
        opportunity_definition=DEFINITION,
    )


def test_a_premise_the_check_pins_down_passes() -> None:
    constraint = _measure(DECIDED, _deciding_replay, baseline=lambda c: c["left"] == c["right"])

    assert constraint.outcome is Outcome.PASS
    assert constraint.reason is DecisionReason.DECIDED_ON_EVERY_CASE
    assert constraint.free_case_ids == ()
    assert len(constraint.decided_case_ids) == 4
    assert constraint.admissible_assignments == 1
    assert not constraint.blocks


def test_a_supplied_premise_fails_and_reports_how_many_rules_survive() -> None:
    constraint = _measure(SUPPLIED, _supplying_replay)

    assert constraint.outcome is Outcome.FAIL
    assert constraint.reason is DecisionReason.PREMISE_SUPPLIED
    assert len(constraint.free_case_ids) == 4
    # Two values free on each of four independent cases.
    assert constraint.admissible_assignments == 2**4
    assert "supplies it rather than deciding it" in constraint.detail


def test_a_premise_the_model_cannot_express_is_cannot_check_not_fail() -> None:
    """Supplied-but-decidable and undecidable-here are different repairs."""

    constraint = _measure(UNMODELLED, _supplying_replay)

    assert constraint.outcome is Outcome.CANNOT_CHECK
    assert constraint.reason is DecisionReason.UNDECIDABLE_IN_MODEL
    assert constraint.modelled is False
    assert "is not an axis" in constraint.detail
    assert constraint.blocks


def test_an_empty_case_space_blocks_rather_than_passing() -> None:
    constraint = _measure(SUPPLIED, _supplying_replay, cases=())

    assert constraint.outcome is Outcome.CANNOT_CHECK
    assert constraint.reason is DecisionReason.NO_CASES_ENUMERATED
    assert constraint.exercise.opportunities == 0
    assert constraint.admissible_assignments == 0


def test_a_replay_that_rejects_the_shipped_behaviour_is_refused() -> None:
    """Reading a verdict from a broken transcription credits the instrument's own bug."""

    def always_rejects(assignment):
        del assignment
        raise AssertionError("transcription does not match the artifact")

    constraint = _measure(SUPPLIED, always_rejects)

    assert constraint.outcome is Outcome.CANNOT_CHECK
    assert constraint.reason is DecisionReason.BASELINE_REJECTED


def test_an_interpreter_error_is_not_a_decision() -> None:
    """A rule refused by Python was not refused by the claim."""

    def type_error(assignment):
        assignment(CASES[0])
        raise TypeError("boundary error, not a decision")

    with pytest.raises(TypeError):
        _measure(SUPPLIED, type_error)


def test_duplicate_cases_are_refused() -> None:
    with pytest.raises(ValueError, match="not distinct"):
        _measure(SUPPLIED, _supplying_replay, cases=(CASES[0], CASES[0]))


def test_pass_cannot_be_paired_with_a_vacuity_reason() -> None:
    constraint = _measure(DECIDED, _deciding_replay, baseline=lambda c: c["left"] == c["right"])

    with pytest.raises(ValueError, match="cannot yield PASS"):
        DecisionConstraint(
            premise=constraint.premise,
            check_id=constraint.check_id,
            cases=constraint.cases,
            modelled=True,
            exercise=constraint.exercise,
            outcome=Outcome.PASS,
            reason=DecisionReason.NO_CASES_ENUMERATED,
            detail="",
        )


def test_pass_cannot_be_paired_with_a_free_case() -> None:
    free = CaseAdmissibility(
        case_id="left=False right=False",
        baseline_value=True,
        admissible=(False, True),
        domain_size=2,
    )
    constraint = _measure(DECIDED, _deciding_replay, baseline=lambda c: c["left"] == c["right"])

    with pytest.raises(ValueError, match="leave the premise free"):
        DecisionConstraint(
            premise=constraint.premise,
            check_id=constraint.check_id,
            cases=(free,),
            modelled=True,
            exercise=constraint.exercise,
            outcome=Outcome.PASS,
            reason=DecisionReason.DECIDED_ON_EVERY_CASE,
            detail="",
        )


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"premise_id": " "}, "premise id is required"),
        ({"claim_ref": ""}, "name the claim"),
        ({"decision_obligation": "  "}, "state what this premise must be decided from"),
        ({"decided_from": ()}, "decided_from must name the inputs"),
        ({"domain": (True,)}, "decides nothing"),
    ],
)
def test_a_premise_must_state_its_decision(kwargs, message) -> None:
    fields = {
        "premise_id": "p",
        "claim_ref": "C1",
        "decision_obligation": "what it reads",
        "decided_from": ("left",),
        "domain": (False, True),
    }
    fields.update(kwargs)
    with pytest.raises(ValueError, match=message):
        Premise(**fields)


def test_an_admissibility_must_contain_its_baseline() -> None:
    with pytest.raises(ValueError, match="baseline value must be admissible"):
        CaseAdmissibility(
            case_id="c", baseline_value=True, admissible=(False,), domain_size=2
        )


def test_require_decided_names_both_kinds_of_missing_decision() -> None:
    supplied = _measure(SUPPLIED, _supplying_replay)
    unmodelled = _measure(UNMODELLED, _supplying_replay)

    with pytest.raises(UndecidedPremise) as excinfo:
        require_decided((supplied, unmodelled), label="fixture")

    message = str(excinfo.value)
    assert "supplied to the check rather than decided by it" in message
    assert "cannot be decided in this model at all" in message
    assert "16 deciding rules admissible" in message


def test_require_decided_is_silent_when_every_premise_was_decided() -> None:
    decided = _measure(DECIDED, _deciding_replay, baseline=lambda c: c["left"] == c["right"])

    require_decided((decided,), label="fixture")


def test_decision_outcome_is_non_compensatory_and_refuses_an_empty_set() -> None:
    decided = _measure(DECIDED, _deciding_replay, baseline=lambda c: c["left"] == c["right"])
    supplied = _measure(SUPPLIED, _supplying_replay)
    unmodelled = _measure(UNMODELLED, _supplying_replay)

    assert decision_outcome((decided,)) is Outcome.PASS
    assert decision_outcome((decided, unmodelled)) is Outcome.CANNOT_CHECK
    assert decision_outcome((decided, unmodelled, supplied)) is Outcome.FAIL
    with pytest.raises(UndecidedPremise):
        decision_outcome(())


def test_a_result_refuses_to_hold_a_count_over_a_supplied_premise() -> None:
    supplied = _measure(SUPPLIED, _supplying_replay)

    with pytest.raises(UndecidedPremise, match="cannot report"):
        DecidedResult(
            result_id="fixture-theorem",
            reported=(("cases", 4),),
            constraints=(supplied,),
        )


def test_a_result_over_a_decided_premise_is_constructible() -> None:
    decided = _measure(DECIDED, _deciding_replay, baseline=lambda c: c["left"] == c["right"])

    result = DecidedResult(
        result_id="fixture-theorem", reported=(("cases", 4),), constraints=(decided,)
    )

    assert result.as_json()["reported"] == {"cases": 4}
    with pytest.raises(ValueError, match="must carry the decision constraints"):
        DecidedResult(result_id="fixture-theorem", reported=(("cases", 4),), constraints=())


def test_case_label_is_stable_and_order_independent() -> None:
    assert case_label({"right": True, "left": False}) == "left=False right=True"


def test_sampling_whole_rules_backs_the_single_point_count() -> None:
    """The exact admissible-assignment count assumes the assertions factorise."""

    accepted, trials = sample_assignments_accepted(
        SUPPLIED, cases=CASES, replay=_supplying_replay, trials=200
    )

    assert (accepted, trials) == (200, 200)


def test_sampling_finds_the_coupling_a_single_point_sweep_cannot() -> None:
    """A check that couples cases is free at every point and rejects joint rules."""

    def coupled(assignment):
        # Satisfied by the all-True and all-False rules and by nothing between,
        # so every single-case perturbation of an all-True baseline is accepted.
        values = [bool(assignment(case)) for case in CASES]
        assert len(set(values)) == 1 or sum(values) >= len(values) - 1
        return True

    constraint = _measure(SUPPLIED, coupled)
    accepted, trials = sample_assignments_accepted(
        SUPPLIED, cases=CASES, replay=coupled, trials=400
    )

    assert len(constraint.free_case_ids) == 4
    assert constraint.admissible_assignments == 16
    assert accepted < trials


def test_sampling_refuses_an_empty_trial_budget() -> None:
    with pytest.raises(ValueError, match="establishes nothing"):
        sample_assignments_accepted(SUPPLIED, cases=CASES, replay=_supplying_replay, trials=0)
