from orion.mechanics import (
    AuthorityTransport,
    FieldPresence,
    MechanicCell,
    apply_default_handoff_plan,
    default_handoff_plan,
    generate_mechanic_questions,
)


def test_default_handoff_has_explicit_presence_schema_and_authority_semantics():
    plan = default_handoff_plan(MechanicCell("SEARCH.test", "Find evidence.", "fixture"))
    assert plan.schema_version
    assert all(item.presence is FieldPresence.REQUIRED for item in plan.fields)
    evidence = next(item for item in plan.fields if item.field_id == "evidence_ids")
    assert evidence.authority_transport is AuthorityTransport.EXPLICIT_CERTIFICATE_ONLY
    assert "may not infer" in plan.missing_required_semantics


def test_handoff_plan_closes_envelope_question_but_retains_step_specific_payload_open():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_default_handoff_plan(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "HANDOFF" not in dimensions
    assert "STATE" in dimensions
    assert all(field.schema_ref for field in updated.handoff_fields)
    assert any("step-specific handoff payload" in item for item in updated.empirical_open_coordinates)
