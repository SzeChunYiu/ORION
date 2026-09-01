#!/usr/bin/env python3
"""Fail closed on the current ORION-13 Brief Report claim surface."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/orion-13-global-knowledge-portrait"
SOURCE = PAPER / "manuscript/brief-report-final"


def main() -> int:
    common = (SOURCE / "common.tex").read_text(encoding="utf-8")
    adapters = "\n".join(
        (SOURCE / name).read_text(encoding="utf-8")
        for name in ("main.tex", "arxiv.tex")
    )
    bibliography = (SOURCE / "bibliography.bib").read_text(encoding="utf-8")
    authority = (PAPER / "SCOPED_PUBLICATION_TRACK_V1.md").read_text(
        encoding="utf-8"
    )
    text = common + "\n" + adapters
    surface = re.sub(r"\s+", " ", text)
    errors: list[str] = []

    required = {
        "holdout denominator": "32-case holdout",
        "false-merge contrast": "six of 32",
        "paired effect": "-0.1875",
        "fixed-panel diagnostic": "[-0.34375,-0.0625]",
        "false-split null": "false-split difference",
        "family-level breadth": "three authored families",
        "other-family non-discrimination": "other two families (19 cases)",
        "effective conformance states": "eight unique decision archetypes",
        "complete result": "400/400",
        "narrow-interface comparator": "250/400",
        "canonical result": "50/400",
        "same-programme limitation": "same authorship and research programme",
        "raw-text boundary": "raw-text extraction",
        "downstream boundary": "downstream scientific utility",
        "population boundary": "population error rates",
    }
    for label, fragment in required.items():
        if fragment not in surface:
            errors.append(f"missing {label}: {fragment}")

    forbidden = {
        "internal tier label": r"(?i)tier[ _-]?b",
        "private decision token": r"\b(?:CANNOT_CHECK|P3_[A-Z0-9_]+)\b",
        "internal workflow": r"(?i)hostile review|peer.review.ready|package.complete",
        "population inference": r"(?i)population confidence interval",
        "deployed superiority": r"(?i)superior(?:ity)? to deployed",
        "full-paper status": r"(?i)full[- ]length article|full paper",
    }
    for label, pattern in forbidden.items():
        if re.search(pattern, text):
            errors.append(f"forbidden {label}")

    common_surface = re.sub(r"\s+", " ", common)
    if "They do not establish population error" not in common_surface:
        errors.append("abstract does not bound the population interpretation")
    if "Those nulls indicate absent comparison opportunity, not dispensability" not in common_surface:
        errors.append("zero-effect ablations are not retained as bounded nulls")
    if "information-equivalent typed comparator" not in common_surface or "must tie" not in common_surface:
        errors.append("information-equivalent comparator tie is not explicit")

    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography))
    cite_keys: set[str] = set()
    for group in re.findall(r"\\cite\w*\{([^}]+)\}", common):
        cite_keys.update(key.strip() for key in group.split(",") if key.strip())
    missing_citations = sorted(cite_keys - bib_keys)
    if missing_citations:
        errors.append("missing bibliography keys: " + ",".join(missing_citations))

    if "RECLASSIFIED_AS_BRIEF_REPORT" not in authority:
        errors.append("active authority does not record the Brief Report disposition")
    for fragment in ("eight unique", "narrower terminal", "information-equivalent"):
        if fragment not in authority:
            errors.append(f"active authority missing scientific-mass boundary: {fragment}")

    if errors:
        for error in errors:
            print(f"P3_CLAIM_SURFACE_ERROR: {error}")
        return 1
    print("P3_BRIEF_REPORT_BOUNDED_CLAIM_SURFACE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
