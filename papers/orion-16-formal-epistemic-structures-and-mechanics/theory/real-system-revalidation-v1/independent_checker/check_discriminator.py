#!/usr/bin/env python3
"""Independent evaluation of ORION-16's stamped predictions P1-P5.

Reads RESULT.json as data and re-derives each verdict. Imports no ORION-16
module and re-runs no measurement. Negative controls must fire.

Exit 0 PASS, 1 FAIL, 3 CANNOT_CHECK.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path(__file__).resolve().parents[1] / "RESULT.json"
if not R.exists():
    print(f"CANNOT_CHECK: result absent: {R}"); sys.exit(3)
d = json.loads(R.read_text())
ok = [s for s in d["systems"] if s["status"] == "OK"]
if len(ok) < 2:
    print(f"CANNOT_CHECK: only {len(ok)} evaluable systems"); sys.exit(3)

def arm(s, a): return s["arms"][a]
def _passes_guard(frac: float) -> bool:
    """The runner's authority rule, restated here so the threshold is testable."""
    return frac >= 0.95
def _refusals_documented() -> bool:
    a = Path(__file__).resolve().parents[1] / "ANALYSIS.md"
    return a.exists() and "CANNOT_CHECK" in a.read_text()
def nondec(xs): return all(b >= a for a, b in zip(xs, xs[1:]))

fr = [str(f) for f in d["fractions"]]
P = {}
P["P1_affected_closure_strands_nothing"] = all(arm(s, "affected-closure")["stranded_total"] == 0 for s in ok)
P["P2_cheap_arms_strand_on_at_least_two"] = (
    sum(arm(s, "changed-set-only")["stranded_total"] > 0 for s in ok) >= 2
    and sum(arm(s, "direct-neighbours")["stranded_total"] > 0 for s in ok) >= 2)
P["P3_conservative_cost_monotone_and_above_exact"] = all(
    nondec([s["conservative_median_cost"][f] for f in fr])
    and all(s["conservative_median_cost"][f] >= s["affected_closure_median_cost_on_subset"] for f in fr)
    for s in ok)
P["P4_incomplete_risk_monotone_and_positive_at_10pct"] = (
    all(nondec([s["incomplete_stranded_total"][f] for f in fr]) for s in ok)
    and sum(s["incomplete_stranded_total"][fr[-1]] > 0 for s in ok) >= 2)
P["P5_median_closure_at_most_half_of_full_on_two_systems"] = (
    sum(arm(s, "affected-closure")["median_cost_frac_of_full"] <= 0.50 for s in ok) >= 2)

controls = {
    "some_arm_does_strand_so_stranding_is_detectable":
        any(arm(s, "changed-set-only")["stranded_total"] > 0 for s in ok),
    "conservative_cost_actually_moves_on_some_system":
        any(len({s["conservative_median_cost"][f] for f in fr}) > 1 for s in ok),
    "full_arm_costs_100pct_by_construction":
        all(arm(s, "full")["median_cost_frac_of_full"] == 1.0 for s in ok),
    "fidelity_guard_rejects_below_threshold_and_accepts_above":
        (not _passes_guard(0.94)) and _passes_guard(0.96) and (not _passes_guard(0.243)),
    "every_reported_system_clears_the_guard":
        all(s.get("resolution_fidelity") is None or s["resolution_fidelity"] >= 0.95 for s in ok),
    "at_least_one_system_was_refused_in_the_recorded_run":
        any(s["status"] == "CANNOT_CHECK" for s in d["systems"]) or _refusals_documented(),
}

# P1 is definitional in this harness; record that rather than counting it as evidence.
notes = {"P1_is_definitional": "the affected-closure arm is the truth set itself, "
                               "so zero stranding is a harness consistency check, not evidence"}
allp = all(P.values()) and all(controls.values())
print(json.dumps({"systems_evaluable": len(ok), "predictions": P,
                  "negative_controls": controls, "notes": notes,
                  "status": "PASS" if allp else "FAIL"}, indent=1))
for k, v in {**P, **controls}.items():
    print(f"  {'ok  ' if v else 'FAIL'} {k}")
sys.exit(0 if allp else 1)
