#!/usr/bin/env python3
"""Prepare the Q3 cited Markdown for the official anonymous TMLR wrapper.

Allowed transformations are formatting-only: extract title/abstract, drop publication-internal
banner lines, and remove manual heading-number prefixes. Scientific prose/numbers/citations
otherwise remain byte-preserved modulo those formatting operations.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

HEADING_RE = re.compile(r"^(#{2,6})\s+(?:\d+(?:\.\d+)*\.?\s+)(.*)$")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cited-master", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = pathlib.Path(args.cited_master)
    out = pathlib.Path(args.out)
    lines = src.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        print("Q3_TMLR_PREP=FAIL\n- missing H1 title")
        return 1
    title = lines[0][2:].strip()
    try:
        abstract_i = lines.index("## Abstract")
    except ValueError:
        print("Q3_TMLR_PREP=FAIL\n- missing ## Abstract")
        return 1

    next_h2 = next((i for i in range(abstract_i + 1, len(lines)) if lines[i].startswith("## ")), None)
    if next_h2 is None:
        print("Q3_TMLR_PREP=FAIL\n- abstract has no following H2")
        return 1

    abstract_lines = lines[abstract_i + 1:next_h2]
    while abstract_lines and not abstract_lines[0].strip(): abstract_lines.pop(0)
    while abstract_lines and not abstract_lines[-1].strip(): abstract_lines.pop()
    abstract = "\n".join(abstract_lines).strip()
    if not abstract:
        print("Q3_TMLR_PREP=FAIL\n- empty abstract")
        return 1

    normalized=[]
    for line in lines[next_h2:]:
        m=HEADING_RE.match(line)
        normalized.append(f"{m.group(1)} {m.group(2)}" if m else line)
    body="\n".join(normalized).strip()+"\n"
    yaml_abstract="\n".join("  "+ln for ln in abstract.splitlines())
    prepared=("---\n"+f"title: {title!r}\n"+"abstract: |\n"+yaml_abstract+"\n---\n\n"+body)

    for token in (
        "Three-Question Case Series",
        "39,489",
        "agreement did not imply",
        "CONTAMINATED",
        "three valid units",
        "D2/D3",
    ):
        if token.lower() not in prepared.lower():
            print(f"Q3_TMLR_PREP=FAIL\n- required final-manuscript token missing: {token}")
            return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prepared, encoding="utf-8")
    print("Q3_TMLR_PREP=PASS")
    print(f"TITLE={title}")
    print(f"ABSTRACT_CHARS={len(abstract)}")
    print(f"BODY_CHARS={len(body)}")
    print("SCIENTIFIC_PROSE_REWRITE=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
