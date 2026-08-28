#!/usr/bin/env python3
"""Pre-outcome hostile tests for the ORION-02 R24 revival mechanism."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


EXECUTOR = Path(__file__).with_name("fiberguard_pmlb_arm_conditional_r24.py")
WRAPPER = Path(__file__).with_name("run_fiberguard_pmlb_arm_conditional_r24_twice.sh")
SLURM = Path(__file__).with_name("ORION02_R24_EXECUTION.slurm")


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


class IntegratedShieldTests(unittest.TestCase):
    def test_each_arm_receives_its_own_exact_tau_good_fibre(self) -> None:
        module = load_executor()
        ctx, info = module.synthetic_fixture(mode=module.MODE_ARM_CONDITIONAL)
        pools, wc, used = ctx.arm_pools("query", ("G1",), module.TAU)
        self.assertNotIn("query", ctx.roles["shield_table"])
        for arm in module.PORTFOLIO:
            members = pools[arm]
            self.assertIn(len(members), (0, module.POOL_K))
            if members:
                self.assertLessEqual(wc[arm], module.TAU + module.TOL)
                self.assertAlmostEqual(
                    wc[arm], max(ctx.excess_member(name, arm) for name in members)
                )
                self.assertTrue(all(name in info["shield"] for name in members))
                self.assertTrue(used[arm] or len(members) >= module.POOL_K)

    def test_nontrivial_exact_arm_cell_is_preserved(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_fixture(mode=module.MODE_ARM_CONDITIONAL)
        pools, _, used = ctx.arm_pools("query_dense", (), module.TAU)
        self.assertEqual(pools["dct"], ["shield_a", "shield_c"])
        self.assertFalse(used["dct"])

    def test_hostile_scorer_cannot_commit_an_uncertified_arm(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_fixture(mode=module.MODE_ARM_CONDITIONAL)

        def hostile(c, arm, name, acquired):
            pools, wc, _ = c.arm_pools(name, acquired, module.TAU)
            forbidden = next(a for a in module.PORTFOLIO if not pools[a])
            return {a: (0.0 if a == forbidden else 1.0) for a in module.PORTFOLIO}

        decision = module.walk_with_scorer(
            ctx, "query", "STATIC_ADAPTIVE", module.TAU, hostile
        )
        pools, _, _ = ctx.arm_pools(
            "query", tuple(decision["acquired"]), module.TAU
        )
        self.assertTrue(decision["fallback"] or bool(pools[decision["committed"]]))

    def test_query_inside_shield_table_fails_closed(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_fixture(mode=module.MODE_ARM_CONDITIONAL)
        ctx.roles["shield_table"].append("query")
        with self.assertRaises(AssertionError):
            ctx.arm_pools("query", ("G1",), module.TAU)

    def test_evaluation_record_binds_committed_arm_pool_and_exact_bound(self) -> None:
        module = load_executor()
        ctx, _ = module.synthetic_fixture(mode=module.MODE_ARM_CONDITIONAL)
        rows = module.evaluate_arm(ctx, ["query"], "STATIC_ADAPTIVE", module.TAU)
        row = rows["query"]
        self.assertIn(row["committed"], module.PORTFOLIO)
        if row["certified"]:
            self.assertEqual(len(row["pool_members"]), module.POOL_K)
            exact = max(
                ctx.excess_member(name, row["committed"])
                for name in row["pool_members"]
            )
            self.assertAlmostEqual(row["bound"], exact)
            self.assertEqual(row["violation_strict"], row["excess"] > exact + module.TOL)

    def test_synthetic_policy_replay_is_byte_deterministic(self) -> None:
        module = load_executor()
        first = module.synthetic_policy_receipt()
        second = module.synthetic_policy_receipt()
        self.assertEqual(module.canonical_json(first), module.canonical_json(second))
        self.assertTrue(first["hostile_controls"]["arm_specific_pool_integrity"])

    def test_nine_fold_phase_is_deterministic_and_custody_disjoint(self) -> None:
        module = load_executor()
        fold_of, meta, outcomes = module.synthetic_nine_fold_corpus()
        first = module.policy_phase(
            module.MODE_ARM_CONDITIONAL, fold_of, meta, outcomes
        )
        second = module.policy_phase(
            module.MODE_ARM_CONDITIONAL, fold_of, meta, outcomes
        )
        self.assertEqual(module.canonical_json(first), module.canonical_json(second))
        seen_test = []
        for fold in range(module.N_FOLDS):
            roles = first[fold]["roles"]
            role_sets = [set(roles[name]) for name in (
                "test", "proposer_train", "shield_table", "threshold_select"
            )]
            for i, left in enumerate(role_sets):
                for right in role_sets[i + 1 :]:
                    self.assertFalse(left & right)
            seen_test.extend(roles["test"])
            self.assertIn(first[fold]["primary"], module.LEARNED_ARMS)
        self.assertEqual(sorted(seen_test), sorted(fold_of))

    def test_full_state_receipt_keeps_arm_specific_member_maps(self) -> None:
        module = load_executor()
        fold_of, meta, outcomes = module.synthetic_nine_fold_corpus()
        phase = module.policy_phase(module.MODE_ARM_CONDITIONAL, fold_of, meta, outcomes)
        rows = module.full_state_rows(phase, meta, outcomes, module.MODE_ARM_CONDITIONAL)
        self.assertEqual(sorted(rows), sorted(fold_of))
        for row in rows.values():
            self.assertEqual(sorted(row["arm_pools"]), sorted(module.PORTFOLIO))
            for arm in row["admissible"]:
                self.assertEqual(len(row["arm_pools"][arm]), module.POOL_K)
                self.assertLessEqual(row["arm_bounds"][arm], module.TAU + module.TOL)


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

    def test_gate_pass_still_requires_value_adjudication(self) -> None:
        module = load_executor()
        payload = {
            "hostile_controls": {"fixture": True},
            "coverage": {"r23_parent": 0.73, "r24_primary": 0.96, "target": 0.95},
            "primary": {"certified_n": 40, "violations_strict": 4},
            "matched_parent_test": {"mean_diff": -0.001, "ci_upper": 0.003},
            "negative_control_test": {"mean_diff": 0.002, "ci_upper": 0.010},
        }
        self.assertEqual(
            module.decide_terminal(payload),
            "C_R24_ARM_CONDITIONAL_COVERAGE_VALIDITY_PASS_VALUE_NOT_MATERIAL",
        )
        payload["matched_parent_test"]["ci_upper"] = -0.0001
        payload["negative_control_test"] = {"mean_diff": -0.002, "ci_upper": -0.0001}
        self.assertEqual(
            module.decide_terminal(payload),
            "C_R24_ARM_CONDITIONAL_VALUE",
        )


class ExecutionBindingTests(unittest.TestCase):
    def test_wrapper_requires_two_runs_byte_identity_and_two_verifier_passes(self) -> None:
        text = WRAPPER.read_text()
        self.assertIn('run_one "run_a"', text)
        self.assertIn('run_one "run_b"', text)
        self.assertIn('cmp -s "$TMP/run_a.result.json" "$TMP/run_b.result.json"', text)
        self.assertIn('cmp -s "$TMP/run_a.parent.json" "$TMP/run_b.parent.json"', text)
        self.assertIn('cmp -s "$TMP/run_a.terminal.txt" "$TMP/run_b.terminal.txt"', text)
        self.assertIn('verify_one "run_a"', text)
        self.assertIn('verify_one "run_b"', text)
        self.assertIn("failed-executions", text)

    def test_slurm_binds_exact_source_commit_and_clean_tree(self) -> None:
        text = SLURM.read_text()
        self.assertIn('EXPECTED_SOURCE_COMMIT', text)
        self.assertIn('git rev-parse HEAD', text)
        self.assertIn('git status --porcelain', text)
        self.assertIn('run_fiberguard_pmlb_arm_conditional_r24_twice.sh', text)

    def test_slurm_reproduces_the_verified_r23_parent_environment(self) -> None:
        """Job 3550262 task 0 identified the only byte-identical R23 profile."""
        text = SLURM.read_text()
        self.assertIn('#SBATCH --nodelist=cn087', text)
        self.assertIn(
            'unset PYTHONHASHSEED OPENBLAS_NUM_THREADS OMP_NUM_THREADS '
            'MKL_NUM_THREADS NUMEXPR_NUM_THREADS',
            text,
        )
        self.assertNotIn('export OPENBLAS_NUM_THREADS=1', text)


if __name__ == "__main__":
    unittest.main()
