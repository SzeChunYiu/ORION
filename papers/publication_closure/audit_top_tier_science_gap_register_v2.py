#!/usr/bin/env python3
"""Fail-closed structural audit for the ORION-01–25 science-gap register V2.

The audit checks coverage, status arithmetic, and authority boundaries. It does
not verify any paper's theorem or experiment and grants no scientific authority.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

REGISTER = Path("papers/publication_closure/TOP_TIER_SCIENCE_GAP_REGISTER_V2.md")
EXPECTED_MAIN = "87e2bcb330d243b7062ddba1ca26e426632edeab"
EXPECTED_IDS = tuple(f"ORION-{number:02d}" for number in range(1, 26))
BOUNDED = {
    "READY_TO_FILE",
    "RETAINED_NEEDS_LOCAL_CLOSURE",
    "EXTERNAL_AUTHORITY_BLOCKED",
    "TEMPORAL_FROZEN",
}
SUCCESSORS = {
    "UNRUN_OPTIONAL",
    "NOT_SUPPORTED_BOUNDED_RETAINED",
    "NEW_QUESTION_REQUIRED_NO_RESCUE",
    "EXTERNAL_AUTHORITY_REQUIRED",
    "CHECKER_DISAGREEMENT",
    "TEMPORAL_OUTCOMES_UNOPENED",
    "REAL_SYSTEM_LANE_ACTIVE_DO_NOT_DUPLICATE",
    "PROSPECTIVE_RESULT_UNBOUND_TOP_TIER_NOT_EARNED",
    "NOT_INDICATED_BY_ORBIT_COVERAGE",
}
EXPECTED_BOUNDED = {
    "READY_TO_FILE": 10,
    "RETAINED_NEEDS_LOCAL_CLOSURE": 10,
    "EXTERNAL_AUTHORITY_BLOCKED": 4,
    "TEMPORAL_FROZEN": 1,
}
EXTERNAL_IDS = {"ORION-04", "ORION-15", "ORION-18", "ORION-24"}
ROW = re.compile(r"^\| (ORION-\d{2}) \| `([^`]+)` \| `([^`]+)` \| (.+) \| (.+) \|$")
ASSESSMENT = re.compile(r"^\*\*Assessment cut:\*\* `main@([0-9a-f]+)`", re.MULTILINE)
REQUIRED_PHRASES = (
    "supersedes `papers/PUBLICATION_DISPOSITION_MATRIX_V1.md` only for current-state reporting",
    "**Terminal:** `SCIENCE_GAPS_CLASSIFIED__NO_UNEARNED_PROMOTION`",
    "**Scientific authority delta:** `NONE`",
    "Same-programme or same-researcher checking is not external-investigator replication.",
    "Missing historical data must be reported as missing; it must never be synthesized",
    "Passing this audit means the gap map is internally consistent.",
)


def audit_text(text: str) -> dict[str, Any]:
    errors: list[str] = []
    match = ASSESSMENT.search(text)
    assessed_main = match.group(1) if match else None
    if assessed_main != EXPECTED_MAIN:
        errors.append(f"assessment cut drifted: {assessed_main!r}")

    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"required preservation phrase missing: {phrase}")

    rows: list[tuple[str, str, str, str, str]] = []
    for line in text.splitlines():
        row = ROW.fullmatch(line)
        if row:
            rows.append(row.groups())

    ids = tuple(row[0] for row in rows)
    if ids != EXPECTED_IDS:
        errors.append("table must contain ORION-01 through ORION-25 exactly once and in order")

    bounded_counts = Counter()
    for paper_id, bounded, successor, gap, action in rows:
        bounded_counts[bounded] += 1
        if bounded not in BOUNDED:
            errors.append(f"{paper_id}: unknown bounded status {bounded}")
        if successor not in SUCCESSORS:
            errors.append(f"{paper_id}: unknown successor status {successor}")
        if not gap.strip():
            errors.append(f"{paper_id}: empty decisive gap")
        if "Stop: `" not in action:
            errors.append(f"{paper_id}: missing explicit stop terminal")
        row_text = line_for(paper_id, bounded, successor, gap, action)
        if "TOP_TIER_PROMOTION_EARNED" in row_text:
            errors.append(f"{paper_id}: row grants or names unearned top-tier authority")
        if "READY_TO_SUBMIT_TOP_TIER" in row_text:
            errors.append(f"{paper_id}: row grants or names unearned submission authority")
        if paper_id in EXTERNAL_IDS:
            if bounded != "EXTERNAL_AUTHORITY_BLOCKED":
                errors.append(f"{paper_id}: external bounded blocker was softened")
            if successor != "EXTERNAL_AUTHORITY_REQUIRED":
                errors.append(f"{paper_id}: external successor blocker was softened")
        if paper_id == "ORION-07":
            if bounded != "TEMPORAL_FROZEN" or successor != "TEMPORAL_OUTCOMES_UNOPENED":
                errors.append("ORION-07 temporal freeze was softened")

    if dict(bounded_counts) != EXPECTED_BOUNDED:
        errors.append(
            f"bounded-status arithmetic drifted: expected {EXPECTED_BOUNDED}, "
            f"got {dict(bounded_counts)}"
        )
    if "- `TOP_TIER_PROMOTION_EARNED`: 0" not in text:
        errors.append("zero top-tier-promotion count is missing")
    if "No row licenses `READY_TO_SUBMIT_TOP_TIER`" not in text:
        errors.append("portfolio forbidden-upgrade boundary is missing")

    return {
        "schema_version": "orion.top-tier-science-gap-register-audit.v2",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "assessed_main": assessed_main,
        "paper_count": len(rows),
        "bounded_status_counts": dict(bounded_counts),
        "scientific_authority_delta": "NONE",
    }


def line_for(paper_id: str, bounded: str, successor: str, gap: str, action: str) -> str:
    return f"| {paper_id} | `{bounded}` | `{successor}` | {gap} | {action} |"


def audit_path(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "schema_version": "orion.top-tier-science-gap-register-audit.v2",
            "status": "FAIL",
            "errors": [f"cannot read register: {exc}"],
            "paper_count": 0,
            "scientific_authority_delta": "NONE",
        }
    return audit_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--register", type=Path)
    args = parser.parse_args()
    path = args.register or args.root.resolve() / REGISTER
    report = audit_path(path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
