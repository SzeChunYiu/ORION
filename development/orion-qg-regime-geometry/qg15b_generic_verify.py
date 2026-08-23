#!/usr/bin/env python3
"""QG-15b generic verification (frozen scope: protocol section 8).

Independent verifier for QG15B_PREDICATE_LANGUAGE_RESULTS.json. Imports NOTHING
from the qg15b analyzer. StabPrep ground truth is rebuilt from primitives via the
committed independent rebuild (qg15_generic_verify: its own tableau, referee, donor,
structure — no code shared with the analyzer chain). SixLCU ground truth comes from
the committed qg4_second_family machinery (the same committed authority Q3 cites).

It rebuilds both training feature/label tables, verifies the cell tables, E_floor
and any mixed-cell certificate, re-evaluates every serialized witness predicate from
its description, re-runs a COMPLETE brute-force search on the frozen sub-lattice
(K=1 row for D in {1,2,3}; D=1 column for K in {1,2,3}) with its own enumerator and
NO R5/R6 reductions, regenerates the held-out n=4 panel with its own referee, and
verifies the stage digest and the result digest.

Prints exactly one token line:
ORIONQG_QG15B_GENERIC_VERIFY={"decision":"ACCEPT"|"REJECT",...}
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "research" / "extensions" / "orion-qg"))

import qg15_generic_verify as gv  # noqa: E402  (committed independent rebuild)
import qg4_second_family as qg4  # noqa: E402  (committed SixLCU authority)

RESULTS = REPO / "research" / "extensions" / "orion-qg" / "QG15B_PREDICATE_LANGUAGE_RESULTS.json"
PROTOCOL = HERE / "QG15B_PREDICATE_LANGUAGE_PROTOCOL_V1.md"

STAB_FEATURES = [
    "nCZ", "nY", "nSignX", "nSignZ", "nCN", "C_D", "r_X", "c", "LB",
    "C_D-LB", "n-c", "nCN-(n-1)", "C_D-2n",
]
SIX_FEATURES = [
    "maxg2", "best2", "best3", "maxg3", "maxg4", "maxg5", "g6",
    "W", "wF6", "maxwt", "maxpair",
]
OPS = ("==", "<=", ">=")
SUBLATTICE = [(1, 1), (1, 2), (1, 3), (2, 1), (3, 1)]


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def note(msg):
    print(f"[qg15b-verify] {msg}", file=sys.stderr)


# ------------------------------------------------------------- ground truth
def stab_vec(feats, cd, lb, rx, c, n):
    return (
        feats["nCZ"], feats["nY"], feats["nSignX"], feats["nSignZ"], feats["nCN"],
        cd, rx, c, lb, cd - lb, n - c, feats["nCN"] - (n - 1), cd - 2 * n,
    )


def rebuild_stabprep():
    per_n = {}
    for n in (1, 2, 3):
        dist = gv.referee(n)
        rows = []
        for state in sorted(dist.keys(), key=lambda s: gv.state_key(s, n)):
            prep, cd, feats = gv.donor(state, n)
            assert gv.apply_circuit(gv.start(n), prep) == state
            lb, rx, c = gv.structure(state, n)
            copt = dist[state]
            assert lb <= copt <= cd
            rows.append((stab_vec(feats, cd, lb, rx, c, n), copt == cd))
        per_n[n] = rows
    return per_n


def rebuild_sixlcu(gen):
    rows = []
    for n, codes in gen:
        rec = qg4.eval_instance(codes, n)
        f = rec["features"]
        wts = [qg4.term_wt(cde, n) for cde in codes]
        maxpair = max(rec["wF"][pm] for pm in qg4.PAIR_MASKS)
        rows.append((
            (f["maxg2"], f["best2"], f["best3"], f["maxg3"], f["maxg4"], f["maxg5"],
             f["g6"], rec["W"], rec["wF"][63], max(wts), maxpair),
            rec["label"],
        ))
    return rows


# ------------------------------------------------------------- predicate eval
def eval_predicate(witness, feature_names, vec):
    if "constant" in witness:
        return witness["constant"]
    idx = {nm: i for i, nm in enumerate(feature_names)}
    for conj in witness["conjunctions"]:
        ok = True
        for lit in conj:
            x = vec[idx[lit["feature"]]]
            t = lit["threshold"]
            op = lit["op"]
            hit = (x == t) if op == "==" else ((x <= t) if op == "<=" else (x >= t))
            if hit == lit["negated"]:
                ok = False
                break
        if ok:
            return True
    return False


def pred_flags(witness, feature_names, rows):
    memo = {}
    out = []
    for vec, _lab in rows:
        r = memo.get(vec)
        if r is None:
            r = eval_predicate(witness, feature_names, vec)
            memo[vec] = r
        out.append(r)
    return out


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


# ------------------------------------------------------------- cells + brute
def build_cells(rows):
    counts = {}
    for vec, lab in rows:
        cell = counts.setdefault(vec, [0, 0])
        cell[0 if lab else 1] += 1
    cells = sorted(counts.keys())
    pos = [counts[v][0] for v in cells]
    neg = [counts[v][1] for v in cells]
    return cells, pos, neg


def literal_vectors(cells, nfeat):
    """All non-constant distinct literal truth vectors over cells (both polarities).

    Own enumerator; dedup by truth vector only (no R5/R6 reductions)."""
    ncells = len(cells)
    seen = set()
    vecs = []
    for fi in range(nfeat):
        col = [v[fi] for v in cells]
        for t in sorted(set(col)):
            for op in OPS:
                for negated in (False, True):
                    tv = tuple(
                        ((x == t) if op == "==" else
                         (x <= t) if op == "<=" else (x >= t)) != negated
                        for x in col)
                    if all(tv) or not any(tv):
                        continue
                    if tv in seen:
                        continue
                    seen.add(tv)
                    vecs.append(tv)
    return vecs


def brute_sublattice(cells, pos, neg, lit_vecs):
    """Complete brute-force minerr on the frozen sub-lattice, via float64 BLAS
    (all values are small integers; exactly representable)."""
    P = sum(pos)
    N = sum(neg)
    d = np.array([q - p for p, q in zip(pos, neg)], dtype=np.float64)
    M = np.array(lit_vecs, dtype=np.float64)  # (L, C) 0/1
    L = M.shape[0]
    const_best = float(min(0.0, N - P))  # FALSE score 0; TRUE score N-P
    lit_scores = M @ d  # (L,)
    best = {
        (1, 1): min(const_best, lit_scores.min()),
        (1, 2): min(const_best, lit_scores.min()),
        (1, 3): min(const_best, lit_scores.min()),
        (2, 1): min(const_best, lit_scores.min()),
        (3, 1): min(const_best, lit_scores.min()),
    }
    Mt = M.T  # (C, L)
    idx = np.arange(L)
    for a in range(L - 1):
        Mb = M[a + 1:]  # (nb, C)
        bidx = idx[a + 1:]
        # conjunctions: (a AND b) and (a AND b AND c), c > b
        AND = Mb * M[a]
        and_scores = AND @ d
        best[(2, 1)] = min(best[(2, 1)], and_scores.min())
        S3 = (AND * d) @ Mt  # (nb, L): score of a&b&c
        mask = idx[None, :] <= bidx[:, None]
        S3m = np.where(mask, np.inf, S3)
        m3 = S3m.min()
        if m3 < best[(3, 1)]:
            best[(3, 1)] = m3
        # disjunctions: (a OR b) and (a OR b OR c), c > b
        OR = np.maximum(Mb, M[a])
        or_scores = OR @ d
        best[(1, 2)] = min(best[(1, 2)], or_scores.min())
        SU = ((1.0 - OR) * d) @ Mt  # marginal of c over (a|b)
        tot = or_scores[:, None] + SU
        totm = np.where(mask, np.inf, tot)
        mu = totm.min()
        if mu < best[(1, 3)]:
            best[(1, 3)] = mu
    # monotone closure within the sub-lattice (D<=3 covers D'<D, K<=3 covers K'<K)
    best[(1, 2)] = min(best[(1, 2)], best[(1, 1)])
    best[(1, 3)] = min(best[(1, 3)], best[(1, 2)])
    best[(2, 1)] = min(best[(2, 1)], best[(1, 1)])
    best[(3, 1)] = min(best[(3, 1)], best[(2, 1)])
    return {kd: int(round(P + v)) for kd, v in best.items()}


def minimal_cells_check(surface, target):
    ach = []
    for key, rec in surface.items():
        kpart, dpart = key.split("_")
        K = int(kpart[1:])
        D = int(dpart[1:])
        if not rec["truncated"] and rec["minerr"] == target:
            ach.append((K, D))
    ach.sort()
    minimal = [c for c in ach
               if not any(o != c and o[0] <= c[0] and o[1] <= c[1] for o in ach)]
    headline = min(ach, key=lambda c: (c[0] + c[1], c[0], c[1])) if ach else None
    return ([list(c) for c in ach], [list(c) for c in sorted(minimal)],
            list(headline) if headline else None)


# ------------------------------------------------------------- main
def main() -> int:
    res = json.loads(RESULTS.read_text())
    checks = {}

    checks["schema"] = res.get("schema") == "orion-qg.qg15b_predicate_language.v1"
    checks["protocol_sha256"] = (
        hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == res["protocol_sha256"])
    checks["feature_lists"] = (
        res["language"]["stabprep_features"] == STAB_FEATURES
        and res["language"]["sixlcu_features"] == SIX_FEATURES)

    # result digest (canonical RESULTS minus result_digest minus timing)
    body = {k: v for k, v in res.items() if k not in ("result_digest", "timing")}
    checks["result_digest"] = (
        hashlib.sha256(canonical(body).encode()).hexdigest() == res["result_digest"])

    # stage digest reconstruction (analyzer stage_obj layout)
    stage_obj = {
        "stab_surface": res["stabprep"]["minerr_surface"],
        "six_surface": res["sixlcu"]["minerr_surface"],
        "q1_terminal": res["q1"]["terminal"],
        "q2_terminal": res["q2"]["terminal"],
        "q3_zero_terminal": res["q3"]["zero_terminal"],
        "stab_E_floor": res["stabprep"]["cell_table"]["E_floor"],
        "six_E_floor": res["sixlcu"]["cell_table"]["E_floor"],
        "stab_zero": res["stabprep"]["zero_error"],
        "stab_floor": res["stabprep"]["floor_attainment"],
        "six_zero": res["sixlcu"]["zero_error"],
        "six_floor": res["sixlcu"]["floor_attainment"],
        "calibration_pair": res["q3"]["calibration_pair"],
    }
    checks["stage_digest"] = (
        hashlib.sha256(canonical(stage_obj).encode()).hexdigest()
        == res["selected_predicates_sha256"])

    # ---------------- StabPrep rebuild from primitives
    note("rebuilding StabPrep ground truth from primitives")
    per_n = rebuild_stabprep()
    train = [(v, lab) for n in (1, 2, 3) for v, lab in per_n[n]]
    checks["stab_train_size"] = len(train) == 1146
    cells, pos, neg = build_cells(train)
    e_floor = sum(min(p, q) for p, q in zip(pos, neg))
    mixed = [(i, p, q) for i, (p, q) in enumerate(zip(pos, neg)) if p > 0 and q > 0]
    ct = res["stabprep"]["cell_table"]
    checks["stab_cell_table"] = (
        ct["cells"] == len(cells) and ct["P_total"] == sum(pos)
        and ct["N_total"] == sum(neg) and ct["E_floor"] == e_floor
        and ct["mixed_cells"] == len(mixed))
    mixed_rows = [
        {"feature_vector": dict(zip(STAB_FEATURES, cells[i])), "pos": p, "neg": q}
        for i, p, q in mixed[:20]]
    checks["stab_mixed_cells_verbatim"] = (
        mixed_rows == ct["mixed_cells_verbatim_capped"])
    checks["stab_grids"] = all(
        res["stabprep"]["grids"][STAB_FEATURES[fi]]
        == sorted({v[fi] for v in cells}) for fi in range(len(STAB_FEATURES)))

    # witness re-evaluation on every surface cell
    ok = True
    for key, rec in sorted(res["stabprep"]["minerr_surface"].items()):
        flags = pred_flags(rec["witness"], STAB_FEATURES, train)
        err = sum(1 for f, (_, lab) in zip(flags, train) if f != lab)
        ok &= err == rec["minerr"]
    checks["stab_witness_reeval"] = ok

    # reported confusions on n1/n2/n3/train
    panels = {"n1": per_n[1], "n2": per_n[2], "n3": per_n[3], "train_union": train}
    ok = True
    for cname, entry in res["stabprep"]["reported_confusions"].items():
        for pname, rows in panels.items():
            got = confusion(pred_flags(entry["witness"], STAB_FEATURES, rows),
                            [lab for _, lab in rows])
            ok &= got == entry["confusions"][pname]
    checks["stab_reported_confusions_train"] = ok

    # QG-15 baseline confusions on n1/n2/n3/train
    def baseline(vec, name):
        if name == "P0":
            return vec[0] == 0
        if name == "P1":
            return vec[0] == 0 and vec[2] == 0 and vec[3] == 0
        if name == "P2":
            return vec[9] == 0
        return vec[12] <= 0

    ok = True
    for name in ("P0", "P1", "P2", "selected"):
        entry = res["stabprep"]["qg15_baseline_confusions"][f"QG15_{name}"]
        for pname, rows in panels.items():
            got = confusion([baseline(v, name) for v, _ in rows],
                            [lab for _, lab in rows])
            ok &= got == entry[pname]
    checks["stab_baseline_confusions_train"] = ok

    # complete sub-lattice brute (own enumerator, no R5/R6)
    note("StabPrep sub-lattice brute force")
    lit_vecs = literal_vectors(cells, len(STAB_FEATURES))
    checks["stab_literal_pool"] = (
        len(lit_vecs) == res["stabprep"]["literal_stats"]["pool_literals"])
    brute = brute_sublattice(cells, pos, neg, lit_vecs)
    ok = True
    for (K, D) in SUBLATTICE:
        rec = res["stabprep"]["minerr_surface"][f"K{K}_D{D}"]
        ok &= (not rec["truncated"]) and rec["minerr"] == brute[(K, D)]
    checks["stab_sublattice_minimality"] = ok

    # zero/floor cell bookkeeping recomputed from the recorded surface
    za, zm, zh = minimal_cells_check(res["stabprep"]["minerr_surface"], 0)
    fa, fm, fh = minimal_cells_check(
        res["stabprep"]["minerr_surface"], ct["E_floor"])
    checks["stab_cell_bookkeeping"] = (
        za == res["stabprep"]["zero_error"]["achieving_cells"]
        and zm == res["stabprep"]["zero_error"]["minimal_cells"]
        and zh == res["stabprep"]["zero_error"]["headline_cell"]
        and fa == res["stabprep"]["floor_attainment"]["achieving_cells"]
        and fm == res["stabprep"]["floor_attainment"]["minimal_cells"]
        and fh == res["stabprep"]["floor_attainment"]["headline_cell"])

    # terminal consistency
    q1 = res["q1"]
    q1_rec = res["stabprep"]["minerr_surface"]["K3_D3"]
    q1_expect = ("EXACT_PREDICATE_FOUND_IN_L1"
                 if q1_rec["minerr"] == 0 and not q1_rec["truncated"]
                 else ("L1_UNDECIDED_CAP" if q1_rec["truncated"]
                       else "L1_INSUFFICIENT"))
    checks["q1_consistency"] = (
        q1["terminal"] == q1_expect
        and q1["minerr_at_K3_D3"] == q1_rec["minerr"]
        and q1["minerr_bracket_certified"][1] == q1_rec["minerr"]
        and q1["minerr_bracket_certified"][0]
        == (max(e_floor, 0) if q1_rec["truncated"] else q1_rec["minerr"]))
    checks["q2_consistency"] = (
        (e_floor > 0) == (len(mixed) > 0)
        and (res["q2"]["terminal"].startswith("ZERO_UNACHIEVABLE_ANY_BUDGET")
             if e_floor > 0 else
             not res["q2"]["terminal"].startswith("ZERO_UNACHIEVABLE")))

    # ---------------- held-out n=4 panel (own regeneration + referee)
    note("regenerating n=4 panel + own referee")
    rng = np.random.default_rng(gv.PANEL_SEED)
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
    d4 = gv.referee(4)
    panel_rows = []
    for s in panel:
        prep, cd, feats = gv.donor(s, 4)
        lb, rx, c = gv.structure(s, 4)
        copt = d4[s]
        assert lb <= copt <= cd
        panel_rows.append((stab_vec(feats, cd, lb, rx, c, 4), copt == cd))
    labels4 = [lab for _, lab in panel_rows]
    checks["panel_positives"] = (
        sum(labels4) == res["heldout"]["panel_positives"])
    ok = True
    for cname, entry in res["stabprep"]["reported_confusions"].items():
        got = confusion(pred_flags(entry["witness"], STAB_FEATURES, panel_rows),
                        labels4)
        ok &= got == entry["confusions"]["n4_panel_heldout"]
    for name in ("P0", "P1", "P2", "selected"):
        entry = res["stabprep"]["qg15_baseline_confusions"][f"QG15_{name}"]
        got = confusion([baseline(v, name) for v, _ in panel_rows], labels4)
        ok &= got == entry["n4_panel_heldout"]
    checks["stab_heldout_confusions"] = ok

    # ---------------- SixLCU (committed qg4 authority)
    note("rebuilding SixLCU ground truth")
    six_train = rebuild_sixlcu(qg4.gen_exhaustive_n2())
    checks["six_train_size"] = len(six_train) == 38760
    scells, spos, sneg = build_cells(six_train)
    s_floor = sum(min(p, q) for p, q in zip(spos, sneg))
    sct = res["sixlcu"]["cell_table"]
    smixed = sum(1 for p, q in zip(spos, sneg) if p > 0 and q > 0)
    checks["six_cell_table"] = (
        sct["cells"] == len(scells) and sct["P_total"] == sum(spos)
        and sct["N_total"] == sum(sneg) and sct["E_floor"] == s_floor
        and sct["mixed_cells"] == smixed)
    ok = True
    for key, rec in sorted(res["sixlcu"]["minerr_surface"].items()):
        flags = pred_flags(rec["witness"], SIX_FEATURES, six_train)
        err = sum(1 for f, (_, lab) in zip(flags, six_train) if f != lab)
        ok &= err == rec["minerr"]
    checks["six_witness_reeval"] = ok
    note("SixLCU sub-lattice brute force")
    s_lits = literal_vectors(scells, len(SIX_FEATURES))
    checks["six_literal_pool"] = (
        len(s_lits) == res["sixlcu"]["literal_stats"]["pool_literals"])
    sbrute = brute_sublattice(scells, spos, sneg, s_lits)
    ok = True
    for (K, D) in SUBLATTICE:
        rec = res["sixlcu"]["minerr_surface"][f"K{K}_D{D}"]
        ok &= (not rec["truncated"]) and rec["minerr"] == sbrute[(K, D)]
    checks["six_sublattice_minimality"] = ok
    six_n1 = rebuild_sixlcu(qg4.gen_exhaustive_n1())
    checks["six_n1_size"] = len(six_n1) == 729
    ok = True
    for cname, entry in res["sixlcu"]["reported_confusions"].items():
        got2 = confusion(pred_flags(entry["witness"], SIX_FEATURES, six_train),
                         [lab for _, lab in six_train])
        got1 = confusion(pred_flags(entry["witness"], SIX_FEATURES, six_n1),
                         [lab for _, lab in six_n1])
        ok &= (got2 == entry["confusions"]["n2_fit"]
               and got1 == entry["confusions"]["n1_crosscheck"])
    checks["six_reported_confusions"] = ok
    za, zm, zh = minimal_cells_check(res["sixlcu"]["minerr_surface"], 0)
    checks["six_cell_bookkeeping"] = (
        za == res["sixlcu"]["zero_error"]["achieving_cells"]
        and zm == res["sixlcu"]["zero_error"]["minimal_cells"]
        and zh == res["sixlcu"]["zero_error"]["headline_cell"])
    checks["calibration_consistency"] = (
        ("zero_error_at_K1_D1" in res["q3"]["calibration_pair"]["SixLCU"])
        == (zh == [1, 1]))

    decision = "ACCEPT" if all(checks.values()) else "REJECT"
    print("ORIONQG_QG15B_GENERIC_VERIFY=" + canonical(
        {"decision": decision, "checks": checks,
         "sublattice": {"stab": {f"K{k}_D{d}": v for (k, d), v in sorted(brute.items())},
                        "six": {f"K{k}_D{d}": v for (k, d), v in sorted(sbrute.items())}}}))
    return 0 if decision == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
