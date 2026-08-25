from __future__ import annotations

import pytest

from orion.discovery.decision_geometry import (
    bayes_decision,
    common_optimal_actions,
    minimax_regret_decision,
    partition_bayes_regret,
    refines,
    two_world_hedge_report,
    zero_regret_supported,
)


def test_exec_p12_canonical_third_action_hedge() -> None:
    losses = {
        "left": {0: 0.0, 1: 1.0, 2: 3.0},
        "right": {0: 3.0, 1: 1.0, 2: 0.0},
    }
    report = two_world_hedge_report(losses, "left", "right")
    assert report.left_optima == (0,)
    assert report.right_optima == (2,)
    assert report.best_action == 1
    assert report.cross_action_gap == pytest.approx(3.0)
    assert report.half_gap_value == pytest.approx(1.5)
    assert report.exact_equal_prior_regret == pytest.approx(1.0)
    assert report.hedge_gain == pytest.approx(1.0)
    assert report.hedge_present


def test_zero_one_terminal_pair_has_no_hedge_and_exact_half_error() -> None:
    losses = {
        "world-a": {"A": 0.0, "B": 1.0, "OTHER": 1.0},
        "world-b": {"A": 1.0, "B": 0.0, "OTHER": 1.0},
    }
    report = two_world_hedge_report(losses, "world-a", "world-b")
    assert report.exact_equal_prior_regret == pytest.approx(0.5)
    assert report.half_gap_value == pytest.approx(0.5)
    assert report.hedge_gain == pytest.approx(0.0)
    assert not report.hedge_present


def test_common_optimum_is_exact_zero_regret_support_condition() -> None:
    losses = {
        "s1": {"retain": 0.0, "reopen": 1.0},
        "s2": {"retain": 0.0, "reopen": 0.0},
    }
    assert common_optimal_actions(losses) == ("retain",)
    assert zero_regret_supported(losses)

    incompatible = {
        "s1": {"retain": 0.0, "reopen": 1.0},
        "s2": {"retain": 1.0, "reopen": 0.0},
    }
    assert common_optimal_actions(incompatible) == ()
    assert not zero_regret_supported(incompatible)


def test_bayes_and_minimax_can_choose_different_actions() -> None:
    losses = {
        "common": {"fast": 0.0, "safe": 1.0},
        "rare": {"fast": 10.0, "safe": 1.0},
    }
    bayes = bayes_decision(losses, {"common": 0.99, "rare": 0.01})
    minimax = minimax_regret_decision(losses)
    assert bayes.action == "fast"
    assert minimax.action == "safe"


def test_partition_refinement_cannot_increase_optimal_bayes_regret() -> None:
    losses = {
        "a": {0: 0.0, 1: 1.0},
        "b": {0: 1.0, 1: 0.0},
        "c": {0: 0.0, 1: 1.0},
        "d": {0: 1.0, 1: 0.0},
    }
    coarse = {state: "all" for state in losses}
    finer = {"a": "left", "b": "left", "c": "c", "d": "d"}
    assert refines(finer, coarse)
    coarse_risk = partition_bayes_regret(losses, coarse)
    finer_risk = partition_bayes_regret(losses, finer)
    assert finer_risk <= coarse_risk
    assert coarse_risk == pytest.approx(0.5)
    assert finer_risk == pytest.approx(0.25)


def test_loss_table_rejects_inconsistent_action_sets() -> None:
    with pytest.raises(ValueError, match="same action set"):
        bayes_decision({"a": {0: 0.0}, "b": {0: 0.0, 1: 1.0}})
