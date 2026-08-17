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
    BIND_FROZEN_PACKET = "BIND_FROZEN_PACKET"
    CANNOT_CHECK = "CANNOT_CHECK"
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
    ground_truth_bound: bool = False

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
class FrozenPacketBinding:
    """The declared expected values a preflight must reproduce exactly.

    Shape validation answers "is this a hash?". Only identity comparison answers
    "is this THE hash that was frozen before any outcome was observed", which is
    the property #8 actually requires.
    """

    packet_fingerprint: str
    subject_revision_hash: str
    provider_manifest_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    baseline_id: str
    resource_budget_units: float
    task_ids: tuple[str, ...]
    ground_truth_bound_task_ids: tuple[str, ...] = ()

    @classmethod
    def from_packet_document(cls, document: dict) -> "FrozenPacketBinding":
        """Build the expectation from a published, fingerprint-verified packet.

        Read the document through a loader that verifies `packet_fingerprint`
        first; this constructor trusts the mapping it is handed.
        """

        bindings = tuple(document.get("task_bindings") or ())
        limits = document.get("resource_limits") or {}
        baseline = document.get("matched_baseline") or {}
        evaluator = document.get("evaluator") or {}
        evaluator_hash = document.get("evaluator_artifact_hash") or (
            evaluator.get("artifact_hash") if isinstance(evaluator, dict) else ""
        )
        # The published #8 packet schema does not carry `subject_revision_hash`.
        # Leave it empty. `assess_phase2_preflight` treats an undeclared freeze
        # field as CANNOT_CHECK rather than comparing against "", which would
        # look like the freeze declared the empty string as the expected hash.
        return cls(
            packet_fingerprint=str(document.get("packet_fingerprint", "")),
            subject_revision_hash=str(document.get("subject_revision_hash", "")),
            provider_manifest_hash=str(document.get("provider_manifest_hash", "")),
            evaluator_artifact_hash=str(evaluator_hash or ""),
            evaluation_epoch_id=str(document.get("evaluation_epoch_id", "")),
            baseline_id=str(baseline.get("baseline_id", "")),
            resource_budget_units=float(limits.get("budget_units", 0.0)),
            task_ids=tuple(str(item.get("task_id", "")) for item in bindings),
            ground_truth_bound_task_ids=tuple(
                str(item.get("task_id", ""))
                for item in bindings
                if item.get("ground_truth_bound")
            ),
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
    frozen_packet: FrozenPacketBinding | None = None


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
    # Identity, not count. This previously asked only for ten unique strings,
    # so ten fabricated ids satisfied the gate that guards the entire live
    # campaign — READY_TO_EXECUTE_SHADOW_TRIAL was reachable with attack ids
    # literally named "totally-made-up-0" through "-9". Counting a caller's
    # strings certifies the caller, not the attacks.
    #
    # AUTHORITY_ATTACK_IDS was already declared in this module, ten lines above
    # the check that ignored it. The registry existing and the gate consulting
    # it are different things, which is the whole lesson.
    declared = tuple(preflight.authority_attack_ids)
    unknown = sorted(set(declared) - set(AUTHORITY_ATTACK_IDS))
    absent = sorted(set(AUTHORITY_ATTACK_IDS) - set(declared))
    if len(declared) != len(set(declared)):
        blockers.append("duplicate_authority_attack_id")
    if unknown:
        blockers.append(f"unknown_authority_attack_ids:{','.join(unknown)}")
    if absent:
        blockers.append(f"frozen_authority_attacks_not_declared:{','.join(absent)}")
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
    # Identity, not shape. Everything above asks only whether the caller handed
    # over something hash-shaped: `_sha256` is a 64-hex-character test, so
    # "a" * 64 cleared all three binding gates and READY_TO_EXECUTE_SHADOW_TRIAL
    # -- the gate guarding the entire live campaign -- was reachable with three
    # fabricated strings. That is the same defect the authority-attack registry
    # had one screen above, and it is fixed the same way: by comparing against
    # what was actually frozen.
    #
    # An absent expectation is a blocker, never a pass. A preflight that cannot
    # say what it was frozen against has not been verified, and "not verified"
    # must never be reported as "ready".
    frozen = preflight.frozen_packet
    if frozen is None:
        return Phase2PreflightReport(
            Phase2PreflightStatus.BIND_FROZEN_PACKET,
            ("frozen_packet_binding_absent",),
            task_ids,
            preflight.authority_attack_ids,
        )

    mismatches: list[str] = []
    cannot_check: list[str] = []
    for label, declared, expected in (
        ("subject_revision_hash", preflight.subject_revision_hash, frozen.subject_revision_hash),
        ("provider_manifest_hash", preflight.provider_manifest_hash, frozen.provider_manifest_hash),
        ("evaluator_artifact_hash", preflight.evaluator_artifact_hash, frozen.evaluator_artifact_hash),
        ("evaluation_epoch_id", preflight.evaluation_epoch_id, frozen.evaluation_epoch_id),
        ("baseline_id", preflight.baseline_id, frozen.baseline_id),
    ):
        if not str(expected).strip():
            # A freeze that does not declare the field cannot certify it.
            # Comparing against "" would report a mismatch, as if the freeze
            # had said the value was the empty string, which it did not.
            cannot_check.append(f"{label}_undeclared_in_frozen_packet")
        elif declared != expected:
            mismatches.append(f"{label}_mismatch")
    if frozen.resource_budget_units <= 0:
        cannot_check.append("resource_budget_undeclared_in_frozen_packet")
    elif preflight.resource_budget_units != frozen.resource_budget_units:
        mismatches.append("resource_budget_mismatch")

    # Two frozen task registries exist in this repository and they do not agree.
    # Which one carries the intended Phase-2 subject is a governance decision, so
    # this gate refuses to choose: it names both sides and returns CANNOT_CHECK.
    # Silently adopting either would settle an authority question by fiat, which
    # is the one thing a preflight exists to prevent. Membership is the identity
    # of a registry; order is not.
    frozen_ids = tuple(str(item) for item in frozen.task_ids)
    if not frozen_ids or any(not item.strip() for item in frozen_ids):
        cannot_check.append("frozen_packet_task_ids_undeclared")
    elif frozenset(task_ids) != frozenset(frozen_ids):
        in_source = "|".join(task_ids)
        frozen_listed = "|".join(frozen_ids)
        cannot_check.append(
            f"frozen_packet_registry_divergence:in_source={in_source};frozen={frozen_listed}"
        )

    # A task the freeze says carries held-out ground truth must still declare it
    # here, or the gold-token criteria cannot be evaluated at execution time.
    bound_here = {
        task.task_id
        for task in preflight.tasks
        if getattr(task, "ground_truth_bound", False)
    }
    missing_gold = sorted(set(frozen.ground_truth_bound_task_ids) - bound_here)
    if missing_gold:
        mismatches.append("frozen_ground_truth_not_bound:" + ",".join(missing_gold))

    if cannot_check:
        return Phase2PreflightReport(
            Phase2PreflightStatus.CANNOT_CHECK,
            tuple(cannot_check + mismatches),
            task_ids,
            preflight.authority_attack_ids,
        )
    if mismatches:
        return Phase2PreflightReport(
            Phase2PreflightStatus.BIND_FROZEN_PACKET,
            tuple(mismatches),
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
    "FrozenPacketBinding",
    "FrozenShadowTaskSpec",
    "Phase2ClosurePreflight",
    "Phase2PreflightReport",
    "Phase2PreflightStatus",
    "WIDE_LITERATURE_TASK",
    "assess_phase2_preflight",
    "build_frozen_live_trial_packet",
]
