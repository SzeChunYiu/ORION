#!/usr/bin/env python3
"""Prepare a cited Q1/QG1/QG2 master for a quantum source bundle.

Default mode is formatting-only:
- extract title/abstract;
- discard internal publication-banner lines before the abstract;
- strip manual numeric prefixes from Markdown headings so LaTeX owns numbering;
- append a bounded data/code availability statement selected by paper id.

For venues with a hard abstract-length limit, ``--abstract-overrides-json`` may
replace only the abstract with a centrally reviewed claim-preserving compression.
The canonical cited master remains unchanged. This wrapper grants no scientific
or submission authority.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HEADING_RE = re.compile(r"^(#{2,6})\s+(?:\d+(?:\.\d+)*\.?\s+)(.*)$")
WORD_RE = re.compile(r"\b[\w'-]+\b")

DATA = {
    "Q1": (
        "All load-bearing theorem, counterexample, finite-domain and prospective-result "
        "artifacts are bound to the publication evidence cut in the public repository. "
        "The primary Hamiltonian/library material used for named public subjects remains "
        "at its upstream repository and pinned commit/blob locations. A permanent archive "
        "identifier and explicit reuse licence for ORION-authored code/receipts will be "
        "inserted only after the corresponding release is actually deposited and authorized."
    ),
    "QG1": (
        "All load-bearing exact theorems, finite maps, counterexamples, proof-system bounds, "
        "objective-certificate records and prospective refutations are bound to the publication "
        "evidence cut in the public repository. Public donor compiler/software identities remain "
        "at their upstream repositories and cited revisions. A permanent archive identifier and "
        "explicit reuse licence for ORION-authored code/receipts will be inserted only after an "
        "authorized release."
    ),
    "QG2": (
        "All load-bearing forecast, exact-referee, theorem and repair receipts are bound to "
        "the publication evidence cut in the publicly inspectable repository. Forecast-only "
        "rows without an exact receipt are explicitly marked as unverified and are excluded "
        "from verification counts. A permanent archive identifier and explicit reuse licence "
        "for ORION-authored code/receipts will be inserted only after an authorized release."
    ),
}

REQUIRED = {
    "Q1": ["all-`n`", "donor-exposed", "TARE", "support at most two"],
    "QG1": ["compilation regime geometry", "StabPrep", "SixLCU", "prospective", "refut"],
    "QG2": ["10", "11", "ForecastCertificate", "Qet", "Qualtran"],
}


def load_abstract_override(path: pathlib.Path, paper: str) -> str:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load abstract override file: {exc}") from exc
    if payload.get("schema") != "ORION.TQEAbstractOverrides.v1":
        raise ValueError("wrong abstract-override schema")
    abstracts = payload.get("abstracts")
    if not isinstance(abstracts, dict) or not isinstance(abstracts.get(paper), str):
        raise ValueError(f"missing abstract override for {paper}")
    abstract = abstracts[paper].strip()
    count = len(WORD_RE.findall(abstract))
    if not 150 <= count <= 250:
        raise ValueError(f"venue abstract word count {count} outside 150..250")
    return abstract


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", choices=sorted(DATA), required=True)
    ap.add_argument("--cited-master", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--abstract-overrides-json", default=None)
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

    canonical_abstract = "\n".join(lines[ai + 1 : ni]).strip()
    abstract = canonical_abstract
    abstract_mode = "CANONICAL"
    if args.abstract_overrides_json:
        try:
            abstract = load_abstract_override(pathlib.Path(args.abstract_overrides_json), args.paper)
        except ValueError as exc:
            print(f"QUANTUM_SOURCE_PREP=FAIL\n- {exc}")
            return 1
        abstract_mode = "VENUE_COMPRESSION"

    body_lines: list[str] = []
    for line in lines[ni:]:
        m = HEADING_RE.match(line)
        body_lines.append(f"{m.group(1)} {m.group(2)}" if m else line)
    body = "\n".join(body_lines).strip() + "\n"

    # Claim-bearing required tokens are checked against the canonical scientific
    # master plus body, not against the compressed abstract alone. This prevents
    # a venue word limit from forcing decorative keyword retention while still
    # ensuring the load-bearing scientific surface is present.
    prepared_lower = (title + "\n" + canonical_abstract + "\n" + body).lower()
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
    print(f"ABSTRACT_MODE={abstract_mode}")
    print(f"ABSTRACT_WORDS={len(WORD_RE.findall(abstract))}")
    print("AUTHOR_METADATA=REQUIRED_BEFORE_SUBMISSION")
    print("SCIENTIFIC_PROSE_REWRITE=0" if abstract_mode == "CANONICAL" else "SCIENTIFIC_PROSE_REWRITE=ABSTRACT_COMPRESSION_ONLY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
