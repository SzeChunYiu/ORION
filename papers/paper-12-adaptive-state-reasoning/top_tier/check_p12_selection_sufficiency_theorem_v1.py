#!/usr/bin/env python3
"""Independent falsifier for P12_SELECTION_SUFFICIENCY_THEOREM_V1.

This checker does not reimplement the candidate DP recurrence as its oracle.
It enumerates all feasible subsets directly, compares objective values, tests
three deliberately wrong selectors, and replays the bound NR-13 battery.
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from p12_price_aware_allocator_v1 import price_aware_selection  # noqa: E402

COSTS = (1, 2, 3)
DELTAS = (-1, 0, 1, 2, 3, 4, 5)
PRICES = ((1, 1), (2, 1), (1, 2), (4, 1), (1, 4))
BUDGETS = tuple(range(7))
MAX_N = 4


def item_value(cost: int, delta: int, prices: tuple[int, int]) -> int:
    p_build, p_serve = prices
    return p_serve * delta - p_build * cost


def subset_stats(items, mask: int, prices):
    weight = 0
    value = 0
    selected = []
    for i, (cost, delta) in enumerate(items):
        if mask & (1 << i):
            weight += cost
            value += item_value(cost, delta, prices)
            selected.append(i)
    return weight, value, tuple(selected)


def exhaustive_oracle(items, prices, budget):
    best = None
    best_sets = []
    for mask in range(1 << len(items)):
        weight, value, selected = subset_stats(items, mask, prices)
        if weight > budget:
            continue
        if best is None or value > best:
            best = value
            best_sets = [selected]
        elif value == best:
            best_sets.append(selected)
    assert best is not None
    return best, tuple(best_sets)


def ledger_for(items):
    # Offset certificates so all serve counts remain non-negative even at delta=-1.
    return [
        {
            "sid": f"S{i}",
            "declared_cost": cost,
            "reason_serve_certificate": 10 + delta,
            "state_serve_certificate": 10,
        }
        for i, (cost, delta) in enumerate(items)
    ]


def selected_value(items, selected_sids, prices):
    selected = {int(sid[1:]) for sid in selected_sids}
    return sum(
        item_value(cost, delta, prices)
        for i, (cost, delta) in enumerate(items)
        if i in selected
    )


def selected_weight(items, selected_sids):
    selected = {int(sid[1:]) for sid in selected_sids}
    return sum(cost for i, (cost, _) in enumerate(items) if i in selected)


def mutant_declared_cost_greedy(items, prices, budget):
    # Price-oblivious: cheapest structures first; no marginal-value test.
    used = 0
    out = []
    for i, (cost, _) in sorted(enumerate(items), key=lambda row: (row[1][0], row[0])):
        if used + cost <= budget:
            out.append(f"S{i}")
            used += cost
    return out


def mutant_positive_without_budget(items, prices, budget):
    del budget
    return [
        f"S{i}" for i, (cost, delta) in enumerate(items)
        if item_value(cost, delta, prices) > 0
    ]


def mutant_reversed_sign(items, prices, budget):
    # Exact exhaustive optimization of the wrong sign: minimize true marginal value.
    worst = None
    chosen = ()
    for mask in range(1 << len(items)):
        weight, value, selected = subset_stats(items, mask, prices)
        if weight > budget:
            continue
        if worst is None or value < worst:
            worst = value
            chosen = selected
    return [f"S{i}" for i in chosen]


MUTANTS = {
    "declared_cost_greedy": mutant_declared_cost_greedy,
    "positive_without_budget": mutant_positive_without_budget,
    "reversed_sign": mutant_reversed_sign,
}


def abstract_exhaustive():
    cells = 0
    ledgers = 0
    candidate_failures = []
    mutant_witnesses = {name: None for name in MUTANTS}
    option_space = tuple(itertools.product(COSTS, DELTAS))

    for n in range(1, MAX_N + 1):
        for items in itertools.product(option_space, repeat=n):
            ledgers += 1
            ledger = ledger_for(items)
            for prices in PRICES:
                for budget in BUDGETS:
                    cells += 1
                    oracle_value, _ = exhaustive_oracle(items, prices, budget)
                    selected = price_aware_selection(ledger, prices, budget)
                    got_weight = selected_weight(items, selected)
                    got_value = selected_value(items, selected, prices)
                    if got_weight > budget or got_value != oracle_value:
                        candidate_failures.append({
                            "items": items,
                            "prices": prices,
                            "budget": budget,
                            "candidate_selected": selected,
                            "candidate_weight": got_weight,
                            "candidate_value": got_value,
                            "oracle_value": oracle_value,
                        })
                        # Fail closed quickly: one counterexample is sufficient.
                        return {
                            "ledgers_checked": ledgers,
                            "cells_checked": cells,
                            "candidate_failures": candidate_failures,
                            "mutant_witnesses": mutant_witnesses,
                        }

                    for name, mutant in MUTANTS.items():
                        if mutant_witnesses[name] is not None:
                            continue
                        msel = mutant(items, prices, budget)
                        mweight = selected_weight(items, msel)
                        mvalue = selected_value(items, msel, prices)
                        if mweight > budget or mvalue != oracle_value:
                            mutant_witnesses[name] = {
                                "items": items,
                                "prices": prices,
                                "budget": budget,
                                "selected": msel,
                                "weight": mweight,
                                "value": mvalue,
                                "oracle_value": oracle_value,
                                "failure_mode": "budget" if mweight > budget else "objective",
                            }

    return {
        "ledgers_checked": ledgers,
        "cells_checked": cells,
        "candidate_failures": candidate_failures,
        "mutant_witnesses": mutant_witnesses,
    }


def run_bound_nr13():
    proc = subprocess.run(
        [sys.executable, "run_p12_price_aware_successor_v1.py"],
        cwd=HERE,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONHASHSEED": "0"},
    )
    report = json.loads(proc.stdout)
    sc = report["success_criteria"]
    assert sc["SC1_FLAT_replication_constraint"]["ok"] is True
    assert sc["SC2_price_axis"]["ok"] is True
    assert sc["SC3_shift_axis"]["ok"] is True
    assert report["verdicts"]["successor_price_axis"] == "ROBUST"
    assert report["verdicts"]["successor_distribution_shift_axis"] == "ROBUST"
    assert report["verdicts"]["original_allocator_price_axis"] == "BROKEN"
    assert report["verdicts"]["original_allocator_distribution_shift_axis"] == "BROKEN"

    successor_case_cells = (
        report["coverage"]["v1_case_regime_cells"]
        + report["coverage"]["expanded_case_regime_cells"]
        + report["coverage"]["b2_joint_mixes"] * len(report["regimes"])
    )

    # T4 empirical witnesses use only the frozen expanded 27-case panel.
    witnesses = []
    unique_regime_cells = 0
    for domain in report["expanded_set"]["domains"]:
        for case in domain["cases"]:
            unique = []
            for regime in report["regimes"]:
                name = regime["regime"]
                oracle = case["regimes"][name]["priced_oracle"]
                if oracle["optimal_subset_count"] == 1:
                    unique_regime_cells += 1
                    unique.append((name, tuple(oracle["materialized"])))
            distinct = sorted({subset for _, subset in unique})
            if len(distinct) >= 2:
                witnesses.append({
                    "domain": domain["domain"],
                    "case_id": case["case_id"],
                    "unique_optima": [
                        {"regime": name, "materialized": list(subset)}
                        for name, subset in unique
                    ],
                    "distinct_unique_optimum_count": len(distinct),
                })

    return {
        "successor_zero_regret_case_cells": successor_case_cells,
        "unique_oracle_regime_cells_expanded": unique_regime_cells,
        "price_oblivious_impossibility_witness_cases": len(witnesses),
        "witnesses": witnesses,
        "terminal": report["terminal"],
    }


def main():
    abstract = abstract_exhaustive()
    candidate_green = not abstract["candidate_failures"]
    mutants_green = all(abstract["mutant_witnesses"].values())
    nr13 = run_bound_nr13()

    terminal = (
        "P12_SELECTION_SUFFICIENCY_THEOREM_FALSIFIER_GREEN"
        if candidate_green and mutants_green
        else "P12_SELECTION_SUFFICIENCY_THEOREM_FALSIFIER_RED"
    )
    out = {
        "schema": "p12-selection-sufficiency-theorem-falsifier-v1",
        "study": "P12_SELECTION_SUFFICIENCY_THEOREM_V1",
        "abstract_reduced_state": abstract,
        "candidate_global_optimality_falsifier_green": candidate_green,
        "mutation_sensitivity_green": mutants_green,
        "bound_nr13_replay": nr13,
        "authority_boundary": (
            "Conditional on additive exact charge certificates and the nominal "
            "integer budget. No prospective-cost, external, or deployment authority."
        ),
        "terminal": terminal,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if terminal.endswith("_GREEN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
