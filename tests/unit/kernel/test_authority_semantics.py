from __future__ import annotations

from orion.kernel.gate import AnswerAuthority, AnswerGrading
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
