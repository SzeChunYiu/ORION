"""Fail-closed preflight for P14D's external-validation inputs.

The repository does not contain an external-custody verifier.  Consequently a
locally authored packet can be inventoried here, but it cannot authorize an
external-validation execution merely by declaring itself independent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMA = "ORION.P14D.ExternalAcquisitionPreflight.v1"
BLOCKED_TERMINAL = "P14D_EXTERNAL_ACQUISITION_BLOCKED"
INPUT_DIRECTORY = Path("papers/paper-14-orion-rse/p14d_external_inputs")

REQUIRED_ARTIFACTS = (
    "packet_register.json",
    "common_resource_manifest.json",
    "blinded_assignment_manifest.json",
    "external_adjudicator_custody_attestation.json",
    "frozen_adjudication_rubric.json",
    "independent_adjudications.jsonl",
    "protected_output_register.json",
    "replay_receipt.json",
)


def build_external_acquisition_preflight(repo_root: Path) -> dict[str, Any]:
    """Inventory P14D inputs without converting local labels into custody.

    Actual custody verification requires an independently configured trust
    boundary that is intentionally absent from this repository.  Presence of
    every expected filename therefore remains insufficient for execution.
    """

    input_root = repo_root / INPUT_DIRECTORY
    present = [name for name in REQUIRED_ARTIFACTS if (input_root / name).is_file()]
    missing = [name for name in REQUIRED_ARTIFACTS if name not in present]
    return {
        "schema": SCHEMA,
        "paper_id": "P14",
        "campaign_id": "P14D",
        "terminal": BLOCKED_TERMINAL,
        "execution_authorized": False,
        "input_directory": INPUT_DIRECTORY.as_posix(),
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "present_artifacts": present,
        "missing_artifacts": missing,
        "trusted_external_custody_verifier_configured": False,
        "external_custody_verified": False,
        "reason": (
            "External packet custody, adjudicator independence, blinding, equal resources, "
            "and protected-output integrity cannot be established inside the evaluated lane."
        ),
        "active_authority_unchanged": (
            "P14C_SPECIFICATION_SEPARATED_GOVERNANCE_CONFORMANCE_SUPPORTED"
        ),
    }


__all__ = [
    "BLOCKED_TERMINAL",
    "INPUT_DIRECTORY",
    "REQUIRED_ARTIFACTS",
    "SCHEMA",
    "build_external_acquisition_preflight",
]
