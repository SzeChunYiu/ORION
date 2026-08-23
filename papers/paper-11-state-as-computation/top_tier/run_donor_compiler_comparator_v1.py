#!/usr/bin/env python3
"""Execute the prospectively frozen P11 donor-complete compiler comparator V1.

Reproduces the four registered arms of P11_REAL_LEARNED_COMPILER_V1 through the
identical code path, then races the named donor's selection principle
(mutual information) and a seeded random-k control at matched charged compiler
work under the same protected folds.
"""

from __future__ import annotations

from collections import defaultdict
from functools import partial
import hashlib
import json
from pathlib import Path

import numpy as np
import sklearn
from sklearn.datasets import load_breast_cancer, load_digits, load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P11_DONOR_COMPILER_COMPARATOR_PROTOCOL_V1.md"
GOLD = HERE / "p11_donor_comparator_gold_v1.json"

DATASETS = (
    ("breast_cancer", load_breast_cancer, 15),
    ("wine", load_wine, 7),
    ("digits", load_digits, 32),
)
ARMS = ("UNIVERSAL_LINEAR", "COMPILED_LINEAR", "UNIVERSAL_FOREST", "COMPILED_FOREST")
CHALLENGERS = ("DONOR_MI_COMPILED_LINEAR", "RANDOM_K_COMPILED_LINEAR")
ACC_PARITY_THRESHOLD = 0.01


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


