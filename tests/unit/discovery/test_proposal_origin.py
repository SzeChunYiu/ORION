from __future__ import annotations

import pytest

from orion.discovery.proposal_origin import (
    DiscoveryCreditEvidence,
    DiscoveryCreditState,
    EditKind,
    ReducibilityState,
    TargetOracleAccess,
    build_proposal_origin,
    supplied_menu_is_outside_closure_candidate,
)


def _origin(**overrides):
    values = {
        "proposal_id": "p",
        "frozen_regime_id": "r0",
        "frozen_operator_grammar_id": "g0",
        "edit_kinds": (EditKind.METHOD_LANGUAGE_EDIT,),
        "generator_identity": "generator-v1",
        "generation_trace_ids": ("step-1", "step-2"),
        "validation_request_ids": ("hidden-consequence",),
        "target_oracle_access": TargetOracleAccess.NONE,
        "reducibility_state": ReducibilityState.OUTSIDE_REGISTERED_CLOSURE,
        "newly_constructed_primitive_ids": ("new-operator",),
        "reducibility_evidence_ids": ("old-closure-referee",),
    }
    values.update(overrides)
    return build_proposal_origin(**values)


def test_generated_nonreducible_candidate_can_enter_outside_closure_lane() -> None:
    origin = _origin()
    assert supplied_menu_is_outside_closure_candidate(origin)
    assert not origin.selected_from_supplied_menu_only
    assert not origin.grants_validity_authority
    assert not origin.grants_novelty_authority
    assert not origin.grants_adoption_authority


def test_supplied_menu_selection_does_not_earn_outside_closure_credit() -> None:
    origin = build_proposal_origin(
        proposal_id="menu-choice",
        frozen_regime_id="r0",
        frozen_operator_grammar_id="g0",
        edit_kinds=(EditKind.METHOD_LANGUAGE_EDIT,),
        generator_identity="selector",
        generation_trace_ids=("rank-menu",),
        validation_request_ids=("test",),
        target_oracle_access=TargetOracleAccess.NONE,
        reducibility_state=ReducibilityState.OLD_CLOSURE_EQUIVALENT,
        supplied_candidate_ids=("human-supplied-missing-method",),
    )
    assert origin.selected_from_supplied_menu_only
    assert not supplied_menu_is_outside_closure_candidate(origin)


def test_unmatched_target_oracle_cannot_support_outside_closure_record() -> None:
    with pytest.raises(ValueError, match="target-oracle"):
        _origin(target_oracle_access=TargetOracleAccess.DECLARED_UNMATCHED)


def test_discovery_credit_ladder_is_non_compensatory() -> None:
    proposal_only = DiscoveryCreditEvidence(
        proposal_origin_verified=True,
        old_regime_obstruction_verified=False,
        candidate_nonreducible_verified=False,
        protected_hidden_consequence_passed=True,
        held_out_transfer_passed=True,
        donor_first_refusal_survived=True,
        independent_validity_passed=True,
        external_novelty_and_adoption_passed=True,
    )
    assert proposal_only.maximum_state() is DiscoveryCreditState.PROPOSAL_RECORDED

    validated = DiscoveryCreditEvidence(
        proposal_origin_verified=True,
        old_regime_obstruction_verified=True,
        candidate_nonreducible_verified=True,
        protected_hidden_consequence_passed=True,
        held_out_transfer_passed=True,
        donor_first_refusal_survived=True,
        independent_validity_passed=True,
        external_novelty_and_adoption_passed=False,
    )
    assert validated.maximum_state() is DiscoveryCreditState.VALIDATED_RESIDUAL

    external = DiscoveryCreditEvidence(
        proposal_origin_verified=True,
        old_regime_obstruction_verified=True,
        candidate_nonreducible_verified=True,
        protected_hidden_consequence_passed=True,
        held_out_transfer_passed=True,
        donor_first_refusal_survived=True,
        independent_validity_passed=True,
        external_novelty_and_adoption_passed=True,
    )
    assert (
        external.maximum_state()
        is DiscoveryCreditState.EXTERNALLY_ADJUDICATED_NOVEL_DISCOVERY
    )


def test_cannot_check_reason_overrides_positive_flags() -> None:
    evidence = DiscoveryCreditEvidence(
        proposal_origin_verified=True,
        old_regime_obstruction_verified=True,
        candidate_nonreducible_verified=True,
        protected_hidden_consequence_passed=True,
        held_out_transfer_passed=True,
        donor_first_refusal_survived=True,
        independent_validity_passed=True,
        external_novelty_and_adoption_passed=True,
        cannot_check_reasons=("protected outcome unavailable",),
    )
    assert evidence.maximum_state() is DiscoveryCreditState.CANNOT_CHECK
