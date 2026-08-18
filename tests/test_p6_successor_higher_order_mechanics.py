from dataclasses import replace

import pytest

from orion.transfer.v2.higher_order_epistemic_mechanics import (
    AssessmentStatus,
    ObligationState,
    SelectionStatus,
    assess_mechanic,
    build_mechanic,
    less_or_equal_invasiveness,
    select_minimal_admissible,
    strictly_less_invasive,
)


def _sat(*names: str):
    return {name: ObligationState.SATISFIED for name in names}


def test_narrower_revision_is_unique_minimum_when_both_are_admissible():
    evidence = build_mechanic(
        mechanic_id="acquire-missing-evidence",
        claim_id="C1",
        read_coordinates=("K",),
        write_coordinates=("K",),
        preconditions=("anomaly-observed",),
        hard_requirements=("source-route-available",),
        preservation_obligations=("preserve-model", "preserve-objective"),
        required_authorities=(),
        cost=1.0,
    )
    expand_model = build_mechanic(
        mechanic_id="expand-model-class",
        claim_id="C1",
        read_coordinates=("K", "M"),
        write_coordinates=("K", "M"),
        preconditions=("anomaly-observed",),
        hard_requirements=("model-class-inadequacy-supported",),
        preservation_obligations=("preserve-objective",),
        required_authorities=("MODEL_MUTATION",),
        cost=0.1,  # cheaper must not make the broader write less invasive
    )

    evidence_assessment = assess_mechanic(
        evidence,
        obligation_states=_sat("anomaly-observed", "source-route-available"),
    )
    model_assessment = assess_mechanic(
        expand_model,
        obligation_states=_sat(
            "anomaly-observed", "model-class-inadequacy-supported"
        ),
        granted_authorities=("MODEL_MUTATION",),
    )

    assert evidence_assessment.status is AssessmentStatus.ADMISSIBLE
    assert model_assessment.status is AssessmentStatus.ADMISSIBLE
    assert strictly_less_invasive(evidence, expand_model)
    assert not strictly_less_invasive(expand_model, evidence)

    receipt = select_minimal_admissible(
        (evidence, expand_model),
        (evidence_assessment, model_assessment),
    )
    assert receipt.status is SelectionStatus.UNIQUE_MINIMUM
    assert receipt.selected_mechanic_digest == evidence.digest
    assert receipt.minimal_mechanic_digests == (evidence.digest,)


def test_incomparable_minimal_revisions_are_not_arbitrarily_selected():
    repair_measurement = build_mechanic(
        mechanic_id="repair-measurement",
        claim_id="C2",
        write_coordinates=("F.measurement",),
        preservation_obligations=("preserve-model",),
        cost=1.0,
    )
    repair_execution = build_mechanic(
        mechanic_id="repair-execution",
        claim_id="C2",
        write_coordinates=("X.execution",),
        preservation_obligations=("preserve-model",),
        cost=1.0,
    )
    a = assess_mechanic(repair_measurement, obligation_states={})
    b = assess_mechanic(repair_execution, obligation_states={})

    assert not strictly_less_invasive(repair_measurement, repair_execution)
    assert not strictly_less_invasive(repair_execution, repair_measurement)

    receipt = select_minimal_admissible((repair_measurement, repair_execution), (a, b))
    assert receipt.status is SelectionStatus.MULTIPLE_MINIMA
    assert receipt.selected_mechanic_digest is None
    assert set(receipt.minimal_mechanic_digests) == {
        repair_measurement.digest,
        repair_execution.digest,
    }


def test_narrower_unresolved_candidate_blocks_broader_admissible_promotion():
    narrow = build_mechanic(
        mechanic_id="check-evidence-route",
        claim_id="C3",
        write_coordinates=("K",),
        hard_requirements=("route-status-known",),
        preservation_obligations=("preserve-model", "preserve-objective"),
        cost=1.0,
    )
    broad = build_mechanic(
        mechanic_id="rewrite-model",
        claim_id="C3",
        write_coordinates=("K", "M"),
        preservation_obligations=("preserve-objective",),
        required_authorities=("MODEL_MUTATION",),
        cost=1.0,
    )
    narrow_assessment = assess_mechanic(
        narrow,
        obligation_states={"route-status-known": ObligationState.UNRESOLVED},
    )
    broad_assessment = assess_mechanic(
        broad,
        obligation_states={},
        granted_authorities=("MODEL_MUTATION",),
    )

    assert narrow_assessment.status is AssessmentStatus.UNRESOLVED
    assert broad_assessment.status is AssessmentStatus.ADMISSIBLE
    assert strictly_less_invasive(narrow, broad)

    receipt = select_minimal_admissible(
        (narrow, broad), (narrow_assessment, broad_assessment)
    )
    assert receipt.status is SelectionStatus.UNRESOLVED
    assert receipt.selected_mechanic_digest is None
    assert "NARROWER_UNRESOLVED_CANDIDATE" in receipt.reasons


