#!/usr/bin/env python3
"""ORION-05 V2 Stage 1: same-domain positive-control discovery.

Protocol: ORION05.GLOBAL_OBSTRUCTION_BASIS.v2, stage_1_positive_control_discovery.

Domain: lexicographic combinations_with_replacement of six codes from 1..15,
excluding the 5,005 all-distinct sets -> 33,755 repeated-target multisets. The
confirmatory 5,005-row distinct-target domain is deliberately NOT touched here.

Estimand: minimum cost over all 15 perfect matchings of the six target slots, at
max_support=1 (C1) and max_support=2 (C2). Gap = C1 - C2. That is exactly what
solve_six_targets computes; it enumerates perfect_matchings internally.

Selection rule: scan in lexicographic order and record the first three instances
with C1 > C2. No manual substitution. If fewer than three exist the terminal is
CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS and confirmation must not run.

This also discriminates two of the registered theory candidates: a domain-wide
absence of gaps supports O05-C2 (relaxation law) and falsifies O05-C3
(gap-preservation class); any surviving gaps are C3's candidate class.

HARD CONSTRAINT (inherited from the v1 compute plan): no control or census
solve runs on the Mac. Local use is limited to --smoke, which performs zero
solver instances. Every solving mode here is LUNARC-only.
"""

from __future__ import annotations
import argparse, json, sys, time
from itertools import combinations_with_replacement

SOLVER_REL = "papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py"


def _load_solver(repo_root: str):
    """Import the paper's own solver. Deliberately lazy: --smoke must not need it."""
    import importlib.util
    from pathlib import Path as _P
    path = _P(repo_root) / SOLVER_REL
    if not path.is_file():
        raise SystemExit(f"solver not found at {path}; pass --repo-root")
    spec = importlib.util.spec_from_file_location("orion05_solver", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["orion05_solver"] = mod
    spec.loader.exec_module(mod)
    return mod

# The 15 non-identity two-qubit Pauli codes, in the production convention:
# a dense Pauli is a pair of local codes (0=I,1=X,2=Y,3=Z); code index 1..15
# enumerates the non-identity pairs in lexicographic order.
CODES = [(a, b) for a in range(4) for b in range(4)][1:]
assert len(CODES) == 15


def solve(mod, targets):
    _, w1 = mod.solve_six_targets(targets, max_support=1)
    _, w2 = mod.solve_six_targets(targets, max_support=2)
    return w1.cost, w2.cost


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="stop after N candidates (0 = whole domain)")
    ap.add_argument("--emit", default="STAGE1_RESULT.json")
    ap.add_argument("--progress", type=int, default=200)
    ap.add_argument("--smoke", action="store_true",
                    help="enumeration and binding checks only; performs ZERO solves (safe anywhere)")
    ap.add_argument("--start", type=int, default=0, help="lexicographic index to resume from")
    ap.add_argument("--repo-root", default=".")
    a = ap.parse_args()

    if a.smoke:
        total = sum(1 for _ in combinations_with_replacement(range(1, 16), 6))
        distinct = sum(1 for c in combinations_with_replacement(range(1, 16), 6) if len(set(c)) == 6)
        rep = total - distinct
        ok = (len(CODES) == 15 and total == 38760 and distinct == 5005 and rep == 33755)
        print(json.dumps({"mode": "smoke", "solves_performed": 0, "codes": len(CODES),
                          "domain_total": total, "all_distinct_excluded": distinct,
                          "repeated_target_domain": rep, "matches_protocol_33755": rep == 33755,
                          "enumeration_ok": ok}, indent=2))
        return 0 if ok else 1

    mod = _load_solver(a.repo_root)
    positives, scanned, skipped_distinct = [], 0, 0
    gap_hist = {}
    t0 = time.time()
    for combo in combinations_with_replacement(range(1, 16), 6):
        if len(set(combo)) == 6:
            skipped_distinct += 1
            continue
        targets = [list(CODES[c - 1]) for c in combo]
        c1, c2 = solve(mod, targets)
        scanned += 1
        gap = c1 - c2
        gap_hist[gap] = gap_hist.get(gap, 0) + 1
        if gap > 0:
            positives.append({"codes": list(combo), "targets": targets, "c1": c1, "c2": c2, "gap": gap,
                              "lex_index": scanned})
        if a.progress and scanned % a.progress == 0:
            el = time.time() - t0
            print(f"  scanned {scanned} in {el:.0f}s ({scanned/el:.0f}/s) positives={len(positives)}", flush=True)
        if a.limit and scanned >= a.limit:
            break

    elapsed = time.time() - t0
    terminal = ("SAME_DOMAIN_POSITIVE_CONTROLS_FOUND" if len(positives) >= 3
                else "CANNOT_CHECK_NO_SAME_DOMAIN_POSITIVE_CONTROLS")
    out = {
        "schema": "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage1",
        "estimand": "min cost over all 15 perfect matchings; gap = C1 - C2",
        "domain": "combinations_with_replacement(1..15, 6) excluding all-distinct",
        "domain_size_expected": 33755,
        "scanned": scanned,
        "skipped_all_distinct": skipped_distinct,
        "complete": not a.limit,
        "positives_found": len(positives),
        "first_three_positives": positives[:3],
        "all_positives": positives,
        "gap_histogram": {str(k): v for k, v in sorted(gap_hist.items())},
        "terminal": terminal,
        "elapsed_seconds": round(elapsed, 1),
        "theory_reading": (
            "no positive gap anywhere in the repeated-target domain supports O05-C2 "
            "(matching relaxation erases the historical gaps) and falsifies O05-C3 "
            "(gap-preservation class); any positives are C3's candidate class"
        ),
    }
    with open(a.emit, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in
                      ("scanned", "skipped_all_distinct", "positives_found", "terminal", "elapsed_seconds")}, indent=2))
    print("gap histogram:", out["gap_histogram"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
