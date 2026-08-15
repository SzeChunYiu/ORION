from orion.mechanics import (
    MechanicCell,
    RetrySafety,
    TransitionDeterminism,
    apply_default_transition_plan,
    default_transition_plan,
    generate_mechanic_questions,
)


def test_transition_plan_declares_guarded_nondeterministic_and_retry_semantics():
    plan = default_transition_plan(
        MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    )
    assert any(
        item.determinism is TransitionDeterminism.EXTERNAL_NONDETERMINISTIC
        for item in plan.rules
    )
    assert any(
        item.retry_safety is RetrySafety.SIDE_EFFECT_GUARD_REQUIRED
        for item in plan.rules
    )
    assert all(item.preconditions and item.postconditions for item in plan.rules)
    assert "P(next_state,output,status)" in plan.state_relation


def test_transition_plan_keeps_step_specific_dynamics_question_provisionally_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_transition_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "TRANSITION_MODEL" in dimensions
    assert "TRANSITION_MODEL" in {item.value for item in updated.provisional_dimensions}
    assert "MATHEMATICS" in dimensions
    assert any(
        "step-specific transition relation" in item
        for item in updated.empirical_open_coordinates
    )
