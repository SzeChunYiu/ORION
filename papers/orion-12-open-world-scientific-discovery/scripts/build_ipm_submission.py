#!/usr/bin/env python3
"""Generate the attributed arXiv adapter from the canonical filing source.

The historical filename is retained because repository automation already calls
it. ``manuscript/ipm_submission.tex`` is the filing-science authority;
``manuscript/main.tex`` is a non-filing long-form research record.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
CANONICAL = PAPER / "manuscript" / "ipm_submission.tex"
ARXIV = PAPER / "manuscript" / "arxiv_submission.tex"


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f"expected one adapter anchor, found {source.count(old)}: {old!r}")
    return source.replace(old, new, 1)


def render(source: str) -> str:
    rendered = source
    rendered = replace_once(
        rendered,
        "% Canonical anonymous IP&M filing source.\n"
        "\\documentclass[a4paper,fleqn]{cas-sc}\n"
        "\\usepackage{natbib}\n",
        "% Generated attributed arXiv adapter from ipm_submission.tex; do not edit by hand.\n"
        "\\documentclass[11pt]{article}\n"
        "\\usepackage{natbib}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\usepackage[hidelinks]{hyperref}\n",
    )
    ipm_only = (
        "% IPM-ONLY BEGIN: CAS last-page footer correction\n"
        "% CAS records the page counter after a final \\clearpage; write the shipped-page\n"
        "% total after the class hook so the footer includes deferred figure pages.\n"
        "\\makeatletter\n"
        "\\AtEndDocument{%\n"
        "  \\immediate\\write\\@auxout{\\string\\csxdef{lastpage}{\\number\\numexpr\\value{page}-1\\relax}}%\n"
        "}\n"
        "\\makeatother\n"
        "% IPM-ONLY END: CAS last-page footer correction\n\n"
    )
    rendered = replace_once(rendered, ipm_only, "")
    rendered = replace_once(rendered, r"\title[mode=title]{", r"\title{")
    rendered = replace_once(
        rendered,
        r"\author[1]{Anonymous authors}",
        "\\author{Sze Chun Yiu\\\\Stockholm University\\\\"
        "\\texttt{sze-chun.yiu@fysik.su.se}}",
    )
    rendered = replace_once(
        rendered,
        "\\shorttitle{Acquisition Is Not Closure}\n"
        "\\shortauthors{Anonymous authors}\n",
        "",
    )
    rendered = replace_once(
        rendered,
        r"\hypersetup{pdfauthor={Anonymous authors},pdftitle={Acquisition Is Not Closure: Fail-Closed Control for Open-World Scientific-Literature Discovery}}",
        r"\hypersetup{pdfauthor={Sze Chun Yiu},pdftitle={Acquisition Is Not Closure: Fail-Closed Control for Open-World Scientific-Literature Discovery}}",
    )
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(CANONICAL.read_text(encoding="utf-8"))
    if args.check:
        if not ARXIV.exists() or ARXIV.read_text(encoding="utf-8") != expected:
            raise SystemExit("arXiv adapter drifted from canonical ipm_submission.tex")
        print("arXiv adapter matches canonical ipm_submission.tex")
        return 0
    ARXIV.write_text(expected, encoding="utf-8")
    print(f"wrote {ARXIV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
