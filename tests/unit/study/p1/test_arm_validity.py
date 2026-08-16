from __future__ import annotations

from orion.study.p1.arm_validity import (
    ArmVerdict,
    assess_arm_discrimination,
    assess_pair_discrimination,
)


def test_identical_systems_did_not_discriminate() -> None:
    """The observed case, reduced. On the frozen P1 pilot every mechanical
    system scored 5/90 and ORION reframed 0/90; H1 came back NOT_SUPPORTED with
    an interval of exactly [0.0000, 0.0000]. A paired bootstrap over identical
    vectors is zero by construction, so the statistics could not tell that null
    apart from a real one."""

    outcomes = {name: [1, 0, 0, 1, 0] for name in ("orion", "arex", "scion", "iris")}
    report = assess_arm_discrimination(outcomes)
    assert report.verdict is ArmVerdict.DID_NOT_DISCRIMINATE
    assert not report.permits_system_comparison
    assert report.distinct_behaviour_groups == 1
    assert len(report.largest_group) == 4


def test_one_differing_system_is_enough_to_discriminate() -> None:
    outcomes = {
        "orion": [1, 1, 0],
        "arex": [1, 0, 0],
        "scion": [1, 0, 0],
    }
    report = assess_arm_discrimination(outcomes)
    assert report.verdict is ArmVerdict.DISCRIMINATED
    assert report.permits_system_comparison
    assert report.distinct_behaviour_groups == 2


def test_a_single_system_cannot_be_compared_to_anything() -> None:
    report = assess_arm_discrimination({"orion": [1, 0]})
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert not report.permits_system_comparison


def test_an_empty_arm_is_cannot_check_not_a_null_result() -> None:
    report = assess_arm_discrimination({"orion": [], "arex": []})
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert "no outcomes recorded" in report.reasons[0]


def test_a_pair_that_never_differs_cannot_support_a_verdict() -> None:
    """A hypothesis verdict rests on one pair, so the pair is what must be
    checked. NOT_SUPPORTED asserts the subject is not better; CANNOT_CHECK
    asserts nothing was measured. Only the second is honest here."""

    report = assess_pair_discrimination([1, 0, 1], [1, 0, 1])
    assert report.verdict is ArmVerdict.DID_NOT_DISCRIMINATE


def test_mismatched_pair_lengths_refuse_rather_than_truncate() -> None:
    report = assess_pair_discrimination([1, 0, 1], [1, 0])
    assert report.verdict is ArmVerdict.CANNOT_CHECK
    assert "different lengths" in report.reasons[0]


def test_discrimination_is_about_the_vector_not_the_aggregate() -> None:
    """Two systems can share a rate while disagreeing case by case. That is a
    real difference the arm detected, and it must not be folded away — an
    aggregate-only check would call this degenerate."""

    report = assess_arm_discrimination({"a": [1, 0, 1, 0], "b": [0, 1, 0, 1]})
    assert report.verdict is ArmVerdict.DISCRIMINATED
    assert sum([1, 0, 1, 0]) == sum([0, 1, 0, 1])
