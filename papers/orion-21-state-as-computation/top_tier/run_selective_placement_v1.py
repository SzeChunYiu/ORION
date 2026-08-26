#!/usr/bin/env python3
"""NR-12: execute the prospectively frozen P11 selective placement study V1.

Re-executes the frozen P11_QUERY_FAMILY_PHASE_V1 battery unmodified (same folds,
scaler, SelectKBest(k=16), access classes, seeds, tolerance) and adds ONLY the
frozen train-only placement selector. See P11_SELECTIVE_PLACEMENT_PROTOCOL_V1.md.
"""
from __future__ import annotations
from collections import defaultdict
import hashlib, json, math
from pathlib import Path
import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_SELECTIVE_PLACEMENT_PROTOCOL_V1.md"
FROZEN_PRIMARY = HERE / "p11_query_family_phase_primary_v1.json"
D = 64; K = 16; QUERIES = list(range(10))
ARMS = ("LINEAR", "RBF", "KNN")
OUTER_FROZEN = 20261121
OUTER_SECONDARY = [20261122, 20261123, 20261124]
INNER_SEED = 2026112207
INNER_MODEL_SEED_BASE = 2026112500
BATTERY_MODEL_SEED_BASE = 2026112100  # frozen V1 formula
TOL = 0.02
V1_BASELINE = {"LINEAR": 3, "RBF": 5, "KNN": 5}


def model(kind, seed):
    if kind == "LINEAR": return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)
    if kind == "RBF": return SVC(C=1.0, kernel="rbf", gamma="scale")
    if kind == "KNN": return KNeighborsClassifier(n_neighbors=7, weights="distance")
    raise ValueError(kind)


def selector_placements(xf_tr_full, y_tr_full, fold):
    """Frozen train-only selector: inner-CV LINEAR compiled-vs-universal tolerance."""
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=INNER_SEED)
    placements = {}
    for q in QUERIES:
        yt = (y_tr_full == q).astype(int)
        uni, comp = [], []
        for itr, iva in inner.split(xf_tr_full, yt):
            sc = StandardScaler().fit(xf_tr_full[itr])
            a_tr, a_va = sc.transform(xf_tr_full[itr]), sc.transform(xf_tr_full[iva])
            skb = SelectKBest(score_func=f_classif, k=K).fit(a_tr, yt[itr])
            c_tr, c_va = skb.transform(a_tr), skb.transform(a_va)
            m = model("LINEAR", INNER_MODEL_SEED_BASE + fold * 10 + q)
            m.fit(a_tr, yt[itr]); uni.append(balanced_accuracy_score(yt[iva], m.predict(a_va)))
            m = model("LINEAR", INNER_MODEL_SEED_BASE + fold * 10 + q)
            m.fit(c_tr, yt[itr]); comp.append(balanced_accuracy_score(yt[iva], m.predict(c_va)))
        placements[q] = {
            "inner_universal_mean": float(np.mean(uni)),
            "inner_compiled_mean": float(np.mean(comp)),
            "inner_delta": float(np.mean(comp) - np.mean(uni)),
            "placed": bool(np.mean(comp) >= np.mean(uni) - TOL),
        }
    return placements


