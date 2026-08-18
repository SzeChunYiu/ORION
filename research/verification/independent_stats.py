"""Independent statistics from written P4/P3/P2/P1 analysis plans.

Implemented from the published formulas, not by importing
``research/paper-programme-v1/protocols/publication_stats.py``.
"""
from __future__ import annotations

import math
import random
from statistics import mean
from typing import Sequence

WILSON_Z = 1.959963984540054


def wilson_interval(successes: int, total: int, z: float = WILSON_Z) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    if successes < 0 or successes > total:
        raise ValueError("successes must be between 0 and total")
    p = successes / total
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    half = z * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total))) / denom
    return max(0.0, center - half), min(1.0, center + half)


def percentile(values: Sequence[float], q: float) -> float:
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


def bootstrap_mean_ci(
    values: Sequence[float],
    *,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 20260816,
) -> tuple[float, float, float]:
    if not values:
        raise ValueError("values must be non-empty")
    xs = tuple(float(v) for v in values)
    rng = random.Random(seed)
    boot = [mean(rng.choices(xs, k=len(xs))) for _ in range(resamples)]
    alpha = (1.0 - confidence) / 2.0
    return mean(xs), percentile(boot, alpha), percentile(boot, 1.0 - alpha)


def paired_bootstrap_difference_ci(
    candidate: Sequence[float],
    baseline: Sequence[float],
    *,
    confidence: float = 0.95,
    resamples: int = 10_000,
    seed: int = 20260816,
) -> tuple[float, float, float]:
    if len(candidate) != len(baseline) or not candidate:
        raise ValueError("candidate and baseline must have the same positive length")
    diffs = tuple(float(a) - float(b) for a, b in zip(candidate, baseline, strict=True))
    return bootstrap_mean_ci(diffs, confidence=confidence, resamples=resamples, seed=seed)


def implied_binary_vector(successes: int, total: int) -> tuple[float, ...]:
    if successes < 0 or successes > total:
        raise ValueError("successes out of range")
    return tuple([1.0] * successes + [0.0] * (total - successes))


def majority_bool(values: Sequence[bool]) -> bool:
    if not values:
        raise ValueError("values must be non-empty")
    return sum(1 for value in values if value) * 2 >= len(values)


def macro_f1(per_label: dict[str, tuple[int, int, int]]) -> float:
    """per_label maps label -> (tp, fp, fn)."""
    scores: list[float] = []
    for tp, fp, fn in per_label.values():
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        if precision + recall == 0:
            scores.append(0.0)
        else:
            scores.append(2.0 * precision * recall / (precision + recall))
    if not scores:
        raise ValueError("no labels")
    return sum(scores) / len(scores)
