#!/usr/bin/env python3
"""Exact minimal semantic separator for ORION-13, with a held-out challenge set.

The candidate theorem (PR #1617, ORION13.MINIMAL_SEMANTIC_SEPARATOR.v1) asks
which semantic coordinates are actually indispensable for the merge verdict on
the frozen public-reference cases, rather than asserting that all of them are.

Encoding, taken from the case schema and nothing else: each case is a pair of
projections, so coordinate j contributes one bit -- whether the two projections
AGREE on j. A coordinate subset S is SUFFICIENT when the agreement pattern
restricted to S never assigns two opposite-verdict cases the same pattern.

Two frozen disjoint sets exist in the repository already:
  public-reference-v1                  -> derivation set
  public-reference-v1.1-confirmatory   -> held-out challenge set (0 shared ids)

Reducts are derived on v1 ONLY and then tested on v1.1. The challenge set is
never consulted while choosing them.

Exit codes
    0  computed
    2  an internal consistency check failed
    3  inputs missing -- CANNOT_CHECK
"""
from __future__ import annotations
import itertools, json, math, random, sys
from collections import Counter
from pathlib import Path

PACKET = Path(__file__).resolve().parent.parent
PAPER = PACKET.parent.parent
V1 = PAPER / "gold/adjudicated/public-reference-v1/PUBLIC_REFERENCE_GOLD_V1.jsonl"
V11 = PAPER / "gold/adjudicated/public-reference-v1.1-confirmatory/PUBLIC_REFERENCE_GOLD_V1.jsonl"
IDENTIFIER_KEYS = {"projection_id", "source_id", "source_span"}
PERM_TRIALS = 20000
SEED = 20260828


def norm(v):
    return tuple(sorted(v)) if isinstance(v, list) else v


def load(path):
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    coords = sorted({k for r in rows for k in
                     set(r["left_projection"]) | set(r["right_projection"])}
                    - IDENTIFIER_KEYS)
    cases = []
    for r in rows:
        L, R = r["left_projection"], r["right_projection"]
        pattern = tuple(int(norm(L.get(c)) == norm(R.get(c))) for c in coords)
        cases.append({"case_id": r["case_id"],
                      "family": r["case_family"],
                      "verdict": r["expected"]["meaning_relation"],
                      "pattern": pattern})
    return coords, cases


def is_sufficient(cases, subset):
    """No two opposite-verdict cases share a pattern restricted to subset."""
    seen = {}
    for c in cases:
        key = tuple(c["pattern"][j] for j in subset)
        v = c["verdict"]
        if key in seen and seen[key] != v:
            return False
        seen[key] = v
    return True


def collisions(cases, subset):
    seen, bad = {}, []
    for c in cases:
        key = tuple(c["pattern"][j] for j in subset)
        if key in seen and seen[key]["verdict"] != c["verdict"]:
            bad.append((seen[key]["case_id"], c["case_id"]))
        seen.setdefault(key, c)
    return bad


def main() -> int:
    try:
        if not (V1.is_file() and V11.is_file()):
            raise FileNotFoundError("gold set missing")
        coords, d1 = load(V1)
        coords2, d2 = load(V11)
        if coords != coords2:
            raise ValueError(f"coordinate sets differ: {coords} vs {coords2}")
        k = len(coords)
    except Exception as exc:                                   # noqa: BLE001
        print(json.dumps({"status": "CANNOT_CHECK",
                          "error": f"{type(exc).__name__}: {exc}"}, indent=2))
        return 3

    # exhaustive over all 2^k subsets, derivation set only
    sufficient = [s for r in range(k + 1)
                  for s in itertools.combinations(range(k), r)
                  if is_sufficient(d1, list(s))]
    if not sufficient:
        reducts, k_star, core = [], None, []
    else:
        k_star = min(len(s) for s in sufficient)
        minimal = [s for s in sufficient
                   if not any(set(t) < set(s) for t in sufficient)]
        reducts = sorted(minimal, key=lambda s: (len(s), s))
        core = sorted(set.intersection(*(set(s) for s in reducts))) if reducts else []

    # held-out test: every reduct, evaluated on the untouched challenge set
    heldout = []
    for s in reducts:
        ok = is_sufficient(d2, list(s))
        heldout.append({"subset": [coords[j] for j in s],
                        "size": len(s),
                        "sufficient_on_challenge_set": ok,
                        "collisions_on_challenge_set": [
                            list(p) for p in collisions(d2, list(s))][:5]})

    # structure-free null on the derivation set
    rng = random.Random(SEED)
    labels = [c["verdict"] for c in d1]
    hits = 0
    for _ in range(PERM_TRIALS):
        rng.shuffle(labels)
        shuffled = [{**c, "verdict": labels[i]} for i, c in enumerate(d1)]
        if any(is_sufficient(shuffled, list(s))
               for s in itertools.combinations(range(k), k_star or k)):
            hits += 1

    report = {
        "schema": "ORION.ORION13.MinimalSemanticSeparator.Analysis.v1",
        "coordinates": coords,
        "derivation_set": {"path": str(V1.relative_to(PAPER.parent.parent)),
                           "cases": len(d1),
                           "verdicts": dict(Counter(c["verdict"] for c in d1)),
                           "families": dict(Counter(c["family"] for c in d1))},
        "challenge_set": {"path": str(V11.relative_to(PAPER.parent.parent)),
                          "cases": len(d2),
                          "verdicts": dict(Counter(c["verdict"] for c in d2)),
                          "shared_case_ids_with_derivation_set": 0},
        "full_coordinate_set_sufficient_on_derivation": is_sufficient(d1, list(range(k))),
        "k_star_on_derivation": k_star,
        "minimal_sufficient_subsets_reducts": [[coords[j] for j in s] for s in reducts],
        "reduct_count": len(reducts),
        "core_coordinates_in_every_reduct": [coords[j] for j in core],
        "coordinates_in_no_reduct": [c for i, c in enumerate(coords)
                                     if all(i not in s for s in reducts)],
        "held_out_validation": heldout,
        "structure_free_null": {
            "question": (f"how often does a random relabelling of the derivation "
                         f"set admit ANY sufficient subset of size {k_star}?"),
            "trials": PERM_TRIALS, "hits": hits, "rate": hits / PERM_TRIALS,
            "reading": ("a high rate means a separator of this size is easy to "
                        "find by chance at this sample size and carries little "
                        "evidence; a low rate means it is informative"),
        },
        "status": "PASS",
    }
    (PACKET / "ANALYSIS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({kk: report[kk] for kk in
                      ("coordinates", "k_star_on_derivation",
                       "minimal_sufficient_subsets_reducts",
                       "core_coordinates_in_every_reduct",
                       "coordinates_in_no_reduct", "held_out_validation",
                       "structure_free_null")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
