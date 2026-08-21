"""Superiority margins that cannot be reported against an arm that never answered.

A comparison reports a difference: the candidate's score minus the comparator's.
That difference is the same number in two entirely different worlds --- the
comparator read every case and did worse, and the comparator emitted one label
over the whole evaluation set and scored whatever the label prior happened to be.
An accuracy cannot tell them apart, because a constant predictor's accuracy *is*
the prior of the label it emits, so the published margin becomes ``1 - prior``
and carries nothing about the two systems.

P9's D1 whole-domain transfer result is the live example, measured on the shipped
archive ``research/extensions/p9-structured-neural/execution/
D1_EXECUTION_RESULT_V1_2.json`` (``result_digest sha256:34003fb8...``), whose
128-case protected split carries 32 ``ALIGNED``, 64 ``OBSTRUCTION`` and 32
``UNRESOLVED``:

===================== ======== ===================== ============== ============
arm                   accuracy distinct predictions  informedness   margin
===================== ======== ===================== ============== ============
``TYPED_RELATIONAL``  1.0      3                     1.000          ---
``UNTYPED_PAIR``      0.90625  3                     0.896          0.09375
``TYPED_SERIALIZED``  0.5      **1** (``OBSTRUCTION``) **0.000**     0.50
``TRANSCRIPT_BAG``    0.25     **1** (``ALIGNED``)    **0.000**      0.75
===================== ======== ===================== ============== ============

Both arms the paper's headline differences are taken against emit a single label
on all 128 cases. Their accuracies are therefore identities: ``0.25 = 32/128``
and ``0.5 = 64/128``. So ``typed_minus_transcript = 0.75`` is
``1 - prior(ALIGNED)`` and ``typed_minus_same_information_serialized = 0.5`` is
``1 - prior(OBSTRUCTION)``. Re-compose the protected split without touching a
representation, a feature family, a fitted model or a prediction and the first
sweeps from 0.0588 to 0.9706 while the second sweeps from 0.0294 to 0.9412.

The failure class is recorded under
``research/failures/2026-08-unresponsive-comparator-prior-valued-margin/``.

This is not the failure :mod:`orion.study.p3.treatment_contrast` catches, and
that module's instrument returns ``PASS`` here. There the *cause* did not vary:
the arm re-ran the system on an unchanged input. Here the treatment varied on
128 of 128 cases, the decision moved on 96 of them, and
``assess_coordinate_necessity`` reports ``COORDINATE_LOAD_BEARING`` --- because
what varied is real and what did not vary is the comparator's *answer*. Nor is it
:mod:`orion.study.p1.arm_validity`: that asks whether the compared systems
differed from each other, and these four differ on every vector.
:mod:`orion.programme.benchmark_identifiability` already says the decisive
sentence about probes --- "informedness is 0 for every constant predictor" ---
and this module is that sentence asked about an arm of a superiority contrast
rather than about a leak probe.

The fix is to make the comparator's response part of the margin's type. A
comparator carries how many protected cases it answered with something other
than its own most frequent answer, and an arm that departed from it zero times
returns :data:`~orion.programme.records.Outcome.CANNOT_CHECK`, which by
``Outcome.blocks`` stops a promotion exactly as ``FAIL`` does.

Two constraints carry the weight.

The verdict is built from :class:`~orion.programme.guard_exercise.GuardExercise`
rather than beside it, so "the comparator gave one answer" and "the guard was
never pressed" are one state with one answer, and ``GuardAssessment`` already
refuses to pair ``PASS`` with a vacuity reason.

Informedness is reported alongside accuracy because it is the composition-free
statistic. Across every re-composition of P9's protected split the accuracy
margin moves over almost its whole range and the informedness margin is
1.000000; a difference that survives re-composition is about the systems, and one
that does not is about the split.

Nothing here weakens a real comparison. It strengthens the one P9 actually has:
``UNTYPED_PAIR`` responded on 76 of 128 cases, and the 0.09375 margin over it is
the only one of the three that measures a representation.

Scope-general on purpose. It knows nothing about representations, transfer or P9;
it takes gold labels and two arms' predictions and returns a typed verdict.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Hashable, Sequence

from orion.programme.guard_exercise import GuardAssessment, GuardExercise, assess_guard
from orion.programme.records import Outcome


class PriorValuedMargin(ValueError):
    """Raised when a margin is quoted before its comparator was shown to answer."""


class MarginReason(str, Enum):
    """Why a contrast came out the way it did.

    The ``is_vacuity`` members are the point of the module: each is a way for a
    difference to be arithmetically correct while measuring the evaluation set
    rather than the systems.
    """

    COMPARATOR_RESPONDED = "COMPARATOR_RESPONDED"
    TREATED_BELOW_TRIVIAL_FLOOR = "TREATED_BELOW_TRIVIAL_FLOOR"
    COMPARATOR_CONSTANT = "COMPARATOR_CONSTANT"
    TREATED_CONSTANT = "TREATED_CONSTANT"
    NO_EVAL_CASES = "NO_EVAL_CASES"
    GOLD_CONSTANT_ON_EVAL = "GOLD_CONSTANT_ON_EVAL"
    MARGIN_FINER_THAN_RESOLUTION = "MARGIN_FINER_THAN_RESOLUTION"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report an unmeasured margin, not a result."""

        return self in {
            MarginReason.COMPARATOR_CONSTANT,
            MarginReason.TREATED_CONSTANT,
            MarginReason.NO_EVAL_CASES,
            MarginReason.GOLD_CONSTANT_ON_EVAL,
            MarginReason.MARGIN_FINER_THAN_RESOLUTION,
        }


