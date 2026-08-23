from __future__ import annotations

from orion_research_harness.ocme_runtime import (
    LowerLevelResult,
    MethodEdit,
    OCMEEpisode,
    OCMETerminal,
    ObstructionCertificate,
    ObstructionKind,
    OutsideClosureVerification,
    REQUIRED_LOWER_LEVEL_ROUTE_KINDS,
    TransferEvidence,
    assess_ocme_episode,
)


def _lower(check_id: str, *, succeeded: bool = False) -> LowerLevelResult:
    return LowerLevelResult(
        check_id=check_id,
        route_kind=check_id,
        succeeded=succeeded,
        evidence_ids=(f"e:{check_id}",),
    )


def _valid_obstruction() -> ObstructionCertificate:
    return ObstructionCertificate(
        certificate_id="obs:1",
        kind=ObstructionKind.EXACT_FINITE_NONREACHABILITY,
        target_id="target:1",
        old_closure_ids=("m:a", "m:b"),
        evidence_ids=("e:obs",),
        independently_verified=True,
        all_registered_baselines_exhausted=True,
        timeout_only=False,
    )


def _base(**changes) -> OCMEEpisode:
    values = dict(
        episode_id="ocme:1",
        problem_model_frozen=True,
        verifier_available=True,
        access_model_frozen=True,
        resource_model_frozen=True,
        lower_level_results=tuple(_lower(route) for route in REQUIRED_LOWER_LEVEL_ROUTE_KINDS),
        obstruction=_valid_obstruction(),
        candidate_edit=None,
        outside_closure=None,
        transfer=None,
        problem_solving_gain=True,
        donor_same_reach=False,
        independent_reproduction=False,
    )
    values.update(changes)
    return OCMEEpisode(**values)


def test_timeout_or_failed_trace_alone_is_not_an_obstruction_certificate():
    obstruction = ObstructionCertificate(
        certificate_id="obs:timeout",
        kind=ObstructionKind.RESOURCE_BOUNDED_OBSTRUCTION,
        target_id="target:1",
        old_closure_ids=("m:a",),
        evidence_ids=("e:timeout",),
        independently_verified=True,
        all_registered_baselines_exhausted=False,
        timeout_only=True,
    )
    decision = assess_ocme_episode(_base(obstruction=obstruction))
    assert decision.terminal is OCMETerminal.CANNOT_CHECK
    assert decision.jump_open is False
    assert "timeout" in " ".join(decision.reasons).lower()


def test_lower_level_success_closes_method_language_escalation():
    results = list(_base().lower_level_results)
    index = REQUIRED_LOWER_LEVEL_ROUTE_KINDS.index("REPRESENTATION_REPAIR")
    results[index] = _lower("REPRESENTATION_REPAIR", succeeded=True)
    decision = assess_ocme_episode(_base(lower_level_results=tuple(results)))
    assert decision.terminal is OCMETerminal.OCME_LOWER_LEVEL_CAUSE
    assert decision.jump_open is False


def test_verified_obstruction_opens_jump_but_does_not_self_authorize_invention():
    decision = assess_ocme_episode(_base())
    assert decision.terminal is OCMETerminal.CANNOT_CHECK
    assert decision.jump_open is True
    assert decision.grants_scientific_authority is False
    assert decision.grants_novelty_authority is False


def test_known_composition_alias_is_rejected_as_method_expansion():
    edit = MethodEdit(
        edit_id="edit:macro",
        semantic_operator_ids=("m:a", "m:b"),
        claimed_new_reach_ids=("target:1",),
        expands_to_old_closure=True,
        access_model_ids=("access:v1",),
    )
    outside = OutsideClosureVerification(
        verification_id="outside:1",
        edit_id=edit.edit_id,
        verifier_id="independent:checker",
        candidate_issuer_id="candidate:generator",
        outside_old_closure=False,
        evidence_ids=("e:outside",),
    )
    decision = assess_ocme_episode(_base(candidate_edit=edit, outside_closure=outside))
    assert decision.terminal is not OCMETerminal.OCME_METHOD_EXPANSION_SUPPORTED
    assert decision.edit_disposition == "KNOWN_COMPOSITION"


