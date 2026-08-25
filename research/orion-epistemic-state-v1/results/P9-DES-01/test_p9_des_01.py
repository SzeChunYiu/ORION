from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p9_des_01", HERE / "run_p9_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def test_freeze_and_axes_are_exact() -> None:
    freeze = load("FREEZE_V1.json")
    RUNNER.validate_freeze(freeze)
    assert len(RUNNER.model_cell_ids(freeze)) == 1344
    assert len(set(RUNNER.model_cell_ids(freeze))) == 1344
    assert len(RUNNER.numerical_cell_ids(freeze)) == 12
    assert len(set(RUNNER.numerical_cell_ids(freeze))) == 12
    assert freeze["decision_rule"]["scalarization"] == "FORBIDDEN"


def test_packet_is_denominator_complete_and_cannot_check() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    counts = packet["denominators"]
    assert counts["model_cell_denominator"] == 1344
    assert counts["numerical_cell_denominator"] == 12
    assert counts["planned_cell_denominator"] == 1356
    assert counts["cells_executed"] == 0
    assert counts["cells_cannot_check"] == 1356
    assert counts["slurm_jobs_submitted"] == 0
    assert counts["gpu_jobs_submitted"] == 0
    assert counts["rows_dropped"] == 0
    assert len(packet["case_outcomes"]) == 1356
    assert all(row["status"] == "CANNOT_CHECK" for row in packet["case_outcomes"])
    assert packet["exact_terminal"] == "OPEN_WEIGHT_AND_NUMERICAL_BUILD_CUSTODY_UNAVAILABLE"


def test_no_proxy_and_gpu_prohibition() -> None:
    preflight = load("ACQUISITION_PREFLIGHT_V1.json")
    donor = load("IDEAL_DONOR_RESULT_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    assert preflight["gpu_execution_permitted"] is False
    assert preflight["weak_proxy_substituted"] is False
    assert donor["state"] == "NOT_RUN"
    assert donor["weak_proxy_substituted"] is False
    assert controls["classical_capacity_ladder_substituted_for_open_weights"] is False
    assert controls["package_version_manifest_treated_as_binary_identity"] is False
    assert controls["null_adverse_cannot_check_erased"] is False


def test_packet_digests_and_authority_boundary() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    assert packet["freeze_sha256"] == sha256("FREEZE_V1.json")
    assert packet["raw_manifest_sha256"] == sha256("RAW_MANIFEST_V1.json")
    for name, digest in packet["component_sha256"].items():
        assert sha256(name) == digest
    assert packet["external_authority_state"] == "CANNOT_CHECK"
    assert packet["manuscript_writing_owner"] == "P1_P15_REWRITE_LANE"
    assert packet["paper_authority_delta"] == "NONE"


def test_all_outputs_are_canonical_json() -> None:
    for name in (*RUNNER.EXPECTED_OUTPUTS, *RUNNER.CUSTOM_OUTPUTS):
        payload = load(name)
        assert (HERE / name).read_bytes() == RUNNER.canonical_bytes(payload)
