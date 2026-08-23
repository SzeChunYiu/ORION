"""P10's prospective manuscript cannot be mistaken for a result."""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p10.active_claim_authority import (
    ACTIVE_TERMINAL,
    build_active_claim_authority,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-10-structured-problem-solving"
AUTHORITY = PAPER / "P10_ACTIVE_CLAIM_AUTHORITY_V1.json"


def test_committed_record_is_rebuilt_from_bound_bytes() -> None:
    assert json.loads(AUTHORITY.read_text(encoding="utf-8")) == build_active_claim_authority()


def test_all_six_hypotheses_are_prospective_not_negative_or_positive() -> None:
    authority = build_active_claim_authority()
    assert authority["active_terminal"] == ACTIVE_TERMINAL
    assert authority["scientific_result_state"] == "NO_P10_PROTECTED_RESULT"
    assert set(authority["hypotheses"]) == {f"H{index}" for index in range(1, 7)}
    assert set(authority["hypotheses"].values()) == {"PROSPECTIVE_NOT_EXECUTED"}
    assert authority["active_empirical_claim"] is None
    assert authority["promotion_allowed"] is False


def test_predecessor_local_closure_cannot_discharge_p10() -> None:
    boundary = build_active_claim_authority()["predecessor_boundary"]
    assert boundary["authority"] == "LOCAL_REPRODUCIBLE_CORE_ONLY"
    assert set(boundary["does_not_discharge"]) == {f"H{index}" for index in range(1, 7)}


def test_manuscript_itself_declares_prospective_status() -> None:
    status = (PAPER / "manuscript/sections/16-claim-ladder-and-status.tex").read_text(
        encoding="utf-8"
    )
    assert "prospective maximum-claim manuscript" in status
    assert "does not assert method-space expansion" in status


def test_public_surfaces_point_to_active_record() -> None:
    for relative in ("README.md", "CLAIM_EVIDENCE_LEDGER.md"):
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "P10_ACTIVE_CLAIM_AUTHORITY_V1.json" in text
