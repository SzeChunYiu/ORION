"""The three states a receipt's verdict can be in, and the two it must not pass in.

The emitters here are deliberately tiny. The instrument's own fidelity to P8's
shipped artifacts is pinned in ``tests/unit/study/p8/``; what is pinned here is
that a constant verdict beside a moving measurement returns ``FAIL``, and that a
register which never perturbed anything returns ``CANNOT_CHECK`` rather than the
pass its zero violations would otherwise buy.
"""

from __future__ import annotations

import pytest

from orion.programme.guard_exercise import GuardVerdictReason, worst_outcome
from orion.programme.records import Outcome
from orion.programme.terminal_responsiveness import (
    DeclaredBound,
    SelfIssuedAuthority,
    WithholdingCase,
    measure_declared_bound,
    measure_receipt_responsiveness,
    overridden,
    require_earned,
    require_responsive,
)


def responsive(payload: dict[str, object]) -> dict[str, object]:
    """An emitter whose verdict is computed from the rate it publishes."""

    rate = float(payload["rate"])
    return {"terminal": "CLEAR" if rate == 1.0 else "NOT_CLEAR", "accuracy": rate}


def unconditional(payload: dict[str, object]) -> dict[str, object]:
    """P8's shape: a live rate and a verdict that is a literal beside it."""

    return {"terminal": "CLEAR", "accuracy": float(payload["rate"])}


def _case(case_id: str, rate: float) -> WithholdingCase:
    return WithholdingCase(
        case_id=case_id,
        withholds=f"a suite scoring {rate} on its own panel is not clear",
        payload={"rate": rate},
    )


def _measure(emit, cases):
    return measure_receipt_responsiveness(
        emit,
        label="demo/terminal",
        baseline={"rate": 1.0},
        verdict_field="terminal",
        evidence_fields=("accuracy",),
        cases=cases,
    )


def test_verdict_that_tracks_the_measurement_passes():
    response = _measure(responsive, (_case("all-wrong", 0.0), _case("half-wrong", 0.5)))

    assert response.outcome is Outcome.PASS
    assert response.assessment.reason is GuardVerdictReason.HELD_UNDER_EXERCISE
    assert response.unmoved == ()
    assert response.contradicted == ()
    assert response.verdicts_observed == ("CLEAR", "NOT_CLEAR")
    assert response.exercise.opportunities == 2
    assert response.exercise.violations == 0


def test_constant_verdict_beside_a_moving_rate_fails_and_names_the_cases():
    response = _measure(unconditional, (_case("all-wrong", 0.0), _case("half-wrong", 0.5)))

    assert response.outcome is Outcome.FAIL
    assert response.assessment.reason is GuardVerdictReason.VIOLATED
    assert response.unmoved == ("all-wrong", "half-wrong")
    # The damning subset: the receipt's own number moved and its verdict did not.
    assert response.contradicted == ("all-wrong", "half-wrong")
    assert response.verdicts_observed == ("CLEAR",)
    assert response.blocks


def test_empty_register_cannot_check_rather_than_pass():
    response = _measure(unconditional, ())

    assert response.outcome is Outcome.CANNOT_CHECK
    assert response.assessment.reason is GuardVerdictReason.NEVER_EXERCISED
    assert response.assessment.reason.is_vacuity
    assert response.blocks


def test_register_that_perturbs_nothing_is_not_a_denominator():
    """A payload that reproduces the baseline receipt is an unapplied treatment."""

    response = _measure(unconditional, (_case("same-as-baseline", 1.0),))

    assert response.inert_cases == ("same-as-baseline",)
    assert response.exercise.opportunities == 0
    assert response.outcome is Outcome.CANNOT_CHECK
    assert response.contradicted == ()


def test_inert_cases_leave_the_denominator_and_live_ones_stay():
    response = _measure(unconditional, (_case("same-as-baseline", 1.0), _case("all-wrong", 0.0)))

    assert response.inert_cases == ("same-as-baseline",)
    assert response.exercise.opportunities == 1
    assert response.exercise.violations == 1
    assert response.outcome is Outcome.FAIL


def test_a_responsive_verdict_on_an_inert_case_is_still_not_counted():
    """The verdict moving on a payload the receipt ignored would be reading the payload."""

    def peeks(payload: dict[str, object]) -> dict[str, object]:
        return {"terminal": str(payload.get("label", "CLEAR")), "accuracy": 1.0}

    response = measure_receipt_responsiveness(
        peeks,
        label="demo/terminal",
        baseline={"rate": 1.0, "label": "CLEAR"},
        verdict_field="terminal",
        evidence_fields=("accuracy",),
        cases=(
            WithholdingCase(
                case_id="relabelled-only",
                withholds="the verdict must not turn on a label the payload carries",
                payload={"rate": 1.0, "label": "NOT_CLEAR"},
            ),
        ),
    )

    assert response.inert_cases == ()
    assert response.exercise.opportunities == 1
    assert response.outcome is Outcome.PASS


