"""Comprehensive tests for ORION Paper 3 statistics module.

Tests cover: wilson_interval, percentile, bootstrap_mean_ci,
paired_bootstrap_difference_ci, holm_correction, cohens_h,
effect_size_category, check_superiority_margin,
check_non_inferiority_margin, discipline_stratified_analysis,
aggregate_across_runs, check_safety_margin_from_aggregates.
"""
from __future__ import annotations

import math
import pytest
from orion.study.statistics import (
    aggregate_across_runs,
    bootstrap_mean_ci,
    check_non_inferiority_margin,
    check_safety_margin_from_aggregates,
    check_superiority_margin,
    cohens_h,
    discipline_stratified_analysis,
    effect_size_category,
    holm_correction,
    paired_bootstrap_difference_ci,
    percentile,
    wilson_interval,
)


# ── Wilson interval ───────────────────────────────────────────────────────────

def test_wilson_interval_zero_total():
    with pytest.raises(ValueError):
        wilson_interval(0, 0)


def test_wilson_interval_successes_exceed_total():
    with pytest.raises(ValueError):
        wilson_interval(5, 3)


def test_wilson_interval_negative_successes():
    with pytest.raises(ValueError):
        wilson_interval(-1, 10)


def test_wilson_interval_symmetric():
    lo, hi = wilson_interval(50, 100)
    assert lo < 0.5 < hi
    assert lo >= 0.0
    assert hi <= 1.0


def test_wilson_interval_extreme():
    lo, hi = wilson_interval(0, 100)
    assert lo == 0.0
    lo, hi = wilson_interval(100, 100)
    assert hi == 1.0


def test_wilson_interval_custom_z():
    lo, hi = wilson_interval(30, 100, z=1.0)
    assert lo < 0.3 < hi


# ── percentile ────────────────────────────────────────────────────────────────

def test_percentile_empty():
    with pytest.raises(ValueError):
        percentile([], 0.5)


def test_percentile_invalid_q():
    with pytest.raises(ValueError):
        percentile([1.0], -0.1)
    with pytest.raises(ValueError):
        percentile([1.0], 1.5)


def test_percentile_single():
    assert percentile([3.14], 0.5) == 3.14


def test_percentile_median_odd():
    assert percentile([1.0, 2.0, 3.0], 0.5) == 2.0


def test_percentile_median_even():
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == pytest.approx(2.5)


def test_percentile_extremes():
    vals = [1.0, 2.0, 3.0]
    assert percentile(vals, 0.0) == 1.0
    assert percentile(vals, 1.0) == 3.0


# ── bootstrap_mean_ci ─────────────────────────────────────────────────────────

def test_bootstrap_ci_constant_values():
    vals = [1.0, 1.0, 1.0, 1.0, 1.0]
    mean, lo, hi = bootstrap_mean_ci(vals, seed=42)
    assert mean == 1.0
    assert lo <= mean <= hi


def test_bootstrap_ci_increasing_values():
    vals = list(range(100))
    mean, lo, hi = bootstrap_mean_ci(vals, seed=42)
    assert mean == pytest.approx(49.5)
    assert lo <= mean <= hi
    assert lo > 0


def test_bootstrap_ci_empty():
    with pytest.raises(ValueError):
        bootstrap_mean_ci([])


def test_bootstrap_ci_confidence_out_of_range():
    with pytest.raises(ValueError):
        bootstrap_mean_ci([1.0], confidence=1.5)
    with pytest.raises(ValueError):
        bootstrap_mean_ci([1.0], confidence=0)


# ── paired_bootstrap_difference_ci ───────────────────────────────────────────

def test_paired_bootstrap_identical():
    mean, lo, hi = paired_bootstrap_difference_ci([1.0, 2.0], [1.0, 2.0], seed=42)
    assert mean == 0.0
    assert lo <= 0.0 <= hi


def test_paired_bootstrap_shifted():
    mean, lo, hi = paired_bootstrap_difference_ci([3.0, 4.0], [1.0, 2.0], seed=42)
    assert mean == 2.0
    assert lo > 0


def test_paired_bootstrap_mismatched_lengths():
    with pytest.raises(ValueError):
        paired_bootstrap_difference_ci([1.0, 2.0], [1.0])


# ── Holm correction ───────────────────────────────────────────────────────────

def test_holm_empty():
    assert holm_correction([]) == []


def test_holm_no_correction_single():
    adj = holm_correction([0.01])
    assert adj[0] == pytest.approx(0.01)


def test_holm_correction_increases_p():
    pvals = [0.01, 0.02, 0.03, 0.40]
    adj = holm_correction(pvals)
    assert all(a >= p for a, p in zip(adj, pvals))


def test_holm_caps_at_one():
    pvals = [0.6, 0.7]
    adj = holm_correction(pvals)
    assert all(a <= 1.0 for a in adj)
    assert adj[1] == 1.0  # 0.7 * 2 = 1.4 capped to 1.0, then monotonicity


