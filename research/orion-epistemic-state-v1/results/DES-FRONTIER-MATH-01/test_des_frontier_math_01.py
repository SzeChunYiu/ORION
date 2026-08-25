from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_des_frontier_math_01.py")
SPEC = importlib.util.spec_from_file_location("des_frontier_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
FREEZE = json.loads(Path(__file__).with_name("FREEZE_V1.json").read_text())


def test_absent_external_target_fails_closed(tmp_path: Path) -> None:
    attained, errors, transfer = MODULE.validate_transfer(tmp_path, FREEZE)
    assert attained is False
    assert errors == ["FRONTIER_MATH_ESCROW_TRANSFER_V1.json absent"]
    assert transfer is None


def test_self_custodied_target_is_not_external(tmp_path: Path) -> None:
    payload = {
        "schema": "orion.des.frontier-math-escrow-transfer.v1",
        "job_id": MODULE.JOB,
        "subject_revision": FREEZE["subject_revision"],
        "target_id": "t",
        "external_custodian_id": "orion",
        "custodian_lineage_overlaps_orion": True,
        "sealed_before_executor_access": True,
        "executor_saw_target_or_outcome": False,
        "target_statement_sha256": "a" * 64,
        "old_grammar_sha256": "b" * 64,
        "exact_checker_sha256": "c" * 64,
        "donor_refusal_sha256": "d" * 64,
        "heldout_siblings_sha256": "e" * 64,
    }
    (tmp_path / "FRONTIER_MATH_ESCROW_TRANSFER_V1.json").write_text(json.dumps(payload))
    attained, errors, _ = MODULE.validate_transfer(tmp_path, FREEZE)
    assert attained is False
    assert "external custody independence not established" in errors
