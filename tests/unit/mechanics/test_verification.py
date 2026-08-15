from orion.mechanics import (
    MechanicCell,
    VerificationMethod,
    VerificationStage,
    apply_default_verification_plan,
    default_verification_plan,
    generate_mechanic_questions,
)


def test_default_verification_plan_separates_plan_from_evidence():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    plan = default_verification_plan(cell)
    assert {item.method for item in plan.obligations} >= {
        VerificationMethod.ANALYSIS,
        VerificationMethod.TEST,
        VerificationMethod.FRESH_TRANSFER,
    }
    assert any(item.stage is VerificationStage.EMPIRICAL_PROMOTION for item in plan.obligations)
    # A plan contains obligation identities, not a fabricated PASS receipt.
    assert all(item.required_artifact_kind for item in plan.obligations)


def test_attaching_verification_plan_closes_only_the_specification_question():
    cell = MechanicCell("SEARCH.test", "Find evidence.", "fixture")
    before = {item.dimension.value for item in generate_mechanic_questions(cell)}
    after = {item.dimension.value for item in generate_mechanic_questions(apply_default_verification_plan(cell))}
    assert "VERIFICATION" in before
    assert "VERIFICATION" not in after
    assert "FAILURE" in after
    assert "OBSERVABILITY" in after
