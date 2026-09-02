#!/usr/bin/env python3
"""ORION-08 successor: N4-E power extension V1 — determine the two surviving
N4-E contrasts (the proxy row is the surviving comparison closest to zero
relative to its width) by continuing the frozen RNG stream to N_EXT=4000
episodes.

Protocol: PROTOCOL_N4E_POWER.md (committed before any outcome). Derivation and
power arithmetic: DERIVATION_N4E_POWER.md. The frozen module, protocol, and
published analysis are untouched; bootstrap machinery is the frozen
publication_analysis.py implementation (imported; the 97.5% variant replicates
its loop verbatim with the registered seed and levels).

Exit codes: 0 N4E_POWER_DETERMINED_BOTH, 1 N4E_POWER_PARTIAL_*, 3 prefix fail.
"""

from __future__ import annotations

import importlib.util
import json
import platform
import sys
from pathlib import Path
from random import Random
from statistics import fmean

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent.parent  # papers/orion-08-typed-state
N_EXT = 4000
FROZEN_N = 400
DELTA = 0.3  # practical-equivalence bound (registered)
BOOT_SEED_EXT = "20260902"
FROZEN_BOOT_SEED = 20260822  # publication_analysis.py's constant
BOOT_DRAWS = 5000

CONTRASTS = {
    "decision_voi_vs_llm_proxy_utility": ("LLM_PROXY_HEURISTIC",
                                          "E-voi-vs-proxy"),
    "decision_voi_vs_infogain_utility": ("INFOGAIN", "E-voi-vs-infogain"),
}
TREATMENT = "ORION_DECISION_VOI"
METRIC = "utility"

# frozen secondary analysis machinery (import, not re-implement)
_spec = importlib.util.spec_from_file_location(
    "publication_analysis", PARENT / "publication_analysis.py")
pa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pa)
quantile = pa.quantile
m = pa.load("n4_e_active_experiments")


def bootstrap_ci(rows: list[float], seed_label: str,
                 lo_q: float, hi_q: float) -> list[float]:
    """Verbatim replication of publication_analysis's paired bootstrap loop with
    the registered extension seed string and quantile levels."""
    rng = Random(f"{BOOT_SEED_EXT}:{seed_label}")
    means = []
    n = len(rows)
    for _ in range(BOOT_DRAWS):
        means.append(fmean(rows[rng.randrange(n)] for _ in range(n)))
    return [quantile(means, lo_q), quantile(means, hi_q)]


def frozen_ci(rows: list[float], seed_label: str) -> dict:
    """P1 cross-check: byte-faithful re-run of the FROZEN summary (frozen seed
    string, frozen 95% levels) on the prefix episodes."""
    rng = Random(f"{FROZEN_BOOT_SEED}:{seed_label}")
    means = []
    n = len(rows)
    for _ in range(BOOT_DRAWS):
        means.append(fmean(rows[rng.randrange(n)] for _ in range(n)))
    return {
        "n_pairs": n,
        "mean_difference": fmean(rows),
        "bootstrap_95pct_ci": [quantile(means, 0.025), quantile(means, 0.975)],
        "paired_win_fraction": sum(v > 0.0 for v in rows) / n,
        "paired_tie_fraction": sum(abs(v) <= 1e-12 for v in rows) / n,
        "paired_loss_fraction": sum(v < 0.0 for v in rows) / n,
    }


def paired_diffs(episodes, comparator: str) -> list[float]:
    return [float(m.run_arm(TREATMENT, ep)[METRIC])
            - float(m.run_arm(comparator, ep)[METRIC])
            for ep in episodes]


def gate(ci: list[float]) -> str:
    if ci[0] > 0.0:
        return "RESOLVED_POSITIVE"
    if ci[1] < 0.0:
        return "RESOLVED_NEGATIVE"
    if ci[0] > -DELTA and ci[1] < DELTA:
        return "BOUNDED_NULL"
    return "UNRESOLVED"


