#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
CHECKER = ROOT / "proof_checker_v3.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("orion01_proof_checker_v3", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IndependentProofCheckerTests(unittest.TestCase):
    def test_import_surface_is_standard_library_only(self) -> None:
        tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])
        self.assertEqual(
            imported_roots,
            {"__future__", "argparse", "itertools", "json", "pathlib", "typing"},
        )

    def test_all_declared_checks_pass(self) -> None:
        result = load_checker().run_checks()
        self.assertTrue(result["implementation_independent"])
        self.assertTrue(result["all_passed"])
        self.assertEqual(
            result["terminal"], "SUPPORTED_WITHIN_DECLARED_FINITE_SCOPE"
        )
        by_name = {check["name"]: check for check in result["checks"]}
        binary = by_name["binary_generated_span_identity"]
        self.assertEqual(binary["families"], 276)
        self.assertEqual(binary["generated_span_equalities"], 276)
        self.assertEqual(binary["strict_inequality_cases"], 0)
        self.assertEqual(
            by_name["exact_one_argument_restore_sensitivity"]["comparisons"],
            582528,
        )
        self.assertEqual(
            by_name["proper_deletion_and_zero_sum_free_terminal"]["fixtures"], 3
        )

    def test_restricted_binary_alphabet_never_beats_its_generated_span_rank(self) -> None:
        checker = load_checker()
        for alphabet in ((), (3,), (3, 5), (0, 3, 5)):
            rank = checker.f2_span_rank(alphabet)
            zsf = checker.zsf_bruteforce(
                alphabet,
                lambda left, right: left ^ right,
                0,
                4,
            )
            self.assertEqual(zsf, rank)

    def test_two_site_support_obstruction_is_recomputed_from_primitives(self) -> None:
        checker = load_checker()
        check = getattr(checker, "check_r6m_two_site_support_obstruction", None)
        self.assertIsNotNone(
            check,
            "the standalone checker must expose the claimed two-site obstruction",
        )
        result = check()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["support_two_cost"], 5)
        self.assertEqual(result["support_at_most_one_optimum"], 6)
        self.assertEqual(result["strict_gap"], 1)
        self.assertEqual(result["frame_six_tuples_enumerated"], 7**6)
        self.assertEqual(result["feasible_frame_six_tuples"], 12**3)
        self.assertEqual(result["tag_keys_enumerated"], 16)
        self.assertTrue(result["complete_support_at_most_one_enumeration"])

    def test_r6i_word_length_is_joint_block_column_support(self) -> None:
        checker = load_checker()
        check = getattr(checker, "check_r6i_joint_column_statistic", None)
        self.assertIsNotNone(
            check,
            "the checker must distinguish joint active columns from individual weight",
        )
        result = check()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["disjoint_example_joint_columns"], 2)
        self.assertEqual(result["disjoint_example_maximum_individual_weight"], 1)
        self.assertTrue(result["statistics_are_not_interchangeable"])
        self.assertEqual(result["block_a_basis_rank"], 5)
        self.assertEqual(result["block_b_basis_rank"], 5)
        self.assertTrue(result["basis_vectors_are_10_bit_encodings"])

    def test_cli_output_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            completed = subprocess.run(
                [sys.executable, str(CHECKER), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            stdout_result = json.loads(completed.stdout)
            file_result = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(stdout_result, file_result)
            self.assertTrue(file_result["all_passed"])


if __name__ == "__main__":
    unittest.main()
