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


def test_current_program_advances_to_actions_after_saturation_spec():
    metrics = observe_current_mechanics_program()
    counts = dict(metrics.open_by_dimension)
    assert MechanicDimension.SATURATION.value not in counts
    assert counts[MechanicDimension.ACTIONS.value] == metrics.mechanic_count


def test_action_wave_is_mechanically_scheduled():
    tasks = plan_current_program_research(limit=8)
    assert len(tasks) == 8
    assert all(item.query.route_kind is SearchRouteKind.FUNCTION_ONLY for item in tasks)
    assert all(item.query.text for item in tasks)
