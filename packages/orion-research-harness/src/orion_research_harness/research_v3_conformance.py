from __future__ import annotations

from orion.core.residuals import Residual, ResidualKind, Responsibility
from orion.core.solution import SolutionStatus

from . import paper_structure as _paper_structure
from . import recursive_runner as _recursive_runner
from .paper_structure import SupportedClaim
from .paper_structure_consensus import _merge_lane_claims
from .research_director import ResearchDirectiveKind, direct_research


def _claim(claim_id: str, value: str) -> SupportedClaim:
    return SupportedClaim(
        claim_id=claim_id,
        coordinate="target_role",
        value=value,
        quote="explicit source target",
        start=0,
        end=22,
        span_digest="sha256:" + "a" * 64,
    )


def research_v3_conformance() -> dict[str, object]:
    verified = direct_research(
        solution_status=SolutionStatus.SOLVED_VERIFIED,
        material_residuals=(),
    )
    method = direct_research(
        solution_status=SolutionStatus.CANNOT_CHECK,
        material_residuals=(
            Residual(
                "r:method",
                ResidualKind.METHOD_GAP,
                "method-language adequacy remains unresolved",
                candidate_responsibilities=(Responsibility.METHOD,),
            ),
        ),
    )

    shared = _claim("support:shared", "localization")
    merged, lanes, conflicts = _merge_lane_claims(
        {"lane_a": (shared,), "lane_b": (shared,)}
    )
    _, _, scalar_conflicts = _merge_lane_claims(
        {
            "lane_a": (_claim("support:a", "localization"),),
            "lane_b": (_claim("support:b", "classification"),),
        }
    )

    probes = {
        "verified_solution_requires_saturation_before_task_stop": (
            verified.kind is ResearchDirectiveKind.ASSESS_SATURATION
            and verified.grants_global_task_stop_authority is False
        ),
        "method_residual_routes_to_ocme_not_jump": (
            method.kind is ResearchDirectiveKind.ASSESS_OCME
            and method.paper_ids == ("P10",)
        ),
        "consensus_identical_claim_retains_both_lanes": (
            len(merged) == 1
            and lanes.get("support:shared") == ("lane_a", "lane_b")
            and conflicts == ()
        ),
        "consensus_scalar_disagreement_fails_closed": scalar_conflicts == ("target_role",),
        "consensus_extractor_registered": hasattr(
            _paper_structure, "run_paper_structure_consensus"
        ),
        "recursive_director_integration_installed": bool(
            getattr(_recursive_runner, "_research_director_integration_installed", False)
        ),
    }
    operational = bool(probes) and all(probes.values())
    return {
        "schema": "ORION.HarnessResearchDirectorConsensusConformance.v3",
        "terminal": (
            "ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_OPERATIONAL"
            if operational
            else "ORION_HARNESS_RESEARCH_DIRECTOR_CONSENSUS_EXTRACTION_V3_NOT_OPERATIONAL"
        ),
        "operational": operational,
        "failed_probes": [key for key, value in probes.items() if not value],
        "probes": probes,
        "grants_scientific_authority": False,
        "grants_novelty_authority": False,
        "grants_promotion_authority": False,
        "grants_global_task_stop_authority": False,
        "note": (
            "This gate checks V3 research-control semantics. Consensus extraction replay, "
            "coverage review, and source-support verification are additionally exercised by hostile package tests."
        ),
    }


__all__ = ["research_v3_conformance"]
