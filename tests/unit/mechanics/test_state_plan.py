from orion.mechanics import (
    MechanicCell,
    StateMutability,
    StateRole,
    apply_default_state_plan,
    default_state_plan,
    generate_mechanic_questions,
)


def test_state_plan_binds_replay_identity_and_transition_controlled_working_state():
    plan = default_state_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    roles = {item.role for item in plan.variables}
    assert StateRole.INPUT_SNAPSHOT in roles
    assert StateRole.WORKING in roles
    assert StateRole.OUTPUT_SNAPSHOT in roles
    assert any(
        item.mutability is StateMutability.TRANSITION_CONTROLLED
        for item in plan.variables
    )
    assert "hidden mutation" in plan.mutation_rule


def test_state_plan_keeps_step_specific_state_question_provisionally_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_state_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "STATE" in dimensions
    assert "STATE" in {item.value for item in updated.provisional_dimensions}
    assert "TRANSITION_MODEL" in dimensions
    assert any(
        "step-specific scientific/algorithmic state" in item
        for item in updated.empirical_open_coordinates
    )
