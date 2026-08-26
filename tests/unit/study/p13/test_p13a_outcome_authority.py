"""P13A's self-scored safety zero cannot authorize empirical superiority."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from orion.study.p13.outcome_authority import (
    AUTHORITY_TERMINAL,
    build_active_authority,
    build_outcome_adjudication,
)

ROOT = Path(__file__).resolve().parents[4]
PAPER = ROOT / "papers/orion-23-responsibility-carrying-state"
ADJUDICATION = PAPER / "P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json"
ACTIVE = PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V1.json"
SUCCESSOR_ACTIVE = PAPER / "P13_ACTIVE_CLAIM_AUTHORITY_V2.json"
SUCCESSOR_TERMINAL = "P13_CONTROLLED_AUTHENTICATED_CERTIFICATE_AUTHORITY_SUPPORTED"


def test_committed_adjudication_is_recomputed() -> None:
    actual = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    assert actual == build_outcome_adjudication()
    audit = actual["audit"]
    assert audit["enumerated_points"] == 3840

    self_scored = audit["self_scored_endpoint"]
    assert self_scored["realized"] == 0
    assert self_scored["exercise"]["opportunities"] == 0
    assert self_scored["action_contingent"] == 2304
    assert self_scored["outcome_contingent"] == 0
    assert self_scored["entailed"] is True
    assert self_scored["blind"] is True
    assert self_scored["outcome"] == "CANNOT_CHECK"


def test_independent_gold_control_makes_unsafe_reuse_reachable() -> None:
    control = build_outcome_adjudication()["audit"]["independent_gold_endpoint_control"]
    assert control["realized"] == 0
    assert control["exercise"]["opportunities"] == 1536
    assert control["outcome_contingent"] == 1536
    assert control["entailed"] is False
    assert control["outcome"] == "PASS"


def test_duplicate_provenance_baseline_cannot_create_a_second_comparison() -> None:
    audit = build_outcome_adjudication()["audit"]
    assert audit["duplicate_arms"] == [["PROVENANCE_ONLY", "UNQUALIFIED"]]
    assert "correct_cannot_check_rate" in audit["instrument_only_endpoints"]


def test_active_authority_keeps_exact_core_and_withholds_superiority() -> None:
    digest = sha256(ADJUDICATION.read_bytes()).hexdigest()
    expected = build_active_authority(digest)
    actual = json.loads(ACTIVE.read_text(encoding="utf-8"))
    assert actual == expected
    assert actual["active_terminal"] == AUTHORITY_TERMINAL
    by_id = {item["claim_id"]: item for item in actual["claim_leaves"]}
    assert by_id["P13.EXACT.RESPONSIBILITY_RELATIVE_SUPPORT"]["outcome"] == "SUPPORTED_EXACT"
    assert by_id["P13A.EMPIRICAL.SAFETY_COST_SUPERIORITY"]["outcome"] == "CANNOT_CHECK"
    assert actual["superiority_promotion_allowed"] is False


def test_current_publication_surfaces_bind_successor_and_historical_adjudication() -> None:
    authority_surfaces = (
        "README.md",
        "CLAIM_EVIDENCE_LEDGER.md",
        "PEER_REVIEW_READINESS.md",
        "PR_SCOPE.md",
        "MANUSCRIPT.md",
    )
    for relative in authority_surfaces:
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json" in text, relative
        assert "P13_ACTIVE_CLAIM_AUTHORITY_V2.json" in text, relative
        assert SUCCESSOR_TERMINAL in text, relative

    for relative in (
        "manuscript/sections/00-abstract.md",
        "manuscript/sections/06-results.md",
    ):
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "controlled finite-world" in text, relative
        assert "external" in text or "outcome-entailment" in text, relative

    authority = json.loads(SUCCESSOR_ACTIVE.read_text(encoding="utf-8"))
    assert authority["promotion_allowed"] is True
    assert authority["active_terminal"] == SUCCESSOR_TERMINAL
    assert authority["historical_boundary_leaf"]["terminal"] == AUTHORITY_TERMINAL


def test_current_publication_surfaces_use_the_active_adjudication() -> None:
    surfaces = (
        "README.md",
        "CLAIM_EVIDENCE_LEDGER.md",
        "PEER_REVIEW_READINESS.md",
        "PR_SCOPE.md",
        "MANUSCRIPT.md",
    )
    for relative in surfaces:
        text = (PAPER / relative).read_text(encoding="utf-8")
        assert "P13A_OUTCOME_ENTAILMENT_ADJUDICATION_V1.json" in text, relative
        assert AUTHORITY_TERMINAL in text, relative
        assert "SUPPORTED / PRIMARY" not in text, relative


def test_current_submission_sources_do_not_retain_withdrawn_empirical_claims() -> None:
    surfaces = [
        PAPER / "MANUSCRIPT.md",
        PAPER / "manuscript/sections/02-donor-boundary-and-theory.md",
        PAPER / "manuscript/sections/08-limitations-and-conclusion.md",
        *sorted((PAPER / "manuscript/_markdown_main").glob("*.md.tex")),
    ]
    forbidden = (
        "measured interior safety",
        "occupies the desired interior",
        "can eliminate unsafe compact reuse",
        "eliminate structurally unsafe state reuse",
        "safety–cost superiority evidence",
    )
    for path in surfaces:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in text, (path, phrase)
