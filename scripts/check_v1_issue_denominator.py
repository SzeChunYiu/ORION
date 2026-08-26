#!/usr/bin/env python3
"""Bind the V1 issue-ledger denominator to the acquired open-issue census.

check_orion_v1_freeze.py verifies the ledger's internal arithmetic, but its
coverage.complete flag and all_open_issue_count are ledger-declared. A ledger
could therefore claim a complete census that was never acquired.

This checker removes that seam: when the ledger declares completeness, the
declaration must equal a census artifact that itself passed its own negative
controls. It grants no scientific authority and never repairs anything.

Exit 0 pass, 1 fail, 2 CANNOT_CHECK (distinct: could not check is never
reported as checked and fine).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LEDGER = Path("research/orion-v1-freeze/V1_ISSUE_DISPOSITION_LEDGER_V1.json")


def fail(msg: str) -> int:
    print(f"V1_ISSUE_DENOMINATOR: FAIL — {msg}")
    return 1


def cannot(msg: str) -> int:
    print(f"V1_ISSUE_DENOMINATOR: CANNOT_CHECK — {msg}")
    return 2


def main() -> int:
    root = Path.cwd()
    try:
        led = json.loads((root / LEDGER).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return cannot(f"ledger absent: {LEDGER}")
    cov = led.get("coverage") or {}
    if not isinstance(cov, dict):
        return fail("coverage block missing or not an object")

    rel = cov.get("census_acquisition")
    if not rel:
        if cov.get("complete") is True:
            return fail("coverage.complete is true but no census_acquisition is bound")
        return cannot("no census bound and completeness not claimed")

    path = root / rel
    try:
        cen = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return fail(f"bound census artifact missing: {rel}")

    controls_path = path.parent / "NEGATIVE_CONTROLS.json"
    try:
        ctl = json.loads(controls_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return cannot(f"census negative controls absent: {controls_path}")

    if ctl.get("duplicate_issue_numbers") != 0:
        return fail(f"census reports {ctl.get('duplicate_issue_numbers')} duplicate issue numbers")
    if ctl.get("non_open_rows") != 0:
        return fail(f"census reports {ctl.get('non_open_rows')} non-open rows")
    if ctl.get("search_denominator_drift") is not False:
        return fail("census reports search denominator drift")

    census_numbers = {i["number"] for i in cen["issues"]}
    ledger_numbers = {r["number"] for r in led["entries"]}
    if len(census_numbers) != cen.get("count"):
        return fail(f"census self-inconsistent: {len(census_numbers)} rows vs count {cen.get('count')}")

    if cov.get("complete") is True:
        missing = sorted(census_numbers - ledger_numbers)
        extra = sorted(ledger_numbers - census_numbers)
        if missing or extra:
            return fail(f"completeness claimed but ledger != census; missing={missing[:10]} extra={extra[:10]}")
        if cov.get("all_open_issue_count") != cen["count"]:
            return fail(
                f"all_open_issue_count {cov.get('all_open_issue_count')} != census count {cen['count']}"
            )
        pending = sum(r["disposition"] == "PENDING_ATOMIC_AUDIT" for r in led["entries"])
        if pending:
            return fail(f"completeness claimed with {pending} rows still PENDING_ATOMIC_AUDIT")

    print(
        "V1_ISSUE_DENOMINATOR: PASS — "
        f"census={cen['count']} ledger={len(ledger_numbers)} complete={cov.get('complete')} "
        f"controls_clean=True"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
