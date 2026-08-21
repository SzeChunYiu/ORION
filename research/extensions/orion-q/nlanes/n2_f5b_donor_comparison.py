"""ORION-Q N2-F5B: donor comparison for the carried-forward F5 crossover residual.

Executes development/orion-q-nlane-closure/N2_F5B_DONOR_COMPARISON_PROTOCOL.md
(frozen before outcomes). The F5 residual (#675 family 5, RESIDUAL_SUPPORTED)
may not claim standing value until a Predict-and-Conquer-style model-selection
donor gets first right of refusal, and until both candidate and donor are also
compared on a misspecified world whose true forms lie in neither library.

The F5 world, grids, candidate mechanism and hostile broken-form control are
imported from n2_f5_crossover_prediction.py (never edited, never re-derived).
Exact-synthetic scope only.
"""

from __future__ import annotations

import json
import math
import os

import numpy as np

import n2_f5_crossover_prediction as f5

SEED = f5.SEED  # bookkeeping only; everything is grid-deterministic
ETA = f5.ETA
A1, A2, A3, A4 = 1.0, 25.0, 0.35, 6.0  # MIS world constants (frozen in protocol)
ES, EL, ER, ED = 1.15, 0.9, 2.1, 0.7   # MIS world exponents (frozen in protocol)
MARGIN = 0.02        # F5B-G4 comparison margin (same as F5-G2)
SUFF_TOL = 1e-9      # F5B-G3 donor-sufficiency tolerance
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(HERE, "N2_F5B_DONOR_COMPARISON_RESULTS.json")
F5_RESULTS_PATH = os.path.join(HERE, "N2_F5_CROSSOVER_PREDICTION_RESULTS.json")

TRAIN, PRIMARY, H1_FAR = f5.TRAIN, f5.PRIMARY, f5.H1_FAR


# ---------------- MIS world (true forms outside both libraries) ----------------

def cost_s_mis(L, lam, d):
    return A1 * L ** EL * (lam * d) ** ES + A2 * L ** EL


def cost_r_mis(L, lam, d):
    return A3 * (lam * d) ** ER * (1.0 + A4 / d ** ED)


def winner(cs_fn, cr_fn):
    return lambda L, lam, d: "S" if cs_fn(L, lam, d) <= cr_fn(L, lam, d) else "R"


TRUTH_ORIG = winner(f5.cost_s, lambda L, lam, d: f5.cost_r(L, lam, d))
TRUTH_H2 = winner(f5.cost_s, lambda L, lam, d: f5.cost_r(L, lam, d, broken=True))
TRUTH_MIS = winner(cost_s_mis, cost_r_mis)


# ---------------- typed argmin prediction (shared eta band) ----------------

def typed_argmin(cs_fn, cr_fn):
    def predict(L, lam, d):
        cs, cr = cs_fn(L, lam, d), cr_fn(L, lam, d)
        denom = max(abs(cs), abs(cr))
        if denom <= 0.0:
            return "UNCERTAIN"
        if abs(cs - cr) / denom < ETA:
            return "UNCERTAIN"
        return "S" if cs <= cr else "R"

    return predict


# ---------------- candidate on MIS (same frozen features, MIS observations) ----------------

def fit_candidate_generic(train, obs_s, obs_r):
    Xs = np.array([[L * lam * d, L] for L, lam, d in train])
    Xr = np.array([[(lam * d) ** 2, (lam * d) ** 2 / d] for L, lam, d in train])
    ws, *_ = np.linalg.lstsq(Xs, np.array(obs_s), rcond=None)
    wr, *_ = np.linalg.lstsq(Xr, np.array(obs_r), rcond=None)
    cs_fn = lambda L, lam, d: ws[0] * L * lam * d + ws[1] * L
    cr_fn = lambda L, lam, d: wr[0] * (lam * d) ** 2 + wr[1] * (lam * d) ** 2 / d
    return typed_argmin(cs_fn, cr_fn), cs_fn, cr_fn, {
        "ws": [float(x) for x in ws], "wr": [float(x) for x in wr]}


