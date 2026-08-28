#!/usr/bin/env python3
"""Generate the IP&M CAS single-column adapter from the canonical manuscript."""

from __future__ import annotations

import argparse
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
MAIN = PAPER / "manuscript" / "main.tex"
TARGET = PAPER / "manuscript" / "ipm_submission.tex"


def render(source: str) -> str:
    replacements = (
        (
            r"\documentclass[11pt]{article}",
            r"\documentclass[a4paper,fleqn]{cas-sc}" + "\n" + r"\usepackage{natbib}",
        ),
        (r"\usepackage[margin=1in]{geometry}" + "\n", ""),
        (r"\usepackage[hidelinks]{hyperref}" + "\n", ""),
        (r"\title{", r"\title[mode=title]{"),
        (r"\author{Anonymous authors}", r"\author[1]{Anonymous authors}"),
        (
            r"\begin{document}" + "\n",
            r"\begin{document}"
            + "\n"
            + r"\shorttitle{Acquisition Is Not Closure}"
            + "\n"
            + r"\shortauthors{Anonymous authors}"
            + "\n",
        ),
        (
            r"\maketitle" + "\n",
            r"\maketitle"
            + "\n"
            + r"\hypersetup{pdfauthor={Anonymous authors},pdftitle={Acquisition Is Not Closure: Fail-Closed Control for Open-World Scientific-Literature Discovery}}"
            + "\n",
        ),
    )
    rendered = source
    for old, new in replacements:
        if old not in rendered:
            raise ValueError(f"canonical source is missing adapter anchor: {old!r}")
        rendered = rendered.replace(old, new, 1)
    return "% Generated target adapter from main.tex; do not edit by hand.\n" + rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(MAIN.read_text(encoding="utf-8"))
    if args.check:
        if not TARGET.exists() or TARGET.read_text(encoding="utf-8") != expected:
            raise SystemExit("IP&M adapter drifted from canonical main.tex")
        print("IP&M adapter matches canonical main.tex")
        return 0
    TARGET.write_text(expected, encoding="utf-8")
    print(f"wrote {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
