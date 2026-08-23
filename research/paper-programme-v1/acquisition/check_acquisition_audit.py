#!/usr/bin/env python3
"""Keep the acquisition audit honest against the ledger it audits.

Three ways this file could quietly go wrong, all checked here:

* it stops covering every blocked item, so a blocker silently drops out;
* it restates an item's ledger category wrongly, so the reclassification is
  measured against the wrong baseline;
* its summary counts drift from its own items, so the headline overstates.

Offline by design. Route reachability is a separate concern with its own
network probe, because a checker that needs the internet cannot run in the
place where it matters most.

Exit codes: 0 consistent, 2 inconsistent, 3 CANNOT_CHECK.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

AUDITED_CATEGORIES = ("EXTERNAL_EVIDENCE_BLOCKER", "PROSPECTIVE_SUCCESSOR_REQUIRED")
SUMMARY_FIELDS = {
    "LOCALLY_UNEXECUTED": "locally_unexecuted",
    "LOCALLY_BROKEN": "locally_broken",
    "PROCURABLE_FREE": "procurable_free",
    "PARTIALLY_PROCURABLE": "partially_procurable",
    "EXTERNALLY_BLOCKED": "externally_blocked_with_no_free_route",
}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_acquisition_audit.py LEDGER.json AUDIT.json")
        return 3
    try:
        ledger = json.loads(Path(sys.argv[1]).read_text())
        audit = json.loads(Path(sys.argv[2]).read_text())
    except Exception as exc:
        print(f"CANNOT_CHECK: {exc}")
        return 3

    expected = {
        item["item_id"]: item["category"]
        for paper in ledger["papers"]
        for item in paper["items"]
        if item["category"] in AUDITED_CATEGORIES
    }
    actual = {item["item_id"]: item["ledger_category"] for item in audit["items"]}

    problems = []
    for missing in sorted(set(expected) - set(actual)):
        problems.append(f"UNCOVERED_BLOCKER {missing} ({expected[missing]})")
    for extra in sorted(set(actual) - set(expected)):
        problems.append(f"AUDITS_A_NONEXISTENT_ITEM {extra}")
    for item_id in sorted(set(expected) & set(actual)):
        if expected[item_id] != actual[item_id]:
            problems.append(
                f"CATEGORY_MISSTATED {item_id}: audit says {actual[item_id]}, ledger says {expected[item_id]}"
            )

    counts = Counter(item["reclassified_as"] for item in audit["items"])
    summary = audit["summary"]
    if summary.get("items_audited") != len(audit["items"]):
        problems.append("SUMMARY_COUNT_WRONG items_audited")
    for label, field in SUMMARY_FIELDS.items():
        if summary.get(field, 0) != counts.get(label, 0):
            problems.append(f"SUMMARY_COUNT_WRONG {field}: says {summary.get(field)}, items give {counts.get(label, 0)}")

    # A residual of class F is the one thing that cannot be procured, so the
    # count of items carrying one is load-bearing and must not drift either.
    f_residual = sum(1 for item in audit["items"] if "F" in (item.get("residual_requirement") or "")[:2])
    if summary.get("items_with_a_class_F_residual") != f_residual:
        problems.append(
            f"SUMMARY_COUNT_WRONG items_with_a_class_F_residual: says "
            f"{summary.get('items_with_a_class_F_residual')}, items give {f_residual}"
        )

    for problem in problems:
        print(problem)
    print(
        f"\nblocked_items_in_ledger={len(expected)} audited={len(actual)} "
        f"problems={len(problems)}"
    )
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
