from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.benchmarks.result import BenchmarkReport, BenchmarkStatus


class ExternalEvidenceStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


class ExternalCriterion(str, Enum):
    # Paper I
    P1_HIDDEN_FORMULATION_TASKS = "P1_HIDDEN_FORMULATION_TASKS"
    P1_STATIC_WORKFLOW_BASELINE = "P1_STATIC_WORKFLOW_BASELINE"
    P1_AGENT_TREE_BASELINE = "P1_AGENT_TREE_BASELINE"
    P1_RESOURCE_MATCH = "P1_RESOURCE_MATCH"
    P1_LABELS_HIDDEN = "P1_LABELS_HIDDEN"
    P1_FRESH_CASES = "P1_FRESH_CASES"
    P1_ROOT_OUTCOME_BETTER = "P1_ROOT_OUTCOME_BETTER"
    P1_UNNECESSARY_REFRAME_NOT_WORSE = "P1_UNNECESSARY_REFRAME_NOT_WORSE"

    # Paper II
    P2_COMPLETE_GOLD = "P2_COMPLETE_GOLD"
    P2_MATCHED_SIMPLE_BASELINE = "P2_MATCHED_SIMPLE_BASELINE"
    P2_PROVIDER_TRACE_FROZEN = "P2_PROVIDER_TRACE_FROZEN"
    P2_SYSTEM_BEATS_BASELINE = "P2_SYSTEM_BEATS_BASELINE"

    # Paper III
    P3_THREE_DOMAIN_CASE = "P3_THREE_DOMAIN_CASE"
    P3_MULTIPLE_OPERATIONALIZATIONS = "P3_MULTIPLE_OPERATIONALIZATIONS"
    P3_SOURCE_PROJECTION_GOLD = "P3_SOURCE_PROJECTION_GOLD"
    P3_MAPPING_GOLD = "P3_MAPPING_GOLD"
    P3_LONG_CONTEXT_BASELINE = "P3_LONG_CONTEXT_BASELINE"
    P3_RAG_TRANSLATION_BASELINE = "P3_RAG_TRANSLATION_BASELINE"
    P3_FLAT_SCHEMA_BASELINE = "P3_FLAT_SCHEMA_BASELINE"
    P3_SEMANTIC_ABLATION = "P3_SEMANTIC_ABLATION"
    P3_FALSE_INTEGRATION_BETTER = "P3_FALSE_INTEGRATION_BETTER"
    P3_SOURCE_RECOVERABILITY_NOT_WORSE = "P3_SOURCE_RECOVERABILITY_NOT_WORSE"

    # Paper IV
    P4_SOURCE_ATTRIBUTION_BENCHMARK = "P4_SOURCE_ATTRIBUTION_BENCHMARK"
    P4_SEARCH_CONTAMINATION_AUDIT = "P4_SEARCH_CONTAMINATION_AUDIT"
    P4_EVALUATOR_LOCKED = "P4_EVALUATOR_LOCKED"
    P4_HELDOUT_ACCESS_LOGGED = "P4_HELDOUT_ACCESS_LOGGED"
    P4_MATCHED_VERIFIER_BASELINE = "P4_MATCHED_VERIFIER_BASELINE"
    P4_FALSE_PROMOTION_BETTER = "P4_FALSE_PROMOTION_BETTER"

    # Paper V
    P5_DIRECT_SELF_EDIT_BASELINE = "P5_DIRECT_SELF_EDIT_BASELINE"
    P5_AGENT_DESIGN_BASELINE = "P5_AGENT_DESIGN_BASELINE"
    P5_FAILURE_CAUSES_HIDDEN = "P5_FAILURE_CAUSES_HIDDEN"
    P5_FRESH_TRANSFER = "P5_FRESH_TRANSFER"
    P5_EVALUATOR_FROZEN = "P5_EVALUATOR_FROZEN"
    P5_NEGATIVE_HISTORY_COMPLETE = "P5_NEGATIVE_HISTORY_COMPLETE"
    P5_PROTECTED_ACCESS_LOGGED = "P5_PROTECTED_ACCESS_LOGGED"
    P5_ROOT_IMPROVEMENT_BETTER = "P5_ROOT_IMPROVEMENT_BETTER"


