from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension

from .battery import host_battery
from .evidence import EvidenceResolution, resolve_evidence_refs


class AnswerAuthority(str, Enum):
    """How far one answer may move a mechanic dimension.

    The ladder exists because `questioning._satisfied` treats any non-empty
    tuple as a satisfied dimension. Left ungated, a self-answering loop closes
    its own audit questions by writing arbitrary strings. Machine answers
    therefore stop at `EVIDENCE_BOUND`, which applies content but leaves the
    dimension provisional and the question open. Raw discriminating checks are
    diagnostic only: they do not establish evaluator authority, evidence
    relevance, or relying-party authorization and can never mint `VERIFIED`.
    """

    REJECTED = "REJECTED"
    PROPOSED = "PROPOSED"
    EVIDENCE_BOUND = "EVIDENCE_BOUND"
    VERIFIED = "VERIFIED"


class CheckOutcome(str, Enum):
    """Why a discriminating check did or did not license verified closure."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    NOT_SOUND = "NOT_SOUND"
    NOT_DISCRIMINATING = "NOT_DISCRIMINATING"
    NOT_REGISTERED = "NOT_REGISTERED"
    DIMENSION_MISMATCH = "DIMENSION_MISMATCH"
    LANE_NOT_INDEPENDENT = "LANE_NOT_INDEPENDENT"
    CHRONOLOGY_UNVERIFIED = "CHRONOLOGY_UNVERIFIED"
    ERRORED = "ERRORED"


@dataclass(frozen=True)
class DiscriminatingCheck:
    """An executable claim that a mechanic dimension is genuinely answered.

    Formally a triple (predicate, positive fixture, declared negatives). The
    predicate must accept its positive fixture and reject every declared
    negative *and* every member of the host battery for its dimension. The
    battery is what makes the requirement bite: negatives chosen only by the
    check's author can be trivially weak, so admissibility would not exclude
    `lambda cell: bool(cell.some_field)` — the very predicate the authority
    ladder exists to refuse.
    """

    check_id: str
    dimension: MechanicDimension
    lane: str
    predicate: Callable[[MechanicCell], bool]
    positive_fixture: MechanicCell
    negative_fixtures: tuple[MechanicCell, ...] = ()
    frozen_at_round: int | None = None

    def __post_init__(self) -> None:
        if not self.check_id.strip() or not self.lane.strip():
            raise ValueError("discriminating check identity and lane are required")

    def predates(self, round_index: int) -> bool:
        """Whether this check was frozen before the round being graded began.

        `frozen_at_round = n` means the check was fixed before round `n` ran, so
        it may judge rounds `n` and later but not earlier ones. Unknown
        chronology is never treated as satisfied: a check written after seeing
        the answer it judges is a restatement of that answer, so an unpinned
        check can never promote to verified.
        """

        return self.frozen_at_round is not None and self.frozen_at_round <= round_index


@dataclass(frozen=True)
class AnswerGrading:
    """The gate verdict for one answer record."""

    record_id: str
    mechanic_id: str
    dimension: MechanicDimension
    authority: AnswerAuthority
    evidence: tuple[EvidenceResolution, ...] = ()
    check_id: str = ""
    check_outcome: CheckOutcome | None = None
    reasons: tuple[str, ...] = ()
    #: Whether the cited evidence was shown to SUPPORT the claim, as distinct
    #: from being authentic. Content binding establishes that a citation is
    #: really the artifact it names and really says what it is quoted as
    #: saying. It establishes nothing about whether that content supports the
    #: claim it is offered for.
    #:
    #: The hostile battery for issue #59 made the difference concrete: an
    #: answer asserting a claim while citing an artifact that explicitly
    #: CONTRADICTS it still graded EVIDENCE_BOUND and folded into the cell.
    #: EVIDENCE_BOUND is a name that overclaims, and the honest repair is to
    #: stop letting the name carry a guarantee nothing computes.
    #:
    #: None means not established. It is never set True by this module, because
    #: nothing here can establish it; a caller that can must set it explicitly
    #: and say how. Distinguishing "could not check" from "checked and fine" is
    #: the whole point.
    support_established: bool | None = None
    #: Whether the cited evidence was shown to have INFLUENCED the answer.
    #: A citation can be authentic, supporting, and entirely inert. Deciding
    #: this needs an ablation — remove the citation, see whether the answer
    #: changes — which the gate cannot perform on a record it is merely
    #: grading. None means not established, for the same reason.
    influence_established: bool | None = None

    #: Prerequisites this grading was required to establish. Recording the
    #: support and influence axes was not enough on its own: an axis that
    #: nothing consults is a note, not a gate. When a prerequisite is required
    #: and not established, the answer is inapplicable regardless of how well
    #: it did on every other axis — non-compensatory, like the hard gates.
    required_prerequisites: frozenset[str] = frozenset()

    @property
    def unmet_prerequisites(self) -> tuple[str, ...]:
        """Required prerequisites this grading did not establish.

        `None` (not checked) fails a requirement exactly as `False` does. A
        prerequisite that was demanded and not evaluated has not been met; only
        `True` discharges it.
        """

        unmet: list[str] = []
        if "support" in self.required_prerequisites and self.support_established is not True:
            unmet.append("support_not_established")
        if "influence" in self.required_prerequisites and self.influence_established is not True:
            unmet.append("influence_not_established")
        return tuple(unmet)

    @property
    def applicable(self) -> bool:
        """Whether the answer may be folded into the cell at all."""

        if self.unmet_prerequisites:
            return False
        return (
            self.authority is AnswerAuthority.EVIDENCE_BOUND
            or self.authority is AnswerAuthority.VERIFIED
        )


def run_discriminating_check(
    check: DiscriminatingCheck, cell: MechanicCell
) -> tuple[CheckOutcome, tuple[str, ...]]:
    """Admit the check against its fixtures and the host battery, then apply it.

    Order matters: the check is judged before it is trusted. An inadmissible
    check never reaches the answered cell, so a predicate that separates
    nothing cannot report a pass.
    """

    negatives = tuple(check.negative_fixtures) + host_battery(check.dimension, cell)
    try:
        if not bool(check.predicate(check.positive_fixture)):
            return CheckOutcome.NOT_SOUND, ("check rejects its own positive fixture",)
        accepted = tuple(
            item.mechanic_id for item in negatives if bool(check.predicate(item))
        )
    except Exception as error:  # noqa: BLE001 - a check that crashes cannot verify
        return CheckOutcome.ERRORED, (f"check raised {type(error).__name__}: {error}",)
    if accepted:
        return CheckOutcome.NOT_DISCRIMINATING, tuple(
            f"check accepts negative '{item}', so it separates nothing" for item in accepted
        )
    try:
        passed = bool(check.predicate(cell))
    except Exception as error:  # noqa: BLE001
        return CheckOutcome.ERRORED, (f"check raised {type(error).__name__}: {error}",)
    if not passed:
        return CheckOutcome.FAILED, ("check rejects the answered cell",)
    return CheckOutcome.PASSED, ()


def discrimination_order(check: DiscriminatingCheck) -> int:
    """How many distinct negatives the check must reject to be admitted."""

    return len(check.negative_fixtures) + len(host_battery(check.dimension))


def grade_answer(
    record: AnswerRecord,
    candidate_cell: MechanicCell,
    *,
    evidence_roots: Mapping[str, Path],
    checks: Mapping[str, DiscriminatingCheck] = {},
    require_digest: bool = True,
    round_index: int = 0,
) -> AnswerGrading:
    """Grade one proposal against evidence resolution and a diagnostic check.

    `candidate_cell` is the cell as it would look with this answer applied, so
    a check inspects the claimed end state rather than the pre-answer cell. A
    diagnostic `PASSED` outcome is preserved for later appraisal, but it is not
    transition authority and therefore never promotes the proposal here.
    """

    reasons: list[str] = []
    resolutions = resolve_evidence_refs(
        record.evidence_refs, evidence_roots, require_digest=require_digest
    )
    unresolved = tuple(item for item in resolutions if not item.resolved)
    reasons.extend(f"evidence_{item.status.value.lower()}:{item.ref}" for item in unresolved)

    if not resolutions:
        reasons.append("answer cites no evidence")
        authority = AnswerAuthority.PROPOSED
    elif unresolved:
        authority = AnswerAuthority.PROPOSED
    else:
        authority = AnswerAuthority.EVIDENCE_BOUND

    # EVERY admissible check for the dimension must pass, not merely the first
    # one by identifier. The earlier form sorted the registry and broke out of
    # the loop unconditionally, so with two admissible checks for one dimension
    # the lexicographically first decided the verdict — whoever named a check
    # chose which check judged, and a strict check could be silently outranked
    # by a narrow one registered under an earlier name. No test covered two
    # checks on one dimension, so it went unseen until the hostile battery
    # registered `check:a-narrow` and `check:a-strict` for the same cell and got
    # PASSED or FAILED depending only on the names.
    #
    # A check that is same-lane or not frozen in time is INADMISSIBLE: it does
    # not judge, and it does not block a check that is admissible. Only when no
    # admissible check exists does its inadmissibility become the outcome.
    check_id = ""
    outcome: CheckOutcome | None = None
    admissible: list[tuple[str, DiscriminatingCheck]] = []
    inadmissible: list[tuple[str, CheckOutcome]] = []
    for candidate_id, check in sorted(checks.items()):
        if check.dimension is not record.dimension:
            continue
        if check.lane == record.lane:
            inadmissible.append((candidate_id, CheckOutcome.LANE_NOT_INDEPENDENT))
            reasons.append(
                f"check '{candidate_id}' shares lane '{record.lane}' with the answer it would verify"
            )
            continue
        if not check.predates(round_index):
            inadmissible.append((candidate_id, CheckOutcome.CHRONOLOGY_UNVERIFIED))
            reasons.append(
                f"check '{candidate_id}' is not frozen before round {round_index}"
            )
            continue
        admissible.append((candidate_id, check))

    if admissible:
        # Non-compensatory across checks: one failure blocks regardless of how
        # many others pass, and the failing check is the one named in the
        # grading so the reason is attributable.
        for candidate_id, check in admissible:
            candidate_outcome, check_reasons = run_discriminating_check(check, candidate_cell)
            reasons.extend(f"check_{item}" for item in check_reasons)
            if outcome is None or candidate_outcome is not CheckOutcome.PASSED:
                check_id, outcome = candidate_id, candidate_outcome
            if candidate_outcome is not CheckOutcome.PASSED:
                break
    elif inadmissible:
        check_id, outcome = inadmissible[0]

    if outcome is None:
        check_outcome = CheckOutcome.NOT_REGISTERED
        reasons.append(f"no discriminating check registered for {record.dimension.value}")
    else:
        check_outcome = outcome

    if record.waiver_reason and authority is not AnswerAuthority.VERIFIED:
        # A waiver removes the question outright; there is no provisional waiver,
        # so an unverified waiver is refused rather than downgraded.
        reasons.append("waivers require verified authority")
        authority = AnswerAuthority.REJECTED

    return AnswerGrading(
        record_id=record.record_id,
        mechanic_id=record.mechanic_id,
        dimension=record.dimension,
        authority=authority,
        evidence=resolutions,
        check_id=check_id,
        check_outcome=check_outcome,
        reasons=tuple(reasons),
    )
