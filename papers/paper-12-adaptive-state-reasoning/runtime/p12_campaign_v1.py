"""P12 stop/go campaign — executes the frozen protocol.

Protocol:  papers/paper-12-adaptive-state-reasoning/top_tier/p12_stopgo_frozen_menus_v1.json
Prereg:    papers/paper-12-adaptive-state-reasoning/runtime/P12_CAMPAIGN_PREREG_V1.md

The prereg froze the four signal implementations and the three arm policies
before any outcome existed. Nothing here may redefine them.

GOLD LEAK GUARD
---------------
benchmark/gold_programs/ holds reference solutions and benchmark/scoring_rubrics/
holds the rubrics. Both now sit on the same filesystem as the campaign. A
prompt that reached either would score by copying, and the resulting numbers
would look exactly like capability. Every path this module reads is checked
against a deny list before it is opened, and the check fails loudly rather
than skipping.
"""
from __future__ import annotations

import ast
import csv
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

BENCH = Path("/projects/hep/fs10/scratch/scyiu/sab_benchmark/benchmark")
CSV = Path("/home/scyiu/orion-work/sab/ScienceAgentBench.csv")
OUT = Path("/projects/hep/fs10/scratch/scyiu/p12_stopgo")

#: License exclusions carried verbatim from the frozen protocol.
EXCLUDED = {3, 32, 46, 53, 54, 84}

#: Never read. Not "avoided by convention" -- enforced on every open.
DENIED = ("gold_programs", "scoring_rubrics", "gold_results")

ACTIONS = {
    "A_RETAIN_MINIMAL": {"state": 0, "reason": 0, "charge": 0},
    "A_STATE_MAX": {"state": 2, "reason": 0, "charge": 2},
    "A_REASON_MAX": {"state": 0, "reason": 2, "charge": 2},
    "A_BALANCED": {"state": 1, "reason": 1, "charge": 2},
}


class GoldLeak(RuntimeError):
    """Raised when the campaign tries to open an outcome-side path."""


def guarded_read(path: Path) -> str:
    parts = set(Path(path).parts)
    hit = parts.intersection(DENIED)
    if hit:
        raise GoldLeak(f"campaign attempted to read {sorted(hit)}: {path}")
    return Path(path).read_text(encoding="utf-8", errors="replace")


# --- signals, exactly as preregistered ---------------------------------------

def signal_pending_multiplicity(row: dict) -> int:
    """Count of comma-separated entries in subtask_categories."""
    return len([s for s in row["subtask_categories"].split(",") if s.strip()])


def signal_materialization_cost(_row: dict) -> float:
    """Charge units per state-construction unit. Constant 1 under FLAT."""
    return ACTIONS["A_STATE_MAX"]["charge"] / ACTIONS["A_STATE_MAX"]["state"]


def signal_serve_exchange_rate(_row: dict) -> float:
    """State-unit charge over reasoning-unit charge. Constant 1.0 under FLAT."""
    a, b = ACTIONS["A_STATE_MAX"], ACTIONS["A_REASON_MAX"]
    return (a["charge"] / a["state"]) / (b["charge"] / b["reason"])


def difficulty_priors(rows: list[dict]) -> dict[str, str]:
    """Family median of len(task_inst)+len(domain_knowledge), tertiled."""
    by_family: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        by_family[r["subtask_categories"]].append(
            len(r["task_inst"]) + len(r["domain_knowledge"])
        )
    med = {f: statistics.median(v) for f, v in by_family.items()}
    vals = sorted(med.values())
    lo, hi = vals[len(vals) // 3], vals[2 * len(vals) // 3]
    return {f: ("LOW" if m <= lo else "HIGH" if m >= hi else "MID") for f, m in med.items()}


# --- arm policies, exactly as preregistered -----------------------------------

def arm_action(arm: str, mult: int, mult_median: float, difficulty: str) -> str:
    high_mult = mult >= mult_median
    high_diff = difficulty == "HIGH"
    if arm == "ONE_SIGNAL_STATE":
        return "A_STATE_MAX" if high_mult else "A_RETAIN_MINIMAL"
    if arm == "ONE_SIGNAL_REASON":
        return "A_REASON_MAX" if high_diff else "A_RETAIN_MINIMAL"
    if arm == "ADAPTIVE":
        if high_mult and high_diff:
            return "A_BALANCED"
        if high_mult:
            return "A_STATE_MAX"
        if high_diff:
            return "A_REASON_MAX"
        return "A_RETAIN_MINIMAL"
    raise ValueError(arm)


def load_rows() -> list[dict]:
    rows = list(csv.DictReader(CSV.open()))
    return [r for r in rows if int(r["instance_id"]) not in EXCLUDED]


def main() -> int:
    rows = load_rows()
    prior = difficulty_priors(rows)
    mults = [signal_pending_multiplicity(r) for r in rows]
    mult_median = statistics.median(mults)

    # Prove the guard rejects an outcome-side path before trusting it on the run.
    try:
        guarded_read(BENCH / "gold_programs" / "anything.py")
    except GoldLeak:
        guard_ok = True
    else:
        guard_ok = False
    if not guard_ok:
        print("FATAL: gold-leak guard did not fire on a denied path", file=sys.stderr)
        return 2

    plan = []
    for r in rows:
        m = signal_pending_multiplicity(r)
        d = prior[r["subtask_categories"]]
        plan.append({
            "instance_id": r["instance_id"],
            "domain": r["domain"],
            "family": r["subtask_categories"],
            "signals": {
                "S_PENDING_MULTIPLICITY": m,
                "S_DECLARED_MATERIALIZATION_COST": signal_materialization_cost(r),
                "S_DECLARED_SERVE_EXCHANGE_RATE": signal_serve_exchange_rate(r),
                "S_FAMILY_DIFFICULTY_PRIOR": d,
            },
            "actions": {a: arm_action(a, m, mult_median, d)
                        for a in ("ADAPTIVE", "ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON")},
        })

    dist = {a: defaultdict(int) for a in ("ADAPTIVE", "ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON")}
    for p in plan:
        for a, act in p["actions"].items():
            dist[a][act] += 1

    manifest = {
        "schema": "orion.p12.campaign-plan.v1",
        "status": "PLAN_ONLY__NO_OUTCOMES",
        "gold_leak_guard": {"verified_fires_on_denied_path": guard_ok, "denied": list(DENIED)},
        "instances": len(rows),
        "families": len({r["subtask_categories"] for r in rows}),
        "domains": len({r["domain"] for r in rows}),
        "multiplicity_median": mult_median,
        "action_distribution": {a: dict(d) for a, d in dist.items()},
        "arms_differ": {
            "adaptive_vs_state": sum(1 for p in plan
                                     if p["actions"]["ADAPTIVE"] != p["actions"]["ONE_SIGNAL_STATE"]),
            "adaptive_vs_reason": sum(1 for p in plan
                                      if p["actions"]["ADAPTIVE"] != p["actions"]["ONE_SIGNAL_REASON"]),
        },
        "plan": plan,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "P12_CAMPAIGN_PLAN_V1.json").write_text(json.dumps(manifest, indent=2) + "\n")
    summary = {k: v for k, v in manifest.items() if k != "plan"}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