_REQUIRED: dict[str, frozenset[ExternalCriterion]] = {
    "P1": frozenset(item for item in ExternalCriterion if item.value.startswith("P1_")),
    "P2": frozenset(item for item in ExternalCriterion if item.value.startswith("P2_")),
    "P3": frozenset(item for item in ExternalCriterion if item.value.startswith("P3_")),
    "P4": frozenset(item for item in ExternalCriterion if item.value.startswith("P4_")),
    "P5": frozenset(item for item in ExternalCriterion if item.value.startswith("P5_")),
}


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class ExternalEvidenceRecord:
    """One externally produced, independently verified paper-gate observation."""

    paper_id: str
    criterion: ExternalCriterion
    evidence_artifact_id: str
    evidence_artifact_hash: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    evaluation_epoch_id: str
    split_id: str
    status: ExternalEvidenceStatus
    frozen_before_candidate: bool
    fresh_split: bool
    note: str

    def __post_init__(self) -> None:
        if self.paper_id not in _REQUIRED:
            raise ValueError("external evidence paper id must be one of P1..P5")
        if self.criterion not in _REQUIRED[self.paper_id]:
            raise ValueError("external criterion does not belong to the declared paper")
        if any(
            not item.strip()
            for item in (
                self.evidence_artifact_id,
                self.evaluation_epoch_id,
                self.split_id,
                self.note,
            )
        ):
            raise ValueError("external evidence identity/epoch/split/note are required")
        for digest in (
            self.evidence_artifact_hash,
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if not _sha256(digest):
                raise ValueError("external evidence digests must be SHA-256")

    @property
    def independently_verified(self) -> bool:
        return self.producer_process_lineage_hash != self.verifier_process_lineage_hash


@dataclass(frozen=True)
class ExternalEvidenceManifest:
    """One frozen external evaluation campaign for the flagship papers."""

    manifest_id: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    records: tuple[ExternalEvidenceRecord, ...]

    def __post_init__(self) -> None:
        if not self.manifest_id.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("external manifest identity/epoch are required")
        if not _sha256(self.subject_revision_hash) or not _sha256(self.evaluator_artifact_hash):
            raise ValueError("external manifest subject/evaluator hashes must be SHA-256")


def empty_external_manifest() -> ExternalEvidenceManifest:
    """Repository-only state: no external evidence exists in independent custody."""

    return ExternalEvidenceManifest(
        manifest_id="external-evidence:absent",
        subject_revision_hash="0" * 64,
        evaluator_artifact_hash="0" * 64,
        evaluation_epoch_id="external-evaluation:unavailable",
        records=(),
    )


def assess_external_paper(
    manifest: ExternalEvidenceManifest,
    paper_id: str,
) -> BenchmarkReport:
    if paper_id not in _REQUIRED:
        raise ValueError("unknown flagship paper id")

    by_criterion: dict[ExternalCriterion, list[ExternalEvidenceRecord]] = {}
    for record in manifest.records:
        if record.paper_id == paper_id:
            by_criterion.setdefault(record.criterion, []).append(record)

    missing = tuple(
        sorted(_REQUIRED[paper_id].difference(by_criterion), key=lambda item: item.value)
    )
    cannot_check: list[str] = [f"missing_external_record:{item.value}" for item in missing]
    failures: list[str] = []

    for criterion, records in sorted(by_criterion.items(), key=lambda item: item[0].value):
        if len(records) != 1:
            cannot_check.append(f"criterion_not_uniquely_bound:{criterion.value}")
            continue
        record = records[0]
        if record.subject_revision_hash != manifest.subject_revision_hash:
            cannot_check.append(f"subject_revision_mismatch:{criterion.value}")
        if record.evaluator_artifact_hash != manifest.evaluator_artifact_hash:
            cannot_check.append(f"evaluator_mismatch:{criterion.value}")
        if record.evaluation_epoch_id != manifest.evaluation_epoch_id:
            cannot_check.append(f"evaluation_epoch_mismatch:{criterion.value}")
        if not record.independently_verified:
            cannot_check.append(f"self_verified_external_record:{criterion.value}")
        if not record.frozen_before_candidate:
            cannot_check.append(f"posthoc_external_evaluator:{criterion.value}")
        if not record.fresh_split:
            cannot_check.append(f"nonfresh_external_record:{criterion.value}")
        if record.status is ExternalEvidenceStatus.CANNOT_CHECK:
            cannot_check.append(f"criterion_cannot_check:{criterion.value}")
        elif record.status is ExternalEvidenceStatus.FAIL:
            failures.append(f"criterion_failed:{criterion.value}")

    if cannot_check:
        return BenchmarkReport(
            paper_id=paper_id,
            case_id=f"external:{paper_id.lower()}",
            status=BenchmarkStatus.CANNOT_CHECK,
            blockers=tuple(dict.fromkeys(cannot_check)),
        )
    if failures:
        return BenchmarkReport(
            paper_id=paper_id,
            case_id=f"external:{paper_id.lower()}",
            status=BenchmarkStatus.FAIL,
            blockers=tuple(failures),
        )
    return BenchmarkReport(
        paper_id=paper_id,
        case_id=f"external:{paper_id.lower()}",
        status=BenchmarkStatus.PASS,
        metrics=(("all_external_criteria_pass", 1.0),),
    )


def assess_external_flagship(
    manifest: ExternalEvidenceManifest,
) -> tuple[BenchmarkReport, ...]:
    return tuple(assess_external_paper(manifest, paper_id) for paper_id in ("P1", "P2", "P3", "P4", "P5"))


__all__ = [
    "ExternalCriterion",
    "ExternalEvidenceManifest",
    "ExternalEvidenceRecord",
    "ExternalEvidenceStatus",
    "assess_external_flagship",
    "assess_external_paper",
    "empty_external_manifest",
]
