from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER, INDEPENDENCE_TERMINAL

EXCLUDED_NAMES = {
    ".DS_Store",
    ".coverage",
    "SOURCE_MANIFEST.json",
    "SOURCE_MANIFEST.sha256",
    "ENGINEERING_RECEIPT.json",
    "TREE_DIGEST.sha256",
    "STAGING_TREE_MANIFEST.json",
    "STAGING_DIGEST.sha256",
    "TARGET_RESOURCE_PILOT_RECEIPT.json",
    "TARGET_RESOURCE_PILOT_SUBMISSION_CONTRACT.json",
    "coverage.json",
}
EXCLUDED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__", "htmlcov"}


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _included_files(root: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"source tree contains a symlink: {relative.as_posix()}")
        if not path.is_file():
            continue
        if path.name in EXCLUDED_NAMES or any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        files.append(path)
    return tuple(sorted(files, key=lambda item: item.relative_to(root).as_posix()))


def build_source_manifest(root: Path | str) -> dict[str, Any]:
    base = Path(root).resolve()
    if not base.is_dir():
        raise ValueError("manifest root must be a directory")
    entries = [
        {
            "path": path.relative_to(base).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in _included_files(base)
    ]
    tree_digest = hashlib.sha256(canonical_json_bytes(entries)).hexdigest()
    return {
        "schema_version": "nq-engine-a-source-manifest-v1",
        "independence_terminal": INDEPENDENCE_TERMINAL,
        "exposure_markers": [EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER],
        "files": entries,
        "source_tree_sha256": tree_digest,
    }


def verify_source_manifest(root: Path | str, manifest: object) -> tuple[str, ...]:
    base = Path(root).resolve()
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        return ("manifest structure is invalid",)
    errors: list[str] = []
    declared: dict[str, dict[str, Any]] = {}
    for raw_entry in manifest["files"]:
        if not isinstance(raw_entry, dict) or not isinstance(raw_entry.get("path"), str):
            errors.append("manifest contains an invalid file entry")
            continue
        relative = raw_entry["path"]
        candidate = Path(relative)
        if candidate.is_absolute() or ".." in candidate.parts:
            errors.append(f"unsafe manifest path: {relative}")
            continue
        if relative in declared:
            errors.append(f"duplicate manifest path: {relative}")
            continue
        declared[relative] = raw_entry
    actual_paths = {path.relative_to(base).as_posix(): path for path in _included_files(base)}
    for relative in sorted(set(actual_paths) - set(declared)):
        errors.append(f"unmanifested source: {relative}")
    for relative in sorted(set(declared) - set(actual_paths)):
        errors.append(f"manifested source missing: {relative}")
    for relative in sorted(set(actual_paths) & set(declared)):
        path = actual_paths[relative]
        entry = declared[relative]
        if entry.get("size_bytes") != path.stat().st_size:
            errors.append(f"size mismatch: {relative}")
        if entry.get("sha256") != sha256_file(path):
            errors.append(f"digest mismatch: {relative}")
    canonical_entries = [declared[path] for path in sorted(declared)]
    expected_tree = hashlib.sha256(canonical_json_bytes(canonical_entries)).hexdigest()
    if manifest.get("source_tree_sha256") != expected_tree:
        errors.append("source tree digest mismatch")
    if manifest.get("independence_terminal") != INDEPENDENCE_TERMINAL:
        errors.append("independence terminal mismatch")
    if manifest.get("exposure_markers") != [EXPECTED_OUTCOME_MARKER, EXPOSURE_MARKER]:
        errors.append("exposure marker mismatch")
    return tuple(errors)
