"""Do a paper's reader-facing documents cite the same active authority?

A paper typically has three surfaces a reader meets: the manuscript, the claim
ledger and the readiness report. When two cite an authority record and the third
cites none, the third is free-floating -- and nothing will flag it when the
authority moves, because it is not reading from one. That is how a readiness
decision outlives the evidence it was based on.

This is the drift the stale-authority audit in #1169 caught after it had already
produced wrong statements in P12 and P15. Catching it as misalignment finds the
same defect a version earlier, while the documents still agree on content and
only disagree on what they are bound to.

Citing a superseded version alongside the current one is not misalignment. A
document may name V2 while designating V3 as current, which the supersession
checker already governs; what matters here is the *set* of versions each surface
treats as active.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXIT_PASS = 0
EXIT_MISALIGNED = 2
EXIT_CANNOT_CHECK = 3

SURFACES = {
    "manuscript": ("MANUSCRIPT.md", "manuscript/main.tex", "manuscript/FINAL.md", "manuscript/FINAL_V5.md"),
    "ledger": ("CLAIM_EVIDENCE_LEDGER.md", "CLAIM_EVIDENCE_LEDGER_V1.md", "CLAIM_LEDGER_V1.md"),
    "readiness": ("PEER_REVIEW_READINESS.md", "JOURNAL_READINESS.md"),
}
AUTHORITY = re.compile(r"([A-Z0-9]+)_ACTIVE_CLAIM_AUTHORITY_V(\d+)\.json")
#: Versions named as historical do not indicate what a surface is bound to.
HISTORICAL_NEAR = re.compile(
    r"\b(?:historical|superseded|preserved|previous|prior)\b", re.I
)
#: An explicit active designation wins over any nearby historical word. P11's
#: ledger says V2 "is the sole active lifecycle record. It binds the P11I leaf,
#: retains P11H..." -- "retains" governs a leaf, not the authority, and a naive
#: proximity rule read the sole active record as historical.
ACTIVE_NEAR = re.compile(
    r"\b(?:sole active|active authority|active lifecycle|current authority|"
    r"active claim authority|is the sole|binds)\b", re.I
)
WINDOW = 120


@dataclass
class Surfaces:
    paper: str
    cited: dict[str, set[str]] = field(default_factory=dict)
    present: dict[str, str] = field(default_factory=dict)

    @property
    def binding(self) -> dict[str, set[str]]:
        return {k: v for k, v in self.cited.items() if v}

    @property
    def unbound(self) -> list[str]:
        return sorted(k for k in self.present if not self.cited.get(k))

    @property
    def disagreeing(self) -> bool:
        sets = list(self.binding.values())
        return len(sets) > 1 and any(s != sets[0] for s in sets[1:])


def _active_versions(text: str) -> set[str]:
    """Versions the document treats as active, ignoring ones marked historical."""
    out: set[str] = set()
    for m in AUTHORITY.finditer(text):
        left = text[max(0, m.start() - WINDOW) : m.start()]
        right = text[m.end() : m.end() + WINDOW]
        window = left + " " + right
        if ACTIVE_NEAR.search(window):
            out.add(m.group(2))
            continue
        if HISTORICAL_NEAR.search(window):
            continue
        out.add(m.group(2))
    return out


def audit_repository(root: Path | None = None) -> list[Surfaces]:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    out: list[Surfaces] = []
    for d in sorted(p for p in papers.iterdir() if p.is_dir()):
        if not any(d.glob("*ACTIVE_CLAIM_AUTHORITY*.json")):
            continue
        rec = Surfaces(d.name)
        for role, names in SURFACES.items():
            for n in names:
                f = d / n
                if f.is_file():
                    rec.present[role] = n
                    rec.cited[role] = _active_versions(f.read_text(errors="replace"))
                    break
        out.append(rec)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        records = audit_repository(args.root)
    except FileNotFoundError as exc:
        print(f"AUTHORITY_ALIGNMENT_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    bad = 0
    for rec in records:
        cited = " ".join(
            f"{role}={'V' + ','.join(sorted(v)) if v else '-'}" for role, v in sorted(rec.cited.items())
        )
        if rec.disagreeing:
            print(f"  DISAGREE  {rec.paper:42s} {cited}")
            bad += 1
        elif rec.unbound:
            print(f"  UNBOUND   {rec.paper:42s} {cited}  free-floating: {rec.unbound}")
            bad += 1
        else:
            print(f"  ALIGNED   {rec.paper:42s} {cited}")
    print(f"\npapers with an authority record: {len(records)}   misaligned: {bad}")
    if bad:
        print("AUTHORITY_ALIGNMENT_MISALIGNED: a surface citing no authority cannot be")
        print("flagged when the authority moves, because it is not reading from one")
        return EXIT_MISALIGNED
    print("AUTHORITY_ALIGNMENT_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
