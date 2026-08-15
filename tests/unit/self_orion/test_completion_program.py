from orion.mechanics import MechanicDimension
from orion.self_orion import (
    completion_program_cells,
    next_completion_questions,
    observe_completion_program,
)

_PROVISIONAL_STEP_SPECIFIC = {
    MechanicDimension.VERIFICATION.value,
    MechanicDimension.FAILURE.value,
    MechanicDimension.OBSERVABILITY.value,
    MechanicDimension.HANDOFF.value,
    MechanicDimension.STATE.value,
    MechanicDimension.TRANSITION_MODEL.value,
    MechanicDimension.MATHEMATICS.value,
    MechanicDimension.DEPENDENCIES.value,
    MechanicDimension.METRICS.value,
    MechanicDimension.UNCERTAINTY.value,
    MechanicDimension.INVARIANTS.value,
    MechanicDimension.PARENT_DISCIPLINE.value,
    MechanicDimension.SEARCH_COVERAGE.value,
    MechanicDimension.SATURATION.value,
}


def test_completion_controller_closes_new_layers_without_fabricating_step_specific_answers():
    state = observe_completion_program()
    metrics = state.metrics
    counts = dict(metrics.open_by_dimension)

    assert metrics.mechanic_count >= 59
    assert metrics.unknown_child_count == 0
    assert metrics.cycle_count == 0
    assert getattr(metrics, "unknown_dependency_count", 0) == 0
    assert getattr(metrics, "dependency_cycle_count", 0) == 0
    assert getattr(metrics, "mixed_cycle_count", 0) == 0

    # The continuation closes actions/objective/optimization/resources/diagnosis/
    # storage/provenance/engineering at the generic specification layer. Codex's
    # MechanicCell.v1 deliberately leaves universal envelopes provisional for these
    # fourteen step-specific dimensions, so generic scaffolding cannot manufacture
    # closure.
    assert set(counts) == _PROVISIONAL_STEP_SPECIFIC
    assert all(counts[dimension] == metrics.mechanic_count for dimension in _PROVISIONAL_STEP_SPECIFIC)
    assert metrics.open_question_count == metrics.mechanic_count * len(_PROVISIONAL_STEP_SPECIFIC)
    assert metrics.ready_mechanic_count == 0
    assert not state.benchmarkable

    frontier = next_completion_questions(limit=8)
    assert frontier
    assert all(item.dimension.value in _PROVISIONAL_STEP_SPECIFIC for item in frontier)


def test_universal_completion_layers_do_not_erase_empirical_open_coordinates():
    cells = completion_program_cells()
    assert cells
    assert all(cell.empirical_open_coordinates for cell in cells)
    assert all(
        any(
            "step-specific" in item
            or "actual" in item
            or "prospective" in item
            or "parent-domain" in item
            for item in cell.empirical_open_coordinates
        )
        for cell in cells
    )
