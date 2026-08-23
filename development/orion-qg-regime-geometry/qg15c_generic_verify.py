#!/usr/bin/env python3
"""QG-15c generic verification — independent, pure-primitive.

Verifies research/extensions/orion-qg/QG15C_VOCABULARY_RESULTS.json. It imports
NOTHING from the QG-15c analyzer, nothing from qg15_third_family and nothing from
qg15b_predicate_language. All ground truth is rebuilt from the committed independent
primitive layer qg15_generic_verify (Paulis carried as (sign, letters) with the gate
conjugation tables derived numerically from the gate unitaries — no tableau rules
shared with the analyzer chain). On top of that layer this file re-derives, from
scratch:

  * the frozen GE donor SCHEDULE TRACE (per-step cost, events, pivot weight/sign,
    route, pre-step X-rank),
  * the frozen micro-step words for both routes and the E3 schedule ladder,
  * the tensor-factor restriction and its donor cost,
  * all 33 V2 features and all 13 V1 features,
  * the V1 and V2 cell tables, mixed-cell sets and error floors,
  * its own literal enumeration and a complete brute-force minimum-error search on
    a sub-lattice, with no R5/R6 reductions,
  * the seeded n=4 panel and its labels via its own Dijkstra referee.

Verifier scope is the protocol's section 8 scope in full, including the complete
brute-force minimum-error check on the sub-lattice {(1,1),(1,2),(1,3),(2,1)} (naive
enumeration of all unions/intersections over the verifier's own literal pool, with no
R5/R6 reductions and no pruning bounds).

Prints exactly one token line:
ORIONQG_QG15C_GENERIC_VERIFY={"decision":"ACCEPT"|"REJECT",...}
"""

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import qg15_generic_verify as gv  # noqa: E402  (committed independent primitive layer)

RESULTS = REPO / "research" / "extensions" / "orion-qg" / "QG15C_VOCABULARY_RESULTS.json"
QG15B_RESULTS = (REPO / "research" / "extensions" / "orion-qg"
                 / "QG15B_PREDICATE_LANGUAGE_RESULTS.json")
QG15_RESULTS = (REPO / "research" / "extensions" / "orion-qg"
                / "QG15_THIRD_FAMILY_RESULTS.json")
PROTOCOL = HERE / "QG15C_VOCABULARY_PROTOCOL_V1.md"
PANEL_SEED = 20260821
OPS = ("==", "<=", ">=")
SUBLATTICE = [(1, 1), (1, 2), (1, 3), (2, 1)]

V1_FEATURES = [
    "nCZ", "nY", "nSignX", "nSignZ", "nCN", "C_D", "r_X", "c", "LB",
    "C_D-LB", "n-c", "nCN-(n-1)", "C_D-2n",
]
V2_NEW_FEATURES = [
    "sched_cost_max", "sched_cost_argmax", "sched_cost_first", "sched_cost_last",
    "sched_cost_descents", "sched_cost_moment", "sched_steps_ge4",
    "sched_steps_zero", "sched_events_max", "sched_steps_Y_and_sign",
    "sched_steps_Y_only", "sched_steps_sign_only", "sched_pivot_sign_count",
    "sched_pivot_wt_max", "sched_route_Z", "sched_rank_drops",
    "fac_size_max", "fac_cost_max", "C_E3", "C_D-C_E3",
]
V2_FEATURES = V1_FEATURES + V2_NEW_FEATURES


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def note(msg):
    print(f"[qg15c-verify] {msg}", file=sys.stderr)


# ------------------------------------------------------------- Pauli accessors
def xm(p, n):
    return sum(1 << j for j in range(n) if p[1][j] in (1, 2))


def zm(p, n):
    return sum(1 << j for j in range(n) if p[1][j] in (2, 3))


def pkey(p, n):
    return (xm(p, n), zm(p, n), p[0])


def rank_f2(vals):
    basis = []
    for v in vals:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def r_x(st, n):
    return rank_f2([xm(p, n) for p in st])


# ---------------------------------------------- frozen micro-steps (rebuilt)
EV0 = ("nCZ", "nY", "nSignX", "nSignZ", "nCN")


