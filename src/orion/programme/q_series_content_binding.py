"""Content-addressed drift checking for the canonical ORION-Q paper set.

The older global paper survey predates the Q namespace. This checker binds the
canonical files selected by ``Q_SERIES_FINAL_SPEC_V1.json`` without pretending
that historical drafts are part of the submission package.

Git blob identities are used because they are already the repository's immutable
content identities. The checker recomputes them from working-tree bytes rather
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
    return hashlib.sha1(header + data).hexdigest()  # noqa: S324 - Git identity, not security


def load_q_series_content_binding(repo_root: Path) -> dict[str, Any]:
    """Load and validate the committed cross-paper Q-series binding manifest."""

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
    for index, row in enumerate(files):
        if not isinstance(row, dict):
            raise TypeError(f"Q-series binding row {index} must be an object")
        path_value = row.get("path")
        expected = row.get("git_blob_sha1")
        if not isinstance(path_value, str) or not path_value.strip():
            raise ValueError(f"Q-series binding row {index} path must be non-empty")
        if not isinstance(expected, str) or len(expected) != 40:
            raise ValueError(f"{path_value}: invalid Git blob SHA-1")
    return raw


def q_series_bound_rows_for_directory(
    repo_root: Path, directory: Path
) -> tuple[dict[str, Any], ...]:
    """Rows from the cross-paper binding that belong to one paper directory.

    Returns an empty tuple when the Q-series binding is absent or when the
    directory is not one of its watched surfaces. Parsing errors deliberately
    propagate so a malformed declared binding cannot silently degrade to UNBOUND.
    """

    path = repo_root / BINDING_PATH
    if not path.is_file():
        return ()
    raw = load_q_series_content_binding(repo_root)
    relative = directory.relative_to(repo_root).as_posix().rstrip("/") + "/"
    rows = tuple(
        row for row in raw["files"] if str(row.get("path", "")).startswith(relative)
    )
    seen = [str(row["path"]) for row in rows]
    if len(seen) != len(set(seen)):
        raise ValueError(f"duplicate Q-series bound path under {relative}")
    return rows


def inspect_q_series_content_binding(repo_root: Path) -> QSeriesContentBindingReport:
    raw = load_q_series_content_binding(repo_root)
    drifted: list[str] = []
    missing: list[str] = []
    seen: set[str] = set()

    for row in raw["files"]:
        path_value = str(row["path"])
        expected = str(row["git_blob_sha1"])
        if path_value in seen:
            raise ValueError(f"duplicate Q-series bound path: {path_value}")
        seen.add(path_value)

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
    "load_q_series_content_binding",
    "q_series_bound_rows_for_directory",
    "require_q_series_content_binding",
]
