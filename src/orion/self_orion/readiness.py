from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ShadowSelfDrivingArchitectureEvidence:
    structural_questions_closed: bool
    graph_integrity_passed: bool
    mechanical_work_selection_present: bool
    autonomous_research_loop_present: bool
    development_proposal_boundary_present: bool
    content_addressed_patch_boundary_present: bool
    isolated_sandbox_boundary_present: bool
    protected_assurance_boundary_present: bool
    failure_history_preserved: bool
    self_merge_absent: bool


@dataclass(frozen=True)
class ReadinessEvidence:
    """Empirical evidence required for Governed Self-ORION, not just architecture."""

    detects_self_failure: bool
    localizes_responsibility: bool
    searches_outside_incumbent_neighborhood: bool
    absorbs_external_knowledge: bool
    freezes_evaluator_before_outcome: bool
    challenger_beats_incumbent_development: bool
    challenger_passes_fresh_assurance: bool
    preserves_negative_history: bool
    scoped_promotion_only: bool


class SelfOrionReadinessStage(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    SHADOW_SELF_DRIVING = "SHADOW_SELF_DRIVING"
    GOVERNED_SELF_ORION = "GOVERNED_SELF_ORION"


def assess_shadow_self_driving_architecture(evidence: ShadowSelfDrivingArchitectureEvidence) -> bool:
    """Architecture gate: can ORION drive the loop with host/provider boundaries?"""

    return all(evidence.__dict__.values())


def assess_readiness(evidence: ReadinessEvidence) -> bool:
    """Conservative empirical gate from Shadow self-driving to Governed Self-ORION."""

    return all(evidence.__dict__.values())


def assess_readiness_stage(
    architecture: ShadowSelfDrivingArchitectureEvidence,
    empirical: ReadinessEvidence,
) -> SelfOrionReadinessStage:
    if not assess_shadow_self_driving_architecture(architecture):
        return SelfOrionReadinessStage.BOOTSTRAP
    if assess_readiness(empirical):
        return SelfOrionReadinessStage.GOVERNED_SELF_ORION
    return SelfOrionReadinessStage.SHADOW_SELF_DRIVING


__all__ = [
    "ReadinessEvidence",
    "SelfOrionReadinessStage",
    "ShadowSelfDrivingArchitectureEvidence",
    "assess_readiness",
    "assess_readiness_stage",
    "assess_shadow_self_driving_architecture",
]
