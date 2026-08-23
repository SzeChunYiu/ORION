#!/usr/bin/env python3
"""Independent QG-15 verifier: rebuilds the StabPrep referee, donor, structure,
predicate and prospective pipeline from primitives, importing nothing from the
analyzer. Internal representation is deliberately different: Paulis are
(sign, letters-tuple) with letters 0=I,1=X,2=Y,3=Z, and the gate conjugation
tables are derived numerically from the gate unitaries (not written as tableau
rules). Scope frozen in QG15_THIRD_FAMILY_PROTOCOL_V1.md section 7.
Prints exactly one token line ORIONQG_QG15_GENERIC_VERIFY={...}.
"""
from __future__ import annotations

import hashlib
import heapq
import itertools
import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "development" / "orion-qg-regime-geometry" / "QG15_THIRD_FAMILY_PROTOCOL_V1.md"
RESULTS = REPO / "research" / "extensions" / "orion-qg" / "QG15_THIRD_FAMILY_RESULTS.json"
COST = {"H": 1, "S": 1, "SDG": 1, "CX": 3}
PANEL_SEED = 20260821


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ------------------------------------------------- conjugation tables (numeric)
_P = {
    0: np.eye(2, dtype=complex),
    1: np.array([[0, 1], [1, 0]], dtype=complex),
    2: np.array([[0, -1j], [1j, 0]], dtype=complex),
    3: np.array([[1, 0], [0, -1]], dtype=complex),
}


def _match_1q(m):
    for letter, mat in _P.items():
        for sign in (1, -1):
            if np.allclose(m, sign * mat):
                return letter, sign
    raise AssertionError("not a signed Pauli")


def _match_2q(m):
    for a, b in itertools.product(range(4), range(4)):
        mat = np.kron(_P[a], _P[b])
        for sign in (1, -1):
            if np.allclose(m, sign * mat):
                return a, b, sign
    raise AssertionError("not a signed 2q Pauli")


