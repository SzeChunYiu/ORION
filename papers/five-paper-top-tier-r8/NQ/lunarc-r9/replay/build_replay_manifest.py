#!/usr/bin/env python3
"""Build the path-scoped source/result manifest for the R9 rank-two replay gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import control_replay as replay

REPLAY_PATHS = tuple(
    sorted(
        (
            "CONTROL_PROTOCOL.json",
            "README.md",
            "build_replay_manifest.py",
            "control_replay.py",
            "controls/RANK2_PREFIX_CONTROL_RECEIPT.json",
            "engine_b/NON_OUTCOME_VALIDATION.json",
            "engine_b/SOURCE_MANIFEST.json",
            "tests/test_control_replay.py",
            "verify_control_receipt.py",
        )
    )
)


class ReplayManifestMismatch(RuntimeError):
    pass


def _file_record(root: Path, relative: str) -> dict[str, Any]:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError(f"replay manifest path is not canonical: {relative}")
    source = root / path
    if source.is_symlink():
        raise ValueError(f"replay manifest path is a symlink: {relative}")
    data = source.read_bytes()
    return {
        "path": relative,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _core(files: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "ORION.NQ.R9.CRABRank2ReplayManifest.v1",
        "scientific_subject": replay.SCIENTIFIC_SUBJECT,
        "custody_parent": replay.CUSTODY_PARENT,
        "engine_a_tree": "b64f2188238e5fc869680ca117d241a0a3615349",
        "engine_b_independence": "STANDALONE_NO_ENGINE_A_IMPORT",
        "full_census_authorized": False,
        "files": files,
    }


def build_replay_manifest(root: Path, paths: Sequence[str] = REPLAY_PATHS) -> dict[str, Any]:
    normalized = tuple(sorted(set(paths)))
    if len(normalized) != len(paths):
        raise ValueError("replay manifest paths must be unique")
    files = [_file_record(root.resolve(), relative) for relative in normalized]
    core = _core(files)
    return {**core, "manifest_sha256": replay._sha256(core)}


def verify_replay_manifest(root: Path, manifest: Mapping[str, Any]) -> None:
    expected_fields = set(_core([])) | {"manifest_sha256"}
    if type(manifest) is not dict or set(manifest) != expected_fields:
        raise ReplayManifestMismatch("replay manifest fields are not exact")
    if manifest["schema"] != "ORION.NQ.R9.CRABRank2ReplayManifest.v1":
        raise ReplayManifestMismatch("replay manifest schema mismatch")
    if manifest["scientific_subject"] != replay.SCIENTIFIC_SUBJECT:
        raise ReplayManifestMismatch("replay manifest scientific subject mismatch")
    if manifest["custody_parent"] != replay.CUSTODY_PARENT:
        raise ReplayManifestMismatch("replay manifest custody parent mismatch")
    if manifest["engine_b_independence"] != "STANDALONE_NO_ENGINE_A_IMPORT":
        raise ReplayManifestMismatch("replay manifest independence boundary mismatch")
    if manifest["full_census_authorized"] is not False:
        raise ReplayManifestMismatch("replay manifest unexpectedly authorizes full census")
    files = manifest["files"]
    if type(files) is not list or [record.get("path") for record in files] != sorted(
        record.get("path") for record in files
    ):
        raise ReplayManifestMismatch("replay manifest files are not sorted")
    if manifest["manifest_sha256"] != replay._sha256(_core(files)):
        raise ReplayManifestMismatch("replay manifest digest mismatch")
    for record in files:
        try:
            observed = _file_record(root.resolve(), record["path"])
        except (KeyError, OSError, TypeError, ValueError) as error:
            raise ReplayManifestMismatch("replay manifest file is unavailable") from error
        if observed != record:
            raise ReplayManifestMismatch(f"replay manifest mismatch for {record['path']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=replay.REPLAY_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=replay.REPLAY_ROOT / "REPLAY_SOURCE_MANIFEST.json",
    )
    args = parser.parse_args()
    manifest = build_replay_manifest(args.root)
    temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, args.output)
    verify_replay_manifest(args.root, manifest)
    print(manifest["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
