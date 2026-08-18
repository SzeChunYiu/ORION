"""Deterministic tranche-0 summary for P9 structural-world information views."""

from __future__ import annotations

from .identifiability import analyze_identifiability
from .structural_world import (
    P9StructuralWorld,
    ViewMode,
    failure_history_pair,
    relation_semantics_pair,
    transport_gluing_pair,
)


def bootstrap_worlds() -> tuple[P9StructuralWorld, ...]:
    """Return the frozen tranche-0 hostile worlds in deterministic family order."""

    return (
        *relation_semantics_pair(),
        *transport_gluing_pair(),
        *failure_history_pair(),
    )


def bootstrap_information_lattice() -> dict[str, object]:
    """Summarize which progressively richer views identify the frozen gold."""

    worlds = bootstrap_worlds()
    reports: dict[str, object] = {}
    for mode in ViewMode:
        report = analyze_identifiability(worlds, mode)
        reports[mode.value] = {
            "sample_count": report.sample_count,
            "unique_fingerprint_count": report.unique_fingerprint_count,
            "collision_count": len(report.collisions),
            "is_identifying": report.is_identifying,
            "collisions": [
                {
                    "fingerprint": collision.fingerprint,
                    "world_ids": list(collision.world_ids),
                    "targets": list(collision.targets),
                }
                for collision in report.collisions
            ],
        }

    return {
        "schema": "P9.bootstrap-information-lattice.v0",
        "world_count": len(worlds),
        "world_ids": [world.world_id for world in worlds],
        "views": reports,
        "scientific_authority": "NONE_MODEL_EVALUATION_ONLY",
    }
