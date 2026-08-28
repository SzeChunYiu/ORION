#!/usr/bin/env python3
"""Frozen ORION-02 R23 density-backoff revival.

R23 changes one scientific mechanism relative to the corrected R22 parent:
when an exact median-split cell contains fewer than two shield members, it
backs off to the two Hamming-nearest shield members with lexical name ties.
The R22 scalar-F* defect is corrected identically in both parent and revival
evaluators and is not counted as a scientific lever.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import platform
from pathlib import Path
import sys
import time
from typing import Any, Callable, Sequence

import numpy as np
import scipy
import sklearn


HERE = Path(__file__).resolve().parent
R22_DIR = HERE.parent / "r22-proposal-ordering"
R22_EXECUTOR = R22_DIR / "fiberguard_pmlb_proposal_ordering_r22.py"
R22_RESULT = R22_DIR / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_RESULTS.json"
R22_FREEZE = R22_DIR / "FIBERGUARD_PMLB_R22_DATASET_FREEZE.json"

R22_EXECUTOR_SHA256 = "b445555cbbb37fcfa16f7bf528fb68dd4030a8e87465a9cb585548c37f272fe8"
R22_RESULT_SHA256 = "39f47c7806ba77b94a495851f5d51fa111e551db983aa7a31607d5b4bc4f2623"
R22_FREEZE_SHA256 = "d29c9f098c34032097ed364021923db24370aa7d7e7d041c8ed67ca0d8116a77"
R22_TERMINAL = "C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE"

SCHEMA = "ORION.FiberGuard.PMLBProposalOrdering.R23.v1"
PARENT_SCHEMA = "ORION.FiberGuard.PMLBProposalOrdering.R22CorrectedExact.v1"
MODE_EXACT = "R22C_EXACT_CELL"
MODE_BACKOFF = "R23_HAMMING_BACKOFF_K2"
MODE_LEXICAL_CONTROL = "R23_LEXICAL_BACKOFF_K2_NEGATIVE_CONTROL"
BACKOFF_K = 2
COVERAGE_TARGET = 0.95
VALIDITY_GATE = 0.10
MATERIAL_FRACTION = 0.05
TOL = 1e-9
TAU = 0.02
BOOTSTRAP_REPLICATES = 20_000
BOOTSTRAP_SEED_TEXT = "ORION02_R23_PMLB_DENSITY_BACKOFF_BOOTSTRAP_V1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode())


def json_float(value: float) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"nonfinite value in receipt: {value!r}")
    return round(out, 12)


def derive_seed(*parts: object) -> int:
    text = "|".join(str(part) for part in parts)
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big") % (2**31 - 1)


def _load_r22():
    if sha256_bytes(R22_EXECUTOR.read_bytes()) != R22_EXECUTOR_SHA256:
        raise RuntimeError("R22 executor binding drift")
    spec = importlib.util.spec_from_file_location("orion02_r22_frozen_parent", R22_EXECUTOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen R22 executor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r22 = _load_r22()
PORTFOLIO = r22.PORTFOLIO
GROUPS = r22.GROUPS
LEARNED_ARMS = r22.LEARNED_ARMS
SHUFFLED_ARMS = tuple("SHUFFLED_" + arm for arm in LEARNED_ARMS)
STATIC_ARMS = ("SHIELD_FREE", "SHIELD_FULL", "STATIC_ADAPTIVE")
TEST_ARMS = STATIC_ARMS + LEARNED_ARMS
N_FOLDS = r22.N_FOLDS


def hamming_distances(query: np.ndarray, table: np.ndarray) -> np.ndarray:
    """Direct elementwise Hamming distances; no norm-expansion algebra."""
    q = np.asarray(query, dtype=np.int8)
    x = np.asarray(table, dtype=np.int8)
    if x.ndim != 2 or q.ndim != 1 or x.shape[1] != q.shape[0]:
        raise ValueError("Hamming shape mismatch")
    return np.count_nonzero(x != q[None, :], axis=1)


class FoldContext(r22.FoldContext):
    """R22 machinery with corrected F* and a frozen shield-pool mode."""

    def __init__(self, fold: int, roles: dict[str, list[str]], meta: dict[str, dict[str, list[float]]],
                 outcomes: dict[str, dict[str, float]], mode: str) -> None:
        if mode not in {MODE_EXACT, MODE_BACKOFF, MODE_LEXICAL_CONTROL}:
            raise ValueError(f"unknown shield mode: {mode}")
        super().__init__(fold, roles, meta, outcomes)
        self.mode = mode
        self.f_star_arm = min(
            PORTFOLIO,
            key=lambda arm: (
                float(np.mean([outcomes[name][arm] for name in self.roles["shield_table"]])),
                arm,
            ),
        )

    def fallback_decision(self, acquired: tuple[str, ...]) -> dict[str, Any]:
        return {
            "committed": self.f_star_arm,
            "acquired": sorted(acquired),
            "certified": False,
            "fallback": True,
            "bound": None,
            "wc": None,
            "members": [],
            "used_backoff": False,
        }

    def selected_members(self, name: str, acquired: tuple[str, ...]) -> tuple[list[str], bool]:
        shield = sorted(self.roles["shield_table"])
        assert name not in shield, "custody leak: query name inside shield table"
        state = tuple(self.state_indices(acquired))
        exact = list(self.cell_table(state).get(self.cell_of(name, state), []))
        if self.mode == MODE_EXACT or len(exact) >= r22.MIN_CELL_MEMBERS:
            return sorted(exact), False
        if len(shield) < BACKOFF_K:
            return [], True
        if self.mode == MODE_LEXICAL_CONTROL:
            return shield[:BACKOFF_K], True
        query_cell = np.asarray(self.cell_of(name, state), dtype=np.int8)
        member_cells = np.asarray([self.cell_of(member, state) for member in shield], dtype=np.int8)
        distances = hamming_distances(query_cell, member_cells)
        ranked = sorted(range(len(shield)), key=lambda i: (int(distances[i]), shield[i]))
        return [shield[i] for i in ranked[:BACKOFF_K]], True

    def shield_query(self, name: str, acquired: tuple[str, ...], tau: float) -> tuple[list[str], dict[str, float], list[str], bool]:
        members, used_backoff = self.selected_members(name, acquired)
        wc = {arm: math.inf for arm in PORTFOLIO}
        if len(members) >= r22.MIN_CELL_MEMBERS:
            for arm in PORTFOLIO:
                wc[arm] = max(self.excess_member(member, arm) for member in members)
        admissible = sorted(arm for arm in PORTFOLIO if wc[arm] <= tau)
        return admissible, wc, members, used_backoff


def static_score(ctx: FoldContext, arm: str, name: str, acquired: tuple[str, ...]) -> dict[str, float]:
    _, wc, _, _ = ctx.shield_query(name, acquired, TAU)
    return {a: wc[a] for a in PORTFOLIO}


def learned_score(ctx: FoldContext, arm: str, name: str, acquired: tuple[str, ...]) -> dict[str, float]:
    return ctx.propose_errors(arm, acquired, name)


def score_for(arm: str) -> Callable[[FoldContext, str, str, tuple[str, ...]], dict[str, float]]:
    if arm.startswith("LEARNED_") or arm.startswith("SHUFFLED_"):
        return learned_score
    return static_score


def _commit_decision(ctx: FoldContext, acquired: tuple[str, ...], committed: str, wc: dict[str, float],
                     members: list[str], used_backoff: bool) -> dict[str, Any]:
    return {
        "committed": committed,
        "acquired": sorted(acquired),
        "certified": True,
        "fallback": False,
        "bound": json_float(wc[committed]),
        "wc": wc[committed],
        "members": members,
        "used_backoff": used_backoff,
    }


def walk(ctx: FoldContext, name: str, arm: str, tau: float) -> dict[str, Any]:
    """Myopic acquisition walk; scorers can rank only shield-admissible arms."""
    scorer = score_for(arm)
    acquired: tuple[str, ...] = ()
    if arm == "SHIELD_FREE":
        admissible, wc, members, used = ctx.shield_query(name, (), tau)
        if not admissible:
            return ctx.fallback_decision(())
        best = min(admissible, key=lambda a: (wc[a], a))
        return _commit_decision(ctx, (), best, wc, members, used)
    if arm == "SHIELD_FULL":
        full = tuple(sorted(GROUPS))
        admissible, wc, members, used = ctx.shield_query(name, full, tau)
        if not admissible:
            return ctx.fallback_decision(full)
        best = min(admissible, key=lambda a: (wc[a], a))
        return _commit_decision(ctx, full, best, wc, members, used)
    while True:
        admissible, wc, members, used = ctx.shield_query(name, acquired, tau)
        legal = sorted(g for g in GROUPS if g not in acquired)
        if not admissible:
            if legal:
                acquired = acquired + (legal[0],)
                continue
            return ctx.fallback_decision(acquired)
        scores_now = scorer(ctx, arm, name, acquired)
        commit_loss_now = min(scores_now[a] for a in admissible)
        gains: dict[str, float] = {}
        for group in legal:
            next_acquired = acquired + (group,)
            next_admissible, _, _, _ = ctx.shield_query(name, next_acquired, tau)
            gains[group] = (
                -math.inf
                if not next_admissible
                else commit_loss_now - min(scorer(ctx, arm, name, next_acquired)[a] for a in next_admissible)
            )
        finite = {g: value for g, value in gains.items() if value > -math.inf}
        best_group = max(sorted(finite), key=lambda g: finite[g]) if finite else None
        if best_group is not None and finite[best_group] > TOL:
            acquired = acquired + (best_group,)
            continue
        best = min(admissible, key=lambda a: (scores_now[a], a))
        return _commit_decision(ctx, acquired, best, wc, members, used)


def walk_with_scorer(ctx: FoldContext, name: str, arm: str, tau: float, scorer: Callable) -> dict[str, Any]:
    """The production walk with an injected hostile scorer for invariance tests."""
    acquired: tuple[str, ...] = ()
    while True:
        admissible, wc, members, used = ctx.shield_query(name, acquired, tau)
        legal = sorted(g for g in GROUPS if g not in acquired)
        if not admissible:
            if legal:
                acquired = acquired + (legal[0],)
                continue
            return ctx.fallback_decision(acquired)
        scores_now = scorer(ctx, arm, name, acquired)
        commit_loss_now = min(scores_now[a] for a in admissible)
        gains = {}
        for group in legal:
            nxt = acquired + (group,)
            adm2, _, _, _ = ctx.shield_query(name, nxt, tau)
            gains[group] = -math.inf if not adm2 else commit_loss_now - min(scorer(ctx, arm, name, nxt)[a] for a in adm2)
        finite = {g: value for g, value in gains.items() if value > -math.inf}
        best_group = max(sorted(finite), key=lambda g: finite[g]) if finite else None
        if best_group is not None and finite[best_group] > TOL:
            acquired = acquired + (best_group,)
            continue
        best = min(admissible, key=lambda a: (scores_now[a], a))
        return _commit_decision(ctx, acquired, best, wc, members, used)


def excess_of(ctx: FoldContext, name: str, decision: dict[str, Any]) -> float:
    committed = decision["committed"]
    if committed not in PORTFOLIO:
        raise ValueError(f"non-executable committed arm: {committed}")
    return ctx.excess_member(name, committed)


def evaluate_arm(ctx: FoldContext, names: Sequence[str], arm: str, tau: float) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for name in names:
        decision = walk(ctx, name, arm, tau)
        excess = json_float(excess_of(ctx, name, decision))
        rows[name] = {
            "committed": decision["committed"],
            "acquired": decision["acquired"],
            "groups_acquired": len(decision["acquired"]),
            "certified": decision["certified"],
            "fallback": decision["fallback"],
            "bound": decision["bound"],
            "excess": excess,
            "pool_members": decision["members"],
            "used_backoff": decision["used_backoff"],
            "violation_strict": bool(decision["certified"] and excess > decision["bound"] + TOL),
            "violation_tau": bool(decision["certified"] and excess > tau + TOL),
        }
    return rows


def arm_summary(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    excesses = np.asarray([row["excess"] for row in rows.values()], dtype=float)
    certified = [row for row in rows.values() if row["certified"]]
    return {
        "n": len(rows),
        "mean_excess": json_float(float(excesses.mean())),
        "p95_excess": json_float(float(np.percentile(excesses, 95.0))),
        "max_excess": json_float(float(excesses.max())),
        "mean_groups_acquired": json_float(float(np.mean([row["groups_acquired"] for row in rows.values()]))),
        "certified_n": len(certified),
        "certified_fraction": json_float(float(len(certified) / len(rows))),
        "fallback_fraction": json_float(float(np.mean([row["fallback"] for row in rows.values()]))),
        "backoff_fraction": json_float(float(np.mean([row["used_backoff"] for row in rows.values()]))),
        "violations_strict": sum(row["violation_strict"] for row in certified),
        "violations_tau": sum(row["violation_tau"] for row in certified),
        "mean_bound": (
            json_float(float(np.mean([row["bound"] for row in certified]))) if certified else None
        ),
    }


def select_primary(rows_by_arm: dict[str, dict[str, dict[str, Any]]]) -> str:
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


def policy_phase(mode: str, fold_of: dict[str, int], meta: dict[str, dict[str, list[float]]],
                 outcomes: dict[str, dict[str, float]]) -> dict[int, dict[str, Any]]:
    per_fold: dict[int, dict[str, Any]] = {}
    for fold in range(N_FOLDS):
        roles = r22.role_names(fold, fold_of)
        ctx = FoldContext(fold, roles, meta, outcomes, mode)
        threshold = {arm: evaluate_arm(ctx, roles["threshold_select"], arm, TAU) for arm in LEARNED_ARMS + SHUFFLED_ARMS}
        primary = select_primary({arm: threshold[arm] for arm in LEARNED_ARMS})
        tests = {arm: evaluate_arm(ctx, roles["test"], arm, TAU) for arm in TEST_ARMS}
        per_fold[fold] = {
            "roles": roles,
            "f_star_arm": ctx.f_star_arm,
            "primary": primary,
            "threshold_select": threshold,
            "test": tests,
        }
    return per_fold


def lexical_control_phase(fold_of: dict[str, int], meta: dict[str, dict[str, list[float]]],
                          outcomes: dict[str, dict[str, float]]) -> dict[int, dict[str, Any]]:
    per_fold = {}
    for fold in range(N_FOLDS):
        roles = r22.role_names(fold, fold_of)
        ctx = FoldContext(fold, roles, meta, outcomes, MODE_LEXICAL_CONTROL)
        per_fold[fold] = {
            "roles": roles,
            "f_star_arm": ctx.f_star_arm,
            "test": {"STATIC_ADAPTIVE": evaluate_arm(ctx, roles["test"], "STATIC_ADAPTIVE", TAU)},
        }
    return per_fold


def pool_rows(per_fold: dict[int, dict[str, Any]], meta: dict[str, dict[str, list[float]]],
              outcomes: dict[str, dict[str, float]], mode: str) -> dict[str, dict[str, Any]]:
    rows = {}
    full = tuple(sorted(GROUPS))
    for fold in range(N_FOLDS):
        roles = per_fold[fold]["roles"]
        ctx = FoldContext(fold, roles, meta, outcomes, mode)
        for name in roles["test"]:
            admissible, wc, members, used = ctx.shield_query(name, full, TAU)
            rows[name] = {
                "fold": fold,
                "members": members,
                "used_backoff": used,
                "admissible": admissible,
                "best_bound": json_float(min(wc[a] for a in admissible)) if admissible else None,
            }
    return {name: rows[name] for name in sorted(rows)}


def pool_summary(rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "pool_formed_fraction": json_float(float(np.mean([len(row["members"]) >= BACKOFF_K for row in rows.values()]))),
        "certified_coverage": json_float(float(np.mean([bool(row["admissible"]) for row in rows.values()]))),
        "backoff_used_fraction": json_float(float(np.mean([row["used_backoff"] for row in rows.values()]))),
        "mean_pool_size": json_float(float(np.mean([len(row["members"]) for row in rows.values()]))),
    }


def pooled_rows(per_fold: dict[int, dict[str, Any]], arm: str) -> dict[str, dict[str, Any]]:
    rows = {}
    for fold in range(N_FOLDS):
        rows.update(per_fold[fold]["test"][arm])
    return rows


def pooled_primary(per_fold: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows = {}
    for fold in range(N_FOLDS):
        arm = per_fold[fold]["primary"]
        rows.update(per_fold[fold]["test"][arm])
    return rows


def paired_bootstrap(diffs: np.ndarray, label: str) -> dict[str, Any]:
    rng = np.random.default_rng(derive_seed(BOOTSTRAP_SEED_TEXT, label))
    indices = rng.integers(0, diffs.size, size=(BOOTSTRAP_REPLICATES, diffs.size))
    means = diffs[indices].mean(axis=1)
    lo, hi = (float(x) for x in np.percentile(means, [2.5, 97.5]))
    return {"ci_lower": json_float(lo), "ci_upper": json_float(hi), "replicates": BOOTSTRAP_REPLICATES}


def comparison(left: dict[str, dict[str, Any]], right: dict[str, dict[str, Any]], label: str) -> dict[str, Any]:
    names = sorted(set(left) & set(right))
    if names != sorted(left) or names != sorted(right):
        raise ValueError("paired comparison subject mismatch")
    diffs = np.asarray([left[name]["excess"] - right[name]["excess"] for name in names], dtype=float)
    boot = paired_bootstrap(diffs, label)
    return {
        "left_minus_right_by_dataset": {name: json_float(diffs[i]) for i, name in enumerate(names)},
        "mean_diff": json_float(float(diffs.mean())),
        "ci_lower": boot["ci_lower"],
        "ci_upper": boot["ci_upper"],
        "bootstrap_replicates": boot["replicates"],
    }


def decide_terminal(payload: dict[str, Any]) -> str:
    if not all(payload["hostile_controls"].values()):
        return "C_R23_PMLB_BACKOFF_HOSTILE_CONTROL_FAILED"
    parent_cov = payload["coverage"]["r22c_exact_full_state"]
    coverage = payload["coverage"]["r23_backoff_full_state"]
    if coverage <= parent_cov + TOL:
        return "C_R23_PMLB_BACKOFF_NO_COVERAGE_IMPROVEMENT"
    if coverage < COVERAGE_TARGET - TOL:
        return "C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE"
    primary = payload["arms_summary"]["R23_BACKOFF_PRIMARY_LEARNED"]
    certified_n = primary.get("certified_n", primary["n"])
    violation_rate = primary["violations_strict"] / certified_n if certified_n else math.inf
    if violation_rate > VALIDITY_GATE + TOL:
        return "C_R23_PMLB_BACKOFF_CERTIFICATE_INVALID"
    static = payload["arms_summary"]["R23_BACKOFF_STATIC_ADAPTIVE"]
    test = payload["primary_test"]
    ratio_ok = test["primary_mean_excess"] <= (1.0 - MATERIAL_FRACTION) * static["mean_excess"] + TOL
    cost_ok = test["mean_groups_acquired_primary"] <= test["mean_groups_acquired_static"] + TOL
    if test["mean_diff"] < -TOL and ratio_ok and test["ci_upper"] < 0.0 and cost_ok:
        return "C_R23_PMLB_BACKOFF_VALUE"
    if test["mean_diff"] < -TOL:
        return "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NOT_MATERIAL"
    if abs(test["mean_diff"]) <= TOL:
        return "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_NULL"
    return "C_R23_PMLB_BACKOFF_COVERAGE_RESTORED_VALUE_ADVERSE"


def _copy_context(base: Any, mode: str) -> FoldContext:
    ctx = object.__new__(FoldContext)
    ctx.fold = base.fold
    ctx.roles = {role: sorted(names) for role, names in base.roles.items()}
    ctx.meta = base.meta
    ctx.outcomes = base.outcomes
    ctx.scalar_layout = list(base.scalar_layout)
    ctx.edges = list(base.edges)
    ctx.vectors = {name: np.array(values, copy=True) for name, values in base.vectors.items()}
    ctx._cells = {}
    ctx._proposers = {}
    ctx.custody_seen = set()
    ctx.mode = mode
    ctx.f_star_arm = min(
        PORTFOLIO,
        key=lambda arm: (float(np.mean([ctx.outcomes[name][arm] for name in ctx.roles["shield_table"]])), arm),
    )
    return ctx


def synthetic_fixture(mode: str = MODE_BACKOFF) -> tuple[FoldContext, dict[str, Any]]:
    base, info = r22.synthetic_fixture()
    return _copy_context(base, mode), info


def synthetic_sparse_fixture(mode: str = MODE_BACKOFF) -> tuple[FoldContext, dict[str, Any]]:
    shield = ["shield_a", "shield_b", "shield_c"]
    queries = ["query", "query_dense"]
    proposer = [f"prop{i}" for i in range(4)]
    threshold = ["threshold"]
    meta: dict[str, dict[str, list[float]]] = {}
    vectors = {
        "shield_a": [0.0, 0.0, 0.0],
        "shield_b": [1.0, 1.0, 0.0],
        "shield_c": [0.0, 0.0, 1.0],
        "query": [1.0, 1.0, 1.0],
        "query_dense": [0.0, 0.0, 0.5],
        "prop0": [0.0, 0.0, 0.0],
        "prop1": [1.0, 1.0, 1.0],
        "prop2": [0.0, 1.0, 0.0],
        "prop3": [1.0, 0.0, 1.0],
        "threshold": [0.0, 1.0, 1.0],
    }
    for name, values in vectors.items():
        meta[name] = {"G0": values[:2], "G1": [values[2]], "G2": [0.0], "G3": [0.0]}
    outcomes = {}
    for i, name in enumerate(vectors):
        row = {arm: 0.10 + 0.01 * j + 0.001 * i for j, arm in enumerate(PORTFOLIO)}
        row["best"] = min(row.values())
        outcomes[name] = row
    ctx = object.__new__(FoldContext)
    ctx.fold = 0
    ctx.roles = {"test": queries, "proposer_train": proposer, "shield_table": shield, "threshold_select": threshold}
    ctx.meta = meta
    ctx.outcomes = outcomes
    ctx.scalar_layout = [("G0", 0), ("G0", 1), ("G1", 0)]
    ctx.edges = [0.5, 0.5, 0.5]
    ctx.vectors = {name: np.asarray(values, dtype=float) for name, values in vectors.items()}
    ctx._cells = {}
    ctx._proposers = {}
    ctx.custody_seen = set()
    ctx.mode = mode
    ctx.f_star_arm = "dct"
    return ctx, {"shield": shield, "queries": queries}


def hostile_controls(exact: dict[int, dict[str, Any]], backoff: dict[int, dict[str, Any]],
                     exact_repeat: dict[int, dict[str, Any]], backoff_repeat: dict[int, dict[str, Any]],
                     audit: dict[str, dict[str, Any]], outcomes: dict[str, dict[str, float]],
                     negative_control: dict[int, dict[str, Any]]) -> dict[str, bool]:
    controls: dict[str, bool] = {}
    controls["r22_executor_binding"] = sha256_bytes(R22_EXECUTOR.read_bytes()) == R22_EXECUTOR_SHA256
    controls["r22_dataset_freeze_binding"] = sha256_bytes(R22_FREEZE.read_bytes()) == R22_FREEZE_SHA256
    controls["metadata_audit"] = all(row["bytes_match_freeze_sha256"] and row["rows_features_classes_match"] for row in audit.values())
    controls["determinism_exact_policy"] = digest_json(exact) == digest_json(exact_repeat)
    controls["determinism_backoff_policy"] = digest_json(backoff) == digest_json(backoff_repeat)
    controls["f_star_is_executable_best_shield_arm"] = all(
        fold_row["f_star_arm"] in PORTFOLIO
        and fold_row["f_star_arm"] == min(
            PORTFOLIO,
            key=lambda arm: (
                float(np.mean([outcomes[name][arm] for name in fold_row["roles"]["shield_table"]])),
                arm,
            ),
        )
        for fold_row in exact.values()
    )
    controls["all_excesses_nonnegative"] = all(
        row["excess"] >= -TOL
        for phase in (exact, backoff, negative_control)
        for fold_row in phase.values()
        for arm_rows in fold_row["test"].values()
        for row in arm_rows.values()
    )
    controls["fold_partition_disjoint"] = all(
        not (set(row["roles"]["test"]) & set(row["roles"][role]))
        for row in backoff.values()
        for role in ("proposer_train", "shield_table", "threshold_select")
    )
    controls["vbs_dominance"] = all(outcomes[name]["best"] <= min(outcomes[name][arm] for arm in PORTFOLIO) + TOL for name in outcomes)
    syn, info = synthetic_fixture(MODE_BACKOFF)
    def hostile(c, arm, name, acquired):
        admissible, _, _, _ = c.shield_query(name, acquired, TAU)
        forbidden = next((a for a in PORTFOLIO if a not in admissible), PORTFOLIO[-1])
        return {a: (0.0 if a == forbidden else 1.0) for a in PORTFOLIO}
    invariant = True
    for name in info["queries"]:
        decision = walk_with_scorer(syn, name, "STATIC_ADAPTIVE", TAU, hostile)
        admissible, _, _, _ = syn.shield_query(name, tuple(decision["acquired"]), TAU)
        invariant = invariant and (decision["fallback"] or decision["committed"] in admissible)
    controls["hostile_scorer_admissibility_invariance"] = invariant
    sparse, _ = synthetic_sparse_fixture(MODE_BACKOFF)
    before = sparse.selected_members("query", ("G1",))
    sparse.roles["shield_table"] = list(reversed(sparse.roles["shield_table"]))
    sparse._cells = {}
    controls["backoff_order_invariance"] = before == sparse.selected_members("query", ("G1",))
    controls["negative_control_separate"] = bool(negative_control) and MODE_LEXICAL_CONTROL != MODE_BACKOFF
    return controls


def validate_r22_result(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if sha256_bytes(data) != R22_RESULT_SHA256:
        raise ValueError("frozen R22 result binding drift")
    payload = json.loads(data)
    if payload.get("terminal") != R22_TERMINAL:
        raise ValueError("frozen R22 terminal drift")
    if payload.get("coverage", {}).get("primary_tau_full_state") != 0.0:
        raise ValueError("frozen R22 coverage drift")
    return payload


def build_corrected_parent_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": PARENT_SCHEMA,
        "original_r22": payload["original_r22"],
        "correction": payload["evaluator_correction"],
        "corpus": payload["corpus"],
        "outcomes_sha256": digest_json(payload["outcomes"]),
        "meta_features_sha256": digest_json(payload["meta_features"]),
        "coverage_records": payload["coverage_records"][MODE_EXACT],
        "coverage": payload["coverage"]["r22c_exact_full_state"],
        "arms_summary": {
            key: value for key, value in payload["arms_summary"].items() if key.startswith("R22C_EXACT_")
        },
        "folds": payload["folds"][MODE_EXACT],
        "authority": {
            "scientific_authority_delta": "NONE",
            "submission_authorized": False,
            "top_tier_gate_pass": False,
            "original_negative_preserved": True,
        },
    }


def execute(subject_repo: Path, freeze_path: Path, r22_result_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    original = validate_r22_result(r22_result_path)
    if sha256_bytes(freeze_path.read_bytes()) != R22_FREEZE_SHA256:
        raise ValueError("R22 dataset freeze binding drift")
    freeze = r22.load_freeze(freeze_path)
    corpus_loaded = r22.verify_and_load_corpus(subject_repo, freeze)
    loaded, audit = corpus_loaded["loaded"], corpus_loaded["audit"]
    excluded = sorted(name for name, data in loaded.items() if data["min_class_count"] < r22.MIN_CLASS_COUNT)
    admissible = sorted(name for name, data in loaded.items() if data["min_class_count"] >= r22.MIN_CLASS_COUNT)
    fold_of = r22.assign_folds(admissible)
    outcomes, meta = r22.generate_outcomes(loaded, freeze)

    exact = policy_phase(MODE_EXACT, fold_of, meta, outcomes)
    exact_repeat = policy_phase(MODE_EXACT, fold_of, meta, outcomes)
    backoff = policy_phase(MODE_BACKOFF, fold_of, meta, outcomes)
    backoff_repeat = policy_phase(MODE_BACKOFF, fold_of, meta, outcomes)
    negative_control = lexical_control_phase(fold_of, meta, outcomes)

    exact_pool = pool_rows(exact, meta, outcomes, MODE_EXACT)
    backoff_pool = pool_rows(backoff, meta, outcomes, MODE_BACKOFF)
    negative_pool = pool_rows(negative_control, meta, outcomes, MODE_LEXICAL_CONTROL)
    exact_pool_summary = pool_summary(exact_pool)
    backoff_pool_summary = pool_summary(backoff_pool)
    negative_pool_summary = pool_summary(negative_pool)

    exact_static = pooled_rows(exact, "STATIC_ADAPTIVE")
    exact_primary = pooled_primary(exact)
    backoff_static = pooled_rows(backoff, "STATIC_ADAPTIVE")
    backoff_primary = pooled_primary(backoff)
    negative_static = pooled_rows(negative_control, "STATIC_ADAPTIVE")

    summaries = {
        "R22C_EXACT_STATIC_ADAPTIVE": arm_summary(exact_static),
        "R22C_EXACT_PRIMARY_LEARNED": arm_summary(exact_primary),
        "R23_BACKOFF_STATIC_ADAPTIVE": arm_summary(backoff_static),
        "R23_BACKOFF_PRIMARY_LEARNED": arm_summary(backoff_primary),
        "R23_LEXICAL_CONTROL_STATIC_ADAPTIVE": arm_summary(negative_static),
    }
    for prefix, phase in (("R22C_EXACT", exact), ("R23_BACKOFF", backoff)):
        for arm in STATIC_ARMS + LEARNED_ARMS:
            summaries[f"{prefix}_{arm}"] = arm_summary(pooled_rows(phase, arm))

    primary_cmp = comparison(backoff_primary, backoff_static, "learned-v-static")
    primary_cmp.update({
        "comparator": "R23_BACKOFF_STATIC_ADAPTIVE",
        "primary_mean_excess": summaries["R23_BACKOFF_PRIMARY_LEARNED"]["mean_excess"],
        "static_mean_excess": summaries["R23_BACKOFF_STATIC_ADAPTIVE"]["mean_excess"],
        "mean_groups_acquired_primary": summaries["R23_BACKOFF_PRIMARY_LEARNED"]["mean_groups_acquired"],
        "mean_groups_acquired_static": summaries["R23_BACKOFF_STATIC_ADAPTIVE"]["mean_groups_acquired"],
    })
    matched_cmp = comparison(backoff_static, exact_static, "backoff-static-v-exact-static")
    matched_cmp.update({
        "left": "R23_BACKOFF_STATIC_ADAPTIVE",
        "right": "R22C_EXACT_STATIC_ADAPTIVE",
        "coverage_gain": json_float(backoff_pool_summary["certified_coverage"] - exact_pool_summary["certified_coverage"]),
    })

    controls = hostile_controls(exact, backoff, exact_repeat, backoff_repeat, audit, outcomes, negative_control)
    controls["original_r22_result_binding"] = sha256_bytes(r22_result_path.read_bytes()) == R22_RESULT_SHA256

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "upstream": {
            "repo": r22.PMLB_REPO,
            "commit": r22.PMLB_COMMIT,
            "tree": r22.PMLB_TREE,
            "license_blob": r22.LICENSE_BLOB,
            "summary_blob": r22.SUMMARY_BLOB,
        },
        "original_r22": {
            "result_sha256": R22_RESULT_SHA256,
            "executor_sha256": R22_EXECUTOR_SHA256,
            "dataset_freeze_sha256": R22_FREEZE_SHA256,
            "terminal": original["terminal"],
            "full_state_coverage": original["coverage"]["primary_tau_full_state"],
            "preserved_unchanged": True,
            "performance_values_authoritative": False,
            "performance_values_reason": "R22 scalar grand-mean F* was not an executable arm and produced impossible negative excess",
        },
        "evaluator_correction": {
            "name": "R22C_EXECUTABLE_F_STAR_ARM",
            "old_behavior": "scalar grand mean over every shield member and portfolio arm",
            "corrected_behavior": "single portfolio arm with minimum mean endpoint on shield-table rows; lexical arm tie",
            "applied_identically_to_parent_and_revival": True,
            "scientific_lever": False,
        },
        "r23_lever": {
            "name": MODE_BACKOFF,
            "k": BACKOFF_K,
            "distance": "direct Hamming distance over the current state's proposer-train median-split bit vector",
            "tie_break": "member dataset name lexical ascending",
            "activation": "only when the exact cell has fewer than two shield members",
            "worst_case": "exact maximum excess over the selected shield members",
            "outcome_independent_selection": True,
        },
        "negative_control": {
            "name": MODE_LEXICAL_CONTROL,
            "selection": "first two shield member names lexically when exact cell is sparse; ignores geometry and outcomes",
            "gating": False,
        },
        "corpus": {
            "frozen_datasets": len(freeze),
            "admissible": len(admissible),
            "excluded": excluded,
            "fold_assignment": {name: fold_of[name] for name in sorted(fold_of)},
            "fold_sizes": {str(fold): sum(value == fold for value in fold_of.values()) for fold in range(N_FOLDS)},
            "audit": audit,
        },
        "outcomes": {name: {arm: json_float(outcomes[name][arm]) for arm in list(PORTFOLIO) + ["best"]} for name in sorted(outcomes)},
        "meta_features": {name: {group: [json_float(value) for value in meta[name][group]] for group in ("G0", "G1", "G2", "G3")} for name in sorted(meta)},
        "folds": {
            MODE_EXACT: {str(fold): exact[fold] for fold in range(N_FOLDS)},
            MODE_BACKOFF: {str(fold): backoff[fold] for fold in range(N_FOLDS)},
            MODE_LEXICAL_CONTROL: {str(fold): negative_control[fold] for fold in range(N_FOLDS)},
        },
        "coverage_records": {
            MODE_EXACT: exact_pool,
            MODE_BACKOFF: backoff_pool,
            MODE_LEXICAL_CONTROL: negative_pool,
        },
        "coverage": {
            "r22_original_full_state": original["coverage"]["primary_tau_full_state"],
            "r22c_exact_full_state": exact_pool_summary["certified_coverage"],
            "r23_backoff_full_state": backoff_pool_summary["certified_coverage"],
            "negative_control_full_state": negative_pool_summary["certified_coverage"],
            "target": COVERAGE_TARGET,
            "exact_summary": exact_pool_summary,
            "backoff_summary": backoff_pool_summary,
            "negative_control_summary": negative_pool_summary,
        },
        "arms_summary": summaries,
        "primary_test": primary_cmp,
        "matched_parent_test": matched_cmp,
        "hostile_controls": controls,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "machine": platform.machine(),
        },
        "authority": {
            "scientific_authority_delta": "NONE",
            "submission_authorized": False,
            "top_tier_gate_pass": False,
            "freeze_authorized": False,
            "peer_reviewed_independent_reproduction": False,
            "scope": "pinned PMLB subject, identical corpus/folds/outcomes/budget only",
        },
    }
    payload["terminal"] = decide_terminal(payload)
    parent_receipt = build_corrected_parent_receipt(payload)
    payload["corrected_parent_receipt_sha256"] = digest_json(parent_receipt)
    return payload, parent_receipt


def run_self_test() -> None:
    exact, info = synthetic_fixture(MODE_EXACT)
    assert exact.f_star_arm == "dct"
    fallback = exact.fallback_decision(())
    assert fallback["committed"] in PORTFOLIO and fallback["fallback"]
    assert all(excess_of(exact, name, fallback) >= -TOL for name in info["queries"])
    sparse, _ = synthetic_sparse_fixture(MODE_BACKOFF)
    members, used = sparse.selected_members("query", ("G1",))
    assert used and members == ["shield_b", "shield_c"]
    dense, used_dense = sparse.selected_members("query_dense", ())
    assert not used_dense and dense == ["shield_a", "shield_c"]
    negative, _ = synthetic_sparse_fixture(MODE_LEXICAL_CONTROL)
    assert negative.selected_members("query", ("G1",))[0] == ["shield_a", "shield_b"]
    print("SELF_TEST_OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject-repo", type=Path)
    parser.add_argument("--freeze", type=Path, default=R22_FREEZE)
    parser.add_argument("--r22-result", type=Path, default=R22_RESULT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--corrected-parent-output", type=Path)
    parser.add_argument("--terminal-output", type=Path)
    parser.add_argument("--timings-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    required = (args.subject_repo, args.output, args.corrected_parent_output, args.terminal_output)
    if any(value is None for value in required):
        parser.error("--subject-repo, --output, --corrected-parent-output, and --terminal-output are required")
    started = time.time()
    try:
        payload, parent = execute(args.subject_repo.resolve(), args.freeze.resolve(), args.r22_result.resolve())
    except (ValueError, OSError, KeyError, MemoryError, RuntimeError, AssertionError) as exc:
        failure = {
            "schema": SCHEMA,
            "terminal": "CANNOT_CHECK_R23_PMLB_BACKOFF_SOURCE_RESOURCE_OR_BINDING",
            "failure_stage": type(exc).__name__,
            "failure_detail": str(exc)[:2000],
        }
        args.output.write_text(canonical_json(failure) + "\n")
        args.corrected_parent_output.write_text(canonical_json(failure) + "\n")
        args.terminal_output.write_text(failure["terminal"] + "\n")
        print(failure["terminal"])
        print("FAILURE_DETAIL " + failure["failure_detail"][:200])
        return 2
    args.output.write_text(canonical_json(payload) + "\n")
    args.corrected_parent_output.write_text(canonical_json(parent) + "\n")
    args.terminal_output.write_text(payload["terminal"] + "\n")
    if args.timings_output is not None:
        args.timings_output.write_text(canonical_json({
            "schema": "ORION.FiberGuard.PMLBProposalOrdering.R23.Timings.v1",
            "wall_seconds_total": round(time.time() - started, 3),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
            "machine": platform.machine(),
        }) + "\n")
    print(payload["terminal"])
    print("RESULT_SHA256 " + sha256_bytes(args.output.read_bytes()))
    print("CORRECTED_PARENT_SHA256 " + sha256_bytes(args.corrected_parent_output.read_bytes()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
