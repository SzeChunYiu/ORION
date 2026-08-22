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


def _lower(route_kind: str) -> LowerLevelResult:
    return LowerLevelResult(
        check_id=f"check:{route_kind}",
        route_kind=route_kind,
        succeeded=False,
        evidence_ids=(f"e:{route_kind}",),
    )


def _obstruction() -> ObstructionCertificate:
    return ObstructionCertificate(
        certificate_id="obs:coverage",
        kind=ObstructionKind.EXACT_FINITE_NONREACHABILITY,
        target_id="target:coverage",
        old_closure_ids=("m:old",),
        evidence_ids=("e:obs",),
        independently_verified=True,
        all_registered_baselines_exhausted=True,
    )


def _positive_episode(*, lower_level_results) -> OCMEEpisode:
    edit = MethodEdit(
        edit_id="edit:new",
        semantic_operator_ids=("m:new",),
        claimed_new_reach_ids=("target:coverage", "held:1"),
        expands_to_old_closure=False,
        access_model_ids=("access:v1",),
    )
    outside = OutsideClosureVerification(
        verification_id="outside:coverage",
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
    return OCMEEpisode(
        episode_id="ocme:coverage",
        problem_model_frozen=True,
        verifier_available=True,
        access_model_frozen=True,
        resource_model_frozen=True,
        lower_level_results=tuple(lower_level_results),
        obstruction=_obstruction(),
        candidate_edit=edit,
        outside_closure=outside,
        transfer=transfer,
        problem_solving_gain=True,
        donor_same_reach=False,
        independent_reproduction=True,
    )


def test_empty_lower_level_ledger_cannot_open_ocme_jump_even_with_positive_obstruction_flags():
    decision = assess_ocme_episode(_positive_episode(lower_level_results=()))
    assert decision.terminal is OCMETerminal.CANNOT_CHECK
    assert decision.jump_open is False
    assert "first-right-of-refusal" in " ".join(decision.reasons).lower()


def test_missing_one_required_lower_level_route_cannot_open_ocme_jump():
    missing = REQUIRED_LOWER_LEVEL_ROUTE_KINDS[-1]
    ledger = tuple(
        _lower(route_kind)
        for route_kind in REQUIRED_LOWER_LEVEL_ROUTE_KINDS
        if route_kind != missing
    )
    decision = assess_ocme_episode(_positive_episode(lower_level_results=ledger))
    assert decision.terminal is OCMETerminal.CANNOT_CHECK
    assert decision.jump_open is False
    assert missing in " ".join(decision.reasons)


def test_full_eight_route_first_right_of_refusal_still_allows_positive_ocme_terminal():
    ledger = tuple(_lower(route_kind) for route_kind in REQUIRED_LOWER_LEVEL_ROUTE_KINDS)
    decision = assess_ocme_episode(_positive_episode(lower_level_results=ledger))
    assert decision.terminal is OCMETerminal.OCME_METHOD_EXPANSION_SUPPORTED
    assert decision.jump_open is True


def test_duplicate_lower_level_route_families_are_rejected_at_episode_construction():
    duplicate = (_lower("SEARCH_MORE"), LowerLevelResult(
        check_id="check:search-more:2",
        route_kind="SEARCH_MORE",
        succeeded=False,
        evidence_ids=("e:search-more:2",),
    ))
    try:
        _positive_episode(lower_level_results=duplicate)
    except ValueError as exc:
        assert "route" in str(exc).lower() and "unique" in str(exc).lower()
    else:  # pragma: no cover - hostile regression assertion
        raise AssertionError("duplicate lower-level route family was accepted")
