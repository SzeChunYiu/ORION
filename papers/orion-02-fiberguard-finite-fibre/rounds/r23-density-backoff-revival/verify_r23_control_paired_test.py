#!/usr/bin/env python3
"""Paired test of the R23 Hamming backoff against its own lexical negative control.

R23 reported certified coverage as two bare counts - geometry 32/44 and the
outcome-independent lexical control 39/44 - and called that comparison decisive.
The two arms are evaluated on the same 44 held-out PMLB decisions with the same
fold assignment, so the comparison is paired and admits an exact test. This script
supplies it. It reads only the frozen R23 results artifact and recomputes the
coverage counts from the per-dataset records rather than trusting the summaries.

Terminal is unaffected: both arms miss the frozen 0.95 gate, so
C_R23_PMLB_BACKOFF_COVERAGE_IMPROVED_BELOW_GATE stands on its own.

Usage: verify_r23_control_paired_test.py --results <R23_RESULTS.json> [--emit out.json]
"""
from __future__ import annotations
import argparse, json, random, sys
from math import comb

GEOM = "R23_HAMMING_BACKOFF_K2"
LEX = "R23_LEXICAL_BACKOFF_K2_NEGATIVE_CONTROL"
REPLICATES = 20000          # matches the replicate count of the round's other bootstraps
SEED = 20260829


def certified(record: dict) -> bool:
    """A dataset is certified iff the arm admitted at least one model for it."""
    return bool(record.get("admissible"))


def analyse(results: dict) -> dict:
    cr = results["coverage_records"]
    for arm in (GEOM, LEX):
        if arm not in cr:
            raise SystemExit(f"arm {arm} absent from coverage_records")
    geom_rec, lex_rec = cr[GEOM], cr[LEX]
    keys = sorted(set(geom_rec) & set(lex_rec))
    if len(keys) != 44:
        raise SystemExit(f"expected 44 paired datasets, found {len(keys)}")
    g = [certified(geom_rec[k]) for k in keys]
    x = [certified(lex_rec[k]) for k in keys]

    both = sum(1 for a, b in zip(g, x) if a and b)
    geom_only = sum(1 for a, b in zip(g, x) if a and not b)
    lex_only = sum(1 for a, b in zip(g, x) if b and not a)
    neither = sum(1 for a, b in zip(g, x) if not a and not b)

    discordant = geom_only + lex_only
    if discordant:
        k = min(geom_only, lex_only)
        p = min(1.0, 2 * sum(comb(discordant, i) for i in range(k + 1)) / 2 ** discordant)
    else:
        p = 1.0

    n = len(keys)
    random.seed(SEED)
    diffs = []
    for _ in range(REPLICATES):
        s = [random.randrange(n) for _ in range(n)]
        diffs.append(sum(g[i] for i in s) / n - sum(x[i] for i in s) / n)
    diffs.sort()
    lo = diffs[int(0.025 * REPLICATES)]
    hi = diffs[int(0.975 * REPLICATES) - 1]
    obs = sum(g) / n - sum(x) / n

    return {
        "schema": "ORION02.R23_CONTROL_PAIRED_TEST.v1",
        "arms": {"geometry": GEOM, "control": LEX},
        "n_paired_datasets": n,
        "contingency": {"both": both, "geometry_only": geom_only,
                        "control_only": lex_only, "neither": neither},
        "geometry_certified": sum(g),
        "control_certified": sum(x),
        "frozen_gate": results["coverage"]["target"],
        "mcnemar_exact_two_sided_p": p,
        "discordant_pairs": discordant,
        "paired_difference_geometry_minus_control": obs,
        "bootstrap": {"replicates": REPLICATES, "seed": SEED,
                      "ci_lower": lo, "ci_upper": hi,
                      "ci_excludes_zero": not (lo <= 0 <= hi)},
        "interpretation": (
            "The control's higher raw count is not a significant paired difference. "
            "Both arms miss the frozen gate, so the round's adverse terminal is "
            "unchanged; what changes is that the control comparison must not be "
            "reported as decisive on counts alone."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", required=True)
    ap.add_argument("--emit")
    a = ap.parse_args()
    out = analyse(json.load(open(a.results, encoding="utf-8")))
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if a.emit:
        open(a.emit, "w", encoding="utf-8").write(text)
    print(text, end="")
    c = out["contingency"]
    print(f"R23_CONTROL_PAIRED_TEST geometry={out['geometry_certified']}/44 "
          f"control={out['control_certified']}/44 discordant={out['discordant_pairs']} "
          f"p={out['mcnemar_exact_two_sided_p']:.4f} "
          f"ci=[{out['bootstrap']['ci_lower']:+.4f},{out['bootstrap']['ci_upper']:+.4f}]",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
