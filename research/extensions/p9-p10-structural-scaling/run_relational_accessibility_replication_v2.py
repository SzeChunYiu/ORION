from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "RELATIONAL_ACCESSIBILITY_REPLICATION_V2.json"
DIMS = (3, 5, 9, 17, 33, 65)
REPS = (0, 1, 2)
N_TRAIN = 4096
N_TEST = 16384
N_SHUFFLES = 64


def sample(d: int, n: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = rng.choice(np.array([-1.0, 1.0]), size=(n, d), replace=True)
    c = rng.choice(np.array([-1.0, 1.0]), size=(n, d), replace=True)
    y = (np.sum(x * c, axis=1) > 0).astype(np.int64)
    return x, c, y


def flat(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, c), axis=1)


def relational(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, x * c), axis=1)


def broken(x: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.concatenate((x, x * np.roll(c, -1, axis=1)), axis=1)


def fit_accuracy(xtr: np.ndarray, ytr: np.ndarray, xte: np.ndarray, yte: np.ndarray) -> float:
    model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=5000)
    model.fit(xtr, ytr)
    return float(model.score(xte, yte))


def main() -> None:
    cells: list[dict[str, Any]] = []
    for d in DIMS:
        for r in REPS:
            train_seed = 5_100_001 + 10_007 * d + 101 * r
            test_seed = 6_100_001 + 20_011 * d + 103 * r
            xtr, ctr, ytr = sample(d, N_TRAIN, train_seed)
            xte, cte, yte = sample(d, N_TEST, test_seed)
            ftr, fte = flat(xtr, ctr), flat(xte, cte)
            rtr, rte = relational(xtr, ctr), relational(xte, cte)
            flat_acc = fit_accuracy(ftr, ytr, fte, yte)
            rel_acc = fit_accuracy(rtr, ytr, rte, yte)
            broken_acc = fit_accuracy(broken(xtr, ctr), ytr, broken(xte, cte), yte)

            recon_failures = int(np.count_nonzero(xtr * (xtr * ctr) != ctr))
            recon_failures += int(np.count_nonzero(xte * (xte * cte) != cte))

            prng = np.random.default_rng(8_100_001 + 40_009 * d + 1013 * r)
            perm = prng.permutation(d)
            pf_acc = fit_accuracy(flat(xtr[:, perm], ctr[:, perm]), ytr, flat(xte[:, perm], cte[:, perm]), yte)
            pr_acc = fit_accuracy(relational(xtr[:, perm], ctr[:, perm]), ytr, relational(xte[:, perm], cte[:, perm]), yte)

            nulls: list[float] = []
            for j in range(N_SHUFFLES):
                seed = 7_100_001 + 30_011 * d + 1009 * r + j
                shuffled = np.array(ytr, copy=True)
                np.random.default_rng(seed).shuffle(shuffled)
                nulls.append(fit_accuracy(rtr, shuffled, rte, yte))
            null_ge = sum(v >= rel_acc for v in nulls)
            p_emp = (1 + null_ge) / (N_SHUFFLES + 1)

            checks = {
                "relational_ge_0_95": rel_acc >= 0.95,
                "flat_le_0_65": flat_acc <= 0.65,
                "delta_ge_0_30": rel_acc - flat_acc >= 0.30,
                "relational_gt_all_shuffle_nulls": rel_acc > max(nulls),
                "empirical_p_is_1_over_65": p_emp == 1 / 65,
                "broken_lt_0_65": broken_acc < 0.65,
                "reconstruction_zero": recon_failures == 0,
                "flat_permutation_change_lt_0_03": abs(pf_acc - flat_acc) < 0.03,
                "relational_permutation_change_lt_0_03": abs(pr_acc - rel_acc) < 0.03,
            }
            cells.append({
                "dimension": d,
                "replication": r,
                "train_seed": train_seed,
                "test_seed": test_seed,
                "flat_accuracy": flat_acc,
                "relational_accuracy": rel_acc,
                "absolute_accuracy_delta": rel_acc - flat_acc,
                "broken_relation_accuracy": broken_acc,
                "reconstruction_failure_count": recon_failures,
                "surface_permutation": {
                    "permutation": [int(v) for v in perm.tolist()],
                    "flat_accuracy": pf_acc,
                    "relational_accuracy": pr_acc,
                    "flat_absolute_change": abs(pf_acc - flat_acc),
                    "relational_absolute_change": abs(pr_acc - rel_acc),
                },
                "label_shuffle_null": {
                    "count": N_SHUFFLES,
                    "accuracies": nulls,
                    "mean": float(np.mean(nulls)),
                    "std": float(np.std(nulls)),
                    "median": float(np.median(nulls)),
                    "maximum": max(nulls),
                    "null_at_least_observed_count": null_ge,
                    "empirical_one_sided_p": p_emp,
                },
                "checks": checks,
                "cell_pass": all(checks.values()),
            })

    deltas = [float(c["absolute_accuracy_delta"]) for c in cells]
    all_cells_pass = all(bool(c["cell_pass"]) for c in cells)
    aggregate_checks = {
        "all_18_cells_pass": all_cells_pass,
        "median_delta_ge_0_45": float(np.median(deltas)) >= 0.45,
    }
    terminal = (
        "RELATIONAL_ACCESSIBILITY_REPLICATED_CONTROLLED_CLASS"
        if all(aggregate_checks.values())
        else "RELATIONAL_ACCESSIBILITY_REPLICATION_GATE_NOT_MET"
    )
    result = {
        "schema": "P9P10.RelationalAccessibilityReplication.v2",
        "protocol": "RELATIONAL_ACCESSIBILITY_REPLICATION_PROTOCOL_V2.md",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "platform": platform.platform(),
        },
        "dimensions": list(DIMS),
        "replications_per_dimension": len(REPS),
        "n_train": N_TRAIN,
        "n_test": N_TEST,
        "shuffle_null_draws_per_cell": N_SHUFFLES,
        "cells": cells,
        "aggregate": {
            "cell_count": len(cells),
            "passed_cell_count": sum(bool(c["cell_pass"]) for c in cells),
            "median_delta": float(np.median(deltas)),
            "minimum_delta": min(deltas),
            "maximum_delta": max(deltas),
            "mean_flat_accuracy": float(np.mean([c["flat_accuracy"] for c in cells])),
            "mean_relational_accuracy": float(np.mean([c["relational_accuracy"] for c in cells])),
            "aggregate_checks": aggregate_checks,
        },
        "terminal": terminal,
        "claim_boundary": "Fresh controlled replication of a restricted linear-learner accessibility separation; no LLM or natural-domain scaling claim.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    OUT.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
