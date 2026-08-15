from orion.core.search import SearchRouteKind
from orion.mechanics import (
    MechanicDimension,
    expanded_workflow_cells,
    observe_mechanics_program,
    plan_program_questions,
    plan_program_research,
)


def test_mechanics_program_exposes_development_numbers():
    cells = expanded_workflow_cells()
    metrics = observe_mechanics_program(cells)
    assert metrics.mechanic_count >= 59
    assert metrics.ready_mechanic_count == 0
    assert metrics.open_question_count >= 1200
    counts = dict(metrics.open_by_dimension)
    assert counts[MechanicDimension.VERIFICATION.value] == metrics.mechanic_count
    assert counts[MechanicDimension.FAILURE.value] == metrics.mechanic_count
    assert counts[MechanicDimension.OBSERVABILITY.value] == metrics.mechanic_count
    assert metrics.unknown_child_count == 0
    assert metrics.cycle_count == 0


def test_global_scheduler_is_breadth_first_not_one_cell_deep():
    cells = expanded_workflow_cells()
    questions = plan_program_questions(cells, limit=20)
    assert len({item.mechanic_id for item in questions}) == 20
    assert all(item.dimension is MechanicDimension.VERIFICATION for item in questions)


def test_global_questions_become_search_tasks_without_llm_planning():
    cells = expanded_workflow_cells()
    tasks = plan_program_research(cells, limit=8)
    assert len(tasks) == 8
    assert all(item.query.route_kind is SearchRouteKind.CROSS_DOMAIN for item in tasks)
    assert all(item.query.text for item in tasks)
