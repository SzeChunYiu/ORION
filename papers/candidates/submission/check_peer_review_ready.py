#!/usr/bin/env python3
"""Deterministic structural gate for the P6-P8 journal submission packages.

This checker establishes package completeness, not scientific novelty or peer review.
It intentionally uses only the Python standard library.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAPERS = ROOT / "papers"
CAND = PAPERS / "candidates"

P6 = PAPERS / "paper-06-formal-epistemic-structures-and-mechanics" / "submission"
P7 = PAPERS / "paper-07-epistemic-navigation-open-worlds" / "submission"
P8 = PAPERS / "paper-08-epistemic-authority-autonomous-science" / "submission"

REQUIRED_PROGRAMME = [
    CAND / "P6_P10_ISSUE_RECONCILIATION_2026-08-18.md",
    CAND / "PEER_REVIEW_READY_GATE_2026-08-18.md",
    CAND / "PRE_SUBMISSION_LITERATURE_DELTA_2026-08-18.md",
    CAND / "VENUE_REQUIREMENTS_VERIFIED_2026-08-18.md",
    CAND / "SUBMISSION_CLAIM_AUTHORITY_V1.md",
    CAND / "PEER_REVIEW_READY_PACKAGE.md",
    CAND / "submission" / "build_and_audit_p6_p8_pdfs.py",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def text(path: Path) -> str:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def visible_words(s: str) -> list[str]:
    s = re.sub(r"\\[A-Za-z]+(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", s)
    s = re.sub(r"[$\\{}_^~]", " ", s)
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", s)


def check_citation_closure(s: str, path: Path) -> None:
    bibkeys = re.findall(r"\\bibitem\{([^}]+)\}", s)
    require(len(bibkeys) == len(set(bibkeys)), f"duplicate bibliography key in {path}")
    require(bibkeys, f"empty bibliography in {path}")

    cited: set[str] = set()
    for group in re.findall(r"\\cite\{([^}]+)\}", s):
        cited.update(k.strip() for k in group.split(",") if k.strip())
    missing = sorted(cited.difference(bibkeys))
    require(not missing, f"citation keys missing from bibliography in {path}: {missing}")


def check_tex(path: Path, *, jaamas: bool = False) -> None:
    s = text(path)
    lower = s.lower()
    require("\\begin{document}" in s and "\\end{document}" in s, f"document wrapper missing: {path}")
    require(s.count("{") == s.count("}"), f"unbalanced braces in {path}")
    for env in ("document", "abstract", "thebibliography"):
        require(s.count(f"\\begin{{{env}}}") == s.count(f"\\end{{{env}}}"),
                f"unbalanced {env} environment in {path}")
    require("\\begin{abstract}" in s and "\\end{abstract}" in s, f"abstract missing: {path}")
    require("\\section{introduction}" in lower, f"Introduction missing: {path}")
    require("\\section{limitations}" in lower, f"Limitations missing: {path}")
    require("\\section{conclusion}" in lower, f"Conclusion missing: {path}")
    require("\\begin{thebibliography}" in s, f"reference list missing: {path}")
    require("\\bibitem{" in s and "\\cite{" in s, f"in-text/reference citations missing: {path}")
    check_citation_closure(s, path)
    require("chatgpt" in lower and "openai" in lower, f"AI-use disclosure missing: {path}")
    require("stockholm university" in lower and "sze-chun.yiu@fysik.su.se" in lower,
            f"author/corresponding metadata missing: {path}")
    for bad in ("TODO", "TBD", "PLACEHOLDER", "INSERT CITATION", "FIXME"):
        require(bad not in s, f"submission placeholder {bad!r} in {path}")
    # Submitted papers may discuss priority language as a nonclaim; common sales
    # formulations themselves are prohibited by the submission contract.
    for banned in ("we are the first", "first-ever", "first of its kind", "unprecedented framework"):
        require(banned not in lower, f"unsupported novelty phrase {banned!r} in {path}")

    if jaamas:
        m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", s, flags=re.S)
        require(m is not None, "JAAMAS abstract parse failed")
        n = len(visible_words(m.group(1)))
        require(150 <= n <= 250, f"JAAMAS abstract must be 150-250 words, got {n}")
        km = re.search(r"\\textbf\{Keywords:\}\s*(.+)", s)
        require(km is not None, "JAAMAS keywords missing")
        keywords = [x.strip() for x in km.group(1).split(";") if x.strip()]
        require(4 <= len(keywords) <= 6, f"JAAMAS requires 4-6 keywords, got {len(keywords)}")
        require("statements and declarations" in lower, "JAAMAS Statements and Declarations missing")
        require("use of large language models" in lower, "JAAMAS LLM-use section missing")


def check_highlights(path: Path) -> None:
    lines = [ln.strip() for ln in text(path).splitlines() if ln.strip()]
    require(3 <= len(lines) <= 5, f"Elsevier highlights must contain 3-5 bullets: {path}")
    for line in lines:
        require(len(line) <= 85, f"highlight exceeds 85 chars ({len(line)}): {line}")


def check_jaamas_sheet(path: Path) -> None:
    s = text(path).lower()
    for marker in (
        "## 1.", "## 2.", "## 3.", "## 4.",
        "main claim", "evidence", "closest", "published before",
    ):
        require(marker in s, f"JAAMAS information-sheet requirement missing: {marker}")
    require(len(visible_words(s)) >= 700, "JAAMAS information sheet is not substantive enough")


def main() -> None:
    for path in REQUIRED_PROGRAMME:
        text(path)

    check_tex(P6 / "AIJ_MANUSCRIPT.tex")
    p6_text = text(P6 / "AIJ_MANUSCRIPT.tex")
    p6_flat = " ".join(p6_text.split())
    for marker in (
        "Sequential composition is",
        "A conditional requires",
        "Independent parallel composition",
        "Recursive composition additionally requires",
    ):
        require(marker in p6_flat, f"P6 composition form missing: {marker}")
    check_highlights(P6 / "HIGHLIGHTS.txt")
    text(P6 / "COVER_LETTER.md")

    check_tex(P7 / "AIJ_MANUSCRIPT.tex")
    p7_text = text(P7 / "AIJ_MANUSCRIPT.tex")
    p7_flat = " ".join(p7_text.split())
    for marker in (
        "A route identity binds",
        "Structural equivalence requires",
        "DEFER\\_REVISIT",
        "A forced reframe requires",
    ):
        require(marker in p7_flat, f"P7 route/recovery primitive missing: {marker}")
    check_highlights(P7 / "HIGHLIGHTS.txt")
    text(P7 / "COVER_LETTER.md")

    check_tex(P8 / "JAAMAS_MANUSCRIPT.tex", jaamas=True)
    p8_text = text(P8 / "JAAMAS_MANUSCRIPT.tex")
    p8_flat = " ".join(p8_text.split())
    for marker in (
        "absence of an observed blocker",
        "Confidence, expected utility, support, and permission",
        "Authority is non-monotone",
        "Demotion is forward-only",
        "Protected custody is likewise one root class",
    ):
        require(marker in p8_flat, f"P8 V2.1 reviewer-facing primitive missing: {marker}")
    check_jaamas_sheet(P8 / "JAAMAS_INFORMATION_SHEET.md")
    text(P8 / "COVER_LETTER.md")

    lit = text(CAND / "PRE_SUBMISSION_LITERATURE_DELTA_2026-08-18.md")
    require("Round 1" in lit and "Round 2" in lit, "two literature rounds not frozen")
    require("SUBMISSION_SCOPED_RESIDUALS = STABLE_2026_08_18" in lit,
            "literature terminal missing")

    claims = text(CAND / "SUBMISSION_CLAIM_AUTHORITY_V1.md")
    for paper in ("P6-S1", "P7-S1", "P8-S1"):
        require(paper in claims, f"submission claim authority missing for {paper}")
    require("SUBMISSION_HEADLINE_AUTHORITY = COMPLETE" in claims,
            "submission claim-authority terminal missing")
    require("empirical superiority over ideal donor product: `CANNOT_CHECK / NOT CLAIMED`" in claims,
            "empirical-superiority nonclaim missing")

    workflow = text(ROOT / ".github" / "workflows" / "p6-p8-candidate-ci.yml")
    require("Build and audit submission PDFs" in workflow,
            "submission PDF build/audit is not wired into candidate CI")
    require("Archive audited submission PDFs" in workflow,
            "audited submission PDFs are not retained as an exact-head artifact")

    print("P6-P8 peer-review-ready structural gate: PASS")


if __name__ == "__main__":
    main()
