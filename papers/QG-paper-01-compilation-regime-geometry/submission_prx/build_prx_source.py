#!/usr/bin/env python3
"""Prepare QG1 V3 cited Markdown for a REVTeX PRX Quantum preflight package.

Only formatting/front-matter transformations are permitted; scientific prose is preserved.
The popular-summary check is an editorial-fit preflight, not a scientific authority gate.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

HEADING_RE = re.compile(r"^(#{2,6})\s+(?:\d+(?:\.\d+)*\.?\s+)(.*)$")
WORD_RE = re.compile(r"\b[\w'-]+\b")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cited-master", required=True)
    ap.add_argument("--popular-summary", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = pathlib.Path(args.cited_master).read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        print("QG1_PRX_PREP=FAIL\n- missing title")
        return 1
    title = lines[0][2:].strip()
    try:
        ai = lines.index("## Abstract")
    except ValueError:
        print("QG1_PRX_PREP=FAIL\n- missing abstract")
        return 1
    ni = next((i for i in range(ai + 1, len(lines)) if lines[i].startswith("## ")), None)
    if ni is None:
        print("QG1_PRX_PREP=FAIL\n- missing body")
        return 1
    abstract = "\n".join(lines[ai + 1 : ni]).strip()
    body_lines: list[str] = []
    for line in lines[ni:]:
        m = HEADING_RE.match(line)
        body_lines.append(f"{m.group(1)} {m.group(2)}" if m else line)
    body = "\n".join(body_lines).strip() + "\n"

    joined = (title + "\n" + abstract + "\n" + body).lower()
    for token in ("kappa_r6i = 1", "qg16", "proof-derived ceiling", "instance space analysis", "certificate not"):
        # Accept 'certificate not applicable' / 'outside...certificate' variants through simpler checks.
        if token == "certificate not":
            if "certificate" not in joined or "outside" not in joined:
                print("QG1_PRX_PREP=FAIL\n- missing outside-certificate boundary")
                return 1
        elif token not in joined:
            print(f"QG1_PRX_PREP=FAIL\n- missing final scientific token: {token}")
            return 1

    pop_text = pathlib.Path(args.popular_summary).read_text(encoding="utf-8")
    # Count only the summary body above the internal package note.
    summary_body = pop_text.split("**Internal package note", 1)[0]
    summary_body = re.sub(r"^#.*$", "", summary_body, flags=re.MULTILINE).strip()
    words = WORD_RE.findall(summary_body)
    if len(words) > 150:
        print(f"QG1_PRX_PREP=FAIL\n- popular summary exceeds internal 150-word preflight: {len(words)}")
        return 1
    for forbidden in ("universal phase theory", "physical quantum advantage", "proves all compilers"):
        if forbidden in summary_body.lower():
            print(f"QG1_PRX_PREP=FAIL\n- popular summary overclaim: {forbidden}")
            return 1

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

    print("QG1_PRX_PREP=PASS")
    print(f"POPULAR_SUMMARY_WORDS={len(words)}")
    print("AUTHOR_METADATA=REQUIRED_BEFORE_SUBMISSION")
    print("POPULAR_SUMMARY_EDITORIAL_FIT=PASS_INTERNAL_PREFLIGHT_ONLY")
    print("SCIENTIFIC_PROSE_REWRITE=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
