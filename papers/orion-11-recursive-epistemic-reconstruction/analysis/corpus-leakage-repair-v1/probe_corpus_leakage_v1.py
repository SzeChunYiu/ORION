#!/usr/bin/env python3
"""Mine the ORION-11 hidden-shift suite for surface features that predict family.

`evidence/MECHANICAL_SOLVABILITY_AUDIT_V1.md` found one such feature by hand: a
regex over resource path stems, ``/(proposal|trial)/``, recovering 10 of the 11
DECOMPOSITION cases with zero false positives. A hand-found probe answers
"is this feature diagnostic?" but not "which features are?", and a repair aimed
at the one probe anybody happened to write is a repair aimed at the wrong thing.

So this enumerates the feature space instead. Everything here reads only what a
`PublicView` exposes -- `case_id`, `public_prompt`, `observable_resources`,
`budget_class` -- because that is what a blind responder sees. `task_family` and
`protected_gold` are read only to score, never to build a feature.

**Why a shuffle null is mandatory here.** With 66 cases, 11 per family, and
thousands of candidate features, perfect precision is cheap: any token appearing
in exactly two cases that happen to share a family scores 1.00. Reporting those
as leakage would bury the real finding in noise, and would make any repair look
successful merely by moving tokens around. Every run therefore re-mines the same
feature space against shuffled family labels and reports how many features clear
the same bar by chance. A repair has only worked when the observed count falls
into that null distribution.

Reported features are additionally required to clear a recall floor. A feature
firing on two of eleven cases is not a shortcut a responder could exploit even
at precision 1.00; it is an accident of vocabulary.

Exit codes: ``0`` no feature clears the bar, ``1`` at least one does (leakage
present), ``3`` the corpus could not be read.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

SHORT_FAMILY = {
    "evidence_only_negative_control": "EVID",
    "execution_only_negative_control": "EXEC",
    "hidden_decomposition_or_interface": "DECOMP",
    "hidden_measurement_or_operationalization": "MEAS",
    "hidden_parent_domain": "PARENT",
    "hidden_representation_or_coordinate_system": "REPR",
}

#: Splitting a path on these gives the tokens a filename glob can key on.
TOKEN_SPLIT = re.compile(r"[/\-_.:\s]+")

#: An `observable_resources` entry is "<path> <em dash> <description>". Only the
#: path is a surface feature; the description is content a responder must read.
EM_DASH = "—"


def load_from_cases(root: Path) -> list[dict]:
    """Read the live corpus: one JSON per case under pilot/ and test/."""
    records = []
    for split in ("pilot", "test"):
        directory = root / split
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            family = SHORT_FAMILY.get(payload["task_family"])
            if family is None:
                raise SystemExit(f"unknown task_family in {path}: {payload['task_family']}")
            records.append({
                "case_id": payload["case_id"],
                "family": family,
                "prompt": payload.get("public_prompt", ""),
                "paths": [r.split(EM_DASH)[0].strip() for r in payload["observable_resources"]],
                "budget": payload.get("budget_class", ""),
            })
    return records


def load_from_audit(path: Path) -> list[dict]:
    """Read the pre-repair snapshot the audit itself graded.

    The audit JSON stores each case's resource lines as "R<n> <path> '<text>'",
    so the paths it actually scored are recoverable. That makes the baseline a
    reproduction of the audited bytes rather than a reconstruction from history,
    which matters because the live corpus has since been renamed.
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for case in payload["cases"]:
        paths = []
        for line in case["resource_lines"]:
            match = re.match(r"^R\d+\s+(\S+)", line)
            if match:
                paths.append(match.group(1))
        records.append({
            "case_id": case["case_id"],
            "family": case["gold_family"],
            "prompt": "",  # the audit deliberately did not freeze prompts; see its note
            "paths": paths,
            "budget": "",
        })
    return records


#: Set by --paths-only. The audit did not freeze `public_prompt` (a concurrent
#: agent was rewording prompts throughout), so the pre-repair snapshot carries
#: paths and nothing else. Comparing a prompt-inclusive "after" against a
#: paths-only "before" would credit the repair with removing features the
#: baseline never had the chance to exhibit, so the comparison run is restricted
#: to the subspace both sides actually share.
PATHS_ONLY = False


