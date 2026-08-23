"""The margin instrument must separate a lost race from an unwinnable one.

Both produce the same positive number. What distinguishes them is whether the
loser could have scored what the winner scored, and these tests pin that the
distinction survives every path through the module.
"""

from __future__ import annotations

import pytest

from orion.programme.attainable_margin import (
    ArmCapability,
    AttainableMargin,
    HandicappedContrast,
    MarginAssessment,
    MarginVerdictReason,
    assess_attainable_margin,
    capability_from_cases,
    require_attainable,
)
from orion.programme.records import Outcome


def arm(arm_id: str, achieved: float, ceiling: float) -> ArmCapability:
    return ArmCapability(
        arm_id=arm_id,
        achieved=achieved,
        ceiling=ceiling,
        capability_definition=f"{arm_id} may emit its declared decision set",
        ceiling_definition=f"{arm_id} scored under a perfect mechanism, same inputs",
    )


def test_ceiling_below_achieved_is_refused_at_construction() -> None:
    with pytest.raises(ValueError, match="above its own ceiling"):
        arm("candidate", achieved=0.9, ceiling=0.5)


def test_definitions_must_be_stated() -> None:
    with pytest.raises(ValueError, match="a capability definition is required"):
        ArmCapability(
            arm_id="candidate",
            achieved=0.5,
            ceiling=0.9,
            capability_definition="  ",
            ceiling_definition="measured under a perfect mechanism",
        )
    with pytest.raises(ValueError, match="a ceiling definition is required"):
        ArmCapability(
            arm_id="candidate",
            achieved=0.5,
            ceiling=0.9,
            capability_definition="may emit anything",
            ceiling_definition="",
        )


def test_headroom_is_what_the_mechanism_could_still_buy() -> None:
    assert arm("candidate", achieved=0.4, ceiling=0.75).headroom == pytest.approx(0.35)
    assert arm("saturated", achieved=0.75, ceiling=0.75).headroom == 0.0


def test_capability_from_cases_averages_and_bounds_per_case() -> None:
    built = capability_from_cases(
        "baseline",
        achieved_scores=[1.0, 0.0, 1.0, 0.0],
        ceiling_scores=[1.0, 1.0, 1.0, 0.0],
        capability_definition="two decisions",
        ceiling_definition="best of those two decisions per case",
    )
    assert built.achieved == pytest.approx(0.5)
    assert built.ceiling == pytest.approx(0.75)

    with pytest.raises(ValueError, match="the ceiling covers different cases"):
        capability_from_cases(
            "baseline",
            achieved_scores=[1.0, 0.0],
            ceiling_scores=[1.0],
            capability_definition="two decisions",
            ceiling_definition="best per case",
        )
    with pytest.raises(ValueError, match="does not bound this arm"):
        capability_from_cases(
            "baseline",
            achieved_scores=[1.0, 1.0],
            ceiling_scores=[1.0, 0.0],
            capability_definition="two decisions",
            ceiling_definition="best per case",
        )
    with pytest.raises(ValueError, match="zero cases"):
        capability_from_cases(
            "baseline",
            achieved_scores=[],
            ceiling_scores=[],
            capability_definition="two decisions",
            ceiling_definition="best per case",
        )


def test_margin_is_attainable_when_the_baseline_could_have_won() -> None:
    verdict = assess_attainable_margin(
        "fair",
        winner=arm("candidate", achieved=0.80, ceiling=1.0),
        baseline=arm("comparator", achieved=0.60, ceiling=0.95),
        min_attainable_margin=0.15,
    )
    assert verdict.outcome is Outcome.PASS
    assert verdict.reason is MarginVerdictReason.MARGIN_ATTAINABLE
    assert verdict.blocks is False
    assert verdict.margin.handicap == 0.0
    assert verdict.margin.attainable_margin == pytest.approx(0.20)
    assert verdict.margin.handicap_share == pytest.approx(0.0)


def test_attainable_margin_below_the_threshold_is_a_real_negative() -> None:
    verdict = assess_attainable_margin(
        "fair-but-small",
        winner=arm("candidate", achieved=0.80, ceiling=1.0),
        baseline=arm("comparator", achieved=0.76, ceiling=0.95),
        min_attainable_margin=0.15,
    )
    assert verdict.outcome is Outcome.FAIL
    assert verdict.reason is MarginVerdictReason.MARGIN_BELOW_THRESHOLD
    assert verdict.reason.is_vacuity is False


