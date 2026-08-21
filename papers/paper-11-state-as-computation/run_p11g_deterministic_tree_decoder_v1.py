from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression

SEED = 2026082120
CELLS = ((17, 4, 5), (19, 3, 7))
TRAIN_SIZES = (64, 128, 256, 512, 1024)
N_TEST = 4096
N_QUERIES = 3
N_TREES = 96
OUT = Path(__file__).with_name("P11G_DETERMINISTIC_TREE_DECODER_RESULT_V1.json")


def bank(x: np.ndarray, subsets: list[tuple[int, ...]]) -> np.ndarray:
    idx = np.asarray(subsets, dtype=np.int16)
    return np.prod(x[:, idx], axis=2, dtype=np.int8)


def threshold(curve: dict[int, float]) -> int | None:
    for n in TRAIN_SIZES:
        if curve[n] >= 0.95:
            return n
    return None


def tree_seed(ci: int, qi: int, n: int) -> int:
    return SEED + 10_000 * ci + 100 * qi + n


def compiled_seed(ci: int, qi: int, n: int) -> int:
    return SEED + 100_000 + 10_000 * ci + 100 * qi + n


def scientific_payload() -> dict[str, object]:
    rng = np.random.default_rng(SEED)
    cells: list[dict[str, object]] = []
    laundering_failures: list[list[object]] = []

    for ci, (d, s, r) in enumerate(CELLS):
        subsets = list(itertools.combinations(range(d), s))
        nb = len(subsets)
        queries = [rng.choice(nb, size=r, replace=False).tolist() for _ in range(N_QUERIES)]
        test_x = rng.choice((-1, 1), size=(N_TEST, d)).astype(np.int8)
        test_bank = bank(test_x, subsets)
        test_y: list[np.ndarray] = []

        for qi, active in enumerate(queries):
            vals = test_bank[:, active]
            signed = np.where(vals.sum(axis=1) > 0, 1, -1).astype(np.int8)
            test_y.append((signed > 0).astype(np.int8))
            for j in range(r):
                if np.array_equal(vals[:, j], signed):
                    laundering_failures.append([ci, qi, j, "equals"])
                if np.array_equal(vals[:, j], -signed):
                    laundering_failures.append([ci, qi, j, "negates"])

        curves: dict[str, dict[int, float]] = {
            "UNIVERSAL_EXTRA_TREES": {},
            "COMPILED_L2": {},
        }
        for n in TRAIN_SIZES:
            x = rng.choice((-1, 1), size=(n, d)).astype(np.int8)
            b = bank(x, subsets)
            scores = {k: [] for k in curves}

            for qi, active in enumerate(queries):
                y = (b[:, active].sum(axis=1) > 0).astype(np.int8)

                tree = ExtraTreesClassifier(
                    n_estimators=N_TREES,
                    max_features="sqrt",
                    random_state=tree_seed(ci, qi, n),
                    n_jobs=1,
                )
                tree.fit(b, y)
                scores["UNIVERSAL_EXTRA_TREES"].append(float(tree.score(test_bank, test_y[qi])))

                compiled = LogisticRegression(
                    C=1.0,
                    solver="liblinear",
                    max_iter=1000,
                    random_state=compiled_seed(ci, qi, n),
                )
                compiled.fit(b[:, active], y)
                scores["COMPILED_L2"].append(float(compiled.score(test_bank[:, active], test_y[qi])))

            for arm in curves:
                curves[arm][n] = float(np.mean(scores[arm]))

        thresholds = {arm: threshold(curve) for arm, curve in curves.items()}
        cells.append(
            {
                "cell": [d, s, r],
                "universal_dimension": nb,
                "compiled_dimension": r,
                "curves": {
                    arm: {str(n): v for n, v in curve.items()}
                    for arm, curve in curves.items()
                },
                "threshold_0_95": thresholds,
                "compiled_minus_tree_at_64": (
                    curves["COMPILED_L2"][64] - curves["UNIVERSAL_EXTRA_TREES"][64]
                ),
            }
        )

    scientific_gates = {
        "no_answer_laundering": not laundering_failures,
        "compiled_by_64": all(
            c["threshold_0_95"]["COMPILED_L2"] is not None
            and c["threshold_0_95"]["COMPILED_L2"] <= 64
            for c in cells
        ),
        "tree_threshold_ge_256": all(
            c["threshold_0_95"]["UNIVERSAL_EXTRA_TREES"] is None
            or c["threshold_0_95"]["UNIVERSAL_EXTRA_TREES"] >= 256
            for c in cells
        ),
        "delta64_ge_0_20": all(c["compiled_minus_tree_at_64"] >= 0.20 for c in cells),
    }

    return {
        "schema": "ORION.P11G.DeterministicTreeDecoder.ScientificPayload.v1",
        "protocol": "P11G_DETERMINISTIC_TREE_DECODER_PROTOCOL_V1.md",
        "seed": SEED,
        "n_trees": N_TREES,
        "n_jobs": 1,
        "cells": cells,
        "laundering_failures": laundering_failures,
        "scientific_gates": scientific_gates,
    }


