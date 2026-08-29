#!/usr/bin/env python3
"""ORION-24: leave-one-family/domain-out robustness against principled nulls.

Reads the already-frozen external-v1 gold and SYSTEMB decisions. No labels, decisions,
thresholds, or corpus membership are changed. For each deletion, the stratified null is
RECOMPUTED on the retained rows so it gets the strongest fair majority label available
within each remaining domain.

This is internal-panel sensitivity analysis, not external validation or population
inference. Exit 0 means the analysis completed, not that a scientific promotion gate passed.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os

BASE = "papers/orion-24-orion-rse/top_tier/external_v1"
GOLD = f"{BASE}/protected/p14_external_gold_v1.jsonl"
SYSTEMB = f"{BASE}/pilot/decisions/p14_external_decisions_SYSTEMB_v1.jsonl"


def repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def load_jsonl(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def exact_binomial_two_sided(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2 * tail)


def evaluate(rows: list[dict], pred_b: dict[str, str]) -> dict:
    ids = [r["packet_id"] for r in rows]
    gold = {r["packet_id"]: r["gold_disposition"] for r in rows}

    by_domain = collections.defaultdict(collections.Counter)
    for r in rows:
        by_domain[r["domain"]][r["gold_disposition"]] += 1
    domain_majority = {
        domain: counts.most_common(1)[0][0]
        for domain, counts in sorted(by_domain.items())
    }
    pred_strat = {r["packet_id"]: domain_majority[r["domain"]] for r in rows}
    pred_promote = {packet_id: "PROMOTE" for packet_id in ids}

    def score(pred):
        return sum(pred.get(packet_id) == gold[packet_id] for packet_id in ids)

    def paired(null_pred):
        b = sum(
            pred_b.get(packet_id) == gold[packet_id]
            and null_pred.get(packet_id) != gold[packet_id]
            for packet_id in ids
        )
        c = sum(
            pred_b.get(packet_id) != gold[packet_id]
            and null_pred.get(packet_id) == gold[packet_id]
            for packet_id in ids
        )
        return {
            "system_only_correct": b,
            "null_only_correct": c,
            "two_sided_exact_p": exact_binomial_two_sided(b, c),
            "favours_systemb": b > c,
        }

    return {
        "n": len(ids),
        "systemb_score": score(pred_b),
        "always_promote_score": score(pred_promote),
        "stratified_score": score(pred_strat),
        "domain_majority": domain_majority,
        "vs_always_promote": paired(pred_promote),
        "vs_stratified": paired(pred_strat),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()

    root = repo_root(os.path.dirname(os.path.abspath(__file__)))
    gold_path = os.path.join(root, GOLD)
    b_path = os.path.join(root, SYSTEMB)
    if not os.path.isfile(gold_path) or not os.path.isfile(b_path):
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "INPUT_ABSENT"}))
        return 3

    rows = load_jsonl(gold_path)
    decisions = load_jsonl(b_path)
    pred_b = {r["packet_id"]: r["disposition"] for r in decisions}
    gold_ids = {r["packet_id"] for r in rows}
    if set(pred_b) != gold_ids:
        missing = sorted(gold_ids - set(pred_b))
        extra = sorted(set(pred_b) - gold_ids)
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "ID_MISMATCH",
                          "missing": missing, "extra": extra}, indent=2))
        return 3

    full = evaluate(rows, pred_b)
    families = sorted({r["family"] for r in rows})
    domains = sorted({r["domain"] for r in rows})

    leave_family = {}
    for family in families:
        kept = [r for r in rows if r["family"] != family]
        leave_family[family] = evaluate(kept, pred_b)

    leave_domain = {}
    for domain in domains:
        kept = [r for r in rows if r["domain"] != domain]
        leave_domain[domain] = evaluate(kept, pred_b)

    # Family-local contribution against the full-panel stratified null. This is descriptive:
    # it shows which families supply/consume the aggregate margin, not independent replications.
    full_majority = full["domain_majority"]
    family_local = {}
    for family in families:
        subset = [r for r in rows if r["family"] == family]
        b_correct = sum(pred_b[r["packet_id"]] == r["gold_disposition"] for r in subset)
        n_correct = sum(full_majority[r["domain"]] == r["gold_disposition"] for r in subset)
        family_local[family] = {
            "n": len(subset),
            "systemb_correct": b_correct,
            "stratified_correct": n_correct,
            "margin": b_correct - n_correct,
        }

    family_strat_margins = [
        item["vs_stratified"]["system_only_correct"]
        - item["vs_stratified"]["null_only_correct"]
        for item in leave_family.values()
    ]
    domain_strat_margins = [
        item["vs_stratified"]["system_only_correct"]
        - item["vs_stratified"]["null_only_correct"]
        for item in leave_domain.values()
    ]

    out = {
        "checker": "orion24_leave_one_group_robustness_v1",
        "status": "MEASURED",
        "scientific_authority_delta": "NONE",
        "claim_scope": (
            "Sensitivity of the fixed 67-packet internally adjudicated panel only; "
            "not external validation and not population inference."
        ),
        "full": full,
        "leave_one_family_out": leave_family,
        "leave_one_domain_out": leave_domain,
        "family_local_contribution_vs_full_stratified": family_local,
        "summary": {
            "families": len(families),
            "domains": len(domains),
            "all_family_deletions_favour_systemb_vs_stratified": all(
                item["vs_stratified"]["favours_systemb"] for item in leave_family.values()
            ),
            "all_domain_deletions_favour_systemb_vs_stratified": all(
                item["vs_stratified"]["favours_systemb"] for item in leave_domain.values()
            ),
            "minimum_leave_family_stratified_discordance_margin": min(family_strat_margins),
            "minimum_leave_domain_stratified_discordance_margin": min(domain_strat_margins),
            "families_with_positive_local_margin": sum(
                item["margin"] > 0 for item in family_local.values()
            ),
            "families_with_zero_local_margin": sum(
                item["margin"] == 0 for item in family_local.values()
            ),
            "families_with_negative_local_margin": sum(
                item["margin"] < 0 for item in family_local.values()
            ),
        },
    }

    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            fh.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