def features(record: dict) -> set[str]:
    """Every surface feature this case exhibits. No description text is read."""
    found: set[str] = set()
    paths = record["paths"]

    for path in paths:
        for token in TOKEN_SPLIT.split(path.lower()):
            if token:
                found.add(f"path_token:{token}")
        if "." in path.rsplit("/", 1)[-1]:
            found.add("ext:" + path.rsplit(".", 1)[-1].lower())
        if path.startswith("closure:"):
            found.add("has_closure_resource")

    # Ordering: a responder can read position without reading content.
    if paths:
        for token in TOKEN_SPLIT.split(paths[0].lower()):
            if token:
                found.add(f"first_path_token:{token}")
        for token in TOKEN_SPLIT.split(paths[-1].lower()):
            if token:
                found.add(f"last_path_token:{token}")

    # Counting features, as thresholds so a single count cannot hide a trend.
    n_res = len(paths)
    n_closure = sum(1 for p in paths if p.startswith("closure:"))
    max_depth = max((p.count("/") for p in paths), default=0)
    for k in range(0, 13):
        if n_res >= k:
            found.add(f"n_resources>={k}")
        if n_res <= k:
            found.add(f"n_resources<={k}")
        if n_closure >= k:
            found.add(f"n_closure>={k}")
    for k in range(0, 5):
        if max_depth >= k:
            found.add(f"max_path_depth>={k}")

    prompt = "" if PATHS_ONLY else record["prompt"]
    if prompt:
        for word in re.findall(r"[a-z']+", prompt.lower()):
            found.add(f"prompt_word:{word}")
        words = len(prompt.split())
        for k in range(0, 210, 10):
            if words >= k:
                found.add(f"prompt_words>={k}")
            if words <= k:
                found.add(f"prompt_words<={k}")
    if record["budget"]:
        found.add(f"budget:{record['budget']}")
    return found


def hypergeom_sf(hits: int, fires: int, family_size: int, total: int) -> float:
    """P(at least `hits` of `fires` land in the family) under random assignment."""
    denominator = math.comb(total, fires)
    upper = min(family_size, fires)
    tail = sum(
        math.comb(family_size, i) * math.comb(total - family_size, fires - i)
        for i in range(hits, upper + 1)
    )
    return tail / denominator


def mine(records: list[dict], families: list[str], *, min_precision: float,
         min_recall: float) -> tuple[list[dict], int]:
    """Every (feature, family) pair clearing both floors, plus the space size."""
    total = len(records)
    per_case = [features(r) for r in records]
    universe: set[str] = set()
    for item in per_case:
        universe |= item
    by_family = {f: sum(1 for r in records if r["family"] == f) for f in families}

    fires_index: dict[str, list[int]] = defaultdict(list)
    for index, item in enumerate(per_case):
        for name in item:
            fires_index[name].append(index)

    results = []
    for name in sorted(universe):
        indices = fires_index[name]
        fires = len(indices)
        if fires == 0:
            continue
        counts: dict[str, int] = defaultdict(int)
        for i in indices:
            counts[records[i]["family"]] += 1
        for family in families:
            hits = counts.get(family, 0)
            if hits == 0:
                continue
            precision = hits / fires
            recall = hits / by_family[family]
            if precision < min_precision or recall < min_recall:
                continue
            results.append({
                "feature": name,
                "family": family,
                "true_positives": hits,
                "false_positives": fires - hits,
                "false_negatives": by_family[family] - hits,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "p_value": hypergeom_sf(hits, fires, by_family[family], total),
                "cases": [records[i]["case_id"] for i in indices
                          if records[i]["family"] == family],
            })
    results.sort(key=lambda r: (-r["recall"], -r["precision"], r["feature"]))
    return results, len(universe)


def mine_disjunctions(records: list[dict], families: list[str], *, min_precision: float,
                      min_recall: float, min_support: int = 2) -> list[dict]:
    """Greedy unions of same-family features -- the shape real leakage takes.

    The audit's own probe is ``/(proposal|trial)/``: two tokens, neither of which
    reaches recall 0.5 alone (5 and 5 of 11), whose union reaches 0.91. Mining
    single features therefore misses it entirely, and a first version of this
    script duly reported the known-leaking corpus clean. A naming *convention*
    spread over several words is the normal case, not the exception, so the
    disjunction is the unit that has to be searched.

    Members must fire on at least `min_support` cases: a token appearing in one
    case has precision 1.00 by construction and unions of singletons would
    reconstruct the family list one case at a time, which measures nothing.
    """
    total = len(records)
    per_case = [features(r) for r in records]
    by_family = {f: sum(1 for r in records if r["family"] == f) for f in families}

    out = []
    for family in families:
        members = []
        for name in sorted({n for item in per_case for n in item}):
            fires = [i for i, item in enumerate(per_case) if name in item]
            hits = [i for i in fires if records[i]["family"] == family]
            if len(fires) >= min_support and len(hits) / len(fires) >= min_precision:
                members.append((name, set(fires), set(hits)))
        members.sort(key=lambda m: -len(m[2]))

        chosen: list[str] = []
        union_fires: set[int] = set()
        union_hits: set[int] = set()
        for name, fires, hits in members:
            new_fires = union_fires | fires
            new_hits = union_hits | hits
            if not new_fires:
                continue
            if len(new_hits) / len(new_fires) >= min_precision and len(new_hits) > len(union_hits):
                chosen.append(name)
                union_fires, union_hits = new_fires, new_hits
        if not chosen or not union_fires:
            continue
        precision = len(union_hits) / len(union_fires)
        recall = len(union_hits) / by_family[family]
        if precision < min_precision or recall < min_recall:
            continue
        out.append({
            "rule": " OR ".join(chosen),
            "members": chosen,
            "family": family,
            "true_positives": len(union_hits),
            "false_positives": len(union_fires) - len(union_hits),
            "false_negatives": by_family[family] - len(union_hits),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "p_value": hypergeom_sf(len(union_hits), len(union_fires),
                                    by_family[family], total),
            "cases": sorted(records[i]["case_id"] for i in union_hits),
        })
    out.sort(key=lambda r: (-r["recall"], -r["precision"]))
    return out


