"""Generic epistemic-tension hypotheses for zero-error and anomaly-driven inquiry.

The module deliberately does not freeze a universal taxonomy of scientific
opportunity.  Callers supply string-typed candidate tensions, support witnesses,
defeaters, and discriminators.  A report can preserve plural or unresolved
opportunities and explicitly allows `empirical_residual_present=False`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


class EvidencePresence(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNRESOLVED = "UNRESOLVED"


class TensionStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    PLURAL = "PLURAL"
    NO_MATERIAL_TENSION = "NO_MATERIAL_TENSION"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class EpistemicTensionCandidate:
    tension_id: str
    regime_id: str
    kind: str
    target_contract_ids: tuple[str, ...]
    required_witness_ids: tuple[str, ...]
    defeating_witness_ids: tuple[str, ...]
    discriminator_ids: tuple[str, ...]
    downstream_contract_ids: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicTensionCandidate.v1",
            "tension_id": self.tension_id,
            "regime_id": self.regime_id,
            "kind": self.kind,
            "target_contract_ids": list(self.target_contract_ids),
            "required_witness_ids": list(self.required_witness_ids),
            "defeating_witness_ids": list(self.defeating_witness_ids),
            "discriminator_ids": list(self.discriminator_ids),
            "downstream_contract_ids": list(self.downstream_contract_ids),
            "authority_scope": "NON_AUTHORIZING_INQUIRY_HYPOTHESIS_ONLY",
        }

    def verify(self) -> None:
        if not self.tension_id or not self.regime_id or not self.kind:
            raise ValueError("tension, regime, and kind identities are required")
        if not self.target_contract_ids or not self.required_witness_ids:
            raise ValueError("tension requires target contracts and support witnesses")
        if set(self.required_witness_ids) & set(self.defeating_witness_ids):
            raise ValueError("support and defeater witness roles overlap")
        if not self.discriminator_ids:
            raise ValueError("tension candidate requires a discriminator")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("tension candidate digest mismatch")


def build_tension_candidate(
    *,
    tension_id: str,
    regime_id: str,
    kind: str,
    target_contract_ids: Sequence[str],
    required_witness_ids: Sequence[str],
    discriminator_ids: Sequence[str],
    defeating_witness_ids: Sequence[str] = (),
    downstream_contract_ids: Sequence[str] = (),
) -> EpistemicTensionCandidate:
    payload = {
        "version": "EpistemicTensionCandidate.v1",
        "tension_id": str(tension_id),
        "regime_id": str(regime_id),
        "kind": str(kind),
        "target_contract_ids": list(_sorted_unique(target_contract_ids)),
        "required_witness_ids": list(_sorted_unique(required_witness_ids)),
        "defeating_witness_ids": list(_sorted_unique(defeating_witness_ids)),
        "discriminator_ids": list(_sorted_unique(discriminator_ids)),
        "downstream_contract_ids": list(_sorted_unique(downstream_contract_ids)),
        "authority_scope": "NON_AUTHORIZING_INQUIRY_HYPOTHESIS_ONLY",
    }
    candidate = EpistemicTensionCandidate(
        tension_id=payload["tension_id"],
        regime_id=payload["regime_id"],
        kind=payload["kind"],
        target_contract_ids=tuple(payload["target_contract_ids"]),
        required_witness_ids=tuple(payload["required_witness_ids"]),
        defeating_witness_ids=tuple(payload["defeating_witness_ids"]),
        discriminator_ids=tuple(payload["discriminator_ids"]),
        downstream_contract_ids=tuple(payload["downstream_contract_ids"]),
        digest=content_digest(payload),
    )
    candidate.verify()
    return candidate


@dataclass(frozen=True)
class EpistemicTensionReport:
    regime_id: str
    status: TensionStatus
    empirical_residual_present: bool | None
    identified_tension_id: str | None
    surviving_tension_ids: tuple[str, ...]
    defeated_tension_ids: tuple[str, ...]
    unresolved_tension_ids: tuple[str, ...]
    missing_evidence_ids: tuple[str, ...]
    candidate_digests: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_revision_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicTensionReport.v1",
            "regime_id": self.regime_id,
            "status": self.status.value,
            "empirical_residual_present": self.empirical_residual_present,
            "identified_tension_id": self.identified_tension_id,
            "surviving_tension_ids": list(self.surviving_tension_ids),
            "defeated_tension_ids": list(self.defeated_tension_ids),
            "unresolved_tension_ids": list(self.unresolved_tension_ids),
            "missing_evidence_ids": list(self.missing_evidence_ids),
            "candidate_digests": list(self.candidate_digests),
            "reasons": list(self.reasons),
            "grants_revision_authority": False,
        }

    def verify(self) -> None:
        if self.status is TensionStatus.IDENTIFIED:
            if self.identified_tension_id is None:
                raise ValueError("identified tension requires an identity")
            if self.surviving_tension_ids != (self.identified_tension_id,):
                raise ValueError("identified tension must be the only survivor")
        elif self.identified_tension_id is not None:
            raise ValueError("non-identified tension report cannot select one tension")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("tension report digest mismatch")


def assess_tensions(
    candidates: Sequence[EpistemicTensionCandidate],
    *,
    evidence_presence: Mapping[str, EvidencePresence],
    empirical_residual_present: bool | None,
) -> EpistemicTensionReport:
    if not candidates:
        raise ValueError("at least one tension candidate is required")
    for candidate in candidates:
        candidate.verify()
    ids = [candidate.tension_id for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate tension candidate")
    regime_ids = {candidate.regime_id for candidate in candidates}
    if len(regime_ids) != 1:
        raise ValueError("tension assessment is regime-relative")
    regime_id = next(iter(regime_ids))

    evidence = {
        str(key): EvidencePresence(value) for key, value in evidence_presence.items()
    }
    surviving: list[str] = []
    defeated: list[str] = []
    unresolved: list[str] = []
    missing: set[str] = set()

    for candidate in candidates:
        hard_defeat = False
        candidate_unresolved = False
        for witness_id in candidate.required_witness_ids:
            state = evidence.get(witness_id)
            if state is None:
                missing.add(witness_id)
                candidate_unresolved = True
            elif state is EvidencePresence.UNRESOLVED:
                missing.add(witness_id)
                candidate_unresolved = True
            elif state is EvidencePresence.ABSENT:
                hard_defeat = True
        for defeater_id in candidate.defeating_witness_ids:
            state = evidence.get(defeater_id)
            if state is None:
                missing.add(defeater_id)
                candidate_unresolved = True
            elif state is EvidencePresence.UNRESOLVED:
                missing.add(defeater_id)
                candidate_unresolved = True
            elif state is EvidencePresence.PRESENT:
                hard_defeat = True
        if hard_defeat:
            defeated.append(candidate.tension_id)
        elif candidate_unresolved:
            unresolved.append(candidate.tension_id)
        else:
            surviving.append(candidate.tension_id)

    reasons: list[str] = []
    identified: str | None = None
    if unresolved:
        status = TensionStatus.UNRESOLVED
        reasons.append("ONE_OR_MORE_TENSION_HYPOTHESES_REQUIRE_UNRESOLVED_EVIDENCE")
    elif len(surviving) == 1:
        status = TensionStatus.IDENTIFIED
        identified = surviving[0]
    elif len(surviving) > 1:
        status = TensionStatus.PLURAL
        reasons.append("MULTIPLE_MATERIAL_TENSIONS_SURVIVE")
    else:
        status = TensionStatus.NO_MATERIAL_TENSION
        reasons.append("ALL_REGISTERED_TENSION_HYPOTHESES_DEFEATED")

    payload = {
        "version": "EpistemicTensionReport.v1",
        "regime_id": regime_id,
        "status": status.value,
        "empirical_residual_present": empirical_residual_present,
        "identified_tension_id": identified,
        "surviving_tension_ids": sorted(surviving),
        "defeated_tension_ids": sorted(defeated),
        "unresolved_tension_ids": sorted(unresolved),
        "missing_evidence_ids": sorted(missing),
        "candidate_digests": sorted(candidate.digest for candidate in candidates),
        "reasons": sorted(set(reasons)),
        "grants_revision_authority": False,
    }
    report = EpistemicTensionReport(
        regime_id=regime_id,
        status=status,
        empirical_residual_present=empirical_residual_present,
        identified_tension_id=identified,
        surviving_tension_ids=tuple(payload["surviving_tension_ids"]),
        defeated_tension_ids=tuple(payload["defeated_tension_ids"]),
        unresolved_tension_ids=tuple(payload["unresolved_tension_ids"]),
        missing_evidence_ids=tuple(payload["missing_evidence_ids"]),
        candidate_digests=tuple(payload["candidate_digests"]),
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "EpistemicTensionCandidate",
    "EpistemicTensionReport",
    "EvidencePresence",
    "TensionStatus",
    "assess_tensions",
    "build_tension_candidate",
]
