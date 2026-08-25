from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p1_des_01", HERE / "run_p1_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def test_freeze_is_exact_and_noncompensatory() -> None:
    freeze = load("FREEZE_V1.json")
    RUNNER.validate_freeze(freeze)
    assert freeze["subject_revision"] == "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
    assert freeze["study"]["case_denominator"] == 150
    assert freeze["study"]["arms"] == [
        "dynamic_responsibility_conditioned_minimal_reconstruction",
        "one_shot_reconstruction",
        "reflection_reconstruction",
        "no_reconstruction",
        "donor_complete_diagnosis",
    ]
    assert freeze["decision_rule"]["scalarization"] == "FORBIDDEN"
    assert freeze["terminals"]["positive"] == (
        "RESPONSIBILITY_CONDITIONED_MINIMAL_RECONSTRUCTION_PROSPECTIVELY_SUPPORTED"
    )


def test_result_packet_is_denominator_complete_and_bound() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    raw = load("RAW_MANIFEST_V1.json")
    counts = packet["denominators"]
    assert counts["case_denominator"] == 150
    assert counts["scienceagentbench_cases"] == 102
    assert counts["counterfactual_cases"] == 48
    assert counts["arm_denominator"] == 5
    assert counts["stochastic_repeats"] == 5
    assert counts["planned_run_cell_denominator"] == 3750
    assert counts["run_cells_executed"] == 0
    assert len(packet["case_outcomes"]) == 150
    assert len(raw["case_outcomes"]) == 150
    assert all(row["status"] == "CANNOT_CHECK" for row in packet["case_outcomes"])
    assert packet["raw_manifest_sha256"] == sha256("RAW_MANIFEST_V1.json")
    assert packet["freeze_sha256"] == sha256("FREEZE_V1.json")
    assert packet["paper_authority_delta"] == "NONE"
    assert packet["external_authority_state"] == "CANNOT_CHECK"


def test_no_proxy_or_negative_history_erasure() -> None:
    donor = load("IDEAL_DONOR_RESULT_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    primary = load("PRIMARY_RESULT_V1.json")
    assert donor["weak_proxy_substituted"] is False
    assert donor["state"] == "NOT_RUN"
    assert controls["prompt_template_probe"].startswith("PREVIOUS_66_CASE_LINEAGE_KNOWN_TO_LEAK")
    assert primary["cannot_check_rows"] == 150
    assert primary["negative_or_harmful_rows"] == 0
    assert primary["rows_dropped"] if "rows_dropped" in primary else True


def test_all_required_outputs_exist_and_are_canonical_json() -> None:
    for name in RUNNER.EXPECTED_OUTPUTS:
        path = HERE / name
        payload = json.loads(path.read_text())
        assert path.read_bytes() == RUNNER.canonical_bytes(payload)
