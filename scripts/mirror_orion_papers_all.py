#!/usr/bin/env python3
"""Exact ORION-01--25 paper/package mirror with declared target overlays."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile


PAPERS = (
    "orion-01-certificate-realization",
    "orion-02-fiberguard-finite-fibre",
    "orion-03-typed-merge-falsification",
    "orion-04-rooted-completion-certificates",
    "orion-05-tare-expressivity",
    "orion-06-recursive-recovery",
    "orion-07-dual-instrument",
    "orion-08-typed-state",
    "orion-09-compilation-regime-geometry",
    "orion-10-certified-static-forecasting",
    "orion-11-recursive-epistemic-reconstruction",
    "orion-12-open-world-scientific-discovery",
    "orion-13-global-knowledge-portrait",
    "orion-14-verified-scientific-discovery",
    "orion-15-self-orion",
    "orion-16-formal-epistemic-structures-and-mechanics",
    "orion-17-epistemic-navigation-open-worlds",
    "orion-18-epistemic-authority-autonomous-science",
    "orion-19-structured-epistemic-learning",
    "orion-20-structured-problem-solving",
    "orion-21-state-as-computation",
    "orion-22-adaptive-state-reasoning",
    "orion-23-responsibility-carrying-state",
    "orion-24-orion-rse",
    "orion-25-orion-research-harness",
)
SUPPORT_PATHS = (
    "AUTHOR_IDENTITY_V1.json",
    "SUBMISSION_POLICY_V1.md",
    "publication_closure/orion_all_submission_20260831",
    "publication_closure/vendor/jair-author-kit-20260216",
    "skills/nature/nature-publication-closure",
)
TARGET_OVERLAYS = {"PROVENANCE.md", "MIRROR_RECEIPT_2026-08-31.md", "code"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_map(root: Path, exclude_overlays: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if exclude_overlays and rel.parts[0] in TARGET_OVERLAYS:
            continue
        result[rel.as_posix()] = sha256(path)
    return result


def safe_target(target_root: Path, relative: Path) -> Path:
    root = target_root.resolve()
    if root == Path("/") or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("unsafe mirror target")
    destination = (root / "v1-papers" / relative).resolve()
    if root not in destination.parents:
        raise ValueError("mirror destination escapes target root")
    return destination


def copy_item(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def replace_exact(source: Path, destination: Path) -> None:
    if destination.exists():
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()
    copy_item(source, destination)
    if source.is_dir():
        if tree_map(source) != tree_map(destination):
            raise RuntimeError(f"support-tree mismatch: {source}")
    elif sha256(source) != sha256(destination):
        raise RuntimeError(f"support-file mismatch: {source}")


def mirror_paper(source_root: Path, target_root: Path, paper: str, source_commit: str) -> None:
    source = source_root / "papers" / paper
    package = source / "submission/publication-ready-20260831/PACKAGE_MANIFEST.json"
    if not source.is_dir() or not package.is_file():
        raise FileNotFoundError(f"current source/package missing: {paper}")
    destination = safe_target(target_root, Path(paper))
    with tempfile.TemporaryDirectory(prefix=f"{paper}-overlays-") as tmp:
        overlays = Path(tmp)
        if destination.exists():
            for name in TARGET_OVERLAYS:
                item = destination / name
                if item.exists():
                    copy_item(item, overlays / name)
            shutil.rmtree(destination)
        copy_item(source, destination)
        for item in overlays.iterdir():
            copy_item(item, destination / item.name)
    receipt = destination / "MIRROR_RECEIPT_2026-08-31.md"
    receipt.write_text(
        f"""# Exact mirror receipt -- {paper}

Source repository: `SzeChunYiu/ORION`  
Source commit: `{source_commit}`  
Source path: `papers/{paper}/`  
Target path: `v1-papers/{paper}/`  
Publication-ready manifest SHA-256: `{sha256(package)}`

