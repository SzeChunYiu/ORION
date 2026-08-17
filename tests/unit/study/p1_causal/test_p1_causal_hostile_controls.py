"""Hostile controls: gold leak, probe-as-authority, known-answer selectivity."""

from __future__ import annotations

from orion.study.p1_causal.belief import AuthorityClass, uniform_unresolved
from orion.study.p1_causal.campaign import live_campaign_status
from orion.study.p1_causal.cases import known_answer_bundles
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
    for bundle in bundles:
        publics = bundle.public_members()
        assert len(publics) >= 2
        stages = {bundle.gold_for(item.member_id).true_stage for item in publics}
        assert len(stages) == len(publics)
        symptoms = {item.shared_surface_symptoms for item in publics}
        assert len(symptoms) == 1
        for view in publics:
            assert "true_stage" not in view.to_payload()


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


def test_live_campaign_cannot_check_without_credential(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    status = live_campaign_status()
    assert status.status == "CANNOT_CHECK"
    assert status.credential_present is False
