#!/usr/bin/env python3
"""Independent falsifier for P12_CERTIFICATE_NECESSITY_THEOREM_V1.

Implements the frozen five-gate contract exactly. This checker does not
reimplement the candidate DP as its oracle: optimality is decided by direct
exhaustive subset enumeration. `price_aware_selection` is imported only as
the candidate under test (Gate G4), exactly as in the parent falsifier.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from p12_price_aware_allocator_v1 import price_aware_selection  # noqa: E402

COSTS = (1, 2, 3)
DELTAS = (-1, 0, 1, 2, 3, 4, 5)
PRICES = ((1, 1), (2, 1), (1, 2), (4, 1), (1, 4))
BUDGETS = tuple(range(7))
NS = (1, 2)


def item_value(cost: int, delta: int, prices: tuple[int, int]) -> int:
    p_build, p_serve = prices
    return p_serve * delta - p_build * cost


def exhaustive_oracle(items, prices, budget):
    """Return (best_value, optimal_subset_tuple_list) over feasible subsets."""
    best = None
    best_sets = []
    for mask in range(1 << len(items)):
        weight = 0
        value = 0
        selected = []
        for i, (cost, delta) in enumerate(items):
            if mask & (1 << i):
                weight += cost
                value += item_value(cost, delta, prices)
                selected.append(i)
        if weight > budget:
            continue
        if best is None or value > best:
            best = value
            best_sets = [tuple(selected)]
        elif value == best:
            best_sets.append(tuple(selected))
    assert best is not None
    return best, best_sets


def ledger_for(items):
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


# --- registered coarsening families (frozen in the theorem document) -------

def c0_identity(delta: int) -> int:
    return delta


def c1_sign_only(delta: int) -> str:
    if delta < 0:
        return "-"
    if delta == 0:
        return "0"
    return "+"


def c2a_interval_k2(delta: int) -> int:
    return 2 * (delta // 2)


def c2b_interval_k3(delta: int) -> int:
    return 3 * (delta // 3)


def c3a_threshold_theta1(delta: int) -> int:
    return 1 if delta >= 1 else 0


def c3b_threshold_theta2(delta: int) -> int:
    return 1 if delta >= 2 else 0


def c4_declared_cost_only(delta: int) -> str:
    del delta
    return "none"


FAMILIES = {
    "C0_identity": c0_identity,
    "C1_sign_only": c1_sign_only,
    "C2a_interval_k2": c2a_interval_k2,
    "C2b_interval_k3": c2b_interval_k3,
    "C3a_threshold_theta1": c3a_threshold_theta1,
    "C3b_threshold_theta2": c3b_threshold_theta2,
    "C4_declared_cost_only": c4_declared_cost_only,
}


def all_ledgers():
    option_space = tuple(itertools.product(COSTS, DELTAS))
    for n in NS:
        for items in itertools.product(option_space, repeat=n):
            yield n, items


def family_report(coarsen):
    """Gate G1/G2 enumeration for one family."""
    groups = {}
    ledgers_seen = 0
    cells = 0
    for n, items in all_ledgers():
        ledgers_seen += 1
        image = tuple(coarsen(delta) for _, delta in items)
        for prices in PRICES:
            for budget in BUDGETS:
                cells += 1
                key = (n, tuple(cost for cost, _ in items), prices, budget, image)
                groups.setdefault(key, []).append(items)

    oracle_cache = {}

    def oracle(items, prices, budget):
        ck = (items, prices, budget)
        if ck not in oracle_cache:
            oracle_cache[ck] = exhaustive_oracle(items, prices, budget)
        return oracle_cache[ck]

    witnesses = []
    pairs_checked = 0
    for key, members in groups.items():
        if len(members) < 2:
            continue
        n, _, prices, budget, _image = key
        for a, b in itertools.combinations(members, 2):
            pairs_checked += 1
            best_a, sets_a = oracle(a, prices, budget)
            best_b, sets_b = oracle(b, prices, budget)
            if len(sets_a) != 1 or len(sets_b) != 1:
                continue
            if sets_a[0] != sets_b[0]:
                witnesses.append({
                    "prices": list(prices),
                    "budget": budget,
                    "ledger_a": [list(x) for x in a],
                    "ledger_b": [list(x) for x in b],
                    "unique_optimum_a": [f"S{i}" for i in sets_a[0]],
                    "unique_optimum_b": [f"S{i}" for i in sets_b[0]],
                    "objective_a": best_a,
                    "objective_b": best_b,
                })

    delta_pairs_separated = set()
    for w in witnesses:
        deltas_a = [d for _, d in w["ledger_a"]]
        deltas_b = [d for _, d in w["ledger_b"]]
        for da, db in zip(deltas_a, deltas_b):
            if da != db:
                delta_pairs_separated.add(tuple(sorted((da, db))))

    minimal_n = None
    for w in witnesses:
        w_n = len(w["ledger_a"])
        if minimal_n is None or w_n < minimal_n:
            minimal_n = w_n

    return {
        "ledgers_enumerated": ledgers_seen,
        "cells_enumerated": cells,
        "groups": len(groups),
        "indistinguishable_pairs_checked": pairs_checked,
        "witness_pairs": len(witnesses),
        "minimal_witness_ledger_size": minimal_n,
        "delta_pairs_separated": sorted(list(p) for p in delta_pairs_separated),
        "first_witness": witnesses[0] if witnesses else None,
    }


def reconstruction_error_witness(coarsen, mode):
    """Gate G3: optimistic/pessimistic reconstruction must err somewhere.

    Reconstruction maps every observed cell back to the cell's max (optimistic)
    or min (pessimistic) reachable delta, then runs the exact parent DP on the
    reconstructed ledger. An error is a budget violation or a strict objective
    shortfall versus the exhaustive oracle on the TRUE ledger.
    """
    cell_members = {}
    for delta in DELTAS:
        cell_members.setdefault(coarsen(delta), []).append(delta)

    def reconstruct(delta):
        members = cell_members[coarsen(delta)]
        return max(members) if mode == "optimistic" else min(members)

    for n, items in all_ledgers():
        true_items = items
        recon_items = tuple((cost, reconstruct(delta)) for cost, delta in items)
        ledger = ledger_for(recon_items)
        for prices in PRICES:
            for budget in BUDGETS:
                oracle_value, _ = exhaustive_oracle(true_items, prices, budget)
                selected = price_aware_selection(ledger, prices, budget)
                weight = selected_weight(true_items, selected)
                value = selected_value(true_items, selected, prices)
                if weight > budget or value < oracle_value:
                    return {
                        "mode": mode,
                        "true_ledger": [list(x) for x in true_items],
                        "reconstructed_ledger": [list(x) for x in recon_items],
                        "prices": list(prices),
                        "budget": budget,
                        "selected": selected,
                        "weight": weight,
                        "objective": value,
                        "oracle_value": oracle_value,
                        "failure_mode": "budget" if weight > budget else "objective",
                    }
    return None


def sufficiency_recheck():
    """Gate G4: parent DP objective equals the exhaustive oracle everywhere."""
    cells = 0
    failures = []
    for n, items in all_ledgers():
        ledger = ledger_for(items)
        for prices in PRICES:
            for budget in BUDGETS:
                cells += 1
                oracle_value, _ = exhaustive_oracle(items, prices, budget)
                selected = price_aware_selection(ledger, prices, budget)
                weight = selected_weight(items, selected)
                value = selected_value(items, selected, prices)
                if weight > budget or value != oracle_value:
                    failures.append({
                        "items": [list(x) for x in items],
                        "prices": list(prices),
                        "budget": budget,
                        "selected": selected,
                        "weight": weight,
                        "value": value,
                        "oracle_value": oracle_value,
                    })
                    if len(failures) >= 5:
                        break
            if failures:
                break
        if failures:
            break
    return {"cells_checked": cells, "failures": failures}


def main():
    reports = {}
    for name, coarsen in FAMILIES.items():
        reports[name] = family_report(coarsen)

    mutants = {}
    for name in ("C1_sign_only", "C2a_interval_k2", "C2b_interval_k3",
                 "C3a_threshold_theta1", "C3b_threshold_theta2",
                 "C4_declared_cost_only"):
        coarsen = FAMILIES[name]
        mutants[name] = {
            "optimistic": reconstruction_error_witness(coarsen, "optimistic"),
            "pessimistic": reconstruction_error_witness(coarsen, "pessimistic"),
        }

    sufficiency = sufficiency_recheck()

    g1_green = reports["C0_identity"]["witness_pairs"] == 0
    coarsening_names = [n for n in FAMILIES if n != "C0_identity"]
    g2_green = all(reports[n]["witness_pairs"] >= 1 for n in coarsening_names)
    g3_green = all(
        mutants[n][mode] is not None
        for n in coarsening_names
        for mode in ("optimistic", "pessimistic")
    )
    g4_green = not sufficiency["failures"]
    expected_cells = sum(
        (len(COSTS) * len(DELTAS)) ** k for k in NS
    ) * len(PRICES) * len(BUDGETS)
    g5_green = all(
        reports[n]["ledgers_enumerated"] == sum((len(COSTS) * len(DELTAS)) ** k for k in NS)
        and reports[n]["cells_enumerated"] == expected_cells
        for n in FAMILIES
    )

    gates = {
        "G1_exact_field_control_zero_witnesses": g1_green,
        "G2_every_coarsening_has_witness": g2_green,
        "G3_reconstruction_mutants_err": g3_green,
        "G4_parent_dp_matches_oracle_everywhere": g4_green,
        "G5_enumeration_complete": g5_green,
    }
    terminal = (
        "P12_CERTIFICATE_NECESSITY_THEOREM_FALSIFIER_GREEN"
        if all(gates.values())
        else "P12_CERTIFICATE_NECESSITY_THEOREM_FALSIFIER_RED"
    )
    out = {
        "schema": "p12-certificate-necessity-theorem-falsifier-v1",
        "study": "P12_CERTIFICATE_NECESSITY_THEOREM_V1",
        "registered_state": {
            "ledger_sizes": list(NS),
            "costs": list(COSTS),
            "deltas": list(DELTAS),
            "prices": [list(p) for p in PRICES],
            "budgets": list(BUDGETS),
        },
        "family_reports": reports,
        "reconstruction_mutant_witnesses": mutants,
        "sufficiency_recheck": sufficiency,
        "gates": gates,
        "authority_boundary": (
            "Necessity is mechanized on the registered reduced state for the "
            "witness families; N1 is general. No prospective-cost, external, or "
            "deployment authority. Parent sufficiency authority inherited "
            "unchanged."
        ),
        "terminal": terminal,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if terminal.endswith("_GREEN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
