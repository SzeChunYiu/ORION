#!/usr/bin/env python3
"""Mutation tests for the ORION-19 through ORION-15 recovery packet."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("recovery_checker", HERE / "check_descending_recovery.py")
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

class DescendingRecoveryMutationTests(unittest.TestCase):
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
        self.assertGreaterEqual(len(checker.validate(self.root)), 12)
    def test_02_wrong_order_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["paper_order"] = [18, 19, 17, 16, 15]
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("descending order")
    def test_03_orion19_da_pass_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][0]["v3"]["d_a_decision"] = "ACCESSIBILITY"
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("D-A CANNOT_CHECK erased")
    def test_04_orion19_v2_failure_erasure_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][0]["v3"]["v2_terminal_retained"] = "SUPPORTED"
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("V2 failure erased")
    def test_05_orion19_fake_ut3_execution_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][0]["ut3"]["cells_executed"] = 1
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("UT3 execution fabricated")
    def test_06_orion18_external_validation_pass_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][1]["external_validation"] = "PASS"
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("external validation self-certified")
    def test_07_orion17_outcome_before_prediction_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][2]["chronology"]["outcome_time_utc"] = "2026-08-28T19:21:00Z"
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("prospective chronology violated")
    def test_08_orion17_filing_ready_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][2]["filing_ready"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("filing blocker erased")
    def test_09_orion17_self_adjudication_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][2]["governance"]["governance_adjudicated_by_this_packet"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("governance self-adjudicated")
    def test_10_orion16_competing_protocol_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][3]["canonical_acquisition"]["duplicate_protocol_created"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("canonical acquisition duplicated")
    def test_11_orion16_top_tier_promotion_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][3]["pr1692_result"]["top_tier_authority"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("top-tier authority self-awarded")
    def test_12_orion15_hidden_rule_defect_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][4]["independent_verification"]["rule_defect_detected"] = False
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("rule defect hidden")
    def test_13_orion15_perfect_ceiling_restoration_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json"); v["papers"][4]["glm53_harvest"]["former_perfect_treatment_ceiling_reproduced"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("perfect ceiling falsely restored")
    def test_14_source_branch_head_drift_is_rejected(self) -> None:
        v = load(self.root, "RECOVERY_MANIFEST.json"); v["artifacts"][0]["branch_head"] = "0" * 40
        dump(self.root, "RECOVERY_MANIFEST.json", v); rewrite_sums(self.root)
        self.assert_rejected("branch head drift")
    def test_15_checksum_tamper_is_rejected(self) -> None:
        with (self.root / "README.md").open("a", encoding="utf-8") as handle: handle.write("\ntamper\n")
        self.assert_rejected("checksum mismatch")

if __name__ == "__main__":
    unittest.main(verbosity=2)
