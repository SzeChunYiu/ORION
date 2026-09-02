#!/usr/bin/env python3
"""ORION-08 successor: N4-B power extension V1 — determine the two undetermined
scoped_vs_never contrasts by continuing the frozen RNG stream to N_EXT=2000
episodes per regime.

Protocol: PROTOCOL_N4B_POWER.md (committed before any outcome). Derivation and
power arithmetic: DERIVATION_N4B_POWER.md. The frozen module, protocol, and
published analysis are untouched; bootstrap machinery is the frozen
publication_analysis.py implementation (imported; the 97.5% variant replicates
its loop verbatim with the registered seed and levels).

Exit codes: 0 N4B_POWER_DETERMINED_BOTH, 1 N4B_POWER_PARTIAL_*, 3 prefix fail.
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
N_EXT = 2000
FROZEN_N = 200
DELTA = 1.0  # practical-equivalence bound (registered)
BOOT_SEED_EXT = "20260902"
FROZEN_BOOT_SEED = 20260822  # publication_analysis.py's constant
BOOT_DRAWS = 5000

# frozen secondary analysis machinery (import, not re-implement)
_spec = importlib.util.spec_from_file_location(
    "publication_analysis", PARENT / "publication_analysis.py")
pa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pa)
quantile = pa.quantile
m = pa.load("n4_b_stale_receipt_reopening")


def bootstrap_ci(rows: list[float], seed_label: str,
                 lo_q: float, hi_q: float) -> list[float]:
    """Verbatim replication of publication_analysis.paired_summary's loop with
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


def paired_diffs(episodes, treatment: str, comparator: str) -> list[float]:
    return [float(m.run_arm(treatment, ep)["mean_round_utility"])
            - float(m.run_arm(comparator, ep)["mean_round_utility"])
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
    frozen_rows = frozen["studies"]["N4_B"]

    # episodes: A1-N4B layout — frozen blocks first (both regimes' prefixes
    # byte-identical to the frozen analysis), then extend each block in order
    rng = Random(m.SEED)
    episodes = {reg: [m.generate_episode(reg, rng) for _ in range(FROZEN_N)]
                for reg in m.REGIMES}
    for reg in m.REGIMES:
        episodes[reg].extend(m.generate_episode(reg, rng)
                             for _ in range(N_EXT - FROZEN_N))

    # ---- P1 prefix cross-check (gated, first) ----
    p1 = {}
    p1_ok = True
    for reg in m.REGIMES:
        prefix = paired_diffs(episodes[reg][:FROZEN_N],
                              "ORION_SCOPED_REOPEN", "NEVER_REOPEN")
        got = frozen_ci(prefix, f"B-{reg}-never")
        want = frozen_rows[reg]["scoped_vs_never_mean_round_utility"]
        diffs = {k: abs(got[k] - want[k]) for k in
                 ("mean_difference", "paired_win_fraction",
                  "paired_tie_fraction", "paired_loss_fraction")}
        diffs["ci_lo"] = abs(got["bootstrap_95pct_ci"][0] - want["bootstrap_95pct_ci"][0])
        diffs["ci_hi"] = abs(got["bootstrap_95pct_ci"][1] - want["bootstrap_95pct_ci"][1])
        p1[reg] = {"max_abs_diff": max(diffs.values()), "pass": max(diffs.values()) < 1e-9}
        p1_ok = p1_ok and p1[reg]["pass"]
        print(f"P1 {reg}: max|diff|={p1[reg]['max_abs_diff']:.3e} "
              f"{'PASS' if p1[reg]['pass'] else 'FAIL'}", flush=True)
    if not p1_ok:
        out = {"schema": "ORION08.N4B_POWER.v1", "p1_prefix": p1,
               "terminal": "N4B_POWER_PREFIX_FAIL",
               "environment": {"python": platform.python_version(),
                               "node": platform.node()}}
        Path(HERE / "RESULTS_N4B_POWER_V1.json").write_text(
            json.dumps(out, indent=2, sort_keys=True) + "\n")
        print(json.dumps(out, indent=2, sort_keys=True))
        return 3

    # ---- targets (Bonferroni m=2 -> per-comparison 97.5%) + monitoring ----
    targets, monitoring, split = {}, {}, {}
    for reg in m.REGIMES:
        d_never = paired_diffs(episodes[reg], "ORION_SCOPED_REOPEN", "NEVER_REOPEN")
        d_unsc = paired_diffs(episodes[reg], "ORION_SCOPED_REOPEN",
                              "UNSCOPED_CHANGE_REOPEN")
        ci = bootstrap_ci(d_never, f"n4b-power:{reg}-never", 0.0125, 0.9875)
        n = len(d_never)
        targets[reg] = {
            "n": n, "mean": fmean(d_never), "ci_975": ci, "verdict": gate(ci),
            "win": sum(v > 0 for v in d_never) / n,
            "loss": sum(v < 0 for v in d_never) / n,
            "tie": sum(abs(v) <= 1e-12 for v in d_never) / n,
        }
        monitoring[reg] = {
            "scoped_vs_unscoped_mean": fmean(d_unsc),
            "frozen_mean": frozen_rows[reg]["scoped_vs_unscoped_mean_round_utility"]["mean_difference"],
            "within_10pct": abs(fmean(d_unsc)
                                - frozen_rows[reg]["scoped_vs_unscoped_mean_round_utility"]["mean_difference"])
            <= 0.10 * abs(frozen_rows[reg]["scoped_vs_unscoped_mean_round_utility"]["mean_difference"]),
        }
        half = n // 2
        split[reg] = {"first1000_mean": fmean(d_never[:half]),
                      "second1000_mean": fmean(d_never[half:]),
                      "full_mean": fmean(d_never)}
        t = targets[reg]
        print(f"{reg}: mean={t['mean']:+.4f} CI97.5=[{ci[0]:+.4f},{ci[1]:+.4f}] "
              f"win/loss/tie={t['win']:.3f}/{t['loss']:.3f}/{t['tie']:.3f} "
              f"-> {t['verdict']}", flush=True)

    determined = {r: targets[r]["verdict"] != "UNRESOLVED" for r in targets}
    if all(determined.values()):
        terminal = "N4B_POWER_DETERMINED_BOTH"
        rc = 0
    else:
        terminal = ("N4B_POWER_PARTIAL_" + "_".join(
            r.lower() for r, ok in determined.items() if not ok))
        rc = 1

    out = {"schema": "ORION08.N4B_POWER.v1",
           "design": {"n_ext": N_EXT, "delta": DELTA, "bootstrap_draws": BOOT_DRAWS,
                      "seed_ext": BOOT_SEED_EXT, "module_seed": m.SEED,
                      "bonferroni_family": 2},
           "p1_prefix": p1, "targets": targets, "monitoring": monitoring,
           "split_half": split, "terminal": terminal,
           "environment": {"python": platform.python_version(),
                           "node": platform.node()}}
    Path(HERE / "RESULTS_N4B_POWER_V1.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"targets": {r: targets[r]["verdict"] for r in targets},
                      "monitoring": monitoring, "terminal": terminal},
                     indent=2), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
