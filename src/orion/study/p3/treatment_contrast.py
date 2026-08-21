"""Ablation verdicts that cannot report a null the ablation never produced.

An ablation reports a paired difference: the arm's rate minus the full system's
rate. When the difference is zero on every case the bootstrap returns
``0.0`` with a ``[0.0, 0.0]`` interval, and a zero-width interval reads as the
most decisive null an experiment can produce. It is the same number whether the
coordinate was stripped and the decision survived, or the coordinate was never
there to strip.

P3's ``P3.C6`` --- "necessity of every coordinate" --- is the live example, and
it is measured. ``orion.study.p3_public_reference_analysis.ablated_relation``
ablates by ``replace(projection, measurement_ids=())``. In both frozen atlases
(``gold/adjudicated/public-reference-v1`` and ``-v1.1-confirmatory``)
``measurement_ids`` and ``temporal_context_ids`` are empty on **32 of 32** cases,
so that ``replace`` is the identity, the arm compares ``compare_meaning(l, r)``
against itself, and ``ANALYSIS.json`` records::

    "remove_measurement":      {"false_merge_ablation_minus_full":
                                {"candidate_minus_baseline": 0.0,
                                 "ci95_low": 0.0, "ci95_high": 0.0}}
    "remove_temporal_context": ... identical ...

The rule under test is not the problem. A pair differing only on
``measurement_ids`` compares ``DISTINCT_MEASUREMENT``, and stripping the
coordinate flips it to ``CONTEXTUAL_DIFFERENCE``; a pair differing only on
``temporal_context_ids`` compares ``CONTEXTUAL_DIFFERENCE`` and flips to
``COMPATIBLE``. The coordinate is load-bearing in the code and absent from the
corpus, and the report cannot tell those apart.

The two arms that *did* apply a treatment are the useful contrast: on the
confirmatory atlas ``remove_referent`` altered the compared inputs on 32 of 32
cases and ``remove_construct`` on 19 of 32, and neither changed a decision. That is
a real negative --- the referent coordinate is not load-bearing on this corpus
--- and it deserves to be distinguishable from the two arms that measured
nothing. Today all four print ``0.0 [0.0, 0.0]``.

The fix is to make the treatment contrast part of the verdict. A contrast
carries how many cases the treatment actually altered, and an arm that altered
none returns :data:`~orion.programme.records.Outcome.CANNOT_CHECK`, which by
``Outcome.blocks`` stops a promotion exactly as ``FAIL`` does.

This is the independent-variable sibling of
:mod:`orion.programme.guard_exercise`: that module establishes that the outcome
*could* have varied, this one that the cause *did*. It is also the data-level
form of ``research/failures/2026-08-unreachable-operator-inert-ablation/`` ---
there the operator was unreachable, here the operator ran on all 32 cases and its
argument was already empty, so operator coverage reports it as exercised.

The module is scope-general. It knows nothing about coordinates, meaning
relations or P3; it takes two runs and returns a typed verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Hashable, Sequence

from orion.programme.records import Outcome


class InertAblation(ValueError):
    """An ablation arm's treatment left every case unchanged."""


