"""Immutable evaluation-epoch manifest schema.

An epoch manifest is a sealed snapshot. This module ships the shape and refuses
to emit a populated live epoch: there are no executed cycles, so a non-empty
manifest would be a fabricated history.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orion.programme.activation import PREPARATORY_STATUS, UNBOUND_DIGEST
from orion.programme.identity import is_sha256, seal

EPOCH_MANIFEST_SCHEMA = "orion.programme.epoch-manifest.v1"


@dataclass(frozen=True)
class EpochManifest:
    """One evaluation epoch. Empty/unbound is the only honest current instance."""

    epoch_id: str
    sequence: int
    evaluator_artifact_hash: str = UNBOUND_DIGEST
    cycle_receipt_ids: tuple[str, ...] = ()
    object_layer_digest: str = UNBOUND_DIGEST
    search_universe_digest: str = UNBOUND_DIGEST
    method_layer_digest: str = UNBOUND_DIGEST
    frozen: bool = False


def epoch_manifest_payload(manifest: EpochManifest) -> dict[str, Any]:
    return seal(
        {
            "schema_version": EPOCH_MANIFEST_SCHEMA,
            "epoch_id": manifest.epoch_id,
            "sequence": manifest.sequence,
            "programme_status": PREPARATORY_STATUS,
            "evaluator_artifact_hash": manifest.evaluator_artifact_hash,
            "cycle_receipt_ids": list(manifest.cycle_receipt_ids),
            "object_layer_digest": manifest.object_layer_digest,
            "search_universe_digest": manifest.search_universe_digest,
            "method_layer_digest": manifest.method_layer_digest,
            "frozen": manifest.frozen,
            "live_epoch": False,
        }
    )


def validate_epoch_manifest(manifest: EpochManifest) -> tuple[str, ...]:
    errors: list[str] = []
    if not manifest.epoch_id.strip():
        errors.append("epoch_id is required")
    if manifest.sequence < 0:
        errors.append("epoch sequence must be non-negative")
    for field_name in (
        "evaluator_artifact_hash",
        "object_layer_digest",
        "search_universe_digest",
        "method_layer_digest",
    ):
        value = getattr(manifest, field_name)
        if not is_sha256(value):
            errors.append(f"{field_name} must be a SHA-256 digest")
    if manifest.frozen:
        errors.append("an epoch cannot be frozen while programme activation is withheld")
    if manifest.cycle_receipt_ids:
        errors.append("epoch manifest must not cite cycle receipts that have not been produced")
    bound_layers = [
        getattr(manifest, name) != UNBOUND_DIGEST
        for name in (
            "evaluator_artifact_hash",
            "object_layer_digest",
            "search_universe_digest",
            "method_layer_digest",
        )
    ]
    if any(bound_layers):
        errors.append("epoch layer digests must remain unbound until a host records a real epoch")
    return tuple(dict.fromkeys(errors))


def unexecuted_epoch_manifest() -> EpochManifest:
    return EpochManifest(epoch_id="phase4:epoch:unexecuted", sequence=0)


__all__ = [
    "EPOCH_MANIFEST_SCHEMA",
    "EpochManifest",
    "epoch_manifest_payload",
    "unexecuted_epoch_manifest",
    "validate_epoch_manifest",
]
