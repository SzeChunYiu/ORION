#!/usr/bin/env python3
"""ORION11.COSTED_EPISTEMIC_ORDERING.v1 runner.

Generates the frozen world family ORION11.COSTED_ORDERING.WORLDS.v1, runs the
registered arms, emits raw_traces.jsonl in TRACE_SCHEMA_V1 format, and computes
RESULT_V1.json (gates G1-G7, stratified bootstrap, Holm, terminal).

PREREGISTERED STUDY.  The protocol, the terminal set and the trace schema are
FROZEN.  This runner implements them as written.  Every deviation forced by an
internal inconsistency in the frozen documents is recorded in
RESULT_V1.json["protocol_concerns"] and is NOT silently resolved.

Stages
------
  --stage emit-anchor : run ONLY the non-gate arms, write the per-world-set
                        anchor reference, exit.  No gate arm is executed, so
                        no gate-relevant outcome can be read before the
                        reference is frozen.
  --stage run         : reproduce the anchor reference, then run every arm,
                        emit traces and the analysis object.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# FROZEN CONSTANTS.  Fixed before any world was generated or any arm was run.
# --------------------------------------------------------------------------
SUCCESSOR_ID = "ORION11.COSTED_EPISTEMIC_ORDERING.v1"
WORLD_FAMILY_ID = "ORION11.COSTED_ORDERING.WORLDS.v1"

# PROTOCOL.statistics says "seed frozen here" but PROTOCOL.json contains no
# literal seed.  See protocol_concerns[PC-02].  Both seeds below are fixed in
# this file before execution; the bootstrap seed is the value committed by the
# R4 predecessor runner.
FROZEN_WORLD_SEED = 20260828
FROZEN_BOOTSTRAP_SEED = 202608280411

N_WORLDS = 2882
BUDGET_CEILING = 4.0
RESAMPLES = 10000
DECOMP_TOL = 1e-9
G1_MARGIN = -0.01
G3_RATIO_THRESHOLD = 0.80
G4_DP_FACTOR = 1.10
HOLM_ALPHA = 0.05

PROBE_COST = 0.25          # cost of one Active-VOI diagnostic probe
REOPEN_UNIT_COST = 0.10    # cost per re-validated dependency-impact id

STRATA = (
    ("theorem_valid", 0.50),
    ("ratio_aligned", 0.10),
    ("violate_A1_noninterference", 0.10),
    ("violate_A2_veto_monotonicity", 0.10),
    ("violate_A3_safety", 0.10),
    ("violate_A4_nonnegative_cost", 0.10),
)

# TRACE_SCHEMA_V1 arm_id enum (7 arms).  PROTOCOL.arms declares 8; see
# protocol_concerns[PC-01].
SCHEMA_ARMS = (
    "exact_dp_oracle",
    "orion_level_monotone",
    "faithful_active_voi",
    "global_flat_voi",
    "gain_per_cost_greedy",
    "cost_greedy_repair",
    "random_safe_ablation",
)
OFF_SCHEMA_ARMS = ("random_unsafe_ablation",)

# Arms read by any of G1-G7.  Asserted mechanically below.
GATE_ARMS = frozenset(
    {"orion_level_monotone", "faithful_active_voi", "gain_per_cost_greedy", "exact_dp_oracle"}
)
# Anchor arms = arms read by NO gate.  Stage 1 runs only these.
ANCHOR_ARMS = tuple(a for a in SCHEMA_ARMS + OFF_SCHEMA_ARMS if a not in GATE_ARMS)

ORACLE_STRATA = frozenset({"theorem_valid", "ratio_aligned"})

LEVELS = (0, 1, 2)          # K (evidence), W (execution), M (mutation/high)
LEVEL_NAMES = {0: "K_evidence", 1: "W_execution", 2: "M_mutation"}


# ==========================================================================
# World family
# ==========================================================================
def stratum_counts() -> list[tuple[str, int]]:
    """Largest-remainder allocation of N_WORLDS across the declared shares.

    Tie-break on equal fractional parts: earliest stratum in PROTOCOL order.
    """
    raw = [(sid, N_WORLDS * share) for sid, share in STRATA]
    base = [(sid, int(math.floor(v))) for sid, v in raw]
    deficit = N_WORLDS - sum(n for _, n in base)
    frac = sorted(
        ((raw[i][1] - base[i][1], i) for i in range(len(raw))),
        key=lambda t: (-t[0], t[1]),
    )
    counts = dict(base)
    for _, idx in frac[:deficit]:
        counts[raw[idx][0]] += 1
    return [(sid, counts[sid]) for sid, _ in STRATA]


def _decreasing_ratios(rng: np.random.Generator, n: int) -> np.ndarray:
    """Strictly decreasing positive ratio targets with a guaranteed gap."""
    gaps = rng.uniform(0.06, 0.18, size=n)
    top = 1.40
    vals = top - np.cumsum(gaps) + gaps[0]
    return np.maximum(vals, 0.08)


def make_world(index: int, stratum: str) -> dict[str, Any]:
    """Generate one world.  Fully determined by (FROZEN_WORLD_SEED, index)."""
    seed = FROZEN_WORLD_SEED * 100000 + index
    rng = np.random.default_rng([FROZEN_WORLD_SEED, index])

    n_per_level = [int(rng.integers(2, 4)) for _ in LEVELS]   # 2..3 classes/level
    levels: list[int] = []
    for lv, k in zip(LEVELS, n_per_level):
        levels.extend([lv] * k)
    n = len(levels)

    if stratum == "ratio_aligned":
        # Construct the Theorem C equality case: p/c is strictly decreasing in
        # level, so the level-monotone order IS the flat p/c order.
        costs = rng.uniform(0.20, 0.90, size=n)
        ratios = _decreasing_ratios(rng, n)      # already level-sorted order
        p_raw = ratios * costs
        priors = p_raw / p_raw.sum()
    else:
        costs = rng.uniform(0.15, 0.95, size=n)
        p_raw = rng.uniform(0.3, 3.0, size=n)
        priors = p_raw / p_raw.sum()

    actual_costs = costs.copy()                  # host-side true expenditure, >= 0
    visible_costs = costs.copy()                 # candidate-visible per_check_cost

    if stratum == "violate_A4_nonnegative_cost":
        # The VIOLATION is in the world's cost structure (the published signal),
        # not in the accounting.  TRACE_SCHEMA hard invariant requires recorded
        # components to stay non-negative, so actual_costs are untouched.
        k = int(rng.integers(1, 3))
        victims = rng.choice(n, size=k, replace=False)
        for v in victims:
            visible_costs[v] = 0.0 if rng.random() < 0.5 else -rng.uniform(0.05, 0.40)

    # Interference likelihood table: P(observation == "SHIFT" | tested k negative,
    # true class j).  Uniform 0.5 => uninformative => A1 (noninterference) holds.
    interference = np.full((n, n), 0.5)
    if stratum == "violate_A1_noninterference":
        for k in range(n):
            for j in range(n):
                if levels[j] > levels[k]:
                    interference[k][j] = 0.82
                elif levels[j] < levels[k]:
                    interference[k][j] = 0.18

    i_star = int(rng.choice(n, p=priors))

    # A2 exemptions: high-level classes legitimately admissible without
    # exhausting the level below.
    a2_exempt: set[int] = set()
    if stratum == "violate_A2_veto_monotonicity":
        highs = [i for i in range(n) if levels[i] > 0]
        if highs:
            k = int(rng.integers(1, min(3, len(highs)) + 1))
            a2_exempt = {int(x) for x in rng.choice(highs, size=k, replace=False)}

    a3_safety_active = stratum != "violate_A3_safety"

    # Host-only response structure.  Only i* is fully admissible.  A few
    # non-i* classes return target_success but fail admission (protected sibling
    # broken, or dependency impact mismatched): pure cost decoys, rejected
    # identically by every arm that applies the admission test.
    breaks_sibling = np.zeros(n, dtype=bool)
    dep_mismatch = np.zeros(n, dtype=bool)
    pseudo_success = np.zeros(n, dtype=bool)
    candidates = [i for i in range(n) if i != i_star and levels[i] > 0]
    if candidates:
        k = int(rng.integers(0, min(2, len(candidates)) + 1))
        if k:
            for d in rng.choice(candidates, size=k, replace=False):
                d = int(d)
                pseudo_success[d] = True
                if rng.random() < 0.5:
                    breaks_sibling[d] = True
                else:
                    dep_mismatch[d] = True

    dep_impact = rng.integers(0, 4, size=n)     # |dependency_impact_set|
    reopen = dep_impact * REOPEN_UNIT_COST

    return {
        "world_id": f"W{index:05d}",
        "stratum": stratum,
        "seed": seed,
        "n": n,
        "levels": levels,
        "visible_costs": visible_costs,      # candidate-visible per_check_cost
        "actual_costs": actual_costs,        # host-side true expenditure
        "confidences": priors,               # public_repair_menu confidence
        "priors": priors,                    # host-only true_class_priors
        "i_star": i_star,
        "interference": interference,        # public_diagnostic_menu likelihoods
        "a2_exempt": a2_exempt,
        "a3_safety_active": a3_safety_active,
        "breaks_sibling": breaks_sibling,
        "dep_mismatch": dep_mismatch,
        "pseudo_success": pseudo_success,
        "reopen": reopen,
        "dep_impact": dep_impact,
        "gold_minimal_repair": f"R{i_star:02d}",
    }


def build_world_family() -> list[dict[str, Any]]:
    worlds: list[dict[str, Any]] = []
    idx = 0
    for sid, count in stratum_counts():
        for _ in range(count):
            worlds.append(make_world(idx, sid))
            idx += 1
    assert len(worlds) == N_WORLDS, len(worlds)
    return worlds


def world_set_digest(worlds: list[dict[str, Any]]) -> str:
    """sha256 over the candidate-visible + host-only content of the world set."""
    h = hashlib.sha256()
    for w in worlds:
        h.update(w["world_id"].encode())
        h.update(w["stratum"].encode())
        h.update(str(w["seed"]).encode())
        h.update(np.asarray(w["levels"], dtype=np.int64).tobytes())
        h.update(np.round(w["visible_costs"], 12).tobytes())
        h.update(np.round(w["actual_costs"], 12).tobytes())
        h.update(np.round(w["priors"], 12).tobytes())
        h.update(np.round(w["interference"], 12).tobytes())
        h.update(str(w["i_star"]).encode())
        h.update(np.asarray(sorted(w["a2_exempt"]), dtype=np.int64).tobytes())
        h.update(b"1" if w["a3_safety_active"] else b"0")
        h.update(w["breaks_sibling"].tobytes())
        h.update(w["dep_mismatch"].tobytes())
        h.update(w["pseudo_success"].tobytes())
        h.update(np.asarray(w["dep_impact"], dtype=np.int64).tobytes())
    return h.hexdigest()


# ==========================================================================
# Session: the only channel between an arm and a world
# ==========================================================================
class Session:
    """Budgeted interaction.  Arms see candidate-visible fields only."""

    def __init__(self, world: dict[str, Any], rng: np.random.Generator):
        self.w = world
        self.rng = rng
        self.n = world["n"]
        self.levels = list(world["levels"])
        self.visible_costs = list(world["visible_costs"])
        self.confidences = list(world["confidences"])
        self.interference = world["interference"]
        self.spent = 0.0
        self.inspection = 0.0
        self.intervention = 0.0
        self.reopening = 0.0
        self.tested: list[int] = []
        self.actions: list[dict[str, Any]] = []
        self.selected: int | None = None
        self.terminated_reason = "not_started"
        self.budget_exceeded = False
        self._step = 0

    # -- internals ---------------------------------------------------------
    def _afford(self, cost: float) -> bool:
        return self.spent + cost <= BUDGET_CEILING + DECOMP_TOL

    def _log(self, kind: str, level: int | None, target: str, component: str, cost: float):
        self._step += 1
        self.actions.append(
            {
                "step": self._step,
                "kind": kind,
                "level": level,
                "target": target,
                "cost_component": component,
                "cost": float(cost),
            }
        )

    # -- arm-facing API ----------------------------------------------------
    def run_probe(self, probe_kind: str) -> str | None:
        """Active-VOI diagnostic probe.  Returns None if unaffordable."""
        if not self._afford(PROBE_COST):
            self.budget_exceeded = True
            return None
        self.spent += PROBE_COST
        self.inspection += PROBE_COST
        self._log("probe", None, probe_kind, "inspection", PROBE_COST)
        lvl = self.levels[self.w["i_star"]]
        if probe_kind == "source":
            return "SOURCE_GAP" if lvl == 0 else "NO_SOURCE_GAP"
        return "EXECUTION_GAP" if lvl == 1 else "NO_EXECUTION_GAP"

    def test_repair(self, cid: int) -> dict[str, Any] | None:
        """Trial-apply repair class ``cid``.  This IS a mutation (A3)."""
        cost = float(self.w["actual_costs"][cid])
        if not self._afford(cost):
            self.budget_exceeded = True
            return None
        self.spent += cost
        self.tested.append(cid)
        is_star = cid == self.w["i_star"]
        target_success = bool(is_star or self.w["pseudo_success"][cid])
        sibling_ok = not bool(self.w["breaks_sibling"][cid])
        dep_ok = not bool(self.w["dep_mismatch"][cid])
        admissible = target_success and sibling_ok and dep_ok
        component = "intervention" if admissible else "inspection"
        if admissible:
            self.intervention += cost
        else:
            self.inspection += cost
        self._log("test_repair", self.levels[cid], f"R{cid:02d}", component, cost)
        obs = None
        if not admissible:
            pstar = float(self.interference[cid][self.w["i_star"]])
            obs = "SHIFT" if self.rng.random() < pstar else "NO_SHIFT"
        return {
            "cid": cid,
            "target_success": target_success,
            "protected_sibling_ok": sibling_ok,
            "dependency_impact_match": dep_ok,
            "admissible": admissible,
            "observation": obs,
        }

    def commit(self, cid: int) -> None:
        """Select an admissible repair and pay its dependency reopening."""
        self.selected = cid
        cost = float(self.w["reopen"][cid])
        if not self._afford(cost):
            self.budget_exceeded = True
            self.selected = None
            self.terminated_reason = "budget_exhausted_on_reopening"
            return
        self.spent += cost
        self.reopening += cost
        self._log("reopen", self.levels[cid], f"R{cid:02d}", "reopening", cost)


# ==========================================================================
# Belief and ordering helpers (arm-side; visible fields only)
# ==========================================================================
def ratio_key(belief: np.ndarray, visible_costs: list[float], cid: int) -> tuple:
    """Smith-ratio sort key.  Visible cost <= 0 => +inf ratio, checked first.

    Within the +inf group, most-negative visible cost first (it reduces cost),
    then class index.  Deterministic, no float accident.
    """
    c = visible_costs[cid]
    if c <= 0.0:
        return (0, c, cid)
    return (1, -(belief[cid] / c), cid)


def bayes_update(belief: np.ndarray, interference: np.ndarray, cid: int, obs: str | None) -> np.ndarray:
    """Exclude the tested class; fold in the emitted interference likelihood."""
    b = belief.copy()
    b[cid] = 0.0
    if obs is not None:
        lik = interference[cid]
        b = b * (lik if obs == "SHIFT" else (1.0 - lik))
    s = b.sum()
    if s <= 0.0:
        b = np.zeros_like(belief)
        return b
    return b / s


def filtration_violated(world: dict[str, Any], tested: list[int]) -> bool:
    """A3: mutation at level > L(i*) before F_{L(i*)} exhausted."""
    if not world["a3_safety_active"]:
        return False
    levels = world["levels"]
    lstar = levels[world["i_star"]]
    below = {i for i in range(world["n"]) if levels[i] <= lstar}
    seen: set[int] = set()
    for cid in tested:
        if levels[cid] > lstar and not below.issubset(seen) and cid not in world["a2_exempt"]:
            return True
        seen.add(cid)
    return False


# ==========================================================================
# Arms
# ==========================================================================
def _run_ordering_policy(sess: Session, key_fn: Callable[[np.ndarray, int], tuple],
                         admissible_ids: Callable[[np.ndarray], list[int]]) -> None:
    """Adaptive ordering arm: re-rank the remaining classes after every
    observation, then test the current best.  Under A1 the emitted likelihood
    is uninformative, so this is identical to a static ordering."""
    belief = np.asarray(sess.confidences, dtype=float).copy()
    belief = belief / belief.sum()
    remaining = set(range(sess.n))
    while remaining:
        pool = [c for c in admissible_ids(belief) if c in remaining]
        if not pool:
            sess.terminated_reason = "no_admissible_candidate_remaining"
            return
        pool.sort(key=lambda c: key_fn(belief, c))
        cid = pool[0]
        r = sess.test_repair(cid)
        if r is None:
            sess.terminated_reason = "budget_exhausted"
            return
        if r["admissible"]:
            sess.commit(cid)
            if sess.selected is not None:
                sess.terminated_reason = "admissible_repair_selected"
            return
        remaining.discard(cid)
        belief = bayes_update(belief, sess.interference, cid, r["observation"])
    sess.terminated_reason = "menu_exhausted_no_admissible_repair"


def arm_orion_level_monotone(sess: Session) -> None:
    """Responsibility filtration: level-monotone, p/c within level, admission
    test (protected sibling + dependency impact) applied."""
    def gate(_belief):
        # open level l+1 only when every class in F_l has been tested
        tested = set(sess.tested)
        for lv in LEVELS:
            at = [c for c in range(sess.n) if sess.levels[c] == lv]
            open_here = [c for c in at if c not in tested]
            if open_here:
                return open_here
        return []
    _run_ordering_policy(sess, lambda b, c: ratio_key(b, sess.visible_costs, c), gate)


def arm_gain_per_cost_greedy(sess: Session) -> None:
    """Unconstrained p/c ordering (Theorem A).  Mandatory donor baseline."""
    _run_ordering_policy(
        sess,
        lambda b, c: ratio_key(b, sess.visible_costs, c),
        lambda b: list(range(sess.n)),
    )


def arm_global_flat_voi(sess: Session) -> None:
    """VOI over all levels at once, no filtration, cost-blind."""
    _run_ordering_policy(
        sess,
        lambda b, c: (-b[c], c),
        lambda b: list(range(sess.n)),
    )


def arm_cost_greedy_repair(sess: Session) -> None:
    """Cheapest check first, priors ignored."""
    _run_ordering_policy(
        sess,
        lambda b, c: (sess.visible_costs[c], c),
        lambda b: list(range(sess.n)),
    )


def arm_random_safe_ablation(sess: Session) -> None:
    """Random admissible (topological) ordering."""
    order = {c: sess.rng.random() for c in range(sess.n)}
    def gate(_belief):
        tested = set(sess.tested)
        for lv in LEVELS:
            at = [c for c in range(sess.n) if sess.levels[c] == lv]
            open_here = [c for c in at if c not in tested]
            if open_here:
                return open_here
        return []
    _run_ordering_policy(sess, lambda b, c: (order[c], c), gate)


def arm_random_unsafe_ablation(sess: Session) -> None:
    """Random unconstrained ordering; may violate the filtration."""
    order = {c: sess.rng.random() for c in range(sess.n)}
    _run_ordering_policy(sess, lambda b, c: (order[c], c), lambda b: list(range(sess.n)))


def arm_faithful_active_voi(sess: Session) -> None:
    """Faithful to R4 ``activevoi_search_admitted_parent``.

    Exactly the frozen parent's structure: source probe -> branch and take the
    SINGLE top-confidence evidence repair; else execution probe -> branch and
    take the SINGLE top-confidence execution repair; else ordered high-level
    search under the admission test the parent already applies.  Only the final
    single high-level pick was turned into a search by the R4 repair; the
    lower-level single picks are preserved unchanged.
    """
    belief = np.asarray(sess.confidences, dtype=float).copy()
    belief = belief / belief.sum()

    src = sess.run_probe("source")
    if src is None:
        sess.terminated_reason = "no_budget_source_probe"
        return
    if src == "SOURCE_GAP":
        pool = [c for c in range(sess.n) if sess.levels[c] == 0]
        cid = sorted(pool, key=lambda c: (-belief[c], c))[0]
        r = sess.test_repair(cid)
        if r is None:
            sess.terminated_reason = "budget_exhausted"
            return
        if r["admissible"]:
            sess.commit(cid)
            if sess.selected is not None:
                sess.terminated_reason = "source_probe"
            return
        sess.terminated_reason = "source_probe"
        return

    ex = sess.run_probe("execution")
    if ex is None:
        sess.terminated_reason = "no_budget_execution_probe"
        return
    if ex == "EXECUTION_GAP":
        pool = [c for c in range(sess.n) if sess.levels[c] == 1]
        cid = sorted(pool, key=lambda c: (-belief[c], c))[0]
        r = sess.test_repair(cid)
        if r is None:
            sess.terminated_reason = "budget_exhausted"
            return
        if r["admissible"]:
            sess.commit(cid)
            if sess.selected is not None:
                sess.terminated_reason = "execution_probe"
            return
        sess.terminated_reason = "execution_probe"
        return

    # lower levels ruled out by the probes, then ordered admitted search
    remaining = {c for c in range(sess.n) if sess.levels[c] >= 2}
    while remaining:
        cid = sorted(remaining, key=lambda c: (-belief[c], c))[0]
        r = sess.test_repair(cid)
        if r is None:
            sess.terminated_reason = "budget_exhausted"
            return
        if r["admissible"]:
            sess.commit(cid)
            if sess.selected is not None:
                sess.terminated_reason = "lower_levels_ruled_out_then_search"
            return
        remaining.discard(cid)
        belief = bayes_update(belief, sess.interference, cid, r["observation"])
    sess.terminated_reason = "no_admissible_high_level_repair"


POLICY_ARMS: dict[str, Callable[[Session], None]] = {
    "orion_level_monotone": arm_orion_level_monotone,
    "faithful_active_voi": arm_faithful_active_voi,
    "global_flat_voi": arm_global_flat_voi,
    "gain_per_cost_greedy": arm_gain_per_cost_greedy,
    "cost_greedy_repair": arm_cost_greedy_repair,
    "random_safe_ablation": arm_random_safe_ablation,
    "random_unsafe_ablation": arm_random_unsafe_ablation,
}


# ==========================================================================
# Exact DP oracle (sees host-only fields)
# ==========================================================================
def dp_oracle(world: dict[str, Any]) -> dict[str, Any]:
    """Exact minimum expected cost by subset dynamic programming.

    E[total] = sum_k c_k * P(pos(i*) >= pos(k))  +  sum_j p_j * reopen_j
    The reopening term is ordering-independent.
    """
    n = world["n"]
    p = np.asarray(world["priors"], dtype=float)
    c = np.asarray(world["actual_costs"], dtype=float)
    full = (1 << n) - 1
    # f[S] = min expected inspection+intervention cost still to be paid given
    # that the classes in S have already been tested (and none was i*).
    f = np.full(1 << n, np.nan)
    nxt = np.full(1 << n, -1, dtype=np.int64)
    f[full] = 0.0
    for S in range(full - 1, -1, -1):
        rem_mass = sum(p[j] for j in range(n) if not (S >> j) & 1)
        best = math.inf
        best_j = -1
        for j in range(n):
            if (S >> j) & 1:
                continue
            val = c[j] * rem_mass + f[S | (1 << j)]
            if val < best - 1e-15:
                best = val
                best_j = j
        f[S] = best
        nxt[S] = best_j
    order: list[int] = []
    S = 0
    while S != full:
        j = int(nxt[S])
        order.append(j)
        S |= 1 << j
    # exact decomposition along the optimal order
    exp_inspection = 0.0
    exp_intervention = 0.0
    cum = 0.0
    for j in order:
        exp_intervention += c[j] * p[j]
        exp_inspection += c[j] * (1.0 - cum - p[j])
        cum += p[j]
    exp_reopen = float((p * np.asarray(world["reopen"], dtype=float)).sum())
    return {
        "order": order,
        "inspection": float(exp_inspection),
        "intervention": float(exp_intervention),
        "reopening": exp_reopen,
        "total": float(exp_inspection + exp_intervention + exp_reopen),
    }


def dp_matches_smith(world: dict[str, Any], order: list[int]) -> bool:
    """Instrument check: on a theorem-valid world the DP optimum must be the
    p/c-sorted order (Theorem A)."""
    p = np.asarray(world["priors"], dtype=float)
    c = np.asarray(world["actual_costs"], dtype=float)
    ratios = [p[j] / c[j] for j in order]
    return all(ratios[i] >= ratios[i + 1] - 1e-12 for i in range(len(ratios) - 1))


# ==========================================================================
# Execution
# ==========================================================================
def _arm_seed(arm_id: str) -> int:
    """Stable across processes: Python's str hash is salted per interpreter."""
    return int.from_bytes(hashlib.sha256(arm_id.encode()).digest()[:4], "big")


