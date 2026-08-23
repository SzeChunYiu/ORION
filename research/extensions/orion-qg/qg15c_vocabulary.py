#!/usr/bin/env python3
"""QG-15c feature-vocabulary analyzer.

Frozen protocol:
development/orion-qg-regime-geometry/QG15C_VOCABULARY_PROTOCOL_V1.md
(sha256 recorded in RESULTS; frozen BEFORE any QG-15c outcome).

QG-15b measured a budget- and grid-independent floor of 43/1146 on the StabPrep
donor-exact boundary: 12 cells of the 13-feature vocabulary V1 carry both labels.
The reopen adjudication classified that FAILED_DEFINITION. This lane (a) diagnoses
the collisions, (b) freezes an enlarged, schedule/path-aware vocabulary V2 (33
integer features, V1 verbatim as a prefix) motivated by that diagnosis, and (c)
re-runs QG-15b's exact minimum-error search machinery over V2 on the same n<=3
domain (1146 instances), reporting the new mixed-cell count and error floor.

Committed machinery imported unmodified: qg15_third_family (referee, donor,
micro-steps, ladder, structure, panel) and qg15b_predicate_language (the Arm
literal/conjunction/branch-and-bound machinery, monkey-patched ONLY in its frozen
lattice/node-budget module constants, per protocol section 5 -- no file is edited).

Stdout: two deterministic receipt lines (stage digest first, then the receipt).
Stderr: stage runtimes (the only non-deterministic output).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qg15_third_family as qg15  # noqa: E402  (committed, unmodified)
import qg15b_predicate_language as qg15b  # noqa: E402  (committed, unmodified)

REPO = Path(__file__).resolve().parents[3]
PROTOCOL = (
    REPO / "development" / "orion-qg-regime-geometry"
    / "QG15C_VOCABULARY_PROTOCOL_V1.md"
)
HERE = Path(__file__).resolve().parent
QG15_RESULTS = HERE / "QG15_THIRD_FAMILY_RESULTS.json"
QG15B_RESULTS = HERE / "QG15B_PREDICATE_LANGUAGE_RESULTS.json"
RESULTS_PATH = HERE / "QG15C_VOCABULARY_RESULTS.json"
SCHEMA = "orion-qg.qg15c_vocabulary.v1"
CHECKOUT_REVISION = "f7d6898ab0fa21e7684ac4a8ef8e5b94322b2800"

# ---- frozen search lattice (protocol s.5); applied to the committed qg15b machinery
K_LATTICE = (1, 2)
D_LATTICE = (1, 2, 3, 4, 5, 6)
NODE_BUDGET = 3_000_000
MIXED_CELL_CAP = 20
SUB_LATTICE_NOTE = "K<=2, D<=6; K=3 excluded by pre-freeze runtime arithmetic"

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

_HELDOUT_UNLOCKED = False   # G5 code-structural held-out discipline flag
_STUB_TRIGGERED = False     # G4: set if any referee entry point is called while stubbed


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def log_time(label, t0):
    t1 = time.perf_counter()
    print(f"[qg15c] {label}: {t1 - t0:.2f}s", file=sys.stderr)
    return t1


# ------------------------------------------------------- G4 referee stub context
class RefereeStub:
    """Replaces the referee entry points with a raising stub for the duration of
    feature computation.  Any feature that needs the optimum is circular and
    inadmissible; this makes that structurally impossible rather than asserted."""

    NAMES = ("referee", "referee_lex", "extract_optimal_circuit")

    def __enter__(self):
        self.saved = {nm: getattr(qg15, nm) for nm in self.NAMES}

        def stub(*_a, **_k):
            global _STUB_TRIGGERED
            _STUB_TRIGGERED = True
            raise AssertionError("G4 violated: referee called during feature computation")

        for nm in self.NAMES:
            setattr(qg15, nm, stub)
        return self

    def __exit__(self, *exc):
        for nm, fn in self.saved.items():
            setattr(qg15, nm, fn)
        return False


# ------------------------------------------------------------- schedule trace
ZERO_EV = {"nCZ": 0, "nY": 0, "nSignX": 0, "nSignZ": 0, "nCN": 0}


def donor_trace(state, n):
    """Replay the frozen GE donor, recording the per-step schedule (protocol 3.1)."""
    st = list(state)
    processed = 0
    steps = []
    for q in range(n):
        rho = qg15.r_x(tuple(sorted(st)), n)
        cands = qg15.x_candidates(st, q, processed, n)
        if cands:
            pivot = cands[0]
            gates, st, ev = qg15.micro_steps(st, pivot, q, "X", processed, n)
            route = "X"
        else:
            zq = 1 << q
            neg = (1 << (2 * n)) | zq
            if neg in st:
                pivot = neg
                gates, st, ev = qg15.micro_steps(st, neg, q, "Z", processed, n)
                route = "Z"
            else:
                assert zq in st
                pivot, gates, ev, route = zq, [], dict(ZERO_EV), "N"
        px, pz = qg15._xof(pivot, n), qg15._zof(pivot, n)
        steps.append({
            "cost": qg15.circuit_cost(gates),
            "ev": {k: ev.get(k, 0) for k in ZERO_EV},
            "wt": sum(1 for j in range(n) if ((px >> j) & 1) or ((pz >> j) & 1)),
            "sign": qg15._sof(pivot, n),
            "route": route,
            "rho": rho,
        })
        processed |= 1 << q
    assert tuple(sorted(st)) == qg15.start_state(n), "GE donor did not disentangle"
    return steps


def tensor_parts(state, n):
    """Frozen tensor_factors cut, returned as qubit masks."""
    full = (1 << n) - 1
    cuts = []
    for sub in range(1, full):
        ca = sum(1 for e in state
                 if ((qg15._xof(e, n) | qg15._zof(e, n)) & ~sub & full) == 0)
        cb = sum(1 for e in state
                 if ((qg15._xof(e, n) | qg15._zof(e, n)) & sub) == 0)
        if (ca.bit_length() - 1) + (cb.bit_length() - 1) == n:
            cuts.append(sub)
    parts = [full]
    for cut in cuts:
        nxt = []
        for p in parts:
            a, b = p & cut, p & ~cut & full
            if a:
                nxt.append(a)
            if b:
                nxt.append(b)
        parts = nxt
    return parts


def restrict(state, part, n):
    """Restrict the state to one tensor factor; qubits relabelled ascending."""
    qs = [j for j in range(n) if (part >> j) & 1]
    m = len(qs)
    full = (1 << n) - 1
    sub = set()
    for e in state:
        x, z = qg15._xof(e, n), qg15._zof(e, n)
        if ((x | z) & ~part & full) != 0:
            continue
        nx = nz = 0
        for i, j in enumerate(qs):
            nx |= ((x >> j) & 1) << i
            nz |= ((z >> j) & 1) << i
        sub.add((qg15._sof(e, n) << (2 * m)) | (nx << m) | nz)
    sub = tuple(sorted(sub))
    assert len(sub) == 1 << m, "tensor restriction is not a stabilizer state"
    return sub, m


def feature_vectors(state, n):
    """Returns (v1_tuple, v2_tuple). Referee-free by construction (gate G4)."""
    prep, cd, feats, _dis = qg15.donor(state, n)
    assert qg15.apply_circuit(qg15.start_state(n), prep, n) == state, "G2 donor validity"
    lb, rx, c = qg15.lower_bound(state, n)
    v1 = (feats["nCZ"], feats["nY"], feats["nSignX"], feats["nSignZ"], feats["nCN"],
          cd, rx, c, lb, cd - lb, n - c, feats["nCN"] - (n - 1), cd - 2 * n)

    steps = donor_trace(state, n)
    costs = [s["cost"] for s in steps]
    assert sum(costs) == cd, "G3 schedule-trace cost consistency"
    agg = {k: sum(s["ev"][k] for s in steps) for k in ZERO_EV}
    assert agg == feats, "G3 schedule-trace event consistency"

    cmax = max(costs)
    argmax = costs.index(cmax)
    descents = sum(1 for q in range(n - 1) if costs[q] > costs[q + 1])
    moment = sum(q * costs[q] for q in range(n))
    ge4 = sum(1 for x in costs if x >= 4)
    zero = sum(1 for x in costs if x == 0)
    ev_tot = [sum(s["ev"].values()) for s in steps]
    y = [s["ev"]["nY"] for s in steps]
    sg = [s["ev"]["nSignX"] + s["ev"]["nSignZ"] for s in steps]
    y_and_sign = sum(1 for q in range(n) if y[q] >= 1 and sg[q] >= 1)
    y_only = sum(1 for q in range(n) if y[q] >= 1 and sg[q] == 0)
    sign_only = sum(1 for q in range(n) if y[q] == 0 and sg[q] >= 1)
    piv_sign = sum(s["sign"] for s in steps)
    piv_wt = max(s["wt"] for s in steps)
    route_z = sum(1 for s in steps if s["route"] == "Z")
    rho = [s["rho"] for s in steps] + [0]
    rank_drops = sum(1 for q in range(n) if rho[q] > rho[q + 1])

    parts = tensor_parts(state, n)
    fac_size = 0
    fac_cost = 0
    for p in parts:
        sub, m = restrict(state, p, n)
        fac_size = max(fac_size, m)
        fac_cost = max(fac_cost, qg15.donor(sub, m)[1])

    ce3 = qg15.ladder_min(state, n, True, True, {})[0]
    assert ce3 <= cd, "ladder enlargement must not exceed the donor"

    v2 = v1 + (cmax, argmax, costs[0], costs[n - 1], descents, moment, ge4, zero,
               max(ev_tot), y_and_sign, y_only, sign_only, piv_sign, piv_wt,
               route_z, rank_drops, fac_size, fac_cost, ce3, cd - ce3)
    assert len(v2) == 33
    return v1, v2, cd, lb, costs


# --------------------------------------------------------------------- helpers
def confusion(flags, labels):
    return qg15b.confusion(flags, labels)


def cell_table(rows, idx):
    """rows: list of (v1, v2, label, ...). idx selects which vector."""
    counts = {}
    for r in rows:
        cell = counts.setdefault(r[idx], [0, 0])
        cell[0 if r[2] else 1] += 1
    cells = sorted(counts.keys())
    pos = [counts[v][0] for v in cells]
    neg = [counts[v][1] for v in cells]
    mixed = [i for i, (p, q) in enumerate(zip(pos, neg)) if p > 0 and q > 0]
    floor = sum(min(p, q) for p, q in zip(pos, neg))
    return cells, pos, neg, mixed, floor


def permutation_related(a, na, b, nb):
    if na != nb:
        return False
    n = na
    for perm in itertools.permutations(range(n)):
        out = []
        for e in a:
            x, z, s = qg15._xof(e, n), qg15._zof(e, n), qg15._sof(e, n)
            nx = nz = 0
            for j in range(n):
                nx |= ((x >> j) & 1) << perm[j]
                nz |= ((z >> j) & 1) << perm[j]
            out.append((s << (2 * n)) | (nx << n) | nz)
        if tuple(sorted(out)) == tuple(b):
            return True
    return False


def weight_enum(state, n):
    w = {}
    for e in state:
        x, z = qg15._xof(e, n), qg15._zof(e, n)
        wt = sum(1 for j in range(n) if ((x >> j) & 1) or ((z >> j) & 1))
        w[wt] = w.get(wt, 0) + 1
    return {str(k): v for k, v in sorted(w.items())}


def neg_census(state, n):
    return sum(1 for e in state if qg15._sof(e, n))


def factor_sizes(state, n):
    return sorted(bin(p).count("1") for p in tensor_parts(state, n))


def pair_record(pos_row, neg_row):
    """A minimal distinguishing pair with its explicit structural difference."""
    def side(r):
        n, key = r[3], r[4]
        return {
            "n": n,
            "canonical_key": list(key),
            "pauli": [qg15.pauli_str(e, n) for e in key],
            "C_D": r[5],
            "C_opt": r[6],
            "donor_step_cost_profile": list(r[7]),
            "tensor_factor_sizes": factor_sizes(key, n),
            "weight_enumerator": weight_enum(key, n),
            "negative_sign_census": neg_census(key, n),
        }
    p, q = side(pos_row), side(neg_row)
    cp, cq = p["donor_step_cost_profile"], q["donor_step_cost_profile"]
    if cp == cq:
        diff = (f"donor step-cost profiles are IDENTICAL ({cp}); the whole frozen "
                "schedule-shape block is blind to this pair, which is therefore not "
                "separated by any statistic of the donor's per-step cost sequence")
    elif sorted(cp) == sorted(cq):
        diff = ("donor step-cost profiles are ORDER-distinct permutations of one "
                f"another: {cp} (donor-exact) vs {cq} (trade); every order-insensitive "
                "summary of the schedule is blind to this pair")
    else:
        diff = ("donor step-cost MULTISETS differ: "
                f"{cp} (donor-exact) vs {cq} (trade); the aggregate event counters and "
                "the total C_D coincide, so V1 sees one point")
    return {
        "donor_exact_member": p,
        "trade_member": q,
        "trade_gap_C_D_minus_C_opt": q["C_D"] - q["C_opt"],
        "structural_difference_V1_cannot_see": diff,
        "profiles_identical": cp == cq,
        "profiles_equal_as_multisets": sorted(cp) == sorted(cq),
        "qubit_permutation_related": permutation_related(
            tuple(p["canonical_key"]), p["n"], tuple(q["canonical_key"]), q["n"]),
        "same_tensor_factor_sizes": p["tensor_factor_sizes"] == q["tensor_factor_sizes"],
        "same_weight_enumerator": p["weight_enumerator"] == q["weight_enumerator"],
        "same_negative_sign_census":
            p["negative_sign_census"] == q["negative_sign_census"],
    }


def cell_report(cells, pos, neg, mixed, rows, idx, feature_names, cap):
    """Serialize up to `cap` mixed cells with a minimal distinguishing pair each."""
    by_cell = {}
    for r in rows:
        by_cell.setdefault(r[idx], []).append(r)
    out = []
    for i in mixed[:cap]:
        vec = cells[i]
        members = sorted(by_cell[vec], key=lambda r: (r[3], r[4]))
        pm = [r for r in members if r[2]]
        nm = [r for r in members if not r[2]]
        out.append({
            "feature_vector": dict(zip(feature_names, vec)),
            "pos": pos[i],
            "neg": neg[i],
            "n_values": sorted({r[3] for r in members}),
            "trade_gaps": sorted({r[5] - r[6] for r in nm}),
            "minimal_distinguishing_pair": pair_record(pm[0], nm[0]),
        })
    return out


# ------------------------------------------------------------------------ main
def main() -> int:
    global _HELDOUT_UNLOCKED
    t0 = time.perf_counter()
    timing = {}
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    qg15_res = json.loads(QG15_RESULTS.read_text())
    qg15b_res = json.loads(QG15B_RESULTS.read_text())

    # ---- stage A: labels from the committed referee, then referee-free features
    ta = time.perf_counter()
    dists = {n: qg15.referee(n) for n in (1, 2, 3)}
    rows = []          # (v1, v2, label, n, key, C_D, C_opt, step_costs)
    with RefereeStub():
        for n in (1, 2, 3):
            for key in sorted(dists[n].keys()):
                v1, v2, cd, lb, costs = feature_vectors(key, n)
                copt = dists[n][key]
                assert lb <= copt <= cd, "G2 lower-bound sandwich"
                rows.append((v1, v2, copt == cd, n, key, cd, copt, tuple(costs)))
    assert not _STUB_TRIGGERED, "G4 violated"
    assert len(rows) == 1146
    ta = log_time("A ground truth + V2 features", ta)
    timing["A_features"] = round(ta - t0, 3)

    # ---- stage B: G1 receipt bindings (QG-15 and QG-15b, verbatim)
    per_n_rows = {n: [r for r in rows if r[3] == n] for n in (1, 2, 3)}
    censuses = {n: sum(1 for r in per_n_rows[n] if r[2]) for n in (1, 2, 3)}
    c1 = qg15_res["component1_regime_map"]["per_n"]
    for n in (1, 2, 3):
        assert c1[f"n{n}"]["instances"] == len(per_n_rows[n])
        assert c1[f"n{n}"]["donor_exact"] == censuses[n], ("G1 census", n)
    conf_store = qg15_res["component4_predicate"]["confusion_matrices"]
    key_map = {1: "n1", 2: "n2", 3: "n3_fit"}
    for n in (1, 2, 3):
        labs = [r[2] for r in per_n_rows[n]]
        for name in ("P0", "P1", "P2", "selected"):
            got = confusion(
                [qg15b.qg15_baseline_flags(r[0], name) for r in per_n_rows[n]], labs)
            assert got == conf_store[key_map[n]][name], ("G1 confusion", n, name)

    v1_cells, v1_pos, v1_neg, v1_mixed, v1_floor = cell_table(rows, 0)
    b15 = qg15b_res["stabprep"]["cell_table"]
    assert len(v1_cells) == b15["cells"], "G1 V1 cell count"
    assert len(v1_mixed) == b15["mixed_cells"] == 12, "G1 V1 mixed count"
    assert v1_floor == b15["E_floor"] == 43, "G1 V1 floor"
    assert sum(v1_pos) == b15["P_total"] and sum(v1_neg) == b15["N_total"]
    stored = sorted(canonical(x) for x in b15["mixed_cells_verbatim_capped"])
    rebuilt = sorted(canonical({"feature_vector": dict(zip(V1_FEATURES, v1_cells[i])),
                                "pos": v1_pos[i], "neg": v1_neg[i]}) for i in v1_mixed)
    assert stored == rebuilt, "G1 V1 mixed-cell records verbatim"
    tb = log_time("B receipt bindings", ta)
    timing["B_bindings"] = round(tb - ta, 3)

    # ---- Q1: diagnosis of the 12 V1 collisions
    q1_cells = cell_report(v1_cells, v1_pos, v1_neg, v1_mixed, rows, 0,
                           V1_FEATURES, MIXED_CELL_CAP)
    q1_summary = {
        "mixed_cells": len(v1_mixed),
        "E_floor": v1_floor,
        "all_pairs_differ_in_step_cost_profile": all(
            c["minimal_distinguishing_pair"]["donor_exact_member"][
                "donor_step_cost_profile"]
            != c["minimal_distinguishing_pair"]["trade_member"][
                "donor_step_cost_profile"] for c in q1_cells),
        "pairs_with_equal_profile_multiset": sum(
            1 for c in q1_cells
            if c["minimal_distinguishing_pair"]["profiles_equal_as_multisets"]),
        "pairs_qubit_permutation_related": sum(
            1 for c in q1_cells
            if c["minimal_distinguishing_pair"]["qubit_permutation_related"]),
        "diagnosis": (
            "V1 is a bag of donor events plus a total: it records how many "
            "Y/sign/CNOT corrections the frozen GE donor performed and their total "
            "cost, but not how those events are distributed over the elimination "
            "steps. Donor suboptimality is a per-step property (a step paying a "
            "Y-correction AND a sign-correction on one weight-1 pivot costs 4 where "
            "the referee pays 2), so V1 cannot separate a schedule that pairs the two "
            "events on one step from one that spreads them over two steps."),
    }
    tq1 = log_time("Q1 diagnosis", tb)
    timing["Q1_diagnosis"] = round(tq1 - tb, 3)

    # ---- stage C: V2 cell table + floor (search-independent, grid-independent)
    v2_cells, v2_pos, v2_neg, v2_mixed, v2_floor = cell_table(rows, 1)
    v2_report = cell_report(v2_cells, v2_pos, v2_neg, v2_mixed, rows, 1,
                            V2_FEATURES, len(v2_mixed))
    tc = log_time("C V2 cell table", tq1)
    timing["C_cell_table"] = round(tc - tq1, 3)

    # ---- stage D: QG-15b search machinery over V2 on the frozen lattice
    qg15b.K_LATTICE = K_LATTICE
    qg15b.D_LATTICE = D_LATTICE
    qg15b.NODE_BUDGET = NODE_BUDGET
    train = [(r[1], r[2]) for r in rows]
    arm = qg15b.Arm("StabPrepV2", V2_FEATURES, train)
    assert arm.E_floor == v2_floor and len(arm.mixed) == len(v2_mixed)
    surface = arm.run_lattice()
    qg15b.check_monotonicity(surface)
    for rec in surface.values():
        assert rec["minerr"] >= arm.E_floor, "G8 floor consistency"
        flags = qg15b.pred_flags(rec["witness"], V2_FEATURES, train)
        err = sum(1 for f, (_, lab) in zip(flags, train) if f != lab)
        assert err == rec["minerr"], "G8 witness re-evaluation"
    zero_cells = qg15b.minimal_cells(surface, lambda e: e == 0)
    floor_cells = qg15b.minimal_cells(surface, lambda e, f=arm.E_floor: e == f)
    td = log_time("D V2 lattice search", tc)
    timing["D_search"] = round(td - tc, 3)

    # ---- terminal on the training domain
    if v2_floor == 0 and len(v2_mixed) == 0:
        terminal = "QG15C_FEATURE_DETERMINATION_RESTORED"
    else:
        terminal = "QG15C_FLOOR_PERSISTS__COLLISIONS_CHARACTERIZED"
    lattice_note = None
    if terminal == "QG15C_FEATURE_DETERMINATION_RESTORED":
        lattice_note = (None if zero_cells["headline_cell"]
                        else "LATTICE_DID_NOT_ATTAIN_ZERO")

    # headline predicate for H2 (best cell on the lattice, deterministic tie-break)
    if zero_cells["headline_cell"]:
        head = tuple(zero_cells["headline_cell"])
    elif floor_cells["headline_cell"]:
        head = tuple(floor_cells["headline_cell"])
    else:
        head = min(sorted(surface), key=lambda c: (surface[c]["minerr"], c[0] + c[1],
                                                   c[0], c[1]))
    head_witness = surface[head]["witness"]

    # training cell-purity map for H1
    purity = {}
    for i, vec in enumerate(v2_cells):
        purity[vec] = (v2_neg[i] == 0)

    # ---- surviving-collision characterization battery (protocol 7.1)
    surviving = {
        "count": len(v2_mixed),
        "E_floor": v2_floor,
        "n_values_present": sorted({v for c in v2_report for v in c["n_values"]}),
        "all_at_single_n": (
            len({v for c in v2_report for v in c["n_values"]}) <= 1
            if v2_report else None),
        "all_cells_single_gap": (all(len(c["trade_gaps"]) == 1 for c in v2_report)
                                 if v2_report else None),
        "trade_gaps_present": sorted({g for c in v2_report for g in c["trade_gaps"]}),
        "pairs_with_identical_step_cost_profile": sum(
            1 for c in v2_report
            if c["minimal_distinguishing_pair"]["profiles_identical"]),
        "pairs_qubit_permutation_related": sum(
            1 for c in v2_report
            if c["minimal_distinguishing_pair"]["qubit_permutation_related"]),
        "pairs_same_tensor_factor_sizes": sum(
            1 for c in v2_report
            if c["minimal_distinguishing_pair"]["same_tensor_factor_sizes"]),
        "pairs_same_weight_enumerator": sum(
            1 for c in v2_report
            if c["minimal_distinguishing_pair"]["same_weight_enumerator"]),
        "pairs_same_negative_sign_census": sum(
            1 for c in v2_report
            if c["minimal_distinguishing_pair"]["same_negative_sign_census"]),
        "cells_verbatim_capped": v2_report[:MIXED_CELL_CAP],
        "cells_serialization_capped": len(v2_report) > MIXED_CELL_CAP,
        "impossibility_theorem_obligation": (
            "Two failed vocabularies are evidence, not proof. An impossibility theorem "
            "would have to fix a precise feature class F (e.g. all functions of the "
            "r-local marginals of the stabilizer group; all permutation-invariant "
            "functions of the signed Pauli weight enumerator; all functions of the "
            "frozen donor gate word up to reordering) and prove: for every f in F "
            "there exist n-qubit stabilizer states S+, S- with f(S+) = f(S-), "
            "C_opt(S+) = C_D(S+) and C_opt(S-) < C_D(S-). This lane supplies witnesses "
            "only; it does not quantify over F and asserts no impossibility."),
    }

    # ---- stage digest BEFORE any held-out computation (G5)
    stage_obj = {
        "v1_cells": len(v1_cells), "v1_mixed": len(v1_mixed), "v1_floor": v1_floor,
        "v2_cells": len(v2_cells), "v2_mixed": len(v2_mixed), "v2_floor": v2_floor,
        "surface": qg15b.surface_json(surface),
        "zero_error_cells": zero_cells,
        "floor_attainment_cells": floor_cells,
        "headline_cell": list(head),
        "headline_witness": head_witness,
        "terminal": terminal,
        "lattice_note": lattice_note,
        "v2_features": V2_FEATURES,
    }
    stage_digest = sha256_text(canonical(stage_obj))
    assert not _HELDOUT_UNLOCKED, "G5 violated"
    print(f"ORIONQG_QG15C_STAGE_DIGEST={stage_digest}")
    sys.stdout.flush()
    _HELDOUT_UNLOCKED = True
    te = log_time("E stage digest", td)
    timing["E_stage_digest"] = round(te - td, 3)

    # ---- stage F: held-out n=4 panel, untouched until now
    assert _HELDOUT_UNLOCKED
    panel = qg15.build_panel()
    panel_feats = []
    with RefereeStub():
        for key in panel:
            v1, v2, cd, lb, costs = feature_vectors(key, 4)
            panel_feats.append((v1, v2, cd, lb, key, tuple(costs)))
    assert not _STUB_TRIGGERED, "G4 violated (panel)"
    dist4 = qg15.referee(4)
    assert len(dist4) == qg15.expected_count(4)
    panel_rows = []
    for v1, v2, cd, lb, key, costs in panel_feats:
        copt = dist4[key]
        assert lb <= copt <= cd
        panel_rows.append((v1, v2, copt == cd, 4, key, cd, copt, costs))
    labels4 = [r[2] for r in panel_rows]
    conf4 = qg15_res["component4_predicate"]["confusion_matrices"]["n4_panel_heldout"]
    for name in ("P0", "P1", "P2", "selected"):
        got = confusion(
            [qg15b.qg15_baseline_flags(r[0], name) for r in panel_rows], labels4)
        assert got == conf4[name], ("G1 n4 baseline binding", name)

    h1_flags = [purity.get(r[1], False) for r in panel_rows]
    h1_unseen = sum(1 for r in panel_rows if r[1] not in purity)
    h1 = {
        "rule": ("predict donor-exact iff the held-out V2 vector equals a training "
                 "cell whose training members are all donor-exact; unseen vectors "
                 "predict negative and are reported separately"),
        "confusion": confusion(h1_flags, labels4),
        "unseen_cells": h1_unseen,
        "panel_size": len(panel_rows),
    }
    h2 = {
        "cell": list(head),
        "witness": head_witness,
        "train_errors": surface[head]["minerr"],
        "confusion": confusion(
            qg15b.pred_flags(head_witness, V2_FEATURES, [(r[1], r[2]) for r in panel_rows]),
            labels4),
    }
    # V2 collisions ON the panel itself (mixed panel cells against training cells)
    p_cells, p_pos, p_neg, p_mixed, p_floor = cell_table(panel_rows, 1)
    heldout = {
        "panel": "QG-15 seeded n=4 panel (seed 20260821, 120 states, regenerated)",
        "panel_positives": sum(labels4),
        "labeled_after_stage_digest": True,
        "H1_cell_lookup": h1,
        "H2_lattice_predicate": h2,
        "panel_internal_V2_mixed_cells": len(p_mixed),
        "panel_internal_V2_floor": p_floor,
        "verdict_H1": ("HELDOUT_EXACT" if h1["confusion"]["errors"] == 0
                       else f"HELDOUT_REFUTED({h1['confusion']['errors']}/{len(panel_rows)})"),
        "verdict_H2": ("HELDOUT_EXACT" if h2["confusion"]["errors"] == 0
                       else f"HELDOUT_REFUTED({h2['confusion']['errors']}/{len(panel_rows)})"),
    }
    tf = log_time("F held-out panel", te)
    timing["F_heldout"] = round(tf - te, 3)

    # ---- gates, authority, results
    any_trunc = any(r["truncated"] for r in surface.values())
    gates = {
        "G1_receipt_binding": True,
        "G2_donor_validity": True,
        "G3_schedule_trace_consistency": True,
        "G4_referee_free_features": not _STUB_TRIGGERED,
        "G5_heldout_discipline_stamp_first": bool(_HELDOUT_UNLOCKED),
        "G6_search_completeness_accounting": True,
        "G7_surface_monotonicity": True,
        "G8_floor_consistency_and_witness_reeval": True,
        "G9_determinism_no_wallclock_in_digest": True,
        "G10_no_new_subject_data_no_network": True,
    }
    if not all(gates.values()):
        terminal = "QG15C_CANNOT_CHECK"
    authority = (
        f"ORION_QG15C_FEATURE_VOCABULARY_{terminal}__STABPREP_DONOR_EXACT_BOUNDARY_"
        "VOCABULARY_DETERMINATION_ON_VERIFIED_DOMAINS__NOT_R6"
    )

    results = {
        "schema": SCHEMA,
        "programme": ("ORION-QG lane QG-15c (PROGRAMME_CHARTER_V1.md, issue #740); "
                      "reopen-adjudicated successor of QG-15b (FAILED_DEFINITION)"),
        "protocol": ("development/orion-qg-regime-geometry/"
                     "QG15C_VOCABULARY_PROTOCOL_V1.md"),
        "protocol_sha256": protocol_sha,
        "checkout_revision": CHECKOUT_REVISION,
        "qg15_results_sha256": hashlib.sha256(QG15_RESULTS.read_bytes()).hexdigest(),
        "qg15b_results_sha256": hashlib.sha256(QG15B_RESULTS.read_bytes()).hexdigest(),
        "bindings": {
            "qg15_donor_censuses": {f"n{n}": censuses[n] for n in (1, 2, 3)},
            "qg15_confusions_reproduced": True,
            "qg15b_v1_cells": len(v1_cells),
            "qg15b_v1_mixed_cells": len(v1_mixed),
            "qg15b_v1_E_floor": v1_floor,
            "qg15b_v1_mixed_records_verbatim": True,
            "training_rows": len(rows),
        },
        "vocabulary": {
            "V1_features": V1_FEATURES,
            "V2_features": V2_FEATURES,
            "V2_new_features": V2_NEW_FEATURES,
            "V1_is_prefix_of_V2": True,
            "computability_class": (
                "each feature is a function of the target state and n alone, computed "
                "from the frozen GE donor family and F2 linear algebra; no feature "
                "calls the exact referee or uses C_opt (enforced structurally: the "
                "referee entry points are replaced by a raising stub for the whole "
                "feature-computation phase)"),
            "referee_stub_triggered": _STUB_TRIGGERED,
        },
        "q1_collision_diagnosis": {
            "summary": q1_summary,
            "cells_verbatim": q1_cells,
        },
        "v2_cell_table": {
            "cells": len(v2_cells),
            "P_total": sum(v2_pos),
            "N_total": sum(v2_neg),
            "mixed_cells": len(v2_mixed),
            "E_floor": v2_floor,
            "E_floor_V1": v1_floor,
            "training_domain": "StabPrep exhaustive n=1..3 union (1146 instances)",
            "target_label": "donor_exact := (C_opt == C_D)",
            "grid_and_budget_independent": True,
        },
        "search": {
            "lattice": {"K": list(K_LATTICE), "D": list(D_LATTICE),
                        "note": SUB_LATTICE_NOTE},
            "node_budget_per_cell": NODE_BUDGET,
            "literal_stats": arm.literal_stats,
            "conjunction_stats": {f"K{k}": v for k, v in sorted(arm.conj_stats.items())},
            "grids": {V2_FEATURES[i]: arm.grids[i] for i in range(len(V2_FEATURES))},
            "minerr_surface": qg15b.surface_json(surface),
            "zero_error_cells": zero_cells,
            "floor_attainment_cells": floor_cells,
            "headline_cell": list(head),
            "headline_witness": head_witness,
            "any_cell_truncated": any_trunc,
            "lattice_note": lattice_note,
        },
        "surviving_collisions": surviving,
        "heldout": heldout,
        "stage_digest": stage_digest,
        "gates": gates,
        "terminal": terminal,
        "authority": authority,
        "caps_disclosed": [
            "runtime cap < 25 min per run",
            f"lattice frozen at K<=2, D<=6 ({SUB_LATTICE_NOTE})",
            f"node budget {NODE_BUDGET} DFS expansions per lattice cell",
            f"mixed cells serialized verbatim capped at {MIXED_CELL_CAP} "
            "(counts always exact)",
            "held-out panel is the single seeded 120-state n=4 panel",
        ],
        "claim_boundary": (
            "All measurements are over the frozen finite domains and the frozen "
            "vocabularies only: StabPrep exhaustive n<=3 (1146 instances) with one "
            "seeded 120-state n=4 panel. The mixed-cell count and E_floor are "
            "properties of the frozen vocabulary on that domain, budget- and "
            "grid-independent, but not theorems for all n, for other vocabularies, or "
            "for other families. No impossibility claim is made. Ground-truth "
            "machinery is the committed QG-15/QG-15b machinery, imported unmodified, "
            "and earns no new credit. NOT_R6. No new subject data; the protected "
            "stretched-N2 subject is untouched."
        ),
        "novelty_credit": False,
        "r6_authority": False,
        "network_access": False,
        "chemistry_sources_read": False,
        "reserved_stretched_n2_accessed": False,
        "responsibility": "qg15c lane, ORION-QG programme, 2026-08-22",
    }
    digest = sha256_text(canonical(results))
    results["result_digest"] = digest
    results["timing"] = timing
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    receipt = {
        "schema": SCHEMA,
        "terminal": terminal,
        "V1_mixed_cells": len(v1_mixed),
        "V1_E_floor": v1_floor,
        "V2_features": len(V2_FEATURES),
        "V2_cells": len(v2_cells),
        "V2_mixed_cells": len(v2_mixed),
        "V2_E_floor": v2_floor,
        "headline_cell": list(head),
        "headline_train_errors": surface[head]["minerr"],
        "heldout_H1": heldout["verdict_H1"],
        "heldout_H2": heldout["verdict_H2"],
        "gates_all_pass": all(gates.values()),
        "protocol_sha256": protocol_sha,
        "stage_digest": stage_digest,
        "result_digest": digest,
        "authority": authority,
    }
    print("ORIONQG_QG15C_VOCABULARY=" + canonical(receipt))
    print(f"[qg15c] total: {time.perf_counter() - t0:.2f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
