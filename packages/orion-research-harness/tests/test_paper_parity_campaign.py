from __future__ import annotations

from pathlib import Path

from orion_research_harness import (
    ResearchWorkspace,
    build_donor_campaign_manifest,
    run_campaign,
    run_campaign_cycle,
)
from orion_research_harness.donor_campaign import (
    build_donor_campaign_manifest as module_build_donor_campaign_manifest,
)


def _problem(profile: str) -> dict[str, object]:
    return {
        "problem_id": f"parity-{profile}",
        "question": "Find the strongest defensible method and preserve all unresolved obligations.",
        "scope": "Use strongest donors before ORION-only claims.",
        "initial_domain_ids": ["quantum"] if profile == "orion-q" else ["science"],
        "success_criteria": ["No donor omission.", "No authority escalation."],
        "navigation_profile": profile,
    }


def test_donor_campaign_builder_root_export_is_module_identity():
    assert build_donor_campaign_manifest is module_build_donor_campaign_manifest


def test_normal_orion_campaign_is_immediately_terminal_when_no_external_donor(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    manifest = build_donor_campaign_manifest(_problem("orion"))
    assert manifest["donor_registry_id"] == "orion:donors:normal:v2"
    assert manifest["initial_phase"] == "DONOR_COMPLETE"
    result = run_campaign(workspace, manifest)
    assert result["status"] == "TERMINAL"
    assert result["cycles"][-1]["terminal"] == "DONOR_BASELINE_SATURATED"
    assert result["grants_scientific_authority"] is False


def test_orion_q_campaign_requests_external_donor_and_advances_on_bound_result(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    manifest = build_donor_campaign_manifest(_problem("orion-q"))
    assert manifest["donor_registry_id"] == "orion:donors:orion-q:v2"
    assert len(manifest["capabilities"]) == 13
    first = run_campaign_cycle(workspace, manifest, auto_service_local=False)
    assert first["status"] == "PENDING_CAPABILITY"
    request = first["request"]
    assert request["capability"] == "DONOR_EXECUTE"
    capability_id = request["payload"]["capability"]["capability_id"]
    workspace.ingest_result(
        request["request_id"],
        success=True,
        output={
            "capability_id": capability_id,
            "status": "SUCCESS",
            "candidate_summary": "Donor produced a bounded candidate; ORION must independently verify it.",
            "verifier_status": "DONOR_VERIFIER_PASS",
            "resource_summary": "matched-budget receipt present",
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
        },
        executor="test-donor-host",
    )
    advanced = run_campaign_cycle(workspace, manifest, auto_service_local=False)
    assert advanced["status"] == "ADVANCED"
    assert advanced["capability_id"].startswith("execute:orion-q:")
    assert advanced["state"]["cycle_index"] == 1
    assert advanced["grants_scientific_authority"] is False


def test_donor_campaign_rejects_authority_escalation(tmp_path: Path):
    workspace = ResearchWorkspace.initialize(tmp_path / "ws", project_root=tmp_path)
    manifest = build_donor_campaign_manifest(_problem("orion-q"))
    first = run_campaign_cycle(workspace, manifest, auto_service_local=False)
    request = first["request"]
    capability_id = request["payload"]["capability"]["capability_id"]
    workspace.ingest_result(
        request["request_id"],
        success=True,
        output={
            "capability_id": capability_id,
            "status": "SUCCESS",
            "candidate_summary": "unsafe claim",
            "verifier_status": "PASS",
            "resource_summary": "receipt",
            "grants_scientific_authority": True,
        },
        executor="hostile-donor",
    )
    import pytest

    with pytest.raises(ValueError, match="authority escalation"):
        run_campaign_cycle(workspace, manifest, auto_service_local=False)
