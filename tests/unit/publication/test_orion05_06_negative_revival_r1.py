from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Orion0506NegativeRevivalR1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r13 = load(
            "orion05_r13",
            ROOT / "papers/orion-05-tare-expressivity/orion05_r13_parent_certificate_ordering.py",
        )
        cls.xover = load(
            "orion05_xover_revival",
            ROOT / "papers/orion-05-tare-expressivity/orion05_xover_budget_revival.py",
        )
        cls.o6 = load(
            "orion06_negative_coverage",
            ROOT / "papers/orion-06-recursive-recovery/revival/verify_orion06_negative_coverage.py",
        )
        cls.bundle = load(
            "orion0506_revival_bundle",
            ROOT / "development/orion-05-06-negative-revival-r1-2026-08-27/verify_revival_bundle.py",
        )

    def test_r13_protocol_excludes_pilot_and_freezes_all_heldout_matchings(self):
        protocol = json.loads(
            (ROOT / "papers/orion-05-tare-expressivity/rounds/r13-parent-certificate-ordering/ORION05_R13_PROTOCOL.json").read_text()
        )
        self.assertEqual(protocol["status"], "FROZEN_BEFORE_CONFIRMATORY_OUTCOME")
        exposed = set(protocol["confirmatory_panel"]["excluded_exposed_indices"])
        heldout = set(protocol["confirmatory_panel"]["included_heldout_indices"])
        self.assertFalse(exposed & heldout)
        self.assertEqual(exposed | heldout, set(range(15)))
        self.assertEqual(protocol["confirmatory_panel"]["cell_count"], 24)

    def test_r13_parent_certificate_projection_is_exact_on_one_small_cell(self):
        row = self.r13.evaluate_cell(ROOT, "H4", 1, projection=1)
        self.assertTrue(row["projection_valid"])
        self.assertEqual(row["parent_cost"], row["projected_cost"])
        self.assertLessEqual(row["maximum_frame_support"], 2)
        self.assertGreaterEqual(row["charged_total_wall_ns"], row["parent_wall_ns"])

    def test_r13_adjudication_can_improve_completion_without_promoting_value(self):
        rows = [
            {
                "subject": subject,
                "matching_index": index,
                "projection_valid": True,
                "parent_cost": 9,
                "projected_cost": 9,
                "parent_wall_ns": 100,
                "charged_total_wall_ns": 101,
            }
            for subject in ("H4", "N2")
            for index in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13)
        ]
        result = self.r13.adjudicate(rows)
        self.assertEqual(result["revival_outcome"], "IMPROVED")
        self.assertEqual(result["scientific_authority_delta"], "NONE")
        self.assertTrue(result["r12_null_preserved"])
        self.assertFalse(result["authority"]["standalone_production_value"])

    def test_xover_selector_reconstructs_lexicographically_first_frozen_n6_cell(self):
        selection = self.xover.select_frozen_cell(ROOT)
        self.assertEqual(selection["family"], "uniform")
        self.assertEqual(selection["n"], 6)
        self.assertEqual(selection["instance_index"], 0)
        self.assertEqual(
            selection["targets"],
            [[5, 2], [5, 11], [6, 48], [52, 32], [5, 26], [49, 2]],
        )

    def test_xover_timeout_remains_negative_and_exact_only_improves_one_cell(self):
        timeout = self.xover.adjudicate(
            {"status": "TIMEOUT", "timeout_seconds": 1800},
            {"status": "COMPLETED", "cost": 19, "witness_valid": True},
        )
        self.assertEqual(timeout["revival_outcome"], "RETAINED_NEGATIVE")
        self.assertEqual(timeout["original_verdict_preserved"], "RUN_INCOMPLETE")
        exact = self.xover.adjudicate(
            {"status": "EXACT", "cost": 19, "witness_valid": True},
            {"status": "COMPLETED", "cost": 19, "witness_valid": True},
        )
        self.assertEqual(exact["revival_outcome"], "IMPROVED")
        self.assertFalse(exact["authority"]["whole_panel_revival"])

    def test_orion06_recomputes_partition_and_keeps_unfinished_distinct(self):
        audit = self.o6.build_audit(ROOT)
        self.assertEqual(audit["denominator"], {"eligible": 51, "included": 23, "excluded": 28, "edges": 13})
        self.assertEqual(len(audit["standalone_rows"]), 7)
        by_id = {row["id"]: row for row in audit["standalone_rows"]}
        self.assertEqual(by_id["R2_KNOWN_OPERATOR_TRANSFER"]["revival_outcome"], "RETAINED_NEGATIVE")
        self.assertEqual(by_id["R4C_H2_REGIME_LIMITED"]["revival_outcome"], "UNFINISHED")
        self.assertNotIn("UNSOLVABLE", {row["revival_outcome"] for row in audit["standalone_rows"]})
        self.assertEqual(audit["cross_domain_general_method"]["revival_outcome"], "CANNOT_CHECK")
        self.assertEqual(audit["scientific_authority_delta"], "NONE")

    def test_lunarc_bundle_is_byte_bound_and_row_complete(self):
        report = self.bundle.verify(ROOT)
        self.assertEqual(report["terminal"], "ORION0506_REVIVAL_BUNDLE_VERIFIED")
        self.assertEqual(report["source_chronology"]["protocol_commit"], "9f7e66f26148387115354d4853f3f67b7bacc02d")
        self.assertEqual(report["source_chronology"]["execution_commit"], "506b84e6c47558764b95f4482ce6691bb3757723")
        self.assertEqual(report["remote_stage"]["manifest_entries"], 257)
        self.assertEqual(report["remote_stage"]["manifest_failures"], 0)
        self.assertEqual(report["r13"]["cells"], 24)
        self.assertEqual(report["r13"]["unique_cells"], 24)
        self.assertEqual(report["r13"]["exposed_indices_seen"], [])
        self.assertTrue(report["r13"]["all_witness_checks_pass"])
        self.assertEqual(report["xover"]["outcome"], "RETAINED_NEGATIVE")
        self.assertEqual(report["xover"]["legacy_status"], "TIMEOUT")
        self.assertEqual(report["orion06_audit"]["unfinished"], 4)
        self.assertEqual(report["unsolvable"], [])

    def test_orion06_revival_protocol_declares_four_distinct_honest_attempts(self):
        protocol = json.loads(
            (
                ROOT
                / "papers/orion-06-recursive-recovery/revival/ORION06_NEGATIVE_REVIVAL_R1_PROTOCOL.json"
            ).read_text()
        )
        self.assertEqual(protocol["status"], "FROZEN_BEFORE_NEW_RESOURCE_OUTCOMES")
        attempts = {row["source_negative_id"]: row for row in protocol["attempts"]}
        self.assertEqual(
            set(attempts),
            {
                "R4C_H2_REGIME_LIMITED",
                "R5B_PROOF_OUTER_REPLAY",
                "R6I_EXACT_RANK2",
                "R6K_EXACT_RESTORE_FACTOR",
            },
        )
        self.assertEqual(attempts["R4C_H2_REGIME_LIMITED"]["subject"]["nonidentity_terms"], 14)
        self.assertEqual(attempts["R4C_H2_REGIME_LIMITED"]["enumeration"]["perfect_matchings"], 135135)
        self.assertEqual(
            attempts["R5B_PROOF_OUTER_REPLAY"]["subject"]["frozen_source_indices"],
            [12, 18, 22, 25, 27, 31],
        )
        self.assertTrue(attempts["R5B_PROOF_OUTER_REPLAY"]["subject"]["already_open"])
        self.assertFalse(attempts["R5B_PROOF_OUTER_REPLAY"]["authority"]["prospective_confirmation"])
        self.assertEqual(attempts["R6I_EXACT_RANK2"]["lever"], "R6K_JOINT_RESTORE_FACTOR_EXACT_REPLAY")
        self.assertTrue(attempts["R6I_EXACT_RANK2"]["source_outcome_already_known"])
        self.assertEqual(attempts["R6K_EXACT_RESTORE_FACTOR"]["lever"], "R6L_THREE_TARE2_ARITY_SWAP_DONOR_REPLAY")
        self.assertTrue(attempts["R6K_EXACT_RESTORE_FACTOR"]["source_outcome_already_known"])
        self.assertEqual(protocol["unsolvable"], [])
        self.assertFalse(protocol["authority"]["final_freeze"])


if __name__ == "__main__":
    unittest.main()
