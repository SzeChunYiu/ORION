from __future__ import annotations

import pytest

from orion_research_harness.frontier_benchmark import (
    DeferredAlignment,
    FrontierDecisionItem,
    FrontierInstrumentDecision,
)


def item() -> FrontierDecisionItem:
    return FrontierDecisionItem.create(
        item_id="Q3-demo",
        programme_id="P",
        question="which scientific move is licensed next?",
        evidence_digest="e" * 64,
        admissible_evidence=("receipt:a", "receipt:b"),
        diagnosis_coordinates=("D1", "D2"),
        move_coordinates=("M1", "M2"),
        deferred_scoring_rule="later exact evidence resolves the frozen coordinate",
        freeze_epoch="2026-08-22T12:00:00Z",
    )


def test_item_is_content_bound_and_non_authorizing() -> None:
    value = item()
    value.validate()
    raw = value.unsigned()
    assert raw["grants_scientific_authority"] is False
    assert raw["grants_novelty_authority"] is False


def test_decision_must_use_same_evidence_state() -> None:
    value = item()
    decision = FrontierInstrumentDecision.create(
        item=value,
        instrument_id="A",
        diagnosis=("D1",),
        move=("M1",),
        decision_epoch="2026-08-22T12:05:00Z",
    )
    decision.validate_against(value)
    assert decision.unsigned()["predicts_correctness"] is False


def test_cannot_check_cannot_select_a_move() -> None:
    value = item()
    with pytest.raises(ValueError, match="cannot-check"):
        FrontierInstrumentDecision.create(
            item=value,
            instrument_id="A",
            diagnosis=("D1",),
            move=("M1",),
            cannot_check=True,
            decision_epoch="2026-08-22T12:05:00Z",
        )


def test_resolved_alignment_vocabulary_keeps_unresolved_and_invalidated() -> None:
    assert {value.value for value in DeferredAlignment} == {
        "ALIGNED",
        "MISALIGNED",
        "UNRESOLVED",
        "INVALIDATED_ITEM",
    }
