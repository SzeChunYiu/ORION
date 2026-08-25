#!/usr/bin/env python3
"""Convert Pandoc's Abstract section into a LaTeX abstract environment."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: postprocess_submission_tex_v5.py PATH")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    heading = "\\hypertarget{abstract}{%\n\\section{Abstract}\\label{abstract}}\n\n"
    if text.count(heading) != 1:
        raise SystemExit(f"expected one Pandoc Abstract heading in {path}")
    if text.count("\\textbf{Keywords:}") != 1:
        raise SystemExit(f"expected one Keywords marker in {path}")

    text = text.replace(heading, "\\begin{abstract}\n", 1)
    text = text.replace(
        "\\textbf{Keywords:}",
        "\\end{abstract}\n\n\\noindent\\textbf{Keywords:}",
        1,
    )
    path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
