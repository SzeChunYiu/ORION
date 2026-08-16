"""Explicit quarantine for pre-transition ORION ledgers.

Legacy ANSWER/GRADING/ROUND rows remain an immutable archive and may be imported
only as proposal material. Historical raw VERIFIED labels never become protected
transition authority. This module plans migration; it does not rewrite the old
ledger in place.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from .store import EntryKind, LedgerStore
from .transition import canonical_digest


class MigrationStatus(str, Enum):
    EMPTY = "EMPTY"
    PROTECTED = "PROTECTED"
    MIGRATION_REQUIRED = "MIGRATION_REQUIRED"
    MIXED_LEDGER_REQUIRES_QUARANTINE = "MIXED_LEDGER_REQUIRES_QUARANTINE"


@dataclass(frozen=True)
class LegacyProposalImport:
    source_sequence: int
    source_entry_hash: str
    source_payload: Mapping[str, Any]

    @property
    def grants_authority(self) -> bool:
        return False


@dataclass(frozen=True)
class LegacyMigrationPlan:
    status: MigrationStatus
    archive_sha256: str
    legacy_entry_hashes: tuple[str, ...]
    proposal_imports: tuple[LegacyProposalImport, ...]
    prior_authority_discarded: bool
    reasons: tuple[str, ...]
    plan_id: str

    @property
    def grants_authority(self) -> bool:
        return False


def inspect_migration_status(store: LedgerStore) -> MigrationStatus:
    entries = store.entries()
    if not entries:
        return MigrationStatus.EMPTY
    transition_count = sum(entry.kind is EntryKind.TRANSITION for entry in entries)
    if transition_count == len(entries):
        return MigrationStatus.PROTECTED
    if transition_count:
        return MigrationStatus.MIXED_LEDGER_REQUIRES_QUARANTINE
    return MigrationStatus.MIGRATION_REQUIRED


def build_legacy_migration_plan(store: LedgerStore) -> LegacyMigrationPlan:
    status = inspect_migration_status(store)
    raw_bytes = store.path.read_bytes()
    archive_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    entries = store.entries()
    imports = tuple(
        LegacyProposalImport(entry.sequence, entry.entry_hash, entry.payload)
        for entry in entries
        if entry.kind is EntryKind.ANSWER
    )
    reasons: list[str] = []
    if status is MigrationStatus.EMPTY:
        reasons.append("empty_ledger_requires_no_migration")
    elif status is MigrationStatus.PROTECTED:
        reasons.append("ledger_already_uses_protected_transition_envelopes")
    elif status is MigrationStatus.MIXED_LEDGER_REQUIRES_QUARANTINE:
        reasons.append("loose_and_protected_rows_must_not_be_replayed_as_one_authority_stream")
    else:
        reasons.extend(
            (
                "legacy_answer_rows_import_as_proposals_only",
                "legacy_grading_or_verified_labels_are_not_authority",
                "old_chain_is_preserved_by_archive_sha256",
                "explicit_protected_genesis_required_after_quarantine",
            )
        )
    payload = {
        "status": status.value,
        "archive_sha256": archive_sha256,
        "legacy_entry_hashes": [entry.entry_hash for entry in entries],
        "proposal_imports": [
            {
                "source_sequence": item.source_sequence,
                "source_entry_hash": item.source_entry_hash,
                "source_payload": item.source_payload,
            }
            for item in imports
        ],
        "prior_authority_discarded": status
        in {
            MigrationStatus.MIGRATION_REQUIRED,
            MigrationStatus.MIXED_LEDGER_REQUIRES_QUARANTINE,
        },
        "reasons": reasons,
    }
    return LegacyMigrationPlan(
        status,
        archive_sha256,
        tuple(entry.entry_hash for entry in entries),
        imports,
        payload["prior_authority_discarded"],
        tuple(reasons),
        canonical_digest(payload, domain="orion.legacy-migration-plan.v1"),
    )


def write_archive_copy(store: LedgerStore, destination: Path) -> str:
    """Write an exact archive copy; never modifies the source ledger."""

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = store.path.read_bytes()
    destination.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
        raise IOError("legacy archive copy failed digest verification")
    return digest


__all__ = [
    "LegacyMigrationPlan",
    "LegacyProposalImport",
    "MigrationStatus",
    "build_legacy_migration_plan",
    "inspect_migration_status",
    "write_archive_copy",
]
