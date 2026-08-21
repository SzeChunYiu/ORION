"""ORION-Q N4-E: active discriminating interface-experiment selection.

Frozen protocol:
development/orion-q-nlane-closure/N4_E_ACTIVE_EXPERIMENTS_PROTOCOL.md
All probing arms share priors and the SAME stopping rule; only next-experiment
selection differs. Decoy facts (max entropy, decision-irrelevant) are a hostile
control for pure information gain.

Run:
    python research/extensions/orion-q/nlanes/n4_e_active_experiments.py
"""

from __future__ import annotations

import json
import math
import os
import random
from statistics import fmean

SEED = 20260821
EPISODES = 400
N_FACTS = 6
LOAD_BEARING = (0, 1, 2, 3)
DECOYS = (4, 5)
N_PLANS = 8
REWARD = 20.0
FAIL_PENALTY = 8.0
VOI_EPS = 1e-9
ARMS = (
    "ORACLE",
    "RANDOM_ORDER",
    "CHEAPEST_FIRST",
    "INFOGAIN",
    "ORION_DECISION_VOI",
    "LLM_PROXY_HEURISTIC",
)


def generate_episode(rng: random.Random) -> dict:
    priors = []
    costs = []
    for i in range(N_FACTS):
        if i in LOAD_BEARING:
            priors.append(rng.uniform(0.25, 0.85))
        else:
            priors.append(rng.uniform(0.45, 0.55))
        costs.append(rng.uniform(0.2, 1.5))
    truths = [rng.random() < priors[i] for i in range(N_FACTS)]
    plans = []
    for _ in range(N_PLANS):
        k = rng.randint(2, 3)
        facts = rng.sample(LOAD_BEARING, k)
        clause = [(f, rng.random() < 0.5) for f in facts]  # (fact, required_value)
        plans.append({"cost": rng.uniform(2.0, 8.0), "clause": clause})
    return {
        "priors": priors,
        "costs": costs,
        "truths": truths,
        "plans": plans,
        "arm_seed": rng.randrange(2**31),
    }


def clause_prob(plan: dict, known: dict, priors: list) -> float:
    prob = 1.0
    for fact, required in plan["clause"]:
        if fact in known:
            if known[fact] != required:
                return 0.0
        else:
            p = priors[fact]
            prob *= p if required else (1.0 - p)
    return prob


def best_decision(episode: dict, known: dict):
    """Return (value, plan_index_or_None). Value = max(0, best plan EU)."""
    best_v = 0.0
    best_j = None
    for j, plan in enumerate(episode["plans"]):
        prob = clause_prob(plan, known, episode["priors"])
        eu = prob * REWARD - plan["cost"] - (1.0 - prob) * FAIL_PENALTY
        if eu > best_v:
            best_v = eu
            best_j = j
    return best_v, best_j


def net_voi(episode: dict, known: dict, fact: int) -> float:
    p = episode["priors"][fact]
    known[fact] = True
    v_pos, _ = best_decision(episode, known)
    known[fact] = False
    v_neg, _ = best_decision(episode, known)
    del known[fact]
    v_now, _ = best_decision(episode, known)
    return p * v_pos + (1.0 - p) * v_neg - v_now - episode["costs"][fact]


def select_next(arm: str, episode: dict, known: dict, arm_rng: random.Random) -> int:
    unknown = [i for i in range(N_FACTS) if i not in known]
    if arm == "RANDOM_ORDER":
        return arm_rng.choice(unknown)
    if arm == "CHEAPEST_FIRST":
        return min(unknown, key=lambda i: (episode["costs"][i], i))
    if arm == "INFOGAIN":
        def entropy(i):
            p = episode["priors"][i]
            if p <= 0.0 or p >= 1.0:
                return 0.0
            return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)
        return max(unknown, key=lambda i: (entropy(i), -i))
    if arm == "ORION_DECISION_VOI":
        def ratio(i):
            gain = net_voi(episode, known, i) + episode["costs"][i]
            return gain / episode["costs"][i]
        return max(unknown, key=lambda i: (ratio(i), -i))
    if arm == "LLM_PROXY_HEURISTIC":
        order = []
        for plan in sorted(episode["plans"], key=lambda pl: pl["cost"]):
            for fact, _ in plan["clause"]:
                if fact not in order:
                    order.append(fact)
        for fact in order:
            if fact not in known:
                return fact
        return min(unknown, key=lambda i: (episode["costs"][i], i))
    raise ValueError(arm)


