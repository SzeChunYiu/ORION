"""P1-P4 may not claim a 75+ publication score before their external gates pass.

Issue #1086 states the rule. A stated rule that nothing checks is a rule the
next document can quietly break, so this enforces it against the live tree.

The check is deliberately asymmetric. Claiming a score is what needs
justification; not claiming one needs none. A paper that says nothing about its
score passes trivially and correctly -- silence is not a violation. What fails
is a P1-P4 document asserting it has reached the bar while no artifact records
its external gate passing.

``CANNOT_CHECK`` is a separate exit code from ``PASS``. A tree that cannot be
read has not been found compliant.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXIT_PASS = 0
EXIT_UNGATED_CLAIM = 2
EXIT_CANNOT_CHECK = 3

#: The papers the rule names.
GATED_PAPERS = ("paper-01", "paper-02", "paper-03", "paper-04")

#: A score claim: a publication/readiness score at or above the bar.
SCORE_CLAIM = re.compile(
    r"(?:publication|readiness|journal|submission)\s*(?:-|\s)?score[^0-9\n]{0,24}(\d{2,3})"
    r"|(\d{2,3})\s*/\s*100\b"
    r"|scores?\s+(\d{2,3})\s*(?:points|/100)",
    re.IGNORECASE,
)
BAR = 75

#: Words marking the number as a target or threshold rather than an achievement.
#: "cannot reach 75 until H1-H6 execute" is the rule being obeyed, not broken.
ASPIRATIONAL = (
    "cannot", "may not", "only after", "target", "bar", "threshold", "gate",
    "required", "until", "would", "if ", "to reach", "not yet", "aim",
    "does not", "before",
)
CONTEXT = 160

#: Evidence that an external gate actually passed.
GATE_PASS_MARKERS = ("GATE_PASSED", "EXTERNAL_GATE_PASS", "gate_passed\": true")


@dataclass
class Claim:
    paper: str
    document: str
    value: int
    context: str
    gated: bool = False


@dataclass
class Report:
    claims: list[Claim] = field(default_factory=list)
    papers_scanned: int = 0
    documents_scanned: int = 0

    @property
    def ungated(self) -> list[Claim]:
        return [c for c in self.claims if not c.gated]


def _is_aspirational(text: str, start: int) -> bool:
    window = text[max(0, start - CONTEXT) : start].lower()
    return any(cue in window for cue in ASPIRATIONAL)


def _gate_evidence(paper_dir: Path) -> bool:
    for path in paper_dir.rglob("*"):
        if path.suffix.lower() not in {".json", ".md"} or not path.is_file():
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        if any(marker in text for marker in GATE_PASS_MARKERS):
            return True
    return False


def audit_repository(root: Path | None = None) -> Report:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    report = Report()
    for paper_dir in sorted(p for p in papers.iterdir() if p.is_dir()):
        if not any(paper_dir.name.startswith(p) for p in GATED_PAPERS):
            continue
        report.papers_scanned += 1
        has_gate = _gate_evidence(paper_dir)
        for path in sorted(paper_dir.glob("*.md")):
            text = path.read_text(errors="replace")
            report.documents_scanned += 1
            for match in SCORE_CLAIM.finditer(text):
                raw = next(g for g in match.groups() if g)
                value = int(raw)
                if value < BAR or value > 100:
                    continue
                if _is_aspirational(text, match.start()):
                    continue
                report.claims.append(
                    Claim(
                        paper=paper_dir.name,
                        document=path.name,
                        value=value,
                        context=" ".join(
                            text[max(0, match.start() - 90) : match.end() + 40].split()
                        ),
                        gated=has_gate,
                    )
                )
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        report = audit_repository(args.root)
    except FileNotFoundError as exc:
        print(f"PUBLICATION_SCORE_GATE_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    print(f"gated papers scanned:    {report.papers_scanned}")
    print(f"documents scanned:       {report.documents_scanned}")
    print(f"score claims at or above {BAR}: {len(report.claims)}")
    for claim in report.claims:
        mark = "GATED" if claim.gated else "UNGATED"
        print(f"  {mark} {claim.paper}/{claim.document}: {claim.value} -- {claim.context[:120]}")
    if report.ungated:
        print(f"PUBLICATION_SCORE_GATE_UNGATED_CLAIM: {len(report.ungated)}")
        return EXIT_UNGATED_CLAIM
    print("PUBLICATION_SCORE_GATE_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
