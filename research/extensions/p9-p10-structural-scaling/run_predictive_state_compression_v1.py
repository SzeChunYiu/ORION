from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "PREDICTIVE_STATE_COMPRESSION_V1.json"
K_GRID = (17, 33, 65)
N_GRID = (32, 64, 128, 256, 512, 1024, 2048, 4096)
REPS = (0, 1, 2)
N_TEST = 16384
TARGET = 0.90


def sample(k: int, n: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.choice(np.array([-1.0, 1.0]), size=(n, k), replace=True)
    c = rng.choice(np.array([-1.0, 1.0]), size=(n, k), replace=True)
    r = x * c
    y = (np.sum(r, axis=1) > 0).astype(np.int64)
    return x, c, r, y


def nuisance(k: int, n: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).choice(np.array([-1.0, 1.0]), size=(n, 4 * k), replace=True)


def fit_metrics(xtr: np.ndarray, ytr: np.ndarray, xte: np.ndarray, yte: np.ndarray) -> tuple[float, float]:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(xtr, ytr)
    prob = model.predict_proba(xte)[:, 1]
    pred = (prob >= 0.5).astype(np.int64)
    return float(np.mean(pred == yte)), float(log_loss(yte, prob, labels=[0, 1]))


def threshold(curve: list[dict[str, Any]], arm: str) -> int | None:
    for row in curve:
        if float(row[arm]["mean_accuracy"]) >= TARGET:
            return int(row["n_train"])
    return None


def main() -> None:
    cells: list[dict[str, Any]] = []
    max_abs_corr_all: list[float] = []
    for k in K_GRID:
        rep_data: list[dict[str, Any]] = []
        for rep in REPS:
            train_seed = 13_100_001 + 230_003 * k + 1009 * rep
            test_seed = 13_200_003 + 250_007 * k + 1013 * rep
            ztrain_seed = 13_300_007 + 270_011 * k + 1019 * rep
            ztest_seed = 13_400_009 + 290_021 * k + 1021 * rep
            xtr, _, rtr, ytr = sample(k, max(N_GRID), train_seed)
            xte, _, rte, yte = sample(k, N_TEST, test_seed)
            ztr = nuisance(k, max(N_GRID), ztrain_seed)
            zte = nuisance(k, N_TEST, ztest_seed)
            y_center = yte.astype(float) - float(np.mean(yte))
            y_norm = float(np.sqrt(np.sum(y_center * y_center)))
            corrs: list[float] = []
            for j in range(zte.shape[1]):
                z_center = zte[:, j] - float(np.mean(zte[:, j]))
                denom = float(np.sqrt(np.sum(z_center * z_center))) * y_norm
                corr = 0.0 if denom == 0 else float(np.sum(z_center * y_center) / denom)
                corrs.append(corr)
            max_abs_corr = max(abs(v) for v in corrs)
            max_abs_corr_all.append(max_abs_corr)
            metrics_by_n: list[dict[str, Any]] = []
            for n in N_GRID:
                arms = {
                    "minimal": (rtr[:n], rte),
                    "full": (np.concatenate((xtr[:n], rtr[:n]), axis=1), np.concatenate((xte, rte), axis=1)),
                    "padded": (
                        np.concatenate((xtr[:n], rtr[:n], ztr[:n]), axis=1),
                        np.concatenate((xte, rte, zte), axis=1),
                    ),
                }
                row: dict[str, Any] = {"n_train": n}
                for arm, (atr, ate) in arms.items():
                    acc, loss = fit_metrics(atr, ytr[:n], ate, yte)
                    row[arm] = {"accuracy": acc, "log_loss": loss}
                metrics_by_n.append(row)
            rep_data.append({
                "replication": rep,
                "train_seed": train_seed,
                "test_seed": test_seed,
                "nuisance_train_seed": ztrain_seed,
                "nuisance_test_seed": ztest_seed,
                "max_abs_nuisance_label_correlation": max_abs_corr,
                "metrics_by_n": metrics_by_n,
            })

        curve: list[dict[str, Any]] = []
        for idx, n in enumerate(N_GRID):
            row: dict[str, Any] = {"n_train": n}
            for arm in ("minimal", "full", "padded"):
                accs = [float(rep["metrics_by_n"][idx][arm]["accuracy"]) for rep in rep_data]
                losses = [float(rep["metrics_by_n"][idx][arm]["log_loss"]) for rep in rep_data]
                row[arm] = {
                    "mean_accuracy": float(np.mean(accs)),
                    "std_accuracy": float(np.std(accs)),
                    "mean_log_loss": float(np.mean(losses)),
                    "std_log_loss": float(np.std(losses)),
                }
            curve.append(row)
        min_n = threshold(curve, "minimal")
        full_n = threshold(curve, "full")
        padded_n = threshold(curve, "padded")
        cells.append({
            "k": k,
            "feature_dimensions": {"minimal": k, "full": 2 * k, "padded": 6 * k},
            "replications": rep_data,
            "mean_curve": curve,
            "sample_threshold_0_90": {"minimal": min_n, "full": full_n, "padded": padded_n},
            "threshold_ratios": {
                "full_to_minimal": float(full_n / min_n) if full_n is not None and min_n is not None else None,
                "padded_to_minimal": float(padded_n / min_n) if padded_n is not None and min_n is not None else None,
            },
        })

    full_ratios = [float(c["threshold_ratios"]["full_to_minimal"]) for c in cells if c["threshold_ratios"]["full_to_minimal"] is not None]
    padded_ratios = [float(c["threshold_ratios"]["padded_to_minimal"]) for c in cells if c["threshold_ratios"]["padded_to_minimal"] is not None]
    low_n_logloss_wins = 0
    for cell in cells:
        first = cell["mean_curve"][0]
        if first["minimal"]["mean_log_loss"] <= first["full"]["mean_log_loss"] and first["minimal"]["mean_log_loss"] <= first["padded"]["mean_log_loss"]:
            low_n_logloss_wins += 1
    checks = {
        "minimal_ge_0_95_all_at_4096": all(c["mean_curve"][-1]["minimal"]["mean_accuracy"] >= 0.95 for c in cells),
        "minimal_threshold_no_later_than_full_all": all(
            c["sample_threshold_0_90"]["minimal"] is not None
            and (c["sample_threshold_0_90"]["full"] is None or c["sample_threshold_0_90"]["minimal"] <= c["sample_threshold_0_90"]["full"])
            for c in cells
        ),
        "minimal_threshold_no_later_than_padded_all": all(
            c["sample_threshold_0_90"]["minimal"] is not None
            and (c["sample_threshold_0_90"]["padded"] is None or c["sample_threshold_0_90"]["minimal"] <= c["sample_threshold_0_90"]["padded"])
            for c in cells
        ),
        "median_full_to_minimal_ge_1_5": bool(full_ratios) and float(np.median(full_ratios)) >= 1.5,
        "median_padded_to_minimal_ge_2": bool(padded_ratios) and float(np.median(padded_ratios)) >= 2.0,
        "minimal_low_n_logloss_best_at_least_two_k": low_n_logloss_wins >= 2,
        "nuisance_correlation_sentinel": max(max_abs_corr_all) < 0.04,
    }
    terminal = (
        "PREDICTIVE_STATE_COMPRESSION_ADVANTAGE_SUPPORTED"
        if all(checks.values())
        else "PREDICTIVE_STATE_COMPRESSION_GATE_NOT_MET"
    )
    result = {
        "schema": "P9P10.PredictiveStateCompression.v1",
        "protocol": "PREDICTIVE_STATE_COMPRESSION_PROTOCOL_V1.md",
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
        "aggregate": {
            "full_to_minimal_threshold_ratios": full_ratios,
            "padded_to_minimal_threshold_ratios": padded_ratios,
            "median_full_to_minimal_threshold_ratio": float(np.median(full_ratios)) if full_ratios else None,
            "median_padded_to_minimal_threshold_ratio": float(np.median(padded_ratios)) if padded_ratios else None,
            "low_n_logloss_winning_k_count": low_n_logloss_wins,
            "maximum_abs_nuisance_label_correlation": max(max_abs_corr_all),
            "checks": checks,
        },
        "terminal": terminal,
        "claim_boundary": "Predictive-sufficiency/nuisance-state result; compact arm is not information-equivalent to full world state and no natural-language context claim is implied.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
