from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_des_responsibility_01.py")
SPEC = importlib.util.spec_from_file_location("des_responsibility_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
FREEZE = json.loads(Path(__file__).with_name("FREEZE_V1.json").read_text())


def test_absent_escrow_fails_closed(tmp_path: Path) -> None:
    attained, errors, transfer = MODULE.validate_escrow(tmp_path, FREEZE)
    assert attained is False
    assert errors == ["ESCROW_TRANSFER_V1.json absent"]
    assert transfer is None


def test_self_custodied_or_small_transfer_is_rejected(tmp_path: Path) -> None:
    payload = {
        "schema": "orion.des.external-incident-escrow-transfer.v1",
        "job_id": MODULE.JOB_ID,
        "subject_revision": FREEZE["subject_revision"],
        "external_custodian_id": "same-programme",
        "custodian_lineage_overlaps_orion": True,
        "domains": ["one"],
        "case_count": 1,
        "outcome_accessed_by_executor": False,
        "freeze_precedes_outcome_access": True,
        "sealed_case_manifest_sha256": "a" * 64,
        "external_scorer_sha256": "b" * 64,
        "gold_sha256": "c" * 64,
    }
    (tmp_path / "ESCROW_TRANSFER_V1.json").write_text(json.dumps(payload))
    attained, errors, _ = MODULE.validate_escrow(tmp_path, FREEZE)
    assert attained is False
    assert "custodian independence is not established" in errors
    assert "fewer than three external domains" in errors
    assert "external case denominator below freeze" in errors
