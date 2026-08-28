#!/usr/bin/env python3
"""Tests for the independent ORION-02 R24 result verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


VERIFIER = Path(__file__).with_name("verify_fiberguard_pmlb_arm_conditional_r24.py")


def load_verifier():
    spec = importlib.util.spec_from_file_location("orion02_r24_verifier", VERIFIER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R24 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IndependentMechanicsTests(unittest.TestCase):
    def test_verifier_does_not_import_the_r24_executor(self) -> None:
        source = VERIFIER.read_text() if VERIFIER.exists() else ""
        self.assertNotIn("import fiberguard_pmlb_arm_conditional_r24", source)
        self.assertNotIn("from fiberguard_pmlb_arm_conditional_r24", source)

    def test_independent_density_radius(self) -> None:
        verifier = load_verifier()
        self.assertEqual(verifier.minimum_density_radius(7, 15), 2)
        self.assertEqual(verifier.minimum_density_radius(4, 15), 1)

    def test_independent_arm_pool_rebuilds_boundary_witnesses(self) -> None:
        verifier = load_verifier()
        query = (1, 1, 1, 1, 1, 1, 1)
        cells = {
            "a": (1, 1, 1, 1, 1, 1, 0),
            "b": (1, 1, 1, 1, 1, 0, 0),
            "c": (1, 1, 1, 1, 0, 0, 0),
        }
        excess = {"a": 0.004, "b": 0.019, "c": 0.018}
        self.assertEqual(
            verifier.independent_arm_pool(
                query, cells, excess, tau=0.02, radius=2, k=2
            ),
            ["b", "a"],
        )

    def test_record_comparison_tolerates_only_one_serialized_bound_unit(self) -> None:
        verifier = load_verifier()
        rebuilt = {
            "q": {
                "fold": 1,
                "arm_pools": {"hgb": ["a", "b"]},
                "arm_bounds": {"hgb": 0.017178063488},
                "arm_used_backoff": {"hgb": True},
                "admissible": ["hgb"],
                "best_arm": "hgb",
                "best_bound": 0.017178063488,
            }
        }
        stored = {"q": {**rebuilt["q"], "arm_bounds": {"hgb": 0.017178063489}}}
        self.assertTrue(verifier.full_state_records_match(rebuilt, stored))
        stored["q"]["arm_bounds"]["hgb"] = 0.017178063490
        self.assertFalse(verifier.full_state_records_match(rebuilt, stored))

    def test_terminal_is_derived_not_trusted(self) -> None:
        verifier = load_verifier()
        payload = {
            "hostile_controls": {"x": True},
            "coverage": {"r23_parent": 0.73, "r24_primary": 0.96, "target": 0.95},
            "primary": {"certified_n": 40, "violations_strict": 5},
            "matched_parent_test": {"mean_diff": -0.01, "ci_upper": -0.001},
            "negative_control_test": {"mean_diff": -0.01, "ci_upper": -0.001},
        }
        self.assertEqual(
            verifier.derive_terminal(payload),
            "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID",
        )


if __name__ == "__main__":
    unittest.main()
