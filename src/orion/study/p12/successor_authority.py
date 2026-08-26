"""Content-bound active authority for P12B after the P12A comparison failure."""

from __future__ import annotations

from hashlib import sha256
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from orion.study.p12.equal_action_successor_v1_1 import (
    LOCKED_NUMPY_VERSION,
    LOCKED_PYTHON_VERSION,
    LOCKED_UV_LOCK_SHA256,
    SUPPORTED,
    adjudicate,
    build_core,
)

SCHEMA_V3 = "ORION.P12.ActiveClaimAuthority.v3"
SCHEMA = "ORION.P12.ActiveClaimAuthority.v4"
ACTIVE_TERMINAL = "P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-22-adaptive-state-reasoning"
PATHS = {
    "historical_p12a_authority": PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V1.json",
    "previous_p12b_authority": PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V2.json",
    "historical_p12b_result_v1": PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1.json",
    "p12b_protocol": PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_PROTOCOL_V1.md",
    "p12b_protocol_amendment": PAPER / "P12B_PROTOCOL_AMENDMENT_V1_1.md",
    "p12b_preflight": PAPER / "P12B_PREFLIGHT_ATTAINABILITY_V1_1.json",
    "p12b_locked_environment_revalidation": PAPER / "P12B_LOCKED_ENVIRONMENT_REVALIDATION_V1_1.md",
    "p12b_subject_module_v1_1": REPO_ROOT / "src/orion/study/p12/equal_action_successor_v1_1.py",
    "p12b_runner_v1_1": PAPER / "run_p12b_equal_action_signal_complementarity_v1_1.py",
    "p12b_result_v1_1": PAPER / "P12B_EQUAL_ACTION_SIGNAL_COMPLEMENTARITY_RESULT_V1_1.json",
    "uv_lock": REPO_ROOT / "uv.lock",
}
V4_PATHS = {
    "transfer_result_receipt": PAPER / "top_tier/P12_TRANSFER_ALLOCATION_RESULT_RECEIPT_V1.md",
    "robustness_result_receipt": PAPER / "top_tier/P12_ROBUSTNESS_STRESS_RESULT_RECEIPT_V1.md",
    "price_aware_preregistration": PAPER / "top_tier/P12_PRICE_AWARE_SUCCESSOR_PROTOCOL_PREREG_V1.json",
    "price_aware_result": PAPER / "top_tier/P12_PRICE_AWARE_SUCCESSOR_RESULT_V1.json",
    "price_aware_result_receipt": PAPER / "top_tier/P12_PRICE_AWARE_SUCCESSOR_RESULT_RECEIPT_V1.md",
    "selection_sufficiency_receipt": PAPER / "top_tier/P12_SELECTION_SUFFICIENCY_RESULT_RECEIPT_V1.md",
    "certificate_necessity_receipt": PAPER / "top_tier/P12_CERTIFICATE_NECESSITY_RESULT_RECEIPT_V1.md",
}


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _verified_result() -> dict[str, Any]:
    result = json.loads(PATHS["p12b_result_v1_1"].read_text(encoding="utf-8"))
    rebuilt_core = build_core()
    # NumPy's runtime version is receipt metadata, not a scientific input.
    # Normalize it to the separately frozen V1.1 environment before comparing
    # the scientific core so the authority builder is portable across readers.
    rebuilt_core["environment"] = {
        "python_implementation": "CPython",
        "python_version": LOCKED_PYTHON_VERSION,
        "numpy_version": LOCKED_NUMPY_VERSION,
        "uv_lock_path": "uv.lock",
        "uv_lock_sha256": LOCKED_UV_LOCK_SHA256,
    }
    if result["core"] != rebuilt_core:
        raise ValueError("P12B committed core does not match fresh reconstruction")
    replay = result.get("replay", {})
    rebuilt = adjudicate(result["core"], byte_identical_replay=replay.get("byte_identical") is True)
    for key in ("summary", "gates", "terminal"):
        if result.get(key) != rebuilt[key]:
            raise ValueError(f"P12B committed {key} is not recomputed from the core")
    if result["terminal"] != SUPPORTED:
        raise ValueError("P12B successor did not reach its frozen positive terminal")
    return result


