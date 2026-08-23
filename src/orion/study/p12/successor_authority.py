"""Content-bound active authority for P12B after the P12A comparison failure."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from orion.study.p12.equal_action_successor import SUPPORTED, adjudicate, build_core

SCHEMA = "ORION.P12.ActiveClaimAuthority.v2"
ACTIVE_TERMINAL = "P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-12-adaptive-state-reasoning"
PATHS = {
    "historical_p12a_authority": PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V1.json",
    "p12b_protocol": PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_PROTOCOL_V1.md",
    "p12b_protocol_amendment": PAPER / "P12B_PROTOCOL_AMENDMENT_V1_1.md",
    "p12b_preflight": PAPER / "P12B_PREFLIGHT_ATTAINABILITY_V1_1.json",
    "p12b_subject_module": REPO_ROOT / "src/orion/study/p12/equal_action_successor.py",
    "p12b_runner": PAPER / "run_p12b_equal_action_signal_complementarity_v1.py",
    "p12b_result": PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1.json",
}


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _verified_result() -> dict[str, Any]:
    result = json.loads(PATHS["p12b_result"].read_text(encoding="utf-8"))
    if result["core"] != build_core():
        raise ValueError("P12B committed core does not match fresh reconstruction")
    replay = result.get("replay", {})
    rebuilt = adjudicate(result["core"], byte_identical_replay=replay.get("byte_identical") is True)
    for key in ("summary", "gates", "terminal"):
        if result.get(key) != rebuilt[key]:
            raise ValueError(f"P12B committed {key} is not recomputed from the core")
    if result["terminal"] != SUPPORTED:
        raise ValueError("P12B successor did not reach its frozen positive terminal")
    return result


def build_active_claim_authority() -> dict[str, Any]:
    result = _verified_result()
    summary = result["summary"]
    return {
        "schema": SCHEMA,
        "paper_id": "P12",
        "active_terminal": ACTIVE_TERMINAL,
        "paper_level_outcome": "SUPPORTED_IN_REGISTERED_EQUAL_ACTION_WORLD",
        "promotion_allowed": True,
        "active_claim_leaf": {
            "claim_id": "P12B.EQUAL_ACTION.TWO_SIGNAL_COMPLEMENTARITY",
            "status": "SUPPORTED_REPLICATED_FAMILY_PANEL",
            "terminal": result["terminal"],
            "scope": {
                "independent_family_rng_blocks": 32,
                "technical_episodes_per_family": 1024,
                "fixed_sigma_strata": [0.2, 0.4, 0.6, 0.8],
                "identical_action_count_per_arm": 4,
                "budget": 2,
                "scoring": "exact_required_allocation",
            },
            "effect": {
                "mean_gain_vs_stronger_one_signal": summary["mean_delta_vs_stronger_one_signal"],
                "stratified_family_bootstrap_95ci": summary["stratified_family_bootstrap_95ci"],
                "minimum_family_gain": summary["minimum_family_delta"],
            },
            "maximum_authorized_wording": (
                "Across 32 independent simulated family RNG blocks in the registered "
                "equal-action four-regime world, the two-signal policy improved exact "
                "allocation accuracy over the stronger one-signal policy by 0.253906 "
                "on average (stratified family-block 95% bootstrap interval "
                "0.251221 to 0.256653)."
            ),
        },
        "historical_boundary_leaf": {
            "claim_id": "P12A.TWO_SIGNAL_SUPERIORITY_OVER_ONE_AXIS_POLICIES",
            "terminal": "P12A_SUPERIORITY_AUTHORITY_WITHHELD",
            "authority": "HISTORICAL_COMPARISON_FAILURE_NOT_ACTIVE",
            "reason": "BASELINE_CEILING_BELOW_WINNER",
        },
        "evidence_bindings": {key: _binding(path) for key, path in PATHS.items()},
        "forbidden_promotions": [
            "P12A_ACTION_SET_HANDICAP_AS_SIGNAL_EFFECT",
            "TECHNICAL_EPISODES_AS_INDEPENDENT_N",
            "NATURALISTIC_AGENT_SUPERIORITY",
            "EXTERNAL_SYSTEM_GENERALIZATION",
            "UNREGISTERED_NOISE_MIXTURE_GENERALIZATION",
        ],
    }


__all__ = ["ACTIVE_TERMINAL", "build_active_claim_authority"]
