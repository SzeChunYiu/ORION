from orion.mechanics import MathematicalFamily, MechanicCell, apply_candidate_mathematical_formulation, candidate_mathematical_formulation, generate_mechanic_questions


def test_candidate_math_refuses_convenience_assumptions():
    formulation = candidate_mathematical_formulation(MechanicCell("DIAGNOSE.test", "Diagnose a failure.", "fixture"))
    assert MathematicalFamily.HYPOTHESIS_SET in formulation.families
    assert any("fabricated probability" in item for item in formulation.forbidden_implicit_assumptions)
    assert "set-valued" in formulation.fallback_semantics


def test_candidate_math_is_a_reopenable_specification_not_final_validity_claim():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    updated = apply_candidate_mathematical_formulation(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "MATHEMATICS" not in dimensions
    assert "METRICS" in dimensions
    assert any("adequacy of the candidate mathematical" in item for item in updated.empirical_open_coordinates)
