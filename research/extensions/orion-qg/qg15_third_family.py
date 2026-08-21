#!/usr/bin/env python3
"""QG-15 third-family instance analyzer — StabPrep regime geometry.

Frozen protocol: development/orion-qg-regime-geometry/QG15_THIRD_FAMILY_PROTOCOL_V1.md
(sha256 recorded in RESULTS). Self-contained: stdlib + numpy (seeded rng only).
Stdout: two deterministic receipt lines (prospective stamp first, then the receipt).
Stderr: stage runtimes (the only non-deterministic output).
"""
from __future__ import annotations

import hashlib
import heapq
import itertools
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROTOCOL = REPO / "development" / "orion-qg-regime-geometry" / "QG15_THIRD_FAMILY_PROTOCOL_V1.md"
RESULTS_PATH = Path(__file__).resolve().parent / "QG15_THIRD_FAMILY_RESULTS.json"
SCHEMA = "orion-qg.qg15_third_family.v1"
BASE_REVISION = "40e0160f3c54ecd7f3e0e0a82b1719ce09b90ab8"
PANEL_SEED = 20260821
COST = {"H": 1, "S": 1, "SDG": 1, "CX": 3}
INVKIND = {"H": "H", "S": "SDG", "SDG": "S", "CX": "CX"}

_REFEREE4_INVOKED = False  # G8 code-structural prospective discipline flag
_STAMP_PRINTED = False


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# ---------------------------------------------------------------- Pauli algebra
def make_ctx(n: int):
    """Per-n context: masks, gate list (frozen order), gate appliers."""
    mask = (1 << n) - 1
    twon = 2 * n
    gates = []
    for q in range(n):
        gates.append(("H", q))
    for q in range(n):
        gates.append(("S", q))
    for q in range(n):
        gates.append(("SDG", q))
    for c in range(n):
        for t in range(n):
            if c != t:
                gates.append(("CX", c, t))
    return {"n": n, "mask": mask, "twon": twon, "gates": gates}


def conj(gate, e: int, n: int) -> int:
    mask = (1 << n) - 1
    twon = 2 * n
    z = e & mask
    x = (e >> n) & mask
    s = e >> twon
    kind = gate[0]
    if kind == "H":
        q = gate[1]
        xb = (x >> q) & 1
        zb = (z >> q) & 1
        s ^= xb & zb
        if xb != zb:
            x ^= 1 << q
            z ^= 1 << q
    elif kind == "S":
        q = gate[1]
        xb = (x >> q) & 1
        zb = (z >> q) & 1
        s ^= xb & zb
        z ^= xb << q
    elif kind == "SDG":
        q = gate[1]
        xb = (x >> q) & 1
        zb = (z >> q) & 1
        s ^= xb & (zb ^ 1)
        z ^= xb << q
    else:  # CX
        c, t = gate[1], gate[2]
        xc = (x >> c) & 1
        zt = (z >> t) & 1
        xt = (x >> t) & 1
        zc = (z >> c) & 1
        s ^= xc & zt & (xt ^ zc ^ 1)
        x ^= xc << t
        z ^= zt << c
    return (s << twon) | (x << n) | z


def apply_state(state, gate, n: int):
    return tuple(sorted(conj(gate, e, n) for e in state))


def start_state(n: int):
    return tuple(range(1 << n))


def apply_circuit(state, circuit, n: int):
    for g in circuit:
        state = apply_state(state, g, n)
    return state


def circuit_cost(circuit) -> int:
    return sum(COST[g[0]] for g in circuit)


def inv_gate(g):
    return (INVKIND[g[0]],) + tuple(g[1:])


def pauli_str(e: int, n: int) -> str:
    mask = (1 << n) - 1
    z = e & mask
    x = (e >> n) & mask
    s = e >> (2 * n)
    # letter table: 00 I, 10 X, 01 Z, 11 Y
    letters = []
    for q in range(n):
        xb = (x >> q) & 1
        zb = (z >> q) & 1
        letters.append({(0, 0): "I", (1, 0): "X", (0, 1): "Z", (1, 1): "Y"}[(xb, zb)])
    return ("-" if s else "+") + "".join(letters)


def expected_count(n: int) -> int:
    out = 1 << n
    for k in range(1, n + 1):
        out *= (1 << k) + 1
    return out


# ---------------------------------------------------------------- exact referee
def referee(n: int):
    """Dijkstra over the full stabilizer-state graph. Returns dist dict."""
    ctx = make_ctx(n)
    start = start_state(n)
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, s = heapq.heappop(heap)
        if d > dist[s]:
            continue
        for g in ctx["gates"]:
            t = apply_state(s, g, n)
            nd = d + COST[g[0]]
            old = dist.get(t)
            if old is None or nd < old:
                dist[t] = nd
                heapq.heappush(heap, (nd, t))
    assert len(dist) == expected_count(n), (n, len(dist))
    return dist


def referee_lex(n: int, kinds):
    """Lexicographic (cost, count-of-kinds) Dijkstra: per-state minimum secondary
    count among cost-optimal circuits."""
    ctx = make_ctx(n)
    start = start_state(n)
    dist = {start: (0, 0)}
    heap = [((0, 0), start)]
    while heap:
        d, s = heapq.heappop(heap)
        if d > dist[s]:
            continue
        for g in ctx["gates"]:
            t = apply_state(s, g, n)
            nd = (d[0] + COST[g[0]], d[1] + (1 if g[0] in kinds else 0))
            old = dist.get(t)
            if old is None or nd < old:
                dist[t] = nd
                heapq.heappush(heap, (nd, t))
    return dist