# ---------------- donor: Predict-and-Conquer-style model selection ----------------
# Frozen library M1..M6; frozen validation split (train index i % 4 == 3);
# select by relative RMSE on validation; refit winner on full training.

MODEL_LIBRARY = (
    ("M1_true_s_form", lambda L, lam, d: [L * lam * d, L]),
    ("M2_true_r_form", lambda L, lam, d: [(lam * d) ** 2, (lam * d) ** 2 / d]),
    ("M3_affine", lambda L, lam, d: [1.0, L, lam, d]),
    ("M4_bilinear", lambda L, lam, d: [L * lam, L * d, lam * d, L]),
    ("M5_powerlaw", None),  # log-space power law, handled specially
    ("M6_quad_mix", lambda L, lam, d: [1.0, (lam * d) ** 2, L * lam * d, L]),
)


def _fit_model(name, feats, pts, ys):
    if name == "M5_powerlaw":
        X = np.array([[1.0, math.log(L), math.log(lam), math.log(d)] for L, lam, d in pts])
        w, *_ = np.linalg.lstsq(X, np.log(np.array(ys)), rcond=None)
        fn = lambda L, lam, d: math.exp(
            w[0] + w[1] * math.log(L) + w[2] * math.log(lam) + w[3] * math.log(d))
    else:
        X = np.array([feats(*p) for p in pts])
        w, *_ = np.linalg.lstsq(X, np.array(ys), rcond=None)
        fn = lambda L, lam, d: float(np.dot(w, feats(L, lam, d)))
    return fn, [float(x) for x in w]


def fit_donor_route(train, obs):
    fit_idx = [i for i in range(len(train)) if i % 4 != 3]
    val_idx = [i for i in range(len(train)) if i % 4 == 3]
    fit_pts = [train[i] for i in fit_idx]
    fit_ys = [obs[i] for i in fit_idx]
    val_pts = [train[i] for i in val_idx]
    val_ys = [obs[i] for i in val_idx]

    selection = {}
    best_name, best_score = None, math.inf
    for name, feats in MODEL_LIBRARY:
        fn, _ = _fit_model(name, feats, fit_pts, fit_ys)
        rel = [(fn(*p) - y) / y for p, y in zip(val_pts, val_ys)]
        score = math.sqrt(sum(r * r for r in rel) / len(rel))
        finite = math.isfinite(score)
        selection[name] = {"val_rel_rmse": score if finite else None, "finite": finite}
        if finite and score < best_score:  # ties keep earlier (frozen library order)
            best_name, best_score = name, score
    feats = dict(MODEL_LIBRARY)[best_name]
    fn, w = _fit_model(best_name, feats, train, obs)  # refit on full training
    return fn, {"selected": best_name, "weights": w, "selection_scores": selection}


def fit_donor(train, obs_s, obs_r):
    cs_fn, info_s = fit_donor_route(train, obs_s)
    cr_fn, info_r = fit_donor_route(train, obs_r)
    return typed_argmin(cs_fn, cr_fn), cs_fn, cr_fn, {"route_S": info_s, "route_R": info_r}


# ---------------- informational baselines (context only in F5B) ----------------

def fit_nn(train, labels):
    feats = np.array([[math.log(L), math.log(lam), math.log(d)] for L, lam, d in train])

    def predict(L, lam, d):
        q = np.array([math.log(L), math.log(lam), math.log(d)])
        return labels[int(np.argmin(np.sum((feats - q) ** 2, axis=1)))]

    return predict


def fit_linear(train, labels):
    X = np.array([[1.0, math.log(L), math.log(lam), math.log(d)] for L, lam, d in train])
    y = np.array([1.0 if s == "S" else -1.0 for s in labels])
    w, *_ = np.linalg.lstsq(X, y, rcond=None)
    return lambda L, lam, d: "S" if (
        w[0] + w[1] * math.log(L) + w[2] * math.log(lam) + w[3] * math.log(d)) >= 0 else "R"


# ---------------- scoring (identical rule and summation order to F5) ----------------

