"""P12 stop/go gate — applies the frozen decision rule to scored episodes.

Gate (verbatim from p12_stopgo_frozen_menus_v1.json):
  adaptive gain >= 3 normalized points; block-bootstrap lower CI > 0;
  positive in >=2/3 domains and every leave-one-domain-out; max regret <= 2 pp.

Fail action, also frozen: stop the positive complementarity claim and publish a
boundary/null result. Do not iterate until positive.

DEGENERACY CHECK comes first. If every arm scores zero, the arms are tied
because nothing was solved, not because allocation does not matter. That is a
floor effect and it is reported as FLOOR, never as a null result about
allocation. A gate applied to an all-zero table would "fail" for a reason it
cannot see, and the failure would be misread as evidence.
"""
from __future__ import annotations
import json, glob, random, statistics, sys
from collections import defaultdict
from pathlib import Path

SCORES = Path("/projects/hep/fs10/scratch/scyiu/p12_stopgo/scores")
OUT = Path("/projects/hep/fs10/scratch/scyiu/p12_stopgo/P12_STOPGO_RESULT_V1.json")
ARMS = ("ADAPTIVE", "ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON")
GAIN_MIN, REGRET_MAX, BOOT = 3.0, 2.0, 5000


def family_means(rows, arm, domains=None):
    by = defaultdict(list)
    for r in rows:
        if r["arm"] != arm:
            continue
        if domains and r["domain"] not in domains:
            continue
        by[r["family"]].append(r["outcome"])
    return {f: statistics.mean(v) for f, v in by.items()}


def gain_points(rows, domains=None):
    """Adaptive minus the STRONGER one-signal arm, in normalized points (x100)."""
    a = family_means(rows, "ADAPTIVE", domains)
    best_other, best_name = None, None
    for arm in ("ONE_SIGNAL_STATE", "ONE_SIGNAL_REASON"):
        m = family_means(rows, arm, domains)
        mv = statistics.mean(m.values()) if m else 0.0
        if best_other is None or mv > best_other:
            best_other, best_name = mv, arm
    av = statistics.mean(a.values()) if a else 0.0
    return (av - best_other) * 100.0, best_name, av * 100.0, best_other * 100.0


def bootstrap_lcb(rows, n=BOOT, seed=20260825):
    """Block bootstrap over task families -- the protocol's inference unit."""
    rng = random.Random(seed)
    fams = sorted({r["family"] for r in rows})
    by_fam = defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)
    diffs = []
    for _ in range(n):
        drawn = [f for f in (rng.choice(fams) for _ in fams)]
        sample = [r for f in drawn for r in by_fam[f]]
        diffs.append(gain_points(sample)[0])
    diffs.sort()
    return diffs[int(0.025 * len(diffs))]


def main() -> int:
    rows = [json.loads(Path(f).read_text()) for f in glob.glob(str(SCORES / "*.json"))]
    if not rows:
        print("CANNOT_CHECK: no scored episodes"); return 2

    outcomes = [r["outcome"] for r in rows]
    total_positive = sum(outcomes)
    per_arm = {a: statistics.mean([r["outcome"] for r in rows if r["arm"] == a] or [0]) for a in ARMS}

    result = {
        "schema": "orion.p12.stopgo-result.v1",
        "episodes": len(rows),
        "families": len({r["family"] for r in rows}),
        "domains": sorted({r["domain"] for r in rows}),
        "model_families": sorted({r["model_family"] for r in rows}),
        "arm_mean_outcome": {a: round(v, 4) for a, v in per_arm.items()},
        "episodes_with_positive_outcome": int(total_positive),
        "diagnostics": {
            "programs_ran": sum(1 for r in rows if r.get("program_ran")),
            "produced_output": sum(1 for r in rows if r.get("produced_output")),
            "eval_ran": sum(1 for r in rows if r.get("eval_ran")),
        },
    }

    if total_positive == 0:
        result["terminal"] = "P12_STOPGO_FLOOR__GATE_NOT_APPLICABLE"
        result["reading"] = (
            "Every arm scored zero. The arms are tied because nothing was solved, "
            "not because allocation does not matter. The gate is not applied: a "
            "decision rule run on an all-zero table would report a failure it "
            "cannot distinguish from a floor, and that failure would be misread "
            "as evidence about allocation. This is a substrate/capability result, "
            "not a complementarity result."
        )
        OUT.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2)); return 0

    gain, best_other, adaptive_pts, other_pts = gain_points(rows)
    lcb = bootstrap_lcb(rows)
    doms = sorted({r["domain"] for r in rows})
    per_domain = {d: gain_points(rows, {d})[0] for d in doms}
    lodo = {d: gain_points(rows, set(doms) - {d})[0] for d in doms}
    regret = max(0.0, -min(per_domain.values()))

    checks = {
        "gain_at_least_3_points": gain >= GAIN_MIN,
        "bootstrap_lcb_above_zero": lcb > 0,
        "positive_in_at_least_two_thirds_of_domains":
            sum(1 for v in per_domain.values() if v > 0) >= (2 * len(doms) + 2) // 3,
        "positive_in_every_leave_one_domain_out": all(v > 0 for v in lodo.values()),
        "max_regret_at_most_2_points": regret <= REGRET_MAX,
    }
    passed = all(checks.values())
    result.update({
        "adaptive_points": round(adaptive_pts, 2),
        "strongest_one_signal": best_other,
        "strongest_one_signal_points": round(other_pts, 2),
        "gain_points": round(gain, 2),
        "bootstrap_lcb_points": round(lcb, 2),
        "per_domain_gain": {k: round(v, 2) for k, v in per_domain.items()},
        "leave_one_domain_out_gain": {k: round(v, 2) for k, v in lodo.items()},
        "max_regret_points": round(regret, 2),
        "gate_checks": checks,
        "terminal": "P12_STOPGO_ADAPTIVE_COMPLEMENTARITY_SUPPORTED" if passed
                    else "P12_STOPGO_BOUNDARY_NULL",
        "fail_action_if_failed": (
            "Frozen: stop the positive complementarity claim and publish a "
            "boundary/null result. Do not iterate until positive."
        ),
    })
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "per_domain_gain"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
