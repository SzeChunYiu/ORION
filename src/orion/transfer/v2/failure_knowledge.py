"""Scoped negative knowledge for ORION failure epistemology.

A failure event is not a permanent prohibition.  This module records what a
failure is claimed to exclude, which alternatives remain live, and the exact
context coordinates under which that negative lesson may be reused.  Declared
context changes can explicitly reopen the failed route.

All records are non-authorizing.  They do not establish scientific refutation,
novelty, or adoption authority by themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .canonical import content_digest


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


def _ordered(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(value) for value in values)


def _canonical_context(values: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    for raw_key, raw_value in values.items():
        key = str(raw_key)
        value = str(raw_value)
        if not key or not value:
            raise ValueError("failure context coordinates and values must be non-empty")
        rows.append((key, value))
    rows.sort(key=lambda row: row[0])
    if len({key for key, _ in rows}) != len(rows):
        raise ValueError("duplicate failure context coordinate")
    return tuple(rows)


class FailureApplicabilityStatus(str, Enum):
    APPLIES = "APPLIES"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    REOPENED = "REOPENED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class FailureKnowledge:
    failure_id: str
    target_contract_id: str
    regime_id: str
    attempted_trace_ids: tuple[str, ...]
    observed_failure_id: str
    responsibility_state_id: str
    excluded_condition_ids: tuple[str, ...]
    still_live_alternative_ids: tuple[str, ...]
    preserved_success_ids: tuple[str, ...]
    frozen_context: tuple[tuple[str, str], ...]
    required_same_coordinates: tuple[str, ...]
    reopen_on_change_coordinates: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    authority_owner_id: str
    digest: str

    @property
    def grants_scientific_refutation(self) -> bool:
        return False

    @property
    def grants_global_prohibition(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureKnowledge.v1",
            "failure_id": self.failure_id,
            "target_contract_id": self.target_contract_id,
            "regime_id": self.regime_id,
            "attempted_trace_ids": list(self.attempted_trace_ids),
            "observed_failure_id": self.observed_failure_id,
            "responsibility_state_id": self.responsibility_state_id,
            "excluded_condition_ids": list(self.excluded_condition_ids),
            "still_live_alternative_ids": list(self.still_live_alternative_ids),
            "preserved_success_ids": list(self.preserved_success_ids),
            "frozen_context": [list(row) for row in self.frozen_context],
            "required_same_coordinates": list(self.required_same_coordinates),
            "reopen_on_change_coordinates": list(self.reopen_on_change_coordinates),
            "evidence_ids": list(self.evidence_ids),
            "authority_owner_id": self.authority_owner_id,
            "grants_scientific_refutation": False,
            "grants_global_prohibition": False,
        }

    def verify(self) -> None:
        if not self.failure_id or not self.target_contract_id or not self.regime_id:
            raise ValueError("failure, contract, and regime identities are required")
        if not self.observed_failure_id or not self.responsibility_state_id:
            raise ValueError("observed failure and responsibility state identities are required")
        if not self.attempted_trace_ids:
            raise ValueError("failure knowledge requires an attempted trace")
        if any(not trace_id for trace_id in self.attempted_trace_ids):
            raise ValueError("failure attempt trace identities must be non-empty")
        if not self.excluded_condition_ids:
            raise ValueError("failure knowledge requires at least one scoped excluded condition")
        if not self.evidence_ids or not self.authority_owner_id:
            raise ValueError("failure evidence and authority owner identities are required")
        context_keys = {key for key, _ in self.frozen_context}
        same = set(self.required_same_coordinates)
        reopen = set(self.reopen_on_change_coordinates)
        overlap = same & reopen
        if overlap:
            raise ValueError(
                "required-same and reopen-on-change context roles overlap: "
                + ",".join(sorted(overlap))
            )
        unknown = (same | reopen) - context_keys
        if unknown:
            raise ValueError(
                "failure applicability coordinate missing from frozen context: "
                + ",".join(sorted(unknown))
            )
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure knowledge digest mismatch")


def build_failure_knowledge(
    *,
    failure_id: str,
    target_contract_id: str,
    regime_id: str,
    attempted_trace_ids: Sequence[str],
    observed_failure_id: str,
    responsibility_state_id: str,
    excluded_condition_ids: Sequence[str],
    frozen_context: Mapping[str, str],
    evidence_ids: Sequence[str],
    authority_owner_id: str,
    still_live_alternative_ids: Sequence[str] = (),
    preserved_success_ids: Sequence[str] = (),
    required_same_coordinates: Sequence[str] = (),
    reopen_on_change_coordinates: Sequence[str] = (),
) -> FailureKnowledge:
    context = _canonical_context(frozen_context)
    payload = {
        "version": "FailureKnowledge.v1",
        "failure_id": str(failure_id),
        "target_contract_id": str(target_contract_id),
        "regime_id": str(regime_id),
        "attempted_trace_ids": list(_ordered(attempted_trace_ids)),
        "observed_failure_id": str(observed_failure_id),
        "responsibility_state_id": str(responsibility_state_id),
        "excluded_condition_ids": list(_sorted_unique(excluded_condition_ids)),
        "still_live_alternative_ids": list(_sorted_unique(still_live_alternative_ids)),
        "preserved_success_ids": list(_sorted_unique(preserved_success_ids)),
        "frozen_context": [list(row) for row in context],
        "required_same_coordinates": list(_sorted_unique(required_same_coordinates)),
        "reopen_on_change_coordinates": list(_sorted_unique(reopen_on_change_coordinates)),
        "evidence_ids": list(_sorted_unique(evidence_ids)),
        "authority_owner_id": str(authority_owner_id),
        "grants_scientific_refutation": False,
        "grants_global_prohibition": False,
    }
    record = FailureKnowledge(
        failure_id=payload["failure_id"],
        target_contract_id=payload["target_contract_id"],
        regime_id=payload["regime_id"],
        attempted_trace_ids=tuple(payload["attempted_trace_ids"]),
        observed_failure_id=payload["observed_failure_id"],
        responsibility_state_id=payload["responsibility_state_id"],
        excluded_condition_ids=tuple(payload["excluded_condition_ids"]),
        still_live_alternative_ids=tuple(payload["still_live_alternative_ids"]),
        preserved_success_ids=tuple(payload["preserved_success_ids"]),
        frozen_context=context,
        required_same_coordinates=tuple(payload["required_same_coordinates"]),
        reopen_on_change_coordinates=tuple(payload["reopen_on_change_coordinates"]),
        evidence_ids=tuple(payload["evidence_ids"]),
        authority_owner_id=payload["authority_owner_id"],
        digest=content_digest(payload),
    )
    record.verify()
    return record


@dataclass(frozen=True)
class FailureApplicationReport:
    failure_digest: str
    status: FailureApplicabilityStatus
    applicable_excluded_condition_ids: tuple[str, ...]
    changed_coordinates: tuple[str, ...]
    missing_coordinates: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    @property
    def grants_global_prohibition(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "FailureApplicationReport.v1",
            "failure_digest": self.failure_digest,
            "status": self.status.value,
            "applicable_excluded_condition_ids": list(self.applicable_excluded_condition_ids),
            "changed_coordinates": list(self.changed_coordinates),
            "missing_coordinates": list(self.missing_coordinates),
            "reasons": list(self.reasons),
            "grants_global_prohibition": False,
        }

    def verify(self) -> None:
        if self.status is not FailureApplicabilityStatus.APPLIES:
            if self.applicable_excluded_condition_ids:
                raise ValueError("non-applicable failure knowledge cannot emit exclusions")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("failure applicability digest mismatch")


def assess_failure_applicability(
    failure: FailureKnowledge,
    *,
    current_context: Mapping[str, str],
) -> FailureApplicationReport:
    """Assess whether scoped failure knowledge can constrain a new episode.

    Missing load-bearing context keeps the lesson unresolved.  A changed
    `reopen_on_change` coordinate explicitly reopens the old failed route.  A
    changed `required_same` coordinate makes the old lesson inapplicable.  Only
    an exact compatible context emits the recorded exclusions.
    """

    failure.verify()
    frozen = dict(failure.frozen_context)
    current = {str(key): str(value) for key, value in current_context.items()}
    relevant = set(failure.required_same_coordinates) | set(
        failure.reopen_on_change_coordinates
    )
    missing = sorted(coordinate for coordinate in relevant if coordinate not in current)
    changed = sorted(
        coordinate
        for coordinate in relevant
        if coordinate in current and current[coordinate] != frozen[coordinate]
    )

    reasons: list[str] = []
    exclusions: tuple[str, ...] = ()
    if missing:
        status = FailureApplicabilityStatus.UNRESOLVED
        reasons.append("REQUIRED_FAILURE_CONTEXT_MISSING")
    else:
        reopened = sorted(set(changed) & set(failure.reopen_on_change_coordinates))
        incompatible = sorted(set(changed) & set(failure.required_same_coordinates))
        if reopened:
            status = FailureApplicabilityStatus.REOPENED
            reasons.append("DECLARED_REOPEN_COORDINATE_CHANGED")
        elif incompatible:
            status = FailureApplicabilityStatus.NOT_APPLICABLE
            reasons.append("REQUIRED_SAME_CONTEXT_CHANGED")
        else:
            status = FailureApplicabilityStatus.APPLIES
            exclusions = failure.excluded_condition_ids

    payload = {
        "version": "FailureApplicationReport.v1",
        "failure_digest": failure.digest,
        "status": status.value,
        "applicable_excluded_condition_ids": list(exclusions),
        "changed_coordinates": changed,
        "missing_coordinates": missing,
        "reasons": sorted(set(reasons)),
        "grants_global_prohibition": False,
    }
    report = FailureApplicationReport(
        failure_digest=failure.digest,
        status=status,
        applicable_excluded_condition_ids=exclusions,
        changed_coordinates=tuple(changed),
        missing_coordinates=tuple(missing),
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "FailureApplicabilityStatus",
    "FailureApplicationReport",
    "FailureKnowledge",
    "assess_failure_applicability",
    "build_failure_knowledge",
]
