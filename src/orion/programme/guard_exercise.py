"""Guard verdicts that cannot report a pass the guard never earned.

A harm guard is reported as a count or a rate of violations. That number is zero
in two entirely different worlds: the guard was pressed and held, and the guard
was never pressed. A count cannot tell them apart, so a campaign in which
nothing was ever at risk reads exactly like a campaign in which everything was
at risk and nothing broke.

P2's false-closure guard is the live example, measured both ways:

- On the frozen 390-task controlled world, ``orion_full`` claims task
  completeness 260 times and is premature on 0 of those 260. The guard has a
  denominator and it holds.
- On the 24-task external Wide acquisition slice
  (``P2_V2_ACQUISITION_DEV3R_RESULT_2026-08-18.json``) both arms report
  ``tasks_closed_as_complete: 0``. Both therefore score zero false closures, and
  a non-inferiority comparison between them "passes" while comparing two empty
  sets.

The failure class is recorded under
``research/failures/2026-08-vacuous-guard-zero-denominator/``. It is the same
shape as the P1 inert ablation (``research/failures/
2026-08-unreachable-operator-inert-ablation/``): a number that reads as a
measured zero but is a structural one.

The fix is to make the denominator part of the verdict's type. An exercise
carries the number of *opportunities* the guard had to fire alongside the number
of times it did, and a guard with no opportunities returns
:data:`~orion.programme.records.Outcome.CANNOT_CHECK` --- which, by
``Outcome.blocks``, stops a promotion exactly as ``FAIL`` does.

Nothing here weakens a real result. The controlled guard gets *stronger* when
its denominator is stated: a rate over all 390 tasks hides that ORION declined
to close 130 times and was never wrong on the 260 it did close. "Never wrong in
260 closures" is a claim about a mechanism; "rate 0.0 over 390 tasks" is
compatible with never closing at all.

This module is scope-general. It knows nothing about closure, discovery or P2;
it takes counts and returns a typed verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.programme.records import Outcome


class GuardVerdictReason(str, Enum):
    """Why a guard assessment came out the way it did.

    The three ``*_NEVER_EXERCISED`` reasons are the point of the module: they are
    the states that a violation count alone renders as an indistinguishable zero.
    """

    HELD_UNDER_EXERCISE = "HELD_UNDER_EXERCISE"
    VIOLATED = "VIOLATED"
    NEVER_EXERCISED = "NEVER_EXERCISED"
    CANDIDATE_NEVER_EXERCISED = "CANDIDATE_NEVER_EXERCISED"
    COMPARATOR_NEVER_EXERCISED = "COMPARATOR_NEVER_EXERCISED"
    NEITHER_ARM_EXERCISED = "NEITHER_ARM_EXERCISED"
    CLAIM_FINER_THAN_RESOLUTION = "CLAIM_FINER_THAN_RESOLUTION"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report a missing denominator, not a result."""

        return self in {
            GuardVerdictReason.NEVER_EXERCISED,
            GuardVerdictReason.CANDIDATE_NEVER_EXERCISED,
            GuardVerdictReason.COMPARATOR_NEVER_EXERCISED,
            GuardVerdictReason.NEITHER_ARM_EXERCISED,
        }


