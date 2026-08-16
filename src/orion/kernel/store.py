from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import fcntl

from .transaction import TransitionTransaction, transaction_payload
from .transition import LedgerExpectation

_GENESIS_HASH = "0" * 64
_LEDGER_FILENAME = "ledger.jsonl"
_LOCK_FILENAME = ".ledger.jsonl.lock"
_TEMP_PREFIX = ".ledger.jsonl."
_TEMP_SUFFIX = ".tmp"


class _ExpectedHeadUnset:
    pass


_EXPECTED_HEAD_UNSET = _ExpectedHeadUnset()


class EntryKind(str, Enum):
    """The durable record kinds a self-driving ORION run may append."""

    ROUND = "ROUND"
    ANSWER = "ANSWER"
    GRADING = "GRADING"
    EPISODE = "EPISODE"
    RECEIPT = "RECEIPT"
    GUARD = "GUARD"
    RESIDUAL = "RESIDUAL"
    SOURCE = "SOURCE"
    READ = "READ"
    TRANSITION = "TRANSITION"


@dataclass(frozen=True)
class LedgerEntry:
    """One append-only, hash-chained ledger row."""

    sequence: int
    kind: EntryKind
    payload: Mapping[str, Any]
    prev_hash: str
    entry_hash: str


class LedgerIntegrityError(RuntimeError):
    """Raised when a ledger on disk cannot be replayed as a valid chain."""


class StaleLedgerHead(RuntimeError):
    """Raised when an append's compare-and-swap precondition is stale."""

    def __init__(self, expected_head: str | None, actual_head: str | None) -> None:
        self.expected_head = expected_head
        self.actual_head = actual_head
        super().__init__(
            f"expected ledger head {expected_head!r}, found {actual_head!r}"
        )


class StaleTransitionExpectation(RuntimeError):
    """Raised when any protected transition revision is stale."""

    def __init__(self, coordinate: str, expected: str | None, actual: str | None) -> None:
        self.coordinate = coordinate
        self.expected = expected
        self.actual = actual
        super().__init__(f"stale {coordinate}: expected {expected!r}, found {actual!r}")


class LegacyLedgerRequiresMigration(RuntimeError):
    """Protected transitions cannot anchor silently on legacy loose rows."""


class TransactionIdConflict(RuntimeError):
    """A transaction id was reused for different canonical content."""


