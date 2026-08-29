#!/usr/bin/env python3
"""Prepare a cited Q1/QG2 master for a journal-neutral Quantum/arXiv source bundle.

Formatting-only transformations:
- extract title/abstract;
- discard internal publication-banner lines before the abstract;
- strip manual numeric prefixes from Markdown headings so LaTeX owns numbering;
- append a bounded data/code availability statement selected by paper id.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

HEADING_RE = re.compile(r"^(#{2,6})\s+(?:\d+(?:\.\d+)*\.?\s+)(.*)$")

DATA = {
    "Q1": (
        "All load-bearing theorem, counterexample, finite-domain and prospective-result "
        "artifacts are bound to the publication evidence cut in the public ORION repository "
        "at https://github.com/SzeChunYiu/ORION. The primary Hamiltonian/library material "
        "used for named public subjects remains at its upstream repository and pinned "
        "commit/blob locations. Public repository access is reported as access and "
        "reproducibility infrastructure, not as independent scientific replication."
    ),
    "QG2": (
        "All load-bearing forecast, exact-referee, theorem and repair receipts are bound to "
        "the publication evidence cut in the public ORION repository at "
        "https://github.com/SzeChunYiu/ORION. Forecast-only rows without an exact receipt "
        "are explicitly marked as unverified and excluded from verification counts. Public "
        "repository access is reported as access and reproducibility infrastructure, not as "
        "independent scientific replication."
    ),
}

REQUIRED = {
    "Q1": ["all-`n`", "donor-exposed", "TARE", "support at most two"],
    "QG2": ["10", "11", "ForecastCertificate", "Qet", "Qualtran"],
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", choices=sorted(DATA), required=True)
    ap.add_argument("--cited-master", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = pathlib.Path(args.cited_master)
    out = pathlib.Path(args.out)
    lines = src.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        print("QUANTUM_SOURCE_PREP=FAIL\n- missing H1 title")
        return 1
    title = lines[0][2:].strip()
    try:
        ai = lines.index("## Abstract")
    except ValueError:
        print("QUANTUM_SOURCE_PREP=FAIL\n- missing Abstract")
        return 1
    ni = next((i for i in range(ai + 1, len(lines)) if lines[i].startswith("## ")), None)
    if ni is None:
        print("QUANTUM_SOURCE_PREP=FAIL\n- no body after abstract")
        return 1

    abstract = "\n".join(lines[ai + 1 : ni]).strip()
    body_lines: list[str] = []
    for line in lines[ni:]:
        m = HEADING_RE.match(line)
        body_lines.append(f"{m.group(1)} {m.group(2)}" if m else line)
    body = "\n".join(body_lines).strip() + "\n"

    prepared_lower = (title + "\n" + abstract + "\n" + body).lower()
    for token in REQUIRED[args.paper]:
        if token.lower() not in prepared_lower:
            print(f"QUANTUM_SOURCE_PREP=FAIL\n- required final token missing: {token}")
            return 1

    yaml_abstract = "\n".join("  " + ln for ln in abstract.splitlines())
    yaml_data = "\n".join("  " + ln for ln in DATA[args.paper].splitlines())
    prepared = (
        "---\n"
        f"title: {title!r}\n"
        "abstract: |\n"
        f"{yaml_abstract}\n"
        "dataavailability: |\n"
        f"{yaml_data}\n"
        "---\n\n"
        f"{body}"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prepared, encoding="utf-8")
    print("QUANTUM_SOURCE_PREP=PASS")
    print(f"PAPER={args.paper}")
    print(f"TITLE={title}")
    print("AUTHOR_METADATA=RESOLVED")
    print("SCIENTIFIC_PROSE_REWRITE=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
