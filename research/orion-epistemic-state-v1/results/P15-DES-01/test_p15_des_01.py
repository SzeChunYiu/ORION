from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p15_des_01", HERE / "run_p15_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def test_freeze_retains_the_exact_production_denominator_and_donor_family() -> None:
    freeze = load("FREEZE_V1.json")
    RUNNER.validate_freeze(freeze)
    assert freeze["subject_revision"] == "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
    assert freeze["study"]["case_denominator"] == 50
    assert freeze["study"]["production_workload_denominator"] == 30
    assert freeze["study"]["fault_denominator"] == 20
    assert freeze["study"]["runtime_images"] == [
        "runtime_image_slot_01",
        "runtime_image_slot_02",
        "runtime_image_slot_03",
    ]
    assert freeze["study"]["sites"] == [
        "primary_production_site",
        "independent_cross_site_replay",
    ]
    assert freeze["study"]["arms"] == [
        "nominal_logs",
        "structured_provenance",
        "deterministic_replay",
        "multi_lane_agreement",
        "production_attestation_product",
        "dynamic_sei",
        "ideal_execution_science_product",
    ]
    assert freeze["study"]["seeds"] == [1515, 1516, 1517]
    assert freeze["study"]["planned_run_cell_denominator"] == 6300
    assert freeze["decision_rule"]["scalarization"] == "FORBIDDEN"
    assert freeze["terminals"]["cannot_check"] == (
        "P15_PRODUCTION_HOST_PROCESS_KEY_CUSTODY_AND_CROSS_SITE_REPLAY_CANNOT_CHECK"
    )
    assert freeze["terminals"]["positive"] == (
        "DYNAMIC_EXECUTION_INTEGRITY_NONINTERFERENCE_PRODUCTION_REPLICATED"
    )


def test_planned_rows_are_unique_fault_balanced_and_denominator_complete() -> None:
    rows = RUNNER.planned_case_rows()
    assert len(rows) == 50
    assert len({row["case_id"] for row in rows}) == 50
    assert RUNNER.case_counts(rows) == {
        "production_workloads": 30,
        "host_resource_faults": 5,
        "process_lifecycle_publication_race_faults": 5,
        "key_attestation_custody_faults": 5,
        "evaluator_site_custody_faults": 5,
    }
    assert all(row["status"] == "CANNOT_CHECK" for row in rows)
    assert all(row["outcome"] is None for row in rows)
    assert all(row["eligible_for_hypothesis_testing"] is False for row in rows)


def test_result_packet_binds_every_row_and_preserves_prospective_hypotheses() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    raw = load("RAW_MANIFEST_V1.json")
    primary = load("PRIMARY_RESULT_V1.json")
    counts = packet["denominators"]
    assert counts["case_denominator"] == 50
    assert counts["production_workload_denominator"] == 30
    assert counts["fault_denominator"] == 20
    assert counts["runtime_image_denominator"] == 3
    assert counts["site_denominator"] == 2
    assert counts["arm_denominator"] == 7
    assert counts["seed_denominator"] == 3
    assert counts["planned_run_cell_denominator"] == 6300
    assert counts["run_cells_executed"] == 0
    assert counts["cases_cannot_check"] == 50
    assert len(packet["case_outcomes"]) == 50
    assert packet["case_outcomes"] == raw["case_outcomes"]
    assert packet["freeze_sha256"] == sha256("FREEZE_V1.json")
    assert packet["raw_manifest_sha256"] == sha256("RAW_MANIFEST_V1.json")
    assert packet["exact_terminal"] == (
        "P15_PRODUCTION_HOST_PROCESS_KEY_CUSTODY_AND_CROSS_SITE_REPLAY_CANNOT_CHECK"
    )
    assert packet["paper_authority_delta"] == "NONE"
    assert packet["external_authority_state"] == "CANNOT_CHECK"
    assert primary["hypotheses"] == {
        name: "PROSPECTIVE_NOT_EXECUTED"
        for name in ("H1", "H2", "H3", "H4", "H5", "H6", "H7")
    }


def test_bounded_receipts_and_unbound_remote_lineage_are_not_substituted() -> None:
    freeze = load("FREEZE_V1.json")
    donor = load("IDEAL_DONOR_RESULT_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    custom = load("P15_PRODUCTION_NONINTERFERENCE_RESULT_V1.json")
    assert donor["weak_proxy_substituted"] is False
    assert donor["state"] == "NOT_RUN"
    assert freeze["exclusions"]["bounded_sei_provenance_attestation_receipts"] == (
        "RETAINED_BOUNDED_EVIDENCE_NOT_PRODUCTION_OR_CROSS_SITE_SUBSTITUTE"
    )
    assert freeze["exclusions"]["lunarc_exec_p15_01"] == (
        "UNBOUND_INTERNAL_LINEAGE_NOT_PRODUCTION_OR_INDEPENDENT_SITE_AUTHORITY"
    )
    assert controls["internal_fixture_substitution"] is False
    assert controls["same_site_replay_treated_as_independent"] is False
    assert controls["existing_bounded_receipts"]["sei_case_denominator"] == 18
    assert controls["existing_bounded_receipts"]["provenance_attestation_case_denominator"] == 22
    assert controls["existing_bounded_receipts"]["full_key_compromise_signature_detections"] == 0
    assert controls["existing_bounded_receipts"]["full_key_compromise_false_promotions"] == 6
    assert custom["production_cases_scored"] == 0
    assert custom["cross_site_replays_completed"] == 0
    assert custom["production_noninterference_estimate"] is None


def test_missing_transfer_state_does_not_treat_directories_as_inputs(tmp_path: Path) -> None:
    for filename in RUNNER.REQUIRED_TRANSFER_FILES.values():
        (tmp_path / filename).mkdir()
    state = RUNNER.transfer_state(tmp_path)
    assert all(item["present"] is False for item in state.values())
    assert all(item["sha256"] is None for item in state.values())


def test_all_required_outputs_are_canonical_json() -> None:
    for name in RUNNER.EXPECTED_OUTPUTS:
        path = HERE / name
        payload = json.loads(path.read_text())
        assert path.read_bytes() == RUNNER.canonical_bytes(payload)
