#!/usr/bin/env python3
"""ORION-02 R24 arm-conditional boundary-witness finite fibres."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from math import comb
import platform
from pathlib import Path
import time
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
R23_RESULT = HERE.parent / "r23-density-backoff-revival" / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R23_RESULTS.json"
R23_RESULT_SHA256 = "cf1a0db71ab135278b64c02633f07d05a23604a121f0b62743f4e59c6358fc77"
SCHEMA = "ORION.FiberGuard.PMLBArmConditionalBoundaryFibres.R24.Result.v1"
BOOTSTRAP_REPLICATES = 20_000


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


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
LEARNED_ARMS = r23.LEARNED_ARMS
STATIC_ARMS = r23.STATIC_ARMS
TEST_ARMS = r23.TEST_ARMS
N_FOLDS = r23.N_FOLDS


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


def evaluate_arm(
    ctx: ArmConditionalContext, names: list[str], arm: str, tau: float
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for name in names:
        decision = walk(ctx, name, arm, tau)
        excess = r23.json_float(ctx.excess_member(name, decision["committed"]))
        bound = decision["bound"]
        rows[name] = {
            "committed": decision["committed"],
            "acquired": decision["acquired"],
            "groups_acquired": len(decision["acquired"]),
            "certified": decision["certified"],
            "fallback": decision["fallback"],
            "bound": bound,
            "excess": excess,
            "pool_members": decision["members"],
            "used_backoff": decision["used_backoff"],
            "violation_strict": bool(
                decision["certified"] and excess > float(bound) + TOL
            ),
            "violation_tau": bool(decision["certified"] and excess > tau + TOL),
        }
    return rows


def arm_summary(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    excesses = np.asarray([float(row["excess"]) for row in rows.values()])
    certified = [row for row in rows.values() if row["certified"]]
    return {
        "n": len(rows),
        "certified_n": len(certified),
        "certified_fraction": r23.json_float(len(certified) / len(rows)),
        "mean_excess": r23.json_float(float(excesses.mean())),
        "p95_excess": r23.json_float(float(np.percentile(excesses, 95.0))),
        "max_excess": r23.json_float(float(excesses.max())),
        "mean_groups_acquired": r23.json_float(
            float(np.mean([row["groups_acquired"] for row in rows.values()]))
        ),
        "violations_strict": sum(bool(row["violation_strict"]) for row in certified),
        "violations_tau": sum(bool(row["violation_tau"]) for row in certified),
        "mean_bound": (
            r23.json_float(float(np.mean([row["bound"] for row in certified])))
            if certified
            else None
        ),
    }


def synthetic_policy_receipt() -> dict[str, Any]:
    ctx, _ = synthetic_fixture(MODE_ARM_CONDITIONAL)
    rows = evaluate_arm(ctx, ["query", "query_dense"], "STATIC_ADAPTIVE", TAU)
    integrity = True
    for name, row in rows.items():
        if not row["certified"]:
            continue
        expected = max(
            ctx.excess_member(member, row["committed"])
            for member in row["pool_members"]
        )
        integrity = integrity and abs(expected - row["bound"]) <= TOL
        integrity = integrity and name not in row["pool_members"]
    return {
        "rows": rows,
        "summary": arm_summary(rows),
        "hostile_controls": {"arm_specific_pool_integrity": bool(integrity)},
    }


def synthetic_nine_fold_corpus() -> tuple[
    dict[str, int],
    dict[str, dict[str, list[float]]],
    dict[str, dict[str, float]],
]:
    names = [f"dataset_{i}" for i in range(N_FOLDS)]
    fold_of = {name: i for i, name in enumerate(names)}
    meta: dict[str, dict[str, list[float]]] = {}
    outcomes: dict[str, dict[str, float]] = {}
    for i, name in enumerate(names):
        meta[name] = {
            "G0": [float((i >> bit) & 1) for bit in range(4)],
            "G1": [float(i % 3) / 2.0],
            "G2": [float((i * 2) % 5) / 4.0],
            "G3": [float((i * 3) % 7) / 6.0],
        }
        row = {
            arm: r23.json_float(0.10 + 0.01 * ((j - i) % len(PORTFOLIO)))
            for j, arm in enumerate(PORTFOLIO)
        }
        row["best"] = min(row.values())
        outcomes[name] = row
    return fold_of, meta, outcomes


def select_primary(
    rows_by_arm: Mapping[str, Mapping[str, Mapping[str, Any]]]
) -> str:
    summaries = {arm: arm_summary(rows) for arm, rows in rows_by_arm.items()}
    return min(
        LEARNED_ARMS,
        key=lambda arm: (
            summaries[arm]["mean_excess"],
            summaries[arm]["p95_excess"],
            summaries[arm]["max_excess"],
            arm,
        ),
    )


def policy_phase(
    mode: str,
    fold_of: dict[str, int],
    meta: dict[str, dict[str, list[float]]],
    outcomes: dict[str, dict[str, float]],
) -> dict[int, dict[str, Any]]:
    per_fold: dict[int, dict[str, Any]] = {}
    for fold in range(N_FOLDS):
        roles = r23.r22.role_names(fold, fold_of)
        ctx = ArmConditionalContext(fold, roles, meta, outcomes, mode)
        threshold = {
            arm: evaluate_arm(ctx, roles["threshold_select"], arm, TAU)
            for arm in LEARNED_ARMS
        }
        primary = select_primary(threshold)
        tests = {
            arm: evaluate_arm(ctx, roles["test"], arm, TAU)
            for arm in TEST_ARMS
        }
        per_fold[fold] = {
            "roles": roles,
            "f_star_arm": ctx.f_star_arm,
            "primary": primary,
            "threshold_select": threshold,
            "test": tests,
        }
    return per_fold


def full_state_rows(
    phase: dict[int, dict[str, Any]],
    meta: dict[str, dict[str, list[float]]],
    outcomes: dict[str, dict[str, float]],
    mode: str,
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    full = tuple(sorted(GROUPS))
    for fold in range(N_FOLDS):
        roles = phase[fold]["roles"]
        ctx = ArmConditionalContext(fold, roles, meta, outcomes, mode)
        for name in roles["test"]:
            pools, wc, used = ctx.arm_pools(name, full, TAU)
            admissible = sorted(
                arm for arm in PORTFOLIO if pools[arm] and wc[arm] <= TAU + TOL
            )
            rows[name] = {
                "fold": fold,
                "arm_pools": pools,
                "arm_bounds": {
                    arm: (r23.json_float(wc[arm]) if math.isfinite(wc[arm]) else None)
                    for arm in PORTFOLIO
                },
                "arm_used_backoff": used,
                "admissible": admissible,
                "best_arm": (
                    min(admissible, key=lambda arm: (wc[arm], arm))
                    if admissible
                    else None
                ),
                "best_bound": (
                    r23.json_float(min(wc[arm] for arm in admissible))
                    if admissible
                    else None
                ),
            }
    return {name: rows[name] for name in sorted(rows)}


def pooled_rows(
    phase: Mapping[int, Mapping[str, Any]], arm: str
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for fold in range(N_FOLDS):
        rows.update(phase[fold]["test"][arm])
    return rows


def pooled_primary(
    phase: Mapping[int, Mapping[str, Any]]
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for fold in range(N_FOLDS):
        rows.update(phase[fold]["test"][phase[fold]["primary"]])
    return rows


def full_state_summary(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    covered = sum(bool(row["admissible"]) for row in rows.values())
    return {
        "n": len(rows),
        "certified_n": covered,
        "certified_coverage": r23.json_float(covered / len(rows)),
        "mean_admissible_arms": r23.json_float(
            float(np.mean([len(row["admissible"]) for row in rows.values()]))
        ),
    }


def _stored_parent_primary(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    folds = payload["folds"][r23.MODE_BACKOFF]
    for fold in range(N_FOLDS):
        record = folds[str(fold)]
        rows.update(record["test"][record["primary"]])
    return rows


def _matched_negative_primary(
    negative: Mapping[int, Mapping[str, Any]],
    geometry: Mapping[int, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for fold in range(N_FOLDS):
        rows.update(negative[fold]["test"][geometry[fold]["primary"]])
    return rows


def comparison(
    left: dict[str, dict[str, Any]],
    right: dict[str, dict[str, Any]],
    label: str,
) -> dict[str, Any]:
    # R23's independent, deterministic paired bootstrap accepts an arbitrary
    # label; an R24-specific label therefore produces a distinct frozen stream.
    return r23.comparison(left, right, "R24_" + label)


def _pool_integrity(
    rows: Mapping[str, Mapping[str, Any]],
    outcomes: Mapping[str, Mapping[str, float]],
) -> bool:
    for query, row in rows.items():
        if query in {member for pool in row["arm_pools"].values() for member in pool}:
            return False
        rebuilt_admissible: list[str] = []
        for arm in PORTFOLIO:
            members = row["arm_pools"][arm]
            stored = row["arm_bounds"][arm]
            if not members:
                if stored is not None:
                    return False
                continue
            if len(members) < POOL_K:
                return False
            exact = max(outcomes[member][arm] - outcomes[member]["best"] for member in members)
            if stored is None or abs(float(stored) - exact) > 1.1e-12:
                return False
            if exact <= TAU + TOL:
                rebuilt_admissible.append(arm)
        if sorted(rebuilt_admissible) != sorted(row["admissible"]):
            return False
    return True


def execute(
    subject_repo: Path,
    freeze_path: Path,
    r22_result_path: Path,
    r23_result_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if sha256_bytes(r23_result_path.read_bytes()) != R23_RESULT_SHA256:
        raise ValueError("frozen R23 result binding drift")
    stored_r23 = json.loads(r23_result_path.read_bytes())
    parent, corrected_r22 = r23.execute(subject_repo, freeze_path, r22_result_path)
    if canonical_json(parent) + "\n" != r23_result_path.read_text():
        raise ValueError("fresh R23 parent replay is not byte-identical to the frozen result")

    fold_of = {name: int(fold) for name, fold in parent["corpus"]["fold_assignment"].items()}
    meta = parent["meta_features"]
    outcomes = parent["outcomes"]
    geometry = policy_phase(MODE_ARM_CONDITIONAL, fold_of, meta, outcomes)
    geometry_repeat = policy_phase(MODE_ARM_CONDITIONAL, fold_of, meta, outcomes)
    negative = policy_phase(MODE_LEXICAL_CONTROL, fold_of, meta, outcomes)

    geometry_full = full_state_rows(geometry, meta, outcomes, MODE_ARM_CONDITIONAL)
    geometry_full_repeat = full_state_rows(
        geometry_repeat, meta, outcomes, MODE_ARM_CONDITIONAL
    )
    negative_full = full_state_rows(negative, meta, outcomes, MODE_LEXICAL_CONTROL)
    geometry_summary = full_state_summary(geometry_full)
    negative_summary = full_state_summary(negative_full)

    primary = pooled_primary(geometry)
    parent_primary = _stored_parent_primary(parent)
    negative_primary = _matched_negative_primary(negative, geometry)
    static = pooled_rows(geometry, "STATIC_ADAPTIVE")
    summaries = {
        "R24_PRIMARY_LEARNED": arm_summary(primary),
        "R24_STATIC_ADAPTIVE": arm_summary(static),
        "R23_PARENT_PRIMARY_LEARNED": r23.arm_summary(parent_primary),
        "R24_LEXICAL_MATCHED_PRIMARY": arm_summary(negative_primary),
    }
    for arm in TEST_ARMS:
        summaries[f"R24_{arm}"] = arm_summary(pooled_rows(geometry, arm))

    matched_parent = comparison(primary, parent_primary, "primary-v-r23-primary")
    matched_parent.update({"left": "R24_PRIMARY_LEARNED", "right": "R23_PARENT_PRIMARY_LEARNED"})
    negative_test = comparison(primary, negative_primary, "primary-v-lexical-matched")
    negative_test.update({"left": "R24_PRIMARY_LEARNED", "right": "R24_LEXICAL_MATCHED_PRIMARY"})
    learned_static = comparison(primary, static, "primary-v-static")
    learned_static.update({"left": "R24_PRIMARY_LEARNED", "right": "R24_STATIC_ADAPTIVE"})

    controls = {
        "r23_executor_binding": sha256_bytes(R23_EXECUTOR.read_bytes()) == R23_EXECUTOR_SHA256,
        "r23_result_binding": sha256_bytes(r23_result_path.read_bytes()) == R23_RESULT_SHA256,
        "fresh_r23_parent_byte_identity": canonical_json(parent) == canonical_json(stored_r23),
        "geometry_policy_deterministic": canonical_json(geometry) == canonical_json(geometry_repeat),
        "geometry_full_state_deterministic": canonical_json(geometry_full) == canonical_json(geometry_full_repeat),
        "geometry_pool_integrity": _pool_integrity(geometry_full, outcomes),
        "negative_control_pool_integrity": _pool_integrity(negative_full, outcomes),
        "negative_control_present": bool(negative_full),
        "test_query_custody_disjoint": all(
            not (set(geometry[fold]["roles"]["test"]) & set(geometry[fold]["roles"]["shield_table"]))
            for fold in range(N_FOLDS)
        ),
        "r23_adverse_terminal_preserved": parent["terminal"]
        == "C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE",
    }

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "upstream": parent["upstream"],
        "corpus": parent["corpus"],
        "outcomes": outcomes,
        "meta_features": meta,
        "r23_parent": {
            "result_sha256": R23_RESULT_SHA256,
            "terminal": parent["terminal"],
            "full_state_coverage": parent["coverage"]["r23_backoff_full_state"],
            "preserved_unchanged": True,
        },
        "r24_mechanism": {
            "name": MODE_ARM_CONDITIONAL,
            "pool_k": POOL_K,
            "tau": TAU,
            "radius_rule": "smallest Hamming radius whose uniform-cell occupancy expects at least two shield members",
            "arm_condition": "member excess for the candidate arm is at most tau",
            "boundary_rule": "within the radius, select the two largest arm excesses; distance then dataset name break ties",
            "exact_preservation": "retain a nontrivial exact cell for an arm only when every member is tau-good for that arm",
            "known_outcome_exposure": "the complete R23 result was inspected before R24 design; R24 is prospective only for its new policy output",
        },
        "negative_control": {
            "name": MODE_LEXICAL_CONTROL,
            "geometry": False,
            "same_arm_good_filter_and_boundary_rule": True,
        },
        "folds": {
            MODE_ARM_CONDITIONAL: {str(fold): geometry[fold] for fold in range(N_FOLDS)},
            MODE_LEXICAL_CONTROL: {str(fold): negative[fold] for fold in range(N_FOLDS)},
        },
        "coverage_records": {
            MODE_ARM_CONDITIONAL: geometry_full,
            MODE_LEXICAL_CONTROL: negative_full,
        },
        "coverage": {
            "r23_parent": parent["coverage"]["r23_backoff_full_state"],
            "r24_primary": geometry_summary["certified_coverage"],
            "r24_negative_control": negative_summary["certified_coverage"],
            "target": COVERAGE_TARGET,
            "geometry_summary": geometry_summary,
            "negative_control_summary": negative_summary,
        },
        "arms_summary": summaries,
        "primary": summaries["R24_PRIMARY_LEARNED"],
        "matched_parent_test": matched_parent,
        "negative_control_test": negative_test,
        "learned_static_test": learned_static,
        "hostile_controls": controls,
        "environment": parent["environment"],
        "authority": {
            "scientific_authority_delta": "NONE",
            "submission_authorized": False,
            "top_tier_gate_pass": False,
            "freeze_authorized": False,
            "external_independence": False,
            "scope": "same pinned PMLB corpus/folds/outcomes as outcome-exposed R23",
        },
    }
    payload["terminal"] = decide_terminal(payload)
    return payload, corrected_r22


def run_self_test() -> None:
    receipt = synthetic_policy_receipt()
    assert all(receipt["hostile_controls"].values())
    fold_of, meta, outcomes = synthetic_nine_fold_corpus()
    first = policy_phase(MODE_ARM_CONDITIONAL, fold_of, meta, outcomes)
    second = policy_phase(MODE_ARM_CONDITIONAL, fold_of, meta, outcomes)
    assert canonical_json(first) == canonical_json(second)
    rows = full_state_rows(first, meta, outcomes, MODE_ARM_CONDITIONAL)
    assert _pool_integrity(rows, outcomes)
    print("SELF_TEST_OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-repo", type=Path)
    parser.add_argument("--freeze", type=Path, default=r23.R22_FREEZE)
    parser.add_argument("--r22-result", type=Path, default=r23.R22_RESULT)
    parser.add_argument("--r23-result", type=Path, default=R23_RESULT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--r23-parent-output", type=Path)
    parser.add_argument("--terminal-output", type=Path)
    parser.add_argument("--timings-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    required = (
        args.subject_repo,
        args.output,
        args.r23_parent_output,
        args.terminal_output,
    )
    if any(value is None for value in required):
        parser.error(
            "--subject-repo, --output, --r23-parent-output, and --terminal-output are required"
        )
    started = time.time()
    try:
        payload, _ = execute(
            args.subject_repo.resolve(),
            args.freeze.resolve(),
            args.r22_result.resolve(),
            args.r23_result.resolve(),
        )
        parent_bytes = args.r23_result.read_bytes()
    except (ValueError, OSError, KeyError, MemoryError, RuntimeError, AssertionError) as exc:
        failure = {
            "schema": SCHEMA,
            "terminal": "CANNOT_CHECK_R24_ARM_CONDITIONAL_SOURCE_RESOURCE_OR_BINDING",
            "failure_stage": type(exc).__name__,
            "failure_detail": str(exc)[:2000],
        }
        args.output.write_text(canonical_json(failure) + "\n")
        args.r23_parent_output.write_text(canonical_json(failure) + "\n")
        args.terminal_output.write_text(failure["terminal"] + "\n")
        print(failure["terminal"])
        print("FAILURE_DETAIL " + failure["failure_detail"][:200])
        return 2
    args.output.write_text(canonical_json(payload) + "\n")
    args.r23_parent_output.write_bytes(parent_bytes)
    args.terminal_output.write_text(payload["terminal"] + "\n")
    if args.timings_output is not None:
        args.timings_output.write_text(
            canonical_json(
                {
                    "schema": "ORION.FiberGuard.PMLBArmConditionalBoundaryFibres.R24.Timings.v1",
                    "wall_seconds_total": round(time.time() - started, 3),
                    "python": platform.python_version(),
                    "machine": platform.machine(),
                }
            )
            + "\n"
        )
    print(payload["terminal"])
    print("RESULT_SHA256 " + sha256_bytes(args.output.read_bytes()))
    print("R23_PARENT_SHA256 " + sha256_bytes(args.r23_parent_output.read_bytes()))
    return 0


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
    parent = payload.get("matched_parent_test")
    negative = payload.get("negative_control_test")
    if (
        parent
        and negative
        and float(parent["mean_diff"]) < -TOL
        and float(parent["ci_upper"]) < 0.0
        and float(negative["mean_diff"]) < -TOL
        and float(negative["ci_upper"]) < 0.0
    ):
        return "C_R24_ARM_CONDITIONAL_VALUE"
    return "C_R24_ARM_CONDITIONAL_COVERAGE_VALIDITY_PASS_VALUE_NOT_MATERIAL"


if __name__ == "__main__":
    raise SystemExit(main())
