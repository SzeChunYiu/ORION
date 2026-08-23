"""ORION-Q N4-A: UNKNOWN interface feasibility + value-of-information probing.

Frozen protocol: development/orion-q-nlane-closure/N4_A_UNKNOWN_VOI_PROTOCOL.md
Exact synthetic, deterministic, no authority beyond the receipt's claim boundary.

Run:
    python research/extensions/orion-q/nlanes/n4_a_unknown_voi.py
"""

from __future__ import annotations

import itertools
import json
import os
import random
from statistics import fmean

SEED = 20260821
EPISODES = 300
WIDTH = 3
LAYERS = 4
P_KNOWN = 0.55
P_FEAS = {"T0": 0.90, "T1": 0.50, "T2": 0.15}
TYPES = ("T0", "T1", "T2")
PROBE_COST = 0.4
REWARD = 20.0
FAIL_PENALTY = 8.0
ARMS = (
    "FULL_ORACLE",
    "GREEDY_KNOWN_GRAPH",
    "OPTIMIST_COMMIT",
    "PURE_VOI_UNIFORM",
    "ORION_TYPED_VOI",
    "LLM_PROXY_HEURISTIC",
)


def generate_world(rng: random.Random) -> dict:
    """Layered DAG s -> L1..L4 (width 3) -> t with typed feasibility."""
    layer_nodes = [[(layer, w) for w in range(WIDTH)] for layer in range(LAYERS)]
    edges = {}

    def add_edge(u, v):
        etype = TYPES[rng.randrange(3)]
        edges[(u, v)] = {
            "cost": rng.uniform(1.0, 5.0),
            "type": etype,
            "feasible": rng.random() < P_FEAS[etype],
            "known": rng.random() < P_KNOWN,
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
    return {"edges": edges, "paths": paths}


def path_cost(world, path):
    return sum(world["edges"][e]["cost"] for e in path)


def path_eu(world, path, revealed, prior_fn):
    """Expected utility under beliefs: known + revealed facts + priors."""
    prob = 1.0
    for e in path:
        edge = world["edges"][e]
        if edge["known"]:
            fact = edge["feasible"]
        elif e in revealed:
            fact = revealed[e]
        else:
            prob *= prior_fn(edge)
            continue
        if not fact:
            # Known-infeasible edge: committing this path certainly fails.
            return -path_cost(world, path) - FAIL_PENALTY
        # Known/revealed feasible edge contributes probability 1.0.
    return prob * REWARD - path_cost(world, path) - (1.0 - prob) * FAIL_PENALTY


def best_value(world, revealed, prior_fn):
    """max(0, best path EU); returns (value, best_path_or_None)."""
    best = 0.0
    best_path = None
    for path in world["paths"]:
        eu = path_eu(world, path, revealed, prior_fn)
        if eu > best:
            best = eu
            best_path = path
    return best, best_path


def voi_arm(world, prior_fn):
    """Myopic VOI probing loop; returns (committed_path_or_None, probes_spent, n_probes)."""
    revealed = {}
    probes_spent = 0.0
    n_probes = 0
    unknown = [
        e for e, edge in world["edges"].items() if not edge["known"]
    ]
    while True:
        v_now, _ = best_value(world, revealed, prior_fn)
        best_gain = 1e-9
        best_edge = None
        for e in unknown:
            if e in revealed:
                continue
            p = prior_fn(world["edges"][e])
            revealed[e] = True
            v_pos, _ = best_value(world, revealed, prior_fn)
            revealed[e] = False
            v_neg, _ = best_value(world, revealed, prior_fn)
            del revealed[e]
            gain = p * v_pos + (1.0 - p) * v_neg - v_now - PROBE_COST
            if gain > best_gain:
                best_gain = gain
                best_edge = e
        if best_edge is None:
            break
        revealed[best_edge] = world["edges"][best_edge]["feasible"]
        probes_spent += PROBE_COST
        n_probes += 1
    v_final, path = best_value(world, revealed, prior_fn)
    return (path if v_final > 0.0 else None), probes_spent, n_probes


def run_arm(arm: str, world) -> dict:
    edges = world["edges"]
    probes_spent = 0.0
    n_probes = 0
    committed = None

    if arm == "FULL_ORACLE":
        feas = [p for p in world["paths"] if all(edges[e]["feasible"] for e in p)]
        if feas:
            best = min(feas, key=lambda p: path_cost(world, p))
            if REWARD - path_cost(world, best) > 0.0:
                committed = best
    elif arm == "GREEDY_KNOWN_GRAPH":
        cand = [
            p
            for p in world["paths"]
            if all(edges[e]["known"] and edges[e]["feasible"] for e in p)
        ]
        if cand:
            best = min(cand, key=lambda p: path_cost(world, p))
            if REWARD - path_cost(world, best) > 0.0:
                committed = best
    elif arm == "OPTIMIST_COMMIT":
        cand = [
            p
            for p in world["paths"]
            if not any(edges[e]["known"] and not edges[e]["feasible"] for e in p)
        ]
        if cand:
            committed = min(cand, key=lambda p: path_cost(world, p))
    elif arm == "LLM_PROXY_HEURISTIC":
        cand = [
            p
            for p in world["paths"]
            if not any(edges[e]["known"] and not edges[e]["feasible"] for e in p)
        ]
        if cand:
            def marked_up(p):
                return sum(
                    edges[e]["cost"] * (1.2 if not edges[e]["known"] else 1.0)
                    for e in p
                )
            best = min(cand, key=marked_up)
            if REWARD - marked_up(best) > 0.0:
                committed = best
    elif arm == "PURE_VOI_UNIFORM":
        committed, probes_spent, n_probes = voi_arm(world, lambda edge: 0.5)
    elif arm == "ORION_TYPED_VOI":
        committed, probes_spent, n_probes = voi_arm(
            world, lambda edge: P_FEAS[edge["type"]]
        )
    else:
        raise ValueError(arm)

    if committed is None:
        utility = -probes_spent
        success = False
        abstained = True
    else:
        abstained = False
        cost = path_cost(world, committed)
        success = all(edges[e]["feasible"] for e in committed)
        if success:
            utility = REWARD - cost - probes_spent
        else:
            utility = -cost - FAIL_PENALTY - probes_spent
    return {
        "utility": utility,
        "success": success,
        "abstained": abstained,
        "probes_spent": probes_spent,
        "n_probes": n_probes,
    }


def main() -> None:
    rng = random.Random(SEED)
    worlds = [generate_world(rng) for _ in range(EPISODES)]

    per_arm = {}
    for arm in ARMS:
        rows = [run_arm(arm, world) for world in worlds]
        per_arm[arm] = {
            "mean_utility": fmean(r["utility"] for r in rows),
            "success_rate": fmean(1.0 if r["success"] else 0.0 for r in rows),
            "abstain_rate": fmean(1.0 if r["abstained"] else 0.0 for r in rows),
            "mean_probe_spend": fmean(r["probes_spent"] for r in rows),
            "mean_probe_count": fmean(float(r["n_probes"]) for r in rows),
        }
    oracle_mu = per_arm["FULL_ORACLE"]["mean_utility"]
    for arm in ARMS:
        per_arm[arm]["mean_regret_vs_oracle"] = oracle_mu - per_arm[arm]["mean_utility"]

    mu = {arm: per_arm[arm]["mean_utility"] for arm in ARMS}
    gates = {
        "G1_oracle_upper_bound": all(mu["FULL_ORACLE"] >= mu[a] for a in ARMS),
        "G2_orion_beats_known_graph": mu["ORION_TYPED_VOI"] > mu["GREEDY_KNOWN_GRAPH"],
        "G3_orion_beats_uniform_voi": mu["ORION_TYPED_VOI"] > mu["PURE_VOI_UNIFORM"],
        "G4_blind_commit_punished": (
            mu["OPTIMIST_COMMIT"] < mu["ORION_TYPED_VOI"]
            and mu["OPTIMIST_COMMIT"] < mu["GREEDY_KNOWN_GRAPH"]
        ),
        "G5_orion_beats_llm_proxy": mu["ORION_TYPED_VOI"] > mu["LLM_PROXY_HEURISTIC"],
    }
    if not gates["G1_oracle_upper_bound"] or not gates["G4_blind_commit_punished"]:
        terminal = "N4_A_WORLD_INVALID"
    elif gates["G2_orion_beats_known_graph"] and gates["G3_orion_beats_uniform_voi"]:
        terminal = (
            "N4_A_TYPED_VOI_SUPPORTED__EXACT_SYNTHETIC"
            if gates["G5_orion_beats_llm_proxy"]
            else "N4_A_TYPED_VOI_NO_ADVANTAGE"
        )
    else:
        terminal = "N4_A_TYPED_VOI_NO_ADVANTAGE"

    result = {
        "schema": "ORIONQ.N4A.UnknownFeasibilityVOI.v1",
        "issue": 677,
        "family": "1_unknown_feasibility_voi",
        "protocol": "development/orion-q-nlane-closure/N4_A_UNKNOWN_VOI_PROTOCOL.md",
        "seed": SEED,
        "episodes": EPISODES,
        "world": {
            "layers": LAYERS,
            "width": WIDTH,
            "paths": WIDTH ** LAYERS,
            "p_known": P_KNOWN,
            "p_feas_by_type": P_FEAS,
            "probe_cost": PROBE_COST,
            "reward": REWARD,
            "fail_penalty": FAIL_PENALTY,
        },
        "arms": per_arm,
        "gates": gates,
        "terminal": terminal,
        "interpretation": {
            "authority": (
                "exact-synthetic-bounded; no real-quantum, no P10, no novelty, "
                "no LLM-capability claims; LLM_PROXY is a fixed heuristic, not "
                "an LLM measurement"
            ),
            "claim_boundary": (
                "Applies only to the frozen layered-DAG world with typed "
                "generator priors exposed as facts; does not close family 1 "
                "beyond this construction and grants no authority over real "
                "interface graphs."
            ),
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print("ORIONQ_N4_A_UNKNOWN_VOI=" + json.dumps(result, sort_keys=True, separators=(",", ":")))
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "N4_A_UNKNOWN_VOI_RESULTS.json"
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
