#!/usr/bin/env python3
"""Measure when a 'bootstrap 95% lower bound > 0' gate stops being a 2.5% test.

ORION-paper#49 freezes gates of the form "family-block bootstrap 95% lower bound
> 0" and "paired 95% lower bound > 0". Those are only 2.5% tests when there are
enough independent blocks to resample. `bootstrap_mean_interval` in
tier_a_analysis_common_v1.py is statistically sound -- but it returns
`(v, v)` for a single value, a zero-width interval whose lower bound is positive
whenever `v` is, and it applies no minimum-n floor.

This calibrates the gate against the null (true mean 0) at each n and reports the
smallest n at which its false-positive rate is at or below nominal. It is a
measurement, not a claim that any particular study is underpowered: which lanes
have how many independent blocks is a separate, protected question.

Exit codes: 0 clean, 2 a finding, 3 could not check.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMMON = ROOT / "papers/publication_closure/tier_a_analysis_common_v1.py"
NOMINAL = 0.025
TRIALS = 400
RESAMPLES = 400
SEED = 20260902


def main() -> int:
    if not COMMON.is_file():
        print(f"CANNOT CHECK: {COMMON} not found")
        return 3
    spec = importlib.util.spec_from_file_location("tier_a_common", COMMON)
    common = importlib.util.module_from_spec(spec)
    sys.modules["tier_a_common"] = common
    spec.loader.exec_module(common)

    rng = random.Random(SEED)
    rows = []
    for n in (1, 2, 3, 5, 8, 12, 20, 30):
        positives = 0
        for trial in range(TRIALS):
            values = [rng.gauss(0.0, 1.0) for _ in range(n)]
            low, _ = common.bootstrap_mean_interval(values, f"n{n}t{trial}", resamples=RESAMPLES)
            if low > 0:
                positives += 1
        rate = positives / TRIALS
        rows.append({"n": n, "false_positive_rate": round(rate, 4),
                     "at_or_below_nominal": rate <= NOMINAL * 2})

    smallest_sound = next((r["n"] for r in rows if r["at_or_below_nominal"]), None)
    report = {
        "record": "BOOTSTRAP_MIN_N_GUARD_V1",
        "nominal_one_sided_rate": NOMINAL,
        "trials_per_n": TRIALS,
        "null_false_positive_by_n": rows,
        "smallest_n_at_or_below_twice_nominal": smallest_sound,
        "degenerate_single_value_interval_is_zero_width": (
            common.bootstrap_mean_interval([0.001], "probe") == (0.001, 0.001)
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))

    n1 = next(r for r in rows if r["n"] == 1)
    if n1["false_positive_rate"] <= NOMINAL * 2:
        print("FINDING: the n=1 gate did not misbehave, which contradicts the "
              "zero-width interval it returns; the probe is not measuring what it claims")
        return 2
    print(
        f"MEASURED: a 'bootstrap lower bound > 0' gate has a {n1['false_positive_rate']:.3f} "
        f"false-positive rate at n=1 against a nominal {NOMINAL}, and reaches nominal by "
        f"n={smallest_sound}. Any frozen gate of this form needs a preregistered minimum "
        f"block count; the primitive itself applies none."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
