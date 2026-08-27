"""Typed P15 claim authority across methods, acquisition, and bounded results.

V1 and V2 are retained as historical lifecycle records. V3 is the current
bounded scientific authority after the frozen SEI, provenance-interoperability,
and attestation-chain studies. None of these records can self-promote P15 to
external validation or top-tier submission readiness.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

SCHEMA = "ORION.P15.ActiveClaimAuthority.v1"
ACTIVE_TERMINAL = "P15_METHODS_SCOPE_ONLY"
SUCCESSOR_SCHEMA = "ORION.P15.ActiveClaimAuthority.v2"
SUCCESSOR_TERMINAL = "P15_PROSPECTIVE_ACQUISITION_PROTOCOL_FROZEN"
CURRENT_SCHEMA = "ORION.P15.ActiveClaimAuthority.v3"
CURRENT_TERMINAL = "P15_BOUNDED_SEI_PROVENANCE_ATTESTATION_EARNED"

REPO_ROOT = Path(__file__).resolve().parents[4]
HARNESS_PACKAGE = REPO_ROOT / "packages/orion-research-harness/pyproject.toml"
DUAL_PROTOCOL = (
    REPO_ROOT
    / "development/orion-q-max-r0/DUAL_HARNESS_AGREEMENT_BENCHMARK_V0_PROTOCOL.md"
)
PAPER = REPO_ROOT / "papers/orion-25-orion-research-harness"
V1_AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V1.json"
V2_AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V2.json"
ACQUISITION_PROTOCOL = PAPER / "P15A_RESEARCH_HARNESS_ACQUISITION_PROTOCOL_V1.md"
ACQUISITION_PREFLIGHT = PAPER / "P15A_ACQUISITION_PREFLIGHT_V1.json"
ACQUISITION_VALIDATOR = REPO_ROOT / "src/orion/study/p15/acquisition.py"
SEI_RECEIPT = PAPER / "top_tier/P15_SEI_RESULT_RECEIPT_V1.md"
PROVENANCE_RECEIPT = PAPER / "top_tier/P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md"
ATTESTATION_RECEIPT = PAPER / "top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2.md"
ATTESTATION_RUN2_RECEIPT = PAPER / "top_tier/P15_ATTESTATION_COMPOSITION_RESULT_RECEIPT_V2_RUN2.md"

# Frozen V1 diagnostic-input digests: the historical V1 authority must rebuild
# from these recorded values even though the harness package has since evolved.
HARNESS_PACKAGE_V1_SHA256 = "bfe497e0c16cde06431799a5a7f1e260757c9744402f40b16c2cff76643dcec7"
DUAL_PROTOCOL_V1_SHA256 = "af686698c0e9acca6e9a5f9c385473d14bff058cfcf4fe55c971c702ebbaec0c"

V2_AUTHORITY_BLOB_SHA = "f3aec42f1cfd3f33c2dbf63fc69921791fd29731"
SEI_RECEIPT_BLOB_SHA = "39e58c3babfa1e6dcd8c52b2b297e266f2208c07"
PROVENANCE_RECEIPT_BLOB_SHA = "0b86c992767d9da7bbdc3e5a5e175d1ab2ea1808"
ATTESTATION_RECEIPT_BLOB_SHA = "25f83c837cf480f0ca9d085184cc313fd21599cf"
ATTESTATION_RUN2_RECEIPT_BLOB_SHA = "61ca00bba4fefdc9213a7830d3eeaf16b6577f69"


def _binding(path: Path) -> dict[str, str]:
    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _frozen_binding(path: Path, sha256_hex: str) -> dict[str, str]:
    """Bind a historical record to its frozen digest.

    Historical authorities are immutable records: they must rebuild from the
    digests recorded when they were frozen, never from the current working
    tree (the harness package legitimately evolves after a V1 freeze).
    """

    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256_hex,
    }


def _git_binding(path: Path, blob_sha: str) -> dict[str, str]:
    """Bind an immutable repository object; execution SHA-256 lives in its receipt."""

    return {
        "artifact": str(path.relative_to(REPO_ROOT)),
        "git_blob_sha": blob_sha,
    }


def build_active_claim_authority() -> dict[str, Any]:
    """Rebuild historical V1 methods-only authority."""

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
            "research_harness_package": _frozen_binding(
                HARNESS_PACKAGE, HARNESS_PACKAGE_V1_SHA256
            ),
            "dual_harness_protocol": _frozen_binding(
                DUAL_PROTOCOL, DUAL_PROTOCOL_V1_SHA256
            ),
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
    """Rebuild historical V2 frozen-acquisition authority."""

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


def build_current_claim_authority() -> dict[str, Any]:
    """Bind the current bounded P15 result stack without widening authority."""

    return {
        "schema": CURRENT_SCHEMA,
        "paper_id": "P15",
        "active_terminal": CURRENT_TERMINAL,
        "lifecycle_state": "BOUNDED_SCIENTIFIC_RESULT_EARNED",
        "scientific_result_state": "BOUNDED_EMPIRICAL_SUPPORTED",
        "active_hypothesis": "SCIENTIFIC_EXECUTION_INTEGRITY_SEPARATION",
        "active_empirical_claim": (
            "Execution integrity, provenance representation, cryptographic attestation, "
            "scientific validity, and claim authority remain distinct layers on the "
            "registered bounded fault/interoperability/attestation studies."
        ),
        "promotion_allowed": False,
        "historical_authority": _git_binding(V2_AUTHORITY, V2_AUTHORITY_BLOB_SHA),
        "result_authority": {
            "sei_fault_v1": {
                **_git_binding(SEI_RECEIPT, SEI_RECEIPT_BLOB_SHA),
                "terminal": "P15_SEI_BOUNDED_FAULT_V1_GREEN",
            },
            "provenance_interop_v1": {
                **_git_binding(PROVENANCE_RECEIPT, PROVENANCE_RECEIPT_BLOB_SHA),
                "terminal": "P15_PROVENANCE_INTEROP_V1_SUPPORTED",
                "independent_terminal": "P15_PROVENANCE_INTEROP_SECOND_INDEPENDENT_CHECKER_GREEN",
            },
            "attestation_composition_v2": {
                **_git_binding(ATTESTATION_RECEIPT, ATTESTATION_RECEIPT_BLOB_SHA),
                "terminal": "P15_ATTESTATION_COMPOSITION_V2_SUPPORTED",
                "independent_terminal": "P15_ATTESTATION_COMPOSITION_V2_SECOND_CHECKER_GREEN",
                "deterministic_replay": {
                    **_git_binding(
                        ATTESTATION_RUN2_RECEIPT, ATTESTATION_RUN2_RECEIPT_BLOB_SHA
                    ),
                    "ci_run_id": 32665597624,
                    "note": (
                        "Independent second execution of the frozen protocol; "
                        "artifact-member SHA-256 digests identical to the canonical "
                        "run 32664075763."
                    ),
                },
            },
        },
        "bounded_findings": {
            "sei_false_authorized_science": 0,
            "provenance_round_trip_rate": 1.0,
            "provenance_scientific_field_leakage": 0,
            "attestation_base_chain_verification_rate": 1.0,
            "attestation_non_compromise_attack_detection_complete": True,
            "attestation_valid_workload_false_rejections": 0,
            "attestation_chain_plus_sei_gold_agreement": "22/22",
            "full_key_compromise_signature_detections": 0,
            "full_key_compromise_false_promotions": 6,
        },
        "full_key_compromise_boundary": (
            "Composed-signature validity is evidence about the key set, not about "
            "key custody or fact truth; chain-plus-SEI inherits key custody as an "
            "unregistered premise."
        ),
        "authorized_claim": (
            "At bounded scope, P15 separates execution/provenance/attestation evidence "
            "from scientific validity and claim authority: SEI blocks false scientific "
            "promotion in the frozen fault corpus, the separation survives W3C PROV and "
            "RO-Crate/Workflow-Run import, and a three-link Ed25519 chain detects the "
            "registered non-compromise tamper/replay attacks without observed false "
            "rejection while exposing full key compromise as outside signature authority."
        ),
        "forbidden_states": [
            "SIGNATURE_PROVES_SCIENTIFIC_TRUTH",
            "KEY_CUSTODY_VERIFIED",
            "UNIVERSAL_EXECUTION_CORRECTNESS",
            "PRODUCTION_SCALE_VALIDATED",
            "SUPERIORITY_SUPPORTED",
            "EXTERNAL_VALIDATION_COMPLETE",
            "TOP_TIER_SUBMISSION_READY",
        ],
        "remaining_external_requirements": [
            "production_scale_host_and_process_fault_campaign",
            "runtime_storage_and_false_rejection_overhead_characterization",
            "clean_environment_independent_replay",
            "final_current_nearest_work_refresh",
            "final_manuscript_evidence_environment_pdf_binding",
        ],
    }


__all__ = [
    "ACTIVE_TERMINAL",
    "CURRENT_SCHEMA",
    "CURRENT_TERMINAL",
    "SCHEMA",
    "SUCCESSOR_SCHEMA",
    "SUCCESSOR_TERMINAL",
    "build_active_claim_authority",
    "build_current_claim_authority",
    "build_successor_claim_authority",
]
