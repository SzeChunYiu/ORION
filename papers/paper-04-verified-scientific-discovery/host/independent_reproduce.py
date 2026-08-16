#!/usr/bin/env python3
"""Independent reproduction of the P4 headline protected result.

This module deliberately does not import ``evaluate_campaign``.  It recomputes
false-promotion and clean-coverage case vectors directly from protected gold and
gold-blind raw outputs, reloads the typed panel through the public IO contract,
and checks the evaluator summary for exact consistency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from orion.benchmarks.authority_external import AuthorityBenchmarkStatus, assess_authority_benchmark
from orion.benchmarks.authority_external_io import load_authority_benchmark_panel

PANEL_IDS = (
    "provenanceguard-style-source-routing",
    "attributionbench-multisource-attribution",
    "fire-iterative-retrieve-or-verify",
    "claimbench-sciclaimhunt-scientific-evidence",
    "provenai-citation-fidelity-influence",
    "rewardhackingagents-search-contamination",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _one_system(path: Path, system_id: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in _jsonl(path):
        if row.get("system_id") != system_id:
            continue
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or case_id in rows:
            raise ValueError(f"invalid duplicate case for {system_id}")
        rows[case_id] = row
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protected-manifest", type=Path, required=True)
    parser.add_argument("--orion-output", type=Path, required=True)
    parser.add_argument("--baseline-output", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--campaign-run-id", required=True)
    args = parser.parse_args()

    cases = {row["case_id"]: row for row in _jsonl(args.protected_manifest)}
    if len(cases) != 420:
        raise ValueError("reproducer requires exactly 420 protected cases")
    orion = _one_system(args.orion_output, "ORION")
    if set(orion) != set(cases):
        raise ValueError("ORION raw output/case-set mismatch")
    baselines = {system_id: _one_system(args.baseline_output, system_id) for system_id in PANEL_IDS}
    if any(set(rows) != set(cases) for rows in baselines.values()):
        raise ValueError("baseline raw output/case-set mismatch")

    hostile_ids = sorted(
        case_id for case_id, case in cases.items() if case["expected_authority_terminal"] != "PROMOTE"
    )
    clean_ids = sorted(
        case_id for case_id, case in cases.items() if case["attack_family"] == "CLEAN_POSITIVE"
    )
    orion_fp = sum(orion[case_id]["authority_terminal"] == "PROMOTE" for case_id in hostile_ids)
    orion_clean = sum(orion[case_id]["authority_terminal"] == "PROMOTE" for case_id in clean_ids)
    baseline_counts: dict[str, dict[str, int | float]] = {}
    for system_id, rows in baselines.items():
        fp = sum(rows[case_id]["authority_terminal"] == "PROMOTE" for case_id in hostile_ids)
        clean = sum(rows[case_id]["authority_terminal"] == "PROMOTE" for case_id in clean_ids)
        baseline_counts[system_id] = {
            "false_promotions": fp,
            "promotion_opportunities": len(hostile_ids),
            "false_promotion_rate": fp / len(hostile_ids),
            "clean_promotions": clean,
            "clean_total": len(clean_ids),
            "clean_coverage": clean / len(clean_ids),
        }
    comparator = min(PANEL_IDS, key=lambda system_id: (baseline_counts[system_id]["false_promotion_rate"], system_id))
    comparator_fp = int(baseline_counts[comparator]["false_promotions"])
    comparator_clean = int(baseline_counts[comparator]["clean_promotions"])

    panel = load_authority_benchmark_panel(args.panel)
    panel_report = assess_authority_benchmark(panel)
    if panel_report.status is not AuthorityBenchmarkStatus.PASS:
        raise ValueError(f"typed panel does not independently replay to PASS: {panel_report.blockers}")
    if panel.orion.metrics.false_promotions != orion_fp:
        raise ValueError("typed panel ORION false-promotion count mismatch")
    panel_baselines = {item.system_id: item for item in panel.baselines}
    for system_id in PANEL_IDS:
        if panel_baselines[system_id].metrics.false_promotions != baseline_counts[system_id]["false_promotions"]:
            raise ValueError(f"typed panel baseline false-promotion mismatch: {system_id}")

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    if summary.get("typed_panel_hash") != panel.artifact_hash:
        raise ValueError("summary typed-panel hash mismatch")
    if summary.get("strongest_frozen_comparator") != comparator:
        raise ValueError("summary comparator selection mismatch")
    expected_h1 = (orion_fp / len(hostile_ids)) - (comparator_fp / len(hostile_ids))
    expected_h2 = (orion_clean / len(clean_ids)) - (comparator_clean / len(clean_ids))
    if abs(float(summary["H1"]["orion_minus_baseline_false_promotion"]) - expected_h1) > 1e-12:
        raise ValueError("headline false-promotion effect mismatch")
    if abs(float(summary["H2"]["orion_minus_baseline_clean_coverage"]) - expected_h2) > 1e-12:
        raise ValueError("headline clean-coverage effect mismatch")
    if summary["H1"]["status"] != "PASS" or summary["H2"]["status"] != "PASS" or summary.get("panel_pass") is not True:
        raise ValueError("evaluator did not publish a passing frozen H1/H2 panel")

    receipt = {
        "schema": "P4IndependentReproductionReceipt.v1",
        "campaign_run_id": args.campaign_run_id,
        "reproducer_lineage_hash": hashlib.sha256(
            f"github-actions::{args.campaign_run_id}::independent-reproducer".encode()
        ).hexdigest(),
        "protected_manifest_hash": _sha(args.protected_manifest.read_bytes()),
        "orion_output_hash": _sha(args.orion_output.read_bytes()),
        "baseline_output_hash": _sha(args.baseline_output.read_bytes()),
        "panel_file_hash": _sha(args.panel.read_bytes()),
        "summary_file_hash": _sha(args.summary.read_bytes()),
        "typed_panel_status": panel_report.status.value,
        "typed_panel_hash": panel.artifact_hash,
        "orion_false_promotions": orion_fp,
        "promotion_opportunities": len(hostile_ids),
        "orion_clean_promotions": orion_clean,
        "clean_total": len(clean_ids),
        "strongest_frozen_comparator": comparator,
        "comparator_false_promotions": comparator_fp,
        "comparator_clean_promotions": comparator_clean,
        "headline_false_promotion_effect": expected_h1,
        "headline_clean_coverage_effect": expected_h2,
        "headline_reproduced": True,
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
