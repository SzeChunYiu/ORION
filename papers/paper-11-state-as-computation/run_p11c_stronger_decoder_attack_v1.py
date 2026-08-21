from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression

SEED = 2026082111
CELLS = ((17, 4, 5), (19, 3, 7))
TRAIN_SIZES = (64, 128, 256, 512, 1024, 2048)
N_TEST = 8192
N_QUERIES = 5
TARGET = 0.95
OUT = Path(__file__).with_name("P11C_STRONGER_DECODER_ATTACK_RESULT_V1.json")


def parity_bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    out = np.empty((x.shape[0], len(subsets)), dtype=np.int8)
    for j, subset in enumerate(subsets):
        out[:, j] = np.prod(x[:, subset], axis=1)
    return out


def l2() -> LogisticRegression:
    return LogisticRegression(C=1.0, solver="liblinear", max_iter=1000)


def l1() -> LogisticRegression:
    return LogisticRegression(C=0.1, penalty="l1", solver="liblinear", max_iter=1000)


def threshold(curve: dict[int, float]) -> int | None:
    for n in TRAIN_SIZES:
        if curve[n] >= TARGET:
            return n
    return None


def main() -> None:
    rng = np.random.default_rng(SEED)
    cells = []
    laundering_failures = []

    for cell_index, (d, s, r) in enumerate(CELLS):
        subsets = list(itertools.combinations(range(d), s))
        n_basis = len(subsets)
        query_sets = [
            [int(i) for i in rng.choice(n_basis, size=r, replace=False)]
            for _ in range(N_QUERIES)
        ]
        test_x = rng.choice((-1, 1), size=(N_TEST, d)).astype(np.int8)
        test_bank = parity_bank(test_x, subsets)
        test_y = []
        for qi, active in enumerate(query_sets):
            values = test_bank[:, active]
            signed = np.where(values.sum(axis=1) > 0, 1, -1).astype(np.int8)
            test_y.append((signed > 0).astype(np.int8))
            for j in range(r):
                if np.array_equal(values[:, j], signed):
                    laundering_failures.append([cell_index, qi, j, "equals"])
                if np.array_equal(values[:, j], -signed):
                    laundering_failures.append([cell_index, qi, j, "negates"])

        curves = {
            "UNIVERSAL_L2": {},
            "UNIVERSAL_L1": {},
            "UNIVERSAL_EXTRA_TREES": {},
            "COMPILED_L2": {},
        }
        for n in TRAIN_SIZES:
            train_x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
            train_bank = parity_bank(train_x, subsets)
            score_lists = {k: [] for k in curves}
            for qi, active in enumerate(query_sets):
                train_active = train_bank[:, active]
                y = (train_active.sum(axis=1) > 0).astype(np.int8)
                ty = test_y[qi]

                m = l2()
                m.fit(train_bank, y)
                score_lists["UNIVERSAL_L2"].append(float(m.score(test_bank, ty)))

                m = l1()
                m.fit(train_bank, y)
                score_lists["UNIVERSAL_L1"].append(float(m.score(test_bank, ty)))

                m = ExtraTreesClassifier(
                    n_estimators=256,
                    max_features="sqrt",
                    random_state=SEED + 1000 * cell_index + qi,
                    n_jobs=-1,
                )
                m.fit(train_bank, y)
                score_lists["UNIVERSAL_EXTRA_TREES"].append(float(m.score(test_bank, ty)))

                m = l2()
                m.fit(train_active, y)
                score_lists["COMPILED_L2"].append(
                    float(m.score(test_bank[:, active], ty))
                )

            for arm in curves:
                curves[arm][n] = float(np.mean(score_lists[arm]))

        thresholds = {arm: threshold(curves[arm]) for arm in curves}
        universal_arms = ("UNIVERSAL_L2", "UNIVERSAL_L1", "UNIVERSAL_EXTRA_TREES")
        reached = [thresholds[a] for a in universal_arms if thresholds[a] is not None]
        best_universal_threshold = min(reached) if reached else None
        compiled_threshold = thresholds["COMPILED_L2"]
        best_universal_64 = max(curves[a][64] for a in universal_arms)
        ratio_gate = (
            compiled_threshold is not None
            and (
                best_universal_threshold is None
                or best_universal_threshold >= 4 * compiled_threshold
            )
        )
        cells.append(
            {
                "d": d,
                "s": s,
                "r": r,
                "universal_dimension": n_basis,
                "compiled_dimension": r,
                "query_sets": query_sets,
                "curves": {
                    arm: {str(n): value for n, value in curve.items()}
                    for arm, curve in curves.items()
                },
                "threshold_0_95": thresholds,
                "best_universal_threshold_0_95": best_universal_threshold,
                "compiled_threshold_0_95": compiled_threshold,
                "best_universal_over_compiled_threshold_ratio_gate": ratio_gate,
                "compiled_minus_best_universal_at_64": curves["COMPILED_L2"][64]
                - best_universal_64,
            }
        )

    gates = {
        "no_answer_laundering": not laundering_failures,
        "compiled_reaches_by_64": all(
            row["compiled_threshold_0_95"] is not None
            and row["compiled_threshold_0_95"] <= 64
            for row in cells
        ),
        "best_universal_threshold_ratio_ge_4": all(
            row["best_universal_over_compiled_threshold_ratio_gate"] for row in cells
        ),
        "compiled_minus_best_universal_at_64_ge_0_20": all(
            row["compiled_minus_best_universal_at_64"] >= 0.20 for row in cells
        ),
    }
    terminal = (
        "P11C_STRONGER_DECODER_GAP_SUPPORTED"
        if all(gates.values())
        else "P11C_STRONGER_DECODER_GAP_NOT_MET"
    )
    payload = {
        "schema": "ORION.P11C.StrongerDecoderAttack.v1",
        "protocol": "P11C_STRONGER_DECODER_ATTACK_PROTOCOL_V1.md",
        "seed": SEED,
        "cells": cells,
        "train_sizes": list(TRAIN_SIZES),
        "test_n": N_TEST,
        "queries_per_cell": N_QUERIES,
        "laundering_failures": laundering_failures,
        "gates": gates,
        "terminal": terminal,
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(json.dumps({
        "terminal": terminal,
        "gates": gates,
        "cells": [{
            "cell": [r["d"], r["s"], r["r"]],
            "thresholds": r["threshold_0_95"],
            "delta64": r["compiled_minus_best_universal_at_64"],
        } for r in cells],
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }, indent=2, sort_keys=True))
    if terminal != "P11C_STRONGER_DECODER_GAP_SUPPORTED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
