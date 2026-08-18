from __future__ import annotations

import pytest

from orion.self_orion.epistemic_control import (
    EpistemicControlStatus,
    compose_epistemic_control,
)
from orion.self_orion.revision_gate import assess_revision_gate
from orion.transfer.v2.epistemic_computation import (
    ComputationActionState,
    assess_computation_action,
    build_computation_action,
    select_epistemic_computation,
)
from orion.transfer.v2.epistemic_responsibility import (
    assess_responsibility,
    build_responsibility_hypothesis,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    ObligationState,
    assess_mechanic,
    build_mechanic,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceCheckState,
    assess_interface_adequacy,
    build_interface_check,
)
from orion.transfer.v2.social_evidence import (
    TruthfulnessState,
    assess_social_evidence_independence,
    build_social_evidence_record,
)
from orion.transfer.v2.uncertainty_containment import (
    ValidityState,
    assess_containment,
    build_validity_envelope,
)

CLAIM = "claim:t7"


def _responsibility(*, ambiguous: bool = False):
    left = build_responsibility_hypothesis(
        hypothesis_id="interface-gap",
        claim_id=CLAIM,
        expected_observations={"probe": ("INTERFACE",)},
        support_evidence_ids=("e:left",),
    )
    right = build_responsibility_hypothesis(
        hypothesis_id="model-gap",
        claim_id=CLAIM,
        expected_observations={"probe": ("INTERFACE",) if ambiguous else ("MODEL",)},
        support_evidence_ids=("e:right",),
    )
    return assess_responsibility((left, right), observed_outcomes={"probe": "INTERFACE"})


def _interface(state: InterfaceCheckState = InterfaceCheckState.PASS):
    return assess_interface_adequacy(
        (
            build_interface_check(
                check_id="frame",
                scope="F",
                state=state,
                evidence_ids=("e:frame",),
                required=True,
            ),
        )
    )


def _revision_candidate():
    responsibility = _responsibility()
    interface = _interface()
    narrow = build_mechanic(
        mechanic_id="repair-interface",
        claim_id=CLAIM,
        kind="INTERFACE_REPAIR",
        write_coordinates=("F",),
        hard_requirements=("diagnostic",),
        preservation_obligations=("preserve:M",),
    )
    broad = build_mechanic(
        mechanic_id="rewrite-model",
        claim_id=CLAIM,
        kind="MODEL_REVISION",
        write_coordinates=("F", "M"),
        hard_requirements=("diagnostic",),
    )
    mechanics = (narrow, broad)
    assessments = tuple(
        assess_mechanic(item, obligation_states={"diagnostic": ObligationState.SATISFIED})
        for item in mechanics
    )
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("repair-interface", "rewrite-model")},
        interface_repair_mechanic_ids=("repair-interface",),
        interface_coordinates=("F",),
    )


def _revision_unresolved():
    responsibility = _responsibility(ambiguous=True)
    interface = _interface()
    mechanic = build_mechanic(
        mechanic_id="candidate",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("M",),
    )
    assessment = assess_mechanic(mechanic, obligation_states={})
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=(mechanic,),
        assessments=(assessment,),
        responsibility_bindings={"interface-gap": ("candidate",), "model-gap": ("candidate",)},
    )


def _revision_multiple():
    responsibility = _responsibility()
    interface = _interface()
    left = build_mechanic(
        mechanic_id="left",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("M",),
        preservation_obligations=("preserve:F",),
    )
    right = build_mechanic(
        mechanic_id="right",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("Q",),
        preservation_obligations=("preserve:F",),
    )
    mechanics = (left, right)
    assessments = tuple(assess_mechanic(item, obligation_states={}) for item in mechanics)
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=mechanics,
        assessments=assessments,
        responsibility_bindings={"interface-gap": ("left", "right")},
    )


def _revision_no_admissible():
    responsibility = _responsibility()
    interface = _interface()
    mechanic = build_mechanic(
        mechanic_id="blocked",
        claim_id=CLAIM,
        kind="REVISION",
        write_coordinates=("M",),
        hard_requirements=("required",),
    )
    assessment = assess_mechanic(
        mechanic,
        obligation_states={"required": ObligationState.VIOLATED},
    )
    return assess_revision_gate(
        responsibility=responsibility,
        interface=interface,
        mechanics=(mechanic,),
        assessments=(assessment,),
        responsibility_bindings={"interface-gap": ("blocked",)},
    )


def _computation(*, hard: bool = False, optional_value: float = 5.0, blocked: bool = False):
    action = build_computation_action(
        action_id="verify" if hard else "diagnose",
        claim_id=CLAIM,
        kind="VERIFY" if hard else "DIAGNOSE",
        expected_decision_value=0.0 if hard else optional_value,
        cost=1.0,
        hard_requirements=("ready",) if blocked else (),
        discharges_obligations=("must-verify",) if hard else (),
    )
    assessment = assess_computation_action(
        action,
        requirement_states={"ready": ComputationActionState.VIOLATED} if blocked else {},
    )
    return select_epistemic_computation(
        (action,),
        (assessment,),
        active_hard_obligations=("must-verify",) if hard else (),
    )


