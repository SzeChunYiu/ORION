from orion.mechanics import (
    MechanicCell,
    MechanicRunStatus,
    apply_default_failure_plan,
    default_failure_plan,
    generate_mechanic_questions,
)


def test_failure_plan_separates_observation_effect_cause_detection_and_recovery():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    plan = default_failure_plan(cell)
    assert len(plan.modes) >= 6
    assert any(item.outcome is MechanicRunStatus.BLOCKED for item in plan.modes)
    assert any(item.outcome is MechanicRunStatus.CANNOT_CHECK for item in plan.modes)
    assert any(item.outcome is MechanicRunStatus.PARTIAL for item in plan.modes)
    for mode in plan.modes:
        assert mode.propagated_effects
        assert mode.cause_hypotheses
        assert mode.detection_signals
        assert mode.detection_rule
        assert mode.recovery_actions
        assert mode.falsifier


def test_failure_plan_keeps_step_specific_failure_question_provisionally_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    before = {item.dimension.value for item in generate_mechanic_questions(cell)}
    updated = apply_default_failure_plan(cell)
    after = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "FAILURE" in before
    assert "FAILURE" in after
    assert "FAILURE" in {item.value for item in updated.provisional_dimensions}
    assert "DIAGNOSIS" in after
    assert any(
        "step-specific failure-mode" in item
        for item in updated.empirical_open_coordinates
    )
