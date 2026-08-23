"""P15 must remain methods-only until protected P15 evidence exists."""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p15.active_claim_authority import (
    ACTIVE_TERMINAL,
    build_active_claim_authority,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-15-orion-research-harness"
AUTHORITY = PAPER / "P15_ACTIVE_CLAIM_AUTHORITY_V1.json"


def test_committed_authority_is_rebuilt_from_bound_inputs() -> None:
    assert json.loads(AUTHORITY.read_text(encoding="utf-8")) == build_active_claim_authority()


def test_pre_protocol_directory_is_not_misclassified_as_a_negative_result() -> None:
    authority = build_active_claim_authority()
    assert authority["active_terminal"] == ACTIVE_TERMINAL
    assert authority["lifecycle_state"] == "METHODS_SCOPE_ONLY"
    assert authority["scientific_result_state"] == "NO_SCIENTIFIC_RESULT"
    assert authority["active_hypothesis"] is None
    assert authority["active_empirical_claim"] is None


def test_methods_state_cannot_be_promoted_to_a_positive_empirical_claim() -> None:
    authority = build_active_claim_authority()
    assert authority["promotion_allowed"] is False
    assert "SUPPORTED_EMPIRICAL" in authority["forbidden_states"]
    assert "claim_evidence_ledger" not in authority["promotion_requirements"]
    assert "prospectively_frozen_p15_protocol" in authority["promotion_requirements"]
    assert "protected_p15_result" in authority["promotion_requirements"]


def test_public_surface_points_to_the_typed_authority_and_ledger() -> None:
    text = (PAPER / "README.md").read_text(encoding="utf-8")
    assert "P15_ACTIVE_CLAIM_AUTHORITY_V1.json" in text
    assert "CLAIM_EVIDENCE_LEDGER.md" in text
    assert "METHODS_SCOPE_ONLY / NO_SCIENTIFIC_RESULT" in text
