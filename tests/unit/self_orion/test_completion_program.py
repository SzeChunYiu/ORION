from orion.self_orion import completion_program_cells, next_completion_questions, observe_completion_program


def test_completion_controller_makes_every_registered_cell_structurally_benchmarkable():
    state = observe_completion_program()
    assert state.metrics.mechanic_count >= 59
    assert state.metrics.unknown_child_count == 0
    assert state.metrics.cycle_count == 0
    assert state.metrics.open_question_count == 0
    assert state.metrics.ready_mechanic_count == state.metrics.mechanic_count
    assert state.benchmarkable
    assert next_completion_questions(limit=8) == ()


def test_benchmarkable_does_not_mean_empirically_closed():
    cells = completion_program_cells()
    assert cells
    assert all(cell.empirical_open_coordinates for cell in cells)
    assert all(any("step-specific" in item or "actual" in item or "prospective" in item or "parent-domain" in item for item in cell.empirical_open_coordinates) for cell in cells)
