#!/usr/bin/env python3
"""MAX-R5D development-only exact 10-term controlled-cost matching on open N2.

This is a development discriminator after the R5B outer-control negative and R5C
controlled-cost repair. N2 is already open. The script cannot authorize R5/R6.

Frozen method:
- exact R5C per-edge controlled-CNOT auxiliary representation;
- exhaustive perfect matchings inside disjoint coefficient-local windows of 10;
- exact sparse global DP keyed by (direct-count delta, CNOT delta), retaining the
  minimum normalization delta for every key;
- final T must not worsen (equivalently direct-count delta >= 0);
- total normalization increase <= 1% of the controlled-cost adjacent incumbent.
"""
from __future__ import annotations

import json
from functools import lru_cache

import max_r5c_n2_controlled_cost_development as r5c
import max_r5b_n2_proof_outer_replay as r5b
import max_r5_n2_joint_internal_confirmation as r5v1

h = r5c.h
WINDOW = 10
NORM_FRAC = 0.01


def enumerate_matchings(items: tuple[int, ...]):
    if not items:
        yield tuple()
        return
    a = items[0]
    rest = items[1:]
    for pos, b in enumerate(rest):
        rem = rest[:pos] + rest[pos + 1 :]
        for tail in enumerate_matchings(rem):
            yield ((a, b),) + tail


@lru_cache(maxsize=500000)
def edge_by_index(i: int, j: int, terms_key: tuple):
    # terms_key is intentionally unused except to bind the cache to one immutable
    # sorted-term universe within the process.
    terms = _TERMS
    return r5c.edge(terms[i], terms[j])


_TERMS = []


def metrics_for_pairs(pairs):
    lam = 0.0
    cnot = t = direct = 0
    key = _TERMS_KEY
    for i, j in pairs:
        e = edge_by_index(min(i, j), max(i, j), key)
        lam += e["lambda"]
        cnot += e["CNOT"]
        t += e["T"]
        direct += e["direct"]
    return {"Lambda": float(lam), "CNOT": int(cnot), "T": int(t), "direct": int(direct)}


_TERMS_KEY = tuple()


def dominates(a, b):
    # Coordinates are deltas from the local adjacent baseline; lower is better
    # for all three here (dlambda, dT, dCNOT).
    return (
        a["dl"] <= b["dl"] + 1e-15
        and a["dT"] <= b["dT"]
        and a["dC"] <= b["dC"]
        and (
            a["dl"] < b["dl"] - 1e-15
            or a["dT"] < b["dT"]
            or a["dC"] < b["dC"]
        )
    )


def local_frontier(indices, baseline_pairs):
    base = metrics_for_pairs(baseline_pairs)
    raw = []
    count = 0
    for pairs in enumerate_matchings(tuple(indices)):
        count += 1
        m = metrics_for_pairs(pairs)
        raw.append({
            "pairs": pairs,
            "metrics": m,
            "dl": m["Lambda"] - base["Lambda"],
            "dC": m["CNOT"] - base["CNOT"],
            "dT": m["T"] - base["T"],
            "dD": m["direct"] - base["direct"],
        })
    # Exact local Pareto pruning. 945 candidates/window => quadratic is bounded.
    keep = []
    for i, a in enumerate(raw):
        if any(i != j and dominates(b, a) for j, b in enumerate(raw)):
            continue
        keep.append(a)
    keep.sort(key=lambda x: (x["dl"], x["dT"], x["dC"], x["pairs"]))
    return base, keep, count


def prune_same_direct(states):
    """Exact dominance prune at fixed direct delta.

    State map values are (minimum dlambda, choice tuple). For a fixed direct
    delta, a state with no larger CNOT delta and no larger dlambda dominates.
    Cross-direct pruning is intentionally omitted, so this cannot remove a state
    needed to satisfy final T/direct constraints.
    """
    by_d = {}
    for (dD, dC), (dl, choices) in states.items():
        by_d.setdefault(dD, []).append((dC, dl, choices))
    out = {}
    for dD, rows in by_d.items():
        rows.sort(key=lambda x: (x[0], x[1], x[2]))
        best_dl = float("inf")
        for dC, dl, choices in rows:
            if dl < best_dl - 1e-15:
                out[(dD, dC)] = (dl, choices)
                best_dl = dl
    return out


