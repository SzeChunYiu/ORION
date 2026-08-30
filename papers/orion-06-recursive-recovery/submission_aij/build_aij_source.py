#!/usr/bin/env python3
"""Prepare Q2 V3 cited Markdown for an AIJ/elsarticle preflight package.

Formatting-only transformations are permitted. Highlights are checked independently from the
scientific manuscript and grant no scientific authority.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

HEADING_RE = re.compile(r"^(#{2,6})\s+(?:\d+(?:\.\d+)*\.?\s+)(.*)$")

# pdfLaTeX in the release workflows does not accept every Unicode punctuation
# code point emitted by the scientific Markdown.  These substitutions are
# typography-only and preserve the scientific text/identifiers.
PDFLATEX_SAFE_REPLACEMENTS = {
    "′": "'",
    "″": "''",
}


def pdflatex_safe(text: str) -> str:
    for old, new in PDFLATEX_SAFE_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cited-master", required=True)
    ap.add_argument("--highlights", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = pathlib.Path(args.cited_master).read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        print("Q2_AIJ_PREP=FAIL\n- missing title")
        return 1
    title = lines[0][2:].strip()
    try:
        ai = lines.index("## Abstract")
    except ValueError:
        print("Q2_AIJ_PREP=FAIL\n- missing abstract")
        return 1
    ni = next((i for i in range(ai + 1, len(lines)) if lines[i].startswith("## ")), None)
    if ni is None:
        print("Q2_AIJ_PREP=FAIL\n- missing body")
        return 1
    abstract = "\n".join(lines[ai + 1 : ni]).strip()
    body_lines: list[str] = []
    for line in lines[ni:]:
        m = HEADING_RE.match(line)
        body_lines.append(f"{m.group(1)} {m.group(2)}" if m else line)
    body = "\n".join(body_lines).strip() + "\n"

    joined = (title + "\n" + abstract + "\n" + body).lower()
    for token in ("51-receipt", "23 publication graph nodes", "28", "13 asserted successor edges", "scienceagentbench", "scientistone"):
        if token.lower() not in joined:
            print(f"Q2_AIJ_PREP=FAIL\n- missing final scientific token: {token}")
            return 1

    highlights = [ln.strip() for ln in pathlib.Path(args.highlights).read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not (3 <= len(highlights) <= 5):
        print(f"Q2_AIJ_PREP=FAIL\n- highlights count must be 3-5: {len(highlights)}")
        return 1
    for line in highlights:
        if len(line) > 85:
            print(f"Q2_AIJ_PREP=FAIL\n- highlight exceeds 85 chars ({len(line)}): {line}")
            return 1

    # Normalize only known release-toolchain-incompatible punctuation after all
    # scientific-content/token checks, so the normalization cannot satisfy or
    # alter a scientific gate.
    title = pdflatex_safe(title)
    abstract = pdflatex_safe(abstract)
    body = pdflatex_safe(body)

    yaml_abstract = "\n".join("  " + ln for ln in abstract.splitlines())
    prepared = (
        "---\n"
        f"title: {title!r}\n"
        "abstract: |\n"
        f"{yaml_abstract}\n"
        "---\n\n"
        f"{body}"
    )
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prepared, encoding="utf-8")

    print("Q2_AIJ_PREP=PASS")
    print(f"HIGHLIGHTS={len(highlights)}")
    print("AUTHOR_METADATA=REQUIRED_BEFORE_SUBMISSION")
    print("PDFLATEX_SAFE_PUNCTUATION_NORMALIZATION=1")
    print("SCIENTIFIC_PROSE_REWRITE=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())