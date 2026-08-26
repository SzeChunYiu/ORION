from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import verify_lane_b_evidence as verifier  # noqa: E402


class LaneBEvidenceVerifierTests(unittest.TestCase):
    def test_frozen_bundle_is_self_consistent(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(verifier.verify_bundle(root), [])

    def test_theorem_repair_cross_audit_preserves_the_adverse_ceiling(self) -> None:
        root = Path(__file__).resolve().parents[1]
        review = json.loads(
            (root / "THEOREM_REPAIR_CROSS_AUDIT.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            review["reviewed_commit"],
            "82e94b19b9b79733bd5353cb433e48fe338e4423",
        )
        self.assertEqual(
            review["terminal"],
            "AB_THEOREM_REPAIR_PARTIAL_PASS__T10_CONVENTION_REQUIRED",
        )
        by_id = {row["id"]: row["verdict"] for row in review["objects"]}
        self.assertEqual(by_id["AB-T10"], "REPAIR_INCOMPLETE")
        self.assertEqual(by_id["AB-T13"], "PASS_INTERNAL_CALIBRATION_ONLY")
        self.assertEqual(
            review["donor_absorption"]["broad_claim"],
            "DONOR_ABSORBED",
        )
        self.assertEqual(
            review["claim_ceiling"]["external_significance"], "CANNOT_CHECK"
        )


if __name__ == "__main__":
    unittest.main()
