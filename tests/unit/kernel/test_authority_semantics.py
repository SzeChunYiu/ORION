from __future__ import annotations

from orion.kernel.gate import AnswerAuthority, AnswerGrading, EvidenceUseAssessment
from orion.mechanics.model import MechanicDimension


def _grading(**kwargs) -> AnswerGrading:
    return AnswerGrading(
        record_id="r1",
        mechanic_id="m1",
        dimension=MechanicDimension.INPUTS,
        authority=AnswerAuthority.EVIDENCE_BOUND,
        **kwargs,
    )


def test_evidence_bound_does_not_claim_support() -> None:
    """Content binding establishes that a citation is authentic. It establishes
    nothing about whether that content supports the claim it is offered for.

    The hostile battery for issue #59 made this concrete: an answer asserting a
    claim while citing an artifact that explicitly CONTRADICTS it still graded
    EVIDENCE_BOUND and folded into the cell. The name overclaimed. The axis is
    now explicit and unestablished by default, so a reader of a grading can see
    the difference instead of inferring a guarantee from a word.
    """

    grading = _grading()
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND
    assert grading.support_established is None
    assert grading.influence_established is None


def test_unestablished_is_none_and_never_false() -> None:
    """None means "not checked"; False would mean "checked and absent". A gate
    that cannot perform the check must not report the stronger of the two."""

    grading = _grading()
    assert grading.support_established is not False
    assert grading.influence_established is not False


def test_a_caller_that_can_establish_support_may_say_so() -> None:
    """The axes are set by whoever can compute them, not by the gate. Nothing in
    the kernel sets them True, because nothing in the kernel can."""

    grading = _grading(support_established=True, influence_established=False)
    assert grading.support_established is True
    assert grading.influence_established is False
    assert grading.applicable


def test_a_required_prerequisite_that_was_never_checked_blocks_promotion() -> None:
    """Recording an axis is not gating on it. An axis nothing consults is a
    note, and the first version of this repair only wrote the note.

    None fails a requirement exactly as False does: a prerequisite that was
    demanded and never evaluated has not been met, and only True discharges it.
    Otherwise "we did not look" would promote as readily as "we looked and it
    was fine" — the exact conflation the ladder exists to prevent.
    """

    unchecked = _grading(required_prerequisites=frozenset({"support"}))
    assert unchecked.support_established is None
    assert unchecked.unmet_prerequisites == ("support_not_established",)
    assert not unchecked.applicable

    established = _grading(
        required_prerequisites=frozenset({"support"}), support_established=True
    )
    assert established.unmet_prerequisites == ()
    assert established.applicable


def test_prerequisites_are_non_compensatory() -> None:
    """A perfect answer on every other axis does not buy off a missing one."""

    grading = _grading(
        required_prerequisites=frozenset({"support", "influence"}),
        support_established=True,
        influence_established=False,
    )
    assert grading.authority is AnswerAuthority.EVIDENCE_BOUND
    assert grading.unmet_prerequisites == ("influence_not_established",)
    assert not grading.applicable


def test_nothing_is_required_by_default() -> None:
    """Requirements are declared by whoever imposes them. A gate that demanded
    support universally would refuse every answer in the repository, which is
    solving the problem by measuring nothing."""

    assert _grading().unmet_prerequisites == ()
    assert _grading().applicable


def test_protected_assessment_requires_independent_lineage_and_exact_evidence() -> None:
    assessment = EvidenceUseAssessment(
        assessment_id="a1",
        record_id="r1",
        evaluator_id="protected-evaluator",
        evaluator_revision="c" * 64,
        lane="protected-lane",
        evidence_refs=("e1",),
        support_established=True,
        influence_established=True,
        frozen_at_round=0,
    )
    assert assessment.evaluator_revision == "c" * 64
    assert assessment.support_established is True
    assert assessment.influence_established is True


def test_unknown_prerequisite_is_never_silently_ignored() -> None:
    grading = _grading(required_prerequisites=frozenset({"support", "unknown"}))
    assert "support_not_established" in grading.unmet_prerequisites
