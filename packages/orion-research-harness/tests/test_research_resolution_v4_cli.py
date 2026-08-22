from __future__ import annotations

import json

from orion_research_harness.paper_cli import main


def _read(capsys):
    return json.loads(capsys.readouterr().out)


def test_resolution_plan_cli_builds_active_evidence_obligation(capsys):
    payload = {
        "outcome_kind": "UNRESOLVED",
        "subject_id": "claim:x",
        "unresolved_class": "EVIDENCE",
        "reason_codes": ["MISSING_INDEPENDENT_VERIFICATION"],
        "required_object_ids": ["verify:claim:x"],
    }
    assert main(["resolution-plan", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    assert result["schema"] == "ORION.ResearchResolutionObligation.v1"
    assert result["outcome_kind"] == "UNRESOLVED"
    assert result["state"] == "ACTIVE"
    assert result["next_actions"] == ["ACQUIRE_EVIDENCE", "VERIFY_EVIDENCE"]
    assert result["grants_global_task_stop_authority"] is False


def test_resolution_plan_cli_preserves_negative_as_negative(capsys):
    payload = {
        "outcome_kind": "NEGATIVE",
        "result_id": "negative:1",
        "subject_id": "method:x",
        "negative_kind": "DONOR_SUBSUMED",
        "evidence_ids": ["e:donor"],
        "reason_codes": ["SAME_REACH_UNDER_FROZEN_MODEL"],
    }
    assert main(["resolution-plan", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    assert result["schema"] == "ORION.ResearchNegativeResult.v1"
    assert result["outcome_kind"] == "NEGATIVE"
    assert "REGISTER_DONOR_SUBSUMPTION" in result["dispositions"]
    assert result["grants_novelty_authority"] is False


def test_p13_cannot_check_is_not_bare(capsys):
    assert main(["p13-action", "Z1", "VERIFY"]) == 0
    result = _read(capsys)
    assert result["action"] == "CANNOT_CHECK"
    assert result["resolution_obligation"]["schema"] == "ORION.ResearchResolutionObligation.v1"
    assert result["resolution_obligation"]["next_actions"] == ["DIAGNOSE_RESPONSIBILITY"]
