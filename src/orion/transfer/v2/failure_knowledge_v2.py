"""Reviewed V2 scoped-failure applicability surface.

The original V1 implementation is preserved in ``failure_knowledge_v1``. V2
keeps the same record/report schema while hardening context applicability:
every frozen context coordinate must be explicitly classified, at least one
load-bearing coordinate is required, and a changed required-same coordinate
outranks any simultaneous reopen-on-change coordinate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from . import failure_knowledge_v1 as _v1
from .canonical import content_digest


FailureApplicabilityStatus = _v1.FailureApplicabilityStatus
FailureApplicationReport = _v1.FailureApplicationReport


@dataclass(frozen=True)
class FailureKnowledge(_v1.FailureKnowledge):
    """V2 failure record with exhaustive applicability-role coverage."""

    def verify(self) -> None:
        super().verify()
        context_keys = {key for key, _ in self.frozen_context}
        roles = set(self.required_same_coordinates) | set(
            self.reopen_on_change_coordinates
        )
        if not context_keys:
            raise ValueError("failure knowledge requires a non-empty frozen context")
        if not roles:
            raise ValueError(
                "failure context coordinates must be classified for applicability"
            )
        unclassified = context_keys - roles
        if unclassified:
            raise ValueError(
                "frozen failure context coordinate lacks applicability role: "
                + ",".join(sorted(unclassified))
            )


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
    context = _v1._canonical_context(frozen_context)
    payload = {
        "version": "FailureKnowledge.v1",
        "failure_id": str(failure_id),
        "target_contract_id": str(target_contract_id),
        "regime_id": str(regime_id),
        "attempted_trace_ids": list(_v1._ordered(attempted_trace_ids)),
        "observed_failure_id": str(observed_failure_id),
        "responsibility_state_id": str(responsibility_state_id),
        "excluded_condition_ids": list(_v1._sorted_unique(excluded_condition_ids)),
        "still_live_alternative_ids": list(
            _v1._sorted_unique(still_live_alternative_ids)
        ),
        "preserved_success_ids": list(_v1._sorted_unique(preserved_success_ids)),
        "frozen_context": [list(row) for row in context],
        "required_same_coordinates": list(
            _v1._sorted_unique(required_same_coordinates)
        ),
        "reopen_on_change_coordinates": list(
            _v1._sorted_unique(reopen_on_change_coordinates)
        ),
        "evidence_ids": list(_v1._sorted_unique(evidence_ids)),
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


def assess_failure_applicability(
    failure: FailureKnowledge,
    *,
    current_context: Mapping[str, str],
) -> FailureApplicationReport:
    """Apply a scoped negative lesson only under fully compatible context.

    Missing load-bearing context remains unresolved. If any required-same
    coordinate changes, the old lesson is inapplicable even when a separate
    reopen coordinate also changed. Only after required-same compatibility is
    established may a reopen-on-change coordinate reopen the prior route.
    """

    failure.verify()
    frozen = dict(failure.frozen_context)
    current = {str(key): str(value) for key, value in current_context.items()}
    relevant = set(frozen)
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
        incompatible = sorted(set(changed) & set(failure.required_same_coordinates))
        reopened = sorted(set(changed) & set(failure.reopen_on_change_coordinates))
        if incompatible:
            status = FailureApplicabilityStatus.NOT_APPLICABLE
            reasons.append("REQUIRED_SAME_CONTEXT_CHANGED")
            if reopened:
                reasons.append("REOPEN_CHANGE_IGNORED_DUE_TO_REQUIRED_SAME_MISMATCH")
        elif reopened:
            status = FailureApplicabilityStatus.REOPENED
            reasons.append("DECLARED_REOPEN_COORDINATE_CHANGED")
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
