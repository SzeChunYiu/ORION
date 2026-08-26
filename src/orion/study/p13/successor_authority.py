"""Content-bound P13B controlled finite-world active authority."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from orion.study.p13.authenticated_successor import SUPPORTED, adjudicate, build_core

SCHEMA = "ORION.P13.ActiveClaimAuthority.v2"
ACTIVE_TERMINAL = "P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-23-responsibility-carrying-state"
PATHS = {
    "historical_p13a_authority": PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V1.json",
    "p13b_protocol": PAPER / "P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_PROTOCOL_V1.md",
    "p13b_gold_spec": PAPER / "P13B_GOLD_SUPPORT_SPEC_V1.json",
    "p13b_subject_module": REPO_ROOT / "src/orion/study/p13/authenticated_successor.py",
    "p13b_runner": PAPER / "run_p13b_authenticated_certificate_corruption_v1.py",
    "p13b_result": PAPER / "P13B_AUTHENTICATED_CERTIFICATE_CORRUPTION_RESULT_V1.json",
}


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _verified_result() -> dict[str, Any]:
    result = json.loads(PATHS["p13b_result"].read_text(encoding="utf-8"))
    if result["core"] != build_core():
        raise ValueError("P13B committed core does not match fresh finite-panel reconstruction")
    replay = result.get("replay", {})
    rebuilt = adjudicate(result["core"], byte_identical_replay=replay.get("byte_identical") is True)
    for key in ("summary", "gates", "terminal"):
        if result.get(key) != rebuilt[key]:
            raise ValueError(f"P13B committed {key} is not recomputed from the core")
    if result["terminal"] != SUPPORTED:
        raise ValueError("P13B did not reach its frozen controlled positive terminal")
    return result


def build_active_claim_authority() -> dict[str, Any]:
    result = _verified_result()
    summary = result["summary"]
    return {
        "schema": SCHEMA,
        "paper_id": "P13",
        "active_terminal": ACTIVE_TERMINAL,
        "paper_level_outcome": "SUPPORTED_CONTROLLED_FINITE_WORLD_WITH_EXTERNAL_BOUNDARY",
        "promotion_allowed": True,
        "active_claim_leaves": [
            {
                "claim_id": "P13.EXACT.RESPONSIBILITY_RELATIVE_SUPPORT",
                "status": "SUPPORTED_EXACT",
                "scope": "REGISTERED_FINITE_CONSTRUCTED_WORLD",
            },
            {
                "claim_id": "P13B.AUTHENTICATED_CERTIFICATE.CORRUPTION_SAFETY_COST",
                "status": "SUPPORTED_CONTROLLED_FINITE_WORLD",
                "terminal": result["terminal"],
                "scope": {
                    "state_forms": 6,
                    "tasks": 5,
                    "state_task_denominator": 30,
                    "registered_corruption_worlds": 4,
                    "gold": "locally_authored_certificate_independent",
                    "external_validation": False,
                },
                "result": {
                    "mutation_opportunities_per_world": summary["mutation_opportunities_by_world"],
                    "authenticated_unsafe_reuse_per_world": summary["authenticated_unsafe_reuse_by_world"],
                    "valid_panel_cost_ratio_vs_always_raw": summary["valid_panel_authenticated_cost_ratio_vs_always_raw"],
                },
                "maximum_authorized_wording": (
                    "In the registered 30-case finite state-task panel, every one of "
                    "four certificate-corruption worlds had 30 live mutation "
                    "opportunities; authenticated RCS rejected all mutated certificates, "
                    "made zero gold-scored unsafe reuses in every world, and cost 0.6111 "
                    "times always-raw on the valid-certificate panel."
                ),
            },
        ],
        "historical_boundary_leaf": {
            "claim_id": "P13A.EMPIRICAL.SAFETY_COST_SUPERIORITY",
            "terminal": "P13A_EMPIRICAL_SAFETY_COST_AUTHORITY_WITHHELD",
            "authority": "HISTORICAL_SELF_SCORED_ENDPOINT_NOT_ACTIVE",
            "reason": "SELF_SCORED_OUTCOME_NOT_CONTINGENT",
        },
        "evidence_bindings": {key: _binding(path) for key, path in PATHS.items()},
        "forbidden_promotions": [
            "EXTERNAL_VALIDATION",
            "REAL_AGENT_SAFETY",
            "POPULATION_GENERALIZATION",
            "CERTIFICATE_AUTHORITY_INDEPENDENT_OF_AUTHORS",
            "P13A_SELF_SCORED_ZERO_AS_EMPIRICAL_SAFETY",
        ],
    }


__all__ = ["ACTIVE_TERMINAL", "build_active_claim_authority"]