@dataclass(frozen=True)
class ComparatorResponse:
    """One arm's record of what it did with the protected split.

    ``response_definition`` is required and must be non-empty for the same reason
    ``GuardExercise.opportunity_definition`` is: an arm whose inputs cannot be
    stated in a sentence cannot be audited for having read them, and the D1
    result that motivated this module named its arms (``TRANSCRIPT_BAG``) without
    ever recording that two of them answered every case identically.

    ``departures`` is the denominator. It counts the cases the arm answered with
    something other than its own most frequent answer --- the cases on which its
    score is a response rather than a tally of the split.
    """

    arm_id: str
    eval_cases: int
    correct: int
    prediction_counts: tuple[tuple[str, int], ...]
    label_counts: tuple[tuple[str, int], ...]
    departures: int
    departure_errors: int
    informedness: float | None
    response_definition: str

    def __post_init__(self) -> None:
        if not self.arm_id.strip():
            raise ValueError("arm id is required")
        if not self.response_definition.strip():
            raise ValueError(
                f"{self.arm_id}: a response definition is required; an arm whose inputs "
                "cannot be stated cannot be shown to have read the cases"
            )
        if self.eval_cases < 0 or self.correct < 0 or self.departures < 0:
            raise ValueError(f"{self.arm_id}: counts cannot be negative")
        if self.correct > self.eval_cases:
            raise ValueError(
                f"{self.arm_id}: {self.correct} correct exceeds {self.eval_cases} scored"
            )
        if self.departures > self.eval_cases:
            raise ValueError(
                f"{self.arm_id}: {self.departures} departures exceeds {self.eval_cases} scored"
            )
        if self.departure_errors > self.departures:
            raise ValueError(
                f"{self.arm_id}: {self.departure_errors} wrong departures exceeds "
                f"{self.departures} departures"
            )

    @property
    def accuracy(self) -> float | None:
        """The arm's accuracy, or ``None`` when it scored nothing.

        ``None`` rather than ``0.0`` for the reason ``GuardExercise.violation_rate``
        is: the failure this module prevents is a number standing in for an
        absent measurement.
        """

        if self.eval_cases == 0:
            return None
        return self.correct / self.eval_cases

    @property
    def distinct_predictions(self) -> int:
        return len(self.prediction_counts)

    @property
    def constant(self) -> bool:
        """True when the arm gave one answer, so its accuracy is a label prior."""

        return self.eval_cases > 0 and self.distinct_predictions == 1

    @property
    def trivial_floor(self) -> float | None:
        """Accuracy of the best constant predictor on this evaluation set.

        The score any arm gets for free. A margin computed against a comparator
        below it is a margin over an arm that guessed worse than not guessing.
        """

        if self.eval_cases == 0 or not self.label_counts:
            return None
        return max(count for _, count in self.label_counts) / self.eval_cases

    @property
    def prior_of_emitted(self) -> float | None:
        """For a constant arm, the label prior its accuracy is identically equal to."""

        if not self.constant:
            return None
        emitted = self.prediction_counts[0][0]
        priors = dict(self.label_counts)
        return priors.get(emitted, 0) / self.eval_cases

    @property
    def resolution(self) -> float | None:
        """Finest non-zero accuracy difference this many cases can express."""

        if self.eval_cases == 0:
            return None
        return 1.0 / self.eval_cases

    def as_json(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "eval_cases": self.eval_cases,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "prediction_counts": [list(item) for item in self.prediction_counts],
            "label_counts": [list(item) for item in self.label_counts],
            "distinct_predictions": self.distinct_predictions,
            "constant": self.constant,
            "departures": self.departures,
            "departure_errors": self.departure_errors,
            "informedness": self.informedness,
            "trivial_floor": self.trivial_floor,
            "prior_of_emitted": self.prior_of_emitted,
            "resolution": self.resolution,
            "response_definition": self.response_definition,
        }


