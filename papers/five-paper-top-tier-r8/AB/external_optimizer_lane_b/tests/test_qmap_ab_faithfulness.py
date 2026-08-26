from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import qmap_ab_faithfulness as audit  # noqa: E402


class QmapABFaithfulnessTests(unittest.TestCase):
    def test_complete_qmap_synthesis_inventory_is_frozen(self) -> None:
        self.assertEqual(
            audit.QMAP_SINGLE_QUBIT_GATES,
            ("NONE", "X", "Y", "Z", "H", "S", "SDG"),
        )
        self.assertEqual(audit.QMAP_TWO_QUBIT_GATES, ("CX",))
        self.assertEqual(
            audit.QMAP_TARGET_METRICS,
            ("GATES", "TWO_QUBIT_GATES", "DEPTH"),
        )

    def test_every_projected_qmap_gate_is_bijective_and_rank_preserving(self) -> None:
        for n_qubits in range(2, 6):
            universe = tuple(range(1 << (2 * n_qubits)))
            for gate in audit.qmap_gate_inventory(n_qubits):
                transformed = tuple(
                    audit.apply_qmap_label_gate(label, n_qubits, gate)
                    for label in universe
                )
                self.assertEqual(len(set(transformed)), len(universe), gate)
                self.assertEqual(
                    audit.gf2_rank(universe[1 : 2 * n_qubits + 1]),
                    audit.gf2_rank(transformed[1 : 2 * n_qubits + 1]),
                    gate,
                )

    def test_strong_fuse_has_a_rank_and_cardinality_delta_no_qmap_move_has(
        self,
    ) -> None:
        before = (0b001, 0b010)
        after = audit.ab_fuse(before, 0, 1)
        self.assertEqual(after, (0b011,))
        self.assertEqual(audit.gf2_rank(before), 2)
        self.assertEqual(audit.gf2_rank(after), 1)
        self.assertEqual(len(after) - len(before), -1)
        self.assertEqual(audit.AB_FUSE_LIVE_FRAGMENT_COST_DELTA, -1)
        self.assertEqual(audit.QMAP_GATE_SEQUENCE_COST_DELTA, 1)
        self.assertEqual(audit.QMAP_TABLEAU_ROW_COUNT_DELTA, 0)

    def test_weak_delete_has_a_rank_and_cardinality_delta_no_qmap_move_has(
        self,
    ) -> None:
        before = (0b001, 0b010, 0b011, 0b100)
        self.assertEqual(audit.xor_sum(before), 0b100)
        after = audit.ab_delete(before, (0, 1, 2))
        self.assertEqual(after, (0b100,))
        self.assertEqual(audit.gf2_rank(before), 3)
        self.assertEqual(audit.gf2_rank(after), 1)
        self.assertEqual(len(after) - len(before), -3)

    def test_fuse_is_many_to_one_but_every_qmap_gate_is_invertible(self) -> None:
        left = audit.ab_fuse((0b001, 0b010), 0, 1)
        right = audit.ab_fuse((0b100, 0b111), 0, 1)
        self.assertEqual(left, right)
        self.assertNotEqual((0b001, 0b010), (0b100, 0b111))
        self.assertTrue(audit.every_qmap_gate_has_legal_inverse())

    def test_fuse_rejects_moves_outside_the_frozen_ab_grammar(self) -> None:
        with self.assertRaises(ValueError):
            audit.ab_fuse((0b001, 0b001), 0, 1)
        with self.assertRaises(ValueError):
            audit.ab_fuse((0b000, 0b001), 0, 1)

    def test_assessment_rejects_one_representation_and_cost_bidirectionality(
        self,
    ) -> None:
        assessment = audit.assess_faithfulness()
        self.assertEqual(assessment["terminal"], "CANNOT_CHECK")
        self.assertFalse(assessment["faithful_external_realization"])
        self.assertEqual(assessment["candidate"], "MQT_QMAP_CLIFFORD_SYNTHESIS")
        by_obligation = {
            row["obligation"]: row["disposition"] for row in assessment["mapping_table"]
        }
        self.assertEqual(by_obligation["AB_WEAK_DELETE_TO_QMAP"], "REFUTED")
        self.assertEqual(by_obligation["AB_STRONG_FUSE_TO_QMAP"], "REFUTED")
        self.assertEqual(by_obligation["QMAP_MOVES_TO_AB_BIDIRECTIONAL"], "REFUTED")
        self.assertEqual(by_obligation["ONE_COST_CONTRACT"], "REFUTED")
        self.assertEqual(by_obligation["REALIZED_WEAK_TERMINAL"], "CANNOT_CHECK")
        self.assertEqual(
            assessment["next_smallest_discriminator"],
            "EXTERNAL_MOVE_DECREASES_LIVE_FRAGMENT_CARDINALITY_WITHOUT_GARBAGE_QUOTIENT",
        )


if __name__ == "__main__":
    unittest.main()
