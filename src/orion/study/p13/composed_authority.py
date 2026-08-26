"""Content-bound P13C composed active authority (V3).

V3 extends the V2 (P13B) authority with the composed safety-efficacy leaf. V2
remains the active authority for the P13B leaf and is retained unchanged; the
recursive-resolution ledger continues to pin its P13.B item to V2.
"""

from __future__ import annotations

import importlib.util
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

SCHEMA = "ORION.P13.ActiveClaimAuthority.v3"
ACTIVE_TERMINAL = "P13_CONTROLLED_COMPOSED_SAFETY_EFFICACY_AUTHORITY_SUPPORTED"
COMPOSED_TERMINAL = "P13C_COMPOSED_SAFETY_EFFICACY_SUPPORTED"
V2_SCHEMA = "ORION.P13.ActiveClaimAuthority.v2"
V2_ACTIVE_TERMINAL = "P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-23-responsibility-carrying-state"
RUNNER = PAPER / "run_p13c_composed_safety_efficacy_v1.py"
PATHS = {
    "historical_p13b_authority": PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V2.json",
    "p13c_protocol": PAPER / "P13C_COMPOSED_SAFETY_EFFICACY_PROTOCOL_V1.md",
    "p13c_gold_spec": PAPER / "P13C_COMPOSED_GOLD_SPEC_V1.json",
    "p13c_subject_module": REPO_ROOT / "src/orion/study/p13/authenticated_successor.py",
    "p13c_runner": RUNNER,
    "p13c_result": PAPER / "P13C_COMPOSED_RESULT_V1.json",
    "p13c_receipt": PAPER / "P13C_COMPOSED_RESULT_RECEIPT_V1.md",
}


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _runner_module() -> Any:
    spec = importlib.util.spec_from_file_location("p13c_composed_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise ValueError("P13C runner could not be loaded for recomputation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verified_result() -> dict[str, Any]:
    result = json.loads(PATHS["p13c_result"].read_text(encoding="utf-8"))
    core = result["core"]
    if core["protocol_sha256"] != _binding(PATHS["p13c_protocol"])["sha256"]:
        raise ValueError("P13C committed core does not bind the frozen protocol file")
    if core["gold_spec_sha256"] != _binding(PATHS["p13c_gold_spec"])["sha256"]:
        raise ValueError("P13C committed core does not bind the frozen gold-spec file")
    replay = result["replay"]
    if replay["byte_identical"] is not True:
        raise ValueError("P13C committed replay is not byte-identical")
    if replay["first_core_sha256"] != replay["second_core_sha256"]:
        raise ValueError("P13C committed replay subprocess digests diverge")
    rebuilt = _runner_module().adjudicate(core, byte_identical_replay=True)
    for key in ("summary", "gates", "terminal"):
        if result.get(key) != rebuilt[key]:
            raise ValueError(f"P13C committed {key} is not recomputed from the core")
    sub = core["parent_form_subpanel"]
    sub_ratio = sub["AUTHENTICATED_RCS"]["cost"] / sub["ALWAYS_RAW"]["cost"]
    if abs(result["subpanel_cost_ratio_vs_always_raw"] - sub_ratio) > 1e-12:
        raise ValueError("P13C committed parent-form subpanel ratio is not recomputed")
    if result["terminal"] != COMPOSED_TERMINAL:
        raise ValueError("P13C did not reach its frozen composed terminal")
    if not all(result["gates"].values()):
        raise ValueError("P13C gates are not all green")
    return result


def _verified_v2() -> dict[str, Any]:
    """Load the committed V2 authority and verify its structure and bindings.

    V2's own builder reconstructs the P13B panel core in memory, which embeds
    the interpreter version; rebuilding it here would make V3
    environment-sensitive. V2 is instead bound by content hash, and its
    self-consistency is checked structurally.
    """
    v2 = json.loads(PATHS["historical_p13b_authority"].read_text(encoding="utf-8"))
    if v2["schema"] != V2_SCHEMA:
        raise ValueError("P13 V2 authority has unexpected schema")
    if v2["active_terminal"] != V2_ACTIVE_TERMINAL:
        raise ValueError("P13 V2 authority terminal drifted")
    if v2["promotion_allowed"] is not True:
        raise ValueError("P13 V2 authority no longer allows promotion")
    leaves = {leaf["claim_id"] for leaf in v2["active_claim_leaves"]}
    if leaves != {
        "P13.EXACT.RESPONSIBILITY_RELATIVE_SUPPORT",
        "P13B.AUTHENTICATED_CERTIFICATE.CORRUPTION_SAFETY_COST",
    }:
        raise ValueError("P13 V2 authority leaves drifted")
    return v2


def build_composed_claim_authority() -> dict[str, Any]:
    result = _verified_result()
    v2 = _verified_v2()
    arms = result["summary"]["arms"]
    counts = result["core"]["counts"]
    composed_leaf = {
        "claim_id": "P13C.COMPOSED.SAFETY_EFFICACY",
        "status": "SUPPORTED_CONTROLLED_COMPOSED_FINITE_WORLD",
        "terminal": COMPOSED_TERMINAL,
        "scope": {
            "authority_boundary": "registered_composed_finite_world_randomized",
            "episodes": counts["episodes"],
            "episode_design": "24 families x 512 episodes, seed 2026082113",
            "state_forms": 6,
            "registered_corruption_worlds": 4,
            "corruption_schedule": "frozen 1-in-5",
            "scheduled_corrupted_episodes": counts["corrupted_episodes"],
            "gold": "p13a_truth_model_embedding",
            "external_validation": False,
        },
        "result": {
            "authenticated_unsafe_reuse": arms["AUTHENTICATED_RCS"]["unsafe_reuse"],
            "scheduled_corruptions_rejected": (
                f'{counts["corrupted_certificates_rejected"]}/{counts["corrupted_episodes"]}'
            ),
            "authenticated_verified_correct_rate": arms["AUTHENTICATED_RCS"]["verified_correct_rate"],
            "unverified_rcs_verified_correct_rate": arms["UNVERIFIED_RCS"]["verified_correct_rate"],
            "always_raw_verified_correct_rate": arms["ALWAYS_RAW"]["verified_correct_rate"],
            "authenticated_mean_cost": arms["AUTHENTICATED_RCS"]["mean_cost"],
            "always_raw_mean_cost": arms["ALWAYS_RAW"]["mean_cost"],
            "authenticated_cost_ratio_vs_always_raw": (
                arms["AUTHENTICATED_RCS"]["mean_cost"] / arms["ALWAYS_RAW"]["mean_cost"]
            ),
            "parent_form_subpanel_cost_ratio_vs_always_raw": result["subpanel_cost_ratio_vs_always_raw"],
            "unverified_rcs_unsafe_reuse": arms["UNVERIFIED_RCS"]["unsafe_reuse"],
            "unverified_rcs_unsafe_by_world": {
                world: record["unsafe"]
                for world, record in result["summary"]["unverified_by_world"].items()
            },
            "authenticated_cannot_check_cases": arms["AUTHENTICATED_RCS"]["cannot_check"],
            "byte_identical_replay_core_sha256": result["replay"]["first_core_sha256"],
        },
        "maximum_authorized_wording": (
            "In the registered composed finite world (12,288 episodes; 2,457 "
            "scheduled corruptions), authenticated RCS made zero unsafe reuses, "
            "rejected every scheduled corruption, was noninferior in verified "
            "correctness to both always-raw (0.95247) and unverified RCS "
            "(0.98063) at 0.97933, and cost 0.539 times always-raw overall and "
            "0.498 on the parent-form subpanel, while unverified RCS committed "
            "330 unsafe reuses (FORGED 66, OVERBROAD 87, STALE 177) and 123 "
            "adversary-induced unnecessary reopens under omitted support."
        ),
    }
    return {
        "schema": SCHEMA,
        "paper_id": "P13",
        "active_terminal": ACTIVE_TERMINAL,
        "paper_level_outcome": "SUPPORTED_CONTROLLED_COMPOSED_FINITE_WORLD_WITH_EXTERNAL_BOUNDARY",
        "promotion_allowed": True,
        "active_claim_leaves": [*v2["active_claim_leaves"], composed_leaf],
        "historical_boundary_leaf": v2["historical_boundary_leaf"],
        "historical_authority_note": (
            "P13_ACTIVE_CLAIM_AUTHORITY_V2.json remains the active authority for "
            "the P13B leaf and is retained unchanged; V3 adds the composed P13C "
            "leaf on top of the identical V2 leaves."
        ),
        "evidence_bindings": {
            **v2["evidence_bindings"],
            **{key: _binding(path) for key, path in PATHS.items()},
        },
        "forbidden_promotions": [
            *v2["forbidden_promotions"],
            "P13C_COMPOSED_RESULT_AS_EXTERNAL_VALIDATION",
            "P13C_COMPOSED_RESULT_AS_POPULATION_EVIDENCE",
        ],
    }


__all__ = ["ACTIVE_TERMINAL", "COMPOSED_TERMINAL", "build_composed_claim_authority"]
