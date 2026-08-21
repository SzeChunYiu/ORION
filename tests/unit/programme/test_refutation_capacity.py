"""A mechanized check must not report a pass no false theory could have failed."""

from __future__ import annotations

import pytest

from orion.programme.guard_exercise import GuardVerdictReason
from orion.programme.records import Outcome
from orion.programme.refutation_capacity import (
    AxisSensitivity,
    FalseTheory,
    MechanizedCheck,
    ModelPoint,
    RefutationCapacity,
    TheoryDivergence,
    UnrefutableCheck,
    assess_theory_coverage,
    axis_sensitivity,
    divergence_of,
    measure_refutation_capacity,
    require_refutable,
)

SPACE: tuple[ModelPoint, ...] = tuple(
    {"label": label, "left": left, "right": right}
    for label in ("a", "b")
    for left in (False, True)
    for right in (False, True)
)


def reference(point: ModelPoint) -> bool:
    return bool(point["left"]) and bool(point["right"])


def restated(point: ModelPoint) -> bool:
    """Extensionally the reference, written the other way round."""

    return not (not point["left"] or not point["right"])


def _theory(theory_id: str, rule) -> FalseTheory:
    return FalseTheory(theory_id=theory_id, breaks="a stated claim", rule=rule)


DROPS_RIGHT = _theory("drops_right", lambda point: bool(point["left"]))
ALWAYS_TRUE = _theory("always_true", lambda point: True)
READS_LABEL = _theory("reads_label", lambda point: point["label"] == "a")


def _real_check() -> MechanizedCheck:
    """Rejects any rule that disagrees with the reference anywhere in the space."""

    return MechanizedCheck(
        check_id="total_agreement",
        asserts="the rule agrees with the reference on every enumerated point",
        accepts=lambda rule: all(rule(point) == reference(point) for point in SPACE),
    )


def _tautological_check() -> MechanizedCheck:
    """P6's shape: a counter over a condition that compares an expression to itself."""

    return MechanizedCheck(
        check_id="self_comparison",
        asserts="the rule agrees with a copy of itself on every enumerated point",
        accepts=lambda rule: not any(rule(point) != rule(point) for point in SPACE),
    )


def _asserting_check() -> MechanizedCheck:
    """A checker script's shape: it raises rather than returning False."""

    def accepts(rule) -> bool:
        for point in SPACE:
            assert rule(point) == reference(point)
        return True

    return MechanizedCheck(check_id="asserting", asserts="same, by assert", accepts=accepts)


def _measure(check: MechanizedCheck, theories) -> RefutationCapacity:
    return measure_refutation_capacity(
        check,
        reference=reference,
        reference_id="reference",
        theories=theories,
        space=SPACE,
    )


def test_check_that_rejects_every_false_theory_passes() -> None:
    capacity = _measure(_real_check(), (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL))

    assert capacity.outcome is Outcome.PASS
    assert not capacity.blocks
    assert capacity.survivors == ()
    assert set(capacity.refuted) == {"drops_right", "always_true", "reads_label"}
    assert capacity.exercise.opportunities == 3
    assert capacity.exercise.violations == 0


def test_tautological_check_accepts_every_false_theory_and_fails() -> None:
    capacity = _measure(_tautological_check(), (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL))

    assert capacity.outcome is Outcome.FAIL
    assert capacity.blocks
    assert len(capacity.survivors) == 3
    assert capacity.assessment.reason is GuardVerdictReason.VIOLATED


def _partial_check() -> MechanizedCheck:
    """Has real capacity, and a blind spot: it never looks where ``right`` is false."""

    return MechanizedCheck(
        check_id="right_only",
        asserts="the rule agrees with the reference wherever right holds",
        accepts=lambda rule: all(
            rule(point) == reference(point) for point in SPACE if point["right"]
        ),
    )


def test_a_check_with_a_blind_spot_still_has_capacity() -> None:
    """Per check the question is only whether anything could fail it."""

    capacity = _measure(_partial_check(), (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL))

    assert capacity.outcome is Outcome.PASS
    assert capacity.survivors == ("drops_right",)
    assert set(capacity.refuted) == {"always_true", "reads_label"}


