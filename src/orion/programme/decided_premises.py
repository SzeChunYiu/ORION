"""Mechanized claims that cannot report a pass on a premise they were handed.

A formal claim usually has two halves. One is a *decision*: given a case, which
way does the hard predicate go. The other is a *mapping*: given that predicate's
value, which terminal follows. Only the first is normally the science; the second
is usually a table anyone would write the same way.

A checker that takes the predicate as a parameter and enumerates both of its
values verifies the second half exhaustively and says nothing whatever about the
first. The case count is real, the enumeration is complete, and the quantity the
claim is about was supplied by the caller.

P7 is the live example, measured on the shipped artifacts. ``papers/
paper-07-epistemic-navigation-open-worlds/formal/check_theory_closure_v2.py`` is
the authority ``REPRODUCE_V2_1.md`` names for "all 64 transport-coordinate
combinations", and its transport theorem reads::

    def transfer_terminal(t: Transport, *, target_ambiguous_if_missing: bool) -> str:
        if t.complete:
            return "TRANSFER_CLOSURE"
        return "REOPEN" if target_ambiguous_if_missing else "CANNOT_CHECK"

``target_ambiguous_if_missing`` is the paper's C4 --- whether the unresolved part
of a transport witness admits one target completion preserving the certificate
and one invalidating it --- and the checker used to pass it in as ``True`` and
then as ``False`` for every one of the 64 states. Measured over that space, **0
of 64 cases constrained it**: all 2**64 ambiguity predicates were accepted,
including the constant-false one that is the exact V1 error the V2 core says it
fixes.

**Repaired 2026-08-22, and the repair is what the class prescribes.** The
shipped checker now enumerates an admissible target-completion class beside each
witness and decides the premise per case with its own ``extension_ambiguous``.
The axis it needed was missing, not the assertion: 960 cases, 0 free, exactly one
admissible rule, 0 of 5,000 random whole rules accepted, and
``theory_closure_terminal`` moves ``CANNOT_CHECK`` to ``PASS``. The 960 is not a
larger 64 --- it is 64 coordinate states crossed with 15 completion classes, and
the two counts are incomparable, which the artifacts say. The pre-repair model is
kept as an explicitly labelled counterfactual and still reports
``UNDECIDABLE_IN_MODEL`` on its 64, so the contrast this module teaches from
stays runnable.

The failure class is recorded under
``research/failures/2026-08-supplied-premise-unbuilt-decision/``.

This is not the P6 tautology in another shape, and the distinction is the reason
the module exists. ``check_support_transport`` **has** refutation capacity: four
declared wrong theories of the terminal map are all refuted by it, so
:mod:`orion.programme.refutation_capacity` clears it. What no register of false
theories can reach is a wrong theory of *ambiguity*, because there is no rule to
perturb --- perturbing a parameter changes the case, not the theory. **The space
of false theories a checker can be measured against is bounded by which of the
claim's predicates it computes**, and a supplied premise silently removes itself
from that register.

So the verdict here is asked of the premise rather than of the check, and it is
built on :class:`orion.programme.guard_exercise.GuardExercise` rather than beside
it: the opportunities are the enumerated cases and the violations are the cases
that leave the premise free. "The checker enumerated nothing" and "the guard was
never pressed" are then one state with one three-valued answer, and
:data:`~orion.programme.records.Outcome.CANNOT_CHECK` blocks a promotion exactly
as ``FAIL`` does.

Two premises fail differently and the difference is worth a separate reason.
``bridge_match`` in P7's closure-carrying checker is supplied while the model
carries both donor transforms the bridge is a property of --- it *could* have
been decided there and was not. ``target_ambiguous_if_missing`` is supplied and
the model has no admissible-completion class in it at all, so no rule written
against that space could decide it. The first is an omission; the second says the
model is too poor to express the claim.

Scope-general on purpose. It knows nothing about closure, transport or P7; it
takes a premise, a case space and a replay of somebody's assertions, and returns
a typed verdict.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Hashable, Sequence

from orion.programme.guard_exercise import GuardExercise, assess_guard
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import ModelPoint, RefutationCapacity

#: A candidate rule that decides one premise from the case, i.e. the thing the
#: audited artifact was supposed to contain and does not.
Assignment = Callable[[ModelPoint], Hashable]

#: Replays an artifact's own assertions with one premise decided by a rule.
#: ``bool`` rather than a verdict object for the reason
#: :class:`orion.programme.refutation_capacity.MechanizedCheck` uses one: a
#: checker script has two outcomes, and flattening keeps the transcription
#: faithful to the artifact being audited.
AssertionReplay = Callable[[Assignment], bool]

#: The arm label every decision exercise carries. There is only one arm --- a
#: premise is not compared against a comparator premise --- but ``GuardExercise``
#: requires the field and naming it keeps the emitted JSON readable.
ENUMERATED_CASES = "enumerated-cases"


class UndecidedPremise(ValueError):
    """Raised when a mechanized result is read before its premise was decided."""


class DecisionReason(str, Enum):
    """Why a premise came out decided, supplied, or unaskable.

    The three vacuity reasons are the point of the module: each is a state in
    which a checker reports a full case count while the claim's own predicate was
    never computed from anything.
    """

    DECIDED_ON_EVERY_CASE = "DECIDED_ON_EVERY_CASE"
    PREMISE_SUPPLIED = "PREMISE_SUPPLIED"
    UNDECIDABLE_IN_MODEL = "UNDECIDABLE_IN_MODEL"
    NO_CASES_ENUMERATED = "NO_CASES_ENUMERATED"
    BASELINE_REJECTED = "BASELINE_REJECTED"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report an absent question, not an answer."""

        return self in {
            DecisionReason.UNDECIDABLE_IN_MODEL,
            DecisionReason.NO_CASES_ENUMERATED,
            DecisionReason.BASELINE_REJECTED,
        }


