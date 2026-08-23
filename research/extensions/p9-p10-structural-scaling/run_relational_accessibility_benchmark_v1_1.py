from __future__ import annotations

import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "RELATIONAL_ACCESSIBILITY_BENCHMARK_V1_1.json"

PROTOCOL = "P9P10.RelationalAccessibilityProtocol.v1.1"
DIMENSIONS = (3, 5, 9, 17, 33, 65)
TRAIN_SIZES = (64, 128, 256, 512, 1024, 2048, 4096)
TEST_N = 8192
LOGISTIC_C = 1.0
LOGISTIC_MAX_ITER = 5000
TREE_DEPTHS: tuple[int | None, ...] = (2, 4, 8, 16, None)
TREE_RANDOM_STATE = 271828


def sample_task(d: int, n: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.choice(np.array([-1.0, 1.0]), size=(n, d), replace=True)
    c = rng.choice(np.array([-1.0, 1.0]), size=(n, d), replace=True)
    score = np.sum(x * c, axis=1)
    if np.any(score == 0):
        raise RuntimeError("odd dimension unexpectedly produced an alignment tie")
    y = (score > 0).astype(np.int64)
    return x, c, y


def flat_representation(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, c), axis=1)


def relational_representation(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, x * c), axis=1)


def broken_relational_representation(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    shifted_c = np.roll(c, shift=-1, axis=1)
    return np.concatenate((x, x * shifted_c), axis=1)


def reconstruction_failures(x: np.ndarray, c: np.ndarray) -> int:
    r = x * c
    reconstructed = x * r
    return int(np.count_nonzero(reconstructed != c))


def fit_logistic(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray) -> dict[str, Any]:
    if len(np.unique(train_y)) != 2:
        raise RuntimeError("frozen training sample does not contain both labels")
    model = LogisticRegression(
        C=LOGISTIC_C,
        solver="lbfgs",
        max_iter=LOGISTIC_MAX_ITER,
    )
    model.fit(train_x, train_y)
    accuracy = float(model.score(test_x, test_y))
    n_iter = int(np.max(model.n_iter_))
    return {
        "accuracy": accuracy,
        "correct": int(round(accuracy * len(test_y))),
        "test_n": int(len(test_y)),
        "coefficient_l2_norm": float(np.linalg.norm(model.coef_)),
        "intercept": [float(v) for v in model.intercept_.tolist()],
        "n_iter": n_iter,
        "converged_before_max_iter": n_iter < LOGISTIC_MAX_ITER,
    }


def fit_tree(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray, depth: int | None) -> dict[str, Any]:
    model = DecisionTreeClassifier(max_depth=depth, random_state=TREE_RANDOM_STATE)
    model.fit(train_x, train_y)
    accuracy = float(model.score(test_x, test_y))
    return {
        "max_depth": depth,
        "accuracy": accuracy,
        "correct": int(round(accuracy * len(test_y))),
        "test_n": int(len(test_y)),
        "fitted_depth": int(model.get_depth()),
        "leaf_count": int(model.get_n_leaves()),
    }


def accuracy_threshold_size(rows: dict[str, dict[str, Any]], representation: str, threshold: float = 0.90) -> int | str:
    for n in TRAIN_SIZES:
        if float(rows[str(n)][representation]["accuracy"]) >= threshold:
            return n
    return "NOT_REACHED"


def main() -> None:
    cells: dict[str, Any] = {}
    primary: dict[str, Any] = {}
    controls: dict[str, Any] = {}
    reconstruction_failure_count = 0

    for d in DIMENSIONS:
        test_seed = 2_000_003 + 2017 * d
        x_test, c_test, y_test = sample_task(d, TEST_N, test_seed)
        reconstruction_failure_count += reconstruction_failures(x_test, c_test)
        flat_test = flat_representation(x_test, c_test)
        rel_test = relational_representation(x_test, c_test)

        dim_rows: dict[str, Any] = {}
        train_cache: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
        for n_train in TRAIN_SIZES:
            train_seed = 1_000_003 + 1009 * d + n_train
            x_train, c_train, y_train = sample_task(d, n_train, train_seed)
            train_cache[n_train] = (x_train, c_train, y_train)
            reconstruction_failure_count += reconstruction_failures(x_train, c_train)
            flat_train = flat_representation(x_train, c_train)
            rel_train = relational_representation(x_train, c_train)
            dim_rows[str(n_train)] = {
                "seed": train_seed,
                "flat": fit_logistic(flat_train, y_train, flat_test, y_test),
                "relational": fit_logistic(rel_train, y_train, rel_test, y_test),
            }

        cells[str(d)] = {
            "dimension": d,
            "test_seed": test_seed,
            "test_n": TEST_N,
            "test_positive_rate": float(np.mean(y_test)),
            "training": dim_rows,
            "sample_threshold_0_90": {
                "flat": accuracy_threshold_size(dim_rows, "flat"),
                "relational": accuracy_threshold_size(dim_rows, "relational"),
            },
        }

        canonical = dim_rows["4096"]
        delta = float(canonical["relational"]["accuracy"] - canonical["flat"]["accuracy"])
        primary[str(d)] = {
            "flat_accuracy": canonical["flat"]["accuracy"],
            "relational_accuracy": canonical["relational"]["accuracy"],
            "absolute_accuracy_delta": delta,
        }

        x_train, c_train, y_train = train_cache[4096]
        flat_train = flat_representation(x_train, c_train)
        rel_train = relational_representation(x_train, c_train)

        # Broken relation: a fixed non-identity cyclic candidate-coordinate shift.
        broken_train = broken_relational_representation(x_train, c_train)
        broken_test = broken_relational_representation(x_test, c_test)
        broken = fit_logistic(broken_train, y_train, broken_test, y_test)

        # Label shuffle: representation bytes stay fixed; only training labels move.
        shuffle_rng = np.random.default_rng(3_000_001 + d)
        shuffled_y = np.array(y_train, copy=True)
        shuffle_rng.shuffle(shuffled_y)
        shuffled_flat = fit_logistic(flat_train, shuffled_y, flat_test, y_test)
        shuffled_rel = fit_logistic(rel_train, shuffled_y, rel_test, y_test)

        # Shared coordinate permutation preserves the semantic alignment relation.
        permutation_rng = np.random.default_rng(4_000_001 + d)
        permutation = permutation_rng.permutation(d)
        px_train = x_train[:, permutation]
        pc_train = c_train[:, permutation]
        px_test = x_test[:, permutation]
        pc_test = c_test[:, permutation]
        perm_flat = fit_logistic(
            flat_representation(px_train, pc_train),
            y_train,
            flat_representation(px_test, pc_test),
            y_test,
        )
        perm_rel = fit_logistic(
            relational_representation(px_train, pc_train),
            y_train,
            relational_representation(px_test, pc_test),
            y_test,
        )

        trees = {
            "flat": [
                fit_tree(flat_train, y_train, flat_test, y_test, depth)
                for depth in TREE_DEPTHS
            ],
            "relational": [
                fit_tree(rel_train, y_train, rel_test, y_test, depth)
                for depth in TREE_DEPTHS
            ],
        }

        controls[str(d)] = {
            "broken_relation": broken,
            "label_shuffle": {
                "seed": 3_000_001 + d,
                "flat": shuffled_flat,
                "relational": shuffled_rel,
            },
            "surface_permutation": {
                "seed": 4_000_001 + d,
                "permutation": [int(v) for v in permutation.tolist()],
                "flat": perm_flat,
                "relational": perm_rel,
                "flat_absolute_change": abs(float(perm_flat["accuracy"]) - float(canonical["flat"]["accuracy"])),
                "relational_absolute_change": abs(float(perm_rel["accuracy"]) - float(canonical["relational"]["accuracy"])),
            },
            "tree_capacity_probe": trees,
        }

    endpoint_checks = {
        "delta_gt_0_30_all_dimensions": all(float(row["absolute_accuracy_delta"]) > 0.30 for row in primary.values()),
        "relational_gt_0_90_all_dimensions": all(float(row["relational_accuracy"]) > 0.90 for row in primary.values()),
        "flat_lt_0_65_all_dimensions": all(float(row["flat_accuracy"]) < 0.65 for row in primary.values()),
        "bijection_reconstruction_failures_zero": reconstruction_failure_count == 0,
        "broken_relation_lt_0_65_all_dimensions": all(float(row["broken_relation"]["accuracy"]) < 0.65 for row in controls.values()),
        "label_shuffle_lt_0_65_all_dimensions": all(
            float(row["label_shuffle"][rep]["accuracy"]) < 0.65
            for row in controls.values()
            for rep in ("flat", "relational")
        ),
        "surface_permutation_change_lt_0_03_all_dimensions": all(
            float(row["surface_permutation"][key]) < 0.03
            for row in controls.values()
            for key in ("flat_absolute_change", "relational_absolute_change")
        ),
    }
    passed = all(endpoint_checks.values())

    artifact = {
        "schema": "P9P10.RelationalAccessibilityResult.v1.1",
        "protocol": PROTOCOL,
        "protocol_files": [
            "RELATIONAL_ACCESSIBILITY_BENCHMARK_PROTOCOL_V1.md",
            "RELATIONAL_ACCESSIBILITY_BENCHMARK_PROTOCOL_V1_1_AMENDMENT.md",
        ],
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "frozen_dimensions": list(DIMENSIONS),
        "frozen_train_sizes": list(TRAIN_SIZES),
        "protected_test_n_per_dimension": TEST_N,
        "cells": cells,
        "primary_at_n4096": primary,
        "controls_at_n4096": controls,
        "reconstruction_failure_count": reconstruction_failure_count,
        "endpoint_checks": endpoint_checks,
        "terminal": (
            "RELATIONAL_ACCESSIBILITY_GAP_SUPPORTED_CONTROLLED_CLASS"
            if passed
            else "RELATIONAL_ACCESSIBILITY_PRIMARY_GATE_NOT_MET"
        ),
        "claim_boundary": (
            "Controlled information-equivalent restricted-learner benchmark only; "
            "does not establish an LLM scaling law, natural-domain effect, or causal mechanism for P9 D1."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
