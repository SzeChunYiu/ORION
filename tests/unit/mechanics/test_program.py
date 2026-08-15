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


def test_current_program_advances_to_parent_discipline_after_dependency_contracts():
    metrics = observe_current_mechanics_program()
    counts = dict(metrics.open_by_dimension)
    for closed in (MechanicDimension.VERIFICATION, MechanicDimension.FAILURE, MechanicDimension.OBSERVABILITY, MechanicDimension.HANDOFF, MechanicDimension.STATE, MechanicDimension.TRANSITION_MODEL, MechanicDimension.MATHEMATICS, MechanicDimension.METRICS, MechanicDimension.UNCERTAINTY, MechanicDimension.INVARIANTS, MechanicDimension.DEPENDENCIES):
        assert closed.value not in counts
    assert counts[MechanicDimension.PARENT_DISCIPLINE.value] == metrics.mechanic_count


def test_global_scheduler_is_breadth_first_on_parent_discipline_wave():
    questions = plan_current_program_questions(limit=20)
    assert len({item.mechanic_id for item in questions}) == 20
    assert all(item.dimension is MechanicDimension.PARENT_DISCIPLINE for item in questions)


def test_parent_discipline_wave_uses_parent_discipline_route_without_llm_planning():
    tasks = plan_current_program_research(limit=8)
    assert len(tasks) == 8
    assert all(item.query.route_kind is SearchRouteKind.PARENT_DISCIPLINE for item in tasks)
    assert all(item.query.text for item in tasks)