def build_active_claim_authority_v3() -> dict[str, Any]:
    result = _verified_result()
    summary = result["summary"]
    return {
        "schema": SCHEMA_V3,
        "paper_id": "P12",
        "active_terminal": ACTIVE_TERMINAL,
        "paper_level_outcome": "SUPPORTED_IN_REGISTERED_EQUAL_ACTION_WORLD",
        "promotion_allowed": True,
        "active_claim_leaf": {
            "claim_id": "P12B.EQUAL_ACTION.TWO_SIGNAL_COMPLEMENTARITY",
            "status": "SUPPORTED_LOCKED_ENVIRONMENT_REVALIDATED_FAMILY_PANEL",
            "terminal": result["terminal"],
            "scope": {
                "independent_family_rng_blocks": 32,
                "technical_episodes_per_family": 1024,
                "fixed_sigma_strata": [0.2, 0.4, 0.6, 0.8],
                "identical_action_count_per_arm": 4,
                "budget": 2,
                "scoring": "exact_required_allocation",
                "locked_environment": {
                    "python_version": LOCKED_PYTHON_VERSION,
                    "numpy_version": LOCKED_NUMPY_VERSION,
                    "uv_lock_sha256": LOCKED_UV_LOCK_SHA256,
                },
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


def build_active_claim_authority() -> dict[str, Any]:
    """Build V4 by retaining V3 and binding the landed transfer lifecycle."""

    authority = deepcopy(build_active_claim_authority_v3())
    authority.update(
        {
            "schema": SCHEMA,
            "paper_level_outcome": "SUPPORTED_WITH_TRANSFER_AND_CERTIFICATE_BOUNDS",
            "top_tier_submission_allowed": False,
            "external_public_benchmark_status": "CANNOT_CHECK_NO_BOUND_PUBLIC_DATA_RESULT",
            "artifact_identity_note": (
                "No P12C artifact exists. The adverse landed study is "
                "P12_ROBUSTNESS_STRESS_V1; the later successor is conditional on exact "
                "published charge certificates and is not public-data validation."
            ),
            "transfer_claim_leaf": {
                "claim_id": "P12.TRANSFER.EXACT.THREE_DOMAIN.V1",
                "status": "SUPPORTED_BOUNDED_INTERNAL_EXACT_DOMAINS",
                "terminal": "P12_TRANSFER_ALLOCATION_V1_SUPPORTED",
                "scope": {
                    "domains": ["SAT_PROPAGATION", "PATH_PLANNING", "KNAPSACK"],
                    "cases": 9,
                    "domain_specific_parameters": 0,
                    "allocator_regret_positive_cells": 0,
                    "exact_outputs_all_arms": True,
                },
            },
            "robustness_boundary_leaf": {
                "claim_id": "P12.TRANSFER.ROBUSTNESS.STRESS.V1",
                "authority": "BINDING_NEGATIVE_BOUNDARY",
                "terminal": "P12_ROBUSTNESS_STRESS_V1_EXECUTED",
                "price_axis": "BROKEN",
                "distribution_shift_axis": "BROKEN",
                "flat_replication": "SUPPORTED",
                "retuned": False,
            },
            "price_aware_successor_leaf": {
                "claim_id": "P12.PRICE_AWARE.EXACT_CERTIFICATE.SUCCESSOR.V1",
                "status": "SUPPORTED_CONDITIONAL_ON_EXACT_PUBLISHED_CERTIFICATES",
                "terminal": "P12_PRICE_AWARE_SUCCESSOR_SUPPORTED",
                "successor_positive_cells": 0,
                "battery_cells_cross_checked": 195,
                "new_free_parameters": 0,
                "forward_time_deployability": "CANNOT_CHECK",
            },
            "selection_information_boundary": {
                "sufficiency_terminal": "P12_SELECTION_SUFFICIENCY_THEOREM_FALSIFIER_GREEN",
                "necessity_terminal": "P12_CERTIFICATE_NECESSITY_THEOREM_FALSIFIER_GREEN",
                "maximum_authorized_use": (
                    "Exact additive charge certificates are sufficient for optimal selection, "
                    "and each registered coarsening admits an impossibility witness in the "
                    "registered reduced environment. Certificate availability before action "
                    "is not established."
                ),
            },
        }
    )
    authority["evidence_bindings"].update(
        {key: _binding(path) for key, path in V4_PATHS.items()}
    )
    authority["forbidden_promotions"].extend(
        [
            "PRICE_OR_SHIFT_ROBUSTNESS_OF_V1_ALLOCATOR",
            "FORWARD_TIME_DEPLOYABILITY_FROM_EXACT_CERTIFICATES",
            "SCIENCEAGENTBENCH_OR_EXTERNAL_TRANSFER",
            "P12C_ARTIFACT_IDENTITY",
        ]
    )
    return authority


__all__ = [
    "ACTIVE_TERMINAL",
    "SCHEMA",
    "SCHEMA_V3",
    "build_active_claim_authority",
    "build_active_claim_authority_v3",
]
