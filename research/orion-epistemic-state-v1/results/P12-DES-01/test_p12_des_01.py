from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p12_des_01", HERE / "run_p12_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def test_freeze_and_preflight_fail_closed() -> None:
    freeze = load("FREEZE_V1.json")
    preflight = load("LUNARC_PREFLIGHT_V1.json")
    RUNNER.validate_freeze(freeze)
    RUNNER.validate_preflight(preflight)
    assert freeze["current_flat_stopgo"]["clean_license_case_denominator"] == 96
    assert preflight["scienceagentbench"]["official_archive"]["all_entries_encrypted"] is True
    assert preflight["scienceagentbench"]["official_evaluation_runnable"] is False


def test_case_rows_are_exact_and_complete() -> None:
    rows = RUNNER.planned_case_rows(load("../../../../papers/orion-22-adaptive-state-reasoning/runtime/P12_CAMPAIGN_PLAN_V1.json"))
    assert len(rows) == 96
    assert len({row["task_family"] for row in rows}) == 24
    assert {row["domain"] for row in rows} == {
        "Computational Chemistry",
        "Geographical Information Science",
        "Bioinformatics",
        "Psychology and Cognitive science",
    }
    assert all(row["status"] == "CANNOT_CHECK" for row in rows)
    assert all(row["task_outcome"] is None for row in rows)


def test_generated_packet_retains_authority_and_proxy_boundaries() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    assert packet["exact_terminal"] == RUNNER.TERMINAL
    assert packet["denominators"]["planned_run_cell_denominator"] == "CANNOT_CHECK_NOT_FROZEN"
    assert packet["denominators"]["run_cells_executed"] == 0
    assert packet["denominators"]["slurm_jobs_submitted"] == 0
    assert packet["manuscript_writing_owner"] == "P1_P15_REWRITE_LANE"
    assert packet["computation_session_paper_authority_delta"] == "NONE"
    assert controls["metadata_parseability_substituted_for_task_outcomes"] is False
    assert controls["historical_nonflat_result_substituted"] is False