def test_worst_outcome_rolls_up_the_assessment():
    failing = _measure(unconditional, (_case("all-wrong", 0.0),))
    passing = _measure(responsive, (_case("all-wrong", 0.0),))

    assert worst_outcome((passing.assessment, failing.assessment)) is Outcome.FAIL


def test_require_responsive_raises_and_names_the_contradiction():
    response = _measure(unconditional, (_case("all-wrong", 0.0),))

    with pytest.raises(SelfIssuedAuthority) as error:
        require_responsive(response)
    assert "all-wrong" in str(error.value)
    assert "'terminal'" in str(error.value)

    require_responsive(_measure(responsive, (_case("all-wrong", 0.0),)))


def test_withholding_case_demands_an_id_and_a_reason():
    with pytest.raises(ValueError, match="id is required"):
        WithholdingCase(case_id=" ", withholds="because", payload={})
    with pytest.raises(ValueError, match="state why"):
        WithholdingCase(case_id="x", withholds="  ", payload={})


def test_duplicate_case_ids_are_refused():
    with pytest.raises(ValueError, match="distinct"):
        _measure(unconditional, (_case("dup", 0.0), _case("dup", 0.5)))


def test_verdict_cannot_be_its_own_evidence():
    with pytest.raises(ValueError, match="own evidence"):
        measure_receipt_responsiveness(
            unconditional,
            label="demo/terminal",
            baseline={"rate": 1.0},
            verdict_field="terminal",
            evidence_fields=("terminal",),
            cases=(_case("all-wrong", 0.0),),
        )


def test_absent_field_is_refused_rather_than_read_as_unmoved():
    with pytest.raises(ValueError, match="no field 'missing'"):
        measure_receipt_responsiveness(
            unconditional,
            label="demo/terminal",
            baseline={"rate": 1.0},
            verdict_field="missing",
            evidence_fields=("accuracy",),
            cases=(_case("all-wrong", 0.0),),
        )


def test_nested_field_is_refused_because_moving_is_not_a_verdict_change():
    def with_rows(payload: dict[str, object]) -> dict[str, object]:
        return {"terminal": "CLEAR", "rows": [payload["rate"]]}

    with pytest.raises(ValueError, match="trace scalar verdicts"):
        measure_receipt_responsiveness(
            with_rows,
            label="demo/terminal",
            baseline={"rate": 1.0},
            verdict_field="terminal",
            evidence_fields=("rows",),
            cases=(_case("all-wrong", 0.0),),
        )


def test_declared_bound_fails_when_the_input_supplies_it():
    def echoes(payload: dict[str, object]) -> dict[str, object]:
        return {"claim_ceiling": payload["claim_ceiling"]}

    bound = measure_declared_bound(
        echoes,
        label="demo/claim_ceiling",
        field="claim_ceiling",
        overreaching_payload={"claim_ceiling": "this proves everything"},
        overreaching_bound="this proves everything",
    )

    assert bound.subject_controlled
    assert bound.outcome is Outcome.FAIL
    assert bound.blocks
    with pytest.raises(SelfIssuedAuthority, match="chose its own ceiling"):
        require_earned(bound)


def test_declared_bound_passes_when_the_emitter_owns_it():
    def owns(_payload: dict[str, object]) -> dict[str, object]:
        return {"claim_ceiling": "bounded synthetic contract suite only"}

    bound = measure_declared_bound(
        owns,
        label="demo/claim_ceiling",
        field="claim_ceiling",
        overreaching_payload={"claim_ceiling": "this proves everything"},
        overreaching_bound="this proves everything",
    )

    assert not bound.subject_controlled
    assert bound.outcome is Outcome.PASS
    require_earned(bound)


def test_declared_bound_demands_a_label_and_a_field():
    with pytest.raises(ValueError, match="label is required"):
        DeclaredBound(label=" ", field="claim_ceiling", injected="a", emitted="b")
    with pytest.raises(ValueError, match="field is required"):
        DeclaredBound(label="demo", field="", injected="a", emitted="b")


def test_overridden_restores_even_when_the_emitter_raises():
    class Module:
        VALUE = "original"

    module = Module()
    with pytest.raises(RuntimeError):
        with overridden(module, VALUE="swapped"):
            assert module.VALUE == "swapped"
            raise RuntimeError("emitter blew up")
    assert module.VALUE == "original"