def test_violated_hard_requirement_blocks_and_unknown_requirement_stays_unresolved():
    mechanic = build_mechanic(
        mechanic_id="high-level-revision",
        claim_id="C4",
        hard_requirements=("lower-level-causes-excluded",),
        write_coordinates=("M",),
        cost=1.0,
    )

    blocked = assess_mechanic(
        mechanic,
        obligation_states={
            "lower-level-causes-excluded": ObligationState.VIOLATED,
        },
    )
    unresolved = assess_mechanic(
        mechanic,
        obligation_states={
            "lower-level-causes-excluded": ObligationState.UNRESOLVED,
        },
    )

    assert blocked.status is AssessmentStatus.BLOCKED
    assert "OBLIGATION_VIOLATED:lower-level-causes-excluded" in blocked.reasons
    assert unresolved.status is AssessmentStatus.UNRESOLVED
    assert "OBLIGATION_UNRESOLVED:lower-level-causes-excluded" in unresolved.reasons


def test_missing_authority_blocks_regardless_of_cost_or_other_evidence():
    mechanic = build_mechanic(
        mechanic_id="objective-revision",
        claim_id="C5",
        write_coordinates=("Q",),
        required_authorities=("OBJECTIVE_MUTATION",),
        cost=0.0,
    )
    receipt = assess_mechanic(mechanic, obligation_states={})
    assert receipt.status is AssessmentStatus.BLOCKED
    assert "AUTHORITY_MISSING:OBJECTIVE_MUTATION" in receipt.reasons


def test_forbidden_write_blocks_even_when_all_obligations_pass():
    mechanic = build_mechanic(
        mechanic_id="candidate-evaluator-edit",
        claim_id="C6",
        write_coordinates=("A.evaluator",),
        cost=0.0,
    )
    receipt = assess_mechanic(
        mechanic,
        obligation_states={},
        forbidden_writes=("A.evaluator",),
    )
    assert receipt.status is AssessmentStatus.BLOCKED
    assert "FORBIDDEN_WRITE:A.evaluator" in receipt.reasons


def test_cost_does_not_define_invasiveness():
    narrow_expensive = build_mechanic(
        mechanic_id="narrow-expensive",
        claim_id="C7",
        write_coordinates=("K",),
        preservation_obligations=("preserve-model",),
        cost=100.0,
    )
    broad_free = build_mechanic(
        mechanic_id="broad-free",
        claim_id="C7",
        write_coordinates=("K", "M"),
        cost=0.0,
    )
    assert strictly_less_invasive(narrow_expensive, broad_free)


def test_cross_claim_mechanics_are_not_ordered():
    left = build_mechanic(
        mechanic_id="left",
        claim_id="C8-a",
        write_coordinates=("K",),
        cost=1.0,
    )
    right = build_mechanic(
        mechanic_id="right",
        claim_id="C8-b",
        write_coordinates=("K", "M"),
        cost=1.0,
    )
    assert not less_or_equal_invasiveness(left, right)
    assert not strictly_less_invasive(left, right)


def test_digest_tampering_and_self_authorization_are_rejected():
    mechanic = build_mechanic(
        mechanic_id="bounded",
        claim_id="C9",
        write_coordinates=("K",),
        cost=1.0,
    )
    mechanic.verify()

    with pytest.raises(ValueError, match="digest"):
        replace(mechanic, digest="sha256:tampered").verify()

    with pytest.raises(ValueError, match="self-authorize"):
        replace(mechanic, can_self_authorize=True).verify()


def test_missing_obligation_state_fails_closed_to_unresolved():
    mechanic = build_mechanic(
        mechanic_id="needs-check",
        claim_id="C10",
        preconditions=("anomaly-observed",),
        hard_requirements=("discriminator-passed",),
        cost=1.0,
    )
    receipt = assess_mechanic(
        mechanic,
        obligation_states={"anomaly-observed": ObligationState.SATISFIED},
    )
    assert receipt.status is AssessmentStatus.UNRESOLVED
    assert "OBLIGATION_STATE_MISSING:discriminator-passed" in receipt.reasons
