#!/usr/bin/env python3
"""ORION-02 R24 arm-conditional boundary-witness finite fibres."""

from __future__ import annotations

import hashlib
import importlib.util
import math
from math import comb
from pathlib import Path
from typing import Any, Callable
from typing import Mapping

import numpy as np


TOL = 1e-9
COVERAGE_TARGET = 0.95
VALIDITY_TARGET = 0.10
POOL_K = 2
MODE_ARM_CONDITIONAL = "R24_ARM_CONDITIONAL_BOUNDARY_FIBRES"
MODE_LEXICAL_CONTROL = "R24_LEXICAL_GOOD_BOUNDARY_NEGATIVE_CONTROL"

HERE = Path(__file__).resolve().parent
R23_EXECUTOR = HERE.parent / "r23-density-backoff-revival" / "fiberguard_pmlb_proposal_ordering_r23.py"
R23_EXECUTOR_SHA256 = "6bb4e377462249c3630ceacc56073ba385a82805c79eda58809c42b8ee1562aa"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_r23():
    if sha256_bytes(R23_EXECUTOR.read_bytes()) != R23_EXECUTOR_SHA256:
        raise RuntimeError("R23 executor binding drift")
    spec = importlib.util.spec_from_file_location("orion02_r23_frozen_parent", R23_EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen R23 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r23 = _load_r23()
PORTFOLIO = r23.PORTFOLIO
GROUPS = r23.GROUPS
TAU = r23.TAU


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


class ArmConditionalContext(r23.FoldContext):
    """R23 custody/proposer machinery with one arm-specific fibre per arm."""

    def __init__(
        self,
        fold: int,
        roles: dict[str, list[str]],
        meta: dict[str, dict[str, list[float]]],
        outcomes: dict[str, dict[str, float]],
        mode: str = MODE_ARM_CONDITIONAL,
    ) -> None:
        if mode not in {MODE_ARM_CONDITIONAL, MODE_LEXICAL_CONTROL}:
            raise ValueError(f"unknown R24 mode: {mode}")
        super().__init__(fold, roles, meta, outcomes, r23.MODE_BACKOFF)
        self.r24_mode = mode

    @classmethod
    def from_base(cls, base: Any, mode: str) -> "ArmConditionalContext":
        ctx = object.__new__(cls)
        for name in (
            "fold",
            "meta",
            "outcomes",
            "scalar_layout",
            "edges",
            "f_star_arm",
        ):
            setattr(ctx, name, getattr(base, name))
        ctx.roles = {role: sorted(names) for role, names in base.roles.items()}
        ctx.vectors = {name: np.array(values, copy=True) for name, values in base.vectors.items()}
        ctx._cells = {}
        ctx._proposers = {}
        ctx.custody_seen = set()
        ctx.mode = r23.MODE_BACKOFF
        ctx.r24_mode = mode
        return ctx

    def arm_pools(
        self, name: str, acquired: tuple[str, ...], tau: float
    ) -> tuple[dict[str, list[str]], dict[str, float], dict[str, bool]]:
        shield = sorted(self.roles["shield_table"])
        assert name not in shield, "custody leak: query name inside shield table"
        state = tuple(self.state_indices(acquired))
        query_cell = np.asarray(self.cell_of(name, state), dtype=np.int8)
        cells = {
            member: np.asarray(self.cell_of(member, state), dtype=np.int8)
            for member in shield
        }
        exact = sorted(
            member
            for member in shield
            if np.array_equal(cells[member], query_cell)
        )
        radius = minimum_density_radius(len(state), len(shield))
        pools: dict[str, list[str]] = {}
        wc: dict[str, float] = {}
        used: dict[str, bool] = {}
        for arm in PORTFOLIO:
            excess = {member: self.excess_member(member, arm) for member in shield}
            if len(exact) >= POOL_K and max(excess[member] for member in exact) <= tau + TOL:
                members = exact
                used_backoff = False
            elif self.r24_mode == MODE_LEXICAL_CONTROL:
                members = lexical_good_boundary_pool(excess, tau=tau, k=POOL_K)
                used_backoff = True
            else:
                members = arm_conditional_boundary_pool(
                    query_cell,
                    cells,
                    excess,
                    tau=tau,
                    radius=radius,
                    k=POOL_K,
                )
                used_backoff = True
            pools[arm] = members
            wc[arm] = (
                max(excess[member] for member in members)
                if len(members) >= POOL_K
                else math.inf
            )
            used[arm] = used_backoff
        return pools, wc, used


def _static_score(
    ctx: ArmConditionalContext, arm: str, name: str, acquired: tuple[str, ...]
) -> dict[str, float]:
    _, wc, _ = ctx.arm_pools(name, acquired, TAU)
    return wc


def _learned_score(
    ctx: ArmConditionalContext, arm: str, name: str, acquired: tuple[str, ...]
) -> dict[str, float]:
    return ctx.propose_errors(arm, acquired, name)


def _score_for(arm: str) -> Callable:
    return _learned_score if arm.startswith(("LEARNED_", "SHUFFLED_")) else _static_score


def _commit(
    acquired: tuple[str, ...],
    committed: str,
    pools: dict[str, list[str]],
    wc: dict[str, float],
    used: dict[str, bool],
) -> dict[str, Any]:
    return {
        "committed": committed,
        "acquired": sorted(acquired),
        "certified": True,
        "fallback": False,
        "bound": r23.json_float(wc[committed]),
        "wc": wc[committed],
        "members": pools[committed],
        "used_backoff": used[committed],
    }


def walk_with_scorer(
    ctx: ArmConditionalContext,
    name: str,
    arm: str,
    tau: float,
    scorer: Callable,
) -> dict[str, Any]:
    """R23 acquisition walk with arm-specific admissibility enforced first."""
    acquired: tuple[str, ...] = ()
    while True:
        pools, wc, used = ctx.arm_pools(name, acquired, tau)
        admissible = sorted(a for a in PORTFOLIO if pools[a] and wc[a] <= tau + TOL)
        legal = sorted(group for group in GROUPS if group not in acquired)
        if not admissible:
            if legal:
                acquired = acquired + (legal[0],)
                continue
            return ctx.fallback_decision(acquired)
        scores_now = scorer(ctx, arm, name, acquired)
        commit_loss_now = min(scores_now[a] for a in admissible)
        gains: dict[str, float] = {}
        for group in legal:
            nxt = acquired + (group,)
            next_pools, _, _ = ctx.arm_pools(name, nxt, tau)
            next_admissible = sorted(a for a in PORTFOLIO if next_pools[a])
            gains[group] = (
                -math.inf
                if not next_admissible
                else commit_loss_now
                - min(scorer(ctx, arm, name, nxt)[a] for a in next_admissible)
            )
        finite = {group: value for group, value in gains.items() if value > -math.inf}
        best_group = max(sorted(finite), key=lambda group: finite[group]) if finite else None
        if best_group is not None and finite[best_group] > TOL:
            acquired = acquired + (best_group,)
            continue
        committed = min(admissible, key=lambda a: (scores_now[a], a))
        return _commit(acquired, committed, pools, wc, used)


def walk(ctx: ArmConditionalContext, name: str, arm: str, tau: float) -> dict[str, Any]:
    return walk_with_scorer(ctx, name, arm, tau, _score_for(arm))


def synthetic_fixture(
    mode: str = MODE_ARM_CONDITIONAL,
) -> tuple[ArmConditionalContext, dict[str, Any]]:
    base, info = r23.synthetic_sparse_fixture(mode=r23.MODE_BACKOFF)
    return ArmConditionalContext.from_base(base, mode), info


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
