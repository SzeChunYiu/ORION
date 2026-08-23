from __future__ import annotations

import json
from typing import Any, Mapping

from .campaign_runner import run_campaign
from .campaign_store import CampaignStore
from .donor_campaign import build_donor_campaign_manifest
from .runner import run_problem
from .workspace import ResearchWorkspace

_MAX_DONOR_CONTEXT_CHARS = 60_000
_MAX_OBSERVATION_CHARS = 4_000


def _donor_context(workspace: ResearchWorkspace, manifest: Mapping[str, Any]) -> str:
    campaign_id = str(manifest["campaign_id"])
    raw = CampaignStore(workspace).latest_state(campaign_id)
    if raw is None:
        return ""
    observations = raw.get("observations", ())
    rows: list[str] = []
    if isinstance(observations, list):
        for row in observations:
            if not isinstance(row, list) or len(row) != 2:
                continue
            key = str(row[0])
            value = str(row[1])
            if key.startswith("DONOR_STATUS:") and value == "PENDING":
                continue
            rows.append(f"{key}={value[:_MAX_OBSERVATION_CHARS]}")
    deferred = manifest.get("deferred_donor_obligation_ids", ())
    if isinstance(deferred, list) and deferred:
        rows.append("DEFERRED_DONOR_REOPEN_OBLIGATIONS=" + ",".join(map(str, deferred)))
    text = "\n".join(rows)
    return text[:_MAX_DONOR_CONTEXT_CHARS]


def run_research_lane(
    workspace: ResearchWorkspace,
    problem_data: Mapping[str, Any],
    *,
    max_iterations: int = 3,
    require_verified_answer: bool = True,
    max_campaign_cycles: int = 64,
) -> dict[str, Any]:
    """Run one donor-first paper-parity research lane.

    Stage 1 exhausts registered external strongest-incumbent donor capabilities through
    non-authorizing campaign receipts. Stage 2 runs public canonical ORION with the
    donor observations as explicitly non-authorizing context. ORION must still acquire
    and verify evidence before scientific authority can increase.
    """

    profile = str(problem_data.get("navigation_profile", "orion"))
    manifest = build_donor_campaign_manifest(
        problem_data,
        navigation_profile=profile,
    )
    campaign = run_campaign(
        workspace,
        manifest,
        max_cycles=max_campaign_cycles,
        auto_service_local=True,
    )
    if campaign["status"] != "TERMINAL":
        return {
            "schema": "ORION.ResearchLaneOutcome.v1",
            "status": "DONOR_STAGE_" + str(campaign["status"]),
            "navigation_profile": profile,
            "campaign": campaign,
            "root_orion_started": False,
            "grants_scientific_authority": False,
            "grants_novelty_authority": False,
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
        }
    donor_context = _donor_context(workspace, manifest)
    enriched = dict(problem_data)
    original_scope = str(problem_data.get("scope", ""))
    if donor_context:
        enriched["scope"] = (
            original_scope
            + "\n\nNON-AUTHORIZING STRONGEST-DONOR OBSERVATIONS (candidate context only; "
            "independently verify before scientific use):\n"
            + donor_context
        )
    root = run_problem(
        workspace,
        enriched,
        max_iterations=max_iterations,
        require_verified_answer=require_verified_answer,
    )
    return {
        "schema": "ORION.ResearchLaneOutcome.v1",
        "status": "ROOT_" + str(root["status"]),
        "navigation_profile": profile,
        "campaign_id": manifest["campaign_id"],
        "campaign_manifest_digest": __import__("hashlib").sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "donor_stage_terminal": campaign["cycles"][-1].get("terminal", "DONOR_STAGE_TERMINAL"),
        "root_orion_started": True,
        "root": root,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
    }


__all__ = ["run_research_lane"]
