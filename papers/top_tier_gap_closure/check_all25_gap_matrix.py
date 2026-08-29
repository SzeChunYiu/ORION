#!/usr/bin/env python3
"""Validate the compact ORION-01..25 top-tier science-gap plan."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "ALL25_TOP_TIER_SCIENCE_GAP_INDEX_V1.json"
SUMMARY = ROOT / "ALL25_TOP_TIER_SCIENCE_GAP_SUMMARY_V1.md"
REQUIRED = {
    "id",
    "slug",
    "working_title",
    "execution_priority",
    "current_programme_authorization",
    "current_defensible_ceiling",
    "primary_top_tier_gap",
    "decisive_increment_beyond_current_paper",
    "unit_of_inference",
    "primary_endpoint",
    "predeclared_success_gate",
    "decisive_falsifier",
    "stop_rule",
    "immediate_repository_actions",
    "forbidden_claim_upgrades",
    "external_human_or_institutional_authority_required",
    "top_tier_promotion_earned",
    "scientific_authority_delta",
}
EXPECTED_IDS = [f"ORION-{i:02d}" for i in range(1, 26)]
EXPECTED_P0 = {"ORION-02", "ORION-16", "ORION-17", "ORION-22", "ORION-23", "ORION-25"}
EXPECTED_SHARED = {"ORION-02", "ORION-08", "ORION-09", "ORION-10", "ORION-13", "ORION-19", "ORION-22"}


def main() -> int:
    errors: list[str] = []
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    base = index.get("assessed_main_commit")
    if index.get("authority", {}).get("top_tier_promotions_earned_by_this_artifact") != 0:
        errors.append("portfolio promotions must be zero")
    if index.get("authority", {}).get("scientific_authority_delta") != "NONE":
        errors.append("portfolio scientific authority delta must be NONE")

    papers: list[dict[str, object]] = []
    for rel in index.get("matrix_chunks", []):
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"missing chunk: {rel}")
            continue
        chunk = json.loads(path.read_text(encoding="utf-8"))
        if chunk.get("assessed_main_commit") != base:
            errors.append(f"{rel}: base mismatch")
        if chunk.get("scientific_authority_delta") != "NONE":
            errors.append(f"{rel}: authority delta")
        papers.extend(chunk.get("papers", []))

    ids = [paper.get("id") for paper in papers]
    if ids != EXPECTED_IDS:
        errors.append(f"ids/order mismatch: {ids!r}")

    for paper in papers:
        pid = str(paper.get("id"))
        missing = REQUIRED - set(paper)
        if missing:
            errors.append(f"{pid}: missing {sorted(missing)}")
        if paper.get("top_tier_promotion_earned") is not False:
            errors.append(f"{pid}: promotion must be false")
        if paper.get("scientific_authority_delta") != "NONE":
            errors.append(f"{pid}: authority delta")
        for field in ("immediate_repository_actions", "forbidden_claim_upgrades"):
            value = paper.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{pid}: {field} empty")
        for field in (
            "current_programme_authorization",
            "current_defensible_ceiling",
            "primary_top_tier_gap",
            "decisive_increment_beyond_current_paper",
            "unit_of_inference",
            "primary_endpoint",
            "predeclared_success_gate",
            "decisive_falsifier",
            "stop_rule",
        ):
            if not str(paper.get(field, "")).strip():
                errors.append(f"{pid}: {field} empty")

    p0 = {str(p["id"]) for p in papers if p.get("execution_priority") == "P0_BREAKTHROUGH"}
    if p0 != EXPECTED_P0:
        errors.append(f"P0 set mismatch: {sorted(p0)}")

    shared = set(index.get("shared_theorem_spine", {}).get("papers", []))
    if shared != EXPECTED_SHARED:
        errors.append(f"shared-theorem set mismatch: {sorted(shared)}")

    summary = SUMMARY.read_text(encoding="utf-8")
    for pid in EXPECTED_IDS:
        if summary.count(f"| {pid} |") != 1:
            errors.append(f"summary row missing/duplicate: {pid}")

    if errors:
        print("ALL25_TOP_TIER_SCIENCE_GAP_MATRIX_V1_RED")
        for error in errors:
            print("-", error)
        return 1

    print(f"ALL25_TOP_TIER_SCIENCE_GAP_MATRIX_V1_GREEN papers={len(papers)} promotions=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
