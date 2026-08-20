"""Deterministic ORION-Q MAX-R0 heterogeneous research-state diagnostic.

This diagnostic asks whether one domain-neutral scoped failure/reopening contract
retains value across four synthetic quantum research regimes.  It is not a
protected confirmatory experiment and grants no P10, novelty, or real-quantum
authority.

Run:
    python research/extensions/orion-q/max_r0_heterogeneous_arena.py
"""

from __future__ import annotations

import json
import random
from statistics import fmean

SEED = 20260820
EPISODES_PER_DOMAIN = 20_000
BOOTSTRAP_REPEATS = 2_000

DOMAINS = {
    "SYNTHESIS": {
        "p_prev": 0.65,
        "p_change": 0.42,
        "p_primary_reopen_success": 0.985,
        "p_primary_same_success": 0.08,
        "p_backup": 0.95,
        "primary_cost": 1.0,
        "backup_cost": 4.0,
    },
    "ALGO_INTERFACE": {
        "p_prev": 0.58,
        "p_change": 0.36,
        "p_primary_reopen_success": 0.975,
        "p_primary_same_success": 0.06,
        "p_backup": 0.94,
        "primary_cost": 1.4,
        "backup_cost": 5.2,
    },
    "QEC_CODESIGN": {
        "p_prev": 0.72,
        "p_change": 0.48,
        "p_primary_reopen_success": 0.965,
        "p_primary_same_success": 0.10,
        "p_backup": 0.92,
        "primary_cost": 2.0,
        "backup_cost": 7.5,
    },
    "FORMAL_REASONING": {
        "p_prev": 0.61,
        "p_change": 0.33,
        "p_primary_reopen_success": 0.99,
        "p_primary_same_success": 0.05,
        "p_backup": 0.96,
        "primary_cost": 0.8,
        "backup_cost": 3.3,
    },
}

POLICIES = ("NO_HISTORY", "RAW_HISTORY", "SCOPED_HISTORY", "ORACLE")


def generate_episode(domain: str, cfg: dict[str, float], rng: random.Random) -> dict[str, object]:
    previous_failure = rng.random() < cfg["p_prev"]
    relevant_context_changed = (
        rng.random() < cfg["p_change"] if previous_failure else False
    )
    p_primary = (
        cfg["p_primary_reopen_success"]
        if (not previous_failure or relevant_context_changed)
        else cfg["p_primary_same_success"]
    )
    return {
        "domain": domain,
        "previous_failure": previous_failure,
        "relevant_context_changed": relevant_context_changed,
        "primary_success": rng.random() < p_primary,
        "backup_success": rng.random() < cfg["p_backup"],
        "primary_cost": cfg["primary_cost"],
        "backup_cost": cfg["backup_cost"],
    }


def choose(policy: str, episode: dict[str, object]) -> str:
    if policy == "NO_HISTORY":
        return "primary"
    if policy == "RAW_HISTORY":
        return "backup" if episode["previous_failure"] else "primary"
    if policy == "SCOPED_HISTORY":
        same_failure_context = (
            episode["previous_failure"] and not episode["relevant_context_changed"]
        )
        return "backup" if same_failure_context else "primary"
    if policy == "ORACLE":
        if episode["primary_success"]:
            return "primary"
        if episode["backup_success"]:
            return "backup"
        return "primary"
    raise ValueError(f"unknown policy: {policy}")


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    low = int(pos)
    high = min(low + 1, len(ordered) - 1)
    weight = pos - low
    return ordered[low] * (1.0 - weight) + ordered[high] * weight


def main() -> None:
    rng = random.Random(SEED)
    all_pairs: list[tuple[int, int, float, float]] = []
    domain_results: dict[str, object] = {}

    for domain, cfg in DOMAINS.items():
        episodes = [
            generate_episode(domain, cfg, rng) for _ in range(EPISODES_PER_DOMAIN)
        ]
        domain_results[domain] = {}

        for policy in POLICIES:
            successes = 0
            total_cost = 0.0
            repeated_dead_ends = 0
            reopen_correct = 0
            reopen_total = 0

            for episode in episodes:
                choice = choose(policy, episode)
                successes += int(bool(episode[f"{choice}_success"]))
                total_cost += float(episode[f"{choice}_cost"])
                if (
                    choice == "primary"
                    and episode["previous_failure"]
                    and not episode["relevant_context_changed"]
                ):
                    repeated_dead_ends += 1
                if episode["previous_failure"]:
                    reopen_total += 1
                    intended = (
                        "primary" if episode["relevant_context_changed"] else "backup"
                    )
                    reopen_correct += int(choice == intended)

            domain_results[domain][policy] = {
                "success_rate": successes / EPISODES_PER_DOMAIN,
                "mean_cost": total_cost / EPISODES_PER_DOMAIN,
                "repeated_dead_end_rate": repeated_dead_ends / EPISODES_PER_DOMAIN,
                "reopen_decision_accuracy": reopen_correct / reopen_total,
            }

        for episode in episodes:
            raw_choice = choose("RAW_HISTORY", episode)
            scoped_choice = choose("SCOPED_HISTORY", episode)
            all_pairs.append(
                (
                    int(bool(episode[f"{raw_choice}_success"])),
                    int(bool(episode[f"{scoped_choice}_success"])),
                    float(episode[f"{raw_choice}_cost"]),
                    float(episode[f"{scoped_choice}_cost"]),
                )
            )

    success_deltas = [scoped - raw for raw, scoped, _, _ in all_pairs]
    cost_deltas = [scoped - raw for _, _, raw, scoped in all_pairs]

    boot_rng = random.Random(SEED + 1)
    n = len(all_pairs)
    boot_success: list[float] = []
    boot_cost: list[float] = []
    for _ in range(BOOTSTRAP_REPEATS):
        sampled = [boot_rng.randrange(n) for _ in range(n)]
        boot_success.append(fmean(success_deltas[i] for i in sampled))
        boot_cost.append(fmean(cost_deltas[i] for i in sampled))

    result = {
        "schema": "ORIONQ.MAXR0HeterogeneousArenaResult.v1",
        "seed": SEED,
        "episodes_per_domain": EPISODES_PER_DOMAIN,
        "domains": domain_results,
        "aggregate": {
            "scoped_minus_raw_success_rate": fmean(success_deltas),
            "scoped_minus_raw_success_rate_bootstrap_95": [
                percentile(boot_success, 0.025),
                percentile(boot_success, 0.975),
            ],
            "scoped_minus_raw_mean_cost": fmean(cost_deltas),
            "scoped_minus_raw_mean_cost_bootstrap_95": [
                percentile(boot_cost, 0.025),
                percentile(boot_cost, 0.975),
            ],
        },
        "interpretation": {
            "milestone": "MAX_R1_GENERAL_SCOPED_FAILURE_STATE_VALUE__SYNTHETIC",
            "authority": "diagnostic_synthetic_only",
            "p10_authorized": False,
            "novelty_authorized": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
