#!/usr/bin/env python3
"""Outcome-blind hostile controls for the C-NBR2 nearest-anchor repair."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
EXECUTOR = HERE / "certified_neighborhood_conformal.py"


def load_executor():
    spec = importlib.util.spec_from_file_location("cnbr2_recovery_subject", EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load C-NBR2 executor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run() -> dict[str, object]:
    module = load_executor()
    original_mu = module.MU_K
    module.MU_K = 2
    try:
        anchors = np.asarray(
            [
                [10.0, 0.0],
                [0.0, 0.0],
                [5.0, 0.0],
            ],
            dtype=float,
        )
        regrets = np.asarray(
            [
                [9.0, 1.0],
                [0.0, 8.0],
                [3.0, 2.0],
            ],
            dtype=float,
        )
        query = np.asarray(
            [
                [0.25, 0.0],
                [4.50, 0.0],
                [9.50, 0.0],
            ],
            dtype=float,
        )
        distances = module.pairwise_distances(query, anchors)
        expected = np.min(distances, axis=1)
        defective = distances[:, 0]
        mean_regret, d1, action = module.neighborhood_predictor(
            anchors, regrets, query
        )
        if not np.array_equal(d1, expected):
            raise AssertionError((d1, expected))
        if np.array_equal(d1, defective):
            raise AssertionError("hostile subject did not distinguish rowwise nearest anchor")

        permutation = np.asarray([2, 0, 1], dtype=int)
        permuted_mean, permuted_d1, permuted_action = module.neighborhood_predictor(
            anchors[permutation], regrets[permutation], query
        )
        if not np.array_equal(d1, permuted_d1):
            raise AssertionError("nearest-anchor distance depends on anchor row order")
        if not np.array_equal(mean_regret, permuted_mean):
            raise AssertionError("neighbor regret mean depends on anchor row order")
        if not np.array_equal(action, permuted_action):
            raise AssertionError("selected base action depends on anchor row order")

        source = EXECUTOR.read_text(encoding="utf-8")
        if "d1 = distances[:, 0]" in source:
            raise AssertionError("defective predictor column-zero projection remains")
        if ")[:, 0]\n        arm[\"receipt\"][\"covered_median_d1\"]" in source:
            raise AssertionError("defective geometry column-zero projection remains")
        if source.count(".min(axis=1)") < 2:
            raise AssertionError("rowwise nearest-anchor semantics not explicit twice")

        return {
            "schema": "ORION02.CNBR2.NearestAnchorRecoveryControl.v2",
            "terminal": "C_NBR2_NEAREST_ANCHOR_DEFECT_ONLY_REPAIR_PASS",
            "queries": len(query),
            "anchors": len(anchors),
            "expected_d1": [float(value) for value in expected],
            "defective_column_zero_d1": [float(value) for value in defective],
            "anchor_permutation": [int(value) for value in permutation],
            "controls": {
                "rowwise_minimum_exact": True,
                "defective_column_zero_distinguished": True,
                "anchor_permutation_d1_invariant": True,
                "anchor_permutation_mean_regret_invariant": True,
                "anchor_permutation_action_invariant": True,
                "defective_source_expressions_absent": True,
            },
            "authority": {
                "outcome_data_read": False,
                "scientific_result": False,
                "external_independence": False,
                "journal_authority": False,
            },
        }
    finally:
        module.MU_K = original_mu


def main() -> int:
    import json

    result = run()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
