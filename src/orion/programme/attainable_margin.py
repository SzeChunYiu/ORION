"""Superiority margins that cannot be reported over a baseline which could not compete.

A comparison arm is a control only for the variable the claim names. When the
arms differ in a *second* way that the claim does not mention, the reported
margin is a measurement of that second difference, and no amount of correct
arithmetic downstream --- paired differences, family bootstraps, worst-case
minima --- converts it back into evidence about the mechanism.

P12A is the live example, and it is measured. Its receipt reports
``mean_joint_gain_vs_best_one_axis = 0.334717`` for a frozen two-signal
allocation rule against two "one-axis adaptive" baselines, over 16 families of
512 items at an identical two-unit budget. The named variable is how many
pre-outcome signals a policy reads. The unnamed one is how many allocations it
is permitted to emit: ``JOINT_FROZEN`` chooses among ``{(0,0),(1,1),(2,0),(0,2)}``
and ``ADAPTIVE_STATE_ONLY`` among ``{(0,0),(2,0)}``, so the baseline cannot
express ``(1,1)`` or ``(0,2)`` and fails every ``BOTH`` and every ``REASON``
item whatever its signal says.

Give that baseline a perfect signal and it reaches **0.475464**, below the
winner's *achieved* 0.858154 in 16 of 16 families. So of the 0.395020 per-arm
margin, 0.382690 was unreachable before the experiment started and 0.012329 was
in play. Match the capability --- one signal, same four allocations --- and the
gain falls to 0.040771 with a worst family of 0.001953, and the shipped gate
battery returns ``P12A_JOINT_ALLOCATION_SUPERIORITY_GATE_NOT_MET``.

The failure class is recorded under
``research/failures/2026-08-handicapped-baseline-unattainable-margin/``.

The fix is to make the baseline's ceiling part of the verdict's type. An arm
carries what it *achieved* and what it *could have achieved* if the mechanism
under test were perfect and every other constraint on it stayed as shipped; the
gap between the winner's score and the loser's ceiling is the part of the margin
the mechanism was never able to buy. When that gap is positive the honest
verdict is :data:`~orion.programme.records.Outcome.CANNOT_CHECK` --- not ``FAIL``,
because a handicapped comparison does not show the mechanism to be worthless, it
shows nothing --- and ``CANNOT_CHECK`` blocks a promotion exactly as ``FAIL``
does.

This is the third member of a set. :mod:`orion.programme.guard_exercise`
establishes that the outcome *could* have varied;
:class:`orion.study.p3.treatment_contrast.TreatmentContrast` that the cause *did*
vary; this one that the cause was the *only* thing that varied enough to matter.
An ablation can pass all three of the earlier checks and still be confounded:
P12A's arms are reachable, its treatment is applied on every item, and four of
its seven gates have real refutation capacity.

Scope-general on purpose. It knows nothing about allocations, budgets or P12; it
takes two scored arms and their ceilings and returns a typed verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Any, Sequence

from orion.programme.records import Outcome


class HandicappedContrast(ValueError):
    """Raised when a margin is read over a baseline that could not have won."""


class MarginVerdictReason(str, Enum):
    """Why an attainable-margin assessment came out the way it did.

    ``BASELINE_CEILING_BELOW_WINNER`` is the point of the module: it is the state
    a reported margin renders as a decisive superiority result.
    """

    MARGIN_ATTAINABLE = "MARGIN_ATTAINABLE"
    MARGIN_BELOW_THRESHOLD = "MARGIN_BELOW_THRESHOLD"
    BASELINE_CEILING_BELOW_WINNER = "BASELINE_CEILING_BELOW_WINNER"
    NO_MARGIN_TO_ATTRIBUTE = "NO_MARGIN_TO_ATTRIBUTE"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report a missing comparison, not a result."""

        return self in {
            MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER,
            MarginVerdictReason.NO_MARGIN_TO_ATTRIBUTE,
        }


