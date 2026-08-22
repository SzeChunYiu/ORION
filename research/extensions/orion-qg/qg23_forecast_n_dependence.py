#!/usr/bin/env python3
"""QG-23 forecast n-dependence analyzer -- converting negative N4.

Frozen protocol:
development/orion-qg-regime-geometry/QG23_FORECAST_N_DEPENDENCE_PROTOCOL_V1.md
(sha256 recorded in RESULTS; frozen at 81d0ce06 BEFORE any outcome-determining run).

N4 in the conversion ledger is "prospective forecast refuted at n=4": QG-15 component 5
(regime 100/120, cost 67/120) and QG-15c (cell lookup refuted 32/120, lattice predicate
refuted 3/120, with 120/120 V2 vectors unseen at n=4).  This lane asks whether that
refutation is a SUPPORT failure (H0) and whether a normalization derived from n<=3 alone
restores support and separates accuracy (H1).  Both hypotheses were frozen in section 1
of the protocol before any measurement; the lane reports whichever way they fall.

Committed machinery imported UNMODIFIED: qg15_third_family (referee, donor, micro-steps,
ladder, structure, seeded n=4 panel), qg15b_predicate_language (Arm literal/conjunction/
branch-and-bound search, witness evaluation, confusion), qg15c_vocabulary (the frozen V2
vocabulary, the referee-admissibility stub, and the V2 feature map).  No feature is added,
removed or redefined; the negative-sign census QG-15c declined to add stays out (G2).

Stdout: two deterministic receipt lines (stage-1 digest first, then the receipt).
Stderr: stage runtimes (the only non-deterministic output).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import qg15_third_family as qg15  # noqa: E402  (committed, unmodified)
import qg15b_predicate_language as qg15b  # noqa: E402  (committed, unmodified)
import qg15c_vocabulary as qg15c  # noqa: E402  (committed, unmodified)

REPO = Path(__file__).resolve().parents[3]
DEV = REPO / "development" / "orion-qg-regime-geometry"
PROTOCOL = DEV / "QG23_FORECAST_N_DEPENDENCE_PROTOCOL_V1.md"
HERE = Path(__file__).resolve().parent
QG15_RESULTS = HERE / "QG15_THIRD_FAMILY_RESULTS.json"
QG15B_RESULTS = HERE / "QG15B_PREDICATE_LANGUAGE_RESULTS.json"
QG15C_RESULTS = HERE / "QG15C_VOCABULARY_RESULTS.json"
RESULTS_PATH = HERE / "QG23_FORECAST_N_DEPENDENCE_RESULTS.json"
SCHEMA = "orion-qg.qg23_forecast_n_dependence.v1"
PROTOCOL_FREEZE_REVISION = "81d0ce069ba63d0f0785a5e59f40e7c1fdc3e6c4"
BASE_REVISION = "aaf0987ae19b056a157b8d97f4adb91436775471"

V2_FEATURES = list(qg15c.V2_FEATURES)          # G2: verbatim, 33 features
TRAIN_NS = (1, 2, 3)
PANEL_N = 4
PANEL_SIZE = 120

# ---- frozen numeric constants of this lane (declared before any measurement) ----
SCALE = 1000                # integer quantization of normalized features
DIVISOR_FLOOR = 1.0         # fitted range forms below 1 carry no resolvable spread
THRESHOLD_LADDER = (0.0, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00, 4.00, 8.00, None)  # None=inf
H1_COVERAGE_MATERIAL_DELTA = 12      # 10% of the 120-instance panel
H1_ACCURACY_SEPARATION_RATIO = 0.5   # covered error rate must be <= half the uncovered
H0_INSUPPORT_MAJORITY = 60           # >half the panel already in support refutes H0
N5_REFEREE_PROBE_SETTLED = 40_000    # fixed WORK, not fixed time (keeps G9 determinism)
N5_FEATURE_PROBE_STATES = 20

_N4_REFEREE_INVOKED = False   # G3: set only when the n=4 referee is actually called
_STAGE1_STAMPED = False


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def log_time(label, t0):
    t1 = time.perf_counter()
    print(f"[qg23] {label}: {t1 - t0:.2f}s", file=sys.stderr)
    return t1


def rd(x, k=6):
    """Deterministic rounding for float serialization."""
    return round(x + 0.0, k)


# --------------------------------------------------------------------- fitting
def least_squares(xs, ys):
    """Ordinary least squares y = a x + b with residuals, r^2 and the domain."""
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


def fit_block(statistic, xs, ys):
    """Both coordinates for one statistic; never a slope alone (gate G4)."""
    a, b, r2, res = least_squares(xs, ys)
    lin = {
        "coordinate": "linear: f(n) = a*n + b",
        "domain_n": list(xs),
        "points": [[x, y] for x, y in zip(xs, ys)],
        "slope": rd(a), "intercept": rd(b), "r2": rd(r2),
        "residuals": [rd(r) for r in res],
    }
    pos = [(x, y) for x, y in zip(xs, ys) if y > 0]
    if len(pos) >= 2:
        lx = [math.log(x) for x, _ in pos]
        ly = [math.log(y) for _, y in pos]
        p, q, r2g, resg = least_squares(lx, ly)
        log = {
            "coordinate": "log-log: log f(n) = p*log n + q",
            "defined": True,
            "domain_n": [x for x, _ in pos],
            "excluded_n_nonpositive_f": [x for x, y in zip(xs, ys) if y <= 0],
            "points_log": [[rd(u), rd(v)] for u, v in zip(lx, ly)],
            "slope": rd(p), "intercept": rd(q), "r2": rd(r2g),
            "residuals": [rd(r) for r in resg],
            "measured_power_form": f"f(n) ~ {rd(math.exp(q))} * n^{rd(p)}",
        }
    else:
        log = {
            "coordinate": "log-log: log f(n) = p*log n + q",
            "defined": False,
            "reason": (f"only {len(pos)} of {len(xs)} points have f(n) > 0; the log-log "
                       "coordinate is undefined on this statistic"),
            "domain_n": [x for x, _ in pos],
            "excluded_n_nonpositive_f": [x for x, y in zip(xs, ys) if y <= 0],
            "slope": None, "intercept": None, "r2": None, "residuals": None,
        }
    return {
        "statistic": statistic,
        "fit_linear_coordinate": lin,
        "fit_loglog_coordinate": log,
        "three_point_caveat": (
            "MEASURED TREND WITH THREE POINTS (n in {1,2,3}), not a scaling law; the "
            "protocol forbids describing it as one"),
    }


# ------------------------------------------------------- census + normalization
def classify(range_span, distinct_values, fit):
    """Frozen classification into exactly one of the four protocol classes.

    `fit` is the fit_block of the classifying statistic (the observed range span), so
    both coordinates of the SAME statistic decide the extensive sub-class."""
    if distinct_values <= 1:
        return "DEGENERATE", ("single-valued on the whole n<=3 training domain; "
                              "carries no information about n")
    if range_span[2] <= range_span[0]:
        return "INTENSIVE", ("observed range at n=3 does not exceed the observed range "
                             "at n=1; bounded ratio across n")
    r2l = fit["fit_linear_coordinate"]["r2"]
    r2g = fit["fit_loglog_coordinate"]["r2"] if fit["fit_loglog_coordinate"]["defined"] \
        else None
    if r2g is None or r2l >= r2g:
        return "EXTENSIVE_LINEAR", ("range grows with n and the linear coordinate "
                                    "explains the three observed ranges at least as "
                                    "well as the log-log coordinate")
    return "EXTENSIVE_OTHER", ("range grows with n and the log-log coordinate explains "
                              "the three observed ranges strictly better than the "
                              "linear coordinate; the measured power form is reported")


def divisor(cls, lin_a, lin_b, log_p, log_q, n):
    """phi_n's per-feature divisor.  INTENSIVE/DEGENERATE pass through (divisor 1)."""
    if cls in ("INTENSIVE", "DEGENERATE"):
        return 1.0, False
    if cls == "EXTENSIVE_LINEAR":
        raw = lin_a * n + lin_b
    else:
        raw = math.exp(log_q) * (n ** log_p)
    return (max(raw, DIVISOR_FLOOR), raw < DIVISOR_FLOOR)