@dataclass(frozen=True)
class GuardExercise:
    """One arm's record of how often a guard could have fired, and how often it did.

    ``opportunity_definition`` is required and must be non-empty. A denominator
    you cannot state in a sentence is a denominator you cannot defend, and the
    P2 campaign that motivated this module reported its numerator with no stated
    denominator at all.
    """

    guard_id: str
    arm_id: str
    opportunities: int
    violations: int
    opportunity_definition: str

    def __post_init__(self) -> None:
        if not self.guard_id.strip():
            raise ValueError("guard id is required")
        if not self.arm_id.strip():
            raise ValueError("arm id is required")
        if not self.opportunity_definition.strip():
            raise ValueError(
                f"{self.guard_id}/{self.arm_id}: an opportunity definition is required; "
                "a guard whose denominator cannot be stated cannot be defended"
            )
        if self.opportunities < 0:
            raise ValueError(f"{self.guard_id}/{self.arm_id}: opportunities cannot be negative")
        if self.violations < 0:
            raise ValueError(f"{self.guard_id}/{self.arm_id}: violations cannot be negative")
        if self.violations > self.opportunities:
            raise ValueError(
                f"{self.guard_id}/{self.arm_id}: {self.violations} violations exceeds "
                f"{self.opportunities} opportunities; a guard cannot fail more often than it ran"
            )

    @property
    def exercised(self) -> bool:
        return self.opportunities > 0

    @property
    def violation_rate(self) -> float | None:
        """The violation rate, or ``None`` when the guard was never exercised.

        ``None`` rather than ``0.0`` on purpose: the whole failure this module
        prevents is a zero standing in for an absent measurement.
        """

        if not self.exercised:
            return None
        return self.violations / self.opportunities

    @property
    def resolution(self) -> float | None:
        """Finest non-zero violation rate this many opportunities can express.

        With ``n`` opportunities the observable rates are ``0, 1/n, 2/n, ...``.
        A ceiling strictly between 0 and ``1/n`` is finer than the instrument.
        """

        if not self.exercised:
            return None
        return 1.0 / self.opportunities

    def as_json(self) -> dict[str, object]:
        return {
            "guard_id": self.guard_id,
            "arm_id": self.arm_id,
            "opportunities": self.opportunities,
            "violations": self.violations,
            "opportunity_definition": self.opportunity_definition,
            "exercised": self.exercised,
            "violation_rate": self.violation_rate,
            "resolution": self.resolution,
        }


@dataclass(frozen=True)
class GuardAssessment:
    """A three-valued guard verdict carrying the exercises it was computed from."""

    guard_id: str
    outcome: Outcome
    reason: GuardVerdictReason
    detail: str
    exercises: tuple[GuardExercise, ...]

    def __post_init__(self) -> None:
        if not self.exercises:
            raise ValueError(f"{self.guard_id}: an assessment must carry its exercises")
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.guard_id}: {self.reason.value} cannot yield PASS; "
                "that substitution is the failure this module exists to prevent"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, object]:
        return {
            "guard_id": self.guard_id,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "exercises": [item.as_json() for item in self.exercises],
        }


def assess_guard(
    exercise: GuardExercise, *, max_violation_rate: float = 0.0
) -> GuardAssessment:
    """Assess one arm against a violation ceiling.

    ``max_violation_rate=0.0`` --- "no violations at all" --- is answerable by any
    positive number of opportunities, because a single violation would show. A
    ceiling strictly between 0 and ``1/opportunities`` is not: every observable
    outcome either satisfies it trivially or overshoots it by a whole unit, so
    passing carries no information beyond "zero observed" and the honest verdict
    is ``CANNOT_CHECK``.
    """

    if not 0.0 <= max_violation_rate <= 1.0:
        raise ValueError(f"{exercise.guard_id}: violation ceiling must lie in [0, 1]")

    if not exercise.exercised:
        return GuardAssessment(
            guard_id=exercise.guard_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=GuardVerdictReason.NEVER_EXERCISED,
            detail=(
                f"{exercise.arm_id} had 0 opportunities to violate {exercise.guard_id} "
                f"({exercise.opportunity_definition}); zero violations out of zero "
                "opportunities is an absent measurement, not a guard that held"
            ),
            exercises=(exercise,),
        )

    resolution = exercise.resolution
    assert resolution is not None  # exercised implies a resolution
    if 0.0 < max_violation_rate < resolution:
        return GuardAssessment(
            guard_id=exercise.guard_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=GuardVerdictReason.CLAIM_FINER_THAN_RESOLUTION,
            detail=(
                f"{exercise.arm_id}: a ceiling of {max_violation_rate} is finer than the "
                f"{resolution} resolution of {exercise.opportunities} opportunities; the "
                "instrument cannot distinguish satisfying it from observing zero"
            ),
            exercises=(exercise,),
        )

    rate = exercise.violation_rate
    assert rate is not None
    if rate <= max_violation_rate:
        return GuardAssessment(
            guard_id=exercise.guard_id,
            outcome=Outcome.PASS,
            reason=GuardVerdictReason.HELD_UNDER_EXERCISE,
            detail=(
                f"{exercise.arm_id}: {exercise.violations} violations in "
                f"{exercise.opportunities} opportunities ({exercise.opportunity_definition})"
            ),
            exercises=(exercise,),
        )
    return GuardAssessment(
        guard_id=exercise.guard_id,
        outcome=Outcome.FAIL,
        reason=GuardVerdictReason.VIOLATED,
        detail=(
            f"{exercise.arm_id}: {exercise.violations} violations in "
            f"{exercise.opportunities} opportunities is rate {rate}, above {max_violation_rate}"
        ),
        exercises=(exercise,),
    )