def run_arm(world: dict[str, Any], arm_id: str) -> dict[str, Any]:
    if arm_id == "exact_dp_oracle":
        d = dp_oracle(world)
        actions = []
        step = 0
        cum = 0.0
        p = np.asarray(world["priors"], dtype=float)
        c = np.asarray(world["actual_costs"], dtype=float)
        for j in d["order"]:
            step += 1
            actions.append({"step": step, "kind": "expected_test_rejected",
                            "level": world["levels"][j], "target": f"R{j:02d}",
                            "cost_component": "inspection",
                            "cost": float(c[j] * (1.0 - cum - p[j]))})
            step += 1
            actions.append({"step": step, "kind": "expected_test_selected",
                            "level": world["levels"][j], "target": f"R{j:02d}",
                            "cost_component": "intervention",
                            "cost": float(c[j] * p[j])})
            cum += p[j]
        step += 1
        actions.append({"step": step, "kind": "expected_reopen", "level": None,
                        "target": "ALL", "cost_component": "reopening",
                        "cost": d["reopening"]})
        return {
            "world_id": world["world_id"], "stratum": world["stratum"],
            "arm_id": arm_id, "seed": world["seed"],
            "protected_root_task_success": True,
            "forbidden_high_level_mutation": filtration_violated(world, d["order"]),
            "cost": {"inspection": d["inspection"], "intervention": d["intervention"],
                     "reopening": d["reopening"], "total": d["total"]},
            "budget_exceeded": bool(d["total"] > BUDGET_CEILING),
            "actions": actions,
            "terminated_reason": "exact_dp_optimum",
        }

    rng = np.random.default_rng([FROZEN_WORLD_SEED, world["seed"], _arm_seed(arm_id)])
    sess = Session(world, rng)
    POLICY_ARMS[arm_id](sess)
    success = sess.selected is not None and sess.selected == world["i_star"]
    total = sess.inspection + sess.intervention + sess.reopening
    return {
        "world_id": world["world_id"], "stratum": world["stratum"],
        "arm_id": arm_id, "seed": world["seed"],
        "protected_root_task_success": bool(success),
        "forbidden_high_level_mutation": filtration_violated(world, sess.tested),
        "cost": {"inspection": float(sess.inspection), "intervention": float(sess.intervention),
                 "reopening": float(sess.reopening), "total": float(total)},
        "budget_exceeded": bool(sess.budget_exceeded or total > BUDGET_CEILING + DECOMP_TOL),
        "actions": sess.actions,
        "terminated_reason": sess.terminated_reason,
    }