def _informedness(gold: Sequence[str], predicted: Sequence[str]) -> float | None:
    """Macro informedness (``TPR + TNR - 1``) over the labels present in gold.

    Accuracy on a skewed label rewards a constant predictor in proportion to the
    skew; informedness is 0 for every constant predictor and 1 only for exact
    separation, so it is the statistic that survives re-composing the split. A
    label with no positives or no negatives contributes nothing rather than a
    zero, because an undefined term averaged in as 0.0 would penalise an arm for
    the split's shape.
    """

    per_label: list[float] = []
    for label in sorted(set(gold)):
        tp = sum(1 for g, p in zip(gold, predicted) if g == label and p == label)
        fn = sum(1 for g, p in zip(gold, predicted) if g == label and p != label)
        fp = sum(1 for g, p in zip(gold, predicted) if g != label and p == label)
        tn = sum(1 for g, p in zip(gold, predicted) if g != label and p != label)
        if tp + fn == 0 or tn + fp == 0:
            continue
        per_label.append(tp / (tp + fn) + tn / (tn + fp) - 1.0)
    if not per_label:
        return None
    return sum(per_label) / len(per_label)


def score_comparator(
    arm_id: str,
    *,
    gold: Sequence[Hashable],
    predicted: Sequence[Hashable],
    response_definition: str,
) -> ComparatorResponse:
    """Measure what an arm did with the split, rather than trusting its score.

    The predictions are compared against each other, not only against gold. An
    arm called a "same-information control" that answers every protected case
    with one label is indistinguishable from a constant at this boundary, and
    that is precisely the fact its name asserts is false.
    """

    if len(gold) != len(predicted):
        raise ValueError(f"{arm_id}: {len(predicted)} predictions over {len(gold)} gold labels")
    gold_values = [str(value) for value in gold]
    predicted_values = [str(value) for value in predicted]
    prediction_counts = tuple(sorted(Counter(predicted_values).items()))
    label_counts = tuple(sorted(Counter(gold_values).items()))
    modal = max(prediction_counts, key=lambda item: (item[1], item[0]))[0] if prediction_counts else None
    departures = [
        (g, p) for g, p in zip(gold_values, predicted_values, strict=True) if p != modal
    ]
    return ComparatorResponse(
        arm_id=arm_id,
        eval_cases=len(gold_values),
        correct=sum(1 for g, p in zip(gold_values, predicted_values, strict=True) if g == p),
        prediction_counts=prediction_counts,
        label_counts=label_counts,
        departures=len(departures),
        departure_errors=sum(1 for g, p in departures if g != p),
        informedness=_informedness(gold_values, predicted_values),
        response_definition=response_definition,
    )