def run_seed(outer_seed):
    bunch = load_digits(); X = np.asarray(bunch.data, dtype=np.float64); y = np.asarray(bunch.target)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=outer_seed)
    rows = []; placements_by_fold = {}; train_sizes = []
    for fold, (tr, te) in enumerate(cv.split(X, y)):
        train_sizes.append(len(tr))
        scaler = StandardScaler().fit(X[tr]); xf_tr = scaler.transform(X[tr]); xf_te = scaler.transform(X[te])
        placements_by_fold[fold] = selector_placements(X[tr], y[tr], fold)
        for q in QUERIES:
            yt = (y[tr] == q).astype(int); ye = (y[te] == q).astype(int)
            comp = SelectKBest(score_func=f_classif, k=K).fit(xf_tr, yt)
            xc_tr = comp.transform(xf_tr); xc_te = comp.transform(xf_te)
            placed = placements_by_fold[fold][q]["placed"]
            for kind in ARMS:
                seed = BATTERY_MODEL_SEED_BASE + fold * 10 + q
                for state, xt, xv in (("UNIVERSAL", xf_tr, xf_te), ("COMPILED", xc_tr, xc_te)):
                    m = model(kind, seed); m.fit(xt, yt)
                    rows.append({"fold": fold, "query": q, "access": kind, "state": state,
                                 "balanced_accuracy": float(balanced_accuracy_score(ye, m.predict(xv)))})
    by = defaultdict(list)
    for r in rows: by[(r["query"], r["access"], r["state"])].append(r["balanced_accuracy"])
    support_counts = {}; query_results = {}; fp_fn = {}
    v1_qs = json.loads(FROZEN_PRIMARY.read_text())["query_results"] if outer_seed == OUTER_FROZEN else None
    max_dev = 0.0
    for kind in ARMS:
        n = 0
        for q in QUERIES:
            u = by[(q, kind, "UNIVERSAL")]; c = by[(q, kind, "COMPILED")]
            um = float(np.mean(u)); cm = float(np.mean(c))
            placed_folds = [placements_by_fold[f][q]["placed"] for f in range(5)]
            pm = float(np.mean([ci if pl else ui for pl, ui, ci in zip(placed_folds, u, c)]))
            supported = pm >= um - TOL; n += int(supported)
            query_results[f"{kind}:{q}"] = {
                "universal_mean": um, "compiled_mean": cm, "placed_mean": pm,
                "placed_delta": pm - um, "compiled_delta": cm - um,
                "quality_supported": supported, "placed_folds": placed_folds,
            }
            if v1_qs is not None:
                max_dev = max(max_dev, abs(um - v1_qs[f"{kind}:{q}"]["universal_mean"]),
                              abs(cm - v1_qs[f"{kind}:{q}"]["compiled_mean"]))
        support_counts[kind] = n
        fp = sum(1 for q in QUERIES if any(pl for pl in query_results[f"{kind}:{q}"]["placed_folds"])
                 and not query_results[f"{kind}:{q}"]["compiled_delta"] >= -TOL)
        # stricter per-fold FP: a (fold,query) placed cell whose compiled test BA that fold
        # fell more than TOL below that fold's universal BA
        fpf = 0
        for q in QUERIES:
            for f in range(5):
                if placements_by_fold[f][q]["placed"]:
                    uf = by[(q, kind, "UNIVERSAL")][f]; cf = by[(q, kind, "COMPILED")][f]
                    fpf += int(not (cf >= uf - TOL))
        fn = sum(1 for q in QUERIES if not any(pl for pl in query_results[f"{kind}:{q}"]["placed_folds"])
                 and query_results[f"{kind}:{q}"]["compiled_delta"] >= -TOL)
        fp_fn[kind] = {"false_positives_query_level": fp, "false_positives_fold_cells": fpf,
                       "false_negatives_query_level": fn}
    fold_sizes = {str(f): sum(1 for q in QUERIES if placements_by_fold[f][q]["placed"]) for f in range(5)}
    n_train_mean = float(np.mean(train_sizes))
    be_per_placed = {}
    for f in range(5):
        be_per_placed[str(f)] = math.floor(train_sizes[f] * D / (D - K)) + 1
    resource = {
        "selective_state_floats_per_example_by_fold": {f: D + K * s for f, s in fold_sizes.items()},
        "universal_state_floats_per_example": D,
        "memory_gap_per_example_by_fold": {f: K * s for f, s in fold_sizes.items()},
        "memory_never_wins": all(D + K * s > D for s in fold_sizes.values()),
        "break_even_horizon_per_placed_query_by_fold": be_per_placed,
        "mean_break_even_horizon_per_placed_query": math.floor(n_train_mean * D / (D - K)) + 1,
        "future_query_arrival_tax": "one fit iff the arriving responsibility is placed by the train-only rule; zero otherwise",
    }
    nonvacuous = all(s >= 1 for s in fold_sizes.values())
    gate = {
        "nonvacuity_all_folds": nonvacuous,
        "linear_support_ge_8": support_counts["LINEAR"] >= 8,
        "stronger_support_ge_8": max(support_counts["RBF"], support_counts["KNN"]) >= 8,
        "all_ten_reported": len(query_results) == 30,
        "no_family_below_frozen_baseline": all(support_counts[a] >= V1_BASELINE[a] for a in ARMS),
        "resource_identities": resource["memory_never_wins"]
                                and resource["mean_break_even_horizon_per_placed_query"] == math.floor(n_train_mean * D / (D - K)) + 1,
    }
    positive = all(gate.values())
    return {
        "outer_seed": outer_seed,
        "environment": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "support_counts": support_counts,
        "v1_baseline_counts": V1_BASELINE,
        "query_results": query_results,
        "placements_by_fold": {str(f): {str(q): placements_by_fold[f][q] for q in QUERIES} for f in range(5)},
        "fold_placement_sizes": fold_sizes,
        "selector_fp_fn": fp_fn,
        "resource": resource,
        "gate_components": gate,
        "frozen_battery_max_deviation_from_v1_receipt": max_dev if v1_qs is not None else None,
        "rows": rows,
        "terminal": "P11_SELECTIVE_PLACEMENT_V1_SUPPORTED" if positive else "P11_SELECTIVE_PLACEMENT_V1_GATE_NOT_MET",
    }


def main():
    primary = run_seed(OUTER_FROZEN)
    secondary = []
    for s in OUTER_SECONDARY:
        r = run_seed(s); r.pop("rows"); secondary.append(r)
    terminal = primary["terminal"]
    receipt = {
        "schema": "P11.SelectivePlacementResult.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "primary": primary,
        "secondary_seeds": secondary,
        "terminal": terminal,
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    out = HERE / "p11_selective_placement_primary_v1.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True))
    slim = {k: v for k, v in receipt.items() if k != "primary"}
    slim["primary"] = {k: v for k, v in primary.items() if k != "rows"}
    print(json.dumps(slim, indent=2, sort_keys=True))
    assert terminal == "P11_SELECTIVE_PLACEMENT_V1_SUPPORTED", json.dumps(slim, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
