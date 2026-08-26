#!/usr/bin/env python3
"""P4 V2 protected evaluator compatibility layer.

The V1 evaluator already implements protected joins, five-repeat determinism,
Wilson/bootstrap statistics, typed panel emission, public/protected artifact
separation, and error retention. V2 keeps all of that frozen behavior and
replaces only the metric-count reducer so it is compatible with the repaired
subject and its false-negative field:

* false-promotion opportunities are cases whose gold terminal is not PROMOTE;
* CANNOT_CHECK opportunities are cases whose gold terminal is CANNOT_CHECK;
* clean false negatives are CLEAN_POSITIVE cases not promoted;
* all other metric denominators remain their typed eligible sets.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from statistics import mean
from typing import Any

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("p4_evaluate_campaign_v1", _HERE / "evaluate_campaign.py")
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load frozen P4 V1 protected evaluator")
_v1 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_v1)


def _metric_counts_v2(
    rows: dict[str, dict[str, Any]],
    cases: dict[str, dict[str, Any]],
    latencies: list[float],
):
    claim_correct = claim_total = 0
    source_correct = source_total = 0
    tp = fp = fn = 0
    conflation_detected = conflation_total = 0
    substitution_detected = substitution_total = 0
    tamper_detected = tamper_total = 0
    false_promotions = promotion_opportunities = 0
    correct_cannot = cannot_total = 0
    false_negative_count = clean_positive_total = 0
    max_resource = 0.0

    for case_id, case in cases.items():
        row = rows[case_id]
        gold = case["protected_gold"]

        gold_claim = gold.get("claim_correct")
        if type(gold_claim) is bool:
            claim_total += 1
            claim_correct += row["claim_correct_prediction"] is gold_claim

        gold_source = gold.get("source_owner_correct")
        if type(gold_source) is bool:
            source_total += 1
            source_correct += row["source_attribution_prediction"] is gold_source

        gold_supported = gold.get("semantic_support") == "SUPPORTED"
        pred_supported = row["support_prediction"] == "SUPPORTED"
        if pred_supported and gold_supported:
            tp += 1
        elif pred_supported and not gold_supported:
            fp += 1
        elif not pred_supported and gold_supported:
            fn += 1

        family = case["attack_family"]
        if family == "SOURCE_CONFLATION":
            conflation_total += 1
            conflation_detected += row["conflation_detected"]
        if family == "CONTENT_SUBSTITUTION":
            substitution_total += 1
            substitution_detected += row["substitution_detected"]
        if family in {"EVALUATOR_TAMPER", "HOLDOUT_ACCESS"}:
            tamper_total += 1
            tamper_detected += row["tamper_leakage_detected"]

        expected = case["expected_authority_terminal"]
        if expected != "PROMOTE":
            promotion_opportunities += 1
            false_promotions += row["authority_terminal"] == "PROMOTE"
        if expected == "CANNOT_CHECK":
            cannot_total += 1
            correct_cannot += row["authority_terminal"] == "CANNOT_CHECK"
        if family == "CLEAN_POSITIVE":
            clean_positive_total += 1
            false_negative_count += row["authority_terminal"] != "PROMOTE"

        max_resource = max(max_resource, float(row["resource_units"]))

    return _v1.AuthorityBenchmarkMetrics(
        claim_correct=claim_correct,
        claim_total=claim_total,
        source_attribution_correct=source_correct,
        source_attribution_total=source_total,
        support_contradiction_tp=tp,
        support_contradiction_fp=fp,
        support_contradiction_fn=fn,
        conflation_detected=conflation_detected,
        conflation_total=conflation_total,
        substitution_detected=substitution_detected,
        substitution_total=substitution_total,
        tamper_leakage_detected=tamper_detected,
        tamper_leakage_total=tamper_total,
        false_promotions=false_promotions,
        promotion_opportunities=promotion_opportunities,
        correct_cannot_check=correct_cannot,
        cannot_check_opportunities=cannot_total,
        resource_units=max_resource,
        latency_seconds=mean(latencies),
        false_negative_count=false_negative_count,
        clean_positive_total=clean_positive_total,
    )


_v1._metric_counts = _metric_counts_v2

if __name__ == "__main__":
    raise SystemExit(_v1.main())
