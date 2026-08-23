from __future__ import annotations

from orion import OrionSolver
from orion.core.problem import Problem
from orion.engine.paper_parity_solver import PaperParityOrionSolver
from orion.engine.solver import SolverConfig
from orion.providers.llm import CallableLLMProvider
from orion.providers.retrieval import InMemoryRetrievalProvider
from orion.providers.verification import InMemoryVerificationProvider
from orion.runtime import OrionRuntime


def _runtime(profile: str = "orion") -> OrionRuntime:
    return OrionRuntime.from_providers(
        llm=CallableLLMProvider(lambda request: '{"queries":[]}', model_id="parity-test"),
        retrieval=InMemoryRetrievalProvider({}),
        verification=InMemoryVerificationProvider(frozenset()),
        config=SolverConfig(max_iterations=1),
        navigation_profile=profile,
    )


def test_top_level_orion_solver_is_paper_parity_solver():
    assert OrionSolver is PaperParityOrionSolver


def test_public_runtime_binds_normal_navigation_into_m_state():
    runtime = _runtime("orion")
    result = runtime.solve(
        Problem(
            "parity-runtime",
            "What can be established?",
            initial_domain_ids=("science",),
        )
    )
    plan = runtime.navigation_plan
    assert plan is not None
    assert plan.profile == "orion"
    assert result.final_state.method.navigation_plan_digest == plan.plan_digest
    assert result.final_state.method.atomization_digest == plan.atomization_digest
    assert result.final_state.method.donor_registry_digest == plan.donor_registry_digest
    assert result.final_state.method.donor_registry_id == "orion:donors:normal:v2"
    assert result.final_state.method.donor_composition_graph_id == "orion:donor-composition:normal:v1"
    assert result.final_state.method.donor_composition_graph_digest
    assert result.final_state.method.active_fibre_ids == plan.active_fibre_ids
    assert result.final_state.metadata


def test_public_runtime_can_bind_orion_q_donor_profile():
    runtime = _runtime("orion-q")
    result = runtime.solve(
        Problem(
            "parity-runtime-q",
            "Find a quantum method under proof and resource obligations.",
            initial_domain_ids=("quantum",),
        )
    )
    plan = runtime.navigation_plan
    assert plan is not None
    assert plan.profile == "orion-q"
    assert result.final_state.method.donor_registry_id == "orion:donors:orion-q:v2"
    assert result.final_state.method.donor_composition_graph_id == "orion:donor-composition:orion-q:v1"
    assert result.final_state.method.donor_composition_graph_digest
    assert any(
        donor_id.startswith("orion-q:")
        for route in plan.fibre_routes
        for donor_id in route.executable_donor_ids
    )
