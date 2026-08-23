from __future__ import annotations

from pathlib import Path

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import initialize_campaign, run_campaign
from orion_research_harness.domains.orion_rg import (
    X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST,
)
from orion_research_harness.domains.registry import builtin_campaign_ids
from orion_research_harness.workspace import ResearchWorkspace


def test_x1b_k3_confirmatory_campaign_runs_through_harness(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    manifest = X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST
    validate_manifest(manifest)
    assert manifest["campaign_id"] in builtin_campaign_ids()
    assert "orion-rg:x1c-c45-mixed-kernel-frontier" not in builtin_campaign_ids()

    workspace = ResearchWorkspace.initialize(
        tmp_path / "ws",
        project_root=repo_root,
        allow_process_tools=True,
    )
    initial = initialize_campaign(workspace, manifest)
    assert initial.phase_id == "S0"
    assert initial.authority_ceiling == "FINITE_CONFIRMATORY_RECONSTRUCTION_ONLY"

    outcome = run_campaign(
        workspace,
        manifest,
        max_cycles=2,
        auto_service_local=True,
    )
    assert outcome["status"] == "TERMINAL"
    assert (
        outcome["terminal"]
        == "X1B_K3_FINITE_CONFIRMATORY_RECONSTRUCTION__NO_C15_THEOREM_AUTHORITY"
    )

    final = CampaignState.from_dict(
        workspace.load_latest_campaign_state(manifest["campaign_id"])
    )
    assert final.phase_id == "FINITE_CONFIRMED"
    assert final.observation_map["X1B_K3_FINITE_CONFIRMED"] == "YES"
    assert final.authority_ceiling == "FINITE_CONFIRMATORY_RECONSTRUCTION_ONLY"