@dataclass(frozen=True)
class ContrastMargin:
    """A three-valued verdict on whether a published difference measures the systems."""

    label: str
    treated: ComparatorResponse
    comparator: ComparatorResponse
    outcome: Outcome
    reason: MarginReason
    detail: str
    assessment: GuardAssessment

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("a contrast label is required")
        if self.treated.eval_cases != self.comparator.eval_cases:
            raise ValueError(
                f"{self.label}: {self.treated.arm_id} scored {self.treated.eval_cases} cases "
                f"and {self.comparator.arm_id} scored {self.comparator.eval_cases}; a paired "
                "margin over different splits is not a margin"
            )
        if self.treated.label_counts != self.comparator.label_counts:
            raise ValueError(
                f"{self.label}: the two arms were scored against different gold distributions"
            )
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.label}: {self.reason.value} cannot yield PASS; that substitution is "
                "the failure this module exists to prevent"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def published_margin(self) -> float | None:
        """The difference an artifact reports: candidate accuracy minus comparator."""

        if self.treated.accuracy is None or self.comparator.accuracy is None:
            return None
        return self.treated.accuracy - self.comparator.accuracy

    @property
    def informedness_margin(self) -> float | None:
        """The same difference in the statistic that does not move with the split."""

        if self.treated.informedness is None or self.comparator.informedness is None:
            return None
        return self.treated.informedness - self.comparator.informedness

    @property
    def earned_margin(self) -> float | None:
        """How far the candidate beats the better of the comparator and a constant.

        A comparator scoring below the trivial floor cannot lend the difference
        between them to the candidate: that part of the published margin was
        supplied by the split's label prior, not won.
        """

        floor = self.comparator.trivial_floor
        if self.treated.accuracy is None or self.comparator.accuracy is None or floor is None:
            return None
        return self.treated.accuracy - max(self.comparator.accuracy, floor)

    @property
    def prior_supplied(self) -> float | None:
        """The part of the published margin the label prior supplied."""

        published = self.published_margin
        earned = self.earned_margin
        if published is None or earned is None:
            return None
        return published - earned

    def as_json(self) -> dict[str, object]:
        return {
            "label": self.label,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "published_margin": self.published_margin,
            "informedness_margin": self.informedness_margin,
            "earned_margin": self.earned_margin,
            "prior_supplied": self.prior_supplied,
            "treated": self.treated.as_json(),
            "comparator": self.comparator.as_json(),
            "assessment": self.assessment.as_json(),
        }


def _exercise(label: str, comparator: ComparatorResponse) -> GuardExercise:
    return GuardExercise(
        guard_id=label,
        arm_id=comparator.arm_id,
        opportunities=comparator.departures,
        violations=comparator.departure_errors,
        opportunity_definition=(
            f"protected cases on which {comparator.arm_id} answered something other than its "
            "own most frequent answer, so its score is a response to the case rather than a "
            "tally of the split's label prior"
        ),
    )