def assess_non_inferiority(
    *, candidate: GuardExercise, comparator: GuardExercise, margin: float = 0.0
) -> GuardAssessment:
    """Assess "candidate is no worse than comparator" on one guard.

    Both arms must be exercised. Non-inferiority between two unexercised guards
    is a statement about two empty sets, and it is the exact claim P2-U-T2 would
    have been able to assert from the 24-task external slice where neither arm
    ever closed a task.
    """

    if candidate.guard_id != comparator.guard_id:
        raise ValueError(
            f"cannot compare {candidate.guard_id} against {comparator.guard_id}: "
            "non-inferiority is defined within one guard"
        )
    if candidate.arm_id == comparator.arm_id:
        raise ValueError(f"{candidate.guard_id}: an arm cannot be its own comparator")
    if margin < 0.0:
        raise ValueError(f"{candidate.guard_id}: a non-inferiority margin cannot be negative")

    guard_id = candidate.guard_id
    exercises = (candidate, comparator)
    if not candidate.exercised and not comparator.exercised:
        return GuardAssessment(
            guard_id=guard_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=GuardVerdictReason.NEITHER_ARM_EXERCISED,
            detail=(
                f"neither {candidate.arm_id} nor {comparator.arm_id} had an opportunity to "
                f"violate {guard_id} ({candidate.opportunity_definition}); both score zero "
                "and the comparison is between two empty sets"
            ),
            exercises=exercises,
        )
    if not candidate.exercised:
        return GuardAssessment(
            guard_id=guard_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=GuardVerdictReason.CANDIDATE_NEVER_EXERCISED,
            detail=(
                f"{candidate.arm_id} had 0 opportunities to violate {guard_id} while "
                f"{comparator.arm_id} had {comparator.opportunities}; the candidate's zero "
                "is an absent measurement and cannot be credited as parity"
            ),
            exercises=exercises,
        )
    if not comparator.exercised:
        return GuardAssessment(
            guard_id=guard_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=GuardVerdictReason.COMPARATOR_NEVER_EXERCISED,
            detail=(
                f"{comparator.arm_id} had 0 opportunities to violate {guard_id} while "
                f"{candidate.arm_id} had {candidate.opportunities}; there is no comparator "
                "rate to be no worse than"
            ),
            exercises=exercises,
        )

    candidate_rate = candidate.violation_rate
    comparator_rate = comparator.violation_rate
    assert candidate_rate is not None and comparator_rate is not None
    if candidate_rate <= comparator_rate + margin:
        return GuardAssessment(
            guard_id=guard_id,
            outcome=Outcome.PASS,
            reason=GuardVerdictReason.HELD_UNDER_EXERCISE,
            detail=(
                f"{candidate.arm_id} {candidate.violations}/{candidate.opportunities} "
                f"vs {comparator.arm_id} {comparator.violations}/{comparator.opportunities} "
                f"within margin {margin}"
            ),
            exercises=exercises,
        )
    return GuardAssessment(
        guard_id=guard_id,
        outcome=Outcome.FAIL,
        reason=GuardVerdictReason.VIOLATED,
        detail=(
            f"{candidate.arm_id} rate {candidate_rate} exceeds {comparator.arm_id} rate "
            f"{comparator_rate} by more than margin {margin}"
        ),
        exercises=exercises,
    )


def worst_outcome(assessments: tuple[GuardAssessment, ...]) -> Outcome:
    """Non-compensatory roll-up: any FAIL dominates, any CANNOT_CHECK blocks.

    ``FAIL`` outranks ``CANNOT_CHECK`` in the report because a demonstrated
    violation is more informative than a missing measurement, but both block.
    """

    if not assessments:
        raise ValueError("an empty assessment set cannot be rolled up; it blocks by construction")
    outcomes = {item.outcome for item in assessments}
    if Outcome.FAIL in outcomes:
        return Outcome.FAIL
    if Outcome.CANNOT_CHECK in outcomes:
        return Outcome.CANNOT_CHECK
    return Outcome.PASS


__all__ = [
    "GuardAssessment",
    "GuardExercise",
    "GuardVerdictReason",
    "assess_guard",
    "assess_non_inferiority",
    "worst_outcome",
]
