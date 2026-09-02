#!/usr/bin/env python3
"""Fail when a CANONICAL_* decision file and the publication-freeze addendum
name different manuscript versions.

Drift class (ORION-paper issue #78, authority-surface sweep): a paper's
newest `CANONICAL_*.md` designates `MANUSCRIPT_V4.md` while the newest
`PUBLICATION_FREEZE_ADDENDUM_V*.md` still freezes `MANUSCRIPT_V2.md`, so a
reader auditing "what is frozen" obtains a superseded theorem inventory.
The 2026-09-02 fixes landed additive addendum successors; this check keeps
the class from recurring silently.

Rules, per `papers/orion-*` directory:

1. Designation. Among backticked `` `MANUSCRIPT*.md` `` / `` `CLAIM_LEDGER*.md` ``
   tokens in the highest-version `CANONICAL_*.md`, the highest version per
   family is the designated canonical surface. (Historical tokens are always
   lower versions in the shipped files; the script prints what it saw.)
2. Agreement. The highest-version `PUBLICATION_FREEZE_ADDENDUM_V<n>.md`
   (exact pattern `V<digits>.md`; parallel-preservation copies with suffixes
   are deliberately not consulted) must name BOTH designated files.
   Papers with an addendum but no CANONICAL file skip to rule 3.
3. No dangling pointers. Every manuscript/ledger token frozen by the newest
   addendum must exist on disk in the paper directory.

Exit codes: 0 agreement holds; 1 drift; 3 nothing to check (no addendum).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PAPERS = REPO / "papers"

CANONICAL_RE = re.compile(r"^CANONICAL_[A-Z0-9_]*V(\d+)\.md$")
ADDENDUM_RE = re.compile(r"^PUBLICATION_FREEZE_ADDENDUM_V(\d+)\.md$")
TOKEN_RE = re.compile(r"`((?:MANUSCRIPT|CLAIM_LEDGER)[A-Za-z0-9_]*\.md)`")
VERSION_RE = re.compile(r"V(\d+)(?:\.md)?$")


def version_of(token: str) -> int:
    match = VERSION_RE.search(token)
    return int(match.group(1)) if match else 0


def newest_by_version(paths: list[Path], pattern: re.Pattern[str]) -> Path | None:
    best: tuple[int, Path] | None = None
    for path in paths:
        match = pattern.match(path.name)
        if match and (best is None or int(match.group(1)) > best[0]):
            best = (int(match.group(1)), path)
    return best[1] if best else None


def designated_families(text: str) -> dict[str, str]:
    """Highest-version MANUSCRIPT*/CLAIM_LEDGER* token per family."""
    chosen: dict[str, str] = {}
    for token in TOKEN_RE.findall(text):
        family = "MANUSCRIPT" if token.startswith("MANUSCRIPT") else "CLAIM_LEDGER"
        current = chosen.get(family)
        if current is None or version_of(token) > version_of(current):
            chosen[family] = token
    return chosen


def check_paper(paper: Path) -> tuple[list[str], list[str]]:
    """Return (errors, notes) for one paper directory."""
    errors: list[str] = []
    notes: list[str] = []
    files = list(paper.iterdir())

    canonical = newest_by_version(files, CANONICAL_RE)
    addendum = newest_by_version(files, ADDENDUM_RE)
    if addendum is None:
        return [], [f"{paper.name}: no freeze addendum (not checked)"]
    notes.append(
        f"{paper.name}: canonical={canonical.name if canonical else '-'} "
        f"addendum={addendum.name}"
    )

    addendum_text = addendum.read_text(encoding="utf-8")

    if canonical is not None:
        canonical_text = canonical.read_text(encoding="utf-8")
        designated = designated_families(canonical_text)
        if "MANUSCRIPT" not in designated or "CLAIM_LEDGER" not in designated:
            # Different convention (e.g. orion-11 designates manuscript/main.tex):
            # no versioned surface, so no version disagreement to detect. State
            # it rather than silently passing; the dangling-token rule still runs.
            notes.append(
                f"{paper.name}: {canonical.name} names no versioned "
                f"MANUSCRIPT*/CLAIM_LEDGER* token (version agreement n/a)"
            )
        for family, token in sorted(designated.items()):
            if token not in addendum_text:
                errors.append(
                    f"{paper.name}: {canonical.name} designates `{token}` but "
                    f"{addendum.name} never names it"
                )
            notes.append(f"{paper.name}: designated {family} -> {token}")

    for token in sorted(set(TOKEN_RE.findall(addendum_text))):
        if not (paper / token).is_file():
            errors.append(f"{paper.name}: {addendum.name} freezes `{token}` "
                          f"which does not exist on disk")
    return errors, notes


def main() -> int:
    errors: list[str] = []
    notes: list[str] = []
    for paper in sorted(PAPERS.glob("orion-*")):
        if not paper.is_dir():
            continue
        paper_errors, paper_notes = check_paper(paper)
        errors.extend(paper_errors)
        notes.extend(paper_notes)

    for note in notes:
        print(f"note: {note}")
    if errors:
        for error in errors:
            print(f"FREEZE_CANONICAL_DRIFT: {error}", file=sys.stderr)
        return 1
    print("FREEZE_CANONICAL_AGREEMENT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
