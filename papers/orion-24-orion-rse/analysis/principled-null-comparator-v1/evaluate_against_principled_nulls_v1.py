#!/usr/bin/env python3
"""ORION-24: re-evaluate the external panel against non-degenerate comparators.

The packet's only complete comparator, SYSTEMA, emits `PROMOTE` on 65 of 67 packets
(the other two are `CANNOT_CHECK`) against a gold distribution spanning eight
dispositions. Beating an always-promote system establishes very little: its 11/11 score
on `STRONG_PROMOTABLE` is what always-promote scores by construction, and its 0/56
everywhere else is the same fact seen from the other side.

That is a comparator defect, not a result. The lever is to replace it with nulls that
cannot win by construction, and to ask whether the advantage survives them.

Three nulls, none of which can see an outcome:

  ALWAYS_PROMOTE        the incumbent, kept so the change in the comparison is visible
  MARGINAL_MATCHED      samples dispositions from the gold marginal distribution, so it
                        reproduces the label frequencies exactly in expectation and can
                        only be beaten by per-item discrimination rather than by knowing
                        which labels are common
  STRATIFIED_BY_DOMAIN  per-domain majority disposition; beats MARGINAL wherever a domain
                        is skewed, so it is the harder null of the two

MARGINAL_MATCHED is stochastic, so it is evaluated over many seeds and reported as a
distribution, with a one-sided empirical p for the observed system score.

Exit codes: 0 measured · 3 CANNOT_CHECK (inputs absent)
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import random
import sys

EXIT_OK, EXIT_CANNOT_CHECK = 0, 3

BASE = "papers/orion-24-orion-rse/top_tier/external_v1"
GOLD = f"{BASE}/protected/p14_external_gold_v1.jsonl"
DECISIONS = {
    "SYSTEMA": f"{BASE}/pilot/decisions/p14_external_decisions_SYSTEMA_v1.jsonl",
    "SYSTEMB": f"{BASE}/pilot/decisions/p14_external_decisions_SYSTEMB_v1.jsonl",
}


def _repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        # .git is a directory in a normal clone and a FILE inside a git worktree.
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def load(path: str):
    if not os.path.isfile(path):
        return None
    return [json.loads(l) for l in open(path) if l.strip()]


def exact_binomial_two_sided(b: int, c: int) -> float:
    """Exact two-sided McNemar on discordant pairs, in log10 to avoid overflow."""
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
    ap.add_argument("--seeds", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260829)
    ap.add_argument("--json-out", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.smoke:
        args.seeds = 200

    root = _repo_root(os.path.dirname(os.path.abspath(__file__)))
    gold = load(os.path.join(root, GOLD))
    if not gold:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "GOLD_ABSENT"}))
        return EXIT_CANNOT_CHECK
    g = {r["packet_id"]: r for r in gold}

    systems = {}
    for name, rel in DECISIONS.items():
        rows = load(os.path.join(root, rel))
        if rows:
            systems[name] = {r["packet_id"]: r.get("disposition") for r in rows}
    if not systems:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": "NO_DECISION_FILES"}))
        return EXIT_CANNOT_CHECK

    ids = sorted(g)
    gold_disp = {p: g[p]["gold_disposition"] for p in ids}
    marg = collections.Counter(gold_disp.values())
    labels = sorted(marg)
    weights = [marg[l] for l in labels]

    # STRATIFIED_BY_DOMAIN: per-domain majority label, computed from gold only.
    by_dom = collections.defaultdict(collections.Counter)
    for p in ids:
        by_dom[g[p]["domain"]][gold_disp[p]] += 1
    dom_major = {d: c.most_common(1)[0][0] for d, c in by_dom.items()}

    def score(pred: dict) -> int:
        return sum(1 for p in ids if pred.get(p) == gold_disp[p])

    nulls = {
        "ALWAYS_PROMOTE": {p: "PROMOTE" for p in ids},
        "STRATIFIED_BY_DOMAIN": {p: dom_major[g[p]["domain"]] for p in ids},
    }

    rng = random.Random(args.seed)
    marginal_scores = []
    for _ in range(args.seeds):
        pred = {p: rng.choices(labels, weights=weights, k=1)[0] for p in ids}
        marginal_scores.append(score(pred))
    marginal_scores.sort()
    mean_marg = sum(marginal_scores) / len(marginal_scores)

    out = {
        "checker": "orion24_principled_null_comparator_v1",
        "n_packets": len(ids),
        "gold_marginal": dict(marg),
        "domain_majority": dom_major,
        "incumbent_comparator_is_degenerate": {
            "system": "SYSTEMA",
            "modal_disposition": collections.Counter(systems.get("SYSTEMA", {}).values()).most_common(1)[0]
            if "SYSTEMA" in systems else None,
            "distinct_dispositions_emitted": len(set(systems.get("SYSTEMA", {}).values()))
            if "SYSTEMA" in systems else None,
            "gold_distinct_dispositions": len(marg),
        },
        "scores": {},
        "marginal_null": {
            "seeds": args.seeds,
            "mean": mean_marg,
            "p05": marginal_scores[int(0.05 * (args.seeds - 1))],
            "p95": marginal_scores[int(0.95 * (args.seeds - 1))],
            "max": marginal_scores[-1],
        },
        "comparisons": [],
    }
    for name, pred in nulls.items():
        out["scores"][name] = score(pred)
    for name, pred in systems.items():
        out["scores"][name] = score(pred)

    for sysname, sysmap in systems.items():
        for nullname, nullpred in nulls.items():
            b = sum(1 for p in ids if sysmap.get(p) == gold_disp[p] and nullpred[p] != gold_disp[p])
            c = sum(1 for p in ids if sysmap.get(p) != gold_disp[p] and nullpred[p] == gold_disp[p])
            lg = exact_binomial_two_sided(b, c)
            out["comparisons"].append({
                "system": sysname, "null": nullname,
                "system_only_correct": b, "null_only_correct": c,
                "log10_p": lg,
                "discriminates": lg < math.log10(0.05),
                "favours": (sysname if b > c else nullname) if lg < math.log10(0.05) else None,
            })
        s = score(sysmap)
        beats = sum(1 for x in marginal_scores if x >= s)
        out["comparisons"].append({
            "system": sysname, "null": "MARGINAL_MATCHED",
            "system_score": s, "null_mean": mean_marg,
            "empirical_p_null_ge_system": beats / len(marginal_scores),
            "discriminates": beats / len(marginal_scores) < 0.05,
            "favours": sysname if beats / len(marginal_scores) < 0.05 else None,
        })

    out["status"] = "MEASURED"
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
