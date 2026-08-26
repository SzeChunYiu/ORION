#!/usr/bin/env python3
"""Tests for the post-lock Q1-A registered-proof comparison."""

import itertools
import json
import unittest
from pathlib import Path

import verify_q1_a_comparison_r9 as comparison
import verify_q1_a_reconstruction_r9 as phase1

HERE = Path(__file__).resolve().parent


class RegisteredProofComparisonTests(unittest.TestCase):
    def test_registered_stronger_two_coordinate_bound_is_valid(self):
        signatures = tuple(itertools.product((0, 1), repeat=2))
        largest_minimum = 0
        for length in range(3, 8):
            for seq in itertools.product(signatures, repeat=length):
                if phase1.xor_signature(seq)[0] != 1:
                    continue
                removal = phase1.find_proper_zero_sum_subset(seq)
                self.assertIsNotNone(removal)
                largest_minimum = max(largest_minimum, len(removal))
        self.assertEqual(largest_minimum, 2)

    def test_first_disagreement_is_preserved_without_claim_widening(self):
        receipt = comparison.build_final_receipt()
        first = receipt["comparison"]["first_disagreement"]
        self.assertEqual(first["id"], "D01_CLAIM_QUANTIFIER_STRENGTH")
        self.assertEqual(first["independent_phase1"], "existence_of_support_at_most_two_exact_optimum")
        self.assertEqual(first["registered_proof"], "nonincreasing_transform_of_every_feasible_configuration")
        self.assertEqual(first["effect_on_frozen_ledger_claim"], "NONE")
        self.assertEqual(receipt["terminal"], "PROOF_RECONSTRUCTED_EQUIVALENT")

    def test_registered_proof_hash_hostile_control_rejects_tampering(self):
        proof = (HERE.parents[1] / "Q-paper-01-tare-expressivity/HUMAN_PROOF_R6S_2026-08-22.md").read_bytes()
        self.assertTrue(comparison.matches_registered_proof(proof))
        self.assertFalse(comparison.matches_registered_proof(proof + b"\nTAMPERED"))

    def test_local_cardinality_difference_is_preserved(self):
        receipt = comparison.build_final_receipt()
        delta = next(row for row in receipt["comparison"]["rows"] if row["id"] == "D02_DELETION_CARDINALITY")
        self.assertEqual(delta["independent_phase1"], "at_most_3")
        self.assertEqual(delta["registered_proof"], "at_most_2")
        self.assertEqual(delta["effect_on_frozen_ledger_claim"], "NONE")

    def test_final_receipt_matches_committed_machine_receipt(self):
        committed = json.loads((HERE / "Q1_A_FINAL_COMPARISON_RECEIPT_R9.json").read_text())
        generated = comparison.build_final_receipt()
        self.assertEqual(generated, committed)
        self.assertEqual(committed["phase_order"]["phase_1_commit"], "dcf642b091f4a11fcaa97f583cb9e0598c883777")
        self.assertEqual(committed["source_binding"]["registered_proof"]["git_blob_sha1"], "a22754e8afef0e9914b75b37f0aee673ccd2ca95")
        self.assertEqual(committed["independence"]["external_independence"], "CANNOT_CHECK")
        self.assertEqual(committed["authority"]["journal_authority"], "CANNOT_CHECK")


if __name__ == "__main__":
    unittest.main()
