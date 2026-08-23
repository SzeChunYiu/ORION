"""Receipts whose verdict cannot be a word the run had no way of withholding.

An artifact reports a measurement and a verdict, and a reader takes the verdict.
Those two are the same pair in two entirely different worlds: the verdict was
computed from the measurement and came out favourable, and the verdict was
written into the emitter's source text beside a measurement it never reads. The
receipt cannot tell them apart, because a constant and a computed value look
identical once serialized.

P8 is the live example, measured both ways.
``research/extensions/p8-method-authority/run_anti_laundering_bench.py`` built
its summary as

.. code-block:: python

    out = {..., 'illicit_coercion_block_rate': sum(r['pass'] for r in attacks)/len(attacks),
           ..., 'terminal': 'P8_P9_P10_ANTI_LAUNDERING_CLEAR',
           'claim_ceiling': panel['claim_ceiling']}

Four rates are computed. The terminal was a literal, and the claim ceiling was
the input echoed back. Replacing the authority mechanism with one that launders
every capability into every authority coordinate drops
``illicit_coercion_block_rate`` from 1.0 to 0.0 --- all seven named attack cases
flip from ``BLOCKED`` to ``SUPPORTED`` --- and the emitted terminal was still
``P8_P9_P10_ANTI_LAUNDERING_CLEAR``. Inverting every expectation in the frozen
panel puts all four rates at 0.0, and the terminal did not move. Over every
input tried, the number of distinct terminals the emitter could produce was one.

That bench derives its terminal from the four rates as of 2026-08-21, so the
register below now moves it and the responsiveness leg passes; the measurement is
what established that, and the ceiling half of the receipt is still an input
echo. The failure class is recorded under
``research/failures/2026-08-unconditional-terminal-self-issued-authority/``.

This is not the failure :mod:`orion.programme.refutation_capacity` catches, and
that module's instrument does not see it. There the *predicate* was a tautology,
so the verdict could not vary because nothing could satisfy its false branch.
Here the measurement varies across its whole range --- 1.0 to 0.0 on four
independent rates --- and the verdict still does not, because the verdict is not
downstream of the measurement at all. A check with no falsifier at least has a
check; this has a string.

The fix is to make responsiveness part of the verdict's type. The emitter is run
against a register of **withholding cases** --- inputs a reader can read and
agree must not earn the baseline verdict --- and the verdict is three-valued:

* some case moved the verdict and none failed to: the verdict is a function of
  something, :data:`~orion.programme.records.Outcome.PASS`;
* a case moved the receipt's own evidence and left the verdict where it was:
  :data:`~orion.programme.records.Outcome.FAIL`, and the offending cases are
  named;
* nothing in the register perturbed the receipt at all:
  :data:`~orion.programme.records.Outcome.CANNOT_CHECK`, which by
  ``Outcome.blocks`` stops a promotion exactly as ``FAIL`` does.

Two constraints carry most of the weight.

A case only counts if the receipt actually changed somewhere. A payload that
leaves every traced field where it was is
:class:`orion.study.p3.treatment_contrast.TreatmentContrast`'s unapplied
treatment: the emitter was re-run, not perturbed, and crediting the unmoved
verdict against it would score the instrument on a no-op. Such cases are
excluded from the denominator and reported, exactly as
:func:`~orion.programme.refutation_capacity.measure_refutation_capacity`
excludes theories that never diverge.

The damning subset is separated out. A case where *only* the verdict stayed put
while the receipt's own rates moved is stronger evidence than a case where
nothing much happened, because it shows the emitter holding a number and a word
that contradict each other in the same object.

The second half of the module is about the bound rather than the verdict. A
``claim_ceiling`` copied from the input is a limit the subject of the receipt
writes for itself, and a ceiling nobody but the claimant can lower is not a
ceiling. :func:`measure_declared_bound` injects an overreaching bound into the
input and reports whether the receipt repeats it.

The verdict is built from :class:`orion.programme.guard_exercise.GuardExercise`
rather than beside it: the opportunities are the live withholding cases and the
violations are the ones the verdict ignored, so "nobody proposed an input that
should have been refused" and "the guard was never pressed" are the same state
with the same answer.

Scope-general on purpose. It knows nothing about authority, laundering or P8; it
takes an emitter, a baseline input and a register of inputs that should have
come out differently, and returns a typed verdict.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Hashable, Iterator, Mapping, Sequence

from orion.programme.guard_exercise import GuardAssessment, GuardExercise, assess_guard
from orion.programme.records import Outcome

#: An artifact's emitter: the callable that turns one input into one receipt.
#:
#: The real shipped function, not a re-implementation. A responsiveness measured
#: against a paraphrase of the emitter is a statement about the paraphrase, which
#: is the mistake ``research/failures/
#: 2026-08-unfalsifiable-check-zero-refutation-capacity/`` records about a second
#: implementation that could not disagree with the first.
Emitter = Callable[[Any], Mapping[str, object]]

#: The arm label every responsiveness exercise carries. There is only one arm ---
#: a receipt is not compared against a comparator receipt --- but
#: ``GuardExercise`` requires the field, and naming it keeps the JSON readable.
DECLARED_WITHHOLDING_CASES = "declared-withholding-cases"


class SelfIssuedAuthority(ValueError):
    """Raised when a receipt's verdict or bound is read before the run could set it."""


