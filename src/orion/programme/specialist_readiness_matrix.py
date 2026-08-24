"""One machine-readable P1-P15 specialist-readiness matrix.

Every field is derived from something in the tree and carries the path it came
from. Nothing is asserted: a field with no evidence is ABSENT with a reason,
never a default that reads like a finding.

The point of a matrix over prose is that a gap becomes addressable. "P7 has no
rights statement" is a task; a readiness paragraph that simply does not mention
rights is not, because nothing distinguishes it from one where rights were
considered and found fine.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_CANNOT_CHECK = 3

#: Paper numbers are not one-to-one with directory names: two directories start
#: paper-02 and two start paper-04. Taking the first alphabetically gives
#: paper-02-global-knowledge-portrait for P2, which is a different paper, and
#: the matrix then reports P2 as almost entirely absent. The slug for each
#: number is taken from the titles #1131 itself declares.
CANONICAL: tuple[tuple[str, str], ...] = (
    ("P1", "paper-01-recursive-epistemic-reconstruction"),
    ("P2", "paper-02-open-world-scientific-discovery"),
    ("P3", "paper-03-global-knowledge-portrait"),
    ("P4", "paper-04-verified-scientific-discovery"),
    ("P5", "paper-05-self-orion"),
    ("P6", "paper-06-formal-epistemic-structures-and-mechanics"),
    ("P7", "paper-07-epistemic-navigation-open-worlds"),
    ("P8", "paper-08-epistemic-authority-autonomous-science"),
    ("P9", "paper-09-structured-epistemic-learning"),
    ("P10", "paper-10-structured-problem-solving"),
    ("P11", "paper-11-state-as-computation"),
    ("P12", "paper-12-adaptive-state-reasoning"),
    ("P13", "paper-13-responsibility-carrying-state"),
    ("P14", "paper-14-orion-rse"),
    ("P15", "paper-15-orion-research-harness"),
)

FIELDS = (
    "SCIENTIFIC_RESULT",
    "CURRENT_MANUSCRIPT",
    "CURRENT_PDF",
    "RIGHTS",
    "REVIEWER_ACCESS",
    "TARGET_FIT",
    "INDEPENDENT_AUDIT",
    "SUBMISSION_BYTES",
    "TOP_TIER_GATE",
)

TERMINAL = re.compile(r"^\*\*(?:Current )?[Tt]erminal:\*\*\s*(.+)$", re.M)
TARGET = re.compile(r"(?:target venue|target journal|Target venue|submitted to|Target:)\s*[:\-]?\s*\*{0,2}([^\n*]{3,80})", re.I)
RIGHTS = re.compile(r"(licen[cs]e|rights|CC BY|MIT|Apache|ODC-By|redistribut)", re.I)
REVIEWER = re.compile(r"(reviewer[- ]access|controlled audit route|access route for reviewers|reviewer route)", re.I)
AUDIT = re.compile(r"(independent (?:reproduction|implementation|checker|audit)|second independent|structurally independent)", re.I)
BYTES = re.compile(r"(submission[- ]byte|SHA256SUMS|content[- ]bound|sha256)", re.I)
TOPTIER = re.compile(r"(TOP_TIER|top[- ]tier gate)", re.I)


def _first(paths: list[Path]) -> Path | None:
    return paths[0] if paths else None


def _scan(d: Path, pattern: re.Pattern[str], globs=("*.md",)) -> tuple[str, str] | None:
    for g in globs:
        for f in sorted(d.glob(g)):
            m = pattern.search(f.read_text(errors="replace"))
            if m:
                value = (m.group(1) if m.groups() else m.group(0)).strip()
                return value[:120], f.name
    return None


def derive(paper_dir: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}

    def put(field: str, hit, absent_reason: str) -> None:
        if hit:
            out[field] = {"status": "PRESENT", "value": hit[0], "source": hit[1]}
        else:
            out[field] = {"status": "ABSENT", "reason": absent_reason}

    put("SCIENTIFIC_RESULT", _scan(paper_dir, TERMINAL),
        "no **Terminal:** or **Current terminal:** line in any top-level document")

    auth = sorted(paper_dir.glob("*ACTIVE_CLAIM_AUTHORITY*.json"))
    if auth:
        out["SCIENTIFIC_RESULT"].setdefault("authority", auth[-1].name)

    man = _first(sorted(paper_dir.glob("MANUSCRIPT*.md")) + sorted(paper_dir.glob("manuscript/*.tex")))
    out["CURRENT_MANUSCRIPT"] = (
        {"status": "PRESENT", "value": man.name, "source": str(man.relative_to(paper_dir))}
        if man else {"status": "ABSENT", "reason": "no MANUSCRIPT*.md or manuscript/*.tex"}
    )

    pdf = _first(sorted(paper_dir.glob("manuscript/*.pdf")) + sorted(paper_dir.glob("*.pdf")))
    out["CURRENT_PDF"] = (
        {"status": "PRESENT", "value": pdf.name, "source": str(pdf.relative_to(paper_dir))}
        if pdf else {"status": "ABSENT", "reason": "no rendered PDF in the tree"}
    )

    put("RIGHTS", _scan(paper_dir, RIGHTS), "no licence, rights or redistribution statement found")
    put("REVIEWER_ACCESS", _scan(paper_dir, REVIEWER), "no reviewer-access or controlled audit route described")
    put("TARGET_FIT", _scan(paper_dir, TARGET), "no target venue or journal named")
    put("INDEPENDENT_AUDIT", _scan(paper_dir, AUDIT), "no independent reproduction, implementation or checker described")
    put("SUBMISSION_BYTES", _scan(paper_dir, BYTES), "no submission-byte binding, SHA256SUMS or content binding found")
    put("TOP_TIER_GATE", _scan(paper_dir, TOPTIER), "optional field; no top-tier gate referenced")
    return out


def build(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    matrix: dict[str, dict] = {}
    for pid, slug in CANONICAL:
        matches = [papers / slug] if (papers / slug).is_dir() else []
        if not matches:
            matrix[pid] = {"directory": None, "fields": {f: {"status": "CANNOT_CHECK",
                           "reason": f"expected directory {slug} does not exist"} for f in FIELDS}}
            continue
        d = matches[0]
        matrix[pid] = {"directory": d.name, "fields": derive(d)}
    return {
        "schema": "ORION.SpecialistReadinessMatrix.v1",
        "fields": list(FIELDS),
        "semantics": {
            "PRESENT": "evidence found in the tree; value and source path recorded",
            "ABSENT": "no evidence found; the reason names what was looked for",
            "CANNOT_CHECK": "the question could not be asked, distinct from answered no",
        },
        "derivation": "every value is read from the paper's own files; none is asserted",
        "papers": matrix,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--write", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        matrix = build(args.root)
    except FileNotFoundError as exc:
        print(f"READINESS_MATRIX_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    if args.write:
        args.write.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.write}")
    hdr = f"{'paper':6s}" + "".join(f"{f[:11]:12s}" for f in FIELDS)
    print(hdr)
    for pid, rec in matrix["papers"].items():
        row = f"{pid:6s}"
        for f in FIELDS:
            st = rec["fields"][f]["status"]
            row += f"{{'PRESENT':'yes','ABSENT':'-','CANNOT_CHECK':'?'}}[st]:12s".format() if False else f"{'yes' if st=='PRESENT' else ('-' if st=='ABSENT' else '?'):12s}"
        print(row)
    present = sum(1 for r in matrix["papers"].values() for f in FIELDS if r["fields"][f]["status"] == "PRESENT")
    total = len(matrix["papers"]) * len(FIELDS)
    print(f"\npopulated: {present}/{total} cells")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
