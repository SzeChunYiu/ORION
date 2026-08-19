from __future__ import annotations

from orion.transfer.v2.higher_order_formal_closure import (
    FormalClosureRecommendation,
    build_formal_closure_report,
    run_finite_formal_closure_checks,
)


def test_finite_formal_closure_battery_is_green_and_non_authorizing() -> None:
    report = run_finite_formal_closure_checks()

    assert report.all_checks_passed is True
    assert report.generated_revision_signatures >= 24
    assert report.preorder_reflexive_cases == report.generated_revision_signatures
    assert report.preorder_transitivity_checks > 0
    assert report.strict_minimality_checks > 0
    assert report.narrower_unresolved_blocks_broader is True
    assert report.incomparable_minima_remain_plural is True
    assert report.authority_noncompensatory is True
    assert report.hard_computation_obligation_precedence is True
    assert report.local_compute_stop_is_not_global_stop is True
    assert report.containment_never_promotes_truth is True
    assert report.shared_provenance_not_independent is True
    assert report.incomplete_social_provenance_unresolved is True
    assert report.composed_controller_non_authorizing is True
    assert report.grants_scientific_authority is False


def test_formal_parent_saturation_recommends_components_only_terminal() -> None:
    closure = build_formal_closure_report()

    assert closure.parent_component_count >= 7
    assert closure.parent_coverage_complete is True
    assert closure.unresolved_parent_components == ()
    assert closure.new_unified_primitive_count == 0
    assert closure.recommendation is FormalClosureRecommendation.FORMAL_COMPONENTS_ONLY_NO_UNIFIED_CALCULUS
    assert closure.finite_checker_green is True
    assert closure.grants_scientific_authority is False
    assert closure.grants_novelty_authority is False
    assert closure.grants_paper_promotion_authority is False


def test_closure_is_a_negative_unification_result_not_a_t1_t8_rollback() -> None:
    closure = build_formal_closure_report()

    # The implemented component contracts survive as framework substrate even
    # though no scientifically distinct universal calculus is claimed.
    assert "KEEP_TYPED_COMPONENT_INTERFACES" in closure.design_dispositions
    assert "KEEP_NON_AUTHORIZING_COMPOSITION" in closure.design_dispositions
    assert "STRIKE_UNIFIED_CALCULUS_NOVELTY" in closure.design_dispositions
    assert "JUMP_REMAINS_SEPARATE_FOLLOWUP" in closure.design_dispositions