def shuffle_null(records: list[dict], families: list[str], *, min_precision: float,
                 min_recall: float, trials: int, seed: int) -> dict:
    """How many features clear the bar when the labels carry no information.

    Same feature space, same floors, family labels permuted. Without this the
    count of surviving features is uninterpretable: it is not obvious from the
    outside whether 30 perfect-precision features means a leaking corpus or an
    over-eager miner.
    """
    rng = random.Random(seed)
    labels = [r["family"] for r in records]
    counts = []
    disjunction_counts = []
    for _ in range(trials):
        rng.shuffle(labels)
        shuffled = [dict(r, family=labels[i]) for i, r in enumerate(records)]
        found, _ = mine(shuffled, families, min_precision=min_precision,
                        min_recall=min_recall)
        counts.append(len(found))
        disjunction_counts.append(len(mine_disjunctions(
            shuffled, families, min_precision=min_precision, min_recall=min_recall)))
    counts.sort()
    disjunction_counts.sort()
    return {
        "trials": trials,
        "seed": seed,
        "single": {
            "mean": round(sum(counts) / len(counts), 3),
            "max": counts[-1],
            "p95": counts[min(len(counts) - 1, int(0.95 * len(counts)))],
        },
        "disjunction": {
            "mean": round(sum(disjunction_counts) / len(disjunction_counts), 3),
            "max": disjunction_counts[-1],
            "p95": disjunction_counts[min(len(disjunction_counts) - 1,
                                          int(0.95 * len(disjunction_counts)))],
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--cases-root", type=Path, help="directory holding pilot/ and test/")
    source.add_argument("--audit-json", type=Path, help="pre-repair snapshot to reproduce")
    parser.add_argument("--label", default="", help="name for this run in the output")
    parser.add_argument("--min-precision", type=float, default=0.9)
    parser.add_argument("--min-recall", type=float, default=0.5)
    parser.add_argument("--null-trials", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260829)
    parser.add_argument("--out", type=Path, help="write the full report here")
    parser.add_argument("--paths-only", action="store_true",
                        help="ignore prompt features, for comparison against the "
                             "audit snapshot which did not freeze prompts")
    arguments = parser.parse_args(argv)

    global PATHS_ONLY
    PATHS_ONLY = arguments.paths_only

    try:
        if arguments.cases_root:
            records = load_from_cases(arguments.cases_root)
        else:
            records = load_from_audit(arguments.audit_json)
    except (OSError, ValueError, KeyError) as error:
        print(f"CANNOT_CHECK: {error}", file=sys.stderr)
        return 3
    if not records:
        print("CANNOT_CHECK: no cases loaded", file=sys.stderr)
        return 3

    families = sorted({r["family"] for r in records})
    leaks, space = mine(records, families, min_precision=arguments.min_precision,
                        min_recall=arguments.min_recall)
    rules = mine_disjunctions(records, families, min_precision=arguments.min_precision,
                              min_recall=arguments.min_recall)
    null = shuffle_null(records, families, min_precision=arguments.min_precision,
                        min_recall=arguments.min_recall,
                        trials=arguments.null_trials, seed=arguments.seed)

    leaking = len(leaks) > null["single"]["max"] or len(rules) > null["disjunction"]["max"]
    report = {
        "label": arguments.label,
        "source": str(arguments.cases_root or arguments.audit_json),
        "cases": len(records),
        "families": {f: sum(1 for r in records if r["family"] == f) for f in families},
        "feature_space_size": space,
        "floors": {"min_precision": arguments.min_precision,
                   "min_recall": arguments.min_recall},
        "single_features_clearing_floors": len(leaks),
        "disjunction_rules_clearing_floors": len(rules),
        "shuffle_null": null,
        "verdict": "LEAKING" if leaking else "WITHIN_NULL",
        "features": leaks,
        "disjunction_rules": rules,
    }
    if arguments.out:
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")
    print(f"{arguments.label or arguments.source}: {len(records)} cases, "
          f"{space} candidate features")
    print(f"  single    : {len(leaks):>3} clear floors (null mean "
          f"{null['single']['mean']}, max {null['single']['max']})")
    print(f"  disjunction: {len(rules):>3} clear floors (null mean "
          f"{null['disjunction']['mean']}, max {null['disjunction']['max']})")
    print(f"  VERDICT: {report['verdict']}")
    for item in rules:
        print(f"  RULE {item['family']:<7} p={item['precision']:.2f} "
              f"r={item['recall']:.2f} TP={item['true_positives']:<2} "
              f"FP={item['false_positives']:<2} {item['rule'][:130]}")
    for item in leaks[:15]:
        print(f"  SINGLE {item['family']:<7} p={item['precision']:.2f} "
              f"r={item['recall']:.2f} TP={item['true_positives']:<2} "
              f"FP={item['false_positives']:<2} {item['feature']}")
    if len(leaks) > 15:
        print(f"  ... {len(leaks) - 15} more single features (see --out)")
    return 1 if leaking else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
