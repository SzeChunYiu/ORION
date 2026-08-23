"""ORION-Q N1-C fresh re-execution: partial applicability + costly verification.

Frozen protocol: development/orion-q-nlane-closure/N1_C_PROTOCOL.md (issue #674, family N1-C).
Re-executes the registered design of issue comment 5355071291 (never committed). Deterministic
exact-synthetic diagnostic; no P10, novelty, or real-quantum authority.

Run:
    python research/extensions/orion-q/nlanes/n1c_costly_verification_voi.py
"""

from __future__ import annotations

import json
import os

import numpy as np

SCHEMA = "ORIONQ.N1C_CostlyVerificationVOI.v1"
AUTHORITY = "N1C_DIAGNOSTIC__NO_P10_AUTHORITY__NO_NOVELTY_AUTHORITY__EXACT_SYNTHETIC_ONLY"

SEED = 20260821
BOOT_SEED = 20260822
N_TRAIN = 5_000
N_EVAL = 20_000
N_CAND = 40
BUDGET = 6
N_BOOT = 2_000

COST_VALS = np.array([1, 2, 3])
COST_P = np.array([0.5, 0.3, 0.2])
Q_P = np.array([0.5, 0.3, 0.2])                 # LOW / MED / HIGH prevalence
Q_BASE = np.array([0.03, 0.15, 0.50])
REC_P_BY_COST = np.array([np.nan, 0.6, 0.4, 0.25])  # index by cost value
STALE_GIVEN_REC = 0.55
CUR_MULT = 0.02
STALE_MULT = 2.4
STALE_CAP = 0.92

POLICIES = ("CHEAPEST_FIRST", "PERMANENT_PRUNE", "LEARNED_UNSCOPED", "LEARNED_TYPED_SCOPED",
            "IDEAL_VOI_PARENT")


def generate(rng: np.random.Generator, n: int):
    cost = rng.choice(COST_VALS, size=(n, N_CAND), p=COST_P)
    q = rng.choice(3, size=(n, N_CAND), p=Q_P)
    record = rng.random((n, N_CAND)) < REC_P_BY_COST[cost]
    stale = record & (rng.random((n, N_CAND)) < STALE_GIVEN_REC)
    p = Q_BASE[q].copy()
    p = np.where(record & ~stale, p * CUR_MULT, p)
    p = np.where(stale, np.minimum(STALE_CAP, p * STALE_MULT), p)
    applicable = rng.random((n, N_CAND)) < p
    return cost, q, record, stale, p, applicable


def cell_means(q, record, stale, applicable, typed: bool) -> dict:
    est = {}
    for qq in range(3):
        if typed:
            masks = {0: (q == qq) & ~record,
                     1: (q == qq) & record & ~stale,
                     2: (q == qq) & stale}
        else:
            masks = {0: (q == qq) & ~record, 1: (q == qq) & record}
        for key, m in masks.items():
            est[(qq, key)] = float(applicable[m].mean()) if int(m.sum()) > 30 else 0.0
    return est


def play(scores, cost, applicable, record, stale):
    """Verify candidates in descending score order under the cost budget."""
    n = cost.shape[0]
    solved = np.zeros(n, bool)
    spent = np.zeros(n)
    nver = np.zeros(n)
    fesc = np.zeros(n)
    unknown = np.full(n, float(N_CAND))
    for i in range(n):
        order = np.argsort(-scores[i], kind="stable")
        b = BUDGET
        for j in order:
            if not np.isfinite(scores[i][j]):
                continue  # policy-refused candidate (PERMANENT_PRUNE)
            c = cost[i, j]
            if c > b:
                continue
            b -= c
            spent[i] += c
            nver[i] += 1
            unknown[i] -= 1
            if record[i, j] and not stale[i, j]:
                fesc[i] += 1
            if applicable[i, j]:
                solved[i] = True
                break
    return solved, spent, nver, fesc, unknown


