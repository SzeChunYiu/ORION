#!/usr/bin/env python3
"""CLI wrapper for the P6-P15 top-tier promotion contract audit."""

from __future__ import annotations

from pathlib import Path
import sys

from orion.programme.top_tier_promotion import audit_top_tier_promotion


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    findings = audit_top_tier_promotion(root)
    if not findings:
        print("P6_P15_TOP_TIER_PROMOTION_CONTRACT_GREEN")
        return 0

    for finding in findings:
        print(f"{finding.code}: {finding.path}: {finding.detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
