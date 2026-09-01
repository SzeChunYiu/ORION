#!/usr/bin/env python3
"""Dependency-free deterministic analysis primitives for Tier-A preregistered studies."""
from __future__ import annotations

import hashlib
import math
from typing import Iterable

DEFAULT_RESAMPLES = 10_000


def finite_float(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    if not vals:
        raise ValueError("mean of empty collection")
    return sum(vals) / len(vals)


def _index(key: str, replicate: int, draw: int, n: int) -> int:
    digest = hashlib.sha256(f"{key}|{replicate}|{draw}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % n


def bootstrap_mean_interval(values: list[float], key: str, resamples: int = DEFAULT_RESAMPLES) -> tuple[float, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty collection")
    if resamples < 2:
        raise ValueError("resamples must be >=2")
    if len(values) == 1:
        return values[0], values[0]
    n = len(values)
    samples: list[float] = []
    for b in range(resamples):
        total = 0.0
        for j in range(n):
            total += values[_index(key, b, j, n)]
        samples.append(total / n)
    samples.sort()
    lo = samples[math.floor(0.025 * (resamples - 1))]
    hi = samples[math.ceil(0.975 * (resamples - 1))]
    return lo, hi


def require_disjoint(left: Iterable[str], right: Iterable[str], label: str) -> None:
    overlap = sorted(set(left) & set(right))
    if overlap:
        raise ValueError(f"{label} overlap: {overlap[:10]}")


def charged_saving(candidate_costs: Iterable[float], ceiling_costs: Iterable[float]) -> float:
    cand = sum(candidate_costs)
    ceiling = sum(ceiling_costs)
    if ceiling <= 0:
        raise ValueError("ceiling cost must be positive")
    return 1.0 - cand / ceiling
