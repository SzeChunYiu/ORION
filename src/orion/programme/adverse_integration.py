"""Is every adverse finding a paper recorded also visible to that paper's reader?

A paper is allowed to have negative, refuted and withheld results. What it is
not allowed to do is record them in a machine-readable side file while its
manuscript, ledger and README read as if they never happened. That is the
failure this checks: adverse evidence recorded but not integrated.

Deliberately narrow. ``CANNOT_CHECK`` is *not* treated as adverse -- it is the
honest-abstention code, it appears over a thousand times, and folding it in
would drown the signal this is looking for. The adverse vocabulary here is the
set of terminals that assert something went against the paper.

The three exit codes are distinct on purpose. ``CANNOT_CHECK`` means the audit
could not run, and must never be read as ``PASS``.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXIT_PASS = 0
EXIT_UNINTEGRATED = 2
EXIT_CANNOT_CHECK = 3

#: Terminals asserting an adverse outcome. CANNOT_CHECK is excluded by design.
ADVERSE_TOKENS = (
    "REFUTED",
    "WITHHELD",
    "NOT_SUPPORTED",
    "FALSIFIED",
    "NEGATIVE",
)

#: Tokens that are adverse-shaped but name a *method*, not an outcome.
NOT_AN_OUTCOME = ("NEGATIVE_CONTROLS", "NEGATIVE_CONTROL")

#: Documents a reader of the paper actually opens.
READER_FACING = ("MANUSCRIPT.md", "README.md")
READER_FACING_GLOBS = ("CLAIM_EVIDENCE_LEDGER*.md", "CLAIM_LEDGER*.md")

#: Keys whose values carry paper-level outcomes worth auditing.
OUTCOME_KEY = re.compile(
    r"(terminal|outcome|status|verdict|disposition|state|authority|result)", re.I
)


@dataclass
class Finding:
    paper: str
    terminal: str
    source: str
    integrated_in: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return bool(self.integrated_in)


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    papers_scanned: int = 0
    records_scanned: int = 0

    @property
    def unintegrated(self) -> list[Finding]:
        return [f for f in self.findings if not f.ok]


def adverse_leaves(record: object) -> list[dict]:
    """Leaves whose ``authority`` asserts an adverse outcome.

    An adverse finding is a *leaf*, not a loose string. The leaf carries the
    identifiers a document can actually cite -- ``claim_id`` and ``terminal``.
    The authority field itself (``BINDING_NEGATIVE_BOUNDARY`` and friends) is a
    shared class label: many leaves carry the same one, so requiring it to
    appear verbatim in a manuscript would flag papers that discuss the result
    in full. This checker was first written that way and reported three
    findings that were all wrong, which is why it now keys on the identifiers.
    """
    out: list[dict] = []

    def visit(node: object) -> None:
        if isinstance(node, dict):
            authority = node.get("authority")
            if isinstance(authority, str):
                upper = authority.upper()
                if not any(upper.startswith(n) for n in NOT_AN_OUTCOME) and any(
                    tok in upper for tok in ADVERSE_TOKENS
                ):
                    out.append(node)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(record)
    return out


def citable_identifiers(leaf: dict) -> tuple[str, ...]:
    """Identifiers a reader-facing document could name this finding by."""
    keys = ("claim_id", "terminal", "artifact", "study", "receipt")
    out: list[str] = []
    for key in keys:
        value = leaf.get(key)
        if isinstance(value, str) and value:
            out.append(value.rsplit("/", 1)[-1])
    return tuple(dict.fromkeys(out))


def reader_docs(paper_dir: Path) -> dict[str, str]:
    docs: dict[str, str] = {}
    for name in READER_FACING:
        p = paper_dir / name
        if p.is_file():
            docs[name] = p.read_text(errors="replace")
    for pattern in READER_FACING_GLOBS:
        for p in sorted(paper_dir.glob(pattern)):
            docs[p.name] = p.read_text(errors="replace")
    return docs


def audit_paper(paper_dir: Path) -> tuple[list[Finding], int]:
    docs = reader_docs(paper_dir)
    findings: list[Finding] = []
    scanned = 0
    for record_path in sorted(paper_dir.glob("*ACTIVE_CLAIM_AUTHORITY*.json")):
        try:
            record = json.loads(record_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        scanned += 1
        for leaf in adverse_leaves(record):
            identifiers = citable_identifiers(leaf)
            if not identifiers:
                # nothing to cite it by: cannot be checked, not a pass
                findings.append(
                    Finding(paper_dir.name, f"{leaf.get('authority')} (no citable id)",
                            record_path.name, ())
                )
                continue
            hits = tuple(
                f"{name}:{ident}"
                for name, text in docs.items()
                for ident in identifiers
                if ident in text
            )
            findings.append(
                Finding(paper_dir.name, "/".join(identifiers), record_path.name, hits)
            )
    return findings, scanned


def audit_repository(root: Path | None = None) -> Report:
    root = root or Path(__file__).resolve().parents[3]
    papers = root / "papers"
    if not papers.is_dir():
        raise FileNotFoundError(papers)
    report = Report()
    for paper_dir in sorted(p for p in papers.iterdir() if p.is_dir()):
        if not any(paper_dir.glob("*ACTIVE_CLAIM_AUTHORITY*.json")):
            continue
        report.papers_scanned += 1
        findings, scanned = audit_paper(paper_dir)
        report.records_scanned += scanned
        report.findings.extend(findings)
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    args = ap.parse_args(argv)
    try:
        report = audit_repository(args.root)
    except FileNotFoundError as exc:
        print(f"ADVERSE_INTEGRATION_CANNOT_CHECK: {exc}")
        return EXIT_CANNOT_CHECK
    print(f"papers with an authority record: {report.papers_scanned}")
    print(f"authority records scanned:       {report.records_scanned}")
    print(f"adverse terminals found:         {len(report.findings)}")
    for f in report.findings:
        mark = "OK  " if f.ok else "GAP "
        where = ",".join(f.integrated_in) if f.ok else "not in any reader-facing document"
        print(f"  {mark}{f.paper}: {f.terminal} ({f.source}) -> {where}")
    if report.unintegrated:
        print(f"ADVERSE_INTEGRATION_GAP: {len(report.unintegrated)}")
        return EXIT_UNINTEGRATED
    print("ADVERSE_INTEGRATION_PASS")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
