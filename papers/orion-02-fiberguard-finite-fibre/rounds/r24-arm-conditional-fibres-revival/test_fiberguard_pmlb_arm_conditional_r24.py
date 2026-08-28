#!/usr/bin/env python3
"""Pre-outcome hostile tests for the ORION-02 R24 revival mechanism."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


EXECUTOR = Path(__file__).with_name("fiberguard_pmlb_arm_conditional_r24.py")


def load_executor():
    spec = importlib.util.spec_from_file_location("orion02_r24_executor", EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R24 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DensityRadiusTests(unittest.TestCase):
    def test_radius_is_smallest_hamming_ball_with_two_expected_members(self) -> None:
        module = load_executor()
        self.assertEqual(module.minimum_density_radius(n_bits=7, shield_n=15), 2)
        self.assertEqual(module.minimum_density_radius(n_bits=4, shield_n=15), 1)
        self.assertGreaterEqual(module.expected_ball_members(7, 15, 2), 2.0)
        self.assertLess(module.expected_ball_members(7, 15, 1), 2.0)


class ArmConditionalPoolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.query = np.array([1, 1, 1, 1, 1, 1, 1], dtype=np.int8)
        self.cells = {
            "a": np.array([1, 1, 1, 1, 1, 1, 0], dtype=np.int8),
            "b": np.array([1, 1, 1, 1, 1, 0, 0], dtype=np.int8),
            "c": np.array([1, 1, 1, 1, 0, 0, 0], dtype=np.int8),
            "d": np.array([0, 0, 0, 0, 0, 0, 0], dtype=np.int8),
        }
        self.excess = {"a": 0.004, "b": 0.019, "c": 0.018, "d": 0.020}

    def test_pool_uses_only_local_tau_good_members(self) -> None:
        module = load_executor()
        members = module.arm_conditional_boundary_pool(
            self.query, self.cells, self.excess, tau=0.02, radius=2, k=2
        )
        self.assertEqual(members, ["b", "a"])

    def test_boundary_witness_is_preferred_over_optimistic_low_excess(self) -> None:
        module = load_executor()
        cells = dict(self.cells)
        cells["e"] = np.array([1, 1, 1, 1, 1, 0, 1], dtype=np.int8)
        excess = {**self.excess, "e": 0.017}
        members = module.arm_conditional_boundary_pool(
            self.query, cells, excess, tau=0.02, radius=2, k=2
        )
        self.assertEqual(members, ["b", "e"])
        self.assertAlmostEqual(max(excess[name] for name in members), 0.019)

    def test_members_beyond_radius_or_above_tau_are_rejected(self) -> None:
        module = load_executor()
        excess = dict(self.excess)
        excess["b"] = 0.0200001
        members = module.arm_conditional_boundary_pool(
            self.query, self.cells, excess, tau=0.02, radius=2, k=2
        )
        self.assertEqual(members, [])

    def test_selection_is_invariant_to_mapping_insertion_order(self) -> None:
        module = load_executor()
        before = module.arm_conditional_boundary_pool(
            self.query, self.cells, self.excess, tau=0.02, radius=2, k=2
        )
        after = module.arm_conditional_boundary_pool(
            self.query,
            dict(reversed(list(self.cells.items()))),
            dict(reversed(list(self.excess.items()))),
            tau=0.02,
            radius=2,
            k=2,
        )
        self.assertEqual(before, after)

    def test_lexical_control_ignores_geometry_but_keeps_good_boundary_rule(self) -> None:
        module = load_executor()
        members = module.lexical_good_boundary_pool(self.excess, tau=0.02, k=2)
        self.assertEqual(members, ["d", "b"])


class TerminalTests(unittest.TestCase):
    def test_coverage_then_strict_validity_precedence(self) -> None:
        module = load_executor()
        payload = {
            "hostile_controls": {"fixture": True},
            "coverage": {"r23_parent": 0.73, "r24_primary": 0.94, "target": 0.95},
            "primary": {"certified_n": 40, "violations_strict": 0},
        }
        self.assertEqual(
            module.decide_terminal(payload),
            "C_R24_ARM_CONDITIONAL_COVERAGE_IMPROVED_BELOW_GATE",
        )
        payload["coverage"]["r24_primary"] = 0.96
        payload["primary"]["violations_strict"] = 5
        self.assertEqual(
            module.decide_terminal(payload),
            "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID",
        )


if __name__ == "__main__":
    unittest.main()
