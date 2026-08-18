"""Task-relative interface adequacy receipts for the P6 successor programme.

The scopes in this module are caller-declared strings.  They are not a frozen
ontology of observation, measurement, representation, reward, or uncertainty.
The only formal rule is fail-closed aggregation of explicitly required checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .canonical import content_digest


class InterfaceCheckState(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"


class InterfaceAdequacyStatus(str, Enum):
    ADEQUATE = "ADEQUATE"
    REPAIR_REQUIRED = "REPAIR_REQUIRED"
    UNRESOLVED = "UNRESOLVED"


def _sorted_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value) for value in values}))


@dataclass(frozen=True)
class InterfaceAdequacyCheck:
    check_id: str
    scope: str
    state: InterfaceCheckState
    evidence_ids: tuple[str, ...]
    required: bool
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicInterfaceAdequacyCheck.v1",
            "check_id": self.check_id,
            "scope": self.scope,
            "state": self.state.value,
            "evidence_ids": list(self.evidence_ids),
            "required": self.required,
            "authority_scope": "NON_AUTHORIZING_INTERFACE_CHECK_ONLY",
        }

    def verify(self) -> None:
        if not self.check_id or not self.scope:
            raise ValueError("interface check identity and scope are required")
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("interface check digest mismatch")


def build_interface_check(
    *,
    check_id: str,
    scope: str,
    state: InterfaceCheckState,
    evidence_ids: Sequence[str] = (),
    required: bool = True,
) -> InterfaceAdequacyCheck:
    if not isinstance(state, InterfaceCheckState):
        state = InterfaceCheckState(state)
    payload = {
        "version": "EpistemicInterfaceAdequacyCheck.v1",
        "check_id": str(check_id),
        "scope": str(scope),
        "state": state.value,
        "evidence_ids": list(_sorted_unique(evidence_ids)),
        "required": bool(required),
        "authority_scope": "NON_AUTHORIZING_INTERFACE_CHECK_ONLY",
    }
    check = InterfaceAdequacyCheck(
        check_id=payload["check_id"],
        scope=payload["scope"],
        state=state,
        evidence_ids=tuple(payload["evidence_ids"]),
        required=payload["required"],
        digest=content_digest(payload),
    )
    check.verify()
    return check


@dataclass(frozen=True)
class InterfaceAdequacyReport:
    status: InterfaceAdequacyStatus
    check_digests: tuple[str, ...]
    failed_check_ids: tuple[str, ...]
    unresolved_check_ids: tuple[str, ...]
    failed_scopes: tuple[str, ...]
    unresolved_scopes: tuple[str, ...]
    advisory_check_ids: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "EpistemicInterfaceAdequacyReport.v1",
            "status": self.status.value,
            "check_digests": list(self.check_digests),
            "failed_check_ids": list(self.failed_check_ids),
            "unresolved_check_ids": list(self.unresolved_check_ids),
            "failed_scopes": list(self.failed_scopes),
            "unresolved_scopes": list(self.unresolved_scopes),
            "advisory_check_ids": list(self.advisory_check_ids),
            "reasons": list(self.reasons),
            "permits_broader_revision_consideration": self.permits_broader_revision_consideration,
            "grants_scientific_authority": False,
        }

    @property
    def permits_broader_revision_consideration(self) -> bool:
        return self.status is InterfaceAdequacyStatus.ADEQUATE

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("interface adequacy report digest mismatch")
        if self.status is InterfaceAdequacyStatus.ADEQUATE:
            if self.failed_check_ids or self.unresolved_check_ids:
                raise ValueError("adequate interface cannot have unresolved required checks")


def assess_interface_adequacy(
    checks: Sequence[InterfaceAdequacyCheck],
) -> InterfaceAdequacyReport:
    """Aggregate explicit required interface checks with failure precedence.

    Advisory checks are retained for lineage but never compensate a required
    failure or unresolved coordinate.  A report marked ``ADEQUATE`` only means
    the registered required checks passed; it is not a global sufficiency proof.
    """

    if not checks:
        raise ValueError("at least one interface adequacy check is required")
    for check in checks:
        check.verify()

    ids = [check.check_id for check in checks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate interface check")

    failed = tuple(
        sorted(
            check.check_id
            for check in checks
            if check.required and check.state is InterfaceCheckState.FAIL
        )
    )
    unresolved = tuple(
        sorted(
            check.check_id
            for check in checks
            if check.required and check.state is InterfaceCheckState.UNRESOLVED
        )
    )
    failed_scopes = tuple(
        sorted(
            {
                check.scope
                for check in checks
                if check.required and check.state is InterfaceCheckState.FAIL
            }
        )
    )
    unresolved_scopes = tuple(
        sorted(
            {
                check.scope
                for check in checks
                if check.required and check.state is InterfaceCheckState.UNRESOLVED
            }
        )
    )
    advisory = tuple(sorted(check.check_id for check in checks if not check.required))

    reasons: list[str] = []
    if failed:
        status = InterfaceAdequacyStatus.REPAIR_REQUIRED
        reasons.append("REQUIRED_INTERFACE_CHECK_FAILED")
        if unresolved:
            reasons.append("ADDITIONAL_INTERFACE_CHECKS_UNRESOLVED")
    elif unresolved:
        status = InterfaceAdequacyStatus.UNRESOLVED
        reasons.append("REQUIRED_INTERFACE_CHECK_UNRESOLVED")
    else:
        status = InterfaceAdequacyStatus.ADEQUATE

    payload = {
        "version": "EpistemicInterfaceAdequacyReport.v1",
        "status": status.value,
        "check_digests": sorted(check.digest for check in checks),
        "failed_check_ids": list(failed),
        "unresolved_check_ids": list(unresolved),
        "failed_scopes": list(failed_scopes),
        "unresolved_scopes": list(unresolved_scopes),
        "advisory_check_ids": list(advisory),
        "reasons": sorted(set(reasons)),
        "permits_broader_revision_consideration": status is InterfaceAdequacyStatus.ADEQUATE,
        "grants_scientific_authority": False,
    }
    report = InterfaceAdequacyReport(
        status=status,
        check_digests=tuple(payload["check_digests"]),
        failed_check_ids=failed,
        unresolved_check_ids=unresolved,
        failed_scopes=failed_scopes,
        unresolved_scopes=unresolved_scopes,
        advisory_check_ids=advisory,
        reasons=tuple(payload["reasons"]),
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "InterfaceAdequacyCheck",
    "InterfaceAdequacyReport",
    "InterfaceAdequacyStatus",
    "InterfaceCheckState",
    "assess_interface_adequacy",
    "build_interface_check",
]