def score_arm(predict, points, truth_fn):
    total = 0.0
    confident = confident_correct = uncertain = 0
    for L, lam, d in points:
        truth = truth_fn(L, lam, d)
        pred = predict(L, lam, d)
        if pred == "UNCERTAIN":
            total += 0.5
            uncertain += 1
        else:
            confident += 1
            if pred == truth:
                total += 1.0
                confident_correct += 1
    return {
        "score": total / len(points),
        "uncertain_rate": uncertain / len(points),
        "confident_accuracy": (confident_correct / confident) if confident else None,
        "n_points": len(points),
    }


def probe(cs_fn, cr_fn, d_true):
    d_fit = f5.bisect_crossover(cs_fn, cr_fn, 128.0, 2.0, lo=4.0, hi=4096.0)
    err = abs(d_fit - d_true) / d_true if (d_fit is not None and d_true) else None
    return {"d_fitted": d_fit, "relative_error": err}


# ---------------- pipeline ----------------

def pipeline() -> dict:
    # --- fit and FREEZE everything on training observations only ---
    # ORIG candidate: the F5 arm itself, imported (fit_orion), not reimplemented.
    cand_orig_pred, cand_orig_fit = f5.fit_orion(TRAIN)
    ws, wr = cand_orig_fit["ws"], cand_orig_fit["wr"]
    cand_orig_cs = lambda L, lam, d: ws[0] * L * lam * d + ws[1] * L
    cand_orig_cr = lambda L, lam, d: wr[0] * (lam * d) ** 2 + wr[1] * (lam * d) ** 2 / d

    obs_s_orig = [f5.cost_s(*p) for p in TRAIN]
    obs_r_orig = [f5.cost_r(*p) for p in TRAIN]
    obs_s_mis = [cost_s_mis(*p) for p in TRAIN]
    obs_r_mis = [cost_r_mis(*p) for p in TRAIN]

    donor_orig_pred, don_o_cs, don_o_cr, donor_orig_fit = fit_donor(TRAIN, obs_s_orig, obs_r_orig)
    cand_mis_pred, can_m_cs, can_m_cr, cand_mis_fit = fit_candidate_generic(
        TRAIN, obs_s_mis, obs_r_mis)
    donor_mis_pred, don_m_cs, don_m_cr, donor_mis_fit = fit_donor(TRAIN, obs_s_mis, obs_r_mis)

    labels_orig = [TRUTH_ORIG(*p) for p in TRAIN]
    labels_mis = [TRUTH_MIS(*p) for p in TRAIN]
    arms_orig = {
        "candidate_orion_analytic_typed": cand_orig_pred,
        "donor_model_selection": donor_orig_pred,
        "b1_nearest_neighbor": fit_nn(TRAIN, labels_orig),
        "b3_linear_classifier": fit_linear(TRAIN, labels_orig),
    }
    arms_mis = {
        "candidate_orion_analytic_typed": cand_mis_pred,
        "donor_model_selection": donor_mis_pred,
        "b1_nearest_neighbor": fit_nn(TRAIN, labels_mis),
        "b3_linear_classifier": fit_linear(TRAIN, labels_mis),
    }

    # --- score frozen predictors on held-out / hostile worlds ---
    worlds = {}
    for wname, pts, truth, arms in (
        ("orig_primary_heldout", PRIMARY, TRUTH_ORIG, arms_orig),
        ("orig_h1_far_extrapolation", H1_FAR, TRUTH_ORIG, arms_orig),
        ("orig_h2_broken_form", PRIMARY, TRUTH_H2, arms_orig),
        ("mis_primary_heldout", PRIMARY, TRUTH_MIS, arms_mis),
    ):
        res = {name: score_arm(pred, pts, truth) for name, pred in arms.items()}
        res["oracle"] = score_arm(truth, pts, truth)
        worlds[wname] = res

    # --- informational crossover probes at frozen path L=128, lam=2.0 ---
    d_true_orig = f5.bisect_crossover(
        f5.cost_s, lambda L, lam, d: f5.cost_r(L, lam, d), 128.0, 2.0, lo=4.0, hi=4096.0)
    d_true_mis = f5.bisect_crossover(cost_s_mis, cost_r_mis, 128.0, 2.0, lo=4.0, hi=4096.0)
    probes = {
        "path": {"L": 128, "lam": 2.0, "d_range": [4, 4096]},
        "orig": {"d_true": d_true_orig,
                 "candidate": probe(cand_orig_cs, cand_orig_cr, d_true_orig),
                 "donor": probe(don_o_cs, don_o_cr, d_true_orig)},
        "mis": {"d_true": d_true_mis,
                "candidate": probe(can_m_cs, can_m_cr, d_true_mis),
                "donor": probe(don_m_cs, don_m_cr, d_true_mis)},
    }

    # --- gates (F5B-G1 determinism is added in main) ---
    with open(F5_RESULTS_PATH) as fh:
        f5_results = json.load(fh)
    f5_scores = {
        "primary": f5_results["worlds"]["primary_heldout"]["orion_analytic_typed"]["score"],
        "h1": f5_results["worlds"]["h1_far_extrapolation"]["orion_analytic_typed"]["score"],
        "h2": f5_results["worlds"]["h2_broken_form"]["orion_analytic_typed"]["score"],
    }
    cand = "candidate_orion_analytic_typed"
    donor = "donor_model_selection"
    cand_scores = {
        "primary": worlds["orig_primary_heldout"][cand]["score"],
        "h1": worlds["orig_h1_far_extrapolation"][cand]["score"],
        "h2": worlds["orig_h2_broken_form"][cand]["score"],
    }
    g2 = cand_scores == f5_scores

    cand_orig = worlds["orig_primary_heldout"][cand]["score"]
    donor_orig = worlds["orig_primary_heldout"][donor]["score"]
    cand_mis = worlds["mis_primary_heldout"][cand]["score"]
    donor_mis = worlds["mis_primary_heldout"][donor]["score"]
    g3_donor_sufficient = donor_orig >= cand_orig - SUFF_TOL
    if cand_mis > donor_mis + MARGIN:
        mis_verdict = "CANDIDATE_AHEAD"
    elif donor_mis > cand_mis + MARGIN:
        mis_verdict = "DONOR_AHEAD"
    else:
        mis_verdict = "TIE"
    g5 = all(worlds[w][a]["score"] <= worlds[w]["oracle"]["score"] + 1e-12
             for w in worlds for a in worlds[w])
    g6 = (worlds["orig_h2_broken_form"][cand]["score"] <= cand_orig - 0.01
          and worlds["orig_h2_broken_form"][donor]["score"] <= donor_orig - 0.01)

    return {
        "schema": "ORIONQ.N2F5BDonorComparisonResult.v1",
        "issue": "SzeChunYiu/ORION#675",
        "family": "f5_residual_donor_comparison",
        "protocol": "development/orion-q-nlane-closure/N2_F5B_DONOR_COMPARISON_PROTOCOL.md",
        "parent_run": {"protocol": "development/orion-q-nlane-closure/N2_F5_PROTOCOL.md",
                       "results": "research/extensions/orion-q/nlanes/N2_F5_CROSSOVER_PREDICTION_RESULTS.json",
                       "terminal": f5_results["terminal"],
                       "orion_scores": f5_scores},
        "seed": SEED,
        "eta_uncertain_band": ETA,
        "comparison_margin": MARGIN,
        "sufficiency_tolerance": SUFF_TOL,
        "mis_world_constants": {"a1": A1, "a2": A2, "a3": A3, "a4": A4,
                                "e_s": ES, "e_L": EL, "e_r": ER, "e_d": ED},
        "mis_world_design_check_labels": {
            "train": {"S": sum(1 for s in labels_mis if s == "S"),
                      "R": sum(1 for s in labels_mis if s == "R")},
            "primary": {"S": sum(1 for p in PRIMARY if TRUTH_MIS(*p) == "S"),
                        "R": sum(1 for p in PRIMARY if TRUTH_MIS(*p) == "R")},
        },
        "n_train": len(TRAIN),
        "fitted": {
            "candidate_orig": cand_orig_fit,
            "candidate_mis": cand_mis_fit,
            "donor_orig": donor_orig_fit,
            "donor_mis": donor_mis_fit,
        },
        "worlds": worlds,
        "crossover_probes": probes,
        "gates": {
            "F5B_G2_f5_reproduction": g2,
            "F5B_G3_donor_sufficiency_orig": g3_donor_sufficient,
            "F5B_G4_mis_world_verdict": mis_verdict,
            "F5B_G5_oracle_bound": g5,
            "F5B_G6_hostile_bite_both": g6,
        },
        "headline": {
            "orig_primary": {"candidate": cand_orig, "donor": donor_orig},
            "mis_primary": {"candidate": cand_mis, "donor": donor_mis},
            "orig_h2_broken": {
                "candidate": worlds["orig_h2_broken_form"][cand]["score"],
                "donor": worlds["orig_h2_broken_form"][donor]["score"]},
        },
        "authority": "exact_synthetic_frozen_world_only; not measured-implementation, hardware, or novelty authority",
        "claim_boundary": (
            "Donor comparison holds only for the frozen world pair of "
            "N2_F5B_DONOR_COMPARISON_PROTOCOL.md (ORIG imported unchanged from F5; MIS frozen "
            "here with true forms outside both libraries). DONOR_ABSORBED retires the F5 "
            "residual's standing-value claim without retiring F5's internal receipts; nothing "
            "here creates LOWER_BOUND, hardware, or novelty authority."
        ),
    }


