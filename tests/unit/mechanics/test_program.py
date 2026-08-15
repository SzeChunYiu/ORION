from orion.core.search import SearchRouteKind
from orion.mechanics import MechanicDimension, expanded_workflow_cells, observe_current_mechanics_program, observe_mechanics_program, plan_current_program_questions, plan_current_program_research


def test_raw_decomposition_exposes_development_numbers():
    metrics = observe_mechanics_program(expanded_workflow_cells())
    assert metrics.mechanic_count >= 59
    assert metrics.ready_mechanic_count == 0
    assert metrics.open_question_count >= 1200
    counts = dict(metrics.open_by_dimension)
    assert counts[MechanicDimension.VERIFICATION.value] == metrics.mechanic_count
    assert counts[MechanicDimension.FAILURE.value] == metrics.mechanic_count
    assert metrics.unknown_child_count == 0
    assert metrics.cycle_count == 0


def test_current_program_advances_to_uncertainty():
    metrics = observe_current_mechanics_program()
    counts = dict(metrics.open_by_dimension)
    for closed in (MechanicDimension.VERIFICATION, MechanicDimension.FAILURE, MechanicDimension.OBSERVABILITY, MechanicDimension.HANDOFF, MechanicDimension.STATE, MechanicDimension.TRANSITION_MODEL, MechanicDimension.MATHEMATICS, MechanicDimension.METRICS):
        assert closed.value not in counts
    assert counts[MechanicDimension.UNCERTAINTY.value] == metrics.mechanic_count


def test_global_scheduler_is_breadth_first_not_one_cell_deep():
    questions = plan_current_program_questions(limit=20)
    assert len({item.mechanic_id for item in questions}) == 20
    assert all(item.dimension is MechanicDimension.UNCERTAINTY for item in questions)


def test_current_global_questions_become_search_tasks_without_llm_planning():
    tasks = plan_current_program_research(limit=8)
    assert len(tasks) == 8
    assert all(item.query.route_kind is SearchRouteKind.FUNCTION_ONLY for item in tasks)
    assert all(item.query.text for item in tasks)