def test_holm_monotonic():
    pvals = [0.001, 0.01, 0.5]
    adj = holm_correction(pvals)
    for i in range(len(adj) - 1):
        assert adj[i] <= adj[i + 1] + 1e-10


# ── Cohen's h ─────────────────────────────────────────────────────────────────

def test_cohens_h_identical():
    assert cohens_h(0.5, 0.5) == 0.0


def test_cohens_h_positive():
    h = cohens_h(0.8, 0.3)
    assert h > 0


def test_cohens_h_negative():
    h = cohens_h(0.3, 0.8)
    assert h < 0


def test_cohens_h_extreme():
    h = cohens_h(1.0, 0.0)
    assert h > 0


# ── effect_size_category ──────────────────────────────────────────────────────

def test_effect_size_negligible():
    assert effect_size_category(0.1) == "negligible"


def test_effect_size_small():
    assert effect_size_category(0.3) == "small"


def test_effect_size_medium():
    assert effect_size_category(0.6) == "medium"


def test_effect_size_large():
    assert effect_size_category(0.9) == "large"


def test_effect_size_negative():
    assert effect_size_category(-0.6) == "medium"


# ── safety margin checks ──────────────────────────────────────────────────────

def test_superiority_passed():
    out = check_superiority_margin(0.50, 0.60, margin=0.05)
    assert out["superiority_passed"] is True
    assert out["absolute_improvement"] == pytest.approx(0.10, abs=1e-6)


def test_superiority_failed():
    out = check_superiority_margin(0.58, 0.60, margin=0.05)
    assert out["superiority_passed"] is False


def test_non_inferiority_passed():
    out = check_non_inferiority_margin(0.90, 0.92, margin=0.03)
    assert out["non_inferiority_passed"] is True


def test_non_inferiority_failed():
    out = check_non_inferiority_margin(0.80, 0.92, margin=0.03)
    assert out["non_inferiority_passed"] is False


# ── discipline_stratified_analysis ────────────────────────────────────────────

def test_discipline_stratified():
    gold = [{"discipline": "biomed", "integration_verdict": "OBSTRUCTION"},
            {"discipline": "physics", "integration_verdict": "GLUE_ALLOWED"}]
    pred = [{"integration_verdict": "GLUE_ALLOWED"},
            {"integration_verdict": "GLUE_ALLOWED"}]

    def fake_metric(g, p):
        return {"fm": 1.0 if len(g) == 1 else 0.5}

    out = discipline_stratified_analysis(gold, pred, fake_metric)
    assert "biomed" in out
    assert "physics" in out
    assert "pooled" in out


def test_discipline_stratified_empty():
    out = discipline_stratified_analysis([], [], lambda g, p: {"ok": 1.0})
    assert "pooled" in out


# ── aggregate_across_runs ─────────────────────────────────────────────────────

def test_aggregate_single_run():
    runs = [{"fm": 0.1, "vi": 0.9}]
    out = aggregate_across_runs(runs)
    assert out["fm"]["mean"] == 0.1
    assert out["fm"]["n_runs"] == 1
    assert out["vi"]["mean"] == 0.9


def test_aggregate_multiple_runs():
    runs = [{"fm": 0.1, "vi": 0.9}, {"fm": 0.2, "vi": 0.8}, {"fm": 0.15, "vi": 0.85}]
    out = aggregate_across_runs(runs)
    assert out["fm"]["mean"] == pytest.approx(0.15)
    assert out["fm"]["min"] == 0.1
    assert out["fm"]["max"] == 0.2
    assert out["fm"]["ci95_low"] <= out["fm"]["mean"] <= out["fm"]["ci95_high"]


def test_aggregate_empty():
    out = aggregate_across_runs([])
    assert out == {}


# ── check_safety_margin_from_aggregates ───────────────────────────────────────

def test_safety_margin_both_passed():
    cand = {"false_merge_rate": 0.50, "valid_integration_rate": 0.91}
    base = {"false_merge_rate": 0.60, "valid_integration_rate": 0.92}
    out = check_safety_margin_from_aggregates(cand, base)
    assert out["both_passed"] is True
    assert out["superiority"]["superiority_passed"] is True
    assert out["non_inferiority"]["non_inferiority_passed"] is True


def test_safety_margin_superiority_fails():
    cand = {"false_merge_rate": 0.58, "valid_integration_rate": 0.91}
    base = {"false_merge_rate": 0.60, "valid_integration_rate": 0.92}
    out = check_safety_margin_from_aggregates(cand, base)
    assert out["both_passed"] is False
    assert out["superiority"]["superiority_passed"] is False
    assert out["non_inferiority"]["non_inferiority_passed"] is True


def test_safety_margin_non_inferiority_fails():
    cand = {"false_merge_rate": 0.50, "valid_integration_rate": 0.80}
    base = {"false_merge_rate": 0.60, "valid_integration_rate": 0.92}
    out = check_safety_margin_from_aggregates(cand, base)
    assert out["both_passed"] is False
    assert out["non_inferiority"]["non_inferiority_passed"] is False
