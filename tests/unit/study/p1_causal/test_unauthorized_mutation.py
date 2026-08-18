"""Unauthorized mutation is blocked; UNRESOLVED never licenses W/M rewrite."""

from __future__ import annotations

import pytest

from orion.study.p1_causal.belief import (
    ALL_AUTHORITY_CLASSES,
    AuthorityClass,
    UnauthorizedBeliefMutation,
    replace_masses,
    uniform_unresolved,
)
from orion.study.p1_causal.licensing import (
    EpistemicAction,
    RefusalReason,
    UnauthorizedMutationError,
    apply_licensed_action,
    audit_matrix,
    request_action,
)


def test_unresolved_is_the_initial_state() -> None:
    state = uniform_unresolved()
    assert state.authority_class is AuthorityClass.UNRESOLVED
    assert state.diagnosable is False
    assert state.intervention_backed is False
    assert {item.class_id for item in state.supports} == set(ALL_AUTHORITY_CLASSES)


def test_unresolved_refuses_every_mutating_action() -> None:
    state = uniform_unresolved()
    for action in (
        EpistemicAction.REWRITE_FORMULATION,
        EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        EpistemicAction.REWRITE_METHOD,
        EpistemicAction.BROAD_WM_MUTATION,
    ):
        decision = request_action(state, action)
        assert decision.granted is False
        assert decision.mutates is True
        if action is EpistemicAction.REWRITE_METHOD:
            assert decision.refusal is RefusalReason.PROTECTED_METHOD
        elif action is EpistemicAction.BROAD_WM_MUTATION:
            assert decision.refusal is RefusalReason.BROAD_MUTATION_FORBIDDEN
        else:
            assert decision.refusal is RefusalReason.UNRESOLVED
            assert decision.cannot_check is True
        with pytest.raises(UnauthorizedMutationError):
            apply_licensed_action(state, action)


def test_unresolved_may_probe() -> None:
    decision = request_action(uniform_unresolved(), EpistemicAction.RUN_PROBE)
    assert decision.granted is True
    assert decision.mutates is False


def test_unresolved_cannot_be_marked_intervention_backed() -> None:
    state = uniform_unresolved()
    masses = {item: state.mass(item) for item in ALL_AUTHORITY_CLASSES}
    with pytest.raises(UnauthorizedBeliefMutation):
        replace_masses(state, masses, intervention_backed=True)


def test_evidence_cannot_rewrite_formulation_or_search() -> None:
    state = uniform_unresolved()
    masses = {item: 0.05 for item in ALL_AUTHORITY_CLASSES}
    masses[AuthorityClass.EVIDENCE] = 0.8
    diagnosed = replace_masses(
        state, masses, intervention_backed=True, intervention_ids=("i0",)
    )
    assert diagnosed.authority_class is AuthorityClass.EVIDENCE
    for action in (
        EpistemicAction.REWRITE_FORMULATION,
        EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        EpistemicAction.BROAD_WM_MUTATION,
    ):
        decision = request_action(diagnosed, action)
        assert decision.granted is False
        with pytest.raises(UnauthorizedMutationError):
            apply_licensed_action(diagnosed, action)
    acquire = request_action(diagnosed, EpistemicAction.ACQUIRE_EVIDENCE)
    assert acquire.granted is True


def test_matrix_audit_passes() -> None:
    assert audit_matrix() == ()
