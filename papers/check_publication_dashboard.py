#!/usr/bin/env python3
"""Structural guard for the papers publication dashboard.

This checker grants no scientific, venue, or submission authority. It only makes
portfolio-control drift fail visibly: all 25 canonical papers must have one
portfolio row and the README must retain the science-first status/wave contract.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "papers" / "README.md"
ALIASES = ROOT / "papers" / "PAPER_ALIASES.md"

REQUIRED_SECTIONS = (
    "## Non-negotiable publication policy",
    "## Canonical paper identities",
    "## Portfolio dashboard",
    "## Active closure waves",
    "## Common scientific gates for every paper",
    "## Venue routing rules",
    "## Status-update discipline",
)

REQUIRED_STATUS_TOKENS = (
    "SCIENCE_RED",
    "SCIENCE_OPEN",
    "SCIENCE_VERIFIED_BOUNDED",
    "PACKAGE_OPEN",
    "READY_SPECIALIST",
    "TOP_TIER_PROMOTION_PENDING",
    "TOP_TIER_READY",
    "FILING_ONLY",
    "CANNOT_CHECK",
    "ROUTING_REQUIRED",
)

REQUIRED_WAVES = ("Wave A", "Wave B1", "Wave B2", "Wave C1/C2/C3")


def main() -> int:
    errors: list[str] = []

    if not README.is_file():
        errors.append("MISSING_PAPERS_README")
        body = ""
    else:
        body = README.read_text(encoding="utf-8")

    if not ALIASES.is_file():
        errors.append("MISSING_PAPER_ALIASES_AUTHORITY")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"MISSING_DASHBOARD_SECTION:{section}")

    for token in REQUIRED_STATUS_TOKENS:
        if token not in body:
            errors.append(f"MISSING_STATUS_TOKEN:{token}")

    for wave in REQUIRED_WAVES:
        if wave not in body:
            errors.append(f"MISSING_WAVE:{wave}")

    if "exactly five numbered flagship papers" in body.lower():
        errors.append("STALE_FIVE_FLAGSHIP_IDENTITY_RULE")

    row_ids = re.findall(r"^\| \*\*(ORION-\d{2}) —", body, flags=re.MULTILINE)
    expected = {f"ORION-{idx:02d}" for idx in range(1, 26)}
    observed = set(row_ids)
    if observed != expected:
        errors.append(
            "CANONICAL_PORTFOLIO_ROW_SET_MISMATCH:"
            f"missing={sorted(expected - observed)}:extra={sorted(observed - expected)}"
        )
    duplicates = sorted({paper_id for paper_id in row_ids if row_ids.count(paper_id) != 1})
    if duplicates:
        errors.append(f"DUPLICATE_CANONICAL_PORTFOLIO_ROWS:{duplicates}")

    canonical_dirs = sorted(
        path.name for path in (ROOT / "papers").glob("orion-[0-9][0-9]-*") if path.is_dir()
    )
    for idx in range(1, 26):
        prefix = f"orion-{idx:02d}-"
        matches = [name for name in canonical_dirs if name.startswith(prefix)]
        if len(matches) != 1:
            errors.append(f"CANONICAL_DIRECTORY_COUNT:{idx:02d}:{matches}")

    if "README edit cannot promote a claim" not in body:
        errors.append("MISSING_NON_AUTHORITY_BOUNDARY")
    if "Science first" not in body:
        errors.append("MISSING_SCIENCE_FIRST_RULE")

    if errors:
        print("PUBLICATION_DASHBOARD_CHECK=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PUBLICATION_DASHBOARD_CHECK=PASS")
    print("CANONICAL_PAPERS=25")
    print("README_AUTHORITY=ROUTING_AND_STATUS_INDEX_ONLY")
    print("SCIENTIFIC_AUTHORITY=NOT_GRANTED_BY_THIS_CHECK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
