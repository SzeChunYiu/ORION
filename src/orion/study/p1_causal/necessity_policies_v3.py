"""Round-F strengthened P1 necessity policy registry.

Adds a donor-faithful *mechanism-level* CausalFlow/HERALD parent on top of the
v2.2 policy set.  It spends the same four-unit budget to observe all available
counterfactual repairs, retains inclusion-minimal target-flipping repairs, and
chooses among them using only public proposal confidence.  It deliberately does
not use ORION's science-specific protected-invariant or K/W/M-level necessity
criteria; those are the residual under test.
"""

from __future__ import annotations

from .absorbed_mechanics import (
    CounterfactualRepairCandidate,
    inclusion_minimal_successful_repairs,
)
from .necessity_engine import NecessityInteractor
from .necessity_policies import (
    ABLATION_ARMS as BASE_ABLATION_ARMS,
    RUNNABLE_ARMS as BASE_RUNNABLE_ARMS,
    NecessityPolicyOutcome,
)


def _expected_impact(
    session: NecessityInteractor,
    coordinate: str,
) -> tuple[str, ...]:
    direct = {
        item.closure_id
        for item in session.public.dependencies
        if item.declared_coordinate == coordinate
    }
    selected = set(direct)
    changed = True
    while changed:
        changed = False
        for item in session.public.dependencies:
            if item.closure_id in selected:
                continue
            if any(parent in selected for parent in item.parent_ids):
                selected.add(item.closure_id)
                changed = True
    return tuple(
        item.closure_id
        for item in session.public.dependencies
        if item.closure_id in selected
    )


def causalflow_minimal_counterfactual_parent(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    """Absorb causal/inclusion-minimal counterfactual repair.

    All repair interventions are attempted under the same four-unit frozen
    budget.  Successful interventions are converted to atomic edit sets and the
    inclusion-minimal set is retained.  Selection then uses public confidence.
    Protected sibling validity is *observed* in the host response but is not a
    selection criterion here; making it part of the scientific admission rule
    is the residual P1 tests prospectively.
    """

    public_by_id = {item.repair_id: item for item in session.public.repairs}
    observed: list[CounterfactualRepairCandidate] = []
    for repair in session.public.repairs:
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        observed.append(
            CounterfactualRepairCandidate(
                repair_id=repair.repair_id,
                edited_atoms=frozenset(
                    {f"{repair.level.value}:{repair.coordinate}"}
                ),
                target_success=bool(tested.response.target_success),
                protected_ok=bool(tested.response.protected_sibling_ok),
            )
        )
    minimal = inclusion_minimal_successful_repairs(observed)
    if not minimal.repair_ids:
        return NecessityPolicyOutcome(
            arm_id="causalflow_minimal_counterfactual_parent",
            selected_repair_id=None,
            reopened_ids=(),
            tested_repair_ids=tuple(getattr(session, "tested_repair_ids", ())),
            tested_probe_ids=tuple(getattr(session, "tested_probe_ids", ())),
            spent_budget=float(getattr(session, "spent_budget", 0.0)),
            notes=("no_successful_counterfactual_repair",),
        )
    selected_id = sorted(
        minimal.repair_ids,
        key=lambda repair_id: (
            -public_by_id[repair_id].proposal_confidence,
            repair_id,
        ),
    )[0]
    selected = public_by_id[selected_id]
    reopened = (
        _expected_impact(session, selected.coordinate)
        if selected.level.value in {"FORMULATION", "SEARCH_UNIVERSE"}
        else ()
    )
    return NecessityPolicyOutcome(
        arm_id="causalflow_minimal_counterfactual_parent",
        selected_repair_id=selected_id,
        reopened_ids=reopened,
        tested_repair_ids=tuple(getattr(session, "tested_repair_ids", ())),
        tested_probe_ids=tuple(getattr(session, "tested_probe_ids", ())),
        spent_budget=float(getattr(session, "spent_budget", 0.0)),
        notes=("causal_inclusion_minimal_target_flip",),
    )


# Keep ORION last for readability; insert the new strongest donor parent directly
# before it.  No existing arm is removed.
RUNNABLE_ARMS = (
    *BASE_RUNNABLE_ARMS[:-1],
    causalflow_minimal_counterfactual_parent,
    BASE_RUNNABLE_ARMS[-1],
)
ABLATION_ARMS = BASE_ABLATION_ARMS


__all__ = [
    "ABLATION_ARMS",
    "RUNNABLE_ARMS",
    "causalflow_minimal_counterfactual_parent",
]
