"""Protected research-state identity extension.

Codex's frozen V1 mechanics projection predates ``AnswerRecord.metric_payload``.
Rather than silently changing its historical canonical profile, protected
transitions use this domain-separated extension. It is byte-for-byte compatible
with the V1 projection hash when no metric payload is present, and commits the
complete metric semantics once such records enter protected state.
"""

from __future__ import annotations

from typing import Any

from .transition import ProgramProjection, canonical_digest, projection_hash


def _metric_payload(record) -> list[dict[str, Any]]:  # noqa: ANN001
    return [
        {
            "metric_id": metric.metric_id,
            "description": metric.description,
            "kind": metric.kind.value,
            "direction": metric.direction.value,
            "unit": metric.unit,
            "required_for_handoff": metric.required_for_handoff,
            "threshold_semantics": metric.threshold_semantics,
            "uncertainty_semantics": metric.uncertainty_semantics,
        }
        for metric in record.metric_payload
    ]


def protected_projection_hash(projection: ProgramProjection) -> str:
    legacy = projection_hash(projection)
    metric_extensions = [
        {
            "record_id": record.record_id,
            "metric_payload": _metric_payload(record),
        }
        for record in sorted(projection.records, key=lambda item: item.record_id)
        if record.metric_payload
    ]
    if not metric_extensions:
        return legacy
    return canonical_digest(
        {
            "base_projection_hash": legacy,
            "metric_extensions": metric_extensions,
        },
        domain="orion.protected-projection.v1",
    )


__all__ = ["protected_projection_hash"]