def _local_stop_computation():
    action = build_computation_action(
        action_id="wait",
        claim_id=CLAIM,
        kind="WAIT",
        expected_decision_value=1.0,
        cost=1.0,
    )
    assessment = assess_computation_action(action, requirement_states={})
    return select_epistemic_computation((action,), (assessment,))


def _containment(state: ValidityState, *, claim: str = CLAIM):
    envelope = build_validity_envelope(
        envelope_id="env:t7",
        claim_id=claim,
        subject_id="subject:t7",
        context_states={"current": state},
        evidence_ids=("e:validity",),
    )
    return assess_containment(envelope, context_id="current")


def _social(*, correlated: bool):
    left = build_social_evidence_record(
        report_id="r1",
        agent_id="a",
        claim_id=CLAIM,
        direct_observation_ids=("oa",),
        upstream_source_ids=("shared" if correlated else "sa",),
        truthfulness_state=TruthfulnessState.SATISFIED,
    )
    right = build_social_evidence_record(
        report_id="r2",
        agent_id="b",
        claim_id=CLAIM,
        direct_observation_ids=("ob",),
        upstream_source_ids=("shared" if correlated else "sb",),
        truthfulness_state=TruthfulnessState.SATISFIED,
    )
    return assess_social_evidence_independence((left, right))


def test_hard_computation_preempts_selectable_revision() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_computation(hard=True),
    )
    assert report.status is EpistemicControlStatus.COMPUTATION_REQUIRED
    assert report.selected_computation_action_id == "verify"
    assert report.selected_revision_mechanic_id is None


def test_revision_candidate_beats_optional_positive_compute() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_computation(optional_value=100.0),
    )
    assert report.status is EpistemicControlStatus.REVISION_CANDIDATE
    assert report.selected_revision_mechanic_id == "repair-interface"
    assert report.selected_computation_action_id is None


def test_unresolved_revision_can_recommend_optional_diagnostic() -> None:
    report = compose_epistemic_control(
        revision=_revision_unresolved(),
        computation=_computation(optional_value=5.0),
    )
    assert report.status is EpistemicControlStatus.COMPUTATION_RECOMMENDED
    assert report.selected_computation_action_id == "diagnose"


def test_invalid_containment_blocks_revision_candidate() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_local_stop_computation(),
        containment=_containment(ValidityState.INVALID),
    )
    assert report.status is EpistemicControlStatus.CONTAINED
    assert report.selected_revision_mechanic_id is None


def test_unresolved_containment_fails_closed() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_local_stop_computation(),
        containment=_containment(ValidityState.UNRESOLVED),
    )
    assert report.status is EpistemicControlStatus.UNRESOLVED


def test_correlated_required_social_evidence_blocks_revision() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_local_stop_computation(),
        social_evidence=(_social(correlated=True),),
        require_independent_social_evidence=True,
    )
    assert report.status is EpistemicControlStatus.SOCIAL_EVIDENCE_REQUIRED
    assert report.selected_revision_mechanic_id is None


def test_independent_required_social_evidence_allows_revision() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_local_stop_computation(),
        social_evidence=(_social(correlated=False),),
        require_independent_social_evidence=True,
    )
    assert report.status is EpistemicControlStatus.REVISION_CANDIDATE


def test_multiple_revision_minima_remain_ambiguous() -> None:
    report = compose_epistemic_control(
        revision=_revision_multiple(),
        computation=_computation(optional_value=100.0),
    )
    assert report.status is EpistemicControlStatus.REVISION_AMBIGUOUS
    assert report.selected_computation_action_id is None


def test_local_compute_stop_never_grants_global_task_stop() -> None:
    report = compose_epistemic_control(
        revision=_revision_unresolved(),
        computation=_local_stop_computation(),
    )
    assert report.status is EpistemicControlStatus.LOCAL_COMPUTATION_STOP
    assert report.grants_global_task_stop_authority is False
    assert report.grants_scientific_authority is False


def test_no_admissible_revision_and_no_admissible_compute() -> None:
    report = compose_epistemic_control(
        revision=_revision_no_admissible(),
        computation=_computation(blocked=True),
    )
    assert report.status is EpistemicControlStatus.NO_ADMISSIBLE_ACTION


def test_cross_claim_containment_is_rejected() -> None:
    with pytest.raises(ValueError, match="claim-relative"):
        compose_epistemic_control(
            revision=_revision_candidate(),
            computation=_local_stop_computation(),
            containment=_containment(ValidityState.SUPPORTED, claim="claim:other"),
        )


def test_every_control_decision_is_non_authorizing() -> None:
    report = compose_epistemic_control(
        revision=_revision_candidate(),
        computation=_local_stop_computation(),
    )
    assert report.grants_scientific_authority is False
    assert report.grants_revision_authority is False
    assert report.grants_adoption_authority is False
    assert report.grants_promotion_authority is False
    assert report.grants_merge_authority is False
    assert report.grants_global_task_stop_authority is False
