"""ORION-Q N4-B: stale failure receipts on the interface graph — scoped reopening.

Frozen protocol:
development/orion-q-nlane-closure/N4_B_STALE_RECEIPT_REOPENING_PROTOCOL.md
Exact synthetic, deterministic, no authority beyond the receipt's claim boundary.

Run:
    python research/extensions/orion-q/nlanes/n4_b_stale_receipt_reopening.py
"""

from __future__ import annotations

import itertools
import json
import os
import random
from statistics import fmean

SEED = 20260821
EPISODES_PER_REGIME = 200
ROUNDS = 6
WIDTH = 3
LAYERS = 3
P_RECEIPT = 0.45
P_RECOVER = 0.85
P_BASE_FEASIBLE = 0.95
REWARD = 20.0
FAIL_PENALTY = 8.0
SCOPES = ((("REP",), 0.4), (("ACCESS",), 0.4), (("REP", "ACCESS"), 0.2))
REGIMES = {
    "STALE_MATTERS": {"REP": 0.30, "ACCESS": 0.20, "NOISE": 0.50},
    "REOPEN_WASTEFUL": {"REP": 0.02, "ACCESS": 0.02, "NOISE": 0.60},
}
ARMS = (
    "ORACLE_AVAILABILITY",
    "NEVER_REOPEN",
    "ALWAYS_REOPEN",
    "UNSCOPED_CHANGE_REOPEN",
    "ORION_SCOPED_REOPEN",
)


def draw_scope(rng: random.Random):
    x = rng.random()
    acc = 0.0
    for scope, p in SCOPES:
        acc += p
        if x < acc:
            return scope
    return SCOPES[-1][0]


def generate_episode(regime: str, rng: random.Random) -> dict:
    layer_nodes = [[(layer, w) for w in range(WIDTH)] for layer in range(LAYERS)]
    edges = {}

    def add_edge(u, v):
        has_receipt = rng.random() < P_RECEIPT
        edges[(u, v)] = {
            "cost": rng.uniform(1.0, 5.0),
            "receipt_scope": draw_scope(rng) if has_receipt else None,
            "recovered_feasible": rng.random() < P_RECOVER,
            "base_feasible": rng.random() < P_BASE_FEASIBLE,
        }

    for node in layer_nodes[0]:
        add_edge("s", node)
    for layer in range(LAYERS - 1):
        for u in layer_nodes[layer]:
            for v in layer_nodes[layer + 1]:
                add_edge(u, v)
    for node in layer_nodes[-1]:
        add_edge(node, "t")

    paths = []
    for combo in itertools.product(*layer_nodes):
        node_seq = ["s", *combo, "t"]
        paths.append(tuple(zip(node_seq[:-1], node_seq[1:])))

    flips = REGIMES[regime]
    rounds = []
    changed = {"REP": False, "ACCESS": False, "NOISE": False}
    for _ in range(ROUNDS):
        for coord in ("REP", "ACCESS", "NOISE"):
            if rng.random() < flips[coord]:
                changed[coord] = True
        rounds.append(dict(changed))
    return {"edges": edges, "paths": paths, "rounds": rounds}


def true_feasible(edge: dict, changed: dict) -> bool:
    scope = edge["receipt_scope"]
    if scope is None:
        return edge["base_feasible"]
    if any(changed[coord] for coord in scope):
        return edge["recovered_feasible"]
    return False


def believes_available(arm: str, edge: dict, changed: dict) -> bool:
    scope = edge["receipt_scope"]
    if arm == "ORACLE_AVAILABILITY":
        return true_feasible(edge, changed)
    if scope is None:
        return True
    if arm == "NEVER_REOPEN":
        return False
    if arm == "ALWAYS_REOPEN":
        return True
    if arm == "UNSCOPED_CHANGE_REOPEN":
        return changed["REP"] or changed["ACCESS"] or changed["NOISE"]
    if arm == "ORION_SCOPED_REOPEN":
        return any(changed[coord] for coord in scope)
    raise ValueError(arm)


def run_arm(arm: str, episode: dict) -> dict:
    edges = episode["edges"]
    utilities = []
    failures = 0
    abstains = 0
    attempts = 0
    for changed in episode["rounds"]:
        candidates = [
            p
            for p in episode["paths"]
            if all(believes_available(arm, edges[e], changed) for e in p)
        ]
        if not candidates:
            utilities.append(0.0)
            abstains += 1
            continue
        path = min(candidates, key=lambda p: sum(edges[e]["cost"] for e in p))
        cost = sum(edges[e]["cost"] for e in path)
        attempts += 1
        if all(true_feasible(edges[e], changed) for e in path):
            utilities.append(REWARD - cost)
        else:
            utilities.append(-cost - FAIL_PENALTY)
            failures += 1
    return {
        "mean_round_utility": fmean(utilities),
        "failure_attempts": failures,
        "abstains": abstains,
        "attempts": attempts,
    }


