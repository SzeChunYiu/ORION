#!/usr/bin/env python3
"""Lane B: the deterministic instrument for the public prospective series.

Frozen BEFORE any Lane A diagnosis is written and before any outcome exists.
Lane B is a rule set over typed observations, exactly as
`instances/Q3-R1-QG19/LANE_B_MANIFEST.json` specifies for the internal series
(`rule_set: q3_replacement_controller.py::decide`). It never sees free text, a
prediction, or an outcome -- only the typed fields below.

The point of the paper is that Lane A (an LLM host diagnosis) and Lane B (this
rule set) are genuinely different instruments. So this file contains no learned
parameters and no appeal to a model: every threshold is a stated integer, chosen
before the packets were built, and each is justified in the protocol rather than
tuned against results that do not yet exist.
"""
from __future__ import annotations

from typing import Any

SCHEMA = "ORIONQ.Q3PublicLaneBController.v1"

#: Frozen thresholds. Chosen before any packet was scored; see PROTOCOL_V2.md.
STALE_DAYS = 90          # an open PR older than this is treated as drifting
LARGE_CHANGED_FILES = 20  # broad diffs need more coordination to land
LARGE_LINES = 500

#: Allowed verdicts. Three-valued on purpose: "still open at the horizon" is a
#: real outcome and must not be collapsed into "not merged".
VERDICTS = ("PREDICT_MERGED", "PREDICT_CLOSED_UNMERGED", "PREDICT_UNRESOLVED_AT_HORIZON")


def decide(obs: dict[str, Any]) -> dict[str, Any]:
    """Map typed observations to one verdict plus the rules that fired.

    Deterministic and total: every input yields a verdict and a rule trace, so a
    disagreement with Lane A is always attributable to a named rule.
    """
    age = int(obs["age_days_at_freeze"])
    files = int(obs["changed_files"])
    lines = int(obs["additions"]) + int(obs["deletions"])

    fired: list[str] = []

    stale = age > STALE_DAYS
    broad = files > LARGE_CHANGED_FILES or lines > LARGE_LINES
    tiny = files <= 2 and lines <= 50

    if stale:
        fired.append(f"R1_STALE(age={age}>{STALE_DAYS})")
    if broad:
        fired.append(f"R2_BROAD(files={files},lines={lines})")
    if tiny:
        fired.append(f"R3_TINY(files={files},lines={lines})")

    # R4 dominance order, frozen: staleness dominates size, and a broad diff on a
    # stale PR is the least likely thing to land. A tiny fresh diff is the most.
    if stale and broad:
        verdict = "PREDICT_UNRESOLVED_AT_HORIZON"
        fired.append("R4_STALE_AND_BROAD->UNRESOLVED")
    elif stale:
        verdict = "PREDICT_UNRESOLVED_AT_HORIZON"
        fired.append("R4_STALE->UNRESOLVED")
    elif tiny:
        verdict = "PREDICT_MERGED"
        fired.append("R4_TINY_AND_FRESH->MERGED")
    elif broad:
        verdict = "PREDICT_UNRESOLVED_AT_HORIZON"
        fired.append("R4_BROAD_AND_FRESH->UNRESOLVED")
    else:
        verdict = "PREDICT_MERGED"
        fired.append("R4_DEFAULT_MODERATE_FRESH->MERGED")

    assert verdict in VERDICTS
    return {
        "schema": SCHEMA,
        "verdict": verdict,
        "rules_fired": fired,
        "typed_observations_used": {
            "age_days_at_freeze": age,
            "changed_files": files,
            "total_lines": lines,
        },
        "scientific_outcome_accessed": False,
    }


def self_test() -> dict[str, Any]:
    """Discrimination probes. A controller that always says one thing is useless,
    so prove it separates before it is used on anything."""
    cases = [
        ({"age_days_at_freeze": 5, "changed_files": 1, "additions": 3, "deletions": 1},
         "PREDICT_MERGED", "tiny and fresh"),
        ({"age_days_at_freeze": 400, "changed_files": 1, "additions": 3, "deletions": 1},
         "PREDICT_UNRESOLVED_AT_HORIZON", "stale dominates tiny"),
        ({"age_days_at_freeze": 5, "changed_files": 90, "additions": 5000, "deletions": 10},
         "PREDICT_UNRESOLVED_AT_HORIZON", "broad and fresh"),
        ({"age_days_at_freeze": 10, "changed_files": 5, "additions": 100, "deletions": 20},
         "PREDICT_MERGED", "moderate and fresh"),
    ]
    results = []
    for obs, expected, why in cases:
        got = decide(obs)["verdict"]
        results.append({"why": why, "expected": expected, "got": got, "ok": got == expected})
    distinct = {r["got"] for r in results}
    return {
        "cases": results,
        "all_ok": all(r["ok"] for r in results),
        "distinct_verdicts_produced": sorted(distinct),
        "discriminates": len(distinct) > 1,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2, sort_keys=True))
