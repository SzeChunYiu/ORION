#!/usr/bin/env python3
"""Materialize the prospectively frozen, outcome-blind native audit sample."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CORPUS_MANIFEST = ROOT / "MATHLIB_CORPUS_V2_MANIFEST.json"
PROTOCOL = ROOT / "NATIVE_VERIFICATION_PROTOCOL_V1.json"
OUTPUT = ROOT / "NATIVE_VERIFICATION_SAMPLE_V1.json"
MODULE_SALT = "ORION-P10-NATIVE-MODULES-V1"
FILE_SALT = "ORION-P10-NATIVE-FILE-V1"


def rank(value: str, salt: str) -> str:
    return hashlib.sha256(f"{value}\0{salt}".encode()).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    protocol = json.loads(PROTOCOL.read_text())
    manifest = json.loads(CORPUS_MANIFEST.read_text())
    if sha256(CORPUS_MANIFEST) != protocol["source"]["corpus_manifest_sha256"]:
        raise AssertionError("corpus manifest differs from frozen protocol")

    modules = sorted(
        {item["top_module"] for item in manifest["files"]},
        key=lambda module: rank(module, MODULE_SALT),
    )[: protocol["selection"]["sample_size"]]
    sample = []
    for module in modules:
        candidates = [item for item in manifest["files"] if item["top_module"] == module]
        item = min(candidates, key=lambda candidate: rank(candidate["path"], FILE_SALT))
        sample.append(
            {
                "top_module": module,
                "module_rank_sha256": rank(module, MODULE_SALT),
                "path": item["path"],
                "path_rank_sha256": rank(item["path"], FILE_SALT),
                "source_sha256": item["sha256"],
                "bytes": item["bytes"],
            }
        )

    output = {
        "schema": "P10NativeVerificationSample.v1",
        "protocol_sha256": sha256(PROTOCOL),
        "corpus_manifest_sha256": sha256(CORPUS_MANIFEST),
        "sample_size": len(sample),
        "population_size": manifest["selected_files"],
        "files": sample,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(f"P10 native audit sample: FROZEN ({len(sample)} of {manifest['selected_files']} files)")


if __name__ == "__main__":
    main()
