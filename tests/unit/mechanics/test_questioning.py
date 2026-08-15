from orion.mechanics import (
    DimensionWaiver,
    MechanicCell,
    MechanicDimension,
    generate_mechanic_questions,
    mechanical_workflow_backlog,
)


def test_incomplete_cell_mechanically_exposes_load_bearing_questions():
    cell = MechanicCell("SEARCH.test", "Find relevant evidence.", "one research fibre")
    dimensions = {item.dimension for item in generate_mechanic_questions(cell)}
    required = {
        MechanicDimension.OBSERVABILITY,
        MechanicDimension.MATHEMATICS,
        MechanicDimension.METRICS,
        MechanicDimension.HANDOFF,
        MechanicDimension.FAILURE,
        MechanicDimension.STORAGE,
        MechanicDimension.ENGINEERING,
        MechanicDimension.PARENT_DISCIPLINE,
        MechanicDimension.SATURATION,
    }
    assert required <= dimensions


def test_dimension_can_only_disappear_through_evidence_or_explicit_waiver():
    cell = MechanicCell(
        "PURE.test",
        "A pure deterministic transform.",
        "known-answer fixture",
        waivers=(DimensionWaiver(MechanicDimension.ENGINEERING, "no side effects or concurrent runtime in this fixture"),),
    )
    dimensions = {item.dimension for item in generate_mechanic_questions(cell)}
    assert MechanicDimension.ENGINEERING not in dimensions
    assert MechanicDimension.MATHEMATICS in dimensions


def test_orion_workflow_is_intentionally_open_not_fake_complete():
    backlog = mechanical_workflow_backlog()
    assert len(backlog) > 100
    assert any(item.mechanic_id == "SEARCH.v1" and item.dimension is MechanicDimension.OBSERVABILITY for item in backlog)
    assert any(item.mechanic_id == "ABSORB.v1" and item.dimension is MechanicDimension.PARENT_DISCIPLINE for item in backlog)
    assert any(item.mechanic_id == "SATURATE_BOUNDED.v3" and item.dimension is MechanicDimension.SATURATION for item in backlog)
