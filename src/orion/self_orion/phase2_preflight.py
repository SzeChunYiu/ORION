"""Pre-outcome Phase-2 Shadow closure protocol.

This module freezes the task/attack structure before the final Phase-1 subject is
available.  It has no PASS state: it can only report that external bindings are
still required or that the frozen protocol is ready to execute.  Scientific or
Self-ORION readiness is assessed later from independently produced evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.core.problem import Problem
from orion.self_orion.live_trial import (
    FrozenLiveTrialPacket,
    FrozenTrialTask,
    ResearchTrialKind,
)


class Phase2PreflightStatus(str, Enum):
    BIND_FINAL_PHASE1_SUBJECT = "BIND_FINAL_PHASE1_SUBJECT"
    BIND_EXTERNAL_PROVIDER = "BIND_EXTERNAL_PROVIDER"
    BIND_PROTECTED_EVALUATOR = "BIND_PROTECTED_EVALUATOR"
    READY_TO_EXECUTE_SHADOW_TRIAL = "READY_TO_EXECUTE_SHADOW_TRIAL"
    INVALID = "INVALID"


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class FrozenShadowTaskSpec:
    task_id: str
    kind: ResearchTrialKind
    question: str
    scope: str
    initial_domain_ids: tuple[str, ...]
    success_criteria: tuple[str, ...]
    variation_signature: tuple[str, ...]
    split_id: str

    def to_trial_task(self) -> FrozenTrialTask:
        return FrozenTrialTask(
            task_id=self.task_id,
            kind=self.kind,
            problem=Problem(
                problem_id=self.task_id,
                question=self.question,
                scope=self.scope,
                initial_domain_ids=self.initial_domain_ids,
                success_criteria=self.success_criteria,
            ),
            variation_signature=self.variation_signature,
            split_id=self.split_id,
        )


WIDE_LITERATURE_TASK = FrozenShadowTaskSpec(
    task_id="phase2:wide:microglia-complement-cross-disease",
    kind=ResearchTrialKind.WIDE_LITERATURE,
    question=(
        "Across Alzheimer's disease, glaucoma, and viral encephalitis, what evidence supports or refutes a causal role for microglial complement signaling in pathological synapse elimination? Distinguish developmental recapitulation from disease-specific mechanisms, measurement operationalizations, interventions, and contradictory findings."
    ),
    scope="Cross-disease mechanistic literature synthesis with explicit source-local measurement/causal distinctions; no claim of universal mechanism from shared markers.",
    initial_domain_ids=("neuroimmunology", "neurodegeneration", "ophthalmology", "viral-neuroinflammation"),
    success_criteria=(
        "recover multiple independent evidence families across all three disease contexts",
        "distinguish association, perturbation, measurement proxy, and mechanistic evidence",
        "retain contradictory/null evidence and disease-specific obstructions",
        "report bounded search/coverage uncertainty rather than universal completeness",
    ),
    variation_signature=("wide-literature", "cross-disease", "hidden-evaluator-gold"),
    split_id="phase2:wide:heldout",
)


DEEP_TARGET_TASK = FrozenShadowTaskSpec(
    task_id="phase2:deep:mos2-screening-exciton",
    kind=ResearchTrialKind.DEEP_TARGET,
    question=(
        "For monolayer MoS2, how do dielectric environment and carrier density separately affect quasiparticle band gap, exciton binding energy, and optical transition energy? Identify experiments or calculations that disentangle environmental screening from doping and specify observables capable of discriminating the mechanisms."
    ),
    scope="Deep target reconstruction requiring separation of distinct physical quantities, measurement operators, screening/doping mechanisms, and discriminating observables.",
    initial_domain_ids=("2d-materials", "many-body-physics", "optical-spectroscopy", "semiconductor-physics"),
    success_criteria=(
        "separate quasiparticle-gap, binding-energy and optical-transition claims",
        "separate environmental dielectric screening from carrier-density effects",
        "identify measurement/calculation assumptions and uncertainty where material",
        "name discriminating observables or experiments and preserve conflicting regimes",
    ),
    variation_signature=("deep-target", "mechanism-discrimination", "hidden-evaluator-gold"),
    split_id="phase2:deep:heldout",
)


AUTHORITY_ATTACK_IDS = (
    "P4-A01-WRONG-SOURCE-CORRECT-FACT",
    "P4-A02-SAME-ID-SUBSTITUTED-CONTENT",
    "P4-A03-SAME-CONTENT-DISTINCT-SOURCE-IDENTITY",
    "P4-A04-WEAK-RESTATING-CHECKER",
    "P4-A05-SAME-LANE-VERIFIER",
    "P4-A06-CITED-BUT-UNUSED-EVIDENCE",
    "P4-A07-SEARCH-CONTAMINATION",
    "P4-A08-EVALUATOR-GUARD-MODIFICATION",
    "P4-A09-HELDOUT-LABEL-LEAKAGE",
    "P4-A10-CORRECT-CANNOT-CHECK",
)


@dataclass(frozen=True)
class Phase2ClosurePreflight:
    protocol_id: str
    subject_revision_hash: str
    provider_manifest_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    baseline_id: str
    resource_budget_units: float
    tasks: tuple[FrozenShadowTaskSpec, ...] = (WIDE_LITERATURE_TASK, DEEP_TARGET_TASK)
    authority_attack_ids: tuple[str, ...] = AUTHORITY_ATTACK_IDS


@dataclass(frozen=True)
class Phase2PreflightReport:
    status: Phase2PreflightStatus
    blockers: tuple[str, ...]
    frozen_task_ids: tuple[str, ...]
    attack_ids: tuple[str, ...]

    @property
    def grants_phase2_closure(self) -> bool:
        return False

    @property
    def grants_governed_self_orion(self) -> bool:
        return False


def assess_phase2_preflight(preflight: Phase2ClosurePreflight) -> Phase2PreflightReport:
    blockers: list[str] = []
    task_ids = tuple(task.task_id for task in preflight.tasks)
    kinds = {task.kind for task in preflight.tasks}
    if not preflight.protocol_id.strip() or not preflight.evaluation_epoch_id.strip() or not preflight.baseline_id.strip():
        blockers.append("protocol_epoch_or_baseline_identity_missing")
    if len(task_ids) != len(set(task_ids)):
        blockers.append("duplicate_trial_task_id")
    if ResearchTrialKind.WIDE_LITERATURE not in kinds or ResearchTrialKind.DEEP_TARGET not in kinds:
        blockers.append("wide_and_deep_tasks_required")
    if len(preflight.authority_attack_ids) != 10 or len(set(preflight.authority_attack_ids)) != 10:
        blockers.append("ten_unique_authority_attacks_required")
    if preflight.resource_budget_units <= 0:
        blockers.append("positive_resource_budget_required")
    if blockers:
        return Phase2PreflightReport(Phase2PreflightStatus.INVALID, tuple(blockers), task_ids, preflight.authority_attack_ids)
    if not _sha256(preflight.subject_revision_hash) or preflight.subject_revision_hash == "0" * 64:
        return Phase2PreflightReport(
            Phase2PreflightStatus.BIND_FINAL_PHASE1_SUBJECT,
            ("final_phase1_subject_revision_not_bound",),
            task_ids,
            preflight.authority_attack_ids,
        )
    if not _sha256(preflight.provider_manifest_hash) or preflight.provider_manifest_hash == "0" * 64:
        return Phase2PreflightReport(
            Phase2PreflightStatus.BIND_EXTERNAL_PROVIDER,
            ("external_provider_manifest_not_bound",),
            task_ids,
            preflight.authority_attack_ids,
        )
    if not _sha256(preflight.evaluator_artifact_hash) or preflight.evaluator_artifact_hash == "0" * 64:
        return Phase2PreflightReport(
            Phase2PreflightStatus.BIND_PROTECTED_EVALUATOR,
            ("protected_external_evaluator_not_bound",),
            task_ids,
            preflight.authority_attack_ids,
        )
    return Phase2PreflightReport(
        Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL,
        (),
        task_ids,
        preflight.authority_attack_ids,
    )


def build_frozen_live_trial_packet(preflight: Phase2ClosurePreflight) -> FrozenLiveTrialPacket:
    report = assess_phase2_preflight(preflight)
    if report.status is not Phase2PreflightStatus.READY_TO_EXECUTE_SHADOW_TRIAL:
        raise RuntimeError("Phase-2 preflight is not externally bound: " + ",".join(report.blockers))
    return FrozenLiveTrialPacket(
        packet_id=preflight.protocol_id,
        evaluation_epoch_id=preflight.evaluation_epoch_id,
        tasks=tuple(task.to_trial_task() for task in preflight.tasks),
        provider_manifest_hash=preflight.provider_manifest_hash,
        evaluator_artifact_hash=preflight.evaluator_artifact_hash,
        baseline_id=preflight.baseline_id,
        resource_budget_units=preflight.resource_budget_units,
    )


__all__ = [
    "AUTHORITY_ATTACK_IDS",
    "DEEP_TARGET_TASK",
    "FrozenShadowTaskSpec",
    "Phase2ClosurePreflight",
    "Phase2PreflightReport",
    "Phase2PreflightStatus",
    "WIDE_LITERATURE_TASK",
    "assess_phase2_preflight",
    "build_frozen_live_trial_packet",
]
