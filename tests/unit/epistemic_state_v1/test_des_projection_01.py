from dataclasses import fields
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = (
    ROOT
    / "research"
    / "orion-epistemic-state-v1"
    / "results"
    / "DES-PROJECTION-01"
    / "run_des_projection_01.py"
)
SPEC = importlib.util.spec_from_file_location("orion_des_projection_01", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


def test_freeze_denominator_matches_cartesian_class():
    freeze = json.loads(RUNNER_PATH.with_name("FREEZE_V1.json").read_text())
    product = 1
    for factor in freeze["case_denominator"]["factors"]:
        product *= len(factor["values"])

    assert product == RUNNER.EXPECTED_STATE_CASES == 2_880
    assert 2 * product == RUNNER.EXPECTED_PROJECTION_ROWS == 5_760
    assert len(list(RUNNER.factor_cases())) == product


def test_reference_and_oracles_agree_on_boundary_fixtures():
    policy = RUNNER.promotion_policy("paper:write")
    fixtures = [
        {
            "responsibility_matches": True,
            "identified": "TRUE",
            "obligations_complete": True,
            "support_complete": True,
            "active_defeater": False,
            "custody_external": True,
            "authority_present": True,
            "evidence_mode": "PARTIAL",
            "open_method_gap": False,
        },
        {
            "responsibility_matches": True,
            "identified": "CANNOT_CHECK",
            "obligations_complete": True,
            "support_complete": True,
            "active_defeater": False,
            "custody_external": True,
            "authority_present": True,
            "evidence_mode": "KNOWN_TRUE",
            "open_method_gap": False,
        },
        {
            "responsibility_matches": True,
            "identified": "TRUE",
            "obligations_complete": True,
            "support_complete": True,
            "active_defeater": False,
            "custody_external": False,
            "authority_present": False,
            "evidence_mode": "KNOWN_TRUE",
            "open_method_gap": False,
        },
    ]

    for factors_map in fixtures:
        promotion = policy.project(RUNNER.make_state(factors_map))
        assert promotion is RUNNER.oracle_promotion(factors_map)
        assert RUNNER.readiness_projection(
            promotion, factors_map["evidence_mode"]
        ) is RUNNER.oracle_readiness(factors_map)


def test_precondition_accepts_frozen_state_shape(tmp_path):
    state_check = next(
        item
        for item in RUNNER.preconditions(tmp_path)
        if item["id"] == "reference_state_field_count"
    )

    assert len(fields(RUNNER.State)) == 20
    assert state_check["expected"] == 20
    assert state_check["passed"] is True


def test_artifact_record_serializes_external_test_output(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text("{}\n")

    record = RUNNER.artifact_record(artifact)

    assert record["path"] == artifact.resolve().as_posix()
    assert record["bytes"] == 3


def test_case_exception_is_retained_as_cannot_check(monkeypatch):
    case = next(iter(RUNNER.factor_cases()))

    def fail_state(_factors_map):
        raise ValueError("retained test exception")

    monkeypatch.setattr(RUNNER, "make_state", fail_state)
    rows = RUNNER.execute_cases([case])

    assert len(rows) == 1
    assert rows[0]["case_id"] == case[0]
    assert rows[0]["execution_status"] == "CANNOT_CHECK"
    assert rows[0]["exception"]["type"] == "ValueError"


def test_case_id_renaming_control_detects_case_id_leakage(monkeypatch):
    cases = list(RUNNER.factor_cases())[:2]
    rows = RUNNER.execute_cases(cases)
    clean_evaluate_case = RUNNER.evaluate_case

    def contaminated_evaluate_case(case_id, factors_map):
        row = clean_evaluate_case(case_id, factors_map)
        if case_id.startswith("renamed-"):
            row["next_action"] = "CONTAMINATED_BY_CASE_ID"
        return row

    monkeypatch.setattr(RUNNER, "evaluate_case", contaminated_evaluate_case)
    controls = RUNNER.build_negative_controls(rows, {"all_reachable_groups_noninjective": True})
    case_id_control = next(
        item for item in controls["controls"] if item["control_id"] == "CASE_ID_RENAMING"
    )

    assert case_id_control["passed"] is False
    assert controls["all_passed"] is False
    assert controls["leakage_detected"] is True


@pytest.mark.parametrize(
    ("system", "raw", "expected"),
    [("Darwin", 1_048_576, 1.0), ("Linux", 1_024, 1.0)],
)
def test_resident_memory_units_are_normalized(system, raw, expected):
    assert RUNNER.resident_memory_mib(raw, system=system) == expected
