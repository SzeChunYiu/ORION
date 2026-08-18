"""Compose belief → discriminator → intervention → license. No LLM."""

from __future__ import annotations

from dataclasses import dataclass

from .belief import AuthorityClass, BeliefState, MUTATION_BEARING, uniform_unresolved
from .cases import PublicMemberView, World
from .discriminator import (
    DEFAULT_PROBES,
    ProbeCatalog,
    ProbeSpec,
    select_discriminator,
)
from .intervention import (
    InterventionSpec,
    apply_intervention,
    apply_probe,
    match_outcome,
)
from .licensing import EpistemicAction, LicenseDecision, request_action


@dataclass(frozen=True)
class CausalCycle:
    view: PublicMemberView
    state: BeliefState
    decisions: tuple[LicenseDecision, ...]
    cannot_check: bool
    notes: tuple[str, ...]

    def to_payload(self) -> dict:
        return {
            "member_id": self.view.member_id,
            "authority_class": self.state.authority_class.value,
            "intervention_backed": self.state.intervention_backed,
            "cannot_check": self.cannot_check,
            "decisions": [item.to_payload() for item in self.decisions],
            "notes": list(self.notes),
            "public_view": self.view.to_payload(),
        }


_INTERVENTION_BY_CLASS: dict[AuthorityClass, InterventionSpec] = {
    AuthorityClass.EVIDENCE: InterventionSpec(
        intervention_id="acquire_omitted_source",
        hypothesized=AuthorityClass.EVIDENCE,
        predicted_observable="source_present",
        expected_direction="appear",
    ),
    AuthorityClass.SEARCH_UNIVERSE: InterventionSpec(
        intervention_id="expand_active_domains",
        hypothesized=AuthorityClass.SEARCH_UNIVERSE,
        predicted_observable="source_in_universe",
        expected_direction="appear",
    ),
    AuthorityClass.EXECUTION: InterventionSpec(
        intervention_id="repair_tooling",
        hypothesized=AuthorityClass.EXECUTION,
        predicted_observable="rerun_agrees",
        expected_direction="appear",
    ),
    AuthorityClass.FORMULATION: InterventionSpec(
        intervention_id="rewrite_implicated_coordinate",
        hypothesized=AuthorityClass.FORMULATION,
        predicted_observable="residual_removed",
        expected_direction="appear",
    ),
}


def run_cycle(
    view: PublicMemberView,
    world: World,
    *,
    catalog: ProbeCatalog | None = None,
    max_probes: int = 2,
) -> CausalCycle:
    """Mechanical cycle. ``world`` is host-side and must not be logged as gold.

    The public probe/intervention allowlists are a hard candidate capability
    boundary. An empty allowlist stays empty; the cycle never falls back to a
    broader catalog or runs an unadvertised intervention.
    """

    if not isinstance(view, PublicMemberView):
        raise TypeError("candidates receive PublicMemberView only")
    menu = catalog or ProbeCatalog(DEFAULT_PROBES)
    allowed = [probe for probe in menu.probes if probe.probe_id in view.allowed_probe_ids]
    probes = ProbeCatalog(tuple(allowed))
    state = uniform_unresolved(evidence_ids=(f"surface:{view.member_id}",))
    notes: list[str] = []
    used: set[str] = set()
    for _ in range(max_probes):
        choice = select_discriminator(state, probes, used=frozenset(used))
        if choice.probe is None:
            notes.append(choice.reason)
            break
        probe: ProbeSpec = choice.probe
        if probe.probe_id not in view.allowed_probe_ids:
            notes.append(f"probe_not_allowed:{probe.probe_id}")
            used.add(probe.probe_id)
            continue
        reported = world.probe_reports.get(probe.probe_id)
        state = apply_probe(state, probe, reported)
        used.add(probe.probe_id)
        notes.append(f"ran_probe:{probe.probe_id}")
    hypothesized = state.authority_class
    if hypothesized is not AuthorityClass.UNRESOLVED:
        spec = _INTERVENTION_BY_CLASS[hypothesized]
        if spec.intervention_id not in view.allowed_intervention_ids:
            notes.append(f"intervention_not_allowed:{spec.intervention_id}")
        else:
            observed = world.intervention_directions.get(spec.intervention_id, "vanish")
            outcome = match_outcome(spec, observed)
            state = apply_intervention(state, spec, outcome)
            notes.append(f"ran_intervention:{spec.intervention_id}:{outcome.matched}")
    decisions = tuple(request_action(state, action) for action in EpistemicAction)
    cannot_check = (
        state.authority_class is AuthorityClass.UNRESOLVED
        or (
            state.authority_class in MUTATION_BEARING
            and not state.intervention_backed
        )
        or any(
            item.cannot_check
            for item in decisions
            if item.action in MUTATING_FOR_CHECK
        )
    )
    return CausalCycle(
        view=view,
        state=state,
        decisions=decisions,
        cannot_check=cannot_check,
        notes=tuple(notes),
    )


MUTATING_FOR_CHECK = frozenset(
    {
        EpistemicAction.REWRITE_FORMULATION,
        EpistemicAction.EXPAND_SEARCH_UNIVERSE,
        EpistemicAction.BROAD_WM_MUTATION,
        EpistemicAction.REWRITE_METHOD,
    }
)
