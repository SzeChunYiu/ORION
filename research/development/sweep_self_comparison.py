"""Sweep every paper for the guard that compares a value with itself.

``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity`` was
recorded against P6. The same guard was later found in P7 and three times in P8,
by reading rather than by any mechanism. This is the sweep that failure record
never had.

A paper is only reported clean when something was actually scanned. Zero
findings over zero files is the vacuous-guard shape the class itself names, so a
paper whose scan had no denominator is ``NOT_SWEPT``, not ``SWEPT_CLEAN``.

Usage::

    python research/development/sweep_self_comparison.py            # report
    python research/development/sweep_self_comparison.py --json     # machine form
    python research/development/sweep_self_comparison.py --check    # non-zero on any finding
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from orion.programme.failure_class_coverage import PAPER_IDS
from orion.programme.self_comparison_scan import scan_paths

#: Where each paper's executable content lives. A paper's roots are the places a
#: reader would look for its code; an empty set means the scope is undetermined,
#: which is a reason to withhold a clean verdict rather than to issue one.
ROOT_PATTERNS = (
    "papers/paper-{nn}-*",
    "research/claim_expansion/p{n}",
    "src/orion/study/p{n}",
    "research/extensions/p{n}-*",
    "research/campaigns/*p{n}-*",
    "research/revival/p{n}",
    "tests/unit/p{n}",
    "tests/unit/study/p{n}",
)

#: Papers whose subject is not under ``papers/``. P15 is a systems paper about
#: the harness package, and its README names that package as what it covers, so
#: scanning only ``papers/paper-15-*`` would produce a clean verdict over a
#: directory containing one README --- the vacuous shape this sweep exists to
#: refuse.
EXTRA_ROOTS: dict[int, tuple[str, ...]] = {
    15: ("packages/orion-research-harness",),
}

MIN_FILES_FOR_A_CLEAN_VERDICT = 1


def paper_roots(n: int) -> list[Path]:
    out: list[Path] = []
    for pattern in ROOT_PATTERNS + EXTRA_ROOTS.get(n, ()):
        out += [Path(p) for p in glob.glob(pattern.format(n=n, nn=f"{n:02d}"))]
    return [p for p in out if p.exists()]


def scanned_files(roots: list[Path]) -> int:
    total = 0
    for root in roots:
        if root.is_file():
            total += int(root.suffix == ".py")
            continue
        for path in root.rglob("*.py"):
            if any(part in {".venv", "__pycache__", ".git"} for part in path.parts):
                continue
            total += 1
    return total


def sweep() -> dict[str, object]:
    papers = []
    for n in PAPER_IDS:
        roots = paper_roots(n)
        files = scanned_files(roots)
        findings = scan_paths(roots)
        if files < MIN_FILES_FOR_A_CLEAN_VERDICT:
            state = "NOT_SWEPT"
            note = "no python file was scanned, so a clean verdict would have no denominator"
        elif findings:
            state = "FOUND"
            note = f"{len(findings)} self-resolving comparison(s)"
        else:
            state = "SWEPT_CLEAN"
            note = f"{files} files scanned, none containing a self-resolving comparison"
        papers.append(
            {
                "paper_id": n,
                "roots": [str(r) for r in roots],
                "files_scanned": files,
                "findings": [f.summary for f in findings],
                "state": state,
                "note": note,
            }
        )
    return {
        "schema_version": "orion.programme.self-comparison-sweep.v1",
        "failure_class": "2026-08-unfalsifiable-check-zero-refutation-capacity",
        "detector": "orion.programme.self_comparison_scan",
        "papers": papers,
        "total_findings": sum(len(p["findings"]) for p in papers),
        "swept_clean": [p["paper_id"] for p in papers if p["state"] == "SWEPT_CLEAN"],
        "not_swept": [p["paper_id"] for p in papers if p["state"] == "NOT_SWEPT"],
        "found_in": [p["paper_id"] for p in papers if p["state"] == "FOUND"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the machine-readable report")
    parser.add_argument("--check", action="store_true", help="exit non-zero on any finding")
    args = parser.parse_args()

    report = sweep()
    if args.json:
        print(json.dumps(report, indent=1, sort_keys=True))
    else:
        print(f"failure class: {report['failure_class']}")
        print(f"detector:      {report['detector']}\n")
        print(f"{'paper':7s} {'files':>6s}  state")
        for p in report["papers"]:
            print(f"P{p['paper_id']:<6d} {p['files_scanned']:6d}  {p['state']:12s} {p['note']}")
            for finding in p["findings"]:
                print(f"          {finding}")
        print(
            f"\nswept clean: {len(report['swept_clean'])}/15   "
            f"found in: {len(report['found_in'])}   "
            f"not swept: {len(report['not_swept'])}  {report['not_swept']}"
        )
    if args.check and report["total_findings"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
