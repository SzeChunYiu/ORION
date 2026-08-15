from orion.mechanics import DependencyKind, MechanicCell, apply_default_dependency_plan, default_dependency_plan, generate_mechanic_questions


def test_dependency_plan_binds_identity_failure_propagation_and_no_implicit_fallback():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture", dependency_ids=("FRAME.v1",))
    plan = default_dependency_plan(cell)
    assert plan.dependencies[0].kind is DependencyKind.MECHANIC
    assert "exact dependency" in plan.dependencies[0].identity_binding
    assert "propagated" in plan.dependencies[0].failure_propagation
    assert "No implicit fallback" in plan.dependencies[0].fallback_semantics


def test_root_dependency_is_derived_from_declared_children():
    cell = MechanicCell("ROOT.test", "Compose children.", "fixture", child_mechanic_ids=("A", "B"))
    updated = apply_default_dependency_plan(cell)
    assert updated.dependency_ids == ("A", "B")
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "DEPENDENCIES" not in dimensions
    assert "PARENT_DISCIPLINE" in dimensions
