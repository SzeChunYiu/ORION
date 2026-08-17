"""Intervention-supported update.

A probe updates support and never sets ``intervention_backed``.
An intervention sets ``intervention_backed`` only when the observable moves
in the predicted direction for a named class.
"""

from __future__ import annotations

from dataclasses import dataclass

from .belief import (
    ALL_AUTHORITY_CLASSES,
    AuthorityClass,
    BeliefState,
    UnauthorizedBeliefMutation,
    replace_masses,
    uniform_unresolved,
)
from .discriminator import ProbeSpec


@dataclass(frozen=True)
class InterventionSpec:
    intervention_id: str
    hypothesized: AuthorityClass
    predicted_observable: str
    expected_direction: str
    cost: int = 1

    def __post_init__(self) -> None:
        if self.hypothesized is AuthorityClass.UNRESOLVED:
            raise UnauthorizedBeliefMutation(
                "an intervention must name a resolved class"
            )
        if self.expected_direction not in {"increase", "decrease", "appear", "vanish"}:
            raise ValueError(
                f"{self.intervention_id}: unknown direction {self.expected_direction}"
            )


@dataclass(frozen=True)
class InterventionOutcome:
    intervention_id: str
    observed_observable: str
    observed_direction: str
    matched: bool

    def to_payload(self) -> dict:
        return {
            "intervention_id": self.intervention_id,
            "observed_observable": self.observed_observable,
            "observed_direction": self.observed_direction,
            "matched": self.matched,
        }


def apply_probe(
    state: BeliefState,
    probe: ProbeSpec,
    reported: AuthorityClass | None,
) -> BeliefState:
    """Update support from a probe. Authority is never granted here."""

    notes = (*state.notes, f"probe:{probe.probe_id}")
    probe_ids = (*state.probe_ids, probe.probe_id)
    if reported is None or probe.blind or reported not in probe.separates:
        return BeliefState(
            supports=state.supports,
            evidence_ids=state.evidence_ids,
            probe_ids=probe_ids,
            intervention_ids=state.intervention_ids,
            intervention_backed=False,
            notes=(*notes, "probe_inconclusive"),
        )
    masses = {item: state.mass(item) for item in ALL_AUTHORITY_CLASSES}
    masses[reported] += 1.0
    masses[AuthorityClass.UNRESOLVED] *= 0.5
    evidence_id = f"probe:{probe.probe_id}:{reported.value}"
    support_ids = {item.class_id: item.support_ids for item in state.supports}
    support_ids[reported] = (*support_ids[reported], evidence_id)
    updated = replace_masses(
        state,
        masses,
        evidence_ids=(*state.evidence_ids, evidence_id),
        probe_ids=probe_ids,
        intervention_ids=state.intervention_ids,
        intervention_backed=False,
        notes=notes,
        support_ids=support_ids,
    )
    # Probe path must remain not intervention-backed even if unique-argmax.
    if updated.intervention_backed:
        raise UnauthorizedBeliefMutation("a probe granted authority")
    return updated


def apply_intervention(
    state: BeliefState,
    spec: InterventionSpec,
    outcome: InterventionOutcome,
) -> BeliefState:
    """Authority is granted only on a matched, diagnosis-specific intervention."""

    if outcome.intervention_id != spec.intervention_id:
        raise UnauthorizedBeliefMutation("intervention outcome id mismatch")
    notes = (*state.notes, f"intervention:{spec.intervention_id}")
    intervention_ids = (*state.intervention_ids, spec.intervention_id)
    masses = {item: state.mass(item) for item in ALL_AUTHORITY_CLASSES}
    if not outcome.matched:
        masses[spec.hypothesized] *= 0.5
        masses[AuthorityClass.UNRESOLVED] += 0.5
        return replace_masses(
            state,
            masses,
            intervention_ids=intervention_ids,
            intervention_backed=False,
            notes=(*notes, "intervention_missed"),
        )
    masses[spec.hypothesized] += 2.0
    masses[AuthorityClass.UNRESOLVED] *= 0.25
    evidence_id = f"intervention:{spec.intervention_id}:{spec.hypothesized.value}"
    support_ids = {
        item.class_id: item.support_ids for item in state.supports
    }
    support_ids[spec.hypothesized] = (
        *support_ids[spec.hypothesized],
        evidence_id,
    )
    return replace_masses(
        state,
        masses,
        evidence_ids=(*state.evidence_ids, evidence_id),
        intervention_ids=intervention_ids,
        intervention_backed=True,
        notes=(*notes, "intervention_matched"),
        support_ids=support_ids,
    )


def match_outcome(spec: InterventionSpec, observed_direction: str) -> InterventionOutcome:
    matched = observed_direction == spec.expected_direction
    return InterventionOutcome(
        intervention_id=spec.intervention_id,
        observed_observable=spec.predicted_observable,
        observed_direction=observed_direction,
        matched=matched,
    )


# Imported by tests that assert the initial state constructor still exists.
_ = uniform_unresolved
