#!/usr/bin/env python3
"""Prepare the Q4 cited Markdown for the official TMLR wrapper.

Allowed transformations are formatting-only:
- extract title and abstract;
- drop publication-internal provenance banner lines before the abstract;
- remove manual numeric prefixes from Markdown headings so LaTeX owns numbering;
- preserve all body prose, numbers and citation tokens otherwise.
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
    text = src.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        print("Q4_TMLR_PREP=FAIL\n- missing H1 title")
        return 1
    title = lines[0][2:].strip()

    try:
        abstract_i = lines.index("## Abstract")
    except ValueError:
        print("Q4_TMLR_PREP=FAIL\n- missing ## Abstract")
        return 1

    next_h2 = None
    for i in range(abstract_i + 1, len(lines)):
        if lines[i].startswith("## "):
            next_h2 = i
            break
    if next_h2 is None:
        print("Q4_TMLR_PREP=FAIL\n- abstract has no following H2")
        return 1

    abstract_lines = lines[abstract_i + 1 : next_h2]
    while abstract_lines and not abstract_lines[0].strip():
        abstract_lines.pop(0)
    while abstract_lines and not abstract_lines[-1].strip():
        abstract_lines.pop()
    abstract = "\n".join(abstract_lines).strip()
    if not abstract:
        print("Q4_TMLR_PREP=FAIL\n- empty abstract")
        return 1

    body_lines = lines[next_h2:]
    normalized: list[str] = []
    for line in body_lines:
        m = HEADING_RE.match(line)
        if m:
            line = f"{m.group(1)} {m.group(2)}"
        normalized.append(line)
    body = "\n".join(normalized).strip() + "\n"

    # Make a Pandoc YAML metadata block. Use a YAML literal for abstract to preserve
    # Markdown citations/emphasis in the abstract.
    yaml_abstract = "\n".join("  " + ln for ln in abstract.splitlines())
    prepared = (
        "---\n"
        f"title: {title!r}\n"
        "abstract: |\n"
        f"{yaml_abstract}\n"
        "---\n\n"
        f"{body}"
    )

    # Hard scientific-content guards.
    for token in (
        "Typed and Scoped Partial-Knowledge State",
        "scope invalidation",
        "ContextNest",
        "ORION-23",
        "exact-synthetic",
    ):
        if token.lower() not in prepared.lower():
            print(f"Q4_TMLR_PREP=FAIL\n- required final-manuscript token missing: {token}")
            return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prepared, encoding="utf-8")
    print("Q4_TMLR_PREP=PASS")
    print(f"TITLE={title}")
    print(f"ABSTRACT_CHARS={len(abstract)}")
    print(f"BODY_CHARS={len(body)}")
    print("SCIENTIFIC_PROSE_REWRITE=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
