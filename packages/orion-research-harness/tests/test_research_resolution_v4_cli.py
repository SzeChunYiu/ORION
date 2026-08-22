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


def test_research_direct_resource_bound_uses_resource_resolution_not_responsibility(capsys):
    payload = {
        "solution_status": "CANNOT_CHECK",
        "residuals": [],
        "resource_bound_hit": True,
        "identity_ambiguity_hit": False,
    }
    assert main(["research-direct", "--json", json.dumps(payload)]) == 4
    result = _read(capsys)
    assert result["kind"] == "CANNOT_CHECK"
    resolution = result["resolution_obligation"]
    assert resolution["unresolved_class"] == "RESOURCE"
    assert "REQUEST_RESOURCE_WIDENING" in resolution["next_actions"]
    assert "DIAGNOSE_RESPONSIBILITY" not in resolution["next_actions"]


def _donor_subsumed_payload_with_shared_evidence():
    route_kinds = (
        "SEARCH_MORE",
        "REPRESENTATION_REPAIR",
        "IMPLEMENTATION_REPAIR",
        "LIBRARY_RETRIEVAL",
        "ACTION_ABSTRACTION_MACRO_MINING",
        "PROOF_REPAIR",
        "PROGRAM_SYNTHESIS",
        "EVOLUTIONARY_SEARCH",
    )
    return {
        "episode_id": "ocme:shared-evidence",
        "problem_model_frozen": True,
        "verifier_available": True,
        "access_model_frozen": True,
        "resource_model_frozen": True,
        "lower_level_results": [
            {
                "check_id": f"check:{kind}",
                "route_kind": kind,
                "succeeded": False,
                "evidence_ids": [f"e:{kind}"],
            }
            for kind in route_kinds
        ],
        "obstruction": {
            "certificate_id": "obs:shared",
            "kind": "EXACT_FINITE_NONREACHABILITY",
            "target_id": "target:1",
            "old_closure_ids": ["m:a", "m:b"],
            "evidence_ids": ["e:shared"],
            "independently_verified": True,
            "all_registered_baselines_exhausted": True,
            "timeout_only": False,
        },
        "candidate_edit": {
            "edit_id": "edit:new",
            "semantic_operator_ids": ["m:new"],
            "claimed_new_reach_ids": ["target:1", "held:1"],
            "expands_to_old_closure": False,
            "access_model_ids": ["access:v1"],
        },
        "outside_closure": {
            "verification_id": "outside:1",
            "edit_id": "edit:new",
            "verifier_id": "checker:independent",
            "candidate_issuer_id": "candidate:generator",
            "outside_old_closure": True,
            "evidence_ids": ["e:outside"],
        },
        "transfer": {
            "held_out_ids": ["held:1"],
            "positive_transfer_ids": ["held:1"],
            "frozen_access_model_ids": ["access:v1"],
            "false_expansion_rate": 0.0,
            "false_expansion_guard": 0.05,
            "semantic_preservation": True,
            "strong_baseline_same_reach": True,
            "evidence_ids": ["e:shared"],
        },
        "problem_solving_gain": True,
        "donor_same_reach": True,
        "independent_reproduction": True,
    }


def test_ocme_donor_negative_deduplicates_shared_evidence(capsys):
    payload = _donor_subsumed_payload_with_shared_evidence()
    assert main(["ocme-assess", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    assert result["decision"]["terminal"] == "OCME_DONOR_SUBSUMED"
    negative = result["negative_result"]
    assert negative["outcome_kind"] == "NEGATIVE"
    assert negative["evidence_ids"] == ["e:shared"]
    assert "REGISTER_DONOR_SUBSUMPTION" in negative["dispositions"]


def test_p13_cannot_check_is_not_bare(capsys):
    assert main(["p13-action", "Z1", "VERIFY"]) == 0
    result = _read(capsys)
    assert result["action"] == "CANNOT_CHECK"
    assert result["resolution_obligation"]["schema"] == "ORION.ResearchResolutionObligation.v1"
    assert result["resolution_obligation"]["next_actions"] == ["DIAGNOSE_RESPONSIBILITY"]
