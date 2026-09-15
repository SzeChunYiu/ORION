"""Sections 8 and 9 -- the authority boundary and bounded-saturation outcomes.

`AuthorityDecision` can only ever be a refusal, and
`BoundedSaturationState.certifies_recall` is fixed at False. Both are structural,
not conventional: promotion is refused by construction rather than by review.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from orion.experience.model import LessonAuthority, TaskEpisode

from .constants import SUCCESS_BOUNDARY


class AuthorityRequestKind(str, Enum):
    PROMOTE_SELF_ORION = "PROMOTE_SELF_ORION"
    MERGE_REPAIR = "MERGE_REPAIR"
    RAISE_LESSON_AUTHORITY = "RAISE_LESSON_AUTHORITY"
    MODIFY_EVALUATOR = "MODIFY_EVALUATOR"


@dataclass(frozen=True)
class AuthorityDecision:
    """A refusal, structurally.

    `granted` exists so the refusal is explicit in the record, and construction
    raises if it is True. A boundary enforced by convention is a boundary one
    future caller flips; this one cannot be flipped without editing the type.
    """

    request_kind: AuthorityRequestKind
    requester: str
    granted: bool = False
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.granted:
            raise ValueError(
                "no model output, trial result or Self-ORION proposal may grant "
                "authority; promotion is reserved to the protected host"
            )
        if not self.requester.strip():
            raise ValueError("an authority request must name its requester")


def request_promotion(
    request_kind: AuthorityRequestKind,
    *,
    requester: str,
    model_output_digest: str = "",
) -> AuthorityDecision:
    """Always refuse. Model output is an input to governance, never a grant.

    `model_output_digest` is recorded so the refusal is attributable to a
    specific output, not so the output can influence the answer -- a stronger
    or more confident response produces the identical refusal.
    """

    reasons = [
        "no model output may directly increase authority",
        "Self-ORION may diagnose and propose repairs but may not merge or promote them",
        SUCCESS_BOUNDARY,
    ]
    if model_output_digest:
        reasons.append(f"refused request bound to model output {model_output_digest}")
    return AuthorityDecision(request_kind, requester, False, tuple(reasons))


@dataclass(frozen=True)
class RepairProposal:
    """A diagnosis plus a proposed repair, with no route to being applied here."""

    proposal_id: str
    mechanic_id: str
    diagnosis: str
    proposed_repair: str
    supporting_episode_ids: tuple[str, ...]
    authority: LessonAuthority = LessonAuthority.CANDIDATE
    merge_authorized: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id.strip() or not self.diagnosis.strip():
            raise ValueError("repair proposal identity and diagnosis are required")
        if not self.proposed_repair.strip() or not self.supporting_episode_ids:
            raise ValueError("repair proposal requires a repair and supporting episodes")
        if self.authority is not LessonAuthority.CANDIDATE or self.merge_authorized:
            raise ValueError(
                "a Self-ORION repair proposal cannot carry promoted authority or "
                "self-authorize its own merge"
            )


def propose_repair(
    episodes: Sequence[TaskEpisode],
    *,
    proposal_id: str,
    diagnosis: str,
    proposed_repair: str,
) -> RepairProposal | None:
    """Turn immutable episodes into a proposal. Returns None without evidence."""

    grouped = sorted(episodes, key=lambda item: item.episode_id)
    if not grouped:
        return None
    mechanic_ids = {item.mechanic_id for item in grouped}
    if len(mechanic_ids) != 1:
        return None
    return RepairProposal(
        proposal_id=proposal_id,
        mechanic_id=grouped[0].mechanic_id,
        diagnosis=diagnosis,
        proposed_repair=proposed_repair,
        supporting_episode_ids=tuple(item.episode_id for item in grouped),
    )


# ---------------------------------------------------------------------------
# 9. Bounded saturation as an outcome
# ---------------------------------------------------------------------------


class BoundedSaturationOutcome(str, Enum):
    OPEN = "OPEN"
    CANNOT_CHECK = "CANNOT_CHECK"
    A_PRIORI_FRAME_FLAT = "A_PRIORI_FRAME_FLAT"


@dataclass(frozen=True)
class BoundedSaturationState:
    """OPEN and CANNOT_CHECK are outcomes of the trial, not failures of it.

    A run that ends OPEN has measured that the search was still growing; a run
    that ends CANNOT_CHECK has measured that it could not tell. Both are
    findings. Treating either as an error is what pushes a system to manufacture
    a flat verdict, and `certifies_recall` stays False for all three outcomes
    for the same reason `orion.kernel.saturation` fixes it: N flat rounds under
    a frozen basis is a budget stop, not a recall claim.
    """

    outcome: BoundedSaturationOutcome
    reasons: tuple[str, ...] = ()

    @property
    def is_failure(self) -> bool:
        return False

    @property
    def certifies_recall(self) -> bool:
        return False


def pre_execution_saturation_state() -> BoundedSaturationState:
    """The honest saturation state before the trial has run a single round."""

    return BoundedSaturationState(
        BoundedSaturationOutcome.CANNOT_CHECK,
        (
            "no round has been observed because the live trial has not executed",
            "flatness is undefined without at least one growth vector under the basis",
        ),
    )
