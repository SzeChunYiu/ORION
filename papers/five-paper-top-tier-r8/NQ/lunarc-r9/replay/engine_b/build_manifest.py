#!/usr/bin/env python3
"""Build and verify the deterministic NQ Engine B source manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import engine_b as eb


class SourceManifestMismatch(RuntimeError):
    pass


SOURCE_PATHS = tuple(
    sorted(
        (
            "BLINDING_DISCLOSURE.json",
            "CERTIFICATE_SCHEMA.json",
            "EXTERNAL_DRUP_CHECKER_PROTOCOL.json",
            "FULL_CENSUS_DECLARED_MANIFEST.json",
            "FULL_CENSUS_MANIFEST_SCHEMA.json",
            "FULL_REPLAY_AUTHORIZATION.json",
            "INPUT_SCHEMA.json",
            "PROOF_OF_COMPLETENESS.md",
            "README.md",
            "requirements.txt",
            "SOURCE_PROTOCOL.json",
            "SUBMISSION_BLOCKER.json",
            "batch_engine_b.py",
            "batch_external_drup.py",
            "build_manifest.py",
            "crb_census.py",
            "docs/plans/2026-08-26-crb-full-manifest-design.md",
            "docs/plans/2026-08-26-crb-full-manifest-implementation.md",
            "docs/plans/2026-08-27-crb-census-coverage-argument.md",
            "engine_b.py",
            "external_drup.py",
            "full_manifest.py",
            "run_engine_b.py",
            "slurm/job_nq_r8_engine_b.slurm",
            "slurm/job_nq_r9_crb_full_census.slurm",
            "slurm/submit_crb_full_census.sh",
            "symmetry.py",
            "tests/test_batch_and_authority.py",
            "tests/test_batch_external_drup.py",
            "tests/test_crb_census.py",
            "tests/test_engine_b_primitives.py",
            "tests/test_external_drup.py",
            "tests/test_full_manifest.py",
            "tests/test_source_packet.py",
            "verify_receipt.py",
        )
    )
)


def _core(files: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "ORION.NQ.EngineB.SourceManifest.v1",
        "subject_commit": eb.SUBJECT_COMMIT,
        "files": files,
    }


def build_source_manifest(root: Path, paths: Sequence[str]) -> dict[str, Any]:
    root = root.resolve()
    normalized = sorted(set(paths))
    if len(normalized) != len(paths):
        raise ValueError("source manifest paths must be unique")
    files = []
    for relative in normalized:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
            raise ValueError(f"source manifest path is not canonical: {relative}")
        source = root / path
        if source.is_symlink():
            raise ValueError(f"source manifest file must not be a symlink: {relative}")
        data = source.read_bytes()
        files.append(
            {
                "path": relative,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    core = _core(files)
    return {
        **core,
        "manifest_sha256": hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest(),
    }


def verify_source_manifest(root: Path, manifest: Mapping[str, Any]) -> None:
    if type(manifest) is not dict or set(manifest) != {
        "schema",
        "subject_commit",
        "files",
        "manifest_sha256",
    }:
        raise SourceManifestMismatch("source manifest fields are not exact")
    if manifest["schema"] != "ORION.NQ.EngineB.SourceManifest.v1":
        raise SourceManifestMismatch("source manifest schema mismatch")
    if manifest["subject_commit"] != eb.SUBJECT_COMMIT:
        raise SourceManifestMismatch("source manifest subject mismatch")
    files = manifest["files"]
    if type(files) is not list or any(
        type(record) is not dict or set(record) != {"path", "bytes", "sha256"} for record in files
    ):
        raise SourceManifestMismatch("source manifest file records are invalid")
    paths = [record["path"] for record in files]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise SourceManifestMismatch("source manifest paths are not sorted and unique")
    core = _core(files)
    expected_digest = hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest()
    if manifest["manifest_sha256"] != expected_digest:
        raise SourceManifestMismatch("source manifest content digest mismatch")
    root = root.resolve()
    for record in files:
        path = Path(record["path"])
        if path.is_absolute() or ".." in path.parts:
            raise SourceManifestMismatch(f"source path is not canonical: {path}")
        source = root / path
        if source.is_symlink():
            raise SourceManifestMismatch(f"source path is a symlink: {path}")
        try:
            data = source.read_bytes()
        except OSError as error:
            raise SourceManifestMismatch(f"source file is unavailable: {path}") from error
        observed = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if observed != {"bytes": record["bytes"], "sha256": record["sha256"]}:
            raise SourceManifestMismatch(f"source manifest mismatch for {path}")


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--output", type=Path, default=root / "SOURCE_MANIFEST.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_source_manifest(args.root, SOURCE_PATHS)
    temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, args.output)
    print(manifest["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
