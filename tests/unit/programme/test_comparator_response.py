"""A superiority margin is evidence only while its comparator answered the cases.

The fixtures below are the two states a published difference cannot tell apart:
a comparator that read every case and did worse, and a comparator that emitted
one label and scored the label prior.
"""

from __future__ import annotations

import pytest

from orion.programme.comparator_response import (
    ComparatorResponse,
    ContrastMargin,
    EarnedMargin,
    MarginReason,
    PriorValuedMargin,
    measure_composition_sensitivity,
    measure_contrast_margin,
    require_responsive_comparator,
    score_comparator,
)
from orion.programme.guard_exercise import GuardVerdictReason
from orion.programme.records import Outcome

# P9's protected D1 split, in the proportions the archive carries: 32 ALIGNED,
# 64 OBSTRUCTION, 32 UNRESOLVED.
GOLD = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 64 + ["UNRESOLVED"] * 32
PERFECT = list(GOLD)
CONSTANT_ALIGNED = ["ALIGNED"] * 128
CONSTANT_OBSTRUCTION = ["OBSTRUCTION"] * 128


def _response(arm_id: str, predicted: list[str]) -> ComparatorResponse:
    return score_comparator(
        arm_id,
        gold=GOLD,
        predicted=predicted,
        response_definition="a frozen arm scored on the frozen protected split",
    )


def test_a_constant_arms_accuracy_is_the_label_prior():
    arm = _response("TRANSCRIPT_BAG", CONSTANT_ALIGNED)

    assert arm.constant is True
    assert arm.distinct_predictions == 1
    assert arm.accuracy == 0.25
    assert arm.prior_of_emitted == 0.25
    assert arm.accuracy == arm.prior_of_emitted
    assert arm.informedness == 0.0
    assert arm.departures == 0


def test_a_responding_arm_departs_from_its_own_modal_answer():
    predicted = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 52 + ["ALIGNED"] * 12 + ["UNRESOLVED"] * 32
    arm = _response("UNTYPED_PAIR", predicted)

    assert arm.constant is False
    assert arm.accuracy == 0.90625
    assert arm.departures == 76
    assert arm.informedness is not None and arm.informedness > 0.8


def test_the_margin_against_a_constant_arm_cannot_be_checked():
    margin = measure_contrast_margin(
        "typed minus transcript",
        treated=_response("TYPED_RELATIONAL", PERFECT),
        comparator=_response("TRANSCRIPT_BAG", CONSTANT_ALIGNED),
    )

    assert margin.published_margin == 0.75
    assert margin.outcome is Outcome.CANNOT_CHECK
    assert margin.reason is MarginReason.COMPARATOR_CONSTANT
    assert margin.blocks is True
    # The guard carries the vacuity: the comparator never left its modal answer.
    assert margin.assessment.outcome is Outcome.CANNOT_CHECK
    assert margin.assessment.reason is GuardVerdictReason.NEVER_EXERCISED


def test_the_published_margin_is_one_minus_the_emitted_labels_prior():
    for predicted, prior in ((CONSTANT_ALIGNED, 0.25), (CONSTANT_OBSTRUCTION, 0.5)):
        margin = measure_contrast_margin(
            "typed minus a constant",
            treated=_response("TYPED_RELATIONAL", PERFECT),
            comparator=_response("CONSTANT", predicted),
        )
        assert margin.published_margin == 1.0 - prior


def test_a_responding_comparator_passes_and_the_margin_is_fully_earned():
    predicted = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 52 + ["ALIGNED"] * 12 + ["UNRESOLVED"] * 32
    margin = measure_contrast_margin(
        "typed minus untyped",
        treated=_response("TYPED_RELATIONAL", PERFECT),
        comparator=_response("UNTYPED_PAIR", predicted),
    )

    assert margin.outcome is Outcome.PASS
    assert margin.reason is MarginReason.COMPARATOR_RESPONDED
    assert margin.published_margin == 0.09375
    assert margin.earned_margin == 0.09375
    assert margin.prior_supplied == 0.0


