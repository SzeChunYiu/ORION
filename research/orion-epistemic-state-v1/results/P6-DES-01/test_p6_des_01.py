from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("run_p6_des_01", HERE / "run_p6_des_01.py")
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes()).hexdigest()


def test_freeze_is_exact_and_noncompensatory() -> None:
    freeze = load("FREEZE_V1.json")
    RUNNER.validate_freeze(freeze)
    assert freeze["study"]["primary_case_denominator"] == 16
    assert freeze["study"]["domain_denominator"] == 4
    assert freeze["decision_rule"]["scalarization"] == "FORBIDDEN"
    assert freeze["terminals"]["positive"] == (
        "EXACT_DYNAMIC_REVALIDATION_STRICTLY_EXTENDS_NATIVE_DEPENDENCY_SELECTION"
    )
    assert freeze["chronology"]["historical_outcome_visibility"] != "NONE"


def test_primary_result_preserves_exactness_savings_and_donor_absorption() -> None:
    primary = load("PRIMARY_RESULT_V1.json")
    exact = primary["policy_results"]["exact_dynamic_revalidation"]
    native = primary["policy_results"]["native_dependency_selector"]
    assert primary["exact_terminal"] == (
        "EXACT_DYNAMIC_REVALIDATION_STRICTLY_EXTENDS_NATIVE_DEPENDENCY_SELECTION"
    )
    assert exact["exact_accuracy"] == 1.0
    assert exact["retained_invalid"] == 0
    assert exact["unnecessary_reopen"] == 0
    assert native["retained_invalid"] > 0
    assert len(primary["native_unsafe_domains"]) == 4
    assert all(row["exact_work_savings_vs_full_reset"] > 0 for row in primary["domain_results"])

    donor = load("IDEAL_DONOR_RESULT_V1.json")
    assert donor["weak_proxy_substituted"] is False
    assert donor["ideal_case_level_agreement_with_exact"] is True
    assert donor["donor_absorption_state"] == "IDEAL_PRODUCT_EQUIVALENT_ON_FROZEN_PANEL"
    assert donor["external_donor_execution"] == "CANNOT_CHECK"


def test_mutations_and_negative_controls_are_denominator_complete() -> None:
    controls = load("NEGATIVE_CONTROLS_V1.json")
    audit = controls["mutation_audit"]
    assert controls["ets_case_denominator"] == 18
    assert controls["ets_exact_matches"] == 18
    assert controls["assumption_case_denominator"] == 12
    assert audit["mutation_denominator"] == 4
    assert audit["mutations_killed"] == 4
    assert audit["mutations_survived"] == []
    assert controls["label_leakage_audit"]["passed"] is True
    assert controls["adverse_and_cannot_check_rows_retained"] is True
    assert controls["rows_dropped"] == 0


def test_packet_binds_every_output_and_retains_authority_boundary() -> None:
    packet = load("RESULT_BINDING_PACKET_V1.json")
    counts = packet["denominators"]
    assert counts["primary_case_denominator"] == 16
    assert counts["domain_denominator"] == 4
    assert counts["policy_denominator"] == 4
    assert counts["primary_policy_decision_denominator"] == 64
    assert counts["mutation_denominator"] == counts["mutations_killed"] == 4
    assert counts["rows_dropped"] == 0
    assert len(packet["case_outcomes"]) == 16
    assert packet["freeze_sha256"] == sha256("FREEZE_V1.json")
    assert packet["raw_manifest_sha256"] == sha256("RAW_MANIFEST_V1.json")
    for name, digest in packet["component_sha256"].items():
        assert sha256(name) == digest
    assert packet["external_authority_state"] == "CANNOT_CHECK"
    assert packet["paper_authority_delta"] == "NONE"
    assert packet["manuscript_writing_owner"] == "P1_P15_REWRITE_LANE"


def test_native_checks_and_json_are_complete() -> None:
    receipts = load("NATIVE_CHECKER_RECEIPTS_V1.json")
    assert receipts["checker_denominator"] == 7
    assert receipts["checkers_passed"] == 7
    assert receipts["all_passed"] is True
    assert all(row["same_programme_only"] for row in receipts["rows"])
    for name in (*RUNNER.EXPECTED_OUTPUTS, *RUNNER.CUSTOM_OUTPUTS):
        payload = load(name)
        assert (HERE / name).read_bytes() == RUNNER.canonical_bytes(payload)
