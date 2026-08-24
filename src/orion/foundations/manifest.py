"""Content binding for the self-contained foundations tranche."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

from .ledger import BASE_COMMIT, BRANCH

ALLOWED_PREFIXES = (
    ".github/workflows/orion-foundations.yml",
    "research/orion-foundations-v2/",
    "src/orion/foundations/",
    "tests/foundations/",
)
EXCLUDED_NAMES = {"CONTENT_MANIFEST_V1.json", "SHA256SUMS"}
PROTECTED_PREFIX = (
    "development/"
    "p1-scienceagentbench-protected-rr1-one-tuple-finalizer-freeze-v1-2026-08-24/"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _candidate_paths(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if path.name in EXCLUDED_NAMES:
            continue
        if not any(
            relative == prefix or relative.startswith(prefix)
            for prefix in ALLOWED_PREFIXES
        ):
            continue
        yield path


def build_content_manifest(root: Path) -> dict[str, Any]:
    entries = []
    for path in sorted(_candidate_paths(root)):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(PROTECTED_PREFIX):
            raise ValueError(f"protected P1 path entered foundations manifest: {relative}")
        entries.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": "orion.foundations.content-manifest.v1",
        "issue": 1220,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "authority_delta": "NONE",
        "p1_rr1_coordination": "UNTOUCHED",
        "entries": entries,
    }


def render_sha256sums(manifest: dict[str, Any], manifest_path: Path) -> str:
    lines = [f"{entry['sha256']}  {entry['path']}" for entry in manifest["entries"]]
    lines.append(
        f"{sha256_file(manifest_path)}  "
        "research/orion-foundations-v2/CONTENT_MANIFEST_V1.json"
    )
    return "\n".join(lines) + "\n"
