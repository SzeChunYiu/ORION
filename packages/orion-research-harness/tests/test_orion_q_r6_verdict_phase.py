from __future__ import annotations

from orion_research_harness.domains.orion_q import MAX_R6_CAMPAIGN_MANIFEST


def test_r6_prospective_replay_capability_is_registered():
    capability = MAX_R6_CAMPAIGN_MANIFEST["capabilities"]["orion_q.r6_prospective_replay"]
    assert capability["host_capability"] == "SHELL"
    assert capability["payload"]["argv"] == [
        "python",
        "max_r6_exact_tare3_prospective_replay.py",
    ]
    assert capability["next_phase"] == "R6_VERDICT"
    contract = capability["result_contract"]
    assert contract["prefix"] == "ORIONQ_MAX_R6_EXACT_TARE3_PROSPECTIVE_REPLAY="
    evidence_keys = {rule["evidence_key"] for rule in contract["evidence_rules"]}
    assert {
        "R6_EARNED",
        "R6_PROSPECTIVE_AUTHORITY",
        "R6_PROTECTED_SUBJECT_ACCESSED",
    } <= evidence_keys


def test_r6_verdict_is_recorded_not_required():
    # The campaign must record the frozen gate outcome as evidence; it must
    # never make campaign success conditional on r6_earned being true, and it
    # must never mention the protected subject in the capability declaration.
    capability = MAX_R6_CAMPAIGN_MANIFEST["capabilities"]["orion_q.r6_prospective_replay"]
    required = capability["result_contract"]["required_payload_values"]
    assert all(row["path"] != ["r6_earned"] for row in required)
    protected_path = MAX_R6_CAMPAIGN_MANIFEST["protected_refs"][0]["path"]
    assert protected_path not in " ".join(capability["payload"]["argv"])
    assert all(
        protected_path not in declared
        for declared in capability["declared_read_paths"]
    )


def test_p10_result_phase_forces_prospective_evaluation():
    phase = MAX_R6_CAMPAIGN_MANIFEST["phases"]["P10_RESULT"]
    assert phase.get("terminal") is not True
    assert phase["active_hard_obligations"] == ["R6_PROSPECTIVE_GATE_EVALUATION"]
    action = next(
        item
        for item in phase["computation_actions"]
        if item["action_id"] == "COMPUTE:R6_PROSPECTIVE_REPLAY"
    )
    assert action["discharges_obligations"] == ["R6_PROSPECTIVE_GATE_EVALUATION"]
    assert (
        phase["selected_capabilities"]["COMPUTE:R6_PROSPECTIVE_REPLAY"]
        == "orion_q.r6_prospective_replay"
    )


def test_r6_verdict_terminal_grants_no_authority():
    phase = MAX_R6_CAMPAIGN_MANIFEST["phases"]["R6_VERDICT"]
    assert phase["terminal"] is True
    assert phase["terminal_name"] == "R6_PROSPECTIVE_VERDICT_RECORDED__NOT_SELF_AUTHORIZING"
    assert (
        MAX_R6_CAMPAIGN_MANIFEST["authority_ceiling"]
        == "BELOW_R6_UNTIL_PROTECTED_PROMOTION"
    )
