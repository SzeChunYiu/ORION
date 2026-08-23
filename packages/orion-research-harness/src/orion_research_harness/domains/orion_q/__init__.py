"""ORION-Q campaigns for the shared research harness."""

from __future__ import annotations

from copy import deepcopy

from .max_r6 import MAX_R6_CAMPAIGN_MANIFEST as _RAW_MAX_R6_CAMPAIGN_MANIFEST


def _phase_scoped_manifest():
    """Return the canonical exported manifest with phase-local bindings only.

    The source manifest intentionally shares binding vocabulary across N0/N1/N2,
    but the strict harness contract requires every phase to bind only hypotheses
    present in that phase. Filtering is structural normalization, not a gate
    relaxation: no hypothesis, mechanic, observation, capability, threshold, or
    protected-reference rule is changed.
    """

    manifest = deepcopy(_RAW_MAX_R6_CAMPAIGN_MANIFEST)
    for phase in manifest["phases"].values():
        hypotheses = phase.get("responsibility_hypotheses")
        bindings = phase.get("responsibility_bindings")
        if not isinstance(hypotheses, list) or not isinstance(bindings, dict):
            continue
        active = {str(row["hypothesis_id"]) for row in hypotheses}
        phase["responsibility_bindings"] = {
            str(hypothesis_id): list(mechanic_ids)
            for hypothesis_id, mechanic_ids in bindings.items()
            if str(hypothesis_id) in active
        }
    return manifest


MAX_R6_CAMPAIGN_MANIFEST = _phase_scoped_manifest()

__all__ = ["MAX_R6_CAMPAIGN_MANIFEST"]