def extract_optimal_circuit(state, dist, n: int):
    """Deterministic backward walk (frozen gate order)."""
    ctx = make_ctx(n)
    circuit = []
    s = state
    d = dist[s]
    while d > 0:
        found = False
        for g in ctx["gates"]:
            p = apply_state(s, inv_gate(g), n)
            pd = dist.get(p)
            if pd is not None and pd + COST[g[0]] == d:
                circuit.append(g)
                s, d = p, pd
                found = True
                break
        assert found, "no predecessor found"
    circuit.reverse()
    assert s == start_state(n)
    return circuit


# ---------------------------------------------------------------- donor (GE)
def _xof(e, n):
    return (e >> n) & ((1 << n) - 1)


def _zof(e, n):
    return e & ((1 << n) - 1)


def _sof(e, n):
    return e >> (2 * n)


def _pivot_key(e, n):
    return (_xof(e, n), _zof(e, n), _sof(e, n))


def micro_steps(st, pivot, q: int, route: str, processed: int, n: int):
    """Run the frozen micro-steps for one qubit under the given route.
    Returns (gates, new_state_list, events). st is a list of encoded elements."""
    st = list(st)
    pv = pivot
    gates = []
    events = {"nCZ": 0, "nY": 0, "nSignX": 0, "nSignZ": 0, "nCN": 0}

    def emit(g):
        nonlocal st, pv
        st = [conj(g, e, n) for e in st]
        pv = conj(g, pv, n)
        gates.append(g)

    if route == "X":
        assert (_xof(pv, n) >> q) & 1 == 1
        if (_zof(pv, n) >> q) & 1:
            emit(("S", q))
            events["nY"] += 1
        for j in range(n):
            if j == q or (processed >> j) & 1:
                continue
            xj = (_xof(pv, n) >> j) & 1
            zj = (_zof(pv, n) >> j) & 1
            if xj and zj:
                emit(("S", j))
                events["nY"] += 1
            xj = (_xof(pv, n) >> j) & 1
            zj = (_zof(pv, n) >> j) & 1
            if xj:
                emit(("CX", q, j))
                events["nCN"] += 1
            elif zj:
                emit(("H", j))
                emit(("CX", q, j))
                emit(("H", j))
                events["nCZ"] += 1
                events["nCN"] += 1
        assert _xof(pv, n) == 1 << q and _zof(pv, n) == 0
        if _sof(pv, n):
            emit(("S", q))
            emit(("S", q))
            events["nSignX"] += 1
        emit(("H", q))
    else:  # Z-route
        assert (_zof(pv, n) >> q) & 1 == 1
        if (_xof(pv, n) >> q) & 1:
            emit(("S", q))
            emit(("H", q))
            events["nY"] += 1
        for j in range(n):
            if j == q or (processed >> j) & 1:
                continue
            xj = (_xof(pv, n) >> j) & 1
            zj = (_zof(pv, n) >> j) & 1
            if xj and zj:
                emit(("S", j))
                emit(("H", j))
                emit(("CX", j, q))
                events["nY"] += 1
                events["nCN"] += 1
            elif xj:
                emit(("H", j))
                emit(("CX", j, q))
                emit(("H", j))
                events["nCZ"] += 1
                events["nCN"] += 1
            elif zj:
                emit(("CX", j, q))
                events["nCN"] += 1
        assert _xof(pv, n) == 0 and _zof(pv, n) == 1 << q
        if _sof(pv, n):
            emit(("H", q))
            emit(("S", q))
            emit(("S", q))
            emit(("H", q))
            events["nSignZ"] += 1
    assert pv == (1 << q), "pivot must end as +Z_q"
    return gates, st, events


def x_candidates(st, q: int, processed: int, n: int):
    out = []
    for e in st:
        x = _xof(e, n)
        z = _zof(e, n)
        if (x >> q) & 1 and not (x & processed) and not (z & processed):
            out.append(e)
    return sorted(out, key=lambda e: _pivot_key(e, n))


def z_candidates(st, q: int, processed: int, n: int):
    out = []
    for e in st:
        x = _xof(e, n)
        z = _zof(e, n)
        if (z >> q) & 1 and not (x & processed) and not (z & processed):
            out.append(e)
    return sorted(out, key=lambda e: _pivot_key(e, n))


def donor(state, n: int):
    """Frozen GE donor. Returns (prep_circuit, C_D, features, disentangle_gates)."""
    st = list(state)
    all_gates = []
    feats = {"nCZ": 0, "nY": 0, "nSignX": 0, "nSignZ": 0, "nCN": 0}
    processed = 0
    for q in range(n):
        cands = x_candidates(st, q, processed, n)
        if cands:
            gates, st, events = micro_steps(st, cands[0], q, "X", processed, n)
        else:
            zq = 1 << q
            neg = (1 << (2 * n)) | zq
            if neg in st:
                gates, st, events = micro_steps(st, neg, q, "Z", processed, n)
            else:
                assert zq in st
                gates, events = [], {}
        for k, v in events.items():
            feats[k] += v
        all_gates.extend(gates)
        processed |= 1 << q
    assert tuple(sorted(st)) == start_state(n)
    prep = [inv_gate(g) for g in reversed(all_gates)]
    cd = circuit_cost(all_gates)
    return prep, cd, feats, all_gates


