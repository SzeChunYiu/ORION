#!/usr/bin/env python3
"""Do ORION-11's ablation arms actually discriminate, and on which outcome?

The concern this answers is that the costed-ordering comparisons "cannot distinguish
full ORION from the comparator" and that "several ablations behave identically". Both are
measurable from the emitted per-run traces rather than argued, so this measures them.

Three things, in order:

  1. BEHAVIOURAL identity. Two arms that emit the same ordered action sequence on the same
     (world, seed, stratum) are behaviourally inert with respect to each other, and no
     outcome measure can separate them. Costs are excluded from the fingerprint so that
     float noise cannot manufacture a difference.
  2. Discrimination on RAW SUCCESS (`protected_root_task_success`).
  3. Discrimination on the protocol's FROZEN PRIMARY CRITERION, which PROTOCOL.json
     defines as `protected_root_task_success AND NOT forbidden_high_level_mutation`.

Steps 2 and 3 disagree sharply, and that disagreement is the point: raw success ignores
the constraint the method exists to enforce, so arms that violate it in a third to a half
of runs appear to win. The criterion used here is not chosen by this script — it is read
from the frozen protocol.

Exact two-sided McNemar on discordant pairs, computed in log space so that n in the
thousands does not overflow.

Exit codes: 0 measured · 3 CANNOT_CHECK (inputs absent)
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import math
import os
import sys

EXIT_OK, EXIT_CANNOT_CHECK = 0, 3

EXP = ("papers/orion-11-recursive-epistemic-reconstruction/"
       "experiments/costed-ordering-v1")
ORION = "orion_level_monotone"


def _repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def load_traces(root: str):
    p = os.path.join(root, EXP, "raw_traces.jsonl.gz")
    if not os.path.isfile(p):
        return None
    with gzip.open(p, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def primary_criterion(root: str) -> str | None:
    p = os.path.join(root, EXP, "PROTOCOL.json")
    if not os.path.isfile(p):
        return None
    d = json.load(open(p))
    pc = d.get("primary_criterion")
    if isinstance(pc, dict):
        return pc.get("definition")
    return pc if isinstance(pc, str) else None


def trace_sig(r) -> str | None:
    a = r.get("actions")
    if a is None:
        return None
    seq = [(x.get("kind"), x.get("target"), x.get("level")) for x in a]
    return hashlib.sha256(json.dumps(seq, sort_keys=True).encode()).hexdigest()[:16]


def log10_mcnemar(b: int, c: int) -> float:
    """log10 of the exact two-sided McNemar p on b+c discordant pairs."""
    n = b + c
    if n == 0:
        return 0.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1))
    if tail <= 0:
        return float("-inf")
    return min(0.0, math.log10(2 * tail) - n * math.log10(2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    root = _repo_root(os.path.dirname(os.path.abspath(__file__)))
    rows = load_traces(root)
    if not rows:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "RAW_TRACES_ABSENT"}))
        return EXIT_CANNOT_CHECK
    if args.smoke:
        rows = rows[:2000]

    crit = primary_criterion(root)
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["world_id"], r["seed"], r["stratum"])][r["arm_id"]] = r

    def raw(r):
        return bool(r["protected_root_task_success"])

    def joint(r):
        return bool(r["protected_root_task_success"]) and not bool(
            r["forbidden_high_level_mutation"]
        )

    arms = sorted({r["arm_id"] for r in rows})
    profile = {}
    for a in arms:
        rs = [r for r in rows if r["arm_id"] == a]
        profile[a] = {
            "n": len(rs),
            "raw_success_rate": sum(raw(r) for r in rs) / len(rs),
            "forbidden_rate": sum(bool(r["forbidden_high_level_mutation"]) for r in rs) / len(rs),
            "joint_clear_rate": sum(joint(r) for r in rs) / len(rs),
        }

    comparisons = []
    for a in arms:
        if a == ORION:
            continue
        n = same_trace = 0
        stats = {}
        for outcome_name, fn in (("raw_success", raw), ("frozen_primary", joint)):
            ow = cw = 0
            for _k, d in by.items():
                if ORION not in d or a not in d:
                    continue
                o, c = fn(d[ORION]), fn(d[a])
                if o and not c:
                    ow += 1
                elif c and not o:
                    cw += 1
            lg = log10_mcnemar(ow, cw)
            stats[outcome_name] = {
                "discordant": ow + cw,
                "orion_better": ow,
                "comparator_better": cw,
                "log10_p": lg,
                "discriminates": lg < math.log10(0.05),
                "favours": ("ORION" if ow > cw else "COMPARATOR") if lg < math.log10(0.05) else None,
            }
        for _k, d in by.items():
            if ORION not in d or a not in d:
                continue
            n += 1
            t1, t2 = trace_sig(d[ORION]), trace_sig(d[a])
            if t1 is not None and t1 == t2:
                same_trace += 1
        comparisons.append({
            "comparator": a,
            "paired_cases": n,
            "identical_action_trace_rate": (same_trace / n) if n else None,
            "behaviourally_inert": bool(n and same_trace == n),
            "outcomes": stats,
        })

    prim = [c for c in comparisons if c["outcomes"]["frozen_primary"]["discriminates"]]
    out = {
        "checker": "orion11_discriminating_power_v1",
        "frozen_primary_criterion": crit,
        "rows": len(rows),
        "arms": len(arms),
        "paired_cases": len(by),
        "arm_profile": profile,
        "comparisons": comparisons,
        "summary": {
            "behaviourally_inert_arms": [c["comparator"] for c in comparisons if c["behaviourally_inert"]],
            "discriminating_on_raw_success": sum(
                1 for c in comparisons if c["outcomes"]["raw_success"]["discriminates"]),
            "discriminating_on_frozen_primary": len(prim),
            "frozen_primary_favouring_orion": sum(
                1 for c in prim if c["outcomes"]["frozen_primary"]["favours"] == "ORION"),
            "total_comparisons": len(comparisons),
        },
        "status": "MEASURED",
    }
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