def canonical_bytes(payload: Any) -> bytes:
    """Encode a payload as canonical JSON so digests are reproducible."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_entry_hash(
    sequence: int, kind: EntryKind, payload: Mapping[str, Any], prev_hash: str
) -> str:
    """Bind an entry to its position, content and predecessor."""

    return hashlib.sha256(
        canonical_bytes(
            {
                "sequence": sequence,
                "kind": kind.value,
                "payload": payload,
                "prev_hash": prev_hash,
            }
        )
    ).hexdigest()


def _decode(line: str, line_number: int) -> LedgerEntry:
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as error:
        raise LedgerIntegrityError(
            f"line {line_number} is not valid JSON: {error}"
        ) from error
    missing = {"sequence", "kind", "payload", "prev_hash", "entry_hash"} - set(raw)
    if missing:
        raise LedgerIntegrityError(
            f"line {line_number} is missing fields: {', '.join(sorted(missing))}"
        )
    try:
        kind = EntryKind(raw["kind"])
    except ValueError as error:
        raise LedgerIntegrityError(f"line {line_number} has unknown kind") from error
    return LedgerEntry(
        sequence=int(raw["sequence"]),
        kind=kind,
        payload=raw["payload"],
        prev_hash=str(raw["prev_hash"]),
        entry_hash=str(raw["entry_hash"]),
    )


class LedgerStore:
    """Durable append-only state for a self-driving ORION run.

    Loose historical row kinds remain readable for migration/diagnostics, but
    protected state changes are represented by one ``TRANSITION`` envelope.
    """

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._path = self._root / _LEDGER_FILENAME
        self._lock_path = self._root / _LOCK_FILENAME
        self._path.touch(exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def path(self) -> Path:
        return self._path

    def _raw_lines(self) -> Iterator[tuple[int, str]]:
        with self._path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if line.strip():
                    yield line_number, line

    def entries(self, kind: EntryKind | None = None) -> tuple[LedgerEntry, ...]:
        """Replay the ledger, verifying the chain, optionally filtered by kind."""

        replayed: list[LedgerEntry] = []
        prev_hash = _GENESIS_HASH
        for line_number, line in self._raw_lines():
            entry = _decode(line, line_number)
            expected_sequence = len(replayed)
            if entry.sequence != expected_sequence:
                raise LedgerIntegrityError(
                    f"line {line_number} has sequence {entry.sequence}, expected {expected_sequence}"
                )
            if entry.prev_hash != prev_hash:
                raise LedgerIntegrityError(
                    f"line {line_number} does not chain to its predecessor"
                )
            recomputed = compute_entry_hash(
                entry.sequence, entry.kind, entry.payload, entry.prev_hash
            )
            if recomputed != entry.entry_hash:
                raise LedgerIntegrityError(
                    f"line {line_number} content does not match its recorded digest"
                )
            replayed.append(entry)
            prev_hash = entry.entry_hash
        if kind is None:
            return tuple(replayed)
        return tuple(item for item in replayed if item.kind is kind)

    def head(self) -> LedgerEntry | None:
        entries = self.entries()
        return entries[-1] if entries else None

    @contextmanager
    def _exclusive_lock(self) -> Iterator[None]:
        descriptor = os.open(self._lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def _cleanup_stale_temporaries(self) -> None:
        for candidate in self._root.glob(f"{_TEMP_PREFIX}*{_TEMP_SUFFIX}"):
            try:
                candidate.unlink()
            except FileNotFoundError:
                pass

    def _fsync_directory(self) -> None:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        descriptor = os.open(self._root, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _persist_entry(
        self,
        *,
        entries: tuple[LedgerEntry, ...],
        kind: EntryKind,
        payload: Mapping[str, Any],
    ) -> LedgerEntry:
        actual_head = entries[-1].entry_hash if entries else None
        sequence = len(entries)
        prev_hash = actual_head if actual_head is not None else _GENESIS_HASH
        normalized = json.loads(canonical_bytes(payload))
        entry = LedgerEntry(
            sequence=sequence,
            kind=kind,
            payload=normalized,
            prev_hash=prev_hash,
            entry_hash=compute_entry_hash(sequence, kind, normalized, prev_hash),
        )
        encoded_entry = canonical_bytes(
            {
                "sequence": entry.sequence,
                "kind": entry.kind.value,
                "payload": entry.payload,
                "prev_hash": entry.prev_hash,
                "entry_hash": entry.entry_hash,
            }
        ) + b"\n"
        old_content = self._path.read_bytes()
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=self._root,
                prefix=_TEMP_PREFIX,
                suffix=_TEMP_SUFFIX,
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(old_content)
                if old_content and not old_content.endswith(b"\n"):
                    handle.write(b"\n")
                handle.write(encoded_entry)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self._path)
            temporary_path = None
            self._fsync_directory()
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink()
                except FileNotFoundError:
                    pass
        return entry

    def append(
        self,
        kind: EntryKind,
        payload: Mapping[str, Any],
        *,
        expected_head: str | None | _ExpectedHeadUnset = _EXPECTED_HEAD_UNSET,
    ) -> LedgerEntry:
        """Atomically append a loose/diagnostic row.

        Protected state changes must use :meth:`append_transaction` instead.
        """

        if kind is EntryKind.TRANSITION:
            raise ValueError("TRANSITION entries must use append_transaction")
        with self._exclusive_lock():
            self._cleanup_stale_temporaries()
            entries = self.entries()
            actual_head = entries[-1].entry_hash if entries else None
            if (
                not isinstance(expected_head, _ExpectedHeadUnset)
                and expected_head != actual_head
            ):
                raise StaleLedgerHead(expected_head, actual_head)
            return self._persist_entry(entries=entries, kind=kind, payload=payload)

    @staticmethod
    def _transition_identity_payload(transaction: TransitionTransaction) -> dict[str, Any]:
        return {
            "transaction_id": transaction.transaction_id,
            "transaction": transaction_payload(transaction),
        }

    @staticmethod
    def _transaction_id(entry: LedgerEntry) -> str:
        return str(entry.payload.get("transaction_id", ""))

    @staticmethod
    def _transition_state(entry: LedgerEntry) -> tuple[str, str, str]:
        if entry.kind is not EntryKind.TRANSITION:
            raise LedgerIntegrityError("transition state requested from non-transition row")
        transaction = entry.payload.get("transaction")
        if not isinstance(transaction, Mapping):
            raise LedgerIntegrityError("transition row is missing its canonical envelope")
        decision = transaction.get("decision")
        if not isinstance(decision, Mapping):
            raise LedgerIntegrityError("transition row is missing authorization decision")
        research = str(transaction.get("committed_post_state_hash", ""))
        authority = str(decision.get("authority_revision", ""))
        support = str(decision.get("support_revision", ""))
        if not research or not authority or not support:
            raise LedgerIntegrityError("transition row is missing protected revision state")
        return research, authority, support

    def protected_expectation(self) -> LedgerExpectation | None:
        """Return the exact revision tuple for the next protected transaction.

        Legacy-only ledgers deliberately have no protected expectation: they must
        pass through explicit migration quarantine first.
        """

        entries = self.entries()
        if not entries:
            return None
        transitions = tuple(item for item in entries if item.kind is EntryKind.TRANSITION)
        if not transitions:
            raise LegacyLedgerRequiresMigration(
                "non-empty ledger has no protected transition genesis"
            )
        last = transitions[-1]
        if last is not entries[-1]:
            raise LegacyLedgerRequiresMigration(
                "loose rows after protected transition require explicit migration/reconciliation"
            )
        research, authority, support = self._transition_state(last)
        return LedgerExpectation(last.entry_hash, research, authority, support)

    def append_transaction(
        self,
        transaction: TransitionTransaction,
        *,
        expected: LedgerExpectation,
    ) -> LedgerEntry:
        """Atomically append one complete protected transition envelope.

        Under one writer lock this checks ledger head, research-state hash,
        authority revision and support revision. The same transaction ID/content
        is idempotent; the same ID with different content is a typed conflict.
        """

        if transaction.plan.expectation != expected:
            raise StaleTransitionExpectation(
                "transaction_plan_expectation",
                repr(expected),
                repr(transaction.plan.expectation),
            )
        payload = self._transition_identity_payload(transaction)
        normalized_payload = json.loads(canonical_bytes(payload))
        with self._exclusive_lock():
            self._cleanup_stale_temporaries()
            entries = self.entries()

            for entry in entries:
                if entry.kind is not EntryKind.TRANSITION:
                    continue
                if self._transaction_id(entry) != transaction.transaction_id:
                    continue
                if entry.payload == normalized_payload:
                    return entry
                raise TransactionIdConflict(
                    f"transaction id {transaction.transaction_id} already exists with different content"
                )

            actual_head = entries[-1].entry_hash if entries else None
            if expected.ledger_head != actual_head:
                raise StaleTransitionExpectation(
                    "ledger_head", expected.ledger_head, actual_head
                )

            transitions = tuple(item for item in entries if item.kind is EntryKind.TRANSITION)
            if not entries:
                # Explicit protected genesis: the plan itself binds the exact
                # seed projection and captured authority/support revisions.
                actual_research = transaction.plan.pre_state_hash
                actual_authority = transaction.evidence_snapshot.captured_at_authority_revision
                actual_support = transaction.evidence_snapshot.captured_at_support_revision
            elif not transitions:
                raise LegacyLedgerRequiresMigration(
                    "legacy loose ledger cannot become protected state implicitly"
                )
            elif transitions[-1] is not entries[-1]:
                raise LegacyLedgerRequiresMigration(
                    "loose rows after protected transition require migration before another protected commit"
                )
            else:
                actual_research, actual_authority, actual_support = self._transition_state(
                    transitions[-1]
                )

            for coordinate, expected_value, actual_value in (
                ("research_state_hash", expected.research_state_hash, actual_research),
                ("authority_revision", expected.authority_revision, actual_authority),
                ("support_revision", expected.support_revision, actual_support),
            ):
                if expected_value != actual_value:
                    raise StaleTransitionExpectation(
                        coordinate, expected_value, actual_value
                    )

            return self._persist_entry(
                entries=entries,
                kind=EntryKind.TRANSITION,
                payload=normalized_payload,
            )

    def verify(self) -> tuple[str, ...]:
        """Return integrity violations; empty means the local chain is intact."""

        try:
            self.entries()
        except LedgerIntegrityError as error:
            return (str(error),)
        return ()

    def completed_round_count(self) -> int:
        """How many legacy loose rounds this run durably completed."""

        return len(self.entries(EntryKind.ROUND))
