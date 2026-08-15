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
        raise LedgerIntegrityError(f"line {line_number} is not valid JSON: {error}") from error
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

    The ledger is the whole persisted state: a run is resumed by replaying it,
    not by trusting a summary file. Each entry is chained to its predecessor,
    so a silently edited or truncated history is detectable rather than
    inherited as fact.
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
        """Serialize writers on an inode that is never replaced."""

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

    def append(
        self,
        kind: EntryKind,
        payload: Mapping[str, Any],
        *,
        expected_head: str | None | _ExpectedHeadUnset = _EXPECTED_HEAD_UNSET,
    ) -> LedgerEntry:
        """Atomically append an entry, optionally requiring an exact head hash.

        Passing ``expected_head=None`` explicitly requires an empty ledger.
        Omitting it performs an unconditional append against the locked,
        verified current head.
        """

        with self._exclusive_lock():
            self._cleanup_stale_temporaries()
            entries = self.entries()
            actual_head = entries[-1].entry_hash if entries else None
            if not isinstance(expected_head, _ExpectedHeadUnset) and expected_head != actual_head:
                raise StaleLedgerHead(expected_head, actual_head)

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

    def verify(self) -> tuple[str, ...]:
        """Return integrity violations; an empty tuple means the chain is intact."""

        try:
            self.entries()
        except LedgerIntegrityError as error:
            return (str(error),)
        return ()

    def completed_round_count(self) -> int:
        """How many rounds this run has already durably completed."""

        return len(self.entries(EntryKind.ROUND))
