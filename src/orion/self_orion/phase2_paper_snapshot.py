from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from orion.self_orion.subject_binding import RepositorySubjectAttestation


PAPER_PROGRAMME_SNAPSHOT_SCHEMA = "Phase2PaperProgrammeSnapshot.v1"
REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES = (
    "research/paper-programme-v1/",
    "papers/orion-11-recursive-epistemic-reconstruction/",
    "papers/orion-12-open-world-scientific-discovery/",
    "papers/orion-13-global-knowledge-portrait/",
    "papers/orion-14-verified-scientific-discovery/",
    "papers/orion-15-self-orion/",
)


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _is_required_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES)


@dataclass(frozen=True)
class PaperProgrammeEntry:
    path: str
    content_sha256: str

    def __post_init__(self) -> None:
        if not self.path.strip() or not _sha256(self.content_sha256):
            raise ValueError("paper programme entry path/content SHA-256 are required")
        if not _is_required_path(self.path):
            raise ValueError("paper programme entry lies outside the frozen paper prefixes")


@dataclass(frozen=True)
class Phase2PaperProgrammeSnapshot:
    snapshot_id: str
    integration_commit_oid: str
    entries: tuple[PaperProgrammeEntry, ...]

    def __post_init__(self) -> None:
        if not self.snapshot_id.strip() or not self.integration_commit_oid.strip():
            raise ValueError("paper programme snapshot identity/commit are required")
        paths = tuple(item.path for item in self.entries)
        if not paths or paths != tuple(sorted(paths)) or len(paths) != len(set(paths)):
            raise ValueError("paper programme snapshot paths must be non-empty, unique and sorted")
        for prefix in REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES:
            if not any(path.startswith(prefix) for path in paths):
                raise ValueError(f"paper programme snapshot is missing required prefix: {prefix}")

    @property
    def artifact_hash(self) -> str:
        payload = {
            "snapshot_id": self.snapshot_id,
            "integration_commit_oid": self.integration_commit_oid,
            "required_prefixes": list(REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES),
            "entries": [
                {"path": item.path, "content_sha256": item.content_sha256}
                for item in self.entries
            ],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def paper_programme_snapshot_from_subject(
    subject: RepositorySubjectAttestation,
    *,
    snapshot_id: str = "phase2:paper-programme",
) -> Phase2PaperProgrammeSnapshot:
    entries = tuple(
        PaperProgrammeEntry(item.path, item.content_sha256)
        for item in subject.tracked_objects
        if _is_required_path(item.path)
    )
    return Phase2PaperProgrammeSnapshot(
        snapshot_id=snapshot_id,
        integration_commit_oid=subject.commit_oid,
        entries=entries,
    )


def expected_paper_programme_entries(
    subject: RepositorySubjectAttestation,
) -> tuple[PaperProgrammeEntry, ...]:
    return paper_programme_snapshot_from_subject(subject).entries


def paper_programme_snapshot_to_dict(
    snapshot: Phase2PaperProgrammeSnapshot,
) -> dict[str, object]:
    return {
        "schema": PAPER_PROGRAMME_SNAPSHOT_SCHEMA,
        "artifact_hash": snapshot.artifact_hash,
        "snapshot_id": snapshot.snapshot_id,
        "integration_commit_oid": snapshot.integration_commit_oid,
        "required_prefixes": list(REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES),
        "entries": [
            {"path": item.path, "content_sha256": item.content_sha256}
            for item in snapshot.entries
        ],
    }


def write_paper_programme_snapshot(
    snapshot: Phase2PaperProgrammeSnapshot, path: Path | str
) -> None:
    Path(path).write_text(
        json.dumps(paper_programme_snapshot_to_dict(snapshot), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


def load_paper_programme_snapshot(path: Path | str) -> Phase2PaperProgrammeSnapshot:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema") != PAPER_PROGRAMME_SNAPSHOT_SCHEMA:
        raise ValueError(
            f"paper programme snapshot schema must be {PAPER_PROGRAMME_SNAPSHOT_SCHEMA}"
        )
    if tuple(raw.get("required_prefixes", ())) != REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES:
        raise ValueError("paper programme frozen required prefixes changed")
    entries_raw = raw.get("entries")
    if not isinstance(entries_raw, list):
        raise ValueError("paper programme snapshot entries must be an array")
    snapshot = Phase2PaperProgrammeSnapshot(
        snapshot_id=raw["snapshot_id"],
        integration_commit_oid=raw["integration_commit_oid"],
        entries=tuple(
            PaperProgrammeEntry(
                path=item["path"],
                content_sha256=item["content_sha256"],
            )
            for item in entries_raw
        ),
    )
    if raw.get("artifact_hash") != snapshot.artifact_hash:
        raise ValueError("paper programme snapshot artifact hash mismatch")
    return snapshot


__all__ = [
    "PAPER_PROGRAMME_SNAPSHOT_SCHEMA",
    "REQUIRED_PHASE2_PAPER_PROGRAMME_PREFIXES",
    "PaperProgrammeEntry",
    "Phase2PaperProgrammeSnapshot",
    "expected_paper_programme_entries",
    "load_paper_programme_snapshot",
    "paper_programme_snapshot_from_subject",
    "paper_programme_snapshot_to_dict",
    "write_paper_programme_snapshot",
]
