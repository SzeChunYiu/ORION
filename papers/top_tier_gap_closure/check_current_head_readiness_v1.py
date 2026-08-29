#!/usr/bin/env python3
"""Fail-closed structural checker for the additive all-25 current-head readiness pack."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_IDS = [f"ORION-{i:02d}" for i in range(1, 26)]
ASSESSED_HEAD = "645ed920b65877af05f9cd9321b4de5af6171bb4"
GREEN = "ORION_ALL25_CURRENT_HEAD_READINESS_V1_GREEN"
RED = "ORION_ALL25_CURRENT_HEAD_READINESS_V1_RED"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8", errors="strict")


def main() -> int:
    try:
        readiness = read("ALL25_CURRENT_HEAD_READINESS_2026-08-29.md")
        patchset = read("ALL25_MANUSCRIPT_UPGRADE_PATCHSET_2026-08-29.md")
        matrix = read("ALL25_DETAILED_EXECUTION_MATRIX_V2.md")

        require("**Scientific-authority delta:** `NONE`" in readiness, "readiness authority guard missing")
        require("**Authority delta:** `NONE`" in patchset, "patchset authority guard missing")
        require("**Authority delta:** `NONE`" in matrix, "matrix authority guard missing")

        for text, label in ((readiness, "readiness"), (patchset, "patchset"), (matrix, "matrix")):
            require(ASSESSED_HEAD in text, f"{label} assessed-head anchor missing")
            require("TOP_TIER_SUCCESSOR_EARNED" not in text, f"{label} contains unauthorized earned-promotion token")

        readiness_ids = re.findall(r"^\| \*\*(ORION-\d{2})\*\* \|", readiness, flags=re.MULTILINE)
        matrix_ids = re.findall(r"^\| \*\*(ORION-\d{2})\*\* \|", matrix, flags=re.MULTILINE)
        patch_ids = re.findall(r"^## (ORION-\d{2})\b", patchset, flags=re.MULTILINE)

        require(readiness_ids == EXPECTED_IDS, f"readiness coverage/order mismatch: {readiness_ids}")
        require(matrix_ids == EXPECTED_IDS, f"matrix coverage/order mismatch: {matrix_ids}")
        require(patch_ids == EXPECTED_IDS, f"patchset coverage/order mismatch: {patch_ids}")

        require(readiness.count("`B0_PACKAGE_ONLY`") >= 1, "readiness lacks package-only class")
        require(readiness.count("`T3_PROMOTION_ROUTE_STOPPED`") >= 1, "readiness lacks adverse promotion class")
        require("same-programme agents cannot" in (readiness + matrix + patchset).lower(), "external-authority boundary missing")
        require("CANNOT_CHECK" in readiness and "CANNOT_CHECK" in patchset and "CANNOT_CHECK" in matrix, "CANNOT_CHECK boundary missing")

        print(f"{GREEN} papers=25 head={ASSESSED_HEAD} promotions=0")
        return 0
    except Exception as exc:
        print(f"{RED}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
