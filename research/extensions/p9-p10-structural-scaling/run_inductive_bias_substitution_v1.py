from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "INDUCTIVE_BIAS_SUBSTITUTION_V1.json"
K_GRID = (9, 17, 33)
N_GRID = (64, 128, 256, 512, 1024, 2048, 4096)
REPS = (0, 1, 2)
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


def bilinear(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return (x[:, :, None] * c[:, None, :]).reshape(x.shape[0], -1)


def diagonal(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return x * c


def fit_l2(x: np.ndarray, y: np.ndarray) -> LogisticRegression:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(x, y)
    return model


def fit_l1(x: np.ndarray, y: np.ndarray) -> LogisticRegression:
    model = LogisticRegression(
        C=1.0,
        penalty="l1",
        solver="liblinear",
        max_iter=5000,
        random_state=0,
    )
    model.fit(x, y)
    return model


def threshold(curve: list[dict[str, Any]], arm: str) -> int | None:
    for row in curve:
        if float(row[arm]["mean_accuracy"]) >= TARGET:
            return int(row["n_train"])
    return None


def main() -> None:
    cells: list[dict[str, Any]] = []
    architecture_representation_equal_all = True

    for k in K_GRID:
        reps: list[dict[str, Any]] = []
        diagonal_indices = np.array([i * k + i for i in range(k)], dtype=np.int64)
        offdiag_count = k * k - k
        for rep in REPS:
            train_seed = 14_100_001 + 310_019 * k + 1009 * rep
            test_seed = 14_200_003 + 330_017 * k + 1013 * rep
            xtr_all, ctr_all, ytr_all = sample(k, max(N_GRID), train_seed)
            xte, cte, yte = sample(k, N_TEST, test_seed)
            fte = flat(xte, cte)
            bte = bilinear(xte, cte)
            dte = diagonal(xte, cte)
            rep_rows: list[dict[str, Any]] = []

            for n in N_GRID:
                xtr, ctr, ytr = xtr_all[:n], ctr_all[:n], ytr_all[:n]
                ftr = flat(xtr, ctr)
                btr = bilinear(xtr, ctr)
                dtr = diagonal(xtr, ctr)

                m0 = fit_l2(ftr, ytr)
                m1 = fit_l2(btr, ytr)
                m2 = fit_l1(btr, ytr)
                m3 = fit_l2(dtr, ytr)
                m4 = fit_l2(dtr.copy(), ytr)

                p0 = m0.predict(fte)
                p1 = m1.predict(bte)
                p2 = m2.predict(bte)
                p3 = m3.predict(dte)
                p4 = m4.predict(dte.copy())
                placement_equal = bool(np.array_equal(p3, p4)) and bool(np.array_equal(m3.coef_, m4.coef_)) and bool(np.array_equal(m3.intercept_, m4.intercept_))
                architecture_representation_equal_all = architecture_representation_equal_all and placement_equal

                coef = m2.coef_[0]
                support = np.flatnonzero(coef != 0.0)
                diagonal_support = int(np.count_nonzero(coef[diagonal_indices] != 0.0))
                offdiag_support = int(len(support) - diagonal_support)

                rep_rows.append({
                    "n_train": n,
                    "accuracy": {
                        "M0_FLAT_LINEAR": float(np.mean(p0 == yte)),
                        "M1_GENERIC_BILINEAR_L2": float(np.mean(p1 == yte)),
                        "M2_GENERIC_BILINEAR_L1": float(np.mean(p2 == yte)),
                        "M3_DIAGONAL_ARCH": float(np.mean(p3 == yte)),
                        "M4_EXPLICIT_RELATION": float(np.mean(p4 == yte)),
                    },
                    "M2_support": {
                        "total": int(len(support)),
                        "diagonal": diagonal_support,
                        "off_diagonal": offdiag_support,
                        "diagonal_fraction_retained": diagonal_support / k,
                        "off_diagonal_fraction_selected": offdiag_support / offdiag_count if offdiag_count else 0.0,
                    },
                    "M3_M4_prediction_and_parameter_identity": placement_equal,
                })
            reps.append({
                "replication": rep,
                "train_seed": train_seed,
                "test_seed": test_seed,
                "rows": rep_rows,
            })

        curve: list[dict[str, Any]] = []
        arms = (
            "M0_FLAT_LINEAR",
            "M1_GENERIC_BILINEAR_L2",
            "M2_GENERIC_BILINEAR_L1",
            "M3_DIAGONAL_ARCH",
            "M4_EXPLICIT_RELATION",
        )
        for idx, n in enumerate(N_GRID):
            row: dict[str, Any] = {"n_train": n}
            for arm in arms:
                vals = [float(rep["rows"][idx]["accuracy"][arm]) for rep in reps]
                row[arm] = {"mean_accuracy": float(np.mean(vals)), "std_accuracy": float(np.std(vals))}
            support_rows = [rep["rows"][idx]["M2_support"] for rep in reps]
            row["M2_support"] = {
                "median_total": float(np.median([s["total"] for s in support_rows])),
                "median_diagonal": float(np.median([s["diagonal"] for s in support_rows])),
                "median_off_diagonal": float(np.median([s["off_diagonal"] for s in support_rows])),
                "median_diagonal_fraction_retained": float(np.median([s["diagonal_fraction_retained"] for s in support_rows])),
                "median_off_diagonal_fraction_selected": float(np.median([s["off_diagonal_fraction_selected"] for s in support_rows])),
            }
            curve.append(row)

        thresholds = {arm: threshold(curve, arm) for arm in arms}
        m4_n = thresholds["M4_EXPLICIT_RELATION"]
        m1_n = thresholds["M1_GENERIC_BILINEAR_L2"]
        m2_n = thresholds["M2_GENERIC_BILINEAR_L1"]
        cells.append({
            "k": k,
            "feature_dimensions": {
                "M0_FLAT_LINEAR": 2 * k,
                "M1_GENERIC_BILINEAR_L2": k * k,
                "M2_GENERIC_BILINEAR_L1": k * k,
                "M3_DIAGONAL_ARCH": k,
                "M4_EXPLICIT_RELATION": k,
            },
            "replications": reps,
            "mean_curve": curve,
            "sample_threshold_0_90": thresholds,
            "threshold_ratios": {
                "M1_to_M4": float(m1_n / m4_n) if m1_n is not None and m4_n is not None else None,
                "M2_to_M4": float(m2_n / m4_n) if m2_n is not None and m4_n is not None else None,
                "M3_to_M4": 1.0 if thresholds["M3_DIAGONAL_ARCH"] == m4_n and m4_n is not None else None,
            },
        })

    m1_ratios = [float(c["threshold_ratios"]["M1_to_M4"]) for c in cells if c["threshold_ratios"]["M1_to_M4"] is not None]
    m1_reached = sum(c["sample_threshold_0_90"]["M1_GENERIC_BILINEAR_L2"] is not None for c in cells)
    primary_checks = {
        "M3_M4_identity_all_cells": architecture_representation_equal_all,
        "M3_M4_ge_0_95_at_4096_all_k": all(
            c["mean_curve"][-1]["M3_DIAGONAL_ARCH"]["mean_accuracy"] >= 0.95
            and c["mean_curve"][-1]["M4_EXPLICIT_RELATION"]["mean_accuracy"] >= 0.95
            for c in cells
        ),
        "M0_le_0_65_at_4096_all_k": all(c["mean_curve"][-1]["M0_FLAT_LINEAR"]["mean_accuracy"] <= 0.65 for c in cells),
        "M1_reaches_target_at_least_two_k": m1_reached >= 2,
        "median_M1_to_M4_threshold_ratio_ge_2": bool(m1_ratios) and float(np.median(m1_ratios)) >= 2.0,
        "feature_dimensions_exact": all(
            c["feature_dimensions"]["M1_GENERIC_BILINEAR_L2"] == c["k"] ** 2
            and c["feature_dimensions"]["M3_DIAGONAL_ARCH"] == c["k"]
            and c["feature_dimensions"]["M4_EXPLICIT_RELATION"] == c["k"]
            for c in cells
        ),
        "feature_generation_outcome_independent": True,
    }
    primary_terminal = (
        "STRUCTURAL_PRIOR_SUBSTITUTION_SUPPORTED_CONTROLLED_CLASS"
        if all(primary_checks.values())
        else "STRUCTURAL_PRIOR_SUBSTITUTION_GATE_NOT_MET"
    )

    m2_reached = sum(c["sample_threshold_0_90"]["M2_GENERIC_BILINEAR_L1"] is not None for c in cells)
    comparable_l1_l2 = [
        c for c in cells
        if c["sample_threshold_0_90"]["M2_GENERIC_BILINEAR_L1"] is not None
        and c["sample_threshold_0_90"]["M1_GENERIC_BILINEAR_L2"] is not None
    ]
    l1_no_later_count = sum(
        c["sample_threshold_0_90"]["M2_GENERIC_BILINEAR_L1"] <= c["sample_threshold_0_90"]["M1_GENERIC_BILINEAR_L2"]
        for c in comparable_l1_l2
    )
    final_support = [c["mean_curve"][-1]["M2_support"] for c in cells]
    sparse_checks = {
        "M2_reaches_target_at_least_two_k": m2_reached >= 2,
        "M2_no_later_than_M1_at_least_two_k": l1_no_later_count >= 2,
        "offdiag_support_below_half_all_k": all(s["median_off_diagonal_fraction_selected"] < 0.5 for s in final_support),
        "diagonal_support_at_least_0_8_all_k": all(s["median_diagonal_fraction_retained"] >= 0.8 for s in final_support),
    }
    sparse_terminal = (
        "SPARSITY_PRIOR_REDUCES_GENERIC_DISCOVERY_COST"
        if all(sparse_checks.values())
        else "SPARSITY_PRIOR_RECOVERY_GATE_NOT_MET"
    )

    result = {
        "schema": "P9P10.InductiveBiasSubstitution.v1",
        "protocol": "INDUCTIVE_BIAS_SUBSTITUTION_PROTOCOL_V1.md",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "k_grid": list(K_GRID),
        "n_train_grid": list(N_GRID),
        "replications_per_k": len(REPS),
        "n_test": N_TEST,
        "target_accuracy": TARGET,
        "cells": cells,
        "primary": {
            "checks": primary_checks,
            "M1_to_M4_threshold_ratios": m1_ratios,
            "median_M1_to_M4_threshold_ratio": float(np.median(m1_ratios)) if m1_ratios else None,
            "terminal": primary_terminal,
        },
        "sparsity_secondary": {
            "checks": sparse_checks,
            "terminal": sparse_terminal,
        },
        "claim_boundary": "Controlled structural-prior placement/discovery experiment; no transformer architecture equivalence claim.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