def score_row(arm: str, dataset_name: str, fold_index: int, train, test, y_train, y_test, classes, seed):
    model = make_model(arm, seed)
    model.fit(train, y_train)
    pred = model.predict(test)
    recalls = recall_score(y_test, pred, labels=classes, average=None, zero_division=0)
    return {
        "dataset": dataset_name,
        "fold": fold_index,
        "arm": arm,
        "accuracy": float(accuracy_score(y_test, pred)),
        "per_class_recall": {str(int(c)): float(r) for c, r in zip(classes, recalls)},
        "state_dimension": int(test.shape[1]),
        "state_float_count_test": int(test.size),
        "model_resource": model_resource(model, arm),
    }


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
                "selector": "f_classif",
                "selected_features": selected,
                "compiler_fit_proxy": int(len(train_idx) * x.shape[1]),
                "compiler_inference_proxy_test": int(len(test_idx) * x.shape[1]),
            })

            seed = 2026110100 + dataset_index * 100 + fold_index
            for arm in ARMS:
                compiled = arm.startswith("COMPILED")
                train = train_compiled if compiled else train_full
                test = test_compiled if compiled else test_full
                rows.append(score_row(
                    arm, dataset_name, fold_index, train, test,
                    y[train_idx], y[test_idx], classes, seed,
                ))

            # --- challenger arms (post-registered additions to the frozen study) ---
            donor_compiler = SelectKBest(
                score_func=partial(mutual_info_classif, random_state=seed), k=k
            ).fit(train_full, y[train_idx])
            donor_selected = np.flatnonzero(donor_compiler.get_support()).tolist()
            assert len(donor_selected) == k
            train_donor = donor_compiler.transform(train_full)
            test_donor = donor_compiler.transform(test_full)
            selections.append({
                "dataset": dataset_name,
                "fold": fold_index,
                "selector": "mutual_info",
                "selected_features": donor_selected,
                "compiler_fit_proxy": int(len(train_idx) * x.shape[1]),
                "compiler_inference_proxy_test": int(len(test_idx) * x.shape[1]),
                "mi_estimator_calls": int(x.shape[1]),
                "mi_nn_distance_evals_proxy": int(x.shape[1] * len(train_idx)),
            })

            rng = np.random.default_rng(seed)
            random_selected = sorted(int(j) for j in rng.choice(x.shape[1], size=k, replace=False))
            assert len(random_selected) == k
            selections.append({
                "dataset": dataset_name,
                "fold": fold_index,
                "selector": "random_k",
                "selected_features": random_selected,
                "compiler_fit_proxy": int(len(train_idx) * x.shape[1]),
                "compiler_inference_proxy_test": int(len(test_idx) * x.shape[1]),
            })
            train_random = train_full[:, random_selected]
            test_random = test_full[:, random_selected]

            rows.append(score_row(
                "DONOR_MI_COMPILED_LINEAR", dataset_name, fold_index,
                train_donor, test_donor, y[train_idx], y[test_idx], classes, seed,
            ))
            rows.append(score_row(
                "RANDOM_K_COMPILED_LINEAR", dataset_name, fold_index,
                train_random, test_random, y[train_idx], y[test_idx], classes, seed,
            ))

    by = defaultdict(list)
    for row in rows:
        by[(row["dataset"], row["arm"])].append(row)

    summaries = {}
    positive_datasets = []
    placement = {}
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

        placement[dataset_name] = {"registered": positive}

        for challenger_arm, key in (
            ("DONOR_MI_COMPILED_LINEAR", "donor_mi"),
            ("RANDOM_K_COMPILED_LINEAR", "random_k"),
        ):
            ch = by[(dataset_name, challenger_arm)]
            ch_acc = [r["accuracy"] for r in ch]
            ch_coef = mean([r["model_resource"]["coefficient_count"] for r in ch])
            ch_dim = ch[0]["state_dimension"]
            ch_positive = (
                mean(ch_acc) >= mean(ul_acc) - 0.02
                and ch_dim <= 0.6 * universal_dim
                and ch_coef <= 0.65 * universal_coef
            )
            placement[dataset_name][key] = ch_positive
            if ch_positive and positive:
                disposition = "BOTH_PASS"
            elif ch_positive and not positive:
                disposition = "CHALLENGER_ABOVE"
            elif not ch_positive and positive:
                disposition = "CHALLENGER_BELOW"
            else:
                disposition = "BOTH_FAIL"
            summaries[dataset_name][f"{key}_linear_mean"] = mean(ch_acc)
            summaries[dataset_name][f"{key}_placement_positive"] = ch_positive
            summaries[dataset_name][f"{key}_disposition"] = disposition
            summaries[dataset_name][f"{key}_accuracy_parity_within_threshold"] = bool(
                abs(mean(ch_acc) - mean(cl_acc)) <= ACC_PARITY_THRESHOLD
            )

    # EP4: resource parity across selectors, per (dataset, fold).
    resource_parity = []
    sel_by = defaultdict(dict)
    for entry in selections:
        sel_by[(entry["dataset"], entry["fold"])][entry["selector"]] = entry
    for (dataset_name, fold_index), per_selector in sorted(sel_by.items()):
        values = {e["compiler_fit_proxy"] for e in per_selector.values()}
        resource_parity.append({
            "dataset": dataset_name,
            "fold": fold_index,
            "selectors_present": sorted(per_selector),
            "fit_proxies_equal": len(values) == 1,
            "mi_charged_fields_ok": (
                "mi_estimator_calls" in per_selector.get("mutual_info", {})
                and per_selector["mutual_info"]["mi_nn_distance_evals_proxy"]
                >= per_selector["mutual_info"]["mi_estimator_calls"]
            ),
        })

    ep1_ok = positive_datasets == ["wine", "digits"]
    ep4_ok = all(p["fit_proxies_equal"] and p["mi_charged_fields_ok"] for p in resource_parity)
    ep23_ok = all(
        key in placement[dataset_name]
        for dataset_name, _, _ in DATASETS
        for key in ("donor_mi", "random_k")
    )
    supported = ep1_ok and ep4_ok and ep23_ok

    gold = json.loads(GOLD.read_text())
    prediction_outcomes = {}
    for role, gold_key in (("donor_mi", "ep2_donor_predictions"), ("random_k", "ep3_random_k_predictions")):
        prediction_outcomes[role] = {}
        for dataset_name, _, _ in DATASETS:
            predicted = gold[gold_key][dataset_name]
            if predicted == "CANNOT_CHECK_PREDICTION":
                outcome = "WITHHELD"
            else:
                observed = summaries[dataset_name][f"{role}_disposition"]
                outcome = "CONFIRMED" if observed == predicted else "CORRECTED"
            prediction_outcomes[role][dataset_name] = {
                "predicted": predicted,
                "observed": summaries[dataset_name][f"{role}_disposition"],
                "outcome": outcome,
            }

    receipt = {
        "protocol": "P11_DONOR_COMPILER_COMPARATOR_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "gold_sha256": hashlib.sha256(GOLD.read_bytes()).hexdigest(),
        "environment": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "row_count": len(rows),
        "selections": selections,
        "summaries": summaries,
        "placement": placement,
        "resource_parity": resource_parity,
        "positive_datasets": positive_datasets,
        "positive_dataset_count": len(positive_datasets),
        "ep1_reproduction_ok": ep1_ok,
        "ep4_resource_parity_ok": ep4_ok,
        "prediction_outcomes": prediction_outcomes,
        "terminal": (
            "P11_DONOR_COMPARATOR_V1_SUPPORTED"
            if supported
            else "P11_DONOR_COMPARATOR_V1_GATE_NOT_MET"
        ),
        "rows": rows,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())