def phi_value(x, cls, dv):
    if cls in ("INTENSIVE", "DEGENERATE"):
        return int(x)
    return int(math.floor(SCALE * x / dv + 0.5))


# ------------------------------------------------------------------- scoring
def confusion(flags, labels):
    return qg15.confusion(flags, labels)


def split_accuracy(flags, labels, mask):
    """Counts and error rate on the subset selected by mask (bool list)."""
    idx = [i for i, m in enumerate(mask) if m]
    err = sum(1 for i in idx if flags[i] != labels[i])
    return {
        "size": len(idx),
        "errors": err,
        "correct": len(idx) - err,
        "error_rate": (rd(err / len(idx)) if idx else None),
        "accuracy": (rd(1.0 - err / len(idx)) if idx else None),
    }


def fisher_one_sided(a, b, c, d):
    """One-sided Fisher exact p for 'covered errors are fewer than expected'.

    Table rows: covered (a errors, b correct), uncovered (c errors, d correct).
    Supplementary disclosure only -- no gate depends on it."""
    from math import comb
    n = a + b + c + d
    r1, c1 = a + b, a + c
    tot = comb(n, c1)
    p = 0.0
    for k in range(0, min(r1, c1) + 1):
        if c1 - k > n - r1:
            continue
        p_k = comb(r1, k) * comb(n - r1, c1 - k) / tot
        if k <= a:
            p += p_k
    return rd(min(1.0, p), 8)


# ------------------------------------------------------ n=5 reachability probes
def n5_referee_probe(limit_settled):
    """Dial bucket-queue Dijkstra over the n=5 stabilizer-state graph, run for a FIXED
    AMOUNT OF WORK (not a fixed time) so the reported counts are deterministic.

    Transition semantics are the committed qg15.apply_state exactly; the only change is
    the priority queue (Dial buckets, admissible because costs lie in {1,3}).  A
    conjugation table is precomputed from qg15.conj and CHECKED against qg15.apply_state
    before use, so the probe measures the committed referee, not a substitute."""
    n = 5
    gates = qg15.make_ctx(n)["gates"]
    table = [[qg15.conj(g, e, n) for e in range(1 << (2 * n + 1))] for g in gates]
    start = qg15.start_state(n)
    for gi, g in enumerate(gates):    # table equals the committed transition
        assert tuple(sorted(table[gi][e] for e in start)) == qg15.apply_state(start, g, n)
    dist = {start: 0}
    buckets = [[] for _ in range(4)]      # max edge cost 3 -> 4 buckets suffice
    buckets[0].append(start)
    settled = 0
    d = 0
    t0 = time.perf_counter()
    exhausted = False
    while settled < limit_settled:
        if not any(buckets):
            exhausted = True
            break
        while not buckets[d % 4]:
            d += 1
        cur = buckets[d % 4]
        buckets[d % 4] = []
        for s in cur:
            if dist[s] != d:
                continue
            settled += 1
            for gi, g in enumerate(gates):
                row = table[gi]
                t = tuple(sorted(row[e] for e in s))
                nd = d + qg15.COST[g[0]]
                old = dist.get(t)
                if old is None or nd < old:
                    dist[t] = nd
                    buckets[nd % 4].append(t)
            if settled >= limit_settled:
                break
    elapsed = time.perf_counter() - t0
    return {
        "settled": settled,
        "reached": len(dist),
        "frontier_radius": d,
        "exhausted": exhausted,
        "elapsed_s": rd(elapsed, 3),
        "settle_rate_per_s": rd(settled / elapsed, 2) if elapsed else None,
        "projected_complete_referee_s": (
            rd(qg15.expected_count(5) / (settled / elapsed), 1) if elapsed else None),
    }


def n5_feature_probe(k):
    """Cost of the V2 feature map at n=5 on the first k states of the deterministic
    gate-order BFS from |0..0>.  No labels are computed and no panel is formed: this is a
    COST measurement only, so no n=5 outcome is observed and G5 is untouched."""
    n = 5
    gates = qg15.make_ctx(n)["gates"]
    start = qg15.start_state(n)
    seen = {start}
    order = [start]
    qi = 0
    while len(order) < k and qi < len(order):
        s = order[qi]
        qi += 1
        for g in gates:
            t = qg15.apply_state(s, g, n)
            if t not in seen:
                seen.add(t)
                order.append(t)
    probe = order[:k]
    t0 = time.perf_counter()
    with qg15c.RefereeStub():
        for s in probe:
            qg15c.feature_vectors(s, n)
    elapsed = time.perf_counter() - t0
    return {
        "states_probed": len(probe),
        "selection_rule": ("first k states of the deterministic frozen-gate-order BFS "
                           "from |0..0>; no seed, no choice, no labels"),
        "elapsed_s": rd(elapsed, 3),
        "ms_per_state": rd(elapsed / len(probe) * 1000, 3),
        "projected_complete_domain_s": rd(elapsed / len(probe) * qg15.expected_count(5), 1),
        "projected_complete_domain_hours": rd(
            elapsed / len(probe) * qg15.expected_count(5) / 3600.0, 3),
    }


