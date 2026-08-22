#!/usr/bin/env python3
"""QG-23 generic verification -- independent, pure-primitive, and falsifiable.

Verifies research/extensions/orion-qg/QG23_FORECAST_N_DEPENDENCE_RESULTS.json.

It imports NOTHING from the QG-23 analyzer, and nothing from qg15_third_family,
qg15b_predicate_language or qg15c_vocabulary.  All ground truth is rebuilt through the
committed independent verifier layers qg15_generic_verify (Paulis carried as
(sign, letters) with the gate conjugation tables derived numerically from the gate
unitaries -- no tableau rules shared with the analyzer chain) and qg15c_generic_verify
(its independent rebuild of the frozen GE donor schedule trace, the E3 ladder, the
tensor-factor restriction and all 33 V2 features).  On top of those layers this file
re-derives, from scratch and WITHOUT taking the analyzer's numbers as inputs:

  * the complete n<=3 training table with labels from its own Dijkstra referee,
  * the per-feature observed range spans and maxima at n = 1,2,3,
  * both fits in both coordinates, with residuals and domains, and the frozen
    four-way classification,
  * the normalization map phi_n, its divisors and its integer quantization,
  * the normalized n<=3 support box, the normalized n=4 panel and the support radii,
  * the cell-lookup predictions (raw and normalized) and every confusion,
  * the full coverage/accuracy trade-off curve at every threshold on the ladder,
  * the H0 and H1 verdicts and the terminal, from its own numbers,
  * the stage-1 prediction digest, rebuilt field by field,
  * an independent literal enumeration and a complete brute-force minimum-error search
    on a sub-lattice for BOTH the raw and the normalized arms, with no R5/R6 reductions
    and no pruning bounds.

Serialized predicates (the lattice witnesses) are treated as CLAIMS and re-evaluated
against independently rebuilt feature vectors; the sub-lattice brute force independently
bounds the claimed minima.

FALSIFIABILITY.  A verifier that cannot fail proves nothing, so this one demonstrates its
own teeth in-run: after judging the real receipt it re-judges several deliberately
tampered copies of it.  Each tamper is a single minimal field mutation AND the tampered
copy's result_digest is recomputed so that it is internally self-consistent -- the
tampers are therefore caught by the independent re-derivation, not by a hash mismatch.
Every tamper must REJECT or the verifier itself reports FALSIFIABILITY_NOT_DEMONSTRATED.

Usage:  qg23_generic_verify.py [RESULTS_JSON]

Prints exactly one token line:
ORIONQG_QG23_GENERIC_VERIFY={"decision":"ACCEPT"|"REJECT",...}
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

import qg15_generic_verify as gv  # noqa: E402  (committed independent primitive layer)
import qg15c_generic_verify as gv15c  # noqa: E402  (committed independent V2 layer)

DEFAULT_RESULTS = (REPO / "research" / "extensions" / "orion-qg"
                   / "QG23_FORECAST_N_DEPENDENCE_RESULTS.json")
QG15_RESULTS = (REPO / "research" / "extensions" / "orion-qg"
                / "QG15_THIRD_FAMILY_RESULTS.json")
QG15B_RESULTS = (REPO / "research" / "extensions" / "orion-qg"
                 / "QG15B_PREDICATE_LANGUAGE_RESULTS.json")
QG15C_RESULTS = (REPO / "research" / "extensions" / "orion-qg"
                 / "QG15C_VOCABULARY_RESULTS.json")
PROTOCOL = HERE / "QG23_FORECAST_N_DEPENDENCE_PROTOCOL_V1.md"
OUTPUT = HERE / "QG23_GENERIC_VERIFICATION.json"

PANEL_SEED = 20260821
PANEL_SIZE = 120
SCALE = 1000
DIVISOR_FLOOR = 1.0
THRESHOLD_LADDER = (0.0, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00, 4.00, 8.00, None)
H1_COVERAGE_MATERIAL_DELTA = 12
H1_ACCURACY_SEPARATION_RATIO = 0.5
H0_INSUPPORT_MAJORITY = 60
SUBLATTICE = [(1, 1), (1, 2), (1, 3), (2, 1)]
V2_FEATURES = list(gv15c.V2_FEATURES)
CONSUMED = {
    "normalized_cell_lookup": "exact_cell",
    "normalized_lattice_headline": "box_support",
    "normalized_lattice_inherited_cell": "box_support",
}
UNSIGNED_EXCLUDE = ("result_digest", "timing", "n5_measured_obstacle")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def note(msg):
    print(f"[qg23-verify] {msg}", file=sys.stderr)


def rd(x, k=6):
    return round(x + 0.0, k)


def digest_of(raw):
    unsigned = {k: v for k, v in raw.items() if k not in UNSIGNED_EXCLUDE}
    return hashlib.sha256(canonical(unsigned).encode()).hexdigest()


# ------------------------------------------------------------------ own fitting
def lsq(xs, ys):
    m = len(xs)
    mx = sum(xs) / m
    my = sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx if sxx else 0.0
    b = my - a * mx
    res = [y - (a * x + b) for x, y in zip(xs, ys)]
    sst = sum((y - my) ** 2 for y in ys)
    sse = sum(r * r for r in res)
    r2 = 1.0 if sst == 0.0 else 1.0 - sse / sst
    return a, b, r2, res


def fit_pair(xs, ys):
    a, b, r2, res = lsq(xs, ys)
    pos = [(x, y) for x, y in zip(xs, ys) if y > 0]
    if len(pos) >= 2:
        p, q, r2g, resg = lsq([math.log(x) for x, _ in pos],
                              [math.log(y) for _, y in pos])
        log = (True, p, q, r2g, resg, [x for x, _ in pos])
    else:
        log = (False, None, None, None, None, [x for x, _ in pos])
    return (a, b, r2, res), log


def classify(span, distinct, r2_lin, log_defined, r2_log):
    if distinct <= 1:
        return "DEGENERATE"
    if span[2] <= span[0]:
        return "INTENSIVE"
    if (not log_defined) or r2_lin >= r2_log:
        return "EXTENSIVE_LINEAR"
    return "EXTENSIVE_OTHER"


def divisor(cls, a, b, p, q, n):
    if cls in ("INTENSIVE", "DEGENERATE"):
        return 1.0
    raw = (a * n + b) if cls == "EXTENSIVE_LINEAR" else math.exp(q) * (n ** p)
    return max(raw, DIVISOR_FLOOR)


def phi_val(x, cls, dv):
    if cls in ("INTENSIVE", "DEGENERATE"):
        return int(x)
    return int(math.floor(SCALE * x / dv + 0.5))


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


def split_accuracy(flags, labels, mask):
    idx = [i for i, m in enumerate(mask) if m]
    err = sum(1 for i in idx if flags[i] != labels[i])
    return {"size": len(idx), "errors": err, "correct": len(idx) - err,
            "error_rate": (rd(err / len(idx)) if idx else None),
            "accuracy": (rd(1.0 - err / len(idx)) if idx else None)}


# --------------------------------------------------- independent ground truth
class Ground:
    """Everything the verifier derives on its own, before it looks at any claim."""

    def __init__(self):
        self.protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
        self.r15 = json.loads(QG15_RESULTS.read_text())
        self.r15b = json.loads(QG15B_RESULTS.read_text())
        self.r15c = json.loads(QG15C_RESULTS.read_text())
        self.NF = len(V2_FEATURES)

        note("rebuilding referee + donor + schedule trace + V2 features for n<=3")
        rows = []
        for n in (1, 2, 3):
            dist = gv.referee(n)
            for state in sorted(dist, key=lambda s: gv.state_key(s, n)):
                _v1, v2, cd, lb, _c = gv15c.features(state, n)
                copt = dist[state]
                assert lb <= copt <= cd
                rows.append((v2, copt == cd, n))
        self.rows = rows

        note("re-deriving the census, both fits in both coordinates, and phi_n")
        per_n = {n: [r for r in rows if r[2] == n] for n in (1, 2, 3)}
        self.census = {}
        self.cls_of = {}
        self.div_of = {}
        for i, name in enumerate(V2_FEATURES):
            obs = {n: [r[0][i] for r in per_n[n]] for n in (1, 2, 3)}
            span = [max(obs[n]) - min(obs[n]) for n in (1, 2, 3)]
            omax = [max(obs[n]) for n in (1, 2, 3)]
            omin = [min(obs[n]) for n in (1, 2, 3)]
            lin, log = fit_pair([1, 2, 3], span)
            mlin, mlog = fit_pair([1, 2, 3], omax)
            distinct = len({r[0][i] for r in rows})
            cls = classify(span, distinct, rd(lin[2]), log[0],
                           rd(log[3]) if log[0] else None)
            ra, rb = rd(lin[0]), rd(lin[1])
            rp, rq = (rd(log[1]), rd(log[2])) if log[0] else (None, None)
            self.cls_of[i] = cls
            self.div_of[i] = (cls, {n: divisor(cls, ra, rb, rp, rq, n)
                                    for n in (1, 2, 3, 4, 5)})
            self.census[name] = {
                "span": span, "max": omax, "min": omin, "distinct": distinct,
                "cls": cls, "lin": lin, "log": log, "mlin": mlin, "mlog": mlog,
                "ra": ra, "rb": rb, "rp": rp, "rq": rq,
            }
        self.class_counts = {}
        for i in range(self.NF):
            self.class_counts[self.cls_of[i]] = self.class_counts.get(
                self.cls_of[i], 0) + 1

        note("regenerating the seeded n=4 panel and labelling it independently")
        rng = np.random.default_rng(PANEL_SEED)
        panel, seen = [], set()
        while len(panel) < PANEL_SIZE:
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
        self.panel = panel
        self.panel_keys_sha = hashlib.sha256(
            "\n".join(canonical(list(gv.state_key(s, 4)))
                      for s in panel).encode()).hexdigest()
        self.pfeat = []
        for s in panel:
            _v1, v2, cd, lb, _c = gv15c.features(s, 4)
            self.pfeat.append((v2, cd, lb, s))
        d4 = gv.referee(4)
        self.n4_states = len(d4)
        self.labels4 = []
        for v2, cd, lb, s in self.pfeat:
            copt = d4[s]
            assert lb <= copt <= cd
            self.labels4.append(copt == cd)

        NF = self.NF
        self.raw_lo = [min(r[0][i] for r in rows) for i in range(NF)]
        self.raw_hi = [max(r[0][i] for r in rows) for i in range(NF)]
        self.raw_box_in = [all(self.raw_lo[i] <= p[0][i] <= self.raw_hi[i]
                               for i in range(NF)) for p in self.pfeat]
        self.train_cells = {}
        for v2, lab, _n in rows:
            self.train_cells[v2] = self.train_cells.get(v2, True) and lab
        self.raw_seen = [p[0] in self.train_cells for p in self.pfeat]

        note("re-deriving the normalized tables, the support box and the radii")
        self.nrows = [(self.phi(r[0], r[2]), r[1], r[2]) for r in rows]
        self.npanel = [self.phi(p[0], 4) for p in self.pfeat]
        self.n_lo = [min(r[0][i] for r in self.nrows) for i in range(NF)]
        self.n_hi = [max(r[0][i] for r in self.nrows) for i in range(NF)]
        self.n_den = [(self.n_hi[i] - self.n_lo[i]) if self.n_hi[i] > self.n_lo[i]
                      else max(abs(self.n_lo[i]), 1) for i in range(NF)]
        self.dists = [self.sdist(v) for v in self.npanel]
        self.norm_box_in = [d == 0.0 for d in self.dists]
        self.norm_cells = {}
        for v, lab, _n in self.nrows:
            self.norm_cells[v] = self.norm_cells.get(v, True) and lab
        self.norm_seen = [v in self.norm_cells for v in self.npanel]
        self.ladder = []
        for tau in THRESHOLD_LADDER:
            lim = math.inf if tau is None else tau
            self.ladder.append((("inf" if tau is None else tau),
                                [d <= lim for d in self.dists]))

        note("independent literal enumeration + brute-force sub-lattice (both arms)")
        self.arms = {}
        for arm_key, tab in (("raw_arm", [(r[0], r[1]) for r in rows]),
                             ("normalized_arm", [(r[0], r[1]) for r in self.nrows])):
            cells, pos, neg, mixed, floor = gv15c.build_cells(
                [(t[0], t[0], t[1]) for t in tab], 0)
            masks, _grids = gv15c.literal_masks(cells, NF)
            brute = gv15c.brute_sublattice(cells, pos, neg, masks)
            self.arms[arm_key] = {
                "table": tab, "cells": len(cells), "mixed": len(mixed),
                "floor": floor, "P": sum(pos), "N": sum(neg),
                "pool": len(masks), "brute": brute,
            }

    def phi(self, vec, n):
        return tuple(phi_val(vec[i], self.div_of[i][0], self.div_of[i][1][n])
                     for i in range(self.NF))

    def sdist(self, v):
        worst = 0.0
        for i in range(self.NF):
            if v[i] < self.n_lo[i]:
                e = (self.n_lo[i] - v[i]) / self.n_den[i]
            elif v[i] > self.n_hi[i]:
                e = (v[i] - self.n_hi[i]) / self.n_den[i]
            else:
                e = 0.0
            if e > worst:
                worst = e
        return worst

    def train_err(self, wit, tab):
        memo = {}
        e = 0
        for vec, lab in tab:
            r = memo.get(vec)
            if r is None:
                r = gv15c.eval_predicate(wit, V2_FEATURES, vec)
                memo[vec] = r
            e += (r != lab)
        return e


# ------------------------------------------------------------- the check battery
def evaluate(raw, G):
    """Every check, as a pure function of the claimed receipt and the independent
    ground truth.  Returns (checks, rebuilt)."""
    checks = {}
    rebuilt = {}
    NF = G.NF
    labels4 = G.labels4

    # ---- envelope
    checks["schema"] = raw.get("schema") == "orion-qg.qg23_forecast_n_dependence.v1"
    checks["protocol_sha256"] = raw.get("protocol_sha256") == G.protocol_sha
    checks["result_digest"] = raw.get("result_digest") == digest_of(raw)
    checks["upstream_receipt_hashes"] = (
        raw["qg15_results_sha256"] == hashlib.sha256(
            QG15_RESULTS.read_bytes()).hexdigest()
        and raw["qg15b_results_sha256"] == hashlib.sha256(
            QG15B_RESULTS.read_bytes()).hexdigest()
        and raw["qg15c_results_sha256"] == hashlib.sha256(
            QG15C_RESULTS.read_bytes()).hexdigest())

    # ---- G1 / G2
    checks["G1_receipt_bindings_exact"] = (
        G.r15["component5_prospective"]["regime_correct"] == 100
        and G.r15["component5_prospective"]["cost_correct"] == 67
        and G.r15["component5_prospective"]["panel"]["size"] == 120
        and G.r15b["stabprep"]["cell_table"]["mixed_cells"] == 12
        and G.r15b["stabprep"]["cell_table"]["E_floor"] == 43
        and len(G.r15c["vocabulary"]["V2_features"]) == 33
        and G.r15c["v2_cell_table"]["mixed_cells"] == 1
        and G.r15c["v2_cell_table"]["E_floor"] == 1
        and G.r15c["heldout"]["H1_cell_lookup"]["confusion"]["errors"] == 32
        and G.r15c["heldout"]["H1_cell_lookup"]["unseen_cells"] == 120
        and G.r15c["heldout"]["H2_lattice_predicate"]["confusion"]["errors"] == 3
        and raw["gates"]["G1_receipt_bindings_exact"] is True
        and raw["gates"]["G1_mismatches"] == {})
    checks["G2_vocabulary_verbatim"] = (
        V2_FEATURES == G.r15c["vocabulary"]["V2_features"]
        and len(V2_FEATURES) == 33
        and V2_FEATURES[:13] == G.r15c["vocabulary"]["V1_features"]
        and "negative_sign_census" not in V2_FEATURES
        and [rec["feature"] for rec in
             raw["q1_extensive_intensive_census"]["per_feature"]] == V2_FEATURES
        and raw["gates"]["G2_no_vocabulary_change"] is True)

    checks["training_domain_complete"] = (
        len(G.rows) == 1146 == raw["domains"]["training_instances"])
    rebuilt["training_rows"] = len(G.rows)

    # ---- Q1 census, field by field
    stored = {rec["feature"]: rec
              for rec in raw["q1_extensive_intensive_census"]["per_feature"]}
    ok = True
    fits_complete = True
    for i, name in enumerate(V2_FEATURES):
        c = G.census[name]
        rec = stored.get(name)
        if rec is None:
            ok = False
            continue
        a, b, r2l, resl = c["lin"]
        ld, p, q, r2g, resg, ldom = c["log"]
        ok &= rec["class"] == c["cls"]
        ok &= rec["observed_range_span_per_n"] == {f"n{n}": c["span"][n - 1]
                                                  for n in (1, 2, 3)}
        ok &= rec["observed_max_per_n"] == {f"n{n}": c["max"][n - 1] for n in (1, 2, 3)}
        ok &= rec["observed_min_per_n"] == {f"n{n}": c["min"][n - 1] for n in (1, 2, 3)}
        ok &= rec["distinct_values_on_training_domain"] == c["distinct"]
        fs = rec["fit_of_range_span"]
        ok &= fs["fit_linear_coordinate"]["slope"] == rd(a)
        ok &= fs["fit_linear_coordinate"]["intercept"] == rd(b)
        ok &= fs["fit_linear_coordinate"]["r2"] == rd(r2l)
        ok &= fs["fit_linear_coordinate"]["residuals"] == [rd(x) for x in resl]
        ok &= fs["fit_linear_coordinate"]["points"] == [[n, c["span"][n - 1]]
                                                        for n in (1, 2, 3)]
        ok &= fs["fit_loglog_coordinate"]["defined"] == ld
        if ld:
            ok &= fs["fit_loglog_coordinate"]["slope"] == rd(p)
            ok &= fs["fit_loglog_coordinate"]["intercept"] == rd(q)
            ok &= fs["fit_loglog_coordinate"]["r2"] == rd(r2g)
            ok &= fs["fit_loglog_coordinate"]["residuals"] == [rd(x) for x in resg]
            ok &= fs["fit_loglog_coordinate"]["domain_n"] == ldom
        fm = rec["fit_of_observed_max"]
        ma, mb, mr2, mres = c["mlin"]
        ok &= fm["fit_linear_coordinate"]["slope"] == rd(ma)
        ok &= fm["fit_linear_coordinate"]["r2"] == rd(mr2)
        ok &= fm["fit_linear_coordinate"]["residuals"] == [rd(x) for x in mres]
        ok &= fm["fit_loglog_coordinate"]["defined"] == c["mlog"][0]
        for blk in (fs, fm):
            fits_complete &= (blk["fit_linear_coordinate"]["domain_n"] == [1, 2, 3]
                              and blk["fit_linear_coordinate"]["residuals"] is not None
                              and "fit_loglog_coordinate" in blk
                              and "three_point_caveat" in blk)
        ok &= rec["phi_divisor_per_n"] == {f"n{n}": rd(G.div_of[i][1][n])
                                           for n in (1, 2, 3, 4, 5)}
        out = sum(1 for pf in G.pfeat
                  if not (G.raw_lo[i] <= pf[0][i] <= G.raw_hi[i]))
        ok &= rec["panel_out_of_range_on_this_feature_alone"] == out
        ok &= rec["training_observed_range_n_le_3"] == [G.raw_lo[i], G.raw_hi[i]]
        nout = sum(1 for v in G.npanel if not (G.n_lo[i] <= v[i] <= G.n_hi[i]))
        ok &= rec["panel_out_of_normalized_range_on_this_feature_alone"] == nout
        ok &= rec["normalized_training_range_n_le_3"] == [G.n_lo[i], G.n_hi[i]]
    checks["census_per_feature_rederived"] = bool(ok)
    checks["G4_both_fits_both_coordinates_residuals_domain"] = bool(
        fits_complete
        and raw["gates"]["G4_both_fits_both_coordinates_residuals_domain"] is True)
    checks["class_counts"] = (
        raw["q1_extensive_intensive_census"]["class_counts"] == G.class_counts)
    rebuilt["class_counts"] = G.class_counts

    # ---- H0 support census
    def class_out(pred):
        sel = [i for i in range(NF) if pred(G.cls_of[i])]
        return sum(1 for p in G.pfeat
                   if any(not (G.raw_lo[i] <= p[0][i] <= G.raw_hi[i]) for i in sel))

    h0 = raw["q1_extensive_intensive_census"]["support_failure_census_H0"]
    intensive_only = class_out(lambda c: c in ("INTENSIVE", "DEGENERATE"))
    checks["H0_support_census"] = (
        h0["intensive_and_degenerate_combined"][
            "panel_vectors_out_of_support_on_this_class_alone"] == intensive_only
        and h0["extensive_combined"][
            "panel_vectors_out_of_support_on_this_class_alone"]
        == class_out(lambda c: c.startswith("EXTENSIVE"))
        and h0["panel_in_box_support_unnormalized"] == sum(G.raw_box_in)
        and h0["panel_out_of_box_support_unnormalized"] == PANEL_SIZE - sum(G.raw_box_in)
        and h0["panel_exact_cell_seen_unnormalized"] == sum(G.raw_seen)
        and h0["panel_exact_cell_unseen_unnormalized"] == PANEL_SIZE - sum(G.raw_seen))
    rebuilt["intensive_only_out_of_support"] = intensive_only
    rebuilt["panel_out_of_box_support_unnormalized"] = PANEL_SIZE - sum(G.raw_box_in)

    # ---- panel provenance
    checks["G5_no_panel_reselection"] = (
        G.panel_keys_sha == G.r15["component5_prospective"]["panel"]["panel_keys_sha256"]
        == raw["domains"]["panel_keys_sha256"]
        and raw["gates"]["G5_no_panel_reselection"] is True
        and raw["q3_abstaining_forecaster"]["prospective_n5"][
            "sampled_panel_formed"] is False)
    checks["n4_state_space_complete"] = (
        G.n4_states == gv.expected_count(4) == raw["domains"]["n4_state_space"])
    checks["panel_positives"] = (
        sum(labels4) == 32
        == raw["q2_normalization"]["unnormalized_baselines_recomputed_in_run"][
            "panel_positives_recomputed"]
        == G.r15c["heldout"]["panel_positives"])
    rebuilt["panel_positives"] = sum(labels4)

    # ---- coverage
    cov = raw["q2_normalization"]["coverage"]
    checks["coverage"] = (
        cov["unnormalized"]["box_support_in"] == sum(G.raw_box_in)
        and cov["unnormalized"]["exact_cell_seen"] == sum(G.raw_seen)
        and cov["normalized"]["box_support_in"] == sum(G.norm_box_in)
        and cov["normalized"]["exact_cell_seen"] == sum(G.norm_seen)
        and cov["delta_box_support"] == sum(G.norm_box_in) - sum(G.raw_box_in)
        and cov["delta_exact_cell"] == sum(G.norm_seen) - sum(G.raw_seen)
        and cov["panel_size"] == PANEL_SIZE == len(G.npanel))
    rebuilt["coverage_unnormalized_box"] = sum(G.raw_box_in)
    rebuilt["coverage_normalized_box"] = sum(G.norm_box_in)
    rebuilt["coverage_unnormalized_exact_cell"] = sum(G.raw_seen)
    rebuilt["coverage_normalized_exact_cell"] = sum(G.norm_seen)

    # ---- predictors: rebuilt cell lookup, re-evaluated witnesses
    refit = raw["q2_normalization"]["predictor_refit"]
    raw_wit = refit["raw_arm"]["headline_witness"]
    nrm_wit = refit["normalized_arm"]["headline_witness"]
    inh_wit = refit["normalized_arm"]["inherited_witness"]
    preds = {
        "raw_cell_lookup_qg15c": [G.train_cells.get(p[0], False) for p in G.pfeat],
        "raw_lattice_qg15c_headline": [
            gv15c.eval_predicate(raw_wit, V2_FEATURES, p[0]) for p in G.pfeat],
        "normalized_cell_lookup": [G.norm_cells.get(v, False) for v in G.npanel],
        "normalized_lattice_headline": [
            gv15c.eval_predicate(nrm_wit, V2_FEATURES, v) for v in G.npanel],
        "normalized_lattice_inherited_cell": [
            gv15c.eval_predicate(inh_wit, V2_FEATURES, v) for v in G.npanel],
    }
    stored_scores = raw["q2_normalization"]["predictor_scores"]
    ok = set(stored_scores) == set(preds)
    for name, flags in preds.items():
        s = stored_scores.get(name)
        if s is None:
            ok = False
            continue
        cov_mask = G.norm_box_in if name.startswith("normalized") else G.raw_box_in
        seen_mask = G.norm_seen if name.startswith("normalized") else G.raw_seen
        conf = confusion(flags, labels4)
        ok &= s["confusion"] == conf and s["errors_out_of_120"] == conf["errors"]
        ok &= s["box_support_covered"] == split_accuracy(flags, labels4, cov_mask)
        ok &= s["box_support_uncovered"] == split_accuracy(
            flags, labels4, [not m for m in cov_mask])
        ok &= s["exact_cell_seen"] == split_accuracy(flags, labels4, seen_mask)
        ok &= s["exact_cell_unseen"] == split_accuracy(
            flags, labels4, [not m for m in seen_mask])
    checks["predictor_scores_rederived"] = bool(ok)

    base = raw["q2_normalization"]["unnormalized_baselines_recomputed_in_run"]
    raw_cl = confusion(preds["raw_cell_lookup_qg15c"], labels4)["errors"]
    raw_lat = confusion(preds["raw_lattice_qg15c_headline"], labels4)["errors"]
    checks["baselines_recomputed_32_and_3"] = (
        raw_cl == 32 == base["cell_lookup_recomputed_in_run"]
        == G.r15c["heldout"]["H1_cell_lookup"]["confusion"]["errors"]
        and raw_lat == 3 == base["lattice_recomputed_in_run"]
        == G.r15c["heldout"]["H2_lattice_predicate"]["confusion"]["errors"])
    checks["raw_headline_witness_is_the_qg15c_witness"] = (
        canonical(raw_wit) == canonical(
            G.r15c["heldout"]["H2_lattice_predicate"]["witness"])
        and refit["raw_arm"]["headline_cell"] == G.r15c["search"]["headline_cell"])
    rebuilt["baseline_cell_lookup"] = raw_cl
    rebuilt["baseline_lattice"] = raw_lat
    rebuilt["normalized_cell_lookup_errors"] = confusion(
        preds["normalized_cell_lookup"], labels4)["errors"]
    rebuilt["normalized_lattice_errors"] = confusion(
        preds["normalized_lattice_headline"], labels4)["errors"]

    # ---- every witness on both surfaces re-evaluated for its training error
    ok = True
    for arm_key in ("raw_arm", "normalized_arm"):
        tab = G.arms[arm_key]["table"]
        for _cell, rec in refit[arm_key]["minerr_surface"].items():
            ok &= G.train_err(rec["witness"], tab) == rec["minerr"]
    checks["witness_training_error_reevaluated"] = bool(ok)

    # ---- independent cell tables + brute-force sub-lattice minima, both arms
    ok = True
    for arm_key in ("raw_arm", "normalized_arm"):
        A = G.arms[arm_key]
        ok &= (A["cells"] == refit[arm_key]["cells"]
               and A["mixed"] == refit[arm_key]["mixed_cells"]
               and A["floor"] == refit[arm_key]["E_floor"]
               and A["P"] == refit[arm_key]["P_total"]
               and A["N"] == refit[arm_key]["N_total"]
               and A["pool"] == refit[arm_key]["literal_stats"]["pool_literals"])
        for (K, D) in SUBLATTICE:
            rec = refit[arm_key]["minerr_surface"][f"K{K}_D{D}"]
            ok &= (not rec["truncated"]) and rec["minerr"] == A["brute"][(K, D)]
    checks["sublattice_minimality_both_arms"] = bool(ok)
    rebuilt["sublattice"] = {
        k: {"cells": v["cells"], "mixed": v["mixed"], "E_floor": v["floor"],
            "literal_pool": v["pool"],
            "sublattice_minerr": {f"K{a}_D{b}": w
                                  for (a, b), w in sorted(v["brute"].items())}}
        for k, v in G.arms.items()}

    # ---- Q3 curve at every threshold (G6, two-sided)
    ok = True
    two_sided = True
    curves = raw["q3_abstaining_forecaster"]["curves"]
    ok &= set(curves) == set(preds)
    for name, flags in preds.items():
        stored_rows = curves.get(name, {}).get("ladder", [])
        ok &= len(stored_rows) == len(G.ladder)
        for row, (tau, mask) in zip(stored_rows, G.ladder):
            pred = split_accuracy(flags, labels4, mask)
            abst = split_accuracy(flags, labels4, [not m for m in mask])
            ok &= (row["support_radius_tau"] == tau
                   and row["predicted"] == pred["size"]
                   and row["coverage_fraction"] == rd(pred["size"] / PANEL_SIZE)
                   and row["errors_among_predicted"] == pred["errors"]
                   and row["error_rate_among_predicted"] == pred["error_rate"]
                   and row["abstained"] == abst["size"]
                   and row["errors_among_abstained"] == abst["errors"]
                   and row["error_rate_among_abstained"] == abst["error_rate"])
            two_sided &= ("predicted" in row and "error_rate_among_predicted" in row)
    checks["q3_curves_rederived"] = bool(ok)
    checks["G6_abstention_reported_two_sided"] = bool(
        two_sided and raw["gates"]["G6_abstention_reported_two_sided"] is True)
    checks["frozen_ladder_matches"] = (
        raw["q3_abstaining_forecaster"]["frozen_threshold_ladder"]
        == [("inf" if t is None else t) for t in THRESHOLD_LADDER])

    # ---- H0 / H1 / terminal, recomputed from the verifier's own numbers
    box_out = PANEL_SIZE - sum(G.raw_box_in)
    h0_refuted = (box_out > 0 and intensive_only >= box_out) or (
        sum(G.raw_box_in) > H0_INSUPPORT_MAJORITY)
    h0_want = "REFUTED" if h0_refuted else "BORNE_OUT"
    checks["H0_verdict"] = raw["verdicts"]["H0"] == h0_want
    rebuilt["H0"] = h0_want

    h1_any = h1_consumed = False
    for name in preds:
        if not name.startswith("normalized"):
            continue
        for measure, mask, delta in (
                ("box_support", G.norm_box_in,
                 sum(G.norm_box_in) - sum(G.raw_box_in)),
                ("exact_cell", G.norm_seen, sum(G.norm_seen) - sum(G.raw_seen))):
            cv = split_accuracy(preds[name], labels4, mask)
            uv = split_accuracy(preds[name], labels4, [not m for m in mask])
            cov_ok = delta >= H1_COVERAGE_MATERIAL_DELTA
            acc_ok = (cv["error_rate"] is not None and uv["error_rate"] is not None
                      and uv["error_rate"] > 0
                      and cv["error_rate"] / uv["error_rate"]
                      <= H1_ACCURACY_SEPARATION_RATIO)
            if cov_ok and acc_ok:
                h1_any = True
                if CONSUMED[name] == measure:
                    h1_consumed = True
    h1_want = "BORNE_OUT" if h1_consumed else "REFUTED"
    checks["H1_verdict"] = raw["verdicts"]["H1"] == h1_want
    checks["H1_alternative_reading_disclosed"] = (
        raw["criterion_disclosure"]["H1_under_all_pairs_reading"]
        == ("BORNE_OUT" if h1_any else "REFUTED")
        and raw["criterion_disclosure"]["H1_under_consumed_measure_reading"] == h1_want)
    rebuilt["H1"] = h1_want
    rebuilt["H1_all_pairs_reading"] = "BORNE_OUT" if h1_any else "REFUTED"

    if h0_want == "REFUTED":
        want_terminal = "QG23_H0_REFUTED__THE_FORECAST_IS_WRONG_NOT_MISAPPLIED"
    elif h1_want == "BORNE_OUT":
        want_terminal = ("QG23_N_DEPENDENCE_EXPLAINS_THE_REFUTATION__"
                         "CERTIFIED_REGION_ESTABLISHED")
    else:
        want_terminal = ("QG23_PARTIAL__SUPPORT_DIAGNOSED_BUT_NORMALIZATION_"
                         "DOES_NOT_TRANSFER")
    checks["terminal_follows_the_verdicts"] = raw["terminal"] == want_terminal
    checks["authority_string_matches_terminal"] = (
        raw["authority"] == f"ORION_QG23_FORECAST_N_DEPENDENCE_{raw['terminal']}__"
        "STABPREP_DONOR_EXACT_BOUNDARY_SUPPORT_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6")
    rebuilt["terminal"] = want_terminal

    # ---- stage-1 digest, rebuilt field by field
    stage1 = {
        "protocol_sha256": G.protocol_sha,
        "v2_features": V2_FEATURES,
        "phi_n": {
            "scale": SCALE,
            "divisor_floor": DIVISOR_FLOOR,
            "per_feature": [
                {"feature": V2_FEATURES[i], "class": G.cls_of[i],
                 "divisor_n1": rd(G.div_of[i][1][1]), "divisor_n2": rd(G.div_of[i][1][2]),
                 "divisor_n3": rd(G.div_of[i][1][3]), "divisor_n4": rd(G.div_of[i][1][4])}
                for i in range(NF)],
        },
        "normalized_training_support_box": [[G.n_lo[i], G.n_hi[i]] for i in range(NF)],
        "panel_keys_sha256": G.panel_keys_sha,
        "normalized_panel_vectors": [list(v) for v in G.npanel],
        "raw_panel_vectors": [list(p[0]) for p in G.pfeat],
        "support_distances": [rd(d) for d in G.dists],
        "predictions": {k: list(map(bool, v)) for k, v in sorted(preds.items())},
        "abstain_masks": {str(t): list(map(bool, m)) for t, m in G.ladder},
        "raw_headline_cell": refit["raw_arm"]["headline_cell"],
        "raw_headline_witness": raw_wit,
        "normalized_headline_cell": refit["normalized_arm"]["headline_cell"],
        "normalized_headline_witness": nrm_wit,
        "normalized_inherited_cell": refit["normalized_arm"]["inherited_cell"],
        "normalized_inherited_witness": inh_wit,
        "contains_n4_referee_output": False,
    }
    checks["stage1_digest"] = raw["stage1_digest"] == hashlib.sha256(
        canonical(stage1).encode()).hexdigest()

    # ---- staging, accounting, ceiling, gates, claim boundary
    checks["G3_staging_enforced_structurally"] = (
        raw["gates"]["G3_staging_enforced_structurally"] is True
        and raw["gates"]["G3_stub_triggered"] is False
        and raw["gates"]["G3_n4_referee_before_stage1_digest"] is False
        and raw["stage1_scope"]["stub_ever_triggered"] is False
        and raw["stage1_scope"]["stub_installed_during_stage1"] is True
        and raw["stage1_scope"]["stub_removed_after_stage1"] is True
        and raw["stage1_scope"]["contains_n4_referee_output"] is False
        and sorted(raw["stage1_scope"]["referee_entry_points_stubbed"])
        == ["extract_optimal_circuit", "referee", "referee_lex"])
    n5 = raw["q3_abstaining_forecaster"]["prospective_n5"]
    checks["G7_no_silent_truncation"] = (
        raw["domains"]["training_instances"] == 1146
        and raw["domains"]["held_out_instances"] == PANEL_SIZE
        and raw["domains"]["n4_state_space"] == gv.expected_count(4)
        and n5["n5_attempted"] is False
        and n5["component"] == "NOT_ATTEMPTED"
        and n5["observed_state_count_expected"] == gv.expected_count(5) == 2423520
        and n5["n5_outcome_observed"] is False
        and isinstance(n5["reason"], str) and len(n5["reason"]) > 200
        and "referee_probe" in raw.get("n5_measured_obstacle", {})
        and "feature_probe" in raw.get("n5_measured_obstacle", {})
        and raw["gates"]["G7_no_silent_truncation"] is True)
    checks["G8_authority_ceiling_NOT_R6"] = (
        raw["authority"].endswith("__NOT_R6")
        and raw["r6_authority"] is False
        and raw["novelty_credit"] is False
        and raw["novelty_authority"] is False
        and raw["physical_quantum_advantage_claim"] is False
        and raw["network_access"] is False
        and raw["chemistry_sources_read"] is False
        and raw["reserved_stretched_n2_accessed"] is False)
    checks["G9_timing_excluded_from_digest"] = (
        all(k in raw for k in ("timing", "n5_measured_obstacle"))
        and raw["gates"]["G9_determinism_timing_excluded_from_digest"] is True)
    checks["G10_hypotheses_stated_before_measurement"] = (
        "H0_support_hypothesis" in raw["hypotheses_frozen_before_measurement"]
        and "H1_normalization_hypothesis" in raw["hypotheses_frozen_before_measurement"]
        and raw["verdicts"]["H0"] in ("BORNE_OUT", "REFUTED")
        and raw["verdicts"]["H1"] in ("BORNE_OUT", "REFUTED")
        and raw["gates"]["G10_H0_H1_stated_before_measurement"] is True)
    checks["gates_all_true"] = (
        raw["gates_all_pass"] is True
        and all(v is True for k, v in raw["gates"].items()
                if isinstance(v, bool) and k not in (
                    "G3_stub_triggered", "G3_n4_referee_before_stage1_digest"))
        and raw["gates"]["G3_stub_triggered"] is False
        and raw["gates"]["G3_n4_referee_before_stage1_digest"] is False)
    checks["claim_boundary_states_the_weaker_object"] = (
        "DIFFERENT, WEAKER OBJECT" in raw["claim_boundary"]
        and "CANNOT" in raw["claim_boundary"].upper())
    return checks, rebuilt


# --------------------------------------------------------------- tamper battery
def tampers():
    """Minimal single-field mutations, each of which MUST be rejected."""
    def t_h1(d):
        d["verdicts"]["H1"] = "BORNE_OUT"
        d["terminal"] = ("QG23_N_DEPENDENCE_EXPLAINS_THE_REFUTATION__"
                         "CERTIFIED_REGION_ESTABLISHED")
        d["authority"] = f"ORION_QG23_FORECAST_N_DEPENDENCE_{d['terminal']}__" \
            "STABPREP_DONOR_EXACT_BOUNDARY_SUPPORT_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6"

    def t_cov(d):
        d["q2_normalization"]["coverage"]["normalized"]["box_support_in"] += 9

    def t_baseline(d):
        d["q2_normalization"]["predictor_scores"][
            "raw_lattice_qg15c_headline"]["errors_out_of_120"] = 0
        d["q2_normalization"]["unnormalized_baselines_recomputed_in_run"][
            "lattice_recomputed_in_run"] = 0

    def t_class(d):
        for rec in d["q1_extensive_intensive_census"]["per_feature"]:
            if rec["class"] == "EXTENSIVE_OTHER":
                rec["class"] = "EXTENSIVE_LINEAR"
                break

    def t_witness(d):
        w = d["q2_normalization"]["predictor_refit"]["raw_arm"]["headline_witness"]
        w["conjunctions"][0][0]["threshold"] += 1

    def t_curve(d):
        d["q3_abstaining_forecaster"]["curves"][
            "raw_lattice_qg15c_headline"]["ladder"][0]["errors_among_predicted"] = 0

    def t_stage1(d):
        d["stage1_digest"] = "0" * 64

    def t_census_out(d):
        d["q1_extensive_intensive_census"]["support_failure_census_H0"][
            "intensive_and_degenerate_combined"][
                "panel_vectors_out_of_support_on_this_class_alone"] = 120

    return [
        ("H1_verdict_flipped_to_BORNE_OUT", t_h1),
        ("normalized_box_coverage_inflated", t_cov),
        ("lattice_baseline_claimed_perfect", t_baseline),
        ("one_feature_reclassified_as_linear", t_class),
        ("raw_headline_witness_threshold_shifted", t_witness),
        ("one_tradeoff_curve_cell_zeroed", t_curve),
        ("stage1_digest_replaced", t_stage1),
        ("H0_census_claims_intensive_features_did_it", t_census_out),
    ]


# ------------------------------------------------------------------------ main
def main() -> int:
    results_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_RESULTS
    raw = json.loads(results_path.read_text())
    G = Ground()

    checks, rebuilt = evaluate(raw, G)
    decision = "ACCEPT" if all(checks.values()) else "REJECT"

    note("demonstrating falsifiability on self-consistent tampered copies")
    demo = []
    for name, mutate in tampers():
        d = copy.deepcopy(raw)
        mutate(d)
        d.pop("result_digest", None)
        d["result_digest"] = digest_of(d)          # keep the copy self-consistent
        tchecks, _ = evaluate(d, G)
        tdec = "ACCEPT" if all(tchecks.values()) else "REJECT"
        demo.append({
            "tamper": name,
            "decision": tdec,
            "self_consistent_digest": tchecks.get("result_digest") is True,
            "checks_that_caught_it": sorted(k for k, v in tchecks.items() if not v),
        })
    all_rejected = all(x["decision"] == "REJECT" for x in demo)
    all_consistent = all(x["self_consistent_digest"] for x in demo)
    if not (all_rejected and all_consistent):
        decision = "REJECT"

    payload = {
        "decision": decision,
        "results_file": str(results_path),
        "checks": checks,
        "check_count": len(checks),
        "checks_failed": sorted(k for k, v in checks.items() if not v),
        "rebuilt": rebuilt,
        "falsifiability_demonstration": {
            "status": ("DEMONSTRATED" if (all_rejected and all_consistent)
                       else "FALSIFIABILITY_NOT_DEMONSTRATED"),
            "method": (
                "each tampered copy is a single minimal field mutation with its "
                "result_digest RECOMPUTED so the copy is internally self-consistent; a "
                "tamper is therefore caught by the independent re-derivation, not by a "
                "hash mismatch"),
            "tampers_tried": len(demo),
            "all_rejected": all_rejected,
            "cases": demo,
        },
        "verifier_scope": (
            "protocol section 8 verifier scope in full: complete n<=3 rebuild from the "
            "independent primitive layer, independent census with both fits in both "
            "coordinates and their residuals and domains, independent phi_n, independent "
            "panel regeneration and labelling, independent cell tables and a complete "
            "brute-force sub-lattice minimum-error search over {(1,1),(1,2),(1,3),(2,1)} "
            "for BOTH arms with no R5/R6 reductions and no pruning bounds, the full "
            "trade-off curve at every threshold, the H0/H1/terminal chain recomputed "
            "from the verifier's own numbers, and a field-by-field rebuild of the "
            "stage-1 digest"),
        "independence": (
            "imports nothing from qg23_forecast_n_dependence, qg15_third_family, "
            "qg15b_predicate_language or qg15c_vocabulary; ground truth comes from the "
            "committed qg15_generic_verify / qg15c_generic_verify layers, whose Pauli "
            "representation and conjugation tables are numerically derived and share no "
            "code with the analyzer chain. Serialized predicates are treated as claims "
            "and re-evaluated, never trusted."),
    }
    print("ORIONQG_QG23_GENERIC_VERIFY=" + canonical(payload))
    if results_path == DEFAULT_RESULTS:
        OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0 if decision == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
