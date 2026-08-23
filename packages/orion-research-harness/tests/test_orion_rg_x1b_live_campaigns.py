from __future__ import annotations

from pathlib import Path

from orion_research_harness.campaign_control import validate_manifest
from orion_research_harness.campaign_protocol import CampaignState
from orion_research_harness.campaign_runner import initialize_campaign, run_campaign
from orion_research_harness.domains.orion_rg import (
    X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST,
    X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST,
)
from orion_research_harness.domains.registry import builtin_campaign_ids
from orion_research_harness.workspace import ResearchWorkspace


def _run(tmp_path, repo_root: Path, manifest):
    validate_manifest(manifest)
    workspace = ResearchWorkspace.initialize(
        tmp_path,
        project_root=repo_root,
        allow_process_tools=True,
    )
    initialize_campaign(workspace, manifest)
    outcome = run_campaign(
        workspace,
        manifest,
        max_cycles=2,
        auto_service_local=True,
    )
    final = CampaignState.from_dict(
        workspace.load_latest_campaign_state(manifest["campaign_id"])
    )
    return outcome, final


def test_x1b_live_campaigns_preserve_positive_and_negative_finite_evidence(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    ids = builtin_campaign_ids()
    assert X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST["campaign_id"] in ids
    assert X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST["campaign_id"] in ids
    assert "orion-rg:x1c-c45-mixed-kernel-frontier" not in ids

    k3_outcome, k3_final = _run(
        tmp_path / "k3",
        repo_root,
        X1B_K3_SCALAR_CONFIRM_CAMPAIGN_MANIFEST,
    )
    assert k3_outcome["status"] == "TERMINAL"
    assert (
        k3_outcome["terminal"]
        == "X1B_K3_FINITE_CONFIRMATORY_RECONSTRUCTION__NO_C15_THEOREM_AUTHORITY"
    )
    assert k3_final.phase_id == "FINITE_CONFIRMED"
    assert k3_final.observation_map["X1B_K3_FINITE_CONFIRMED"] == "YES"
    assert k3_final.authority_ceiling == "FINITE_CONFIRMATORY_RECONSTRUCTION_ONLY"

    k4_outcome, k4_final = _run(
        tmp_path / "k4",
        repo_root,
        X1B_K4_ANCHORED_REPLAY_CAMPAIGN_MANIFEST,
    )
    assert k4_outcome["status"] == "TERMINAL"
    assert (
        k4_outcome["terminal"]
        == "X1B_K4_ONE_FUNCTIONAL_ANCHOR_REFUTED__SIX_OBSTRUCTIONS_REPLAYED"
    )
    assert k4_final.phase_id == "NEGATIVE_REPLAYED"
    assert k4_final.observation_map["X1B_K4_ONE_FUNCTIONAL_CLOSED"] == "NO"
    assert k4_final.authority_ceiling == "NEGATIVE_FINITE_STRATEGY_EVIDENCE_ONLY"
