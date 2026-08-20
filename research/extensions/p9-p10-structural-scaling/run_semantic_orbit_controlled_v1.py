from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "SEMANTIC_ORBIT_CONTROLLED_V1.json"
K_GRID = (9, 17, 33)
N_TRAIN = 1024
N_TEST = 4096
N_ORBIT = 32


def sample(k: int, n: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.choice(np.array([-1.0, 1.0]), size=(n, k), replace=True)
    c = rng.choice(np.array([-1.0, 1.0]), size=(n, k), replace=True)
    y = (np.sum(x * c, axis=1) > 0).astype(np.int64)
    return x, c, y


def flat(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, c), axis=1)


def relational(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, x * c), axis=1)


def fit_model(x: np.ndarray, y: np.ndarray) -> LogisticRegression:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(x, y)
    return model


def orbit_metrics(preds: np.ndarray, y: np.ndarray, canonical: np.ndarray) -> dict[str, float]:
    # preds shape: orbit x n_items, binary labels.
    ones = np.sum(preds == 1, axis=0)
    zeros = preds.shape[0] - ones
    oir = 1.0 - np.maximum(ones, zeros) / preds.shape[0]
    any_change = np.any(preds != preds[0:1], axis=0)
    return {
        "mean_orbit_accuracy": float(np.mean(preds == y[None, :])),
        "mean_oir": float(np.mean(oir)),
        "p95_oir": float(np.quantile(oir, 0.95)),
        "fraction_items_any_prediction_change": float(np.mean(any_change)),
        "fraction_orbit_predictions_different_from_canonical": float(np.mean(preds != canonical[None, :])),
    }


def main() -> None:
    cells: list[dict[str, Any]] = []
    for k in K_GRID:
        train_seed = 11_100_001 + 130_003 * k
        test_seed = 11_200_003 + 150_001 * k
        orbit_seed = 11_300_007 + 170_003 * k
        xtr, ctr, ytr = sample(k, N_TRAIN, train_seed)
        xte, cte, yte = sample(k, N_TEST, test_seed)

        poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
        ftr = flat(xtr, ctr)
        fte = flat(xte, cte)
        poly.fit(ftr[:1])
        flat_model = fit_model(poly.transform(ftr), ytr)
        rel_model = fit_model(relational(xtr, ctr), ytr)

        flat_canonical = flat_model.predict(poly.transform(fte))
        rel_canonical = rel_model.predict(relational(xte, cte))
        flat_canonical_acc = float(np.mean(flat_canonical == yte))
        rel_canonical_acc = float(np.mean(rel_canonical == yte))

        rng = np.random.default_rng(orbit_seed)
        flat_preds: list[np.ndarray] = []
        rel_preds: list[np.ndarray] = []
        transformations: list[dict[str, Any]] = []
        preservation_failures = 0
        for j in range(N_ORBIT):
            perm = rng.permutation(k)
            signs = rng.choice(np.array([-1.0, 1.0]), size=k, replace=True)
            xt = xte[:, perm] * signs
            ct = cte[:, perm] * signs
            yt = (np.sum(xt * ct, axis=1) > 0).astype(np.int64)
            failures = int(np.count_nonzero(yt != yte))
            preservation_failures += failures
            flat_preds.append(flat_model.predict(poly.transform(flat(xt, ct))))
            rel_preds.append(rel_model.predict(relational(xt, ct)))
            transformations.append({
                "index": j,
                "permutation": [int(v) for v in perm.tolist()],
                "negative_sign_count": int(np.count_nonzero(signs < 0)),
                "target_preservation_failures": failures,
            })

        flat_matrix = np.stack(flat_preds, axis=0)
        rel_matrix = np.stack(rel_preds, axis=0)
        fm = orbit_metrics(flat_matrix, yte, flat_canonical)
        rm = orbit_metrics(rel_matrix, yte, rel_canonical)
        cells.append({
            "k": k,
            "train_seed": train_seed,
            "test_seed": test_seed,
            "orbit_seed": orbit_seed,
            "feature_dimensions": {
                "flat_quadratic": int(poly.n_output_features_),
                "relational_linear": int(2 * k),
            },
            "canonical_accuracy": {
                "flat_quadratic": flat_canonical_acc,
                "relational_linear": rel_canonical_acc,
            },
            "orbit": {
                "flat_quadratic": fm,
                "relational_linear": rm,
                "relational_oir_advantage": fm["mean_oir"] - rm["mean_oir"],
            },
            "target_preservation_failure_count": preservation_failures,
            "transformations": transformations,
        })

    comparisons = [cell["orbit"]["relational_oir_advantage"] for cell in cells]
    checks = {
        "relational_canonical_ge_0_95_all": all(cell["canonical_accuracy"]["relational_linear"] >= 0.95 for cell in cells),
        "relational_orbit_accuracy_ge_0_95_all": all(cell["orbit"]["relational_linear"]["mean_orbit_accuracy"] >= 0.95 for cell in cells),
        "relational_mean_oir_le_0_02_all": all(cell["orbit"]["relational_linear"]["mean_oir"] <= 0.02 for cell in cells),
        "relational_oir_no_worse_at_least_two_k": sum(v >= -1e-12 for v in comparisons) >= 2,
        "mean_oir_advantage_ge_0_005": float(np.mean(comparisons)) >= 0.005,
        "target_preservation_zero_all": all(cell["target_preservation_failure_count"] == 0 for cell in cells),
    }
    bounded_relational_stability = all([
        checks["relational_canonical_ge_0_95_all"],
        checks["relational_orbit_accuracy_ge_0_95_all"],
        checks["relational_mean_oir_le_0_02_all"],
        checks["target_preservation_zero_all"],
    ])
    terminal = (
        "RELATIONAL_SEMANTIC_ORBIT_STABILITY_SUPPORTED_CONTROLLED_CLASS"
        if all(checks.values())
        else "RELATIONAL_SEMANTIC_ORBIT_BOUNDED_STABILITY_ONLY"
        if bounded_relational_stability
        else "RELATIONAL_SEMANTIC_ORBIT_GATE_NOT_MET"
    )
    result = {
        "schema": "P9P10.SemanticOrbitControlled.v1",
        "protocol": "SEMANTIC_ORBIT_CONTROLLED_PROTOCOL_V1.md",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "k_grid": list(K_GRID),
        "n_train": N_TRAIN,
        "n_test": N_TEST,
        "orbit_size": N_ORBIT,
        "cells": cells,
        "aggregate": {
            "mean_relational_oir_advantage": float(np.mean(comparisons)),
            "checks": checks,
        },
        "terminal": terminal,
        "claim_boundary": "Controlled semantics-preserving signed-permutation orbit stability; not natural-language or Lean semantic-orbit evidence.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
