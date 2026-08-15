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
    output_artifact_ids: tuple[str, ...] = ()
    handoff_values: tuple[tuple[str, str], ...] = ()
    metric_observations: tuple[MetricObservation, ...] = ()
    residual_ids: tuple[str, ...] = ()
    failure_signature: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    cost_units: float = 0.0
    latency_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not self.receipt_id.strip() or not self.mechanic_id.strip():
            raise ValueError("mechanic receipt identity and mechanic id are required")
        if self.cost_units < 0 or self.latency_seconds < 0:
            raise ValueError("mechanic cost and latency cannot be negative")
        keys = [key for key, _ in self.handoff_values]
        if len(set(keys)) != len(keys):
            raise ValueError("mechanic handoff values must have unique field ids")
        if self.status in {
            MechanicRunStatus.FAILED,
            MechanicRunStatus.PARTIAL,
            MechanicRunStatus.BLOCKED,
            MechanicRunStatus.CANNOT_CHECK,
        } and not (self.failure_signature or self.residual_ids):
            raise ValueError("non-success mechanic receipts require a failure signature or residual")
