#!/usr/bin/env python3
"""Detectable-effect statement for ORION-21's preregistered >=8/10 family gate.

P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET is a NEGATIVE read off a frozen gate: at
least 8 of 10 digit responsibilities must be quality-supported. The arms returned
LINEAR 3/10, RBF 5/10, KNN 5/10, and thresholds were not retuned.

Nothing in the round states what per-responsibility capability a >=8/10 rule at
n=10 can actually detect. Without that, "family-scale capability is absent" and
"the gate cannot see it at n=10" are indistinguishable readings of the same
number, and they carry opposite implications for the paper's scope claim.

Everything here is exact binomial arithmetic over the ten registered
responsibilities. It adds no experiment, reads no outcome, and moves no terminal:
the gate was missed and remains missed. It bounds what the miss licenses.

Usage: compute_gate_design_power_v1.py [--emit out.json]
"""
from __future__ import annotations
import argparse, json
from math import comb

N = 10
GATE = 8
OBSERVED = {"LINEAR": 3, "RBF": 5, "KNN": 5}


def p_at_least(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def p_at_most(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def _bisect(predicate) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if predicate(mid):
            lo = mid
        else:
            hi = mid
    return lo


def power_threshold(target: float) -> float:
    """Smallest true capability at which the gate passes with probability >= target."""
    return _bisect(lambda p: p_at_least(GATE, N, p) < target)


def clopper_pearson(x: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact two-sided interval; the conservative choice for a small-n proportion."""
    lower = _bisect(lambda p: p_at_least(x, N, p) < alpha / 2) if x > 0 else 0.0
    upper = _bisect(lambda p: p_at_most(x, N, p) > alpha / 2) if x < N else 1.0
    return lower, upper


def analyse() -> dict:
    p80 = power_threshold(0.80)
    p50 = power_threshold(0.50)
    curve = {f"{p:.2f}": p_at_least(GATE, N, p)
             for p in (0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)}
    arms = {}
    for name, x in OBSERVED.items():
        lo, hi = clopper_pearson(x)
        arms[name] = {
            "observed": f"{x}/{N}",
            "ci95_lower": lo,
            "ci95_upper": hi,
            "excludes_80pct_power_region": hi < p80,
        }
    return {
        "schema": "ORION21.QUERY_FAMILY_GATE_DESIGN_POWER.v1",
        "gate": f">={GATE}/{N}",
        "false_pass_rate_at_p_0_5": p_at_least(GATE, N, 0.5),
        "power_curve": curve,
        "capability_for_80pct_power": p80,
        "capability_for_50pct_power": p50,
        "arms": arms,
        "reading": (
            "Every arm's exact interval lies below the capability the gate is powered "
            "to detect, so the miss is not an artefact of n=10: capability at the "
            "preregistered level is excluded. Capability in the 0.6-0.8 band is not "
            "excluded, and there the gate's power is 17-68%, so the NEGATIVE bounds "
            "family-scale capability below the registered bar rather than establishing "
            "that capability is absent."
        ),
        "terminal_unchanged": "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit")
    a = ap.parse_args()
    out = analyse()
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if a.emit:
        open(a.emit, "w", encoding="utf-8").write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
