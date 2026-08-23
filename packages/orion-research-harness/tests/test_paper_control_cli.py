from __future__ import annotations

import json

from orion_research_harness.paper_cli import main


def _read(capsys):
    return json.loads(capsys.readouterr().out)


def test_mechanic_apply_cli_executes_p6_contract(capsys):
    payload = {
        "state": {
            "coordinate_values": {"x": "old"},
            "claim_statuses": {"q": "CERTIFIED"},
            "dependencies": [],
            "evidence_ids": ["e:base"],
            "provenance_ids": ["p:base"],
            "hard_obligations": [],
            "authorities": [],
            "protected_root_ids": ["root:protected"],
            "epoch": 1,
            "history": [],
        },
        "contract": {
            "mechanic_id": "m:set-x",
            "read_ids": ["x"],
            "write_ids": ["x"],
            "write_values": {"x": "new"},
        },
    }
    assert main(["mechanic-apply", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    assert result["result"]["terminal"] == "APPLIED"
    assert result["result"]["state"]["coordinate_values"] == [["x", "new"]]
    assert result["grants_scientific_authority"] is False


def test_dependency_repair_cli_reopens_p6_affected_claims(capsys):
    payload = {
        "state": {
            "coordinate_values": {},
            "claim_statuses": {"q_root": "CERTIFIED", "q_child": "CERTIFIED"},
            "dependencies": [["q_root", "q_child"]],
            "evidence_ids": ["e:base"],
            "provenance_ids": ["p:base"],
            "hard_obligations": [],
            "authorities": [],
            "protected_root_ids": ["root:protected"],
            "epoch": 1,
            "history": [],
        },
        "changed_ids": ["q_root"],
        "certificates": [],
    }
    assert main(["dependency-repair", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    statuses = dict(result["state"]["claim_statuses"])
    assert statuses == {"q_root": "OPEN", "q_child": "OPEN"}


def test_authority_check_cli_executes_p8_typed_gate(capsys):
    jt = {"domain": "ASSERT", "kind": "PASS", "scope_ids": ["subject"], "content_contract": "sha256:content", "epoch": 1}
    payload = {
        "effect": {"effect_id": "e", "domain": "ASSERT", "operation": "commit", "scope_ids": ["subject"], "payload_digest": "sha256:payload", "epoch": 1},
        "context": {
            "judgments": [{"judgment_id": "j", "judgment_type": jt, "support_premise_ids": ["premise:science"]}],
            "hard_obligations": [{"obligation_id": "o", "required_type": jt, "additional_premise_ids": ["premise:science"]}],
            "roots": [{"grant_id": "g", "domain": "ASSERT", "scope_ids": ["subject"], "root_id": "root:standing", "root_class": "STANDING_POLICY", "epoch": 1, "payload_digest": "sha256:payload"}],
            "coercions": [],
            "blocker_determinations": {"blocker:absolute": "REFUTED"},
            "required_blocker_type_ids": ["blocker:absolute"],
            "valid_premise_ids": ["premise:science", "root:standing"],
            "revoked_premise_ids": [],
            "support_families": [],
            "history": [],
        },
    }
    assert main(["authority-check", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    assert result["decision"]["terminal"] == "AUTHORIZED"
    assert result["grants_scientific_authority"] is False


def test_ocme_assess_cli_preserves_lower_level_cause(capsys):
    payload = {
        "episode_id": "ocme:cli",
        "problem_model_frozen": True,
        "verifier_available": True,
        "access_model_frozen": True,
        "resource_model_frozen": True,
        "lower_level_results": [{"check_id": "REPRESENTATION_REPAIR", "route_kind": "REPRESENTATION_REPAIR", "succeeded": True, "evidence_ids": ["e:repair"]}],
        "obstruction": None,
        "candidate_edit": None,
        "outside_closure": None,
        "transfer": None,
        "problem_solving_gain": True,
        "donor_same_reach": False,
        "independent_reproduction": False,
    }
    assert main(["ocme-assess", "--json", json.dumps(payload)]) == 0
    result = _read(capsys)
    assert result["decision"]["terminal"] == "OCME_LOWER_LEVEL_CAUSE"
    assert result["decision"]["jump_open"] is False


def test_p11_p14_law_commands_are_host_invokable(capsys):
    assert main(["p11-accessible-rank", "20", "3"]) == 0
    assert _read(capsys)["rank_dimension"] == 1140

    assert main(["p12-allocate", "2", "0", "--budget", "2"]) == 0
    assert _read(capsys)["allocation"] == [2, 0]

    assert main(["p13-action", "Z1", "VERIFY"]) == 0
    assert _read(capsys)["action"] == "CANNOT_CHECK"

    facts = {
        "evidence_integrity": True,
        "frozen_protocol": True,
        "identifiable": True,
        "positive": True,
        "donor_owned": False,
        "interaction_only": False,
        "live_negative_history": False,
        "material_new_evidence": True,
    }
    assert main(["p14-disposition", "--json", json.dumps(facts)]) == 0
    assert _read(capsys)["disposition"] == "SUPPORTED_RESIDUAL"
