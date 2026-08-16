from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _artifact_hash(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class FailureReplayDisposition(str, Enum):
    REPAIRED_REPLAYED_FRESH_TRANSFER = "REPAIRED_REPLAYED_FRESH_TRANSFER"
    RETAINED_BLOCKING_FIBRE = "RETAINED_BLOCKING_FIBRE"


class RecurrenceOutcome(str, Enum):
    NO_UNNOTICED_RECURRENCE = "NO_UNNOTICED_RECURRENCE"
    RECOGNIZED_AND_BLOCKED = "RECOGNIZED_AND_BLOCKED"
    UNNOTICED_RECURRENCE = "UNNOTICED_RECURRENCE"


@dataclass(frozen=True)
class FailureReplayEntry:
    failure_id: str
    failure_class: str
    source_failure_artifact_hash: str
    negative_history_artifact_hash: str
    discriminator_artifact_hash: str
    recurrence_probe_artifact_hash: str
    disposition: FailureReplayDisposition
    recurrence_outcome: RecurrenceOutcome
    replay_artifact_hash: str = ""
    fresh_transfer_artifact_hash: str = ""
    blocking_fibre_artifact_hash: str = ""
    reopen_condition: str = ""

    def __post_init__(self) -> None:
        if not self.failure_id.strip() or not self.failure_class.strip():
            raise ValueError("failure replay entry identity/class are required")
        for digest in (
            self.source_failure_artifact_hash,
            self.negative_history_artifact_hash,
            self.discriminator_artifact_hash,
            self.recurrence_probe_artifact_hash,
        ):
            if not _sha256(digest):
                raise ValueError("failure replay evidence bindings must be SHA-256")
        if self.recurrence_outcome is RecurrenceOutcome.UNNOTICED_RECURRENCE:
            raise ValueError("unnoticed recurrence cannot satisfy failure replay")
        if self.disposition is FailureReplayDisposition.REPAIRED_REPLAYED_FRESH_TRANSFER:
            if not _sha256(self.replay_artifact_hash) or not _sha256(
                self.fresh_transfer_artifact_hash
            ):
                raise ValueError("repaired failure requires replay and fresh-transfer artifacts")
            if self.blocking_fibre_artifact_hash or self.reopen_condition:
                raise ValueError("repaired failure cannot also claim a blocking fibre")
        else:
            if not _sha256(self.blocking_fibre_artifact_hash) or not self.reopen_condition.strip():
                raise ValueError("retained failure requires blocking-fibre artifact and reopen condition")
            if self.replay_artifact_hash or self.fresh_transfer_artifact_hash:
                raise ValueError("retained blocking failure cannot claim successful replay artifacts")

    @property
    def payload(self) -> dict[str, object]:
        return {
            "failure_id": self.failure_id,
            "failure_class": self.failure_class,
            "source_failure_artifact_hash": self.source_failure_artifact_hash,
            "negative_history_artifact_hash": self.negative_history_artifact_hash,
            "discriminator_artifact_hash": self.discriminator_artifact_hash,
            "recurrence_probe_artifact_hash": self.recurrence_probe_artifact_hash,
            "disposition": self.disposition.value,
            "recurrence_outcome": self.recurrence_outcome.value,
            "replay_artifact_hash": self.replay_artifact_hash,
            "fresh_transfer_artifact_hash": self.fresh_transfer_artifact_hash,
            "blocking_fibre_artifact_hash": self.blocking_fibre_artifact_hash,
            "reopen_condition": self.reopen_condition,
        }


@dataclass(frozen=True)
class FailureReplayReceipt:
    receipt_id: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    frozen_failure_index_artifact_hash: str
    important_failure_ids: tuple[str, ...]
    entries: tuple[FailureReplayEntry, ...]
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str

    def __post_init__(self) -> None:
        if not self.receipt_id.strip() or not self.evaluation_epoch_id.strip():
            raise ValueError("failure replay receipt identity/epoch are required")
        for digest in (
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.frozen_failure_index_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if not _sha256(digest):
                raise ValueError("failure replay receipt bindings must be SHA-256")
        if not self.important_failure_ids or any(not item.strip() for item in self.important_failure_ids):
            raise ValueError("failure replay requires a non-empty frozen important-failure set")
        if len(self.important_failure_ids) != len(set(self.important_failure_ids)):
            raise ValueError("important failure identities must be unique")
        entry_ids = tuple(item.failure_id for item in self.entries)
        if len(entry_ids) != len(set(entry_ids)):
            raise ValueError("failure replay entry identities must be unique")
        if set(entry_ids) != set(self.important_failure_ids):
            raise ValueError("failure replay entries must cover the frozen important-failure set exactly")

    @property
    def independently_verified(self) -> bool:
        return self.producer_process_lineage_hash != self.verifier_process_lineage_hash

    @property
    def artifact_hash(self) -> str:
        return _artifact_hash(
            {
                "receipt_id": self.receipt_id,
                "subject_revision_hash": self.subject_revision_hash,
                "evaluator_artifact_hash": self.evaluator_artifact_hash,
                "evaluation_epoch_id": self.evaluation_epoch_id,
                "frozen_failure_index_artifact_hash": self.frozen_failure_index_artifact_hash,
                "important_failure_ids": list(self.important_failure_ids),
                "entries": [item.payload for item in self.entries],
                "producer_process_lineage_hash": self.producer_process_lineage_hash,
                "verifier_process_lineage_hash": self.verifier_process_lineage_hash,
            }
        )


class FinalIntegrationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class FinalIntegrationReceipt:
    receipt_id: str
    subject_revision_hash: str
    evaluator_artifact_hash: str
    evaluation_epoch_id: str
    integration_commit_oid: str
    integration_tree_sha256: str
    ci_run_id: str
    ci_head_commit_oid: str
    ci_evidence_artifact_hash: str
    external_manifest_artifact_hash: str
    papers_claim_ledger_artifact_hash: str
    failure_replay_artifact_hash: str
    producer_process_lineage_hash: str
    verifier_process_lineage_hash: str
    status: FinalIntegrationStatus
    note: str

    def __post_init__(self) -> None:
        required = (
            self.receipt_id,
            self.evaluation_epoch_id,
            self.integration_commit_oid,
            self.ci_run_id,
            self.ci_head_commit_oid,
            self.note,
        )
        if any(not item.strip() for item in required):
            raise ValueError("final integration receipt identity/CI/note fields are required")
        for digest in (
            self.subject_revision_hash,
            self.evaluator_artifact_hash,
            self.integration_tree_sha256,
            self.ci_evidence_artifact_hash,
            self.external_manifest_artifact_hash,
            self.papers_claim_ledger_artifact_hash,
            self.failure_replay_artifact_hash,
            self.producer_process_lineage_hash,
            self.verifier_process_lineage_hash,
        ):
            if not _sha256(digest):
                raise ValueError("final integration artifact bindings must be SHA-256")
        if self.integration_commit_oid != self.ci_head_commit_oid:
            raise ValueError("final integration CI must bind the exact integration commit")

    @property
    def independently_verified(self) -> bool:
        return self.producer_process_lineage_hash != self.verifier_process_lineage_hash

    @property
    def artifact_hash(self) -> str:
        return _artifact_hash(
            {
                "receipt_id": self.receipt_id,
                "subject_revision_hash": self.subject_revision_hash,
                "evaluator_artifact_hash": self.evaluator_artifact_hash,
                "evaluation_epoch_id": self.evaluation_epoch_id,
                "integration_commit_oid": self.integration_commit_oid,
                "integration_tree_sha256": self.integration_tree_sha256,
                "ci_run_id": self.ci_run_id,
                "ci_head_commit_oid": self.ci_head_commit_oid,
                "ci_evidence_artifact_hash": self.ci_evidence_artifact_hash,
                "external_manifest_artifact_hash": self.external_manifest_artifact_hash,
                "papers_claim_ledger_artifact_hash": self.papers_claim_ledger_artifact_hash,
                "failure_replay_artifact_hash": self.failure_replay_artifact_hash,
                "producer_process_lineage_hash": self.producer_process_lineage_hash,
                "verifier_process_lineage_hash": self.verifier_process_lineage_hash,
                "status": self.status.value,
                "note": self.note,
            }
        )


__all__ = [
    "FailureReplayDisposition",
    "FailureReplayEntry",
    "FailureReplayReceipt",
    "FinalIntegrationReceipt",
    "FinalIntegrationStatus",
    "RecurrenceOutcome",
]