@dataclass(frozen=True)
class WithholdingCase:
    """An input a reader can read and agree must not earn the baseline verdict.

    ``withholds`` is required and must be non-empty for the same reason
    ``GuardExercise.opportunity_definition`` is: a perturbation whose grounds
    cannot be stated in a sentence is a fuzz input, not a falsifier, and the
    register is the artifact a reviewer actually audits.
    """

    case_id: str
    withholds: str
    payload: Any

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("a withholding case id is required")
        if not self.withholds.strip():
            raise ValueError(
                f"{self.case_id}: state why this input must not earn the baseline verdict; "
                "an unexplained perturbation proves nothing by being survived"
            )


@dataclass(frozen=True)
class CaseResponse:
    """What one withholding case did to the receipt."""

    case_id: str
    verdict: Hashable
    verdict_moved: bool
    evidence_moved: tuple[str, ...]

    @property
    def inert(self) -> bool:
        """True when the receipt is byte-identical on every traced field.

        Not a survivor and not a refutation: the emitter was re-run rather than
        perturbed, so this case has no bearing on whether the verdict responds.
        """

        return not self.verdict_moved and not self.evidence_moved

    @property
    def contradicted(self) -> bool:
        """True when the receipt's own evidence moved and its verdict did not."""

        return bool(self.evidence_moved) and not self.verdict_moved

    def as_json(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "verdict": self.verdict,
            "verdict_moved": self.verdict_moved,
            "evidence_moved": list(self.evidence_moved),
            "inert": self.inert,
            "contradicted": self.contradicted,
        }


