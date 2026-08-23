"""ORION-Q N4-C: interval-cost Pareto regret vs clairvoyant oracle.

Frozen protocol: development/orion-q-nlane-closure/N4_C_INTERVAL_PARETO_PROTOCOL.md
Exact synthetic, deterministic, no authority beyond the receipt's claim boundary.

Run:
    python research/extensions/orion-q/nlanes/n4_c_interval_pareto.py
"""

from __future__ import annotations

import itertools
import json
import os
import random
from statistics import fmean, median

SEED = 20260821
EPISODES = 400
WIDTH = 3
LAYERS = 3
P_WIDE = 0.3
BUDGET = 4
OBJECTIVES = ("cost", "err")
ARMS = (
    "CLAIRVOYANT_ORACLE",
    "MIDPOINT_OPTIMIZER",
    "ROBUST_WORSTCASE",
    "BEST_CASE",
    "RANDOM_VERIFY_MIDPOINT",
    "ORION_INTERVAL_PARETO",
)


def generate_episode(rng: random.Random) -> dict:
    layer_nodes = [[(layer, w) for w in range(WIDTH)] for layer in range(LAYERS)]
    edges = {}
    edge_order = []

    def add_edge(u, v):
        rec = {}
        wide = rng.random() < P_WIDE
        for obj in OBJECTIVES:
            center = rng.uniform(1.0, 5.0)
            half = rng.uniform(1.0, 2.5) if wide else rng.uniform(0.05, 0.3)
            lo = max(0.05, center - half)
            hi = center + half
            rec[obj] = {"lo": lo, "hi": hi, "true": rng.uniform(lo, hi)}
        edges[(u, v)] = rec
        edge_order.append((u, v))

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
    return {
        "edges": edges,
        "edge_order": edge_order,
        "paths": paths,
        "w": rng.uniform(0.2, 0.8),
        "verify_seed": rng.randrange(2**31),
    }


def path_sum(episode, path, obj, field):
    return sum(episode["edges"][e][obj][field] for e in path)


def true_scalar(episode, path):
    w = episode["w"]
    return w * path_sum(episode, path, "cost", "true") + (1.0 - w) * path_sum(
        episode, path, "err", "true"
    )


def est_scalar(episode, path, verified):
    """Scalarized estimate: verified truths, midpoints elsewhere."""
    w = episode["w"]
    total = 0.0
    for obj, weight in (("cost", w), ("err", 1.0 - w)):
        s = 0.0
        for e in path:
            rec = episode["edges"][e][obj]
            s += rec["true"] if e in verified else 0.5 * (rec["lo"] + rec["hi"])
        total += weight * s
    return total


def endpoint_scalar(episode, path, field):
    w = episode["w"]
    return w * path_sum(episode, path, "cost", field) + (1.0 - w) * path_sum(
        episode, path, "err", field
    )


def interval_survivors(episode):
    """Paths not interval-dominated (dominator hi <= dominated lo in both objectives)."""
    paths = episode["paths"]
    bounds = {
        p: {
            obj: (path_sum(episode, p, obj, "lo"), path_sum(episode, p, obj, "hi"))
            for obj in OBJECTIVES
        }
        for p in paths
    }
    survivors = []
    for p in paths:
        dominated = False
        for q in paths:
            if q is p:
                continue
            leq = all(bounds[q][obj][1] <= bounds[p][obj][0] for obj in OBJECTIVES)
            strict = any(bounds[q][obj][1] < bounds[p][obj][0] for obj in OBJECTIVES)
            if leq and strict:
                dominated = True
                break
        if not dominated:
            survivors.append(p)
    return survivors


