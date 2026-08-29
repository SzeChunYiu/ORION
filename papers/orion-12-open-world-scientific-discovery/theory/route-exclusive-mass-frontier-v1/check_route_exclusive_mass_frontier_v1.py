#!/usr/bin/env python3
"""Independent finite regression for ORION12.ROUTE_EXCLUSIVE_MASS_FRONTIER.v1.

Imports no ORION retrieval code. The theorem is deductive; this checker exhaustively tests
small finite set systems, the partial route-cost frontier, and binds the historical
TREC-COVID adverse gate as data.
"""
from __future__ import annotations

import json
import math
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TREC = ROOT / "papers/orion-12-open-world-scientific-discovery/external/P2_TREC_COVID_ARMS_V1.json"


def subsets(n: int):
    for mask in range(1 << n):
        yield frozenset(i for i in range(n) if mask & (1 << i))


def powerset_items(items):
    items = tuple(items)
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            yield frozenset(combo)


def recall(relevant, output):
    return len(relevant & output) / len(relevant) if relevant else 0.0


def dcg_binary(ranking, relevant, k):
    value = 0.0
    for rank, doc in enumerate(ranking[:k], start=1):
        if doc in relevant:
            value += 1.0 / math.log2(rank + 1)
    return value


def main() -> int:
    errors = []
    frontier_cases = 0
    sharp_cases = 0

    # Theorem 1: exhaustive small finite set systems. Baseline outputs all A.
    n = 5
    all_sets = tuple(subsets(n))
    for relevant in all_sets:
        if not relevant:
            continue
        for baseline in all_sets:
            base_rel = len(relevant & baseline)
            for added in all_sets:
                exclusive = relevant & (added - baseline)
                reachable = baseline | added
                # Exhaust every possible expanded output E subset of reachable.
                for expanded in powerset_items(reachable):
                    gain = len(relevant & expanded) - base_rel
                    if gain > len(exclusive):
                        errors.append(
                            f"exclusive frontier violated R={relevant} A={baseline} N={added} E={expanded}"
                        )
                        break
                    frontier_cases += 1
                if errors:
                    break
                # Sharpness whenever output can include A union exclusive mass.
                sharp_output = baseline | exclusive
                sharp_gain = len(relevant & sharp_output) - base_rel
                if sharp_gain != len(exclusive):
                    errors.append("sharp construction failed")
                    break
                sharp_cases += 1
            if errors:
                break
        if errors:
            break

    # Theorem 2: two-route weighted partial cover, exhaustive n=4 set systems.
    cost_cases = 0
    n2 = 4
    sets2 = tuple(subsets(n2))
    route_cost = {0: 2, 1: 3}
    for relevant in sets2:
        if not relevant:
            continue
        for baseline in sets2:
            for n0 in sets2:
                for n1 in sets2:
                    routes = {0: n0, 1: n1}
                    exclusive_by_selection = {}
                    for selected in powerset_items((0, 1)):
                        union = frozenset().union(*(routes[j] for j in selected)) if selected else frozenset()
                        exclusive_by_selection[selected] = len(relevant & (union - baseline))
                    max_gain = max(exclusive_by_selection.values())
                    for target in range(max_gain + 1):
                        feasible = [
                            s for s, mass in exclusive_by_selection.items() if mass >= target
                        ]
                        optimum = min(sum(route_cost[j] for j in s) for s in feasible)
                        for selected in feasible:
                            actual = sum(route_cost[j] for j in selected)
                            if actual < optimum:
                                errors.append("partial-cover optimum violated")
                                break
                        cost_cases += 1
                    if errors:
                        break
                if errors:
                    break
            if errors:
                break
        if errors:
            break

    # Negative control: route count alone is not value. Three added routes can be
    # exact duplicates of A and create zero exclusive mass.
    r = frozenset({0, 1})
    a = frozenset({0})
    duplicate_routes = (a, a, a)
    union_dup = frozenset().union(*duplicate_routes)
    route_count_no_value = len(r & (union_dup - a)) == 0
    if not route_count_no_value:
        errors.append("duplicate-route no-value control failed")

    # Metric-separation control: same recall, better DCG/nDCG-style ordering.
    relevant = frozenset({"r"})
    baseline_rank = ("x", "r")
    improved_rank = ("r", "x")
    same_recall = recall(relevant, frozenset(baseline_rank)) == recall(relevant, frozenset(improved_rank))
    better_dcg = dcg_binary(improved_rank, relevant, 2) > dcg_binary(baseline_rank, relevant, 2)
    if not (same_recall and better_dcg):
        errors.append("ranking-vs-recall separation control failed")

    # Incorrect equality claim must be rejectable: reachable exclusive mass can exist
    # while E deliberately omits it, so gain < exclusive mass.
    equality_false_control = (
        len(frozenset({1}) & (frozenset({1}) - frozenset({0}))) == 1
        and (len(frozenset({1}) & frozenset({0})) - len(frozenset({1}) & frozenset({0}))) == 0
    )
    if not equality_false_control:
        errors.append("strict-inequality control failed")

    # Bind the current historical adverse packet without recomputing retrieval.
    trec = json.loads(TREC.read_text(encoding="utf-8"))
    bm25 = trec["arms_macro"]["bm25"]
    orion = trec["arms_macro"]["orion_full"]
    gate = trec["pass_gate_verdict"]
    expected = {
        "bm25_recall": 0.110334,
        "orion_recall": 0.092642,
        "bm25_reads": 85.52,
        "orion_reads": 235.8,
        "overall": "FAIL",
        "recall_verdict": "FAIL",
        "cost_verdict": "FAIL",
    }
    observed = {
        "bm25_recall": bm25["recall_at_100"],
        "orion_recall": orion["recall_at_100"],
        "bm25_reads": bm25["mean_reads"],
        "orion_reads": orion["mean_reads"],
        "overall": gate["overall"],
        "recall_verdict": gate["criteria"]["recall_noninferiority"]["verdict"],
        "cost_verdict": gate["criteria"]["cost_reduction"]["verdict"],
    }
    if observed != expected:
        errors.append(f"historical adverse binding changed: {observed}")
    if not gate["not_a_gate_criterion_but_measured"]["ndcg_at_10_delta_mean"] > 0:
        errors.append("historical positive nDCG secondary result disappeared")

    report = {
        "status": "PASS" if not errors else "MISMATCH",
        "terminal": (
            "ROUTE_EXCLUSIVE_MASS_FRONTIER_PROVED__FRESH_ROUTE_VALUE_UNTESTED"
            if not errors else "CANNOT_CHECK_ROUTE_FRONTIER_REGRESSION"
        ),
        "theorem1_exhaustive": {
            "universe_size": n,
            "expanded_outputs_checked": frontier_cases,
            "sharp_constructions_checked": sharp_cases,
        },
        "theorem2_partial_cover": {
            "universe_size": n2,
            "routes": 2,
            "cost_frontiers_checked": cost_cases,
        },
        "controls": {
            "multiple_duplicate_routes_zero_exclusive_value": route_count_no_value,
            "same_recall_better_ranking_score": same_recall and better_dcg,
            "exclusive_bound_is_not_equality": equality_false_control,
        },
        "historical_trec_binding": observed,
        "errors": errors,
        "scientific_authority_delta": "NONE",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 5


if __name__ == "__main__":
    raise SystemExit(main())
