#!/usr/bin/env python3
"""NR-04 stage-1 attribution: where does D-A quality drop in transport?

Three measurements, one per candidate stage:

  A. representation-repair channel fidelity -- is cbrt(x^3) decision-identical
     to the native standardized representation under the frozen access class?
  B. evaluation-channel noise -- what is the sampling sd of the transported
     single-split accuracy vs the decision margin |pooled level - target|?
  C. split-realization divergence -- probe vs protected as two draws from the
     same channel (empirical re-draw distribution).

Read-only w.r.t. frozen artifacts; prints JSON only.
"""

from __future__ import annotations

import hashlib
import json
import platform

import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

TARGET = 0.965
R_DRAWS = 200  # attribution measurement only; V2 protocol constants are separate


def logistic(seed: int) -> LogisticRegression:
    return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)


def main() -> int:
    b = load_digits()
    X = np.asarray(b.data, dtype=np.float64)
    y = np.asarray(b.target, dtype=int)
    Xtr, Xrem, ytr, yrem = train_test_split(
        X, y, test_size=0.4, random_state=20260901, stratify=y
    )
    Xpr, Xte, ypr, yte = train_test_split(
        Xrem, yrem, test_size=0.5, random_state=20260902, stratify=yrem
    )
    sc = StandardScaler().fit(Xtr)
    ntr, npr, nte = sc.transform(Xtr), sc.transform(Xpr), sc.transform(Xte)

    # --- A. repair-channel fidelity -------------------------------------
    rep_tr, rep_pr, rep_te = np.cbrt(ntr**3), np.cbrt(npr**3), np.cbrt(nte**3)
    max_abs_err = float(np.max(np.abs(rep_tr - ntr)))
    rel_err = float(np.max(np.abs(rep_tr - ntr) / np.maximum(np.abs(ntr), 1e-300)))
    m_rep = logistic(902).fit(rep_tr, ytr)
    m_nat = logistic(902).fit(ntr, ytr)
    acc_rep_pr = accuracy_score(ypr, m_rep.predict(rep_pr))
    acc_nat_pr = accuracy_score(ypr, m_nat.predict(npr))
    acc_rep_te = accuracy_score(yte, m_rep.predict(rep_te))
    acc_nat_te = accuracy_score(yte, m_nat.predict(nte))
    coef_gap = float(np.max(np.abs(m_rep.coef_ - m_nat.coef_)))

    # --- B. evaluation-channel noise vs decision margin ------------------
    # Pooled held-out level of the repaired arm (probe+protected, 719 cases).
    pooled_correct = int(round(acc_rep_pr * len(ypr) + acc_rep_te * len(yte)))
    pooled = pooled_correct / (len(ypr) + len(yte))
    n_prot = len(yte)
    se_binom = float(np.sqrt(pooled * (1 - pooled) / n_prot))
    margin = abs(pooled - TARGET)

    # --- C. split-realization divergence --------------------------------
    rng_free = [20260901]  # frozen draw kept; extra draws are measurement only
    accs = []
    for k in range(R_DRAWS):
        Xtr_k, Xrem_k, ytr_k, yrem_k = train_test_split(
            X, y, test_size=0.4, random_state=100000 + k, stratify=y
        )
        Xpr_k, Xte_k, ypr_k, yte_k = train_test_split(
            Xrem_k, yrem_k, test_size=0.5, random_state=200000 + k, stratify=yrem_k
        )
        sc_k = StandardScaler().fit(Xtr_k)
        ctr_k = sc_k.transform(Xtr_k) ** 3
        mk = logistic(902).fit(np.cbrt(ctr_k), ytr_k)
        accs.append(
            accuracy_score(yte_k, mk.predict(np.cbrt(sc_k.transform(Xte_k) ** 3)))
        )
    accs = np.asarray(accs)
    cross_above = float(np.mean(accs >= TARGET))

    out = {
        "schema": "orion.p9.nr04-stage1-attribution.v1",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "digits_label_sha256": hashlib.sha256(y.tobytes()).hexdigest(),
        "A_repair_channel": {
            "max_abs_reconstruction_error": max_abs_err,
            "max_rel_reconstruction_error": rel_err,
            "probe_accuracy_repaired_rep": float(acc_rep_pr),
            "probe_accuracy_native_rep": float(acc_nat_pr),
            "protected_accuracy_repaired_rep": float(acc_rep_te),
            "protected_accuracy_native_rep": float(acc_nat_te),
            "decision_identical_probe": bool(acc_rep_pr == acc_nat_pr),
            "decision_identical_protected": bool(acc_rep_te == acc_nat_te),
            "max_coef_gap_repaired_vs_native": coef_gap,
        },
        "B_evaluation_channel": {
            "probe_accuracy": float(acc_rep_pr),
            "protected_accuracy": float(acc_rep_te),
            "pooled_heldout_level": pooled,
            "pooled_correct": pooled_correct,
            "pooled_n": len(ypr) + len(yte),
            "protected_n": n_prot,
            "binomial_sd_single_split": se_binom,
            "decision_margin_abs_level_minus_target": margin,
            "noise_to_margin_ratio": se_binom / margin if margin > 0 else None,
            "frozen_target": TARGET,
        },
        "C_split_realization": {
            "n_resample_draws": R_DRAWS,
            "frozen_draw_seed_included": rng_free,
            "redraw_mean": float(accs.mean()),
            "redraw_sd": float(accs.std(ddof=1)),
            "redraw_min": float(accs.min()),
            "redraw_max": float(accs.max()),
            "fraction_of_draws_at_or_above_target": cross_above,
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
