"""Content-bound active claim authority for P11's bounded results.

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

SCHEMA_V1 = "ORION.P11.ActiveClaimAuthority.v1"
SCHEMA = "ORION.P11.ActiveClaimAuthority.v2"
ACTIVE_TERMINAL = "P11_WIDTH_CONDITIONED_AUTHORITY_SUPPORTED"
P11I_TERMINAL = "P11I_HIGH_WIDTH_ADVANTAGE_REPLICATED_WIDE_PANEL"
P11H_TERMINAL = "P11H_POOLED_UNIVERSAL_ATTACK_PREVAILED"

REPO_ROOT = Path(__file__).resolve().parents[4]
PAPER = REPO_ROOT / "papers/orion-21-state-as-computation"
P11I_PROTOCOL = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_PROTOCOL_V1.md"
P11I_PREFLIGHT = PAPER / "P11I_PREFLIGHT_ATTAINABILITY_V1.json"
P11I_RUNNER = PAPER / "run_p11i_wide_high_width_replication_v1.py"
P11I_RESULT = PAPER / "P11I_WIDE_HIGH_WIDTH_REPLICATION_RESULT_V1.json"
P11I_RECEIPT = PAPER / "P11I_EXECUTION_RECEIPT_V1.md"
P11I_UNIT_AMENDMENT = PAPER / "P11I_REPLICATION_UNIT_AMENDMENT_V1_1.md"
P11I_REVALIDATION_RUNNER = PAPER / "run_p11i_revalidation_v1_1.py"
P11I_REVALIDATION_RECEIPT = PAPER / "P11I_REVALIDATION_RECEIPT_V1_1.json"
P11H_RESULT = PAPER / "P11H_POOLED_SPARSITY_LADDER_RESULT_V1.json"
QUERY_FAMILY_PRIMARY = PAPER / "top_tier/p11_query_family_phase_primary_v1.json"
QUERY_FAMILY_INDEPENDENT = PAPER / "top_tier/p11_query_family_phase_independent_v1.json"
QUERY_FAMILY_BINDING = PAPER / "top_tier/p11_query_family_phase_binding_v1.json"
QUERY_FAMILY_RECEIPT = PAPER / "top_tier/P11_QUERY_FAMILY_PHASE_RESULT_RECEIPT_V1.md"


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": file_sha256(path),
    }


def build_active_claim_authority_v1() -> dict[str, Any]:
    """Rebuild the superseded V1 authority without changing its bytes."""

    return {
        "schema": SCHEMA_V1,
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


def build_active_claim_authority() -> dict[str, Any]:
    """Build the current V2 authority from the V1 leaves and adverse evidence."""

    authority = build_active_claim_authority_v1()
    authority.update(
        {
            "schema": SCHEMA,
            # The positive terminal remains exactly V1's width-conditioned terminal.
            # The adverse study narrows use; it does not create a joint positive.
            "active_terminal": ACTIVE_TERMINAL,
            "paper_level_outcome": (
                "SUPPORTED_WITH_EXPLICIT_WIDTH_AND_RESPONSIBILITY_BOUNDARIES"
            ),
            "adverse_query_family_leaf": {
                "claim_id": "P11.QUERY_FAMILY.DIGITS.V1",
                "authority": "BINDING_NEGATIVE_BOUNDARY",
                "terminal": "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET",
                "frozen_gate": (
                    "at_least_8_of_10_responsibilities_within_0.02_quality_tolerance"
                ),
                "observed_support_counts": {
                    "KNN": 5,
                    "LINEAR": 3,
                    "RBF": 5,
                    "responsibilities": 10,
                },
                "retuned": False,
                "maximum_authorized_use": (
                    "Report that family-scale 16-of-64 learned compilation was supported "
                    "for 3/10 digit responsibilities under LINEAR access and 5/10 under "
                    "each of RBF and KNN, below the frozen 8/10 gate, while the registered "
                    "resource identities held exactly."
                ),
                "issue_1086_label_note": (
                    "No P11J artifact exists in the repository; the landed adverse study "
                    "integrated here is P11_QUERY_FAMILY_PHASE_V1."
                ),
            },
        }
    )
    authority["evidence_bindings"].update(
        {
            "query_family_binding": _binding(QUERY_FAMILY_BINDING),
            "query_family_independent": _binding(QUERY_FAMILY_INDEPENDENT),
            "query_family_primary": _binding(QUERY_FAMILY_PRIMARY),
            "query_family_receipt": _binding(QUERY_FAMILY_RECEIPT),
        }
    )
    authority["forbidden_promotions"].insert(
        1, "FAMILY_SCALE_COMPILATION_SUPPORT_ON_DIGITS"
    )
    return authority


__all__ = [
    "ACTIVE_TERMINAL",
    "P11H_TERMINAL",
    "P11I_TERMINAL",
    "SCHEMA",
    "SCHEMA_V1",
    "build_active_claim_authority",
    "build_active_claim_authority_v1",
    "file_sha256",
]
