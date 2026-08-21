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
OUT = HERE / "results" / "ACCESS_DEGREE_RECOVERY_V1.json"
K = 13
BLOCKS = (1, 2, 4, 8, 13)
DEGREES = (1, 2, 3, 4)
REPS = (0, 1, 2)
N_TRAIN = 4096
N_TEST = 16384
TARGET = 0.90


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


def transform(train: np.ndarray, test: np.ndarray, degree: int) -> tuple[np.ndarray, np.ndarray, int]:
    if degree == 1:
        return train, test, int(train.shape[1])
    poly = PolynomialFeatures(degree=degree, include_bias=False, interaction_only=True)
    poly.fit(train[:1])
    return poly.transform(train), poly.transform(test), int(poly.n_output_features_)


def fit_score(train: np.ndarray, y_train: np.ndarray, test: np.ndarray, y_test: np.ndarray) -> float:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(train, y_train)
    return float(model.score(test, y_test))


def main() -> None:
    cells: list[dict[str, Any]] = []
    for block in BLOCKS:
        for rep in REPS:
            train_seed = 12_100_001 + 190_001 * block + 1009 * rep
            test_seed = 12_200_003 + 210_011 * block + 1013 * rep
            rtr, ytr = sample(N_TRAIN, train_seed)
            rte, yte = sample(N_TEST, test_seed)
            utr, ute = encode(rtr, block), encode(rte, block)
            failures = int(np.count_nonzero(decode(utr, block) != rtr))
            failures += int(np.count_nonzero(decode(ute, block) != rte))
            degree_rows: list[dict[str, Any]] = []
            for degree in DEGREES:
                xtr, xte, feature_dim = transform(utr, ute, degree)
                degree_rows.append({
                    "degree": degree,
                    "feature_dimension": feature_dim,
                    "accuracy": fit_score(xtr, ytr, xte, yte),
                })
            cells.append({
                "block_length": block,
                "replication": rep,
                "train_seed": train_seed,
                "test_seed": test_seed,
                "decode_failure_count": failures,
                "maximum_inverse_coordinate_degree": min(block, K),
                "degrees": degree_rows,
            })

    by_block: list[dict[str, Any]] = []
    block_degree_means: dict[int, dict[int, float]] = {}
    feature_dims: dict[int, int] = {}
    for block in BLOCKS:
        group = [c for c in cells if c["block_length"] == block]
        means: dict[int, float] = {}
        for degree in DEGREES:
            vals = [
                float(next(row["accuracy"] for row in c["degrees"] if row["degree"] == degree))
                for c in group
            ]
            means[degree] = float(np.mean(vals))
            dims = {
                int(next(row["feature_dimension"] for row in c["degrees"] if row["degree"] == degree))
                for c in group
            }
            if len(dims) != 1:
                raise SystemExit("feature dimension unexpectedly varies across replication")
            feature_dims[degree] = dims.pop()
        block_degree_means[block] = means
        reaching = [degree for degree in DEGREES if means[degree] >= TARGET]
        by_block.append({
            "block_length": block,
            "mean_accuracy_by_degree": {str(d): means[d] for d in DEGREES},
            "minimum_tested_degree_reaching_0_90": min(reaching) if reaching else None,
            "degree4_minus_degree1": means[4] - means[1],
        })

    min_degree = {
        row["block_length"]: row["minimum_tested_degree_reaching_0_90"] for row in by_block
    }
    means = block_degree_means
    checks = {
        "decode_zero_all": all(c["decode_failure_count"] == 0 for c in cells),
        "b1_d1_ge_0_95": means[1][1] >= 0.95,
        "b2_d2_ge_0_95": means[2][2] >= 0.95,
        "b2_d2_minus_d1_ge_0_10": means[2][2] - means[2][1] >= 0.10,
        "b4_d4_ge_0_90": means[4][4] >= 0.90,
        "b4_d4_minus_d1_ge_0_10": means[4][4] - means[4][1] >= 0.10,
        "b4_d4_minus_d2_ge_0_05": means[4][4] - means[4][2] >= 0.05,
        "minimum_degree_landmarks": (
            min_degree[1] == 1
            and min_degree[2] is not None and min_degree[2] >= 2
            and min_degree[4] is not None and min_degree[4] >= 3
        ),
        "feature_dimension_strictly_increasing": all(
            feature_dims[d2] > feature_dims[d1] for d1, d2 in zip(DEGREES[:-1], DEGREES[1:])
        ),
    }
    terminal = (
        "ACCESS_DEGREE_RECOVERY_SUPPORTED_CONTROLLED_CLASS"
        if all(checks.values())
        else "ACCESS_DEGREE_RECOVERY_GATE_NOT_MET"
    )
    result = {
        "schema": "P9P10.AccessDegreeRecovery.v1",
        "protocol": "ACCESS_DEGREE_RECOVERY_PROTOCOL_V1.md",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "k": K,
        "block_lengths": list(BLOCKS),
        "degrees": list(DEGREES),
        "replications_per_block": len(REPS),
        "n_train": N_TRAIN,
        "n_test": N_TEST,
        "target_accuracy": TARGET,
        "feature_dimensions_by_degree": {str(d): feature_dims[d] for d in DEGREES},
        "cells": cells,
        "aggregate": {
            "by_block": by_block,
            "checks": checks,
        },
        "terminal": terminal,
        "claim_boundary": "Restricted polynomial logistic recovery under a bijective obfuscation family; not a transformer/model-size or universal complexity result.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
