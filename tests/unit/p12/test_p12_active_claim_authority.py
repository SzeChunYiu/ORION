"""The historical P12A terminal cannot remain the active claim authority."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pytest

from orion.study.p12.active_authority import (
    AUTHORITY_TERMINAL,
    build_active_authority,
    build_comparison_adjudication,
)

ROOT = Path(__file__).resolve().parents[3]
PAPER = ROOT / "papers/orion-22-adaptive-state-reasoning"
ADJUDICATION = PAPER / "P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json"
ACTIVE = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V1.json"
SUCCESSOR_ACTIVE = PAPER / "P12_ACTIVE_CLAIM_AUTHORITY_V5.json"
SUCCESSOR_TERMINAL = "P12_SIGNAL_COMPLEMENTARITY_AUTHORITY_SUPPORTED"


@pytest.fixture(scope="module")
def adjudication():
    return build_comparison_adjudication()


def test_committed_adjudication_is_recomputed_not_transcribed(adjudication) -> None:
    assert json.loads(ADJUDICATION.read_text(encoding="utf-8")) == adjudication
    comparisons = adjudication["audit"]["comparisons"]
    assert {item["outcome"] for item in comparisons} == {"CANNOT_CHECK"}
    assert {item["reason"] for item in comparisons} == {
        "BASELINE_CEILING_BELOW_WINNER"
    }
    assert all(item["margin"]["baseline"]["ceiling"] < item["margin"]["winner"]["achieved"] for item in comparisons)


def test_capability_matching_flips_only_the_two_comparator_gates(adjudication) -> None:
    matched = adjudication["audit"]["capability_matched_reading"]
    assert matched["terminal"] == "P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET"
    assert matched["mean_gain"] == pytest.approx(0.040771484375)
    assert matched["worst_family_gain"] == pytest.approx(0.001953125)
    assert matched["failed_gates"] == [
        "mean_joint_gain_ge_0_15",
        "worst_family_joint_gain_ge_0_05",
    ]


def test_active_record_binds_the_adjudication_and_forbids_promotion() -> None:
    digest = sha256(ADJUDICATION.read_bytes()).hexdigest()
    expected = build_active_authority(digest)
    actual = json.loads(ACTIVE.read_text(encoding="utf-8"))
    assert actual == expected
    assert actual["active_terminal"] == AUTHORITY_TERMINAL
    assert actual["promotion_allowed"] is False
    assert actual["active_claim"] == "NO_ACTIVE_SUPERIORITY_LEAF"


def test_current_publication_surfaces_bind_positive_successor_and_historical_boundary() -> None:
    authority_surfaces = (
        "README.md",
        "CLAIM_EVIDENCE_LEDGER.md",
        "PEER_REVIEW_READINESS.md",
        "MANUSCRIPT.md",
    )
    for relative in authority_surfaces:
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json" in text, relative
        assert "P12_ACTIVE_CLAIM_AUTHORITY_V5.json" in text, relative
        assert SUCCESSOR_TERMINAL in text, relative

    for relative in (
        "manuscript/sections/00-abstract.md",
        "manuscript/sections/01-introduction.md",
        "manuscript/sections/05-results.md",
        "manuscript/sections/07-related-work-and-limitations.md",
        "manuscript/sections/08-discussion-and-conclusion.md",
    ):
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "equal-action" in text, relative

    for relative in (
        "manuscript/sections/00-abstract.md",
        "manuscript/sections/07-related-work-and-limitations.md",
        "manuscript/sections/08-discussion-and-conclusion.md",
    ):
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "external" in text or "real" in text, relative

    authority = json.loads(SUCCESSOR_ACTIVE.read_text(encoding="utf-8"))
    assert authority["promotion_allowed"] is True
    assert authority["top_tier_submission_allowed"] is False
    assert authority["active_terminal"] == SUCCESSOR_TERMINAL
    assert authority["historical_boundary_leaf"]["terminal"] == AUTHORITY_TERMINAL


def test_current_publication_surfaces_point_to_the_withholding_adjudication() -> None:
    surfaces = (
        "README.md",
        "CLAIM_EVIDENCE_LEDGER.md",
        "PEER_REVIEW_READINESS.md",
        "MANUSCRIPT.md",
    )
    for relative in surfaces:
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "P12A_COMPARISON_VALIDITY_ADJUDICATION_V1.json" in text, relative
        assert "SUPPORTED / PRIMARY" not in text, relative
        assert AUTHORITY_TERMINAL in text, relative


def test_current_submission_sources_do_not_retain_the_withdrawn_dominance_claim() -> None:
    surfaces = [PAPER / "MANUSCRIPT.md", *sorted((PAPER / "manuscript/_markdown_main").glob("*.md.tex"))]
    for path in surfaces:
        text = path.read_text(encoding="utf-8")
        assert "strict dominance over both corresponding one-axis" not in text, path
