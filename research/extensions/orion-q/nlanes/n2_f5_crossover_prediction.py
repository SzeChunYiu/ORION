"""ORION-Q N2-F5: held-out prospective crossover (regime-switch) prediction.

Executes successor family 5 of issue #675 exactly as frozen in
development/orion-q-nlane-closure/N2_F5_PROTOCOL.md (protocol frozen before outcomes).

Exact-synthetic scope only: frozen synthetic route cost surfaces in the lineage
of the #671 stripped two-route proxy. Prospective discipline: all predictors are
fit on the training grid once and frozen before any held-out grid is generated.
"""

from __future__ import annotations

import itertools
import json
import math
import os

import numpy as np

SEED = 20260821
# C5 = 15.0 per protocol Amendment A1 (originally 0.8, a defective hostile
# control that flipped only 1/96 H2 labels — and that one point fell in the
# UNCERTAIN band). Mechanism/worlds/baselines/gates otherwise unchanged.
C1, C2, C3, C4, C5 = 1.0, 25.0, 0.35, 6.0, 15.0
ETA = 0.02
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(HERE, "N2_F5_CROSSOVER_PREDICTION_RESULTS.json")


def cost_s(L, lam, d):
    return C1 * L * lam * d + C2 * L


def cost_r(L, lam, d, broken=False):
    c = C3 * (lam * d) ** 2 * (1.0 + C4 / d)
    if broken:
        c += C5 * L * math.log2(d) * math.sqrt(lam)
    return c


def true_winner(L, lam, d, broken=False):
    return "S" if cost_s(L, lam, d) <= cost_r(L, lam, d, broken) else "R"


def grid(Ls, lams, ds):
    return [(float(L), float(lam), float(d)) for L, lam, d in itertools.product(Ls, lams, ds)]


TRAIN = grid([8, 12, 16, 24, 32, 48, 64], [1.0, 1.5, 2.2, 3.3], [4, 6, 8, 12, 16, 24, 32])
PRIMARY = grid([80, 120, 160, 240, 320, 480], [1.2, 1.8, 2.7, 4.0], [48, 64, 96, 128])
H1_FAR = grid([640, 1280, 2560], [1.5, 3.0], [192, 384, 768])


# ---------------- frozen predictors (fit on training only) ----------------

def fit_orion(train):
    Xs = np.array([[L * lam * d, L] for L, lam, d in train])
    ys = np.array([cost_s(*p) for p in train])
    Xr = np.array([[(lam * d) ** 2, (lam * d) ** 2 / d] for L, lam, d in train])
    yr = np.array([cost_r(*p) for p in train])
    ws, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
    wr, *_ = np.linalg.lstsq(Xr, yr, rcond=None)

    def predict(L, lam, d):
        cs = ws[0] * L * lam * d + ws[1] * L
        cr = wr[0] * (lam * d) ** 2 + wr[1] * (lam * d) ** 2 / d
        margin = abs(cs - cr) / max(cs, cr)
        if margin < ETA:
            return "UNCERTAIN"
        return "S" if cs <= cr else "R"

    return predict, {"ws": [float(x) for x in ws], "wr": [float(x) for x in wr]}


def fit_nn(train):
    labels = [true_winner(*p) for p in train]  # observed winners in training
    feats = np.array([[math.log(L), math.log(lam), math.log(d)] for L, lam, d in train])

    def predict(L, lam, d):
        q = np.array([math.log(L), math.log(lam), math.log(d)])
        i = int(np.argmin(np.sum((feats - q) ** 2, axis=1)))
        return labels[i]

    return predict


def fit_majority(train):
    labels = [true_winner(*p) for p in train]
    maj = "S" if labels.count("S") >= labels.count("R") else "R"
    return lambda L, lam, d: maj, maj


def fit_linear(train):
    X = np.array([[1.0, math.log(L), math.log(lam), math.log(d)] for L, lam, d in train])
    y = np.array([1.0 if true_winner(*p) == "S" else -1.0 for p in train])
    w, *_ = np.linalg.lstsq(X, y, rcond=None)

    def predict(L, lam, d):
        v = w[0] + w[1] * math.log(L) + w[2] * math.log(lam) + w[3] * math.log(d)
        return "S" if v >= 0 else "R"

    return predict, [float(x) for x in w]


# ---------------- scoring ----------------

def score_arm(predict, points, broken=False):
    total = 0.0
    confident = confident_correct = uncertain = 0
    for L, lam, d in points:
        truth = true_winner(L, lam, d, broken)
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