def micro_steps(st, pivot, q, route, processed, n):
    st = list(st)
    pv = pivot
    gates = []
    ev = {k: 0 for k in EV0}

    def emit(g):
        nonlocal st, pv
        st = [gv.conj_pauli(g, p) for p in st]
        pv = gv.conj_pauli(g, pv)
        gates.append(g)

    if route == "X":
        assert pv[1][q] in (1, 2)
        if pv[1][q] == 2:
            emit(("S", q))
            ev["nY"] += 1
        for j in range(n):
            if j == q or (processed >> j) & 1:
                continue
            if pv[1][j] == 2:
                emit(("S", j))
                ev["nY"] += 1
            if pv[1][j] == 1:
                emit(("CX", q, j))
                ev["nCN"] += 1
            elif pv[1][j] == 3:
                emit(("H", j))
                emit(("CX", q, j))
                emit(("H", j))
                ev["nCZ"] += 1
                ev["nCN"] += 1
        assert pv[1][q] == 1 and all(pv[1][j] == 0 for j in range(n) if j != q)
        if pv[0]:
            emit(("S", q))
            emit(("S", q))
            ev["nSignX"] += 1
        emit(("H", q))
    else:
        assert pv[1][q] in (2, 3)
        if pv[1][q] == 2:
            emit(("S", q))
            emit(("H", q))
            ev["nY"] += 1
        for j in range(n):
            if j == q or (processed >> j) & 1:
                continue
            if pv[1][j] == 2:
                emit(("S", j))
                emit(("H", j))
                emit(("CX", j, q))
                ev["nY"] += 1
                ev["nCN"] += 1
            elif pv[1][j] == 1:
                emit(("H", j))
                emit(("CX", j, q))
                emit(("H", j))
                ev["nCZ"] += 1
                ev["nCN"] += 1
            elif pv[1][j] == 3:
                emit(("CX", j, q))
                ev["nCN"] += 1
        assert pv[1][q] == 3 and all(pv[1][j] == 0 for j in range(n) if j != q)
        if pv[0]:
            emit(("H", q))
            emit(("S", q))
            emit(("S", q))
            emit(("H", q))
            ev["nSignZ"] += 1
    assert pv == (0, tuple(3 if j == q else 0 for j in range(n)))
    return gates, st, ev


def cost_of(gates):
    return sum(gv.COST[g[0]] for g in gates)


def x_cands(st, q, processed, n):
    out = [p for p in st if p[1][q] in (1, 2)
           and not (xm(p, n) & processed) and not (zm(p, n) & processed)]
    return sorted(out, key=lambda p: pkey(p, n))


def z_cands(st, q, processed, n):
    out = [p for p in st if p[1][q] in (2, 3)
           and not (xm(p, n) & processed) and not (zm(p, n) & processed)]
    return sorted(out, key=lambda p: pkey(p, n))


def plus_z(q, n):
    return (0, tuple(3 if j == q else 0 for j in range(n)))


def minus_z(q, n):
    return (1, tuple(3 if j == q else 0 for j in range(n)))


def donor_schedule(state, n):
    """Frozen GE donor replay with the per-step trace (protocol 3.1)."""
    st = list(state)
    processed = 0
    steps = []
    all_ev = {k: 0 for k in EV0}
    total = 0
    for q in range(n):
        rho = r_x(st, n)
        cands = x_cands(st, q, processed, n)
        if cands:
            pv = cands[0]
            gates, st, ev = micro_steps(st, pv, q, "X", processed, n)
            route = "X"
        elif minus_z(q, n) in st:
            pv = minus_z(q, n)
            gates, st, ev = micro_steps(st, pv, q, "Z", processed, n)
            route = "Z"
        else:
            assert plus_z(q, n) in st
            pv, gates, ev, route = plus_z(q, n), [], {k: 0 for k in EV0}, "N"
        c = cost_of(gates)
        total += c
        for k in EV0:
            all_ev[k] += ev[k]
        steps.append({
            "cost": c,
            "ev": ev,
            "wt": sum(1 for j in range(n) if pv[1][j] != 0),
            "sign": pv[0],
            "route": route,
            "rho": rho,
        })
        processed |= 1 << q
    assert tuple(sorted(st)) == gv.start(n)
    return steps, total, all_ev


