from dataclasses import FrozenInstanceError

import pytest

from orion.knowledge.atlas_gluing import (
    AtlasChart,
    AtlasGluingTrial,
    AtlasGluingVerdict,
    CycleConsistencyWitness,
    GluingLayer,
    ObstructionType,
    OverlapTransition,
    TransitionVerdict,
    evaluate_atlas_gluing,
    validate_overlap_transition,
)
from orion.knowledge.generator_transport import AbstractionLevel


def _chart(chart_id: str) -> AtlasChart:
    return AtlasChart(chart_id, "apple-object", "what global theory describes q?", AbstractionLevel.L4, f"context-{chart_id}", ("registered-assumption",), ("shared-regime",), (f"evidence-{chart_id}",))


def _transition(source: str, target: str, *, transition_id=None, certified_layers=(GluingLayer.OBSERVATIONAL, GluingLayer.MECHANISTIC), context_alignment_passed=True, assumption_compatibility_passed=True, regime_overlap=("shared-regime",), transition_map_passed=True, preserved=("shared-relation",), not_preserved=("local-coordinate",), declared_before_outcomes=True):
    tid = transition_id or f"{source}-{target}"
    return OverlapTransition(tid, source, target, f"overlap-{source}-{target}", (("role-a", "role-a"),), preserved, not_preserved, certified_layers, context_alignment_passed, assumption_compatibility_passed, regime_overlap, transition_map_passed, (f"evidence-{tid}",), declared_before_outcomes)


def _cycle(consistent=True):
    return CycleConsistencyWitness("cycle-abc", ("A", "B", "C", "A"), consistent, ("cycle-evidence",))


def _trial(**overrides):
    values = dict(
        trial_id="trial-018",
        atlas_object_id="apple-object",
        question_or_qoi="what global theory describes q?",
        abstraction_level=AbstractionLevel.L4,
        requested_layer=GluingLayer.MECHANISTIC,
        charts=(_chart("A"), _chart("B"), _chart("C")),
        transitions=(_transition("A", "B"), _transition("B", "C"), _transition("C", "A")),
        cover_connected=True,
        cover_has_cycles=True,
        cycle_basis_complete=True,
        cycle_witnesses=(_cycle(),),
        global_existence_checked=True,
        global_exists=True,
        uniqueness_checked=True,
        unique_global=True,
        hidden_labels_exposed=False,
        transition_family_frozen_before_outcomes=True,
        target_tested=False,
        target_passed=None,
    )
    values.update(overrides)
    return AtlasGluingTrial(**values)


def _has(report, kind):
    return any(item.obstruction is kind for item in report.obstructions)


def test_consistent_triangle_forms_only_global_proposal():
    report = evaluate_atlas_gluing(_trial())
    assert report.verdict is AtlasGluingVerdict.GLUED_GLOBAL_PORTRAIT_PROPOSAL_ONLY
    assert not report.activates_canonical_knowledge
    assert not report.establishes_mechanism_beyond_requested_layer


def test_pairwise_compatibility_does_not_replace_cycle_global_or_uniqueness_evidence():
    assert evaluate_atlas_gluing(_trial(cycle_witnesses=(_cycle(False),))).verdict is AtlasGluingVerdict.OBSTRUCTED_ATLAS
    assert evaluate_atlas_gluing(_trial(cycle_basis_complete=False)).verdict is AtlasGluingVerdict.CANNOT_CHECK
    assert evaluate_atlas_gluing(_trial(global_existence_checked=False)).verdict is AtlasGluingVerdict.PAIRWISE_COMPATIBLE_GLOBAL_UNPROVEN
    assert evaluate_atlas_gluing(_trial(uniqueness_checked=False)).verdict is AtlasGluingVerdict.GLOBAL_EXISTS_UNIQUENESS_UNPROVEN
    assert evaluate_atlas_gluing(_trial(unique_global=False)).verdict is AtlasGluingVerdict.IDENTIFIED_SET_ONLY


