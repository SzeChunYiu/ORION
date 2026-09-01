#!/usr/bin/env python3
"""Exact-tree mirror for the six 2026-08-31 publication closures."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import tempfile


PAPERS = (
    "orion-13-global-knowledge-portrait",
    "orion-14-verified-scientific-discovery",
    "orion-19-structured-epistemic-learning",
    "orion-21-state-as-computation",
    "orion-23-responsibility-carrying-state",
    "orion-24-orion-rse",
)
FINAL_MANIFESTS = {
    "orion-13-global-knowledge-portrait": "submission/publication-final-20260901/PACKAGE_MANIFEST.json",
}
TARGET_OVERLAYS = {"PROVENANCE.md", "MIRROR_RECEIPT_2026-08-31.md", "code"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if rel.parts[0] in TARGET_OVERLAYS:
            continue
        result[rel.as_posix()] = sha256(path)
    return result


def safe_destination(target_root: Path, paper: str) -> Path:
    resolved_root = target_root.resolve()
    if resolved_root == Path("/") or paper not in PAPERS:
        raise ValueError("unsafe mirror target")
    destination = (resolved_root / "v1-papers" / paper).resolve()
    if resolved_root not in destination.parents:
        raise ValueError("mirror destination escapes target root")
    return destination


def copy_overlay(path: Path, destination: Path) -> None:
    if path.is_dir():
        shutil.copytree(path, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)


def mirror_paper(source_root: Path, target_root: Path, paper: str,
                 source_commit: str) -> None:
    source = source_root / "papers" / paper
    if not source.is_dir():
        raise FileNotFoundError(f"source paper missing: {source}")
    final_manifest = source / FINAL_MANIFESTS.get(
        paper, "submission/final-20260831/PACKAGE_MANIFEST.json"
    )
    if not final_manifest.is_file():
        raise FileNotFoundError(f"final manifest missing: {final_manifest}")
    destination = safe_destination(target_root, paper)
    with tempfile.TemporaryDirectory(prefix=f"{paper}-overlays-") as tmp:
        overlays = Path(tmp)
        if destination.exists():
            for name in TARGET_OVERLAYS:
                item = destination / name
                if item.exists():
                    copy_overlay(item, overlays / name)
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
        for item in overlays.iterdir():
            target = destination / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            copy_overlay(item, target)

    receipt = destination / "MIRROR_RECEIPT_2026-08-31.md"
    receipt.write_text(
        f"""# Exact mirror receipt — {paper}

Source repository: `SzeChunYiu/ORION`
Source commit: `{source_commit}`
Source path: `papers/{paper}/`
Target path: `v1-papers/{paper}/`
Final package manifest SHA-256: `{sha256(final_manifest)}`

Every source file is mirrored byte-for-byte. Target-owned `PROVENANCE.md`,
`MIRROR_RECEIPT_2026-08-31.md` and `code/` are declared overlays and are
excluded from source-tree equality. The target commit is recorded by the
external workflow after commit to avoid a self-referential commit identifier.
""",
        encoding="utf-8",
    )
    if tree_map(source) != tree_map(destination):
        raise RuntimeError(f"post-copy tree mismatch: {paper}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise SystemExit("source commit must be a full lowercase Git object ID")
    for paper in PAPERS:
        mirror_paper(args.source_root.resolve(), args.target_root.resolve(), paper, args.source_commit)
        print(f"MIRRORED {paper}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
