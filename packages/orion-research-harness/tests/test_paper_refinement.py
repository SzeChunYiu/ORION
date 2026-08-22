from __future__ import annotations

from orion_research_harness.paper_refinement import (
    ConcernClass,
    PaperConcern,
    PaperReviewReceipt,
    QUALITY_DIMENSIONS,
    RefinementTerminal,
    RepairRoute,
    VenueReadinessProfile,
    assess_refinement_terminal,
)


def scores(value: float = 9.0) -> dict[str, float]:
    return {key: value for key in QUALITY_DIMENSIONS}


def profile(*, exceptionality: bool = False) -> VenueReadinessProfile:
    return VenueReadinessProfile(
        profile_id="test",
        hard_gates=("validity", "repro"),
        dimension_floor=8.0,
        mean_floor=8.5,
        requires_exceptionality_axis=exceptionality,
    )


def review_with(concern: PaperConcern) -> PaperReviewReceipt:
    return PaperReviewReceipt.create(
        paper_id="QX",
        round_index=0,
        manuscript_digest="m" * 64,
        reviewer_role=concern.reviewer_role,
        context_id="ctx-1",
        target_profile="test",
        concerns=(concern,),
    )


def concern(
    *,
    concern_class: ConcernClass,
    route: RepairRoute,
    role: str = "VALIDITY",
) -> PaperConcern:
    return PaperConcern(
        concern_id="C1",
        reviewer_role=role,
        concern_class=concern_class,
        criterion="validity",
        claim_pointer="headline claim",
        evidence_pointer="main result",
        concern="evidence does not yet establish the headline claim",
        resolution_test="provide the discriminating evidence or narrow the claim",
        repair_route=route,
    )


def test_ready_requires_hard_gates_scores_and_no_blockers() -> None:
    result = assess_refinement_terminal(
        profile=profile(),
        scores=scores(),
        hard_gate_status={"validity": True, "repro": True},
        review_receipts=(),
    )
    assert result is RefinementTerminal.READY_FOR_SCOPED_TARGET


def test_exceptionality_profile_does_not_pass_on_scores_alone() -> None:
    result = assess_refinement_terminal(
        profile=profile(exceptionality=True),
        scores=scores(),
        hard_gate_status={"validity": True, "repro": True},
        review_receipts=(),
    )
    assert result is RefinementTerminal.CONTINUE_REFINEMENT


def test_exceptionality_axis_can_complete_otherwise_ready_profile() -> None:
    result = assess_refinement_terminal(
        profile=profile(exceptionality=True),
        scores=scores(),
        hard_gate_status={"validity": True, "repro": True},
        review_receipts=(),
        exceptionality_axes_passed=("exceptional_insight",),
    )
    assert result is RefinementTerminal.READY_FOR_SCOPED_TARGET


def test_decisive_missing_evidence_stops_instead_of_polishing() -> None:
    result = assess_refinement_terminal(
        profile=profile(),
        scores=scores(),
        hard_gate_status={"validity": True, "repro": True},
        review_receipts=(
            review_with(
                concern(
                    concern_class=ConcernClass.TECHNICAL_BLOCKER,
                    route=RepairRoute.ADD_DECISIVE_EVIDENCE,
                )
            ),
        ),
    )
    assert result is RefinementTerminal.EVIDENCE_BLOCKED


def test_target_mismatch_can_route_to_fallback_without_fake_failure() -> None:
    receipt = review_with(
        concern(
            concern_class=ConcernClass.PUBLICATION_CRITERIA_BLOCKER,
            route=RepairRoute.CHANGE_TARGET_OR_ARTICLE_TYPE,
        )
    )
    assert (
        assess_refinement_terminal(
            profile=profile(),
            scores=scores(),
            hard_gate_status={"validity": True, "repro": True},
            review_receipts=(receipt,),
            fallback_ready=False,
        )
        is RefinementTerminal.TRANSFER_RECOMMENDED
    )
    assert (
        assess_refinement_terminal(
            profile=profile(),
            scores=scores(),
            hard_gate_status={"validity": True, "repro": True},
            review_receipts=(receipt,),
            fallback_ready=True,
        )
        is RefinementTerminal.READY_FOR_FALLBACK
    )


def test_repairable_blocker_keeps_loop_open() -> None:
    result = assess_refinement_terminal(
        profile=profile(),
        scores=scores(),
        hard_gate_status={"validity": True, "repro": True},
        review_receipts=(
            review_with(
                concern(
                    concern_class=ConcernClass.TECHNICAL_BLOCKER,
                    route=RepairRoute.CLARIFY_OR_RESTRUCTURE,
                )
            ),
        ),
    )
    assert result is RefinementTerminal.CONTINUE_REFINEMENT


def test_missing_hard_gate_is_cannot_check_not_pass() -> None:
    result = assess_refinement_terminal(
        profile=profile(),
        scores=scores(),
        hard_gate_status={"validity": True},
        review_receipts=(),
    )
    assert result is RefinementTerminal.CANNOT_CHECK


def test_two_small_improvements_trigger_plateau_stop() -> None:
    result = assess_refinement_terminal(
        profile=profile(),
        scores=scores(7.7),
        hard_gate_status={"validity": True, "repro": True},
        review_receipts=(),
        prior_round_means=(7.4, 7.55),
        round_index=2,
    )
    assert result is RefinementTerminal.PLATEAU_STOP


def test_review_receipt_does_not_self_grant_authority() -> None:
    receipt = PaperReviewReceipt.create(
        paper_id="QX",
        round_index=0,
        manuscript_digest="m" * 64,
        reviewer_role="POSITIONING",
        context_id="ctx-positioning",
        target_profile="test",
    )
    raw = receipt.unsigned()
    assert raw["grants_scientific_authority"] is False
    assert raw["grants_novelty_authority"] is False
    assert raw["predicts_acceptance"] is False