# ==========================================================================
# Hard validation, run BEFORE any statistic is computed
# ==========================================================================
def validate_rows(rows: list[dict[str, Any]], arms: tuple[str, ...],
                  worlds: list[dict[str, Any]]) -> dict[str, Any]:
    """TRACE_SCHEMA_V1 hard invariants.  Any breach => CANNOT_CHECK."""
    problems: list[str] = []
    undecomposable = 0
    worst = 0.0
    for r in rows:
        c = r["cost"]
        d = abs(c["total"] - (c["inspection"] + c["intervention"] + c["reopening"]))
        worst = max(worst, d)
        if d > DECOMP_TOL:
            undecomposable += 1
        for k in ("inspection", "intervention", "reopening", "total"):
            if c[k] < -DECOMP_TOL:
                problems.append(f"negative cost component {k} on {r['world_id']}/{r['arm_id']}")
        s = sum(a["cost"] for a in r["actions"])
        if abs(s - c["total"]) > 1e-8:
            problems.append(f"actions do not sum to total on {r['world_id']}/{r['arm_id']}")
        for forbidden_key in ("gate", "gates", "bootstrap", "terminal", "ci"):
            if forbidden_key in r:
                problems.append(f"row carries derived field {forbidden_key}")
    by_arm: dict[str, set[str]] = {a: set() for a in arms}
    for r in rows:
        by_arm[r["arm_id"]].add(r["world_id"])
    strat_of = {w["world_id"]: w["stratum"] for w in worlds}
    all_ids = {w["world_id"] for w in worlds}
    oracle_ids = {w for w in all_ids if strat_of[w] in ORACLE_STRATA}
    for a in arms:
        expect = oracle_ids if a == "exact_dp_oracle" else all_ids
        if by_arm[a] != expect:
            problems.append(f"arm coverage mismatch for {a}: "
                            f"{len(by_arm[a])} rows vs {len(expect)} expected")
    non_oracle = [a for a in arms if a != "exact_dp_oracle"]
    ref = by_arm[non_oracle[0]]
    for a in non_oracle[1:]:
        if by_arm[a] != ref:
            problems.append(f"pairing incomplete: {a} world set differs")
    return {
        "rows_checked": len(rows),
        "undecomposable_rows": undecomposable,
        "max_decomposition_residual": worst,
        "problems": problems,
        "passed": undecomposable == 0 and not problems,
    }