def ladder_e3(state, n):
    """Order-free + pivot-free + route-free donor-family minimum (QG-15 E3)."""
    full = (1 << n) - 1
    memo = {}

    def rec(st, rem):
        mk = (st, rem)
        hit = memo.get(mk)
        if hit is not None:
            return hit
        if rem == 0:
            memo[mk] = 0
            return 0
        processed = full ^ rem
        best = None
        stl = list(st)
        for q in range(n):
            if not (rem >> q) & 1:
                continue
            branches = []
            xc = x_cands(stl, q, processed, n)
            if xc:
                for p in xc:
                    branches.append(("X", p))
            else:
                forced = minus_z(q, n) if minus_z(q, n) in st else plus_z(q, n)
                branches.append(("Z", forced))
            for p in z_cands(stl, q, processed, n):
                if ("Z", p) not in branches:
                    branches.append(("Z", p))
            for route, pv in branches:
                gates, nst, _ev = micro_steps(stl, pv, q, route, processed, n)
                cand = cost_of(gates) + rec(tuple(sorted(nst)), rem ^ (1 << q))
                if best is None or cand < best:
                    best = cand
        memo[mk] = best
        return best

    return rec(tuple(state), full)


def tensor_parts(state, n):
    full = (1 << n) - 1
    cuts = []
    for sub in range(1, full):
        ca = sum(1 for p in state if ((xm(p, n) | zm(p, n)) & ~sub & full) == 0)
        cb = sum(1 for p in state if ((xm(p, n) | zm(p, n)) & sub) == 0)
        if (ca.bit_length() - 1) + (cb.bit_length() - 1) == n:
            cuts.append(sub)
    parts = [full]
    for cut in cuts:
        nxt = []
        for pt in parts:
            a, b = pt & cut, pt & ~cut & full
            if a:
                nxt.append(a)
            if b:
                nxt.append(b)
        parts = nxt
    return parts


def restrict(state, part, n):
    qs = [j for j in range(n) if (part >> j) & 1]
    m = len(qs)
    full = (1 << n) - 1
    sub = set()
    for p in state:
        if ((xm(p, n) | zm(p, n)) & ~part & full) != 0:
            continue
        sub.add((p[0], tuple(p[1][j] for j in qs)))
    sub = tuple(sorted(sub))
    assert len(sub) == 1 << m
    return sub, m


def features(state, n):
    prep, cd, feats = gv.donor(state, n)
    assert gv.apply_circuit(gv.start(n), prep) == state
    lb, rx, c = gv.structure(state, n)
    v1 = (feats["nCZ"], feats["nY"], feats["nSignX"], feats["nSignZ"], feats["nCN"],
          cd, rx, c, lb, cd - lb, n - c, feats["nCN"] - (n - 1), cd - 2 * n)

    steps, total, agg = donor_schedule(state, n)
    assert total == cd and agg == feats
    costs = [s["cost"] for s in steps]
    cmax = max(costs)
    y = [s["ev"]["nY"] for s in steps]
    sg = [s["ev"]["nSignX"] + s["ev"]["nSignZ"] for s in steps]
    evtot = [sum(s["ev"].values()) for s in steps]
    rho = [s["rho"] for s in steps] + [0]
    parts = tensor_parts(state, n)
    fsize = fcost = 0
    for pt in parts:
        sub, m = restrict(state, pt, n)
        fsize = max(fsize, m)
        fcost = max(fcost, gv.donor(sub, m)[1])
    ce3 = ladder_e3(state, n)
    v2 = v1 + (
        cmax,
        costs.index(cmax),
        costs[0],
        costs[n - 1],
        sum(1 for q in range(n - 1) if costs[q] > costs[q + 1]),
        sum(q * costs[q] for q in range(n)),
        sum(1 for x in costs if x >= 4),
        sum(1 for x in costs if x == 0),
        max(evtot),
        sum(1 for q in range(n) if y[q] >= 1 and sg[q] >= 1),
        sum(1 for q in range(n) if y[q] >= 1 and sg[q] == 0),
        sum(1 for q in range(n) if y[q] == 0 and sg[q] >= 1),
        sum(s["sign"] for s in steps),
        max(s["wt"] for s in steps),
        sum(1 for s in steps if s["route"] == "Z"),
        sum(1 for q in range(n) if rho[q] > rho[q + 1]),
        fsize,
        fcost,
        ce3,
        cd - ce3,
    )
    assert len(v2) == 33
    return v1, v2, cd, lb, tuple(costs)


# --------------------------------------------------------------- table / search
def build_cells(rows, idx):
    counts = {}
    for r in rows:
        cell = counts.setdefault(r[idx], [0, 0])
        cell[0 if r[2] else 1] += 1
    cells = sorted(counts)
    pos = [counts[v][0] for v in cells]
    neg = [counts[v][1] for v in cells]
    mixed = [i for i, (p, q) in enumerate(zip(pos, neg)) if p > 0 and q > 0]
    floor = sum(min(p, q) for p, q in zip(pos, neg))
    return cells, pos, neg, mixed, floor


