from orion.core.search import SearchRouteKind
from orion.mechanics import MechanicCell, MechanicDimension, plan_mechanic_research


def test_mechanical_questions_become_search_queries_without_an_llm():
    cell = MechanicCell("SEARCH.test", "Find relevant knowledge.", "one fibre")
    tasks = plan_mechanic_research(cell, limit=30)
    by_dimension = {item.dimension: item for item in tasks}
    assert by_dimension[MechanicDimension.PARENT_DISCIPLINE].query.route_kind is SearchRouteKind.PARENT_DISCIPLINE
    assert by_dimension[MechanicDimension.SEARCH_COVERAGE].query.route_kind is SearchRouteKind.ADVERSARIAL_OMISSION
    assert by_dimension[MechanicDimension.SATURATION].query.route_kind is SearchRouteKind.LITERATURE_BRIDGE
    assert by_dimension[MechanicDimension.MATHEMATICS].query.route_kind is SearchRouteKind.FUNCTION_ONLY
    assert all(item.query.text for item in tasks)