@dataclass(frozen=True)
class ReceiptResponsiveness:
    """A three-valued verdict on "this receipt's verdict is a function of its run"."""

    label: str
    verdict_field: str
    baseline_verdict: Hashable
    responses: tuple[CaseResponse, ...]
    exercise: GuardExercise
    assessment: GuardAssessment

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("a responsiveness label is required")

    @property
    def outcome(self) -> Outcome:
        return self.assessment.outcome

    @property
    def blocks(self) -> bool:
        return self.assessment.blocks

    @property
    def inert_cases(self) -> tuple[str, ...]:
        return tuple(item.case_id for item in self.responses if item.inert)

    @property
    def unmoved(self) -> tuple[str, ...]:
        """Live cases the verdict ignored --- the violations of the exercise."""

        return tuple(
            item.case_id for item in self.responses if not item.inert and not item.verdict_moved
        )

    @property
    def contradicted(self) -> tuple[str, ...]:
        """Cases where the receipt's own evidence moved and its verdict did not.

        The subset worth quoting: it is the one state in which the artifact
        publishes a number and a word that disagree about the same run.
        """

        return tuple(item.case_id for item in self.responses if item.contradicted)

    @property
    def verdicts_observed(self) -> tuple[Hashable, ...]:
        """Every distinct verdict the emitter produced, baseline included.

        A length of one is the headline: over the whole register the artifact has
        exactly one thing it can say.
        """

        seen: list[Hashable] = [self.baseline_verdict]
        for item in self.responses:
            if item.verdict not in seen:
                seen.append(item.verdict)
        return tuple(seen)

    def as_json(self) -> dict[str, object]:
        return {
            "label": self.label,
            "verdict_field": self.verdict_field,
            "baseline_verdict": self.baseline_verdict,
            "verdicts_observed": list(self.verdicts_observed),
            "inert_cases": list(self.inert_cases),
            "unmoved": list(self.unmoved),
            "contradicted": list(self.contradicted),
            "responses": [item.as_json() for item in self.responses],
            "assessment": self.assessment.as_json(),
        }


def _traced(receipt: Mapping[str, object], field: str, *, label: str, origin: str) -> Hashable:
    """Read one traced field, refusing anything a change cannot be read off."""

    if field not in receipt:
        raise ValueError(f"{label}: {origin} receipt has no field {field!r}")
    value = receipt[field]
    try:
        hash(value)
    except TypeError as error:  # a nested structure's "moved" is not a verdict change
        raise ValueError(
            f"{label}: field {field!r} is {type(value).__name__}; trace scalar verdicts and "
            "rates, not the row list they are computed from"
        ) from error
    return value  # type: ignore[return-value]


def measure_receipt_responsiveness(
    emit: Emitter,
    *,
    label: str,
    baseline: Any,
    verdict_field: str,
    evidence_fields: Sequence[str],
    cases: Sequence[WithholdingCase],
) -> ReceiptResponsiveness:
    """Measure whether any declared withholding case would have moved the verdict.

    ``evidence_fields`` are the receipt's own measured quantities. They are not
    part of the verdict; they are what distinguishes an emitter that was never
    perturbed from one that was perturbed and did not care.
    """

    if not label.strip():
        raise ValueError("a responsiveness label is required")
    if not verdict_field.strip():
        raise ValueError(f"{label}: a verdict field is required")
    traced = tuple(evidence_fields)
    if len(set(traced)) != len(traced):
        raise ValueError(f"{label}: evidence field names must be distinct")
    if verdict_field in traced:
        raise ValueError(
            f"{label}: {verdict_field!r} cannot be its own evidence; the point of the "
            "measurement is whether the verdict tracks something other than itself"
        )
    ids = [case.case_id for case in cases]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label}: withholding case ids must be distinct")

    base_receipt = emit(baseline)
    base_verdict = _traced(base_receipt, verdict_field, label=label, origin="baseline")
    base_evidence = {
        field: _traced(base_receipt, field, label=label, origin="baseline") for field in traced
    }

    responses: list[CaseResponse] = []
    for case in cases:
        receipt = emit(case.payload)
        verdict = _traced(receipt, verdict_field, label=label, origin=case.case_id)
        moved = tuple(
            field
            for field in traced
            if _traced(receipt, field, label=label, origin=case.case_id) != base_evidence[field]
        )
        responses.append(
            CaseResponse(
                case_id=case.case_id,
                verdict=verdict,
                verdict_moved=verdict != base_verdict,
                evidence_moved=moved,
            )
        )

    live = tuple(item for item in responses if not item.inert)
    exercise = GuardExercise(
        guard_id=label,
        arm_id=DECLARED_WITHHOLDING_CASES,
        opportunities=len(live),
        violations=sum(1 for item in live if not item.verdict_moved),
        opportunity_definition=(
            f"registered inputs that must not earn {base_verdict!r} and that move at least "
            f"one of {len(traced)} traced quantities of the {verdict_field!r} receipt"
        ),
    )
    return ReceiptResponsiveness(
        label=label,
        verdict_field=verdict_field,
        baseline_verdict=base_verdict,
        responses=tuple(responses),
        exercise=exercise,
        assessment=assess_guard(exercise),
    )


