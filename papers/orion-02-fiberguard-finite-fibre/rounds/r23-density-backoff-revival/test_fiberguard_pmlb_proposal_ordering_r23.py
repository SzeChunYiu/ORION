#!/usr/bin/env python3
"""Hostile tests for the prospectively frozen ORION-02 R23 revival."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


EXECUTOR = Path(__file__).with_name("fiberguard_pmlb_proposal_ordering_r23.py")


def load_executor():
    spec = importlib.util.spec_from_file_location("orion02_r23_executor", EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R23 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluatorCorrectionTests(unittest.TestCase):
    def test_f_star_is_best_shield_arm_not_scalar_grand_mean(self) -> None:
        module = load_executor()
        ctx, info = module.synthetic_fixture(mode=module.MODE_EXACT)
        # dct has the smallest mean endpoint on the shield table.  The old R22
        # evaluator stored a scalar grand mean here, which made fallback excess
        # negative and was not an executable portfolio arm.
        self.assertEqual(ctx.f_star_arm, "dct")
        self.assertIn(ctx.f_star_arm, module.PORTFOLIO)
        decision = ctx.fallback_decision(())
        self.assertEqual(decision["committed"], "dct")
        self.assertTrue(decision["fallback"])
        self.assertFalse(decision["certified"])
        for name in info["queries"]:
            self.assertGreaterEqual(module.excess_of(ctx, name, decision), -module.TOL)


class DensityBackoffTests(unittest.TestCase):
    def test_sparse_exact_cell_backs_off_to_fixed_two_hamming_nearest(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_sparse_fixture(mode=module.MODE_BACKOFF)
        members, used_backoff = ctx.selected_members("query", ("G1",))
        self.assertTrue(used_backoff)
        self.assertEqual(members, ["shield_b", "shield_c"])
        self.assertEqual(len(members), module.BACKOFF_K)

    def test_exact_cell_with_two_members_is_not_replaced(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_sparse_fixture(mode=module.MODE_BACKOFF)
        members, used_backoff = ctx.selected_members("query_dense", ())
        self.assertFalse(used_backoff)
        self.assertEqual(members, ["shield_a", "shield_c"])

    def test_backoff_selection_is_invariant_to_shield_input_order(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_sparse_fixture(mode=module.MODE_BACKOFF)
        before = ctx.selected_members("query", ("G1",))
        ctx.roles["shield_table"] = list(reversed(ctx.roles["shield_table"]))
        ctx._cells = {}
        after = ctx.selected_members("query", ("G1",))
        self.assertEqual(before, after)

    def test_query_inside_shield_table_fails_closed(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_sparse_fixture(mode=module.MODE_BACKOFF)
        ctx.roles["shield_table"].append("query")
        with self.assertRaises(AssertionError):
            ctx.selected_members("query", ("G1",))

    def test_lexical_pool_is_separate_negative_control(self) -> None:
        module = load_executor()
        backoff, _ = module.synthetic_sparse_fixture(mode=module.MODE_BACKOFF)
        negative, _ = module.synthetic_sparse_fixture(mode=module.MODE_LEXICAL_CONTROL)
        geo_members, _ = backoff.selected_members("query", ("G1",))
        neg_members, _ = negative.selected_members("query", ("G1",))
        self.assertEqual(geo_members, ["shield_b", "shield_c"])
        self.assertEqual(neg_members, ["shield_a", "shield_b"])
        self.assertNotEqual(geo_members, neg_members)


class ShieldAndCustodyTests(unittest.TestCase):
    def test_hostile_scorer_cannot_commit_outside_backoff_shield(self) -> None:
        module = load_executor()
        ctx, info = module.synthetic_fixture(mode=module.MODE_BACKOFF)

        def hostile(c, arm, name, acquired):
            admissible, _, _, _ = c.shield_query(name, acquired, module.TAU)
            forbidden = next(a for a in module.PORTFOLIO if a not in admissible)
            return {a: (0.0 if a == forbidden else 1.0) for a in module.PORTFOLIO}

        for name in info["queries"]:
            decision = module.walk_with_scorer(ctx, name, "STATIC_ADAPTIVE", module.TAU, hostile)
            admissible, _, _, _ = ctx.shield_query(name, tuple(decision["acquired"]), module.TAU)
            self.assertTrue(decision["fallback"] or decision["committed"] in admissible)

    def test_direct_difference_hamming_matches_elementwise(self) -> None:
        module = load_executor()
        q = np.array([0, 1, 1, 0, 1], dtype=np.int8)
        table = np.array([[0, 1, 0, 0, 1], [1, 0, 1, 0, 0]], dtype=np.int8)
        got = module.hamming_distances(q, table)
        expected = np.array([1, 3])
        np.testing.assert_array_equal(got, expected)


class TerminalTests(unittest.TestCase):
    def test_terminal_precedence_and_coverage_gate(self) -> None:
        module = load_executor()

        def payload(*, coverage=1.0, parent=0.0, violations=0, mean_diff=0.0, ci_upper=0.0,
                    primary_mean=0.10, static_mean=0.10, primary_cost=1.0, static_cost=1.0):
            return {
                "hostile_controls": {"fixture": True},
                "coverage": {
                    "r22c_exact_full_state": parent,
                    "r23_backoff_full_state": coverage,
                },
                "arms_summary": {
                    "R23_BACKOFF_PRIMARY_LEARNED": {"violations_strict": violations, "certified_n": 40, "n": 40},
                    "R23_BACKOFF_STATIC_ADAPTIVE": {"mean_excess": static_mean},
                },
                "primary_test": {
                    "mean_diff": mean_diff,
                    "ci_upper": ci_upper,
                    "primary_mean_excess": primary_mean,
                    "mean_groups_acquired_primary": primary_cost,
                    "mean_groups_acquired_static": static_cost,
                },
            }

        self.assertEqual(
            module.decide_terminal(payload(coverage=0.90, parent=0.0)),
            "C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE",
        )
        self.assertEqual(
            module.decide_terminal(payload(coverage=0.0, parent=0.0)),
            "C_R23_PMLB_BACKOFF_NO_COVERAGE_IMPROVEMENT",
        )
        self.assertEqual(
            module.decide_terminal(payload(coverage=1.0, parent=0.0, violations=5)),
            "C_R23_PMLB_BACKOFF_CERTIFICATE_INVALID",
        )
        self.assertEqual(
            module.decide_terminal(payload(coverage=1.0, parent=0.0, mean_diff=-0.01,
                                           ci_upper=-0.001, primary_mean=0.09, static_mean=0.10)),
            "C_R23_PMLB_BACKOFF_VALUE",
        )
        self.assertEqual(
            module.decide_terminal(payload(coverage=1.0, parent=0.0)),
            "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NULL",
        )


class WrapperContractTests(unittest.TestCase):
    def test_wrapper_requires_two_runs_byte_comparison_and_independent_verifier(self) -> None:
        script = Path(__file__).with_name("run_fiberguard_pmlb_proposal_ordering_r23_twice.sh").read_text()
        self.assertIn('run_one "run_a"', script)
        self.assertIn('run_one "run_b"', script)
        self.assertGreaterEqual(script.count("cmp -s"), 3)
        self.assertIn("verify_fiberguard_pmlb_proposal_ordering_r23.py", script)
        self.assertIn("preserve_failure_artifacts", script)
        self.assertIn("FAILED_EXECUTION_DIR", script)

    def test_slurm_binds_frozen_science_without_self_referential_head(self) -> None:
        script = Path(__file__).with_name("ORION02_R23_EXECUTION.slurm").read_text()
        self.assertNotIn('test "$(git rev-parse HEAD)"', script)
        self.assertIn("6bb4e377462249c3630ceacc56073ba385a82805c79eda58809c42b8ee1562aa", script)
        self.assertIn("54574ec9fa5364fb0ad8e5857678930dac3b4483f1b7a9da96829d8e6f0c447f", script)
        self.assertIn("4c8d57f8398d4575097eba16ac7fcd21e467745ad00cfa31df928358e59c6bed", script)


if __name__ == "__main__":
    unittest.main()