def literal_masks(cells, nfeat):
    ncell = len(cells)
    full = (1 << ncell) - 1
    grids = [sorted({v[fi] for v in cells}) for fi in range(nfeat)]
    seen = set()
    pool = []
    for fi in range(nfeat):
        col = [v[fi] for v in cells]
        for t in grids[fi]:
            for op in OPS:
                for neg in (False, True):
                    m = 0
                    for i, x in enumerate(col):
                        hit = (x == t) if op == "==" else (
                            (x <= t) if op == "<=" else (x >= t))
                        if hit != neg:
                            m |= 1 << i
                    if m == 0 or m == full:
                        continue
                    if m in seen:
                        continue
                    seen.add(m)
                    pool.append(m)
    return pool, grids


def scorer(pos, neg):
    groups = {}
    for i, (p, q) in enumerate(zip(pos, neg)):
        d = q - p
        if d:
            groups.setdefault(d, 0)
            groups[d] |= 1 << i
    items = sorted(groups.items())

    def score(mask):
        return sum(d * (mask & m).bit_count() for d, m in items)

    return score


def brute_sublattice(cells, pos, neg, masks):
    P = sum(pos)
    N = sum(neg)
    full = (1 << len(cells)) - 1
    score = scorer(pos, neg)
    out = {}
    singles = [(score(m), m) for m in masks]
    base = min(0, N - P)                      # CONST_FALSE / CONST_TRUE
    out[(1, 1)] = P + min([base] + [s for s, _ in singles])
    best2 = base
    for a in range(len(masks)):
        ma = masks[a]
        sa = singles[a][0]
        if sa < best2:
            best2 = sa
        for b in range(a + 1, len(masks)):
            s = score(ma | masks[b])
            if s < best2:
                best2 = s
    out[(1, 2)] = P + best2
    best3 = best2
    for a in range(len(masks)):
        ma = masks[a]
        for b in range(a + 1, len(masks)):
            u = ma | masks[b]
            for c in range(b + 1, len(masks)):
                s = score(u | masks[c])
                if s < best3:
                    best3 = s
    out[(1, 3)] = P + best3
    bestk2 = base
    for s, _ in singles:
        if s < bestk2:
            bestk2 = s
    for a in range(len(masks)):
        ma = masks[a]
        for b in range(a + 1, len(masks)):
            v = ma & masks[b]
            if v == 0 or v == full:
                continue
            s = score(v)
            if s < bestk2:
                bestk2 = s
    out[(2, 1)] = P + bestk2
    return out


def eval_predicate(witness, names, vec):
    if "constant" in witness:
        return witness["constant"]
    idx = {nm: i for i, nm in enumerate(names)}
    for conj in witness["conjunctions"]:
        ok = True
        for lit in conj:
            x = vec[idx[lit["feature"]]]
            t, op = lit["threshold"], lit["op"]
            hit = (x == t) if op == "==" else ((x <= t) if op == "<=" else (x >= t))
            if hit == lit["negated"]:
                ok = False
                break
        if ok:
            return True
    return False


def confusion(flags, labels):
    tp = fp = fn = tn = 0
    for p, l in zip(flags, labels):
        if p and l:
            tp += 1
        elif p and not l:
            fp += 1
        elif not p and l:
            fn += 1
        else:
            tn += 1
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "errors": fp + fn}


def baseline(v1, name):
    if name == "P0":
        return v1[0] == 0
    if name == "P1":
        return v1[0] == 0 and v1[2] == 0 and v1[3] == 0
    if name == "P2":
        return v1[9] == 0
    if name == "selected":
        return v1[12] <= 0
    raise AssertionError(name)


