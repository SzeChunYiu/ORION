from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p10_des_01", HERE / "run_p10_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def test_freeze_retains_the_exact_wide_denominator_and_donor_family() -> None:
    freeze = load("FREEZE_V1.json")
    RUNNER.validate_freeze(freeze)
    assert freeze["subject_revision"] == "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
    assert freeze["study"]["case_denominator"] == 480
    assert freeze["study"]["protected_task_denominator"] == 400
    assert freeze["study"]["known_method_control_denominator"] == 80
    assert freeze["study"]["arms"] == [
        "orion_dynamic_method_expansion",
        "no_jump_control",
        "exact_exhaustive_search",
        "retrieval_and_repair",
        "program_or_tactic_synthesis",
        "representation_only_transform",
        "library_learning",
        "evolutionary_search",
        "ideal_donor_composed_search",
    ]
    assert freeze["study"]["seeds"] == [1010, 1011, 1012]
    assert freeze["study"]["planned_run_cell_denominator"] == 12960
    assert freeze["decision_rule"]["scalarization"] == "FORBIDDEN"
    assert freeze["terminals"]["cannot_check"] == (
        "P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT"
    )
    assert freeze["terminals"]["positive"] == (
        "VERIFIED_METHOD_SPACE_EXPANSION_BEYOND_IDEAL_DONOR_COMPOSED_SEARCH"
    )


def test_planned_rows_are_unique_and_denominator_complete() -> None:
    rows = RUNNER.planned_case_rows()
    assert len(rows) == 480
    assert len({row["case_id"] for row in rows}) == 480
    assert RUNNER.case_counts(rows) == {
        "lean_tasks": 100,
        "lean_known_method_controls": 20,
        "sygus_tasks": 100,
        "sygus_known_method_controls": 20,
        "ipc_tasks": 100,
        "ipc_known_method_controls": 20,
        "code_tasks": 100,
        "code_known_method_controls": 20,
    }
    assert all(row["status"] == "CANNOT_CHECK" for row in rows)
    assert all(row["outcome"] is None for row in rows)
    assert all(row["eligible_for_hypothesis_testing"] is False for row in rows)


def test_result_packet_binds_every_row_and_preserves_prospective_hypotheses() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    raw = load("RAW_MANIFEST_V1.json")
    primary = load("PRIMARY_RESULT_V1.json")
    counts = packet["denominators"]
    assert counts["case_denominator"] == 480
    assert counts["protected_task_denominator"] == 400
    assert counts["known_method_control_denominator"] == 80
    assert counts["domain_denominator"] == 4
    assert counts["arm_denominator"] == 9
    assert counts["seed_denominator"] == 3
    assert counts["planned_run_cell_denominator"] == 12960
    assert counts["run_cells_executed"] == 0
    assert counts["cases_cannot_check"] == 480
    assert len(packet["case_outcomes"]) == 480
    assert packet["case_outcomes"] == raw["case_outcomes"]
    assert packet["freeze_sha256"] == sha256("FREEZE_V1.json")
    assert packet["raw_manifest_sha256"] == sha256("RAW_MANIFEST_V1.json")
    assert packet["exact_terminal"] == "P10_FULL_FROZEN_DONOR_EVALUATOR_INPUTS_ABSENT"
    assert packet["paper_authority_delta"] == "NONE"
    assert packet["external_authority_state"] == "CANNOT_CHECK"
    assert primary["hypotheses"] == {
        name: "PROSPECTIVE_NOT_EXECUTED" for name in ("H1", "H2", "H3", "H4", "H5", "H6")
    }


def test_no_internal_or_weaker_proxy_is_promoted() -> None:
    freeze = load("FREEZE_V1.json")
    donor = load("IDEAL_DONOR_RESULT_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    custom = load("P10_OBSTRUCTION_AND_FALSE_INVENTION_RESULT_V1.json")
    assert donor["weak_proxy_substituted"] is False
    assert donor["state"] == "NOT_RUN"
    assert freeze["exclusions"]["generated_exact_setting_ocme"] == (
        "EXACT_SETTING_ONLY_NOT_A_NATIVE_DOMAIN_DONOR_OR_HELD_TRANSFER_RESULT"
    )
    assert freeze["exclusions"]["native_lean_11842_transition_lineage"] == (
        "CANNOT_CHECK_NATIVE_STATE_COVERAGE_NOT_ELIGIBLE"
    )
    assert controls["internal_fixture_substitution"] is False
    assert controls["timeout_treated_as_obstruction"] is False
    assert controls["known_method_controls"]["planned_denominator"] == 80
    assert custom["candidate_edits_scored"] == 0
    assert custom["false_inventions"] is None
    assert custom["outside_closure_certificates"] == 0


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
