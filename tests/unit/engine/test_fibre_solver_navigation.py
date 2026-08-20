from __future__ import annotations

from orion.core.problem import Problem
from orion.engine.fibre_solver import select_fibre_solver
from orion.engine.navigation import PaperParityNavigator


def test_normal_fibre_selection_is_deterministic_and_non_authorizing():
    plan = PaperParityNavigator.normal().plan(
        Problem("normal-fibre", "Investigate a search coverage failure.", initial_domain_ids=("science",))
    )
    route = next(item for item in plan.fibre_routes if item.mechanic_id == "SEARCH.v1")
    selection = select_fibre_solver(route, PaperParityNavigator.normal().donor_registry)
    selection.validate()
    assert selection.primary_solver_id
    assert selection.verification_required is True
    assert selection.unsigned()["grants_scientific_authority"] is False


def test_orion_q_fibre_selection_places_external_donor_before_native_fallback():
    navigator = PaperParityNavigator.orion_q()
    plan = navigator.plan(
        Problem(
            "q-fibre",
            "Find a quantum algorithm route under proof and resource obligations.",
            initial_domain_ids=("quantum",),
        )
    )
    route = next(item for item in plan.fibre_routes if item.mechanic_id == "REFRAME.v1")
    selection = select_fibre_solver(route, navigator.donor_registry)
    selection.validate()
    assert selection.donor_solver_ids
    assert selection.primary_solver_id.startswith("host:DONOR_EXECUTE:orion-q:")
    assert any(item == "native-mechanic:REFRAME.v1" for item in selection.fallback_solver_ids)