def main():
    global _TERMS, _TERMS_KEY
    text = h.fetch_source()
    one, two = h.parse_ducc(text)
    paulis, max_imag = h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    if len(terms) % 2:
        raise AssertionError("MAX-R5D currently requires an even N2 nonidentity term count")
    _TERMS = terms
    _TERMS_KEY = tuple((int(k[0]), int(k[1]), format(float(a), ".17g")) for k, a in terms)

    adjacent_pairs = [(i, i + 1) for i in range(0, len(terms), 2)]
    b1 = metrics_for_pairs(adjacent_pairs)
    _b1_again, b2 = r5c.compile_controlled(terms, NORM_FRAC)

    # Reconstruct B0 with the frozen R5B proof-carrying projection.
    singleton = None
    inc_v1, _suc_v1, inc_pairs_v1, _suc_pairs_v1 = r5v1.compile_bounded(terms, singleton, 0.01)
    b0_full = r5b.aggregate(terms, inc_pairs_v1)
    b0 = {
        "Lambda": b0_full["Lambda_joint"],
        "CNOT": b0_full["controlled_outer_standard_CliffordT_projection"]["CNOT"],
        "T": b0_full["controlled_outer_standard_CliffordT_projection"]["T"],
        "direct": b0_full["direct_unitary_blocks"],
    }

    windows = []
    exhaustive = 0
    for start in range(0, len(terms), WINDOW):
        idx = list(range(start, min(start + WINDOW, len(terms))))
        if len(idx) % 2:
            raise AssertionError({"odd_window": idx})
        base_pairs = [(idx[k], idx[k + 1]) for k in range(0, len(idx), 2)]
        base, frontier, count = local_frontier(idx, base_pairs)
        exhaustive += count
        windows.append({"indices": idx, "base": base, "frontier": frontier, "enumerated": count})

    # Suffix bounds keep the global exact sparse DP finite without scalarizing.
    suffix_min_dl = [0.0] * (len(windows) + 1)
    suffix_max_dD = [0] * (len(windows) + 1)
    for wi in range(len(windows) - 1, -1, -1):
        f = windows[wi]["frontier"]
        suffix_min_dl[wi] = suffix_min_dl[wi + 1] + min(x["dl"] for x in f)
        suffix_max_dD[wi] = suffix_max_dD[wi + 1] + max(x["dD"] for x in f)

    budget = NORM_FRAC * b1["Lambda"]
    # Key = (direct delta, CNOT delta); value = (minimum dlambda, local-option choices).
    states = {(0, 0): (0.0, tuple())}
    frontier_sizes = [1]
    for wi, w in enumerate(windows):
        nxt = {}
        for (dD0, dC0), (dl0, choices0) in states.items():
            for oi, opt in enumerate(w["frontier"]):
                dD = dD0 + opt["dD"]
                dC = dC0 + opt["dC"]
                dl = dl0 + opt["dl"]
                # Safe feasibility bounds from the unprocessed windows.
                if dl + suffix_min_dl[wi + 1] > budget + 1e-12:
                    continue
                if dD + suffix_max_dD[wi + 1] < 0:
                    continue
                key = (dD, dC)
                cand = (dl, choices0 + (oi,))
                old = nxt.get(key)
                if old is None or cand < old:
                    nxt[key] = cand
        states = prune_same_direct(nxt)
        frontier_sizes.append(len(states))
        if not states:
            raise AssertionError({"global_frontier_empty_after_window": wi})
        if len(states) > 2_000_000:
            raise RuntimeError({"exact_frontier_saturation": len(states), "window": wi})

    feasible = []
    for (dD, dC), (dl, choices) in states.items():
        if dD >= 0 and dl <= budget + 1e-12:
            feasible.append((dC, dl, -dD, choices, dD))
    if not feasible:
        raise AssertionError("no final T-nonworsening <=1% state")
    dC, dl, _neg_dD, choices, dD = min(feasible, key=lambda x: (x[0], x[1], x[2], x[3]))

    selected_pairs = []
    for wi, oi in enumerate(choices):
        selected_pairs.extend(windows[wi]["frontier"][oi]["pairs"])
    b3 = metrics_for_pairs(selected_pairs)

    # Bind additive reconstruction to the DP deltas.
    if b3["CNOT"] - b1["CNOT"] != dC:
        raise AssertionError("CNOT delta reconstruction mismatch")
    if b3["direct"] - b1["direct"] != dD:
        raise AssertionError("direct delta reconstruction mismatch")
    if abs((b3["Lambda"] - b1["Lambda"]) - dl) > 1e-10:
        raise AssertionError("Lambda delta reconstruction mismatch")
    if b3["T"] > b1["T"]:
        raise AssertionError("T non-compensatory gate violated")

    vs_b0 = 1.0 - b3["CNOT"] / b0["CNOT"]
    vs_b1 = 1.0 - b3["CNOT"] / b1["CNOT"]
    vs_b2 = 1.0 - b3["CNOT"] / b2["CNOT"]
    norm_over_b1 = b3["Lambda"] / b1["Lambda"] - 1.0
    gates = {
        "windows_exhaustive": exhaustive == sum(w["enumerated"] for w in windows),
        "T_nonworsening": b3["T"] <= b1["T"],
        "normalization_le_1pct": norm_over_b1 <= 0.0100000001,
        "strictly_better_than_B2": b3["CNOT"] < b2["CNOT"],
        "CNOT_reduction_vs_B0_ge_0p5pct": vs_b0 >= 0.005,
    }
    out = {
        "schema": "ORIONQ.MAXR5D.N2ControlledMultiwindowDevelopment.v1",
        "authority": "DEVELOPMENT_ONLY__N2_ALREADY_OPEN",
        "source_blob": h.SOURCE_BLOB,
        "window_size": WINDOW,
        "window_count": len(windows),
        "perfect_matchings_enumerated": exhaustive,
        "global_frontier_sizes": frontier_sizes,
        "B0_R5B_original_outer": b0,
        "B1_controlled_aux_adjacent": b1,
        "B2_controlled_quartet_1pct": b2,
        "B3_exact_10term_windows": b3,
        "B3_normalization_over_B1": norm_over_b1,
        "B3_CNOT_reduction_vs_B0": vs_b0,
        "B3_CNOT_reduction_vs_B1": vs_b1,
        "B3_CNOT_reduction_vs_B2": vs_b2,
        "B3_direct_delta_vs_B1": b3["direct"] - b1["direct"],
        "max_imag": max_imag,
        "gates": gates,
        "r5d_development_pass": all(gates.values()),
    }
    print("ORIONQ_MAX_R5D_DEV=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
