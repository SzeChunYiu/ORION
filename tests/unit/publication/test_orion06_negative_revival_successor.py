from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
VERIFIER = (
    ROOT / "papers/orion-06-recursive-recovery/revival/verify_orion06_negative_revival_successor.py"
)


def load_verifier():
    spec = importlib.util.spec_from_file_location("orion06_negative_revival_successor", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Orion06NegativeRevivalSuccessorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load_verifier()
        cls.report = cls.verifier.verify_committed(ROOT)

    def test_every_recorded_negative_has_a_mechanistic_adjudication(self):
        self.assertEqual(self.report["coverage"]["recorded_negative_rows"], 7)
        self.assertEqual(self.report["coverage"]["mechanistically_adjudicated_rows"], 7)
        self.assertEqual(
            self.report["coverage"]["outcomes"],
            {"CORRECT_SUBTRACTION": 1, "IMPROVED": 2, "RETAINED_NEGATIVE": 4},
        )
        self.assertTrue(all(row["original_negative_preserved"] for row in self.report["rows"]))

    def test_executed_outcomes_remain_bounded(self):
        by_id = {row["id"]: row for row in self.report["rows"]}
        self.assertEqual(by_id["R4C_H2_REGIME_LIMITED"]["revival_outcome"], "IMPROVED")
        self.assertEqual(by_id["R5B_PROOF_OUTER_REPLAY"]["revival_outcome"], "IMPROVED")
        self.assertEqual(by_id["R6I_EXACT_RANK2"]["revival_outcome"], "RETAINED_NEGATIVE")
        self.assertEqual(
            by_id["R6K_EXACT_RESTORE_FACTOR"]["revival_outcome"], "CORRECT_SUBTRACTION"
        )
        self.assertIn(
            "open-subject mechanism evidence only",
            by_id["R4C_H2_REGIME_LIMITED"]["execution_evidence"]["attempt"]["residual"],
        )
        self.assertFalse(
            by_id["R6K_EXACT_RESTORE_FACTOR"]["execution_evidence"]["attempt"][
                "donor_novelty_credit"
            ]
        )

    def test_external_gate_is_cannot_check_not_unsolvable(self):
        self.assertEqual(len(self.report["cannot_check"]), 1)
        self.assertEqual(self.report["cannot_check"][0]["classification"], "CANNOT_CHECK")
        self.assertTrue(self.report["cannot_check"][0]["not_unsolvable"])
        self.assertEqual(self.report["unsolvable"], [])

    def test_coverage_completion_does_not_freeze_the_paper(self):
        self.assertEqual(
            self.report["terminal"],
            "ORION06_RECORDED_NEGATIVE_REVIVAL_COVERAGE_COMPLETE__PAPER_FREEZE_WITHHELD",
        )
        self.assertEqual(self.report["scientific_authority_delta"], "NONE")
        self.assertEqual(self.report["paper_freeze"]["status"], "WITHHELD")
        self.assertTrue(self.report["paper_freeze"]["remaining_gates"])
        self.assertFalse(any(self.report["authority"].values()))


if __name__ == "__main__":
    unittest.main()
