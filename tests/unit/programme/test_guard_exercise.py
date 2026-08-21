"""A guard verdict must never spend a zero denominator as a pass."""

from __future__ import annotations

import pytest

from orion.programme.guard_exercise import (
    GuardAssessment,
    GuardExercise,
    GuardVerdictReason,
    assess_guard,
    assess_non_inferiority,
    worst_outcome,
)
from orion.programme.records import Outcome

DEFINITION = "one task on which the system declared completeness"


def exercise(arm: str, opportunities: int, violations: int) -> GuardExercise:
    return GuardExercise(
        guard_id="G",
        arm_id=arm,
        opportunities=opportunities,
        violations=violations,
        opportunity_definition=DEFINITION,
    )


class TestGuardExercise:
    def test_unexercised_rate_is_none_not_zero(self) -> None:
        """The whole failure class is a zero standing in for an absent measurement."""

        item = exercise("a", 0, 0)
        assert item.exercised is False
        assert item.violation_rate is None
        assert item.resolution is None

    def test_exercised_rate_and_resolution(self) -> None:
        item = exercise("a", 16, 0)
        assert item.exercised is True
        assert item.violation_rate == 0.0
        assert item.resolution == pytest.approx(1 / 16)

    def test_an_undefinable_denominator_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="opportunity definition is required"):
            GuardExercise(
                guard_id="G",
                arm_id="a",
                opportunities=3,
                violations=0,
                opportunity_definition="   ",
            )

    def test_more_violations_than_opportunities_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="cannot fail more often than it ran"):
            exercise("a", 2, 3)

    @pytest.mark.parametrize("field", ["opportunities", "violations"])
    def test_negative_counts_are_rejected(self, field: str) -> None:
        kwargs = {"opportunities": 1, "violations": 0}
        kwargs[field] = -1
        with pytest.raises(ValueError, match="cannot be negative"):
            GuardExercise(
                guard_id="G", arm_id="a", opportunity_definition=DEFINITION, **kwargs
            )


class TestAssessGuard:
    def test_zero_of_zero_is_cannot_check_not_pass(self) -> None:
        """The P2 external Wide slice, reduced to one assertion."""

        result = assess_guard(exercise("wide_diversified", 0, 0))
        assert result.outcome is Outcome.CANNOT_CHECK
        assert result.reason is GuardVerdictReason.NEVER_EXERCISED
        assert result.blocks is True

    def test_zero_of_many_is_a_pass_that_names_its_denominator(self) -> None:
        """ORION's controlled result: 0 premature closures in 260 declared closures."""

        result = assess_guard(exercise("orion_full", 260, 0))
        assert result.outcome is Outcome.PASS
        assert result.reason is GuardVerdictReason.HELD_UNDER_EXERCISE
        assert "260 opportunities" in result.detail

    def test_violations_fail(self) -> None:
        result = assess_guard(exercise("bm25_keyword", 390, 390))
        assert result.outcome is Outcome.FAIL
        assert result.reason is GuardVerdictReason.VIOLATED

    def test_rate_at_the_ceiling_passes(self) -> None:
        assert assess_guard(exercise("a", 10, 1), max_violation_rate=0.1).outcome is Outcome.PASS

    def test_ceiling_finer_than_resolution_is_cannot_check(self) -> None:
        """24 opportunities cannot distinguish "rate <= 0.001" from "zero observed"."""

        result = assess_guard(exercise("a", 24, 0), max_violation_rate=0.001)
        assert result.outcome is Outcome.CANNOT_CHECK
        assert result.reason is GuardVerdictReason.CLAIM_FINER_THAN_RESOLUTION

    def test_a_zero_ceiling_is_answerable_at_any_positive_n(self) -> None:
        """"No violations at all" is answerable by one opportunity: one would show."""

        assert assess_guard(exercise("a", 1, 0), max_violation_rate=0.0).outcome is Outcome.PASS

    @pytest.mark.parametrize("ceiling", [-0.01, 1.5])
    def test_out_of_range_ceiling_is_rejected(self, ceiling: float) -> None:
        with pytest.raises(ValueError, match=r"must lie in \[0, 1\]"):
            assess_guard(exercise("a", 4, 0), max_violation_rate=ceiling)


