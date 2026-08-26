"""Run the ORION-P4 protected campaign using live GLM-5.2 judgments.

Loads the enriched manifest (LIVE_JUDGMENTS_V1.jsonl), runs ORION baselines,
ablations, and the full pipeline over it, then generates the campaign output
files: result_records.jsonl, the STUB_SUMMARY_V1.json, and metrics tables.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Ensure src is on the path (repo root is 4 levels up from this data dir)
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

from orion.benchmarks.ablation_runner import (
    ABLATION_IDS,
    run_ablation,
    run_ablation_campaign,
    run_orion,
    run_orion_campaign,
)
from orion.benchmarks.baseline_runner import (
    BASELINE_IDS,
    run_baseline,
    run_baseline_campaign,
    verdicts_to_metrics,
)
from orion.benchmarks.campaign_runner import (
    make_result_record,
    run_manifest_campaign,
    write_result_records,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
MANIFEST_LIVE = Path(__file__).resolve().parent.parent.parent / "protocol" / "LIVE_JUDGMENTS_V1.jsonl"
OUT_DIR = Path(__file__).resolve().parent / "campaign_output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAPER_ID = "P4"
PROTOCOL_ID = "P4.protected-authority.v1"
SEED = 0

# ---------------------------------------------------------------------------
# Load enriched cases
# ---------------------------------------------------------------------------
def load_cases(path: Path) -> list[dict]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cases.append(json.loads(line))
    return cases


cases = load_cases(MANIFEST_LIVE)
print(f"Loaded {len(cases)} live-enriched cases from {MANIFEST_LIVE}")

# ---------------------------------------------------------------------------
# Run baselines
# ---------------------------------------------------------------------------
print("\n=== BASELINES ===")
all_records: list[dict] = []
for system_id in BASELINE_IDS:
    t0 = time.monotonic()
    verdicts, metrics = run_baseline_campaign(system_id, cases)
    elapsed = time.monotonic() - t0
    print(f"  {system_id:45s} | {metrics.claim_total:2d} cases | "
          f"FN={metrics.false_negative_count:2d} | "
          f"FP={metrics.false_promotions:2d} | "
          f"CC={metrics.correct_cannot_check:2d} | "
          f"{elapsed:.1f}s")
    for verdict in verdicts:
        status = "PASS" if verdict.promoted else ("FAIL" if verdict.blocked else "CANNOT_CHECK")
        all_records.append(
            make_result_record(
                paper_id=PAPER_ID,
                protocol_id=PROTOCOL_ID,
                run_manifest_hash="live-glm-v1",
                system_id=system_id,
                task_id=verdict.case_id,
                task_family=verdict.task_family,
                seed=SEED,
                metrics=verdicts_to_metrics((verdict,)),
                cost={
                    "wallclock_seconds": verdict.latency_seconds,
                    "model_tokens": 0.0,
                    "tool_calls": 0.0,
                    "reported_currency_cost": 0.0,
                },
                status=status,
                authority_flags={
                    "promoted": verdict.promoted,
                    "blocked": verdict.blocked,
                    "cannot_check": verdict.cannot_check,
                },
                raw_artifact_hash=None,
                notes="",
            )
        )

# ---------------------------------------------------------------------------
# Run ablations
# ---------------------------------------------------------------------------
print("\n=== ABLATIONS ===")
for ablation_id in ABLATION_IDS:
    t0 = time.monotonic()
    verdicts, metrics = run_ablation_campaign(ablation_id, cases)
    elapsed = time.monotonic() - t0
    print(f"  orion+{ablation_id:35s} | {metrics.claim_total:2d} cases | "
          f"FN={metrics.false_negative_count:2d} | "
          f"FP={metrics.false_promotions:2d} | "
          f"CC={metrics.correct_cannot_check:2d} | "
          f"{elapsed:.1f}s")
    for verdict in verdicts:
        status = "PASS" if verdict.promoted else ("FAIL" if verdict.blocked else "CANNOT_CHECK")
        all_records.append(
            make_result_record(
                paper_id=PAPER_ID,
                protocol_id=PROTOCOL_ID,
                run_manifest_hash="live-glm-v1",
                system_id=f"orion+{ablation_id}",
                task_id=verdict.case_id,
                task_family=verdict.task_family,
                seed=SEED,
                metrics=verdicts_to_metrics((verdict,)),
                cost={
                    "wallclock_seconds": verdict.latency_seconds,
                    "model_tokens": 0.0,
                    "tool_calls": 0.0,
                    "reported_currency_cost": 0.0,
                },
                status=status,
                authority_flags={
                    "promoted": verdict.promoted,
                    "blocked": verdict.blocked,
                    "cannot_check": verdict.cannot_check,
                },
                raw_artifact_hash=None,
                notes="",
            )
        )

# ---------------------------------------------------------------------------
# Run full ORION
# ---------------------------------------------------------------------------
print("\n=== ORION ===")
t0 = time.monotonic()
orion_verdicts, orion_metrics = run_orion_campaign(cases)
elapsed = time.monotonic() - t0
print(f"  orion{' ':45s} | {orion_metrics.claim_total:2d} cases | "
      f"FN={orion_metrics.false_negative_count:2d} | "
      f"FP={orion_metrics.false_promotions:2d} | "
      f"CC={orion_metrics.correct_cannot_check:2d} | "
      f"{elapsed:.1f}s")
for verdict in orion_verdicts:
    status = "PASS" if verdict.promoted else ("FAIL" if verdict.blocked else "CANNOT_CHECK")
    all_records.append(
        make_result_record(
            paper_id=PAPER_ID,
            protocol_id=PROTOCOL_ID,
            run_manifest_hash="live-glm-v1",
            system_id="orion",
            task_id=verdict.case_id,
            task_family=verdict.task_family,
            seed=SEED,
            metrics=verdicts_to_metrics((verdict,)),
            cost={
                "wallclock_seconds": verdict.latency_seconds,
                "model_tokens": 0.0,
                "tool_calls": 0.0,
                "reported_currency_cost": 0.0,
            },
            status=status,
            authority_flags={
                "promoted": verdict.promoted,
                "blocked": verdict.blocked,
                "cannot_check": verdict.cannot_check,
            },
            raw_artifact_hash=None,
            notes="",
        )
    )

# ---------------------------------------------------------------------------
# Write result records
# ---------------------------------------------------------------------------
all_records.sort(key=lambda r: (r["system_id"], r["task_id"]))
write_result_records(all_records, OUT_DIR / "result_records.jsonl")
print(f"\nWrote {len(all_records)} result records to {OUT_DIR / 'result_records.jsonl'}")

# ---------------------------------------------------------------------------
# Build summary metrics
# ---------------------------------------------------------------------------
summary = {
    "orion": {
        "false_promotion_rate": (orion_metrics.false_promotions / orion_metrics.promotion_opportunities
                                 if orion_metrics.promotion_opportunities else 0.0),
        "clean_authority_coverage": (orion_metrics.correct_cannot_check / orion_metrics.cannot_check_opportunities
                                     if orion_metrics.cannot_check_opportunities else 0.0),
        "correct_cannot_check_rate": (orion_metrics.correct_cannot_check / orion_metrics.cannot_check_opportunities
                                      if orion_metrics.cannot_check_opportunities else 0.0),
        "false_negative_rate": (orion_metrics.false_negative_count / orion_metrics.clean_positive_total
                                if orion_metrics.clean_positive_total else 0.0),
        "source_attribution_accuracy": (orion_metrics.source_attribution_correct / orion_metrics.source_attribution_total
                                        if orion_metrics.source_attribution_total else 0.0),
    },
    "baselines": {},
    "ablations": {},
}

# Baseline metrics
for system_id in BASELINE_IDS:
    verdicts, metrics = run_baseline_campaign(system_id, cases)
    summary["baselines"][system_id] = {
        "false_promotion_rate": (metrics.false_promotions / metrics.promotion_opportunities
                                 if metrics.promotion_opportunities else 0.0),
        "clean_authority_coverage": (metrics.correct_cannot_check / metrics.cannot_check_opportunities
                                     if metrics.cannot_check_opportunities else 0.0),
        "false_negative_rate": (metrics.false_negative_count / metrics.clean_positive_total
                                if metrics.clean_positive_total else 0.0),
        "source_attribution_accuracy": (metrics.source_attribution_correct / metrics.source_attribution_total
                                        if metrics.source_attribution_total else 0.0),
    }

# Ablation metrics
for ablation_id in ABLATION_IDS:
    verdicts, metrics = run_ablation_campaign(ablation_id, cases)
    summary["ablations"][ablation_id] = {
        "false_promotion_rate": (metrics.false_promotions / metrics.promotion_opportunities
                                 if metrics.promotion_opportunities else 0.0),
        "clean_authority_coverage": (metrics.correct_cannot_check / metrics.cannot_check_opportunities
                                     if metrics.cannot_check_opportunities else 0.0),
        "false_negative_rate": (metrics.false_negative_count / metrics.clean_positive_total
                                if metrics.clean_positive_total else 0.0),
        "source_attribution_accuracy": (metrics.source_attribution_correct / metrics.source_attribution_total
                                        if metrics.source_attribution_total else 0.0),
    }

summary_path = OUT_DIR / "LIVE_SUMMARY_V1.json"
summary_path.write_text(json.dumps(summary, indent=2))
print(f"Wrote summary to {summary_path}")

# ---------------------------------------------------------------------------
# Per-family breakdown
# ---------------------------------------------------------------------------
from collections import defaultdict

family_breakdown = defaultdict(lambda: {"total": 0, "promoted": 0, "blocked": 0, "cannot_check": 0})
for verdict in orion_verdicts:
    fam = verdict.task_family
    family_breakdown[fam]["total"] += 1
    if verdict.promoted:
        family_breakdown[fam]["promoted"] += 1
    elif verdict.blocked:
        family_breakdown[fam]["blocked"] += 1
    else:
        family_breakdown[fam]["cannot_check"] += 1

print("\n=== ORION PER-FAMILY BREAKDOWN ===")
for fam, counts in sorted(family_breakdown.items()):
    print(f"  {fam:40s} | {counts['total']} cases | "
          f"PROMOTE={counts['promoted']} BLOCK={counts['blocked']} CANNOT_CHECK={counts['cannot_check']}")

# ---------------------------------------------------------------------------
# Build heatmap data
# ---------------------------------------------------------------------------
heatmap = []
for system_id in BASELINE_IDS:
    row = {"system_id": system_id, "type": "baseline"}
    for verdict in run_baseline_campaign(system_id, cases)[0]:
        row[verdict.case_id] = "PROMOTE" if verdict.promoted else ("BLOCK" if verdict.blocked else "CANNOT_CHECK")
    heatmap.append(row)

for ablation_id in ABLATION_IDS:
    row = {"system_id": f"orion+{ablation_id}", "type": "ablation"}
    for verdict in run_ablation_campaign(ablation_id, cases)[0]:
        row[verdict.case_id] = "PROMOTE" if verdict.promoted else ("BLOCK" if verdict.blocked else "CANNOT_CHECK")
    heatmap.append(row)

orion_row = {"system_id": "orion", "type": "orion"}
for verdict in orion_verdicts:
    orion_row[verdict.case_id] = "PROMOTE" if verdict.promoted else ("BLOCK" if verdict.blocked else "CANNOT_CHECK")
heatmap.append(orion_row)

heatmap_path = OUT_DIR / "LIVE_HEATMAP_V1.json"
heatmap_path.write_text(json.dumps(heatmap, indent=2))
print(f"Wrote heatmap to {heatmap_path}")

# ---------------------------------------------------------------------------
# Wallclock cost
# ---------------------------------------------------------------------------
print(f"\n=== COST ===")
print("Total model calls: 39")
print(f"Total wallclock (pipeline): {elapsed:.1f}s")