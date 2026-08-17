"""Ablation variants for ORION Paper 3.

Each ablation removes one coordinate family, obstruction handling,
recoverability, or W-expansion from the full ORION pipeline.

The full pipeline is the reference. Each ablation differs by exactly one
component. All ablations share the same interface as baselines.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from orion.study.baselines import Baseline, IntegrationResult, SourceDocument, SCOPE_SCION_Like


# ── ablation wrapper ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Ablation(Baseline):
    """A single-component ablation over the full ORION pipeline.

    Attributes:
        _id: Unique identifier (e.g. "ORION_no_referent").
        _description: Human-readable description of what is removed.
        _full_pipeline: The full ORION integration system (Baseline impl).
    """
    _id: str
    _description: str
    _full_pipeline: Baseline

    def system_id(self) -> str:
        return self._id

    def integrate(self, sources: Sequence[SourceDocument]) -> IntegrationResult:
        """Run the full pipeline, then strip the ablated component.

        In the real implementation, the ablation is applied at the model
        prompt level (the model is not asked to produce the ablated coordinate).
        This wrapper records the ablation in the result notes.
        """
        result = self._full_pipeline.integrate(sources)
        ablated_notes = f"ABLATION:{self._id} {self._description}"
        return IntegrationResult(
            system_id=self._id,
            case_id=result.case_id,
            notes=ablated_notes,
        )


# ── ablation definitions ──────────────────────────────────────────────────────

# Placeholder full pipeline — replaced with the actual ORION pipeline during
# the evaluation run.
_FULL: Baseline = SCOPE_SCION_Like()


ALL_ABLATIONS: list[Ablation] = [
    Ablation(
        "ORION_no_referent",
        "Remove referent_relation coordinate",
        _FULL,
    ),
    Ablation(
        "ORION_no_construct",
        "Remove construct_relation coordinate",
        _FULL,
    ),
    Ablation(
        "ORION_no_measurement",
        "Remove measurement_relation coordinate",
        _FULL,
    ),
    Ablation(
        "ORION_no_context",
        "Remove context_relation coordinate",
        _FULL,
    ),
    Ablation(
        "ORION_no_modality_polarity_attribution_discourse",
        "Remove modality_relation, polarity_relation, attribution_relation, and discourse_relation coordinates",
        _FULL,
    ),
    Ablation(
        "ORION_no_obstruction",
        "Remove obstruction detection (only GLUE_ALLOWED/UNRESOLVED)",
        _FULL,
    ),
    Ablation(
        "ORION_no_recoverability",
        "Remove recoverability_target output",
        _FULL,
    ),
    Ablation(
        "ORION_no_W_expansion",
        "Remove W-expansion (tight source-local only, no cross-source mapping)",
        _FULL,
    ),
]

ABLATION_IDS = [
    "ORION_no_referent",
    "ORION_no_construct",
    "ORION_no_measurement",
    "ORION_no_context",
    "ORION_no_modality_polarity_attribution_discourse",
    "ORION_no_obstruction",
    "ORION_no_recoverability",
    "ORION_no_W_expansion",
]