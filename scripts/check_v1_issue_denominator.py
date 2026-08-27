#!/usr/bin/env python3
"""Bind the V1 issue-ledger denominator to the acquired open-issue censuses.

check_orion_v1_freeze.py verifies the ledger's internal arithmetic, but its
coverage.complete flag and all_open_issue_count are ledger-declared. A ledger
could therefore claim a complete census that was never acquired.

This checker removes that seam. Two acquisitions are bound:

* ``census_acquisition`` — the freeze-time open-issue census (immutable
  provenance of the original 159 dispositions);
* ``current_open_census`` — a dated re-acquisition of the CURRENT open-issue
  set, so issues opened after the freeze cannot silently fall outside the
  denominator, and rows may only exist for issues that are currently open or
  were open at freeze time.

When the ledger declares completeness, the ledger's issue set must equal the
union of both acquisitions exactly, and every bound census must carry its own
clean negative controls. It grants no scientific authority and never repairs
anything.

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


def load_census(root: Path, rel: str) -> tuple[dict | None, int]:
    """Return (census, exit_code); a None census carries the already-printed reason."""
    path = root / rel
    try:
        cen = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, fail(f"bound census artifact missing: {rel}")
    controls_path = path.parent / "NEGATIVE_CONTROLS.json"
    try:
        ctl = json.loads(controls_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, cannot(f"census negative controls absent: {controls_path}")
    if ctl.get("duplicate_issue_numbers") != 0:
        return None, fail(f"census {rel} reports {ctl.get('duplicate_issue_numbers')} duplicate issue numbers")
    if ctl.get("non_open_rows") != 0:
        return None, fail(f"census {rel} reports {ctl.get('non_open_rows')} non-open rows")
    if ctl.get("search_denominator_drift") is not False:
        return None, fail(f"census {rel} reports search denominator drift")
    numbers = {i["number"] for i in cen["issues"]}
    if len(numbers) != cen.get("count"):
        return None, fail(f"census {rel} self-inconsistent: {len(numbers)} rows vs count {cen.get('count')}")
    return cen, 0


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

    freeze, code = load_census(root, rel)
    if freeze is None:
        return code
    bound = {i["number"] for i in freeze["issues"]}
    current_count = None

    cur_rel = cov.get("current_open_census")
    if not cur_rel and cov.get("complete") is True:
        return fail("coverage.complete is true but no current_open_census is bound")
    if cur_rel:
        current, code = load_census(root, cur_rel)
        if current is None:
            return code
        current_numbers = {i["number"] for i in current["issues"]}
        # Overlap with the freeze census is the expected case: issues open at
        # freeze time that remain open. The union, not either count alone, is
        # the denominator every disposition must be drawn from.
        freeze_ts, current_ts = freeze.get("acquired_at_utc"), current.get("acquired_at_utc")
        if isinstance(freeze_ts, str) and isinstance(current_ts, str) and current_ts < freeze_ts:
            return fail(f"current census {cur_rel} predates the freeze acquisition {rel}")
        bound |= current_numbers
        current_count = len(current_numbers)

    ledger_numbers = {r["number"] for r in led["entries"]}

    if cov.get("complete") is True:
        missing = sorted(bound - ledger_numbers)
        extra = sorted(ledger_numbers - bound)
        if missing or extra:
            return fail(f"completeness claimed but ledger != bound censuses; missing={missing[:10]} extra={extra[:10]}")
        if cov.get("all_open_issue_count") != len(bound):
            return fail(
                f"all_open_issue_count {cov.get('all_open_issue_count')} != bound census count {len(bound)}"
            )
        pending = sum(r["disposition"] == "PENDING_ATOMIC_AUDIT" for r in led["entries"])
        if pending:
            return fail(f"completeness claimed with {pending} rows still PENDING_ATOMIC_AUDIT")

    print(
        "V1_ISSUE_DENOMINATOR: PASS — "
        f"freeze={freeze['count']} current={current_count} bound={len(bound)} "
        f"ledger={len(ledger_numbers)} complete={cov.get('complete')} "
        f"controls_clean=True"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