# ---------------------------------------------------------------- ladder E1-E3
def ladder_min(state, n: int, pivot_free: bool, route_free: bool, memo):
    """Adaptive-order schedule minimum. Returns (cost, disentangle_gates_tuple)."""
    full = (1 << n) - 1

    def rec(key, rem):
        mk = (key, rem)
        hit = memo.get(mk)
        if hit is not None:
            return hit
        if rem == 0:
            assert key == start_state(n)
            res = (0, ())
            memo[mk] = res
            return res
        processed = full ^ rem
        best = None
        for q in range(n):
            if not (rem >> q) & 1:
                continue
            st = list(key)
            branches = []
            xc = x_candidates(st, q, processed, n)
            if xc:
                pivots = xc if pivot_free else xc[:1]
                for p in pivots:
                    branches.append(("X", p))
            else:
                zq = 1 << q
                neg = (1 << (2 * n)) | zq
                forced = neg if neg in st else zq
                branches.append(("Z", forced))
            if route_free:
                for p in z_candidates(st, q, processed, n):
                    if ("Z", p) not in branches:
                        branches.append(("Z", p))
            for route, pivot in branches:
                gates, new_st, _events = micro_steps(st, pivot, q, route, processed, n)
                sub_cost, sub_gates = rec(tuple(sorted(new_st)), rem ^ (1 << q))
                cand = (circuit_cost(gates) + sub_cost, tuple(gates) + sub_gates)
                if best is None or cand < best:
                    best = cand
        memo[mk] = best
        return best

    return rec(tuple(state), full)


# ---------------------------------------------------------------- structure
def rank_f2(vectors) -> int:
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def r_x(state, n: int) -> int:
    return rank_f2([_xof(e, n) for e in state])


def tensor_factors(state, n: int) -> int:
    full = (1 << n) - 1
    cuts = []
    for sub in range(1, full):
        ra = -1
        rb = -1
        ca = sum(1 for e in state if ((_xof(e, n) | _zof(e, n)) & ~sub & full) == 0)
        cb = sum(1 for e in state if ((_xof(e, n) | _zof(e, n)) & sub) == 0)
        ra = ca.bit_length() - 1
        rb = cb.bit_length() - 1
        if ra + rb == n:
            cuts.append(sub)
    parts = [full]
    for cut in cuts:
        new_parts = []
        for p in parts:
            a = p & cut
            b = p & ~cut & full
            if a:
                new_parts.append(a)
            if b:
                new_parts.append(b)
        parts = new_parts
    return len(parts)


def lower_bound(state, n: int):
    rx = r_x(state, n)
    c = tensor_factors(state, n)
    return rx + 3 * (n - c), rx, c


# ---------------------------------------------------------------- predicate
LITERAL_NAMES = [
    "nCZ==0", "nSignX==0", "nSignZ==0", "nY==0", "C_D==LB", "C_D<=LB+1",
    "r_X<=1", "c==n", "nCN<=n-1", "C_D<=2n",
]


def literals(feats, cd, lb, rx, c, n):
    return (
        feats["nCZ"] == 0,
        feats["nSignX"] == 0,
        feats["nSignZ"] == 0,
        feats["nY"] == 0,
        cd == lb,
        cd <= lb + 1,
        rx <= 1,
        c == n,
        feats["nCN"] <= n - 1,
        cd <= 2 * n,
    )


def confusion(pred_flags, labels):
    tp = fp = fn = tn = 0
    for p, l in zip(pred_flags, labels):
        if p and l:
            tp += 1
        elif p and not l:
            fp += 1
        elif not p and l:
            fn += 1
        else:
            tn += 1
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "errors": fp + fn}


# ---------------------------------------------------------------- panel (n=4)
def build_panel(n4: int = 4, size: int = 120, length: int = 24):
    import numpy as np

    rng = np.random.default_rng(PANEL_SEED)
    seen = set()
    panel = []
    while len(panel) < size:
        state = start_state(n4)
        for _ in range(length):
            kind = int(rng.integers(0, 4))
            if kind == 3:
                c = int(rng.integers(0, 4))
                u = int(rng.integers(0, 3))
                others = [x for x in range(4) if x != c]
                t = others[u]
                g = ("CX", c, t)
            else:
                q = int(rng.integers(0, 4))
                g = (["H", "S", "SDG"][kind], q)
            state = apply_state(state, g, n4)
        if state not in seen:
            seen.add(state)
            panel.append(state)
    return panel


# ---------------------------------------------------------------- main
def log_time(label, t0):
    t1 = time.perf_counter()
    print(f"[qg15] {label}: {t1 - t0:.2f}s", file=sys.stderr)
    return t1


