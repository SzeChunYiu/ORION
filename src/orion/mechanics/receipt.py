from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .model import MetricObservation


class MechanicRunStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANNOT_CHECK = "CANNOT_CHECK"


@dataclass(frozen=True)
class MechanicReceipt:
    """Standardized machine-readable handoff from one mechanic execution."""

    receipt_id: str
    mechanic_id: str
    status: MechanicRunStatus
    action_ids: tuple[str, ...] = ()
    output_artifact_ids: tuple[str, ...] = ()
    handoff_values: tuple[tuple[str, str], ...] = ()
    metric_observations: tuple[MetricObservation, ...] = ()
    residual_ids: tuple[str, ...] = ()
    failure_signature: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    evidence_bindings: tuple[tuple[str, str], ...] = ()
    provenance_ids: tuple[str, ...] = ()
    cost_units: float | None = None
    latency_seconds: float | None = None

    def __post_init__(self) -> None:
        if not self.receipt_id.strip() or not self.mechanic_id.strip():
            raise ValueError("mechanic receipt identity and mechanic id are required")
        if self.cost_units is not None and self.cost_units < 0:
            raise ValueError("mechanic cost cannot be negative")
        if self.latency_seconds is not None and self.latency_seconds < 0:
            raise ValueError("mechanic cost and latency cannot be negative")
        keys = [key for key, _ in self.handoff_values]
        if len(set(keys)) != len(keys):
            raise ValueError("mechanic handoff values must have unique field ids")
        binding_ids = [evidence_id for evidence_id, _ in self.evidence_bindings]
        if len(set(binding_ids)) != len(binding_ids):
            raise ValueError("mechanic evidence bindings must have unique ids")
        if set(binding_ids) != set(self.evidence_ids):
            raise ValueError("mechanic receipt must content-bind every evidence id")
        for _, digest in self.evidence_bindings:
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("mechanic evidence bindings require SHA-256 hashes")
        if self.status in {
            MechanicRunStatus.FAILED,
            MechanicRunStatus.PARTIAL,
            MechanicRunStatus.BLOCKED,
            MechanicRunStatus.CANNOT_CHECK,
        } and not (self.failure_signature or self.residual_ids):
            raise ValueError(
                "non-success mechanic receipts require a failure signature or residual"
            )
