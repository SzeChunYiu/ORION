"""Hostile controls: gold leak, capability boundaries, and known-answer selectivity."""

from __future__ import annotations

from dataclasses import replace

import orion.study.p1_causal.controls as controls
from orion.study.p1_causal.belief import AuthorityClass, uniform_unresolved
from orion.study.p1_causal.campaign import live_campaign_status
from orion.study.p1_causal.cases import gold_leak, known_answer_bundles
from orion.study.p1_causal.controls import run_hostile_controls
from orion.study.p1_causal.discriminator import DEFAULT_PROBES, ProbeCatalog, ProbeSpec
from orion.study.p1_causal.engine import run_cycle
from orion.study.p1_causal.intervention import apply_probe
from orion.study.p1_causal.licensing import EpistemicAction, RefusalReason, request_action


def test_all_hostile_controls_pass() -> None:
    receipts = run_hostile_controls()
    failed = [item.to_payload() for item in receipts if not item.satisfied]
    assert failed == []


def test_probe_never_grants_mutating_authority() -> None:
    probe = ProbeSpec(
        probe_id="omitted_source_retrieval",
        cost=1,
        separates=(AuthorityClass.EVIDENCE, AuthorityClass.SEARCH_UNIVERSE),
    )
    updated = apply_probe(uniform_unresolved(), probe, AuthorityClass.SEARCH_UNIVERSE)
    assert updated.intervention_backed is False
    decision = request_action(updated, EpistemicAction.EXPAND_SEARCH_UNIVERSE)
    assert decision.granted is False
    assert decision.refusal is RefusalReason.NOT_INTERVENTION_BACKED


def test_known_answer_pairs_share_surface_and_differ_in_gold() -> None:
    bundles = known_answer_bundles()
    assert bundles
    protected_id_tokens = {
        "evidence",
        "execution",
        "formulation",
        "search-universe",
        "search_universe",
        "retrieval",
        "implementation",
        "environment",
    }
    for bundle in bundles:
        publics = bundle.public_members()
        assert len(publics) >= 2
        stages = {bundle.gold_for(item.member_id).true_stage for item in publics}
        assert len(stages) == len(publics)
        symptoms = {item.shared_surface_symptoms for item in publics}
        assert len(symptoms) == 1
        for view in publics:
            payload = view.to_payload()
            assert "true_stage" not in payload
            assert "bundle_id" not in payload
            assert "confusable_kind" not in payload
            assert gold_leak(view) == ()
            lowered = view.member_id.lower()
            assert not any(token in lowered for token in protected_id_tokens)


def test_cycle_intervention_backs_correct_class() -> None:
    catalog = ProbeCatalog(DEFAULT_PROBES)
    bundle = known_answer_bundles()[0]
    for member in bundle.members:
        cycle = run_cycle(member.public, member.world, catalog=catalog)
        assert cycle.cannot_check is False
        assert cycle.state.intervention_backed is True
        assert cycle.state.authority_class is member.world.gold.true_stage
        granted = {item.action for item in cycle.decisions if item.granted}
        assert EpistemicAction.BROAD_WM_MUTATION not in granted
        assert EpistemicAction.REWRITE_METHOD not in granted


def test_cycle_does_not_fall_back_outside_probe_allowlist() -> None:
    member = known_answer_bundles()[0].members[1]
    restricted = replace(member.public, allowed_probe_ids=())
    cycle = run_cycle(restricted, member.world, catalog=ProbeCatalog(DEFAULT_PROBES))
    assert cycle.state.authority_class is AuthorityClass.UNRESOLVED
    assert cycle.cannot_check is True
    assert not any(note.startswith("ran_probe:") for note in cycle.notes)
    assert "no_separating_probe" in cycle.notes


def test_cycle_does_not_run_unadvertised_intervention() -> None:
    member = known_answer_bundles()[0].members[1]
    restricted = replace(member.public, allowed_intervention_ids=())
    cycle = run_cycle(restricted, member.world, catalog=ProbeCatalog(DEFAULT_PROBES))
    assert cycle.state.authority_class is AuthorityClass.SEARCH_UNIVERSE
    assert cycle.state.intervention_backed is False
    assert cycle.cannot_check is True
    assert "intervention_not_allowed:expand_active_domains" in cycle.notes
    assert not any(note.startswith("ran_intervention:") for note in cycle.notes)
    decision = next(
        item
        for item in cycle.decisions
        if item.action is EpistemicAction.EXPAND_SEARCH_UNIVERSE
    )
    assert decision.granted is False
    assert decision.refusal is RefusalReason.NOT_INTERVENTION_BACKED


def test_oracle_non_runnable_control_can_fail(monkeypatch) -> None:
    monkeypatch.setattr(
        controls,
        "load_protocol",
        lambda: {"baselines": [], "resource_policy": "oracle may be a candidate"},
    )
    receipt = controls._oracle_ceiling_not_a_candidate()
    assert receipt.satisfied is False
    assert "oracle_missing_from_frozen_baselines" in receipt.mismatches
    assert (
        "resource_policy_does_not_bind_oracle_nonrunnable_candidate_rule"
        in receipt.mismatches
    )


def test_oracle_policy_cannot_be_satisfied_by_unrelated_clause(monkeypatch) -> None:
    monkeypatch.setattr(
        controls,
        "load_protocol",
        lambda: {
            "baselines": ["oracle_diagnosis_ceiling_non_runnable"],
            "resource_policy": (
                "Oracle diagnosis may be used as a candidate. "
                "The random baseline is never a candidate."
            ),
        },
    )
    receipt = controls._oracle_ceiling_not_a_candidate()
    assert receipt.satisfied is False
    assert (
        "resource_policy_does_not_bind_oracle_nonrunnable_candidate_rule"
        in receipt.mismatches
    )


def test_live_campaign_cannot_check_without_credential(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    status = live_campaign_status()
    assert status.status == "CANNOT_CHECK"
    assert status.credential_present is False
