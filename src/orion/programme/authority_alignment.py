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

Only *disagreement* fails here. An earlier revision also failed a surface that
cited nothing, and that rule was wrong in six of seven cases: authority can bind
a surface by sha256 from the other direction (P10), a manuscript can be a PDF
with no citable text, and papers phrase the designation too many ways for a
proximity rule to read reliably. Worse, its recommended remedy for P10 -- add a
citation line -- would have changed bytes the authority record binds by digest,
breaking a tamper-evident receipt to satisfy a weaker prose convention. An
unreadable surface now exits CANNOT_CHECK and names the file to read.

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

#: A paper whose manuscript is only a rendered PDF has no citable text surface.
#: P10 ships manuscript/main.pdf and manuscript/sections/; reporting it as
#: free-floating says the manuscript cites no authority when the truth is that
#: nothing here can read it.
PDF_ONLY = ("manuscript/main.pdf",)

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
    r"active claim authority|active terminal|is the sole|binds)\b", re.I
)
WINDOW = 120


@dataclass
class Surfaces:
    paper: str
    cited: dict[str, set[str]] = field(default_factory=dict)
    present: dict[str, str] = field(default_factory=dict)
    split_declared: bool = False
    pdf_only: list[str] = field(default_factory=list)
    reverse_bound: list[str] = field(default_factory=list)

    @property
    def binding(self) -> dict[str, set[str]]:
        return {k: v for k, v in self.cited.items() if v}

    @property
    def unbound(self) -> list[str]:
        return sorted(k for k in self.present if not self.cited.get(k))

    @property
    def disagreeing(self) -> bool:
        if self.split_declared:
            return False
        sets = list(self.binding.values())
        return len(sets) > 1 and any(s != sets[0] for s in sets[1:])


#: A paper may deliberately split authority across records, each governing
#: different claims. P13's ledger says "Active authority is split" and then
#: assigns V1, V2 and V3 to different leaves. Reporting that as disagreement
#: accuses a paper of confusion for being explicit about its structure.
SPLIT_AUTHORITY = re.compile(
    r"\bauthority is split\b|\bsplit authority\b|\bactive authority is split\b", re.I
)

#: A citation inside a section or table whose heading marks it historical is
#: historical however far the heading is. P15 lists superseded records in a
#: two-row table; the heading sits beyond any fixed window for the second row,
#: so a proximity rule read a superseded record as active.
HEADING = re.compile(r"^(?:#{1,6}\s+.*|\|.*Superseded.*\||\|.*Historical.*\|)$", re.M | re.I)


def _governing_heading(text: str, pos: int) -> str:
    starts = [m for m in HEADING.finditer(text) if m.start() < pos]
    return starts[-1].group(0) if starts else ""


def _active_versions(text: str) -> set[str]:
    """Versions the document treats as active, ignoring ones marked historical."""
    out: set[str] = set()
    for m in AUTHORITY.finditer(text):
        heading = _governing_heading(text, m.start())
        if HISTORICAL_NEAR.search(heading) or re.search(r"superseded", heading, re.I):
            continue
        left = text[max(0, m.start() - WINDOW) : m.start()]
        right = text[m.end() : m.end() + WINDOW]
        # When both an active and a historical marker sit near a citation, the
        # closer one governs. A sentence naming both records -- "came from the
        # historical, since-superseded V3; the current authority is V5" -- puts
        # "superseded" against V3 and "current authority" against V5, and a rule
        # that let either win outright mislabelled one of them.
        def _nearest(pattern) -> int | None:
            best = None
            for hit in pattern.finditer(left):
                best = len(left) - hit.end()
            for hit in pattern.finditer(right):
                d = hit.start()
                best = d if best is None else min(best, d)
                break
            return best

        near_active = _nearest(ACTIVE_NEAR)
        near_hist = _nearest(HISTORICAL_NEAR)
        if near_active is not None and (near_hist is None or near_active < near_hist):
            out.add(m.group(2))
            continue
        if near_hist is not None:
            continue
        out.add(m.group(2))
    return out


def _reverse_bound(paper_dir: Path, rel: str) -> set[str]:
    """Authority versions that bind ``rel`` by sha256 rather than being cited by it.

    P10's manuscript names no authority record, but V1 binds
    ``manuscript/main.tex`` by digest. That is a *stronger* tie than a prose
    citation: it is tamper-evident, and it moves when the authority moves. An
    earlier revision of this checker reported that manuscript as free-floating,
    and the obvious remedy -- adding a citation line -- would have changed the
    file's bytes and broken the very receipt the binding provides.
    """
    import json

    out: set[str] = set()
    for rec in sorted(paper_dir.glob("*ACTIVE_CLAIM_AUTHORITY*.json")):
        m = AUTHORITY.search(rec.name)
        if not m:
            continue
        try:
            data = json.loads(rec.read_text(errors="replace"))
        except (json.JSONDecodeError, OSError):
            continue
        bindings = data.get("evidence_bindings")
        if not isinstance(bindings, dict):
            continue
        for entry in bindings.values():
            artifact = entry.get("artifact") if isinstance(entry, dict) else entry
            if isinstance(artifact, str) and artifact.endswith("/" + rel):
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
        for rel in PDF_ONLY:
            if (d / rel).is_file() and not any((d / n).is_file() for n in SURFACES["manuscript"]):
                rec.pdf_only.append(rel)
        for role, names in SURFACES.items():
            for n in names:
                f = d / n
                if f.is_file():
                    rec.present[role] = n
                    cited = _active_versions(f.read_text(errors="replace"))
                    if not cited:
                        cited = _reverse_bound(d, n)
                        if cited:
                            rec.reverse_bound.append(role)
                    rec.cited[role] = cited
                    break
        blob = " ".join(
            (d / n).read_text(errors="replace")
            for names in SURFACES.values() for n in names if (d / n).is_file()
        )
        rec.split_declared = bool(SPLIT_AUTHORITY.search(blob))
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
    unread = 0
    for rec in records:
        cited = " ".join(
            f"{role}={'V' + ','.join(sorted(v)) if v else '-'}" for role, v in sorted(rec.cited.items())
        )
        if rec.disagreeing:
            print(f"  DISAGREE  {rec.paper:42s} {cited}")
            bad += 1
        elif rec.pdf_only and not rec.cited.get("manuscript"):
            print(f"  PDF ONLY  {rec.paper:42s} {cited}  manuscript is {rec.pdf_only[0]}, not text")
            unread += 1
        elif rec.unbound:
            print(f"  UNREAD    {rec.paper:42s} {cited}  no citation found in: {rec.unbound}")
            unread += 1
        else:
            print(f"  ALIGNED   {rec.paper:42s} {cited}")
    print(f"\npapers with an authority record: {len(records)}   "
          f"disagreeing: {bad}   unread: {unread}")
    if bad:
        print("AUTHORITY_ALIGNMENT_MISALIGNED: two surfaces of the same paper name")
        print("different records as active; at most one of them can be right")
        return EXIT_MISALIGNED
    if unread:
        print("AUTHORITY_ALIGNMENT_CANNOT_CHECK: a surface's authority could not be")
        print("read. That is not evidence it has none -- P10's manuscript is bound by")
        print("sha256 from the authority side, and a PDF has no citable text at all.")
        print("Read the named surface; do not treat this as a finding on its own.")
        return EXIT_CANNOT_CHECK
    print("AUTHORITY_ALIGNMENT_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