def main() -> int:
    global _REFEREE4_INVOKED, _STAMP_PRINTED
    t0 = time.perf_counter()
    timing = {}
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()

    # ---------------- stage A: referees n=1..3 + independent brutes + exchange
    ta = time.perf_counter()
    dists = {}
    domains = {}
    for n in (1, 2, 3):
        d = referee(n)
        dists[n] = d
        keys = sorted(d.keys())
        enum_sha = hashlib.sha256(
            "\n".join(canonical(list(k)) for k in keys).encode()
        ).hexdigest()
        domains[f"n{n}"] = {
            "count": len(keys),
            "expected_count": expected_count(n),
            "first_key": list(keys[0]),
            "last_key": list(keys[-1]),
            "enumeration_sha256": enum_sha,
            "max_referee_cost": max(d.values()),
        }
        assert len(keys) == expected_count(n)

    # G2 arm 1: n=1 exhaustive word enumeration (length <= 6 over H,S,SDG)
    one_gates = [("H", 0), ("S", 0), ("SDG", 0)]
    words = [((), start_state(1))]
    all_words = [((), start_state(1))]
    for _ in range(6):
        nxt = []
        for w, s in words:
            for g in one_gates:
                nxt.append((w + (g,), apply_state(s, g, 1)))
        words = nxt
        all_words.extend(nxt)
    assert len(all_words) == 1093
    brute1 = {}
    for w, s in all_words:
        cst = len(w)
        if s not in brute1 or cst < brute1[s]:
            brute1[s] = cst
    assert max(dists[1].values()) < 6, "n=1 word enumeration must cover all optima"
    g2_n1 = all(brute1.get(s) == c for s, c in dists[1].items()) and len(brute1) >= len(dists[1])

    # exchange check: NF1 words achieve referee optimum on every n=1 state
    def nf1(word):
        kinds = [g[0] for g in word]
        if kinds.count("H") > 2:
            return False
        for a, b in zip(kinds, kinds[1:]):
            if a == "H" and b == "H":
                return False
            if {a, b} == {"S", "SDG"}:
                return False
        run = 1
        for a, b in zip(kinds, kinds[1:]):
            run = run + 1 if (a == b and a != "H") else 1
            if run >= 3:
                return False
        return True

    nf_best = {}
    for w, s in all_words:
        if nf1(w):
            cst = len(w)
            if s not in nf_best or cst < nf_best[s]:
                nf_best[s] = cst
    exchange_holds = all(nf_best.get(s) == c for s, c in dists[1].items())

    # G2 arm 2: n=2 Bellman-Ford fixpoint over the complete 60-state space
    n2_states = sorted(dists[2].keys())
    ctx2 = make_ctx(2)
    INF = 10 ** 9
    bf = {s: INF for s in n2_states}
    bf[start_state(2)] = 0
    changed = True
    sweeps = 0
    while changed:
        changed = False
        sweeps += 1
        for s in n2_states:
            ds = bf[s]
            if ds >= INF:
                continue
            for g in ctx2["gates"]:
                t = apply_state(s, g, 2)
                nd = ds + COST[g[0]]
                if nd < bf[t]:
                    bf[t] = nd
                    changed = True
    g2_n2 = all(bf[s] == dists[2][s] for s in n2_states)
    assert g2_n1 and g2_n2, "G2 independent brute agreement failed"
    ta = log_time("stage A referees+brutes", ta)
    timing["A_referees_brutes"] = round(ta - t0, 3)

    # ---------------- stage B: donor + structure on all n<=3 states
    tb = ta
    donor_data = {}  # n -> key -> record
    for n in (1, 2, 3):
        recs = {}
        for key in sorted(dists[n].keys()):
            prep, cd, feats, _ = donor(key, n)
            replay = apply_circuit(start_state(n), prep, n)
            assert replay == key, "G3 donor validity failed"
            copt = dists[n][key]
            assert copt <= cd, "referee exceeded donor"
            lb, rx, c = lower_bound(key, n)
            assert lb <= copt, "G5 lower bound violated"
            recs[key] = {
                "C_D": cd, "C_opt": copt, "gap": cd - copt, "feats": feats,
                "LB": lb, "r_X": rx, "c": c, "prep": prep,
            }
        donor_data[n] = recs
    tb = log_time("stage B donor+structure", tb)
    timing["B_donor_structure"] = round(tb - ta, 3)

    # ---------------- component 1: regime map
    comp1 = {"outcome": "REGIME_MAP_COMPLETE", "per_n": {}}
    for n in (1, 2, 3):
        recs = donor_data[n]
        gaps = {}
        cross = {}
        exact = 0
        for key, r in recs.items():
            gaps[str(r["gap"])] = gaps.get(str(r["gap"]), 0) + 1
            ck = f"rX={r['r_X']},c={r['c']}"
            cell = cross.setdefault(ck, [0, 0])
            cell[0 if r["gap"] == 0 else 1] += 1
        exact = sum(1 for r in recs.values() if r["gap"] == 0)
        comp1["per_n"][f"n{n}"] = {
            "instances": len(recs),
            "donor_exact": exact,
            "donor_exact_fraction": [exact, len(recs)],
            "gap_histogram": dict(sorted(gaps.items(), key=lambda kv: int(kv[0]))),
            "cross_tab_rX_c__exact_trade": dict(sorted(cross.items())),
        }

    # ---------------- stage C: ladder E1-E3
    tc = tb
    ladder_vals = {}  # n -> key -> {1: (cost,gates),2:...,3:...}
    for n in (1, 2, 3):
        memos = {1: {}, 2: {}, 3: {}}
        cfgs = {1: (False, False), 2: (True, False), 3: (True, True)}
        vals = {}
        for key in sorted(dists[n].keys()):
            row = {}
            for lvl, (pf, rf) in cfgs.items():
                cost, gates = ladder_min(key, n, pf, rf, memos[lvl])
                prep = [inv_gate(g) for g in reversed(gates)]
                assert apply_circuit(start_state(n), prep, n) == key, "G4 ladder replay failed"
                assert circuit_cost(prep) == cost
                row[lvl] = (cost, gates)
            cd = donor_data[n][key]["C_D"]
            copt = donor_data[n][key]["C_opt"]
            assert cd >= row[1][0] >= row[2][0] >= row[3][0] >= copt, "G4 nesting failed"
            vals[key] = row
        ladder_vals[n] = vals
    tc = log_time("stage C ladder", tc)
    timing["C_ladder"] = round(tc - tb, 3)

    # ---------------- component 3: sufficiency
    residuals = {}
    for n in (1, 2, 3):
        res = {0: 0, 1: 0, 2: 0, 3: 0}
        for key in dists[n]:
            copt = donor_data[n][key]["C_opt"]
            if donor_data[n][key]["C_D"] > copt:
                res[0] += 1
            for lvl in (1, 2, 3):
                if ladder_vals[n][key][lvl][0] > copt:
                    res[lvl] += 1
        residuals[f"n{n}"] = {f"E{l}_residual": res[l] for l in (0, 1, 2, 3)}
    total_res = {l: sum(residuals[f"n{n}"][f"E{l}_residual"] for n in (1, 2, 3)) for l in (0, 1, 2, 3)}
    if total_res[0] == 0:
        closing = "CLOSED_AT_LEVEL_0"
        min_level = 0
    else:
        min_level = None
        for l in (1, 2, 3):
            if total_res[l] == 0:
                min_level = l
                break
        closing = f"CLOSED_AT_LEVEL_{min_level}" if min_level is not None else "NO_STRICT_SUBEXTENSION_CLOSES"

    budgets = {}
    for n in (1, 2, 3):
        dh = referee_lex(n, {"H"})
        ds_ = referee_lex(n, {"S", "SDG"})
        dc = referee_lex(n, {"CX"})
        for s, v in dh.items():
            assert v[0] == dists[n][s]
        h_star = max(v[1] for v in dh.values())
        s_star = max(v[1] for v in ds_.values())
        c_star = max(v[1] for v in dc.values())
        hmin_gt_rx = sum(1 for s, v in dh.items() if v[1] > r_x(s, n))
        budgets[f"n{n}"] = {
            "h_star_min_H_budget": h_star,
            "s_star_min_Sfamily_budget": s_star,
            "c_star_min_CNOT_budget": c_star,
            "states_with_minimal_optimal_H_count_above_rX": hmin_gt_rx,
            "max_r_X": max(r_x(s, n) for s in dists[n]),
        }
    comp3 = {
        "outcome": closing,
        "minimal_closing_level": min_level,
        "per_n_residuals": residuals,
        "budget_bounds": budgets,
        "exchange_check_n1": {
            "normal_form": "<=2 H, no adjacent HH, no adjacent S/SDG pair, no S-run>=3",
            "outcome": "EXCHANGE_NF1_HOLDS" if exchange_holds else "EXCHANGE_NF1_REFUTED",
            "word_count": 1093,
        },
    }
    tcs = log_time("stage C2 budgets", tc)
    timing["C2_budgets"] = round(tcs - tc, 3)

    # ---------------- component 2: trades
    CLASS_NAMES = {1: "ORDER_TRADE", 2: "PIVOT_TRADE", 3: "ROUTE_TRADE", 4: "GLOBAL_TRADE"}

    def trade_class(n, key):
        copt = donor_data[n][key]["C_opt"]
        for lvl in (1, 2, 3):
            if ladder_vals[n][key][lvl][0] == copt:
                return lvl
        return 4

    def serialize_witness(n, key):
        r = donor_data[n][key]
        opt_circ = extract_optimal_circuit(key, dists[n], n)
        assert circuit_cost(opt_circ) == r["C_opt"]
        assert apply_circuit(start_state(n), opt_circ, n) == key
        return {
            "n": n,
            "canonical_key": list(key),
            "group": [pauli_str(e, n) for e in key],
            "C_D": r["C_D"], "C_opt": r["C_opt"], "gap": r["gap"],
            "C_E1": ladder_vals[n][key][1][0],
            "C_E2": ladder_vals[n][key][2][0],
            "C_E3": ladder_vals[n][key][3][0],
            "trade_class": CLASS_NAMES[trade_class(n, key)],
            "features": r["feats"], "LB": r["LB"], "r_X": r["r_X"], "c": r["c"],
            "donor_circuit": [list(g) for g in r["prep"]],
            "optimal_circuit": [list(g) for g in opt_circ],
        }

    comp2 = {"per_n": {}, "minimal_witnesses": [], "caps": "trade rows capped at 20 per n; one minimal witness per (n, class)"}
    total_trades = 0
    for n in (1, 2, 3):
        trades = [k for k in sorted(dists[n].keys()) if donor_data[n][k]["gap"] > 0]
        total_trades += len(trades)
        class_census = {}
        for k in trades:
            cname = CLASS_NAMES[trade_class(n, k)]
            class_census[cname] = class_census.get(cname, 0) + 1
        rows = [
            {"canonical_key": list(k), "C_D": donor_data[n][k]["C_D"],
             "C_opt": donor_data[n][k]["C_opt"], "gap": donor_data[n][k]["gap"],
             "trade_class": CLASS_NAMES[trade_class(n, k)]}
            for k in trades[:20]
        ]
        comp2["per_n"][f"n{n}"] = {
            "trade_count": len(trades),
            "class_census": dict(sorted(class_census.items())),
            "first_20_trade_rows": rows,
        }
        for cls in (1, 2, 3, 4):
            members = [k for k in trades if trade_class(n, k) == cls]
            if members:
                best = min(members, key=lambda k: (donor_data[n][k]["C_opt"], k))
                comp2["minimal_witnesses"].append(serialize_witness(n, best))
    comp2["outcome"] = "TRADES_FOUND" if total_trades else "NO_TRADES"
    comp2["total_trades"] = total_trades

    # G6 witness recompute from serialized key alone
    for w in comp2["minimal_witnesses"]:
        n = w["n"]
        key = tuple(w["canonical_key"])
        prep2, cd2, feats2, _ = donor(key, n)
        assert cd2 == w["C_D"] and feats2 == w["features"], "G6 donor recompute failed"
        assert dists[n][key] == w["C_opt"], "G6 referee recompute failed"
        dc = [tuple(g) for g in w["donor_circuit"]]
        oc = [tuple(g) for g in w["optimal_circuit"]]
        assert apply_circuit(start_state(n), dc, n) == key
        assert apply_circuit(start_state(n), oc, n) == key
        assert circuit_cost(dc) == w["C_D"] and circuit_cost(oc) == w["C_opt"]
    td = log_time("stage D trades", tcs)
    timing["D_trades"] = round(td - tcs, 3)

    # ---------------- component 4: predicate (selection on fit = n=3)
    def instance_row(n, key):
        r = donor_data[n][key]
        lits = literals(r["feats"], r["C_D"], r["LB"], r["r_X"], r["c"], n)
        return lits, r["gap"] == 0

    fit_rows = [instance_row(3, k) for k in sorted(dists[3].keys())]
    fit_labels = [lab for _, lab in fit_rows]

    def eval_pred(idxs, rows):
        return [all(lits[i] for i in idxs) for lits, _ in rows]

    ladder_defs = {
        "P0": (0,), "P1": (0, 1, 2), "P2": (4,),
    }
    train_err = {}
    for name, idxs in ladder_defs.items():
        flags = eval_pred(idxs, fit_rows)
        train_err[name] = confusion(flags, fit_labels)["errors"]
    selected = None
    for name in ("P0", "P1", "P2"):
        if train_err[name] == 0:
            selected = name
            selected_idxs = ladder_defs[name]
            break
    p3_choice = None
    if selected is None:
        best = None
        for size in (1, 2, 3):
            for combo in itertools.combinations(range(10), size):
                flags = eval_pred(combo, fit_rows)
                err = confusion(flags, fit_labels)["errors"]
                cand = (err, size, combo)
                if best is None or cand < best:
                    best = cand
        p3_choice = best
        selected = "P3"
        selected_idxs = best[2]
    selected_def = " AND ".join(LITERAL_NAMES[i] for i in selected_idxs)

    # confusion matrices on n=1..3 for selected and P0/P1/P2
    conf = {}
    panels_n = {"n1": 1, "n2": 2, "n3_fit": 3}
    for pname, n in panels_n.items():
        rows = [instance_row(n, k) for k in sorted(dists[n].keys())]
        labels = [lab for _, lab in rows]
        conf[pname] = {}
        for name, idxs in list(ladder_defs.items()) + [("selected", selected_idxs)]:
            conf[pname][name] = confusion(eval_pred(idxs, rows), labels)

    # ---------------- component 5: prospective forecast (stamp BEFORE referee4)
    te = time.perf_counter()
    # frozen gap-forecast table from fit domain
    gap_table_counts = {}
    for k in sorted(dists[3].keys()):
        r = donor_data[3][k]
        f = r["feats"]
        tk = f"{f['nCZ']},{f['nSignX']},{f['nSignZ']},{f['nY']}"
        gap_table_counts.setdefault(tk, {}).setdefault(r["gap"], 0)
        gap_table_counts[tk][r["gap"]] += 1
    gap_table = {}
    for tk, cnts in sorted(gap_table_counts.items()):
        best_gap = min(sorted(cnts), key=lambda g: (-cnts[g], g))
        gap_table[tk] = best_gap

    panel = build_panel()
    panel_keys_sha = hashlib.sha256(
        "\n".join(canonical(list(k)) for k in panel).encode()
    ).hexdigest()
    predictions = []
    panel_recs = {}
    for idx, key in enumerate(panel):
        prep, cd, feats, _ = donor(key, 4)
        replay = apply_circuit(start_state(4), prep, 4)
        assert replay == key, "G3 donor validity failed on panel"
        lb, rx, c = lower_bound(key, 4)
        lits = literals(feats, cd, lb, rx, c, 4)
        pred_true = all(lits[i] for i in selected_idxs)
        tk = f"{feats['nCZ']},{feats['nSignX']},{feats['nSignZ']},{feats['nY']}"
        pred_gap = 0 if pred_true else gap_table.get(tk, 0)
        pred_cost = max(lb, cd - pred_gap)
        predictions.append({
            "index": idx, "canonical_key": list(key), "C_D": cd, "LB": lb,
            "r_X": rx, "c": c, "features": feats,
            "predicted_donor_exact": pred_true, "predicted_gap": pred_gap,
            "predicted_C_opt": pred_cost,
        })
        panel_recs[key] = {"C_D": cd, "feats": feats, "LB": lb, "r_X": rx, "c": c,
                           "pred_true": pred_true, "pred_cost": pred_cost, "prep": prep}
    predictions_sha = sha256_text(canonical(predictions))
    assert not _REFEREE4_INVOKED, "G8 violated: referee4 ran before the stamp"
    print(f"ORIONQG_QG15_PROSPECTIVE_PREDICTIONS_SHA256={predictions_sha}")
    sys.stdout.flush()
    _STAMP_PRINTED = True

    _REFEREE4_INVOKED = True
    dist4 = referee(4)
    te2 = log_time("stage E panel+referee4", te)
    timing["E_panel_referee4"] = round(te2 - te, 3)

    regime_correct = cost_correct = 0
    refutations = []
    for p in predictions:
        key = tuple(p["canonical_key"])
        copt = dist4[key]
        r = panel_recs[key]
        assert r["LB"] <= copt, "G5 lower bound violated on panel"
        assert copt <= r["C_D"], "referee exceeded donor on panel"
        actual_exact = copt == r["C_D"]
        rc = p["predicted_donor_exact"] == actual_exact
        cc = p["predicted_C_opt"] == copt
        regime_correct += rc
        cost_correct += cc
        if (not rc or not cc) and len(refutations) < 20:
            refutations.append({
                "index": p["index"], "canonical_key": p["canonical_key"],
                "C_D": r["C_D"], "C_opt_actual": copt,
                "predicted_donor_exact": p["predicted_donor_exact"],
                "actual_donor_exact": actual_exact,
                "predicted_C_opt": p["predicted_C_opt"],
            })
    npanel = len(predictions)
    comp5 = {
        "panel": {"n": 4, "size": npanel, "seed": PANEL_SEED,
                  "circuit_length": 24, "panel_keys_sha256": panel_keys_sha,
                  "n4_state_space": len(dist4), "n4_expected": expected_count(4)},
        "gap_forecast_table": gap_table,
        "predictions_sha256": predictions_sha,
        "predictions_stamped_before_referee": True,
        "predictions": predictions,
        "regime_correct": regime_correct, "regime_refuted": npanel - regime_correct,
        "cost_correct": cost_correct, "cost_refuted": npanel - cost_correct,
        "refutation_witnesses": refutations,
        "regime_outcome": "REGIME_FORECAST_EXACT" if regime_correct == npanel else "REGIME_FORECAST_REFUTED",
        "cost_outcome": "COST_FORECAST_EXACT" if cost_correct == npanel else "COST_FORECAST_REFUTED",
    }
    assert len(dist4) == expected_count(4)

    # held-out predicate confusion on the panel
    rows4 = []
    for key in panel:
        r = panel_recs[key]
        lits = literals(r["feats"], r["C_D"], r["LB"], r["r_X"], r["c"], 4)
        rows4.append((lits, dist4[key] == r["C_D"]))
    labels4 = [lab for _, lab in rows4]
    conf["n4_panel_heldout"] = {}
    for name, idxs in list(ladder_defs.items()) + [("selected", selected_idxs)]:
        conf["n4_panel_heldout"][name] = confusion(eval_pred(idxs, rows4), labels4)

    all_zero = all(conf[p]["selected"]["errors"] == 0 for p in conf)
    zero_fp = all(conf[p]["selected"]["FP"] == 0 for p in conf)
    if total_trades == 0:
        pred_outcome = "FAMILY_CLOSURE"
    elif all_zero and selected in ("P0", "P1"):
        pred_outcome = f"EXACT_PREDICATE_FOUND_{selected}"
    elif all_zero and selected == "P2":
        pred_outcome = "EXACT_BY_LOWER_BOUND_ONLY"
    elif all_zero:
        pred_outcome = "EXACT_PREDICATE_FOUND_P3"
    elif zero_fp:
        pred_outcome = "SUFFICIENT_CONDITION_ONLY"
    else:
        pred_outcome = "NO_CLEAN_PREDICATE"
    comp4 = {
        "target_label": "donor_exact := (C_opt == C_D)",
        "fit_domain": "exhaustive n=3 (1080 instances)",
        "ladder": {"P0": "nCZ==0", "P1": "nCZ==0 AND nSignX==0 AND nSignZ==0",
                   "P2": "C_D==LB", "P3": "best <=3-literal conjunction"},
        "training_errors": train_err,
        "selected": selected,
        "selected_definition": selected_def,
        "selected_literal_indices": list(selected_idxs),
        "p3_search": None if p3_choice is None else
            {"error": p3_choice[0], "size": p3_choice[1], "indices": list(p3_choice[2])},
        "confusion_matrices": conf,
        "held_out_labeled_after_selection": True,
        "outcome": pred_outcome,
    }
    tf = log_time("stage F predicate+confusions", te2)
    timing["F_predicate"] = round(tf - te2, 3)

    # ---------------- gates, terminal, results
    gates = {
        "G1_state_space_ground_truth": True,
        "G2_independent_brute_agreement": bool(g2_n1 and g2_n2),
        "G2_bellman_ford_sweeps": sweeps,
        "G3_donor_validity_all_domains": True,
        "G4_ladder_nesting_and_replay": True,
        "G5_lower_bound_validity": True,
        "G6_witness_recompute": True,
        "G7_predicate_discipline": True,
        "G8_prospective_stamp_before_referee": bool(_STAMP_PRINTED),
        "G9_determinism_no_wallclock_in_digest": True,
        "G10_no_new_subject_data_no_network": True,
    }
    terminal = "TEMPLATE_TRANSFERRED"
    authority = (
        f"ORION_QG15_THIRD_FAMILY_{terminal}__STABPREP_CLIFFORD_SYNTHESIS_"
        "REGIME_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6"
    )
    results = {
        "schema": SCHEMA,
        "programme": "ORION-QG lane QG-15 (PROGRAMME_CHARTER_V1.md, issue #740); third template-transfer instance",
        "template_source": "TARE R6N..R6S (wave 1); SixLCU QG-4 upgraded by QG-12 (wave 2)",
        "protocol": "development/orion-qg-regime-geometry/QG15_THIRD_FAMILY_PROTOCOL_V1.md",
        "protocol_sha256": protocol_sha,
        "base_revision": BASE_REVISION,
        "family": {
            "name": "StabPrep",
            "instance": "n-qubit stabilizer state (full signed stabilizer group, canonical sorted-int key)",
            "gate_set": "H(1), S(1), SDG(1), CNOT(3)",
            "referee": "exact Dijkstra over the complete stabilizer-state graph per n",
            "donor": "frozen greedy echelon synthesis GE (ascending qubit order, min-key pivot, X-route)",
            "materially_different_from": "TARE (no Tag/Restore) and SixLCU (no PREP/SELECT): weighted-gate circuit synthesis against a shortest-path referee",
        },
        "gate_costs": {"H": 1, "S": 1, "SDG": 1, "CNOT": 3},
        "domains": domains,
        "component1_regime_map": comp1,
        "component2_trades": comp2,
        "component3_sufficiency": comp3,
        "component4_predicate": comp4,
        "component5_prospective": comp5,
        "gates": gates,
        "component_outcomes": {
            "component1": comp1["outcome"],
            "component2": comp2["outcome"],
            "component3": comp3["outcome"],
            "component4": comp4["outcome"],
            "component5_regime": comp5["regime_outcome"],
            "component5_cost": comp5["cost_outcome"],
        },
        "terminal": terminal,
        "transfer_verdict": terminal,
        "authority": authority,
        "claim_boundary": (
            "Claims cover exactly the frozen StabPrep family: stabilizer-state preparation from |0..0> "
            "over {H,S,SDG,CNOT} with frozen costs (1,1,1,3), the frozen GE donor and its E1-E3 schedule "
            "enlargements, and the frozen structural lower bound LB = r_X + 3(n-c). All censuses, trade "
            "catalogues, sufficiency verdicts, predicates and forecasts are machine-evidenced only on the "
            "stated finite domains (exhaustive n<=3; one seeded n=4 panel); nothing is a theorem for all n, "
            "for other gate costs or gate sets, for mixed stabilizer codes, or for measurement-assisted "
            "preparation. The referee optimum is a shortest-path cost in the frozen metric; no physical "
            "runtime or quantum-advantage claim. The donor is standard Gaussian-elimination-style synthesis "
            "and earns no novelty credit. The template is the object under test. NOT_R6."
        ),
        "caps_disclosed": [
            "runtime cap < 25 min per run",
            "trade rows serialized: first 20 per n",
            "one minimal witness per (n, trade class)",
            "prospective refutation witnesses capped at 20",
            "panel size 120; one deterministic optimal circuit per witness",
            "verifier ladder scope: serialized witnesses only (per protocol section 7)",
        ],
        "random_seed_panel": PANEL_SEED,
        "predictions_sha256": predictions_sha,
        "novelty_credit": False,
        "r6_authority": False,
        "network_access": False,
        "chemistry_sources_read": False,
        "reserved_stretched_n2_accessed": False,
        "responsibility": "qg15 lane, ORION-QG programme, 2026-08-21",
    }
    digest = sha256_text(canonical(results))
    results["result_digest"] = digest
    results["timing"] = timing
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    receipt = {
        "schema": SCHEMA,
        "terminal": terminal,
        "component_outcomes": results["component_outcomes"],
        "gates_all_pass": all(v is True for k, v in gates.items() if k.startswith("G") and isinstance(v, bool)),
        "protocol_sha256": protocol_sha,
        "predictions_sha256": predictions_sha,
        "result_digest": digest,
        "authority": authority,
    }
    print("ORIONQG_QG15_THIRD_FAMILY=" + canonical(receipt))
    print(f"[qg15] total: {time.perf_counter() - t0:.2f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