def test_disconnected_cover_is_partial_and_declared_connected_but_disconnected_is_cannot_check():
    assert evaluate_atlas_gluing(_trial(cover_connected=False)).verdict is AtlasGluingVerdict.PARTIAL_ATLAS_ONLY
    report = evaluate_atlas_gluing(_trial(transitions=(_transition("A", "B"),)))
    assert report.verdict is AtlasGluingVerdict.CANNOT_CHECK
    assert "declared_topology_mismatch:cover_connected" in report.reasons


def test_context_assumption_regime_layer_and_transition_failures_are_typed_obstructions():
    cases = (
        (_transition("A", "B", context_alignment_passed=False), ObstructionType.CONTEXT_MISMATCH),
        (_transition("A", "B", assumption_compatibility_passed=False), ObstructionType.ASSUMPTION_CONFLICT),
        (_transition("A", "B", regime_overlap=()), ObstructionType.REGIME_DISJOINT),
        (_transition("A", "B", certified_layers=(GluingLayer.OBSERVATIONAL,)), ObstructionType.RELATION_LAYER_NOT_CERTIFIED),
        (_transition("A", "B", transition_map_passed=False), ObstructionType.TRANSITION_MAP_FAILURE),
    )
    for first, kind in cases:
        report = evaluate_atlas_gluing(_trial(transitions=(first, _transition("B", "C"), _transition("C", "A"))))
        assert report.verdict is AtlasGluingVerdict.OBSTRUCTED_ATLAS
        assert _has(report, kind)


def test_self_contradictory_mapping_is_obstruction_and_unknown_evidence_is_cannot_check():
    bad = _transition("A", "B", preserved=("shared",), not_preserved=("shared",))
    report = evaluate_atlas_gluing(_trial(transitions=(bad, _transition("B", "C"), _transition("C", "A"))))
    assert report.verdict is AtlasGluingVerdict.OBSTRUCTED_ATLAS
    assert _has(report, ObstructionType.MAPPING_WITNESS_CONTRADICTION)
    unknown = _transition("A", "B", transition_map_passed=None)
    assert evaluate_atlas_gluing(_trial(transitions=(unknown, _transition("B", "C"), _transition("C", "A")))).verdict is AtlasGluingVerdict.CANNOT_CHECK


def test_hidden_or_posthoc_gluing_trials_invalid():
    assert evaluate_atlas_gluing(_trial(hidden_labels_exposed=True)).verdict is AtlasGluingVerdict.TRIAL_INVALID
    assert evaluate_atlas_gluing(_trial(transition_family_frozen_before_outcomes=False)).verdict is AtlasGluingVerdict.TRIAL_INVALID


def test_acyclic_pairwise_checks_still_need_explicit_global_evidence():
    report = evaluate_atlas_gluing(_trial(transitions=(_transition("A", "B"), _transition("B", "C")), cover_has_cycles=False, cycle_basis_complete=False, cycle_witnesses=(), global_existence_checked=False))
    assert report.verdict is AtlasGluingVerdict.PAIRWISE_COMPATIBLE_GLOBAL_UNPROVEN


def test_native_target_refutation_preserves_valid_gluing_history():
    report = evaluate_atlas_gluing(_trial(target_tested=True, target_passed=False))
    assert report.verdict is AtlasGluingVerdict.GLOBAL_PROPOSAL_REFUTED_OBSTRUCTION_HISTORY_PRESERVED
    assert all(item.verdict is TransitionVerdict.VALID for item in report.transition_reports)


def test_overlap_transition_contract_is_immutable_and_unknown_chronology_cannot_check():
    transition = _transition("A", "B")
    with pytest.raises(FrozenInstanceError):
        transition.transition_id = "changed"  # type: ignore[misc]
    unknown = _transition("A", "B", declared_before_outcomes=None)
    assert validate_overlap_transition(unknown, requested_layer=GluingLayer.MECHANISTIC, chart_ids=("A", "B")).verdict is TransitionVerdict.CANNOT_CHECK
