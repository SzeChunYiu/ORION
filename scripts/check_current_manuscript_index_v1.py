"""Every paper must declare which manuscript is current, and the declaration must be true.

A successor nobody references is a dead artifact. On 2026-09-02 four manuscripts
were adopted in one day — ORION-16 ``FINAL_V6``, ORION-17 ``FINAL_V5``, ORION-18
``FINAL_V5``, ORION-22 ``MANUSCRIPT_V2`` — and afterwards:

- ``FINAL_V6.md`` was referenced by **zero** documents in its package;
- ``MANUSCRIPT_V2.md`` was referenced by **zero**;
- every paper's ``README.md`` still pointed at a superseded version.

The READMEs cannot be corrected in place: they are bound in
``CONTENT_MANIFEST_V1`` and the paper-level ``SHA256SUMS``, whose identity is
frozen. So the pointer lives in one index instead, and this checker keeps the
index honest.

The check that matters is the third one. Declaring a current manuscript is easy
to get right once and easy to leave behind on the next adoption, which is exactly
the failure above. So the checker does not merely confirm the declared file
exists — it looks for a **higher-versioned sibling that the index does not name**
and reds if it finds one.

Exit codes
----------
0   every paper declares a manuscript that exists and is the newest present
2   a declared manuscript is missing, untracked, or superseded by an unlisted sibling
3   CANNOT_CHECK -- the index or the repository could not be read
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "papers" / "publication_closure" / "CURRENT_MANUSCRIPT_INDEX_V1.json"

# FINAL.md < FINAL_V2_1.md < FINAL_V3.md < ... ; MANUSCRIPT.md < MANUSCRIPT_V2.md
VERSIONED = re.compile(r"^(FINAL|MANUSCRIPT)(?:_V(\d+)(?:_(\d+))?)?\.md$")


class CannotCheck(Exception):
    """The check could not run. Distinct from a clean result."""


def version_key(name: str) -> tuple[int, int] | None:
    match = VERSIONED.match(name)
    if not match:
        return None
    major = int(match.group(2)) if match.group(2) else 1
    minor = int(match.group(3)) if match.group(3) else 0
    return (major, minor)


def tracked_files(repo: Path) -> set[str]:
    proc = subprocess.run(
        ["/usr/bin/git", "ls-files"], cwd=repo, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise CannotCheck(f"git ls-files failed: {proc.stderr.strip()}")
    return set(proc.stdout.split())


def check(index: dict, repo: Path) -> list[str]:
    findings: list[str] = []
    tracked = tracked_files(repo)
    for paper_id, entry in sorted(index.get("papers", {}).items()):
        declared = entry.get("current_manuscript")
        if not declared:
            findings.append(f"{paper_id}: no current_manuscript declared")
            continue
        if declared not in tracked:
            findings.append(f"{paper_id}: declared manuscript is not tracked: {declared}")
            continue
        if not (repo / declared).is_file():
            findings.append(f"{paper_id}: declared manuscript is absent: {declared}")
            continue

        declared_path = Path(declared)
        key = version_key(declared_path.name)
        if key is None:
            # A non-versioned name is allowed but cannot be compared; say so
            # rather than silently treating it as newest.
            findings.append(
                f"{paper_id}: declared manuscript {declared_path.name!r} does not "
                "match the versioned naming, so 'is it newest' cannot be decided"
            )
            continue

        # The check that catches an adoption which forgot the index.
        siblings = [
            path
            for path in tracked
            if Path(path).parent == declared_path.parent
            and version_key(Path(path).name) is not None
        ]
        newer = sorted(
            (version_key(Path(s).name), s)
            for s in siblings
            if version_key(Path(s).name) > key  # type: ignore[operator]
        )
        if newer:
            findings.append(
                f"{paper_id}: index names {declared_path.name} but a newer "
                f"manuscript exists and is unlisted: {', '.join(Path(s).name for _, s in newer)}"
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--index", type=Path, default=None)
    args = parser.parse_args(argv)

    index_path = args.index or INDEX
    try:
        if not index_path.is_file():
            raise CannotCheck(f"index absent: {index_path}")
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if not index.get("papers"):
            raise CannotCheck("index declares no papers; nothing was checked")
        findings = check(index, args.repo)
    except CannotCheck as exc:
        print(f"CANNOT_CHECK: {exc}", file=sys.stderr)
        return 3
    except ValueError as exc:
        print(f"CANNOT_CHECK: index is malformed: {exc}", file=sys.stderr)
        return 3

    print(f"checked {len(index['papers'])} paper(s); {len(findings)} finding(s)")
    for finding in findings:
        print(f"  {finding}", file=sys.stderr)
    return 2 if findings else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
