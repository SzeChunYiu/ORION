from __future__ import annotations

from copy import deepcopy

import pytest

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState, ProtectedReference
from orion_research_harness.campaign_runner import initialize_campaign, run_campaign
from orion_research_harness.workspace import ResearchWorkspace


def _manifest():
    return {
        "schema": "ORION.ResearchCampaignManifest.v1",
        "campaign_id": "strict:campaign",
        "claim_id": "strict:claim",
        "initial_phase": "N0",
        "initial_observations": {"READY": "YES"},
        "protected_refs": [
            {
                "ref_id": "fresh",
                "path": "protected/fresh.txt",
                "blob": "",
                "released": False,
            }
        ],
        "capabilities": {
            "strict.compute": {
                "host_capability": "PYTHON",
                "payload": {
                    "code": "print('STRICT={\"ok\": true, \"value\": \"YES\"}')",
                    "cwd": ".",
                    "timeout": 5,
                },
                "result_contract": {
                    "kind": "SHELL_JSON_TOKEN",
                    "prefix": "STRICT=",
                    "required_payload_values": [
                        {"path": ["ok"], "equals": True}
                    ],
                    "evidence_rules": [
                        {
                            "evidence_key": "DONE",
                            "path": ["value"],
                            "transform": "STRING",
                        }
                    ],
                },
                "next_phase": "DONE",
            }
        },
        "phases": {
            "N0": {
                "active_hard_obligations": ["DO"],
                "responsibility_hypotheses": [
                    {
                        "hypothesis_id": "RESP:STRICT",
                        "expected_observations": {"READY": ["YES"]},
                    }
                ],
                "interface_checks": [
                    {
                        "check_id": "IFACE:STRICT",
                        "scope": "STRICT",
                        "state": "PASS",
                        "required": True,
                    }
                ],
                "revision_mechanics": [
                    {
                        "mechanic_id": "REV:STRICT",
                        "kind": "SEARCH_MORE",
                        "write_coordinates": ["SEARCH"],
                        "cost": 1.0,
                    }
                ],
                "computation_actions": [
                    {
                        "action_id": "COMPUTE:STRICT",
                        "kind": "VERIFY",
                        "expected_decision_value": 2.0,
                        "cost": 1.0,
                        "discharges_obligations": ["DO"],
                    }
                ],
                "responsibility_bindings": {"RESP:STRICT": ["REV:STRICT"]},
                "selected_capabilities": {"COMPUTE:STRICT": "strict.compute"},
            },
            "DONE": {
                "terminal": True,
                "terminal_name": "STRICT_DONE",
                "active_hard_obligations": [],
            },
        },
    }


def test_protected_release_never_truthy_string_coerces():
    with pytest.raises(TypeError, match="protected released must be a boolean"):
        ProtectedReference.from_dict(
            {
                "ref_id": "fresh",
                "path": "protected/fresh.txt",
                "blob": "",
                "released": "false",
            }
        )


def test_campaign_state_cycle_index_never_string_coerces(tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    state = initialize_campaign(workspace, _manifest())
    raw = state.as_dict()
    raw["cycle_index"] = "0"
    with pytest.raises(TypeError, match="cycle_index must be an integer"):
        CampaignState.from_dict(raw)


def test_campaign_state_authority_flags_must_remain_literal_false(tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    raw = initialize_campaign(workspace, _manifest()).as_dict()
    raw["grants_scientific_authority"] = True
    with pytest.raises(ValueError, match="authority field must be false"):
        CampaignState.from_dict(raw)


def test_manifest_rejects_string_expected_observation_instead_of_character_splitting():
    manifest = _manifest()
    manifest["phases"]["N0"]["responsibility_hypotheses"][0][
        "expected_observations"
    ]["READY"] = "YES"
    with pytest.raises(TypeError, match="expected observation values must be an array"):
        validate_manifest(manifest)


def test_manifest_rejects_truthy_string_interface_required():
    manifest = _manifest()
    manifest["phases"]["N0"]["interface_checks"][0]["required"] = "false"
    with pytest.raises(TypeError, match="interface required must be a boolean"):
        validate_manifest(manifest)


def test_malformed_successful_campaign_receipt_freezes_state(tmp_path):
    workspace = ResearchWorkspace.initialize(
        tmp_path / "ws", project_root=tmp_path, allow_process_tools=False
    )
    manifest = _manifest()
    initial = initialize_campaign(workspace, manifest)

    first = run_campaign(workspace, manifest, max_cycles=1, auto_service_local=False)
    assert first["status"] == "PENDING_CAPABILITY"
    request_id = first["cycles"][0]["request"]["request_id"]
    workspace.ingest_result(
        request_id,
        success=True,
        output={
            "returncode": 0,
            "stdout": "STRICT={\"ok\": true, \"value\": 7}\n",
            "stderr": "",
        },
        executor="hostile-host",
    )

    outcome = run_campaign(workspace, manifest, max_cycles=1, auto_service_local=False)
    assert outcome["status"] == "CAPABILITY_CONTRACT_FAILED"
    cycle = outcome["cycles"][0]
    assert cycle["status"] == "CAPABILITY_CONTRACT_FAILED"
    assert "STRING transform requires a string" in cycle["error"]
    assert cycle["grants_scientific_authority"] is False

    after = CampaignState.from_dict(
        workspace.load_latest_campaign_state("strict:campaign")
    )
    assert after.state_digest == initial.state_digest
    assert after.phase_id == "N0"
    assert after.cycle_index == 0
    assert "DONE" not in after.observation_map


def test_successful_receipt_with_boolean_as_integer_returncode_is_rejected(tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    manifest = _manifest()
    initial = initialize_campaign(workspace, manifest)
    pending = run_campaign(workspace, manifest, max_cycles=1, auto_service_local=False)
    request_id = pending["cycles"][0]["request"]["request_id"]
    workspace.ingest_result(
        request_id,
        success=True,
        output={
            "returncode": False,
            "stdout": "STRICT={\"ok\": true, \"value\": \"YES\"}\n",
            "stderr": "",
        },
        executor="hostile-host",
    )
    outcome = run_campaign(workspace, manifest, max_cycles=1, auto_service_local=False)
    assert outcome["status"] == "CAPABILITY_CONTRACT_FAILED"
    assert "returncode must be an integer" in outcome["cycles"][0]["error"]
    after = CampaignState.from_dict(
        workspace.load_latest_campaign_state("strict:campaign")
    )
    assert after.state_digest == initial.state_digest


def test_manifest_shadow_allowlist_cannot_silently_reference_unknown_mechanic():
    manifest = _manifest()
    manifest["phases"]["N0"]["shadow_allowed_revision_ids"] = ["REV:TYPO"]
    with pytest.raises(ValueError, match="shadow allowlist references unknown mechanics"):
        validate_manifest(manifest)
