from __future__ import annotations

import hashlib
import json
from pathlib import Path

from orion.self_orion.phase2_terminal_receipts import (
    CIEvidenceConclusion,
    FailureReplayDisposition,
    FailureReplayEntry,
    FailureReplayReceipt,
    FinalCIEvidence,
    FinalIntegrationReceipt,
    FinalIntegrationStatus,
    FrozenFailureIndex,
    FrozenFailureRecord,
    RecurrenceOutcome,
)
from orion.self_orion.subject_binding import (
    SUBJECT_ATTESTATION_SCHEMA,
    RepositorySubjectAttestation,
    TrackedObjectIdentity,
)


FROZEN_FAILURE_INDEX_SCHEMA = "FrozenFailureIndex.v1"
FAILURE_REPLAY_RECEIPT_SCHEMA = "FailureReplayReceipt.v1"
FINAL_CI_EVIDENCE_SCHEMA = "FinalCIEvidence.v1"
FINAL_INTEGRATION_RECEIPT_SCHEMA = "FinalIntegrationReceipt.v1"


def sha256_file(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_failure_index_to_dict(index: FrozenFailureIndex) -> dict[str, object]:
    return {
        "schema": FROZEN_FAILURE_INDEX_SCHEMA,
        "artifact_hash": index.artifact_hash,
        "index_id": index.index_id,
        "subject_revision_hash": index.subject_revision_hash,
        "evaluation_epoch_id": index.evaluation_epoch_id,
        "frozen_before_replay": index.frozen_before_replay,
        "failures": [item.payload for item in index.failures],
    }


def write_frozen_failure_index(index: FrozenFailureIndex, path: Path | str) -> None:
    Path(path).write_text(
        json.dumps(frozen_failure_index_to_dict(index), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_frozen_failure_index(path: Path | str) -> FrozenFailureIndex:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != FROZEN_FAILURE_INDEX_SCHEMA:
        raise ValueError(f"frozen failure index schema must be {FROZEN_FAILURE_INDEX_SCHEMA}")
    failures_raw = raw.get("failures")
    if not isinstance(failures_raw, list):
        raise ValueError("frozen failure index failures must be an array")
    index = FrozenFailureIndex(
        index_id=raw["index_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        frozen_before_replay=raw["frozen_before_replay"],
        failures=tuple(
            FrozenFailureRecord(
                failure_id=item["failure_id"],
                failure_class=item["failure_class"],
                source_failure_artifact_hash=item["source_failure_artifact_hash"],
            )
            for item in failures_raw
        ),
    )
    if raw.get("artifact_hash") != index.artifact_hash:
        raise ValueError("frozen failure index artifact hash mismatch")
    return index


def failure_replay_receipt_to_dict(receipt: FailureReplayReceipt) -> dict[str, object]:
    return {
        "schema": FAILURE_REPLAY_RECEIPT_SCHEMA,
        "artifact_hash": receipt.artifact_hash,
        "receipt_id": receipt.receipt_id,
        "subject_revision_hash": receipt.subject_revision_hash,
        "evaluator_artifact_hash": receipt.evaluator_artifact_hash,
        "evaluation_epoch_id": receipt.evaluation_epoch_id,
        "frozen_failure_index_artifact_hash": receipt.frozen_failure_index_artifact_hash,
        "important_failure_ids": list(receipt.important_failure_ids),
        "entries": [item.payload for item in receipt.entries],
        "producer_process_lineage_hash": receipt.producer_process_lineage_hash,
        "verifier_process_lineage_hash": receipt.verifier_process_lineage_hash,
    }


def write_failure_replay_receipt(
    receipt: FailureReplayReceipt, path: Path | str
) -> None:
    Path(path).write_text(
        json.dumps(failure_replay_receipt_to_dict(receipt), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def load_failure_replay_receipt(path: Path | str) -> FailureReplayReceipt:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != FAILURE_REPLAY_RECEIPT_SCHEMA:
        raise ValueError(
            f"failure replay receipt schema must be {FAILURE_REPLAY_RECEIPT_SCHEMA}"
        )
    entries_raw = raw.get("entries")
    if not isinstance(entries_raw, list):
        raise ValueError("failure replay receipt entries must be an array")
    entries = tuple(
        FailureReplayEntry(
            failure_id=item["failure_id"],
            failure_class=item["failure_class"],
            source_failure_artifact_hash=item["source_failure_artifact_hash"],
            negative_history_artifact_hash=item["negative_history_artifact_hash"],
            discriminator_artifact_hash=item["discriminator_artifact_hash"],
            recurrence_probe_artifact_hash=item["recurrence_probe_artifact_hash"],
            disposition=FailureReplayDisposition(item["disposition"]),
            recurrence_outcome=RecurrenceOutcome(item["recurrence_outcome"]),
            replay_artifact_hash=item.get("replay_artifact_hash", ""),
            fresh_transfer_artifact_hash=item.get("fresh_transfer_artifact_hash", ""),
            blocking_fibre_artifact_hash=item.get("blocking_fibre_artifact_hash", ""),
            reopen_condition=item.get("reopen_condition", ""),
        )
        for item in entries_raw
    )
    important = raw.get("important_failure_ids")
    if not isinstance(important, list):
        raise ValueError("failure replay important_failure_ids must be an array")
    receipt = FailureReplayReceipt(
        receipt_id=raw["receipt_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        frozen_failure_index_artifact_hash=raw["frozen_failure_index_artifact_hash"],
        important_failure_ids=tuple(str(item) for item in important),
        entries=entries,
        producer_process_lineage_hash=raw["producer_process_lineage_hash"],
        verifier_process_lineage_hash=raw["verifier_process_lineage_hash"],
    )
    if raw.get("artifact_hash") != receipt.artifact_hash:
        raise ValueError("failure replay receipt artifact hash mismatch")
    return receipt


def final_ci_evidence_to_dict(evidence: FinalCIEvidence) -> dict[str, object]:
    return {
        "schema": FINAL_CI_EVIDENCE_SCHEMA,
        "artifact_hash": evidence.artifact_hash,
        "ci_run_id": evidence.ci_run_id,
        "head_commit_oid": evidence.head_commit_oid,
        "workflow_identity": evidence.workflow_identity,
        "test_command": evidence.test_command,
        "job_count": evidence.job_count,
        "conclusion": evidence.conclusion.value,
        "producer_process_lineage_hash": evidence.producer_process_lineage_hash,
        "verifier_process_lineage_hash": evidence.verifier_process_lineage_hash,
    }


def write_final_ci_evidence(evidence: FinalCIEvidence, path: Path | str) -> None:
    Path(path).write_text(
        json.dumps(final_ci_evidence_to_dict(evidence), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_final_ci_evidence(path: Path | str) -> FinalCIEvidence:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != FINAL_CI_EVIDENCE_SCHEMA:
        raise ValueError(f"final CI evidence schema must be {FINAL_CI_EVIDENCE_SCHEMA}")
    evidence = FinalCIEvidence(
        ci_run_id=raw["ci_run_id"],
        head_commit_oid=raw["head_commit_oid"],
        workflow_identity=raw["workflow_identity"],
        test_command=raw["test_command"],
        job_count=raw["job_count"],
        conclusion=CIEvidenceConclusion(raw["conclusion"]),
        producer_process_lineage_hash=raw["producer_process_lineage_hash"],
        verifier_process_lineage_hash=raw["verifier_process_lineage_hash"],
    )
    if raw.get("artifact_hash") != evidence.artifact_hash:
        raise ValueError("final CI evidence artifact hash mismatch")
    return evidence


def final_integration_receipt_to_dict(
    receipt: FinalIntegrationReceipt,
) -> dict[str, object]:
    return {
        "schema": FINAL_INTEGRATION_RECEIPT_SCHEMA,
        "artifact_hash": receipt.artifact_hash,
        "receipt_id": receipt.receipt_id,
        "subject_revision_hash": receipt.subject_revision_hash,
        "evaluator_artifact_hash": receipt.evaluator_artifact_hash,
        "evaluation_epoch_id": receipt.evaluation_epoch_id,
        "integration_commit_oid": receipt.integration_commit_oid,
        "integration_tree_sha256": receipt.integration_tree_sha256,
        "ci_run_id": receipt.ci_run_id,
        "ci_head_commit_oid": receipt.ci_head_commit_oid,
        "ci_evidence_artifact_hash": receipt.ci_evidence_artifact_hash,
        "external_manifest_artifact_hash": receipt.external_manifest_artifact_hash,
        "papers_claim_ledger_artifact_hash": receipt.papers_claim_ledger_artifact_hash,
        "failure_replay_artifact_hash": receipt.failure_replay_artifact_hash,
        "producer_process_lineage_hash": receipt.producer_process_lineage_hash,
        "verifier_process_lineage_hash": receipt.verifier_process_lineage_hash,
        "status": receipt.status.value,
        "note": receipt.note,
    }


def write_final_integration_receipt(
    receipt: FinalIntegrationReceipt, path: Path | str
) -> None:
    Path(path).write_text(
        json.dumps(final_integration_receipt_to_dict(receipt), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def load_final_integration_receipt(path: Path | str) -> FinalIntegrationReceipt:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != FINAL_INTEGRATION_RECEIPT_SCHEMA:
        raise ValueError(
            f"final integration receipt schema must be {FINAL_INTEGRATION_RECEIPT_SCHEMA}"
        )
    receipt = FinalIntegrationReceipt(
        receipt_id=raw["receipt_id"],
        subject_revision_hash=raw["subject_revision_hash"],
        evaluator_artifact_hash=raw["evaluator_artifact_hash"],
        evaluation_epoch_id=raw["evaluation_epoch_id"],
        integration_commit_oid=raw["integration_commit_oid"],
        integration_tree_sha256=raw["integration_tree_sha256"],
        ci_run_id=raw["ci_run_id"],
        ci_head_commit_oid=raw["ci_head_commit_oid"],
        ci_evidence_artifact_hash=raw["ci_evidence_artifact_hash"],
        external_manifest_artifact_hash=raw["external_manifest_artifact_hash"],
        papers_claim_ledger_artifact_hash=raw["papers_claim_ledger_artifact_hash"],
        failure_replay_artifact_hash=raw["failure_replay_artifact_hash"],
        producer_process_lineage_hash=raw["producer_process_lineage_hash"],
        verifier_process_lineage_hash=raw["verifier_process_lineage_hash"],
        status=FinalIntegrationStatus(raw["status"]),
        note=raw["note"],
    )
    if raw.get("artifact_hash") != receipt.artifact_hash:
        raise ValueError("final integration receipt artifact hash mismatch")
    return receipt


def load_repository_subject_attestation(
    path: Path | str,
) -> RepositorySubjectAttestation:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != SUBJECT_ATTESTATION_SCHEMA:
        raise ValueError(f"repository subject schema must be {SUBJECT_ATTESTATION_SCHEMA}")
    objects_raw = raw.get("tracked_objects")
    if not isinstance(objects_raw, list):
        raise ValueError("repository subject tracked_objects must be an array")
    attestation = RepositorySubjectAttestation(
        repository_identity=raw["repository_identity"],
        commit_oid=raw["commit_oid"],
        tree_oid=raw["tree_oid"],
        git_object_format=raw["git_object_format"],
        tracked_objects=tuple(
            TrackedObjectIdentity(
                path=item["path"],
                mode=item["mode"],
                object_type=item["object_type"],
                git_oid=item["git_oid"],
                content_sha256=item["content_sha256"],
            )
            for item in objects_raw
        ),
    )
    if raw.get("tracked_object_count") != len(attestation.tracked_objects):
        raise ValueError("repository subject tracked object count mismatch")
    if raw.get("source_tree_sha256") != attestation.source_tree_sha256:
        raise ValueError("repository subject source tree hash mismatch")
    if raw.get("subject_revision_hash") != attestation.subject_revision_hash:
        raise ValueError("repository subject revision hash mismatch")
    return attestation


__all__ = [
    "FAILURE_REPLAY_RECEIPT_SCHEMA",
    "FINAL_CI_EVIDENCE_SCHEMA",
    "FINAL_INTEGRATION_RECEIPT_SCHEMA",
    "FROZEN_FAILURE_INDEX_SCHEMA",
    "failure_replay_receipt_to_dict",
    "final_ci_evidence_to_dict",
    "final_integration_receipt_to_dict",
    "frozen_failure_index_to_dict",
    "load_failure_replay_receipt",
    "load_final_ci_evidence",
    "load_final_integration_receipt",
    "load_frozen_failure_index",
    "load_repository_subject_attestation",
    "sha256_file",
    "write_failure_replay_receipt",
    "write_final_ci_evidence",
    "write_final_integration_receipt",
    "write_frozen_failure_index",
]
