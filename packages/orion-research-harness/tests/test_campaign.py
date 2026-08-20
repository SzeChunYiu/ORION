from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from orion_research_harness.campaign_control import decide_campaign, manifest_digest, validate_manifest
from orion_research_harness.campaign_protocol import CampaignState, ProtectedReference
from orion_research_harness.campaign_runner import (
    _protect_unreleased_refs,
    initialize_campaign,
    run_campaign,
)
from orion_research_harness.domains.orion_q import MAX_R6_CAMPAIGN_MANIFEST
from orion_research_harness.local_tools import service_local_request
from orion_research_harness.workspace import ResearchWorkspace


def _toy_manifest():
    return {
        "schema": "ORION.ResearchCampaignManifest.v1",
        "campaign_id": "toy:campaign",
        "claim_id": "toy:claim",
        "initial_phase": "N0",
        "initial_observations": {"READY": "YES"},
        "protected_refs": [],
        "capabilities": {
            "toy.compute": {
                "host_capability": "PYTHON",
                "payload": {
                    "code": 'print(\'TOY={"ok": true}\')',
                    "cwd": ".",
                    "timeout": 5,
                },
                "result_contract": {
                    "kind": "SHELL_JSON_TOKEN",
                    "prefix": "TOY=",
                    "required_payload_values": [{"path": ["ok"], "equals": True}],
                    "evidence_rules": [
                        {
                            "evidence_key": "DONE",
                            "path": ["ok"],
                            "transform": "BOOL_YES_NO",
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
                        "hypothesis_id": "RESP:TOY",
                        "expected_observations": {"READY": ["YES"]},
                    }
                ],
                "interface_checks": [
                    {"check_id": "IFACE:TOY", "scope": "TOY", "state": "PASS"}
                ],
                "revision_mechanics": [
                    {
                        "mechanic_id": "REV:TOY",
                        "kind": "SEARCH_MORE",
                        "write_coordinates": ["SEARCH"],
                    }
                ],
                "computation_actions": [
                    {
                        "action_id": "COMPUTE:TOY",
                        "kind": "VERIFY",
                        "expected_decision_value": 2.0,
                        "cost": 1.0,
                        "discharges_obligations": ["DO"],
                    }
                ],
                "responsibility_bindings": {"RESP:TOY": ["REV:TOY"]},
                "selected_capabilities": {"COMPUTE:TOY": "toy.compute"},
            },
            "DONE": {
                "terminal": True,
                "terminal_name": "TOY_DONE",
                "active_hard_obligations": [],
            },
        },
    }


def test_generic_campaign_runs_through_shared_local_receipts(tmp_path):
    workspace = ResearchWorkspace.initialize(
        tmp_path / "ws", project_root=tmp_path, allow_process_tools=True
    )
    manifest = _toy_manifest()
    state = initialize_campaign(workspace, manifest)
    decision = decide_campaign(state, manifest)
    assert decision.selected_kind == "COMPUTATION"
    assert decision.selected_id == "COMPUTE:TOY"

    outcome = run_campaign(workspace, manifest, max_cycles=4, auto_service_local=True)
    assert outcome["status"] == "TERMINAL"
    final = CampaignState.from_dict(workspace.load_latest_campaign_state("toy:campaign"))
    assert final.phase_id == "DONE"
    assert final.observation_map["DONE"] == "YES"
    assert final.cycle_index == 1
    assert len(workspace.pending_requests()) == 0


def test_failed_local_process_is_failed_receipt_and_does_not_advance_campaign(tmp_path):
    workspace = ResearchWorkspace.initialize(
        tmp_path / "ws", project_root=tmp_path, allow_process_tools=True
    )
    manifest = _toy_manifest()
    manifest["capabilities"]["toy.compute"]["payload"]["code"] = (
        "import sys; print('partial-evidence'); sys.exit(7)"
    )
    initial = initialize_campaign(workspace, manifest)

    outcome = run_campaign(workspace, manifest, max_cycles=1, auto_service_local=True)
    assert outcome["status"] == "CAPABILITY_FAILED"
    assert len(outcome["cycles"]) == 1
    failed_cycle = outcome["cycles"][0]
    assert failed_cycle["status"] == "CAPABILITY_FAILED"
    result = workspace.load_result(failed_cycle["request"]["request_id"])
    assert result is not None
    assert result.success is False
    assert result.output["returncode"] == 7
    assert "partial-evidence" in result.output["stdout"]
    assert result.error == "local process exited with status 7"

    after = CampaignState.from_dict(workspace.load_latest_campaign_state("toy:campaign"))
    assert after.state_digest == initial.state_digest
    assert after.phase_id == "N0"
    assert after.cycle_index == 0

    # Re-servicing cannot launder the immutable failed result into success.
    replay = service_local_request(workspace, result.request_id)
    assert replay.result_digest == result.result_digest
    assert replay.success is False


def test_campaign_manifest_is_immutable_after_state_freeze(tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    manifest = _toy_manifest()
    initialize_campaign(workspace, manifest)
    modified = deepcopy(manifest)
    modified["initial_observations"]["READY"] = "NO"
    with pytest.raises(ValueError, match="another manifest|different content"):
        initialize_campaign(workspace, modified)


def test_unreleased_protected_reference_cannot_enter_capability_payload(tmp_path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    protected = (
        ProtectedReference(
            ref_id="secret",
            path="protected/secret.txt",
            blob="deadbeef",
            released=False,
        ),
    )
    spec = {
        "host_capability": "PYTHON",
        "payload": {"code": "print('protected/secret.txt')", "cwd": "."},
    }
    with pytest.raises(PermissionError, match="unreleased protected path"):
        _protect_unreleased_refs(
            workspace=workspace,
            protected_refs=protected,
            capability_spec=spec,
        )


def _r6_state(phase_id: str, observations: dict[str, str], obligations=()):
    return CampaignState.create(
        campaign_id=MAX_R6_CAMPAIGN_MANIFEST["campaign_id"],
        claim_id=MAX_R6_CAMPAIGN_MANIFEST["claim_id"],
        phase_id=phase_id,
        cycle_index={"N0": 0, "N1": 1, "N2": 2}[phase_id],
        manifest_digest=manifest_digest(MAX_R6_CAMPAIGN_MANIFEST),
        observations=observations,
        active_hard_obligations=obligations,
        protected_refs=tuple(
            ProtectedReference.from_dict(item)
            for item in MAX_R6_CAMPAIGN_MANIFEST["protected_refs"]
        ),
        authority_ceiling="BELOW_R6_UNTIL_PROTECTED_PROMOTION",
    )


def test_orion_q_manifest_reproduces_native_n0_n1_n2_control():
    validate_manifest(MAX_R6_CAMPAIGN_MANIFEST)

    n0 = _r6_state(
        "N0",
        {"R5H_CURRENT_ALPHABET_EXACT": "YES"},
        obligations=("DONOR_GENERAL_M_TARE_CLOSURE", "DONOR_FOQCS_GENERIC_PREP_CLOSURE"),
    )
    d0 = decide_campaign(n0, MAX_R6_CAMPAIGN_MANIFEST)
    assert d0.selected_id == "COMPUTE:DONOR_CLOSURE_PACKET"
    assert d0.control["status"] == "COMPUTATION_REQUIRED"
    assert d0.shadow_control["selected_computation_action_id"] == "COMPUTE:DONOR_CLOSURE_PACKET"

    n1 = _r6_state(
        "N1",
        {
            "R5H_CURRENT_ALPHABET_EXACT": "YES",
            "GENERAL_M_DONOR_OUTCOME": "NONDOMINATING_OR_CLOSED",
            "FOQCS_GENERIC_PREP_OUTCOME": "GENERIC_MATCHED_ROUTE_AVAILABLE",
        },
    )
    d1 = decide_campaign(n1, MAX_R6_CAMPAIGN_MANIFEST)
    assert d1.responsibility["identified_hypothesis_id"] == "RESP:INTERFACE_INADEQUATE"
    assert d1.selected_id == "REV:CHANGE_INTERFACE"
    assert d1.shadow_control["selected_revision_mechanic_id"] is None

    n2 = _r6_state(
        "N2",
        {
            "R5H_CURRENT_ALPHABET_EXACT": "YES",
            "GENERAL_M_DONOR_OUTCOME": "NONDOMINATING_OR_CLOSED",
            "FOQCS_GENERIC_PREP_OUTCOME": "GENERIC_MATCHED_ROUTE_AVAILABLE",
            "FOQCS_INTERFACE_ENVELOPE": "OPTIMISTIC_BOUND_REGISTERED",
            "FOQCS_OPTIMISTIC_DOMINATES_H4_DONOR": "NO",
            "CURRENT_METHOD_INCREMENTAL_VALUE_ON_H4": "NONE_OVER_DIRECT_CLIQUE_DONOR",
        },
    )
    d2 = decide_campaign(n2, MAX_R6_CAMPAIGN_MANIFEST)
    assert d2.responsibility["identified_hypothesis_id"] == "RESP:METHOD_LANGUAGE_INADEQUATE"
    assert d2.selected_id == "REV:GROW_METHOD_LANGUAGE"
    assert d2.shadow_control["selected_revision_mechanic_id"] is None


def test_orion_q_registered_capabilities_do_not_reference_unreleased_fresh_subject(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=repo_root)
    protected = tuple(
        ProtectedReference.from_dict(item)
        for item in MAX_R6_CAMPAIGN_MANIFEST["protected_refs"]
    )
    for spec in MAX_R6_CAMPAIGN_MANIFEST["capabilities"].values():
        _protect_unreleased_refs(
            workspace=workspace,
            protected_refs=protected,
            capability_spec=spec,
        )