def run_arm(arm: str, episode: dict) -> dict:
    if arm == "ORACLE":
        best_u = 0.0
        for plan in episode["plans"]:
            feasible = all(
                episode["truths"][f] == req for f, req in plan["clause"]
            )
            if feasible:
                best_u = max(best_u, REWARD - plan["cost"])
        return {
            "utility": best_u,
            "probe_spend": 0.0,
            "probe_count": 0,
            "decoy_probes": 0,
            "committed": best_u > 0.0,
            "commit_success": best_u > 0.0,
        }

    arm_rng = random.Random(episode["arm_seed"])
    known: dict[int, bool] = {}
    probe_spend = 0.0
    probe_count = 0
    decoy_probes = 0
    # Shared stopping rule: continue while ANY unknown fact has positive net VOI.
    while len(known) < N_FACTS:
        unknown = [i for i in range(N_FACTS) if i not in known]
        if max(net_voi(episode, known, i) for i in unknown) <= VOI_EPS:
            break
        fact = select_next(arm, episode, known, arm_rng)
        known[fact] = episode["truths"][fact]
        probe_spend += episode["costs"][fact]
        probe_count += 1
        if fact in DECOYS:
            decoy_probes += 1

    value, plan_j = best_decision(episode, known)
    if plan_j is None:
        return {
            "utility": -probe_spend,
            "probe_spend": probe_spend,
            "probe_count": probe_count,
            "decoy_probes": decoy_probes,
            "committed": False,
            "commit_success": False,
        }
    plan = episode["plans"][plan_j]
    feasible = all(episode["truths"][f] == req for f, req in plan["clause"])
    if feasible:
        utility = REWARD - plan["cost"] - probe_spend
    else:
        utility = -plan["cost"] - FAIL_PENALTY - probe_spend
    return {
        "utility": utility,
        "probe_spend": probe_spend,
        "probe_count": probe_count,
        "decoy_probes": decoy_probes,
        "committed": True,
        "commit_success": feasible,
    }


def main() -> None:
    rng = random.Random(SEED)
    episodes = [generate_episode(rng) for _ in range(EPISODES)]

    per_arm = {}
    for arm in ARMS:
        rows = [run_arm(arm, ep) for ep in episodes]
        total_probes = sum(r["probe_count"] for r in rows)
        commits = [r for r in rows if r["committed"]]
        per_arm[arm] = {
            "mean_utility": fmean(r["utility"] for r in rows),
            "mean_probe_spend": fmean(r["probe_spend"] for r in rows),
            "mean_probe_count": fmean(float(r["probe_count"]) for r in rows),
            "commit_rate": len(commits) / EPISODES,
            "commit_accuracy": (
                fmean(1.0 if r["commit_success"] else 0.0 for r in commits)
                if commits
                else 0.0
            ),
            "decoy_probe_fraction": (
                sum(r["decoy_probes"] for r in rows) / total_probes
                if total_probes
                else 0.0
            ),
        }
    oracle_mu = per_arm["ORACLE"]["mean_utility"]
    for arm in ARMS:
        per_arm[arm]["mean_regret_vs_oracle"] = oracle_mu - per_arm[arm]["mean_utility"]

    mu = {arm: per_arm[arm]["mean_utility"] for arm in ARMS}
    orion_decoy = per_arm["ORION_DECISION_VOI"]["decoy_probe_fraction"]
    infogain_decoy = per_arm["INFOGAIN"]["decoy_probe_fraction"]
    gates = {
        "G1_oracle_upper_bound": all(mu["ORACLE"] >= mu[a] for a in ARMS),
        "G2_orion_beats_infogain": mu["ORION_DECISION_VOI"] > mu["INFOGAIN"],
        "G3_orion_beats_order_controls": (
            mu["ORION_DECISION_VOI"] > mu["RANDOM_ORDER"]
            and mu["ORION_DECISION_VOI"] > mu["CHEAPEST_FIRST"]
        ),
        "G4_orion_beats_llm_proxy": mu["ORION_DECISION_VOI"] > mu["LLM_PROXY_HEURISTIC"],
        "G5_decoy_control_valid": (
            infogain_decoy > orion_decoy and infogain_decoy >= 0.10
        ),
    }
    if not gates["G1_oracle_upper_bound"] or not gates["G5_decoy_control_valid"]:
        terminal = "N4_E_WORLD_INVALID"
    elif (
        gates["G2_orion_beats_infogain"]
        and gates["G3_orion_beats_order_controls"]
        and gates["G4_orion_beats_llm_proxy"]
    ):
        terminal = "N4_E_DECISION_COUPLED_SELECTION_SUPPORTED__EXACT_SYNTHETIC"
    else:
        terminal = "N4_E_DECISION_COUPLED_SELECTION_NO_ADVANTAGE"

    result = {
        "schema": "ORIONQ.N4E.ActiveInterfaceExperimentSelection.v1",
        "issue": 677,
        "family": "6_active_discriminating_experiment_selection",
        "protocol": (
            "development/orion-q-nlane-closure/N4_E_ACTIVE_EXPERIMENTS_PROTOCOL.md"
        ),
        "seed": SEED,
        "episodes": EPISODES,
        "world": {
            "n_facts": N_FACTS,
            "load_bearing_facts": list(LOAD_BEARING),
            "decoy_facts": list(DECOYS),
            "n_plans": N_PLANS,
            "reward": REWARD,
            "fail_penalty": FAIL_PENALTY,
            "shared_stopping_rule": (
                "stop when no unknown fact has positive myopic net VOI; "
                "identical for all probing arms"
            ),
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
                "Isolates next-experiment SELECTION quality under a shared "
                "stopping rule on the frozen clause world; not a general "
                "active-learning theorem."
            ),
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print(
        "ORIONQ_N4_E_ACTIVE_EXPERIMENTS="
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    pretty = json.dumps(result, indent=2, sort_keys=True)
    print(pretty)
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "N4_E_ACTIVE_EXPERIMENTS_RESULTS.json",
    )
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(pretty + "\n")


if __name__ == "__main__":
    main()
