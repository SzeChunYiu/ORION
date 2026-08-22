"""Content-addressed drift checking for the canonical ORION-Q paper set.

The older global paper survey predates the Q namespace.  This checker binds the
canonical files selected by ``Q_SERIES_FINAL_SPEC_V1.json`` without pretending
that historical drafts are part of the submission package.

Git blob identities are used because they are already the repository's immutable
content identities.  The checker recomputes them from working-tree bytes rather
than asking Git, so a local uncommitted edit is detected as drift too.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BINDING_PATH = Path("papers/Q_SERIES_CONTENT_BINDING_V1.json")
BINDING_SCHEMA = "ORION.QSeriesContentBinding.v1"


@dataclass(frozen=True)
class QSeriesContentBindingReport:
    files_bound: int
    drifted_paths: tuple[str, ...]
    missing_paths: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.drifted_paths and not self.missing_paths

    def as_json(self) -> dict[str, Any]:
        return {
            "schema": BINDING_SCHEMA,
            "files_bound": self.files_bound,
            "drifted_paths": list(self.drifted_paths),
            "missing_paths": list(self.missing_paths),
            "clean": self.clean,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
        }


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git object identity, not security


def _load_binding(repo_root: Path) -> dict[str, Any]:
    path = repo_root / BINDING_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("Q-series content binding must be a JSON object")
    if raw.get("schema") != BINDING_SCHEMA:
        raise ValueError("unsupported Q-series content binding schema")
    if raw.get("hash_kind") != "git_blob_sha1":
        raise ValueError("Q-series content binding must use git_blob_sha1")
    files = raw.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("Q-series content binding requires at least one file")
    return raw


def inspect_q_series_content_binding(repo_root: Path) -> QSeriesContentBindingReport:
    raw = _load_binding(repo_root)
    drifted: list[str] = []
    missing: list[str] = []
    seen: set[str] = set()

    for row in raw["files"]:
        if not isinstance(row, dict):
            raise TypeError("Q-series binding file row must be an object")
        path_value = row.get("path")
        expected = row.get("git_blob_sha1")
        if not isinstance(path_value, str) or not path_value.strip():
            raise ValueError("Q-series binding path must be non-empty")
        if path_value in seen:
            raise ValueError(f"duplicate Q-series bound path: {path_value}")
        seen.add(path_value)
        if not isinstance(expected, str) or len(expected) != 40:
            raise ValueError(f"{path_value}: invalid Git blob SHA-1")

        path = repo_root / path_value
        if not path.is_file():
            missing.append(path_value)
            continue
        actual = git_blob_sha1(path.read_bytes())
        if actual != expected:
            drifted.append(path_value)

    return QSeriesContentBindingReport(
        files_bound=len(seen),
        drifted_paths=tuple(sorted(drifted)),
        missing_paths=tuple(sorted(missing)),
    )


def require_q_series_content_binding(repo_root: Path) -> None:
    report = inspect_q_series_content_binding(repo_root)
    if not report.clean:
        raise RuntimeError(
            "Q-series canonical publication content drifted; regenerate "
            f"{BINDING_PATH.as_posix()} after reviewing the paper/spec change. "
            f"drifted={report.drifted_paths!r} missing={report.missing_paths!r}"
        )


__all__ = [
    "BINDING_PATH",
    "BINDING_SCHEMA",
    "QSeriesContentBindingReport",
    "git_blob_sha1",
    "inspect_q_series_content_binding",
    "require_q_series_content_binding",
]
