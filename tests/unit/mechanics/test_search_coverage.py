from orion.core.search import SearchRouteKind
from orion.mechanics import (
    MechanicCell,
    apply_default_search_coverage_plan,
    default_search_coverage_plan,
    generate_mechanic_questions,
)


def test_search_coverage_plan_includes_ontology_escape_and_omission_routes():
    plan = default_search_coverage_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    kinds = {item.route_kind for item in plan.obligations}
    assert {
        SearchRouteKind.FUNCTION_ONLY,
        SearchRouteKind.PARENT_DISCIPLINE,
        SearchRouteKind.HISTORICAL_PRECURSOR,
        SearchRouteKind.MATHEMATICAL_EQUIVALENT,
        SearchRouteKind.IMPLEMENTATION_ANALOG,
        SearchRouteKind.LITERATURE_BRIDGE,
        SearchRouteKind.ADVERSARIAL_OMISSION,
        SearchRouteKind.FRESHNESS,
    } <= kinds
    assert "Different query strings are not independent" in plan.route_independence_rule
    assert "never proves" in plan.coverage_claim_boundary


def test_search_coverage_plan_closes_route_family_spec_but_not_saturation():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_search_coverage_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "SEARCH_COVERAGE" in dimensions
    assert "SATURATION" in dimensions
    assert any("actual route execution" in item for item in updated.empirical_open_coordinates)
