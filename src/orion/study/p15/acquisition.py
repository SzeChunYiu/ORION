"""Fail-closed preflight for the prospectively frozen P15A campaign."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMA = "ORION.P15A.AcquisitionPreflight.v1"
BLOCKED_TERMINAL = "P15A_ACQUISITION_BLOCKED_NO_SCIENTIFIC_RESULT"
INPUT_DIRECTORY = Path("papers/orion-25-orion-research-harness/p15a_protected_inputs")

REQUIRED_ARTIFACTS = (
    "programme_paper_issue.json",
    "donor_matrix.json",
    "estimand_and_comparator.json",
    "protected_fault_injection_corpus.jsonl",
    "common_receipt_schema_and_resource_envelope.json",
    "independent_evaluator_custody_attestation.json",
    "frozen_terminal_register.json",
)


def build_acquisition_preflight(repo_root: Path) -> dict[str, Any]:
    """Inventory inputs while refusing self-certified protection/independence.

    A complete-looking local directory is not a protected corpus, an external
    comparator, or an independent evaluator.  No trusted verifier is configured
    in-repository, so the scientific run remains unavailable by construction.
    """

    input_root = repo_root / INPUT_DIRECTORY
    present = [name for name in REQUIRED_ARTIFACTS if (input_root / name).is_file()]
    missing = [name for name in REQUIRED_ARTIFACTS if name not in present]
    return {
        "schema": SCHEMA,
        "paper_id": "P15",
        "campaign_id": "P15A",
        "terminal": BLOCKED_TERMINAL,
        "execution_authorized": False,
        "scientific_result_state": "NO_SCIENTIFIC_RESULT",
        "input_directory": INPUT_DIRECTORY.as_posix(),
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "present_artifacts": present,
        "missing_artifacts": missing,
        "trusted_protected_input_verifier_configured": False,
        "protected_inputs_verified": False,
        "reason": (
            "The paper issue, donor matrix, protected corpus, matched estimand, and "
            "evaluator-separation evidence are absent or not externally verifiable."
        ),
    }


__all__ = [
    "BLOCKED_TERMINAL",
    "INPUT_DIRECTORY",
    "REQUIRED_ARTIFACTS",
    "SCHEMA",
    "build_acquisition_preflight",
]
