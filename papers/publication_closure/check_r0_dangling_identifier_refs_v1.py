#!/usr/bin/env python3
"""Do any documents cite a figure, table or artifact ID that names no file?

#1531 recorded that the R0 namespace unification fired on mathematical
identifiers, not only on paper references, and that the full blast radius was
"being inventoried". The parenthesised shape it named -- `P4(m)` rewritten to
`ORION-14(m)` -- is repaired on main and guarded by
tests/unit/publication/test_five_theory_hardening_r2.py.

This checks the shape nobody swept for: an identifier with no parentheses, glued
to a paper ID. `P1-2_main_outcome` became `ORION-11-2_main_outcome` in prose while
the figure on disk kept its name, so a JOURNAL_READINESS document ended up citing
figures that do not exist.

The test is objective and needs no judgement about which renames were intended:

    the cited ORION-form names no file anywhere in the tree,
    AND the corresponding P-form names a real one.

A genuine paper reference fails the second condition and is never flagged, so this
cannot be used to argue for a blanket revert of the R0 mapping -- which #1531 says
would be as wrong as the original blind rename.

Exit 0 no dangling references, 1 some found, 3 could not check.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: The R0 alias map is P<n> -> ORION-1<n> for n in 1..15.
TOKEN = re.compile(r"(?:P([0-9]{1,2})|ORION-1([0-9]))([-_][A-Za-z0-9_-]{3,})")
SEARCH_SUFFIXES = (".md", ".tex", ".json", ".txt", ".jsonl", ".py")


def _tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True
    )
    return [f for f in out.stdout.split("\n") if f]


def _stems(files: list[str]) -> dict[str, list[str]]:
    stems: dict[str, list[str]] = defaultdict(list)
    for path in files:
        base = os.path.basename(path)
        stems[base.rsplit(".", 1)[0] if "." in base else base].append(path)
    return stems


#: This file names the very tokens it hunts for, in the docstring above and in the
#: constants below, so scanning itself makes it report its own prose as a defect.
#: An earlier checker in this repository shipped with exactly that bug.
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()


def find_dangling() -> list[dict]:
    files = _tracked_files()
    stems = _stems(files)
    cited: dict[str, set[str]] = defaultdict(set)
    for path in files:
        if not path.endswith(SEARCH_SUFFIXES) or path == SELF:
            continue
        full = ROOT / path
        try:
            text = full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "ORION-1" not in text:
            continue
        for match in TOKEN.finditer(text):
            if match.group(2) is None:
                continue
            cited[match.group(0)].add(path)

    dangling = []
    for token, where in cited.items():
        match = re.match(r"ORION-1([0-9])([-_].*)$", token)
        if not match or token in stems:
            continue
        p_form = f"P{int(match.group(1))}{match.group(2)}"
        if p_form not in stems:
            continue
        dangling.append(
            {
                "referenced": token,
                "p_form": p_form,
                "p_form_files": sorted(stems[p_form])[:6],
                "cited_in": sorted(where),
            }
        )
    dangling.sort(key=lambda d: d["referenced"])
    return dangling


def main() -> int:
    try:
        dangling = find_dangling()
    except (OSError, subprocess.CalledProcessError) as error:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(error)}, indent=2))
        return 3

    payload = {
        "schema": "ORION.R0DanglingIdentifierReferences.v1",
        "rule": "cited ORION-form names no file AND its P-form names a real one",
        "dangling": len(dangling),
        "entries": dangling,
        "scientific_authority_delta": "NONE",
        "status": "CLEAN" if not dangling else "DANGLING_REFERENCES",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not dangling else 1


if __name__ == "__main__":
    raise SystemExit(main())