# ------------------------------------------------------------------------ main
def main() -> int:
    raw = json.loads(RESULTS.read_text())
    b15 = json.loads(QG15B_RESULTS.read_text())
    r15 = json.loads(QG15_RESULTS.read_text())
    checks = {}
    checks["schema"] = raw.get("schema") == "orion-qg.qg15c_vocabulary.v1"
    checks["protocol_sha256"] = raw.get("protocol_sha256") == hashlib.sha256(
        PROTOCOL.read_bytes()).hexdigest()
    unsigned = {k: v for k, v in raw.items() if k not in ("result_digest", "timing")}
    checks["result_digest"] = raw.get("result_digest") == hashlib.sha256(
        canonical(unsigned).encode()).hexdigest()
    checks["upstream_receipt_hashes"] = (
        raw["qg15_results_sha256"] == hashlib.sha256(QG15_RESULTS.read_bytes()).hexdigest()
        and raw["qg15b_results_sha256"] == hashlib.sha256(
            QG15B_RESULTS.read_bytes()).hexdigest())
    checks["vocabulary_frozen_list"] = (
        raw["vocabulary"]["V2_features"] == V2_FEATURES
        and raw["vocabulary"]["V1_features"] == V1_FEATURES
        and V2_FEATURES[:13] == V1_FEATURES)

    # ---------------- rebuild n<=3 ground truth and both feature tables
    note("rebuilding referee + donor + schedule trace + V2 features for n<=3")
    rows = []
    censuses = {}
    for n in (1, 2, 3):
        dist = gv.referee(n)
        exact = 0
        for state in sorted(dist, key=lambda s: gv.state_key(s, n)):
            v1, v2, cd, lb, costs = features(state, n)
            copt = dist[state]
            assert lb <= copt <= cd
            lab = copt == cd
            exact += lab
            rows.append((v1, v2, lab, n, gv.state_key(state, n), cd, copt, costs, state))
        censuses[n] = exact
    checks["training_rows"] = len(rows) == 1146 == raw["bindings"]["training_rows"]
    checks["donor_censuses"] = all(
        censuses[n] == raw["bindings"]["qg15_donor_censuses"][f"n{n}"]
        == r15["component1_regime_map"]["per_n"][f"n{n}"]["donor_exact"]
        for n in (1, 2, 3))

    # QG-15 baseline confusions on n=1,2,3
    key_map = {1: "n1", 2: "n2", 3: "n3_fit"}
    ok = True
    for n in (1, 2, 3):
        sub = [r for r in rows if r[3] == n]
        labs = [r[2] for r in sub]
        for name in ("P0", "P1", "P2", "selected"):
            got = confusion([baseline(r[0], name) for r in sub], labs)
            ok &= got == r15["component4_predicate"]["confusion_matrices"][
                key_map[n]][name]
    checks["qg15_baseline_confusions"] = ok

    # ---------------- V1 cell table binds QG-15b verbatim
    v1c, v1p, v1n, v1m, v1f = build_cells(rows, 0)
    cb = b15["stabprep"]["cell_table"]
    stored = sorted(canonical(x) for x in cb["mixed_cells_verbatim_capped"])
    rebuilt = sorted(canonical({"feature_vector": dict(zip(V1_FEATURES, v1c[i])),
                                "pos": v1p[i], "neg": v1n[i]}) for i in v1m)
    checks["v1_cell_table_binds_qg15b"] = (
        len(v1c) == cb["cells"] == raw["bindings"]["qg15b_v1_cells"]
        and len(v1m) == cb["mixed_cells"] == 12
        and v1f == cb["E_floor"] == 43 == raw["bindings"]["qg15b_v1_E_floor"]
        and stored == rebuilt)

    # ---------------- Q1 diagnosis records
    q1 = raw["q1_collision_diagnosis"]
    by_v1 = {}
    for r in rows:
        by_v1.setdefault(r[0], []).append(r)
    ok = True
    for rec in q1["cells_verbatim"]:
        vec = tuple(rec["feature_vector"][f] for f in V1_FEATURES)
        members = sorted(by_v1[vec], key=lambda r: (r[3], r[4]))
        pm = [r for r in members if r[2]]
        nm = [r for r in members if not r[2]]
        ok &= rec["pos"] == len(pm) and rec["neg"] == len(nm)
        pair = rec["minimal_distinguishing_pair"]
        ok &= pair["donor_exact_member"]["canonical_key"] == list(pm[0][4])
        ok &= pair["trade_member"]["canonical_key"] == list(nm[0][4])
        ok &= pair["donor_exact_member"]["donor_step_cost_profile"] == list(pm[0][7])
        ok &= pair["trade_member"]["donor_step_cost_profile"] == list(nm[0][7])
        ok &= pair["trade_gap_C_D_minus_C_opt"] == nm[0][5] - nm[0][6]
    checks["q1_diagnosis_records"] = ok and len(q1["cells_verbatim"]) == 12
    checks["q1_all_pairs_differ_in_profile"] = (
        q1["summary"]["all_pairs_differ_in_step_cost_profile"] is True
        and all(rec["minimal_distinguishing_pair"]["donor_exact_member"][
            "donor_step_cost_profile"]
            != rec["minimal_distinguishing_pair"]["trade_member"][
                "donor_step_cost_profile"] for rec in q1["cells_verbatim"]))

    # ---------------- V2 cell table, floor, surviving collisions
    v2c, v2p, v2n, v2m, v2f = build_cells(rows, 1)
    ct = raw["v2_cell_table"]
    checks["v2_cell_table"] = (
        len(v2c) == ct["cells"] and sum(v2p) == ct["P_total"]
        and sum(v2n) == ct["N_total"] and len(v2m) == ct["mixed_cells"]
        and v2f == ct["E_floor"])
    checks["v2_floor_at_most_v1_floor"] = v2f <= v1f
    by_v2 = {}
    for r in rows:
        by_v2.setdefault(r[1], []).append(r)
    surv = raw["surviving_collisions"]
    ok = surv["count"] == len(v2m) and surv["E_floor"] == v2f
    for rec in surv["cells_verbatim_capped"]:
        vec = tuple(rec["feature_vector"][f] for f in V2_FEATURES)
        ok &= vec in by_v2
        members = sorted(by_v2.get(vec, []), key=lambda r: (r[3], r[4]))
        pm = [r for r in members if r[2]]
        nm = [r for r in members if not r[2]]
        ok &= bool(pm) and bool(nm)
        ok &= rec["pos"] == len(pm) and rec["neg"] == len(nm)
        pair = rec["minimal_distinguishing_pair"]
        ok &= pair["donor_exact_member"]["canonical_key"] == list(pm[0][4])
        ok &= pair["trade_member"]["canonical_key"] == list(nm[0][4])
        ok &= pair["trade_member"]["C_opt"] == nm[0][6]
        ok &= pair["donor_exact_member"]["C_opt"] == pm[0][6] == pm[0][5]
    checks["surviving_collision_records"] = ok

    # ---------------- literals and complete brute force on the sub-lattice
    note("independent literal enumeration + brute-force sub-lattice")
    masks, _grids = literal_masks(v2c, len(V2_FEATURES))
    checks["literal_pool_size"] = (
        len(masks) == raw["search"]["literal_stats"]["pool_literals"])
    brute = brute_sublattice(v2c, v2p, v2n, masks)
    ok = True
    for (K, D) in SUBLATTICE:
        rec = raw["search"]["minerr_surface"][f"K{K}_D{D}"]
        ok &= (not rec["truncated"]) and rec["minerr"] == brute[(K, D)]
    checks["sublattice_minimality"] = ok

    # ---------------- witness re-evaluation over the whole surface
    train = [(r[1], r[2]) for r in rows]
    ok = True
    for name, rec in sorted(raw["search"]["minerr_surface"].items()):
        flags = [eval_predicate(rec["witness"], V2_FEATURES, v) for v, _ in train]
        err = sum(1 for f, (_, lab) in zip(flags, train) if f != lab)
        ok &= err == rec["minerr"] and rec["minerr"] >= v2f
    checks["witness_reevaluation_and_floor"] = ok
    ok = True
    for (K, D), rec in ((tuple(int(x) for x in k[1:].split("_D")), v)
                        for k, v in raw["search"]["minerr_surface"].items()):
        if rec["truncated"]:
            continue
        for (K2, D2), rec2 in ((tuple(int(x) for x in k[1:].split("_D")), v)
                               for k, v in raw["search"]["minerr_surface"].items()):
            if rec2["truncated"] or not (K2 >= K and D2 >= D):
                continue
            ok &= rec2["minerr"] <= rec["minerr"]
    checks["surface_monotonicity"] = ok

    # ---------------- stage digest reconstruction
    stage_obj = {
        "v1_cells": len(v1c), "v1_mixed": len(v1m), "v1_floor": v1f,
        "v2_cells": len(v2c), "v2_mixed": len(v2m), "v2_floor": v2f,
        "surface": raw["search"]["minerr_surface"],
        "zero_error_cells": raw["search"]["zero_error_cells"],
        "floor_attainment_cells": raw["search"]["floor_attainment_cells"],
        "headline_cell": raw["search"]["headline_cell"],
        "headline_witness": raw["search"]["headline_witness"],
        "terminal": raw["terminal"],
        "lattice_note": raw["search"]["lattice_note"],
        "v2_features": V2_FEATURES,
    }
    checks["stage_digest"] = raw["stage_digest"] == hashlib.sha256(
        canonical(stage_obj).encode()).hexdigest()

    # ---------------- terminal consistency
    if v2f == 0 and len(v2m) == 0:
        want = "QG15C_FEATURE_DETERMINATION_RESTORED"
    else:
        want = "QG15C_FLOOR_PERSISTS__COLLISIONS_CHARACTERIZED"
    checks["terminal_matches_cell_table"] = raw["terminal"] == want
    checks["authority_ceiling"] = (
        raw["authority"].endswith("__NOT_R6")
        and raw["r6_authority"] is False and raw["novelty_credit"] is False
        and raw["network_access"] is False
        and raw["reserved_stretched_n2_accessed"] is False)

    # ---------------- held-out panel: independent regeneration + labels
    note("regenerating the seeded n=4 panel and labelling with an independent referee")
    rng = np.random.default_rng(PANEL_SEED)
    panel = []
    seen = set()
    while len(panel) < 120:
        s = gv.start(4)
        for _ in range(24):
            kind = int(rng.integers(0, 4))
            if kind == 3:
                cq = int(rng.integers(0, 4))
                u = int(rng.integers(0, 3))
                t = [x for x in range(4) if x != cq][u]
                g = ("CX", cq, t)
            else:
                g = (["H", "S", "SDG"][kind], int(rng.integers(0, 4)))
            s = gv.apply_gate(s, g)
        if s not in seen:
            seen.add(s)
            panel.append(s)
    pfeat = [features(s, 4) for s in panel]
    d4 = gv.referee(4)
    checks["n4_state_space"] = len(d4) == gv.expected_count(4)
    prows = []
    for s, (v1, v2, cd, lb, costs) in zip(panel, pfeat):
        copt = d4[s]
        assert lb <= copt <= cd
        prows.append((v1, v2, copt == cd))
    labs4 = [r[2] for r in prows]
    checks["panel_positives"] = sum(labs4) == raw["heldout"]["panel_positives"]
    ok = True
    for name in ("P0", "P1", "P2", "selected"):
        got = confusion([baseline(r[0], name) for r in prows], labs4)
        ok &= got == r15["component4_predicate"]["confusion_matrices"][
            "n4_panel_heldout"][name]
    checks["panel_qg15_baselines"] = ok

    purity = {v2c[i]: (v2n[i] == 0) for i in range(len(v2c))}
    h1_flags = [purity.get(r[1], False) for r in prows]
    h1 = raw["heldout"]["H1_cell_lookup"]
    checks["heldout_H1"] = (
        confusion(h1_flags, labs4) == h1["confusion"]
        and sum(1 for r in prows if r[1] not in purity) == h1["unseen_cells"])
    h2 = raw["heldout"]["H2_lattice_predicate"]
    h2_flags = [eval_predicate(h2["witness"], V2_FEATURES, r[1]) for r in prows]
    checks["heldout_H2"] = confusion(h2_flags, labs4) == h2["confusion"]
    _pc, _pp, _pn, pm4, pf4 = build_cells([(r[0], r[1], r[2]) for r in prows], 1)
    checks["panel_internal_cells"] = (
        len(pm4) == raw["heldout"]["panel_internal_V2_mixed_cells"]
        and pf4 == raw["heldout"]["panel_internal_V2_floor"])
    checks["gates_all_true"] = all(raw["gates"].values())

    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    print("ORIONQG_QG15C_GENERIC_VERIFY=" + canonical({
        "decision": decision,
        "checks": checks,
        "rebuilt": {
            "training_rows": len(rows),
            "V1_cells": len(v1c), "V1_mixed": len(v1m), "V1_E_floor": v1f,
            "V2_cells": len(v2c), "V2_mixed": len(v2m), "V2_E_floor": v2f,
            "literal_pool": len(masks),
            "sublattice_minerr": {f"K{k}_D{d}": v for (k, d), v in sorted(brute.items())},
            "panel_positives": sum(labs4),
        },
        "verifier_scope": (
            "protocol s.8 in full; sub-lattice brute force over {(1,1),(1,2),(1,3),"
            "(2,1)} by naive enumeration, no R5/R6 reductions, no pruning bounds"),
    }))
    return 0 if decision == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
import hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; QG=ROOT/'research/extensions/orion-qg'; sys.path.insert(0,str(QG))
import qg15_third_family as q15  # noqa:E402
RESULT=ROOT/'artifacts/orion-qg-qg15c-enlarged-vocab.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG15C_ENLARGED_VOCAB_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg15c-generic.json'; TOKEN='ORIONQG_QG15C_GENERIC='; K=('H','S','SDG','CX'); KC={x:i for i,x in enumerate(K)}
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def stat(a): return min(a),max(a),sum(x*x for x in a),sum(x==0 for x in a)
def vec(state,n,dist):
 prep,cd,f,path=q15.donor(state,n); lb,rx,c=q15.lower_bound(state,n); b=[f['nCZ'],f['nY'],f['nSignX'],f['nSignZ'],f['nCN'],cd,rx,c,lb,cd-lb,n-c,f['nCN']-(n-1),cd-2*n]; tot=Counter(); loads={x:[0]*n for x in ('H','S','SDG','IN','OUT')}; edges=Counter(); kinds=[]
 for g in path:
  kind=g[0]; tot[kind]+=1; kinds.append(kind)
  if kind=='CX': edges[(g[1],g[2])]+=1; loads['OUT'][g[1]]+=1; loads['IN'][g[2]]+=1
  else: loads[kind][g[1]]+=1
 b += [tot[x] for x in K]
 for x in ('H','S','SDG','IN','OUT'): b += list(stat(loads[x]))
 indeg=[sum(edges[(c,t)]>0 for c in range(n) if c!=t) for t in range(n)]; outdeg=[sum(edges[(c,t)]>0 for t in range(n) if t!=c) for c in range(n)]; b += [len(edges),max(edges.values()) if edges else 0,sum(v*v for v in edges.values()),sum(edges[(a,z)]>0 and edges[(z,a)]>0 for a in range(n) for z in range(a+1,n)),max(indeg) if indeg else 0,max(outdeg) if outdeg else 0,sum(x*x for x in indeg),sum(x*x for x in outdeg)]
 tr=Counter((KC[a],KC[z]) for a,z in zip(kinds,kinds[1:])); b += [tr[(a,z)] for a in range(4) for z in range(4)]
 if kinds:
  runs=[]; cur=kinds[0]; size=1
  for x in kinds[1:]:
   if x==cur: size+=1
   else: runs.append(size); cur=x; size=1
  runs.append(size); b += [KC[kinds[0]],KC[kinds[-1]],len(runs),max(runs),len(set(kinds))]
 else: b += [4,4,0,0,0]
 return tuple(int(x) for x in b), dist[state]==cd

