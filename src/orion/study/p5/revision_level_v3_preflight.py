"""Fail-closed confirmatory preflight for Self-ORION V3.

A complete implementation is not a completed experiment.  This module refuses a
confirmatory freeze until subject/split/evaluator/protected-custody identities and
load-bearing comparator structural bindings are concrete.  It intentionally
supports ``CANNOT_CHECK`` while #452/#454 remain unfrozen.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from orion.transfer.v2.canonical import content_digest

_HEX = frozenset("0123456789abcdef")
_PLACEHOLDERS = {"", "UNBOUND", "UNKNOWN", "CANNOT_CHECK", "TBD", "TODO"}


class BaselineBindingDisposition(str, Enum):
    MECHANISM_COMPARATOR_BOUND = "MECHANISM_COMPARATOR_BOUND"
    OFFICIAL_REPRODUCTION_BOUND = "OFFICIAL_REPRODUCTION_BOUND"
    CANNOT_CHECK = "CANNOT_CHECK"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class BaselineStructuralBinding:
    baseline_id: str
    donor_id: str
    source_identity: str
    disposition: BaselineBindingDisposition
    structural_binding_id: str
    official_reproduction: bool
    notes: tuple[str, ...]
    digest: str

    @classmethod
    def build(
        cls,
        *,
        baseline_id: str,
        donor_id: str,
        source_identity: str,
        disposition: BaselineBindingDisposition | str,
        structural_binding_id: str,
        official_reproduction: bool,
        notes: Sequence[str] = (),
    ) -> "BaselineStructuralBinding":
        disposition = (
            disposition
            if isinstance(disposition, BaselineBindingDisposition)
            else BaselineBindingDisposition(disposition)
        )
        baseline_id = str(baseline_id)
        donor_id = str(donor_id)
        source_identity = str(source_identity)
        structural_binding_id = str(structural_binding_id)
        if not baseline_id or not donor_id or not source_identity:
            raise ValueError("baseline/donor/source identities are required")
        bound = disposition in {
            BaselineBindingDisposition.MECHANISM_COMPARATOR_BOUND,
            BaselineBindingDisposition.OFFICIAL_REPRODUCTION_BOUND,
        }
        if bound and not structural_binding_id:
            raise ValueError("bound baseline requires structural binding identity")
        if official_reproduction and disposition is not BaselineBindingDisposition.OFFICIAL_REPRODUCTION_BOUND:
            raise ValueError("official reproduction label requires OFFICIAL_REPRODUCTION_BOUND disposition")
        if disposition is BaselineBindingDisposition.OFFICIAL_REPRODUCTION_BOUND and not official_reproduction:
            raise ValueError("official reproduction disposition requires official_reproduction=true")
        note_tuple = tuple(sorted({str(note) for note in notes}))
        payload = {
            "version": "SelfOrionV3BaselineStructuralBinding.v1",
            "baseline_id": baseline_id,
            "donor_id": donor_id,
            "source_identity": source_identity,
            "disposition": disposition.value,
            "structural_binding_id": structural_binding_id,
            "official_reproduction": bool(official_reproduction),
            "notes": list(note_tuple),
            "grants_donor_equivalence": disposition is BaselineBindingDisposition.OFFICIAL_REPRODUCTION_BOUND,
            "grants_scientific_authority": False,
        }
        result = cls(
            baseline_id=baseline_id,
            donor_id=donor_id,
            source_identity=source_identity,
            disposition=disposition,
            structural_binding_id=structural_binding_id,
            official_reproduction=bool(official_reproduction),
            notes=note_tuple,
            digest=content_digest(payload),
        )
        result.verify()
        return result

    @property
    def bound_for_confirmatory(self) -> bool:
        return self.disposition in {
            BaselineBindingDisposition.MECHANISM_COMPARATOR_BOUND,
            BaselineBindingDisposition.OFFICIAL_REPRODUCTION_BOUND,
        }

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SelfOrionV3BaselineStructuralBinding.v1",
            "baseline_id": self.baseline_id,
            "donor_id": self.donor_id,
            "source_identity": self.source_identity,
            "disposition": self.disposition.value,
            "structural_binding_id": self.structural_binding_id,
            "official_reproduction": self.official_reproduction,
            "notes": list(self.notes),
            "grants_donor_equivalence": self.disposition is BaselineBindingDisposition.OFFICIAL_REPRODUCTION_BOUND,
            "grants_scientific_authority": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("baseline structural binding digest mismatch")


@dataclass(frozen=True)
class ConfirmatoryExecutionBinding:
    protocol_id: str
    subject_revision: str
    protected_suite_commitment: str
    candidate_packet_sha256: str
    final_split_sha256: str
    evaluator_sha256: str
    evaluation_epoch: str
    baseline_config_sha256: str
    fresh_transfer_evaluator_sha256: str
    result_verifier_owner: str
    candidate_policy_owner: str
    protected_evaluator_owner: str
    outcome_accessed: bool


class ConfirmatoryPreflightStatus(str, Enum):
    READY_TO_FREEZE_CONFIRMATORY = "READY_TO_FREEZE_CONFIRMATORY"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class ConfirmatoryPreflightReport:
    protocol_id: str
    status: ConfirmatoryPreflightStatus
    blockers: tuple[str, ...]
    baseline_binding_digests: tuple[str, ...]
    digest: str

    @property
    def grants_scientific_authority(self) -> bool:
        return False

    @property
    def grants_p5_peer_review_ready(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return self.status is ConfirmatoryPreflightStatus.READY_TO_FREEZE_CONFIRMATORY

    def unsigned(self) -> dict[str, object]:
        return {
            "version": "SelfOrionV3ConfirmatoryPreflight.v1",
            "protocol_id": self.protocol_id,
            "status": self.status.value,
            "blockers": list(self.blockers),
            "baseline_binding_digests": list(self.baseline_binding_digests),
            "grants_scientific_authority": False,
            "grants_p5_peer_review_ready": False,
        }

    def verify(self) -> None:
        if content_digest(self.unsigned()) != self.digest:
            raise ValueError("confirmatory preflight digest mismatch")
        if self.status is ConfirmatoryPreflightStatus.READY_TO_FREEZE_CONFIRMATORY and self.blockers:
            raise ValueError("ready confirmatory preflight cannot have blockers")


def _is_hex(value: str, length: int) -> bool:
    return len(value) == length and value.lower() == value and all(char in _HEX for char in value)


def _concrete(value: str) -> bool:
    return value.strip().upper() not in _PLACEHOLDERS


def assess_confirmatory_preflight(
    binding: ConfirmatoryExecutionBinding,
    baseline_bindings: Sequence[BaselineStructuralBinding],
    *,
    required_baseline_ids: Sequence[str],
) -> ConfirmatoryPreflightReport:
    blockers: list[str] = []
    if not _concrete(binding.protocol_id):
        blockers.append("protocol_id_unbound")
    if not _is_hex(binding.subject_revision, 40):
        blockers.append("subject_revision_unbound_or_invalid")
    for field, value in (
        ("protected_suite_commitment", binding.protected_suite_commitment),
        ("candidate_packet_sha256", binding.candidate_packet_sha256),
        ("final_split_sha256", binding.final_split_sha256),
        ("evaluator_sha256", binding.evaluator_sha256),
        ("baseline_config_sha256", binding.baseline_config_sha256),
        ("fresh_transfer_evaluator_sha256", binding.fresh_transfer_evaluator_sha256),
    ):
        if not _is_hex(value, 64):
            blockers.append(f"{field}_unbound_or_invalid")
    if not _concrete(binding.evaluation_epoch):
        blockers.append("evaluation_epoch_unbound")
    if binding.result_verifier_owner != "#283":
        blockers.append("result_verifier_owner_not_283")
    if not _concrete(binding.candidate_policy_owner) or not _concrete(binding.protected_evaluator_owner):
        blockers.append("candidate_or_evaluator_owner_unbound")
    elif binding.candidate_policy_owner == binding.protected_evaluator_owner:
        blockers.append("candidate_controls_protected_evaluator")
    if binding.outcome_accessed:
        blockers.append("outcome_accessed_before_confirmatory_freeze")

    by_id: dict[str, BaselineStructuralBinding] = {}
    for baseline in baseline_bindings:
        baseline.verify()
        if baseline.baseline_id in by_id:
            raise ValueError(f"duplicate baseline structural binding: {baseline.baseline_id}")
        by_id[baseline.baseline_id] = baseline
    for baseline_id in sorted(set(map(str, required_baseline_ids))):
        baseline = by_id.get(baseline_id)
        if baseline is None:
            blockers.append(f"baseline_binding_missing:{baseline_id}")
        elif not baseline.bound_for_confirmatory:
            blockers.append(f"baseline_binding_not_confirmatory:{baseline_id}:{baseline.disposition.value}")

    status = (
        ConfirmatoryPreflightStatus.CANNOT_CHECK
        if blockers
        else ConfirmatoryPreflightStatus.READY_TO_FREEZE_CONFIRMATORY
    )
    blocker_tuple = tuple(sorted(set(blockers)))
    baseline_digests = tuple(sorted(baseline.digest for baseline in baseline_bindings))
    payload = {
        "version": "SelfOrionV3ConfirmatoryPreflight.v1",
        "protocol_id": binding.protocol_id,
        "status": status.value,
        "blockers": list(blocker_tuple),
        "baseline_binding_digests": list(baseline_digests),
        "grants_scientific_authority": False,
        "grants_p5_peer_review_ready": False,
    }
    report = ConfirmatoryPreflightReport(
        protocol_id=binding.protocol_id,
        status=status,
        blockers=blocker_tuple,
        baseline_binding_digests=baseline_digests,
        digest=content_digest(payload),
    )
    report.verify()
    return report


__all__ = [
    "BaselineBindingDisposition",
    "BaselineStructuralBinding",
    "ConfirmatoryExecutionBinding",
    "ConfirmatoryPreflightReport",
    "ConfirmatoryPreflightStatus",
    "assess_confirmatory_preflight",
]