def test_candidate_cannot_self_certify_outside_closure():
    edit = MethodEdit(
        edit_id="edit:new",
        semantic_operator_ids=("m:new",),
        claimed_new_reach_ids=("target:1",),
        expands_to_old_closure=False,
        access_model_ids=("access:v1",),
    )
    outside = OutsideClosureVerification(
        verification_id="outside:self",
        edit_id=edit.edit_id,
        verifier_id="candidate:generator",
        candidate_issuer_id="candidate:generator",
        outside_old_closure=True,
        evidence_ids=("e:self",),
    )
    decision = assess_ocme_episode(_base(candidate_edit=edit, outside_closure=outside))
    assert decision.terminal is OCMETerminal.CANNOT_CHECK
    assert decision.jump_open is True


def test_hidden_access_model_widening_blocks_expansion():
    edit = MethodEdit(
        edit_id="edit:new",
        semantic_operator_ids=("m:new",),
        claimed_new_reach_ids=("target:1",),
        expands_to_old_closure=False,
        access_model_ids=("access:v2",),
    )
    outside = OutsideClosureVerification(
        verification_id="outside:1",
        edit_id=edit.edit_id,
        verifier_id="independent:checker",
        candidate_issuer_id="candidate:generator",
        outside_old_closure=True,
        evidence_ids=("e:outside",),
    )
    transfer = TransferEvidence(
        held_out_ids=("held:1",),
        positive_transfer_ids=("held:1",),
        frozen_access_model_ids=("access:v1",),
        false_expansion_rate=0.0,
        false_expansion_guard=0.05,
        semantic_preservation=True,
        strong_baseline_same_reach=False,
        evidence_ids=("e:transfer",),
    )
    decision = assess_ocme_episode(
        _base(
            candidate_edit=edit,
            outside_closure=outside,
            transfer=transfer,
            independent_reproduction=True,
        )
    )
    assert decision.terminal is OCMETerminal.CANNOT_CHECK


def test_donor_same_reach_yields_donor_subsumed_not_invention():
    edit = MethodEdit(
        edit_id="edit:new",
        semantic_operator_ids=("m:new",),
        claimed_new_reach_ids=("target:1",),
        expands_to_old_closure=False,
        access_model_ids=("access:v1",),
    )
    outside = OutsideClosureVerification(
        verification_id="outside:1",
        edit_id=edit.edit_id,
        verifier_id="independent:checker",
        candidate_issuer_id="candidate:generator",
        outside_old_closure=True,
        evidence_ids=("e:outside",),
    )
    transfer = TransferEvidence(
        held_out_ids=("held:1",),
        positive_transfer_ids=("held:1",),
        frozen_access_model_ids=("access:v1",),
        false_expansion_rate=0.0,
        false_expansion_guard=0.05,
        semantic_preservation=True,
        strong_baseline_same_reach=True,
        evidence_ids=("e:transfer",),
    )
    decision = assess_ocme_episode(
        _base(
            candidate_edit=edit,
            outside_closure=outside,
            transfer=transfer,
            donor_same_reach=True,
            independent_reproduction=True,
        )
    )
    assert decision.terminal is OCMETerminal.OCME_DONOR_SUBSUMED


def test_complete_independent_outside_closure_transfer_can_support_method_expansion():
    edit = MethodEdit(
        edit_id="edit:new",
        semantic_operator_ids=("m:new",),
        claimed_new_reach_ids=("target:1", "held:1"),
        expands_to_old_closure=False,
        access_model_ids=("access:v1",),
    )
    outside = OutsideClosureVerification(
        verification_id="outside:1",
        edit_id=edit.edit_id,
        verifier_id="independent:checker",
        candidate_issuer_id="candidate:generator",
        outside_old_closure=True,
        evidence_ids=("e:outside",),
    )
    transfer = TransferEvidence(
        held_out_ids=("held:1", "held:2"),
        positive_transfer_ids=("held:1",),
        frozen_access_model_ids=("access:v1",),
        false_expansion_rate=0.01,
        false_expansion_guard=0.05,
        semantic_preservation=True,
        strong_baseline_same_reach=False,
        evidence_ids=("e:transfer",),
    )
    decision = assess_ocme_episode(
        _base(
            candidate_edit=edit,
            outside_closure=outside,
            transfer=transfer,
            independent_reproduction=True,
        )
    )
    assert decision.terminal is OCMETerminal.OCME_METHOD_EXPANSION_SUPPORTED
    assert decision.jump_open is True
    assert decision.grants_scientific_authority is False
    assert decision.grants_novelty_authority is False
