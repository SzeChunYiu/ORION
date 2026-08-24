#!/usr/bin/env python3
"""Materialize the frozen, outcome-blind P10 Mathlib source sample."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPECTED_COMMIT = "e72c1e277f31441626621f7d0c7207862fc25569"
EXPECTED_TOOLCHAIN = "leanprover/lean4:v4.34.0-rc1"
SELECTION_SALT = "ORION-P10-MATHLIB-V2"
EXCLUDED_TOP_MODULES = {"Deprecated", "Testing"}
FILES_PER_TOP_MODULE = 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()


def selection_key(relative_path: str) -> tuple[str, str]:
    digest = hashlib.sha256(f"{relative_path}\0{SELECTION_SALT}".encode()).hexdigest()
    return digest, relative_path


def select_paths(mathlib_root: Path) -> tuple[list[Path], dict[str, int]]:
    by_module: dict[str, list[Path]] = {}
    for path in (mathlib_root / "Mathlib").rglob("*.lean"):
        relative = path.relative_to(mathlib_root)
        top_module = relative.parts[1]
        if top_module in EXCLUDED_TOP_MODULES:
            continue
        by_module.setdefault(top_module, []).append(path)

    selected: list[Path] = []
    counts: dict[str, int] = {}
    for top_module in sorted(by_module):
        ranked = sorted(
            by_module[top_module],
            key=lambda path: selection_key(path.relative_to(mathlib_root).as_posix()),
        )
        chosen = ranked[:FILES_PER_TOP_MODULE]
        selected.extend(chosen)
        counts[top_module] = len(chosen)
    return selected, counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mathlib-root", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=HERE / "corpus" / f"mathlib4_{EXPECTED_COMMIT[:12]}",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=HERE / "MATHLIB_CORPUS_V2_MANIFEST.json",
    )
    args = parser.parse_args()
    source_root = args.mathlib_root.resolve()
    output_root = args.output_root.resolve()

    if git_head(source_root) != EXPECTED_COMMIT:
        raise SystemExit("Mathlib source revision mismatch")
    if (source_root / "lean-toolchain").read_text().strip() != EXPECTED_TOOLCHAIN:
        raise SystemExit("Mathlib Lean toolchain mismatch")
    if output_root.exists() or args.manifest.exists():
        raise SystemExit("refusing to overwrite an existing corpus or manifest")

    selected, counts = select_paths(source_root)
    files = []
    for source in sorted(selected, key=lambda item: item.relative_to(source_root).as_posix()):
        relative = source.relative_to(source_root)
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        files.append(
            {
                "path": relative.as_posix(),
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
                "top_module": relative.parts[1],
            }
        )

    support_files = []
    for name in ["LICENSE", "lean-toolchain", "lakefile.lean", "lake-manifest.json"]:
        source = source_root / name
        destination = output_root / name
        shutil.copy2(source, destination)
        support_files.append(
            {"path": name, "bytes": source.stat().st_size, "sha256": sha256(source)}
        )

    manifest = {
        "schema": "P10MathlibCorpusManifest.v2",
        "source": {
            "repository": "https://github.com/leanprover-community/mathlib4",
            "commit": EXPECTED_COMMIT,
            "commit_time": "2026-08-18T08:09:40Z",
            "lean_toolchain": EXPECTED_TOOLCHAIN,
            "license": "Apache-2.0",
        },
        "selection": {
            "eligible": "*.lean below active Mathlib top-level modules",
            "excluded_top_modules": sorted(EXCLUDED_TOP_MODULES),
            "ranking": "sha256(relative_path + NUL + selection_salt), then relative path",
            "selection_salt": SELECTION_SALT,
            "files_per_top_module": FILES_PER_TOP_MODULE,
            "outcome_blind": True,
        },
        "selected_files": len(files),
        "selected_bytes": sum(item["bytes"] for item in files),
        "top_module_counts": counts,
        "files": files,
        "support_files": support_files,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        f"materialized {manifest['selected_files']} files / "
        f"{manifest['selected_bytes']} bytes across {len(counts)} top modules"
    )


if __name__ == "__main__":
    main()
