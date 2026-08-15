from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadinessEvidence:
    detects_self_failure: bool
    localizes_responsibility: bool
    searches_outside_incumbent_neighborhood: bool
    absorbs_external_knowledge: bool
    freezes_evaluator_before_outcome: bool
    challenger_beats_incumbent_development: bool
    challenger_passes_fresh_assurance: bool
    preserves_negative_history: bool
    scoped_promotion_only: bool


def assess_readiness(evidence: ReadinessEvidence) -> bool:
    """Conservative gate for moving from LLM-led bootstrap to governed Self-ORION."""

    return all(evidence.__dict__.values())
