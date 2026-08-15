import pytest

from orion.mechanics import (
    MechanicCell,
    ObservationClass,
    ObservationSpec,
    apply_default_observation_plan,
    default_observation_plan,
    generate_mechanic_questions,
)


def test_runtime_telemetry_cannot_mint_scientific_authority():
    with pytest.raises(ValueError, match="cannot directly create scientific authority"):
        ObservationSpec(
            "o",
            "SEARCH.test",
            ObservationClass.RUNTIME_TELEMETRY,
            "latency",
            "clock",
            "s",
            "completion",
            "clock resolution",
            "runtime control",
            may_create_scientific_authority=True,
        )


def test_default_observation_plan_is_runtime_baseline_not_scientific_measurement():
    plan = default_observation_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    assert len(plan.observations) >= 6
    assert all(item.observation_class is not ObservationClass.SCIENTIFIC_MEASUREMENT for item in plan.observations)
    assert all(not item.may_create_scientific_authority for item in plan.observations)
    assert any(item.quantity_or_measurand == "wall-clock execution latency" for item in plan.observations)


def test_observation_plan_closes_runtime_observability_but_keeps_measurement_validity_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_observation_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "OBSERVABILITY" not in dimensions
    assert "METRICS" in dimensions
    assert any("measurement validity" in item for item in updated.empirical_open_coordinates)
