#!/usr/bin/env python3
"""Generate the current bounded P9/P10 publication manifest."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
#: The lane and its sibling paper packages were promoted from papers/candidates/
#: into papers/; the shared cross-paper apparatus stayed behind in candidates/.
PAPERS = ROOT.parent
CANDIDATES = PAPERS / "candidates"
OUTPUT = ROOT / "PUBLICATION_MANIFEST_SHA256.txt"


def included_files() -> list[Path]:
    roots = [
        ROOT / "framework",
        ROOT / "results",
        PAPERS / "paper-09-executable-research-core",
        PAPERS / "paper-10-content-bound-math-evaluation",
    ]
    suffixes = {".arff", ".bib", ".json", ".lean", ".md", ".py", ".sh", ".txt"}
    # The 2026-08-20 P10 publication overlay (PUBLICATION_MANIFEST_P10_V2.txt)
    # carries four ADDITIVE files by exact Git-blob identity; they are scoped to
    # the overlay only and must stay absent from this SHA256 manifest, whose V2
    # closure check requires exactly the five superseded legacy P10 paths.
    v2_additive = {
        "paper-10-content-bound-math-evaluation/P10_REVIEW_EXPANSION_BOUNDARY.md",
        "paper-10-content-bound-math-evaluation/REVIEW_PACKAGE_STATUS_2026-08-20.md",
        "paper-10-content-bound-math-evaluation/analyze_module_robustness_v1.py",
        "paper-10-content-bound-math-evaluation/results/MATHLIB_TRANSFER_V2_1_MODULE_ROBUSTNESS_RECEIPT_V1.json",
    }
    files = [
        path
        for base in roots
        for path in base.rglob("*")
        if path.is_file()
        and not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
        and (path.suffix in suffixes or path.name == "LICENSE")
        and path.relative_to(PAPERS).as_posix() not in v2_additive
    ]
    files.extend(
        [
            ROOT / "LOCAL_CLOSURE_AUTHORITY.json",
            ROOT / "REPRODUCE.md",
            ROOT / "REPRODUCE_LOCAL_CLOSURE.sh",
            ROOT / "SCRIPT_MANIFEST_SHA256.txt",
            ROOT / "VERIFY_LOCAL_CLOSURE.sh",
            ROOT / "generate_publication_manifest.py",
            PAPERS
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
        "# Paths are relative to papers/orion-learning-machine.",
    ]
    for path in included_files():
        relative = Path(os.path.relpath(path, ROOT)).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    OUTPUT.write_text("\n".join(lines) + "\n")
    print(f"P9/P10 publication manifest: WROTE {len(lines) - 2} files")


if __name__ == "__main__":
    main()
