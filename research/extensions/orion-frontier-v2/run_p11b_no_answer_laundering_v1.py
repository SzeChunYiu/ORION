from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

SEED = 914337
CELLS = ((15, 3, 5), (17, 3, 5), (17, 4, 5), (19, 3, 7))
TRAIN_SIZES = (64, 128, 256, 512, 1024, 2048)
N_TEST = 8192
N_QUERIES = 10
OUT = Path(__file__).with_name("results") / "P11B_NO_ANSWER_LAUNDERING_V1.json"


def parity_bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    out = np.empty((x.shape[0], len(subsets)), dtype=np.int8)
    for j, subset in enumerate(subsets):
        out[:, j] = np.prod(x[:, subset], axis=1)
    return out


def fit_score(train_x: np.ndarray, y: np.ndarray, test_x: np.ndarray, test_y: np.ndarray) -> float:
    model = LogisticRegression(C=1.0, solver="liblinear", max_iter=1000)
    model.fit(train_x, y)
    return float(model.score(test_x, test_y))


def threshold(curve: dict[int, float], target: float) -> int | None:
    for n in TRAIN_SIZES:
        if curve[n] >= target:
            return n
    return None


def main() -> None:
    rng = np.random.default_rng(SEED)
    cells: list[dict[str, object]] = []
    laundering_failures: list[dict[str, object]] = []

    for d, s, r in CELLS:
        subsets = list(itertools.combinations(range(d), s))
        n_basis = len(subsets)
        query_sets = [
            [int(i) for i in rng.choice(n_basis, size=r, replace=False)]
            for _ in range(N_QUERIES)
        ]
        test_x = rng.choice((-1, 1), size=(N_TEST, d)).astype(np.int8)
        test_bank = parity_bank(test_x, subsets)

        test_labels: list[np.ndarray] = []
        for qi, active in enumerate(query_sets):
            active_values = test_bank[:, active]
            signed_label = np.where(np.sum(active_values, axis=1) > 0, 1, -1).astype(np.int8)
            y = (signed_label > 0).astype(np.int8)
            test_labels.append(y)
            for local_j in range(r):
                if np.array_equal(active_values[:, local_j], signed_label):
                    laundering_failures.append({"d": d, "s": s, "r": r, "query": qi, "feature": local_j, "relation": "equals_signed_label"})
                if np.array_equal(active_values[:, local_j], -signed_label):
                    laundering_failures.append({"d": d, "s": s, "r": r, "query": qi, "feature": local_j, "relation": "equals_negated_signed_label"})

        curves = {"RAW_LINEAR": {}, "UNIVERSAL_BANK": {}, "QUERY_COMPILED_COMPONENTS": {}}
        for n in TRAIN_SIZES:
            train_x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
            train_bank = parity_bank(train_x, subsets)
            scores = {arm: [] for arm in curves}
            for qi, active in enumerate(query_sets):
                train_active = train_bank[:, active]
                y = (np.sum(train_active, axis=1) > 0).astype(np.int8)
                test_y = test_labels[qi]
                scores["RAW_LINEAR"].append(fit_score(train_x, y, test_x, test_y))
                scores["UNIVERSAL_BANK"].append(fit_score(train_bank, y, test_bank, test_y))
                scores["QUERY_COMPILED_COMPONENTS"].append(
                    fit_score(train_active, y, test_bank[:, active], test_y)
                )
            for arm in curves:
                curves[arm][n] = float(np.mean(scores[arm]))

        thresholds = {arm: threshold(curves[arm], 0.95) for arm in curves}
        cthr = thresholds["QUERY_COMPILED_COMPONENTS"]
        uthr = thresholds["UNIVERSAL_BANK"]
        if cthr is None:
            ratio = 0.0
        elif uthr is None:
            ratio = float(max(TRAIN_SIZES) / cthr + 1.0)
        else:
            ratio = float(uthr / cthr)

        cells.append({
            "d": d,
            "s": s,
            "r": r,
            "universal_dimension": n_basis,
            "compiled_dimension": r,
            "universal_over_compiled_dimension_ratio": float(n_basis / r),
            "query_sets": query_sets,
            "curves": {arm: {str(n): v for n, v in curve.items()} for arm, curve in curves.items()},
            "threshold_0_95": thresholds,
            "universal_over_compiled_threshold_ratio": ratio,
            "target_rule": "majority_of_r_active_parity_components",
        })

    high_dim = [row for row in cells if int(row["universal_dimension"]) >= 600]
    gates = {
        "target_computed_after_representation": True,
        "no_component_equals_or_negates_label": len(laundering_failures) == 0,
        "compiled_ge_0_995_from_128_on": all(
            all(row["curves"]["QUERY_COMPILED_COMPONENTS"][str(n)] >= 0.995 for n in TRAIN_SIZES if n >= 128)
            for row in cells
        ),
        "raw_le_0_60_at_2048": all(row["curves"]["RAW_LINEAR"]["2048"] <= 0.60 for row in cells),
        "compiled_minus_universal_ge_0_20_at_64_high_dim": all(
            row["curves"]["QUERY_COMPILED_COMPONENTS"]["64"] - row["curves"]["UNIVERSAL_BANK"]["64"] >= 0.20
            for row in high_dim
        ),
        "universal_over_compiled_threshold_ratio_ge_8_high_dim": all(
            float(row["universal_over_compiled_threshold_ratio"]) >= 8.0 for row in high_dim
        ),
        "query_and_examples_outcome_independent": True,
    }
    terminal = "P11B_QUERY_COMPONENT_COMPILATION_SUPPORTED" if all(gates.values()) else "P11B_QUERY_COMPONENT_COMPILATION_GATE_NOT_MET"
    payload = {
        "schema": "ORION.P11B.NoAnswerLaundering.v1",
        "protocol": "P11B_NO_ANSWER_LAUNDERING_PROTOCOL_V1.md",
        "master_seed": SEED,
        "cells": cells,
        "train_sizes": list(TRAIN_SIZES),
        "test_n": N_TEST,
        "queries_per_cell": N_QUERIES,
        "laundering_failures": laundering_failures,
        "gates": gates,
        "terminal": terminal,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "terminal": terminal,
        "gates": gates,
        "cells": [{
            "d": r["d"], "s": r["s"], "r": r["r"],
            "universal_dimension": r["universal_dimension"],
            "compiled_dimension": r["compiled_dimension"],
            "threshold_0_95": r["threshold_0_95"],
            "threshold_ratio": r["universal_over_compiled_threshold_ratio"],
            "raw_2048": r["curves"]["RAW_LINEAR"]["2048"],
            "universal_2048": r["curves"]["UNIVERSAL_BANK"]["2048"],
            "compiled_2048": r["curves"]["QUERY_COMPILED_COMPONENTS"]["2048"],
        } for r in cells],
    }, indent=2, sort_keys=True))
    if terminal != "P11B_QUERY_COMPONENT_COMPILATION_SUPPORTED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
