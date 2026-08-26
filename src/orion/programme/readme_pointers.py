"""Does each paper's README point to exactly one active manuscript, authority and readiness report?

#1131 requires it. The failure this prevents is a reader opening a README and
finding two manuscripts, or three authority records, with nothing saying which
one is current -- at which point the reader picks, and the paper has delegated
its own currency decision to whoever is reading.

Zero is reported separately from many, because they are different problems. A
README naming no authority may have none to name; a README naming three may
have designated one of them and be perfectly clear.

That last point is why this counts designations rather than mentions. A first
version of this checker counted how many authority filenames appeared and
called three of them ambiguous. All three were fine: P15 writes "Current
authority: V3" with V1 and V2 under a Historical lifecycle heading, and P12
writes "Current claim authority is V5, which extends V4". Mentioning a
superseded record while naming the current one is exactly what good practice
looks like, and a checker that punished it would push papers toward deleting
their history.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from orion.programme.specialist_readiness_matrix import CANONICAL

EXIT_PASS = 0
EXIT_AMBIGUOUS = 2
EXIT_CANNOT_CHECK = 3
EXIT_MISSING = 4

#: Names explicitly marked historical are not competing current pointers. P12
#: writes "`MANUSCRIPT.md` is a historical integrated review snapshot"; counting
#: that as a second manuscript would flag a README for being clearer than one
#: that silently omitted the old file.
HISTORICAL = re.compile(
    r"`?([A-Za-z0-9_./-]+\.(?:json|md|tex|pdf))`?[^\n]{0,80}?"
    r"\b(?:historical|superseded|preserved|old|previous|prior)\b"
    r"|\b(?:historical|superseded|preserved|old|previous|prior)\b[^\n]{0,80}?"
    r"`?([A-Za-z0-9_./-]+\.(?:json|md|tex|pdf))`?",
    re.IGNORECASE,
)

#: A README is unambiguous when it designates one item as current, however many
#: it mentions. These are the forms the papers actually use.
DESIGNATION = re.compile(
    r"(?:current(?:ly)?\s+(?:claim\s+)?(?:authority|manuscript|readiness)"
    r"[^\n]{0,40}?|\*\*Current[^*]{0,40}?:\*\*\s*)`?([A-Za-z0-9_./-]+\.(?:json|md|tex|pdf))",
    re.IGNORECASE,
)

PATTERNS = {
    "manuscript": re.compile(r"(MANUSCRIPT[A-Z0-9_]*\.md|manuscript/[A-Za-z0-9_./-]+\.(?:md|tex|pdf))"),
    "authority": re.compile(r"([A-Z0-9]+_ACTIVE_CLAIM_AUTHORITY_V\d+\.json)"),
    "readiness": re.compile(r"([A-Z_]*READINESS[A-Z_]*\.md)"),
}


@dataclass
class PaperPointers:
    paper: str
    counts: dict[str, int] = field(default_factory=dict)
    names: dict[str, tuple[str, ...]] = field(default_factory=dict)
    readme_exists: bool = True

    designated: tuple[str, ...] = ()
    historical: tuple[str, ...] = ()

    @property
    def ambiguous(self) -> list[str]:
        """Several mentioned AND none of them designated as current."""
        out = []
        for key, n in self.counts.items():
            names = self.names.get(key, ())
            # names marked historical do not compete for currency
            live = [x for x in names if x not in self.historical]
            if len(live) <= 1:
                continue
            if any(d in names for d in self.designated):
                continue
            out.append(key)
        return sorted(out)

    @property
    def absent(self) -> list[str]:
        return sorted(k for k, n in self.counts.items() if n == 0)


def audit_repository(root: Path | None = None) -> list[PaperPointers]:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    out: list[PaperPointers] = []
    for paper_id, canonical_name in CANONICAL:
        d = papers / canonical_name
        if not d.is_dir():
            # Synthetic test trees and incomplete historical checkouts may not
            # carry the current slug. Preserve the old prefix fallback there,
            # but never let a retained redirect outrank a present canonical
            # directory (for example P2's retired paper-02-global-* redirect).
            prefix = f"paper-{int(paper_id[1:]):02d}"
            matches = sorted(
                candidate
                for candidate in papers.iterdir()
                if candidate.is_dir() and candidate.name.startswith(prefix)
            )
            if not matches:
                out.append(
                    PaperPointers(
                        canonical_name,
                        {key: 0 for key in PATTERNS},
                        {},
                        False,
                    )
                )
                continue
            d = matches[0]
        readme = d / "README.md"
        if not readme.is_file():
            out.append(PaperPointers(d.name, {k: 0 for k in PATTERNS}, {}, False))
            continue
        text = readme.read_text(errors="replace")
        rec = PaperPointers(d.name)
        for key, pattern in PATTERNS.items():
            found = tuple(sorted(set(pattern.findall(text))))
            rec.names[key] = found
            rec.counts[key] = len(found)
        rec.designated = tuple(sorted(set(DESIGNATION.findall(text))))
        rec.historical = tuple(sorted({g for pair in HISTORICAL.findall(text) for g in pair if g}))
        out.append(rec)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    # P13 is a documented exception rather than a defect: V3's own
    # historical_authority_note states "V2 remains the active authority for the
    # P13B leaf ... V3 adds the composed P13C leaf on top of the identical V2
    # leaves". Two active authorities is that paper's design, stated in the
    # record. #1131 asks for exactly one, which is a question for the author and
    # not something a checker should settle by choosing one.
    args = ap.parse_args(argv)
    try:
        records = audit_repository(args.root)
    except FileNotFoundError as exc:
        print(f"README_POINTERS_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    exact = ambiguous = absent = 0
    for rec in records:
        if not rec.readme_exists:
            print(f"  NO README   {rec.paper}")
            absent += 1
            continue
        marks = " ".join(f"{k}={rec.counts[k]}" for k in sorted(PATTERNS))
        if rec.ambiguous:
            print(f"  AMBIGUOUS   {rec.paper:42s} {marks}  several: {rec.ambiguous}")
            ambiguous += 1
        elif rec.absent:
            print(f"  ABSENT      {rec.paper:42s} {marks}  none: {rec.absent}")
            absent += 1
        else:
            print(f"  EXACTLY ONE {rec.paper:42s} {marks}")
            exact += 1
    print(f"\nexactly one of each: {exact}   ambiguous: {ambiguous}   absent: {absent}")
    print("note: paper-13 declares two active authorities by design (V2 for the P13B")
    print("      leaf, V3 for the composed P13C leaf), stated in V3's own record.")
    print("      That is a design question for #1131, not a README defect.")
    if ambiguous:
        print("README_POINTERS_AMBIGUOUS: a README naming several has one and has not said which")
        return EXIT_AMBIGUOUS
    if absent:
        print("README_POINTERS_ABSENT: a README naming none may have none to name")
        return EXIT_MISSING
    print("README_POINTERS_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
