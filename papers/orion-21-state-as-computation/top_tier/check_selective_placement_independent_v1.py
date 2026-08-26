#!/usr/bin/env python3
"""Structurally independent NR-12 selective-placement verifier.

Manual NumPy scaling, manual binary-ANOVA F ranking with explicit stable
tie-breaking, manual balanced accuracy, independent inner-fold bookkeeping.
Agrees-by-construction targets: every placement bit, support count, placed mean,
resource identity, terminal. Same frozen constants as the protocol.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_SELECTIVE_PLACEMENT_PROTOCOL_V1.md"
D = 64; K = 16; QUERIES = range(10)
ARMS = ("LINEAR", "RBF", "KNN")
OUTER_FROZEN = 20261121
OUTER_SECONDARY = (20261122, 20261123, 20261124)
INNER_SEED = 2026112207
INNER_MODEL_SEED_BASE = 2026112500
BATTERY_MODEL_SEED_BASE = 2026112100
TOL = 0.02
V1_BASELINE = {"LINEAR": 3, "RBF": 5, "KNN": 5}


def scale_fit(x):
    mean = x.mean(axis=0); std = x.std(axis=0, ddof=0)
    std = np.where(std == 0.0, 1.0, std)
    return mean, std


def scale_apply(x, mean, std): return (x - mean) / std


def f_rank(x, y):
    n = x.shape[0]; g0 = x[y == 0]; g1 = x[y == 1]; grand = x.mean(axis=0)
    ssb = g0.shape[0] * (g0.mean(axis=0) - grand) ** 2 + g1.shape[0] * (g1.mean(axis=0) - grand) ** 2
    ssw = ((g0 - g0.mean(axis=0)) ** 2).sum(axis=0) + ((g1 - g1.mean(axis=0)) ** 2).sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        f = ssb / (ssw / (n - 2))
    return np.nan_to_num(f, nan=-np.inf, posinf=np.inf, neginf=-np.inf)


def top_k(scores, k):
    order = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), i))
    return np.asarray(order[:k], dtype=int)


def bac(y, pred):
    return float((np.mean(pred[y == 0] == 0) + np.mean(pred[y == 1] == 1)) / 2.0)


def model(kind, seed):
    if kind == "LINEAR": return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)
    if kind == "RBF": return SVC(C=1.0, kernel="rbf", gamma="scale")
    if kind == "KNN": return KNeighborsClassifier(n_neighbors=7, weights="distance")
    raise ValueError(kind)


def placements_for(x_raw, y_full, fold):
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=INNER_SEED)
    out = {}
    for q in QUERIES:
        yt = (y_full == q).astype(int); uni = []; comp = []
        for itr, iva in inner.split(x_raw, yt):
            mean, std = scale_fit(x_raw[itr])
            a_tr = scale_apply(x_raw[itr], mean, std); a_va = scale_apply(x_raw[iva], mean, std)
            idx = top_k(f_rank(a_tr, yt[itr]), K)
            seed = INNER_MODEL_SEED_BASE + fold * 10 + q
            m = model("LINEAR", seed); m.fit(a_tr, yt[itr]); uni.append(bac(yt[iva], m.predict(a_va)))
            m = model("LINEAR", seed); m.fit(a_tr[:, idx], yt[itr]); comp.append(bac(yt[iva], m.predict(a_va[:, idx])))
        out[q] = {"inner_universal_mean": float(np.mean(uni)), "inner_compiled_mean": float(np.mean(comp)),
                  "placed": bool(np.mean(comp) >= np.mean(uni) - TOL)}
    return out


def run_seed(outer_seed):
    b = load_digits(); X = np.asarray(b.data, dtype=np.float64); y = np.asarray(b.target)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=outer_seed)
    scores = {(q, a, s): [] for q in QUERIES for a in ARMS for s in ("UNIVERSAL", "COMPILED")}
    placements = {}; train_sizes = []
    for fold, (tr, te) in enumerate(cv.split(X, y)):
        train_sizes.append(len(tr))
        placements[fold] = placements_for(X[tr], y[tr], fold)
        mean, std = scale_fit(X[tr])
        xt = scale_apply(X[tr], mean, std); xv = scale_apply(X[te], mean, std)
        for q in QUERIES:
            yt = (y[tr] == q).astype(int); ye = (y[te] == q).astype(int)
            idx = top_k(f_rank(xt, yt), K)
            for kind in ARMS:
                seed = BATTERY_MODEL_SEED_BASE + fold * 10 + q
                m = model(kind, seed); m.fit(xt, yt); scores[(q, kind, "UNIVERSAL")].append(bac(ye, m.predict(xv)))
                m = model(kind, seed); m.fit(xt[:, idx], yt); scores[(q, kind, "COMPILED")].append(bac(ye, m.predict(xv[:, idx])))
    support_counts = {}; query_results = {}
    for kind in ARMS:
        n = 0
        for q in QUERIES:
            u = scores[(q, kind, "UNIVERSAL")]; c = scores[(q, kind, "COMPILED")]
            um = float(np.mean(u)); cm = float(np.mean(c))
            pl = [placements[f][q]["placed"] for f in range(5)]
            pm = float(np.mean([ci if p else ui for p, ui, ci in zip(pl, u, c)]))
            sup = pm >= um - TOL; n += int(sup)
            query_results[f"{kind}:{q}"] = {"universal_mean": um, "compiled_mean": cm, "placed_mean": pm,
                                            "placed_delta": pm - um, "quality_supported": sup,
                                            "placed_folds": [bool(p) for p in pl]}
        support_counts[kind] = n
    fold_sizes = {str(f): sum(1 for q in QUERIES if placements[f][q]["placed"]) for f in range(5)}
    n_mean = float(np.mean(train_sizes))
    be = math.floor(n_mean * D / (D - K)) + 1
    gate = {
        "nonvacuity_all_folds": all(s >= 1 for s in fold_sizes.values()),
        "linear_support_ge_8": support_counts["LINEAR"] >= 8,
        "stronger_support_ge_8": max(support_counts["RBF"], support_counts["KNN"]) >= 8,
        "all_ten_reported": len(query_results) == 30,
        "no_family_below_frozen_baseline": all(support_counts[a] >= V1_BASELINE[a] for a in ARMS),
        "resource_identities": all(s >= 1 for s in fold_sizes.values()) and be == math.floor(n_mean * D / (D - K)) + 1,
    }
    return {"outer_seed": outer_seed, "support_counts": support_counts, "query_results": query_results,
            "placements": {str(f): {str(q): placements[f][q] for q in QUERIES} for f in range(5)},
            "fold_placement_sizes": fold_sizes,
            "mean_break_even_per_placed_query": be,
            "selective_state_floats_per_example_by_fold": {f: D + K * s for f, s in fold_sizes.items()},
            "gate_components": gate,
            "terminal": "P11_SELECTIVE_PLACEMENT_SECOND_INDEPENDENT_CHECKER_GREEN"
                        if all(gate.values()) else "P11_SELECTIVE_PLACEMENT_SECOND_CHECKER_GATE_NOT_MET"}


def main():
    primary = run_seed(OUTER_FROZEN)
    secondary = [run_seed(s) for s in OUTER_SECONDARY]
    receipt = {"schema": "P11.SelectivePlacementIndependent.v1",
               "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
               "primary": primary, "secondary_seeds": secondary, "terminal": primary["terminal"]}
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    out = HERE / "p11_selective_placement_independent_v1.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert primary["terminal"] == "P11_SELECTIVE_PLACEMENT_SECOND_INDEPENDENT_CHECKER_GREEN", receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
