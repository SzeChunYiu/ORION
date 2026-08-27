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
    # ``experiments/`` is a root because the code that produced a number is part
    # of what a publication manifest binds. It was absent, so the manifest pinned
    # every committed result and none of the six drivers that computed them --- a
    # reader could verify the numbers had not changed while the program that made
    # them changed underneath.
    roots = [
        ROOT / "experiments",
        ROOT / "framework",
        ROOT / "results",
        PAPERS / "paper-xx-executable-research-core",
        PAPERS / "archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation",
    ]
    # Build output only. This used to be an allowlist of eight suffixes, which
    # silently dropped whatever did not appear on it: a Lean toolchain pin and a
    # native shim, both of which decide what the proofs compile to, were outside
    # the binding because nobody had thought to add ``lean-toolchain`` and
    # ``.c``. An allowlist answers "what did we remember" and a denylist answers
    # "what is deliberately out", and only the second is a denominator.
    excluded_suffixes = {".pyc", ".pyo", ".pyd"}
    # The 2026-08-20 P10 publication overlay (PUBLICATION_MANIFEST_P10_V2.txt)
    # carries four ADDITIVE files by exact Git-blob identity; they are scoped to
    # the overlay only and must stay absent from this SHA256 manifest, whose V2
    # closure check requires exactly the five superseded legacy P10 paths.
    v2_additive = {
        "archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/P10_REVIEW_EXPANSION_BOUNDARY.md",
        "archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/REVIEW_PACKAGE_STATUS_2026-08-20.md",
        "archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/analyze_module_robustness_v1.py",
        "archive/2026-08-pre-unification/paper-xx-content-bound-math-evaluation/results/MATHLIB_TRANSFER_V2_1_MODULE_ROBUSTNESS_RECEIPT_V1.json",
    }
    files = [
        path
        for base in roots
        for path in base.rglob("*")
        if path.is_file()
        # Dot-*directories* are caches and version-control internals; a dot-*file*
        # such as .gitattributes is content the checkout depends on, so the
        # exclusion is on directories only.
        and not any(
            (part.startswith(".") and part != path.name) or part == "__pycache__"
            for part in path.parts
        )
        and path.suffix not in excluded_suffixes
        and path.relative_to(PAPERS).as_posix() not in v2_additive
    ]
    files.extend(
        [
            ROOT / "LOCAL_CLOSURE_AUTHORITY.json",
            ROOT / "PUBLICATION_MANIFEST_P10_V2.txt",
            ROOT / "README.md",
            ROOT / "REPRODUCE.md",
            ROOT / "REPRODUCE_LOCAL_CLOSURE.sh",
            # Lane-root programme doc landed 2026-08-26 (#1490 payload); a
            # committed scope file with no enforced binding is a membership hole.
            ROOT / "RESEARCH_PROGRAMME_V0.md",
            ROOT / "SCRIPT_MANIFEST_SHA256.txt",
            ROOT / "VERIFY_LOCAL_CLOSURE.sh",
            ROOT / "VERIFY_LOCAL_CLOSURE_V2.sh",
            ROOT / "generate_publication_manifest.py",
            PAPERS
            / "orion-18-epistemic-authority-autonomous-science"
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