# ==========================================================================
# Anchor reproduction gate (parameterised per world set, never hardcoded)
# ==========================================================================
def anchor_rates(rows: list[dict[str, Any]], arms: tuple[str, ...]) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    for a in arms:
        sel = [r for r in rows if r["arm_id"] == a]
        n = len(sel)
        out[a] = {
            "success": sum(r["protected_root_task_success"] for r in sel) / n,
            "forbidden": sum(r["forbidden_high_level_mutation"] for r in sel) / n,
            "mean_total_cost": sum(r["cost"]["total"] for r in sel) / n,
            "n": n,
        }
    return out


def code_digest() -> str:
    return hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()


# ==========================================================================
# Statistics
# ==========================================================================
def stratified_resample_indices(strata_index: dict[str, np.ndarray],
                                rng: np.random.Generator) -> np.ndarray:
    return np.concatenate([rng.choice(idx, size=idx.size, replace=True)
                           for idx in strata_index.values()])


def percentile_ci(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return (float("nan"), float("nan"))
    v = sorted(vals)
    n = len(v)
    return (v[int(0.025 * n)], v[min(n - 1, int(0.975 * n))])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["emit-anchor", "run"], required=True)
    ap.add_argument("--anchor-reference", type=Path,
                    default=HERE / "ANCHOR_REFERENCE_COSTED_ORDERING_V1.json")
    ap.add_argument("--outdir", type=Path, default=HERE)
    ap.add_argument("--smoke", type=int, default=0,
                    help="debug only: N worlds with a DIFFERENT seed offset")
    args = ap.parse_args()

    global N_WORLDS, FROZEN_WORLD_SEED, RESAMPLES
    if args.smoke:
        N_WORLDS = args.smoke
        FROZEN_WORLD_SEED = 999999          # deliberately NOT the frozen seed
        RESAMPLES = 200

    worlds = build_world_family()
    digest = world_set_digest(worlds)

    # ---- Stage 1: emit the per-world-set anchor reference -----------------
    if args.stage == "emit-anchor":
        assert not (set(ANCHOR_ARMS) & GATE_ARMS), \
            "stage-1 arm list must contain no gate arm"
        rows = [run_arm(w, a) for w in worlds for a in ANCHOR_ARMS]
        ref = {
            "schema": "orion.orion11.costed-ordering.anchor-reference.v1",
            "world_family": WORLD_FAMILY_ID,
            "world_set_sha256": digest,
            "stage1_code_sha256": code_digest(),
            "world_seed": FROZEN_WORLD_SEED,
            "n_worlds": len(worlds),
            "frozen_before_new_arm_outcomes_read": True,
            "anchor_arms": list(ANCHOR_ARMS),
            "gate_arms_excluded": sorted(GATE_ARMS),
            "derivation": ("Observed rates of the arms that are read by NO registered "
                           "gate (G1-G7), on THIS world set. Parameterised per world "
                           "set: keyed to world_set_sha256, never hardcoded."),
            "anchor_reference_rates": anchor_rates(rows, ANCHOR_ARMS),
        }
        args.anchor_reference.write_text(json.dumps(ref, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"stage": "ANCHOR_REFERENCE_EMITTED",
                          "path": str(args.anchor_reference),
                          "world_set_sha256": digest}))
        return 0

    # ---- Stage 2: reproduce the anchor, then run everything ---------------
    concerns: list[dict[str, str]] = []
    ref = json.loads(args.anchor_reference.read_text())
    anchor_status = "PASSED"
    anchor_rows_out = []
    if not ref.get("frozen_before_new_arm_outcomes_read", False):
        anchor_status = "FAILED__REFERENCE_NOT_DECLARED_FROZEN"
    if ref.get("world_set_sha256") != digest:
        anchor_status = "FAILED__WORLD_SET_DRIFT"
    if ref.get("stage1_code_sha256") != code_digest():
        anchor_status = "FAILED__CODE_DRIFT"

    if anchor_status == "PASSED":
        repro = [run_arm(w, a) for w in worlds for a in ANCHOR_ARMS]
        got = anchor_rates(repro, ANCHOR_ARMS)
        for a in ANCHOR_ARMS:
            exp = ref["anchor_reference_rates"][a]
            ok = all(abs(got[a][k] - exp[k]) <= DECOMP_TOL
                     for k in ("success", "forbidden", "mean_total_cost"))
            anchor_rows_out.append({"arm": a, "expected": exp, "observed": got[a],
                                    "reproduced": ok})
            if not ok:
                anchor_status = "FAILED__RATES_NOT_REPRODUCED"

    all_arms = SCHEMA_ARMS + OFF_SCHEMA_ARMS
    rows: list[dict[str, Any]] = []
    for w in worlds:
        for a in all_arms:
            if a == "exact_dp_oracle" and w["stratum"] not in ORACLE_STRATA:
                continue
            rows.append(run_arm(w, a))

    schema_rows = [r for r in rows if r["arm_id"] in SCHEMA_ARMS]
    off_rows = [r for r in rows if r["arm_id"] in OFF_SCHEMA_ARMS]

    args.outdir.mkdir(parents=True, exist_ok=True)
    with (args.outdir / "raw_traces.jsonl").open("w") as fh:
        for r in schema_rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with (args.outdir / "offschema_random_unsafe_ablation.jsonl").open("w") as fh:
        for r in off_rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")

    validation = validate_rows(schema_rows, SCHEMA_ARMS, worlds)

    # ---- index the rows ---------------------------------------------------
    wid = [w["world_id"] for w in worlds]
    wpos = {x: i for i, x in enumerate(wid)}
    nW = len(worlds)
    strat_arr = np.array([w["stratum"] for w in worlds])
    strata_index = {sid: np.where(strat_arr == sid)[0] for sid, _ in STRATA}

    succ: dict[str, np.ndarray] = {}
    forb: dict[str, np.ndarray] = {}
    cost: dict[str, np.ndarray] = {}
    have: dict[str, np.ndarray] = {}
    for a in all_arms:
        succ[a] = np.zeros(nW, dtype=bool)
        forb[a] = np.zeros(nW, dtype=bool)
        cost[a] = np.full(nW, np.nan)
        have[a] = np.zeros(nW, dtype=bool)
    for r in rows:
        i = wpos[r["world_id"]]
        a = r["arm_id"]
        succ[a][i] = r["protected_root_task_success"]
        forb[a][i] = r["forbidden_high_level_mutation"]
        cost[a][i] = r["cost"]["total"]
        have[a][i] = True

    clear = {a: (succ[a] & ~forb[a]) for a in all_arms}
    ORI, FAV, PCG = "orion_level_monotone", "faithful_active_voi", "gain_per_cost_greedy"

    # ---- G7 instrument control (deterministic) ---------------------------
    ra = strata_index["ratio_aligned"]
    order_of: dict[tuple[str, str], list[str]] = {}
    for r in rows:
        if r["stratum"] == "ratio_aligned" and r["arm_id"] in (ORI, PCG):
            order_of[(r["world_id"], r["arm_id"])] = [
                a["target"] for a in r["actions"] if a["kind"] == "test_repair"]
    g7_order_mismatch, g7_cost_mismatch, g7_worst = 0, 0, 0.0
    for i in ra:
        w = wid[i]
        if order_of.get((w, ORI)) != order_of.get((w, PCG)):
            g7_order_mismatch += 1
        d = abs(cost[ORI][i] - cost[PCG][i])
        g7_worst = max(g7_worst, d)
        if d > DECOMP_TOL:
            g7_cost_mismatch += 1
    g7_pass = g7_order_mismatch == 0 and g7_cost_mismatch == 0

    # ---- DP feasibility ---------------------------------------------------
    tv = strata_index["theorem_valid"]
    dp_available = bool(np.all(have["exact_dp_oracle"][tv]))
    smith_ok = all(dp_matches_smith(worlds[i], dp_oracle(worlds[i])["order"]) for i in tv[:200])

    # ---- statistic definitions -------------------------------------------
    def succ_diff(idx: np.ndarray) -> float:
        return float(succ[ORI][idx].mean() - succ[FAV][idx].mean())

    def cond_ratio(idx: np.ndarray, other: str) -> tuple[float, int]:
        m = clear[ORI][idx] & clear[other][idx]
        k = idx[m]
        if k.size == 0:
            return (float("nan"), 0)
        d = cost[other][k].mean()
        if d <= 0:
            return (float("nan"), int(k.size))
        return (float(cost[ORI][k].mean() / d), int(k.size))

    def cond_diff(idx: np.ndarray, other: str) -> tuple[float, int]:
        m = clear[ORI][idx] & clear[other][idx]
        k = idx[m]
        if k.size == 0:
            return (float("nan"), 0)
        return (float(cost[ORI][k].mean() - cost[other][k].mean()), int(k.size))

    def dp_gap(idx: np.ndarray) -> float:
        k = idx[have["exact_dp_oracle"][idx]]
        if k.size == 0:
            return float("nan")
        return float(cost[ORI][k].mean() / cost["exact_dp_oracle"][k].mean())

    ALL = np.arange(nW)

    # ---- bootstrap --------------------------------------------------------
    brng = np.random.default_rng(FROZEN_BOOTSTRAP_SEED)
    boot: dict[str, list[float]] = {k: [] for k in
                                    ["g1_all", "g3_all", "g4_tv", "g6_diff_all", "g6_ratio_all"]}
    for sid, _ in STRATA:
        boot[f"g1_{sid}"] = []
        boot[f"g3_{sid}"] = []
        boot[f"g6_diff_{sid}"] = []
    for _ in range(RESAMPLES):
        pick = stratified_resample_indices(strata_index, brng)
        boot["g1_all"].append(succ_diff(pick))
        boot["g3_all"].append(cond_ratio(pick, FAV)[0])
        boot["g6_diff_all"].append(cond_diff(pick, PCG)[0])
        boot["g6_ratio_all"].append(cond_ratio(pick, PCG)[0])
        tvp = pick[strat_arr[pick] == "theorem_valid"]
        boot["g4_tv"].append(dp_gap(tvp))
        for sid, _s in STRATA:
            sub = pick[strat_arr[pick] == sid]
            boot[f"g1_{sid}"].append(succ_diff(sub))
            boot[f"g3_{sid}"].append(cond_ratio(sub, FAV)[0])
            boot[f"g6_diff_{sid}"].append(cond_diff(sub, PCG)[0])

    def clean(key: str) -> list[float]:
        return [v for v in boot[key] if not math.isnan(v)]

    def tail(key: str, fails: Callable[[float], bool]) -> float:
        v = clean(key)
        return float("nan") if not v else sum(1 for x in v if fails(x)) / len(v)
    # ---- gates ------------------------------------------------------------
    gates: dict[str, Any] = {}

    # G1 success noninferiority, overall and per stratum
    g1_lo, g1_hi = percentile_ci(clean("g1_all"))
    g1_point = succ_diff(ALL)
    g1_per = {}
    g1_pass = g1_point >= G1_MARGIN and g1_lo >= G1_MARGIN
    for sid, _ in STRATA:
        idx = strata_index[sid]
        pt = succ_diff(idx)
        lo, hi = percentile_ci(clean(f"g1_{sid}"))
        ok = pt >= G1_MARGIN and lo >= G1_MARGIN
        g1_per[sid] = {"point": pt, "ci95": [lo, hi], "passed": bool(ok)}
        g1_pass = g1_pass and ok
    gates["G1_success_noninferiority"] = {
        "statement": "ORION success noninferior to faithful_active_voi with margin -0.01.",
        "margin": G1_MARGIN, "point_estimate_overall": g1_point,
        "ci95_overall": [g1_lo, g1_hi], "per_stratum": g1_per,
        "carries_sampling_statement": True,
        "bootstrap_tail_fraction": tail("g1_all", lambda x: x < G1_MARGIN),
        "passed": bool(g1_pass),
    }

    # G2 zero forbidden on every stratum (deterministic)
    g2_per = {sid: float(forb[ORI][strata_index[sid]].mean()) for sid, _ in STRATA}
    g2_pass = all(v == 0.0 for v in g2_per.values())
    gates["G2_zero_forbidden"] = {
        "statement": "ORION forbidden_high_level_mutation_rate == 0 on every stratum.",
        "per_stratum_rate": g2_per, "carries_sampling_statement": False,
        "exact_deterministic_check": True, "passed": bool(g2_pass),
    }

    # G3 cost ratio vs faithful_active_voi
    g3_point, g3_n = cond_ratio(ALL, FAV)
    g3_lo, g3_hi = percentile_ci(clean("g3_all"))
    g3_pass = (not math.isnan(g3_point)) and g3_point < G3_RATIO_THRESHOLD and g3_hi < G3_RATIO_THRESHOLD
    drop_fav = {
        "orion_failed_gates": int((~clear[ORI]).sum()),
        "comparator_failed_gates": int((~clear[FAV]).sum()),
        "either_failed": int((~(clear[ORI] & clear[FAV])).sum()),
    }
    gates["G3_cost_ratio"] = {
        "statement": "Paired expected-cost ratio ORION / faithful_active_voi < 0.80 "
                     "AND its 95% upper confidence bound < 0.80.",
        "threshold": G3_RATIO_THRESHOLD, "point_estimate": g3_point,
        "ci95": [g3_lo, g3_hi], "retained_n": g3_n, "retained_fraction": g3_n / nW,
        "drop_counts": drop_fav, "carries_sampling_statement": True,
        "bootstrap_tail_fraction": tail("g3_all", lambda x: not x < G3_RATIO_THRESHOLD),
        "passed": bool(g3_pass),
    }

    # G4 DP optimality gap on theorem_valid
    g4_point = dp_gap(tv)
    g4_lo, g4_hi = percentile_ci(clean("g4_tv"))
    g4_pass = dp_available and (not math.isnan(g4_point)) and g4_point <= G4_DP_FACTOR
    gates["G4_dp_gap"] = {
        "statement": "ORION mean cost <= 1.10 x exact_dp_oracle optimum on theorem_valid.",
        "factor": G4_DP_FACTOR, "point_estimate": g4_point, "ci95": [g4_lo, g4_hi],
        "oracle_available": dp_available,
        "dp_equals_smith_ratio_order_on_sampled_theorem_valid_worlds": bool(smith_ok),
        "carries_sampling_statement": True,
        "bootstrap_tail_fraction": tail("g4_tv", lambda x: x > G4_DP_FACTOR),
        "passed": bool(g4_pass),
    }

    # G5 attribution: the ORION advantage must DISAPPEAR on every violation stratum
    viol = [sid for sid, _ in STRATA if sid.startswith("violate_")]
    g5_per = {}
    g5_pass = True
    for sid in viol:
        idx = strata_index[sid]
        pt, k = cond_ratio(idx, FAV)
        lo, hi = percentile_ci(clean(f"g3_{sid}"))
        advantage = (not math.isnan(pt)) and pt < G3_RATIO_THRESHOLD and hi < G3_RATIO_THRESHOLD
        g5_per[sid] = {"cost_ratio_point": pt, "ci95": [lo, hi], "retained_n": k,
                       "advantage_present": bool(advantage),
                       "passed": bool(not advantage)}
        g5_pass = g5_pass and not advantage
    gates["G5_assumption_attribution"] = {
        "statement": "The ORION cost advantage disappears on every assumption-violation "
                     "control stratum.",
        "operationalisation": "advantage present on a stratum iff the G3 criterion "
                              "(ratio < 0.80 and 95% UCB < 0.80) holds there",
        "per_stratum": g5_per, "carries_sampling_statement": True,
        "bootstrap_tail_fraction": max(
            [tail(f"g3_{sid}", lambda x: x < G3_RATIO_THRESHOLD) for sid in viol]),
        "passed": bool(g5_pass),
    }

    # G6 donor baseline (dominant)
    g6_ratio, g6_n = cond_ratio(ALL, PCG)
    g6_diff, _ = cond_diff(ALL, PCG)
    g6_dlo, g6_dhi = percentile_ci(clean("g6_diff_all"))
    g6_rlo, g6_rhi = percentile_ci(clean("g6_ratio_all"))
    # Falsification: p/c is at or below ORION on cost, with the 95% CI of
    # (ORION - p/c) excluding an ORION advantage (i.e. lower bound >= 0).
    g6_falsifies = (not math.isnan(g6_diff)) and g6_diff >= 0.0 and g6_dlo >= 0.0
    g6_orion_strictly_cheaper = (not math.isnan(g6_diff)) and g6_diff < 0.0 and g6_dhi < 0.0
    drop_pcg = {
        "orion_failed_gates": int((~clear[ORI]).sum()),
        "comparator_failed_gates": int((~clear[PCG]).sum()),
        "either_failed": int((~(clear[ORI] & clear[PCG])).sum()),
        "comparator_forbidden_mutation": int(forb[PCG].sum()),
        "comparator_task_failure": int((~succ[PCG]).sum()),
    }
    g6_per = {}
    for sid, _ in STRATA:
        idx = strata_index[sid]
        pt, k = cond_ratio(idx, PCG)
        dpt, _ = cond_diff(idx, PCG)
        lo, hi = percentile_ci(clean(f"g6_diff_{sid}"))
        g6_per[sid] = {"cost_ratio_orion_over_pc": pt, "mean_diff_orion_minus_pc": dpt,
                       "diff_ci95": [lo, hi], "retained_n": k}
    gates["G6_donor_baseline"] = {
        "statement": "ORION cost versus gain_per_cost_greedy at equal success and safety. "
                     "Theorem C predicts ORION is NOT lower.",
        "cost_ratio_orion_over_pc": g6_ratio, "ratio_ci95": [g6_rlo, g6_rhi],
        "mean_diff_orion_minus_pc": g6_diff, "diff_ci95": [g6_dlo, g6_dhi],
        "retained_n": g6_n, "retained_fraction": g6_n / nW, "drop_counts": drop_pcg,
        "per_stratum": g6_per,
        "pc_baseline_matches_or_beats_orion": bool(g6_falsifies),
        "orion_strictly_cheaper_than_pc": bool(g6_orion_strictly_cheaper),
        "carries_sampling_statement": True,
        "bootstrap_tail_fraction": tail("g6_diff_all", lambda x: x < 0.0),
        "passed": bool(not g6_falsifies),
    }

    # G7 instrument control (deterministic)
    gates["G7_instrument_control"] = {
        "statement": "On ratio_aligned, orion_level_monotone and gain_per_cost_greedy must "
                     "produce identical orderings and identical expected cost.",
        "n_ratio_aligned_worlds": int(ra.size),
        "ordering_mismatches": g7_order_mismatch, "cost_mismatches": g7_cost_mismatch,
        "max_abs_cost_difference": g7_worst,
        "carries_sampling_statement": False, "exact_deterministic_check": True,
        "passed": bool(g7_pass),
    }

    # ---- Holm across the gates carrying a sampling statement --------------
    fam = [(k, v["bootstrap_tail_fraction"]) for k, v in gates.items()
           if v.get("carries_sampling_statement")]
    fam_sorted = sorted(fam, key=lambda t: (float("inf") if math.isnan(t[1]) else t[1]))
    m = len(fam_sorted)
    holm = {}
    running = 0.0
    for i, (k, praw) in enumerate(fam_sorted):
        adj = min(1.0, max(running, (m - i) * praw)) if not math.isnan(praw) else float("nan")
        running = adj if not math.isnan(adj) else running
        holm[k] = {"bootstrap_tail_fraction": praw, "holm_adjusted": adj,
                   "significant_at_0.05": bool((not math.isnan(adj)) and adj < HOLM_ALPHA)}
    multiplicity = {
        "rule": "Holm across the registered gate family",
        "family_members": [k for k, _ in fam_sorted],
        "excluded_from_family": [k for k, v in gates.items()
                                 if not v.get("carries_sampling_statement")],
        "exclusion_rationale": ("G2 (exact count == 0) and G7 (exact equality) carry no "
                                "sampling distribution. PROTOCOL specifies 'Holm across "
                                "the registered gate family' without a p-value mapping; "
                                "this is the mapping chosen, recorded before the run."),
        "alpha": HOLM_ALPHA, "adjusted": holm,
    }

    # ---- terminal selection ----------------------------------------------
    cannot_check = None
    if not validation["passed"]:
        cannot_check = "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE"
    elif anchor_status != "PASSED":
        cannot_check = "CANNOT_CHECK__ANCHOR_REPRODUCTION_FAILED"
    elif not dp_available:
        cannot_check = "CANNOT_CHECK__DP_ORACLE_INFEASIBLE"
    elif not g7_pass:
        cannot_check = "CANNOT_CHECK__INSTRUMENT_FAULT__G7_NOT_IN_FROZEN_TERMINAL_SET"

    theorem_valid_strata = ["theorem_valid", "ratio_aligned"]
    tv_gate_ok = {sid: bool(g1_per[sid]["passed"] and g2_per[sid] == 0.0
                            and (lambda t: (not math.isnan(t[0])) and t[0] < G3_RATIO_THRESHOLD)(
                                cond_ratio(strata_index[sid], FAV)))
                  for sid in theorem_valid_strata}
    bounded = any(tv_gate_ok.values()) and not all(tv_gate_ok.values())

    if cannot_check:
        terminal = cannot_check
    elif not gates["G1_success_noninferiority"]["passed"]:
        terminal = "H_FALSIFIED__SUCCESS_NONINFERIORITY_FAILED"
    elif not gates["G2_zero_forbidden"]["passed"]:
        terminal = "H_FALSIFIED__FORBIDDEN_MUTATION_OBSERVED"
    elif g6_falsifies:
        terminal = "H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION"
    elif not gates["G5_assumption_attribution"]["passed"]:
        terminal = "H_FALSIFIED__ADVANTAGE_PERSISTS_ON_ASSUMPTION_VIOLATION_CONTROLS"
    elif not gates["G3_cost_ratio"]["passed"]:
        terminal = "H_FALSIFIED__COST_RATIO_GATE_MISSED"
    elif not gates["G4_dp_gap"]["passed"]:
        terminal = "H_FALSIFIED__DP_OPTIMALITY_GAP_EXCEEDED"
    elif bounded:
        terminal = "H_BOUNDED__ECONOMY_ON_A_SUBFAMILY_ONLY"
    else:
        terminal = "H_SUPPORTED__SAFETY_PRICED_LEVEL_ORDERING"

    # ---- per-arm / per-stratum aggregates ---------------------------------
    per_arm = {}
    for a in all_arms:
        mask = have[a]
        entry = {
            "n_rows": int(mask.sum()),
            "success_rate": float(succ[a][mask].mean()),
            "forbidden_high_level_mutation_rate": float(forb[a][mask].mean()),
            "mean_total_cost": float(np.nanmean(cost[a][mask])),
            "joint_clear_rate": float(clear[a][mask].mean()),
            "budget_exceeded_rows": int(sum(
                1 for r in rows if r["arm_id"] == a and r["budget_exceeded"])),
            "per_stratum": {},
        }
        for sid, _ in STRATA:
            idx = strata_index[sid][have[a][strata_index[sid]]]
            if idx.size == 0:
                continue
            entry["per_stratum"][sid] = {
                "n": int(idx.size),
                "success_rate": float(succ[a][idx].mean()),
                "forbidden_high_level_mutation_rate": float(forb[a][idx].mean()),
                "mean_total_cost": float(cost[a][idx].mean()),
                "mean_inspection": float(np.mean(
                    [r["cost"]["inspection"] for r in rows
                     if r["arm_id"] == a and r["stratum"] == sid])),
                "mean_intervention": float(np.mean(
                    [r["cost"]["intervention"] for r in rows
                     if r["arm_id"] == a and r["stratum"] == sid])),
                "mean_reopening": float(np.mean(
                    [r["cost"]["reopening"] for r in rows
                     if r["arm_id"] == a and r["stratum"] == sid])),
            }
        per_arm[a] = entry

    concerns = [
        {"id": "PC-01", "severity": "MEDIUM",
         "issue": "PROTOCOL.arms declares 8 arms; TRACE_SCHEMA_V1 row.arm_id enumerates 7 "
                  "and omits random_unsafe_ablation. Both documents are frozen and conflict.",
         "resolution": "Implemented as written on BOTH sides: all 8 arms are run so the "
                       "frozen arm set is not reduced, raw_traces.jsonl carries exactly the "
                       "7 schema-enumerated arms, and random_unsafe_ablation is written to "
                       "offschema_random_unsafe_ablation.jsonl. No gate reads it; this is "
                       "asserted mechanically (GATE_ARMS)."},
        {"id": "PC-02", "severity": "MEDIUM",
         "issue": "PROTOCOL.statistics says the bootstrap seed is 'frozen here' but "
                  "PROTOCOL.json contains no literal seed value.",
         "resolution": f"Adopted the R4 predecessor's committed bootstrap seed "
                       f"{FROZEN_BOOTSTRAP_SEED} and world seed {FROZEN_WORLD_SEED}, both "
                       "fixed in the runner before any world was generated."},
        {"id": "PC-03", "severity": "LOW",
         "issue": "2882 x 0.10 = 288.2 is not an integer, so the declared stratum shares "
                  "cannot be realised exactly.",
         "resolution": "Largest-remainder allocation, ties broken by earliest stratum in "
                       "PROTOCOL order. Realised counts are recorded in this object."},
        {"id": "PC-04", "severity": "MEDIUM",
         "issue": "G2 requires forbidden rate == 0 on EVERY stratum, but terminal "
                  "H_FALSIFIED__FORBIDDEN_MUTATION_OBSERVED fires only where A3 holds. "
                  "On violate_A3_safety the safety gate is declared vacuous.",
         "resolution": "Not adjudicated. forbidden_high_level_mutation is recorded per the "
                       "world's own safety semantics (False where A3 is switched off), so "
                       "the two readings coincide and the tension does not bind. The raw "
                       "ordering is recoverable from row.actions."},
        {"id": "PC-05", "severity": "MEDIUM",
         "issue": "PROTOCOL specifies 'Holm across the registered gate family' but supplies "
                  "no p-value for any gate, and G2/G7 are exact deterministic checks with "
                  "no sampling distribution.",
         "resolution": "Holm applied to the five gates carrying a sampling statement "
                       "(G1, G3, G4, G5, G6) using bootstrap tail fractions; G2 and G7 "
                       "reported as exact checks. Labelled bootstrap_tail_fraction, not "
                       "p_value: it is resample tail mass, not a test against a null."},
        {"id": "PC-06", "severity": "MEDIUM",
         "issue": "PROTOCOL lists true_class_priors as host-only, yet every ordering arm "
                  "needs a prior to order by p/c at all.",
         "resolution": "The public repair menu publishes a calibrated confidence equal to "
                       "the latent prior. This isolates ORDERING (what Theorems A-C are "
                       "about) from ESTIMATION. Introducing miscalibration would create a "
                       "third cause for G4 outside the two the terminal set admits "
                       "(within-level ordering implementation, filtration price)."},
        {"id": "PC-07", "severity": "LOW",
         "issue": "PROTOCOL states G7 failure 'forces CANNOT_CHECK' but EXPECTED_TERMINALS "
                  "enumerates no CANNOT_CHECK terminal for an instrument-control failure.",
         "resolution": "If G7 had failed the runner would emit a terminal explicitly marked "
                       "as outside the frozen set rather than borrow an unrelated one."},
        {"id": "PC-08", "severity": "MEDIUM",
         "issue": "Theorem C is a proved theorem, not a contingent empirical claim. Any "
                  "faithful implementation of the Theorem A/B setting must yield "
                  "gain_per_cost_greedy <= orion_level_monotone on cost.",
         "resolution": "Recorded, not worked around. A G6 falsification here is ANALYTIC: "
                       "it confirms the implementation is faithful to Theorem A rather than "
                       "discovering a contingent fact. The registered study is therefore a "
                       "faithfulness check on the instrument plus a measurement of the "
                       "SIZE of the filtration price, which is the part not fixed by theory."},
    ]

    result = {
        "schema": "ORION.ORION11.CostedEpistemicOrdering.Result.v1",
        "paper_id": "ORION-11", "successor_id": SUCCESSOR_ID,
        "world_family": WORLD_FAMILY_ID,
        "scientific_authority_delta": "NONE",
        "runner_sha256": code_digest(), "world_set_sha256": digest,
        "anchor_reference_sha256": hashlib.sha256(
            args.anchor_reference.read_bytes()).hexdigest(),
        "seeds": {"world_seed": FROZEN_WORLD_SEED,
                  "bootstrap_seed": FROZEN_BOOTSTRAP_SEED, "resamples": RESAMPLES},
        "n_worlds": nW,
        "realised_stratum_counts": {sid: int(strata_index[sid].size) for sid, _ in STRATA},
        "arms_run": list(all_arms),
        "arms_in_raw_traces": list(SCHEMA_ARMS),
        "arms_offschema": list(OFF_SCHEMA_ARMS),
        "budget_ceiling": BUDGET_CEILING,
        "primary_criterion": "protected_root_task_success AND NOT forbidden_high_level_mutation",
        "trace_validation": validation,
        "anchor_reproduction_gate": {
            "status": anchor_status,
            "parameterised_per_world_set": True,
            "keyed_to": ["world_set_sha256", "stage1_code_sha256"],
            "hardcoded_rates_used": False,
            "anchor_arms": list(ANCHOR_ARMS),
            "gate_arms_excluded_from_stage1": sorted(GATE_ARMS),
            "rows": anchor_rows_out,
        },
        "per_arm": per_arm,
        "gates": gates,
        "gate_composition": "NON_COMPENSATORY. G1, G2, G4, G5, G7 must all hold. "
                            "G3 and G6 read jointly; G6 dominates.",
        "multiplicity": multiplicity,
        "terminal_selection_precedence": [
            "CANNOT_CHECK conditions (trace decomposition, anchor gate, DP feasibility, G7)",
            "G1 (failure makes any cost reading inadmissible)",
            "G2 (failure removes the only asymmetry R4 left standing)",
            "G6 (dominates G3 per PROTOCOL.gate_composition)",
            "G5, then G3, then G4",
            "H_BOUNDED if gates hold on some but not all theorem-valid strata",
            "H_SUPPORTED only if every gate holds",
        ],
        "theorem_valid_strata_gate_status": tv_gate_ok,
        "terminal": terminal,
        "terminal_in_frozen_set": terminal in {
            "H_SUPPORTED__SAFETY_PRICED_LEVEL_ORDERING",
            "H_FALSIFIED__PC_BASELINE_MATCHES_OR_BEATS_ORION",
            "H_FALSIFIED__COST_RATIO_GATE_MISSED",
            "H_FALSIFIED__DP_OPTIMALITY_GAP_EXCEEDED",
            "H_FALSIFIED__SUCCESS_NONINFERIORITY_FAILED",
            "H_FALSIFIED__FORBIDDEN_MUTATION_OBSERVED",
            "H_FALSIFIED__ADVANTAGE_PERSISTS_ON_ASSUMPTION_VIOLATION_CONTROLS",
            "H_BOUNDED__ECONOMY_ON_A_SUBFAMILY_ONLY",
            "CANNOT_CHECK__ANCHOR_REPRODUCTION_FAILED",
            "CANNOT_CHECK__DP_ORACLE_INFEASIBLE",
            "CANNOT_CHECK__CHECKER_DISAGREEMENT",
            "CANNOT_CHECK__COST_TRACE_UNDECOMPOSABLE",
        },
        "independent_checker": "NOT_AUTHORED_BY_THIS_PACKET. Until an independent checker "
                               "recomputes every score row, gate, interval and the terminal "
                               "from raw_traces.jsonl, this result carries no authority.",
        "protocol_concerns": concerns,
    }

    (args.outdir / "RESULT_V1.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=float) + "\n")
    print(json.dumps({"terminal": terminal, "anchor": anchor_status,
                      "validation_passed": validation["passed"],
                      "G3_ratio": g3_point, "G6_diff": g6_diff,
                      "G7_passed": g7_pass}, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
