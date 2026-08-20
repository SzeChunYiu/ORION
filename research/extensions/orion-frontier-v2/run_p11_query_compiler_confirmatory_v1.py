from __future__ import annotations

import itertools
import json
import math
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

SEED = 914311
CELLS = ((14, 2), (16, 4), (18, 3), (20, 3))
TRAIN_SIZES = (32, 64, 128, 256, 512, 1024)
N_TEST = 8192
N_QUERIES = 12
OUT = Path(__file__).with_name("results") / "P11_QUERY_COMPILER_CONFIRMATORY_V1.json"
TIMING_OUT = Path(__file__).with_name("results") / "P11_QUERY_COMPILER_TIMING_NONAUTHORITATIVE_V1.json"


def parity_bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    out = np.empty((x.shape[0], len(subsets)), dtype=np.int8)
    for j, subset in enumerate(subsets):
        out[:, j] = np.prod(x[:, subset], axis=1)
    return out


def fit_score(train_x: np.ndarray, y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray) -> float:
    model = LogisticRegression(C=1.0, solver="liblinear", max_iter=1000)
    model.fit(train_x, y)
    return float(model.score(test_x, test_y))


def exhaustive_theory_sanity() -> dict[str, object]:
    checks: list[dict[str, object]] = []
    for d, s in ((5, 2), (6, 3)):
        subsets = list(itertools.combinations(range(d), s))
        worlds = np.array(list(itertools.product((-1, 1), repeat=d)), dtype=np.int8)
        bank = parity_bank(worlds, subsets).astype(np.int64)
        gram = bank.T @ bank
        expected = worlds.shape[0] * np.eye(len(subsets), dtype=np.int64)
        checks.append(
            {
                "d": d,
                "s": s,
                "dimension": len(subsets),
                "expected_dimension": math.comb(d, s),
                "orthogonality_exact": bool(np.array_equal(gram, expected)),
            }
        )
    return {
        "checks": checks,
        "all_green": all(
            row["dimension"] == row["expected_dimension"] and row["orthogonality_exact"]
            for row in checks
        ),
    }


def threshold(curve: dict[int, float], target: float = 0.90) -> int | None:
    for n in TRAIN_SIZES:
        if curve[n] >= target:
            return n
    return None


