#!/usr/bin/env python3
"""Mutation tests for the issue #1701 descending closure packet."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("closure_checker", HERE / "check_descending_closure.py")
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def load(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))


def dump(root: Path, name: str, value) -> None:
    (root / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rewrite_sums(root: Path) -> None:
    lines = []
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.name != "SHA256SUMS"):
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


class DescendingClosureMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / HERE.name
        shutil.copytree(HERE, self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def assert_rejected(self, fragment: str) -> None:
        with self.assertRaises(checker.ValidationError) as ctx:
            checker.validate(self.root)
        self.assertIn(fragment, str(ctx.exception))

    def test_01_canonical_packet_is_green(self) -> None:
        checks = checker.validate(self.root)
        self.assertGreaterEqual(len(checks), 10)

    def test_02_wrong_descending_order_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["paper_order"] = [24, 25, 23, 22, 21, 20]
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("descending order")

    def test_03_fake_top_tier_promotion_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["papers"][0]["issue_terminal"] = "TOP_TIER_SUCCESSOR_EARNED"
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("unexecuted top-tier promotion")

    def test_04_same_operator_independence_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["papers"][0]["successor"]["organizational_independence"]["status"] = "PASS"
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("organizational independence self-certified")

    def test_05_orion24_duplicate_lane_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["papers"][1]["canonical_active_lane"]["duplicate_work"] = True
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("ORION-24 duplicate programme")

    def test_06_orion23_duplicate_lane_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["papers"][2]["canonical_active_lane"]["duplicate_work"] = True
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("ORION-23 duplicate acquisition")

    def test_07_fake_lunarc_success_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["papers"][4]["current_result"]["scientific_execution_run"] = True
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("ORION-21 fake scientific execution")

    def test_08_orion20_indispensability_conflation_is_rejected(self) -> None:
        value = load(self.root, "PAPER_STATUS_V1.json")
        value["papers"][5]["current_result"]["structural_indispensability"] = True
        dump(self.root, "PAPER_STATUS_V1.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("ORION-20 order/structure conflation")

    def test_09_checksum_tamper_is_rejected(self) -> None:
        with (self.root / "README.md").open("a", encoding="utf-8") as handle:
            handle.write("\ntamper\n")
        self.assert_rejected("checksum mismatch")

    def test_10_missing_external_artifact_digest_is_rejected(self) -> None:
        value = load(self.root, "EXTERNAL_SYSTEM_PINS.json")
        value["systems"][0]["artifacts"][0]["sha256"] = "0"
        dump(self.root, "EXTERNAL_SYSTEM_PINS.json", value)
        rewrite_sums(self.root)
        self.assert_rejected("bad artifact SHA-256")


if __name__ == "__main__":
    unittest.main(verbosity=2)
