"""Does a paper's README name the same current manuscript as its claim ledger?

A reader arriving at a paper takes the README's word for which file is the
manuscript. When the ledger has moved on and the README has not, the reader is
sent to a superseded document that still reads as current -- and every check
performed against it is performed against the wrong file.

That is not hypothetical. P6's README named ``FINAL_V4.md`` while both
``CLAIM_LEDGER_V4.md`` and ``manuscript/main.tex`` named ``FINAL_V5.md``, and a
disclosure audit run against the README's pointer reported a statement present
that the current manuscript did not contain.

Ledgers are versioned and not all of them carry a pointer. P4's highest ledger
(V4) has none, so reading "the last ledger with a pointer" silently falls back to
V3 -- which that paper's own README calls the preserved pre-ascent record. Taking
a historical pointer as current would manufacture a disagreement out of nothing,
so this reports CANNOT_CHECK for that shape instead of guessing.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_PASS = 0
EXIT_DISAGREE = 2
EXIT_CANNOT_CHECK = 3

POINTER = re.compile(
    r"\*\*(?:Current science manuscript|Canonical manuscript|Current manuscript):\*\*\s*`([^`]+)`",
    re.I,
)
LEDGER_VERSION = re.compile(r"_V(\d+)\.md$")


@dataclass
class Pointer:
    paper: str
    readme: str | None = None
    ledger: str | None = None
    ledger_file: str | None = None
    note: str = ""

    @property
    def state(self) -> str:
        if self.readme is None:
            return "NO_README_POINTER"
        if self.ledger is None:
            return "NO_LEDGER_POINTER"
        if self.readme == self.ledger:
            return "AGREE"
        if self.note:
            # The only pointer available came from a ledger that a newer one
            # supersedes, so a mismatch says nothing: P4's README calls exactly
            # that ledger the preserved pre-ascent record. Disagreeing with a
            # historical document is not evidence of drift.
            return "STALE_LEDGER_ONLY"
        return "DISAGREE"


def _ledger_pointer(paper: Path) -> tuple[str | None, str | None, str]:
    """Pointer from the highest-numbered ledger that carries one."""
    ledgers = [
        f
        for f in paper.iterdir()
        if f.is_file() and f.name.startswith(("CLAIM_LEDGER", "CLAIM_EVIDENCE_LEDGER"))
    ]
    if not ledgers:
        return None, None, "no ledger"

    def ver(f: Path) -> int:
        m = LEDGER_VERSION.search(f.name)
        return int(m.group(1)) if m else -1

    ledgers.sort(key=lambda f: (ver(f), f.name))
    highest = ledgers[-1]
    for f in reversed(ledgers):
        m = POINTER.search(f.read_text(errors="replace"))
        if m:
            note = (
                ""
                if f == highest
                else f"pointer from {f.name}, but {highest.name} is newer and has none"
            )
            return m.group(1), f.name, note
    return None, None, f"no ledger names a manuscript ({highest.name} is newest)"


def audit_repository(root: Path | None = None) -> list[Pointer]:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    out: list[Pointer] = []
    for d in sorted(p for p in papers.iterdir() if p.is_dir()):
        readme = d / "README.md"
        if not readme.is_file():
            continue
        rm = POINTER.search(readme.read_text(errors="replace"))
        if not rm:
            continue
        lp, lf, note = _ledger_pointer(d)
        out.append(Pointer(d.name, rm.group(1), lp, lf, note))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        records = audit_repository(args.root)
    except FileNotFoundError as exc:
        print(f"MANUSCRIPT_POINTER_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK

    bad = unread = 0
    for r in records:
        st = r.state
        if st == "DISAGREE":
            bad += 1
            print(f"  DISAGREE  {r.paper:48s} README={r.readme}  {r.ledger_file}={r.ledger}")
        elif st in ("NO_LEDGER_POINTER", "STALE_LEDGER_ONLY"):
            unread += 1
            print(f"  UNREAD    {r.paper:48s} README={r.readme}  ({r.note})")
        else:
            extra = f"  [{r.note}]" if r.note else ""
            print(f"  AGREE     {r.paper:48s} {r.readme}{extra}")
    print(f"\npapers with a README pointer: {len(records)}   disagreeing: {bad}   unread: {unread}")
    if bad:
        print("MANUSCRIPT_POINTER_DISAGREE: the README sends readers to a different")
        print("file than the claim ledger designates; one of them is out of date")
        return EXIT_DISAGREE
    if unread:
        print("MANUSCRIPT_POINTER_CANNOT_CHECK: no ledger names a current manuscript,")
        print("so the README's pointer has nothing to be checked against")
        return EXIT_CANNOT_CHECK
    print("MANUSCRIPT_POINTER_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
