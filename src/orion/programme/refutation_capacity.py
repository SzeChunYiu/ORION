"""Mechanized checks that cannot report a pass no false theory could have failed.

A formal result is reported as a checker that ran and a count of cases it
covered. That pair is identical in two entirely different worlds: the checker
enumerated a space and rejected every wrong theory it was handed, and the
checker enumerated a space and asserted something true of its own definitions.
The case count cannot tell them apart, so a check whose condition is
unsatisfiable reads exactly like a check that survived pressure.

P6 is the worked example, measured both ways. ``research/claim_expansion/p6/
check_p6_x_finite_models.py`` is the authority the superiority ledger names for
P6-U-T1, and it emitted ``"terminal": "PASS"`` from

.. code-block:: python

    def scientific_admissible(state, embedding):
        return donor_valid(state, embedding) and all(state[f] for f in SCI_FIELDS)

    def ideal_product(state, embedding):
        return donor_valid(state, embedding) and all(state[f] for f in SCI_FIELDS)

    if scientific_admissible(s, emb) != ideal_product(s, emb): t4_violations += 1

Two definitions, one expression, written twice. Over the checker's complete
Boolean state space --- 512 states per embedding, 1,536 in all --- the condition
was satisfied 0 times because it was unsatisfiable: with the two sides being one
rule, no theory of scientific admissibility makes them differ.
``t4_violations == 0`` was not a theorem about donor products; it was ``x != x``
counted 1,536 times. ``t1_violations`` was the same shape, and ``t2`` and ``t5``
appended their 96s unconditionally, so four of the five quantities that terminal
read could not be non-zero for any wrong theory. (P6's checkers were repaired on
2026-08-22 --- see :mod:`orion.study.p6` --- by giving the model the primitives
those claims needed. The worked example is kept in the past tense because it is
what this module exists to catch, not because it is still there.)

The failure class is recorded under
``research/failures/2026-08-unfalsifiable-check-zero-refutation-capacity/``.

The fix is to make the falsifier part of the verdict's type. A check is
exercised by a register of **declared false theories** --- rules a reader can
read and agree are wrong --- and the verdict is asked at two levels, because
those are two different failures. Per check: does it reject *any* live false
theory, or is it true of anything? Per panel
(:func:`assess_theory_coverage`): is every false theory rejected by *some*
check, or does one walk through the whole artifact? Both return
:data:`~orion.programme.records.Outcome.CANNOT_CHECK` when there was nothing to
reject, which by ``Outcome.blocks`` stops a promotion exactly as ``FAIL`` does.

The two levels are not redundant, and P6 needed both. Its certificate-lifting
checker had three blocks with real refutation capacity and two with none, which
is the per-check failure; separately it had one wrong theory --- "scientific
standing is preserved with no valid donor certificate underneath it" --- that
survived all five, which is the panel failure and which no per-check verdict
could see.

Two constraints on the register carry most of the weight.

A theory only counts if it is **extensionally different** from the reference
somewhere in the enumerated space. That is
:class:`orion.study.p3.treatment_contrast.TreatmentContrast`'s question asked
about a rule instead of a corpus, and it is not decorative here: P6's
"independent" verifier defines ``independent_lift`` as an early-return loop and
the primary defines ``liftable`` as ``native_valid and all(science)``. They
differ on 0 of the 320 enumerated points, so the second implementation can
confirm the first and refute nothing.

A theory is rejected only when the check's own assertions reject it. A mutant
that raises ``TypeError`` was refuted by Python, not by the theorem, so only
``AssertionError`` counts as a kill --- the distinction
``research/failures/2026-08-digest-representation-boundary-mixup/`` is about.

The verdict is built from :class:`orion.programme.guard_exercise.GuardExercise`
rather than beside it: the opportunities are the live false theories and the
violations are the ones that survived, so "nobody proposed a wrong theory" and
"the guard was never pressed" are the same state and get the same three-valued
answer.

Scope-general on purpose. It knows nothing about certificates, lifting or P6; it
takes a rule, a space and a register of wrong rules, and returns a typed verdict.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Hashable, Mapping, Sequence

from orion.programme.guard_exercise import GuardAssessment, GuardExercise, assess_guard
from orion.programme.records import Outcome

#: One point of a checker's enumerated model space, keyed by named axis.
#:
#: A mapping rather than an opaque object because the axes are what
#: :func:`axis_sensitivity` needs: a checker that loops over an axis no rule
#: reads is multiplying its own case count, and that is invisible unless the
#: axes have names.
ModelPoint = Mapping[str, Hashable]

#: A rule under test: the thing the checker's assertions are about.
Rule = Callable[[ModelPoint], Hashable]

#: The arm label every refutation exercise carries. There is only one arm --- a
#: check is not compared against a comparator check --- but ``GuardExercise``
#: requires the field, and naming it keeps the emitted JSON readable.
DECLARED_FALSE_THEORIES = "declared-false-theories"


class UnrefutableCheck(ValueError):
    """Raised when a check is scored before anything could have made it fail."""


@dataclass(frozen=True)
class FalseTheory:
    """A rule a reader can read and agree is wrong, for the check to reject.

    ``breaks`` is required and must be non-empty for the same reason
    ``GuardExercise.opportunity_definition`` is: a wrong theory whose wrongness
    cannot be stated in a sentence is a mutation, not a falsifier, and the
    register is the artifact a reviewer actually audits.
    """

    theory_id: str
    breaks: str
    rule: Rule

    def __post_init__(self) -> None:
        if not self.theory_id.strip():
            raise ValueError("a false theory id is required")
        if not self.breaks.strip():
            raise ValueError(
                f"{self.theory_id}: state which claim this theory breaks; a rule nobody "
                "can see is wrong does not test anything by being rejected"
            )


@dataclass(frozen=True)
class TheoryDivergence:
    """How far a candidate theory actually departs from the reference rule.

    The counterpart of ``TreatmentContrast.cases_treated``: a theory that agrees
    with the reference on every enumerated point is the reference under another
    name, and a check that "rejects" it would be reading the name.
    """

    theory_id: str
    points: int
    points_changed: int

    def __post_init__(self) -> None:
        if not self.theory_id.strip():
            raise ValueError("a theory id is required")
        if self.points <= 0:
            raise ValueError(f"{self.theory_id}: an empty model space distinguishes nothing")
        if self.points_changed < 0:
            raise ValueError(f"{self.theory_id}: counts cannot be negative")
        if self.points_changed > self.points:
            raise ValueError(
                f"{self.theory_id}: {self.points_changed} divergent points exceeds "
                f"{self.points} enumerated"
            )

    @property
    def applied(self) -> bool:
        return self.points_changed > 0

    @property
    def divergence_rate(self) -> float:
        return self.points_changed / self.points

    def as_json(self) -> dict[str, Any]:
        return {
            "theory_id": self.theory_id,
            "points": self.points,
            "points_changed": self.points_changed,
            "applied": self.applied,
            "divergence_rate": self.divergence_rate,
        }


@dataclass(frozen=True)
class MechanizedCheck:
    """One checkable claim, expressed as a predicate over the rule under test.

    ``accepts`` replays the checker's own assertions and counters against a
    supplied rule and answers the only question that matters about a mechanized
    theorem: does this checker still say PASS if the theory is that one? It is
    ``bool`` rather than a verdict object because a checker script has exactly
    two outcomes, and flattening it here keeps the registration faithful to the
    artifact being audited.
    """

    check_id: str
    asserts: str
    accepts: Callable[[Rule], bool]

    def __post_init__(self) -> None:
        if not self.check_id.strip():
            raise ValueError("a check id is required")
        if not self.asserts.strip():
            raise ValueError(
                f"{self.check_id}: state what this check asserts; an unstated claim "
                "cannot be shown to have a falsifier"
            )


@dataclass(frozen=True)
class RefutationCapacity:
    """A three-valued verdict on "this check could have failed", with its register."""

    check_id: str
    reference_id: str
    divergences: tuple[TheoryDivergence, ...]
    survivors: tuple[str, ...]
    refuted: tuple[str, ...]
    exercise: GuardExercise

    def __post_init__(self) -> None:
        if not self.divergences:
            raise ValueError(
                f"{self.check_id}: a capacity must carry the register it was measured over"
            )

    @property
    def assessment(self) -> GuardAssessment:
        """Three-valued: does this check reject *any* live false theory?

        The ceiling is "at least one refuted" rather than "all refuted" because a
        real checker splits its claims across blocks and no single block covers
        the whole register. What is being asked here is only whether this check
        constrains the theory at all; whether the register is covered is a
        property of the panel and is :func:`assess_theory_coverage`'s question.
        """

        live = self.exercise.opportunities
        ceiling = (live - 1) / live if live else 0.0
        return assess_guard(self.exercise, max_violation_rate=ceiling)

    @property
    def outcome(self) -> Outcome:
        return self.assessment.outcome

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def inert_theories(self) -> tuple[str, ...]:
        """Registered theories that are the reference rule restated.

        Reported rather than silently dropped: a register in which every entry
        is inert is exactly as vacuous as an empty one, and the reader needs to
        see which entries bought nothing.
        """

        return tuple(item.theory_id for item in self.divergences if not item.applied)

    def as_json(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "reference_id": self.reference_id,
            "outcome": self.outcome.value,
            "reason": self.assessment.reason.value,
            "detail": self.assessment.detail,
            "refuted": list(self.refuted),
            "survivors": list(self.survivors),
            "inert_theories": list(self.inert_theories),
            "divergences": [item.as_json() for item in self.divergences],
        }


@dataclass(frozen=True)
class AxisSensitivity:
    """Whether a checker's enumerated axis changes any verdict, or only the case count.

    P6's certificate-lifting checker loops over five donor families and its rule
    never takes the donor as an argument, so its headline 320 / 25 / 155 / 1,055
    are 64 / 5 / 31 / 211 distinct facts and a five-fold relabelling. An axis
    that no verdict depends on is a multiplier on every number the artifact
    reports.
    """

    axis: str
    values: int
    comparable_pairs: int
    verdict_changing_pairs: int

    def __post_init__(self) -> None:
        if not self.axis.strip():
            raise ValueError("an axis name is required")
        if self.verdict_changing_pairs > self.comparable_pairs:
            raise ValueError(
                f"{self.axis}: {self.verdict_changing_pairs} changing pairs exceeds "
                f"{self.comparable_pairs} comparable"
            )

    @property
    def varied(self) -> bool:
        """False when the axis is constant, so nothing about it was ever tested."""

        return self.values > 1 and self.comparable_pairs > 0

    @property
    def inert(self) -> bool:
        return self.varied and self.verdict_changing_pairs == 0

    @property
    def multiplier(self) -> int:
        """How many times an inert axis repeats every case the checker counts."""

        return self.values if self.inert else 1

    def as_json(self) -> dict[str, Any]:
        return {
            "axis": self.axis,
            "values": self.values,
            "comparable_pairs": self.comparable_pairs,
            "verdict_changing_pairs": self.verdict_changing_pairs,
            "varied": self.varied,
            "inert": self.inert,
            "multiplier": self.multiplier,
        }


def divergence_of(
    rule: Rule, *, theory_id: str, reference: Rule, space: Sequence[ModelPoint]
) -> TheoryDivergence:
    """Count the enumerated points on which a candidate theory and the reference differ."""

    if not space:
        raise ValueError(f"{theory_id}: an empty model space distinguishes nothing")
    changed = sum(1 for point in space if rule(point) != reference(point))
    return TheoryDivergence(theory_id=theory_id, points=len(space), points_changed=changed)


def _rejects(check: MechanizedCheck, rule: Rule) -> bool:
    """True when the check's own assertions reject this rule.

    Only ``AssertionError`` counts. A rule that raises ``TypeError`` was refuted
    by the interpreter rather than by the theorem, and crediting that as a kill
    is how a type error at a boundary becomes a scientific result.
    """

    try:
        return not check.accepts(rule)
    except AssertionError:
        return True


def measure_refutation_capacity(
    check: MechanizedCheck,
    *,
    reference: Rule,
    reference_id: str,
    theories: Sequence[FalseTheory],
    space: Sequence[ModelPoint],
) -> RefutationCapacity:
    """Measure whether any declared false theory would have made this check fail.

    The check must accept the reference: a registration that rejects the rule
    the shipped artifact actually ran is a transcription error, and reporting it
    as a refutation would credit the instrument for catching its own bug.

    A theory that agrees with the reference everywhere in ``space`` is excluded
    from the denominator, not counted as a survivor. If such a theory is
    *rejected*, the check is reading something other than the rule's behaviour
    and the measurement is refused outright.
    """

    if not space:
        raise ValueError(f"{check.check_id}: an empty model space distinguishes nothing")
    if not theories:
        raise UnrefutableCheck(
            f"{check.check_id}: no false theory is registered, so the check has nothing "
            "to reject and its pass is a statement about its own definitions"
        )
    if not check.accepts(reference):
        raise ValueError(
            f"{check.check_id}: the check rejects {reference_id}, the rule the audited "
            "artifact ran; fix the registration before reading any verdict from it"
        )

    divergences: list[TheoryDivergence] = []
    survivors: list[str] = []
    refuted: list[str] = []
    for theory in theories:
        divergence = divergence_of(
            theory.rule, theory_id=theory.theory_id, reference=reference, space=space
        )
        divergences.append(divergence)
        rejected = _rejects(check, theory.rule)
        if not divergence.applied:
            if rejected:
                raise ValueError(
                    f"{check.check_id}: rejected {theory.theory_id}, which agrees with "
                    f"{reference_id} on all {len(space)} enumerated points; the check is "
                    "not a function of the rule's behaviour"
                )
            continue
        (refuted if rejected else survivors).append(theory.theory_id)

    live = len(refuted) + len(survivors)
    exercise = GuardExercise(
        guard_id=check.check_id,
        arm_id=DECLARED_FALSE_THEORIES,
        opportunities=live,
        violations=len(survivors),
        opportunity_definition=(
            f"registered false theories that differ from {reference_id} on at least one "
            f"of the {len(space)} enumerated points; {check.asserts}"
        ),
    )
    return RefutationCapacity(
        check_id=check.check_id,
        reference_id=reference_id,
        divergences=tuple(divergences),
        survivors=tuple(survivors),
        refuted=tuple(refuted),
        exercise=exercise,
    )


def axis_sensitivity(
    axis: str, *, reference: Rule, space: Sequence[ModelPoint]
) -> AxisSensitivity:
    """Measure whether the reference verdict ever depends on one enumerated axis.

    Points are compared only against points agreeing on every *other* axis, so
    the answer is about the axis rather than about the space's shape. An axis
    the verdict never depends on is a loop multiplier, and every count the
    checker reports over that loop is repeated once per value.
    """

    if not space:
        raise ValueError(f"{axis}: an empty model space distinguishes nothing")
    missing = [index for index, point in enumerate(space) if axis not in point]
    if missing:
        raise ValueError(
            f"{axis}: absent from {len(missing)} of {len(space)} enumerated points; "
            "an axis that is not on every point cannot be held fixed"
        )

    grouped: dict[tuple[tuple[str, Hashable], ...], list[ModelPoint]] = defaultdict(list)
    for point in space:
        rest = tuple(sorted((key, value) for key, value in point.items() if key != axis))
        grouped[rest].append(point)

    comparable = 0
    changing = 0
    for siblings in grouped.values():
        for left_index in range(len(siblings)):
            for right_index in range(left_index + 1, len(siblings)):
                comparable += 1
                if reference(siblings[left_index]) != reference(siblings[right_index]):
                    changing += 1
    return AxisSensitivity(
        axis=axis,
        values=len({point[axis] for point in space}),
        comparable_pairs=comparable,
        verdict_changing_pairs=changing,
    )


@dataclass(frozen=True)
class TheoryCoverage:
    """Whether the panel as a whole rejects every false theory in the register.

    A check may legitimately be silent about most of the register; the artifact
    may not. A theory no check anywhere rejects is a wrong theory the whole
    result certifies, and it is invisible per-check because each block can point
    at another block.
    """

    label: str
    live: tuple[str, ...]
    unrefuted: tuple[str, ...]
    exercise: GuardExercise

    def __post_init__(self) -> None:
        stray = set(self.unrefuted) - set(self.live)
        if stray:
            raise ValueError(
                f"{self.label}: {sorted(stray)} are reported unrefuted but are not live"
            )

    @property
    def assessment(self) -> GuardAssessment:
        """Three-valued, with no tolerance: one uncaught false theory is one too many."""

        return assess_guard(self.exercise, max_violation_rate=0.0)

    @property
    def outcome(self) -> Outcome:
        return self.assessment.outcome

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "outcome": self.outcome.value,
            "reason": self.assessment.reason.value,
            "detail": self.assessment.detail,
            "live": list(self.live),
            "unrefuted": list(self.unrefuted),
        }


def assess_theory_coverage(
    capacities: Sequence[RefutationCapacity], *, label: str
) -> TheoryCoverage:
    """Roll a panel up by false theory rather than by check.

    Every capacity must have been measured over the same register, because a
    theory absent from one check's register would otherwise read as covered by
    the checks that do carry it.
    """

    if not capacities:
        raise UnrefutableCheck(f"{label}: an empty check panel proves nothing")

    registers = {tuple(item.theory_id for item in capacity.divergences) for capacity in capacities}
    if len(registers) > 1:
        raise ValueError(
            f"{label}: the checks were measured over different registers, so a theory "
            "missing from one would read as covered by another"
        )

    live: list[str] = []
    refuted: set[str] = set()
    for capacity in capacities:
        refuted.update(capacity.refuted)
    for divergence in capacities[0].divergences:
        if divergence.applied:
            live.append(divergence.theory_id)

    unrefuted = tuple(theory_id for theory_id in live if theory_id not in refuted)
    exercise = GuardExercise(
        guard_id=label,
        arm_id=DECLARED_FALSE_THEORIES,
        opportunities=len(live),
        violations=len(unrefuted),
        opportunity_definition=(
            f"registered false theories that differ from the reference somewhere in the "
            f"enumerated space; each must be rejected by at least one of the "
            f"{len(capacities)} checks"
        ),
    )
    return TheoryCoverage(
        label=label, live=tuple(live), unrefuted=unrefuted, exercise=exercise
    )


def require_refutable(capacities: Sequence[RefutationCapacity], *, label: str) -> None:
    """Refuse to report a formal result before it could have come out otherwise.

    The formal-side counterpart of ``require_operators_exercised`` and
    ``require_treatment_applied``: it raises, naming the checks that no wrong
    theory can fail and the wrong theories no check catches, before any case
    count is read as evidence.
    """

    coverage = assess_theory_coverage(capacities, label=label)
    unrefutable = [item.check_id for item in capacities if item.outcome is Outcome.CANNOT_CHECK]
    tautological = [item.check_id for item in capacities if item.outcome is Outcome.FAIL]
    if not unrefutable and not tautological and not coverage.blocks:
        return

    parts = []
    if tautological:
        parts.append(
            f"{len(tautological)} of {len(capacities)} checks reject no declared false "
            f"theory ({', '.join(sorted(tautological))})"
        )
    if unrefutable:
        parts.append(
            f"{len(unrefutable)} of {len(capacities)} checks have no live falsifier at all "
            f"({', '.join(sorted(unrefutable))})"
        )
    if coverage.blocks:
        parts.append(
            f"{len(coverage.unrefuted)} of {len(coverage.live)} false theories are rejected "
            f"by no check ({', '.join(sorted(coverage.unrefuted))})"
            if coverage.unrefuted
            else "no live false theory is registered"
        )
    raise UnrefutableCheck(f"{label}: " + "; ".join(parts))


__all__ = [
    "DECLARED_FALSE_THEORIES",
    "AxisSensitivity",
    "FalseTheory",
    "MechanizedCheck",
    "ModelPoint",
    "RefutationCapacity",
    "Rule",
    "TheoryCoverage",
    "TheoryDivergence",
    "UnrefutableCheck",
    "assess_theory_coverage",
    "axis_sensitivity",
    "divergence_of",
    "measure_refutation_capacity",
    "require_refutable",
]
