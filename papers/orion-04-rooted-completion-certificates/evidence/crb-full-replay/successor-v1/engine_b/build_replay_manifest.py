#!/usr/bin/env python3
"""Build and verify the ORION-04 replay-successor packet manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import engine_b as eb


SCHEMA = "ORION.ORION04.CRB.ReplaySourceManifest.v1"
CURRENT_MAIN_BASE = "f9ea29855578fadd131c115a24dd0e927def4776"
REPLAY_PATHS = tuple(
    sorted(
        (
            "AWAITING_NEW_ONE_SHOT_AUTHORIZATION.json",
            "DEVELOPMENT_PACKET_V1.json",
            "DONOR_DISPOSITION_V1.json",
            "DONOR_SOURCE_MANIFEST_V1.json",
            "GLOBAL_REGISTRY_PREBIND_V1.json",
            "PRESERVED_FAILURE_BINDING_V1.json",
            "README.md",
            "engine_b/EVIDENCE_MANIFEST.json",
            "engine_b/SOURCE_MANIFEST.json",
            "engine_b/SUBMISSION_BLOCKER.json",
            "engine_b/historical/JOB_3544056_CONSUMED_AUTHORIZATION.json",
            "engine_b/historical/README.md",
            "engine_b/historical/STALE_CURRENT_ROOT_FULL_REPLAY_REVIEW.json",
            "engine_b/historical/job_nq_r8_engine_b.slurm",
            "engine_b/historical/job_nq_r9_crb_full_census.slurm",
            "engine_b/historical/submit_crb_full_census.sh",
        )
    )
)


class ReplayManifestMismatch(RuntimeError):
    pass


def _core(files: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "paper_id": "ORION-04",
        "current_main_base": CURRENT_MAIN_BASE,
        "status": "AWAITING_NEW_ONE_SHOT_AUTHORIZATION",
        "authority": {
            "d2": "CANNOT_CHECK",
            "d3": "CANNOT_CHECK",
            "d4": "OPEN",
            "d4_rounds_consumed": 0,
            "external_authority": False,
            "journal_authority": False,
            "scientific_authority_delta": "NONE",
        },
        "files": files,
    }


def build_replay_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: list[dict[str, Any]] = []
    for relative in REPLAY_PATHS:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ReplayManifestMismatch(f"replay packet file is unavailable: {relative}")
        data = path.read_bytes()
        files.append(
            {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        )
    core = _core(files)
    return {**core, "manifest_sha256": hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest()}


def verify_replay_manifest(root: Path, manifest: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema",
        "paper_id",
        "current_main_base",
        "status",
        "authority",
        "files",
        "manifest_sha256",
    }
    if type(manifest) is not dict or set(manifest) != expected_fields:
        raise ReplayManifestMismatch("replay manifest fields are not exact")
    files = manifest.get("files")
    if type(files) is not list or any(
        type(item) is not dict or set(item) != {"path", "bytes", "sha256"} for item in files
    ):
        raise ReplayManifestMismatch("replay manifest records are malformed")
    if tuple(item["path"] for item in files) != REPLAY_PATHS:
        raise ReplayManifestMismatch("replay manifest allowlist mismatch")
    core = _core(files)
    if any(manifest.get(key) != value for key, value in core.items() if key != "files"):
        raise ReplayManifestMismatch("replay manifest identity or authority mismatch")
    if manifest.get("manifest_sha256") != hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest():
        raise ReplayManifestMismatch("replay manifest content digest mismatch")
    root = root.resolve()
    for item in files:
        path = root / item["path"]
        if path.is_symlink() or not path.is_file():
            raise ReplayManifestMismatch(f"replay packet file is unavailable: {item['path']}")
        data = path.read_bytes()
        if {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} != {
            "bytes": item["bytes"],
            "sha256": item["sha256"],
        }:
            raise ReplayManifestMismatch(f"replay manifest mismatch: {item['path']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--output", type=Path, default=root / "REPLAY_SOURCE_MANIFEST_V1.json")
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verify:
        manifest = json.loads(args.output.read_text(encoding="utf-8"))
        verify_replay_manifest(args.root, manifest)
    else:
        manifest = build_replay_manifest(args.root)
        temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
        temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, args.output)
    print(manifest["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
