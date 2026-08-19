from __future__ import annotations

from dataclasses import replace

import pytest

from orion.study.p10.a0_control import (
    ControllerArm,
    ProposalKind,
    Responsibility,
    build_case,
    candidate_packet,
    derive_responsibility,
    evaluate_controller,
    model_payload,
    predict,
    run_a0,
)


@pytest.mark.parametrize("responsibility", list(Responsibility))
def test_gold_is_derived_from_structure_not_stored_label(responsibility: Responsibility):
    case = build_case(responsibility, seed=f"gold-{responsibility.value}")
    assert derive_responsibility(case) is responsibility
    payload_text = repr(model_payload(case))
    assert responsibility.value not in payload_text
    assert "gold" not in payload_text.lower()
    assert "responsibility" not in payload_text.lower()


def test_fixed_candidate_packet_is_identical_in_kind_space_for_every_case():
    packets = []
    for responsibility in Responsibility:
        case = build_case(responsibility, seed=f"packet-{responsibility.value}")
        packet = candidate_packet(case)
        packets.append(tuple(sorted(candidate.kind for candidate in packet)))
        assert {candidate.kind for candidate in packet} == set(ProposalKind)
        assert len({candidate.candidate_id for candidate in packet}) == len(ProposalKind)
    assert len(set(packets)) == 1


def test_surface_reminting_changes_ids_not_structural_gold():
    first = build_case(Responsibility.LOCAL_REPAIR, seed="remint-a")
    second = build_case(Responsibility.LOCAL_REPAIR, seed="remint-b")
    assert first.world_id != second.world_id
    assert model_payload(first) != model_payload(second)
    assert derive_responsibility(first) is derive_responsibility(second) is Responsibility.LOCAL_REPAIR


def test_evaluator_only_mutation_does_not_change_model_payload():
    case = build_case(Responsibility.LOCAL_ACTION, seed="evaluator-only")
    changed = replace(case, evaluator_note="forged-hidden-note")
    assert model_payload(case) == model_payload(changed)
    assert derive_responsibility(case) == derive_responsibility(changed)


def test_dependency_control_handles_missing_evidence_but_not_representation_reframe():
    need = build_case(Responsibility.NEED_EVIDENCE, seed="dep-query")
    unresolved = build_case(Responsibility.UNRESOLVED, seed="dep-unresolved")
    reframe = build_case(Responsibility.REFRAME_REPRESENTATION, seed="dep-reframe")
    assert predict(ControllerArm.DEPENDENCY_SUPPORT_CONTROL, need).kind is ProposalKind.ACQUIRE_EVIDENCE
    assert predict(ControllerArm.DEPENDENCY_SUPPORT_CONTROL, unresolved).kind is ProposalKind.UNRESOLVED
    assert predict(ControllerArm.DEPENDENCY_SUPPORT_CONTROL, reframe).kind is not ProposalKind.REFRAME_REPRESENTATION


def test_symbolic_feasibility_handles_local_repair_and_reframe_but_not_query():
    local = build_case(Responsibility.LOCAL_ACTION, seed="sym-local")
    repair = build_case(Responsibility.LOCAL_REPAIR, seed="sym-repair")
    reframe = build_case(Responsibility.REFRAME_REPRESENTATION, seed="sym-reframe")
    need = build_case(Responsibility.NEED_EVIDENCE, seed="sym-query")
    assert predict(ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL, local).kind is ProposalKind.ACT
    assert predict(ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL, repair).kind is ProposalKind.LOCAL_REPAIR
    assert predict(ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL, reframe).kind is ProposalKind.REFRAME_REPRESENTATION
    assert predict(ControllerArm.SYMBOLIC_FEASIBILITY_CONTROL, need).kind is not ProposalKind.ACQUIRE_EVIDENCE


def test_donor_composed_and_orion_controls_are_candidate_order_invariant():
    case = build_case(Responsibility.REFRAME_REPRESENTATION, seed="order")
    for arm in (ControllerArm.DONOR_COMPOSED_CONTROL, ControllerArm.ORION_RESPONSIBILITY_CONTROL):
        first = predict(arm, case, order_seed="one")
        second = predict(arm, case, order_seed="two")
        assert first.kind is second.kind is ProposalKind.REFRAME_REPRESENTATION


def test_overreach_is_counted_when_reframe_is_chosen_on_narrow_repair_case():
    case = build_case(Responsibility.LOCAL_REPAIR, seed="overreach")
    record = evaluate_controller(case, ProposalKind.REFRAME_REPRESENTATION)
    assert record.correct is False
    assert record.unnecessary_reframe is True
    assert record.false_closure is False


def test_forced_action_on_missing_evidence_is_false_closure():
    case = build_case(Responsibility.NEED_EVIDENCE, seed="false-closure")
    record = evaluate_controller(case, ProposalKind.ACT)
    assert record.correct is False
    assert record.false_closure is True


def test_exact_a0_small_run_keeps_donor_sufficiency_visible():
    result = run_a0(seed="a0-smoke", cases_per_family=12)
    assert result["arms"]["DONOR_COMPOSED_CONTROL"]["accuracy"] == pytest.approx(1.0)
    assert result["arms"]["ORION_RESPONSIBILITY_CONTROL"]["accuracy"] == pytest.approx(1.0)
    assert result["arms"]["DONOR_COMPOSED_CONTROL"]["false_closure_rate"] == pytest.approx(0.0)
    assert result["arms"]["DONOR_COMPOSED_CONTROL"]["unnecessary_reframe_rate"] == pytest.approx(0.0)
    assert result["terminal"] == "P10_EXISTING_STRUCTURED_CONTROL_SUFFICIENT"
    assert result["scientific_authority"] == "NONE_BOUNDED_DIAGNOSTIC"
