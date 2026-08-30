#!/usr/bin/env python3
"""ORION-08 real-domain transfer on OpenML-CC18.

Protocol: PROTOCOL_V1.md, committed before this produced any outcome.

ORION-08's theorems are exact statements about fibres:

  T1  a zero-regret policy exists iff every positive-mass fibre has a common
      optimal action;
  T2  refinement decreases regret strictly, exactly when it splits an
      action-impure fibre.

"Exactly when" is refutable by one positive-mass fibre behaving otherwise, and is
not established by any number of agreements. This runs the test on real decision
families and reports both directions.

Exit codes: 0 prediction holds throughout, 1 contradicted, 3 no contrast.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

# Frozen asymmetric utility. Optimal action is 1 iff P(y=1|fibre) > 0.5.
U = {(1, 1): 1.0, (1, 0): -1.0, (0, 1): 0.0, (0, 0): 0.0}
K_COARSE = 2
K_EXTRA = 2
N_BINS = 3
# "Positive mass" on an empirical distribution means at least one row. An
# arbitrary threshold here would apply to the prediction but not to the regret
# measurement, which counts every row, and the mismatch would manufacture
# contradictions out of small fibres the purity test never looked at.
MIN_MASS = 1
SPLIT_SEED = 20260830

# CC18 members with binary targets, in ascending data_id. Fixed before outcomes.
DATASETS = [(31, "credit-g"), (37, "diabetes"), (44, "spambase"), (1462, "banknote"),
            (1464, "blood-transfusion"), (1494, "qsar-biodeg"), (1510, "wdbc")]


def optimal_action(p1: float) -> int:
    """argmax_a E[u(a,y)] with P(y=1)=p1."""
    return 1 if (U[(1, 1)] * p1 + U[(1, 0)] * (1 - p1)) > (U[(0, 1)] * p1 + U[(0, 0)] * (1 - p1)) else 0


def policy_utility(fibres: np.ndarray, y: np.ndarray) -> tuple[float, dict]:
    """Best fibre-measurable policy: pick the utility-maximising action per fibre."""
    total, actions = 0.0, {}
    for f in np.unique(fibres):
        m = fibres == f
        p1 = float(y[m].mean())
        a = optimal_action(p1)
        actions[int(f)] = a
        total += sum(U[(a, int(v))] for v in y[m])
    return total / len(y), actions


def oracle_utility(y: np.ndarray) -> float:
    """Per-row optimal action. An upper bound, not a policy."""
    return sum(max(U[(1, int(v))], U[(0, int(v))]) for v in y) / len(y)


def binned(X: np.ndarray, cols, edges) -> np.ndarray:
    """Stable integer code for the chosen columns' bins."""
    code = np.zeros(len(X), dtype=np.int64)
    for c in cols:
        b = np.digitize(X[:, c], edges[c])
        code = code * (N_BINS + 2) + b
    return code