def measure_contrast_margin(
    label: str,
    *,
    treated: ComparatorResponse,
    comparator: ComparatorResponse,
    claimed_margin: float = 0.0,
    max_departure_error_rate: float = 1.0,
) -> ContrastMargin:
    """Decide whether ``treated`` minus ``comparator`` is about the two arms.

    ``max_departure_error_rate`` defaults to 1.0 because the verdict this module
    exists for is the *denominator*: a comparator that read the cases and was
    often wrong is still a comparator, and scoring it on its error rate would
    reintroduce the confusion between a weak arm and an absent one. Tighten it
    only when the comparator is itself claimed to be competent.
    """

    assessment = assess_guard(_exercise(label, comparator), max_violation_rate=max_departure_error_rate)

    if comparator.eval_cases == 0:
        return ContrastMargin(
            label=label,
            treated=treated,
            comparator=comparator,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginReason.NO_EVAL_CASES,
            detail=(
                f"{label}: no protected case was scored, so the difference between the arms "
                "is a difference between two empty sets"
            ),
            assessment=assessment,
        )
    if len(comparator.label_counts) < 2:
        only = comparator.label_counts[0][0] if comparator.label_counts else "<none>"
        return ContrastMargin(
            label=label,
            treated=treated,
            comparator=comparator,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginReason.GOLD_CONSTANT_ON_EVAL,
            detail=(
                f"{label}: every protected case carries gold {only!r}, so answering {only!r} "
                "unconditionally scores 1.0 and no difference between arms is informative"
            ),
            assessment=assessment,
        )
    if comparator.constant:
        emitted = comparator.prediction_counts[0][0]
        return ContrastMargin(
            label=label,
            treated=treated,
            comparator=comparator,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginReason.COMPARATOR_CONSTANT,
            detail=(
                f"{label}: {comparator.arm_id} answered {emitted!r} on all "
                f"{comparator.eval_cases} protected cases, so its accuracy is identically "
                f"prior({emitted}) = {comparator.prior_of_emitted} and the published margin "
                "is a statistic of the split's label distribution"
            ),
            assessment=assessment,
        )
    if treated.constant:
        emitted = treated.prediction_counts[0][0]
        return ContrastMargin(
            label=label,
            treated=treated,
            comparator=comparator,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginReason.TREATED_CONSTANT,
            detail=(
                f"{label}: {treated.arm_id} answered {emitted!r} on all {treated.eval_cases} "
                "protected cases; a candidate whose score is a label prior has not been "
                "measured either"
            ),
            assessment=assessment,
        )

    resolution = comparator.resolution
    assert resolution is not None  # a non-empty split has a resolution
    if 0.0 < claimed_margin < resolution:
        return ContrastMargin(
            label=label,
            treated=treated,
            comparator=comparator,
            outcome=Outcome.CANNOT_CHECK,
            reason=MarginReason.MARGIN_FINER_THAN_RESOLUTION,
            detail=(
                f"{label}: a claimed margin of {claimed_margin} is finer than the "
                f"{resolution} resolution of {comparator.eval_cases} cases; every observable "
                "difference either satisfies it trivially or overshoots it by a whole case"
            ),
            assessment=assessment,
        )

    floor = comparator.trivial_floor
    accuracy = treated.accuracy
    assert floor is not None and accuracy is not None  # non-empty split
    if accuracy <= floor:
        return ContrastMargin(
            label=label,
            treated=treated,
            comparator=comparator,
            outcome=Outcome.FAIL,
            reason=MarginReason.TREATED_BELOW_TRIVIAL_FLOOR,
            detail=(
                f"{label}: {treated.arm_id} scores {accuracy} and the best constant on this "
                f"split scores {floor}; a difference over {comparator.arm_id} does not "
                "establish superiority over answering nothing at all"
            ),
            assessment=assessment,
        )
    return ContrastMargin(
        label=label,
        treated=treated,
        comparator=comparator,
        outcome=Outcome.PASS,
        reason=MarginReason.COMPARATOR_RESPONDED,
        detail=(
            f"{label}: {comparator.arm_id} departed from its most frequent answer on "
            f"{comparator.departures}/{comparator.eval_cases} protected cases, and "
            f"{treated.arm_id} scores {accuracy} against a trivial floor of {floor}"
        ),
        assessment=assessment,
    )


@dataclass(frozen=True)
class CompositionSensitivity:
    """How much of a published margin is a property of the evaluation set's shape.

    The counterpart of :class:`orion.programme.refutation_capacity.AxisSensitivity`:
    there an axis that changes no verdict is a multiplier on every count the
    artifact reports, here a margin that moves under re-composition is a
    measurement of the composition. Both are asked of the *shipped* numbers, with
    nothing refitted --- the recompositions below re-score frozen predictions.
    """

    label: str
    compositions: int
    published_margin_low: float
    published_margin_high: float
    informedness_margin_low: float
    informedness_margin_high: float

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("a sensitivity label is required")
        if self.compositions <= 0:
            raise ValueError(f"{self.label}: no composition was scored")
        if self.published_margin_low > self.published_margin_high:
            raise ValueError(f"{self.label}: published margin range is inverted")
        if self.informedness_margin_low > self.informedness_margin_high:
            raise ValueError(f"{self.label}: informedness margin range is inverted")

    @property
    def published_span(self) -> float:
        return self.published_margin_high - self.published_margin_low

    @property
    def informedness_span(self) -> float:
        return self.informedness_margin_high - self.informedness_margin_low

    @property
    def composition_valued(self) -> bool:
        """True when re-composition moved the accuracy margin and informedness not at all.

        Exact equality, in the way ``AxisSensitivity.inert`` counts exactly zero
        verdict-changing pairs: a margin between two arms that both answer the
        same way on every case has an informedness difference that is the same
        number in every sub-multiset of the split, and a span of literally zero
        beside a span of 0.91 is the whole diagnosis.
        """

        return self.published_span > 0.0 and self.informedness_span == 0.0

    def as_json(self) -> dict[str, object]:
        return {
            "label": self.label,
            "compositions": self.compositions,
            "published_margin_low": self.published_margin_low,
            "published_margin_high": self.published_margin_high,
            "published_span": self.published_span,
            "informedness_margin_low": self.informedness_margin_low,
            "informedness_margin_high": self.informedness_margin_high,
            "informedness_span": self.informedness_span,
            "composition_valued": self.composition_valued,
        }


