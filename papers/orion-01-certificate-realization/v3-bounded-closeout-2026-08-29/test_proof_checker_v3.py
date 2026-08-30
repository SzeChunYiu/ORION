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
        self.assertEqual(by_name["restricted_F2_rank_bound"]["families"], 138)
        self.assertEqual(
            by_name["exact_one_argument_restore_sensitivity"]["comparisons"],
            582528,
        )
        self.assertEqual(
            by_name["proper_deletion_and_zero_sum_free_terminal"]["fixtures"], 3
        )

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
