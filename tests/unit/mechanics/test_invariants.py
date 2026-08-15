from orion.mechanics import (
    InvariantKind,
    MechanicCell,
    apply_default_invariant_plan,
    default_invariant_plan,
    generate_mechanic_questions,
)


def test_invariant_plan_preserves_authority_history_reopen_and_root_progress_guards():
    plan = default_invariant_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    kinds = {item.kind for item in plan.invariants}
    assert {InvariantKind.AUTHORITY, InvariantKind.HISTORY, InvariantKind.REOPEN, InvariantKind.ROOT_PROGRESS, InvariantKind.FAILURE_LEARNING} <= kinds
    assert any("Budget exhaustion" in item.statement for item in plan.invariants)
    assert any("hidden mutation" in item.statement for item in plan.invariants)


def test_invariant_plan_keeps_step_specific_obligations_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_invariant_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "INVARIANTS" in dimensions
    assert "DEPENDENCIES" in dimensions
    assert any("step-specific safety/correctness" in item for item in updated.empirical_open_coordinates)
