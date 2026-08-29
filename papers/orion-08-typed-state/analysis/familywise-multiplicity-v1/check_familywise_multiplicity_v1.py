#!/usr/bin/env python3
"""Family-wise adjustment for ORION-08's twelve paired comparisons.

The paired-uncertainty table states that its intervals are per-comparison and not
adjusted for the twelve comparisons shown, and argues one direction: any family-wise
adjustment widens intervals, so rows already containing zero continue to contain zero.
That is correct and it is only half the argument. It does not say whether the rows
that *exclude* zero still exclude it once multiplicity is charged - which is the
direction a referee asks about, because that is where the paper's positive claims live.

Per-episode differences are not published, so the bootstrap intervals cannot be
recomputed at a family-wise level. They do not need to be. The table publishes
`paired_win_fraction`, `paired_loss_fraction` and `n_pairs`, which determine an exact
two-sided sign test per comparison, and exact p-values admit exact Holm-Bonferroni
adjustment over the family.

The sign test is a different and more conservative question than the registered one:
it asks whether the direction of the paired difference is reliable, not whether the
mean difference is. It cannot upgrade a row's registered disposition and is not used
to. It answers only the multiplicity question the caption left open.

Usage: check_familywise_multiplicity_v1.py --source <PUBLICATION_PAIRED_ANALYSIS_V1.json> [--emit out.json]
"""
from __future__ import annotations
import argparse, json
from math import comb

ALPHA = 0.05


def sign_test_two_sided(wins: int, losses: int) -> float:
    """Exact two-sided sign test over discordant pairs; ties are uninformative."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def collect(studies: dict) -> list[dict]:
    found: list[dict] = []

    def walk(node, path=""):
        if isinstance(node, dict):
            if "paired_win_fraction" in node and "n_pairs" in node:
                n = node["n_pairs"]
                ci = node.get("bootstrap_95pct_ci")
                found.append({
                    "comparison": path,
                    "n_pairs": n,
                    "wins": round(node["paired_win_fraction"] * n),
                    "losses": round(node["paired_loss_fraction"] * n),
                    "ties": round(node.get("paired_tie_fraction", 0.0) * n),
                    "mean_difference": node.get("mean_difference"),
                    "bootstrap_95pct_ci": ci,
                    "ci_excludes_zero": bool(ci) and not (ci[0] <= 0 <= ci[1]),
                })
                return
            for key, value in node.items():
                walk(value, f"{path}/{key}" if path else key)

    walk(studies)
    return found


def analyse(payload: dict) -> dict:
    rows = collect(payload["studies"])
    for row in rows:
        row["sign_test_p"] = sign_test_two_sided(row["wins"], row["losses"])
    rows.sort(key=lambda r: r["sign_test_p"])
    m = len(rows)
    for i, row in enumerate(rows):
        row["holm_threshold"] = ALPHA / (m - i)
        row["survives_holm"] = row["sign_test_p"] < row["holm_threshold"]
    survivors = [r for r in rows if r["survives_holm"]]
    positives = [r for r in rows if r["ci_excludes_zero"]]
    return {
        "schema": "ORION08.FAMILYWISE_MULTIPLICITY.v1",
        "family_size": m,
        "alpha": ALPHA,
        "method": "exact two-sided sign test per comparison; Holm-Bonferroni over the family",
        "survive_holm": len(survivors),
        "ci_excluding_zero": len(positives),
        "every_ci_positive_row_survives_holm": all(r["survives_holm"] for r in positives),
        "comparisons": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--emit")
    a = ap.parse_args()
    out = analyse(json.load(open(a.source, encoding="utf-8")))
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if a.emit:
        open(a.emit, "w", encoding="utf-8").write(text)
    print(f"ORION08_FAMILYWISE m={out['family_size']} survive_holm={out['survive_holm']} "
          f"ci_positive={out['ci_excluding_zero']} "
          f"all_positives_survive={out['every_ci_positive_row_survives_holm']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
