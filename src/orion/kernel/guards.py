from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from orion.experience.model import FailurePatternCandidate, LessonAuthority
from orion.mechanics.model import MechanicDimension
from orion.mechanics.questioning import MechanicQuestion

from .gate import AnswerAuthority, AnswerGrading, CheckOutcome

_EVIDENCE_PREFIX = "evidence:"
_CHECK_PREFIX = "check:"
_DIMENSION_PREFIX = "dimension:"


class GuardEffect(str, Enum):
    """What a promoted guard actually does to the next round.

    Every effect is executed by the scheduler or the gate. A guard that only
    described itself would repeat the defect it was learned from: an attested
    guard that never runs.
    """

    REJECT_EVIDENCE_STATUS = "REJECT_EVIDENCE_STATUS"
    REQUIRE_CHECK_FOR_DIMENSION = "REQUIRE_CHECK_FOR_DIMENSION"
    DEPRIORITIZE_DIMENSION = "DEPRIORITIZE_DIMENSION"


@dataclass(frozen=True)
class GuardRule:
    """An executable consequence of a repeated, structurally identical failure."""

    guard_id: str
    pattern_id: str
    effect: GuardEffect
    argument: str
    authority: LessonAuthority
    rationale: str

    def __post_init__(self) -> None:
        if not self.guard_id.strip() or not self.argument.strip():
            raise ValueError("guard identity and argument are required")

    @property
    def active(self) -> bool:
        """Only guards that survived the experience-ledger gate may change behavior."""

        return self.authority is not LessonAuthority.CANDIDATE


def structural_grading_signature(grading: AnswerGrading) -> tuple[str, ...]:
    """Reduce a refusal to its reusable shape, dropping instance-specific values.

    The core signature is what `propose_failure_pattern` intersects across
    failures, so it must contain the *class* of failure and not the particular
    record or reference that triggered it.
    """

    tokens: list[str] = [f"{_DIMENSION_PREFIX}{grading.dimension.value}"]
    for resolution in grading.evidence:
        if not resolution.resolved:
            tokens.append(f"{_EVIDENCE_PREFIX}{resolution.status.value}")
    if not grading.evidence:
        tokens.append(f"{_EVIDENCE_PREFIX}ABSENT")
    if grading.check_outcome is not None and grading.check_outcome is not CheckOutcome.PASSED:
        tokens.append(f"{_CHECK_PREFIX}{grading.check_outcome.value}")
    return tuple(sorted(dict.fromkeys(tokens)))


def variation_grading_signature(grading: AnswerGrading) -> tuple[str, ...]:
    """Keep the instance-specific detail that distinguishes one failure from another."""

    tokens = [f"record:{grading.record_id}", f"mechanic:{grading.mechanic_id}"]
    tokens.extend(f"ref:{item.ref}" for item in grading.evidence if not item.resolved)
    return tuple(sorted(dict.fromkeys(tokens)))


def derive_guard_rule(
    candidate: FailurePatternCandidate, *, authority: LessonAuthority
) -> GuardRule | None:
    """Translate a candidate failure pattern into one executable rule.

    Derivation is mechanical because the core signature is a controlled
    vocabulary emitted by `structural_grading_signature`, not free text.
    """

    core = candidate.core_failure_signature
    evidence_statuses = [
        token[len(_EVIDENCE_PREFIX) :]
        for token in core
        if token.startswith(_EVIDENCE_PREFIX)
    ]
    check_outcomes = [
        token[len(_CHECK_PREFIX) :] for token in core if token.startswith(_CHECK_PREFIX)
    ]
    dimensions = [
        token[len(_DIMENSION_PREFIX) :]
        for token in core
        if token.startswith(_DIMENSION_PREFIX)
    ]
    if evidence_statuses:
        status = sorted(evidence_statuses)[0]
        return GuardRule(
            guard_id=f"guard:{candidate.pattern_id}",
            pattern_id=candidate.pattern_id,
            effect=GuardEffect.REJECT_EVIDENCE_STATUS,
            argument=status,
            authority=authority,
            rationale=f"repeated answers failed evidence resolution with status {status}",
        )
    if check_outcomes and dimensions:
        return GuardRule(
            guard_id=f"guard:{candidate.pattern_id}",
            pattern_id=candidate.pattern_id,
            effect=GuardEffect.REQUIRE_CHECK_FOR_DIMENSION,
            argument=sorted(dimensions)[0],
            authority=authority,
            rationale=(
                "repeated answers for this dimension could not be verified by a "
                f"discriminating check ({sorted(check_outcomes)[0]})"
            ),
        )
    if dimensions:
        return GuardRule(
            guard_id=f"guard:{candidate.pattern_id}",
            pattern_id=candidate.pattern_id,
            effect=GuardEffect.DEPRIORITIZE_DIMENSION,
            argument=sorted(dimensions)[0],
            authority=authority,
            rationale="this dimension repeatedly consumed a round without closing",
        )
    return None


def guard_refusals(
    grading: AnswerGrading, guards: tuple[GuardRule, ...]
) -> tuple[str, ...]:
    """Return the guard-issued reasons this answer must not be applied."""

    reasons: list[str] = []
    for guard in guards:
        if not guard.active:
            continue
        if guard.effect is GuardEffect.REJECT_EVIDENCE_STATUS:
            if any(
                not item.resolved and item.status.value == guard.argument
                for item in grading.evidence
            ):
                reasons.append(f"{guard.guard_id}:evidence_status_{guard.argument}")
        elif guard.effect is GuardEffect.REQUIRE_CHECK_FOR_DIMENSION:
            if (
                grading.dimension.value == guard.argument
                and grading.authority is not AnswerAuthority.VERIFIED
            ):
                reasons.append(f"{guard.guard_id}:verification_required")
    return tuple(reasons)


def apply_selection_guards(
    questions: tuple[MechanicQuestion, ...], guards: tuple[GuardRule, ...]
) -> tuple[MechanicQuestion, ...]:
    """Reorder selection so repeatedly unproductive dimensions stop starving others.

    Deprioritized questions are moved behind the rest rather than dropped: a
    dimension that has failed is still open work, and silently removing it
    would fabricate saturation.
    """

    deprioritized: set[str] = {
        guard.argument
        for guard in guards
        if guard.active and guard.effect is GuardEffect.DEPRIORITIZE_DIMENSION
    }
    if not deprioritized:
        return questions
    ordered = sorted(
        enumerate(questions),
        key=lambda item: (item[1].dimension.value in deprioritized, item[0]),
    )
    return tuple(question for _, question in ordered)


def dimension_is_deprioritized(
    dimension: MechanicDimension, guards: tuple[GuardRule, ...]
) -> bool:
    return any(
        guard.active
        and guard.effect is GuardEffect.DEPRIORITIZE_DIMENSION
        and guard.argument == dimension.value
        for guard in guards
    )
