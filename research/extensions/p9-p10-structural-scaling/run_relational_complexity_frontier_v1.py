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
OUT = HERE / "results" / "RELATIONAL_COMPLEXITY_FRONTIER_V1.json"
K_GRID = (3, 5, 9, 17, 33)
N_GRID = (64, 128, 256, 512, 1024, 2048, 4096)
N_TEST = 16384
TARGET = 0.90


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


def fit_score(xtr: np.ndarray, ytr: np.ndarray, xte: np.ndarray, yte: np.ndarray) -> float:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(xtr, ytr)
    return float(model.score(xte, yte))


def threshold(rows: list[dict[str, Any]], key: str) -> int | None:
    for row in rows:
        if float(row[key]) >= TARGET:
            return int(row["n_train"])
    return None


def main() -> None:
    cells: list[dict[str, Any]] = []
    for k in K_GRID:
        train_seed = 9_100_001 + 70_001 * k
        test_seed = 9_200_003 + 90_001 * k
        x_all, c_all, y_all = sample(k, max(N_GRID), train_seed)
        xte, cte, yte = sample(k, N_TEST, test_seed)
        fte = flat(xte, cte)
        rte = relational(xte, cte)
        poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
        # Fitting the transformer is outcome-independent; dimensions depend only on k.
        poly.fit(flat(x_all[:1], c_all[:1]))
        fte2 = poly.transform(fte)
        recon_failures = int(np.count_nonzero(x_all * (x_all * c_all) != c_all))
        recon_failures += int(np.count_nonzero(xte * (xte * cte) != cte))
        rows: list[dict[str, Any]] = []
        for n in N_GRID:
            xtr, ctr, ytr = x_all[:n], c_all[:n], y_all[:n]
            ftr = flat(xtr, ctr)
            rtr = relational(xtr, ctr)
            ftr2 = poly.transform(ftr)
            rows.append({
                "n_train": n,
                "flat_linear_accuracy": fit_score(ftr, ytr, fte, yte),
                "flat_quadratic_accuracy": fit_score(ftr2, ytr, fte2, yte),
                "relational_linear_accuracy": fit_score(rtr, ytr, rte, yte),
            })
        rel_n = threshold(rows, "relational_linear_accuracy")
        quad_n = threshold(rows, "flat_quadratic_accuracy")
        cells.append({
            "k": k,
            "train_seed": train_seed,
            "test_seed": test_seed,
            "reconstruction_failure_count": recon_failures,
            "feature_dimensions": {
                "flat_linear": int(2 * k),
                "flat_quadratic": int(poly.n_output_features_),
                "relational_linear": int(2 * k),
            },
            "accuracy_curve": rows,
            "sample_threshold_0_90": {
                "flat_linear": threshold(rows, "flat_linear_accuracy"),
                "flat_quadratic": quad_n,
                "relational_linear": rel_n,
            },
            "quadratic_to_relational_threshold_ratio": (
                float(quad_n / rel_n) if quad_n is not None and rel_n is not None else None
            ),
        })

    at_4096 = [cell["accuracy_curve"][-1] for cell in cells]
    ratios = [
        float(cell["quadratic_to_relational_threshold_ratio"])
        for cell in cells
        if cell["quadratic_to_relational_threshold_ratio"] is not None
    ]
    quadratic_reached = sum(cell["sample_threshold_0_90"]["flat_quadratic"] is not None for cell in cells)
    dims = [cell["feature_dimensions"] for cell in cells]
    dim_growth = {
        "flat_quadratic_first": dims[0]["flat_quadratic"],
        "flat_quadratic_last": dims[-1]["flat_quadratic"],
        "relational_first": dims[0]["relational_linear"],
        "relational_last": dims[-1]["relational_linear"],
        "quadratic_growth_factor": dims[-1]["flat_quadratic"] / dims[0]["flat_quadratic"],
        "relational_growth_factor": dims[-1]["relational_linear"] / dims[0]["relational_linear"],
    }
    checks = {
        "relational_ge_0_95_all_at_4096": all(row["relational_linear_accuracy"] >= 0.95 for row in at_4096),
        "flat_linear_le_0_65_all_at_4096": all(row["flat_linear_accuracy"] <= 0.65 for row in at_4096),
        "quadratic_reaches_0_90_at_least_four_dimensions": quadratic_reached >= 4,
        "median_threshold_ratio_ge_2": bool(ratios) and float(np.median(ratios)) >= 2.0,
        "reconstruction_zero_all": all(cell["reconstruction_failure_count"] == 0 for cell in cells),
        "quadratic_feature_growth_faster": dim_growth["quadratic_growth_factor"] > dim_growth["relational_growth_factor"],
    }
    terminal = (
        "RELATIONAL_CAPACITY_FRONTIER_SUPPORTED_CONTROLLED_CLASS"
        if all(checks.values())
        else "RELATIONAL_CAPACITY_FRONTIER_GATE_NOT_MET"
    )
    result = {
        "schema": "P9P10.RelationalComplexityFrontier.v1",
        "protocol": "NOVELTY_EXPANSION_PROTOCOL_V3.md#experiment-a--representation--relational-complexity-capacity-frontier",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "k_grid": list(K_GRID),
        "n_train_grid": list(N_GRID),
        "n_test": N_TEST,
        "target_accuracy": TARGET,
        "cells": cells,
        "aggregate": {
            "quadratic_dimensions_reaching_target": quadratic_reached,
            "threshold_ratios": ratios,
            "median_quadratic_to_relational_threshold_ratio": float(np.median(ratios)) if ratios else None,
            "feature_dimension_growth": dim_growth,
            "checks": checks,
        },
        "terminal": terminal,
        "claim_boundary": "Restricted controlled-class capacity/sample frontier under bijective information-equivalent encodings; not an LLM scaling law.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