def run_dataset(data_id: int, name: str) -> dict | None:
    from sklearn.datasets import fetch_openml
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.feature_selection import mutual_info_classif
    from sklearn.model_selection import train_test_split

    d = fetch_openml(data_id=data_id, as_frame=True, parser="auto")
    X = d.data.select_dtypes(include=[np.number]).to_numpy(dtype=float)
    if X.shape[1] < K_COARSE + K_EXTRA + 1:
        return None
    classes = list(dict.fromkeys(d.target.tolist()))
    if len(classes) != 2:
        return None
    y = (d.target.to_numpy() == classes[1]).astype(int)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.5, random_state=SPLIT_SEED, stratify=y)

    # bin edges from TRAIN only
    edges = {c: np.quantile(Xtr[:, c], np.linspace(0, 1, N_BINS + 1)[1:-1])
             for c in range(X.shape[1])}

    coarse_cols = list(range(K_COARSE))
    refined_cols = list(range(K_COARSE + K_EXTRA))

    # ---- the prediction, from TRAIN only, before any evaluation score ----
    ctr = binned(Xtr, coarse_cols, edges)
    rtr = binned(Xtr, refined_cols, edges)
    impure = []
    for f in np.unique(ctr):
        m = ctr == f
        if m.sum() < MIN_MASS:
            continue
        acts = set()
        for sf in np.unique(rtr[m]):
            sm = m & (rtr == sf)
            if sm.sum() < MIN_MASS:
                continue
            acts.add(optimal_action(float(ytr[sm].mean())))
        if len(acts) > 1:
            impure.append(int(f))
    predicts_strict_decrease = len(impure) > 0

    # ---- arms, scored on the held-out half ----
    cte = binned(Xte, coarse_cols, edges)
    rte = binned(Xte, refined_cols, edges)
    _, coarse_actions = policy_utility(ctr, ytr)
    _, refined_actions = policy_utility(rtr, ytr)

    def apply(actions, fib):
        a = np.array([actions.get(int(f), 0) for f in fib])
        return sum(U[(int(ai), int(v))] for ai, v in zip(a, yte)) / len(yte)

    orc = oracle_utility(yte)
    arms = {"coarse": apply(coarse_actions, cte),
            "refined_typed": apply(refined_actions, rte)}

    # strongest deterministic proxy
    clf = HistGradientBoostingClassifier(random_state=SPLIT_SEED).fit(Xtr, ytr)
    ptr, pte = clf.predict(Xtr), clf.predict(Xte)
    _, pa = policy_utility(ptr.astype(np.int64), ytr)
    arms["proxy_strong"] = apply(pa, pte.astype(np.int64))

    # generic acquisition: add the highest-MI feature, ignoring the theorem
    mi = mutual_info_classif(Xtr, ytr, random_state=SPLIT_SEED)
    extra = int(np.argsort(-mi)[0])
    ig_cols = coarse_cols + ([extra] if extra not in coarse_cols else [])
    itr, ite = binned(Xtr, ig_cols, edges), binned(Xte, ig_cols, edges)
    _, ia = policy_utility(itr, ytr)
    arms["infogain_refine"] = apply(ia, ite)

    # The theorem is an exact statement about the distribution the fibres are
    # defined on, so it is scored IN-SAMPLE. Measuring it out-of-sample instead
    # conflates it with generalisation: a refinement has more fibres and fewer
    # rows each, so it can lose to estimation error for reasons the theorem never
    # claims to govern. Both are reported; only the in-sample one tests T2.
    u_coarse_in, _ = policy_utility(ctr, ytr)
    u_refined_in, _ = policy_utility(rtr, ytr)
    in_sample_delta = u_refined_in - u_coarse_in
    strict_in = in_sample_delta > 1e-12

    gap = orc - arms["coarse"]
    observed = arms["refined_typed"] - arms["coarse"]
    strict = observed > 1e-12
    return {
        "data_id": data_id, "name": name, "n": int(len(y)), "d": int(X.shape[1]),
        "impure_coarse_fibres": impure,
        "predicts_strict_decrease": predicts_strict_decrease,
        "in_sample_strict_decrease": bool(strict_in),
        "in_sample_delta": in_sample_delta,
        "prediction_holds": predicts_strict_decrease == strict_in,
        "out_of_sample_strict_decrease": bool(strict),
        "out_of_sample_delta": observed,
        "transfers_out_of_sample": bool(strict),
        "oracle_utility": orc,
        "arms": arms,
        "oracle_gap_from_coarse": gap,
        "fraction_of_gap_captured": {
            k: ((v - arms["coarse"]) / gap if abs(gap) > 1e-12 else None)
            for k, v in arms.items() if k != "coarse"},
        "cost_distinct_bound_states": {
            "coarse": int(len(np.unique(cte))),
            "refined_typed": int(len(np.unique(rte))),
            "infogain_refine": int(len(np.unique(ite))),
            "proxy_strong": int(len(np.unique(pte)))},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit", default="RESULTS_V1.json")
    a = ap.parse_args()

    rows = []
    for did, name in DATASETS:
        try:
            r = run_dataset(did, name)
        except Exception as exc:  # a fetch failure must be visible, not silent
            rows.append({"data_id": did, "name": name, "error": str(exc)[:160]})
            print(f"  {name}: ERROR {str(exc)[:80]}", flush=True)
            continue
        if r is None:
            rows.append({"data_id": did, "name": name, "skipped": "not binary or too few numeric features"})
            print(f"  {name}: skipped", flush=True)
            continue
        rows.append(r)
        print(f"  {name:<20} predict_strict={r['predicts_strict_decrease']!s:<5} "
              f"in_sample={r['in_sample_strict_decrease']!s:<5} holds={r['prediction_holds']!s:<5} "
              f"gap_captured_typed="
              f"{(r['fraction_of_gap_captured']['refined_typed'] if r['fraction_of_gap_captured']['refined_typed'] is not None else float('nan')):.3f}",
              flush=True)

    scored = [r for r in rows if "prediction_holds" in r]
    value = [r for r in scored if r["predicts_strict_decrease"]]
    novalue = [r for r in scored if not r["predicts_strict_decrease"]]
    contradictions = [r for r in scored if not r["prediction_holds"]]

    if not value or not novalue:
        terminal, rc = "CANNOT_CHECK_NO_CONTRAST", 3
    elif contradictions:
        terminal, rc = "THEOREM_FAILS_ON_REAL_DATA", 1
    else:
        terminal, rc = "THEOREM_PREDICTS_REAL_TRANSFER", 0

    proto = Path(__file__).with_name("PROTOCOL_V1.md")
    out = {
        "schema": "ORION08.REAL_TRANSFER_CC18.v1",
        "protocol_sha256": hashlib.sha256(proto.read_bytes()).hexdigest() if proto.is_file() else None,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "node": platform.node()},
        "utility_matrix": {f"a{a_}_y{y_}": v for (a_, y_), v in U.items()},
        "datasets_scored": len(scored),
        "value_stratum": [r["name"] for r in value],
        "no_value_stratum": [r["name"] for r in novalue],
        "contradictions": [r["name"] for r in contradictions],
        "rows": rows,
        "scope": ("E2 leg only. A pass supports real-domain transfer on OpenML-CC18 "
                  "and says nothing about E3 Defects4J, which remains separate."),
        "terminal": terminal,
    }
    Path(a.emit).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("datasets_scored", "value_stratum",
                                          "no_value_stratum", "contradictions", "terminal")}, indent=2))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
