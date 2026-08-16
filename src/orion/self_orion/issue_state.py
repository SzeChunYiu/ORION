from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class DevelopmentIssueStatus(str, Enum):
    OPEN = "OPEN"
    DIAGNOSING = "DIAGNOSING"
    REPAIR_CANDIDATE = "REPAIR_CANDIDATE"
    ASSURANCE = "ASSURANCE"
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"


class InterventionOutcomeKind(str, Enum):
    IMPROVED = "IMPROVED"
    NO_CHANGE = "NO_CHANGE"
    REGRESSED = "REGRESSED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class IssueTransition:
    transition_id: str
    from_status: DevelopmentIssueStatus
    to_status: DevelopmentIssueStatus
    reason: str
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.transition_id.strip() or not self.reason.strip():
            raise ValueError("issue transition identity and reason are required")


@dataclass(frozen=True)
class InterventionOutcome:
    intervention_id: str
    candidate_id: str
    kind: InterventionOutcomeKind
    evidence_ids: tuple[str, ...]
    episode_ids: tuple[str, ...] = ()
    fresh_transfer: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        if not self.intervention_id.strip() or not self.candidate_id.strip():
            raise ValueError("intervention and candidate identity are required")
        if not self.evidence_ids:
            raise ValueError("intervention outcome requires evidence")


@dataclass(frozen=True)
class DevelopmentIssue:
    """Persistent issue identity spanning diagnosis and multiple interventions.

    Adapted from issue-centric self-improvement work: the issue, rather than a
    particular candidate agent, is the durable learning object. Evidence and
    unsuccessful interventions remain attached to the same issue so later
    development does not rediscover or erase prior negative results.

    This object is epistemic/development state only; it grants neither invention
    authority nor method-promotion authority.
    """

    issue_id: str
    title: str
    symptom_signature: str
    status: DevelopmentIssueStatus = DevelopmentIssueStatus.OPEN
    candidate_cause_ids: tuple[str, ...] = ()
    supported_cause_id: str = ""
    discriminator_evidence_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    failure_episode_ids: tuple[str, ...] = ()
    interventions: tuple[InterventionOutcome, ...] = ()
    transitions: tuple[IssueTransition, ...] = ()

    def __post_init__(self) -> None:
        required = (self.issue_id, self.title, self.symptom_signature)
        if any(not item.strip() for item in required):
            raise ValueError("development issue identity, title and symptom are required")
        if self.supported_cause_id and self.supported_cause_id not in self.candidate_cause_ids:
            raise ValueError("supported cause must be one of the candidate causes")
        if self.supported_cause_id and not self.discriminator_evidence_ids:
            raise ValueError("supported cause requires discriminator evidence")
        intervention_ids = [item.intervention_id for item in self.interventions]
        if len(intervention_ids) != len(set(intervention_ids)):
            raise ValueError("intervention ids must be unique within an issue")
        transition_ids = [item.transition_id for item in self.transitions]
        if len(transition_ids) != len(set(transition_ids)):
            raise ValueError("issue transition ids must be unique")

    @property
    def grants_invention_authority(self) -> bool:
        return False

    @property
    def grants_promotion_authority(self) -> bool:
        return False

    @property
    def has_causal_attribution(self) -> bool:
        return bool(self.supported_cause_id and self.discriminator_evidence_ids)

    def add_evidence(
        self,
        *,
        evidence_ids: tuple[str, ...] = (),
        failure_episode_ids: tuple[str, ...] = (),
    ) -> DevelopmentIssue:
        return replace(
            self,
            evidence_ids=_union(self.evidence_ids, evidence_ids),
            failure_episode_ids=_union(self.failure_episode_ids, failure_episode_ids),
        )

    def propose_causes(self, cause_ids: tuple[str, ...]) -> DevelopmentIssue:
        if not cause_ids or any(not item.strip() for item in cause_ids):
            raise ValueError("candidate causes must be non-empty identities")
        return replace(
            self,
            candidate_cause_ids=_union(self.candidate_cause_ids, cause_ids),
            supported_cause_id="",
            discriminator_evidence_ids=(),
        )

    def support_cause(
        self,
        cause_id: str,
        *,
        discriminator_evidence_ids: tuple[str, ...],
    ) -> DevelopmentIssue:
        if cause_id not in self.candidate_cause_ids:
            raise ValueError("cannot support an unregistered cause hypothesis")
        if not discriminator_evidence_ids:
            raise ValueError("cause attribution requires discriminator evidence")
        return replace(
            self,
            supported_cause_id=cause_id,
            discriminator_evidence_ids=_union(
                self.discriminator_evidence_ids,
                discriminator_evidence_ids,
            ),
        )

    def record_intervention(self, outcome: InterventionOutcome) -> DevelopmentIssue:
        if outcome.intervention_id in {item.intervention_id for item in self.interventions}:
            raise ValueError("intervention already recorded for issue")
        return replace(self, interventions=(*self.interventions, outcome))

    def transition(
        self,
        *,
        transition_id: str,
        to_status: DevelopmentIssueStatus,
        reason: str,
        evidence_ids: tuple[str, ...] = (),
    ) -> DevelopmentIssue:
        allowed = _ALLOWED_TRANSITIONS[self.status]
        if to_status not in allowed:
            raise ValueError(f"issue transition {self.status.value}->{to_status.value} is not licensed")
        if self.status is DevelopmentIssueStatus.RESOLVED and to_status is DevelopmentIssueStatus.OPEN:
            if not evidence_ids:
                raise ValueError("reopening a resolved issue requires new evidence")
        transition = IssueTransition(
            transition_id=transition_id,
            from_status=self.status,
            to_status=to_status,
            reason=reason,
            evidence_ids=evidence_ids,
        )
        return replace(
            self,
            status=to_status,
            transitions=(*self.transitions, transition),
            evidence_ids=_union(self.evidence_ids, evidence_ids),
        )


_ALLOWED_TRANSITIONS: dict[DevelopmentIssueStatus, frozenset[DevelopmentIssueStatus]] = {
    DevelopmentIssueStatus.OPEN: frozenset(
        {DevelopmentIssueStatus.DIAGNOSING, DevelopmentIssueStatus.BLOCKED}
    ),
    DevelopmentIssueStatus.DIAGNOSING: frozenset(
        {DevelopmentIssueStatus.REPAIR_CANDIDATE, DevelopmentIssueStatus.BLOCKED}
    ),
    DevelopmentIssueStatus.REPAIR_CANDIDATE: frozenset(
        {
            DevelopmentIssueStatus.ASSURANCE,
            DevelopmentIssueStatus.DIAGNOSING,
            DevelopmentIssueStatus.BLOCKED,
        }
    ),
    DevelopmentIssueStatus.ASSURANCE: frozenset(
        {
            DevelopmentIssueStatus.RESOLVED,
            DevelopmentIssueStatus.DIAGNOSING,
            DevelopmentIssueStatus.BLOCKED,
        }
    ),
    DevelopmentIssueStatus.RESOLVED: frozenset({DevelopmentIssueStatus.OPEN}),
    DevelopmentIssueStatus.BLOCKED: frozenset(
        {DevelopmentIssueStatus.OPEN, DevelopmentIssueStatus.DIAGNOSING}
    ),
}


def _union(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*left, *right)))


__all__ = [
    "DevelopmentIssue",
    "DevelopmentIssueStatus",
    "InterventionOutcome",
    "InterventionOutcomeKind",
    "IssueTransition",
]
