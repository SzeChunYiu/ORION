from orion.mechanics import MechanicCell, UncertaintyKind, UncertaintyRepresentation, apply_default_uncertainty_plan, default_uncertainty_plan, generate_mechanic_questions


def test_uncertainty_plan_refuses_unlicensed_probability_collapse():
    plan = default_uncertainty_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    assert "only where calibrated" in plan.probability_policy
    by_kind = {item.kind: item for item in plan.rules}
    assert by_kind[UncertaintyKind.SEARCH_COVERAGE].default_representation is UncertaintyRepresentation.UNKNOWN
    assert by_kind[UncertaintyKind.RESPONSIBILITY_CAUSAL].default_representation is UncertaintyRepresentation.ALTERNATIVE_HYPOTHESES
    assert by_kind[UncertaintyKind.RESOURCE_CENSORING].default_representation is UncertaintyRepresentation.CANNOT_CHECK


def test_uncertainty_plan_closes_baseline_semantics_but_keeps_quantification_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_uncertainty_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "UNCERTAINTY" not in dimensions
    assert "INVARIANTS" in dimensions
    assert any("step-specific uncertainty" in item for item in updated.empirical_open_coordinates)