def test_panel_coverage_catches_the_theory_no_check_rejects() -> None:
    """The blind spot is a property of the panel, and each check can point elsewhere."""

    theories = (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL)
    capacities = (_measure(_partial_check(), theories), _measure(_partial_check(), theories))

    coverage = assess_theory_coverage(capacities, label="panel")

    assert coverage.outcome is Outcome.FAIL
    assert coverage.blocks
    assert coverage.unrefuted == ("drops_right",)
    assert coverage.live == ("drops_right", "always_true", "reads_label")


def test_panel_coverage_passes_when_some_check_rejects_each_theory() -> None:
    theories = (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL)
    capacities = (_measure(_partial_check(), theories), _measure(_real_check(), theories))

    coverage = assess_theory_coverage(capacities, label="panel")

    assert coverage.outcome is Outcome.PASS
    assert coverage.unrefuted == ()


def test_panel_coverage_of_an_all_paraphrase_register_cannot_check() -> None:
    capacities = (_measure(_real_check(), (_theory("restated", restated),)),)

    coverage = assess_theory_coverage(capacities, label="panel")

    assert coverage.outcome is Outcome.CANNOT_CHECK
    assert coverage.live == ()


def test_panel_coverage_refuses_checks_measured_over_different_registers() -> None:
    capacities = (
        _measure(_real_check(), (DROPS_RIGHT, ALWAYS_TRUE)),
        _measure(_real_check(), (DROPS_RIGHT,)),
    )

    with pytest.raises(ValueError, match="different registers"):
        assess_theory_coverage(capacities, label="panel")


def test_assertion_error_counts_as_a_refutation() -> None:
    capacity = _measure(_asserting_check(), (DROPS_RIGHT,))

    assert capacity.outcome is Outcome.PASS
    assert capacity.refuted == ("drops_right",)


def test_a_type_error_is_not_a_refutation() -> None:
    """A mutant killed by the interpreter was not killed by the theorem."""

    def accepts(rule) -> bool:
        for point in SPACE:
            if rule(point) is None:
                raise TypeError("rule returned None")
        return True

    check = MechanizedCheck(check_id="typed", asserts="the rule returns a verdict", accepts=accepts)
    returns_none = _theory("returns_none", lambda point: None if point["left"] else False)

    with pytest.raises(TypeError):
        _measure(check, (returns_none,))


def test_theory_identical_to_the_reference_is_not_an_opportunity() -> None:
    """The independent-verifier case: a paraphrase cannot refute anything."""

    capacity = _measure(_real_check(), (_theory("restated", restated), DROPS_RIGHT))

    assert capacity.inert_theories == ("restated",)
    assert capacity.exercise.opportunities == 1
    assert capacity.refuted == ("drops_right",)


def test_register_of_only_identical_theories_cannot_check() -> None:
    capacity = _measure(_real_check(), (_theory("restated", restated),))

    assert capacity.outcome is Outcome.CANNOT_CHECK
    assert capacity.blocks
    assert capacity.assessment.reason is GuardVerdictReason.NEVER_EXERCISED
    assert capacity.exercise.opportunities == 0


def test_empty_register_refuses_rather_than_passing() -> None:
    with pytest.raises(UnrefutableCheck, match="no false theory is registered"):
        _measure(_real_check(), ())


def test_check_that_rejects_the_reference_is_a_misregistration() -> None:
    inverted = MechanizedCheck(
        check_id="inverted",
        asserts="the rule disagrees with the reference everywhere",
        accepts=lambda rule: all(rule(point) != reference(point) for point in SPACE),
    )

    with pytest.raises(ValueError, match="rejects reference"):
        _measure(inverted, (DROPS_RIGHT,))


def test_check_that_rejects_a_paraphrase_is_not_reading_behaviour() -> None:
    """Rejecting an extensionally identical rule means the check reads its identity."""

    by_identity = MechanizedCheck(
        check_id="by_identity",
        asserts="the rule is the reference object",
        accepts=lambda rule: rule is reference,
    )

    with pytest.raises(ValueError, match="not a function of the rule's behaviour"):
        _measure(by_identity, (_theory("restated", restated),))


def test_pass_cannot_be_paired_with_a_vacuity_reason() -> None:
    """Inherited from GuardAssessment, pinned here because it is the substitution."""

    capacity = _measure(_real_check(), (_theory("restated", restated),))

    assert capacity.assessment.reason.is_vacuity
    assert capacity.outcome is not Outcome.PASS


