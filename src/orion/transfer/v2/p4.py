from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from ..defeaters import AuthorityReadiness, Defeater, DefeaterPlanner, EvidenceAction
from .canonical import content_digest


class EvidenceCustody(str, Enum):
    PROTECTED_EVALUATOR = "PROTECTED_EVALUATOR"
    INDEPENDENT_HOST = "INDEPENDENT_HOST"
    CANDIDATE = "CANDIDATE"
    SELF = "SELF"


class P4PlanStatus(str, Enum):
    READY_FOR_EXTERNAL_CHECK = "READY_FOR_EXTERNAL_CHECK"
    GATHER_EVIDENCE = "GATHER_EVIDENCE"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ProtectedEvidenceAction:
    action_id: str
    addresses: frozenset[str]
    success_probability: float
    cost: float
    custody: EvidenceCustody
    source_digest: str

    def __post_init__(self) -> None:
        if not self.action_id:
            raise ValueError("action_id must be non-empty")
        if not 0.0 <= self.success_probability <= 1.0:
            raise ValueError("success_probability must be in [0,1]")
        if self.cost <= 0:
            raise ValueError("cost must be positive")
        if self.source_digest and not self.source_digest.startswith("sha256:"):
            raise ValueError("source_digest must be sha256-prefixed")

    @property
    def protected(self) -> bool:
        return self.custody in {EvidenceCustody.PROTECTED_EVALUATOR, EvidenceCustody.INDEPENDENT_HOST} and bool(self.source_digest)

    def as_base_action(self) -> EvidenceAction:
        return EvidenceAction(
            action_id=self.action_id,
            addresses=self.addresses,
            success_probability=self.success_probability,
            cost=self.cost,
            protected=self.protected,
        )


@dataclass(frozen=True)
class P4PlanReceipt:
    status: P4PlanStatus
    readiness: AuthorityReadiness
    selected_action_id: str | None
    reason_code: str
    expected_risk_reduction_per_cost: float | None
    protected_action_ids: tuple[str, ...]
    unresolved_defeater_ids: tuple[str, ...]
    authority_terminal: str
    receipt_digest: str

    def __post_init__(self) -> None:
        if self.authority_terminal != "NONE":
            raise ValueError("defeater planner cannot grant authority")

    def unsigned_payload(self) -> dict[str, object]:
        return {
            "receipt_version": "ORION_P4_EVIDENCE_PLAN_RECEIPT_V2",
            "status": self.status.value,
            "readiness": self.readiness.value,
            "selected_action_id": self.selected_action_id,
            "reason_code": self.reason_code,
            "expected_risk_reduction_per_cost": self.expected_risk_reduction_per_cost,
            "protected_action_ids": list(self.protected_action_ids),
            "unresolved_defeater_ids": list(self.unresolved_defeater_ids),
            "authority_terminal": self.authority_terminal,
        }

    def to_payload(self) -> dict[str, object]:
        payload = self.unsigned_payload()
        payload["receipt_digest"] = self.receipt_digest
        return payload

    def verify(self) -> None:
        if content_digest(self.unsigned_payload()) != self.receipt_digest:
            raise ValueError("P4 plan receipt digest mismatch")


def plan_protected_evidence(
    defeaters: Sequence[Defeater],
    actions: Sequence[ProtectedEvidenceAction],
    *,
    critical_threshold: float = 0.7,
) -> P4PlanReceipt:
    planner = DefeaterPlanner(critical_threshold=critical_threshold)
    protected_records = tuple(sorted((action for action in actions if action.protected), key=lambda action: action.action_id))
    base_actions = tuple(action.as_base_action() for action in protected_records)
    readiness = planner.readiness(defeaters, base_actions)
    unresolved = tuple(sorted(d.defeater_id for d in defeaters if d.unresolved))
    critical = tuple(d for d in defeaters if d.unresolved and d.severity >= critical_threshold)
    selection_scope = critical if critical else tuple(d for d in defeaters if d.unresolved)
    selected = planner.choose_action(selection_scope, base_actions)

    if readiness is AuthorityReadiness.READY_FOR_EXTERNAL_CHECK:
        status = P4PlanStatus.READY_FOR_EXTERNAL_CHECK
        reason = "NO_UNRESOLVED_DEFEATERS"
    elif readiness is AuthorityReadiness.CANNOT_CHECK:
        status = P4PlanStatus.CANNOT_CHECK
        reason = "CRITICAL_DEFEATER_WITHOUT_PROTECTED_ACTION"
    elif selected is not None:
        status = P4PlanStatus.GATHER_EVIDENCE
        reason = "PROTECTED_EVIDENCE_ACTION_SELECTED"
    else:
        status = P4PlanStatus.BLOCKED
        reason = "UNRESOLVED_NONCRITICAL_DEFEATER"

    score: float | None = None
    if selected is not None:
        unresolved_by_id = {d.defeater_id: d for d in defeaters if d.unresolved}
        benefit = sum(
            unresolved_by_id[defeater_id].severity * selected.success_probability
            for defeater_id in selected.addresses
            if defeater_id in unresolved_by_id
        )
        score = benefit / selected.cost

    unsigned = {
        "receipt_version": "ORION_P4_EVIDENCE_PLAN_RECEIPT_V2",
        "status": status.value,
        "readiness": readiness.value,
        "selected_action_id": selected.action_id if selected is not None else None,
        "reason_code": reason,
        "expected_risk_reduction_per_cost": score,
        "protected_action_ids": [action.action_id for action in protected_records],
        "unresolved_defeater_ids": list(unresolved),
        "authority_terminal": "NONE",
    }
    return P4PlanReceipt(
        status=status,
        readiness=readiness,
        selected_action_id=selected.action_id if selected is not None else None,
        reason_code=reason,
        expected_risk_reduction_per_cost=score,
        protected_action_ids=tuple(action.action_id for action in protected_records),
        unresolved_defeater_ids=unresolved,
        authority_terminal="NONE",
        receipt_digest=content_digest(unsigned),
    )
