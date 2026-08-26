import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / "scripts/check_v3_donor_envelope_spec_v2.py"
STATUS = ROOT / "research/orion-discovery-v3/V3_DONOR_ENVELOPE_01_SPECIFICATION_STATUS_V2.json"
PROTOCOL = ROOT / "research/orion-discovery-v3/V3_DONOR_ENVELOPE_01_PROTOCOL_CANDIDATE_V2.json"


def _checker_api():
    spec = importlib.util.spec_from_file_location("v3_donor_spec_checker", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fail_closed_packet_validates_without_authorizing_execution() -> None:
    api = _checker_api()

    counts = api.validate()

    assert counts == {
        "atoms": 25,
        "taxonomy_occurrences": 77,
        "taxonomy_labels": 75,
        "executable_donors": 0,
        "ideal_products_blocked": 25,
        "partition_slots_unpopulated": 75,
        "remaining_blocker_classes": 6,
    }
    status = json.loads(STATUS.read_text())
    protocol = json.loads(PROTOCOL.read_text())
    assert status["readiness"] == "BLOCKED_SPECIFICATION"
    assert status["execution_authorized"] is False
    assert status["runnable_on_lunarc"] is False
    assert status["scheduler_submission"] is None
    assert protocol["execution_authorized"] is False
    assert protocol["runnable_on_lunarc"] is False


def test_checker_cli_reports_blocked_not_ready() -> None:
    completed = subprocess.run(
        [sys.executable, str(CHECKER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.startswith("V3_DONOR_ENVELOPE_01_BLOCKED_SPECIFICATION_VALID ")
    assert "executable_donors=0" in completed.stdout
    assert "partition_slots_unpopulated=75" in completed.stdout


def test_execution_cannot_be_authorized_while_packet_is_blocked() -> None:
    api = _checker_api()
    document = json.loads(STATUS.read_text())
    document["execution_authorized"] = True

    with pytest.raises(api.SpecificationError, match="execution_authorized"):
        api._require_blocked_identity(document, STATUS.name)


def test_null_material_slot_is_not_a_frozen_input() -> None:
    api = _checker_api()
    protocol = json.loads(PROTOCOL.read_text())
    candidate = copy.deepcopy(protocol["candidate_bundle"])
    candidate["candidate_id"] = "invented-candidate"

    with pytest.raises(api.SpecificationError, match="must be null"):
        api._require_null_fields(
            candidate,
            candidate["immutable_missing_fields"],
            "candidate_bundle",
        )
