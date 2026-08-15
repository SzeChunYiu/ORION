from orion.mechanics import (
    MechanicCell,
    MetricDirection,
    MetricRole,
    apply_default_metric_plan,
    default_metric_plan,
    generate_mechanic_questions,
)


def test_metric_plan_preserves_noncompensatory_gates_and_root_transport():
    plan = default_metric_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    gates = [item for item in plan.requirements if item.role is MetricRole.BLOCKING_GATE]
    assert gates
    assert all(item.spec.direction is MetricDirection.NON_COMPENSATORY_GATE for item in gates)
    assert any(item.role is MetricRole.ROOT_EFFECTIVENESS for item in plan.requirements)
    assert "No universal scalar score" in plan.scalar_aggregation_policy
    assert all(item.root_transport_requirement for item in plan.requirements)


def test_metric_plan_keeps_step_specific_construct_question_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_metric_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "METRICS" in dimensions
    assert "UNCERTAINTY" in dimensions
    assert any("metric validity" in item for item in updated.empirical_open_coordinates)