class TestNonInferiority:
    def test_two_unexercised_arms_are_not_parity(self) -> None:
        """Both P2 external arms closed 0 of 24 tasks; that is not a tie."""

        result = assess_non_inferiority(
            candidate=exercise("wide_diversified", 0, 0),
            comparator=exercise("wide_lexical", 0, 0),
        )
        assert result.outcome is Outcome.CANNOT_CHECK
        assert result.reason is GuardVerdictReason.NEITHER_ARM_EXERCISED

    def test_unexercised_candidate_is_named(self) -> None:
        result = assess_non_inferiority(
            candidate=exercise("cand", 0, 0), comparator=exercise("comp", 390, 390)
        )
        assert result.reason is GuardVerdictReason.CANDIDATE_NEVER_EXERCISED
        assert result.outcome is Outcome.CANNOT_CHECK

    def test_unexercised_comparator_is_named(self) -> None:
        result = assess_non_inferiority(
            candidate=exercise("cand", 260, 0), comparator=exercise("comp", 0, 0)
        )
        assert result.reason is GuardVerdictReason.COMPARATOR_NEVER_EXERCISED
        assert result.outcome is Outcome.CANNOT_CHECK

    def test_both_exercised_compares_rates(self) -> None:
        result = assess_non_inferiority(
            candidate=exercise("orion_full", 260, 0),
            comparator=exercise("bm25_keyword", 390, 390),
        )
        assert result.outcome is Outcome.PASS
        assert len(result.exercises) == 2

    def test_worse_candidate_fails(self) -> None:
        result = assess_non_inferiority(
            candidate=exercise("cand", 10, 5), comparator=exercise("comp", 10, 1)
        )
        assert result.outcome is Outcome.FAIL

    def test_margin_admits_a_bounded_regression(self) -> None:
        result = assess_non_inferiority(
            candidate=exercise("cand", 10, 2), comparator=exercise("comp", 10, 1), margin=0.1
        )
        assert result.outcome is Outcome.PASS

    def test_cross_guard_comparison_is_rejected(self) -> None:
        other = GuardExercise(
            guard_id="H", arm_id="b", opportunities=1, violations=0,
            opportunity_definition=DEFINITION,
        )
        with pytest.raises(ValueError, match="defined within one guard"):
            assess_non_inferiority(candidate=exercise("a", 1, 0), comparator=other)

    def test_an_arm_cannot_be_its_own_comparator(self) -> None:
        with pytest.raises(ValueError, match="own comparator"):
            assess_non_inferiority(candidate=exercise("a", 1, 0), comparator=exercise("a", 1, 0))

    def test_negative_margin_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="margin cannot be negative"):
            assess_non_inferiority(
                candidate=exercise("a", 1, 0), comparator=exercise("b", 1, 0), margin=-0.1
            )


class TestAssessmentInvariants:
    @pytest.mark.parametrize(
        "reason",
        [item for item in GuardVerdictReason if item.is_vacuity],
    )
    def test_no_vacuity_reason_can_be_constructed_as_a_pass(
        self, reason: GuardVerdictReason
    ) -> None:
        """The substitution this module exists to prevent is blocked at construction.

        Every future edit that tries to hand a missing denominator a PASS has to
        get past this, not merely past a reviewer.
        """

        with pytest.raises(ValueError, match="cannot yield PASS"):
            GuardAssessment(
                guard_id="G",
                outcome=Outcome.PASS,
                reason=reason,
                detail="",
                exercises=(exercise("a", 0, 0),),
            )

    def test_an_assessment_must_carry_its_exercises(self) -> None:
        with pytest.raises(ValueError, match="must carry its exercises"):
            GuardAssessment(
                guard_id="G",
                outcome=Outcome.PASS,
                reason=GuardVerdictReason.HELD_UNDER_EXERCISE,
                detail="",
                exercises=(),
            )

    def test_every_reason_is_reachable_from_a_public_entry_point(self) -> None:
        """A reason nothing can produce is dead vocabulary; keep the enum honest."""

        produced = {
            assess_guard(exercise("a", 0, 0)).reason,
            assess_guard(exercise("a", 260, 0)).reason,
            assess_guard(exercise("a", 10, 10)).reason,
            assess_guard(exercise("a", 24, 0), max_violation_rate=0.001).reason,
            assess_non_inferiority(
                candidate=exercise("a", 0, 0), comparator=exercise("b", 0, 0)
            ).reason,
            assess_non_inferiority(
                candidate=exercise("a", 0, 0), comparator=exercise("b", 1, 0)
            ).reason,
            assess_non_inferiority(
                candidate=exercise("a", 1, 0), comparator=exercise("b", 0, 0)
            ).reason,
        }
        assert produced == set(GuardVerdictReason)

    def test_json_round_trip_keeps_the_denominator(self) -> None:
        payload = assess_guard(exercise("orion_full", 260, 0)).as_json()
        assert payload["exercises"][0]["opportunities"] == 260
        assert payload["exercises"][0]["exercised"] is True
        assert payload["outcome"] == "PASS"


class TestRollup:
    def test_fail_dominates(self) -> None:
        assessments = (
            assess_guard(exercise("a", 10, 0)),
            assess_guard(exercise("b", 0, 0)),
            assess_guard(exercise("c", 10, 10)),
        )
        assert worst_outcome(assessments) is Outcome.FAIL

    def test_cannot_check_blocks_a_field_of_passes(self) -> None:
        """Non-compensatory: a win never buys off a missing measurement."""

        assessments = (
            assess_guard(exercise("a", 10, 0)),
            assess_guard(exercise("b", 0, 0)),
        )
        assert worst_outcome(assessments) is Outcome.CANNOT_CHECK

    def test_all_pass(self) -> None:
        assert worst_outcome((assess_guard(exercise("a", 10, 0)),)) is Outcome.PASS

    def test_empty_rollup_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="blocks by construction"):
            worst_outcome(())
