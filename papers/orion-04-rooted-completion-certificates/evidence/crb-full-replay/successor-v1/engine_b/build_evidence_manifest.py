#!/usr/bin/env python3
"""Build and verify the bounded ORION-04 CR-B engineering-evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import engine_b as eb


SCHEMA = "ORION.ORION04.CRB.EvidenceManifest.v1"
EVIDENCE_PATHS = tuple(
    sorted(
        (
            "LOCAL_ENVIRONMENT.json",
            "NON_OUTCOME_VALIDATION.json",
            "FULL_CENSUS_DECLARATION_RECEIPT.json",
            "PYTHON_SAT_INSTALL_GREEN.log",
            "PYTHON_SAT_INSTALL_RED_ENOSPC.log",
            "SOURCE_MANIFEST.json",
            "controls/BATCH_CERTIFICATES.jsonl",
            "controls/BATCH_CONTROL_RECEIPT.json",
            "controls/PYSAT_SAT_CONTROL.json",
            "controls/PYSAT_UNSAT_CONTROL.json",
            "controls/batch_input/INPUT_MANIFEST.json",
            "controls/batch_input/coverage.json",
            "controls/batch_input/records.jsonl",
            "controls/batch_proofs/negative-batch.cnf",
            "controls/batch_proofs/negative-batch.drup",
            "controls/external_drup/EXTERNAL_DRUP_CONTROL_RECEIPT.json",
            "controls/external_drup/UNSAT_CONTROL_CERTIFICATE_V2.json",
            "controls/external_drup/negative-batch.drat-trim.stderr",
            "controls/external_drup/negative-batch.drat-trim.stdout",
            "controls/negative.drup",
        )
    )
)


class EvidenceManifestMismatch(RuntimeError):
    pass


def _core(files: list[dict[str, Any]]) -> dict[str, Any]:
    return {"schema": SCHEMA, "subject_commit": eb.SUBJECT_COMMIT, "files": files}


def build_evidence_manifest(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: list[dict[str, Any]] = []
    for relative in EVIDENCE_PATHS:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise EvidenceManifestMismatch(f"evidence file is unavailable or unsafe: {relative}")
        data = path.read_bytes()
        files.append(
            {"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        )
    core = _core(files)
    return {**core, "manifest_sha256": hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest()}


def verify_evidence_manifest(root: Path, manifest: Mapping[str, Any]) -> None:
    if type(manifest) is not dict or set(manifest) != {
        "schema",
        "subject_commit",
        "files",
        "manifest_sha256",
    }:
        raise EvidenceManifestMismatch("evidence manifest fields are not exact")
    if manifest.get("schema") != SCHEMA or manifest.get("subject_commit") != eb.SUBJECT_COMMIT:
        raise EvidenceManifestMismatch("evidence manifest identity mismatch")
    files = manifest.get("files")
    if type(files) is not list or any(
        type(item) is not dict or set(item) != {"path", "bytes", "sha256"} for item in files
    ):
        raise EvidenceManifestMismatch("evidence manifest records are malformed")
    if tuple(item["path"] for item in files) != EVIDENCE_PATHS:
        raise EvidenceManifestMismatch("evidence manifest allowlist mismatch")
    core = _core(files)
    if manifest.get("manifest_sha256") != hashlib.sha256(eb.canonical_json_bytes(core)).hexdigest():
        raise EvidenceManifestMismatch("evidence manifest content digest mismatch")
    root = root.resolve()
    for item in files:
        path = root / item["path"]
        if path.is_symlink() or not path.is_file():
            raise EvidenceManifestMismatch(f"evidence file is unavailable: {item['path']}")
        data = path.read_bytes()
        if {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()} != {
            "bytes": item["bytes"],
            "sha256": item["sha256"],
        }:
            raise EvidenceManifestMismatch(f"evidence manifest mismatch: {item['path']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--output", type=Path, default=root / "EVIDENCE_MANIFEST.json")
    parser.add_argument("--verify", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.verify:
        manifest = json.loads(args.output.read_text(encoding="utf-8"))
        verify_evidence_manifest(args.root, manifest)
    else:
        manifest = build_evidence_manifest(args.root)
        temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
        temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, args.output)
    print(manifest["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