def main() -> None:
    rng = np.random.default_rng(SEED)
    theory = exhaustive_theory_sanity()
    cell_results: list[dict[str, object]] = []
    timing_rows: list[dict[str, object]] = []

    for d, s in CELLS:
        subsets = list(itertools.combinations(range(d), s))
        universal_dim = len(subsets)
        query_indices = [int(i) for i in rng.choice(universal_dim, size=N_QUERIES, replace=False)]
        test_x = rng.choice((-1, 1), size=(N_TEST, d)).astype(np.int8)
        test_bank = parity_bank(test_x, subsets)
        curves = {"RAW_LINEAR": {}, "UNIVERSAL_BANK": {}, "QUERY_COMPILED": {}}
        per_size: list[dict[str, object]] = []

        for n in TRAIN_SIZES:
            train_x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
            train_bank = parity_bank(train_x, subsets)
            scores = {arm: [] for arm in curves}
            started = time.perf_counter()
            for query_index in query_indices:
                y = (train_bank[:, query_index] > 0).astype(np.int8)
                test_y = (test_bank[:, query_index] > 0).astype(np.int8)
                scores["RAW_LINEAR"].append(fit_score(train_x, y, test_x, test_y))
                scores["UNIVERSAL_BANK"].append(fit_score(train_bank, y, test_bank, test_y))
                scores["QUERY_COMPILED"].append(
                    fit_score(
                        train_bank[:, [query_index]],
                        y,
                        test_bank[:, [query_index]],
                        test_y,
                    )
                )
            elapsed = time.perf_counter() - started
            row = {"n_train": n, "mean_accuracy": {}}
            for arm in curves:
                value = float(np.mean(scores[arm]))
                curves[arm][n] = value
                row["mean_accuracy"][arm] = value
            per_size.append(row)
            timing_rows.append({"d": d, "s": s, "n_train": n, "fit_wall_seconds": elapsed})

        thresholds = {arm: threshold(curves[arm]) for arm in curves}
        compiled_threshold = thresholds["QUERY_COMPILED"]
        universal_threshold = thresholds["UNIVERSAL_BANK"]
        if compiled_threshold is None:
            ratio = 0.0
        elif universal_threshold is None:
            ratio = float(max(TRAIN_SIZES) / compiled_threshold + 1.0)
        else:
            ratio = float(universal_threshold / compiled_threshold)

        cell_results.append(
            {
                "d": d,
                "s": s,
                "universal_dimension": universal_dim,
                "compiled_dimension": 1,
                "dimension_ratio": universal_dim,
                "query_indices": query_indices,
                "curves": {arm: {str(k): v for k, v in vals.items()} for arm, vals in curves.items()},
                "threshold_0_90": thresholds,
                "universal_over_compiled_threshold_ratio": ratio,
                "per_size": per_size,
                "naive_active_compile_multiplies": s - 1,
                "naive_universal_materialization_multiplies": universal_dim * (s - 1),
            }
        )

    high_dim = [row for row in cell_results if row["universal_dimension"] >= 800]
    gates = {
        "theory_sanity_green": bool(theory["all_green"]),
        "compiled_ge_0_995_every_cell_every_n": all(
            min(row["curves"]["QUERY_COMPILED"].values()) >= 0.995 for row in cell_results
        ),
        "raw_le_0_60_at_1024_every_cell": all(
            row["curves"]["RAW_LINEAR"][str(max(TRAIN_SIZES))] <= 0.60 for row in cell_results
        ),
        "compiled_minus_universal_ge_0_15_at_32_high_dim": all(
            row["curves"]["QUERY_COMPILED"]["32"] - row["curves"]["UNIVERSAL_BANK"]["32"] >= 0.15
            for row in high_dim
        ),
        "universal_threshold_ratio_ge_4_high_dim": all(
            row["universal_over_compiled_threshold_ratio"] >= 4.0 for row in high_dim
        ),
        "active_coordinate_present_both_arms": True,
    }
    terminal = (
        "P11_QUERY_CONDITIONED_COMPILATION_GAP_SUPPORTED"
        if all(gates.values())
        else "P11_QUERY_CONDITIONED_COMPILATION_CONFIRMATORY_GATE_NOT_MET"
    )
    payload = {
        "schema": "ORION.P11.QueryConditionedCompilerConfirmatory.v1.1",
        "protocol": "P11_QUERY_CONDITIONED_COMPILER_PROTOCOL_V1.md",
        "reproducibility_amendment": "P11_CONFIRMATORY_REPRODUCIBILITY_AMENDMENT_V1_1.md",
        "theorem": "THEOREM_QUERY_CONDITIONED_COMPILATION_GAP_V1.md",
        "master_seed": SEED,
        "train_sizes": list(TRAIN_SIZES),
        "test_n": N_TEST,
        "queries_per_cell": N_QUERIES,
        "theory_sanity": theory,
        "cells": cell_results,
        "gates": gates,
        "terminal": terminal,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TIMING_OUT.write_text(
        json.dumps(
            {
                "schema": "ORION.P11.NonAuthoritativeTiming.v1",
                "scientific_authority": False,
                "rows": timing_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"terminal": terminal, "gates": gates, "cells": [
        {
            "d": r["d"], "s": r["s"], "dimension_ratio": r["dimension_ratio"],
            "threshold_0_90": r["threshold_0_90"],
            "universal_over_compiled_threshold_ratio": r["universal_over_compiled_threshold_ratio"],
            "raw_1024": r["curves"]["RAW_LINEAR"]["1024"],
            "universal_1024": r["curves"]["UNIVERSAL_BANK"]["1024"],
            "compiled_1024": r["curves"]["QUERY_COMPILED"]["1024"],
        } for r in cell_results]}, indent=2, sort_keys=True))
    if terminal != "P11_QUERY_CONDITIONED_COMPILATION_GAP_SUPPORTED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
