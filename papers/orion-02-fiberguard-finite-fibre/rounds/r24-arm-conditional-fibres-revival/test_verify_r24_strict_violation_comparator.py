from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_r24_strict_violation_comparator import ReconstructionError, reconstruct


RESULT = Path(__file__).resolve().parent / "failed-executions/3550275/run_a.result.json"


class R24StrictViolationComparatorTests(unittest.TestCase):
    def load(self):
        return json.loads(RESULT.read_text(encoding="utf-8"))

    def reconstruct(self, value):
        return reconstruct(value, source_sha256=hashlib.sha256(RESULT.read_bytes()).hexdigest())

    def test_frozen_result_reconstructs_exact_paired_comparator(self):
        report = self.reconstruct(self.load())
        self.assertEqual(report["n"], 44)
        self.assertEqual(report["primary"]["strict_violations"], 20)
        self.assertEqual(report["matched_lexical_control"]["strict_violations"], 14)
        self.assertEqual(
            report["paired_contingency"],
            {
                "both_violate": 14,
                "primary_only_violates": 6,
                "control_only_violates": 0,
                "neither_violates": 24,
            },
        )
        self.assertEqual(report["mcnemar_exact_two_sided_p"], 0.03125)
        self.assertEqual(report["primary"]["gate"], "FAIL")
        self.assertEqual(report["matched_lexical_control"]["gate"], "FAIL")

    def test_missing_serialized_control_flag_fails_closed(self):
        value = copy.deepcopy(self.load())
        fold = value["folds"]["R24_LEXICAL_GOOD_BOUNDARY_NEGATIVE_CONTROL"]["0"]
        arm = value["folds"]["R24_ARM_CONDITIONAL_BOUNDARY_FIBRES"]["0"]["primary"]
        dataset = next(iter(fold["test"][arm]))
        del fold["test"][arm][dataset]["violation_strict"]
        with self.assertRaisesRegex(ReconstructionError, "not Boolean"):
            self.reconstruct(value)

    def test_serialized_summary_mismatch_fails_closed(self):
        value = copy.deepcopy(self.load())
        value["arms_summary"]["R24_LEXICAL_MATCHED_PRIMARY"]["violations_strict"] = 13
        with self.assertRaisesRegex(ReconstructionError, "control summary violation count mismatch"):
            self.reconstruct(value)


if __name__ == "__main__":
    unittest.main()
