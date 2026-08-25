from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


RUNNER = Path(__file__).with_name("run_des_novelty_01.py")
SPEC = importlib.util.spec_from_file_location("des_novelty_runner", RUNNER)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
FREEZE = json.loads(Path(__file__).with_name("FREEZE_V1.json").read_text())


def test_absent_external_review_fails_closed(tmp_path: Path) -> None:
    attained, errors, transfer = MODULE.validate_transfer(tmp_path, FREEZE)
    assert attained is False
    assert errors == ["EXTERNAL_NOVELTY_TRANSFER_V1.json absent"]
    assert transfer is None


def test_internal_reviewers_do_not_establish_external_authority(tmp_path: Path) -> None:
    digest = "a" * 64
    reviewers = {
        dimension: {
            "reviewer_id": f"reviewer-{dimension}",
            "lineage_overlaps_orion": dimension == "exact",
            "signed_report_sha256": digest,
        }
        for dimension in MODULE.DIMENSIONS
    }
    payload = {
        "schema": "orion.des.external-novelty-transfer.v1",
        "job_id": MODULE.JOB_ID,
        "subject_revision": FREEZE["subject_revision"],
        "claim_atoms_sha256": FREEZE["claim_atoms"]["sha256"],
        "reviewers": reviewers,
        "domain_expert_adjudicator": {
            "adjudicator_id": "adjudicator",
            "lineage_overlaps_orion": False,
            "signed_adjudication_sha256": digest,
        },
        "no_material_change_rounds": [
            {
                "claim_atoms_sha256": FREEZE["claim_atoms"]["sha256"],
                "material_change": False,
                "signed_round_receipt_sha256": digest,
            },
            {
                "claim_atoms_sha256": FREEZE["claim_atoms"]["sha256"],
                "material_change": False,
                "signed_round_receipt_sha256": digest,
            },
        ],
        "inaccessible_work_clearance": {"cleared": True, "basis_sha256": digest},
        "sealed_before_executor_outcome_access": True,
        "executor_outcome_accessed_before_freeze": False,
    }
    (tmp_path / "EXTERNAL_NOVELTY_TRANSFER_V1.json").write_text(json.dumps(payload))
    attained, errors, _ = MODULE.validate_transfer(tmp_path, FREEZE)
    assert attained is False
    assert "exact reviewer independence not established" in errors
