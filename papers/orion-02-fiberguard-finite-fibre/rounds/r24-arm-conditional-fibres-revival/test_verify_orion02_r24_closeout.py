#!/usr/bin/env python3
"""Regression tests for the additive R24 counted-adverse closeout."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
VERIFIER = HERE / "verify_orion02_r24_closeout.py"
RECEIPT = HERE / "ORION02_R24_CUSTODY_3550275.json"
LEDGER = HERE.parent / "r23-density-backoff-revival/ORION02_REVIVAL_ATTEMPT_LEDGER_V1.jsonl"


def load_verifier():
    spec = importlib.util.spec_from_file_location("orion02_r24_closeout", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class R24CloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = load_verifier()
        cls.rebuilt = cls.verifier.build()
        cls.committed = json.loads(RECEIPT.read_text())

    def test_committed_receipt_is_rebuilt_exactly(self) -> None:
        self.assertEqual(self.committed, self.rebuilt)

    def test_adverse_terminal_is_counted_without_promotion(self) -> None:
        self.assertEqual(
            self.rebuilt["scientific_outcome"]["terminal"],
            "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID",
        )
        self.assertEqual(self.rebuilt["scientific_outcome"]["coverage"]["r24_primary"], 1.0)
        certificate = self.rebuilt["scientific_outcome"]["certificate"]
        self.assertEqual(certificate["violations_strict"], 20)
        self.assertEqual(certificate["certified_n"], 44)
        self.assertFalse(certificate["valid"])
        self.assertTrue(self.rebuilt["attempt_accounting"]["counts_toward_100"])
        self.assertEqual(self.rebuilt["attempt_accounting"]["attempt_ordinal"], 2)
        self.assertTrue(self.rebuilt["attempt_accounting"]["active_after_completion"])
        authority = self.rebuilt["authority"]
        self.assertEqual(authority["scientific_authority_delta"], "NONE")
        self.assertFalse(
            any(
                authority[key]
                for key in (
                    "external_independence",
                    "submission_authorized",
                    "top_tier_gate_pass",
                    "paper_freeze_authorized",
                )
            )
        )
        self.assertEqual(self.rebuilt["unsolvable"], [])

    def test_verifier_only_recovery_did_not_change_science(self) -> None:
        chronology = self.rebuilt["source_chronology"]
        self.assertEqual(
            chronology["scientific_execution_commit"],
            "e4d12133a662b53135264945451c19f6adf8a04d",
        )
        self.assertEqual(
            chronology["post_outcome_verifier_amendment_commit"],
            "0c42ea7b7698a6e22bb4184b8f75869566f4af4e",
        )
        self.assertTrue(chronology["protected_science_sources_unchanged"])
        self.assertEqual(
            self.rebuilt["scheduler"]["verification_only_job"]["scientific_executor_invoked"],
            False,
        )
        self.assertEqual(self.rebuilt["verification"]["preserved_run_a"], "VERIFY_OK")
        self.assertEqual(self.rebuilt["verification"]["preserved_run_b"], "VERIFY_OK")

    def test_append_only_ledger_contains_one_counted_completion(self) -> None:
        events = [json.loads(line) for line in LEDGER.read_text().splitlines() if line]
        completions = [
            row
            for row in events
            if row.get("attempt_id") == "ORION02-REVIVAL-002-R24-ARM-CONDITIONAL-BOUNDARY-FIBRES"
            and row.get("event") == "COMPLETION_VERIFIED"
        ]
        self.assertEqual(len(completions), 1)
        self.assertTrue(completions[0]["counts_toward_100"])
        self.assertEqual(completions[0]["remaining_attempts"], 98)
        self.assertEqual(
            completions[0]["scientific_terminal"],
            "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID",
        )


if __name__ == "__main__":
    unittest.main()
