from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class ReadinessCriterion(str, Enum):
    DETECTS_SELF_FAILURE = "DETECTS_SELF_FAILURE"
    LOCALIZES_RESPONSIBILITY = "LOCALIZES_RESPONSIBILITY"
    SEARCHES_OUTSIDE_INCUMBENT_NEIGHBORHOOD = "SEARCHES_OUTSIDE_INCUMBENT_NEIGHBORHOOD"
    ABSORBS_EXTERNAL_KNOWLEDGE = "ABSORBS_EXTERNAL_KNOWLEDGE"
    FREEZES_EVALUATOR_BEFORE_OUTCOME = "FREEZES_EVALUATOR_BEFORE_OUTCOME"
    CHALLENGER_BEATS_INCUMBENT_DEVELOPMENT = "CHALLENGER_BEATS_INCUMBENT_DEVELOPMENT"
    CHALLENGER_PASSES_FRESH_ASSURANCE = "CHALLENGER_PASSES_FRESH_ASSURANCE"
    PRESERVES_NEGATIVE_HISTORY = "PRESERVES_NEGATIVE_HISTORY"
    SCOPED_PROMOTION_ONLY = "SCOPED_PROMOTION_ONLY"


_REQUIRED_EMPIRICAL_CRITERIA = frozenset(ReadinessCriterion)


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class ShadowSelfDrivingArchitectureEvidence:
    """Derived architecture observations, not caller-provided pass/fail claims.

    This object may establish only the non-authoritative Shadow stage. It cannot
    promote ORION to primary development authority.
    """

    structural_open_questions: int
    graph_defect_count: int
    mechanical_work_item_count: int
    component_artifact_ids: tuple[str, ...]
    protected_boundary_artifact_ids: tuple[str, ...]
    failure_history_artifact_ids: tuple[str, ...]
    self_merge_capability_present: bool

    def __post_init__(self) -> None:
        if self.structural_open_questions < 0 or self.graph_defect_count < 0:
            raise ValueError("architecture counts cannot be negative")
        if self.mechanical_work_item_count < 0:
            raise ValueError("work-item count cannot be negative")
        if any(not item.strip() for item in (*self.component_artifact_ids, *self.protected_boundary_artifact_ids, *self.failure_history_artifact_ids)):
            raise ValueError("architecture artifact identities must be non-empty")


