#!/usr/bin/env python3
"""Does every journal package's SHA256SUMS use the path root its checker assumes?

`orion.programme.package_currency.survey` resolves each SHA256SUMS entry as
``paper_dir / path``. Five of the six packages write paper-relative paths and are
checked. ORION-05 writes repository-root-relative paths, so every one of its
entries resolves to a file that does not exist, the checker counts all forty as
`missing`, and `missing` is not part of the staleness ratchet's failing
condition.

The result is a package that has never been verified while reporting nothing
wrong. Resolved from the correct root, eleven of its entries are stale --
`main.tex`, the bibliography, and every numbered section.

That is the difference between "checked and fine" and "could not check" showing up
as the former, which is the failure this repository keeps finding in other guises.

Exit 0 every package resolves from the paper directory, 1 some package uses a
different root, 3 could not check.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENTRY = re.compile(r"^([0-9a-f]{64})\s+\*?(.+)$")


def audit() -> list[dict]:
    out = []
    for sums in sorted((ROOT / "papers").glob("*/journal_package/SHA256SUMS")):
        paper_dir = sums.parent.parent
        from_paper = from_root = unresolved = 0
        stale_from_root: list[str] = []
        for line in sums.read_text(errors="replace").splitlines():
            match = ENTRY.match(line)
            if not match:
                continue
            digest, rel = match.group(1), match.group(2)
            as_paper, as_root = paper_dir / rel, ROOT / rel
            if as_paper.is_file():
                from_paper += 1
            elif as_root.is_file():
                from_root += 1
                if hashlib.sha256(as_root.read_bytes()).hexdigest() != digest:
                    stale_from_root.append(rel)
            else:
                unresolved += 1
        out.append(
            {
                "paper": paper_dir.name,
                "entries": from_paper + from_root + unresolved,
                "resolve_from_paper_dir": from_paper,
                "resolve_from_repo_root": from_root,
                "unresolvable": unresolved,
                "stale_once_resolved_from_repo_root": stale_from_root,
                "root_the_checker_assumes": "paper_dir",
                "uses_wrong_root": from_root > from_paper,
            }
        )
    return out


def main() -> int:
    try:
        rows = audit()
    except OSError as error:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(error)}, indent=2))
        return 3
    if not rows:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "no packages found"}, indent=2))
        return 3

    wrong = [r for r in rows if r["uses_wrong_root"]]
    payload = {
        "schema": "ORION.PackageSumsPathRoot.v1",
        "packages": rows,
        "packages_using_the_wrong_root": [r["paper"] for r in wrong],
        "hidden_stale_entries": {
            r["paper"]: r["stale_once_resolved_from_repo_root"] for r in wrong
        },
        "why_this_hides": (
            "package_currency resolves paper_dir/path; entries that do not resolve are "
            "counted missing, and missing is not part of the staleness ratchet's failing "
            "condition, so a package with the wrong root is never checked and never fails"
        ),
        "scientific_authority_delta": "NONE",
        "status": "CLEAN" if not wrong else "WRONG_PATH_ROOT",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not wrong else 1


if __name__ == "__main__":
    raise SystemExit(main())
