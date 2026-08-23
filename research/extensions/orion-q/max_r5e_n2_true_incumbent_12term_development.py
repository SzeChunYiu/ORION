#!/usr/bin/env python3
"""MAX-R5E corrected true-incumbent exact 12-term matching on open N2.

This supersedes the invalid first R5D pass. Every coordinate is bound to the
single jointly realizable R5C zero-slack quartet incumbent B*.
N2 is development-only here and cannot authorize R5/R6.
"""
from __future__ import annotations

import json
from functools import lru_cache

import max_r5c_n2_controlled_cost_development as r5c
import max_r5b_n2_proof_outer_replay as r5b
import max_r5_n2_joint_internal_confirmation as r5v1

h = r5c.h
WINDOW = 12
NORM_FRAC = 0.01
_TERMS = []
_TERMS_KEY = tuple()


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
def edge_by_index(i: int, j: int, universe_key: tuple):
    del universe_key
    return r5c.edge(_TERMS[i], _TERMS[j])


def metrics_for_pairs(pairs):
    out = {"Lambda": 0.0, "CNOT": 0, "T": 0, "direct": 0, "pairs": len(pairs)}
    for i, j in pairs:
        e = edge_by_index(min(i, j), max(i, j), _TERMS_KEY)
        out["Lambda"] += e["lambda"]
        out["CNOT"] += e["CNOT"]
        out["T"] += e["T"]
        out["direct"] += e["direct"]
    out["Lambda"] = float(out["Lambda"])
    return out


def quartet_incumbent_pairs(terms):
    pairs = []
    for s in range(0, len(terms), 4):
        idx = list(range(s, min(s + 4, len(terms))))
        patterns = r5c.pats(idx)
        opts = []
        for oi, ps in enumerate(patterns):
            m = metrics_for_pairs(ps)
            opts.append((m["Lambda"], m["T"], m["CNOT"], oi, tuple(ps)))
        _lam, _t, _c, _oi, chosen = min(opts)
        pairs.extend(chosen)
    return pairs


def frontier_2d(rows):
    """Exact frontier for fixed direct delta in (dC, dl), lower is better."""
    rows = sorted(rows, key=lambda x: (x["dC"], x["dl"], x["pairs"]))
    keep = []
    best_dl = float("inf")
    for r in rows:
        if r["dl"] < best_dl - 1e-15:
            keep.append(r)
            best_dl = r["dl"]
    return keep


def dominates(a, b):
    return (
        a["dD"] >= b["dD"]
        and a["dC"] <= b["dC"]
        and a["dl"] <= b["dl"] + 1e-15
        and (
            a["dD"] > b["dD"]
            or a["dC"] < b["dC"]
            or a["dl"] < b["dl"] - 1e-15
        )
    )


def local_frontier(indices, baseline_pairs):
    base = metrics_for_pairs(baseline_pairs)
    grouped = {}
    count = 0
    for pairs in enumerate_matchings(tuple(indices)):
        count += 1
        m = metrics_for_pairs(pairs)
        r = {
            "pairs": pairs,
            "metrics": m,
            "dl": m["Lambda"] - base["Lambda"],
            "dC": m["CNOT"] - base["CNOT"],
            "dD": m["direct"] - base["direct"],
        }
        grouped.setdefault(r["dD"], []).append(r)
    reduced = []
    for dD in sorted(grouped, reverse=True):
        reduced.extend(frontier_2d(grouped[dD]))
    keep = []
    # Pairwise only after exact per-direct 2D pruning; this set is small.
    for i, a in enumerate(reduced):
        if any(i != j and dominates(b, a) for j, b in enumerate(reduced)):
            continue
        keep.append(a)
    keep.sort(key=lambda x: (-x["dD"], x["dC"], x["dl"], x["pairs"]))
    return base, keep, count, len(reduced)


