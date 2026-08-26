#!/usr/bin/env python3
"""Execute the prospectively frozen P9 real accessibility scaling V1 study."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.datasets import load_breast_cancer, load_digits, load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P9_REAL_ACCESSIBILITY_SCALING_PROTOCOL_V1.md"

DATASETS = (
    ("breast_cancer", load_breast_cancer),
    ("wine", load_wine),
    ("digits", load_digits),
)
REPRESENTATIONS = ("NATIVE", "CUBIC", "REPAIRED", "LOSSY")
MODELS = ("LINEAR", "FOREST_20", "FOREST_200")


def represent(z: np.ndarray, name: str) -> tuple[np.ndarray, int]:
    if name == "NATIVE":
        return z.copy(), 0
    cubic = z ** 3
    if name == "CUBIC":
        return cubic, z.size * 2  # two multiplications per scalar as a transparent proxy
    if name == "REPAIRED":
        repaired = np.cbrt(cubic)
        return repaired, z.size * 3  # cubic proxy plus one inverse-transform op
    if name == "LOSSY":
        lossy = cubic.copy()
        lossy[:, 1::2] = 0.0
        return lossy, z.size * 2 + lossy[:, 1::2].size
    raise ValueError(name)


def make_model(name: str, seed: int):
    if name == "LINEAR":
        return LogisticRegression(C=1.0, max_iter=5000, solver="lbfgs", random_state=seed)
    if name == "FOREST_20":
        return RandomForestClassifier(
            n_estimators=20,
            max_depth=6,
            min_samples_leaf=2,
            n_jobs=1,
            random_state=seed,
        )
    if name == "FOREST_200":
        return RandomForestClassifier(
            n_estimators=200,
            max_depth=6,
            min_samples_leaf=2,
            n_jobs=1,
            random_state=seed,
        )
    raise ValueError(name)


def model_resource(model, name: str) -> dict:
    if name == "LINEAR":
        return {
            "coefficient_count": int(model.coef_.size + model.intercept_.size),
            "iterations": int(np.sum(model.n_iter_)),
        }
    node_counts = [int(est.tree_.node_count) for est in model.estimators_]
    depths = [int(est.tree_.max_depth) for est in model.estimators_]
    return {
        "tree_count": len(model.estimators_),
        "total_node_count": int(sum(node_counts)),
        "mean_max_depth": float(np.mean(depths)),
    }


def mean(xs: list[float]) -> float:
    return float(sum(xs) / len(xs))


def main() -> int:
    rows = []
    reconstruction = []

    for dataset_index, (dataset_name, loader) in enumerate(DATASETS):
        bunch = loader()
        x = np.asarray(bunch.data, dtype=np.float64)
        y = np.asarray(bunch.target)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260823 + dataset_index)

        for fold_index, (train_idx, test_idx) in enumerate(cv.split(x, y)):
            scaler = StandardScaler().fit(x[train_idx])
            z_train = scaler.transform(x[train_idx])
            z_test = scaler.transform(x[test_idx])

            cubic_train, _ = represent(z_train, "CUBIC")
            cubic_test, _ = represent(z_test, "CUBIC")
            repaired_train, _ = represent(z_train, "REPAIRED")
            repaired_test, _ = represent(z_test, "REPAIRED")
            max_err = max(
                float(np.max(np.abs(repaired_train - z_train))),
                float(np.max(np.abs(repaired_test - z_test))),
            )
            reconstruction.append({"dataset": dataset_name, "fold": fold_index, "max_abs_error": max_err})
            assert max_err <= 1e-10, (dataset_name, fold_index, max_err)

            seed = 2026082300 + dataset_index * 100 + fold_index
            for representation in REPRESENTATIONS:
                x_train_rep, train_transform_ops = represent(z_train, representation)
                x_test_rep, test_transform_ops = represent(z_test, representation)
                for model_name in MODELS:
                    model = make_model(model_name, seed)
                    model.fit(x_train_rep, y[train_idx])
                    pred = model.predict(x_test_rep)
                    rows.append({
                        "dataset": dataset_name,
                        "fold": fold_index,
                        "representation": representation,
                        "model": model_name,
                        "accuracy": float(accuracy_score(y[test_idx], pred)),
                        "feature_count": int(x.shape[1]),
                        "train_examples": int(len(train_idx)),
                        "test_examples": int(len(test_idx)),
                        "train_transform_ops": int(train_transform_ops),
                        "test_transform_ops": int(test_transform_ops),
                        "model_resource": model_resource(model, model_name),
                    })

    by = defaultdict(list)
    for row in rows:
        by[(row["dataset"], row["representation"], row["model"])].append(row["accuracy"])

    summaries = {}
    datasets_with_gap = []
    repair_ok = True
    for dataset_name, _ in DATASETS:
        native_linear = by[(dataset_name, "NATIVE", "LINEAR")]
        cubic_linear = by[(dataset_name, "CUBIC", "LINEAR")]
        repaired_linear = by[(dataset_name, "REPAIRED", "LINEAR")]
        native_f20 = by[(dataset_name, "NATIVE", "FOREST_20")]
        cubic_f20 = by[(dataset_name, "CUBIC", "FOREST_20")]
        native_f200 = by[(dataset_name, "NATIVE", "FOREST_200")]
        cubic_f200 = by[(dataset_name, "CUBIC", "FOREST_200")]

        linear_fold_gaps = [a - b for a, b in zip(native_linear, cubic_linear)]
        repair_fold_residuals = [a - b for a, b in zip(native_linear, repaired_linear)]
        gap = mean(linear_fold_gaps)
        repair_residual = mean(repair_fold_residuals)
        if gap >= 0.02:
            datasets_with_gap.append(dataset_name)
        if gap >= 0.01:
            recovered_fraction = 1.0 if gap == 0 else 1.0 - abs(repair_residual) / abs(gap)
            if recovered_fraction < 0.90 or abs(mean(native_linear) - mean(repaired_linear)) > 0.01:
                repair_ok = False
        else:
            recovered_fraction = None

        summaries[dataset_name] = {
            "native_linear_mean": mean(native_linear),
            "cubic_linear_mean": mean(cubic_linear),
            "repaired_linear_mean": mean(repaired_linear),
            "linear_access_gap_mean": gap,
            "linear_access_gap_folds": linear_fold_gaps,
            "repair_residual_mean": repair_residual,
            "repair_recovered_fraction": recovered_fraction,
            "forest20_representation_gap": mean([a - b for a, b in zip(native_f20, cubic_f20)]),
            "forest200_representation_gap": mean([a - b for a, b in zip(native_f200, cubic_f200)]),
            "capacity_gain_on_cubic_f200_vs_linear": mean(cubic_f200) - mean(cubic_linear),
            "lossy": {
                model: mean(by[(dataset_name, "LOSSY", model)]) for model in MODELS
            },
        }

    same_information_valid = all(r["max_abs_error"] <= 1e-10 for r in reconstruction)
    accessibility_positive = bool(datasets_with_gap)
    combined = same_information_valid and accessibility_positive and repair_ok

    receipt = {
        "protocol": "P9_REAL_ACCESSIBILITY_SCALING_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "environment": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "row_count": len(rows),
        "reconstruction": reconstruction,
        "summaries": summaries,
        "same_information_valid": same_information_valid,
        "datasets_with_preregistered_gap": datasets_with_gap,
        "accessibility_positive": accessibility_positive,
        "repair_positive": repair_ok,
        "terminal": (
            "P9_REAL_ACCESSIBILITY_SCALING_V1_SUPPORTED"
            if combined
            else "P9_REAL_ACCESSIBILITY_SCALING_V1_GATE_NOT_MET"
        ),
        "rows": rows,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
