"""Content-bound active claim authority for the P11 width-conditioned result.

P11H and P11I answer different, explicitly scoped questions.  The former is
the immutable adverse result at compiled width ``r=3``; the latter is the
prospectively frozen positive replication at ``r=7``.  This module prevents a
consumer from either flattening those regimes into an unconditional claim or
counting the three fixed geometry strata as nine independent random
replicates.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

SCHEMA = "ORION.P11.ActiveClaimAuthority.v1"
ACTIVE_TERMINAL = "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED"
P11I_TERMINAL = "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL"
P11H_TERMINAL = "P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/paper-11-state-as-computation"
P11I_PROTOCOL = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_PROTOCOL_V1.md"
P11I_PREFLIGHT = PAPER / "P11I_PREFLIGHT_ATTAINABILITY_V1.json"
P11I_RUNNER = PAPER / "run_p11i_wide_high_width_replication_v1.py"
P11I_RESULT = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json"
P11I_RECEIPT = PAPER / "P11I_EXECUTION_RECEIPT_V1.md"
P11I_UNIT_AMENDMENT = PAPER / "P11I_REPLICATION_UNIT_AMENDMENT_V1_1.md"
P11I_REVALIDATION_RUNNER = PAPER / "run_p11i_revalidation_v1_1.py"
P11I_REVALIDATION_RECEIPT = PAPER / "P11I_REVALIDATION_RECEIPT_V1_1.json"
P11H_RESULT = PAPER / "P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": file_sha256(path),
    }


def build_active_claim_authority() -> dict[str, Any]:
    """Build the sole active P11 authority from immutable evidence bytes."""

    return {
        "schema": SCHEMA,
        "paper_id": "P11",
        "active_terminal": ACTIVE_TERMINAL,
        "paper_level_outcome": "SUPPORTED_WITH_EXPLICIT_WIDTH_BOUNDARY",
        "promotion_allowed": True,
        "active_claim_leaf": {
            "claim_id": "P11.R7.POOLED_ATTACK_ADVANTAGE",
            "status": "SUPPORTED_REPLICATED",
            "scope": {
                "compiled_state_width": 7,
                "execution_seeds": 3,
                "fixed_geometry_strata": 3,
                "prespecified_seed_x_geometry_cells": 9,
                "independent_random_replicates": 3,
                "repeated_queries_per_cell": 5,
            },
            "terminal": P11I_TERMINAL,
            "maximum_authorized_wording": (
                "Across three independent RNG replicates and three fixed geometry strata, "
                "all nine prespecified r=7 seed-by-geometry cells passed the frozen "
                "non-compensatory gates while the matched r=3 controls kept the pooled "
                "attack live."
            ),
        },
        "historical_boundary_leaf": {
            "claim_id": "P11.R3.POOLED_ATTACK_ADVANTAGE",
            "authority": "HISTORICAL_BOUNDARY_NOT_ACTIVE_POSITIVE_CLAIM",
            "terminal": P11H_TERMINAL,
            "maximum_authorized_use": (
                "Report that the pooled attack prevailed in the registered narrow-width "
                "regime; never generalize the r=7 result across state width."
            ),
        },
        "evidence_bindings": {
            "p11i_protocol": _binding(P11I_PROTOCOL),
            "p11i_preflight": _binding(P11I_PREFLIGHT),
            "p11i_runner": _binding(P11I_RUNNER),
            "p11i_result": _binding(P11I_RESULT),
            "p11i_receipt": _binding(P11I_RECEIPT),
            "p11i_unit_amendment": _binding(P11I_UNIT_AMENDMENT),
            "p11i_revalidation_runner": _binding(P11I_REVALIDATION_RUNNER),
            "p11i_revalidation_receipt": _binding(P11I_REVALIDATION_RECEIPT),
            "p11h_result": _binding(P11H_RESULT),
        },
        "forbidden_promotions": [
            "UNCONDITIONAL_COMPILED_STATE_ADVANTAGE",
            "NINE_INDEPENDENT_RANDOM_REPLICATES",
            "REAL_SYSTEM_SUPERIORITY",
        ],
    }


__all__ = [
    "ACTIVE_TERMINAL",
    "P11H_TERMINAL",
    "P11I_TERMINAL",
    "SCHEMA",
    "build_active_claim_authority",
    "file_sha256",
]
