"""Typed authority for the pre-protocol P15 methods-paper directory.

The directory documents harness guarantees, but no P15 hypothesis, protected
protocol, or scientific result exists. This is not a failed or unchecked
hypothesis. It is a methods-only lifecycle state that cannot be promoted to an
empirical claim.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

SCHEMA = "ORION.P15.ActiveClaimAuthority.v1"
ACTIVE_TERMINAL = "P15_METHODS_SCOPE_ONLY"
SUCCESSOR_SCHEMA = "ORION.P15.ActiveClaimAuthority.v2"
SUCCESSOR_TERMINAL = "P15_PROSPECTIVE_ACQUISITION_PROTOCOL_FROZEN"

REPO_ROOT = Path(__file__).resolve().parents[4]
HARNESS_PACKAGE = REPO_ROOT / "packages/orion-research-harness/pyproject.toml"
DUAL_PROTOCOL = (
    REPO_ROOT
    / "development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md"
)
PAPER = REPO_ROOT / "papers/paper-15-orion-research-harness"
V1_AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V1.json"
ACQUISITION_PROTOCOL = PAPER / "P15A_RESEARCH_HARNESS_ACQUISITION_PROTOCOL_V1.md"
ACQUISITION_PREFLIGHT = PAPER / "P15A_ACQUISITION_PREFLIGHT_V1.json"
ACQUISITION_VALIDATOR = REPO_ROOT / "src/orion/study/p15/acquisition.py"


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def build_active_claim_authority() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "paper_id": "P15",
        "active_terminal": ACTIVE_TERMINAL,
        "lifecycle_state": "METHODS_SCOPE_ONLY",
        "scientific_result_state": "NO_SCIENTIFIC_RESULT",
        "active_hypothesis": None,
        "active_empirical_claim": None,
        "promotion_allowed": False,
        "diagnostic_inputs": {
            "research_harness_package": _binding(HARNESS_PACKAGE),
            "dual_harness_protocol": _binding(DUAL_PROTOCOL),
        },
        "authorized_claim": (
            "The repository contains two harness surfaces whose receipt and failure-"
            "separation guarantees are candidates for a future methods paper."
        ),
        "forbidden_states": [
            "CANNOT_CHECK",
            "FAIL",
            "SUPPORTED_EMPIRICAL",
            "SUPERIORITY_SUPPORTED",
        ],
        "promotion_requirements": [
            "paper_issue",
            "donor_matrix",
            "prospectively_frozen_p15_protocol",
            "protected_p15_result",
        ],
    }


def build_successor_claim_authority() -> dict[str, Any]:
    """Bind the frozen acquisition path without inventing a P15 result."""

    return {
        "schema": SUCCESSOR_SCHEMA,
        "paper_id": "P15",
        "active_terminal": SUCCESSOR_TERMINAL,
        "lifecycle_state": "PROSPECTIVE_ACQUISITION_PROTOCOL_FROZEN",
        "scientific_result_state": "NO_SCIENTIFIC_RESULT",
        "active_hypothesis": None,
        "active_empirical_claim": None,
        "promotion_allowed": False,
        "historical_authority": _binding(V1_AUTHORITY),
        "acquisition_authority": {
            "campaign_id": "P15A",
            "terminal": "P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT",
            "execution_authorized": False,
            "protocol": _binding(ACQUISITION_PROTOCOL),
            "preflight": _binding(ACQUISITION_PREFLIGHT),
            "validator": _binding(ACQUISITION_VALIDATOR),
            "protected_inputs_verified": False,
        },
        "authorized_claim": (
            "P15 has a prospectively frozen, fail-closed acquisition contract for a "
            "future protected harness evaluation; no scientific execution or result exists."
        ),
        "forbidden_states": [
            "SUPPORTED_EMPIRICAL",
            "SUPERIORITY_SUPPORTED",
            "EXTERNAL_VALIDATION_COMPLETE",
        ],
        "remaining_external_requirements": [
            "programme_paper_issue",
            "donor_matrix",
            "estimand_and_comparator",
            "protected_fault_injection_corpus",
            "independent_evaluator_custody",
        ],
    }


__all__ = [
    "ACTIVE_TERMINAL",
    "SCHEMA",
    "SUCCESSOR_SCHEMA",
    "SUCCESSOR_TERMINAL",
    "build_active_claim_authority",
    "build_successor_claim_authority",
]
