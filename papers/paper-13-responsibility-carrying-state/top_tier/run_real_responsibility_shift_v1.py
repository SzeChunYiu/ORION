#!/usr/bin/env python3
"""Execute prospectively frozen P13 real responsibility-shift V1 study."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P13_REAL_RESPONSIBILITY_SHIFT_PROTOCOL_V1.md"
ALPHA = 0.05
CONFIDENCE_THRESHOLD = 0.90


def logistic(seed: int) -> LogisticRegression:
    return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)


def hoeffding_upper(errors: int, n: int) -> float:
    p_hat = errors / n
    return min(1.0, p_hat + math.sqrt(math.log(1 / ALPHA) / (2 * n)))


def decide_policy(
    policy: str,
    responsibility: str,
    parity_probs: np.ndarray,
    parity_pred: int,
    compact_digit_pred: int,
    raw_digit_pred: int,
) -> tuple[int, str, int, bool]:
    """Return prediction, source, floats-read, unsupported-reuse."""
    confidence = float(np.max(parity_probs))
    if policy in ("UNQUALIFIED", "PROVENANCE_ONLY"):
        if responsibility == "R_PARITY":
            return parity_pred, "COMPACT", 2, False
        return compact_digit_pred, "COMPACT", 2, True

    if policy == "CONFIDENCE_ONLY":
        if confidence >= CONFIDENCE_THRESHOLD:
            if responsibility == "R_PARITY":
                return parity_pred, "COMPACT", 2, False
            return compact_digit_pred, "COMPACT", 2, True
        # Reopen raw. The same fitted parity compiler is run on raw for parity.
        if responsibility == "R_PARITY":
            return parity_pred, "RAW", 64, False
        return raw_digit_pred, "RAW", 64, False

    if policy == "ALWAYS_RAW":
        if responsibility == "R_PARITY":
            return parity_pred, "RAW", 64, False
        return raw_digit_pred, "RAW", 64, False

    if policy == "RCS":
        if responsibility == "R_PARITY":
            return parity_pred, "COMPACT", 2, False
        return raw_digit_pred, "RAW", 64, False

    raise ValueError(policy)


def main() -> int:
    bunch = load_digits()
    x = np.asarray(bunch.data, dtype=np.float64)
    y_digit = np.asarray(bunch.target, dtype=int)
    y_parity = y_digit % 2
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20261301)

    policies = ("UNQUALIFIED", "CONFIDENCE_ONLY", "PROVENANCE_ONLY", "ALWAYS_RAW", "RCS")
    rows = []
    fold_records = []

    for fold, (train_idx, test_idx) in enumerate(cv.split(x, y_digit)):
        scaler = StandardScaler().fit(x[train_idx])
        train = scaler.transform(x[train_idx])
        test = scaler.transform(x[test_idx])
        seed = 2026130100 + fold

        parity_model = logistic(seed).fit(train, y_parity[train_idx])
        train_probs = parity_model.predict_proba(train)
        test_probs = parity_model.predict_proba(test)
        parity_pred_test = np.argmax(test_probs, axis=1).astype(int)

        # Hostile decoder: exact digit prediction using only two compact parity probabilities.
        compact_digit_model = logistic(seed + 1000).fit(train_probs, y_digit[train_idx])
        compact_digit_pred = compact_digit_model.predict(test_probs).astype(int)

        raw_digit_model = logistic(seed + 2000).fit(train, y_digit[train_idx])
        raw_digit_pred = raw_digit_model.predict(test).astype(int)

        parity_errors = int(np.sum(parity_pred_test != y_parity[test_idx]))
        fold_records.append({
            "fold": fold,
            "test_n": int(len(test_idx)),
            "parity_errors": parity_errors,
            "parity_error_rate": parity_errors / len(test_idx),
            "parity_hoeffding_upper_alpha_0_05": hoeffding_upper(parity_errors, len(test_idx)),
            "compiler": {
                "raw_dimension": 64,
                "compact_dimension": 2,
                "parity_model_coefficient_count": int(parity_model.coef_.size + parity_model.intercept_.size),
                "compact_digit_decoder_coefficient_count": int(compact_digit_model.coef_.size + compact_digit_model.intercept_.size),
                "raw_digit_model_coefficient_count": int(raw_digit_model.coef_.size + raw_digit_model.intercept_.size),
                "initial_compact_construction_raw_float_reads": int(len(test_idx) * 64),
                "stored_compact_float_count": int(len(test_idx) * 2),
            },
        })

        for local_i, global_i in enumerate(test_idx):
            probs = test_probs[local_i]
            parity_pred = int(parity_pred_test[local_i])
            c_digit = int(compact_digit_pred[local_i])
            r_digit = int(raw_digit_pred[local_i])
            for responsibility in ("R_PARITY", "R_DIGIT"):
                gold = int(y_parity[global_i]) if responsibility == "R_PARITY" else int(y_digit[global_i])
                for policy in policies:
                    pred, source, floats, unsupported = decide_policy(
                        policy,
                        responsibility,
                        probs,
                        parity_pred,
                        c_digit,
                        r_digit,
                    )
                    rows.append({
                        "fold": fold,
                        "item_index": int(global_i),
                        "responsibility": responsibility,
                        "policy": policy,
                        "gold": gold,
                        "prediction": pred,
                        "correct": pred == gold,
                        "source": source,
                        "floats_read": floats,
                        "unsupported_reuse": unsupported,
                        "parity_confidence": float(np.max(probs)),
                    })

    def subset(policy: str, responsibility: str | None = None):
        return [r for r in rows if r["policy"] == policy and (responsibility is None or r["responsibility"] == responsibility)]

    summaries = {}
    for policy in policies:
        all_rows = subset(policy)
        summaries[policy] = {
            "combined_accuracy": float(np.mean([r["correct"] for r in all_rows])),
            "parity_accuracy": float(np.mean([r["correct"] for r in subset(policy, "R_PARITY")])),
            "digit_accuracy": float(np.mean([r["correct"] for r in subset(policy, "R_DIGIT")])),
            "unsupported_reuse_rate_on_digit": float(np.mean([r["unsupported_reuse"] for r in subset(policy, "R_DIGIT")])),
            "unsupported_reuse_count_on_digit": int(sum(r["unsupported_reuse"] for r in subset(policy, "R_DIGIT"))),
            "mean_floats_read_per_episode": float(np.mean([r["floats_read"] for r in all_rows])),
            "reopen_rate": float(np.mean([r["source"] == "RAW" for r in all_rows])),
        }

    # Fold-by-fold invariants for RCS against its exact component baselines.
    fold_checks = []
    for fold in range(5):
        def acc(policy, responsibility):
            rr = [r for r in rows if r["fold"] == fold and r["policy"] == policy and r["responsibility"] == responsibility]
            return float(np.mean([r["correct"] for r in rr]))
        fold_checks.append({
            "fold": fold,
            "rcs_digit": acc("RCS", "R_DIGIT"),
            "always_raw_digit": acc("ALWAYS_RAW", "R_DIGIT"),
            "rcs_parity": acc("RCS", "R_PARITY"),
            "unqualified_parity": acc("UNQUALIFIED", "R_PARITY"),
        })
    exact_component_equality = all(
        f["rcs_digit"] == f["always_raw_digit"] and f["rcs_parity"] == f["unqualified_parity"]
        for f in fold_checks
    )

    raw_digit_mean = summaries["ALWAYS_RAW"]["digit_accuracy"]
    compact_digit_mean = summaries["UNQUALIFIED"]["digit_accuracy"]
    responsibility_debt = raw_digit_mean - compact_digit_mean
    cost_reduction = 1.0 - summaries["RCS"]["mean_floats_read_per_episode"] / summaries["ALWAYS_RAW"]["mean_floats_read_per_episode"]

    supported = (
        summaries["RCS"]["unsupported_reuse_count_on_digit"] == 0
        and exact_component_equality
        and cost_reduction >= 0.40
        and (
            summaries["CONFIDENCE_ONLY"]["unsupported_reuse_count_on_digit"] > 0
            or summaries["PROVENANCE_ONLY"]["unsupported_reuse_count_on_digit"] > 0
        )
        and responsibility_debt >= 0.15
    )

    receipt = {
        "protocol": "P13_REAL_RESPONSIBILITY_SHIFT_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "environment": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "episode_count": len(rows),
        "fold_records": fold_records,
        "fold_component_checks": fold_checks,
        "summaries": summaries,
        "raw_minus_compact_digit_accuracy": responsibility_debt,
        "rcs_state_read_cost_reduction_vs_always_raw": cost_reduction,
        "exact_component_equality_fold_by_fold": exact_component_equality,
        "terminal": (
            "P13_REAL_RESPONSIBILITY_SHIFT_V1_SUPPORTED"
            if supported
            else "P13_REAL_RESPONSIBILITY_SHIFT_V1_GATE_NOT_MET"
        ),
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