@dataclass(frozen=True)
class DeclaredBound:
    """Whether a receipt's stated limit is one its subject supplied.

    P8's summaries carry ``claim_ceiling``, and every one of them is
    ``panel['claim_ceiling']`` copied through. A bound the claimant writes is a
    sentence about intent; the reader has no way to tell it from a bound the run
    established, because both arrive as a string in the same field.
    """

    label: str
    field: str
    injected: Hashable
    emitted: Hashable

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("a declared-bound label is required")
        if not self.field.strip():
            raise ValueError(f"{self.label}: a bound field is required")

    @property
    def subject_controlled(self) -> bool:
        return self.emitted == self.injected

    @property
    def outcome(self) -> Outcome:
        return Outcome.FAIL if self.subject_controlled else Outcome.PASS

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, object]:
        return {
            "label": self.label,
            "field": self.field,
            "injected": self.injected,
            "emitted": self.emitted,
            "subject_controlled": self.subject_controlled,
            "outcome": self.outcome.value,
        }


def measure_declared_bound(
    emit: Emitter,
    *,
    label: str,
    field: str,
    overreaching_payload: Any,
    overreaching_bound: Hashable,
) -> DeclaredBound:
    """Inject a bound the artifact has no right to and see whether it repeats it.

    ``overreaching_bound`` must be something a reader would refuse on sight, so
    that repeating it is unambiguous. Passing a bound the artifact could
    legitimately have earned turns the measurement into a coin flip.
    """

    receipt = emit(overreaching_payload)
    emitted = _traced(receipt, field, label=label, origin="overreaching")
    return DeclaredBound(
        label=label, field=field, injected=overreaching_bound, emitted=emitted
    )


def require_responsive(response: ReceiptResponsiveness) -> None:
    """Refuse to quote a verdict before some input could have changed it."""

    if not response.blocks:
        return
    detail = response.assessment.detail
    if response.contradicted:
        detail = (
            f"{detail}; the receipt's own evidence moved and {response.verdict_field!r} did "
            f"not on: {', '.join(response.contradicted)}"
        )
    raise SelfIssuedAuthority(
        f"{response.label}: {response.outcome.value} "
        f"({response.assessment.reason.value}) --- {detail}"
    )


def require_earned(bound: DeclaredBound) -> None:
    """Refuse to quote a limit the artifact's own input supplied."""

    if not bound.blocks:
        return
    raise SelfIssuedAuthority(
        f"{bound.label}: {bound.outcome.value} --- {bound.field!r} echoed the injected "
        f"bound {bound.injected!r}; the subject of the receipt chose its own ceiling"
    )


@contextmanager
def overridden(module: Any, **attributes: Any) -> Iterator[None]:
    """Swap module-level attributes for the duration of one emitter call.

    Breaking the mechanism and leaving the panel alone is the measurement that
    matters --- a benchmark can be reworded, a shipped rule cannot --- and the
    only way to reach a rule bound at import time is its module. Restoration is
    unconditional so a raising emitter cannot leave the mutation behind.
    """

    previous = {name: getattr(module, name) for name in attributes}
    for name, value in attributes.items():
        setattr(module, name, value)
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(module, name, value)


__all__ = [
    "DECLARED_WITHHOLDING_CASES",
    "CaseResponse",
    "DeclaredBound",
    "Emitter",
    "ReceiptResponsiveness",
    "SelfIssuedAuthority",
    "WithholdingCase",
    "measure_declared_bound",
    "measure_receipt_responsiveness",
    "overridden",
    "require_earned",
    "require_responsive",
]
