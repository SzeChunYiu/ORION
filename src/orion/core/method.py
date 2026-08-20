from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MethodState:
    """M_t: current ORION method identity, navigation and protected evaluator binding."""

    method_version: str
    operator_ids: tuple[str, ...] = ()
    evaluator_id: str | None = None
    self_development_enabled: bool = False
    navigation_profile: str = ""
    navigation_plan_digest: str = ""
    atomization_digest: str = ""
    donor_registry_id: str = ""
    donor_registry_digest: str = ""
    donor_composition_graph_id: str = ""
    donor_composition_graph_digest: str = ""
    active_fibre_ids: tuple[str, ...] = ()
    deferred_donor_obligation_ids: tuple[str, ...] = ()