def run_arm(arm: str, episode: dict) -> tuple[float, int]:
    """Returns (regret, survivor_count_if_orion_else_-1)."""
    paths = episode["paths"]
    oracle_val = min(true_scalar(episode, p) for p in paths)
    survivors_n = -1

    if arm == "CLAIRVOYANT_ORACLE":
        choice = min(paths, key=lambda p: true_scalar(episode, p))
    elif arm == "MIDPOINT_OPTIMIZER":
        choice = min(paths, key=lambda p: est_scalar(episode, p, frozenset()))
    elif arm == "ROBUST_WORSTCASE":
        choice = min(paths, key=lambda p: endpoint_scalar(episode, p, "hi"))
    elif arm == "BEST_CASE":
        choice = min(paths, key=lambda p: endpoint_scalar(episode, p, "lo"))
    elif arm == "RANDOM_VERIFY_MIDPOINT":
        vrng = random.Random(episode["verify_seed"])
        verified = frozenset(vrng.sample(episode["edge_order"], BUDGET))
        choice = min(paths, key=lambda p: est_scalar(episode, p, verified))
    elif arm == "ORION_INTERVAL_PARETO":
        survivors = interval_survivors(episode)
        survivors_n = len(survivors)
        if len(survivors) == 1:
            choice = survivors[0]
        else:
            shared = set(survivors[0])
            for p in survivors[1:]:
                shared &= set(p)
            scores = []
            for e in episode["edge_order"]:
                if e in shared:
                    scores.append((0.0, e))
                    continue
                appearances = sum(1 for p in survivors if e in p)
                width = sum(
                    episode["edges"][e][obj]["hi"] - episode["edges"][e][obj]["lo"]
                    for obj in OBJECTIVES
                )
                scores.append((width * appearances, e))
            scores.sort(key=lambda t: (-t[0], repr(t[1])))
            verified = frozenset(e for _, e in scores[:BUDGET])
            choice = min(paths, key=lambda p: est_scalar(episode, p, verified))
    else:
        raise ValueError(arm)
    return true_scalar(episode, choice) - oracle_val, survivors_n


def main() -> None:
    rng = random.Random(SEED)
    episodes = [generate_episode(rng) for _ in range(EPISODES)]

    per_arm = {}
    survivor_counts = []
    for arm in ARMS:
        regrets = []
        for ep in episodes:
            regret, surv = run_arm(arm, ep)
            regrets.append(regret)
            if arm == "ORION_INTERVAL_PARETO":
                survivor_counts.append(surv)
        per_arm[arm] = {
            "mean_regret": fmean(regrets),
            "median_regret": median(regrets),
            "zero_regret_fraction": fmean(1.0 if r < 1e-12 else 0.0 for r in regrets),
        }

    mean_survivors = fmean(float(s) for s in survivor_counts)
    mr = {arm: per_arm[arm]["mean_regret"] for arm in ARMS}
    gates = {
        "G1_oracle_zero_regret": mr["CLAIRVOYANT_ORACLE"] == 0.0,
        "G2_orion_beats_no_verification": (
            mr["ORION_INTERVAL_PARETO"] < mr["MIDPOINT_OPTIMIZER"]
            and mr["ORION_INTERVAL_PARETO"] < mr["ROBUST_WORSTCASE"]
            and mr["ORION_INTERVAL_PARETO"] < mr["BEST_CASE"]
        ),
        "G3_targeting_beats_random_verification": (
            mr["ORION_INTERVAL_PARETO"] < mr["RANDOM_VERIFY_MIDPOINT"]
        ),
        "G4_world_ambiguous": mean_survivors > 1.0,
    }
    if not gates["G1_oracle_zero_regret"] or not gates["G4_world_ambiguous"]:
        terminal = "N4_C_WORLD_INVALID"
    elif gates["G2_orion_beats_no_verification"] and gates[
        "G3_targeting_beats_random_verification"
    ]:
        terminal = "N4_C_TARGETED_INTERVAL_PARETO_SUPPORTED__EXACT_SYNTHETIC"
    else:
        terminal = "N4_C_TARGETED_VERIFICATION_NO_ADVANTAGE"

    result = {
        "schema": "ORIONQ.N4C.IntervalParetoRegret.v1",
        "issue": 677,
        "family": "4_interval_cost_pareto_regret",
        "protocol": "development/orion-q-nlane-closure/N4_C_INTERVAL_PARETO_PROTOCOL.md",
        "seed": SEED,
        "episodes": EPISODES,
        "world": {
            "layers": LAYERS,
            "width": WIDTH,
            "p_wide_interval": P_WIDE,
            "verification_budget": BUDGET,
            "objectives": list(OBJECTIVES),
            "mean_interval_dominance_survivors": mean_survivors,
        },
        "arms": per_arm,
        "gates": gates,
        "terminal": terminal,
        "interpretation": {
            "authority": (
                "exact-synthetic-bounded; no real-quantum, no P10, no novelty "
                "claims; regret is scalarized, not full-front hypervolume"
            ),
            "claim_boundary": (
                "Applies only to the frozen interval world and budget B=4; "
                "shows value of Pareto-ambiguity-targeted verification over "
                "untargeted verification and endpoint optimizers on this "
                "construction only."
            ),
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print(
        "ORIONQ_N4_C_INTERVAL_PARETO="
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "N4_C_INTERVAL_PARETO_RESULTS.json"
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