def canonical_text(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def write_once(path: Path) -> None:
    path.write_text(canonical_text(scientific_payload()), encoding="utf-8")


def authoritative_main() -> None:
    with tempfile.TemporaryDirectory(prefix="p11g-replay-") as td:
        root = Path(td)
        a = root / "a.json"
        b = root / "b.json"
        cmd_a = [sys.executable, str(Path(__file__).resolve()), "--once", str(a)]
        cmd_b = [sys.executable, str(Path(__file__).resolve()), "--once", str(b)]
        first = subprocess.run(cmd_a, check=False, capture_output=True, text=True)
        second = subprocess.run(cmd_b, check=False, capture_output=True, text=True)
        subprocess_success = first.returncode == 0 and second.returncode == 0
        if not subprocess_success:
            raise SystemExit(
                "P11G subprocess failure\n"
                + first.stdout
                + first.stderr
                + second.stdout
                + second.stderr
            )
        first_bytes = a.read_bytes()
        second_bytes = b.read_bytes()
        first_sha = hashlib.sha256(first_bytes).hexdigest()
        second_sha = hashlib.sha256(second_bytes).hexdigest()
        replay_match = first_bytes == second_bytes and first_sha == second_sha
        scientific = json.loads(first_bytes.decode("utf-8"))
        scientific_gates = dict(scientific["scientific_gates"])
        gates = dict(scientific_gates)
        gates["two_fresh_subprocess_payloads_byte_identical"] = replay_match
        gates["subprocesses_successful"] = subprocess_success
        terminal = (
            "P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED"
            if all(gates.values())
            else "P11G_DETERMINISTIC_TREE_DECODER_GAP_NOT_MET"
        )
        result = {
            "schema": "ORION.P11G.DeterministicTreeDecoder.v1",
            "protocol": "P11G_DETERMINISTIC_TREE_DECODER_PROTOCOL_V1.md",
            "scientific_payload": scientific,
            "replay": {
                "first_sha256": first_sha,
                "second_sha256": second_sha,
                "byte_identical": replay_match,
                "fresh_python_subprocesses": 2,
            },
            "gates": gates,
            "terminal": terminal,
        }
        text = canonical_text(result)
        OUT.write_text(text, encoding="utf-8")
        print(
            json.dumps(
                {
                    "terminal": terminal,
                    "replay": result["replay"],
                    "cells": [
                        {
                            "cell": c["cell"],
                            "thresholds": c["threshold_0_95"],
                            "delta64": c["compiled_minus_tree_at_64"],
                        }
                        for c in scientific["cells"]
                    ],
                    "gates": gates,
                    "authoritative_sha256": hashlib.sha256(text.encode()).hexdigest(),
                },
                indent=2,
                sort_keys=True,
            )
        )
        if terminal != "P11G_DETERMINISTIC_TREE_DECODER_GAP_SUPPORTED":
            raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", type=Path)
    args = parser.parse_args()
    if args.once is not None:
        write_once(args.once)
        return
    authoritative_main()


if __name__ == "__main__":
    main()