@dataclass(frozen=True)
class ArmCapability:
    """One arm's achieved score beside the best that arm could ever have scored.

    ``ceiling`` is measured, not asserted: it is what the arm scores when the
    mechanism under test is replaced by a perfect oracle and every *other*
    constraint on the arm --- its action set, its budget, its inputs --- is held
    exactly as the campaign shipped it. That is the only construction under which
    ``achieved`` and ``ceiling`` are comparable, which is why
    ``ceiling_definition`` is required for the same reason
    ``GuardExercise.opportunity_definition`` is: a ceiling nobody can state in a
    sentence is a second score, not a bound.

    ``capability_definition`` names what the arm is *permitted* to do. P12A's
    baseline is called ``ADAPTIVE_STATE_ONLY`` and its name describes the signal
    it reads while the handicap lives in the allocations it may emit; a contrast
    whose arms are identified only by name cannot be audited for a second
    difference.
    """

    arm_id: str
    achieved: float
    ceiling: float
    capability_definition: str
    ceiling_definition: str

    def __post_init__(self) -> None:
        if not self.arm_id.strip():
            raise ValueError("an arm id is required")
        for label, text in (
            ("capability", self.capability_definition),
            ("ceiling", self.ceiling_definition),
        ):
            if not text.strip():
                raise ValueError(
                    f"{self.arm_id}: a {label} definition is required; an arm whose "
                    f"{label} cannot be stated cannot be shown to be matched"
                )
        for label, value in (("achieved", self.achieved), ("ceiling", self.ceiling)):
            if not isfinite(value):
                raise ValueError(f"{self.arm_id}: {label} score must be finite")
        if self.ceiling < self.achieved:
            raise ValueError(
                f"{self.arm_id}: scored {self.achieved} above its own ceiling "
                f"{self.ceiling}; the ceiling was measured on a different arm, and a "
                "bound the arm beats bounds nothing"
            )

    @property
    def headroom(self) -> float:
        """How much the mechanism under test could still buy this arm.

        Zero means the arm already extracts everything its capability allows, so
        a better mechanism would change none of its score --- the state P12A's
        ``ADAPTIVE_STATE_ONLY`` is within 0.012329 of.
        """

        return self.ceiling - self.achieved

    def as_json(self) -> dict[str, Any]:
        return {
            "arm_id": self.arm_id,
            "achieved": self.achieved,
            "ceiling": self.ceiling,
            "headroom": self.headroom,
            "capability_definition": self.capability_definition,
            "ceiling_definition": self.ceiling_definition,
        }


@dataclass(frozen=True)
class AttainableMargin:
    """A reported margin split into the part the baseline could have closed and the rest."""

    winner: ArmCapability
    baseline: ArmCapability

    @property
    def reported_margin(self) -> float:
        return self.winner.achieved - self.baseline.achieved

    @property
    def handicap(self) -> float:
        """The part of the margin no value of the mechanism could have closed.

        Clamped at zero because a baseline whose ceiling exceeds the winner's
        score is not handicapped by any amount; it simply lost.
        """

        return max(0.0, self.winner.achieved - self.baseline.ceiling)

    @property
    def attainable_margin(self) -> float:
        """The part of the margin that is a statement about the mechanism."""

        return self.reported_margin - self.handicap

    @property
    def handicap_share(self) -> float | None:
        """Fraction of the reported margin that was unreachable, or ``None`` if there was none."""

        if self.reported_margin <= 0.0:
            return None
        return self.handicap / self.reported_margin

    def as_json(self) -> dict[str, Any]:
        return {
            "winner": self.winner.as_json(),
            "baseline": self.baseline.as_json(),
            "reported_margin": self.reported_margin,
            "handicap": self.handicap,
            "attainable_margin": self.attainable_margin,
            "handicap_share": self.handicap_share,
        }


@dataclass(frozen=True)
class MarginAssessment:
    """A three-valued verdict on "this margin is about the mechanism", with its margin."""

    contrast_id: str
    outcome: Outcome
    reason: MarginVerdictReason
    detail: str
    margin: AttainableMargin

    def __post_init__(self) -> None:
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.contrast_id}: {self.reason.value} cannot yield PASS; "
                "that substitution is the failure this module exists to prevent"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "contrast_id": self.contrast_id,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "margin": self.margin.as_json(),
        }


def capability_from_cases(
    arm_id: str,
    *,
    achieved_scores: Sequence[float],
    ceiling_scores: Sequence[float],
    capability_definition: str,
    ceiling_definition: str,
) -> ArmCapability:
    """Build a capability record from per-case scores rather than two summary numbers.

    The two sequences must be the same cases in the same order, because the
    ceiling is only a bound *per case*: an arm that beats its own ceiling on any
    single case has had the ceiling measured against something it is not, and
    averaging first would hide that behind a mean that still looks like a bound.
    """

    if not achieved_scores:
        raise ValueError(f"{arm_id}: an arm scored on zero cases has no ceiling")
    if len(achieved_scores) != len(ceiling_scores):
        raise ValueError(
            f"{arm_id}: {len(achieved_scores)} achieved scores against "
            f"{len(ceiling_scores)} ceiling scores; the ceiling covers different cases"
        )
    exceeded = [
        index
        for index, (got, best) in enumerate(zip(achieved_scores, ceiling_scores, strict=True))
        if got > best
    ]
    if exceeded:
        shown = ", ".join(str(index) for index in exceeded[:5])
        raise ValueError(
            f"{arm_id}: scored above the ceiling on {len(exceeded)} case(s) "
            f"(indices {shown}); the ceiling does not bound this arm"
        )
    count = len(achieved_scores)
    return ArmCapability(
        arm_id=arm_id,
        achieved=sum(achieved_scores) / count,
        ceiling=sum(ceiling_scores) / count,
        capability_definition=capability_definition,
        ceiling_definition=ceiling_definition,
    )