class NecessityVerdictReason(str, Enum):
    """Why a coordinate-necessity assessment came out the way it did.

    The two ``TREATMENT_*`` reasons are the point of the module: they are the
    states a paired zero difference renders as an indistinguishable null.
    """

    COORDINATE_LOAD_BEARING = "COORDINATE_LOAD_BEARING"
    COORDINATE_NOT_LOAD_BEARING = "COORDINATE_NOT_LOAD_BEARING"
    TREATMENT_NEVER_APPLIED = "TREATMENT_NEVER_APPLIED"
    TREATMENT_TOO_SPARSE = "TREATMENT_TOO_SPARSE"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report a missing contrast, not a result."""

        return self in {
            NecessityVerdictReason.TREATMENT_NEVER_APPLIED,
            NecessityVerdictReason.TREATMENT_TOO_SPARSE,
        }


@dataclass(frozen=True)
class TreatmentContrast:
    """One ablation arm's record of what its treatment actually changed.

    ``treatment_definition`` is required and must be non-empty for the same
    reason ``GuardExercise.opportunity_definition`` is: an arm whose treatment
    cannot be stated in a sentence cannot be audited for having applied it, and
    the P3 analysis that motivated this module named its arms
    (``remove_measurement``) without ever recording what the removal did.

    ``decisions_changed`` may not exceed ``cases_treated``. A decision that
    moved on a case whose input the treatment left alone is not a weak effect;
    it means the arm read something outside the input it claims to vary, and
    every downstream difference is attributed to the wrong cause.
    """

    arm_id: str
    cases: int
    cases_treated: int
    decisions_changed: int
    treatment_definition: str

    def __post_init__(self) -> None:
        if not self.arm_id.strip():
            raise ValueError("an ablation arm id is required")
        if not self.treatment_definition.strip():
            raise ValueError(
                f"{self.arm_id}: a treatment definition is required; an arm whose "
                "treatment cannot be stated cannot be shown to have been applied"
            )
        if self.cases <= 0:
            raise ValueError(f"{self.arm_id}: an arm scored on zero cases has no contrast")
        if self.cases_treated < 0 or self.decisions_changed < 0:
            raise ValueError(f"{self.arm_id}: counts cannot be negative")
        if self.cases_treated > self.cases:
            raise ValueError(
                f"{self.arm_id}: {self.cases_treated} treated exceeds {self.cases} scored"
            )
        if self.decisions_changed > self.cases_treated:
            raise ValueError(
                f"{self.arm_id}: {self.decisions_changed} decisions changed on "
                f"{self.cases_treated} treated cases; a decision that moves on an "
                "untreated case means the arm varies something it does not declare"
            )

    @property
    def applied(self) -> bool:
        return self.cases_treated > 0

    @property
    def treatment_rate(self) -> float:
        """Share of scored cases the treatment altered. Zero means an identity arm."""

        return self.cases_treated / self.cases

    @property
    def effect_rate(self) -> float | None:
        """Decisions changed per treated case, or ``None`` when nothing was treated.

        ``None`` rather than ``0.0`` on purpose: the failure this module prevents
        is a zero standing in for an absent measurement.
        """

        if not self.applied:
            return None
        return self.decisions_changed / self.cases_treated

    @property
    def resolution(self) -> float | None:
        """Smallest non-zero effect ``cases_treated`` contrasts can express.

        A null over two treated cases and a null over two hundred are the same
        point estimate and very different evidence; the resolution is the part a
        zero-width bootstrap interval hides.
        """

        if not self.applied:
            return None
        return 1.0 / self.cases_treated

    def as_json(self) -> dict[str, Any]:
        return {
            "arm_id": self.arm_id,
            "cases": self.cases,
            "cases_treated": self.cases_treated,
            "decisions_changed": self.decisions_changed,
            "treatment_definition": self.treatment_definition,
            "applied": self.applied,
            "treatment_rate": self.treatment_rate,
            "effect_rate": self.effect_rate,
            "resolution": self.resolution,
        }


@dataclass(frozen=True)
class NecessityAssessment:
    """A three-valued verdict on "this coordinate is necessary", with its contrast."""

    arm_id: str
    outcome: Outcome
    reason: NecessityVerdictReason
    detail: str
    contrast: TreatmentContrast

    def __post_init__(self) -> None:
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.arm_id}: {self.reason.value} cannot yield PASS; "
                "that substitution is the failure this module exists to prevent"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, Any]:
        return {
            "arm_id": self.arm_id,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "contrast": self.contrast.as_json(),
        }


def contrast_from_runs(
    arm_id: str,
    *,
    control_inputs: Sequence[Hashable],
    treated_inputs: Sequence[Hashable],
    control_decisions: Sequence[Hashable],
    treated_decisions: Sequence[Hashable],
    treatment_definition: str,
) -> TreatmentContrast:
    """Measure a contrast from the two runs rather than trusting the arm's name.

    The inputs are compared, not the configuration that produced them. An arm
    called ``remove_measurement`` that removes a field which was already empty
    is indistinguishable from the full system at this boundary, and that is
    precisely the fact the arm's name asserts is false.
    """

    if len(control_inputs) != len(treated_inputs):
        raise ValueError(f"{arm_id}: control and treated runs scored different case counts")
    if len(control_decisions) != len(control_inputs):
        raise ValueError(f"{arm_id}: control decisions do not cover its inputs")
    if len(treated_decisions) != len(treated_inputs):
        raise ValueError(f"{arm_id}: treated decisions do not cover its inputs")

    treated_mask = [
        control != treated for control, treated in zip(control_inputs, treated_inputs, strict=True)
    ]
    changed = sum(
        1
        for touched, control, treated in zip(
            treated_mask, control_decisions, treated_decisions, strict=True
        )
        if touched and control != treated
    )
    untouched_but_moved = [
        index
        for index, (touched, control, treated) in enumerate(
            zip(treated_mask, control_decisions, treated_decisions, strict=True)
        )
        if not touched and control != treated
    ]
    if untouched_but_moved:
        shown = ", ".join(str(index) for index in untouched_but_moved[:5])
        raise ValueError(
            f"{arm_id}: decision moved on {len(untouched_but_moved)} case(s) whose input the "
            f"treatment did not alter (indices {shown}); the arm varies something it does "
            "not declare, so no difference it produces is attributable"
        )
    return TreatmentContrast(
        arm_id=arm_id,
        cases=len(control_inputs),
        cases_treated=sum(treated_mask),
        decisions_changed=changed,
        treatment_definition=treatment_definition,
    )


def assess_coordinate_necessity(
    contrast: TreatmentContrast, *, min_treated_cases: int = 1
) -> NecessityAssessment:
    """Assess "removing this coordinate changes the decision" on one arm.

    Three values, because there are three worlds. The coordinate was removed and
    decisions moved (``PASS`` --- necessity demonstrated). It was removed and
    nothing moved (``FAIL`` --- a real negative: not load-bearing on this
    corpus). It was never removed (``CANNOT_CHECK`` --- nothing was measured).
    The current P3 artifact prints the same ``0.0 [0.0, 0.0]`` for the last two.

    ``min_treated_cases`` is the caller's floor on how much contrast a negative
    needs before it is worth publishing as one. Below it the arm blocks rather
    than reporting a null the corpus was too thin to support.
    """

    if min_treated_cases < 1:
        raise ValueError(f"{contrast.arm_id}: a treated-case floor must be at least 1")

    if not contrast.applied:
        return NecessityAssessment(
            arm_id=contrast.arm_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=NecessityVerdictReason.TREATMENT_NEVER_APPLIED,
            detail=(
                f"{contrast.arm_id} altered 0 of {contrast.cases} cases "
                f"({contrast.treatment_definition}); the arm's inputs are identical to the "
                "full system's, so its zero difference is an absent measurement rather "
                "than evidence that the coordinate is unnecessary"
            ),
            contrast=contrast,
        )
    if contrast.cases_treated < min_treated_cases:
        return NecessityAssessment(
            arm_id=contrast.arm_id,
            outcome=Outcome.CANNOT_CHECK,
            reason=NecessityVerdictReason.TREATMENT_TOO_SPARSE,
            detail=(
                f"{contrast.arm_id} altered {contrast.cases_treated} of {contrast.cases} "
                f"cases, below the required {min_treated_cases}; the corpus does not carry "
                "enough contrast for a null to mean the coordinate is unnecessary"
            ),
            contrast=contrast,
        )
    if contrast.decisions_changed:
        return NecessityAssessment(
            arm_id=contrast.arm_id,
            outcome=Outcome.PASS,
            reason=NecessityVerdictReason.COORDINATE_LOAD_BEARING,
            detail=(
                f"{contrast.arm_id} changed {contrast.decisions_changed} of "
                f"{contrast.cases_treated} treated decisions "
                f"({contrast.treatment_definition})"
            ),
            contrast=contrast,
        )
    return NecessityAssessment(
        arm_id=contrast.arm_id,
        outcome=Outcome.FAIL,
        reason=NecessityVerdictReason.COORDINATE_NOT_LOAD_BEARING,
        detail=(
            f"{contrast.arm_id} altered {contrast.cases_treated} of {contrast.cases} cases "
            f"and changed no decision; on this corpus the coordinate is not load-bearing, "
            f"at a resolution of {contrast.resolution}"
        ),
        contrast=contrast,
    )


def require_treatment_applied(contrasts: Sequence[TreatmentContrast], *, label: str) -> None:
    """Refuse to score an ablation panel before every arm applied its treatment.

    This is the one-line precondition P1's ``require_operators_exercised`` is for
    the operator side, moved to the data side: it raises, naming the arms whose
    treatment was the identity, before any difference is computed. Running it
    against the frozen P3 atlas names ``remove_measurement`` and
    ``remove_temporal_context``.
    """

    if not contrasts:
        raise InertAblation(f"{label}: an empty ablation panel measures nothing")
    inert = [item.arm_id for item in contrasts if not item.applied]
    if inert:
        raise InertAblation(
            f"{label}: {len(inert)} of {len(contrasts)} ablation arms never altered any "
            f"case ({', '.join(sorted(inert))}); their inputs equal the full system's, so "
            "any difference reported for them is a difference of a run against itself"
        )


__all__ = [
    "InertAblation",
    "NecessityAssessment",
    "NecessityVerdictReason",
    "TreatmentContrast",
    "assess_coordinate_necessity",
    "contrast_from_runs",
    "require_treatment_applied",
]
