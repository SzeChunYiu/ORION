from __future__ import annotations

from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
    ComputationSelectionStatus,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)


def action(
    name: str,
    *,
    value: float,
    cost: float,
    requirements=(),
    discharges=(),
    authorities=(),
):
    return build_computation_action(
        action_id=name,
        claim_id="claim:compute",
        kind="CALLER_DECLARED",
        expected_decision_value=value,
        cost=cost,
        hard_requirements=requirements,
        discharges_obligations=discharges,
        required_authorities=authorities,
    )


def test_mandatory_verification_precedes_high_value_optional_reasoning() -> None:
    verify = action(
        "protected-verify",
        value=0.0,
        cost=2.0,
        discharges=("must-verify",),
        authorities=("protected-verifier",),
    )
    llm = action("call-llm", value=10.0, cost=1.0)
    assessments = (
        assess_computation_action(
            verify,
            requirement_states={},
            available_authorities=("protected-verifier",),
        ),
        assess_computation_action(llm, requirement_states={}),
    )

    report = select_epistemic_computation(
        (verify, llm),
        assessments,
        active_hard_obligations=("must-verify",),
    )

    assert report.status is ComputationSelectionStatus.SELECTED
    assert report.selected_action_id == "protected-verify"
    assert "HARD_OBLIGATION_PRECEDENCE" in report.reasons
    assert report.grants_scientific_authority is False
    assert report.grants_revision_authority is False


def test_optional_action_cannot_compensate_uncovered_hard_obligation() -> None:
    optional = action("plan", value=100.0, cost=1.0)
    assessment = assess_computation_action(optional, requirement_states={})

    report = select_epistemic_computation(
        (optional,),
        (assessment,),
        active_hard_obligations=("must-verify",),
    )

    assert report.status is ComputationSelectionStatus.NO_ADMISSIBLE
    assert report.selected_action_id is None
    assert "HARD_OBLIGATION_UNCOVERED:must-verify" in report.reasons


def test_unresolved_action_for_only_hard_obligation_keeps_selection_unresolved() -> None:
    verify = action(
        "verify",
        value=0.0,
        cost=1.0,
        requirements=("evidence-ready",),
        discharges=("must-verify",),
    )
    assessment = assess_computation_action(
        verify,
        requirement_states={"evidence-ready": ComputationActionState.UNRESOLVED},
    )

    report = select_epistemic_computation(
        (verify,),
        (assessment,),
        active_hard_obligations=("must-verify",),
    )

    assert report.status is ComputationSelectionStatus.UNRESOLVED
    assert report.selected_action_id is None


def test_equal_positive_net_actions_remain_multiple_optima() -> None:
    left = action("retrieve", value=4.0, cost=1.0)
    right = action("diagnose", value=5.0, cost=2.0)
    assessments = tuple(
        assess_computation_action(candidate, requirement_states={})
        for candidate in (left, right)
    )

    report = select_epistemic_computation((left, right), assessments)

    assert report.status is ComputationSelectionStatus.MULTIPLE_OPTIMA
    assert set(report.optimal_action_ids) == {"retrieve", "diagnose"}
    assert report.selected_action_id is None


def test_nonmandatory_nonpositive_actions_stop_local_computation() -> None:
    wait = action("wait", value=1.0, cost=1.0)
    plan = action("plan", value=1.0, cost=2.0)
    assessments = tuple(
        assess_computation_action(candidate, requirement_states={})
        for candidate in (wait, plan)
    )

    report = select_epistemic_computation((wait, plan), assessments)

    assert report.status is ComputationSelectionStatus.LOCAL_COMPUTATION_STOP
    assert report.selected_action_id is None


def test_missing_authority_blocks_computation_action() -> None:
    protected = action(
        "protected-test",
        value=100.0,
        cost=0.0,
        authorities=("external-host",),
    )
    assessment = assess_computation_action(protected, requirement_states={})

    assert assessment.status.value == "BLOCKED"
    assert "MISSING_AUTHORITY:external-host" in assessment.reasons