def boot_ci(deltas: np.ndarray, rng: np.random.Generator) -> list[float]:
    n = len(deltas)
    idx = rng.integers(0, n, size=(N_BOOT, n))
    means = deltas[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def main() -> None:
    rng = np.random.default_rng(SEED)
    tq_cost, tq, trec, tst, _tp, tapp = generate(rng, N_TRAIN)
    del tq_cost
    est_u = cell_means(tq, trec, tst, tapp, typed=False)
    est_t = cell_means(tq, trec, tst, tapp, typed=True)

    cost, q, record, stale, p_true, applicable = generate(rng, N_EVAL)
    assert int(cost.sum(axis=1).min()) > BUDGET  # G2: full verification unaffordable everywhere

    tiebreak = np.tile(np.arange(N_CAND) * 1e-9, (N_EVAL, 1))
    scores = {}
    scores["CHEAPEST_FIRST"] = -cost.astype(float) - tiebreak
    scores["PERMANENT_PRUNE"] = np.where(record, -np.inf, scores["CHEAPEST_FIRST"])
    su = np.empty((N_EVAL, N_CAND))
    stt = np.empty((N_EVAL, N_CAND))
    for qq in range(3):
        for hr in range(2):
            su[(q == qq) & (record == bool(hr))] = est_u[(qq, hr)]
        stt[(q == qq) & ~record] = est_t[(qq, 0)]
        stt[(q == qq) & record & ~stale] = est_t[(qq, 1)]
        stt[(q == qq) & stale] = est_t[(qq, 2)]
    scores["LEARNED_UNSCOPED"] = su / cost - tiebreak
    scores["LEARNED_TYPED_SCOPED"] = stt / cost - tiebreak
    scores["IDEAL_VOI_PARENT"] = p_true / cost - tiebreak

    arms = {}
    played = {}
    for name in POLICIES:
        solved, spent, nver, fesc, unknown = play(scores[name], cost, applicable, record, stale)
        played[name] = solved
        arms[name] = {
            "solve_rate": float(solved.mean()),
            "mean_verifier_cost": float(spent.mean()),
            "mean_verifications": float(nver.mean()),
            "false_escalation_rate": float(fesc.mean()),
            "mean_unknown_remaining": float(unknown.mean()),
        }
    arms["PERMANENT_PRUNE"]["implicit_unverified_refutations_per_episode"] = float(record.sum(axis=1).mean())

    brng = np.random.default_rng(BOOT_SEED)
    d_tu = played["LEARNED_TYPED_SCOPED"].astype(float) - played["LEARNED_UNSCOPED"].astype(float)
    d_tv = played["LEARNED_TYPED_SCOPED"].astype(float) - played["IDEAL_VOI_PARENT"].astype(float)
    ci_tu = boot_ci(d_tu, brng)
    ci_tv = boot_ci(d_tv, brng)

    cheapest = arms["CHEAPEST_FIRST"]["solve_rate"]
    prune = arms["PERMANENT_PRUNE"]["solve_rate"]
    gates = {
        "G1_WORLD_NONTRIVIAL": bool(0.30 <= cheapest <= 0.85),
        "G2_BUDGET_BINDING": True,  # asserted above: min total candidate cost 40 > budget 6
        "G3_PRUNE_NO_GAIN": bool(prune <= cheapest + 0.01),
        "G4_TYPED_OVER_UNSCOPED": bool(float(d_tu.mean()) > 0 and ci_tu[0] > 0),
        "G5_VOI_PARENT_MATCH": bool((ci_tv[0] <= 0 <= ci_tv[1]) or abs(float(d_tv.mean())) <= 0.01),
    }
    if not (gates["G1_WORLD_NONTRIVIAL"] and gates["G2_BUDGET_BINDING"]):
        terminal = "N1C_WORLD_INVALID"
    elif gates["G4_TYPED_OVER_UNSCOPED"] and gates["G5_VOI_PARENT_MATCH"]:
        terminal = "N1C_TYPED_FAILURE_STATE_VALUE__VOI_POLICY_PARENT_SUFFICIENT"
    elif gates["G4_TYPED_OVER_UNSCOPED"] and ci_tv[0] > 0.005:
        terminal = "N1C_VERIFICATION_ALLOCATION_VALUE"
    elif gates["G4_TYPED_OVER_UNSCOPED"]:
        terminal = "N1C_TYPED_FAILURE_STATE_VALUE__VOI_POLICY_PARENT_SUFFICIENT"
    else:
        terminal = "N1C_VOI_PARENT_SUFFICIENT"

    result = {
        "schema": SCHEMA,
        "issue": 674,
        "family": "N1-C",
        "reexecution_of": "issue-674 comment 5355071291 (original run never committed)",
        "protocol": "development/orion-q-nlane-closure/N1_C_PROTOCOL.md",
        "date": "2026-08-21",
        "seed": SEED,
        "bootstrap_seed": BOOT_SEED,
        "world": {
            "eval_episodes": N_EVAL,
            "train_episodes": N_TRAIN,
            "candidates_per_episode": N_CAND,
            "verifier_cost_budget": BUDGET,
            "unknown_preserved": "unverified candidates stay UNKNOWN; counts reported per arm",
        },
        "arms": arms,
        "paired_deltas": {
            "typed_minus_unscoped_solve": float(d_tu.mean()),
            "typed_minus_unscoped_boot95": ci_tu,
            "typed_minus_voi_solve": float(d_tv.mean()),
            "typed_minus_voi_boot95": ci_tv,
        },
        "gates": gates,
        "terminal": terminal,
        "authority": AUTHORITY,
        "claim_boundary": (
            "Exact-synthetic diagnostic only. Any positive is for typed scoped failure STATE as "
            "decision information under a binding verifier budget; the allocation POLICY is closed "
            "by the donor-complete value-of-information parent given the same typed facts. No P10, "
            "novelty, or real-quantum authority."
        ),
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N1_C_COSTLY_VERIFICATION_RESULTS.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("ORIONQ_N1C_COSTLY_VERIFICATION=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