def main() -> None:
    r1 = pipeline()
    r2 = pipeline()
    deterministic = json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
    g = r1["gates"]
    g["F5B_G1_determinism"] = deterministic
    validity_ok = (deterministic and g["F5B_G2_f5_reproduction"]
                   and g["F5B_G5_oracle_bound"] and g["F5B_G6_hostile_bite_both"])
    donor_sufficient = g["F5B_G3_donor_sufficiency_orig"]
    mis_verdict = g["F5B_G4_mis_world_verdict"]
    if not validity_ok:
        terminal = "N2_F5B_CONTROL_FAILED__NOT_PROMOTABLE"
        disposition = "no disposition: validity/hostile controls failed; F5 residual remains carried forward, unadjudicated"
    elif donor_sufficient and mis_verdict in ("DONOR_AHEAD", "TIE"):
        terminal = "N2_F5B_DONOR_ABSORBED__EXACT_SYNTHETIC_ONLY"
        disposition = ("F5 residual is donor-absorbed: the Predict-and-Conquer-style "
                       "model-selection donor matches or beats the candidate on the original "
                       "world and is not beaten on the misspecified world; the residual "
                       "carries no standing value beyond the donor")
    elif (not donor_sufficient) and mis_verdict == "CANDIDATE_AHEAD":
        terminal = "N2_F5B_RESIDUAL_SURVIVES_DONOR__EXACT_SYNTHETIC_ONLY"
        disposition = "F5 residual survives the donor on both worlds (exact-synthetic scope only)"
    elif donor_sufficient:  # mis_verdict == CANDIDATE_AHEAD
        terminal = "N2_F5B_MIXED__CANDIDATE_AHEAD_ON_MISSPECIFIED_ONLY__EXACT_SYNTHETIC_ONLY"
        disposition = ("mixed: donor absorbs the residual on the original (partly "
                       "well-specified) world; candidate ahead only on the misspecified world")
    else:  # candidate ahead on ORIG, not on MIS
        terminal = "N2_F5B_MIXED__CANDIDATE_AHEAD_ON_ORIGINAL_ONLY__EXACT_SYNTHETIC_ONLY"
        disposition = ("mixed: candidate ahead only on the original (partly well-specified) "
                       "world; donor matches or beats it on the misspecified world")
    r1["terminal"] = terminal
    r1["f5_residual_disposition"] = disposition
    with open(RESULTS_PATH, "w") as fh:
        json.dump(r1, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N2_F5B_DONOR_COMPARISON=" + json.dumps(r1, sort_keys=True))


if __name__ == "__main__":
    main()
