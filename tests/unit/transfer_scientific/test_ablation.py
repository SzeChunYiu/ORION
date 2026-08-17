"""Ablating the transferred mechanic must remove the toy-fixture gain."""

from __future__ import annotations

from orion.transfer.scientific.selector import SelectorKind, select_transfer
from orion.transfer.scientific.toy_fixture import (
    TARGET_SIGNATURE,
    ToyIsolateWorld,
    ablated_source_object,
    nl_insight_baseline,
    positive_source_object,
    score_world,
    target_evidence,
)


def test_transferred_mechanic_beats_no_transfer_and_ablation_removes_gain() -> None:
    world = ToyIsolateWorld()
    transferred = positive_source_object()
    ablated = ablated_source_object()
    receipt = select_transfer(
        transferred,
        TARGET_SIGNATURE,
        evidence=target_evidence(),
        selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
    )
    assert receipt.admitted is True
    no_transfer = score_world(world, steps=())
    with_mechanic = score_world(world, steps=transferred.transformation_steps)
    without_mechanic = score_world(world, steps=ablated.transformation_steps)
    assert with_mechanic > no_transfer
    assert without_mechanic == no_transfer
    assert with_mechanic - without_mechanic == world.mechanic_gain()


def test_natural_language_insight_is_not_transfer_authority() -> None:
    insight = nl_insight_baseline()
    world = ToyIsolateWorld()
    insight_score = score_world(world, steps=insight.transformation_steps)
    mechanic_score = score_world(world, steps=positive_source_object().transformation_steps)
    assert insight_score < mechanic_score
    receipt = select_transfer(
        insight,
        TARGET_SIGNATURE,
        evidence=target_evidence(),
        selector=SelectorKind.EVIDENCE_BOUND_CONTRACT,
    )
    assert receipt.admitted is False
    assert receipt.status.value.startswith("REFUSED")
    assert any("EXECUTABLE" in code or "INSIGHT" in code for code in receipt.reason_codes)
