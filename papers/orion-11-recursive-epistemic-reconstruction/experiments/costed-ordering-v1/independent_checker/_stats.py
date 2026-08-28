"""Stratified percentile bootstrap and the Holm adjustment.

PROTOCOL statistics fixes: pairing by world identity, a stratified percentile
bootstrap of 10000 resamples, and Holm across the registered gate family.

Two properties are deliberate:

1. One shared set of resample indices per stratum drives EVERY statistic, so
   the ratios, the success difference and the per-stratum tests are jointly
   consistent replicate by replicate. Holm over jointly drawn statistics is
   coherent; Holm over independently drawn ones is not.

2. The bootstrap seed is NOT frozen anywhere in the packet (see the defect
   note in _constants). Exact numeric agreement with any other implementation
   is therefore unattainable, so this module's job is self-reproducibility
   plus an honest verdict-stability probe, not bit-matching a runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from . import _constants as K

# Statistic kinds.
KIND_RATIO = "ratio_of_matched_means"
KIND_SUCCESS_DIFF = "paired_success_difference"
KIND_MEAN_RATIO = "ratio_of_unmatched_means"


@dataclass
class Stat:
    """One bootstrap statistic, carried as per-stratum aligned vectors."""

    name: str
    kind: str
    vectors: dict[str, dict[str, np.ndarray]]

    def replicate(self, stratum_idx: dict[str, np.ndarray]) -> np.ndarray:
        num = None
        den = None
        for stratum, vec in self.vectors.items():
            idx = stratum_idx.get(stratum)
            if idx is None:
                continue
            part_num = vec["num"][idx].sum(axis=1)
            part_den = vec["den"][idx].sum(axis=1)
            num = part_num if num is None else num + part_num
            den = part_den if den is None else den + part_den
        if num is None or den is None:
            return np.array([], dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            if self.kind == KIND_SUCCESS_DIFF:
                return np.where(den > 0, num / den, np.nan)
            return np.where(den > 0, num / den, np.nan)


def ratio_stat(name: str, frame: dict[str, Any], strata: tuple[str, ...]) -> Stat:
    """Ratio of matched mean costs: sum(cost_a * m) / sum(cost_b * m)."""
    vectors: dict[str, dict[str, np.ndarray]] = {}
    for stratum in strata:
        block = frame["strata"].get(stratum)
        if block is None:
            continue
        matched = np.asarray(block["matched"], dtype=float)
        vectors[stratum] = {
            "num": np.asarray(block["cost_a"], dtype=float) * matched,
            "den": np.asarray(block["cost_b"], dtype=float) * matched,
        }
    return Stat(name=name, kind=KIND_RATIO, vectors=vectors)


def unmatched_ratio_stat(name: str, frame: dict[str, Any], strata: tuple[str, ...]) -> Stat:
    """Ratio of unconditional mean costs (used for the G4 oracle comparison)."""
    vectors: dict[str, dict[str, np.ndarray]] = {}
    for stratum in strata:
        block = frame["strata"].get(stratum)
        if block is None:
            continue
        vectors[stratum] = {
            "num": np.asarray(block["cost_a"], dtype=float),
            "den": np.asarray(block["cost_b"], dtype=float),
        }
    return Stat(name=name, kind=KIND_MEAN_RATIO, vectors=vectors)


def success_diff_stat(name: str, frame: dict[str, Any], strata: tuple[str, ...]) -> Stat:
    """Paired success-rate difference arm_a - arm_b."""
    vectors: dict[str, dict[str, np.ndarray]] = {}
    for stratum in strata:
        block = frame["strata"].get(stratum)
        if block is None:
            continue
        succ_a = np.asarray(block["success_a"], dtype=float)
        succ_b = np.asarray(block["success_b"], dtype=float)
        vectors[stratum] = {
            "num": succ_a - succ_b,
            "den": np.ones_like(succ_a),
        }
    return Stat(name=name, kind=KIND_SUCCESS_DIFF, vectors=vectors)


def run_bootstrap(
    stats: list[Stat],
    stratum_sizes: dict[str, int],
    seed: int,
    resamples: int = K.BOOTSTRAP_RESAMPLES,
    block: int = K.BOOTSTRAP_BLOCK,
) -> dict[str, np.ndarray]:
    """Draw one shared stratified resample scheme and evaluate every statistic."""
    # Misaligned vectors would silently pair the wrong worlds, which is worse
    # than any refusal. Fail loudly instead.
    for stat in stats:
        for stratum, vec in stat.vectors.items():
            n = stratum_sizes.get(stratum)
            if n is None or len(vec["num"]) != n or len(vec["den"]) != n:
                raise ValueError(
                    f"statistic {stat.name!r} is misaligned on stratum {stratum!r}: "
                    f"vector length {len(vec['num'])} vs stratum size {n}"
                )

    rng = np.random.Generator(np.random.PCG64(seed))
    collected: dict[str, list[np.ndarray]] = {stat.name: [] for stat in stats}
    done = 0
    while done < resamples:
        size = min(block, resamples - done)
        stratum_idx = {
            stratum: rng.integers(0, n, size=(size, n))
            for stratum, n in stratum_sizes.items()
            if n > 0
        }
        for stat in stats:
            collected[stat.name].append(stat.replicate(stratum_idx))
        done += size
    return {
        name: (np.concatenate(chunks) if chunks else np.array([], dtype=float))
        for name, chunks in collected.items()
    }


def percentile_interval(values: np.ndarray, level: float = K.CI_LEVEL) -> dict[str, Any]:
    finite = values[np.isfinite(values)] if values.size else values
    if finite.size == 0:
        return {
            "ci_low": None,
            "ci_high": None,
            "n_valid_resamples": 0,
            "level": level,
            "method": "stratified percentile bootstrap",
        }
    tail = (1.0 - level) / 2.0 * 100.0
    low, high = np.percentile(finite, [tail, 100.0 - tail])
    return {
        "ci_low": float(low),
        "ci_high": float(high),
        "n_valid_resamples": int(finite.size),
        "n_invalid_resamples": int(values.size - finite.size),
        "level": level,
        "method": "stratified percentile bootstrap",
    }


def one_sided_p(values: np.ndarray, threshold: float, direction: str) -> float | None:
    """Bootstrap p-value with the (1 + k) / (B + 1) correction.

    direction "below": H1 is statistic < threshold, so p counts replicates at
    or above the threshold. direction "above": the mirror image.
    """
    finite = values[np.isfinite(values)] if values.size else values
    if finite.size == 0:
        return None
    if direction == "below":
        k = int(np.count_nonzero(finite >= threshold))
    elif direction == "above":
        k = int(np.count_nonzero(finite <= threshold))
    else:
        raise ValueError(f"unknown direction {direction!r}")
    return (1.0 + k) / (finite.size + 1.0)


def holm(p_values: dict[str, float | None], alpha: float = K.ALPHA) -> dict[str, Any]:
    """Holm step-down adjustment across the registered test family.

    Tests whose p-value is unavailable are carried through as unmeasured and
    excluded from the family size, so an unmeasured test neither borrows nor
    donates alpha. Adjusted p-values are monotone non-decreasing, so Holm can
    only ever make a gate HARDER to pass; it is never applied two-way to
    rescue a gate that failed on its own terms.
    """
    measured = {name: p for name, p in p_values.items() if p is not None}
    m = len(measured)
    out: dict[str, Any] = {
        "alpha": alpha,
        "family_size": m,
        "family_members": sorted(p_values),
        "unmeasured": sorted(name for name, p in p_values.items() if p is None),
        "tests": {},
    }
    running = 0.0
    for rank, (name, p) in enumerate(sorted(measured.items(), key=lambda kv: kv[1])):
        adjusted = min(1.0, max(running, (m - rank) * p))
        running = adjusted
        out["tests"][name] = {
            "p_raw": p,
            "p_holm_adjusted": adjusted,
            "rank": rank + 1,
            "rejected_at_alpha": adjusted < alpha,
        }
    for name in out["unmeasured"]:
        out["tests"][name] = {
            "p_raw": None,
            "p_holm_adjusted": None,
            "rank": None,
            "rejected_at_alpha": None,
            "status": "UNMEASURED__NOT_COUNTED_AS_REJECTED",
        }
    return out