def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None); cells=defaultdict(lambda:[0,0]); per={}
 for n in (1,2,3):
  dist=q15.referee(n); exact=0
  for s in sorted(dist):
   v,l=vec(s,n,dist); cells[v][0 if l else 1]+=1; exact+=int(l)
  per[str(n)]={'instances':len(dist),'donor_exact':exact}
 mixed=[(v,p,n) for v,(p,n) in cells.items() if p and n]; floor=sum(min(p,n) for _v,p,n in mixed)
 per_n_match=all(per[k]['instances']==a['domain'][k]['instances'] and per[k]['donor_exact']==a['domain'][k]['donor_exact'] for k in per)
 checks={'schema':a.get('schema')=='ORION.QG.QG15C.EnlargedVocabulary.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'feature_count':all(len(v)==a.get('feature_count') for v in cells),'training_1146':sum(x['instances'] for x in per.values())==1146,'unique_cells':len(cells)==a.get('unique_feature_cells'),'mixed_count':len(mixed)==a.get('mixed_cell_count'),'floor':floor==a.get('irreducible_error_floor'),'per_n':per_n_match,'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 negative=a.get('terminal')=='QG15C_ENLARGED_DONOR_PATH_VOCABULARY_STILL_INSUFFICIENT__MIXED_CELLS_MACHINE_VERIFIED'; positive=a.get('terminal')=='QG15C_L2_FEATURE_DETERMINED_ON_COMPLETE_NLE3__HELDOUT_STAGE_REQUIRED'; consistent=(negative and len(mixed)>0) or (positive and len(mixed)==0); checks['terminal_consistent']=consistent; decision=('ACCEPT_INSUFFICIENT' if negative else 'ACCEPT_HELDOUT_REQUIRED') if all(checks.values()) else 'REJECT'; out={'schema':'ORION.QG.QG15C.Generic.v1','issue':'SzeChunYiu/ORION#840','decision':decision,'checks':checks,'all_checks':all(checks.values()),'mixed_cell_count':len(mixed),'irreducible_error_floor':floor,'terminal':a.get('terminal'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
