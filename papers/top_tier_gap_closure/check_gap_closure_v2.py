#!/usr/bin/env python3
"""Structural fail-closed validator for the ORION-01–25 gap-closure package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GREEN = "ORION_ALL25_TOP_TIER_GAP_CLOSURE_V2_GREEN"
RED = "ORION_ALL25_TOP_TIER_GAP_CLOSURE_V2_RED"
ROOT = Path(__file__).resolve().parent
EXPECTED_IDS = [f"ORION-{i:02d}" for i in range(1, 26)]
EXPECTED_P0 = {"ORION-02", "ORION-16", "ORION-17", "ORION-22", "ORION-23", "ORION-25"}
EXPECTED_SHARED_THEOREM = {"ORION-02", "ORION-08", "ORION-09", "ORION-10", "ORION-13", "ORION-19", "ORION-22"}
EXPECTED_MATRIX_FILES = [
    "ORION-01-05.md",
    "ORION-06-10.md",
    "ORION-11-15.md",
    "ORION-16-20.md",
    "ORION-21-25.md",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    try:
        index = load_json("ALL25_TOP_TIER_SCIENCE_GAP_INDEX_V2.json")
        require(index["schema"] == "ORION.All25TopTierScienceGapIndex.v2", "index schema mismatch")
        require(index["scope"] == "ORION-01 through ORION-25", "scope mismatch")
        require(index["scientific_authority_delta"] == "NONE", "authority delta must be NONE")
        require(index["top_tier_promotions_earned"] == 0, "portfolio promotion count must be zero")

        papers = index["papers"]
        ids = [row["id"] for row in papers]
        require(ids == EXPECTED_IDS, f"paper IDs/order mismatch: {ids}")
        require(len(set(ids)) == 25, "duplicate paper IDs")
        require(all(row["top_tier_promotion_earned"] is False for row in papers), "paper promotion leaked")

        p0 = {row["id"] for row in papers if row["execution_priority"] == "P0_BREAKTHROUGH"}
        require(p0 == EXPECTED_P0, f"P0 set mismatch: {sorted(p0)}")
        shared = set(index["shared_theorem_spine"]["papers"])
        require(shared == EXPECTED_SHARED_THEOREM, f"shared-theorem set mismatch: {sorted(shared)}")

        summary = (ROOT / "ALL25_TOP_TIER_SCIENCE_GAP_SUMMARY_V2.md").read_text(encoding="utf-8")
        for paper_id in EXPECTED_IDS:
            require(summary.count(f"| {paper_id} |") == 1, f"summary row missing/duplicated: {paper_id}")
        require("Promotions earned here:** `0`" in summary, "summary zero-promotion guard missing")

        matrix_ids: list[str] = []
        for filename in EXPECTED_MATRIX_FILES:
            text = (ROOT / "matrix" / filename).read_text(encoding="utf-8")
            matrix_ids.extend(re.findall(r"^## (ORION-\d{2})\b", text, flags=re.MULTILINE))
            require("Authority delta:** `NONE`" in text, f"matrix authority guard missing: {filename}")
        require(matrix_ids == EXPECTED_IDS, f"matrix coverage/order mismatch: {matrix_ids}")

        operational = load_json("operational_gap_audits_v1/RESULT.json")
        require(operational["terminal"] == "ORION_OPERATIONAL_GAP_AUDITS_V1_GREEN", "operational terminal mismatch")
        require(len(operational["audits"]) == 10, "operational audit count mismatch")
        require(operational["top_tier_promotions_earned"] == 0, "operational promotion leaked")
        require(all(a["top_tier_promotion_earned"] is False for a in operational["audits"]), "audit promotion leaked")

        finite = load_json("finite_information_interface_v1/RESULT.json")
        require(finite["terminal"] == "FINITE_INFORMATION_INTERFACE_V1_THEOREMS_REPRODUCED", "finite theorem terminal mismatch")
        require(finite["counters"]["mismatches"] == 0, "finite theorem mismatch counter nonzero")
        require(finite["scientific_authority_delta"] == "NONE", "finite theorem authority drift")

        required_files = [
            "README.md",
            "LATEST_MAIN_SCIENCE_AUDIT_2026-08-29.md",
            "RECENT_COMMIT_RECONCILIATION_V2.md",
            "TOP_TIER_EVIDENCE_CONTRACT_V2.md",
            "adaptive_promotion_budget_v1/THEORY_AUDIT.md",
            "adaptive_promotion_budget_v1/CLAIM_DISPOSITION.md",
            "finite_information_interface_v1/THEORY.md",
            "finite_information_interface_v1/PROTOCOL.json",
            "finite_information_interface_v1/EXPECTED_TERMINALS.md",
            "finite_information_interface_v1/CLAIM_DISPOSITION.md",
            "finite_information_interface_v1/check_theory.py",
            "operational_gap_audits_v1/README.md",
            "operational_gap_audits_v1/check_operational_gap_audits.py",
        ]
        for relative in required_files:
            require((ROOT / relative).is_file(), f"required file missing: {relative}")

        package_text = "\n".join(
            path.read_text(encoding="utf-8", errors="strict")
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix in {".md", ".json", ".py"}
        )
        require('"top_tier_promotion_earned": true' not in package_text, "literal promotion leaked")
        require("T3_INVARIANT_ADDS_NOTHING" in package_text, "ORION-09 adverse terminal lost")
        require("R4" in package_text and "retraction" in package_text.lower(), "ORION-11 retraction guard lost")

        print(f"{GREEN} papers=25 promotions=0 operational_audits=10")
        return 0
    except Exception as exc:
        print(f"{RED}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
