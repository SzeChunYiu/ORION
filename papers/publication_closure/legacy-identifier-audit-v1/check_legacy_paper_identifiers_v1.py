#!/usr/bin/env python3
"""Do any paper documents announce themselves as a different paper?

A document under `papers/orion-06-.../` headed "ORION-02 nearest-work matrix" gives a
reviewer no way to tell whether they are reading the right paper. Three such headers exist
and none is a sanctioned alias: `PAPER_ALIASES.md` carries 39 entries and **not one** maps
an `ORION-NN` id to a different `ORION-NN`. The old ids in that registry are P-series and
letter-series names, so an `ORION-NN` header is unresolvable rather than historical.

This checks the top of each paper's front-matter documents for an `ORION-NN` that
disagrees with its own directory, and consults the alias registry before reporting, so a
genuine registered alias is never flagged.

Exit codes
  0  CLEAN         no unexplained legacy identifier
  1  MISMATCH      a document announces a different paper, unsanctioned by the registry
  3  CANNOT_CHECK  the alias registry is missing, so "sanctioned" cannot be decided
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

EXIT_CLEAN, EXIT_MISMATCH, EXIT_CANNOT_CHECK = 0, 1, 3

FRONT_MATTER = (
    "JOURNAL_READINESS.md",
    "NEAREST_WORK_MATRIX_V3.md",
    "NEAREST_WORK_MATRIX_V4.md",
    "README.md",
    "CLAIM_LEDGER_V1.md",
)
HEADER_LINES = 3  # a stale id in the title block is what misleads; body mentions are fine


def _repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        # .git is a directory in a clone and a FILE inside a git worktree.
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def load_aliases(root: str):
    p = os.path.join(root, "papers", "PAPER_ALIASES.md")
    if not os.path.isfile(p):
        return None
    txt = open(p, encoding="utf-8").read()
    pairs = re.findall(r"\{old:\s*([^,]+?),\s*new:\s*([^}]+?)\}", txt)
    return {o.strip(): n.strip() for o, n in pairs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()

    root = _repo_root(os.path.dirname(os.path.abspath(__file__)))
    aliases = load_aliases(root)
    if aliases is None:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "ALIAS_REGISTRY_ABSENT"}))
        return EXIT_CANNOT_CHECK

    papers_dir = os.path.join(root, "papers")
    findings, checked = [], 0
    for name in sorted(os.listdir(papers_dir)):
        m = re.match(r"orion-(\d+)-", name)
        if not m:
            continue
        own = f"ORION-{int(m.group(1)):02d}"
        for doc in FRONT_MATTER:
            path = os.path.join(papers_dir, name, doc)
            if not os.path.isfile(path):
                continue
            checked += 1
            with open(path, encoding="utf-8", errors="replace") as fh:
                head = "".join(next(fh, "") for _ in range(HEADER_LINES))
            found = re.findall(r"ORION-(\d+)", head)
            if not found:
                continue
            declared = f"ORION-{int(found[0]):02d}"
            if declared == own:
                continue
            # A registered alias is not a defect. The registry maps old->new, so a
            # sanctioned header would appear as an old id resolving to this paper.
            if aliases.get(declared) == own:
                continue
            findings.append({
                "paper_dir": name,
                "document": doc,
                "declares": declared,
                "belongs_to": own,
                "registry_sanctioned": False,
                "why": (
                    f"{declared} is not a registered alias of {own}; "
                    "PAPER_ALIASES.md maps no ORION-NN id to a different ORION-NN"
                ),
            })

    out = {
        "checker": "legacy_paper_identifiers_v1",
        "alias_entries": len(aliases),
        "orion_to_orion_aliases": sum(
            1 for o, n in aliases.items() if o.startswith("ORION-") and o != n
        ),
        "documents_checked": checked,
        "header_lines_inspected": HEADER_LINES,
        "findings": findings,
        "status": "MISMATCH" if findings else "CLEAN",
        "claim_scope": (
            "Reports front-matter identifiers that disagree with their own directory and "
            "are not sanctioned by the alias registry. Says nothing about the content."
        ),
        "grants_authority": "NONE",
    }
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_MISMATCH if findings else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
