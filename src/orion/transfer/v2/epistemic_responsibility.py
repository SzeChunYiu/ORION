"""Non-authorizing revision-responsibility state for the P6 successor programme.

This module deliberately avoids a fixed global taxonomy of scientific failure.
Callers provide claim-relative hypothesis identities and discriminator predictions.
The formal responsibility state may remain plural or unresolved; no report grants
permission to mutate scientific state.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


class ResponsibilityStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"
    NO_SURVIVING = "NO_SURVIVING"


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _canonical_expectations(
    expected_observations: Mapping[str, Sequence[str]],
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    rows: list[tuple[str, tuple[str, ...]]] = []
    for discriminator_id, outcomes in expected_observations.items():
        key = str(discriminator_id)
        allowed = _sorted_unique(outcomes)
        if not key:
            raise ValueError("discriminator identity is required")
        if not allowed:
            raise ValueError("each discriminator requires at least one expected outcome")
        rows.append((key, allowed))
    rows.sort(key=lambda row: row[0])
    return tuple(rows)


@dataclass(frozen=True)
class ResponsibilityHypothesis:
    hypothesis_id: str
    claim_id: str
    expected_observations: tuple[tuple[str, tuple[str, ...]], ...]
    support_evidence_ids: tuple[str, ...]
    defeater_evidence_ids: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicRevisionResponsibilityHypothesis.v1",
            "hypothesis_id": self.hypothesis_id,
            "claim_id": self.claim_id,
            "expected_observations": [
                [discriminator_id, list(outcomes)]
                for discriminator_id, outcomes in self.expected_observations
            ],
            "support_evidence_ids": list(self.support_evidence_ids),
            "defeater_evidence_ids": list(self.defeater_evidence_ids),
            "authority_scope": "NON_AUTHORIZING_RESPONSIBILITY_HYPOTHESIS_ONLY",
        }

    def verify(self) -> None:
        if not self.hypothesis_id or not self.claim_id:
            raise ValueError("responsibility hypothesis and claim identities are required")
        if not self.expected_observations:
            raise ValueError("responsibility hypothesis requires a discriminator prediction")
        discriminator_ids = [row[0] for row in self.expected_observations]
        if len(discriminator_ids) != len(set(discriminator_ids)):
            raise ValueError("duplicate discriminator prediction")
        if any(not outcomes for _, outcomes in self.expected_observations):
            raise ValueError("empty discriminator outcome set")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("responsibility hypothesis digest mismatch")


def build_responsibility_hypothesis(
    *,
    hypothesis_id: str,
    claim_id: str,
    expected_observations: Mapping[str, Sequence[str]],
    support_evidence_ids: Sequence[str] = (),
    defeater_evidence_ids: Sequence[str] = (),
) -> ResponsibilityHypothesis:
    expectations = _canonical_expectations(expected_observations)
    payload = {
        "version": "EpistemicRevisionResponsibilityHypothesis.v1",
        "hypothesis_id": str(hypothesis_id),
        "claim_id": str(claim_id),
        "expected_observations": [
            [discriminator_id, list(outcomes)]
            for discriminator_id, outcomes in expectations
        ],
        "support_evidence_ids": list(_sorted_unique(support_evidence_ids)),
        "defeater_evidence_ids": list(_sorted_unique(defeater_evidence_ids)),
        "authority_scope": "NON_AUTHORIZING_RESPONSIBILITY_HYPOTHESIS_ONLY",
    }
    hypothesis = ResponsibilityHypothesis(
        hypothesis_id=payload["hypothesis_id"],
        claim_id=payload["claim_id"],
        expected_observations=expectations,
        support_evidence_ids=tuple(payload["support_evidence_ids"]),
        defeater_evidence_ids=tuple(payload["defeater_evidence_ids"]),
        digest=content_digest(payload),
    )
    hypothesis.verify()
    return hypothesis


@dataclass(frozen=True)
class ResponsibilityReport:
    claim_id: str
    status: ResponsibilityStatus
    identified_hypothesis_id: str | None
    surviving_hypothesis_ids: tuple[str, ...]
    defeated_hypothesis_ids: tuple[str, ...]
    missing_discriminator_ids: tuple[str, ...]
    unmodeled_discriminator_ids: tuple[str, ...]
    observed_outcomes: tuple[tuple[str, str], ...]
    hypothesis_digests: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicRevisionResponsibilityReport.v1",
            "claim_id": self.claim_id,
            "status": self.status.value,
            "identified_hypothesis_id": self.identified_hypothesis_id,
            "surviving_hypothesis_ids": list(self.surviving_hypothesis_ids),
            "defeated_hypothesis_ids": list(self.defeated_hypothesis_ids),
            "missing_discriminator_ids": list(self.missing_discriminator_ids),
            "unmodeled_discriminator_ids": list(self.unmodeled_discriminator_ids),
            "observed_outcomes": [list(row) for row in self.observed_outcomes],
            "hypothesis_digests": list(self.hypothesis_digests),
            "reasons": list(self.reasons),
            "grants_revision_authority": False,
        }

    @property
    def grants_revision_authority(self) -> bool:
        return False

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("responsibility report digest mismatch")
        if self.status is ResponsibilityStatus.IDENTIFIED:
            if self.identified_hypothesis_id is None:
                raise ValueError("identified responsibility requires one hypothesis")
            if self.surviving_hypothesis_ids != (self.identified_hypothesis_id,):
                raise ValueError("identified responsibility must have one survivor")
        elif self.identified_hypothesis_id is not None:
            raise ValueError("non-identified responsibility cannot select a hypothesis")


def assess_responsibility(
    hypotheses: Sequence[ResponsibilityHypothesis],
    *,
    observed_outcomes: Mapping[str, str],
) -> ResponsibilityReport:
    """Assess a finite claim-relative responsibility hypothesis set.

    Observations only defeat hypotheses whose registered prediction excludes the
    observed outcome. Missing required discriminator observations keep the state
    unresolved. Extra observations are retained as unmodelled rather than being
    coerced into support or authority.
    """

    if not hypotheses:
        raise ValueError("at least one responsibility hypothesis is required")
    for hypothesis in hypotheses:
        hypothesis.verify()

    hypothesis_ids = [hypothesis.hypothesis_id for hypothesis in hypotheses]
    if len(hypothesis_ids) != len(set(hypothesis_ids)):
        raise ValueError("duplicate responsibility hypothesis")
    claim_ids = {hypothesis.claim_id for hypothesis in hypotheses}
    if len(claim_ids) != 1:
        raise ValueError("responsibility assessment is claim-relative")
    claim_id = next(iter(claim_ids))

    observed = {str(key): str(value) for key, value in observed_outcomes.items()}
    modeled_discriminators = {
        discriminator_id
        for hypothesis in hypotheses
        for discriminator_id, _ in hypothesis.expected_observations
    }
    unmodeled = tuple(sorted(set(observed) - modeled_discriminators))

    surviving: list[ResponsibilityHypothesis] = []
    defeated: list[ResponsibilityHypothesis] = []
    missing: set[str] = set()

    for hypothesis in hypotheses:
        expectations = dict(hypothesis.expected_observations)
        contradicted = any(
            discriminator_id in observed
            and observed[discriminator_id] not in allowed_outcomes
            for discriminator_id, allowed_outcomes in expectations.items()
        )
        if contradicted:
            defeated.append(hypothesis)
            continue
        surviving.append(hypothesis)
        missing.update(set(expectations) - set(observed))

    reasons: list[str] = []
    identified: str | None = None
    if not surviving:
        status = ResponsibilityStatus.NO_SURVIVING
        reasons.append("ALL_REGISTERED_RESPONSIBILITIES_DEFEATED")
    elif missing:
        status = ResponsibilityStatus.UNRESOLVED
        reasons.append("REQUIRED_DISCRIMINATOR_OBSERVATION_MISSING")
    elif len(surviving) == 1:
        status = ResponsibilityStatus.IDENTIFIED
        identified = surviving[0].hypothesis_id
    else:
        status = ResponsibilityStatus.AMBIGUOUS
        reasons.append("MULTIPLE_RESPONSIBILITIES_SURVIVE_SAME_OBSERVATIONS")

    payload = {
        "version": "EpistemicRevisionResponsibilityReport.v1",
        "claim_id": claim_id,
        "status": status.value,
        "identified_hypothesis_id": identified,
        "surviving_hypothesis_ids": sorted(
            hypothesis.hypothesis_id for hypothesis in surviving
        ),
        "defeated_hypothesis_ids": sorted(
            hypothesis.hypothesis_id for hypothesis in defeated
        ),
        "missing_discriminator_ids": sorted(missing),
        "unmodeled_discriminator_ids": list(unmodeled),
        "observed_outcomes": [list(row) for row in sorted(observed.items())],
        "hypothesis_digests": sorted(hypothesis.digest for hypothesis in hypotheses),
        "reasons": sorted(set(reasons)),
        "grants_revision_authority": False,
    }
    report = ResponsibilityReport(
        claim_id=claim_id,
        status=status,
        identified_hypothesis_id=identified,
        surviving_hypothesis_ids=tuple(payload["surviving_hypothesis_ids"]),
        defeated_hypothesis_ids=tuple(payload["defeated_hypothesis_ids"]),
        missing_discriminator_ids=tuple(payload["missing_discriminator_ids"]),
        unmodeled_discriminator_ids=tuple(payload["unmodeled_discriminator_ids"]),
        observed_outcomes=tuple((row[0], row[1]) for row in payload["observed_outcomes"]),
        hypothesis_digests=tuple(payload["hypothesis_digests"]),
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "ResponsibilityHypothesis",
    "ResponsibilityReport",
    "ResponsibilityStatus",
    "assess_responsibility",
    "build_responsibility_hypothesis",
]
