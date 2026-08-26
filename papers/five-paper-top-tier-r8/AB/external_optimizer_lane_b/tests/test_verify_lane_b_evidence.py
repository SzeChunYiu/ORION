from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import verify_lane_b_evidence as verifier  # noqa: E402


class LaneBEvidenceVerifierTests(unittest.TestCase):
    def test_frozen_bundle_is_self_consistent(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(verifier.verify_bundle(root), [])


if __name__ == "__main__":
    unittest.main()
