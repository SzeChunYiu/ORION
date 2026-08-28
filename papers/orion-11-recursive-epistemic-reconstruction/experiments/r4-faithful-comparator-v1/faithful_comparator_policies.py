"""ORION-11 R4 faithful-comparator arms.

Each arm is a *minimal competent* repair of one frozen v2.2.4 parent.  Every
frozen parent selects high-level repairs with ``_by_confidence(_high_repairs)[0]``
-- a single top-confidence pick -- and never iterates to an alternative when that
candidate fails admission.  Hidden-shift worlds make the top-confidence
high-level proposal a decoy by construction, so a non-iterating parent cannot
succeed, and every such parent collapses onto the same 0.49375 rate as a
cost-greedy picker.

Each arm below changes exactly ONE thing in its parent -- the single pick becomes
an ordered search under the admission test that parent already applies -- and
changes nothing else: same public world, same four-unit budget, same probe
ladder and branch structure, same scorer.
"""

from __future__ import annotations

from orion.study.p1_causal.absorbed_mechanics import (
    CounterfactualRepairCandidate,
    inclusion_minimal_successful_repairs,
)
from orion.study.p1_causal.necessity_cases import RepairLevel
from orion.study.p1_causal.necessity_engine import NecessityInteractor
from orion.study.p1_causal.necessity_policies import (
    NecessityPolicyOutcome,
    _by_confidence,
    _high_repairs,
    _outcome,
    _probe_by_prefix,
    _reopen_for_selected,
    _repairs_at,
)
from orion.study.p1_causal.necessity_policies_v3 import _expected_impact

_SOURCE_PROBE_PREFIX = "check whether the missing evidence"
_EXEC_PROBE_PREFIX = "check whether the current implementation"


def _search_high_level(session: NecessityInteractor, arm_id: str, note: str):
    """Iterate high-level candidates under the parent's own admission test.

    Returns an outcome on the first admissible candidate, or None if the budget
    is exhausted or no candidate is admissible.
    """
    for repair in _by_confidence(_high_repairs(session)):
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            return None
        if tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome(
                arm_id,
                session,
                repair.repair_id,
                note,
                reopened_ids=_reopen_for_selected(session, repair.repair_id),
            )
    return None


def darc_search_admitted_parent(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    """darc_r2act_dependency_parent, searching instead of taking one pick.

    Branch structure identical to the frozen parent: high-confidence gate, then
    the EVIDENCE/EXECUTION recovery ladder, then the high-level fallback.
    """
    arm = "darc_search_admitted_parent"
    if session.public.initial_high_level_confidence >= 0.80:
        found = _search_high_level(session, arm, "high_confidence_admissible_search")
        if found is not None:
            return found
    for level in (RepairLevel.EVIDENCE, RepairLevel.EXECUTION):
        candidates = _by_confidence(_repairs_at(session, level))
        if not candidates:
            continue
        tested = session.test_repair(candidates[0].repair_id)
        if tested is None:
            break
        if tested.response.target_success and tested.response.protected_sibling_ok:
            return _outcome(
                arm, session, candidates[0].repair_id, "lower_level_recovery"
            )
    found = _search_high_level(session, arm, "fallback_high_level_search")
    if found is not None:
        return found
    return _outcome(arm, session, None, "no_admissible_repair")


def activevoi_search_admitted_parent(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    """active_voi_repair_parent, searching at the terminal high-level step.

    The probe ladder and both early-exit branches are preserved exactly as in
    the frozen parent; only the final single high-level pick becomes a search.
    """
    arm = "activevoi_search_admitted_parent"
    source_probe = _probe_by_prefix(session, _SOURCE_PROBE_PREFIX)
    source = session.run_probe(source_probe.probe_id)
    if source is None:
        return _outcome(arm, session, None, "no_budget_source_probe")
    if source.response.observation == "SOURCE_GAP":
        repair = _by_confidence(_repairs_at(session, RepairLevel.EVIDENCE))[0]
        tested = session.test_repair(repair.repair_id)
        selected = (
            repair.repair_id if tested and tested.response.target_success else None
        )
        return _outcome(arm, session, selected, "source_probe")

    exec_probe = _probe_by_prefix(session, _EXEC_PROBE_PREFIX)
    execution = session.run_probe(exec_probe.probe_id)
    if execution is None:
        return _outcome(arm, session, None, "no_budget_execution_probe")
    if execution.response.observation == "EXECUTION_GAP":
        repair = _by_confidence(_repairs_at(session, RepairLevel.EXECUTION))[0]
        tested = session.test_repair(repair.repair_id)
        selected = (
            repair.repair_id if tested and tested.response.target_success else None
        )
        return _outcome(arm, session, selected, "execution_probe")

    found = _search_high_level(session, arm, "lower_levels_ruled_out_then_search")
    if found is not None:
        return found
    return _outcome(arm, session, None, "no_admissible_high_level_repair")


def causalflow_sibling_admitted_parent(
    session: NecessityInteractor,
) -> NecessityPolicyOutcome:
    """causalflow parent allowed to USE the protected_sibling_ok it already observes.

    Identical to the frozen parent except that inclusion-minimality is computed
    with ``require_protected_ok=True`` -- the flag the frozen parent's own
    docstring records as observed but deliberately unused.
    """
    arm = "causalflow_sibling_admitted_parent"
    public_by_id = {item.repair_id: item for item in session.public.repairs}
    observed: list[CounterfactualRepairCandidate] = []
    for repair in session.public.repairs:
        tested = session.test_repair(repair.repair_id)
        if tested is None:
            break
        observed.append(
            CounterfactualRepairCandidate(
                repair_id=repair.repair_id,
                edited_atoms=frozenset({f"{repair.level.value}:{repair.coordinate}"}),
                target_success=bool(tested.response.target_success),
                protected_ok=bool(tested.response.protected_sibling_ok),
            )
        )
    minimal = inclusion_minimal_successful_repairs(
        observed, require_protected_ok=True
    )
    if not minimal.repair_ids:
        return _outcome(arm, session, None, "no_admissible_counterfactual_repair")
    selected_id = sorted(
        minimal.repair_ids,
        key=lambda rid: (-public_by_id[rid].proposal_confidence, rid),
    )[0]
    selected = public_by_id[selected_id]
    reopened = (
        _expected_impact(session, selected.coordinate)
        if selected.level.value in {"FORMULATION", "SEARCH_UNIVERSE"}
        else ()
    )
    return _outcome(
        arm,
        session,
        selected_id,
        "causal_inclusion_minimal_sibling_admitted",
        reopened_ids=reopened,
    )


R4_NEW_ARMS = (
    darc_search_admitted_parent,
    activevoi_search_admitted_parent,
    causalflow_sibling_admitted_parent,
)

__all__ = ["R4_NEW_ARMS"] + [fn.__name__ for fn in R4_NEW_ARMS]