@dataclass(frozen=True)
class Premise:
    """One predicate a claim says the system decides, with what it must read.

    ``decision_obligation`` and ``decided_from`` are both required, for the reason
    ``GuardExercise.opportunity_definition`` is: a premise whose decision cannot
    be stated in a sentence cannot be shown to have been made, and the names in
    ``decided_from`` are what makes "the model cannot express this decision"
    checkable rather than arguable.
    """

    premise_id: str
    claim_ref: str
    decision_obligation: str
    decided_from: tuple[str, ...]
    domain: tuple[Hashable, ...]

    def __post_init__(self) -> None:
        if not self.premise_id.strip():
            raise ValueError("a premise id is required")
        if not self.claim_ref.strip():
            raise ValueError(f"{self.premise_id}: name the claim this premise belongs to")
        if not self.decision_obligation.strip():
            raise ValueError(
                f"{self.premise_id}: state what this premise must be decided from; a "
                "decision nobody can describe cannot be shown to have been made"
            )
        if not self.decided_from or any(not str(name).strip() for name in self.decided_from):
            raise ValueError(
                f"{self.premise_id}: decided_from must name the inputs the decision reads"
            )
        if len(set(self.domain)) < 2:
            raise ValueError(
                f"{self.premise_id}: a premise with fewer than two values decides nothing"
            )


@dataclass(frozen=True)
class CaseAdmissibility:
    """Which values of a premise one enumerated case still lets the check accept.

    ``admissible`` always contains the baseline value, because the baseline is
    what the shipped artifact ran. A case is ``free`` when it excludes nothing.
    """

    case_id: str
    baseline_value: Hashable
    admissible: tuple[Hashable, ...]
    domain_size: int

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("a case id is required")
        if not self.admissible:
            raise ValueError(
                f"{self.case_id}: the baseline value is admissible by construction, so an "
                "empty admissible set means the replay is not a function of the premise"
            )
        if self.baseline_value not in self.admissible:
            raise ValueError(f"{self.case_id}: the baseline value must be admissible")
        if len(self.admissible) > self.domain_size:
            raise ValueError(f"{self.case_id}: more admissible values than the domain holds")

    @property
    def free(self) -> bool:
        """True when the case rules out no value, so it decides nothing."""

        return len(self.admissible) == self.domain_size

    @property
    def decided(self) -> bool:
        return len(self.admissible) == 1

    def as_json(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "baseline_value": self.baseline_value,
            "admissible": list(self.admissible),
            "free": self.free,
            "decided": self.decided,
        }