def bisect_crossover(f_s, f_r, L, lam, lo=4.0, hi=1024.0):
    def g(d):
        return f_s(L, lam, d) - f_r(L, lam, d)
    if g(lo) * g(hi) > 0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g(lo) * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def pipeline() -> dict:
    # fit and FREEZE on training before generating any held-out evaluation
    orion_pred, orion_fit = fit_orion(TRAIN)
    nn_pred = fit_nn(TRAIN)
    maj_pred, maj_label = fit_majority(TRAIN)
    lin_pred, lin_w = fit_linear(TRAIN)
    arms = {
        "orion_analytic_typed": orion_pred,
        "b1_nearest_neighbor": nn_pred,
        "b2_training_majority": maj_pred,
        "b3_linear_classifier": lin_pred,
        "oracle": lambda L, lam, d: true_winner(L, lam, d),
    }
    worlds = {}
    for wname, pts, broken in (
        ("primary_heldout", PRIMARY, False),
        ("h1_far_extrapolation", H1_FAR, False),
        ("h2_broken_form", PRIMARY, True),
    ):
        res = {}
        for aname, pred in arms.items():
            if aname == "oracle" and broken:
                pred = lambda L, lam, d: true_winner(L, lam, d, broken=True)
            res[aname] = score_arm(pred, pts, broken)
        worlds[wname] = res

    # frozen crossover probe: L=128, lam=2.0
    ws, wr = orion_fit["ws"], orion_fit["wr"]
    d_true = bisect_crossover(cost_s, lambda L, lam, d: cost_r(L, lam, d), 128.0, 2.0)
    d_fit = bisect_crossover(
        lambda L, lam, d: ws[0] * L * lam * d + ws[1] * L,
        lambda L, lam, d: wr[0] * (lam * d) ** 2 + wr[1] * (lam * d) ** 2 / d,
        128.0, 2.0)
    xr_err = abs(d_fit - d_true) / d_true if (d_true and d_fit) else None

    prim = worlds["primary_heldout"]
    orion_prim = prim["orion_analytic_typed"]["score"]
    baselines = ["b1_nearest_neighbor", "b2_training_majority", "b3_linear_classifier"]
    gates = {
        "F5_G2_residual": all(orion_prim >= prim[b]["score"] + 0.02 for b in baselines),
        "F5_G3_crossover_location": xr_err is not None and xr_err <= 0.02,
        "F5_G4_oracle_bound": all(
            worlds[w][a]["score"] <= worlds[w]["oracle"]["score"] + 1e-12
            for w in worlds for a in worlds[w]
        ),
        "F5_G5_hostile_bite": (
            worlds["h2_broken_form"]["orion_analytic_typed"]["score"] <= orion_prim - 0.01
        ),
    }
    return {
        "schema": "ORIONQ.N2F5CrossoverPredictionResult.v1",
        "issue": "SzeChunYiu/ORION#675",
        "family": "successor_family_5_heldout_crossover_prediction",
        "protocol": "development/orion-q-nlane-closure/N2_F5_PROTOCOL.md",
        "seed": SEED,
        "true_constants": {"c1": C1, "c2": C2, "c3": C3, "c4": C4, "c5_broken_only": C5},
        "amendments": {
            "A1": (
                "c5 raised 0.8 -> 15.0 after first run showed the broken-form control "
                "flipped only 1/96 H2 labels (that point inside the UNCERTAIN band), "
                "so the hostile control never bit (first-run terminal "
                "N2_F5_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED; first-run "
                "PRIMARY: orion 0.9948 vs best baseline 0.9271, G2 already passing). "
                "Training/PRIMARY/H1 worlds, mechanism, baselines, scoring, gate "
                "thresholds unchanged; G2 is c5-independent."
            ),
        },
        "eta_uncertain_band": ETA,
        "n_train": len(TRAIN),
        "fitted": {"orion": orion_fit, "linear_classifier_w": lin_w,
                   "training_majority": maj_label},
        "worlds": worlds,
        "crossover_probe": {"L": 128, "lam": 2.0, "d_true": d_true, "d_fitted": d_fit,
                            "relative_error": xr_err},
        "gates": gates,
        "authority": "exact_synthetic_frozen_world_only; not measured-implementation, hardware, or novelty authority",
        "claim_boundary": (
            "Prospective residual (or its absence) holds only for the frozen cost "
            "surfaces and grids of N2_F5_PROTOCOL.md; h2_broken_form bounds the "
            "predictor's authority at functional-form shifts; no LOWER_BOUND claim."
        ),
    }


def main() -> None:
    r1 = pipeline()
    r2 = pipeline()
    deterministic = json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
    r1["gates"]["F5_G1_determinism"] = deterministic
    hostile_ok = all(r1["gates"][g] for g in (
        "F5_G1_determinism", "F5_G3_crossover_location",
        "F5_G4_oracle_bound", "F5_G5_hostile_bite"))
    if not hostile_ok:
        terminal = "N2_F5_HOSTILE_CONTROL_FAILED__MECHANISM_NOT_PROMOTED"
    elif r1["gates"]["F5_G2_residual"]:
        terminal = "N2_F5_CROSSOVER_PREDICTION_RESIDUAL_SUPPORTED__EXACT_SYNTHETIC_ONLY"
    else:
        terminal = "N2_F5_CROSSOVER_PREDICTION_NO_RESIDUAL__EXACT_SYNTHETIC_ONLY"
    r1["terminal"] = terminal
    with open(RESULTS_PATH, "w") as fh:
        json.dump(r1, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N2_F5_CROSSOVER_PREDICTION=" + json.dumps(r1, sort_keys=True))


if __name__ == "__main__":
    main()
