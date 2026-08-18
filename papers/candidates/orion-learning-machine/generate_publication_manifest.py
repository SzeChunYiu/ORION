#!/usr/bin/env python3
"""Generate the current bounded P9/P10 publication manifest."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CANDIDATES = ROOT.parent
OUTPUT = ROOT / "PUBLICATION_MANIFEST_SHA256.txt"


def included_files() -> list[Path]:
    roots = [
        ROOT / "framework",
        ROOT / "results",
        CANDIDATES / "paper-09-executable-research-core",
        CANDIDATES / "paper-10-content-bound-math-evaluation",
    ]
    suffixes = {".arff", ".bib", ".json", ".lean", ".md", ".py", ".sh", ".txt"}
    files = [
        path
        for base in roots
        for path in base.rglob("*")
        if path.is_file()
        and not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
        and (path.suffix in suffixes or path.name == "LICENSE")
    ]
    files.extend(
        [
            ROOT / "LOCAL_CLOSURE_AUTHORITY.json",
            ROOT / "REPRODUCE.md",
            ROOT / "REPRODUCE_LOCAL_CLOSURE.sh",
            ROOT / "SCRIPT_MANIFEST_SHA256.txt",
            ROOT / "VERIFY_LOCAL_CLOSURE.sh",
            ROOT / "generate_publication_manifest.py",
            CANDIDATES
            / "paper-08-epistemic-authority-autonomous-science"
            / "benchmark"
            / "P9_GOVERNED_CAPABILITY_COMPANION.md",
            CANDIDATES / "P6_P10_ISSUE_RECONCILIATION_2026-08-18.md",
        ]
    )
    return sorted(set(files), key=lambda path: Path(os.path.relpath(path, ROOT)).as_posix())


def main() -> None:
    lines = [
        "# ORION P9/P10 bounded publication manifest — generated 2026-08-18",
        "# Paths are relative to papers/candidates/orion-learning-machine.",
    ]
    for path in included_files():
        relative = Path(os.path.relpath(path, ROOT)).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    OUTPUT.write_text("\n".join(lines) + "\n")
    print(f"P9/P10 publication manifest: WROTE {len(lines) - 2} files")


if __name__ == "__main__":
    main()
