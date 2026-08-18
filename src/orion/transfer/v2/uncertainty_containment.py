"""Versioned, non-promoting validity envelopes for uncertainty containment.

Containment restricts admissible use of a subject/claim in caller-declared
contexts.  It is not model repair, a truth certificate, or scientific authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


class ValidityState(str, Enum):
    SUPPORTED = "SUPPORTED"
    INVALID = "INVALID"
    UNRESOLVED = "UNRESOLVED"


class ContainmentStatus(str, Enum):
    IN_SCOPE = "IN_SCOPE"
    BLOCKED = "BLOCKED"
    UNRESOLVED = "UNRESOLVED"


def _normalise_pairs(
    *,
    context_states: Mapping[str, ValidityState | str] | None,
    context_state_pairs: Sequence[tuple[str, ValidityState | str]] | None,
) -> tuple[tuple[str, ValidityState], ...]:
    if context_states is not None and context_state_pairs is not None:
        raise ValueError("provide context_states or context_state_pairs, not both")
    if context_state_pairs is not None:
        seen: set[str] = set()
        rows: list[tuple[str, ValidityState]] = []
        for raw_key, raw_state in context_state_pairs:
            key = str(raw_key)
            if key in seen:
                raise ValueError(f"duplicate context:{key}")
            seen.add(key)
            rows.append((key, raw_state if isinstance(raw_state, ValidityState) else ValidityState(raw_state)))
        rows.sort(key=lambda row: row[0])
        return tuple(rows)
    states = context_states or {}
    return tuple(
        sorted(
            (
                str(key),
                value if isinstance(value, ValidityState) else ValidityState(value),
            )
            for key, value in states.items()
        )
    )


@dataclass(frozen=True)
class EpistemicValidityEnvelope:
    envelope_id: str
    claim_id: str
    subject_id: str
    context_states: tuple[tuple[str, ValidityState], ...]
    evidence_ids: tuple[str, ...]
    parent_envelope_digest: str | None
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicValidityEnvelope.v1",
            "envelope_id": self.envelope_id,
            "claim_id": self.claim_id,
            "subject_id": self.subject_id,
            "context_states": [[key, state.value] for key, state in self.context_states],
            "evidence_ids": list(self.evidence_ids),
            "parent_envelope_digest": self.parent_envelope_digest,
            "establishes_model_correctness": False,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if not self.envelope_id or not self.claim_id or not self.subject_id:
            raise ValueError("validity envelope identities are required")
        keys = [key for key, _ in self.context_states]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate context")
        if self.parent_envelope_digest is not None and not self.parent_envelope_digest.startswith("sha256:"):
            raise ValueError("parent envelope digest must be content-addressed")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("validity envelope digest mismatch")


def build_validity_envelope(
    *,
    envelope_id: str,
    claim_id: str,
    subject_id: str,
    context_states: Mapping[str, ValidityState | str] | None = None,
    context_state_pairs: Sequence[tuple[str, ValidityState | str]] | None = None,
    evidence_ids: Sequence[str] = (),
    parent_envelope_digest: str | None = None,
) -> EpistemicValidityEnvelope:
    rows = _normalise_pairs(
        context_states=context_states,
        context_state_pairs=context_state_pairs,
    )
    payload = {
        "version": "EpistemicValidityEnvelope.v1",
        "envelope_id": str(envelope_id),
        "claim_id": str(claim_id),
        "subject_id": str(subject_id),
        "context_states": [[key, state.value] for key, state in rows],
        "evidence_ids": sorted(set(map(str, evidence_ids))),
        "parent_envelope_digest": parent_envelope_digest,
        "establishes_model_correctness": False,
        "grants_scientific_authority": False,
    }
    envelope = EpistemicValidityEnvelope(
        envelope_id=payload["envelope_id"],
        claim_id=payload["claim_id"],
        subject_id=payload["subject_id"],
        context_states=rows,
        evidence_ids=tuple(payload["evidence_ids"]),
        parent_envelope_digest=parent_envelope_digest,
        digest=content_digest(payload),
    )
    envelope.verify()
    return envelope


@dataclass(frozen=True)
class ContainmentReport:
    envelope_digest: str
    claim_id: str
    subject_id: str
    context_id: str
    status: ContainmentStatus
    reasons: tuple[str, ...]
    digest: str

    @property
    def establishes_model_correctness(self) -> bool:
        return False

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def rewrites_model(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicContainmentReport.v1",
            "envelope_digest": self.envelope_digest,
            "claim_id": self.claim_id,
            "subject_id": self.subject_id,
            "context_id": self.context_id,
            "status": self.status.value,
            "reasons": list(self.reasons),
            "establishes_model_correctness": False,
            "grants_scientific_authority": False,
            "rewrites_model": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("containment report digest mismatch")


def assess_containment(
    envelope: EpistemicValidityEnvelope,
    *,
    context_id: str,
) -> ContainmentReport:
    envelope.verify()
    context = str(context_id)
    states = dict(envelope.context_states)
    reasons: list[str] = []
    state = states.get(context)
    if state is ValidityState.SUPPORTED:
        status = ContainmentStatus.IN_SCOPE
        reasons.append("REGISTERED_CONTEXT_SUPPORTED")
    elif state is ValidityState.INVALID:
        status = ContainmentStatus.BLOCKED
        reasons.append("REGISTERED_CONTEXT_INVALID")
    elif state is ValidityState.UNRESOLVED:
        status = ContainmentStatus.UNRESOLVED
        reasons.append("REGISTERED_CONTEXT_UNRESOLVED")
    else:
        status = ContainmentStatus.UNRESOLVED
        reasons.append("CONTEXT_NOT_REGISTERED")
    payload = {
        "version": "EpistemicContainmentReport.v1",
        "envelope_digest": envelope.digest,
        "claim_id": envelope.claim_id,
        "subject_id": envelope.subject_id,
        "context_id": context,
        "status": status.value,
        "reasons": sorted(set(reasons)),
        "establishes_model_correctness": False,
        "grants_scientific_authority": False,
        "rewrites_model": False,
    }
    report = ContainmentReport(
        envelope_digest=envelope.digest,
        claim_id=envelope.claim_id,
        subject_id=envelope.subject_id,
        context_id=context,
        status=status,
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "ContainmentReport",
    "ContainmentStatus",
    "EpistemicValidityEnvelope",
    "ValidityState",
    "assess_containment",
    "build_validity_envelope",
]
