from __future__ import annotations

from orion.core.problem import Problem
from orion.donors import DonorExecutionMode, normal_orion_donor_registry, orion_q_donor_registry
from orion.engine.navigation import PaperParityNavigator


CORE = {
    "ORION_SOLVE.v1",
    "FRAME.v1",
    "SEARCH.v1",
    "ABSORB.v1",
    "RECONSTRUCT.v1",
    "DETECT.v1",
    "DIAGNOSE.v1",
    "REFRAME.v1",
    "REOPEN.v1",
    "SATURATE_BOUNDED.v3",
}


def test_normal_orion_registry_retains_all_public_and_engineering_donors():
    registry = normal_orion_donor_registry()
    assert len(registry.capabilities) == 44  # 24 public families + E1-E20
    assert registry.registry_id == "orion:donors:normal:v2"
    assert registry.digest
    assert all(item.can_carry_scientific_authority is False for item in registry.capabilities)
    deferred = registry.deferred_reopen_obligations()
    assert deferred
    assert all(item.reopen_trigger for item in deferred)
    ids = {item.capability_id for item in registry.capabilities}
    assert "rakl:context_compiler" in ids
    assert "rakl:route_family_health" in ids
    assert {f"rakl-engineering:E{i}" for i in range(1, 21)} <= ids


def test_orion_q_inherits_all_normal_donors_and_all_quantum_specialists():
    normal = normal_orion_donor_registry()
    quantum = orion_q_donor_registry()
    assert len(quantum.capabilities) == 57
    assert quantum.registry_id == "orion:donors:orion-q:v2"
    assert len(quantum.capabilities) == len(normal.capabilities) + 13
    normal_ids = {item.capability_id for item in normal.capabilities}
    quantum_ids = {item.capability_id for item in quantum.capabilities}
    assert normal_ids < quantum_ids
    q_rows = [item for item in quantum.capabilities if item.capability_id.startswith("orion-q:")]
    assert len(q_rows) == 13
    assert all(item.execution_mode is DonorExecutionMode.EXTERNAL_HOST for item in q_rows)
    assert all(item.host_capability == "DONOR_EXECUTE" for item in q_rows)
    assert all(item.can_carry_scientific_authority is False for item in q_rows)


def test_normal_navigation_retains_complete_atom_graph_and_active_core():
    problem = Problem(
        problem_id="paper-parity-normal",
        question="Find the responsible research fibre and solve a scientific evidence gap.",
        scope="Use recursive decomposition, donor-first search and bounded saturation.",
        initial_domain_ids=("science",),
        success_criteria=("Do not silently drop unresolved donor or fibre obligations.",),
    )
    plan = PaperParityNavigator.normal().plan(problem)
    plan.validate()
    assert len(plan.atoms) >= 59
    assert CORE <= set(plan.active_fibre_ids)
    assert plan.profile == "orion"
    assert plan.donor_registry_id == "orion:donors:normal:v2"
    assert plan.plan_digest
    assert plan.atomization_digest
    assert plan.donor_registry_digest
    assert plan.deferred_donor_obligation_ids
    assert tuple(item.mechanic_id for item in plan.fibre_routes) == plan.active_fibre_ids


def test_quantum_navigation_uses_quantum_supersystem_without_dropping_core():
    problem = Problem(
        problem_id="paper-parity-q",
        question="Find a verified quantum algorithm route under resource and proof obligations.",
        scope="Use strongest donor composition before claiming an ORION-only residual.",
        initial_domain_ids=("quantum",),
        success_criteria=("No novelty credit for donor-owned behavior.",),
    )
    plan = PaperParityNavigator.orion_q().plan(problem)
    plan.validate()
    assert CORE <= set(plan.active_fibre_ids)
    assert plan.profile == "orion-q"
    assert plan.donor_registry_id == "orion:donors:orion-q:v2"
    donor_ids = {
        donor_id
        for route in plan.fibre_routes
        for donor_id in route.executable_donor_ids
    }
    assert any(item.startswith("orion-q:") for item in donor_ids)
    assert any(item.startswith("rakl:") for item in donor_ids)