Every source file is mirrored byte-for-byte. Target-owned `PROVENANCE.md`,
`MIRROR_RECEIPT_2026-08-31.md`, and `code/` are declared overlays and excluded
from source-tree equality. The immutable target commit is recorded by the
workflow after commit, avoiding a self-referential receipt.
""",
        encoding="utf-8",
    )
    if tree_map(source) != tree_map(destination, exclude_overlays=True):
        raise RuntimeError(f"post-copy tree mismatch: {paper}")


def verify_full_report(source_root: Path) -> None:
    closure = source_root / "papers/publication_closure/orion_all_submission_20260831"
    report = json.loads((closure / "VERIFICATION_REPORT.json").read_text(encoding="utf-8"))
    verifier = closure / "verify_all_submission_materials.py"
    builder = closure / "build_all_submission_materials.py"
    if report["aggregate"] != "PASS" or len(report["papers"]) != 25:
        raise RuntimeError("full 25-paper verification report is not PASS")
    if report["verifier_sha256"] != sha256(verifier) or report["builder_sha256"] != sha256(builder):
        raise RuntimeError("verification report does not bind the current builder/verifier")
    for paper in report["papers"]:
        if paper["status"] != "PASS" or "clean_arxiv_build" not in paper["checks"] or "clean_journal_build" not in paper["checks"]:
            raise RuntimeError(f"full clean-build evidence missing for {paper['paper']}")
        package = source_root / paper["package"]
        manifest = package / "PACKAGE_MANIFEST.json"
        if paper["manifest_sha256"] != sha256(manifest):
            raise RuntimeError(
                f"full clean-build report is stale for {paper['paper']}: "
                "PACKAGE_MANIFEST.json changed after the recorded build"
            )


def verify_mirrored_package_checksums(target_root: Path) -> None:
    """Require one checksum-closed current package for every declared paper."""
    checked: list[str] = []
    for paper in PAPERS:
        package = (
            target_root
            / "v1-papers"
            / paper
            / "submission/publication-ready-20260831"
        )
        sums_path = package / "SHA256SUMS"
        if not sums_path.is_file():
            raise RuntimeError(f"mirrored publication checksum file missing: {paper}")
        rows = sums_path.read_text(encoding="utf-8").splitlines()
        if not rows:
            raise RuntimeError(f"mirrored publication checksum file is empty: {paper}")
        seen: set[str] = set()
        for row in rows:
            try:
                expected, relative = row.split("  ", 1)
            except ValueError as exc:
                raise RuntimeError(f"malformed mirrored checksum row: {paper}: {row}") from exc
            path = (package / relative).resolve()
            if package.resolve() not in path.parents or relative in seen:
                raise RuntimeError(f"unsafe or duplicate mirrored checksum path: {paper}: {relative}")
            if not path.is_file() or sha256(path) != expected:
                raise RuntimeError(f"mirrored publication checksum mismatch: {paper}: {relative}")
            seen.add(relative)
        checked.append(paper)
    if tuple(checked) != PAPERS:
        raise RuntimeError("mirrored checksum verification did not cover ORION-01--25 exactly")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--target-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise SystemExit("source commit must be a full lowercase Git object ID")
    source_root = args.source_root.resolve()
    target_root = args.target_root.resolve()
    verify_full_report(source_root)
    registry = json.loads((source_root / "papers/publication_closure/orion_all_submission_20260831/CLOSURE_REGISTRY.json").read_text(encoding="utf-8"))
    if len(registry["papers"]) != 25:
        raise RuntimeError("closure registry does not contain exactly 25 current papers")
    for paper in PAPERS:
        mirror_paper(source_root, target_root, paper, args.source_commit)
        print(f"MIRRORED {paper}")
    verify_mirrored_package_checksums(target_root)
    for rel_string in SUPPORT_PATHS:
        rel = Path(rel_string)
        source = source_root / "papers" / rel
        if not source.exists():
            raise FileNotFoundError(f"support path missing: {source}")
        replace_exact(source, safe_target(target_root, rel))
        print(f"MIRRORED support/{rel.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
