from __future__ import annotations

from pathlib import Path

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import initialize_campaign, run_campaign
from orion_research_harness.domains.orion_rg import (
    X1B_C15_CANDIDATE_PROOF_AUDIT_CAMPAIGN_MANIFEST,
)
from orion_research_harness.domains.registry import builtin_campaign_ids
from orion_research_harness.workspace import ResearchWorkspace


def test_c15_candidate_proof_audit_runs_non_authorizing(tmp_path):
    manifest = X1B_C15_CANDIDATE_PROOF_AUDIT_CAMPAIGN_MANIFEST
    validate_manifest(manifest)
    assert manifest["campaign_id"] in builtin_campaign_ids()

    repo_root = Path(__file__).resolve().parents[3]
    workspace = ResearchWorkspace.initialize(
        tmp_path / "c15-audit-ws",
        project_root=repo_root,
        allow_process_tools=True,
    )
    initial = initialize_campaign(workspace, manifest)
    assert initial.phase_id == "S0"
    assert initial.authority_ceiling == "INTERNAL_CANDIDATE_PROOF_AUDIT_ONLY"

    outcome = run_campaign(
        workspace,
        manifest,
        max_cycles=4,
        auto_service_local=True,
    )
    assert outcome["status"] == "TERMINAL"
    assert outcome["terminal"] == (
        "X1B_C15_CANDIDATE_PROOF_INTERNAL_AUDIT_PASSED__EXTERNAL_REVIEW_PENDING"
    )

    final = CampaignState.from_dict(
        workspace.load_latest_campaign_state(manifest["campaign_id"])
    )
    assert final.phase_id == "INTERNAL_AUDIT_RECORDED"
    assert final.observation_map["X1B_C15_ARTIFACT_INTEGRITY"] == "YES"
    assert final.observation_map["X1B_C15_RESIDUAL_TREE_AUDITED"] == "YES"
    assert final.observation_map["X1B_C15_INTERNAL_AUDIT_PASS"] == "YES"

    # A passing internal audit is deliberately not a theorem/novelty promotion.
    assert final.authority_ceiling == "INTERNAL_CANDIDATE_PROOF_AUDIT_ONLY"
    assert len(workspace.pending_requests()) == 0
