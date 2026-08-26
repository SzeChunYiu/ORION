#!/usr/bin/env python3
"""Tests for the clean-room Q1-A reconstruction verifier."""

import itertools
import json
import unittest
from pathlib import Path

import verify_q1_a_reconstruction_r9 as q1a


HERE = Path(__file__).resolve().parent


class PauliAlgebraTests(unittest.TestCase):
    def test_phase_free_multiplication_and_symplectic_form(self):
        self.assertEqual(q1a.pauli_multiply("XZ", "IX"), "XY")
        self.assertEqual(q1a.pauli_multiply("IZ", "IX"), "IY")
        self.assertEqual(q1a.symplectic("ZI", "XZ"), 1)
        self.assertEqual(q1a.symplectic("IX", "IZ"), 1)
        self.assertEqual(q1a.symplectic("IX", "IX"), 0)

    def test_local_restore_rule_is_two_lipschitz_in_one_donor(self):
        maximum, witness = q1a.maximum_single_donor_f3_increase()
        self.assertEqual(maximum, 2)
        self.assertEqual(witness["before_cost"], 1)
        self.assertEqual(witness["after_cost"], 3)


class ExchangeLemmaTests(unittest.TestCase):
    def test_every_admissible_signature_sequence_has_proper_zero_sum(self):
        signatures = tuple(itertools.product((0, 1), repeat=2))
        for length in range(3, 8):
            for seq in itertools.product(signatures, repeat=length):
                if q1a.xor_signature(seq)[0] != 1:
                    continue
                removal = q1a.find_proper_zero_sum_subset(seq)
                self.assertIsNotNone(removal, (length, seq))
                self.assertGreater(len(removal), 0)
                self.assertLess(len(removal), length)
                self.assertEqual(q1a.xor_signature(seq[i] for i in removal), (0, 0))

    def test_odd_partner_parity_is_load_bearing(self):
        broken = ((0, 1), (1, 0), (1, 1))
        self.assertEqual(q1a.xor_signature(broken), (0, 0))
        self.assertIsNone(q1a.find_proper_zero_sum_subset(broken))

    def test_degenerate_and_alias_signatures_are_removed(self):
        cases = (
            ((0, 0), (1, 0), (0, 1)),
            ((1, 1), (1, 1), (1, 0)),
            ((1, 0), (0, 0), (0, 0)),
        )
        for seq in cases:
            if q1a.xor_signature(seq)[0] == 1:
                removal = q1a.find_proper_zero_sum_subset(seq)
                self.assertIsNotNone(removal)
                self.assertEqual(q1a.xor_signature(seq[i] for i in removal), (0, 0))

    def test_multiplier_two_is_exact_objective_threshold(self):
        control = q1a.objective_multiplier_control()
        self.assertEqual(control["restore_penalty"], 2)
        self.assertEqual(control["net_change_m1"], 1)
        self.assertEqual(control["net_change_m2"], 0)
        self.assertLess(control["net_change_m4"], 0)


class SharpnessWitnessTests(unittest.TestCase):
    def test_support_zero_is_infeasible(self):
        result = q1a.solve_frozen_two_qubit_instance(max_frame_support=0)
        self.assertEqual(result["terminal"], "INFEASIBLE")
        self.assertIsNone(result["optimum"])

    def test_independent_lower_witness_has_exact_five_vs_six_gap(self):
        unrestricted = q1a.solve_frozen_two_qubit_instance(max_frame_support=None)
        support_one = q1a.solve_frozen_two_qubit_instance(max_frame_support=1)
        self.assertEqual(unrestricted["terminal"], "EXACT_OPTIMUM")
        self.assertEqual(support_one["terminal"], "EXACT_OPTIMUM")
        self.assertEqual(unrestricted["optimum"], 5)
        self.assertEqual(support_one["optimum"], 6)
        self.assertEqual(unrestricted["witness"]["tag"], "IX")
        self.assertEqual(unrestricted["witness"]["maximum_frame_support"], 2)

    def test_duplicate_targets_and_objective_ties_remain_admitted(self):
        result = q1a.solve_frozen_two_qubit_instance(max_frame_support=1)
        self.assertEqual(q1a.FROZEN_TARGETS[2], ("IZ", "IZ"))
        self.assertGreater(result["optimum_witness_count"], 1)


class ReceiptTests(unittest.TestCase):
    def test_generated_receipt_matches_committed_receipt(self):
        committed = json.loads((HERE / "Q1_A_PHASE1_RECONSTRUCTION_RECEIPT_R9.json").read_text())
        generated = q1a.build_phase1_receipt()
        self.assertEqual(generated, committed)
        self.assertEqual(committed["phase_1_terminal"], "PHASE1_LOCKED_BEFORE_REGISTERED_PROOF")
        self.assertEqual(committed["independence"]["external_independence"], "CANNOT_CHECK")
        self.assertEqual(committed["authority"]["journal_authority"], "CANNOT_CHECK")


if __name__ == "__main__":
    unittest.main()
