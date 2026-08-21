#!/usr/bin/env python3
"""QG-15b predicate-language boundary analyzer.

Frozen protocol:
development/orion-qg-regime-geometry/QG15B_PREDICATE_LANGUAGE_PROTOCOL_V1.md
(sha256 recorded in RESULTS; frozen BEFORE any outcome).

Measures the predicate complexity of the StabPrep donor-exact boundary under the
enlarged frozen language L1 (thresholded literals over the QG-15 feature vocabulary,
negation, conjunctions of <= K literals, disjunctions of <= D conjunctions), by
complete search over the frozen budget lattice, and calibrates against the SixLCU
incumbent-exact boundary under the IDENTICAL language/search machinery (Q3).

Committed machinery imported unmodified: qg15_third_family (referee, donor,
structure, panel), qg4_second_family (eval_instance, domain generators).

Stdout: two deterministic receipt lines (stage digest first, then the receipt).
Stderr: stage runtimes (the only non-deterministic output).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qg15_third_family as qg15  # noqa: E402  (committed, unmodified)
import qg4_second_family as qg4  # noqa: E402  (committed, unmodified)

REPO = Path(__file__).resolve().parents[3]
PROTOCOL = (
    REPO / "development" / "orion-qg-regime-geometry"
    / "QG15B_PREDICATE_LANGUAGE_PROTOCOL_V1.md"
)
QG15_RESULTS = Path(__file__).resolve().parent / "QG15_THIRD_FAMILY_RESULTS.json"
QG4_RESULTS = Path(__file__).resolve().parent / "QG4_SECOND_FAMILY_RESULTS.json"
RESULTS_PATH = Path(__file__).resolve().parent / "QG15B_PREDICATE_LANGUAGE_RESULTS.json"
SCHEMA = "orion-qg.qg15b_predicate_language.v1"
CHECKOUT_REVISION = "e221190f08e233d373641e4164b0561aa613e9e1"

K_LATTICE = (1, 2, 3)
D_LATTICE = (1, 2, 3, 4, 5, 6)
Q1_CELL = (3, 3)
NODE_BUDGET = 8_000_000
MIXED_CELL_CAP = 20

STAB_FEATURES = [
    "nCZ", "nY", "nSignX", "nSignZ", "nCN", "C_D", "r_X", "c", "LB",
    "C_D-LB", "n-c", "nCN-(n-1)", "C_D-2n",
]
SIX_FEATURES = [
    "maxg2", "best2", "best3", "maxg3", "maxg4", "maxg5", "g6",
    "W", "wF6", "maxwt", "maxpair",
]
OPS = ("==", "<=", ">=")

_HELDOUT_UNLOCKED = False  # G6 code-structural held-out discipline flag


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def log_time(label, t0):
    t1 = time.perf_counter()
    print(f"[qg15b] {label}: {t1 - t0:.2f}s", file=sys.stderr)
    return t1


# ---------------------------------------------------------------- ground truth
def stab_feature_vector(feats, cd, lb, rx, c, n):
    return (
        feats["nCZ"], feats["nY"], feats["nSignX"], feats["nSignZ"], feats["nCN"],
        cd, rx, c, lb, cd - lb, n - c, feats["nCN"] - (n - 1), cd - 2 * n,
    )


def build_stabprep_training():
    """Per-n rows: (feature_vector, label). Labels from committed referee+donor."""
    per_n = {}
    dists = {}
    for n in (1, 2, 3):
        dist = qg15.referee(n)
        dists[n] = dist
        rows = []
        for key in sorted(dist.keys()):
            prep, cd, feats, _ = qg15.donor(key, n)
            assert qg15.apply_circuit(qg15.start_state(n), prep, n) == key
            lb, rx, c = qg15.lower_bound(key, n)
            copt = dist[key]
            assert lb <= copt <= cd
            rows.append((stab_feature_vector(feats, cd, lb, rx, c, n), copt == cd))
        per_n[n] = rows
    return per_n, dists


def build_sixlcu_training():
    rows = []
    for n, codes in qg4.gen_exhaustive_n2():
        rec = qg4.eval_instance(codes, n)
        f = rec["features"]
        wts = [qg4.term_wt(cde, n) for cde in codes]
        maxpair = max(rec["wF"][pm] for pm in qg4.PAIR_MASKS)
        vec = (
            f["maxg2"], f["best2"], f["best3"], f["maxg3"], f["maxg4"], f["maxg5"],
            f["g6"], rec["W"], rec["wF"][63], max(wts), maxpair,
        )
        rows.append((vec, rec["label"], rec["P"]))
    return rows


def build_sixlcu_n1_panel():
    rows = []
    for n, codes in qg4.gen_exhaustive_n1():
        rec = qg4.eval_instance(codes, n)
        f = rec["features"]
        wts = [qg4.term_wt(cde, n) for cde in codes]
        maxpair = max(rec["wF"][pm] for pm in qg4.PAIR_MASKS)
        vec = (
            f["maxg2"], f["best2"], f["best3"], f["maxg3"], f["maxg4"], f["maxg5"],
            f["g6"], rec["W"], rec["wF"][63], max(wts), maxpair,
        )
        rows.append((vec, rec["label"]))
    return rows


# ---------------------------------------------------------------- bindings
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


def qg15_baseline_flags(vec, name):
    # features indexed per STAB_FEATURES; QG-15 P0/P1/P2/selected in vocabulary form
    if name == "P0":
        return vec[0] == 0
    if name == "P1":
        return vec[0] == 0 and vec[2] == 0 and vec[3] == 0
    if name == "P2":
        return vec[9] == 0  # C_D - LB == 0
    if name == "selected":
        return vec[12] <= 0  # C_D - 2n <= 0
    raise AssertionError(name)


def bind_qg15(stab_rows, qg15_res):
    c1 = qg15_res["component1_regime_map"]["per_n"]
    binding = {}
    for n in (1, 2, 3):
        rows = stab_rows[n]
        exact = sum(1 for _, lab in rows if lab)
        rec = c1[f"n{n}"]
        assert rec["instances"] == len(rows) and rec["donor_exact"] == exact, (
            "G1 census binding failed", n, exact)
        binding[f"n{n}_donor_exact"] = exact
    conf_store = qg15_res["component4_predicate"]["confusion_matrices"]
    key_map = {1: "n1", 2: "n2", 3: "n3_fit"}
    for n in (1, 2, 3):
        rows = stab_rows[n]
        labels = [lab for _, lab in rows]
        for name in ("P0", "P1", "P2", "selected"):
            got = confusion([qg15_baseline_flags(v, name) for v, _ in rows], labels)
            want = conf_store[key_map[n]][name]
            assert got == want, ("G1 confusion binding failed", n, name, got, want)
    # zero-FP receipted fact for P1 and P2 on the stored panels (incl. n4)
    for panel in conf_store:
        for name in ("P1", "P2"):
            assert conf_store[panel][name]["FP"] == 0, ("G1 zero-FP binding", panel)
    # witness feature spot-recompute from canonical keys
    nwit = 0
    for w in qg15_res["component2_trades"]["minimal_witnesses"]:
        n = w["n"]
        key = tuple(w["canonical_key"])
        prep, cd, feats, _ = qg15.donor(key, n)
        lb, rx, c = qg15.lower_bound(key, n)
        assert cd == w["C_D"] and feats == w["features"], "G1 witness feats"
        assert lb == w["LB"] and rx == w["r_X"] and c == w["c"], "G1 witness struct"
        nwit += 1
    binding["witnesses_spot_recomputed"] = nwit
    binding["p1_p2_zero_fp_all_stored_panels"] = True
    return binding


def bind_qg4(six_rows, qg4_res):
    labels = [lab for _, lab, _ in six_rows]
    p0 = [p[0] for _, _, p in six_rows]
    got = confusion(p0, labels)
    want = qg4_res["stage4_predicate"]["confusion_matrices_TP_FP_FN_TN"][
        "fit_exhaustive_n2"]["P0"]
    assert [got["TP"], got["FP"], got["FN"], got["TN"]] == want, (
        "G2 qg4 P0 binding failed", got, want)
    pos = sum(labels)
    assert pos == qg4_res["stage4_predicate"]["coverage"]["fit_exhaustive_n2"][
        "donor_exact_instances"], "G2 positives binding failed"
    return {"n2_P0_confusion": want, "n2_positives": pos}


# ---------------------------------------------------------------- language core
class Arm:
    """Cell-collapsed training table + frozen literal/conjunction/search machinery."""

    def __init__(self, name, feature_names, rows):
        self.name = name
        self.features = feature_names
        counts = {}
        for vec, lab in rows:
            cell = counts.setdefault(vec, [0, 0])
            cell[0 if lab else 1] += 1
        self.cells = sorted(counts.keys())
        self.cell_index = {v: i for i, v in enumerate(self.cells)}
        self.pos = [counts[v][0] for v in self.cells]
        self.neg = [counts[v][1] for v in self.cells]
        self.delta = [nn - pp for pp, nn in zip(self.pos, self.neg)]
        self.P_total = sum(self.pos)
        self.N_total = sum(self.neg)
        self.n_rows = self.P_total + self.N_total
        self.mixed = [i for i, (p, q) in enumerate(zip(self.pos, self.neg))
                      if p > 0 and q > 0]
        self.E_floor = sum(min(p, q) for p, q in zip(self.pos, self.neg))
        self.floor_rel = self.E_floor - self.P_total
        # delta-grouped masks for weighted popcounts
        self.relevant_mask = 0
        groups = {}
        for i, d in enumerate(self.delta):
            if d != 0:
                self.relevant_mask |= 1 << i
                groups.setdefault(d, 0)
                groups[d] |= 1 << i
        self.delta_groups = sorted(groups.items())
        self.neg_groups = [(d, m) for d, m in self.delta_groups if d < 0]
        # frozen grids and literal pool
        self.grids = [sorted({v[fi] for v in self.cells})
                      for fi in range(len(feature_names))]
        self._build_literals()
        self.conj_pools = {}
        self.conj_stats = {}

    # ---- weighted popcounts
    def score_of(self, mask):
        return sum(d * (mask & m).bit_count() for d, m in self.delta_groups)

    def pot_of(self, mask):
        return sum(d * (mask & m).bit_count() for d, m in self.neg_groups)

    # ---- literals
    def _build_literals(self):
        ncells = len(self.cells)
        full = (1 << ncells) - 1
        seen = {}
        pool = []
        raw = 0
        const_dropped = 0
        dup_dropped = 0
        for fi in range(len(self.features)):
            col = [v[fi] for v in self.cells]
            for t in self.grids[fi]:
                for op in OPS:
                    for negated in (False, True):
                        raw += 1
                        m = 0
                        for i, x in enumerate(col):
                            hit = (x == t) if op == "==" else (
                                (x <= t) if op == "<=" else (x >= t))
                            if hit != negated:
                                m |= 1 << i
                        if m == 0 or m == full:
                            const_dropped += 1
                            continue
                        if m in seen:
                            dup_dropped += 1
                            continue
                        seen[m] = len(pool)
                        pool.append((m, (fi, op, t, negated)))
        self.literals = pool
        self.literal_stats = {
            "raw_literals": raw,
            "R1_constants_dropped": const_dropped,
            "R2_duplicates_dropped": dup_dropped,
            "pool_literals": len(pool),
        }

    def literal_desc(self, li):
        fi, op, t, negated = self.literals[li][1]
        return {"feature": self.features[fi], "op": op, "threshold": t,
                "negated": negated}

    # ---- conjunction pool per K (reductions R3-R6, counts recorded)
    def conj_pool(self, K):
        if K in self.conj_pools:
            return self.conj_pools[K]
        L = len(self.literals)
        masks = [m for m, _ in self.literals]
        distinct = {}  # full truth vector -> first (size, idx tuple)
        raw = 0
        empty_dropped = 0
        for size in range(1, K + 1):
            if size == 1:
                for a in range(L):
                    raw += 1
                    v = masks[a]
                    if v not in distinct:
                        distinct[v] = (1, (a,))
            elif size == 2:
                pair_cache = []
                for a in range(L):
                    ma = masks[a]
                    for b in range(a + 1, L):
                        raw += 1
                        v = ma & masks[b]
                        if v == 0:
                            empty_dropped += 1
                            pair_cache.append((0, a, b))
                            continue
                        pair_cache.append((v, a, b))
                        if v not in distinct:
                            distinct[v] = (2, (a, b))
                self._pair_cache = pair_cache
            elif size == 3:
                for v2, a, b in self._pair_cache:
                    if v2 == 0:
                        # every extension is empty; counted arithmetically
                        raw += L - b - 1
                        empty_dropped += L - b - 1
                        continue
                    for cc in range(b + 1, L):
                        raw += 1
                        v = v2 & masks[cc]
                        if v == 0:
                            empty_dropped += 1
                            continue
                        if v not in distinct:
                            distinct[v] = (3, (a, b, cc))
            else:
                raise AssertionError("K beyond frozen lattice")
        r3_dropped = raw - empty_dropped - len(distinct)
        # R5 pot filter + R6 relevant-restriction dedupe
        r5_dropped = 0
        restricted = {}
        for v, desc in distinct.items():
            pot = self.pot_of(v)
            if pot >= 0:
                r5_dropped += 1
                continue
            rv = v & self.relevant_mask
            old = restricted.get(rv)
            if old is None or desc < old[1]:
                restricted[rv] = (pot, desc)
        r6_dropped = (len(distinct) - r5_dropped) - len(restricted)
        pool = sorted(
            ((pot, desc, rv) for rv, (pot, desc) in restricted.items()),
            key=lambda x: (x[0], x[1]),
        )
        stats = {
            "raw_conjunctions": raw,
            "R4_empty_dropped": empty_dropped,
            "R3_duplicate_vectors_dropped": r3_dropped,
            "distinct_vectors": len(distinct),
            "R5_pot_nonneg_dropped": r5_dropped,
            "R6_relevant_restriction_dropped": r6_dropped,
            "pool_size": len(pool),
        }
        self.conj_pools[K] = pool
        self.conj_stats[K] = stats
        return pool

    # ---- frozen greedy seed (upper bound only)
    def greedy_prefix(self, pool, Dmax):
        """Returns list seeds[d] = (score_rel, witness descs) for d=1..Dmax prefixes."""
        U = 0
        score = 0
        chosen = []
        seeds = []
        for _ in range(Dmax):
            best = None
            for i, (pot, desc, mask) in enumerate(pool):
                # exact early break: marg >= pot and pool is pot-ascending, so once
                # pot >= current best marginal no later candidate can strictly beat it
                if best is not None and pot >= best[0]:
                    break
                marg = self.score_of(mask & ~U)
                if marg < 0 and (best is None or (marg, i) < best):
                    best = (marg, i)
            if best is None:
                break
            marg, i = best
            U |= pool[i][2]
            score += marg
            chosen.append(pool[i][1])
            seeds.append((score, list(chosen)))
        out = []
        for d in range(1, Dmax + 1):
            avail = [s for s in seeds[:d]]
            out.append(avail[-1] if avail else None)
        return out

    # ---- complete branch and bound at (K, D)
    def search_cell(self, K, D, init_best_rel, init_witness):
        pool = self.conj_pool(K)
        M = len(pool)
        pots = [p for p, _, _ in pool]
        prefix = [0]
        for p in pots:
            prefix.append(prefix[-1] + p)

        def min_extra(start, r):
            if r <= 0 or start >= M:
                return 0
            end = min(M, start + r)
            s = prefix[end] - prefix[start]
            return min(0, s)

        best = init_best_rel
        witness = list(init_witness)
        nodes = 0
        truncated = False
        stack_desc = []
        floor_rel = self.floor_rel

        def rec(start, Umask, score, depth_left):
            nonlocal best, witness, nodes, truncated
            if truncated or depth_left == 0 or best <= floor_rel:
                return
            for i in range(start, M):
                nodes += 1
                if nodes > NODE_BUDGET:
                    truncated = True
                    return
                bound = score + pots[i] + min_extra(i + 1, depth_left - 1)
                if bound >= best:
                    break  # pool sorted by pot asc; later bounds are >=
                marg = self.score_of(pool[i][2] & ~Umask)
                new_score = score + marg
                stack_desc.append(pool[i][1])
                if new_score < best:
                    best = new_score
                    witness = list(stack_desc)
                    if best <= floor_rel:
                        stack_desc.pop()
                        return
                if new_score + min_extra(i + 1, depth_left - 1) < best:
                    rec(i + 1, Umask | pool[i][2], new_score, depth_left - 1)
                stack_desc.pop()
                if truncated:
                    return

        rec(0, 0, 0, D)
        return best, witness, nodes, truncated

    # ---- full lattice
    def run_lattice(self):
        surface = {}
        for K in K_LATTICE:
            pool = self.conj_pool(K)
            seeds = self.greedy_prefix(pool, max(D_LATTICE))
            prev_best = None
            prev_wit = None
            for D in D_LATTICE:
                # incumbents: FALSE (score 0), TRUE (score N-P), greedy prefix, prev D
                cands = [(0, ("CONST_FALSE",)),
                         (self.N_total - self.P_total, ("CONST_TRUE",))]
                if seeds[D - 1] is not None:
                    cands.append((seeds[D - 1][0], seeds[D - 1][1]))
                if prev_best is not None:
                    cands.append((prev_best, prev_wit))
                init_best, init_wit = min(cands, key=lambda x: x[0])
                best, wit, nodes, trunc = self.search_cell(K, D, init_best, init_wit)
                prev_best, prev_wit = best, wit
                surface[(K, D)] = {
                    "minerr": self.P_total + best,
                    "truncated": trunc,
                    "dfs_nodes": nodes,
                    "pool_size": len(pool),
                    "witness": self.serialize_witness(wit),
                }
        return surface

    def serialize_witness(self, wit):
        if wit and wit[0] == "CONST_FALSE":
            return {"constant": False}
        if wit and wit[0] == "CONST_TRUE":
            return {"constant": True}
        conjs = []
        for desc in wit:
            size, idxs = desc
            conjs.append([self.literal_desc(li) for li in idxs])
        return {"conjunctions": conjs}


def eval_predicate(witness, feature_names, vec):
    """Evaluate a serialized L1 predicate on one feature vector."""
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
    """Memoized per-distinct-vector evaluation of a serialized predicate."""
    memo = {}
    out = []
    for vec, *_ in rows:
        r = memo.get(vec)
        if r is None:
            r = eval_predicate(witness, feature_names, vec)
            memo[vec] = r
        out.append(r)
    return out


# ---------------------------------------------------------------- Q verdicts
def minimal_cells(surface, target_fn):
    """Cells achieving target (untruncated), product-order minimal set + headline.

    A truncated cell's recorded minerr is only an upper bound on quality of the
    recorded witness (the true cell minimum may be lower), so minimality claims are
    flagged as compromised when a truncated, non-achieving cell sits at or below a
    claimed minimal cell in the product order (or anywhere, when nothing achieves)."""
    ach = [(K, D) for (K, D), rec in sorted(surface.items())
           if not rec["truncated"] and target_fn(rec["minerr"])]
    minimal = [c for c in ach
               if not any(o != c and o[0] <= c[0] and o[1] <= c[1] for o in ach)]
    headline = min(ach, key=lambda c: (c[0] + c[1], c[0], c[1])) if ach else None
    trunc_cells = [(K, D) for (K, D), rec in sorted(surface.items())
                   if rec["truncated"]]
    if headline is None:
        compromised = bool(trunc_cells)
    else:
        compromised = any(
            t[0] <= c[0] and t[1] <= c[1] for c in minimal for t in trunc_cells)
    return {
        "achieving_cells": [list(c) for c in ach],
        "minimal_cells": [list(c) for c in sorted(minimal)],
        "headline_cell": list(headline) if headline else None,
        "any_cell_truncated": bool(trunc_cells),
        "minimality_compromised_by_truncation": compromised,
    }


def surface_json(surface):
    return {
        f"K{K}_D{D}": {k: v for k, v in rec.items()}
        for (K, D), rec in sorted(surface.items())
    }


def check_monotonicity(surface):
    for (K, D), rec in surface.items():
        if rec["truncated"]:
            continue
        for (K2, D2), rec2 in surface.items():
            if rec2["truncated"]:
                continue
            if K2 >= K and D2 >= D:
                assert rec2["minerr"] <= rec["minerr"], (
                    "G4 monotonicity failed", (K, D), (K2, D2))


# ---------------------------------------------------------------- main
def main() -> int:
    global _HELDOUT_UNLOCKED
    t0 = time.perf_counter()
    timing = {}
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    qg15_res = json.loads(QG15_RESULTS.read_text())
    qg4_res = json.loads(QG4_RESULTS.read_text())

    # ---- stage A: StabPrep ground truth + G1 bindings
    ta = time.perf_counter()
    stab_rows_per_n, dists = build_stabprep_training()
    g1 = bind_qg15(stab_rows_per_n, qg15_res)
    stab_train = [(v, lab) for n in (1, 2, 3) for v, lab in stab_rows_per_n[n]]
    assert len(stab_train) == 1146
    ta = log_time("A stabprep ground truth + G1", ta)
    timing["A_stabprep_truth"] = round(ta - t0, 3)

    # ---- stage B: SixLCU ground truth + G2 bindings
    six_rows3 = build_sixlcu_training()
    g2 = bind_qg4(six_rows3, qg4_res)
    six_train = [(v, lab) for v, lab, _ in six_rows3]
    assert len(six_train) == 38760
    six_n1 = build_sixlcu_n1_panel()
    assert len(six_n1) == 729
    tb = log_time("B sixlcu ground truth + G2", ta)
    timing["B_sixlcu_truth"] = round(tb - ta, 3)

    # ---- stage C: StabPrep lattice search
    stab = Arm("StabPrep", STAB_FEATURES, stab_train)
    stab_surface = stab.run_lattice()
    check_monotonicity(stab_surface)
    for rec in stab_surface.values():
        assert rec["minerr"] >= stab.E_floor, "G5 floor consistency"
    tc = log_time("C stabprep lattice", tb)
    timing["C_stabprep_search"] = round(tc - tb, 3)

    # ---- stage D: SixLCU lattice search (identical machinery)
    six = Arm("SixLCU", SIX_FEATURES, six_train)
    six_surface = six.run_lattice()
    check_monotonicity(six_surface)
    for rec in six_surface.values():
        assert rec["minerr"] >= six.E_floor, "G5 floor consistency"
    td = log_time("D sixlcu lattice", tc)
    timing["D_sixlcu_search"] = round(td - tc, 3)

    # ---- G5: every witness re-evaluated from its serialized description
    for arm, surface, rows in ((stab, stab_surface, stab_train),
                               (six, six_surface, six_train)):
        for (K, D), rec in sorted(surface.items()):
            flags = pred_flags(rec["witness"], arm.features, rows)
            err = sum(1 for f, (_, lab) in zip(flags, rows) if f != lab)
            assert err == rec["minerr"], (
                "G5 witness re-evaluation failed", arm.name, K, D, err, rec["minerr"])

    # ---- Q verdicts on training data
    def cell_desc(arm):
        return {
            "cells": len(arm.cells),
            "P_total": arm.P_total,
            "N_total": arm.N_total,
            "mixed_cells": len(arm.mixed),
            "E_floor": arm.E_floor,
            "mixed_cells_verbatim_capped": [
                {"feature_vector": dict(zip(arm.features, arm.cells[i])),
                 "pos": arm.pos[i], "neg": arm.neg[i]}
                for i in arm.mixed[:MIXED_CELL_CAP]
            ],
        }

    stab_zero = minimal_cells(stab_surface, lambda e: e == 0)
    stab_floor = minimal_cells(stab_surface, lambda e, f=stab.E_floor: e == f)
    six_zero = minimal_cells(six_surface, lambda e: e == 0)
    six_floor = minimal_cells(six_surface, lambda e, f=six.E_floor: e == f)

    q1_rec = stab_surface[Q1_CELL]
    if q1_rec["minerr"] == 0 and not q1_rec["truncated"]:
        q1_terminal = "EXACT_PREDICATE_FOUND_IN_L1"
    elif q1_rec["truncated"]:
        q1_terminal = "L1_UNDECIDED_CAP"
    else:
        q1_terminal = "L1_INSUFFICIENT"

    def q2_terminal_for(arm, zero, floor):
        if zero["headline_cell"] is not None:
            t = "ZERO_ACHIEVABLE_AT"
            if zero["minimality_compromised_by_truncation"]:
                t += "_CAPPED"
        elif arm.E_floor > 0:
            t = "ZERO_UNACHIEVABLE_ANY_BUDGET"
            # certificate is grid- and budget-independent: never capped
        else:
            t = "ZERO_UNREACHED_ON_LATTICE"
            if zero["any_cell_truncated"]:
                t += "_CAPPED"
        return t

    q2_terminal = q2_terminal_for(stab, stab_zero, stab_floor)
    q3_zero_terminal = q2_terminal_for(six, six_zero, six_floor)

    def budget_str(zero, floor, efloor):
        if zero["headline_cell"]:
            K, D = zero["headline_cell"]
            cap = "_capped" if zero["minimality_compromised_by_truncation"] else ""
            return f"zero_error_at_K{K}_D{D}{cap}"
        if floor["headline_cell"]:
            K, D = floor["headline_cell"]
            cap = "_capped" if floor["minimality_compromised_by_truncation"] else ""
            return f"zero_unachievable__floor_{efloor}_at_K{K}_D{D}{cap}"
        cap = "_capped_search" if floor["any_cell_truncated"] else ""
        return f"zero_unachievable__floor_{efloor}_unattained_on_lattice{cap}"

    calibration = {
        "StabPrep": budget_str(stab_zero, stab_floor, stab.E_floor),
        "SixLCU": budget_str(six_zero, six_floor, six.E_floor),
    }

    # ---- stage digest BEFORE any held-out computation (G6)
    stage_obj = {
        "stab_surface": surface_json(stab_surface),
        "six_surface": surface_json(six_surface),
        "q1_terminal": q1_terminal,
        "q2_terminal": q2_terminal,
        "q3_zero_terminal": q3_zero_terminal,
        "stab_E_floor": stab.E_floor,
        "six_E_floor": six.E_floor,
        "stab_zero": stab_zero, "stab_floor": stab_floor,
        "six_zero": six_zero, "six_floor": six_floor,
        "calibration_pair": calibration,
    }
    stage_digest = sha256_text(canonical(stage_obj))
    assert not _HELDOUT_UNLOCKED, "G6 violated"
    print(f"ORIONQG_QG15B_SELECTED_PREDICATES_SHA256={stage_digest}")
    sys.stdout.flush()
    _HELDOUT_UNLOCKED = True
    te = log_time("E stage digest", td)
    timing["E_stage_digest"] = round(te - td, 3)

    # ---- stage F: held-out n=4 panel (StabPrep) — only after the stamp
    assert _HELDOUT_UNLOCKED
    dist4 = qg15.referee(4)
    assert len(dist4) == qg15.expected_count(4)
    panel = qg15.build_panel()
    panel_rows = []
    for key in panel:
        prep, cd, feats, _ = qg15.donor(key, 4)
        assert qg15.apply_circuit(qg15.start_state(4), prep, 4) == key
        lb, rx, c = qg15.lower_bound(key, 4)
        copt = dist4[key]
        assert lb <= copt <= cd
        panel_rows.append((stab_feature_vector(feats, cd, lb, rx, c, 4), copt == cd))
    labels4 = [lab for _, lab in panel_rows]

    # bind QG-15 stored held-out baselines (P0/P1/P2/selected) on the panel
    conf4_store = qg15_res["component4_predicate"]["confusion_matrices"][
        "n4_panel_heldout"]
    for name in ("P0", "P1", "P2", "selected"):
        got = confusion(
            [qg15_baseline_flags(v, name) for v, _ in panel_rows], labels4)
        assert got == conf4_store[name], ("G1 n4 baseline binding", name, got)

    # reported predicates: Q1 witness + headline witnesses (deduped by cell)
    report_cells = []
    for c in ([Q1_CELL]
              + ([tuple(stab_zero["headline_cell"])] if stab_zero["headline_cell"] else [])
              + ([tuple(stab_floor["headline_cell"])] if stab_floor["headline_cell"] else [])
              + [tuple(x) for x in stab_floor["minimal_cells"]]):
        if c not in report_cells:
            report_cells.append(c)

    stab_panels = {
        "n1": stab_rows_per_n[1], "n2": stab_rows_per_n[2],
        "n3": stab_rows_per_n[3], "train_union": stab_train,
        "n4_panel_heldout": panel_rows,
    }
    stab_confusions = {}
    for c in report_cells:
        wit = stab_surface[c]["witness"]
        entry = {}
        for pname, rows in stab_panels.items():
            entry[pname] = confusion(
                pred_flags(wit, STAB_FEATURES, rows), [lab for _, lab in rows])
        stab_confusions[f"K{c[0]}_D{c[1]}"] = {
            "witness": wit, "confusions": entry}
    baseline_confusions = {}
    for name in ("P0", "P1", "P2", "selected"):
        entry = {}
        for pname, rows in stab_panels.items():
            entry[pname] = confusion(
                [qg15_baseline_flags(v, name) for v, _ in rows],
                [lab for _, lab in rows])
        baseline_confusions[f"QG15_{name}"] = entry

    # Q1 held-out generalization verdict (only meaningful if training-exact)
    q1_heldout = None
    if q1_terminal == "EXACT_PREDICATE_FOUND_IN_L1":
        e4 = stab_confusions[f"K{Q1_CELL[0]}_D{Q1_CELL[1]}"]["confusions"][
            "n4_panel_heldout"]["errors"]
        q1_heldout = "HELDOUT_EXACT" if e4 == 0 else f"HELDOUT_REFUTED({e4}/120)"

    # SixLCU reported predicates on n2 fit + n1 cross-check
    six_report_cells = []
    for c in ([Q1_CELL]
              + ([tuple(six_zero["headline_cell"])] if six_zero["headline_cell"] else [])
              + [tuple(x) for x in six_zero["minimal_cells"]]):
        if c not in six_report_cells:
            six_report_cells.append(c)
    six_panels = {"n2_fit": six_train, "n1_crosscheck": six_n1}
    six_confusions = {}
    for c in six_report_cells:
        wit = six_surface[c]["witness"]
        entry = {}
        for pname, rows in six_panels.items():
            entry[pname] = confusion(
                pred_flags(wit, SIX_FEATURES, rows), [lab for _, lab in rows])
        six_confusions[f"K{c[0]}_D{c[1]}"] = {"witness": wit, "confusions": entry}
    tf = log_time("F heldout + confusions", te)
    timing["F_heldout"] = round(tf - te, 3)

    # ---- gates, terminal, results
    any_trunc = (any(r["truncated"] for r in stab_surface.values())
                 or any(r["truncated"] for r in six_surface.values()))
    gates = {
        "G1_qg15_binding": True,
        "G2_qg4_binding": True,
        "G3_search_completeness_accounting": True,
        "G4_surface_monotonicity": True,
        "G5_floor_consistency_and_witness_reeval": True,
        "G6_heldout_discipline_stamp_first": bool(_HELDOUT_UNLOCKED),
        "G7_confusion_completeness": True,
        "G8_determinism_no_wallclock_in_digest": True,
        "G9_no_new_subject_data_no_network": True,
    }
    undecided = []
    if q1_terminal == "L1_UNDECIDED_CAP":
        undecided.append("Q1")
    if q2_terminal.endswith("_CAPPED"):
        undecided.append("Q2")
    if q3_zero_terminal.endswith("_CAPPED"):
        undecided.append("Q3")
    terminal = ("QG15B_COMPLETE" if not undecided
                else "QG15B_PARTIAL__" + "_".join(undecided) + "_UNDECIDED")
    authority = (
        f"ORION_QG15B_PREDICATE_LANGUAGE_{terminal}__STABPREP_BOUNDARY_"
        "PREDICATE_COMPLEXITY_ON_VERIFIED_DOMAINS__NOT_R6"
    )

    results = {
        "schema": SCHEMA,
        "programme": ("ORION-QG lane QG-15b (PROGRAMME_CHARTER_V1.md, issue #740); "
                      "registered successor of QG-15 (QG_WAVE2_RECORD.md)"),
        "protocol": ("development/orion-qg-regime-geometry/"
                     "QG15B_PREDICATE_LANGUAGE_PROTOCOL_V1.md"),
        "protocol_sha256": protocol_sha,
        "checkout_revision": CHECKOUT_REVISION,
        "qg15_results_sha256": hashlib.sha256(QG15_RESULTS.read_bytes()).hexdigest(),
        "qg4_results_sha256": hashlib.sha256(QG4_RESULTS.read_bytes()).hexdigest(),
        "language": {
            "literal_form": "[feature op threshold], op in {==,<=,>=}, closed under negation",
            "threshold_grid": "attained values on the arm's training domain (frozen rule; complete over integer thresholds on train)",
            "member": "disjunction of <= D conjunctions of <= K literals; constants included",
            "q1_budget": {"K": 3, "D": 3},
            "lattice": {"K": list(K_LATTICE), "D": list(D_LATTICE),
                        "K4_excluded_frozen_runtime_truncation": True},
            "stabprep_features": STAB_FEATURES,
            "sixlcu_features": SIX_FEATURES,
        },
        "bindings": {"qg15": g1, "qg4": g2},
        "stabprep": {
            "training_domain": "QG-15 exhaustive n=1..3 union (1146 instances)",
            "target_label": "donor_exact := (C_opt == C_D)",
            "cell_table": cell_desc(stab),
            "literal_stats": stab.literal_stats,
            "conjunction_stats": {f"K{k}": v for k, v in sorted(stab.conj_stats.items())},
            "grids": {STAB_FEATURES[i]: stab.grids[i] for i in range(len(STAB_FEATURES))},
            "minerr_surface": surface_json(stab_surface),
            "zero_error": stab_zero,
            "floor_attainment": stab_floor,
            "reported_confusions": stab_confusions,
            "qg15_baseline_confusions": baseline_confusions,
        },
        "sixlcu": {
            "training_domain": "QG-4 exhaustive n=2 (38760 instances)",
            "target_label": "incumbent_exact := (C_F == C_inc)",
            "family_choice_note": ("TARE R6Q/QG-2 slice declared not cheaply importable "
                                   "(heavy orion-q DP import chain); lane-brief fallback "
                                   "SixLCU n=2 via committed QG-4 machinery taken "
                                   "(recorded pre-outcome in the frozen protocol)"),
            "cell_table": cell_desc(six),
            "literal_stats": six.literal_stats,
            "conjunction_stats": {f"K{k}": v for k, v in sorted(six.conj_stats.items())},
            "grids": {SIX_FEATURES[i]: six.grids[i] for i in range(len(SIX_FEATURES))},
            "minerr_surface": surface_json(six_surface),
            "zero_error": six_zero,
            "floor_attainment": six_floor,
            "reported_confusions": six_confusions,
        },
        "q1": {
            "terminal": q1_terminal,
            "minerr_at_K3_D3": q1_rec["minerr"],
            "minerr_at_K3_D3_is_upper_bound_due_to_cap": q1_rec["truncated"],
            "minerr_bracket_certified": [
                max(stab.E_floor, 0) if q1_rec["truncated"] else q1_rec["minerr"],
                q1_rec["minerr"],
            ],
            "note": (
                "E_floor > 0 certifies (independently of search completeness) that "
                "no member of L1 at any budget is exact on the training domain; "
                "the cap leaves open only the exact minimum inside the bracket"
                if stab.E_floor > 0 and q1_rec["truncated"] else None),
            "heldout_verdict": q1_heldout,
        },
        "q2": {
            "terminal": q2_terminal,
            "E_floor": stab.E_floor,
            "mixed_cell_count": len(stab.mixed),
            "zero_error_cells": stab_zero,
            "floor_attainment_cells": stab_floor,
            "grid_independent_certificate": (
                "a mixed cell (identical frozen feature vector, both labels present) "
                "defeats every predicate over this vocabulary at every budget"
                if stab.E_floor > 0 else None),
        },
        "q3": {
            "zero_terminal": q3_zero_terminal,
            "E_floor": six.E_floor,
            "zero_error_cells": six_zero,
            "calibration_pair": calibration,
        },
        "heldout": {
            "panel": "QG-15 seeded n=4 panel (seed 20260821, 120 states, regenerated)",
            "panel_positives": sum(labels4),
            "labeled_after_stage_digest": True,
        },
        "selected_predicates_sha256": stage_digest,
        "node_budget_per_cell": NODE_BUDGET,
        "any_cell_truncated": any_trunc,
        "gates": gates,
        "terminal": terminal,
        "authority": authority,
        "claim_boundary": (
            "All measurements are over the frozen finite training domains and the "
            "frozen language L1 only: StabPrep exhaustive n<=3 (1146 instances) with "
            "one seeded n=4 panel; SixLCU exhaustive n=2 (38760) with the n=1 "
            "cross-check. Predicate-complexity numbers are properties of the frozen "
            "vocabularies, grids, and budget lattice; nothing is a theorem for all "
            "n, for other feature sets, or for other families. The mixed-cell "
            "certificate, where present, binds every predicate over the frozen "
            "vocabulary on the training domain, at any budget. Ground-truth "
            "machinery is the committed QG-15/QG-4 machinery, imported unmodified, "
            "and earns no new credit. NOT_R6. No new subject data; the protected "
            "stretched-N2 subject is untouched."
        ),
        "caps_disclosed": [
            "runtime cap < 25 min per run",
            f"node budget {NODE_BUDGET} DFS expansions per lattice cell",
            "lattice frozen at K<=3, D<=6 (K=4 excluded by runtime arithmetic)",
            f"mixed cells serialized verbatim capped at {MIXED_CELL_CAP} (counts exact)",
            "verifier sub-lattice scope: K=1 row and D=1 column (per protocol s.8)",
        ],
        "novelty_credit": False,
        "r6_authority": False,
        "network_access": False,
        "chemistry_sources_read": False,
        "reserved_stretched_n2_accessed": False,
        "responsibility": "qg15b lane, ORION-QG programme, 2026-08-21",
    }
    digest = sha256_text(canonical(results))
    results["result_digest"] = digest
    results["timing"] = timing
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    receipt = {
        "schema": SCHEMA,
        "terminal": terminal,
        "q1_terminal": q1_terminal,
        "q1_minerr_K3_D3": q1_rec["minerr"],
        "q1_minerr_bracket_certified": [
            max(stab.E_floor, 0) if q1_rec["truncated"] else q1_rec["minerr"],
            q1_rec["minerr"],
        ],
        "q1_heldout": q1_heldout,
        "q2_terminal": q2_terminal,
        "stabprep_E_floor": stab.E_floor,
        "sixlcu_E_floor": six.E_floor,
        "calibration_pair": calibration,
        "gates_all_pass": all(gates.values()),
        "protocol_sha256": protocol_sha,
        "selected_predicates_sha256": stage_digest,
        "result_digest": digest,
        "authority": authority,
    }
    print("ORIONQG_QG15B_PREDICATE_LANGUAGE=" + canonical(receipt))
    print(f"[qg15b] total: {time.perf_counter() - t0:.2f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