def summarize(rows: list[dict]) -> dict:
    total_attempts = sum(r["attempts"] for r in rows)
    total_rounds = len(rows) * ROUNDS
    return {
        "mean_round_utility": fmean(r["mean_round_utility"] for r in rows),
        "failure_attempt_rate": (
            sum(r["failure_attempts"] for r in rows) / total_attempts
            if total_attempts
            else 0.0
        ),
        "abstain_rate": sum(r["abstains"] for r in rows) / total_rounds,
    }


def main() -> None:
    rng = random.Random(SEED)
    episodes = {
        regime: [generate_episode(regime, rng) for _ in range(EPISODES_PER_REGIME)]
        for regime in REGIMES
    }

    per_regime = {}
    pooled_rows = {arm: [] for arm in ARMS}
    for regime, eps in episodes.items():
        per_regime[regime] = {}
        for arm in ARMS:
            rows = [run_arm(arm, ep) for ep in eps]
            pooled_rows[arm].extend(rows)
            per_regime[regime][arm] = summarize(rows)
    pooled = {arm: summarize(pooled_rows[arm]) for arm in ARMS}
    oracle_mu = pooled["ORACLE_AVAILABILITY"]["mean_round_utility"]
    for arm in ARMS:
        pooled[arm]["mean_regret_vs_oracle"] = (
            oracle_mu - pooled[arm]["mean_round_utility"]
        )

    def mu(scope: dict, arm: str) -> float:
        return scope[arm]["mean_round_utility"]

    g1 = all(
        mu(per_regime[reg], "ORACLE_AVAILABILITY") >= mu(per_regime[reg], a)
        for reg in REGIMES
        for a in ARMS
    ) and all(mu(pooled, "ORACLE_AVAILABILITY") >= mu(pooled, a) for a in ARMS)
    g2 = all(
        mu(pooled, "ORION_SCOPED_REOPEN") > mu(pooled, a)
        for a in ("NEVER_REOPEN", "ALWAYS_REOPEN", "UNSCOPED_CHANGE_REOPEN")
    )
    g3 = mu(per_regime["REOPEN_WASTEFUL"], "ALWAYS_REOPEN") < mu(
        per_regime["REOPEN_WASTEFUL"], "NEVER_REOPEN"
    )
    g4 = all(
        mu(per_regime[reg], "ORION_SCOPED_REOPEN")
        >= max(
            mu(per_regime[reg], "NEVER_REOPEN"),
            mu(per_regime[reg], "ALWAYS_REOPEN"),
        )
        - 0.25
        for reg in REGIMES
    )
    gates = {
        "G1_oracle_upper_bound": g1,
        "G2_pooled_scoped_advantage": g2,
        "G3_wasteful_regime_punishes_always_reopen": g3,
        "G4_per_regime_no_giveback": g4,
    }
    if not g1 or not g3:
        terminal = "N4_B_WORLD_INVALID"
    elif g2 and g4:
        terminal = "N4_B_SCOPED_REOPENING_SUPPORTED__EXACT_SYNTHETIC"
    else:
        terminal = "N4_B_SCOPED_REOPENING_NO_ADVANTAGE"

    result = {
        "schema": "ORIONQ.N4B.StaleReceiptReopening.v1",
        "issue": 677,
        "family": "2_stale_receipt_reopening",
        "protocol": (
            "development/orion-q-nlane-closure/"
            "N4_B_STALE_RECEIPT_REOPENING_PROTOCOL.md"
        ),
        "seed": SEED,
        "episodes_per_regime": EPISODES_PER_REGIME,
        "rounds_per_episode": ROUNDS,
        "world": {
            "layers": LAYERS,
            "width": WIDTH,
            "p_receipt": P_RECEIPT,
            "p_recover": P_RECOVER,
            "p_base_feasible": P_BASE_FEASIBLE,
            "regimes": REGIMES,
            "reward": REWARD,
            "fail_penalty": FAIL_PENALTY,
            "scope_limit": "initial receipts only; no intra-episode receipt accrual",
        },
        "per_regime": per_regime,
        "pooled": pooled,
        "gates": gates,
        "terminal": terminal,
        "interpretation": {
            "authority": (
                "exact-synthetic-bounded; no real-quantum, no P10, no novelty "
                "claims; initial receipts only is a recorded scope limit"
            ),
            "claim_boundary": (
                "Applies only to the frozen two-regime receipt world; the "
                "scoped-reopening advantage is over the registered "
                "never/always/unscoped controls on this construction, not a "
                "general interface-graph theorem."
            ),
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print(
        "ORIONQ_N4_B_STALE_RECEIPT="
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "N4_B_STALE_RECEIPT_REOPENING_RESULTS.json",
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
