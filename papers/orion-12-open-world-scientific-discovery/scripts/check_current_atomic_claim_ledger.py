#!/usr/bin/env python3
"""Validate the Wave-1 atomic-claim release ledger and its summary.

This checker is intentionally structural.  Entailment was adjudicated in the
independent coverage and editorial records; this command makes sure that the
released CSV has not lost rows, warrants, decisions, or allowed release states.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
EDITORIAL = PAPER / "editorial"
SUMMARY = EDITORIAL / "ATOMIC_CLAIM_LEDGER_SUMMARY_2026-08-28.json"
REQUIRED_COLUMNS = {
    "atomic_id",
    "location",
    "exact_atomic_proposition",
    "warrant_pointer",
    "evidence_resolution_status",
    "support_or_entailment_status",
    "independent_check",
    "status",
    "release_action",
}


def fail(message: str) -> None:
    raise ValueError(message)


def check_pathlike_warrants(rows: list[dict[str, str]]) -> None:
    for row in rows:
        for raw in row["warrant_pointer"].split(";"):
            pointer = raw.strip()
            if not pointer or ("/" not in pointer and not pointer.endswith(
                (".bib", ".csv", ".json", ".md", ".py", ".tex")
            )):
                continue
            candidates = (PAPER / pointer, REPO / pointer)
            if not any(path.exists() for path in candidates):
                fail(f"{row['atomic_id']}: missing warrant path {pointer!r}")


def main() -> int:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    ledger = EDITORIAL / summary["ledger"]
    with ledger.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        if not REQUIRED_COLUMNS <= columns:
            fail(f"ledger missing columns: {sorted(REQUIRED_COLUMNS - columns)}")
        rows = list(reader)

    ids = [row["atomic_id"].strip() for row in rows]
    if not ids or any(not item for item in ids) or len(ids) != len(set(ids)):
        fail("atomic IDs must be nonempty and unique")
    if len(rows) != summary["row_count"]:
        fail(f"row-count drift: {len(rows)} != {summary['row_count']}")

    for field in (
        "location",
        "exact_atomic_proposition",
        "warrant_pointer",
        "independent_check",
        "release_action",
    ):
        missing = [row["atomic_id"] for row in rows if not row[field].strip()]
        if missing:
            fail(f"empty {field}: {', '.join(missing)}")

    unresolved = [
        row["atomic_id"]
        for row in rows
        if row["evidence_resolution_status"] != "RESOLVED"
        or row["support_or_entailment_status"] != "ENTAILED"
    ]
    if unresolved:
        fail("unresolved or non-entailed rows: " + ", ".join(unresolved))

    allowed = set(summary["allowed_release_statuses"])
    forbidden = [row["atomic_id"] for row in rows if row["status"] not in allowed]
    if forbidden:
        fail("forbidden release states: " + ", ".join(forbidden))
    counts = dict(Counter(row["status"] for row in rows))
    if counts != summary["status_counts"]:
        fail(f"status-count drift: {counts} != {summary['status_counts']}")
    if summary["forbidden_status_count"] != 0:
        fail("summary records a nonzero forbidden-status count")

    check_pathlike_warrants(rows)
    print(
        "current atomic claim ledger clean: "
        f"{len(rows)} rows; {counts}; zero forbidden release states"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