def test_baseline_that_could_not_reach_the_winner_blocks_as_cannot_check() -> None:
    """The P12A shape: a large margin over an arm whose ceiling is under the winner."""

    verdict = assess_attainable_margin(
        "handicapped",
        winner=arm("candidate", achieved=0.858, ceiling=1.0),
        baseline=arm("comparator", achieved=0.463, ceiling=0.475),
        min_attainable_margin=0.15,
    )
    assert verdict.outcome is Outcome.CANNOT_CHECK
    assert verdict.reason is MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER
    assert verdict.blocks is True
    assert verdict.margin.handicap == pytest.approx(0.383)
    assert verdict.margin.attainable_margin == pytest.approx(0.012)
    assert verdict.margin.handicap_share == pytest.approx(0.383 / 0.395)
    assert "measures" in verdict.detail


def test_an_absent_margin_is_not_a_result() -> None:
    tied = assess_attainable_margin(
        "tied",
        winner=arm("candidate", achieved=0.5, ceiling=1.0),
        baseline=arm("comparator", achieved=0.5, ceiling=1.0),
    )
    assert tied.outcome is Outcome.CANNOT_CHECK
    assert tied.reason is MarginVerdictReason.NO_MARGIN_TO_ATTRIBUTE
    assert tied.margin.handicap_share is None


def test_a_saturated_baseline_is_the_handicapped_case_not_a_fourth_one() -> None:
    """No separate reason for "already at its ceiling": that state is unreachable.

    A positive margin over an arm scoring its own ceiling is definitionally an
    arm whose ceiling is below the winner's score, so a fourth branch for it
    would be a verdict no input could produce.
    """

    saturated = assess_attainable_margin(
        "saturated",
        winner=arm("candidate", achieved=0.60, ceiling=1.0),
        baseline=arm("comparator", achieved=0.50, ceiling=0.50),
    )
    assert saturated.outcome is Outcome.CANNOT_CHECK
    assert saturated.reason is MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER
    assert saturated.margin.handicap == pytest.approx(0.10)
    assert saturated.margin.attainable_margin == pytest.approx(0.0)
    assert {reason.value for reason in MarginVerdictReason} == {
        "MARGIN_ATTAINABLE",
        "MARGIN_BELOW_THRESHOLD",
        "BASELINE_CEILING_BELOW_WINNER",
        "NO_MARGIN_TO_ATTRIBUTE",
    }


def test_a_vacuity_reason_can_never_be_paired_with_pass() -> None:
    margin = AttainableMargin(
        winner=arm("candidate", achieved=0.9, ceiling=1.0),
        baseline=arm("comparator", achieved=0.1, ceiling=0.2),
    )
    with pytest.raises(ValueError, match="cannot yield PASS"):
        MarginAssessment(
            contrast_id="forged",
            outcome=Outcome.PASS,
            reason=MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER,
            detail="asserted rather than measured",
            margin=margin,
        )


def test_negative_threshold_is_refused() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        assess_attainable_margin(
            "bad-threshold",
            winner=arm("candidate", achieved=0.9, ceiling=1.0),
            baseline=arm("comparator", achieved=0.5, ceiling=1.0),
            min_attainable_margin=-0.01,
        )


def test_require_attainable_names_the_baselines_that_could_not_win() -> None:
    winner = arm("candidate", achieved=0.858, ceiling=1.0)
    handicapped = AttainableMargin(winner=winner, baseline=arm("state_only", 0.463, 0.475))
    fair = AttainableMargin(winner=winner, baseline=arm("fair_arm", 0.700, 1.000))

    require_attainable([fair], label="clean-panel")

    with pytest.raises(HandicappedContrast) as caught:
        require_attainable([fair, handicapped], label="P12A")
    message = str(caught.value)
    assert "state_only" in message
    assert "fair_arm" not in message
    assert "1 of 2 baselines" in message

    with pytest.raises(HandicappedContrast, match="compares nothing"):
        require_attainable([], label="empty")


def test_as_json_carries_the_ceilings_the_verdict_was_computed_from() -> None:
    verdict = assess_attainable_margin(
        "handicapped",
        winner=arm("candidate", achieved=0.858, ceiling=1.0),
        baseline=arm("comparator", achieved=0.463, ceiling=0.475),
    )
    payload = verdict.as_json()
    assert payload["outcome"] == "CANNOT_CHECK"
    assert payload["margin"]["baseline"]["ceiling"] == pytest.approx(0.475)
    assert payload["margin"]["baseline"]["headroom"] == pytest.approx(0.012)
    assert payload["margin"]["winner"]["achieved"] == pytest.approx(0.858)
