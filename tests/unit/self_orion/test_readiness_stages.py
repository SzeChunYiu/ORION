from orion.self_orion.readiness import (
    ReadinessEvidence,
    SelfOrionReadinessStage,
    ShadowSelfDrivingArchitectureEvidence,
    assess_readiness_stage,
    assess_shadow_self_driving_architecture,
)


def _architecture(**overrides):
    values = dict(
        structural_questions_closed=True,
        graph_integrity_passed=True,
        mechanical_work_selection_present=True,
        autonomous_research_loop_present=True,
        development_proposal_boundary_present=True,
        content_addressed_patch_boundary_present=True,
        isolated_sandbox_boundary_present=True,
        protected_assurance_boundary_present=True,
        failure_history_preserved=True,
        self_merge_absent=True,
    )
    values.update(overrides)
    return ShadowSelfDrivingArchitectureEvidence(**values)


def _empirical(**overrides):
    values = dict(
        detects_self_failure=False,
        localizes_responsibility=False,
        searches_outside_incumbent_neighborhood=False,
        absorbs_external_knowledge=False,
        freezes_evaluator_before_outcome=False,
        challenger_beats_incumbent_development=False,
        challenger_passes_fresh_assurance=False,
        preserves_negative_history=False,
        scoped_promotion_only=False,
    )
    values.update(overrides)
    return ReadinessEvidence(**values)


def test_complete_architecture_is_shadow_self_driving_even_without_empirical_governed_evidence():
    architecture = _architecture()
    assert assess_shadow_self_driving_architecture(architecture)
    assert assess_readiness_stage(architecture, _empirical()) is SelfOrionReadinessStage.SHADOW_SELF_DRIVING


def test_missing_sandbox_or_self_merge_guard_keeps_system_in_bootstrap():
    assert assess_readiness_stage(_architecture(isolated_sandbox_boundary_present=False), _empirical()) is SelfOrionReadinessStage.BOOTSTRAP
    assert assess_readiness_stage(_architecture(self_merge_absent=False), _empirical()) is SelfOrionReadinessStage.BOOTSTRAP


def test_governed_stage_requires_all_empirical_evidence_after_architecture_gate():
    empirical = _empirical(
        detects_self_failure=True,
        localizes_responsibility=True,
        searches_outside_incumbent_neighborhood=True,
        absorbs_external_knowledge=True,
        freezes_evaluator_before_outcome=True,
        challenger_beats_incumbent_development=True,
        challenger_passes_fresh_assurance=True,
        preserves_negative_history=True,
        scoped_promotion_only=True,
    )
    assert assess_readiness_stage(_architecture(), empirical) is SelfOrionReadinessStage.GOVERNED_SELF_ORION
