#!/usr/bin/env python3
"""Fail-closed structural check for the all-paper donor-subtraction registry."""

from __future__ import annotations

import re
import sys
from pathlib import Path

GREEN = "ORION_DONOR_SUBTRACTION_PLAN_V1_GREEN"
RED = "ORION_DONOR_SUBTRACTION_PLAN_V1_RED"
ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "PRIMARY_SOURCE_DONOR_SUBTRACTION_PLAN_V1.md"
EXPECTED_IDS = [f"ORION-{i:02d}" for i in range(1, 26)]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    try:
        text = PLAN.read_text(encoding="utf-8")
        rows = re.findall(r"^\| (ORION-\d{2}) \|", text, flags=re.MULTILINE)
        require(rows == EXPECTED_IDS, f"paper coverage/order mismatch: {rows}")
        require(len(set(rows)) == 25, "duplicate paper row")
        require(
            "editorial research registry, not a completed literature review" in text,
            "incomplete-literature-review boundary missing",
        )
        require("Authority delta:** `NONE`" in text, "authority-delta guard missing")
        require(
            "Absence of a discovered donor is not proof of novelty." in text,
            "novelty non-inference guard missing",
        )
        require(
            "venue decision is deferred" in text,
            "independent primary-source adjudication gate missing",
        )
        print(f"{GREEN} papers=25 completed_literature_reviews=0 promotions=0")
        return 0
    except Exception as exc:
        print(f"{RED}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
