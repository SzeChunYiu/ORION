#!/usr/bin/env python3
"""ORION-02 R24 arm-conditional boundary-witness finite fibres."""

from __future__ import annotations

from math import comb
from typing import Mapping

import numpy as np


TOL = 1e-9
COVERAGE_TARGET = 0.95
VALIDITY_TARGET = 0.10
POOL_K = 2


def expected_ball_members(n_bits: int, shield_n: int, radius: int) -> float:
    """Uniform-cell occupancy used only to fix the density radius."""
    if n_bits < 0 or shield_n < 0 or not 0 <= radius <= n_bits:
        raise ValueError("invalid Hamming-ball dimensions")
    volume = sum(comb(n_bits, i) for i in range(radius + 1))
    return float(shield_n * volume / (2**n_bits))


def minimum_density_radius(n_bits: int, shield_n: int, minimum_expected: float = 2.0) -> int:
    """Smallest radius whose uniform Hamming ball expects two shield members."""
    if minimum_expected <= 0:
        raise ValueError("minimum_expected must be positive")
    for radius in range(n_bits + 1):
        if expected_ball_members(n_bits, shield_n, radius) >= minimum_expected:
            return radius
    raise ValueError("shield cannot supply the requested expected membership")


def _distance(query: np.ndarray, member: np.ndarray) -> int:
    q = np.asarray(query, dtype=np.int8)
    m = np.asarray(member, dtype=np.int8)
    if q.ndim != 1 or m.shape != q.shape:
        raise ValueError("Hamming shape mismatch")
    return int(np.count_nonzero(q != m))


def arm_conditional_boundary_pool(
    query: np.ndarray,
    member_cells: Mapping[str, np.ndarray],
    member_excess: Mapping[str, float],
    *,
    tau: float,
    radius: int,
    k: int = POOL_K,
) -> list[str]:
    """Return local tau-good witnesses nearest the finite-fibre boundary.

    Geometry is a hard eligibility condition.  Within the local candidate set,
    larger development excess is preferred so that the stored exact maximum is
    not an optimistically easy witness.
    """
    if k < 2:
        raise ValueError("a nontrivial finite fibre requires k >= 2")
    candidates: list[tuple[float, int, str]] = []
    for name in sorted(member_cells):
        if name not in member_excess:
            raise ValueError(f"missing excess for {name}")
        excess = float(member_excess[name])
        distance = _distance(query, member_cells[name])
        if excess <= tau + TOL and distance <= radius:
            candidates.append((-excess, distance, name))
    if len(candidates) < k:
        return []
    candidates.sort()
    return [name for _, _, name in candidates[:k]]


def lexical_good_boundary_pool(
    member_excess: Mapping[str, float], *, tau: float, k: int = POOL_K
) -> list[str]:
    """No-geometry negative control with the identical good-boundary rule."""
    if k < 2:
        raise ValueError("a nontrivial finite fibre requires k >= 2")
    candidates = sorted(
        (-float(excess), name)
        for name, excess in member_excess.items()
        if float(excess) <= tau + TOL
    )
    if len(candidates) < k:
        return []
    return [name for _, name in candidates[:k]]


def decide_terminal(payload: dict) -> str:
    if not all(payload["hostile_controls"].values()):
        return "C_R24_ARM_CONDITIONAL_HOSTILE_CONTROL_FAILED"
    coverage = float(payload["coverage"]["r24_primary"])
    parent = float(payload["coverage"]["r23_parent"])
    target = float(payload["coverage"].get("target", COVERAGE_TARGET))
    if coverage <= parent + TOL:
        return "C_R24_ARM_CONDITIONAL_NO_COVERAGE_IMPROVEMENT"
    if coverage < target - TOL:
        return "C_R24_ARM_CONDITIONAL_COVERAGE_IMPROVED_BELOW_GATE"
    certified_n = int(payload["primary"]["certified_n"])
    violations = int(payload["primary"]["violations_strict"])
    rate = violations / certified_n if certified_n else float("inf")
    if rate > VALIDITY_TARGET + TOL:
        return "C_R24_ARM_CONDITIONAL_CERTIFICATE_INVALID"
    return "C_R24_ARM_CONDITIONAL_COVERAGE_AND_VALIDITY_GATE_PASS"