def assess_attainable_margin(
    contrast_id: str,
    *,
    winner: ArmCapability,
    baseline: ArmCapability,
    min_attainable_margin: float = 0.0,
) -> MarginAssessment:
    """Assess "the winner beat this baseline because of the mechanism" on one pair.

    Three values, because there are three worlds. The baseline could have
    reached the winner's score and did not, by a margin above the threshold
    (``PASS``). It could have and did not, by less than the threshold (``FAIL``
    --- a real negative). It could not have reached that score under any value of
    the mechanism (``CANNOT_CHECK`` --- the comparison is confounded and the
    margin measures the capability gap). P12A's receipt reports the third world
    in the words of the first.

    There is deliberately no fourth reason for "the baseline was already at its
    ceiling". A positive margin over a saturated baseline is exactly a baseline
    whose ceiling sits below the winner's score, so a separate branch for it
    would be a verdict nothing could reach --- the defect
    ``2026-08-unfalsifiable-check-zero-refutation-capacity`` names, reintroduced
    inside its own remedy.
    """

    if min_attainable_margin < 0.0:
        raise ValueError(f"{contrast_id}: an attainable-margin threshold cannot be negative")
    margin = AttainableMargin(winner=winner, baseline=baseline)

    if margin.reported_margin <= 0.0:
        return MarginAssessment(
            contrast_id=contrast_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginVerdictReason.NO_MARGIN_TO_ATTRIBUTE,
            detail=(
                f"{winner.arm_id} scored {winner.achieved} against {baseline.arm_id}'s "
                f"{baseline.achieved}; there is no margin to attribute to anything"
            ),
            margin=margin,
        )
    if margin.handicap > 0.0:
        return MarginAssessment(
            contrast_id=contrast_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginVerdictReason.BASELINE_CEILING_BELOW_WINNER,
            detail=(
                f"{baseline.arm_id} tops out at {baseline.ceiling} "
                f"({baseline.ceiling_definition}), below {winner.arm_id}'s achieved "
                f"{winner.achieved}; {margin.handicap} of the {margin.reported_margin} "
                f"margin was unreachable before the run, so the comparison measures "
                f"{baseline.arm_id}'s capability ({baseline.capability_definition}) "
                "rather than the mechanism"
            ),
            margin=margin,
        )
    if margin.attainable_margin < min_attainable_margin:
        return MarginAssessment(
            contrast_id=contrast_id,
            outcome=Outcome.FAIL,
            reason=MarginVerdictReason.MARGIN_BELOW_THRESHOLD,
            detail=(
                f"{margin.attainable_margin} of the {margin.reported_margin} margin is "
                f"attainable by {baseline.arm_id}, below the declared "
                f"{min_attainable_margin}"
            ),
            margin=margin,
        )
    return MarginAssessment(
        contrast_id=contrast_id,
        outcome=Outcome.PASS,
        reason=MarginVerdictReason.MARGIN_ATTAINABLE,
        detail=(
            f"{baseline.arm_id} could have reached {baseline.ceiling} against "
            f"{winner.arm_id}'s {winner.achieved}; the whole "
            f"{margin.reported_margin} margin was in play"
        ),
        margin=margin,
    )


def require_attainable(margins: Sequence[AttainableMargin], *, label: str) -> None:
    """Refuse to score a superiority panel before every baseline could have won.

    This is ``require_treatment_applied``'s precondition moved from the cause to
    the comparator: it raises, naming the baselines whose ceiling sits below the
    winner's score, before any mean, interval or worst-case minimum is read.
    Running it over P12A's two one-axis arms names both.
    """

    if not margins:
        raise HandicappedContrast(f"{label}: an empty superiority panel compares nothing")
    handicapped = [item for item in margins if item.handicap > 0.0]
    if handicapped:
        named = ", ".join(
            f"{item.baseline.arm_id} (ceiling {item.baseline.ceiling} < "
            f"{item.winner.arm_id}'s {item.winner.achieved})"
            for item in sorted(handicapped, key=lambda item: item.baseline.arm_id)
        )
        raise HandicappedContrast(
            f"{label}: {len(handicapped)} of {len(margins)} baselines could not have "
            f"reached the winner's score under any value of the mechanism ({named}); "
            "the margins reported over them are capability gaps"
        )


__all__ = [
    "ArmCapability",
    "AttainableMargin",
    "HandicappedContrast",
    "MarginAssessment",
    "MarginVerdictReason",
    "assess_attainable_margin",
    "capability_from_cases",
    "require_attainable",
]
