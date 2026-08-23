from __future__ import annotations

import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "INVERTIBLE_OBFUSCATION_LADDER_V1.json"
K = 65
BLOCKS = (1, 2, 4, 8, 16, 32, 65)
REPS = (0, 1, 2)
N_TRAIN = 8192
N_TEST = 32768


def sample(n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    r = rng.choice(np.array([-1.0, 1.0]), size=(n, K), replace=True)
    y = (np.sum(r, axis=1) > 0).astype(np.int64)
    return r, y


def encode(r: np.ndarray, block: int) -> np.ndarray:
    u = np.array(r, copy=True)
    for start in range(0, K, block):
        end = min(K, start + block)
        for j in range(start + 1, end):
            u[:, j] = r[:, j] * r[:, j - 1]
    return u


def decode(u: np.ndarray, block: int) -> np.ndarray:
    r = np.array(u, copy=True)
    for start in range(0, K, block):
        end = min(K, start + block)
        for j in range(start + 1, end):
            r[:, j] = u[:, j] * r[:, j - 1]
    return r


def fit_score(xtr: np.ndarray, ytr: np.ndarray, xte: np.ndarray, yte: np.ndarray) -> float:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(xtr, ytr)
    return float(model.score(xte, yte))


def threshold_block(means: dict[int, float], target: float) -> int | None:
    for block in BLOCKS:
        if means[block] < target:
            return block
    return None


def main() -> None:
    cells: list[dict[str, Any]] = []
    quadratic_blocks = {1, 2, 4, 8}
    for block in BLOCKS:
        for rep in REPS:
            train_seed = 10_100_001 + 100_003 * block + 1009 * rep
            test_seed = 10_200_003 + 120_011 * block + 1013 * rep
            rtr, ytr = sample(N_TRAIN, train_seed)
            rte, yte = sample(N_TEST, test_seed)
            utr, ute = encode(rtr, block), encode(rte, block)
            decoded_train, decoded_test = decode(utr, block), decode(ute, block)
            failures = int(np.count_nonzero(decoded_train != rtr)) + int(np.count_nonzero(decoded_test != rte))
            linear_acc = fit_score(utr, ytr, ute, yte)
            quadratic_acc = None
            quadratic_dim = None
            if block in quadratic_blocks:
                poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
                poly.fit(utr[:1])
                quadratic_dim = int(poly.n_output_features_)
                quadratic_acc = fit_score(poly.transform(utr), ytr, poly.transform(ute), yte)
            cells.append({
                "block_length": block,
                "replication": rep,
                "train_seed": train_seed,
                "test_seed": test_seed,
                "linear_accuracy": linear_acc,
                "quadratic_accuracy": quadratic_acc,
                "quadratic_feature_dimension": quadratic_dim,
                "decode_failure_count": failures,
                "maximum_inverse_coordinate_degree": min(block, K),
            })

    means: dict[int, float] = {}
    stds: dict[int, float] = {}
    quad_means: dict[int, float | None] = {}
    by_block: list[dict[str, Any]] = []
    for block in BLOCKS:
        group = [c for c in cells if c["block_length"] == block]
        linear = [float(c["linear_accuracy"]) for c in group]
        quad = [float(c["quadratic_accuracy"]) for c in group if c["quadratic_accuracy"] is not None]
        means[block] = float(np.mean(linear))
        stds[block] = float(np.std(linear))
        quad_means[block] = float(np.mean(quad)) if quad else None
        by_block.append({
            "block_length": block,
            "mean_linear_accuracy": means[block],
            "std_linear_accuracy": stds[block],
            "mean_quadratic_accuracy": quad_means[block],
            "replications": len(group),
        })

    adjacent_nonincrease = sum(
        means[b2] <= means[b1] + 1e-12 for b1, b2 in zip(BLOCKS[:-1], BLOCKS[1:])
    )
    xs = np.log2(np.array(BLOCKS, dtype=float))
    ys = np.array([means[b] for b in BLOCKS], dtype=float)
    slope = float(np.polyfit(xs, ys, 1)[0])
    checks = {
        "decode_zero_all": all(c["decode_failure_count"] == 0 for c in cells),
        "canonical_mean_ge_0_95": means[1] >= 0.95,
        "full_chain_mean_le_0_70": means[65] <= 0.70,
        "at_least_five_adjacent_nonincreasing": adjacent_nonincrease >= 5,
        "canonical_minus_full_chain_ge_0_20": means[1] - means[65] >= 0.20,
    }
    terminal = (
        "INVERTIBLE_OBFUSCATION_ACCESSIBILITY_TAX_SUPPORTED"
        if all(checks.values())
        else "INVERTIBLE_OBFUSCATION_ACCESSIBILITY_GATE_NOT_MET"
    )
    result = {
        "schema": "P9P10.InvertibleObfuscationLadder.v1",
        "protocol": "NOVELTY_EXPANSION_PROTOCOL_V3.md#experiment-b--invertible-nonlinear-obfuscation-ladder",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "k": K,
        "block_lengths": list(BLOCKS),
        "replications_per_block": len(REPS),
        "n_train": N_TRAIN,
        "n_test": N_TEST,
        "cells": cells,
        "aggregate": {
            "by_block": by_block,
            "adjacent_nonincrease_count": adjacent_nonincrease,
            "linear_accuracy_slope_vs_log2_block": slope,
            "first_block_mean_below_0_80": threshold_block(means, 0.80),
            "first_block_mean_below_0_70": threshold_block(means, 0.70),
            "first_block_mean_below_0_60": threshold_block(means, 0.60),
            "canonical_minus_full_chain_gap": means[1] - means[65],
            "checks": checks,
        },
        "terminal": terminal,
        "claim_boundary": "Bijective nonlinear coordinate-obfuscation accessibility result for fixed logistic learners; no general lower bound or LLM claim.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
