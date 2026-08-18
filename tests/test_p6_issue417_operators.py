from orion.transfer.v2.p6_method_fibres import (
    CompositionContract,
    CompositionKind,
    CompositionStatus,
    StructuralRelation,
    check_composition,
    relation,
)


def test_conditional_composition_requires_right_preconditions():
    clean = CompositionContract(
        CompositionKind.CONDITIONAL,
        right_preconditions=("guard-established",),
        left_guarantees=("guard-established",),
    )
    blocked = CompositionContract(
        CompositionKind.CONDITIONAL,
        right_preconditions=("guard-established", "invariant-preserved"),
        left_guarantees=("guard-established",),
    )
    assert check_composition(clean)[0] is CompositionStatus.COMPATIBLE
    status, reasons = check_composition(blocked)
    assert status is CompositionStatus.BLOCKED
    assert "RIGHT_PRECONDITION_NOT_GUARANTEED:invariant-preserved" in reasons


def test_generalization_is_directional_and_not_equivalence():
    assert relation(
        base_preconditions=("finite", "ordered"),
        candidate_preconditions=("finite",),
        base_effects=("solve",),
        candidate_effects=("solve",),
        requested=StructuralRelation.GENERALIZES,
        obligations_satisfied=True,
    ) is StructuralRelation.GENERALIZES
    assert relation(
        base_preconditions=("finite", "ordered"),
        candidate_preconditions=("finite",),
        base_effects=("solve",),
        candidate_effects=("solve",),
        requested=StructuralRelation.EQUIVALENT,
        obligations_satisfied=True,
    ) is StructuralRelation.UNRESOLVED
