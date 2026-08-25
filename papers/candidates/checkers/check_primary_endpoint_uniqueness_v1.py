#!/usr/bin/env python3
"""Every surviving paper must declare exactly one unique primary endpoint.

#1086's definition of done requires it. Until now nothing measured it, so the
box could only be ticked by assertion.

Two failures are distinguished, because they need different repairs:

  UNDECLARED  a paper declares no machine-readable ``primary_endpoint``.
              Prose saying "the primary endpoint is X" does not count: a
              checker cannot read it, and a box that depends on reading is
              the same defect this programme has already recorded three times
              in its own benchmarks.

  AMBIGUOUS   a paper declares more than one distinct endpoint. "One unique
              primary endpoint" is violated by two, even if both are unique
              across the programme.

  SHARED      two papers declare the SAME endpoint, so their claims are not
              disjoint.

Exit codes:
  0  every surviving paper declares exactly one endpoint and none is shared
  1  at least one paper is UNDECLARED, AMBIGUOUS, or SHARED
  2  the papers tree could not be read (never conflated with 0)
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

KEY = "primary_endpoint"


def _endpoints(paper: Path) -> set[str]:
    found: set[str] = set()
    for f in paper.rglob("*.json"):
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if KEY not in text:
            continue
        try:
            payload = json.loads(text)
        except ValueError:
            continue

        def walk(node: object) -> None:
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == KEY and isinstance(v, str) and v.strip():
                        found.add(v.strip())
                    else:
                        walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(payload)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--papers-root", type=Path, default=Path("papers"))
    args = ap.parse_args()

    root = args.papers_root
    if not root.is_dir():
        print(f"PRIMARY ENDPOINT CHECK: CANNOT_CHECK — {root} is not a directory")
        return 2

    papers = sorted(p for p in root.glob("paper-*") if p.is_dir())
    if not papers:
        print("PRIMARY ENDPOINT CHECK: CANNOT_CHECK — no paper-* directories found")
        return 2

    by_paper = {p.name: _endpoints(p) for p in papers}
    owners: dict[str, list[str]] = collections.defaultdict(list)
    for name, eps in by_paper.items():
        for ep in eps:
            owners[ep].append(name)

    undeclared = sorted(n for n, e in by_paper.items() if not e)
    ambiguous = sorted(n for n, e in by_paper.items() if len(e) > 1)
    shared = sorted(ep for ep, who in owners.items() if len(who) > 1)

    total = len(by_paper)
    clean = total - len(undeclared) - len(ambiguous)
    print(f"PRIMARY ENDPOINT CHECK: {clean}/{total} papers declare exactly one")

    if undeclared:
        print(f"\nUNDECLARED ({len(undeclared)}) — no machine-readable '{KEY}':")
        for n in undeclared:
            print(f"  {n}")
    if ambiguous:
        print(f"\nAMBIGUOUS ({len(ambiguous)}) — more than one distinct endpoint:")
        for n in ambiguous:
            for ep in sorted(by_paper[n]):
                print(f"  {n}: {ep}")
    if shared:
        print(f"\nSHARED ({len(shared)}) — declared by more than one paper:")
        for ep in shared:
            print(f"  {ep} <- {', '.join(owners[ep])}")

    if undeclared or ambiguous or shared:
        print(
            "\nA paper without a machine-readable endpoint cannot be checked for "
            "uniqueness, and a box that depends on reading prose is not a "
            "measurement."
        )
        return 1

    print("clean: every paper declares exactly one endpoint and none is shared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
