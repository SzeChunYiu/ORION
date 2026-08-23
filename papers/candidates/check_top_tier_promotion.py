#!/usr/bin/env python3
"""Dependency-free CLI wrapper for the P6-P15 promotion contract audit."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys


def _load_audit(root: Path):
    module = runpy.run_path(
        str(root / "src" / "orion" / "programme" / "top_tier_promotion.py")
    )
    return module["audit_top_tier_promotion"]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    audit_top_tier_promotion = _load_audit(root)
    findings = audit_top_tier_promotion(root)
    if not findings:
        print("P6_P15_TOP_TIER_PROMOTION_CONTRACT_GREEN")
        return 0

    for finding in findings:
        print(f"{finding.code}: {finding.path}: {finding.detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
