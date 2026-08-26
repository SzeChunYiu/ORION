#!/usr/bin/env python3
"""Publication-only uncertainty analysis for the frozen Q4 synthetic worlds.

This script does not alter any frozen N4 protocol, generator, seed, arm, metric or
primary terminal. It imports the committed experiment implementations, rebuilds
the exact seeded episodes, and adds paired descriptive uncertainty for a small
set of manuscript contrasts. The output is secondary publication analysis, not
new scientific authority.
"""

from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path
from statistics import fmean
from typing import Callable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
NLANE = REPO_ROOT / "research/extensions/orion-q/nlanes"
BOOTSTRAP_SEED = 20260822
BOOTSTRAP_DRAWS = 5000


def load(name: str):
    path = NLANE / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quantile(values: Sequence[float], p: float) -> float:
    rows = sorted(values)
    if not rows:
        raise ValueError("quantile of empty sequence")
    x = (len(rows) - 1) * p
    lo = int(x)
    hi = min(lo + 1, len(rows) - 1)
    fraction = x - lo
    return rows[lo] * (1.0 - fraction) + rows[hi] * fraction


def paired_summary(differences: Sequence[float], *, seed_label: str) -> dict:
    rows = tuple(float(value) for value in differences)
    if not rows:
        raise ValueError("paired summary requires observations")
    rng = random.Random(f"{BOOTSTRAP_SEED}:{seed_label}")
    means = []
    n = len(rows)
    for _ in range(BOOTSTRAP_DRAWS):
        means.append(fmean(rows[rng.randrange(n)] for _ in range(n)))
    return {
        "n_pairs": n,
        "mean_difference": fmean(rows),
        "bootstrap_95pct_ci": [quantile(means, 0.025), quantile(means, 0.975)],
        "paired_win_fraction": sum(value > 0.0 for value in rows) / n,
        "paired_tie_fraction": sum(abs(value) <= 1e-12 for value in rows) / n,
        "paired_loss_fraction": sum(value < 0.0 for value in rows) / n,
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed": f"{BOOTSTRAP_SEED}:{seed_label}",
    }


def contrast(
    episodes: Sequence[object],
    run: Callable[[str, object], dict],
    treatment: str,
    comparator: str,
    metric: str,
    *,
    larger_is_better: bool = True,
    label: str,
) -> dict:
    differences = []
    for episode in episodes:
        a = float(run(treatment, episode)[metric])
        b = float(run(comparator, episode)[metric])
        differences.append(a - b if larger_is_better else b - a)
    out = paired_summary(differences, seed_label=label)
    out.update(
        {
            "treatment": treatment,
            "comparator": comparator,
            "metric": metric,
            "direction": "positive_favors_treatment",
        }
    )
    return out


def study_a() -> dict:
    m = load("n4_a_unknown_voi")
    rng = random.Random(m.SEED)
    episodes = [m.generate_world(rng) for _ in range(m.EPISODES)]
    return {
        "typed_vs_uniform_voi_utility": contrast(
            episodes,
            m.run_arm,
            "ORION_TYPED_VOI",
            "PURE_VOI_UNIFORM",
            "utility",
            label="A-typed-vs-uniform",
        ),
        "typed_vs_known_graph_utility": contrast(
            episodes,
            m.run_arm,
            "ORION_TYPED_VOI",
            "GREEDY_KNOWN_GRAPH",
            "utility",
            label="A-typed-vs-known",
        ),
    }


def study_b() -> dict:
    m = load("n4_b_stale_receipt_reopening")
    rng = random.Random(m.SEED)
    episodes = {
        regime: [m.generate_episode(regime, rng) for _ in range(m.EPISODES_PER_REGIME)]
        for regime in m.REGIMES
    }
    result = {}
    for regime, rows in episodes.items():
        result[regime] = {
            "scoped_vs_never_mean_round_utility": contrast(
                rows,
                m.run_arm,
                "ORION_SCOPED_REOPEN",
                "NEVER_REOPEN",
                "mean_round_utility",
                label=f"B-{regime}-never",
            ),
            "scoped_vs_unscoped_mean_round_utility": contrast(
                rows,
                m.run_arm,
                "ORION_SCOPED_REOPEN",
                "UNSCOPED_CHANGE_REOPEN",
                "mean_round_utility",
                label=f"B-{regime}-unscoped",
            ),
        }
    return result


def study_c() -> dict:
    m = load("n4_c_interval_pareto")
    rng = random.Random(m.SEED)
    episodes = [m.generate_episode(rng) for _ in range(m.EPISODES)]

    def run(arm: str, episode: object) -> dict:
        regret, _ = m.run_arm(arm, episode)
        return {"regret": float(regret)}

    return {
        "orion_vs_random_verification_regret_reduction": contrast(
            episodes,
            run,
            "ORION_INTERVAL_PARETO",
            "RANDOM_VERIFY_MIDPOINT",
            "regret",
            larger_is_better=False,
            label="C-orion-vs-random",
        )
    }


def study_e() -> dict:
    m = load("n4_e_active_experiments")
    rng = random.Random(m.SEED)
    episodes = [m.generate_episode(rng) for _ in range(m.EPISODES)]
    return {
        "decision_voi_vs_infogain_utility": contrast(
            episodes,
            m.run_arm,
            "ORION_DECISION_VOI",
            "INFOGAIN",
            "utility",
            label="E-voi-vs-infogain",
        ),
        "decision_voi_vs_llm_proxy_utility": contrast(
            episodes,
            m.run_arm,
            "ORION_DECISION_VOI",
            "LLM_PROXY_HEURISTIC",
            "utility",
            label="E-voi-vs-proxy",
        ),
    }


def study_f3() -> dict:
    m = load("n4_f3_remint_transport")
    rng = random.Random(m.SEED)
    episodes = {
        regime: [m.generate_episode(regime, rng) for _ in range(m.EPISODES_PER_REGIME)]
        for regime in m.REGIME_ORDER
    }
    return {
        "mixed_typed_vs_rederive_utility": contrast(
            episodes["MIXED_TRANSPORT"],
            m.run_arm,
            "ORION_TYPED_TRANSPORT",
            "RE_DERIVE_SCRATCH",
            "utility",
            label="F3-mixed-rederive",
        ),
        "mixed_typed_vs_naive_utility": contrast(
            episodes["MIXED_TRANSPORT"],
            m.run_arm,
            "ORION_TYPED_TRANSPORT",
            "NAIVE_CARRY_FORWARD",
            "utility",
            label="F3-mixed-naive",
        ),
        "unnecessary_typed_vs_rederive_utility": contrast(
            episodes["REMINT_UNNECESSARY"],
            m.run_arm,
            "ORION_TYPED_TRANSPORT",
            "RE_DERIVE_SCRATCH",
            "utility",
            label="F3-unnecessary-rederive",
        ),
    }


def main() -> None:
    output = {
        "schema": "ORION.Q4.PublicationPairedAnalysis.v1",
        "authority": (
            "secondary deterministic publication analysis over the original frozen seeds; "
            "does not alter primary terminals and grants no real-agent or novelty authority"
        ),
        "method": (
            "paired episode-level mean differences; 95% percentile bootstrap intervals "
            "with 5000 deterministic resamples"
        ),
        "studies": {
            "N4_A": study_a(),
            "N4_B": study_b(),
            "N4_C": study_c(),
            "N4_E": study_e(),
            "N4_F3": study_f3(),
        },
        "N4_D_note": (
            "N4-D is a frozen exact constructed-chain census (200 laundering / 200 honest) "
            "rather than a sampled episode utility comparison; report counts directly."
        ),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
