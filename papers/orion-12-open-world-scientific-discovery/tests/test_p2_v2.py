from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_p2_v2.py"

spec = importlib.util.spec_from_file_location("check_p2_v2", CHECKER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class P2V2WideningContractTests(unittest.TestCase):
    def test_v2_widening_surface_is_fail_closed(self) -> None:
        self.assertEqual(module.validate(), [])

    def test_claim_ladder_cannot_skip_narrowed_predecessor(self) -> None:
        registry = module._load("P2_V2_SYSTEM_REGISTRY.json")
        self.assertEqual(registry["claim_ladder"][0], "P2_NARROWED")
        self.assertEqual(registry["claim_ladder"][-1], "P2_TRANSFER_SUPPORTED")

    def test_max_composed_retains_authority_layer(self) -> None:
        registry = module._load("P2_V2_SYSTEM_REGISTRY.json")
        system = registry["development_systems"]["ORION_MAX_COMPOSED"]
        self.assertIn("typed_closure_authority", system)
        self.assertIn("censoring_obligations", system)
        self.assertIn("earned_route_independence", system)

    def test_hostile_suite_contains_censoring_and_hidden_gold(self) -> None:
        hostile = module._load("P2_V2_HOSTILE_AUTHORITY_CASES.json")
        ids = {case["id"] for case in hostile["cases"]}
        self.assertIn("censored_route", ids)
        self.assertIn("utility_stop_with_hidden_gold", ids)
        self.assertIn("verification_stop_with_censoring", ids)


if __name__ == "__main__":
    unittest.main()