def test_divergence_counts_the_points_a_theory_moves() -> None:
    divergence = divergence_of(
        DROPS_RIGHT.rule, theory_id="drops_right", reference=reference, space=SPACE
    )

    assert divergence.points == 8
    assert divergence.points_changed == 2
    assert divergence.applied
    assert divergence.divergence_rate == pytest.approx(0.25)


def test_divergence_of_a_paraphrase_is_zero() -> None:
    divergence = divergence_of(restated, theory_id="restated", reference=reference, space=SPACE)

    assert divergence.points_changed == 0
    assert not divergence.applied


def test_an_axis_no_verdict_depends_on_is_inert() -> None:
    sensitivity = axis_sensitivity("label", reference=reference, space=SPACE)

    assert sensitivity.varied
    assert sensitivity.inert
    assert sensitivity.comparable_pairs == 4
    assert sensitivity.verdict_changing_pairs == 0
    assert sensitivity.multiplier == 2


def test_an_axis_the_verdict_reads_is_not_inert() -> None:
    sensitivity = axis_sensitivity("left", reference=reference, space=SPACE)

    assert not sensitivity.inert
    assert sensitivity.verdict_changing_pairs == 2
    assert sensitivity.multiplier == 1


def test_a_constant_axis_is_not_reported_as_inert() -> None:
    """Never varied is not the same as varied and ignored."""

    space = tuple({"fixed": "only", "left": left, "right": True} for left in (False, True))
    sensitivity = axis_sensitivity("fixed", reference=reference, space=space)

    assert not sensitivity.varied
    assert not sensitivity.inert


def test_axis_absent_from_a_point_is_refused() -> None:
    space = SPACE + ({"left": True, "right": True},)

    with pytest.raises(ValueError, match="cannot be held fixed"):
        axis_sensitivity("label", reference=reference, space=space)


def test_require_refutable_names_the_tautological_check() -> None:
    theories = (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL)
    capacities = (_measure(_real_check(), theories), _measure(_tautological_check(), theories))

    with pytest.raises(UnrefutableCheck) as caught:
        require_refutable(capacities, label="fixture")

    assert "self_comparison" in str(caught.value)
    assert "reject no declared false theory" in str(caught.value)


def test_require_refutable_names_the_theory_the_panel_misses() -> None:
    theories = (DROPS_RIGHT, ALWAYS_TRUE, READS_LABEL)
    capacities = (_measure(_partial_check(), theories),)

    with pytest.raises(UnrefutableCheck) as caught:
        require_refutable(capacities, label="fixture")

    assert "rejected by no check (drops_right)" in str(caught.value)


def test_require_refutable_names_a_register_of_only_paraphrases() -> None:
    capacities = (_measure(_real_check(), (_theory("restated", restated),)),)

    with pytest.raises(UnrefutableCheck) as caught:
        require_refutable(capacities, label="fixture")

    assert "no live falsifier" in str(caught.value)


def test_require_refutable_passes_a_fully_refuting_panel() -> None:
    capacities = (_measure(_real_check(), (DROPS_RIGHT, ALWAYS_TRUE)),)

    require_refutable(capacities, label="fixture")


def test_require_refutable_refuses_an_empty_panel() -> None:
    with pytest.raises(UnrefutableCheck, match="empty check panel"):
        require_refutable((), label="fixture")


def test_a_false_theory_must_say_what_it_breaks() -> None:
    with pytest.raises(ValueError, match="state which claim this theory breaks"):
        FalseTheory(theory_id="unnamed", breaks="  ", rule=reference)


def test_a_check_must_say_what_it_asserts() -> None:
    with pytest.raises(ValueError, match="state what this check asserts"):
        MechanizedCheck(check_id="silent", asserts="", accepts=lambda rule: True)


def test_divergence_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        TheoryDivergence(theory_id="bad", points=4, points_changed=5)


def test_axis_sensitivity_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        AxisSensitivity(axis="bad", values=2, comparable_pairs=1, verdict_changing_pairs=2)


def test_capacity_json_carries_the_register_it_was_measured_over() -> None:
    payload = _measure(_tautological_check(), (DROPS_RIGHT, ALWAYS_TRUE)).as_json()

    assert payload["outcome"] == "FAIL"
    assert payload["survivors"] == ["drops_right", "always_true"]
    assert [item["theory_id"] for item in payload["divergences"]] == [
        "drops_right",
        "always_true",
    ]
