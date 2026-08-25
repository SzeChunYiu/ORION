from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p5_des_01", HERE / "run_p5_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text())


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def test_freeze_is_exact_noncompensatory_and_separates_authority() -> None:
    freeze = load("FREEZE_V1.json")
    RUNNER.validate_freeze(freeze)
    assert freeze["subject_revision"] == "3c97b87f4f4c8c0365226019236c83d3c4c7bb37"
    assert freeze["study"]["case_denominator"] == 2228
    assert freeze["study"]["arms"] == [
        "no_edit_control",
        "swe_agent_fixed_solver",
        "moss_direct_self_edit",
        "darwin_godel_machine_archive_self_edit",
        "adias_issue_centric_optimization",
        "double_ratchet_metric_only_evolution",
        "scienceclaw_representation_regime",
        "protected_orion_external_adoption",
    ]
    assert freeze["study"]["seeds"] == [5005, 5006, 5007]
    assert freeze["study"]["planned_run_cell_denominator"] == 53472
    assert freeze["decision_rule"]["scalarization"] == "FORBIDDEN"
    assert freeze["authority_separation"] == {
        "candidate": "ARM_ISOLATED_WRITE_CUSTODY",
        "evaluator": "INDEPENDENT_PROTECTED_EVALUATOR_CUSTODY",
        "threshold": "PRE_OUTCOME_EXTERNAL_THRESHOLD_CUSTODY",
        "adoption": "EXTERNAL_HOST_ONLY_ADOPTION_CUSTODY",
    }
    assert freeze["terminals"]["positive"] == (
        "PROTECTED_RECURSIVE_IMPROVEMENT_WITHOUT_SELF_PROMOTION_EXTERNALLY_SUPPORTED"
    )


def test_planned_rows_retain_the_full_public_fresh_and_sentinel_denominators() -> None:
    rows = RUNNER.planned_case_rows()
    assert len(rows) == 2228
    assert len({row["case_id"] for row in rows}) == 2228
    counts = RUNNER.case_counts(rows)
    assert counts == {
        "swe_bench_verified_public_cases": 500,
        "fresh_powered_primary_cases": 768,
        "fresh_powered_replication_cases": 768,
        "fresh_sentinel_primary_cases": 96,
        "fresh_sentinel_replication_cases": 96,
    }
    assert all(row["status"] == "CANNOT_CHECK" for row in rows)
    assert all(row["outcome"] is None for row in rows)
    assert all(row["eligible_for_primary"] is False for row in rows)


def test_result_packet_is_denominator_complete_and_digest_bound() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    raw = load("RAW_MANIFEST_V1.json")
    counts = packet["denominators"]
    assert counts["case_denominator"] == 2228
    assert counts["fresh_powered_cases"] == 1536
    assert counts["fresh_sentinel_cases"] == 192
    assert counts["arm_denominator"] == 8
    assert counts["seed_denominator"] == 3
    assert counts["planned_run_cell_denominator"] == 53472
    assert counts["run_cells_executed"] == 0
    assert counts["cases_executed"] == 0
    assert counts["cases_cannot_check"] == 2228
    assert len(packet["case_outcomes"]) == 2228
    assert len(raw["case_outcomes"]) == 2228
    assert all(row["status"] == "CANNOT_CHECK" for row in packet["case_outcomes"])
    assert packet["raw_manifest_sha256"] == sha256("RAW_MANIFEST_V1.json")
    assert packet["freeze_sha256"] == sha256("FREEZE_V1.json")
    assert packet["paper_authority_delta"] == "NONE"
    assert packet["external_authority_state"] == "CANNOT_CHECK"
    assert packet["exact_terminal"] == (
        "SWE_BENCH_RIGHTS_AND_PROTECTED_FRESH_ADOPTION_CUSTODY_UNAVAILABLE"
    )


def test_no_weak_proxy_fixture_reuse_or_negative_history_erasure() -> None:
    freeze = load("FREEZE_V1.json")
    donor = load("IDEAL_DONOR_RESULT_V1.json")
    controls = load("NEGATIVE_CONTROLS_V1.json")
    primary = load("PRIMARY_RESULT_V1.json")
    assert donor["weak_proxy_substituted"] is False
    assert donor["state"] == "NOT_RUN"
    assert freeze["exclusions"]["existing_96_case_lineage"] == (
        "DIAGNOSTIC_ONLY_NO_TERMINAL_NOT_ELIGIBLE_FOR_P5_DES_01"
    )
    assert freeze["exclusions"]["authored_hidden_cause_fixtures"] == (
        "NOT_PROTECTED_NOT_ELIGIBLE"
    )
    assert controls["existing_96_case_lineage"] == "EXCLUDED_NOT_RESEALED_NOT_REUSED"
    assert controls["authored_fixture_substitution"] is False
    assert primary["cannot_check_rows"] == 2228
    assert primary["negative_or_harmful_rows"] == 0
    assert primary["rows_dropped"] == 0


def test_missing_transfer_state_never_reads_or_hashes_directories(tmp_path: Path) -> None:
    for filename in RUNNER.REQUIRED_TRANSFER_FILES.values():
        (tmp_path / filename).mkdir()
    state = RUNNER.transfer_state(tmp_path)
    assert all(item["present"] is False for item in state.values())
    assert all(item["sha256"] is None for item in state.values())


def test_all_required_outputs_exist_and_are_canonical_json() -> None:
    for name in RUNNER.EXPECTED_OUTPUTS:
        path = HERE / name
        payload = json.loads(path.read_text())
        assert path.read_bytes() == RUNNER.canonical_bytes(payload)
