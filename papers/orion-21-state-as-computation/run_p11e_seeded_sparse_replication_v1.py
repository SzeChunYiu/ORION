from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

SEED = 2026082117
CELLS = ((17, 4, 5), (19, 3, 7))
TRAIN_SIZES = (64, 128, 256, 512, 1024, 2048)
N_TEST = 8192
N_QUERIES = 5
OUT = Path(__file__).with_name("P11E_SEEDED_SPARSE_REPLICATION_RESULT_V1.json")


def bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    idx = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, idx], axis=2, dtype=np.int8)


def threshold(curve: dict[int, float]) -> int | None:
    for n in TRAIN_SIZES:
        if curve[n] >= 0.95:
            return n
    return None


def model_seed(cell_i: int, query_i: int, n: int, arm_offset: int) -> int:
    return SEED + 100_000 * arm_offset + 10_000 * cell_i + 100 * query_i + n


def main() -> None:
    rng = np.random.default_rng(SEED)
    cells = []
    laundering_failures = []

    for ci, (d, s, r) in enumerate(CELLS):
        subsets = list(itertools.combinations(range(d), s))
        nb = len(subsets)
        queries = [rng.choice(nb, size=r, replace=False).tolist() for _ in range(N_QUERIES)]
        test_x = rng.choice((-1, 1), size=(N_TEST, d)).astype(np.int8)
        test_bank = bank(test_x, subsets)
        test_y = []
        for qi, active in enumerate(queries):
            vals = test_bank[:, active]
            signed = np.where(vals.sum(axis=1) > 0, 1, -1).astype(np.int8)
            test_y.append((signed > 0).astype(np.int8))
            for j in range(r):
                if np.array_equal(vals[:, j], signed):
                    laundering_failures.append([ci, qi, j, "equals"])
                if np.array_equal(vals[:, j], -signed):
                    laundering_failures.append([ci, qi, j, "negates"])

        curves = {"UNIVERSAL_L1": {}, "COMPILED_L2": {}}
        for n in TRAIN_SIZES:
            x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
            b = bank(x, subsets)
            scores = {k: [] for k in curves}
            for qi, active in enumerate(queries):
                y = (b[:, active].sum(axis=1) > 0).astype(np.int8)

                m = LogisticRegression(
                    C=0.1,
                    penalty="l1",
                    solver="liblinear",
                    max_iter=1000,
                    random_state=model_seed(ci, qi, n, 1),
                )
                m.fit(b, y)
                scores["UNIVERSAL_L1"].append(float(m.score(test_bank, test_y[qi])))

                m = LogisticRegression(
                    C=1.0,
                    solver="liblinear",
                    max_iter=1000,
                    random_state=model_seed(ci, qi, n, 2),
                )
                m.fit(b[:, active], y)
                scores["COMPILED_L2"].append(float(m.score(test_bank[:, active], test_y[qi])))

            for arm in curves:
                curves[arm][n] = float(np.mean(scores[arm]))

        thresholds = {arm: threshold(curve) for arm, curve in curves.items()}
        ct = thresholds["COMPILED_L2"]
        ut = thresholds["UNIVERSAL_L1"]
        ratio_gate = ct is not None and (ut is None or ut >= 2 * ct)
        cells.append({
            "cell": [d, s, r],
            "universal_dimension": nb,
            "compiled_dimension": r,
            "curves": {arm: {str(n): v for n, v in curve.items()} for arm, curve in curves.items()},
            "threshold_0_95": thresholds,
            "threshold_ratio_ge_2_gate": ratio_gate,
            "compiled_minus_sparse_at_64": curves["COMPILED_L2"][64] - curves["UNIVERSAL_L1"][64],
        })

    gates = {
        "no_answer_laundering": not laundering_failures,
        "compiled_by_64": all(c["threshold_0_95"]["COMPILED_L2"] is not None and c["threshold_0_95"]["COMPILED_L2"] <= 64 for c in cells),
        "sparse_threshold_ge_128": all(c["threshold_0_95"]["UNIVERSAL_L1"] is None or c["threshold_0_95"]["UNIVERSAL_L1"] >= 128 for c in cells),
        "threshold_ratio_ge_2": all(c["threshold_ratio_ge_2_gate"] for c in cells),
        "delta64_ge_0_20": all(c["compiled_minus_sparse_at_64"] >= 0.20 for c in cells),
    }
    terminal = "P11E_SEEDED_SPARSE_RESIDUAL_REPLICATED" if all(gates.values()) else "P11E_SEEDED_SPARSE_RESIDUAL_NOT_REPLICATED"
    payload = {
        "schema": "ORION.P11E.SeededSparseReplication.v1",
        "protocol": "P11E_SEEDED_SPARSE_REPLICATION_PROTOCOL_V1.md",
        "seed": SEED,
        "cells": cells,
        "laundering_failures": laundering_failures,
        "gates": gates,
        "terminal": terminal,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(json.dumps({
        "terminal": terminal,
        "cells": [{"cell": c["cell"], "thresholds": c["threshold_0_95"], "delta64": c["compiled_minus_sparse_at_64"]} for c in cells],
        "gates": gates,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }, indent=2, sort_keys=True))
    if terminal != "P11E_SEEDED_SPARSE_RESIDUAL_REPLICATED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
