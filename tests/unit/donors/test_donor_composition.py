from __future__ import annotations

from orion.donors import normal_orion_donor_registry, orion_q_donor_registry
from orion.donors.composition import normal_orion_donor_graph, orion_q_donor_graph


def test_normal_donor_graph_is_bound_to_full_44_capability_registry():
    registry = normal_orion_donor_registry()
    graph = normal_orion_donor_graph()
    graph.validate(registry)
    assert len(registry.capabilities) == 44
    assert len(graph.routes) == 2
    assert graph.registry_digest == registry.digest
    assert all(route.hard_obligations for route in graph.routes)


def test_orion_q_graph_contains_all_eight_supersystem_composition_routes():
    registry = orion_q_donor_registry()
    graph = orion_q_donor_graph()
    graph.validate(registry)
    assert len(registry.capabilities) == 57
    assert len(graph.routes) == 8
    assert {route.route_id for route in graph.routes} == {
        "q:problem-representation-access-specialist",
        "q:staged-verification-resource",
        "q:successful-trace-abstraction",
        "q:failed-trace-scoped-recovery",
        "q:conjecture-to-proof",
        "q:stack-resource-closure",
        "q:qec-design-evaluation",
        "q:algorithm-to-stack-optimization",
    }
    assert all(route.hard_obligations for route in graph.routes)
    assert all(
        route.as_dict()["grants_scientific_authority"] is False
        for route in graph.routes
    )
