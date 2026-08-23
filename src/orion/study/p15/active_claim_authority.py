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

REPO_ROOT = Path(__file__).resolve().parents[4]
HARNESS_PACKAGE = REPO_ROOT / "packages/orion-research-harness/pyproject.toml"
DUAL_PROTOCOL = (
    REPO_ROOT
    / "development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md"
)


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


__all__ = ["ACTIVE_TERMINAL", "SCHEMA", "build_active_claim_authority"]