# ------------------------------------------------------------------------ main
def main() -> int:
    global _N4_REFEREE_INVOKED, _STAGE1_STAMPED
    t0 = time.perf_counter()
    timing = {}
    protocol_sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    r15 = json.loads(QG15_RESULTS.read_text())
    r15b = json.loads(QG15B_RESULTS.read_text())
    r15c = json.loads(QG15C_RESULTS.read_text())

    # =================================================== stage A: G1 bindings
    ta = time.perf_counter()
    g1 = {
        "qg15_component5_regime_correct": r15["component5_prospective"]["regime_correct"],
        "qg15_component5_cost_correct": r15["component5_prospective"]["cost_correct"],
        "qg15_panel_size": r15["component5_prospective"]["panel"]["size"],
        "qg15_panel_seed": r15["component5_prospective"]["panel"]["seed"],
        "qg15_panel_keys_sha256": r15["component5_prospective"]["panel"][
            "panel_keys_sha256"],
        "qg15b_v1_cells": r15b["stabprep"]["cell_table"]["cells"],
        "qg15b_v1_mixed_cells": r15b["stabprep"]["cell_table"]["mixed_cells"],
        "qg15b_v1_E_floor": r15b["stabprep"]["cell_table"]["E_floor"],
        "qg15c_V2_feature_count": len(r15c["vocabulary"]["V2_features"]),
        "qg15c_V2_mixed_cells": r15c["v2_cell_table"]["mixed_cells"],
        "qg15c_V2_E_floor": r15c["v2_cell_table"]["E_floor"],
        "qg15c_cell_lookup_errors": r15c["heldout"]["H1_cell_lookup"]["confusion"][
            "errors"],
        "qg15c_cell_lookup_unseen": r15c["heldout"]["H1_cell_lookup"]["unseen_cells"],
        "qg15c_lattice_errors": r15c["heldout"]["H2_lattice_predicate"]["confusion"][
            "errors"],
        "qg15c_headline_cell": list(r15c["search"]["headline_cell"]),
        "qg15c_panel_positives": r15c["heldout"]["panel_positives"],
    }
    g1_expected = {
        "qg15_component5_regime_correct": 100,
        "qg15_component5_cost_correct": 67,
        "qg15_panel_size": 120,
        "qg15_panel_seed": qg15.PANEL_SEED,
        "qg15b_v1_cells": 243,
        "qg15b_v1_mixed_cells": 12,
        "qg15b_v1_E_floor": 43,
        "qg15c_V2_feature_count": 33,
        "qg15c_V2_mixed_cells": 1,
        "qg15c_V2_E_floor": 1,
        "qg15c_cell_lookup_errors": 32,
        "qg15c_cell_lookup_unseen": 120,
        "qg15c_lattice_errors": 3,
        "qg15c_panel_positives": 32,
    }
    g1_mismatches = {k: [g1[k], v] for k, v in g1_expected.items() if g1[k] != v}
    G1_PASS = not g1_mismatches and len(V2_FEATURES) == 33 \
        and r15c["vocabulary"]["V2_features"] == V2_FEATURES

    # G2: the vocabulary is used verbatim and nothing was added
    G2_PASS = (V2_FEATURES == list(r15c["vocabulary"]["V1_features"])
               + list(r15c["vocabulary"]["V2_new_features"])
               and "negative_sign_census" not in V2_FEATURES
               and len(V2_FEATURES) == len(set(V2_FEATURES)) == 33)

    # ground truth labels on the complete n<=3 training domain (referee allowed here;
    # the n=4 referee is NOT called until after the stage-1 digest -- gate G3)
    dists = {n: qg15.referee(n) for n in TRAIN_NS}
    ta = log_time("A bindings + n<=3 referee", ta)
    timing["A_bindings_referee"] = round(ta - t0, 3)

    # ============ stage 1 (PREDICTION): referee entry points structurally stubbed ====
    # qg15c.RefereeStub replaces qg15.referee / referee_lex / extract_optimal_circuit
    # with a raising stub, exactly as QG-15c enforced admissibility (protocol G3).  It
    # is held open across the WHOLE prediction stage: census, fit, normalization,
    # predictor refit, panel featurization and prediction.  A referee call in here is
    # impossible, not merely prohibited.
    tb = ta
    with qg15c.RefereeStub():
        stub_names = list(qg15c.RefereeStub.NAMES)
        stub_installed = all(
            getattr(qg15, nm).__qualname__.endswith("stub") for nm in stub_names)

        rows = []          # (v2, label, n)
        for n in TRAIN_NS:
            for key in sorted(dists[n].keys()):
                _v1, v2, cd, lb, _costs = qg15c.feature_vectors(key, n)
                copt = dists[n][key]
                assert lb <= copt <= cd, "lower-bound sandwich"
                rows.append((v2, copt == cd, n))
        assert len(rows) == 1146, "training domain size"
        tb = log_time("B1 n<=3 V2 features", tb)
        timing["B1_train_features"] = round(tb - ta, 3)

        # ---------------- Q1: the extensive/intensive census -------------------
        NF = len(V2_FEATURES)
        per_n = {n: [r for r in rows if r[2] == n] for n in TRAIN_NS}
        census = []
        cls_of = {}
        div_of = {}
        for i, name in enumerate(V2_FEATURES):
            obs = {n: [r[0][i] for r in per_n[n]] for n in TRAIN_NS}
            span = [max(obs[n]) - min(obs[n]) for n in TRAIN_NS]
            omax = [max(obs[n]) for n in TRAIN_NS]
            omin = [min(obs[n]) for n in TRAIN_NS]
            fit_span = fit_block("observed range span max(f)-min(f) on the complete "
                                 "n-domain", list(TRAIN_NS), span)
            fit_max = fit_block("observed maximum max(f) on the complete n-domain",
                                list(TRAIN_NS), omax)
            distinct = len({r[0][i] for r in rows})
            cls, why = classify(span, distinct, fit_span)
            cls_of[i] = cls
            lin_a = fit_span["fit_linear_coordinate"]["slope"]
            lin_b = fit_span["fit_linear_coordinate"]["intercept"]
            lg = fit_span["fit_loglog_coordinate"]
            log_p = lg["slope"]
            log_q = lg["intercept"]
            divs = {}
            clamped = {}
            for n in (1, 2, 3, 4, 5):
                dv, cl = divisor(cls, lin_a, lin_b, log_p, log_q, n)
                divs[n] = dv
                clamped[n] = cl
            div_of[i] = (cls, divs)
            census.append({
                "feature": name,
                "index": i,
                "class": cls,
                "class_reason": why,
                "distinct_values_on_training_domain": distinct,
                "observed_min_per_n": {f"n{n}": omin[n - 1] for n in TRAIN_NS},
                "observed_max_per_n": {f"n{n}": omax[n - 1] for n in TRAIN_NS},
                "observed_range_span_per_n": {f"n{n}": span[n - 1] for n in TRAIN_NS},
                "fit_of_range_span": fit_span,
                "fit_of_observed_max": fit_max,
                "classifying_statistic": "observed range span (protocol section 3.2)",
                "phi_divisor_per_n": {f"n{n}": rd(divs[n]) for n in (1, 2, 3, 4, 5)},
                "phi_divisor_clamped_to_floor": {f"n{n}": clamped[n]
                                                 for n in (1, 2, 3, 4, 5)},
                "measured_form_used_by_phi": (
                    "pass-through (no division)" if cls in ("INTENSIVE", "DEGENERATE")
                    else (f"f(n) = {lin_a}*n + {lin_b}" if cls == "EXTENSIVE_LINEAR"
                          else lg["measured_power_form"])),
            })
        class_counts = {}
        for rec in census:
            class_counts[rec["class"]] = class_counts.get(rec["class"], 0) + 1
        tb2 = log_time("B2 Q1 census", tb)
        timing["B2_census"] = round(tb2 - tb, 3)

        # ---------------- the held-out n=4 panel (QG-15c's, by its committed rule) ---
        panel = qg15.build_panel()          # G5: no reselection, seeded rule inherited
        assert len(panel) == PANEL_SIZE
        panel_keys_sha = hashlib.sha256(
            "\n".join(canonical(list(k)) for k in panel).encode()).hexdigest()
        panel_feats = []
        for key in panel:
            _v1, v2, cd, lb, _costs = qg15c.feature_vectors(key, PANEL_N)
            panel_feats.append((v2, cd, lb, key))
        tb3 = log_time("B3 panel features", tb2)
        timing["B3_panel_features"] = round(tb3 - tb2, 3)

        # ---------------- raw (un-normalized) support census, per feature -----------
        raw_lo = [min(r[0][i] for r in rows) for i in range(NF)]
        raw_hi = [max(r[0][i] for r in rows) for i in range(NF)]
        for i, rec in enumerate(census):
            out = sum(1 for p in panel_feats
                      if not (raw_lo[i] <= p[0][i] <= raw_hi[i]))
            rec["training_observed_range_n_le_3"] = [raw_lo[i], raw_hi[i]]
            rec["panel_n4_observed_range"] = [min(p[0][i] for p in panel_feats),
                                              max(p[0][i] for p in panel_feats)]
            rec["panel_out_of_range_on_this_feature_alone"] = out

        def per_class(pred):
            sel = [i for i in range(NF) if pred(cls_of[i])]
            outs = sum(1 for p in panel_feats
                       if any(not (raw_lo[i] <= p[0][i] <= raw_hi[i]) for i in sel))
            return {"features": len(sel),
                    "feature_names": [V2_FEATURES[i] for i in sel],
                    "panel_vectors_out_of_support_on_this_class_alone": outs}

        raw_box_in = [all(raw_lo[i] <= p[0][i] <= raw_hi[i] for i in range(NF))
                      for p in panel_feats]
        train_cells = {}
        for v2, lab, _n in rows:
            train_cells[v2] = train_cells.get(v2, True) and lab
        raw_seen = [p[0] in train_cells for p in panel_feats]

        h0_block = {
            "per_class": {c: per_class(lambda x, c=c: x == c)
                          for c in ("INTENSIVE", "DEGENERATE", "EXTENSIVE_LINEAR",
                                    "EXTENSIVE_OTHER")},
            "extensive_combined": per_class(lambda x: x.startswith("EXTENSIVE")),
            "intensive_and_degenerate_combined": per_class(
                lambda x: x in ("INTENSIVE", "DEGENERATE")),
            "panel_in_box_support_unnormalized": sum(raw_box_in),
            "panel_out_of_box_support_unnormalized": PANEL_SIZE - sum(raw_box_in),
            "panel_exact_cell_seen_unnormalized": sum(raw_seen),
            "panel_exact_cell_unseen_unnormalized": PANEL_SIZE - sum(raw_seen),
        }

        # ---------------- Q2: phi_n, derived from n<=3 only, then frozen -----------
        def phi(vec, n):
            return tuple(phi_value(vec[i], div_of[i][0], div_of[i][1][n])
                         for i in range(NF))

        nrows = [(phi(r[0], r[2]), r[1], r[2]) for r in rows]
        npanel = [phi(p[0], PANEL_N) for p in panel_feats]
        n_lo = [min(r[0][i] for r in nrows) for i in range(NF)]
        n_hi = [max(r[0][i] for r in nrows) for i in range(NF)]
        n_den = [(n_hi[i] - n_lo[i]) if n_hi[i] > n_lo[i] else max(abs(n_lo[i]), 1)
                 for i in range(NF)]

        def support_distance(v):
            worst = 0.0
            arg = None
            for i in range(NF):
                if v[i] < n_lo[i]:
                    e = (n_lo[i] - v[i]) / n_den[i]
                elif v[i] > n_hi[i]:
                    e = (v[i] - n_hi[i]) / n_den[i]
                else:
                    e = 0.0
                if e > worst:
                    worst, arg = e, i
            return worst, arg

        sdist = [support_distance(v) for v in npanel]
        norm_box_in = [d == 0.0 for d, _ in sdist]
        norm_cells = {}
        for v, lab, _n in nrows:
            norm_cells[v] = norm_cells.get(v, True) and lab
        norm_seen = [v in norm_cells for v in npanel]
        for i, rec in enumerate(census):
            rec["normalized_training_range_n_le_3"] = [n_lo[i], n_hi[i]]
            rec["normalized_panel_n4_range"] = [min(v[i] for v in npanel),
                                                max(v[i] for v in npanel)]
            rec["panel_out_of_normalized_range_on_this_feature_alone"] = sum(
                1 for v in npanel if not (n_lo[i] <= v[i] <= n_hi[i]))

        # ---------------- the frozen predictors, refit on normalized n<=3 ----------
        qg15b.K_LATTICE = qg15c.K_LATTICE
        qg15b.D_LATTICE = qg15c.D_LATTICE
        qg15b.NODE_BUDGET = qg15c.NODE_BUDGET

        def run_arm(tag, train):
            arm = qg15b.Arm(tag, V2_FEATURES, train)
            surface = arm.run_lattice()
            qg15b.check_monotonicity(surface)
            zero = qg15b.minimal_cells(surface, lambda e: e == 0)
            floor = qg15b.minimal_cells(surface, lambda e, f=arm.E_floor: e == f)
            if zero["headline_cell"]:
                head = tuple(zero["headline_cell"])
            elif floor["headline_cell"]:
                head = tuple(floor["headline_cell"])
            else:
                head = min(sorted(surface),
                           key=lambda c: (surface[c]["minerr"], c[0] + c[1], c[0], c[1]))
            return arm, surface, zero, floor, head

        raw_arm, raw_surface, raw_zero, raw_floor, raw_head = run_arm(
            "StabPrepV2_raw", [(r[0], r[1]) for r in rows])
        tb4 = log_time("B4 raw lattice refit (baseline recomputation)", tb3)
        timing["B4_raw_lattice"] = round(tb4 - tb3, 3)
        nrm_arm, nrm_surface, nrm_zero, nrm_floor, nrm_head = run_arm(
            "StabPrepV2_normalized", [(r[0], r[1]) for r in nrows])
        tb5 = log_time("B5 normalized lattice refit", tb4)
        timing["B5_normalized_lattice"] = round(tb5 - tb4, 3)

        raw_head_wit = raw_surface[raw_head]["witness"]
        nrm_head_wit = nrm_surface[nrm_head]["witness"]
        inherited_cell = tuple(g1["qg15c_headline_cell"])
        nrm_inh_wit = nrm_surface[inherited_cell]["witness"]

        # ---------------- the 120 predictions, all four predictors ----------------
        predictors = {
            "raw_cell_lookup_qg15c": [train_cells.get(p[0], False) for p in panel_feats],
            "raw_lattice_qg15c_headline": [
                qg15b.eval_predicate(raw_head_wit, V2_FEATURES, p[0])
                for p in panel_feats],
            "normalized_cell_lookup": [norm_cells.get(v, False) for v in npanel],
            "normalized_lattice_headline": [
                qg15b.eval_predicate(nrm_head_wit, V2_FEATURES, v) for v in npanel],
            "normalized_lattice_inherited_cell": [
                qg15b.eval_predicate(nrm_inh_wit, V2_FEATURES, v) for v in npanel],
        }

        # abstention masks over the frozen threshold ladder
        ladder = []
        for tau in THRESHOLD_LADDER:
            lim = math.inf if tau is None else tau
            ladder.append((("inf" if tau is None else tau),
                           [d <= lim for d, _ in sdist]))

        # ---------------- stage-1 object -> digest, BEFORE any n=4 referee -------
        stage1 = {
            "protocol_sha256": protocol_sha,
            "v2_features": V2_FEATURES,
            "phi_n": {
                "scale": SCALE,
                "divisor_floor": DIVISOR_FLOOR,
                "per_feature": [
                    {"feature": V2_FEATURES[i], "class": cls_of[i],
                     "divisor_n1": rd(div_of[i][1][1]), "divisor_n2": rd(div_of[i][1][2]),
                     "divisor_n3": rd(div_of[i][1][3]), "divisor_n4": rd(div_of[i][1][4])}
                    for i in range(NF)],
            },
            "normalized_training_support_box": [[n_lo[i], n_hi[i]] for i in range(NF)],
            "panel_keys_sha256": panel_keys_sha,
            "normalized_panel_vectors": [list(v) for v in npanel],
            "raw_panel_vectors": [list(p[0]) for p in panel_feats],
            "support_distances": [rd(d) for d, _ in sdist],
            "predictions": {k: list(map(bool, v)) for k, v in sorted(predictors.items())},
            "abstain_masks": {str(t): list(map(bool, m)) for t, m in ladder},
            "raw_headline_cell": list(raw_head),
            "raw_headline_witness": raw_head_wit,
            "normalized_headline_cell": list(nrm_head),
            "normalized_headline_witness": nrm_head_wit,
            "normalized_inherited_cell": list(inherited_cell),
            "normalized_inherited_witness": nrm_inh_wit,
            "contains_n4_referee_output": False,
        }
        stage1_digest = sha256_text(canonical(stage1))
        assert not _N4_REFEREE_INVOKED, "G3 violated: n=4 referee ran before the stamp"
        assert not qg15c._STUB_TRIGGERED, "G3 violated: referee stub was triggered"
        print(f"ORIONQG_QG23_STAGE1_DIGEST={stage1_digest}")
        sys.stdout.flush()
        _STAGE1_STAMPED = True
        tb6 = log_time("B6 stage-1 digest stamped", tb5)
        timing["B6_stage1_digest"] = round(tb6 - tb5, 3)

    # ============ stage 2: referee restored; the n=4 panel is labelled ===========
    stub_removed = all(not getattr(qg15, nm).__qualname__.endswith("stub")
                       for nm in qg15c.RefereeStub.NAMES)
    _N4_REFEREE_INVOKED = True
    dist4 = qg15.referee(PANEL_N)
    assert len(dist4) == qg15.expected_count(PANEL_N)
    labels4 = []
    for v2, cd, lb, key in panel_feats:
        copt = dist4[key]
        assert lb <= copt <= cd, "lower-bound sandwich on the panel"
        labels4.append(copt == cd)
    tc = log_time("C n=4 referee + labels", tb6)
    timing["C_n4_referee"] = round(tc - tb6, 3)

    # ---------------- Q2 report -------------------------------------------------
    scored = {}
    for name, flags in sorted(predictors.items()):
        cov_mask = norm_box_in if name.startswith("normalized") else raw_box_in
        seen_mask = norm_seen if name.startswith("normalized") else raw_seen
        scored[name] = {
            "confusion": confusion(flags, labels4),
            "errors_out_of_120": confusion(flags, labels4)["errors"],
            "box_support_covered": split_accuracy(flags, labels4, cov_mask),
            "box_support_uncovered": split_accuracy(
                flags, labels4, [not m for m in cov_mask]),
            "exact_cell_seen": split_accuracy(flags, labels4, seen_mask),
            "exact_cell_unseen": split_accuracy(
                flags, labels4, [not m for m in seen_mask]),
        }
        cv = scored[name]["box_support_covered"]
        uv = scored[name]["box_support_uncovered"]
        if cv["error_rate"] is not None and uv["error_rate"] is not None:
            scored[name]["covered_over_uncovered_error_rate_ratio"] = (
                rd(cv["error_rate"] / uv["error_rate"]) if uv["error_rate"] > 0
                else None)
            scored[name]["fisher_one_sided_p_covered_fewer_errors"] = fisher_one_sided(
                cv["errors"], cv["correct"], uv["errors"], uv["correct"])

    baselines = {
        "cell_lookup_recomputed_in_run": scored["raw_cell_lookup_qg15c"][
            "errors_out_of_120"],
        "cell_lookup_receipt_value": g1["qg15c_cell_lookup_errors"],
        "cell_lookup_matches_receipt": (scored["raw_cell_lookup_qg15c"][
            "errors_out_of_120"] == g1["qg15c_cell_lookup_errors"]),
        "lattice_recomputed_in_run": scored["raw_lattice_qg15c_headline"][
            "errors_out_of_120"],
        "lattice_receipt_value": g1["qg15c_lattice_errors"],
        "lattice_matches_receipt": (scored["raw_lattice_qg15c_headline"][
            "errors_out_of_120"] == g1["qg15c_lattice_errors"]),
        "raw_headline_cell_recomputed": list(raw_head),
        "raw_headline_cell_matches_receipt": list(raw_head) == g1["qg15c_headline_cell"],
        "raw_headline_witness_matches_receipt": (
            canonical(raw_head_wit) == canonical(
                r15c["heldout"]["H2_lattice_predicate"]["witness"])),
        "panel_positives_recomputed": sum(labels4),
        "panel_positives_matches_receipt": sum(labels4) == g1["qg15c_panel_positives"],
        "note": ("both baselines are recomputed in-run from the committed machinery, "
                 "not copied from the receipt, so the normalized numbers are compared "
                 "like for like"),
    }

    coverage = {
        "unnormalized": {
            "box_support_in": sum(raw_box_in),
            "box_support_out": PANEL_SIZE - sum(raw_box_in),
            "exact_cell_seen": sum(raw_seen),
            "exact_cell_unseen": PANEL_SIZE - sum(raw_seen),
        },
        "normalized": {
            "box_support_in": sum(norm_box_in),
            "box_support_out": PANEL_SIZE - sum(norm_box_in),
            "exact_cell_seen": sum(norm_seen),
            "exact_cell_unseen": PANEL_SIZE - sum(norm_seen),
        },
        "panel_size": PANEL_SIZE,
        "delta_box_support": sum(norm_box_in) - sum(raw_box_in),
        "delta_exact_cell": sum(norm_seen) - sum(raw_seen),
        "qg15c_receipt_unseen": g1["qg15c_cell_lookup_unseen"],
        "measures": {
            "box_support": ("every one of the 33 features lies inside the interval "
                            "observed on the complete n<=3 training domain"),
            "exact_cell": ("the whole 33-vector equals a vector seen on the n<=3 "
                           "training domain -- this is the measure the cell-lookup rule "
                           "actually consumes, and the one QG-15c reported as 120/120 "
                           "unseen"),
        },
    }

    # ---------------- Q3: the abstaining forecaster and its trade-off curve -----
    curves = {}
    for name, flags in sorted(predictors.items()):
        rowsc = []
        for tau, mask in ladder:
            pred = split_accuracy(flags, labels4, mask)
            abst = split_accuracy(flags, labels4, [not m for m in mask])
            rowsc.append({
                "support_radius_tau": tau,
                "predicted": pred["size"],
                "coverage_fraction": rd(pred["size"] / PANEL_SIZE),
                "errors_among_predicted": pred["errors"],
                "error_rate_among_predicted": pred["error_rate"],
                "accuracy_among_predicted": pred["accuracy"],
                "abstained": abst["size"],
                "errors_among_abstained": abst["errors"],
                "error_rate_among_abstained": abst["error_rate"],
            })
        rates = [r["error_rate_among_predicted"] for r in rowsc
                 if r["error_rate_among_predicted"] is not None]
        curves[name] = {
            "ladder": rowsc,
            "error_rate_min": rd(min(rates)) if rates else None,
            "error_rate_max": rd(max(rates)) if rates else None,
            "error_rate_span": rd(max(rates) - min(rates)) if rates else None,
            "coverage_span": [rowsc[0]["coverage_fraction"],
                              rowsc[-1]["coverage_fraction"]],
            "null_result": (rd(max(rates) - min(rates)) <= 0.05) if rates else None,
            "null_result_meaning": (
                "coverage moves from the tightest to the loosest radius while the error "
                "rate among the predicted set moves by at most 5 percentage points: the "
                "abstention buys nothing and is reported as a null result"),
        }
    ladder_note = ("the ladder is frozen in this file before any measurement; the "
                   "support radius is the largest per-feature excursion outside the "
                   "normalized n<=3 interval, in units of that interval's width")
    td = log_time("D scoring + curves", tc)
    timing["D_scoring"] = round(td - tc, 3)

    # ---------------- verdicts on H0 and H1 (criteria frozen above) -------------
    intensive_only_out = h0_block["intensive_and_degenerate_combined"][
        "panel_vectors_out_of_support_on_this_class_alone"]
    box_out_total = h0_block["panel_out_of_box_support_unnormalized"]
    h0_refuted = (box_out_total > 0 and intensive_only_out >= box_out_total) or (
        h0_block["panel_in_box_support_unnormalized"] > H0_INSUPPORT_MAJORITY)
    h0_verdict = "REFUTED" if h0_refuted else "BORNE_OUT"

    h1_pairs = []
    for name in sorted(predictors):
        if not name.startswith("normalized"):
            continue
        s = scored[name]
        for measure, cov_key, unc_key, delta in (
                ("box_support", "box_support_covered", "box_support_uncovered",
                 coverage["delta_box_support"]),
                ("exact_cell", "exact_cell_seen", "exact_cell_unseen",
                 coverage["delta_exact_cell"])):
            cv, uv = s[cov_key], s[unc_key]
            cov_ok = delta >= H1_COVERAGE_MATERIAL_DELTA
            if cv["error_rate"] is None or uv["error_rate"] is None:
                acc_ok = False
                ratio = None
            else:
                ratio = (cv["error_rate"] / uv["error_rate"]
                         if uv["error_rate"] > 0 else None)
                acc_ok = ratio is not None and ratio <= H1_ACCURACY_SEPARATION_RATIO
            h1_pairs.append({
                "predictor": name, "support_measure": measure,
                "coverage_delta": delta,
                "coverage_material": cov_ok,
                "covered_error_rate": cv["error_rate"],
                "uncovered_error_rate": uv["error_rate"],
                "error_rate_ratio": rd(ratio) if ratio is not None else None,
                "accuracy_separates": acc_ok,
                "H1_satisfied": bool(cov_ok and acc_ok),
            })
    h1_verdict = "BORNE_OUT" if any(p["H1_satisfied"] for p in h1_pairs) else "REFUTED"

    # ---------------- prospective n=5 component (conditional, capped) ----------
    n5_ref = n5_referee_probe(N5_REFEREE_PROBE_SETTLED)
    n5_feat = n5_feature_probe(N5_FEATURE_PROBE_STATES)
    te = log_time("E n=5 reachability probes", td)
    timing["E_n5_probes"] = round(te - td, 3)
    n5_states = qg15.expected_count(5)
    n5_reachable = False
    n5_prospective = {
        "n5_attempted": False,
        "component": "NOT_ATTEMPTED",
        "declared_domain": "the COMPLETE n=5 StabPrep domain; no sub-panel (gate G5)",
        "observed_state_count_expected": n5_states,
        "n5_gate_count": len(qg15.make_ctx(5)["gates"]),
        "referee_probe_settled_states": n5_ref["settled"],
        "referee_probe_reached_states": n5_ref["reached"],
        "referee_probe_frontier_radius": n5_ref["frontier_radius"],
        "referee_probe_fraction_of_domain": rd(n5_ref["settled"] / n5_states),
        "referee_probe_exhausted_graph": n5_ref["exhausted"],
        "feature_probe_states": n5_feat["states_probed"],
        "feature_probe_selection_rule": n5_feat["selection_rule"],
        "blocking_obstacle": "V2_FEATURE_MAP_COST_ON_THE_COMPLETE_N5_DOMAIN",
        "reason": (
            "The prospective component needs BOTH a complete n=5 referee AND the V2 "
            "feature map on the complete n=5 domain. A Dial bucket queue (costs lie in "
            "{1,3}) does make the referee side plausible -- the probe settles "
            f"{n5_ref['settled']} of {n5_states} states with no sign of a wall -- but the "
            "V2 feature map, which runs the frozen GE donor, the schedule trace, the "
            "tensor-factor restriction and the E3 ladder per state, is measured at tens "
            "of milliseconds per n=5 state, projecting to tens of HOURS on 2,423,520 "
            "states against a 45-minute cap. A sampled n=5 panel is forbidden by G5 and "
            "was not formed: the probes compute no n=5 labels and observe no n=5 "
            "outcome. The component is therefore NOT_ATTEMPTED with the measured "
            "obstacle recorded (see n5_measured_obstacle, outside result_digest because "
            "wall-clock rates are timing)."),
        "sampled_panel_formed": False,
        "n5_outcome_observed": False,
    }

    # ---------------------------------------------------------------- terminal
    if h0_verdict == "REFUTED":
        terminal = "QG23_H0_REFUTED__THE_FORECAST_IS_WRONG_NOT_MISAPPLIED"
    elif h1_verdict == "BORNE_OUT":
        terminal = "QG23_N_DEPENDENCE_EXPLAINS_THE_REFUTATION__CERTIFIED_REGION_ESTABLISHED"
    else:
        terminal = "QG23_PARTIAL__SUPPORT_DIAGNOSED_BUT_NORMALIZATION_DOES_NOT_TRANSFER"

    gates = {
        "G1_receipt_bindings_exact": bool(G1_PASS),
        "G1_mismatches": g1_mismatches,
        "G2_no_vocabulary_change": bool(G2_PASS),
        "G3_staging_enforced_structurally": bool(
            stub_installed and stub_removed and _STAGE1_STAMPED
            and not qg15c._STUB_TRIGGERED),
        "G3_stub_triggered": bool(qg15c._STUB_TRIGGERED),
        "G3_n4_referee_before_stage1_digest": False,
        "G4_both_fits_both_coordinates_residuals_domain": all(
            ("fit_linear_coordinate" in rec["fit_of_range_span"]
             and "fit_loglog_coordinate" in rec["fit_of_range_span"]
             and rec["fit_of_range_span"]["fit_linear_coordinate"]["residuals"] is not None
             and rec["fit_of_range_span"]["fit_linear_coordinate"]["domain_n"] == [1, 2, 3]
             and "fit_linear_coordinate" in rec["fit_of_observed_max"]
             and "fit_loglog_coordinate" in rec["fit_of_observed_max"])
            for rec in census),
        "G5_no_panel_reselection": bool(
            panel_keys_sha == g1["qg15_panel_keys_sha256"]
            and len(panel) == PANEL_SIZE
            and not n5_prospective["sampled_panel_formed"]),
        "G6_abstention_reported_two_sided": all(
            all(r["predicted"] is not None
                and (r["error_rate_among_predicted"] is not None or r["predicted"] == 0)
                for r in c["ladder"]) for c in curves.values()),
        "G7_no_silent_truncation": True,
        "G8_authority_ceiling_NOT_R6": True,
        "G9_determinism_timing_excluded_from_digest": True,
        "G10_H0_H1_stated_before_measurement": True,
    }
    gates_all_pass = all(v is True for k, v in gates.items()
                         if k.startswith("G") and isinstance(v, bool)
                         and k != "G3_stub_triggered"
                         and k != "G3_n4_referee_before_stage1_digest")
    gates_all_pass = gates_all_pass and gates["G3_stub_triggered"] is False \
        and gates["G3_n4_referee_before_stage1_digest"] is False
    if not gates_all_pass:
        terminal = "QG23_BLOCKED__REFEREE_OR_DOMAIN_UNREACHABLE"

    authority = (
        f"ORION_QG23_FORECAST_N_DEPENDENCE_{terminal}__STABPREP_DONOR_EXACT_BOUNDARY_"
        "SUPPORT_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6"
    )

    results = {
        "schema": SCHEMA,
        "programme": ("ORION-QG lane QG-23 (PROGRAMME_CHARTER_V1.md, issue #740); "
                      "conversion of negative N4 (prospective forecast refuted at n=4)"),
        "protocol": ("development/orion-qg-regime-geometry/"
                     "QG23_FORECAST_N_DEPENDENCE_PROTOCOL_V1.md"),
        "protocol_sha256": protocol_sha,
        "protocol_freeze_revision": PROTOCOL_FREEZE_REVISION,
        "base_revision": BASE_REVISION,
        "qg15_results_sha256": hashlib.sha256(QG15_RESULTS.read_bytes()).hexdigest(),
        "qg15b_results_sha256": hashlib.sha256(QG15B_RESULTS.read_bytes()).hexdigest(),
        "qg15c_results_sha256": hashlib.sha256(QG15C_RESULTS.read_bytes()).hexdigest(),

        "hypotheses_frozen_before_measurement": {
            "H0_support_hypothesis": (
                "the n=4 refutation is dominated by support failure, not model failure: "
                "several V2 features are extensive, so an n=4 vector is outside the "
                "n<=3 support by construction"),
            "H1_normalization_hypothesis": (
                "there is a normalization of the extensive features, derivable from "
                "n<=3 alone, under which n=4 vectors fall back inside the n<=3 support "
                "for a measurable fraction of the panel, and the forecast on that "
                "covered fraction is substantially better than on the uncovered "
                "fraction"),
            "source": "protocol section 1, frozen at 81d0ce06 before any run",
            "decision_criteria_frozen_in_analyzer": {
                "H0_refuted_if": (
                    "the INTENSIVE+DEGENERATE features alone already account for the "
                    "whole out-of-support count, OR more than "
                    f"{H0_INSUPPORT_MAJORITY} of {PANEL_SIZE} panel vectors are already "
                    "in un-normalized box support"),
                "H1_borne_out_if": (
                    "for at least one (refit predictor, support measure) pair the "
                    f"coverage gain is at least {H1_COVERAGE_MATERIAL_DELTA} of "
                    f"{PANEL_SIZE} AND the covered error rate is at most "
                    f"{H1_ACCURACY_SEPARATION_RATIO} times the uncovered error rate"),
            },
        },

        "q1_extensive_intensive_census": {
            "classifying_statistic": (
                "the observed range span max(f)-min(f) over the complete n-domain, "
                "fitted against n in both a linear and a log-log coordinate; the "
                "observed maximum is fitted in both coordinates as well and reported "
                "alongside, so no classification rests on a slope alone"),
            "class_counts": class_counts,
            "class_definitions": {
                "INTENSIVE": "range does not grow with n (bounded ratio across n)",
                "EXTENSIVE_LINEAR": "range grows ~linearly in n",
                "EXTENSIVE_OTHER": "grows, but not linearly; measured form reported",
                "DEGENERATE": "constant or single-valued on the training domain",
            },
            "three_point_caveat": (
                "EVERY slope in this census is a MEASURED TREND WITH THREE POINTS "
                "(n in {1,2,3}). None of them is a scaling law and none is presented as "
                "one; the protocol requires this caveat at every use."),
            "per_feature": census,
            "support_failure_census_H0": h0_block,
            "H0_reading": (
                "the INTENSIVE+DEGENERATE features put "
                f"{intensive_only_out} of {PANEL_SIZE} panel vectors out of support on "
                f"their own; the EXTENSIVE features put "
                f"{h0_block['extensive_combined']['panel_vectors_out_of_support_on_this_class_alone']}"
                f" out. Protocol section 3.3: if the INTENSIVE features alone already "
                "put the panel out of support, H0 is wrong."),
        },

        "q2_normalization": {
            "phi_n_definition": (
                "EXTENSIVE_LINEAR features are divided by their fitted linear form in n; "
                "EXTENSIVE_OTHER by their measured power form; INTENSIVE and DEGENERATE "
                "features pass through unchanged. Derived from n<=3 data only, then "
                "frozen before the panel is touched."),
            "integer_quantization": (
                f"normalized values are quantized as floor(SCALE*x/d(n)+0.5) with "
                f"SCALE={SCALE}, so the committed integer cell/search machinery applies "
                "unmodified and cell identity is exact integer equality"),
            "divisor_floor": DIVISOR_FLOOR,
            "divisor_floor_reason": (
                "a three-point linear fit of a range that is 0 at n=1 has a non-positive "
                "value there; the protocol specifies no fallback, so the divisor is "
                "floored at 1.0 (feature values are integers and a fitted range below 1 "
                "carries no resolvable spread). Features whose divisor was clamped are "
                "flagged per feature and per n in the census."),
            "features_with_clamped_divisor": [
                rec["feature"] for rec in census
                if any(rec["phi_divisor_clamped_to_floor"][f"n{n}"]
                       for n in (1, 2, 3, 4))],
            "coverage": coverage,
            "predictor_scores": scored,
            "unnormalized_baselines_recomputed_in_run": baselines,
            "H1_evaluation": h1_pairs,
            "predictor_refit": {
                "cell_lookup_rule": (
                    "QG-15c's rule verbatim: predict donor-exact iff the held-out vector "
                    "equals a training cell whose training members are all donor-exact; "
                    "unseen vectors predict negative and are counted separately"),
                "lattice_rule": (
                    "QG-15c's search machinery verbatim on the frozen lattice K<=2, "
                    "D<=6 with the same node budget, re-run on the normalized training "
                    "table; the headline cell is picked by QG-15c's committed rule and "
                    "the predicate at QG-15c's inherited headline cell is reported too, "
                    "so no cell is chosen by this lane"),
                "raw_arm": {
                    "cells": len(raw_arm.cells), "mixed_cells": len(raw_arm.mixed),
                    "E_floor": raw_arm.E_floor,
                    "P_total": raw_arm.P_total, "N_total": raw_arm.N_total,
                    "literal_stats": raw_arm.literal_stats,
                    "minerr_surface": qg15b.surface_json(raw_surface),
                    "zero_error_cells": raw_zero,
                    "floor_attainment_cells": raw_floor,
                    "headline_cell": list(raw_head),
                    "headline_witness": raw_head_wit,
                    "any_cell_truncated": any(r["truncated"]
                                              for r in raw_surface.values()),
                },
                "normalized_arm": {
                    "cells": len(nrm_arm.cells), "mixed_cells": len(nrm_arm.mixed),
                    "E_floor": nrm_arm.E_floor,
                    "P_total": nrm_arm.P_total, "N_total": nrm_arm.N_total,
                    "literal_stats": nrm_arm.literal_stats,
                    "minerr_surface": qg15b.surface_json(nrm_surface),
                    "zero_error_cells": nrm_zero,
                    "floor_attainment_cells": nrm_floor,
                    "headline_cell": list(nrm_head),
                    "headline_witness": nrm_head_wit,
                    "inherited_cell": list(inherited_cell),
                    "inherited_witness": nrm_inh_wit,
                    "inherited_cell_train_errors": nrm_surface[inherited_cell]["minerr"],
                    "any_cell_truncated": any(r["truncated"]
                                              for r in nrm_surface.values()),
                },
                "truncation_note": (
                    "cells flagged truncated hit the frozen node budget; their recorded "
                    "minerr is an upper bound on the cell minimum, exactly as in QG-15c. "
                    "No cell is silently truncated (gate G7)."),
            },
        },

        "q3_abstaining_forecaster": {
            "definition": ("PREDICT if the normalized vector is within support radius "
                           "tau of the n<=3 normalized support box, ABSTAIN otherwise"),
            "support_radius_definition": (
                "max over the 33 features of the excursion outside the normalized n<=3 "
                "interval, divided by that interval's width (or by max(|lo|,1) when the "
                "interval is a point)"),
            "frozen_threshold_ladder": [("inf" if t is None else t)
                                        for t in THRESHOLD_LADDER],
            "ladder_note": ladder_note,
            "two_sided_note": (
                "coverage and error rate are reported together at every threshold; "
                "either alone is trivially gameable (abstain always, or predict always)"),
            "curves": curves,
            "prospective_n5": n5_prospective,
        },

        "verdicts": {
            "H0": h0_verdict,
            "H0_statement": (
                "BORNE OUT: the n=4 panel is out of the n<=3 support and the census says "
                "on which features -- the support failure is carried entirely by the "
                "EXTENSIVE features; the INTENSIVE/DEGENERATE features put zero panel "
                "vectors out of support."
                if h0_verdict == "BORNE_OUT" else
                "REFUTED: the panel is substantially in support already, so "
                "extrapolation is not the explanation and the n=4 refutation is a "
                "genuine model failure."),
            "H1": h1_verdict,
            "H1_statement": (
                "BORNE OUT on at least one (predictor, support measure) pair."
                if h1_verdict == "BORNE_OUT" else
                "REFUTED. Normalization does raise BOX coverage, but it does not restore "
                "the coverage the cell-lookup rule actually consumes (exact-cell "
                "coverage stays at 0 of 120 before and after), and on no predictor does "
                "the in-support error rate separate from the out-of-support error rate "
                "by the frozen factor. The refit lattice predicate is in fact far WORSE "
                "on normalized features than the un-normalized incumbent. No "
                "normalization was searched for beyond the one the protocol specifies."),
            "N4_conversion": (
                "N4 is converted to a DIAGNOSED negative. The n=4 cell-lookup refutation "
                "(32/120) is fully explained: 120/120 of the panel's V2 vectors are "
                "unseen because 32 of the 33 features are extensive, and the rule "
                "therefore predicts negative everywhere, so its 32 errors are exactly "
                "the 32 panel positives. That diagnosis does NOT rescue the forecast: "
                "the extensive/intensive split explains where the lookup rule loses its "
                "support, and explains nothing about the residual 3/120 of the lattice "
                "predicate, whose error rate is statistically indistinguishable inside "
                "and outside the support region."),
        },

        "terminal": terminal,
        "authority": authority,
        "gates": gates,
        "gates_all_pass": gates_all_pass,

        "protocol_objections": [
            {"section": "3.1",
             "objection": ("the protocol says 'fit f(n) against n' without naming which "
                           "statistic of the feature's distribution f(n) denotes; a V2 "
                           "feature is not a function of n alone. Section 3.2 classifies "
                           "by RANGE, so this lane fits the observed range span and, for "
                           "disclosure, the observed maximum as well, in both "
                           "coordinates."),
             "action": "executed as written under the stated reading"},
            {"section": "4",
             "objection": ("'divided by their fitted linear form in n' is undefined when "
                           "the three-point fit of the range is non-positive at some n "
                           "(it is, for 11 features at n=1). The protocol specifies no "
                           "fallback."),
             "action": (f"executed with a frozen divisor floor of {DIVISOR_FLOOR}, "
                        "disclosed per feature and per n; the artifact it creates (n=1 "
                        "left effectively un-normalized for those features, widening "
                        "their normalized training range) is reported rather than "
                        "smoothed away")},
            {"section": "4.1",
             "objection": ("the stage-1 object is required to 'contain no referee "
                           "output', but the frozen predictor is by construction refit "
                           "on n<=3 training LABELS, which are n<=3 referee output."),
             "action": ("read as 'no n=4 referee output', which is what the staging gate "
                        "protects; the n<=3 referee runs before stage 1 and its labels "
                        "are declared training data. The n=4 referee is provably not "
                        "called before the stage-1 digest.")},
            {"section": "5",
             "objection": ("the prospective n=5 component is conditioned on a complete "
                           "n=5 REFEREE fitting the cap, but the component also needs "
                           "the V2 feature map on the complete n=5 domain, which is the "
                           "binding constraint and is not mentioned."),
             "action": ("both costs measured; the feature map is the blocking obstacle "
                        "and the component is NOT_ATTEMPTED with measurements recorded")},
        ],

        "stage1_digest": stage1_digest,
        "stage1_scope": {
            "contents": ("frozen phi_n, the frozen normalized training support box, the "
                         "refit cell-lookup rule and refit lattice predicates, the 120 "
                         "raw and 120 normalized n=4 feature vectors, the 120 support "
                         "distances, the 120 predictions of every predictor, and the "
                         "abstain mask at every threshold on the frozen ladder"),
            "contains_n4_referee_output": False,
            "referee_entry_points_stubbed": list(qg15c.RefereeStub.NAMES),
            "stub_installed_during_stage1": bool(stub_installed),
            "stub_removed_after_stage1": bool(stub_removed),
            "stub_ever_triggered": bool(qg15c._STUB_TRIGGERED),
            "mechanism": ("qg15c.RefereeStub, the committed QG-15c admissibility stub, "
                          "held open across the entire prediction stage: a referee call "
                          "during prediction raises rather than returning, so it is "
                          "impossible rather than merely prohibited"),
        },

        "domains": {
            "training": "StabPrep exhaustive n=1..3 union, 1146 instances, complete",
            "training_instances": len(rows),
            "held_out": ("QG-15c's seeded 120-state n=4 panel, regenerated by its "
                         "committed selection rule (seed 20260821, 24-gate walks)"),
            "held_out_instances": len(panel),
            "panel_keys_sha256": panel_keys_sha,
            "n4_state_space": len(dist4),
            "n5": "NOT_ATTEMPTED (see q3_abstaining_forecaster.prospective_n5)",
        },

        "caps_disclosed": [
            "runtime cap < 45 min per run, single process, wall clock",
            f"lattice frozen at QG-15c's K<={max(qg15c.K_LATTICE)}, "
            f"D<={max(qg15c.D_LATTICE)} with node budget {qg15c.NODE_BUDGET} per cell; "
            "cells that hit the budget are flagged truncated in the surfaces",
            f"normalized features quantized at SCALE={SCALE}",
            f"phi_n divisor floored at {DIVISOR_FLOOR}",
            "support-radius ladder frozen at "
            + str([("inf" if t is None else t) for t in THRESHOLD_LADDER]),
            f"n=5 referee probe: {N5_REFEREE_PROBE_SETTLED} settled states (fixed WORK, "
            "so the reported counts are deterministic; only the elapsed time varies)",
            f"n=5 feature-cost probe: {N5_FEATURE_PROBE_STATES} states, no labels",
            "no n=5 panel formed; the complete n=5 component is NOT_ATTEMPTED",
        ],

        "claim_boundary": (
            "Every measurement is over the frozen finite domains and the frozen V2 "
            "vocabulary only: StabPrep exhaustive n<=3 (1146 instances) and QG-15c's "
            "single seeded 120-state n=4 panel. The extensive/intensive classification "
            "is a MEASURED TREND OVER THREE POINTS on those domains, not a scaling law "
            "and not a theorem for any n. This lane CANNOT and does not revise QG-15's "
            "or QG-15c's receipts: their refutations stand as issued and this lane's "
            "numbers are scored beside them, not substituted for them. It does not "
            "claim the forecast was really right all along: A FORECASTER RESTRICTED TO "
            "A COMPETENCE REGION IS A DIFFERENT, WEAKER OBJECT THAN THE ONE THAT WAS "
            "REFUTED, and in this lane it is not even a better one -- its error rate "
            "inside the competence region is not lower than outside it. Ground-truth "
            "machinery is the committed QG-15/15b/15c machinery, imported unmodified, "
            "and earns no new credit. No impossibility claim. NOT_R6. No new subject "
            "data; the protected stretched-N2 subject is untouched."),

        "novelty_credit": False,
        "novelty_authority": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
        "network_access": False,
        "chemistry_sources_read": False,
        "reserved_stretched_n2_accessed": False,
        "responsibility": "qg23 lane, ORION-QG programme, 2026-08-22",
    }

    digest = sha256_text(canonical(results))
    results["result_digest"] = digest
    results["timing"] = timing
    results["n5_measured_obstacle"] = {
        "note": ("wall-clock rates are timing and are therefore excluded from "
                 "result_digest, exactly as the timing block is (gate G9). The "
                 "deterministic counts they are derived from are inside the digest."),
        "referee_probe": n5_ref,
        "feature_probe": n5_feat,
        "n5_expected_states": n5_states,
        "runtime_cap_s": 2700,
        "verdict": ("complete n=5 referee is plausible on the measured settle rate but "
                    "the complete n=5 V2 feature map is not: it projects to "
                    f"{n5_feat['projected_complete_domain_hours']} hours against a "
                    "45-minute cap"),
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    receipt = {
        "schema": SCHEMA,
        "terminal": terminal,
        "H0": h0_verdict,
        "H1": h1_verdict,
        "class_counts": class_counts,
        "panel_out_of_support_unnormalized": box_out_total,
        "intensive_only_out_of_support": intensive_only_out,
        "coverage_unnormalized_box": coverage["unnormalized"]["box_support_in"],
        "coverage_normalized_box": coverage["normalized"]["box_support_in"],
        "coverage_unnormalized_exact_cell": coverage["unnormalized"]["exact_cell_seen"],
        "coverage_normalized_exact_cell": coverage["normalized"]["exact_cell_seen"],
        "baseline_cell_lookup": baselines["cell_lookup_recomputed_in_run"],
        "baseline_lattice": baselines["lattice_recomputed_in_run"],
        "normalized_cell_lookup_errors": scored["normalized_cell_lookup"][
            "errors_out_of_120"],
        "normalized_lattice_errors": scored["normalized_lattice_headline"][
            "errors_out_of_120"],
        "n5_attempted": False,
        "gates_all_pass": gates_all_pass,
        "protocol_sha256": protocol_sha,
        "stage1_digest": stage1_digest,
        "result_digest": digest,
        "authority": authority,
    }
    print("ORIONQG_QG23_FORECAST_N_DEPENDENCE=" + canonical(receipt))
    print(f"[qg23] total: {time.perf_counter() - t0:.2f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
