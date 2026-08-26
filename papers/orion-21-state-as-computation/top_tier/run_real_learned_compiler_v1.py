#!/usr/bin/env python3
"""Execute the prospectively frozen P11 real learned-compiler study."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.datasets import load_breast_cancer, load_digits, load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_REAL_LEARNED_COMPILER_PROTOCOL_V1.md"

DATASETS = (
    ("breast_cancer", load_breast_cancer, 15),
    ("wine", load_wine, 7),
    ("digits", load_digits, 32),
)
ARMS = ("UNIVERSAL_LINEAR", "COMPILED_LINEAR", "UNIVERSAL_FOREST", "COMPILED_FOREST")


def make_model(arm: str, seed: int):
    if arm.endswith("LINEAR"):
        return LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000, random_state=seed)
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        n_jobs=1,
        random_state=seed,
    )


def model_resource(model, arm: str) -> dict:
    if arm.endswith("LINEAR"):
        return {
            "coefficient_count": int(model.coef_.size + model.intercept_.size),
            "iterations": int(np.sum(model.n_iter_)),
        }
    return {
        "tree_count": len(model.estimators_),
        "total_node_count": int(sum(t.tree_.node_count for t in model.estimators_)),
        "mean_max_depth": float(np.mean([t.tree_.max_depth for t in model.estimators_])),
    }


def mean(values):
    return float(np.mean(np.asarray(values, dtype=np.float64)))


def main() -> int:
    rows = []
    selections = []

    for dataset_index, (dataset_name, loader, k) in enumerate(DATASETS):
        bunch = loader()
        x = np.asarray(bunch.data, dtype=np.float64)
        y = np.asarray(bunch.target)
        classes = np.unique(y)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20261101 + dataset_index)

        for fold_index, (train_idx, test_idx) in enumerate(cv.split(x, y)):
            scaler = StandardScaler().fit(x[train_idx])
            train_full = scaler.transform(x[train_idx])
            test_full = scaler.transform(x[test_idx])

            compiler = SelectKBest(score_func=f_classif, k=k).fit(train_full, y[train_idx])
            selected = np.flatnonzero(compiler.get_support()).tolist()
            assert len(selected) == k
            train_compiled = compiler.transform(train_full)
            test_compiled = compiler.transform(test_full)
            assert train_compiled.shape[1] == test_compiled.shape[1] == k
            selections.append({
                "dataset": dataset_name,
                "fold": fold_index,
                "selected_features": selected,
                "compiler_fit_proxy": int(len(train_idx) * x.shape[1]),
                "compiler_inference_proxy_test": int(len(test_idx) * x.shape[1]),
            })

            seed = 2026110100 + dataset_index * 100 + fold_index
            for arm in ARMS:
                compiled = arm.startswith("COMPILED")
                train = train_compiled if compiled else train_full
                test = test_compiled if compiled else test_full
                model = make_model(arm, seed)
                model.fit(train, y[train_idx])
                pred = model.predict(test)
                recalls = recall_score(
                    y[test_idx], pred, labels=classes, average=None, zero_division=0
                )
                rows.append({
                    "dataset": dataset_name,
                    "fold": fold_index,
                    "arm": arm,
                    "accuracy": float(accuracy_score(y[test_idx], pred)),
                    "per_class_recall": {str(int(c)): float(r) for c, r in zip(classes, recalls)},
                    "state_dimension": int(test.shape[1]),
                    "state_float_count_test": int(test.size),
                    "model_resource": model_resource(model, arm),
                })

    by = defaultdict(list)
    for row in rows:
        by[(row["dataset"], row["arm"])].append(row)

    summaries = {}
    positive_datasets = []
    for dataset_name, _, k in DATASETS:
        ul = by[(dataset_name, "UNIVERSAL_LINEAR")]
        cl = by[(dataset_name, "COMPILED_LINEAR")]
        uf = by[(dataset_name, "UNIVERSAL_FOREST")]
        cf = by[(dataset_name, "COMPILED_FOREST")]

        ul_acc = [r["accuracy"] for r in ul]
        cl_acc = [r["accuracy"] for r in cl]
        linear_delta = mean(cl_acc) - mean(ul_acc)
        universal_dim = ul[0]["state_dimension"]
        compiled_dim = cl[0]["state_dimension"]
        universal_coef = mean([r["model_resource"]["coefficient_count"] for r in ul])
        compiled_coef = mean([r["model_resource"]["coefficient_count"] for r in cl])

        positive = (
            mean(cl_acc) >= mean(ul_acc) - 0.02
            and compiled_dim <= 0.6 * universal_dim
            and compiled_coef <= 0.65 * universal_coef
        )
        if positive:
            positive_datasets.append(dataset_name)

        summaries[dataset_name] = {
            "k": k,
            "universal_dimension": universal_dim,
            "compiled_dimension": compiled_dim,
            "state_dimension_ratio": compiled_dim / universal_dim,
            "universal_linear_accuracy_folds": ul_acc,
            "compiled_linear_accuracy_folds": cl_acc,
            "universal_linear_mean": mean(ul_acc),
            "compiled_linear_mean": mean(cl_acc),
            "compiled_minus_universal_linear": linear_delta,
            "universal_linear_coefficient_count_mean": universal_coef,
            "compiled_linear_coefficient_count_mean": compiled_coef,
            "coefficient_ratio": compiled_coef / universal_coef,
            "universal_forest_mean": mean([r["accuracy"] for r in uf]),
            "compiled_forest_mean": mean([r["accuracy"] for r in cf]),
            "compiled_minus_universal_forest": mean([r["accuracy"] for r in cf]) - mean([r["accuracy"] for r in uf]),
            "universal_forest_nodes_mean": mean([r["model_resource"]["total_node_count"] for r in uf]),
            "compiled_forest_nodes_mean": mean([r["model_resource"]["total_node_count"] for r in cf]),
            "positive_dataset": positive,
        }

    supported = len(positive_datasets) >= 2
    receipt = {
        "protocol": "P11_REAL_LEARNED_COMPILER_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "environment": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "row_count": len(rows),
        "selections": selections,
        "summaries": summaries,
        "positive_datasets": positive_datasets,
        "positive_dataset_count": len(positive_datasets),
        "terminal": (
            "P11_REAL_LEARNED_COMPILER_V1_SUPPORTED"
            if supported
            else "P11_REAL_LEARNED_COMPILER_V1_GATE_NOT_MET"
        ),
        "rows": rows,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
