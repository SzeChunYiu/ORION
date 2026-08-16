from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


PAPER_PROGRAMME_SNAPSHOT_SCHEMA = "Phase2PaperProgrammeSnapshot.v1"
PAPER_PROGRAMME_PREFIX = "research/paper-programme-v1/"
REQUIRED_PHASE2_PAPER_PROGRAMME_PATHS = (
    PAPER_PROGRAMME_PREFIX + "FLAGSHIP_FALSIFIER_RESULTS_V1.md",
    PAPER_PROGRAMME_PREFIX + "JOURNAL_READINESS_AUDIT_2026-08-16.md",
    PAPER_PROGRAMME_PREFIX + "JOURNAL_READINESS_STANDARD.md",
    PAPER_PROGRAMME_PREFIX + "NEAREST_WORK_ATLAS.md",
    PAPER_PROGRAMME_PREFIX + "NEAREST_WORK_SUPPLEMENT_2026-08-16.md",
    PAPER_PROGRAMME_PREFIX + "PAPER_01_RECURSIVE_RECONSTRUCTION.md",
    PAPER_PROGRAMME_PREFIX + "PAPER_02_OPEN_WORLD_DISCOVERY.md",
    PAPER_PROGRAMME_PREFIX + "PAPER_03_GLOBAL_PORTRAIT.md",
    PAPER_PROGRAMME_PREFIX + "PAPER_04_VERIFIED_DISCOVERY.md",
    PAPER_PROGRAMME_PREFIX + "PAPER_05_SELF_ORION.md",
    PAPER_PROGRAMME_PREFIX + "README.md",
    PAPER_PROGRAMME_PREFIX + "SATURATION_LEDGER.md",
)


def _sha256(value: str) -> bool:
    return len(value) == 64 and all(character in "0123456789abcdef" for character in value)


@dataclass(frozen=True)
class PaperProgrammeEntry:
    path: str
    content_sha256: str

    def __post_init__(self) -> None:
        if not self.path.strip() or not _sha256(self.content_sha256):
            raise ValueError("paper programme entry path/content SHA-256 are required")


@dataclass(frozen=True)
class Phase2PaperProgrammeSnapshot:
    snapshot_id: str
    integration_commit_oid: str
    entries: tuple[PaperProgrammeEntry, ...]

    def __post_init__(self) -> None:
        if not self.snapshot_id.strip() or not self.integration_commit_oid.strip():
            raise ValueError("paper programme snapshot identity/commit are required")
        paths = tuple(item.path for item in self.entries)
        if paths != REQUIRED_PHASE2_PAPER_PROGRAMME_PATHS:
            raise ValueError("paper programme snapshot must cover the frozen required path set exactly")

    @property
    def artifact_hash(self) -> str:
        payload = {
            "snapshot_id": self.snapshot_id,
            "integration_commit_oid": self.integration_commit_oid,
            "required_paths": list(REQUIRED_PHASE2_PAPER_PROGRAMME_PATHS),
            "entries": [
                {"path": item.path, "content_sha256": item.content_sha256}
                for item in self.entries
            ],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def paper_programme_snapshot_to_dict(
    snapshot: Phase2PaperProgrammeSnapshot,
) -> dict[str, object]:
    return {
        "schema": PAPER_PROGRAMME_SNAPSHOT_SCHEMA,
        "artifact_hash": snapshot.artifact_hash,
        "snapshot_id": snapshot.snapshot_id,
        "integration_commit_oid": snapshot.integration_commit_oid,
        "required_paths": list(REQUIRED_PHASE2_PAPER_PROGRAMME_PATHS),
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
    if tuple(raw.get("required_paths", ())) != REQUIRED_PHASE2_PAPER_PROGRAMME_PATHS:
        raise ValueError("paper programme frozen required paths changed")
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
    "REQUIRED_PHASE2_PAPER_PROGRAMME_PATHS",
    "PaperProgrammeEntry",
    "Phase2PaperProgrammeSnapshot",
    "load_paper_programme_snapshot",
    "paper_programme_snapshot_to_dict",
    "write_paper_programme_snapshot",
]
