#!/usr/bin/env python3
"""Verify every frozen Mathlib corpus byte before analysis or native replay."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "MATHLIB_CORPUS_V2_MANIFEST.json"
CORPUS_ROOT = HERE / "corpus" / "mathlib4_e72c1e277f31"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["source"]["commit"] == "e72c1e277f31441626621f7d0c7207862fc25569"
    assert manifest["source"]["lean_toolchain"] == "leanprover/lean4:v4.34.0-rc1"
    assert manifest["selection"]["outcome_blind"] is True

    expected_paths = set()
    for item in manifest["files"] + manifest["support_files"]:
        path = CORPUS_ROOT / item["path"]
        expected_paths.add(item["path"])
        if not path.is_file():
            raise AssertionError(f"missing frozen source: {item['path']}")
        if path.stat().st_size != item["bytes"]:
            raise AssertionError(f"byte-count drift: {item['path']}")
        if sha256(path) != item["sha256"]:
            raise AssertionError(f"digest drift: {item['path']}")

    actual_sources = {
        path.relative_to(CORPUS_ROOT).as_posix()
        for path in (CORPUS_ROOT / "Mathlib").rglob("*.lean")
    }
    expected_sources = {item["path"] for item in manifest["files"]}
    if actual_sources != expected_sources:
        raise AssertionError("frozen Mathlib source set drift")
    if len(expected_sources) != manifest["selected_files"]:
        raise AssertionError("selected-file count drift")
    if sum(item["bytes"] for item in manifest["files"]) != manifest["selected_bytes"]:
        raise AssertionError("selected-byte total drift")
    print(
        "P10 Mathlib corpus integrity: PASS "
        f"({len(expected_sources)} files, {manifest['selected_bytes']} bytes)"
    )


if __name__ == "__main__":
    main()
