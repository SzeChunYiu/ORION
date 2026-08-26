"""Benchmark scores that refuse to be reported until the label is shown to be earned.

A benchmark score is a claim about a competence. It is only that claim if the
label cannot be recovered by something the competence is not. When a
judgement-free feature of the case --- how many evidence objects it carries,
which field is null, how long a string is --- separates the label, every system
that reads that feature scores well, and the panel's spread stops being a
measurement of the competence and becomes a measurement of who happened to look
at the cue.

P4 is the live example, measured both ways on the 420-case mechanical-gold
battery emitted by ``papers/orion-14-verified-scientific-discovery/host/
generate_protected_cases.py``:

- Under the V1 ``INSUFFICIENT_EVIDENCE`` construction, ``len(evidence) == 0``
  recovers all 30 ``CANNOT_CHECK`` cases with 0 false positives. All eleven
  panel systems scored ``correct_cannot_check_rate`` 1.0 and H3 was reported
  ``NOT_SUPPORTED``.
- The construction was then repaired specifically to remove that cue. Under the
  repaired V2 construction, ``len(evidence[0]["content"])`` recovers the same 30
  cases with 0 false positives --- and does so for every host seed, because the
  content templates are fixed.

The repair moved the leak; it did not close it, and nothing in the harness was
positioned to notice, because no artifact asked whether the label was
recoverable. The failure class is recorded under
``research/failures/2026-08-label-recoverable-from-construction-cue/``.

This module is the missing question, asked as a type. An audit fits declared
judgement-free probes on the split a candidate may legitimately see and scores
them on the split it may not; a probe that separates the label better than
chance makes the audit ``FAIL``, and an audit that could not be run --- no
probes, no eval cases, a constant label, a probe whose cue no case carries ---
returns :data:`~orion.programme.records.Outcome.CANNOT_CHECK`, which blocks as
``FAIL`` does. :class:`AuditedScore` then refuses at construction to carry a
number whose audit blocks, so a leaking benchmark's score cannot be reported as
a result by a later edit.

The relationship to :mod:`orion.programme.guard_exercise` is deliberate and
runs one layer further out. There, a guard's zero was uninterpretable because
its denominator was zero: the mechanism never ran. Here the denominator is
real, the mechanism ran, the arithmetic is right --- and the number still is
not about what it says it is about. :class:`AuditedGuardVerdict` joins the two:
a guard that held under genuine exercise, on a benchmark whose label leaks, is
``CANNOT_CHECK`` rather than ``PASS``.

:mod:`orion.study.p9.identifiability` is the sibling question and the reason
this module keeps the word. There, a view is non-identifying when it carries
*too little*: two worlds needing different gold collapse to one fingerprint, so
no deterministic predictor can exceed a ceiling below 1.0. Here a label is
non-identified when a competence-free slice of the view carries *too much*, and
the same majority-vote-per-fingerprint construction is used to show it. P9's
implementation is bound to ``P9StructuralWorld``, so it is cited rather than
reused; the shared idea is that what a view determines is a property of the
benchmark, measurable before any system is scored on it.

Scope-general on purpose. It knows nothing about scientific promotion, P4 or
evidence; it takes labelled cases and cue values and returns a typed verdict.
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from enum import Enum

from orion.programme.guard_exercise import GuardAssessment
from orion.programme.records import Outcome


class CueKind(str, Enum):
    """What a probe is allowed to read.

    Every member names a feature of the case's *construction* rather than of its
    content. The list is the one #652 wrote down after H3 saturated --- "evidence
    list length, missingness pattern, template, source count or other trivial
    cues" --- turned into an enumeration so that a probe must declare which kind
    of nothing it is reading.
    """

    COUNT = "COUNT"
    """How many of something the case carries."""

    FIELD_MISSINGNESS = "FIELD_MISSINGNESS"
    """Which fields are absent or null, irrespective of the values present."""

    ENUM_VALUE = "ENUM_VALUE"
    """A closed-vocabulary status field read as an opaque token."""

    STRING_SHAPE = "STRING_SHAPE"
    """Length, character class or template shape of a string, never its meaning."""

    ORDINAL_POSITION = "ORDINAL_POSITION"
    """Where the case sits in the emitted order."""

    IDENTIFIER_SHAPE = "IDENTIFIER_SHAPE"
    """Structure of an opaque id: prefix, length, separator count."""


class CaseSplit(str, Enum):
    """Which side of the custody boundary a case sits on.

    ``FIT`` is what a candidate may legitimately see before being scored;
    ``EVAL`` is what it may not. Fitting a probe on ``FIT`` and scoring it on
    ``EVAL`` asks the only question that matters: does the protected split
    actually protect anything?
    """

    FIT = "FIT"
    EVAL = "EVAL"


@dataclass(frozen=True)
class LabelledCase:
    """One benchmark case reduced to its label and its judgement-free cue values."""

    case_id: str
    label: str
    split: CaseSplit
    cues: Mapping[str, Hashable]

    def __post_init__(self) -> None:
        if not self.case_id.strip():
            raise ValueError("case id is required")
        if not self.label.strip():
            raise ValueError(f"{self.case_id}: a label is required")
        if not self.cues:
            raise ValueError(
                f"{self.case_id}: a case with no cue values cannot be probed; "
                "an audit over empty cue maps would report a clean benchmark "
                "because nothing was looked at"
            )


@dataclass(frozen=True)
class ShortcutProbe:
    """A rule that predicts the label from declared judgement-free cues alone.

    ``cue_rationale`` is required and must be non-empty for the same reason
    ``GuardExercise.opportunity_definition`` is: a probe whose cues you cannot
    argue are competence-free is not evidence of a leak, it is a second
    implementation of the task. The sentence has to say why reading these cues
    involves no judgement about the thing being measured.
    """

    probe_id: str
    kind: CueKind
    cue_names: tuple[str, ...]
    cue_rationale: str

    def __post_init__(self) -> None:
        if not self.probe_id.strip():
            raise ValueError("probe id is required")
        if not self.cue_names:
            raise ValueError(f"{self.probe_id}: a probe must name at least one cue")
        if len(set(self.cue_names)) != len(self.cue_names):
            raise ValueError(f"{self.probe_id}: cue names must be distinct")
        if not self.cue_rationale.strip():
            raise ValueError(
                f"{self.probe_id}: a rationale is required; a cue that cannot be argued "
                "to carry none of the competence is not a shortcut probe"
            )

    def signature(self, case: LabelledCase) -> tuple[Hashable, ...] | None:
        """The cue tuple for one case, or ``None`` when a named cue is absent.

        Absence is not a value. A probe that silently treated a missing cue as
        ``None`` would fold "this case has no such field" into the signature and
        so read a missingness cue it never declared.
        """

        try:
            return tuple(case.cues[name] for name in self.cue_names)
        except KeyError:
            return None


@dataclass(frozen=True)
class ProbeResult:
    """How well one probe recovered one label on the eval split.

    The headline number is :attr:`recovery` --- informedness, ``TPR + TNR - 1``
    --- and not accuracy, because benchmark labels are skewed by construction.
    On P4's protected split only 20 of 270 cases are ``CANNOT_CHECK``, so a rule
    that never predicts it is already 92.6% accurate. Informedness is 0 for every
    constant predictor and 1 only for a rule that separates the label exactly, so
    it says what accuracy on a skewed label cannot.
    """

    probe_id: str
    label: str
    fitted_signatures: int
    scored: int
    unscored: int
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    def __post_init__(self) -> None:
        counts = (
            self.fitted_signatures,
            self.scored,
            self.unscored,
            self.true_positive,
            self.false_positive,
            self.true_negative,
            self.false_negative,
        )
        if any(value < 0 for value in counts):
            raise ValueError(f"{self.probe_id}: probe counts cannot be negative")
        confusion = (
            self.true_positive + self.false_positive + self.true_negative + self.false_negative
        )
        if confusion != self.scored:
            raise ValueError(
                f"{self.probe_id}: confusion matrix totals {confusion} over {self.scored} "
                "scored cases; a case that was scored has an outcome"
            )

    @property
    def positives(self) -> int:
        return self.true_positive + self.false_negative

    @property
    def negatives(self) -> int:
        return self.true_negative + self.false_positive

    @property
    def recovery(self) -> float | None:
        """Informedness on the eval split, or ``None`` when it is undefined.

        ``None`` rather than ``0.0``: a probe with no positives or no negatives
        to separate has not been shown clean, and the whole point of the module
        is that an absent measurement must not read as a passing one.
        """

        if self.positives == 0 or self.negatives == 0:
            return None
        return self.true_positive / self.positives + self.true_negative / self.negatives - 1.0

    @property
    def resolution(self) -> float | None:
        """Finest non-zero informedness this eval split can express."""

        if self.positives == 0 or self.negatives == 0:
            return None
        return min(1.0 / self.positives, 1.0 / self.negatives)

    def as_json(self) -> dict[str, object]:
        return {
            "probe_id": self.probe_id,
            "label": self.label,
            "fitted_signatures": self.fitted_signatures,
            "scored": self.scored,
            "unscored": self.unscored,
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "true_negative": self.true_negative,
            "false_negative": self.false_negative,
            "recovery": self.recovery,
            "resolution": self.resolution,
        }


class IdentifiabilityReason(str, Enum):
    """Why an audit came out the way it did.

    The ``is_vacuity`` members are the ones that matter: each is a way for an
    audit to look clean while having established nothing. An audit with no
    probes, an audit with nothing to score, and an audit of a label that never
    varies all report zero recovered labels, and so all three would read as
    "no leak found" if the verdict were a boolean.
    """

    NO_CUE_RECOVERED_LABEL = "NO_CUE_RECOVERED_LABEL"
    LABEL_RECOVERED_BY_CUE = "LABEL_RECOVERED_BY_CUE"
    NO_PROBE_REGISTERED = "NO_PROBE_REGISTERED"
    NO_EVAL_CASES = "NO_EVAL_CASES"
    NO_FIT_CASES = "NO_FIT_CASES"
    LABEL_CONSTANT_ON_EVAL = "LABEL_CONSTANT_ON_EVAL"
    NO_PROBE_SCORED = "NO_PROBE_SCORED"
    TOLERANCE_FINER_THAN_RESOLUTION = "TOLERANCE_FINER_THAN_RESOLUTION"

    @property
    def is_vacuity(self) -> bool:
        """True for the reasons that report a missing audit, not a clean one."""

        return self in {
            IdentifiabilityReason.NO_PROBE_REGISTERED,
            IdentifiabilityReason.NO_EVAL_CASES,
            IdentifiabilityReason.NO_FIT_CASES,
            IdentifiabilityReason.LABEL_CONSTANT_ON_EVAL,
            IdentifiabilityReason.NO_PROBE_SCORED,
            IdentifiabilityReason.TOLERANCE_FINER_THAN_RESOLUTION,
        }


@dataclass(frozen=True)
class IdentifiabilityAudit:
    """A three-valued verdict on whether a label is recoverable without the competence."""

    benchmark_id: str
    label: str
    outcome: Outcome
    reason: IdentifiabilityReason
    detail: str
    results: tuple[ProbeResult, ...]

    def __post_init__(self) -> None:
        if not self.benchmark_id.strip():
            raise ValueError("benchmark id is required")
        if self.outcome is Outcome.PASS and self.reason.is_vacuity:
            raise ValueError(
                f"{self.benchmark_id}/{self.label}: {self.reason.value} cannot yield PASS; "
                "an audit that could not run is not an audit that found nothing"
            )
        if self.outcome is Outcome.PASS and not self.results:
            raise ValueError(
                f"{self.benchmark_id}/{self.label}: a passing audit must carry the probe "
                "results it passed on"
            )

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    @property
    def worst_recovery(self) -> float | None:
        recoveries = [item.recovery for item in self.results if item.recovery is not None]
        return max(recoveries) if recoveries else None

    def as_json(self) -> dict[str, object]:
        return {
            "benchmark_id": self.benchmark_id,
            "label": self.label,
            "outcome": self.outcome.value,
            "reason": self.reason.value,
            "detail": self.detail,
            "worst_recovery": self.worst_recovery,
            "results": [item.as_json() for item in self.results],
        }


def score_probe(
    probe: ShortcutProbe, cases: Iterable[LabelledCase], *, label: str
) -> ProbeResult:
    """Fit ``probe`` on the FIT split and score it one-vs-rest on the EVAL split.

    The fit is a lookup from cue signature to the majority label seen with that
    signature. Nothing more expressive is needed or wanted: the claim being
    tested is that the label falls out of the construction, and a lookup table
    is the weakest rule that can demonstrate it. A stronger learner that found a
    leak would leave open whether the leak or the learner did the work.

    Signatures unseen during fitting are counted as ``unscored`` rather than
    predicted, so a probe cannot earn credit on the eval split for a pattern the
    fit split never showed it.
    """

    materialised = tuple(cases)
    tally: dict[tuple[Hashable, ...], dict[str, int]] = {}
    for case in materialised:
        if case.split is not CaseSplit.FIT:
            continue
        signature = probe.signature(case)
        if signature is None:
            continue
        counts = tally.setdefault(signature, {})
        counts[case.label] = counts.get(case.label, 0) + 1

    # Ties resolve on the label name so a probe's verdict does not depend on
    # case ordering; an audit whose result moved with the manifest's shuffle
    # would be unreproducible in exactly the way a frozen battery forbids.
    rule = {
        signature: max(counts, key=lambda name: (counts[name], name))
        for signature, counts in tally.items()
    }

    tp = fp = tn = fn = unscored = 0
    for case in materialised:
        if case.split is not CaseSplit.EVAL:
            continue
        signature = probe.signature(case)
        predicted = rule.get(signature) if signature is not None else None
        if predicted is None:
            unscored += 1
            continue
        actual_positive = case.label == label
        predicted_positive = predicted == label
        if predicted_positive and actual_positive:
            tp += 1
        elif predicted_positive:
            fp += 1
        elif actual_positive:
            fn += 1
        else:
            tn += 1

    return ProbeResult(
        probe_id=probe.probe_id,
        label=label,
        fitted_signatures=len(rule),
        scored=tp + fp + tn + fn,
        unscored=unscored,
        true_positive=tp,
        false_positive=fp,
        true_negative=tn,
        false_negative=fn,
    )


def audit_label_identifiability(
    *,
    benchmark_id: str,
    label: str,
    cases: Iterable[LabelledCase],
    probes: Iterable[ShortcutProbe],
    max_recovery: float = 0.0,
) -> IdentifiabilityAudit:
    """Audit whether ``label`` survives every declared judgement-free probe.

    ``max_recovery`` is a ceiling on informedness. The default of 0.0 is the
    strict reading and the right one for a mechanical-gold battery: no
    competence-free cue may separate the label at all, and any probe that does
    is reporting that the score measures the cue. A ceiling finer than the eval
    split can express returns ``CANNOT_CHECK`` rather than a pass, for the same
    reason ``assess_guard`` does: every observable value would either satisfy it
    trivially or overshoot it by a whole unit.
    """

    if not 0.0 <= max_recovery <= 1.0:
        raise ValueError(f"{benchmark_id}: an informedness ceiling must lie in [0, 1]")

    materialised = tuple(cases)
    registered = tuple(probes)
    if not registered:
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.CANNOT_CHECK,
            reason=IdentifiabilityReason.NO_PROBE_REGISTERED,
            detail=(
                f"no shortcut probe was registered for {benchmark_id}/{label}; an audit "
                "with nothing to run reports no leak because nobody looked"
            ),
            results=(),
        )

    fit = [case for case in materialised if case.split is CaseSplit.FIT]
    evaluation = [case for case in materialised if case.split is CaseSplit.EVAL]
    if not fit:
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.CANNOT_CHECK,
            reason=IdentifiabilityReason.NO_FIT_CASES,
            detail=(
                f"{benchmark_id}/{label}: no case is on the FIT split, so every probe "
                "fits an empty rule and scores nothing"
            ),
            results=(),
        )
    if not evaluation:
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.CANNOT_CHECK,
            reason=IdentifiabilityReason.NO_EVAL_CASES,
            detail=(
                f"{benchmark_id}/{label}: no case is on the EVAL split; a probe with "
                "nothing to score recovers zero labels for the same reason an unpressed "
                "guard reports zero violations"
            ),
            results=(),
        )

    observed = {case.label for case in evaluation}
    if len(observed) < 2:
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.CANNOT_CHECK,
            reason=IdentifiabilityReason.LABEL_CONSTANT_ON_EVAL,
            detail=(
                f"{benchmark_id}/{label}: every eval case carries {sorted(observed)[0]!r}, "
                "so no probe can be told apart from a constant predictor and the score "
                "computed on this split has no resolving power either"
            ),
            results=(),
        )

    results = tuple(score_probe(probe, materialised, label=label) for probe in registered)
    inert = [item.probe_id for item in results if item.recovery is None]
    if inert:
        # Any inert probe, not only an all-inert set. A probe that could not be
        # scored contributes a silent nothing to the roll-up, which is the P1
        # failure --- an unreachable path counted as a comparison --- reproduced
        # inside the instrument built to catch it.
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.CANNOT_CHECK,
            reason=IdentifiabilityReason.NO_PROBE_SCORED,
            detail=(
                f"{benchmark_id}/{label}: {', '.join(sorted(inert))} produced no positive "
                "or no negative on the eval split; a probe that could not run recovers "
                "zero labels for the same reason an unpressed guard reports zero violations"
            ),
            results=results,
        )

    resolution = min(item.resolution for item in results if item.resolution is not None)
    if 0.0 < max_recovery < resolution:
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.CANNOT_CHECK,
            reason=IdentifiabilityReason.TOLERANCE_FINER_THAN_RESOLUTION,
            detail=(
                f"{benchmark_id}/{label}: a ceiling of {max_recovery} is finer than the "
                f"{resolution} resolution of this eval split; satisfying it is not "
                "distinguishable from observing no leak"
            ),
            results=results,
        )

    leaking = [
        item for item in results if item.recovery is not None and item.recovery > max_recovery
    ]
    if leaking:
        worst = max(leaking, key=lambda item: item.recovery or 0.0)
        return IdentifiabilityAudit(
            benchmark_id=benchmark_id,
            label=label,
            outcome=Outcome.FAIL,
            reason=IdentifiabilityReason.LABEL_RECOVERED_BY_CUE,
            detail=(
                f"{benchmark_id}/{label}: probe {worst.probe_id} recovers the label at "
                f"informedness {worst.recovery} ({worst.true_positive}/{worst.positives} "
                f"of the label, {worst.false_positive} false positives over "
                f"{worst.negatives}) from cues that carry none of the competence"
            ),
            results=results,
        )

    return IdentifiabilityAudit(
        benchmark_id=benchmark_id,
        label=label,
        outcome=Outcome.PASS,
        reason=IdentifiabilityReason.NO_CUE_RECOVERED_LABEL,
        detail=(
            f"{benchmark_id}/{label}: {len(results)} probes scored on "
            f"{len(evaluation)} eval cases; best informedness "
            f"{max(item.recovery for item in results if item.recovery is not None)} "
            f"is within the {max_recovery} ceiling"
        ),
        results=results,
    )


@dataclass(frozen=True)
class AuditedScore:
    """A benchmark score that cannot exist without a passing identifiability audit.

    This is the mechanism, not the report. A score whose audit blocks is not a
    weaker result to be caveated in a limitations paragraph; it is a number that
    has not been shown to be about its subject, and the class refuses to hold
    one. Reporting it therefore requires deleting this type rather than
    forgetting a check.
    """

    score_name: str
    value: float
    audit: IdentifiabilityAudit

    def __post_init__(self) -> None:
        if not self.score_name.strip():
            raise ValueError("score name is required")
        if self.audit.blocks:
            raise ValueError(
                f"{self.score_name}: identifiability audit for "
                f"{self.audit.benchmark_id}/{self.audit.label} returned "
                f"{self.audit.outcome.value} ({self.audit.reason.value}); "
                f"{self.audit.detail}"
            )

    def as_json(self) -> dict[str, object]:
        return {
            "score_name": self.score_name,
            "value": self.value,
            "audit": self.audit.as_json(),
        }


@dataclass(frozen=True)
class AuditedGuardVerdict:
    """A guard verdict read together with the audit of the benchmark it ran on.

    ``GuardAssessment`` already refuses to call an unexercised guard a pass. This
    is the next question, and it is the one P4 raises: the guard *was* exercised,
    on a real denominator, and held --- but on cases whose label a character
    count recovers. ORION's 0 false promotions in 360 opportunities is a genuine
    ``PASS`` by exercise and still not evidence of the competence while the
    battery leaks, so the joined outcome is ``CANNOT_CHECK``.
    """

    guard: GuardAssessment
    audit: IdentifiabilityAudit

    def __post_init__(self) -> None:
        if self.outcome is Outcome.PASS and self.audit.blocks:
            raise ValueError(
                f"{self.guard.guard_id}: a guard cannot pass on a benchmark whose "
                f"{self.audit.label} label audit returned {self.audit.outcome.value}"
            )

    @property
    def outcome(self) -> Outcome:
        """``FAIL`` still dominates: a demonstrated violation outranks a missing audit.

        A guard that failed on a leaking benchmark failed --- the leak would only
        have made passing easier. A guard that *passed* on one has established
        nothing, so the audit's block governs.
        """

        if self.guard.outcome is Outcome.FAIL:
            return Outcome.FAIL
        if self.audit.blocks:
            return Outcome.CANNOT_CHECK
        return self.guard.outcome

    @property
    def blocks(self) -> bool:
        return self.outcome.blocks

    def as_json(self) -> dict[str, object]:
        return {
            "outcome": self.outcome.value,
            "guard": self.guard.as_json(),
            "audit": self.audit.as_json(),
        }


def require_identified(audit: IdentifiabilityAudit) -> None:
    """Raise unless ``audit`` passed. One line, before any score is quoted."""

    if audit.blocks:
        raise ValueError(
            f"{audit.benchmark_id}/{audit.label}: {audit.outcome.value} "
            f"({audit.reason.value}) --- {audit.detail}"
        )


__all__ = [
    "AuditedGuardVerdict",
    "AuditedScore",
    "CaseSplit",
    "CueKind",
    "IdentifiabilityAudit",
    "IdentifiabilityReason",
    "LabelledCase",
    "ProbeResult",
    "ShortcutProbe",
    "audit_label_identifiability",
    "require_identified",
    "score_probe",
]
