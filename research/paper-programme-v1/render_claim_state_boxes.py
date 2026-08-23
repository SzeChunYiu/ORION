#!/usr/bin/env python3
"""Render the per-paper claim-state box from the resolution ledger.

Reviewer 3: a reader cannot tell CANNOT_CHECK, a failed hypothesis, a negative
theorem and an unexecuted protocol apart, and mistaking any of them for the
others misreads the paper. The remedy is one compact box on every abstract and
first results page, saying what is claimed now, what was found and kept, and
what is not claimed at all.

The box is generated from the ledger rather than written by hand, so a paper's
front matter cannot drift away from the authority that governs it. Regenerate
after every ledger change; the output is committed so a diff shows the drift.

Usage:  render_claim_state_boxes.py LEDGER.json [--check EXISTING.md]
Exit codes: 0 written or identical, 2 committed output is stale, 3 cannot check.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# The four states a reader must be able to tell apart, and what each licenses.
LANES = {
    "ACTIVE_POSITIVE_AUTHORITY": (
        "Active claim",
        "carries authority now, within the scope stated on the item",
    ),
    "HISTORICAL_ADVERSE_RESULT": (
        "Historical result, retained",
        "found, kept, and never relabelled; it is evidence, not an open task",
    ),
    "PROSPECTIVE_SUCCESSOR_REQUIRED": (
        "Not claimed - frozen, not yet executed",
        "a registered protocol with no result; absent work, not a negative one",
    ),
    "EXTERNAL_EVIDENCE_BLOCKER": (
        "Not claimed - externally blocked",
        "cannot be decided in this repository at any effort; needs external custody",
    ),
    "FIXED_BY_EXISTING_PR": (
        "Repair in flight",
        "a defect with a named PR, not a scientific state",
    ),
}
ORDER = list(LANES)


def render(ledger: dict) -> str:
    lines = [
        "# Claim-state boxes, one per paper",
        "",
        f"Generated from `{ledger['schema_version']}` dated {ledger['ledger_date']}.",
        "Do not edit by hand -- run `render_claim_state_boxes.py`.",
        "",
        "## How to read a box",
        "",
        "| Lane | What it licenses |",
        "|---|---|",
    ]
    for category in ORDER:
        title, meaning = LANES[category]
        lines.append(f"| **{title}** | {meaning} |")
    lines += [
        "",
        "The two *Not claimed* lanes are the ones most often conflated. A frozen protocol with no",
        "result is not a negative result, and an externally blocked question is not a failed one.",
        "Neither is evidence against the paper; neither is evidence for it.",
        "",
    ]

    for paper in ledger["papers"]:
        lines += [f"## {paper['paper_id']}", ""]
        by_lane: dict[str, list[dict]] = {}
        for item in paper["items"]:
            by_lane.setdefault(item["category"], []).append(item)
        for category in ORDER:
            items = by_lane.get(category)
            if not items:
                continue
            lines.append(f"**{LANES[category][0]}**")
            lines.append("")
            for item in items:
                claim = item.get("claim_id", item["item_id"])
                scope = item.get("scope")
                lines.append(f"- `{claim}`")
                if scope:
                    lines.append(f"  - scope: {scope}")
            lines.append("")
        absent = [c for c in ORDER if c not in by_lane]
        if absent:
            readable = ", ".join(LANES[c][0] for c in absent)
            lines.append(f"*No items in: {readable}.*")
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: render_claim_state_boxes.py LEDGER.json [--check EXISTING.md]")
        return 3
    ledger = json.loads(Path(sys.argv[1]).read_text())
    rendered = render(ledger)
    if "--check" in sys.argv:
        existing = Path(sys.argv[sys.argv.index("--check") + 1])
        if not existing.exists():
            print(f"CANNOT_CHECK: {existing} does not exist")
            return 3
        if existing.read_text() != rendered:
            print(f"STALE: {existing} does not match the ledger; regenerate it")
            return 2
        print("boxes match the ledger")
        return 0
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
