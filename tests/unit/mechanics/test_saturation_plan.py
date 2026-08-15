from orion.mechanics import (
    MechanicCell,
    SaturationCoordinate,
    apply_default_saturation_plan,
    default_saturation_plan,
    generate_mechanic_questions,
)


def test_saturation_plan_requires_formulation_parent_domain_and_failure_flatness():
    plan = default_saturation_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    coordinates = {item.coordinate for item in plan.coordinates}
    assert {SaturationCoordinate.KNOWLEDGE, SaturationCoordinate.FORMULATION, SaturationCoordinate.PARENT_DOMAIN, SaturationCoordinate.FAILURE_EXPERIENCE} <= coordinates
    assert plan.minimum_consecutive_flat_rounds >= 2
    assert not plan.absolute_complete
    assert any("omission" in item for item in plan.required_audits)
    assert any("mask current framework" in item for item in plan.false_saturation_challenges)


def test_saturation_plan_closes_stopping_spec_but_not_empirical_saturation():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_saturation_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "SATURATION" not in dimensions
    assert "ACTIONS" in dimensions
    assert any("prospective false-saturation recall" in item for item in updated.empirical_open_coordinates)