def test_the_prior_supplied_part_is_the_comparators_shortfall_below_the_trivial_floor():
    margin = measure_contrast_margin(
        "typed minus transcript",
        treated=_response("TYPED_RELATIONAL", PERFECT),
        comparator=_response("TRANSCRIPT_BAG", CONSTANT_ALIGNED),
    )

    # Answering OBSTRUCTION unconditionally scores 0.5 on this split, so a quarter
    # of the published 0.75 is the transcript arm guessing worse than not guessing.
    assert margin.comparator.trivial_floor == 0.5
    assert margin.earned_margin == 0.5
    assert margin.prior_supplied == 0.25


def test_a_candidate_beaten_by_a_constant_fails_rather_than_blocks():
    weak = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 28 + ["ALIGNED"] * 36 + ["ALIGNED"] * 32
    comparator = ["ALIGNED"] * 96 + ["UNRESOLVED"] * 32
    margin = measure_contrast_margin(
        "weak minus weaker",
        treated=_response("CANDIDATE", weak),
        comparator=_response("COMPARATOR", comparator),
    )

    assert margin.treated.accuracy is not None
    assert margin.treated.accuracy <= margin.comparator.trivial_floor
    assert margin.outcome is Outcome.FAIL
    assert margin.reason is MarginReason.TREATED_BELOW_TRIVIAL_FLOOR


def test_a_constant_candidate_is_not_measured_either():
    margin = measure_contrast_margin(
        "constant minus responding",
        treated=_response("CANDIDATE", CONSTANT_OBSTRUCTION),
        comparator=_response(
            "COMPARATOR",
            ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 64 + ["ALIGNED"] * 32,
        ),
    )

    assert margin.outcome is Outcome.CANNOT_CHECK
    assert margin.reason is MarginReason.TREATED_CONSTANT


def test_informedness_is_undefined_rather_than_zero_when_gold_never_varies():
    """An absent measurement must not read as a passing one, here as a 0.0 score."""

    gold = ["ALIGNED"] * 8
    arm = score_comparator(
        "A",
        gold=gold,
        predicted=["ALIGNED"] * 4 + ["OBSTRUCTION"] * 4,
        response_definition="scored on a split with one gold label",
    )

    assert arm.informedness is None
    assert arm.accuracy == 0.5


def test_a_constant_gold_split_blocks_before_any_arm_is_blamed():
    gold = ["ALIGNED"] * 8
    margin = measure_contrast_margin(
        "nothing to separate",
        treated=score_comparator(
            "A", gold=gold, predicted=gold, response_definition="answers the only label"
        ),
        comparator=score_comparator(
            "B",
            gold=gold,
            predicted=["OBSTRUCTION"] * 4 + ["ALIGNED"] * 4,
            response_definition="answers two labels on a one-label split",
        ),
    )

    assert margin.outcome is Outcome.CANNOT_CHECK
    assert margin.reason is MarginReason.GOLD_CONSTANT_ON_EVAL


def test_a_claimed_margin_finer_than_one_case_cannot_be_checked():
    predicted = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 52 + ["ALIGNED"] * 12 + ["UNRESOLVED"] * 32
    margin = measure_contrast_margin(
        "typed minus untyped",
        treated=_response("TYPED_RELATIONAL", PERFECT),
        comparator=_response("UNTYPED_PAIR", predicted),
        claimed_margin=1.0 / 256.0,
    )

    assert margin.outcome is Outcome.CANNOT_CHECK
    assert margin.reason is MarginReason.MARGIN_FINER_THAN_RESOLUTION


def test_recomposing_the_split_moves_the_accuracy_margin_and_not_informedness():
    positions = {label: [i for i, g in enumerate(GOLD) if g == label] for label in set(GOLD)}
    compositions = [
        positions["ALIGNED"][:32] + positions["OBSTRUCTION"][:64] + positions["UNRESOLVED"][:32],
        positions["ALIGNED"][:32] + positions["OBSTRUCTION"][:1] + positions["UNRESOLVED"][:1],
        positions["ALIGNED"][:2] + positions["OBSTRUCTION"][:64] + positions["UNRESOLVED"][:2],
    ]
    sensitivity = measure_composition_sensitivity(
        "typed minus transcript",
        gold=GOLD,
        treated=PERFECT,
        comparator=CONSTANT_ALIGNED,
        compositions=compositions,
    )

    assert sensitivity.published_margin_low == pytest.approx(0.0588235, abs=1e-6)
    assert sensitivity.published_margin_high == pytest.approx(0.9705882, abs=1e-6)
    assert sensitivity.informedness_margin_low == 1.0
    assert sensitivity.informedness_margin_high == 1.0
    assert sensitivity.informedness_span == 0.0
    assert sensitivity.composition_valued is True


