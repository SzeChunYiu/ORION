#!/usr/bin/env python3
"""Fail-closed validator for the canonical ORION-01..25 closure programme."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "papers/ALL_25_CLOSURE_MANIFEST_V1.json"
EXPECTED = {f"ORION-{i:02d}" for i in range(1, 26)}
ALLOWED_WAVES = {"A", "B1", "B2", "C"}
ALLOWED_TERMINALS = {"TOP_TIER_SUBMISSION_READY", "BOUNDED_SPECIALIST_SUBMISSION_READY"}


def main() -> int:
    errors: list[str] = []
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if doc.get("schema") != "ORION.All25PublicationClosureManifest.v1":
        errors.append("wrong schema")
    papers = doc.get("papers")
    waves = doc.get("waves")
    if not isinstance(papers, dict):
        errors.append("papers must be an object")
        papers = {}
    if not isinstance(waves, dict):
        errors.append("waves must be an object")
        waves = {}
    if set(papers) != EXPECTED:
        errors.append(f"paper set mismatch missing={sorted(EXPECTED-set(papers))} extra={sorted(set(papers)-EXPECTED)}")
    if set(waves) != ALLOWED_WAVES:
        errors.append(f"wave set mismatch: {sorted(waves)}")

    seen: list[str] = []
    for wave, item in waves.items():
        if not isinstance(item, dict):
            errors.append(f"wave {wave} must be an object")
            continue
        ids = item.get("papers")
        if not isinstance(ids, list):
            errors.append(f"wave {wave} papers must be an array")
            continue
        seen.extend(str(value) for value in ids)
    duplicates = sorted({paper for paper in seen if seen.count(paper) > 1})
    if duplicates:
        errors.append(f"papers appear in multiple waves: {duplicates}")
    if set(seen) != EXPECTED:
        errors.append(f"wave partition mismatch missing={sorted(EXPECTED-set(seen))} extra={sorted(set(seen)-EXPECTED)}")

    for paper_id, item in papers.items():
        if not isinstance(item, dict):
            errors.append(f"{paper_id} entry must be an object")
            continue
        lane = item.get("lane")
        if lane not in ALLOWED_WAVES:
            errors.append(f"{paper_id} invalid lane: {lane}")
            continue
        wave_ids = waves.get(lane, {}).get("papers", []) if isinstance(waves.get(lane), dict) else []
        if paper_id not in wave_ids:
            errors.append(f"{paper_id} lane {lane} disagrees with wave partition")
        if not item.get("bounded_object"):
            errors.append(f"{paper_id} missing bounded_object")
        if not item.get("next_gate"):
            errors.append(f"{paper_id} missing next_gate")

    truth = doc.get("truth_policy", {})
    if truth.get("negative_results_are_binding") is not True:
        errors.append("negative results must be binding")
    if truth.get("cannot_check_is_not_pass") is not True:
        errors.append("CANNOT_CHECK must not be PASS")
    if truth.get("text_only_promotion_forbidden") is not True:
        errors.append("text-only promotion must remain forbidden")
    if truth.get("fallback_terminal") not in ALLOWED_TERMINALS:
        errors.append("invalid fallback terminal")
    if truth.get("max_materially_distinct_science_rounds_before_specialist_fallback") != 3:
        errors.append("science round stop rule must remain exactly 3")

    print(json.dumps({
        "schema": "ORION.All25PublicationClosureManifestCheck.v1",
        "status": "PASS" if not errors else "FAIL",
        "paper_count": len(papers),
        "wave_count": len(waves),
        "terminal_set": sorted(ALLOWED_TERMINALS),
        "errors": errors,
    }, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
