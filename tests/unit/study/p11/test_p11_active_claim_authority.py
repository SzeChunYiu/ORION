"""P11 has one positive, width-conditioned active claim authority."""

from __future__ import annotations

import json
from pathlib import Path

from orion.study.p11.active_claim_authority import (
    ACTIVE_TERMINAL,
    P11H_TERMINAL,
    P11I_TERMINAL,
    build_active_claim_authority,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/paper-11-state-as-computation"
AUTHORITY = PAPER / "P11_ACTIVE_CLAIM_AUTHORITY_V1.json"


def test_committed_authority_is_rebuilt_from_bound_evidence() -> None:
    assert json.loads(AUTHORITY.read_text(encoding="utf-8")) == build_active_claim_authority()


def test_active_leaf_is_positive_and_width_conditioned() -> None:
    authority = build_active_claim_authority()
    active = authority["active_claim_leaf"]
    historical = authority["historical_boundary_leaf"]
    assert authority["active_terminal"] == ACTIVE_TERMINAL
    assert active["terminal"] == P11I_TERMINAL
    assert active["status"] == "SUPPORTED_REPLICATED"
    assert active["scope"]["compiled_state_width"] == 7
    assert historical["terminal"] == P11H_TERMINAL
    assert historical["claim_id"] != active["claim_id"]


def test_replication_count_is_not_inflated_by_fixed_strata() -> None:
    scope = build_active_claim_authority()["active_claim_leaf"]["scope"]
    assert scope["execution_seeds"] == scope["independent_random_replicates"] == 3
    assert scope["fixed_geometry_strata"] == 3
    assert scope["prespecified_seed_x_geometry_cells"] == 9
    assert "NINE_INDEPENDENT_RANDOM_REPLICATES" in build_active_claim_authority()["forbidden_promotions"]


def test_frozen_protocol_and_results_are_content_bound() -> None:
    authority = build_active_claim_authority()
    assert set(authority["evidence_bindings"]) == {
        "p11h_result",
        "p11i_preflight",
        "p11i_protocol",
        "p11i_receipt",
        "p11i_result",
        "p11i_runner",
    }
    assert all(len(item["sha256"]) == 64 for item in authority["evidence_bindings"].values())


def test_current_surfaces_use_the_correct_replication_language() -> None:
    for relative in ("README.md", "CLAIM_EVIDENCE_LEDGER.md", "MANUSCRIPT.md"):
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "P11_ACTIVE_CLAIM_AUTHORITY_V1.json" in text, relative
        assert "nine independent `r=7`" not in text, relative
        assert "nine independent high-width units" not in text, relative
