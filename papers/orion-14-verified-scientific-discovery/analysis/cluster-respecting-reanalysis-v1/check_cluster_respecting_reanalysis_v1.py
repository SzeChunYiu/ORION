#!/usr/bin/env python3
"""Cluster-respecting reanalysis of the ORION-14 protected campaign (run 31968809206).

RUN_QUEUE item P0.3. The published H1 interval is computed over cases. This checker
asks whether the H1 effect survives when the independent unit is the attack family,
which is the unit the campaign actually randomises over.

It does four things, in order, and refuses to skip the first:

  1. Reproduces the published H1 point estimate exactly from `family_summary`.
     If the reproduction fails the checker stops: a reanalysis that cannot first
     recover the published number is not evidence about that number.
  2. MEASURES within-(system, family) verdict constancy on the case rows that carry
     a family label. This is the empirical basis for treating the family as the
     cluster. It is measured, not assumed, and its scope is reported.
  3. Runs an exact two-sided randomisation test over family-label assignment against
     the comparator the campaign artifact itself names in `strongest_frozen_comparator`.
  4. Runs a cluster bootstrap over families for an interval at the clustering unit.

Exit codes
  0  PASS           - H1 reproduced and the effect survives at the clustering unit
  1  FAIL           - H1 reproduced but the effect does not survive
  3  CANNOT_CHECK   - inputs missing/ambiguous; no clustering inferred
  4  REPRO_FAILED   - published aggregate could not be reproduced

`CANNOT_CHECK` is deliberately distinct from both PASS and FAIL: "could not check"
is not "checked and fine".
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

EXIT_PASS, EXIT_FAIL, EXIT_CANNOT_CHECK, EXIT_REPRO_FAILED = 0, 1, 3, 4

CAMPAIGN_REL = (
    "papers/orion-14-verified-scientific-discovery/evidence/"
    "protected-campaign-31968809206"
)
# CLEAN_POSITIVE is excluded from the H1 analysis set: a "false promotion" is not
# defined on a family whose correct terminal IS promotion. This exclusion is not a
# choice made here -- it is the exclusion under which the published H1 reproduces
# exactly, and step 1 fails loudly if that stops being true.
H1_EXCLUDED_FAMILIES = ("CLEAN_POSITIVE",)


def _repo_root(start: str) -> str:
    d = os.path.abspath(start)
    while d != "/":
        if os.path.isdir(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.path.abspath(start)


def _load(root: str):
    base = os.path.join(root, CAMPAIGN_REL)
    need = {
        "summary": "CAMPAIGN_SUMMARY_V1.json",
        "verdicts": "PUBLIC_CANDIDATE_VERDICTS_V1.jsonl",
        "manifest": "PUBLIC_ATTACK_MANIFEST_V1.jsonl",
    }
    missing = [v for v in need.values() if not os.path.isfile(os.path.join(base, v))]
    if missing:
        return None, missing
    summary = json.load(open(os.path.join(base, need["summary"])))
    verdicts = [
        json.loads(l) for l in open(os.path.join(base, need["verdicts"])) if l.strip()
    ]
    manifest = [
        json.loads(l) for l in open(os.path.join(base, need["manifest"])) if l.strip()
    ]
    return (summary, verdicts, manifest), []


def weighted_rate(fs, system, families, n_by_family) -> float:
    total = sum(n_by_family[f] for f in families)
    if total == 0:
        return float("nan")
    return (
        sum(n_by_family[f] * fs[system][f]["false_promotion_rate"] for f in families)
        / total
    )


def exact_two_sided_sign_p(wins: int, losses: int) -> float:
    """Exact two-sided randomisation p over discordant clusters.

    Under the null 'ORION's advantage is unrelated to which family it faces', each
    discordant family independently favours either system with probability 1/2.
    Ties carry no information about direction and are excluded, which is the
    standard exact treatment.
    """
    n = wins + losses
    if n == 0:
        return 1.0
    def comb_sum(k_lo, k_hi):
        return sum(math.comb(n, k) for k in range(k_lo, k_hi + 1))
    obs = min(wins, losses)
    tail = comb_sum(0, obs)
    return min(1.0, 2.0 * tail / (2 ** n))


def cluster_bootstrap(diffs, reps: int, seed: int):
    """Resample FAMILIES (not cases) with replacement."""
    rng = random.Random(seed)
    k = len(diffs)
    if k == 0:
        return (float("nan"), float("nan"))
    means = []
    for _ in range(reps):
        s = sum(diffs[rng.randrange(k)] for _ in range(k))
        means.append(s / k)
    means.sort()
    lo = means[int(0.025 * (reps - 1))]
    hi = means[int(0.975 * (reps - 1))]
    return lo, hi


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bootstrap-reps", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=20260829)
    ap.add_argument("--json-out", default="")
    ap.add_argument("--smoke", action="store_true", help="fast mode, 200 bootstrap reps")
    args = ap.parse_args()
    if args.smoke:
        args.bootstrap_reps = 200

    root = _repo_root(os.path.dirname(os.path.abspath(__file__)))
    loaded, missing = _load(root)
    out = {"checker": "cluster_respecting_reanalysis_v1", "campaign": "31968809206"}
    if loaded is None:
        out["status"] = "CANNOT_CHECK"
        out["reason"] = "MISSING_CAMPAIGN_INPUTS"
        out["missing"] = missing
        print(json.dumps(out, indent=2))
        return EXIT_CANNOT_CHECK

    summary, verdicts, manifest = loaded
    fs = summary["family_summary"]
    families = sorted(fs["ORION"])
    n_by_family = {f: fs["ORION"][f]["n"] for f in families}
    comparator = summary.get("strongest_frozen_comparator")
    out["strongest_frozen_comparator"] = comparator
    out["repeat_count"] = summary.get("repeat_count")
    out["case_count"] = summary.get("case_count")

    if comparator not in fs:
        out["status"] = "CANNOT_CHECK"
        out["reason"] = "NAMED_COMPARATOR_ABSENT_FROM_FAMILY_SUMMARY"
        print(json.dumps(out, indent=2))
        return EXIT_CANNOT_CHECK

    # ---- 1. reproduce the published aggregate -------------------------------
    analysis_families = [f for f in families if f not in H1_EXCLUDED_FAMILIES]
    n_analysis = sum(n_by_family[f] for f in analysis_families)
    orion_rate = weighted_rate(fs, "ORION", analysis_families, n_by_family)
    comp_rate = weighted_rate(fs, comparator, analysis_families, n_by_family)
    reproduced = orion_rate - comp_rate
    published = summary["H1"]["orion_minus_baseline_false_promotion"]
    out["reproduction"] = {
        "analysis_families": len(analysis_families),
        "excluded_families": list(H1_EXCLUDED_FAMILIES),
        "analysis_cases": n_analysis,
        "base_cases": (
            n_analysis // summary["repeat_count"] if summary.get("repeat_count") else None
        ),
        "orion_rate": orion_rate,
        "comparator_rate": comp_rate,
        "reproduced_h1": reproduced,
        "published_h1": published,
        "exact_match": abs(reproduced - published) < 1e-12,
    }
    if not out["reproduction"]["exact_match"]:
        out["status"] = "REPRO_FAILED"
        print(json.dumps(out, indent=2))
        return EXIT_REPRO_FAILED

    # ---- 2. MEASURE within-family constancy on labelled cases ---------------
    fam_of = {r["case_id"]: r["attack_family"] for r in manifest}
    cells = defaultdict(set)
    cell_n = Counter()
    for r in verdicts:
        f = fam_of.get(r["case_id"])
        if f is None:
            continue
        cells[(r["system_id"], f)].add(r["authority_terminal"])
        cell_n[(r["system_id"], f)] += 1
    nonconstant = sorted(k for k, v in cells.items() if len(v) > 1)
    labelled_cases = {r["case_id"] for r in verdicts} & set(fam_of)
    all_cases = {r["case_id"] for r in verdicts}
    out["constancy"] = {
        "labelled_cases": len(labelled_cases),
        "total_cases": len(all_cases),
        "unlabelled_cases": len(all_cases - set(fam_of)),
        "cells_measured": len(cells),
        "rows_measured": sum(cell_n.values()),
        "cells_nonconstant": len(nonconstant),
        "nonconstant_examples": [list(k) for k in nonconstant[:10]],
        "verified_scope": "labelled subset only",
        "unlabelled_disposition": "CANNOT_CHECK_DIRECT_CONSTANCY",
    }
    # Constancy failing does not stop the run; it changes what we may conclude.
    constancy_holds = len(nonconstant) == 0 and len(cells) > 0

    # ---- 3. exact randomisation test at the clustering unit -----------------
    diffs, wins, losses, ties = [], 0, 0, 0
    per_family = {}
    for f in analysis_families:
        d = fs["ORION"][f]["false_promotion_rate"] - fs[comparator][f]["false_promotion_rate"]
        diffs.append(d)
        per_family[f] = d
        if d < 0:
            wins += 1
        elif d > 0:
            losses += 1
        else:
            ties += 1
    p_exact = exact_two_sided_sign_p(wins, losses)
    out["cluster_test"] = {
        "independent_clusters": len(analysis_families),
        "discordant_clusters": wins + losses,
        "favouring_orion": wins,
        "favouring_comparator": losses,
        "tied": ties,
        "exact_two_sided_p": p_exact,
        "null": "ORION's advantage is unrelated to which attack family it faces",
        "per_family_difference": per_family,
    }

    # ---- 4. cluster bootstrap ----------------------------------------------
    lo, hi = cluster_bootstrap(diffs, args.bootstrap_reps, args.seed)
    naive_hw = 1.96 * math.sqrt(0.25 / n_analysis) if n_analysis else float("nan")
    clust_hw = 1.96 * math.sqrt(0.25 / len(analysis_families)) if analysis_families else float("nan")
    out["intervals"] = {
        "published_ci95": [summary["H1"]["ci95_low"], summary["H1"]["ci95_high"]],
        "published_half_width": (summary["H1"]["ci95_high"] - summary["H1"]["ci95_low"]) / 2,
        "case_level_normal_half_width": naive_hw,
        "cluster_level_normal_half_width": clust_hw,
        "width_ratio_cluster_over_case": (clust_hw / naive_hw) if naive_hw else None,
        "cluster_bootstrap_ci95": [lo, hi],
        "bootstrap_reps": args.bootstrap_reps,
        "bootstrap_unit": "family",
        "seed": args.seed,
    }

    # ---- disposition --------------------------------------------------------
    survives = (p_exact < 0.05) and (hi < 0.0)
    out["context"] = {
        "retained_error_case_count": summary.get("retained_error_case_count"),
        "mechanical_gold_cases": summary.get("mechanical_gold_cases"),
        "human_rubric_triggered_cases": summary.get("human_rubric_triggered_cases"),
        "note": (
            "human_rubric_triggered_cases=0 means no case in this campaign received "
            "human adjudication; every terminal is mechanical."
        ),
    }
    if not constancy_holds:
        out["status"] = "CANNOT_CHECK"
        out["reason"] = "WITHIN_FAMILY_CONSTANCY_NOT_ESTABLISHED"
        print(json.dumps(out, indent=2))
        return EXIT_CANNOT_CHECK
    out["status"] = "PASS" if survives else "FAIL"
    out["conclusion"] = (
        "H1 retains sign and direction at the clustering unit"
        if survives
        else "H1 does not survive at the clustering unit"
    )
    print(json.dumps(out, indent=2))
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
            fh.write("\n")
    return EXIT_PASS if survives else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