@dataclass(frozen=True)
class ArchitectureReadinessReport:
    ready: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class ReadinessEvidenceRecord:
    """Content/lineage-bound evidence for one empirical readiness criterion.

    The subject/challenger may create evidence, but it cannot verify its own
    readiness record: producer and verifier process lineages must differ. A
    record is also tied to an evaluator artifact, evaluation epoch and split.
    Even a complete set reaches only READY_PENDING_EXTERNAL_ATTESTATION; ORION
    has no in-process stage meaning that it has promoted itself.
    """

    criterion: ReadinessCriterion
    evidence_artifact_id: str
    evidence_artifact_hash: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    evaluation_epoch_id: str
    split_id: str
    status: EvidenceStatus
    frozen_before_candidate: bool
    fresh_split: bool
    reason: str

    def __post_init__(self) -> None:
        required_text = (
            self.evidence_artifact_id,
            self.evaluation_epoch_id,
            self.split_id,
            self.reason,
        )
        if any(not item.strip() for item in required_text):
            raise ValueError("readiness evidence identity/epoch/split/reason are required")
        for digest in (
            self.evidence_artifact_hash,
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if not _valid_sha256(digest):
                raise ValueError("readiness evidence digests must be SHA-256")

    @property
    def independently_verified(self) -> bool:
        return self.producer_process_lineage_hash != self.verifier_process_lineage_hash


@dataclass(frozen=True)
class EmpiricalReadinessReport:
    criteria: tuple[ReadinessEvidenceRecord, ...]
    missing_criteria: tuple[ReadinessCriterion, ...]
    blockers: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_criteria

    @property
    def passed(self) -> bool:
        return self.complete and not self.blockers


class SelfOrionReadinessStage(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    SHADOW_SELF_DRIVING = "SHADOW_SELF_DRIVING"
    READY_PENDING_EXTERNAL_ATTESTATION = "READY_PENDING_EXTERNAL_ATTESTATION"


def assess_shadow_self_driving_architecture(
    evidence: ShadowSelfDrivingArchitectureEvidence,
) -> ArchitectureReadinessReport:
    blockers: list[str] = []
    if evidence.structural_open_questions:
        blockers.append(f"structural_questions_open:{evidence.structural_open_questions}")
    if evidence.graph_defect_count:
        blockers.append(f"graph_defects:{evidence.graph_defect_count}")
    if evidence.mechanical_work_item_count < 1:
        blockers.append("no_mechanical_work_selection")
    if not evidence.component_artifact_ids:
        blockers.append("architecture_component_artifacts_absent")
    if not evidence.protected_boundary_artifact_ids:
        blockers.append("protected_boundary_artifacts_absent")
    if not evidence.failure_history_artifact_ids:
        blockers.append("failure_history_artifacts_absent")
    if evidence.self_merge_capability_present:
        blockers.append("self_merge_capability_present")
    return ArchitectureReadinessReport(ready=not blockers, blockers=tuple(blockers))


def assess_readiness(
    evidence: tuple[ReadinessEvidenceRecord, ...],
) -> EmpiricalReadinessReport:
    """Assess empirical readiness from independently verified evidence records.

    Caller booleans are not accepted. Duplicate criteria, self-verification,
    post-hoc evaluators, non-fresh evidence and failed/CANNOT_CHECK records all
    remain blockers.
    """

    by_criterion: dict[ReadinessCriterion, list[ReadinessEvidenceRecord]] = {}
    for record in evidence:
        by_criterion.setdefault(record.criterion, []).append(record)

    missing = tuple(
        sorted(
            _REQUIRED_EMPIRICAL_CRITERIA.difference(by_criterion),
            key=lambda item: item.value,
        )
    )
    blockers: list[str] = []
    for criterion, records in sorted(by_criterion.items(), key=lambda item: item[0].value):
        if len(records) != 1:
            blockers.append(f"criterion_not_uniquely_bound:{criterion.value}")
            continue
        record = records[0]
        if record.status is not EvidenceStatus.PASS:
            blockers.append(f"criterion_not_passed:{criterion.value}:{record.status.value}")
        if not record.independently_verified:
            blockers.append(f"self_verified_criterion:{criterion.value}")
        if not record.frozen_before_candidate:
            blockers.append(f"posthoc_evaluator:{criterion.value}")
        if not record.fresh_split:
            blockers.append(f"nonfresh_evidence:{criterion.value}")

    subject_hashes = {record.subject_revision_hash for record in evidence}
    evaluator_hashes = {record.evaluator_artifact_hash for record in evidence}
    epoch_ids = {record.evaluation_epoch_id for record in evidence}
    if len(subject_hashes) > 1:
        blockers.append("readiness_records_bind_multiple_subject_revisions")
    if len(evaluator_hashes) > 1:
        blockers.append("readiness_records_bind_multiple_evaluator_artifacts")
    if len(epoch_ids) > 1:
        blockers.append("readiness_records_bind_multiple_evaluation_epochs")

    return EmpiricalReadinessReport(
        criteria=tuple(evidence),
        missing_criteria=missing,
        blockers=tuple(blockers),
    )


def assess_readiness_stage(
    architecture: ShadowSelfDrivingArchitectureEvidence,
    empirical: tuple[ReadinessEvidenceRecord, ...],
) -> SelfOrionReadinessStage:
    architecture_report = assess_shadow_self_driving_architecture(architecture)
    if not architecture_report.ready:
        return SelfOrionReadinessStage.BOOTSTRAP
    empirical_report = assess_readiness(empirical)
    if empirical_report.passed:
        # This is intentionally a recommendation boundary only. There is no
        # GOVERNED_SELF_ORION enum value inside ORION; external custody must make
        # the actual promotion decision.
        return SelfOrionReadinessStage.READY_PENDING_EXTERNAL_ATTESTATION
    return SelfOrionReadinessStage.SHADOW_SELF_DRIVING


__all__ = [
    "ArchitectureReadinessReport",
    "EmpiricalReadinessReport",
    "EvidenceStatus",
    "ReadinessCriterion",
    "ReadinessEvidenceRecord",
    "SelfOrionReadinessStage",
    "ShadowSelfDrivingArchitectureEvidence",
    "assess_readiness",
    "assess_readiness_stage",
    "assess_shadow_self_driving_architecture",
]
