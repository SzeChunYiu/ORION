"""Bounded social-evidence dependence and hidden-contribution state.

Different agents/processes are not presumed epistemically independent.  This
module uses explicit registered provenance and truthfulness evidence only; it is
not a general theory of testimony, common knowledge, or strategic interaction.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .canonical import content_digest


class TruthfulnessState(str, Enum):
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    UNRESOLVED = "UNRESOLVED"


class SocialEvidenceIndependenceStatus(str, Enum):
    INDEPENDENT = "INDEPENDENT"
    CORRELATED = "CORRELATED"
    UNRESOLVED = "UNRESOLVED"
    UNRELIABLE = "UNRELIABLE"


class ContributionState(str, Enum):
    OBSERVED = "OBSERVED"
    ABSENT = "ABSENT"
    UNRESOLVED = "UNRESOLVED"


class ContributionCreditStatus(str, Enum):
    EXCLUSIVE_SUPPORTED = "EXCLUSIVE_SUPPORTED"
    SHARED = "SHARED"
    UNRESOLVED = "UNRESOLVED"
    NONE_OBSERVED = "NONE_OBSERVED"


def _uniq(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


@dataclass(frozen=True)
class SocialEvidenceRecord:
    report_id: str
    agent_id: str
    claim_id: str
    direct_observation_ids: tuple[str, ...]
    upstream_source_ids: tuple[str, ...]
    truthfulness_state: TruthfulnessState
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SocialEvidenceRecord.v1",
            "report_id": self.report_id,
            "agent_id": self.agent_id,
            "claim_id": self.claim_id,
            "direct_observation_ids": list(self.direct_observation_ids),
            "upstream_source_ids": list(self.upstream_source_ids),
            "truthfulness_state": self.truthfulness_state.value,
            "grants_claim_authority": False,
        }

    def verify(self) -> None:
        if not self.report_id or not self.agent_id or not self.claim_id:
            raise ValueError("social evidence identities are required")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("social evidence digest mismatch")


def build_social_evidence_record(
    *,
    report_id: str,
    agent_id: str,
    claim_id: str,
    direct_observation_ids: Sequence[str] = (),
    upstream_source_ids: Sequence[str] = (),
    truthfulness_state: TruthfulnessState | str = TruthfulnessState.UNRESOLVED,
) -> SocialEvidenceRecord:
    state = (
        truthfulness_state
        if isinstance(truthfulness_state, TruthfulnessState)
        else TruthfulnessState(truthfulness_state)
    )
    payload = {
        "version": "SocialEvidenceRecord.v1",
        "report_id": str(report_id),
        "agent_id": str(agent_id),
        "claim_id": str(claim_id),
        "direct_observation_ids": list(_uniq(direct_observation_ids)),
        "upstream_source_ids": list(_uniq(upstream_source_ids)),
        "truthfulness_state": state.value,
        "grants_claim_authority": False,
    }
    record = SocialEvidenceRecord(
        report_id=payload["report_id"],
        agent_id=payload["agent_id"],
        claim_id=payload["claim_id"],
        direct_observation_ids=tuple(payload["direct_observation_ids"]),
        upstream_source_ids=tuple(payload["upstream_source_ids"]),
        truthfulness_state=state,
        digest=content_digest(payload),
    )
    record.verify()
    return record


@dataclass(frozen=True)
class SocialEvidenceIndependenceReport:
    claim_id: str
    status: SocialEvidenceIndependenceStatus
    report_digests: tuple[str, ...]
    shared_direct_observation_ids: tuple[str, ...]
    shared_upstream_source_ids: tuple[str, ...]
    repeated_agent_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_claim_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SocialEvidenceIndependenceReport.v1",
            "claim_id": self.claim_id,
            "status": self.status.value,
            "report_digests": list(self.report_digests),
            "shared_direct_observation_ids": list(self.shared_direct_observation_ids),
            "shared_upstream_source_ids": list(self.shared_upstream_source_ids),
            "repeated_agent_ids": list(self.repeated_agent_ids),
            "reasons": list(self.reasons),
            "grants_claim_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("social independence digest mismatch")


def _duplicates(sequences: Sequence[Sequence[str]]) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for sequence in sequences:
        for item in set(sequence):
            counts[item] = counts.get(item, 0) + 1
    return tuple(sorted(item for item, count in counts.items() if count > 1))


def assess_social_evidence_independence(
    records: Sequence[SocialEvidenceRecord],
) -> SocialEvidenceIndependenceReport:
    if len(records) < 2:
        raise ValueError("independence assessment requires at least two reports")
    for record in records:
        record.verify()
    report_ids = [record.report_id for record in records]
    if len(report_ids) != len(set(report_ids)):
        raise ValueError("duplicate social evidence report")
    claims = {record.claim_id for record in records}
    if len(claims) != 1:
        raise ValueError("social evidence independence is claim-relative")
    claim_id = next(iter(claims))

    shared_direct = _duplicates([record.direct_observation_ids for record in records])
    shared_upstream = _duplicates([record.upstream_source_ids for record in records])
    repeated_agents = _duplicates([(record.agent_id,) for record in records])
    reasons: list[str] = []

    if any(record.truthfulness_state is TruthfulnessState.VIOLATED for record in records):
        status = SocialEvidenceIndependenceStatus.UNRELIABLE
        reasons.append("TRUTHFULNESS_VIOLATED")
    elif any(record.truthfulness_state is TruthfulnessState.UNRESOLVED for record in records):
        status = SocialEvidenceIndependenceStatus.UNRESOLVED
        reasons.append("TRUTHFULNESS_UNRESOLVED")
    elif any(not record.direct_observation_ids or not record.upstream_source_ids for record in records):
        status = SocialEvidenceIndependenceStatus.UNRESOLVED
        reasons.append("PROVENANCE_BASIS_INCOMPLETE")
    elif shared_direct or shared_upstream or repeated_agents:
        status = SocialEvidenceIndependenceStatus.CORRELATED
        if shared_direct:
            reasons.append("SHARED_DIRECT_OBSERVATION")
        if shared_upstream:
            reasons.append("SHARED_UPSTREAM_SOURCE")
        if repeated_agents:
            reasons.append("REPEATED_AGENT_IDENTITY")
    else:
        status = SocialEvidenceIndependenceStatus.INDEPENDENT
        reasons.append("REGISTERED_PROVENANCE_DISJOINT")

    payload = {
        "version": "SocialEvidenceIndependenceReport.v1",
        "claim_id": claim_id,
        "status": status.value,
        "report_digests": sorted(record.digest for record in records),
        "shared_direct_observation_ids": list(shared_direct),
        "shared_upstream_source_ids": list(shared_upstream),
        "repeated_agent_ids": list(repeated_agents),
        "reasons": sorted(set(reasons)),
        "grants_claim_authority": False,
    }
    report = SocialEvidenceIndependenceReport(
        claim_id=claim_id,
        status=status,
        report_digests=tuple(payload["report_digests"]),
        shared_direct_observation_ids=shared_direct,
        shared_upstream_source_ids=shared_upstream,
        repeated_agent_ids=repeated_agents,
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


@dataclass(frozen=True)
class SocialContribution:
    contribution_id: str
    contributor_id: str
    outcome_id: str
    state: ContributionState
    evidence_ids: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SocialContribution.v1",
            "contribution_id": self.contribution_id,
            "contributor_id": self.contributor_id,
            "outcome_id": self.outcome_id,
            "state": self.state.value,
            "evidence_ids": list(self.evidence_ids),
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if not self.contribution_id or not self.contributor_id or not self.outcome_id:
            raise ValueError("social contribution identities are required")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("social contribution digest mismatch")


def build_social_contribution(
    *,
    contribution_id: str,
    contributor_id: str,
    outcome_id: str,
    state: ContributionState | str,
    evidence_ids: Sequence[str] = (),
) -> SocialContribution:
    resolved_state = state if isinstance(state, ContributionState) else ContributionState(state)
    payload = {
        "version": "SocialContribution.v1",
        "contribution_id": str(contribution_id),
        "contributor_id": str(contributor_id),
        "outcome_id": str(outcome_id),
        "state": resolved_state.value,
        "evidence_ids": list(_uniq(evidence_ids)),
        "grants_scientific_authority": False,
    }
    contribution = SocialContribution(
        contribution_id=payload["contribution_id"],
        contributor_id=payload["contributor_id"],
        outcome_id=payload["outcome_id"],
        state=resolved_state,
        evidence_ids=tuple(payload["evidence_ids"]),
        digest=content_digest(payload),
    )
    contribution.verify()
    return contribution


@dataclass(frozen=True)
class ContributionCreditReport:
    outcome_id: str
    status: ContributionCreditStatus
    observed_contributor_ids: tuple[str, ...]
    absent_contributor_ids: tuple[str, ...]
    unresolved_contributor_ids: tuple[str, ...]
    exclusive_contributor_id: str | None
    contribution_digests: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SocialContributionCreditReport.v1",
            "outcome_id": self.outcome_id,
            "status": self.status.value,
            "observed_contributor_ids": list(self.observed_contributor_ids),
            "absent_contributor_ids": list(self.absent_contributor_ids),
            "unresolved_contributor_ids": list(self.unresolved_contributor_ids),
            "exclusive_contributor_id": self.exclusive_contributor_id,
            "contribution_digests": list(self.contribution_digests),
            "reasons": list(self.reasons),
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("contribution credit digest mismatch")


def assess_contribution_credit(
    contributions: Sequence[SocialContribution],
) -> ContributionCreditReport:
    if not contributions:
        raise ValueError("at least one registered contribution is required")
    for contribution in contributions:
        contribution.verify()
    ids = [contribution.contribution_id for contribution in contributions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate social contribution")
    outcomes = {contribution.outcome_id for contribution in contributions}
    if len(outcomes) != 1:
        raise ValueError("contribution credit is outcome-relative")
    outcome_id = next(iter(outcomes))

    observed = tuple(sorted(contribution.contributor_id for contribution in contributions if contribution.state is ContributionState.OBSERVED))
    absent = tuple(sorted(contribution.contributor_id for contribution in contributions if contribution.state is ContributionState.ABSENT))
    unresolved = tuple(sorted(contribution.contributor_id for contribution in contributions if contribution.state is ContributionState.UNRESOLVED))
    reasons: list[str] = []
    exclusive: str | None = None
    if unresolved:
        status = ContributionCreditStatus.UNRESOLVED
        reasons.append("PLAUSIBLE_CONTRIBUTION_UNRESOLVED")
    elif len(observed) > 1:
        status = ContributionCreditStatus.SHARED
        reasons.append("MULTIPLE_CONTRIBUTORS_OBSERVED")
    elif len(observed) == 1:
        status = ContributionCreditStatus.EXCLUSIVE_SUPPORTED
        exclusive = observed[0]
        reasons.append("ONE_OBSERVED_ALL_OTHERS_REGISTERED_ABSENT")
    else:
        status = ContributionCreditStatus.NONE_OBSERVED
        reasons.append("NO_REGISTERED_CONTRIBUTION_OBSERVED")

    payload = {
        "version": "SocialContributionCreditReport.v1",
        "outcome_id": outcome_id,
        "status": status.value,
        "observed_contributor_ids": list(observed),
        "absent_contributor_ids": list(absent),
        "unresolved_contributor_ids": list(unresolved),
        "exclusive_contributor_id": exclusive,
        "contribution_digests": sorted(contribution.digest for contribution in contributions),
        "reasons": sorted(set(reasons)),
        "grants_scientific_authority": False,
    }
    report = ContributionCreditReport(
        outcome_id=outcome_id,
        status=status,
        observed_contributor_ids=observed,
        absent_contributor_ids=absent,
        unresolved_contributor_ids=unresolved,
        exclusive_contributor_id=exclusive,
        contribution_digests=tuple(payload["contribution_digests"]),
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "ContributionCreditReport",
    "ContributionCreditStatus",
    "ContributionState",
    "SocialContribution",
    "SocialEvidenceIndependenceReport",
    "SocialEvidenceIndependenceStatus",
    "SocialEvidenceRecord",
    "TruthfulnessState",
    "assess_contribution_credit",
    "assess_social_evidence_independence",
    "build_social_contribution",
    "build_social_evidence_record",
]
