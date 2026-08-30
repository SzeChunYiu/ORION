#!/usr/bin/env python3
"""ORION-21 query-family capability successor V2.

Protocol: PROTOCOL_V2.md, committed before this produced any outcome.

V1 asked whether family-scale capability clears >=8/10 and answered no. The
gate-design-power study then showed that miss is real at the registered level but
leaves capability in 0.6-0.8 unresolved, where the V1 gate had 17-68% power. This
estimates capability with enough responsibilities to resolve that band.

Everything mechanical is inherited from V1 verbatim (digits, the 20261121 fold
split, StandardScaler + SelectKBest(f_classif, k=16), the three decoders and
their hyperparameters, and the compiled >= universal - 0.02 quality rule). The
only change is the query family: V1's ten size-one subsets plus the 45 size-two
subsets of the digit alphabet, over the same full dataset. V1's family is the
|S|=1 stratum here, so Stage A reproduces it before anything is extended.

Exit codes: 0 estimated, 3 power still insufficient, 4 reproduction failed.
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

RANDOM_STATE = 20261121
K_SELECT = 16
QUALITY_TOL = 0.02
# Frozen V1 record this study must reproduce on the |S|=1 stratum.
V1_RECORD = {"LINEAR": 3, "RBF": 5, "KNN": 5}
V1_N = 10


def decoders():
    return {
        "LINEAR": lambda: LogisticRegression(C=1, solver="lbfgs", max_iter=5000),
        "RBF": lambda: SVC(C=1, kernel="rbf", gamma="scale"),
        "KNN": lambda: KNeighborsClassifier(n_neighbors=7, weights="distance"),
    }


def one_responsibility(args):
    """Evaluate a single binary responsibility across all folds and decoders."""
    subset, X, y = args
    target = np.isin(y, list(subset)).astype(int)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    acc = {name: {"universal": [], "compiled": []} for name in decoders()}

    # Folds are stratified on the ORIGINAL ten-class labels, exactly as V1 froze.
    for tr, te in skf.split(X, y):
        scaler = StandardScaler().fit(X[tr])
        Xtr_u, Xte_u = scaler.transform(X[tr]), scaler.transform(X[te])
        # Selection sees only the training responsibility: no test label, no
        # future-query outcome.
        sel = SelectKBest(f_classif, k=K_SELECT).fit(Xtr_u, target[tr])
        Xtr_c, Xte_c = sel.transform(Xtr_u), sel.transform(Xte_u)
        for name, make in decoders().items():
            for tag, (a, b) in (("universal", (Xtr_u, Xte_u)), ("compiled", (Xtr_c, Xte_c))):
                m = make().fit(a, target[tr])
                acc[name][tag].append(
                    balanced_accuracy_score(target[te], m.predict(b))
                )

    out = {"subset": sorted(subset), "stratum": len(subset), "per_decoder": {}}
    for name in decoders():
        u = float(np.mean(acc[name]["universal"]))
        c = float(np.mean(acc[name]["compiled"]))
        out["per_decoder"][name] = {
            "universal_mean": u,
            "compiled_mean": c,
            "delta": c - u,
            "quality_supported": bool(c >= u - QUALITY_TOL),
        }
    return out


def clopper_pearson(k: int, n: int, alpha: float = 0.05):
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def read_interval(lo: float, hi: float) -> str:
    if hi < 0.6:
        return "BOUNDED_BELOW_0.6__V1_NEGATIVE_STRENGTHENED"
    if lo >= 0.6 and hi <= 0.8:
        return "RESOLVED_IN_0.6_0.8__REGIME_CONDITIONAL_STILL_BELOW_V1_BAR"
    if lo < 0.8 < hi:
        return "STRADDLES_0.8__NOT_RESOLVED"
    return "OTHER__REPORTED_VERBATIM"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_V2.json")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--smoke", action="store_true",
                    help="|S|=1 stratum only; reproduction check without the extension")
    a = ap.parse_args()

    d = load_digits()
    X, y = d.data, d.target
    singles = [frozenset([i]) for i in range(10)]
    pairs = [frozenset(c) for c in combinations(range(10), 2)]
    family = singles if a.smoke else singles + pairs

    jobs = [(s, X, y) for s in family]
    if a.workers > 1:
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            rows = list(ex.map(one_responsibility, jobs, chunksize=1))
    else:
        rows = [one_responsibility(j) for j in jobs]

    # ---- Stage A: reproduce the frozen |S|=1 stratum before extending ----
    repro, repro_ok = {}, True
    for name in decoders():
        got = sum(r["per_decoder"][name]["quality_supported"]
                  for r in rows if r["stratum"] == 1)
        repro[name] = {"recomputed": got, "v1_recorded": V1_RECORD[name],
                       "matches": got == V1_RECORD[name]}
        repro_ok &= got == V1_RECORD[name]

    # ---- Stage B: capability with intervals, by stratum and pooled ----
    strata = {"single_|S|=1": [1], "pair_|S|=2": [2], "pooled": [1, 2]}
    capability, readings = {}, {}
    for label, keep in strata.items():
        sel = [r for r in rows if r["stratum"] in keep]
        capability[label] = {}
        for name in decoders():
            k = sum(r["per_decoder"][name]["quality_supported"] for r in sel)
            n = len(sel)
            lo, hi = clopper_pearson(k, n)
            capability[label][name] = {
                "supported": k, "n": n,
                "point": (k / n) if n else None,
                "ci95_clopper_pearson": [lo, hi],
                "width": hi - lo,
            }
            if label == "pooled":
                readings[name] = read_interval(lo, hi)

    if not repro_ok:
        terminal, rc = "REPRO_FAILED", 4
    elif a.smoke:
        terminal, rc = "REPRODUCTION_ONLY__NO_EXTENSION", 0
    elif all(v == "STRADDLES_0.8__NOT_RESOLVED" for v in readings.values()):
        terminal, rc = "CANNOT_CHECK_POWER_STILL_INSUFFICIENT", 3
    else:
        terminal, rc = "QUERY_FAMILY_CAPABILITY_ESTIMATED", 0

    proto = Path(__file__).with_name("PROTOCOL_V2.md")
    out = {
        "schema": "ORION21.QUERY_FAMILY_CAPABILITY.v2",
        "parent_terminal": "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET",
        "parent_unchanged": True,
        "estimand": "P(responsibility is quality-supported), compiled >= universal - 0.02",
        "protocol_sha256": hashlib.sha256(proto.read_bytes()).hexdigest()
        if proto.is_file() else None,
        "environment": {
            "python": platform.python_version(),
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "node": platform.node(),
        },
        "family_size": len(family),
        "reproduction_stage_a": repro,
        "reproduction_ok": repro_ok,
        "capability": capability,
        "pooled_readings": readings,
        "dependence_note": (
            "responsibilities within a stratum share one dataset and one fold split, "
            "so they are not independent; these are nominal binomial intervals and the "
            "dependence is stated rather than modelled away"
        ),
        "authority": (
            "estimation study; declares no gate of its own and promotes no ORION-21 "
            "claim. The V1 >=8/10 negative and P11_ACTIVE_CLAIM_AUTHORITY_V2 stand."
        ),
        "terminal": terminal,
        "rows": rows,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("family_size", "reproduction_stage_a", "reproduction_ok",
                       "pooled_readings", "terminal")}, indent=2))
    for name in decoders():
        c = capability["pooled"][name]
        print(f"  pooled {name:<7} {c['supported']}/{c['n']} "
              f"point={c['point']:.3f} CI=[{c['ci95_clopper_pearson'][0]:.3f}, "
              f"{c['ci95_clopper_pearson'][1]:.3f}]")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
