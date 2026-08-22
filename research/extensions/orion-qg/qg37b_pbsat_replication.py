#!/usr/bin/env python3
"""QG-37b: independent exact physical-probe PB/DPLL replication.

This lane reconstructs the response universe from phase-free F2^2/F3 primitives.
It never imports QG-37 production MILP state. A production witness, when present,
is used only as an upper bound after an independent distance-three check.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
QGDIR = ROOT / "research/extensions/orion-qg"
DEV = ROOT / "development/orion-qg-regime-geometry"
QG35 = QGDIR / "QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json"
PROTO = DEV / "QG37B_INDEPENDENT_PBSAT_REPLICATION_PROTOCOL_V1.md"
BIND = DEV / "QG37B_EXECUTION_BINDING_2026-08-22.md"
DEFAULT_PROD = ROOT / "artifacts/orion-qg-qg37-robust.json"
OUT = ROOT / "artifacts/orion-qg-qg37b-pbsat.json"
TOKEN = "ORIONQG_QG37B="
EXACT = "QG37B_INDEPENDENT_EXACT_ROBUST_MINIMA_MACHINE_CHECKED"
DISAGREE = "QG37B_INDEPENDENT_ROBUST_WITNESS_DISAGREEMENT"
CANNOT = "QG37B_CANNOT_CHECK"

BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
CODE = {b: i for i, b in enumerate(BITS)}


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_obj(v: Any) -> str:
    return hashlib.sha256(canon(v).encode()).hexdigest()


def valid_digest(d: dict[str, Any]) -> bool:
    got = d.get("result_digest")
    if not isinstance(got, str):
        return False
    return got == digest_obj({k: v for k, v in d.items() if k != "result_digest"})


def file_sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def mul(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return CODE[(ax ^ bx, az ^ bz)]


def sy(a: int, b: int) -> int:
    ax, az = BITS[a]
    bx, bz = BITS[b]
    return (ax * bz + az * bx) & 1


def f3(a: int, b: int, c: int) -> int:
    return 1 if a == b == c != 0 else int(a != 0) + int(b != 0) + int(c != 0)


def autos():
    return [(0,) + p for p in itertools.permutations((1, 2, 3))]


def orbit(t, aa):
    return {tuple(a[x] for x in t) for a in aa}


def perm(t, p):
    out = []
    for j in range(3):
        a, b = t[2 * j], t[2 * j + 1]
        out.extend((a, b) if p[j] == 0 else (b, a))
    return tuple(out)


def baseline(t, p):
    q = perm(t, p)
    return f3(q[0], q[2], q[4]) + f3(q[1], q[3], q[5])


def aux48():
    pairs = [(a, b) for a in range(1, 4) for b in range(1, 4) if sy(a, b) == 1]
    rows = []
    for ps in itertools.product(pairs, repeat=3):
        fr = tuple(x for z in ps for x in z)
        for tag in range(4):
            l0, l1 = sy(tag, fr[0]), sy(tag, fr[1])
            ok = l0 != l1 and all(
                sy(tag, fr[2 * j]) == l0 and sy(tag, fr[2 * j + 1]) == l1
                for j in (1, 2)
            )
            if ok:
                rows.append((fr, tag))
    return rows


def structural(fr, tag):
    raw = sum(2 * int(fr[2 * j] != 0) + 4 * int(fr[2 * j + 1] != 0) for j in range(3))
    return raw + 2 * int(tag != 0) - 18


def restore(pt, fr):
    r = [mul(pt[i], fr[i]) for i in range(6)]
    return f3(r[0], r[2], r[4]) + f3(r[1], r[3], r[5])


def response(rep, ps, aux):
    out = []
    for p in ps:
        pt = perm(rep, p)
        b = baseline(rep, p)
        for fr, tag in aux:
            out.append(structural(fr, tag) + restore(pt, fr) - b)
    return tuple(out)


def make_groups(vals):
    d = defaultdict(list)
    for i, v in enumerate(vals):
        d[v].append(i)
    return [d[k] for k in sorted(d, key=canon)]


def construct_universe():
    aa = autos()
    ps = list(itertools.product((0, 1), repeat=3))
    aux = aux48()
    obs: dict[tuple[int, ...], set[tuple[int, ...]]] = {}
    for t in itertools.product(range(4), repeat=6):
        o = orbit(t, aa)
        r = min(o)
        obs.setdefault(r, set()).update(o)
    reps = sorted(obs)
    bulk = [tuple(baseline(r, p) for p in ps[:4]) for r in reps]
    mat = np.array([response(r, ps, aux) for r in reps], dtype=np.int16)
    spectrum = [tuple(sorted(int(x) for x in row)) for row in mat]
    joint = make_groups([(bulk[i], spectrum[i]) for i in range(len(reps))])
    return reps, mat, joint


def class_hist(groups):
    return {str(k): int(v) for k, v in sorted(Counter(len(g) for g in groups).items())}


def model(group, mat):
    pairs = list(itertools.combinations(group, 2))
    covers = [0] * mat.shape[1]
    candidates = [0] * len(pairs)
    for j, (a, b) in enumerate(pairs):
        diff = np.flatnonzero(mat[a] != mat[b])
        if len(diff) == 0:
            raise AssertionError("indistinguishable pair inside joint class")
        bit = 1 << j
        pmask = 0
        for p in diff:
            pi = int(p)
            covers[pi] |= bit
            pmask |= 1 << pi
        candidates[j] = pmask
    active = 0
    for p, c in enumerate(covers):
        if c:
            active |= 1 << p
    return pairs, tuple(covers), tuple(candidates), active


def apply_probe(n1: int, n2: int, n3: int, cov: int):
    # n_r marks pairs whose residual demand is at least r.
    return (
        (n1 & ~cov) | (n2 & cov),
        (n2 & ~cov) | (n3 & cov),
        n3 & ~cov,
    )


def marginal(n1: int, n2: int, n3: int, cov: int) -> int:
    return (n1 & cov).bit_count() + (n2 & cov).bit_count() + (n3 & cov).bit_count()


def verify_distance(group, mat, selected):
    if len(group) <= 1:
        return {"minimum_distance": None, "radius1_unique": True, "distance_histogram": {}}
    ds = []
    for a, b in itertools.combinations(group, 2):
        ds.append(sum(int(mat[a, p] != mat[b, p]) for p in selected))
    md = min(ds)
    hist = {str(k): int(v) for k, v in sorted(Counter(ds).items())}
    # min distance >=3 is equivalent to unique correction of one arbitrary coordinate.
    # We also enumerate radius-0/1 words as an implementation binder.
    seen = {}
    unique = True
    for i in group:
        w = tuple(int(mat[i, p]) for p in selected)
        variants = {w}
        for pos, p in enumerate(selected):
            vals = sorted({int(mat[j, p]) for j in group})
            foreign = (max(vals) + 1) if vals else 0
            for sym in vals + [foreign]:
                if sym != w[pos]:
                    z = list(w)
                    z[pos] = sym
                    variants.add(tuple(z))
        for z in variants:
            old = seen.get(z)
            if old is not None and old != i:
                unique = False
                break
            seen[z] = i
        if not unique:
            break
    return {"minimum_distance": int(md), "radius1_unique": bool(unique), "distance_histogram": hist}


def greedy_upper(covers, active, pair_count):
    n1 = n2 = n3 = (1 << pair_count) - 1
    avail = active
    selected = []
    while n1:
        best = None
        x = avail
        while x:
            low = x & -x
            p = low.bit_length() - 1
            x -= low
            gain = marginal(n1, n2, n3, covers[p])
            cand = (-gain, p)
            if best is None or cand < best:
                best = cand
        if best is None or -best[0] <= 0:
            return None
        p = best[1]
        selected.append(p)
        avail &= ~(1 << p)
        n1, n2, n3 = apply_probe(n1, n2, n3, covers[p])
    return selected


def exact_decision(covers, candidates, active, pair_count, k, seconds):
    full = (1 << pair_count) - 1
    deadline = time.monotonic() + seconds
    dead = set()
    nodes = 0

    sys.setrecursionlimit(5000)

    def rec(avail, n1, n2, n3, slots):
        nonlocal nodes
        nodes += 1
        if nodes % 1024 == 0 and time.monotonic() > deadline:
            raise TimeoutError
        if n1 == 0:
            return ()
        if slots <= 0:
            return None
        state = (avail, n1, n2, n3, slots)
        if state in dead:
            return None

        # Propagate constraints whose remaining candidate count equals residual demand.
        while True:
            forced = 0
            best = None
            x = n1
            impossible = False
            while x:
                low = x & -x
                j = low.bit_length() - 1
                x -= low
                need = 1 + int(bool(n2 & low)) + int(bool(n3 & low))
                cm = candidates[j] & avail
                cnt = cm.bit_count()
                if cnt < need:
                    impossible = True
                    break
                if cnt == need:
                    forced |= cm
                slack = cnt - need
                cand = (slack, cnt, -need, j)
                if best is None or cand < best:
                    best = cand
            if impossible:
                dead.add(state)
                return None
            if not forced:
                break
            if forced.bit_count() > slots:
                dead.add(state)
                return None
            chosen = []
            y = forced
            while y:
                low = y & -y
                p = low.bit_length() - 1
                y -= low
                if not (avail & low):
                    continue
                chosen.append(p)
                avail &= ~low
                slots -= 1
                n1, n2, n3 = apply_probe(n1, n2, n3, covers[p])
                if n1 == 0:
                    return tuple(chosen)
                if slots < 0:
                    dead.add(state)
                    return None
            tail = rec(avail, n1, n2, n3, slots)
            if tail is not None:
                return tuple(chosen) + tail
            dead.add(state)
            return None

        total_need = n1.bit_count() + n2.bit_count() + n3.bit_count()
        max_gain = 0
        x = avail
        while x:
            low = x & -x
            p = low.bit_length() - 1
            x -= low
            g = marginal(n1, n2, n3, covers[p])
            if g > max_gain:
                max_gain = g
        if max_gain == 0 or (total_need + max_gain - 1) // max_gain > slots:
            dead.add(state)
            return None

        # Branch on one physical Boolean variable from the tightest unsatisfied PB row.
        assert best is not None
        j = best[3]
        cm = candidates[j] & avail
        plist = []
        y = cm
        while y:
            low = y & -y
            p = low.bit_length() - 1
            y -= low
            plist.append((-marginal(n1, n2, n3, covers[p]), p))
        plist.sort()
        p = plist[0][1]
        bit = 1 << p

        a1, a2, a3 = apply_probe(n1, n2, n3, covers[p])
        tail = rec(avail & ~bit, a1, a2, a3, slots - 1)
        if tail is not None:
            return (p,) + tail
        tail = rec(avail & ~bit, n1, n2, n3, slots)
        if tail is not None:
            return tail
        dead.add(state)
        return None

    try:
        sol = rec(active, full, full, full, k)
        return {"status": "SAT" if sol is not None else "UNSAT", "selected": list(sol or ()), "nodes": nodes, "memo_dead": len(dead)}
    except TimeoutError:
        return {"status": "UNKNOWN", "selected": [], "nodes": nodes, "memo_dead": len(dead)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    ap.add_argument("--production", type=Path, default=DEFAULT_PROD)
    ap.add_argument("--decision-seconds", type=float, default=90.0)
    args = ap.parse_args()

    q35 = json.loads(QG35.read_text())
    q35_ok = (
        q35.get("EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY") is True
        and q35.get("terminal") == "QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED"
        and len(q35.get("class_minima", [])) == 92
    )
    prod = json.loads(args.production.read_text()) if args.production.exists() else None
    reps, mat, joint = construct_universe()
    universe_ok = len(reps) == 715 and mat.shape == (715, 384) and len(joint) == 92
    prod_rows = prod.get("classes", []) if isinstance(prod, dict) else []

    rows = []
    all_exact = q35_ok and universe_ok
    disagreement = False
    for idx, group in enumerate(joint):
        f = int(q35["class_minima"][idx])
        floor = 0 if len(group) <= 1 else f + 2
        pairs, covers, candidates, active = model(group, mat)
        greedy = [] if len(group) <= 1 else greedy_upper(covers, active, len(pairs))
        upper = greedy
        upper_source = "INDEPENDENT_GREEDY"

        if idx < len(prod_rows):
            cand = [int(x) for x in prod_rows[idx].get("selected_probe_indices", [])]
            cert = verify_distance(group, mat, cand)
            if (len(group) <= 1 and not cand) or (cand and cert["minimum_distance"] is not None and cert["minimum_distance"] >= 3 and cert["radius1_unique"]):
                if upper is None or len(cand) < len(upper):
                    upper = cand
                    upper_source = "PRODUCTION_WITNESS_RECHECKED_ONLY"

        if len(group) <= 1:
            minimum, selected, proof, decisions = 0, [], "SINGLETON", []
        elif upper is None:
            minimum, selected, proof, decisions = None, [], "NO_UPPER_BOUND", []
        elif len(upper) == floor:
            cert = verify_distance(group, mat, upper)
            if cert["minimum_distance"] >= 3 and cert["radius1_unique"]:
                minimum, selected, proof, decisions = floor, upper, "PUNCTURING_FLOOR_PLUS_DISTANCE3_WITNESS", []
            else:
                minimum, selected, proof, decisions = None, [], "INVALID_UPPER", []
        else:
            minimum = None
            selected = []
            decisions = []
            proof = "PB_DPLL_CARDINALITY_SEARCH"
            for k in range(floor, len(upper) + 1):
                dec = exact_decision(covers, candidates, active, len(pairs), k, args.decision_seconds)
                decisions.append({"k": k, **dec})
                if dec["status"] == "UNKNOWN":
                    break
                if dec["status"] == "SAT":
                    cert = verify_distance(group, mat, dec["selected"])
                    if cert["minimum_distance"] is not None and cert["minimum_distance"] >= 3 and cert["radius1_unique"]:
                        minimum, selected = k, dec["selected"]
                    break

        exact = minimum is not None
        if not exact:
            all_exact = False
        cert = verify_distance(group, mat, selected) if exact else None
        prod_min = None
        if idx < len(prod_rows) and prod_rows[idx].get("D3_status") == "EXACT":
            prod_min = prod_rows[idx].get("D3_minimum")
            if exact and prod_min != minimum:
                disagreement = True

        rows.append({
            "class_index": idx,
            "class_size": len(group),
            "D1_noiseless_minimum": f,
            "puncturing_floor": floor,
            "status": "EXACT" if exact else "CANNOT_CHECK",
            "D3_minimum": minimum,
            "selected_probe_indices": selected,
            "proof": proof,
            "upper_source": upper_source,
            "upper_cardinality": len(upper) if upper is not None else None,
            "distance_certificate": cert,
            "decisions": decisions,
            "production_claimed_minimum": prod_min,
        })

    minima = [r["D3_minimum"] for r in rows]
    if disagreement:
        terminal = DISAGREE
    elif all_exact:
        terminal = EXACT
    else:
        terminal = CANNOT
    exceptional = [r["class_index"] for r in rows if r["D3_minimum"] is not None and r["class_size"] > 1 and r["D3_minimum"] > r["puncturing_floor"]]
    out = {
        "schema": "ORIONQG.QG37B.IndependentPBSAT.v1",
        "issue": "SzeChunYiu/ORION#937",
        "terminal": terminal,
        "protocol_sha256": file_sha(PROTO),
        "binding_sha256": file_sha(BIND),
        "qg35_parent_sha256": file_sha(QG35),
        "parent_checks": {"qg35_exact": q35_ok, "universe": universe_ok},
        "universe": {"orbits": len(reps), "physical_probes": int(mat.shape[1]), "joint_classes": len(joint), "joint_class_size_histogram": class_hist(joint)},
        "distance_target": 3,
        "classes": rows,
        "exact_minima_vector": minima if all_exact else None,
        "R1_star": max(minima) if all_exact else None,
        "strict_puncturing_exception_class_indices": exceptional,
        "all_92_exact": bool(all_exact),
        "production_disagreement": bool(disagreement),
        "INDEPENDENT_ROBUST_MINIMA_AUTHORITY": bool(all_exact and not disagreement),
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "STOCHASTIC_PHYSICAL_ERROR_RATE": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "GENERIC_CODING_SAT_NOVELTY": False,
        "COMPILER_RUNTIME_ADVANTAGE": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    out["result_digest"] = digest_obj(out)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"terminal": terminal, "all_exact": all_exact, "R1_star": out["R1_star"], "exceptions": exceptional, "disagreement": disagreement, "result_digest": out["result_digest"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