@dataclass(frozen=True)
class DecisionConstraint:
    """A three-valued verdict on "this artifact decided that premise"."""

    premise: Premise
    check_id: str
    cases: tuple[CaseAdmissibility, ...]
    modelled: bool
    exercise: GuardExercise
    outcome: Outcome
    reason: DecisionReason
    detail: str

    def __post_init__(self) -> None:
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.check_id}/{self.premise.premise_id}: {self.reason.value} cannot "
                "yield PASS; that substitution is the failure this module prevents"
            )
        if self.outcome is Outcome.PASS and self.free_case_ids:
            raise ValueError(
                f"{self.check_id}/{self.premise.premise_id}: "
                f"{len(self.free_case_ids)} cases leave the premise free, so it was supplied"
            )
        if self.outcome is not Outcome.PASS and self.reason is DecisionReason.DECIDED_ON_EVERY_CASE:
            raise ValueError(
                f"{self.check_id}/{self.premise.premise_id}: a premise decided on every "
                "case cannot block; the reason and the outcome disagree"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def free_case_ids(self) -> tuple[str, ...]:
        return tuple(case.case_id for case in self.cases if case.free)

    @property
    def decided_case_ids(self) -> tuple[str, ...]:
        return tuple(case.case_id for case in self.cases if case.decided)

    @property
    def admissible_assignments(self) -> int:
        """How many deciding rules this artifact accepts over its own cases.

        One is the only answer compatible with "the artifact decided it". The
        number is reported rather than a boolean because its size is the finding:
        P7's transport theorem accepts 2**64 of them.
        """

        return math.prod(len(case.admissible) for case in self.cases) if self.cases else 0

    def as_json(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "premise_id": self.premise.premise_id,
            "claim_ref": self.premise.claim_ref,
            "decision_obligation": self.premise.decision_obligation,
            "decided_from": list(self.premise.decided_from),
            "modelled": self.modelled,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "cases": len(self.cases),
            "free_cases": len(self.free_case_ids),
            "admissible_assignments": self.admissible_assignments,
            "exercise": self.exercise.as_json(),
        }


def case_label(point: ModelPoint) -> str:
    """A stable, readable id for one enumerated case.

    Derived from the point rather than required as a field so a caller can hand
    over a checker's own model space unchanged.
    """

    return " ".join(f"{key}={point[key]!r}" for key in sorted(point))


def _accepts(replay: AssertionReplay, assignment: Assignment) -> bool:
    """True when the replayed assertions hold under this deciding rule.

    Only ``AssertionError`` counts as a rejection. A rule that raises
    ``TypeError`` was refused by the interpreter rather than by the claim, and
    crediting that as a decision is the boundary mix-up recorded under
    ``research/failures/2026-08-digest-representation-boundary-mixup/``.
    """

    try:
        return bool(replay(assignment))
    except AssertionError:
        return False


def _pin(target_label: str, value: Hashable, baseline: Assignment) -> Assignment:
    """The baseline rule with one case's premise overridden.

    Cases are matched by :func:`case_label` rather than by identity, so a replay
    is free to rebuild its own points from the same values.
    """

    def assignment(point: ModelPoint) -> Hashable:
        return value if case_label(point) == target_label else baseline(point)

    return assignment


def measure_decision_constraint(
    premise: Premise,
    *,
    check_id: str,
    cases: Sequence[ModelPoint],
    replay: AssertionReplay,
    baseline: Assignment,
    opportunity_definition: str,
) -> DecisionConstraint:
    """Measure how much of a premise the audited assertions actually pin down.

    ``replay`` must reproduce the artifact's own assertions with the premise taken
    from a supplied rule rather than from the caller's literal, and it must accept
    ``baseline`` --- the rule the shipped artifact is consistent with. A replay
    that rejects the shipped behaviour is a transcription error, and reading a
    verdict from it would credit the instrument for catching its own bug.

    Each case is perturbed on its own, so :attr:`admissible_assignments` is exact
    only where the artifact's assertions factorise over cases. That is a property
    of the audited artifact, not something to assume:
    :func:`sample_assignments_accepted` tests it directly and should be reported
    beside any large admissible-assignment count.
    """

    axes = {key for point in cases for key in point}
    unmodelled = tuple(name for name in premise.decided_from if name not in axes)
    modelled = not unmodelled

    labels = [case_label(point) for point in cases]
    if len(set(labels)) != len(labels):
        raise ValueError(
            f"{check_id}: the enumerated cases are not distinct, so pinning one would "
            "silently pin its duplicates too"
        )

    if not cases:
        return DecisionConstraint(
            premise=premise,
            check_id=check_id,
            cases=(),
            modelled=modelled,
            exercise=GuardExercise(
                guard_id=f"{check_id}:{premise.premise_id}",
                arm_id=ENUMERATED_CASES,
                opportunities=0,
                violations=0,
                opportunity_definition=opportunity_definition,
            ),
            outcome=Outcome.CANNOT_CHECK,
            reason=DecisionReason.NO_CASES_ENUMERATED,
            detail=(
                f"{check_id} enumerates no case, so {premise.premise_id} was neither "
                "decided nor supplied; there is nothing to read a verdict from"
            ),
        )

    if not _accepts(replay, baseline):
        return DecisionConstraint(
            premise=premise,
            check_id=check_id,
            cases=(),
            modelled=modelled,
            exercise=GuardExercise(
                guard_id=f"{check_id}:{premise.premise_id}",
                arm_id=ENUMERATED_CASES,
                opportunities=0,
                violations=0,
                opportunity_definition=opportunity_definition,
            ),
            outcome=Outcome.CANNOT_CHECK,
            reason=DecisionReason.BASELINE_REJECTED,
            detail=(
                f"{check_id} rejects the baseline rule for {premise.premise_id}, which is "
                "the behaviour the shipped artifact ran; repair the replay before reading "
                "any verdict from it"
            ),
        )

    admissibilities: list[CaseAdmissibility] = []
    for point, label in zip(cases, labels):
        baseline_value = baseline(point)
        admissible = tuple(
            value
            for value in premise.domain
            if value == baseline_value or _accepts(replay, _pin(label, value, baseline))
        )
        admissibilities.append(
            CaseAdmissibility(
                case_id=label,
                baseline_value=baseline_value,
                admissible=admissible,
                domain_size=len(premise.domain),
            )
        )

    free = tuple(item for item in admissibilities if item.free)
    exercise = GuardExercise(
        guard_id=f"{check_id}:{premise.premise_id}",
        arm_id=ENUMERATED_CASES,
        opportunities=len(admissibilities),
        violations=len(free),
        opportunity_definition=opportunity_definition,
    )

    # The model-expressivity question is asked first: where the decision's inputs
    # are absent, "supplied" understates it --- no rule written here could decide
    # the premise, so there is nothing for a repair of this checker to build.
    if not modelled:
        outcome = Outcome.CANNOT_CHECK
        reason = DecisionReason.UNDECIDABLE_IN_MODEL
        detail = (
            f"{premise.premise_id} must be decided from {', '.join(premise.decided_from)}, "
            f"and {', '.join(unmodelled)} is not an axis of the {len(cases)} enumerated "
            f"cases; no rule written against this model could decide it, so {check_id}'s "
            "case count is a count of the mapping downstream of the decision"
        )
    elif free:
        outcome = Outcome.FAIL
        reason = DecisionReason.PREMISE_SUPPLIED
        admissible_rules = math.prod(len(item.admissible) for item in admissibilities)
        detail = (
            f"{len(free)} of {len(admissibilities)} cases accept every value of "
            f"{premise.premise_id}; {check_id} supplies it rather than deciding it from "
            f"{', '.join(premise.decided_from)}, which the model does carry. "
            f"{admissible_rules} deciding rules are admissible, including the constant ones"
        )
    else:
        assessment = assess_guard(exercise)
        outcome = assessment.outcome
        reason = DecisionReason.DECIDED_ON_EVERY_CASE
        detail = (
            f"every one of the {len(admissibilities)} enumerated cases excludes at least "
            f"one value of {premise.premise_id}; {assessment.detail}"
        )

    return DecisionConstraint(
        premise=premise,
        check_id=check_id,
        cases=tuple(admissibilities),
        modelled=modelled,
        exercise=exercise,
        outcome=outcome,
        reason=reason,
        detail=detail,
    )


def sample_assignments_accepted(
    premise: Premise,
    *,
    cases: Sequence[ModelPoint],
    replay: AssertionReplay,
    trials: int = 5_000,
    seed: int = 20260821,
) -> tuple[int, int]:
    """Draw whole deciding rules at random and count how many the replay accepts.

    :func:`measure_decision_constraint` perturbs one case at a time, which counts
    the admissible assignments exactly only if the artifact's assertions factorise
    over cases. Sampling whole assignments tests that directly, and it is the
    difference between "we did not find a constraint" and "there is none": a
    checker whose assertions couple cases can be free at every single point and
    still reject most joint assignments.

    Returned as ``(accepted, trials)`` rather than a ratio, for the reason
    ``GuardExercise`` carries its denominator.
    """

    if trials <= 0:
        raise ValueError(f"{premise.premise_id}: a sample of no trials establishes nothing")
    if not cases:
        return 0, trials

    generator = random.Random(seed)
    labels = [case_label(point) for point in cases]
    accepted = 0
    for _ in range(trials):
        table = {label: generator.choice(premise.domain) for label in labels}
        if _accepts(replay, lambda point: table[case_label(point)]):
            accepted += 1
    return accepted, trials


@dataclass(frozen=True)
class DecidedResult:
    """A reported quantity that refuses to exist while a premise was supplied.

    The counterpart of ``AuditedScore`` for a leaking benchmark and
    ``ProspectiveScore`` for an invertible commitment: publishing P7's "64
    transport-coordinate combinations" as support for C4 has to delete this type
    rather than forget a check.

    ``capacities`` is optional and carries the
    :class:`orion.programme.refutation_capacity.RefutationCapacity` verdicts for
    the same checks, because the two questions are independent and both must be
    answered. P7's transport check refutes every wrong theory of its terminal map
    and still blocks here.
    """

    result_id: str
    reported: tuple[tuple[str, object], ...]
    constraints: tuple[DecisionConstraint, ...]
    capacities: tuple[RefutationCapacity, ...] = ()

    def __post_init__(self) -> None:
        if not self.constraints:
            raise ValueError(
                f"{self.result_id}: a result must carry the decision constraints it was "
                "measured under; an unaudited premise blocks by construction"
            )
        blocking = [item for item in self.constraints if item.blocks]
        if blocking:
            raise UndecidedPremise(
                f"{self.result_id}: cannot report "
                f"{', '.join(name for name, _ in self.reported)} while "
                f"{', '.join(sorted(item.premise.premise_id for item in blocking))} "
                f"{'is' if len(blocking) == 1 else 'are'} not decided by the artifact"
            )
        weak = [item for item in self.capacities if item.blocks]
        if weak:
            raise UndecidedPremise(
                f"{self.result_id}: cannot report a result from "
                f"{', '.join(sorted(item.check_id for item in weak))}, which no declared "
                "false theory can fail"
            )

    def as_json(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "reported": dict(self.reported),
            "constraints": [item.as_json() for item in self.constraints],
            "capacities": [item.as_json() for item in self.capacities],
        }


def decision_outcome(constraints: Sequence[DecisionConstraint]) -> Outcome:
    """Non-compensatory roll-up over premises: any supplied premise dominates.

    An empty set blocks rather than passing, for the reason ``worst_outcome``
    refuses one: a claim nobody registered a premise for was not audited.
    """

    if not constraints:
        raise UndecidedPremise("an empty premise set cannot be rolled up; it blocks by construction")
    outcomes = {item.outcome for item in constraints}
    if Outcome.FAIL in outcomes:
        return Outcome.FAIL
    if Outcome.CANNOT_CHECK in outcomes:
        return Outcome.CANNOT_CHECK
    return Outcome.PASS


def require_decided(constraints: Sequence[DecisionConstraint], *, label: str) -> None:
    """Refuse to report a mechanized result before its own predicate was computed.

    The decision-side counterpart of ``require_operators_exercised``,
    ``require_treatment_applied`` and ``require_refutable``: it raises, naming the
    premises the artifact was handed and the premises its model cannot express,
    before any case count is read as evidence.
    """

    if decision_outcome(constraints) is Outcome.PASS:
        return

    supplied = [item for item in constraints if item.reason is DecisionReason.PREMISE_SUPPLIED]
    unaskable = [item for item in constraints if item.reason is DecisionReason.UNDECIDABLE_IN_MODEL]
    other = [
        item
        for item in constraints
        if item.blocks and item not in supplied and item not in unaskable
    ]

    parts = []
    if supplied:
        parts.append(
            f"{len(supplied)} of {len(constraints)} premises are supplied to the check "
            "rather than decided by it ("
            + ", ".join(
                f"{item.premise.premise_id} free on {len(item.free_case_ids)}/"
                f"{len(item.cases)} cases, {item.admissible_assignments} deciding rules "
                "admissible"
                for item in supplied
            )
            + ")"
        )
    if unaskable:
        parts.append(
            f"{len(unaskable)} of {len(constraints)} premises cannot be decided in this "
            "model at all ("
            + ", ".join(
                f"{item.premise.premise_id} must read "
                f"{', '.join(item.premise.decided_from)}"
                for item in unaskable
            )
            + ")"
        )
    if other:
        parts.append(
            ", ".join(f"{item.premise.premise_id}: {item.reason.value}" for item in other)
        )
    raise UndecidedPremise(f"{label}: " + "; ".join(parts))


__all__ = [
    "ENUMERATED_CASES",
    "Assignment",
    "AssertionReplay",
    "CaseAdmissibility",
    "DecidedResult",
    "DecisionConstraint",
    "DecisionReason",
    "Premise",
    "UndecidedPremise",
    "case_label",
    "decision_outcome",
    "measure_decision_constraint",
    "require_decided",
    "sample_assignments_accepted",
]