def prune_same_direct(states):
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
        raise AssertionError("N2 term count unexpectedly odd")
    _TERMS = terms
    _TERMS_KEY = tuple((int(k[0]), int(k[1]), format(float(a), ".17g")) for k, a in terms)

    # Reconstruct the actual R5C zero-slack quartet incumbent B* and bind it to
    # the original implementation's aggregate.
    bstar_pairs = quartet_incumbent_pairs(terms)
    bstar = metrics_for_pairs(bstar_pairs)
    r5c_base, r5c_zero = r5c.compile_controlled(terms, 0.0)
    bind = {
        "Lambda": abs(bstar["Lambda"] - r5c_base["Lambda"]) <= 1e-12,
        "CNOT": bstar["CNOT"] == r5c_base["CNOT"],
        "T": bstar["T"] == r5c_base["T"],
        "direct": bstar["direct"] == r5c_base["direct"],
        "zero_slack_base_consistent": r5c_zero["T"] <= r5c_base["T"] and r5c_zero["Lambda"] <= r5c_base["Lambda"] + 1e-12,
    }
    if not all(bind.values()):
        raise AssertionError({"true_incumbent_binding": bind, "reconstructed": bstar, "r5c_base": r5c_base, "r5c_zero": r5c_zero})

    _b2base, b2 = r5c.compile_controlled(terms, NORM_FRAC)

    # Original R5B proof-carrying outer incumbent for independent comparison.
    inc_v1, _suc_v1, inc_pairs_v1, _suc_pairs_v1 = r5v1.compile_bounded(terms, None, 0.01)
    b0_full = r5b.aggregate(terms, inc_pairs_v1)
    b0 = {
        "Lambda": b0_full["Lambda_joint"],
        "CNOT": b0_full["controlled_outer_standard_CliffordT_projection"]["CNOT"],
        "T": b0_full["controlled_outer_standard_CliffordT_projection"]["T"],
        "direct": b0_full["direct_unitary_blocks"],
    }

    # Baseline pair ownership by aligned 12-term window.
    windows = []
    exhaustive = 0
    pair_owner = {}
    for p in bstar_pairs:
        pair_owner[tuple(sorted(p))] = True
    for start in range(0, len(terms), WINDOW):
        end = min(start + WINDOW, len(terms))
        idx = list(range(start, end))
        if len(idx) % 2:
            raise AssertionError({"odd_window": idx})
        base_pairs = [p for p in bstar_pairs if start <= p[0] < end and start <= p[1] < end]
        if len(base_pairs) != len(idx) // 2:
            raise AssertionError({"baseline_pair_cut_by_window": [start, end], "pairs": base_pairs})
        base, frontier, count, reduced = local_frontier(idx, base_pairs)
        exhaustive += count
        windows.append({
            "start": start,
            "end": end,
            "base": base,
            "frontier": frontier,
            "enumerated": count,
            "post_2d_rows": reduced,
        })

    # The local baseline aggregates must reconstruct the same B*.
    local_base = {
        "Lambda": sum(w["base"]["Lambda"] for w in windows),
        "CNOT": sum(w["base"]["CNOT"] for w in windows),
        "T": sum(w["base"]["T"] for w in windows),
        "direct": sum(w["base"]["direct"] for w in windows),
    }
    if abs(local_base["Lambda"] - bstar["Lambda"]) > 1e-12 or any(local_base[k] != bstar[k] for k in ("CNOT", "T", "direct")):
        raise AssertionError({"window_baseline_reconstruction": local_base, "bstar": bstar})

    suffix_min_dl = [0.0] * (len(windows) + 1)
    suffix_max_dD = [0] * (len(windows) + 1)
    for wi in range(len(windows) - 1, -1, -1):
        f = windows[wi]["frontier"]
        suffix_min_dl[wi] = suffix_min_dl[wi + 1] + min(x["dl"] for x in f)
        suffix_max_dD[wi] = suffix_max_dD[wi + 1] + max(x["dD"] for x in f)

    budget = NORM_FRAC * bstar["Lambda"]
    states = {(0, 0): (0.0, tuple())}
    frontier_sizes = [1]
    for wi, w in enumerate(windows):
        nxt = {}
        for (dD0, dC0), (dl0, choices0) in states.items():
            for oi, opt in enumerate(w["frontier"]):
                dD = dD0 + opt["dD"]
                dC = dC0 + opt["dC"]
                dl = dl0 + opt["dl"]
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
        raise AssertionError("no final true-incumbent T-nonworsening <=1% state")
    dC, dl, _neg_dD, choices, dD = min(feasible, key=lambda x: (x[0], x[1], x[2], x[3]))

    selected_pairs = []
    for wi, oi in enumerate(choices):
        selected_pairs.extend(windows[wi]["frontier"][oi]["pairs"])
    e = metrics_for_pairs(selected_pairs)
    if e["CNOT"] - bstar["CNOT"] != dC:
        raise AssertionError("CNOT delta mismatch")
    if e["direct"] - bstar["direct"] != dD:
        raise AssertionError("direct delta mismatch")
    if abs((e["Lambda"] - bstar["Lambda"]) - dl) > 1e-10:
        raise AssertionError("Lambda delta mismatch")

    norm_over = e["Lambda"] / bstar["Lambda"] - 1.0
    vs_bstar = 1.0 - e["CNOT"] / bstar["CNOT"]
    vs_b0 = 1.0 - e["CNOT"] / b0["CNOT"]
    vs_b2 = 1.0 - e["CNOT"] / b2["CNOT"]
    gates = {
        "true_incumbent_binding": all(bind.values()),
        "full_windows_10395": all(w["enumerated"] == (10395 if w["end"] - w["start"] == 12 else 1) for w in windows),
        "T_nonworsening_vs_Bstar": e["T"] <= bstar["T"],
        "direct_nonworsening_vs_Bstar": e["direct"] >= bstar["direct"],
        "normalization_le_1pct_vs_Bstar": norm_over <= 0.0100000001,
        "strictly_better_than_B2_CNOT": e["CNOT"] < b2["CNOT"],
        "CNOT_reduction_vs_Bstar_ge_0p5pct": vs_bstar >= 0.005,
        "CNOT_reduction_vs_B0_ge_0p5pct": vs_b0 >= 0.005,
    }
    out = {
        "schema": "ORIONQ.MAXR5E.N2TrueIncumbent12TermDevelopment.v1",
        "authority": "DEVELOPMENT_ONLY__N2_ALREADY_OPEN",
        "source_blob": h.SOURCE_BLOB,
        "window_size": WINDOW,
        "window_count": len(windows),
        "perfect_matchings_enumerated": exhaustive,
        "local_frontier_sizes": [len(w["frontier"]) for w in windows],
        "global_frontier_sizes": frontier_sizes,
        "B0_R5B_original_outer": b0,
        "Bstar_R5C_true_quartet_incumbent": bstar,
        "Bstar_pair_list_sha256": r5b.sha([[int(i), int(j)] for i, j in bstar_pairs]),
        "B2_R5C_quartet_1pct": b2,
        "E_exact_12term": e,
        "E_pair_list_sha256": r5b.sha([[int(i), int(j)] for i, j in selected_pairs]),
        "E_normalization_over_Bstar": norm_over,
        "E_CNOT_reduction_vs_Bstar": vs_bstar,
        "E_CNOT_reduction_vs_B0": vs_b0,
        "E_CNOT_reduction_vs_B2": vs_b2,
        "E_direct_delta_vs_Bstar": e["direct"] - bstar["direct"],
        "max_imag": max_imag,
        "true_incumbent_binding": bind,
        "gates": gates,
        "r5e_development_pass": all(gates.values()),
    }
    print("ORIONQ_MAX_R5E_DEV=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
