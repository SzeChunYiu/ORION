"""P15 lifecycle authority must preserve history and bind bounded current science."""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p15.active_claim_authority import (
    ACTIVE_TERMINAL,
    CURRENT_TERMINAL,
    SUCCESSOR_TERMINAL,
    build_active_claim_authority,
    build_current_claim_authority,
    build_successor_claim_authority,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-15-orion-research-harness"
V1_AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V1.json"
V2_AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V2.json"
V3_AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V3.json"


def test_historical_methods_authority_still_rebuilds() -> None:
    committed = json.loads(V1_AUTHORITY.read_text(encoding="utf-8"))
    assert committed == build_active_claim_authority()
    assert committed["active_terminal"] == ACTIVE_TERMINAL
    assert committed["scientific_result_state"] == "NO_SCIENTIFIC_RESULT"


def test_historical_acquisition_authority_still_rebuilds() -> None:
    committed = json.loads(V2_AUTHORITY.read_text(encoding="utf-8"))
    assert committed == build_successor_claim_authority()
    assert committed["active_terminal"] == SUCCESSOR_TERMINAL
    assert committed["promotion_allowed"] is False
    assert committed["acquisition_authority"]["execution_authorized"] is False


def test_current_authority_is_bounded_empirical_not_self_promoted() -> None:
    committed = json.loads(V3_AUTHORITY.read_text(encoding="utf-8"))
    assert committed == build_current_claim_authority()
    assert committed["active_terminal"] == CURRENT_TERMINAL
    assert committed["scientific_result_state"] == "BOUNDED_EMPIRICAL_SUPPORTED"
    assert committed["promotion_allowed"] is False
    assert "TOP_TIER_SUBMISSION_READY" in committed["forbidden_states"]
    assert "EXTERNAL_VALIDATION_COMPLETE" in committed["forbidden_states"]


def test_current_authority_binds_all_three_result_layers() -> None:
    authority = build_current_claim_authority()
    results = authority["result_authority"]
    assert set(results) == {
        "sei_fault_v1",
        "provenance_interop_v1",
        "attestation_composition_v2",
    }
    for record in results.values():
        path = ROOT / record["artifact"]
        assert path.is_file()
        assert len(record["git_blob_sha"]) == 40


def test_attestation_boundary_cannot_be_promoted_to_truth_or_key_custody() -> None:
    authority = build_current_claim_authority()
    findings = authority["bounded_findings"]
    assert findings["attestation_non_compromise_attack_detection_complete"] is True
    assert findings["attestation_valid_workload_false_rejections"] == 0
    assert findings["full_key_compromise_signature_detections"] == 0
    assert findings["full_key_compromise_false_promotions"] == 6
    assert "SIGNATURE_PROVES_SCIENTIFIC_TRUTH" in authority["forbidden_states"]
    assert "KEY_CUSTODY_VERIFIED" in authority["forbidden_states"]
    assert "unregistered premise" in authority["full_key_compromise_boundary"]


def test_public_surface_points_to_current_authority_and_ledger() -> None:
    text = (PAPER / "README.md").read_text(encoding="utf-8")
    assert "P15_ACTIVE_CLAIM_AUTHORITY_V3.json" in text
    assert "CLAIM_EVIDENCE_LEDGER.md" in text
    assert "BOUNDED_SCIENTIFIC_RESULT_EARNED" in text
    assert "NO_SCIENTIFIC_RESULT" not in text.split("## Historical lifecycle", 1)[0]