def build_tables():
    h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    s = np.diag([1, 1j]).astype(complex)
    sdg = np.diag([1, -1j]).astype(complex)
    tables = {}
    for name, u in (("H", h), ("S", s), ("SDG", sdg)):
        tab = {}
        for letter in range(4):
            tab[letter] = _match_1q(u @ _P[letter] @ u.conj().T)
        tables[name] = tab
    # CNOT with control = first factor, target = second factor
    cx = np.array(
        [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex
    )
    tab = {}
    for a, b in itertools.product(range(4), range(4)):
        tab[(a, b)] = _match_2q(cx @ np.kron(_P[a], _P[b]) @ cx.conj().T)
    tables["CX"] = tab
    return tables


TABLES = build_tables()


# ------------------------------------------------- state algebra (letter tuples)
def conj_pauli(gate, p):
    sign, letters = p
    letters = list(letters)
    kind = gate[0]
    if kind == "CX":
        c, t = gate[1], gate[2]
        a, b, sg = TABLES["CX"][(letters[c], letters[t])]
        letters[c], letters[t] = a, b
        if sg < 0:
            sign ^= 1
    else:
        q = gate[1]
        letter, sg = TABLES[kind][letters[q]]
        letters[q] = letter
        if sg < 0:
            sign ^= 1
    return (sign, tuple(letters))


def encode(p, n: int) -> int:
    """Map to the analyzer's canonical integer encoding for comparison."""
    sign, letters = p
    x = z = 0
    for q, l in enumerate(letters):
        if l in (1, 2):
            x |= 1 << q
        if l in (2, 3):
            z |= 1 << q
    return (sign << (2 * n)) | (x << n) | z


def state_key(state, n: int):
    return tuple(sorted(encode(p, n) for p in state))


def decode_key(key, n: int):
    out = []
    mask = (1 << n) - 1
    for e in key:
        z = e & mask
        x = (e >> n) & mask
        sign = e >> (2 * n)
        letters = []
        for q in range(n):
            xb = (x >> q) & 1
            zb = (z >> q) & 1
            letters.append({(0, 0): 0, (1, 0): 1, (1, 1): 2, (0, 1): 3}[(xb, zb)])
        out.append((sign, tuple(letters)))
    return tuple(out)


def apply_gate(state, gate):
    return tuple(sorted(conj_pauli(gate, p) for p in state))


def apply_circuit(state, circuit):
    for g in circuit:
        state = apply_gate(state, tuple(g))
    return state


def start(n: int):
    out = []
    for m in range(1 << n):
        letters = tuple(3 if (m >> q) & 1 else 0 for q in range(n))
        out.append((0, letters))
    return tuple(sorted(out))


def gate_list(n: int):
    gates = [("H", q) for q in range(n)]
    gates += [("S", q) for q in range(n)]
    gates += [("SDG", q) for q in range(n)]
    gates += [("CX", c, t) for c in range(n) for t in range(n) if c != t]
    return gates


def expected_count(n: int) -> int:
    out = 1 << n
    for k in range(1, n + 1):
        out *= (1 << k) + 1
    return out


def referee(n: int):
    gates = gate_list(n)
    s0 = start(n)
    dist = {s0: 0}
    heap = [(0, s0)]
    while heap:
        d, s = heapq.heappop(heap)
        if d > dist[s]:
            continue
        for g in gates:
            t = apply_gate(s, g)
            nd = d + COST[g[0]]
            if t not in dist or nd < dist[t]:
                dist[t] = nd
                heapq.heappush(heap, (nd, t))
    assert len(dist) == expected_count(n)
    return dist


# ------------------------------------------------- donor (independent rebuild)
def _xzs(p, n):
    e = encode(p, n)
    mask = (1 << n) - 1
    return (e >> n) & mask, e & mask, e >> (2 * n)


def donor(state, n: int):
    st = list(state)
    gates_out = []
    feats = {"nCZ": 0, "nY": 0, "nSignX": 0, "nSignZ": 0, "nCN": 0}
    processed = 0

    def emit(g):
        nonlocal st
        st = [conj_pauli(g, p) for p in st]
        gates_out.append(g)

    for q in range(n):
        cands = []
        for p in st:
            x, z, s = _xzs(p, n)
            if (x >> q) & 1 and not (x & processed) and not (z & processed):
                cands.append(((x, z, s), p))
        if cands:
            cands.sort()
            pv = cands[0][1]

            def track(g):
                nonlocal pv
                emit(g)
                pv = conj_pauli(g, pv)

            if pv[1][q] == 2:  # Y at q
                track(("S", q))
                feats["nY"] += 1
            for j in range(n):
                if j == q or (processed >> j) & 1:
                    continue
                if pv[1][j] == 2:
                    track(("S", j))
                    feats["nY"] += 1
                if pv[1][j] == 1:
                    track(("CX", q, j))
                    feats["nCN"] += 1
                elif pv[1][j] == 3:
                    track(("H", j))
                    track(("CX", q, j))
                    track(("H", j))
                    feats["nCZ"] += 1
                    feats["nCN"] += 1
            assert pv[1][q] == 1 and all(pv[1][j] == 0 for j in range(n) if j != q)
            if pv[0]:
                track(("S", q))
                track(("S", q))
                feats["nSignX"] += 1
            track(("H", q))
            assert pv == (0, tuple(3 if j == q else 0 for j in range(n)))
        else:
            zq = tuple(3 if j == q else 0 for j in range(n))
            if (1, zq) in st:
                for g in (("H", q), ("S", q), ("S", q), ("H", q)):
                    emit(g)
                feats["nSignZ"] += 1
            else:
                assert (0, zq) in st
        processed |= 1 << q
    assert tuple(sorted(st)) == start(n)
    inv = {"H": "H", "S": "SDG", "SDG": "S", "CX": "CX"}
    prep = [(inv[g[0]],) + tuple(g[1:]) for g in reversed(gates_out)]
    return prep, sum(COST[g[0]] for g in gates_out), feats


# ------------------------------------------------- structure
def rank_f2(vectors) -> int:
    basis = []
    for v in vectors:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def structure(state, n: int):
    xs = []
    for p in state:
        x, z, s = _xzs(p, n)
        xs.append(x)
    rx = rank_f2(xs)
    full = (1 << n) - 1
    cuts = []
    for sub in range(1, full):
        ca = cb = 0
        for p in state:
            x, z, _ = _xzs(p, n)
            sup = x | z
            if sup & ~sub & full == 0:
                ca += 1
            if sup & sub == 0:
                cb += 1
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
    c = len(parts)
    return rx + 3 * (n - c), rx, c


def literals(feats, cd, lb, rx, c, n):
    return (
        feats["nCZ"] == 0, feats["nSignX"] == 0, feats["nSignZ"] == 0,
        feats["nY"] == 0, cd == lb, cd <= lb + 1, rx <= 1, c == n,
        feats["nCN"] <= n - 1, cd <= 2 * n,
    )


def confusion(flags, labels):
    tp = fp = fn = tn = 0
    for p, l in zip(flags, labels):
        if p and l:
            tp += 1
        elif p:
            fp += 1
        elif l:
            fn += 1
        else:
            tn += 1
    return {"TP": tp, "FP": fp, "FN": fn, "TN": tn, "errors": fp + fn}


# ------------------------------------------------- main verification
def main() -> int:
    raw = json.loads(RESULTS.read_text())
    checks = {}
    checks["schema"] = raw.get("schema") == "orion-qg.qg15_third_family.v1"
    checks["protocol_sha256"] = raw.get("protocol_sha256") == hashlib.sha256(
        PROTOCOL.read_bytes()
    ).hexdigest()
    unsigned = {k: v for k, v in raw.items() if k not in ("result_digest", "timing")}
    checks["result_digest"] = raw.get("result_digest") == hashlib.sha256(
        canonical(unsigned).encode()
    ).hexdigest()

    dists = {}
    recs = {}
    ok_domains = ok_census = ok_lb = True
    for n in (1, 2, 3):
        d = referee(n)
        dists[n] = d
        keys = sorted(state_key(s, n) for s in d)
        enum_sha = hashlib.sha256(
            "\n".join(canonical(list(k)) for k in keys).encode()
        ).hexdigest()
        dom = raw["domains"][f"n{n}"]
        ok_domains &= (
            dom["count"] == len(keys) == expected_count(n)
            and dom["enumeration_sha256"] == enum_sha
            and dom["first_key"] == list(keys[0])
            and dom["last_key"] == list(keys[-1])
            and dom["max_referee_cost"] == max(d.values())
        )
        # donor census
        gaps = {}
        exact = 0
        by_key = {}
        for s, copt in d.items():
            prep, cd, feats = donor(s, n)
            assert apply_circuit(start(n), prep) == s
            lb, rx, c = structure(s, n)
            ok_lb &= lb <= copt <= cd
            gap = cd - copt
            gaps[str(gap)] = gaps.get(str(gap), 0) + 1
            if gap == 0:
                exact += 1
            by_key[state_key(s, n)] = (cd, copt, feats, lb, rx, c)
        recs[n] = by_key
        c1 = raw["component1_regime_map"]["per_n"][f"n{n}"]
        ok_census &= (
            c1["donor_exact"] == exact
            and c1["gap_histogram"] == dict(sorted(gaps.items(), key=lambda kv: int(kv[0])))
            and c1["instances"] == len(d)
        )
    checks["domains_and_enumeration"] = ok_domains
    checks["donor_census"] = ok_census
    checks["lower_bound_validity"] = ok_lb

    # witnesses
    ok_wit = True
    class_order = {"ORDER_TRADE": 1, "PIVOT_TRADE": 2, "ROUTE_TRADE": 3, "GLOBAL_TRADE": 4}
    for w in raw["component2_trades"]["minimal_witnesses"]:
        n = w["n"]
        key = tuple(w["canonical_key"])
        st = tuple(sorted(decode_key(key, n)))
        assert state_key(st, n) == key
        cd, copt, feats, lb, rx, c = recs[n][key]
        ok_wit &= cd == w["C_D"] and copt == w["C_opt"] and feats == w["features"]
        ok_wit &= lb == w["LB"] and rx == w["r_X"] and c == w["c"]
        dc = [tuple(g) for g in w["donor_circuit"]]
        oc = [tuple(g) for g in w["optimal_circuit"]]
        ok_wit &= apply_circuit(start(n), dc) == st and apply_circuit(start(n), oc) == st
        ok_wit &= sum(COST[g[0]] for g in dc) == w["C_D"]
        ok_wit &= sum(COST[g[0]] for g in oc) == w["C_opt"]
        e1, e2, e3 = w["C_E1"], w["C_E2"], w["C_E3"]
        ok_wit &= w["C_D"] >= e1 >= e2 >= e3 >= w["C_opt"]
        lvl = class_order[w["trade_class"]]
        vals = {1: e1, 2: e2, 3: e3}
        for l in (1, 2, 3):
            if l < lvl:
                ok_wit &= vals[l] > w["C_opt"]
            else:
                ok_wit &= (vals[l] == w["C_opt"]) if lvl <= 3 else (vals[l] > w["C_opt"])
    checks["witness_recompute"] = ok_wit

    # predicate confusion matrices on n=1..3
    sel_idx = tuple(raw["component4_predicate"]["selected_literal_indices"])
    ladder_defs = {"P0": (0,), "P1": (0, 1, 2), "P2": (4,), "selected": sel_idx}
    ok_conf = True
    for pname, n in (("n1", 1), ("n2", 2), ("n3_fit", 3)):
        rows = []
        for key in sorted(recs[n]):
            cd, copt, feats, lb, rx, c = recs[n][key]
            rows.append((literals(feats, cd, lb, rx, c, n), copt == cd))
        labels = [l for _, l in rows]
        for name, idxs in ladder_defs.items():
            got = confusion([all(r[i] for i in idxs) for r, _ in rows], labels)
            ok_conf &= raw["component4_predicate"]["confusion_matrices"][pname][name] == got
    checks["confusion_matrices_n123"] = ok_conf

    # prospective: regenerate panel, recompute predictions, verify stamp, referee n=4
    rng = np.random.default_rng(PANEL_SEED)
    panel = []
    seen = set()
    while len(panel) < 120:
        s = start(4)
        for _ in range(24):
            kind = int(rng.integers(0, 4))
            if kind == 3:
                cq = int(rng.integers(0, 4))
                u = int(rng.integers(0, 3))
                t = [x for x in range(4) if x != cq][u]
                g = ("CX", cq, t)
            else:
                g = (["H", "S", "SDG"][kind], int(rng.integers(0, 4)))
            s = apply_gate(s, g)
        if s not in seen:
            seen.add(s)
            panel.append(s)
    panel_keys = [state_key(s, 4) for s in panel]
    panel_sha = hashlib.sha256(
        "\n".join(canonical(list(k)) for k in panel_keys).encode()
    ).hexdigest()
    checks["panel_regeneration"] = (
        raw["component5_prospective"]["panel"]["panel_keys_sha256"] == panel_sha
    )
    gap_table = raw["component5_prospective"]["gap_forecast_table"]
    preds = []
    panel_info = {}
    for idx, s in enumerate(panel):
        prep, cd, feats = donor(s, 4)
        assert apply_circuit(start(4), prep) == s
        lb, rx, c = structure(s, 4)
        lits = literals(feats, cd, lb, rx, c, 4)
        pred_true = all(lits[i] for i in sel_idx)
        tk = f"{feats['nCZ']},{feats['nSignX']},{feats['nSignZ']},{feats['nY']}"
        pred_gap = 0 if pred_true else gap_table.get(tk, 0)
        pred_cost = max(lb, cd - pred_gap)
        preds.append({
            "index": idx, "canonical_key": list(panel_keys[idx]), "C_D": cd,
            "LB": lb, "r_X": rx, "c": c, "features": feats,
            "predicted_donor_exact": pred_true, "predicted_gap": pred_gap,
            "predicted_C_opt": pred_cost,
        })
        panel_info[panel_keys[idx]] = (cd, feats, lb, rx, c, pred_true, pred_cost)
    checks["predictions_sha256"] = (
        hashlib.sha256(canonical(preds).encode()).hexdigest()
        == raw["predictions_sha256"]
        == raw["component5_prospective"]["predictions_sha256"]
    )
    d4 = referee(4)
    checks["n4_state_space"] = len(d4) == expected_count(4) == raw[
        "component5_prospective"]["panel"]["n4_expected"]
    key4 = {state_key(s, 4): v for s, v in d4.items()}
    regime_ok = cost_ok = 0
    rows4 = []
    lb_ok4 = True
    for k in panel_keys:
        cd, feats, lb, rx, c, pred_true, pred_cost = panel_info[k]
        copt = key4[k]
        lb_ok4 &= lb <= copt <= cd
        if pred_true == (copt == cd):
            regime_ok += 1
        if pred_cost == copt:
            cost_ok += 1
        rows4.append((literals(feats, cd, lb, rx, c, 4), copt == cd))
    c5 = raw["component5_prospective"]
    checks["prospective_counts"] = (
        c5["regime_correct"] == regime_ok and c5["cost_correct"] == cost_ok
        and c5["regime_correct"] + c5["regime_refuted"] == 120
        and c5["cost_correct"] + c5["cost_refuted"] == 120
        and c5["predictions_stamped_before_referee"] is True
    )
    checks["lower_bound_validity_n4"] = lb_ok4
    labels4 = [l for _, l in rows4]
    ok4 = True
    for name, idxs in ladder_defs.items():
        got = confusion([all(r[i] for i in idxs) for r, _ in rows4], labels4)
        ok4 &= raw["component4_predicate"]["confusion_matrices"]["n4_panel_heldout"][name] == got
    checks["confusion_matrix_n4"] = ok4
    checks["gates_all_true"] = all(
        v is True for k, v in raw["gates"].items() if isinstance(v, bool)
    )
    checks["not_r6"] = raw.get("r6_authority") is False and raw.get("novelty_credit") is False
    checks["terminal_consistent"] = raw.get("terminal") == raw.get("transfer_verdict") and (
        raw.get("terminal") == "TEMPLATE_TRANSFERRED"
        or str(raw.get("terminal", "")).startswith("TEMPLATE_PARTIAL__")
    )

    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    print("ORIONQG_QG15_GENERIC_VERIFY=" + canonical({
        "decision": decision,
        "checks": checks,
        "source_result_digest": raw.get("result_digest"),
    }))
    return 0 if decision == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
