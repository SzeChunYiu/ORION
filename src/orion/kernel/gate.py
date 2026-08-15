from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from orion.mechanics.answers import AnswerRecord
from orion.mechanics.model import MechanicCell, MechanicDimension

from .evidence import EvidenceResolution, resolve_evidence_refs


class AnswerAuthority(str, Enum):
    """How far one answer may move a mechanic dimension.

    The ladder exists because `questioning._satisfied` treats any non-empty
    tuple as a satisfied dimension. Left ungated, a self-answering loop closes
    its own audit questions by writing arbitrary strings. Machine answers
    therefore stop at `EVIDENCE_BOUND`, which applies content but leaves the
    dimension provisional and the question open; only an independently
    registered discriminating check reaches `VERIFIED`.
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

    `predicate` must accept `positive_fixture` and reject `negative_fixture`.
    A check that accepts both is not evidence of anything — it is the exact
    signature of closure-by-string-filling — and is refused as
    `NOT_DISCRIMINATING` rather than treated as a pass.
    """

    check_id: str
    dimension: MechanicDimension
    lane: str
    predicate: Callable[[MechanicCell], bool]
    positive_fixture: MechanicCell
    negative_fixture: MechanicCell
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

    @property
    def applicable(self) -> bool:
        """Whether the answer may be folded into the cell at all."""

        return self.authority in {
            AnswerAuthority.EVIDENCE_BOUND,
            AnswerAuthority.VERIFIED,
        }


def run_discriminating_check(
    check: DiscriminatingCheck, cell: MechanicCell
) -> tuple[CheckOutcome, tuple[str, ...]]:
    """Execute a check against its own fixtures before trusting it on a cell."""

    try:
        accepts_positive = bool(check.predicate(check.positive_fixture))
        rejects_negative = not bool(check.predicate(check.negative_fixture))
    except Exception as error:  # noqa: BLE001 - a check that crashes cannot verify
        return CheckOutcome.ERRORED, (f"check raised {type(error).__name__}: {error}",)
    if not accepts_positive:
        return CheckOutcome.NOT_SOUND, ("check rejects its own positive fixture",)
    if not rejects_negative:
        return CheckOutcome.NOT_DISCRIMINATING, (
            "check accepts its own negative fixture, so it separates nothing",
        )
    try:
        passed = bool(check.predicate(cell))
    except Exception as error:  # noqa: BLE001
        return CheckOutcome.ERRORED, (f"check raised {type(error).__name__}: {error}",)
    if not passed:
        return CheckOutcome.FAILED, ("check rejects the answered cell",)
    return CheckOutcome.PASSED, ()


def grade_answer(
    record: AnswerRecord,
    candidate_cell: MechanicCell,
    *,
    evidence_roots: Mapping[str, Path],
    checks: Mapping[str, DiscriminatingCheck] = {},
    require_digest: bool = True,
    round_index: int = 0,
) -> AnswerGrading:
    """Grade one answer against evidence resolution and executable verification.

    `candidate_cell` is the cell as it would look with this answer applied, so
    a check inspects the claimed end state rather than the pre-answer cell.
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

    check_id = ""
    outcome: CheckOutcome | None = None
    for candidate_id, check in sorted(checks.items()):
        if check.dimension is not record.dimension:
            continue
        check_id = candidate_id
        if check.lane == record.lane:
            outcome = CheckOutcome.LANE_NOT_INDEPENDENT
            reasons.append(
                f"check '{candidate_id}' shares lane '{record.lane}' with the answer it would verify"
            )
            break
        if not check.predates(round_index):
            outcome = CheckOutcome.CHRONOLOGY_UNVERIFIED
            reasons.append(
                f"check '{candidate_id}' is not frozen before round {round_index}"
            )
            break
        outcome, check_reasons = run_discriminating_check(check, candidate_cell)
        reasons.extend(f"check_{item}" for item in check_reasons)
        break

    if outcome is None:
        check_outcome = CheckOutcome.NOT_REGISTERED
        reasons.append(f"no discriminating check registered for {record.dimension.value}")
    else:
        check_outcome = outcome

    if (
        authority is AnswerAuthority.EVIDENCE_BOUND
        and check_outcome is CheckOutcome.PASSED
    ):
        authority = AnswerAuthority.VERIFIED

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