def measure_composition_sensitivity(
    label: str,
    *,
    gold: Sequence[Hashable],
    treated: Sequence[Hashable],
    comparator: Sequence[Hashable],
    compositions: Sequence[Sequence[int]],
) -> CompositionSensitivity:
    """Re-score frozen predictions on declared re-compositions of the same cases.

    ``compositions`` are index selections into the evaluation set. Nothing is
    refitted and no case is invented: each composition is a sub-multiset of the
    protected split the artifact already scored, so any movement it produces is
    attributable to the split's shape alone.
    """

    if not compositions:
        raise ValueError(f"{label}: at least one composition is required")
    if not (len(gold) == len(treated) == len(comparator)):
        raise ValueError(f"{label}: the three vectors must cover the same cases")

    published: list[float] = []
    informedness: list[float] = []
    for index, selection in enumerate(compositions):
        if not selection:
            raise ValueError(f"{label}: composition {index} selects no case")
        picked_gold = [gold[position] for position in selection]
        picked_treated = [treated[position] for position in selection]
        picked_comparator = [comparator[position] for position in selection]
        left = score_comparator(
            "treated",
            gold=picked_gold,
            predicted=picked_treated,
            response_definition="frozen predictions re-scored on a re-composed split",
        )
        right = score_comparator(
            "comparator",
            gold=picked_gold,
            predicted=picked_comparator,
            response_definition="frozen predictions re-scored on a re-composed split",
        )
        if left.accuracy is None or right.accuracy is None:
            raise ValueError(f"{label}: composition {index} scored nothing")
        published.append(left.accuracy - right.accuracy)
        if left.informedness is not None and right.informedness is not None:
            informedness.append(left.informedness - right.informedness)
    if not informedness:
        raise ValueError(
            f"{label}: no composition admitted an informedness margin; a sensitivity report "
            "with only accuracies cannot say which statistic moved"
        )
    return CompositionSensitivity(
        label=label,
        compositions=len(compositions),
        published_margin_low=min(published),
        published_margin_high=max(published),
        informedness_margin_low=min(informedness),
        informedness_margin_high=max(informedness),
    )


@dataclass(frozen=True)
class EarnedMargin:
    """A margin that cannot exist without a comparator that answered.

    This is the mechanism, not the report. A margin whose contrast blocks is not
    a weaker result to be caveated in a limitations paragraph; it is a number
    that has not been shown to be about the arms it names, and the class refuses
    to hold one. Reporting it therefore requires deleting this type rather than
    forgetting a check.
    """

    margin_name: str
    value: float
    contrast: ContrastMargin

    def __post_init__(self) -> None:
        if not self.margin_name.strip():
            raise ValueError("margin name is required")
        if self.contrast.blocks:
            raise ValueError(
                f"{self.margin_name}: contrast {self.contrast.label} returned "
                f"{self.contrast.outcome.value} ({self.contrast.reason.value}); "
                f"{self.contrast.detail}"
            )

    def as_json(self) -> dict[str, object]:
        return {
            "margin_name": self.margin_name,
            "value": self.value,
            "contrast": self.contrast.as_json(),
        }


def require_responsive_comparator(
    contrasts: Sequence[ContrastMargin], *, label: str
) -> None:
    """Raise before any margin is read as evidence of superiority.

    The comparison-side counterpart of ``require_operators_exercised``,
    ``require_treatment_applied``, ``require_refutable``, ``require_decided`` and
    ``require_responsive``. One line, and it names the arms that never answered.
    """

    blocked = [item for item in contrasts if item.blocks]
    if not blocked:
        return
    named = "; ".join(
        f"{item.label} [{item.outcome.value}/{item.reason.value}] {item.comparator.arm_id}"
        for item in blocked
    )
    raise PriorValuedMargin(
        f"{label}: {len(blocked)} of {len(contrasts)} contrasts cannot be quoted as a "
        f"superiority margin --- {named}"
    )


__all__ = [
    "ComparatorResponse",
    "CompositionSensitivity",
    "ContrastMargin",
    "EarnedMargin",
    "MarginReason",
    "PriorValuedMargin",
    "measure_composition_sensitivity",
    "measure_contrast_margin",
    "require_responsive_comparator",
    "score_comparator",
]
