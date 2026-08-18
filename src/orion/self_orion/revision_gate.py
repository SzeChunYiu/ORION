"""Prospective Self-ORION V3 adapter for higher-order epistemic mechanics.

This gate is intentionally non-authorizing.  It combines formal responsibility,
interface-adequacy, and minimal-revision receipts to nominate at most one candidate
for later isolated execution, replay, fresh transfer, protected assurance, and
external host disposition.  It never merges or promotes a change.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from orion.transfer.v2.canonical import content_digest
from orion.transfer.v2.epistemic_responsibility import (
    ResponsibilityReport,
    ResponsibilityStatus,
)
from orion.transfer.v2.higher_order_epistemic_mechanics import (
    AssessmentStatus,
    HigherOrderEpistemicMechanic,
    MechanicAssessment,
    SelectionStatus,
    select_minimal_admissible,
)
from orion.transfer.v2.interface_adequacy import (
    InterfaceAdequacyReport,
    InterfaceAdequacyStatus,
)


class RevisionGateStatus(str, Enum):
    CANDIDATE_SELECTED = "CANDIDATE_SELECTED"
    MULTIPLE_MINIMA = "MULTIPLE_MINIMA"
    NO_ADMISSIBLE = "NO_ADMISSIBLE"
    INTERFACE_REPAIR_REQUIRED = "INTERFACE_REPAIR_REQUIRED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class RevisionGateReport:
    claim_id: str
    status: RevisionGateStatus
    responsibility_digest: str
    interface_digest: str
    selected_mechanic_id: str | None
    selected_mechanic_digest: str | None
    candidate_mechanic_ids: tuple[str, ...]
    selection_digest: str | None
    reasons: tuple[str, ...]
    digest: str

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SelfOrionRevisionGateReport.v1",
            "claim_id": self.claim_id,
            "status": self.status.value,
            "responsibility_digest": self.responsibility_digest,
            "interface_digest": self.interface_digest,
            "selected_mechanic_id": self.selected_mechanic_id,
            "selected_mechanic_digest": self.selected_mechanic_digest,
            "candidate_mechanic_ids": list(self.candidate_mechanic_ids),
            "selection_digest": self.selection_digest,
            "reasons": list(self.reasons),
            "grants_adoption_authority": False,
            "grants_promotion_authority": False,
            "grants_merge_authority": False,
        }

    @property
    def grants_adoption_authority(self) -> bool:
        return False

    @property
    def grants_promotion_authority(self) -> bool:
        return False

    @property
    def grants_merge_authority(self) -> bool:
        return False

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("revision gate report digest mismatch")
        if self.status is RevisionGateStatus.CANDIDATE_SELECTED:
            if self.selected_mechanic_id is None or self.selected_mechanic_digest is None:
                raise ValueError("selected gate report requires a candidate")
        elif self.selected_mechanic_id is not None or self.selected_mechanic_digest is not None:
            raise ValueError("non-selected gate report cannot nominate a candidate")


def _gate_report(
    *,
    claim_id: str,
    status: RevisionGateStatus,
    responsibility: ResponsibilityReport,
    interface: InterfaceAdequacyReport,
    candidate_ids: Sequence[str] = (),
    selected_id: str | None = None,
    selected_digest: str | None = None,
    selection_digest: str | None = None,
    reasons: Sequence[str] = (),
) -> RevisionGateReport:
    candidate_tuple = tuple(sorted(set(map(str, candidate_ids))))
    reason_tuple = tuple(sorted(set(map(str, reasons))))
    payload = {
        "version": "SelfOrionRevisionGateReport.v1",
        "claim_id": claim_id,
        "status": status.value,
        "responsibility_digest": responsibility.digest,
        "interface_digest": interface.digest,
        "selected_mechanic_id": selected_id,
        "selected_mechanic_digest": selected_digest,
        "candidate_mechanic_ids": list(candidate_tuple),
        "selection_digest": selection_digest,
        "reasons": list(reason_tuple),
        "grants_adoption_authority": False,
        "grants_promotion_authority": False,
        "grants_merge_authority": False,
    }
    report = RevisionGateReport(
        claim_id=claim_id,
        status=status,
        responsibility_digest=responsibility.digest,
        interface_digest=interface.digest,
        selected_mechanic_id=selected_id,
        selected_mechanic_digest=selected_digest,
        candidate_mechanic_ids=candidate_tuple,
        selection_digest=selection_digest,
        reasons=reason_tuple,
        digest=content_digest(payload),
    )
    report.verify()
    return report


def _selection_report(
    *,
    responsibility: ResponsibilityReport,
    interface: InterfaceAdequacyReport,
    candidates: Sequence[HigherOrderEpistemicMechanic],
    assessment_by_digest: Mapping[str, MechanicAssessment],
    mechanic_by_digest: Mapping[str, HigherOrderEpistemicMechanic],
    extra_reasons: Sequence[str] = (),
    interface_repair_mode: bool = False,
) -> RevisionGateReport:
    assessments = tuple(assessment_by_digest[mechanic.digest] for mechanic in candidates)
    selection = select_minimal_admissible(tuple(candidates), assessments)
    ids = tuple(mechanic.mechanic_id for mechanic in candidates)

    if selection.status is SelectionStatus.UNIQUE_MINIMUM:
        selected_digest = selection.selected_mechanic_digest
        if selected_digest is None:
            raise ValueError("unique T1 selection missing digest")
        selected = mechanic_by_digest[selected_digest]
        reasons = list(extra_reasons)
        if interface_repair_mode:
            reasons.append("INTERFACE_REPAIR_PRECEDENCE")
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.CANDIDATE_SELECTED,
            responsibility=responsibility,
            interface=interface,
            candidate_ids=ids,
            selected_id=selected.mechanic_id,
            selected_digest=selected.digest,
            selection_digest=selection.digest,
            reasons=reasons,
        )

    if selection.status is SelectionStatus.MULTIPLE_MINIMA:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.MULTIPLE_MINIMA,
            responsibility=responsibility,
            interface=interface,
            candidate_ids=ids,
            selection_digest=selection.digest,
            reasons=(*extra_reasons, *selection.reasons),
        )

    if selection.status is SelectionStatus.UNRESOLVED:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.UNRESOLVED,
            responsibility=responsibility,
            interface=interface,
            candidate_ids=ids,
            selection_digest=selection.digest,
            reasons=(*extra_reasons, *selection.reasons),
        )

    status = (
        RevisionGateStatus.INTERFACE_REPAIR_REQUIRED
        if interface_repair_mode
        else RevisionGateStatus.NO_ADMISSIBLE
    )
    return _gate_report(
        claim_id=responsibility.claim_id,
        status=status,
        responsibility=responsibility,
        interface=interface,
        candidate_ids=ids,
        selection_digest=selection.digest,
        reasons=(*extra_reasons, *selection.reasons),
    )


def assess_revision_gate(
    *,
    responsibility: ResponsibilityReport,
    interface: InterfaceAdequacyReport,
    mechanics: Sequence[HigherOrderEpistemicMechanic],
    assessments: Sequence[MechanicAssessment],
    responsibility_bindings: Mapping[str, Sequence[str]],
    interface_repair_mechanic_ids: Sequence[str] = (),
    interface_coordinates: Sequence[str] = (),
) -> RevisionGateReport:
    """Nominate the narrowest formally admissible next revision candidate.

    The gate fails closed on unresolved responsibility/interface state.  When a
    required interface check fails, broader model/method candidates are withheld
    and only explicitly registered interface-repair mechanics with an in-scope
    write footprint are considered.  A nomination remains non-authoritative.
    """

    responsibility.verify()
    interface.verify()
    if not mechanics:
        raise ValueError("revision gate requires candidate mechanics")
    for mechanic in mechanics:
        mechanic.verify()
    for assessment in assessments:
        assessment.verify()

    mechanic_ids = [mechanic.mechanic_id for mechanic in mechanics]
    if len(mechanic_ids) != len(set(mechanic_ids)):
        raise ValueError("duplicate mechanic identity")
    claim_ids = {mechanic.claim_id for mechanic in mechanics}
    if claim_ids != {responsibility.claim_id}:
        raise ValueError("revision gate mechanics are claim-relative")

    mechanic_by_id = {mechanic.mechanic_id: mechanic for mechanic in mechanics}
    mechanic_by_digest = {mechanic.digest: mechanic for mechanic in mechanics}
    assessment_by_digest = {assessment.mechanic_digest: assessment for assessment in assessments}
    if len(assessment_by_digest) != len(assessments):
        raise ValueError("duplicate mechanic assessment")
    if set(assessment_by_digest) != set(mechanic_by_digest):
        raise ValueError("assessment set must match revision-gate mechanics exactly")

    if responsibility.status is not ResponsibilityStatus.IDENTIFIED:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.UNRESOLVED,
            responsibility=responsibility,
            interface=interface,
            reasons=("RESPONSIBILITY_NOT_IDENTIFIED", responsibility.status.value),
        )

    hypothesis_id = responsibility.identified_hypothesis_id
    if hypothesis_id is None:
        raise ValueError("identified responsibility missing hypothesis identity")
    if hypothesis_id not in responsibility_bindings:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.UNRESOLVED,
            responsibility=responsibility,
            interface=interface,
            reasons=(f"RESPONSIBILITY_BINDING_MISSING:{hypothesis_id}",),
        )

    bound_ids = tuple(sorted(set(map(str, responsibility_bindings[hypothesis_id]))))
    missing_bound_ids = tuple(sorted(set(bound_ids) - set(mechanic_by_id)))
    if missing_bound_ids:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.UNRESOLVED,
            responsibility=responsibility,
            interface=interface,
            reasons=tuple(f"BOUND_MECHANIC_MISSING:{item}" for item in missing_bound_ids),
        )

    if interface.status is InterfaceAdequacyStatus.UNRESOLVED:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.UNRESOLVED,
            responsibility=responsibility,
            interface=interface,
            reasons=("INTERFACE_ADEQUACY_UNRESOLVED",),
        )

    if interface.status is InterfaceAdequacyStatus.REPAIR_REQUIRED:
        interface_scope = set(map(str, interface_coordinates))
        repair_ids = tuple(sorted(set(map(str, interface_repair_mechanic_ids))))
        reasons: list[str] = []
        valid_repair_ids: list[str] = []
        for mechanic_id in repair_ids:
            mechanic = mechanic_by_id.get(mechanic_id)
            if mechanic is None:
                reasons.append(f"INTERFACE_REPAIR_MECHANIC_MISSING:{mechanic_id}")
                continue
            if not set(mechanic.write_coordinates) <= interface_scope:
                reasons.append(f"INTERFACE_REPAIR_FOOTPRINT_OUT_OF_SCOPE:{mechanic_id}")
                continue
            if mechanic_id in bound_ids:
                valid_repair_ids.append(mechanic_id)

        if not valid_repair_ids:
            reasons.append("NO_ADMISSIBLE_INTERFACE_REPAIR_REGISTERED")
            return _gate_report(
                claim_id=responsibility.claim_id,
                status=RevisionGateStatus.INTERFACE_REPAIR_REQUIRED,
                responsibility=responsibility,
                interface=interface,
                reasons=reasons,
            )

        candidates = tuple(mechanic_by_id[item] for item in valid_repair_ids)
        return _selection_report(
            responsibility=responsibility,
            interface=interface,
            candidates=candidates,
            assessment_by_digest=assessment_by_digest,
            mechanic_by_digest=mechanic_by_digest,
            extra_reasons=reasons,
            interface_repair_mode=True,
        )

    candidates = tuple(mechanic_by_id[item] for item in bound_ids)
    if not candidates:
        return _gate_report(
            claim_id=responsibility.claim_id,
            status=RevisionGateStatus.UNRESOLVED,
            responsibility=responsibility,
            interface=interface,
            reasons=(f"RESPONSIBILITY_BINDING_EMPTY:{hypothesis_id}",),
        )
    return _selection_report(
        responsibility=responsibility,
        interface=interface,
        candidates=candidates,
        assessment_by_digest=assessment_by_digest,
        mechanic_by_digest=mechanic_by_digest,
    )


__all__ = [
    "RevisionGateReport",
    "RevisionGateStatus",
    "assess_revision_gate",
]
