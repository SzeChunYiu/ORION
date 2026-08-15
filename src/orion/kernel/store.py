from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

_GENESIS_HASH = "0" * 64
_LEDGER_FILENAME = "ledger.jsonl"


class EntryKind(str, Enum):
    """The durable record kinds a self-driving ORION run may append."""

    ROUND = "ROUND"
    ANSWER = "ANSWER"
    GRADING = "GRADING"
    EPISODE = "EPISODE"
    RECEIPT = "RECEIPT"
    GUARD = "GUARD"
    RESIDUAL = "RESIDUAL"


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

    def append(self, kind: EntryKind, payload: Mapping[str, Any]) -> LedgerEntry:
        """Append one entry, chained to the verified current head."""

        entries = self.entries()
        sequence = len(entries)
        prev_hash = entries[-1].entry_hash if entries else _GENESIS_HASH
        normalized = json.loads(canonical_bytes(payload))
        entry = LedgerEntry(
            sequence=sequence,
            kind=kind,
            payload=normalized,
            prev_hash=prev_hash,
            entry_hash=compute_entry_hash(sequence, kind, normalized, prev_hash),
        )
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        "sequence": entry.sequence,
                        "kind": entry.kind.value,
                        "payload": entry.payload,
                        "prev_hash": entry.prev_hash,
                        "entry_hash": entry.entry_hash,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )
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
