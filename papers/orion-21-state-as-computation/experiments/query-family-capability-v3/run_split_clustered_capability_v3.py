#!/usr/bin/env python3
"""ORION-21 capability V3: an interval that respects the fold split.

Protocol: PROTOCOL_V3.md, committed before this produced any outcome.

V2 estimated family-scale capability over 55 responsibilities and reported a
binomial interval, while saying in the same breath that the responsibilities are
not independent: they share one dataset and one StratifiedKFold split. This prices
the second of those. The first is not addressable offline -- only `digits` has the
d >= 16 features and the class count the mechanism needs -- and V3 does not claim
to fix it.

The seed is the clustering unit. Every responsibility in a given repetition is
scored against the same partition, so a partition that happens to favour the
compiled state moves all 55 counts together. Resampling responsibilities, as a
binomial interval implicitly does, cannot see that. Resampling seeds can.

Exit codes: 0 capability survives clustering, 1 reversed, 3 dependence not priced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

import numpy as np
import sklearn
from scipy.stats import beta
from sklearn.datasets import load_digits
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

BASE_SEED = 20261121
N_SEEDS = 20
SEEDS = tuple(BASE_SEED + i for i in range(N_SEEDS))  # fixed here, not chosen later
K_SELECT = 16
QUALITY_TOL = 0.02
DECODERS = ("LINEAR", "RBF", "KNN")


def make(name: str):
    if name == "LINEAR":
        return LogisticRegression(C=1, solver="lbfgs", max_iter=5000)
    if name == "RBF":
        return SVC(C=1, kernel="rbf", gamma="scale")
    return KNeighborsClassifier(n_neighbors=7, weights="distance")


def one_job(args):
    """One (seed, responsibility): quality-supported per decoder."""
    seed, subset, X, y = args
    target = np.isin(y, list(subset)).astype(int)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    acc = {d: {"u": [], "c": []} for d in DECODERS}
    for tr, te in skf.split(X, y):
        scaler = StandardScaler().fit(X[tr])
        Xtr_u, Xte_u = scaler.transform(X[tr]), scaler.transform(X[te])
        sel = SelectKBest(f_classif, k=K_SELECT).fit(Xtr_u, target[tr])
        Xtr_c, Xte_c = sel.transform(Xtr_u), sel.transform(Xte_u)
        for d in DECODERS:
            for tag, (a, b) in (("u", (Xtr_u, Xte_u)), ("c", (Xtr_c, Xte_c))):
                m = make(d).fit(a, target[tr])
                acc[d][tag].append(balanced_accuracy_score(target[te], m.predict(b)))
    out = {"seed": seed, "stratum": len(subset), "supported": {}}
    for d in DECODERS:
        u = float(np.mean(acc[d]["u"]))
        c = float(np.mean(acc[d]["c"]))
        out["supported"][d] = bool(c >= u - QUALITY_TOL)
    return out


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def seed_bootstrap(per_seed, reps=20000, seed=20260830):
    """Percentile interval resampling SEEDS -- the unit that actually varies."""
    rng = np.random.default_rng(seed)
    vals = np.asarray(per_seed, dtype=float)
    draws = rng.choice(vals, size=(reps, vals.size), replace=True).mean(axis=1)
    return [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_V3.json")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--seeds", type=int, default=N_SEEDS)
    a = ap.parse_args()

    d = load_digits()
    X, y = d.data, d.target
    family = [frozenset([i]) for i in range(10)] + [frozenset(c) for c in combinations(range(10), 2)]
    seeds = SEEDS[: a.seeds]
    jobs = [(s, sub, X, y) for s in seeds for sub in family]

    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(one_job, jobs, chunksize=4))
    else:
        rows = [one_job(j) for j in jobs]

    per_seed = {dcd: [] for dcd in DECODERS}
    seed_rows = []
    for s in seeds:
        mine = [r for r in rows if r["seed"] == s]
        entry = {"seed": s, "n": len(mine), "counts": {}}
        for dcd in DECODERS:
            k = sum(r["supported"][dcd] for r in mine)
            entry["counts"][dcd] = k
            per_seed[dcd].append(k / len(mine))
        seed_rows.append(entry)

    n_family = len(family)
    summary, readings = {}, {}
    for dcd in DECODERS:
        vals = per_seed[dcd]
        pooled_k = sum(e["counts"][dcd] for e in seed_rows)
        pooled_n = sum(e["n"] for e in seed_rows)
        nominal = clopper_pearson(
            sum(seed_rows[0]["counts"][dcd] for _ in [0]), n_family
        )  # V2-comparable: one seed, binomial over responsibilities
        clustered = seed_bootstrap(vals)
        summary[dcd] = {
            "per_seed_capability": [round(v, 4) for v in vals],
            "mean_capability": float(np.mean(vals)),
            "seed_spread_min_max": [float(np.min(vals)), float(np.max(vals))],
            "seed_clustered_ci95": clustered,
            "seed_clustered_width": clustered[1] - clustered[0],
            "v2_style_binomial_ci95_first_seed": nominal,
            "v2_style_width": nominal[1] - nominal[0],
            "width_ratio_clustered_over_binomial": (
                (clustered[1] - clustered[0]) / (nominal[1] - nominal[0])
                if nominal[1] > nominal[0] else None
            ),
            "pooled_supported": pooled_k,
            "pooled_n": pooled_n,
        }
        lo, hi = clustered
        if hi < 0.6:
            readings[dcd] = "BELOW_0.6__SURVIVES_CLUSTERING"
        elif lo >= 0.6:
            readings[dcd] = "ABOVE_0.6__REVERSED"
        else:
            readings[dcd] = "STRADDLES_0.6__DEPENDENCE_NOT_PRICED"

    if all(v == "BELOW_0.6__SURVIVES_CLUSTERING" for v in readings.values()):
        terminal, rc = "CAPABILITY_SURVIVES_SPLIT_CLUSTERING", 0
    elif any(v == "ABOVE_0.6__REVERSED" for v in readings.values()):
        terminal, rc = "CAPABILITY_REVERSED", 1
    else:
        terminal, rc = "CANNOT_CHECK_DEPENDENCE_NOT_PRICED", 3

    proto = Path(__file__).with_name("PROTOCOL_V3.md")
    out = {
        "schema": "ORION21.QUERY_FAMILY_CAPABILITY.v3",
        "parent": "ORION21.QUERY_FAMILY_CAPABILITY.v2",
        "parent_unchanged": True,
        "protocol_sha256": hashlib.sha256(proto.read_bytes()).hexdigest() if proto.is_file() else None,
        "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                        "numpy": np.__version__, "node": platform.node()},
        "seeds": list(seeds),
        "family_size": n_family,
        "clustering_unit": "fold seed",
        "per_seed_counts": seed_rows,
        "summary": summary,
        "readings": readings,
        "not_addressed": (
            "the shared dataset. Only digits has the d>=16 features and class count "
            "this mechanism needs among datasets available without network access, so "
            "dataset-level independence is out of reach here and is not claimed."
        ),
        "authority": (
            "estimation study; declares no gate, promotes no ORION-21 claim. V1's "
            ">=8/10 negative and P11_ACTIVE_CLAIM_AUTHORITY_V2 stand."
        ),
        "terminal": terminal,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"terminal": terminal, "readings": readings}, indent=2))
    for dcd in DECODERS:
        s = summary[dcd]
        print(f"  {dcd:<7} mean={s['mean_capability']:.3f} "
              f"clustered CI=[{s['seed_clustered_ci95'][0]:.3f}, {s['seed_clustered_ci95'][1]:.3f}] "
              f"w={s['seed_clustered_width']:.3f} vs binomial w={s['v2_style_width']:.3f} "
              f"ratio={s['width_ratio_clustered_over_binomial']:.2f}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