def main() -> int:
    frozen = json.loads((PARENT / "PUBLICATION_PAIRED_ANALYSIS_V1.json").read_text())
    frozen_rows = frozen["studies"]["N4_E"]

    # episodes: frozen 400-list first (byte-identical prefix), then extend the
    # same single block on the same stream (no regime blocks in N4-E)
    rng = Random(m.SEED)
    episodes = [m.generate_episode(rng) for _ in range(FROZEN_N)]
    episodes.extend(m.generate_episode(rng) for _ in range(N_EXT - FROZEN_N))

    # ---- P1 prefix cross-check (gated, first) ----
    p1 = {}
    p1_ok = True
    for key, (comparator, label) in CONTRASTS.items():
        prefix = paired_diffs(episodes[:FROZEN_N], comparator)
        got = frozen_ci(prefix, label)
        want = frozen_rows[key]
        diffs = {k: abs(got[k] - want[k]) for k in
                 ("mean_difference", "paired_win_fraction",
                  "paired_tie_fraction", "paired_loss_fraction")}
        diffs["ci_lo"] = abs(got["bootstrap_95pct_ci"][0] - want["bootstrap_95pct_ci"][0])
        diffs["ci_hi"] = abs(got["bootstrap_95pct_ci"][1] - want["bootstrap_95pct_ci"][1])
        p1[key] = {"max_abs_diff": max(diffs.values()), "pass": max(diffs.values()) < 1e-9}
        p1_ok = p1_ok and p1[key]["pass"]
        print(f"P1 {key}: max|diff|={p1[key]['max_abs_diff']:.3e} "
              f"{'PASS' if p1[key]['pass'] else 'FAIL'}", flush=True)
    if not p1_ok:
        out = {"schema": "ORION08.N4E_POWER.v1", "p1_prefix": p1,
               "terminal": "N4E_POWER_PREFIX_FAIL",
               "environment": {"python": platform.python_version(),
                               "node": platform.node()}}
        Path(HERE / "RESULTS_N4E_POWER_V1.json").write_text(
            json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps(out, indent=2, sort_keys=True))
        return 3

    # ---- targets (Bonferroni m=2 -> per-comparison 97.5%) + monitoring ----
    targets, monitoring, split = {}, {}, {}
    for key, (comparator, label) in CONTRASTS.items():
        d = paired_diffs(episodes, comparator)
        ci = bootstrap_ci(d, f"n4e-power:{label}", 0.0125, 0.9875)
        n = len(d)
        targets[key] = {
            "n": n, "mean": fmean(d), "ci_975": ci, "verdict": gate(ci),
            "win": sum(v > 0 for v in d) / n,
            "loss": sum(v < 0 for v in d) / n,
            "tie": sum(abs(v) <= 1e-12 for v in d) / n,
        }
        monitoring[key] = {
            "frozen_mean": frozen_rows[key]["mean_difference"],
            "within_10pct": abs(fmean(d) - frozen_rows[key]["mean_difference"])
            <= 0.10 * abs(frozen_rows[key]["mean_difference"]),
        }
        half = n // 2
        split[key] = {"first2000_mean": fmean(d[:half]),
                      "second2000_mean": fmean(d[half:]),
                      "full_mean": fmean(d)}
        t = targets[key]
        print(f"{key}: mean={t['mean']:+.4f} CI97.5=[{ci[0]:+.4f},{ci[1]:+.4f}] "
              f"win/loss/tie={t['win']:.3f}/{t['loss']:.3f}/{t['tie']:.3f} "
              f"-> {t['verdict']}", flush=True)

    determined = {k: targets[k]["verdict"] != "UNRESOLVED" for k in targets}
    if all(determined.values()):
        terminal = "N4E_POWER_DETERMINED_BOTH"
        rc = 0
    else:
        terminal = ("N4E_POWER_PARTIAL_" + "_".join(
            k.replace("_utility", "").replace("decision_voi_vs_", "")
            for k, ok in determined.items() if not ok))
        rc = 1

    out = {"schema": "ORION08.N4E_POWER.v1",
           "design": {"n_ext": N_EXT, "delta": DELTA, "bootstrap_draws": BOOT_DRAWS,
                      "seed_ext": BOOT_SEED_EXT, "module_seed": m.SEED,
                      "bonferroni_family": 2},
           "p1_prefix": p1, "targets": targets, "monitoring": monitoring,
           "split_half": split, "terminal": terminal,
           "environment": {"python": platform.python_version(),
                           "node": platform.node()}}
    Path(HERE / "RESULTS_N4E_POWER_V1.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"targets": {k: targets[k]["verdict"] for k in targets},
                      "monitoring": monitoring, "terminal": terminal},
                     indent=2), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
