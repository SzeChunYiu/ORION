"""Statistical inference for ORION Paper 3 evaluation.

Wraps and extends the shared protocol utilities with P3-specific aggregations:
Wilson intervals, paired bootstrap, Holm correction, safety margin checks,
discipline-aware analysis, and multi-run handling.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict
from statistics import mean
from typing import Callable, Sequence


# ── Wilson interval ───────────────────────────────────────────────────────────

def wilson_interval(successes: int, total: int,
                    z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson 95% confidence interval for a binomial proportion."""
    if total <= 0:
        raise ValueError("total must be positive")
    if successes < 0 or successes > total:
        raise ValueError("successes must be between 0 and total")
    p = successes / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    half = z * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total))) / denom
    lo = center - half
    hi = center + half
    # Clamp near-zero floating-point drift
    if lo < 1e-12:
        lo = 0.0
    if hi > 1.0 - 1e-12:
        hi = 1.0
    return lo, hi


# ── percentile ────────────────────────────────────────────────────────────────

def percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolated percentile from non-empty sequence."""
    if not values:
        raise ValueError("values must be non-empty")
    if not 0 <= q <= 1:
        raise ValueError("q must be in [0, 1]")
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = q * (len(ordered) - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    weight = pos - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


# ── bootstrap ─────────────────────────────────────────────────────────────────

def paired_bootstrap_difference_ci(
    candidate: Sequence[float],
    baseline: Sequence[float],
    *,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 20260816,
) -> tuple[float, float, float]:
    """Paired bootstrap difference CI for (candidate - baseline).

    Returns (mean_difference, ci_low, ci_high).
    """
    if len(candidate) != len(baseline) or not candidate:
        raise ValueError("candidate and baseline must have the same positive length")
    diffs = tuple(float(a) - float(b) for a, b in zip(candidate, baseline, strict=True))
    return _bootstrap_mean_ci(diffs, confidence=confidence, resamples=resamples, seed=seed)


def bootstrap_mean_ci(
    values: Sequence[float],
    *,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 20260816,
) -> tuple[float, float, float]:
    return _bootstrap_mean_ci(values, confidence=confidence, resamples=resamples, seed=seed)


def _bootstrap_mean_ci(
    values: Sequence[float],
    *,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 20260816,
) -> tuple[float, float, float]:
    if not values:
        raise ValueError("values must be non-empty")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")
    xs = tuple(float(v) for v in values)
    rng = random.Random(seed)
    boot = [mean(rng.choices(xs, k=len(xs))) for _ in range(resamples)]
    alpha = (1.0 - confidence) / 2.0
    return mean(xs), percentile(boot, alpha), percentile(boot, 1.0 - alpha)


# ── Holm correction ───────────────────────────────────────────────────────────

def holm_correction(p_values: Sequence[float]) -> list[float]:
    """Holm-Bonferroni corrected p-values.

    Returns adjusted p-values (min 1.0) for the same order as input.
    """
    if not p_values:
        return []
    m = len(p_values)
    indexed = sorted(enumerate(float(p) for p in p_values), key=lambda x: x[1])
    # Step-down Bonferroni in rank order, then cumulative max (Holm's rule:
    # the adjusted sequence is non-decreasing in sorted p order).
    per_rank = [min(1.0, p_ * (m - rank)) for rank, (_, p_) in enumerate(indexed)]
    for i in range(1, m):
        per_rank[i] = max(per_rank[i], per_rank[i - 1])
    adjusted: list[float] = [0.0] * m
    for rank, (orig_idx, _) in enumerate(indexed):
        adjusted[orig_idx] = per_rank[rank]
    return adjusted


# ── effect size ───────────────────────────────────────────────────────────────

def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h for two proportions."""
    return 2.0 * math.asin(math.sqrt(p1)) - 2.0 * math.asin(math.sqrt(p2))


def effect_size_category(h: float) -> str:
    """Interpret Cohen's h: 'small', 'medium', 'large', or 'negligible'."""
    abs_h = abs(h)
    if abs_h < 0.2:
        return "negligible"
    if abs_h < 0.5:
        return "small"
    if abs_h < 0.8:
        return "medium"
    return "large"


