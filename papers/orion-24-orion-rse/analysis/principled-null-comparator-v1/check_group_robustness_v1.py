#!/usr/bin/env python3
"""Independent checker for ORION24.GROUP_ROBUSTNESS.v1.

Recomputes the compact frozen result directly from gold + SYSTEMB decisions. It imports
neither evaluate_against_principled_nulls_v1.py nor leave_one_group_robustness_v1.py.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "papers/orion-24-orion-rse/top_tier/external_v1"
GOLD = BASE / "protected/p14_external_gold_v1.jsonl"
SYSTEMB = BASE / "pilot/decisions/p14_external_decisions_SYSTEMB_v1.jsonl"
RESULT = HERE / "GROUP_ROBUSTNESS_V1.json"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate(rows, pred_b):
    ids = [r["packet_id"] for r in rows]
    gold = {r["packet_id"]: r["gold_disposition"] for r in rows}
    by_domain = collections.defaultdict(collections.Counter)
    for r in rows:
        by_domain[r["domain"]][r["gold_disposition"]] += 1
    majority = {d: c.most_common(1)[0][0] for d, c in by_domain.items()}
    pred_null = {r["packet_id"]: majority[r["domain"]] for r in rows}
    system_score = sum(pred_b[p] == gold[p] for p in ids)
    null_score = sum(pred_null[p] == gold[p] for p in ids)
    b = sum(pred_b[p] == gold[p] and pred_null[p] != gold[p] for p in ids)
    c = sum(pred_b[p] != gold[p] and pred_null[p] == gold[p] for p in ids)
    return {
        "n": len(ids),
        "systemb_score": system_score,
        "stratified_score": null_score,
        "system_only_correct": b,
        "null_only_correct": c,
    }, majority


def main() -> int:
    gold_rows = load_jsonl(GOLD)
    decisions = load_jsonl(SYSTEMB)
    recorded = json.loads(RESULT.read_text(encoding="utf-8"))
    pred_b = {r["packet_id"]: r["disposition"] for r in decisions}
    errors = []

    if len(gold_rows) != 67 or set(pred_b) != {r["packet_id"] for r in gold_rows}:
        errors.append("input denominator or ID set changed")

    full, full_majority = evaluate(gold_rows, pred_b)
    if full != recorded["full"]:
        errors.append(f"full mismatch: {full} != {recorded['full']}")

    families = sorted({r["family"] for r in gold_rows})
    domains = sorted({r["domain"] for r in gold_rows})

    recomputed_family = {}
    for family in families:
        value, _ = evaluate([r for r in gold_rows if r["family"] != family], pred_b)
        recomputed_family[family] = value
    if recomputed_family != recorded["leave_one_family_out"]:
        errors.append("leave-one-family table mismatch")

    recomputed_domain = {}
    for domain in domains:
        value, _ = evaluate([r for r in gold_rows if r["domain"] != domain], pred_b)
        recomputed_domain[domain] = value
    if recomputed_domain != recorded["leave_one_domain_out"]:
        errors.append("leave-one-domain table mismatch")

    local = {}
    for family in families:
        subset = [r for r in gold_rows if r["family"] == family]
        b_correct = sum(pred_b[r["packet_id"]] == r["gold_disposition"] for r in subset)
        n_correct = sum(full_majority[r["domain"]] == r["gold_disposition"] for r in subset)
        local[family] = b_correct - n_correct
    if local != recorded["family_local_margin_vs_full_stratified"]:
        errors.append("family-local margin table mismatch")

    expected_summary = {
        "families": len(families),
        "domains": len(domains),
        "all_family_deletions_favour_systemb_vs_recomputed_stratified": all(
            x["system_only_correct"] > x["null_only_correct"] for x in recomputed_family.values()
        ),
        "all_domain_deletions_favour_systemb_vs_recomputed_stratified": all(
            x["system_only_correct"] > x["null_only_correct"] for x in recomputed_domain.values()
        ),
        "minimum_leave_family_system_only_correct": min(x["system_only_correct"] for x in recomputed_family.values()),
        "maximum_leave_family_null_only_correct": max(x["null_only_correct"] for x in recomputed_family.values()),
        "minimum_leave_domain_system_only_correct": min(x["system_only_correct"] for x in recomputed_domain.values()),
        "maximum_leave_domain_null_only_correct": max(x["null_only_correct"] for x in recomputed_domain.values()),
        "families_with_positive_local_margin": sum(v > 0 for v in local.values()),
        "minimum_family_local_margin": min(local.values()),
    }
    if expected_summary != recorded["summary"]:
        errors.append(f"summary mismatch: {expected_summary} != {recorded['summary']}")

    report = {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "INTERNAL_ADVANTAGE_NOT_DRIVEN_BY_ANY_SINGLE_FAMILY_OR_DOMAIN"
            if not errors else "CANNOT_CHECK_GROUP_ROBUSTNESS_BINDING"
        ),
        "full": full,
        "summary": expected_summary,
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 5


if __name__ == "__main__":
    raise SystemExit(main())
