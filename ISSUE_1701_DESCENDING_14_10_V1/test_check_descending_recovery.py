#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("checker", HERE / "check_descending_recovery.py")
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)

def load(root: Path, name: str):
    return json.loads((root / name).read_text(encoding="utf-8"))

def dump(root: Path, name: str, obj) -> None:
    (root / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def rewrite_sums(root: Path) -> None:
    rows = []
    for p in sorted(root.iterdir(), key=lambda q: q.name):
        if p.is_file() and p.name != "SHA256SUMS":
            rows.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    (root / "SHA256SUMS").write_text("\n".join(rows) + "\n", encoding="utf-8")

class HostileMutations(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / HERE.name
        shutil.copytree(HERE, self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def assert_rejected(self, label: str) -> None:
        with self.assertRaises(CHECKER.ValidationError, msg=label):
            CHECKER.validate(self.root)

    def test_01_whole_branch_merge_is_rejected(self) -> None:
        v = load(self.root, "RECOVERY_MANIFEST.json")
        v["whole_branch_merge_performed"] = True
        dump(self.root, "RECOVERY_MANIFEST.json", v); rewrite_sums(self.root)
        self.assert_rejected("whole branch merge")

    def test_02_direct_main_commit_is_rejected(self) -> None:
        v = load(self.root, "COMMIT_BASE.json")
        v["direct_main_commit"] = True
        dump(self.root, "COMMIT_BASE.json", v); rewrite_sums(self.root)
        self.assert_rejected("direct main")

    def test_03_orion14_400_case_table_fabrication_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][0]["optional_reduct"]["requested_400_case_table_committed"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("fabricated 400-case table")

    def test_04_orion14_stale_pdf_promotion_is_rejected(self) -> None:
        v = load(self.root, "LIVE_MAIN_RECONCILIATION.json")
        v["package_hash_boundaries"]["orion14"]["old_filing_bytes_valid_for_live_main"] = True
        dump(self.root, "LIVE_MAIN_RECONCILIATION.json", v); rewrite_sums(self.root)
        self.assert_rejected("stale ORION-14 PDF")

    def test_05_orion14_null_collapse_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][0]["optional_reduct"]["binary_encoding_admits_no_sufficient_set"] = False
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-14 null collapse")

    def test_06_orion13_necessity_inflation_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][1]["separator"]["full_coordinate_necessity_determined"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-13 necessity inflation")

    def test_07_orion13_other_coordinates_discarded_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][1]["separator"]["other_coordinates_proved_unnecessary"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-13 corpus confound")

    def test_08_orion12_recall_rescue_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][2]["external_gate"]["recall_gate_passed"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-12 recall rescue")

    def test_09_orion12_ndcg_compensation_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][2]["external_gate"]["ndcg_can_rescue_primary_gate"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-12 nDCG compensation")

    def test_10_orion12_stale_archive_promotion_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][2]["package"]["old_filing_bytes_valid_for_live_main"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-12 stale package")

    def test_11_orion11_duplicate_recovery_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][3]["integration_terminal"] = "RECOVERY_READY_FOR_PATHWISE_INTEGRATION"
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-11 duplicate recovery")

    def test_12_orion11_original_cannot_check_erasure_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][3]["faithful_comparator"]["original_replication_history_retained"] = False
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-11 history erasure")

    def test_13_orion11_repair_outcome_leak_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][3]["faithful_comparator"]["stage1_executes_new_arms"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-11 outcome leak")

    def test_14_orion11_costed_result_rescue_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][3]["costed_ordering"]["g3_cost_ratio_passed"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-11 cost rescue")

    def test_15_orion10_expression_size_rescue_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][4]["explanation_gap"]["expression_size_can_rescue_mixed_fibre"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-10 size rescue")

    def test_16_orion10_all_n_authority_is_rejected(self) -> None:
        v = load(self.root, "PAPER_STATUS_V1.json")
        v["papers"][4]["explanation_gap"]["all_n_theorem_authority"] = True
        dump(self.root, "PAPER_STATUS_V1.json", v); rewrite_sums(self.root)
        self.assert_rejected("ORION-10 all-n inflation")

    def test_17_source_branch_head_drift_is_rejected(self) -> None:
        v = load(self.root, "RECOVERY_MANIFEST.json")
        v["artifacts"][0]["branch_head"] = "0" * 40
        dump(self.root, "RECOVERY_MANIFEST.json", v); rewrite_sums(self.root)
        self.assert_rejected("branch head drift")

    def test_18_checksum_tamper_is_rejected(self) -> None:
        with (self.root / "README.md").open("a", encoding="utf-8") as f:
            f.write("\ntamper\n")
        self.assert_rejected("checksum mismatch")

if __name__ == "__main__":
    unittest.main(verbosity=2)