# ── safety margin checks ──────────────────────────────────────────────────────

def check_superiority_margin(
    candidate_rate: float,
    baseline_rate: float,
    margin: float = 0.05,
) -> dict[str, float | bool | str]:
    """Check if candidate_rate <= baseline_rate - margin (superiority)."""
    improvement = baseline_rate - candidate_rate
    passed = improvement >= margin
    return {
        "candidate_rate": candidate_rate,
        "baseline_rate": baseline_rate,
        "absolute_improvement": improvement,
        "superiority_margin": margin,
        "superiority_passed": passed,
    }


def check_non_inferiority_margin(
    candidate_rate: float,
    baseline_rate: float,
    margin: float = 0.03,
) -> dict[str, float | bool | str]:
    """Check if candidate_rate >= baseline_rate - margin (non-inferiority)."""
    deficit = candidate_rate - baseline_rate
    passed = deficit >= -margin
    return {
        "candidate_rate": candidate_rate,
        "baseline_rate": baseline_rate,
        "absolute_deficit": deficit,
        "non_inferiority_margin": margin,
        "non_inferiority_passed": passed,
    }


# ── discipline-aware analysis ─────────────────────────────────────────────────

def discipline_stratified_analysis(
    gold: Sequence[dict[str, object]],
    preds: Sequence[dict[str, object]],
    metric_fn: Callable[..., dict[str, float]],
    *,
    discipline_key: str = "discipline",
) -> dict[str, dict[str, float]]:
    """Compute metric per discipline (stratified), then pooled."""
    by_discipline: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for g, p in zip(gold, preds, strict=True):
        disc = str(g.get(discipline_key, "unknown"))
        by_discipline[disc].append((g, p))
    result: dict[str, dict[str, float]] = {}
    for disc, pairs in sorted(by_discipline.items()):
        gs = [x[0] for x in pairs]
        ps = [x[1] for x in pairs]
        result[disc] = metric_fn(gs, ps)
    # Pooled
    result["pooled"] = metric_fn(gold, preds)
    return result


# ── multi-run handling ────────────────────────────────────────────────────────

def aggregate_across_runs(
    run_results: Sequence[dict[str, float]],
    *,
    confidence: float = 0.95,
) -> dict[str, dict[str, float]]:
    """Aggregate metrics across K stochastic runs.

    For each metric, returns mean, min, max, and bootstrap CI across runs.
    """
    metric_names = list(run_results[0].keys()) if run_results else []
    result: dict[str, dict[str, float]] = {}
    for name in metric_names:
        values = [float(r[name]) for r in run_results if name in r]
        if not values:
            continue
        _, ci_lo, ci_hi = _bootstrap_mean_ci(values, confidence=confidence)
        result[name] = {
            "mean": mean(values),
            "min": min(values),
            "max": max(values),
            "ci95_low": ci_lo,
            "ci95_high": ci_hi,
            "n_runs": float(len(values)),
        }
    return result


# ── safety margin from aggregated results ─────────────────────────────────────

def check_safety_margin_from_aggregates(
    candidate_agg: dict[str, float],
    baseline_agg: dict[str, float],
    *,
    superiority_margin: float = 0.05,
    non_inferiority_margin: float = 0.03,
) -> dict[str, object]:
    """Check both superiority and non-inferiority from run-aggregated means."""
    cand_fm = candidate_agg.get("false_merge_rate", 1.0)
    base_fm = baseline_agg.get("false_merge_rate", 0.0)
    cand_vi = candidate_agg.get("valid_integration_rate", 0.0)
    base_vi = baseline_agg.get("valid_integration_rate", 0.0)
    sup = check_superiority_margin(cand_fm, base_fm, margin=superiority_margin)
    ni = check_non_inferiority_margin(cand_vi, base_vi, margin=non_inferiority_margin)
    return {
        "superiority": sup,
        "non_inferiority": ni,
        "both_passed": bool(sup["superiority_passed"] and ni["non_inferiority_passed"]),
    }