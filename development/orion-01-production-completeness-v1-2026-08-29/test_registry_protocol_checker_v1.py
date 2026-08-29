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
CHECKER = ROOT / "registry_protocol_checker_v1.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("orion01_registry_protocol_checker_v1", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegistryProtocolCheckerTests(unittest.TestCase):
    def test_import_surface_is_standard_library_only(self) -> None:
        tree = ast.parse(CHECKER.read_text(encoding="utf-8"))
        roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        self.assertEqual(
            roots,
            {"__future__", "argparse", "hashlib", "json", "pathlib", "typing"},
        )

    def test_frozen_protocol_passes_without_source_outcome(self) -> None:
        result = load_checker().run_checks()
        self.assertTrue(result["implementation_independent"])
        self.assertFalse(result["source_instance_executed"])
        self.assertTrue(result["all_passed"])
        self.assertEqual(
            result["terminal"],
            "PROTOCOL_FREEZE_VALIDATED__NO_SOURCE_OUTCOME",
        )
        by_name = {row["name"]: row for row in result["checks"]}
        self.assertEqual(by_name["required_files_and_no_outcome_leakage"]["future_only_files_absent"], 18)
        self.assertEqual(by_name["protocol_identity_order_and_gates"]["phases"], 6)
        self.assertEqual(by_name["theorem_question_and_claim_boundaries"]["obligations"], 6)
        self.assertEqual(by_name["adverse_and_cannot_check_ledger"]["rows"], 2)

    def test_cli_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "protocol-check.json"
            completed = subprocess.run(
                [sys.executable, str(CHECKER), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                json.loads(completed.stdout),
                json.loads(output.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