def test_a_real_contrast_is_not_reported_as_composition_valued():
    predicted = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 52 + ["ALIGNED"] * 12 + ["UNRESOLVED"] * 32
    positions = {label: [i for i, g in enumerate(GOLD) if g == label] for label in set(GOLD)}
    sensitivity = measure_composition_sensitivity(
        "typed minus untyped",
        gold=GOLD,
        treated=PERFECT,
        comparator=predicted,
        compositions=[
            positions["ALIGNED"] + positions["OBSTRUCTION"] + positions["UNRESOLVED"],
            positions["ALIGNED"][:8] + positions["OBSTRUCTION"] + positions["UNRESOLVED"][:8],
        ],
    )

    assert sensitivity.informedness_span > 0.0
    assert sensitivity.composition_valued is False


def test_a_margin_whose_contrast_blocks_cannot_be_held():
    margin = measure_contrast_margin(
        "typed minus transcript",
        treated=_response("TYPED_RELATIONAL", PERFECT),
        comparator=_response("TRANSCRIPT_BAG", CONSTANT_ALIGNED),
    )

    with pytest.raises(ValueError, match="COMPARATOR_CONSTANT"):
        EarnedMargin(margin_name="typed_minus_transcript", value=0.75, contrast=margin)


def test_require_responsive_comparator_names_the_arms_that_never_answered():
    responding = ["ALIGNED"] * 32 + ["OBSTRUCTION"] * 52 + ["ALIGNED"] * 12 + ["UNRESOLVED"] * 32
    contrasts = [
        measure_contrast_margin(
            "typed minus transcript",
            treated=_response("TYPED_RELATIONAL", PERFECT),
            comparator=_response("TRANSCRIPT_BAG", CONSTANT_ALIGNED),
        ),
        measure_contrast_margin(
            "typed minus untyped",
            treated=_response("TYPED_RELATIONAL", PERFECT),
            comparator=_response("UNTYPED_PAIR", responding),
        ),
    ]

    with pytest.raises(PriorValuedMargin, match="TRANSCRIPT_BAG"):
        require_responsive_comparator(contrasts, label="P9 D1")


def test_pass_cannot_be_paired_with_a_vacuity_reason():
    """The substitution the module exists to prevent, refused at construction."""

    margin = measure_contrast_margin(
        "typed minus transcript",
        treated=_response("TYPED_RELATIONAL", PERFECT),
        comparator=_response("TRANSCRIPT_BAG", CONSTANT_ALIGNED),
    )

    with pytest.raises(ValueError, match="cannot yield PASS"):
        ContrastMargin(
            label=margin.label,
            treated=margin.treated,
            comparator=margin.comparator,
            outcome=Outcome.PASS,
            reason=MarginReason.COMPARATOR_CONSTANT,
            detail="edited to pass",
            assessment=margin.assessment,
        )


def test_an_arm_without_a_stated_response_definition_is_refused():
    with pytest.raises(ValueError, match="response definition is required"):
        score_comparator("A", gold=GOLD, predicted=PERFECT, response_definition="  ")


def test_arms_scored_on_different_gold_distributions_are_not_a_margin():
    other = ["ALIGNED"] * 64 + ["OBSTRUCTION"] * 64
    with pytest.raises(ValueError, match="different gold distributions"):
        measure_contrast_margin(
            "mismatched",
            treated=_response("A", PERFECT),
            comparator=score_comparator(
                "B",
                gold=other,
                predicted=other,
                response_definition="scored on a different split",
            ),
        )
