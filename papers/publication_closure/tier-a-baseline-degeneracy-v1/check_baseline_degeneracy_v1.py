#!/usr/bin/env python3
"""Registered shortcut probe: are the Tier-A baseline sets actually discriminating?

ORION-paper#49 requires running registered nuisance/shortcut probes. A baseline
set is a shortcut if two nominally different baselines are extensionally
identical, or if one is constant where it is not meant to be: either makes the
comparison weaker than the study claims while every gate still passes. This is
the same defect already found and repaired in A6, where the candidate and the
"information-equivalent ideal donor" both delegated to one function, so the tie
gate could not fail.

Decidable without any protected outcome: each lane's pre-gold input alphabet is
finite, so the baselines are enumerated exhaustively over it.

Exit codes follow the repo convention: 0 clean, 2 a finding, 3 could not check.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A3 = ROOT / "papers/publication_closure/a3-external-change-transport-v1/baselines_v1.py"
A4 = ROOT / "papers/publication_closure/a4-hidden-cause-external-v1/baseline_routers_v1.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def a3_grid() -> list[dict]:
    tri = (True, False, None)
    return [
        {
            "version_changed": v, "provenance_changed": p,
            "semantic_diff_material": s, "confidence_signal_meaningful": m,
            "confidence_signal": c, "confidence_reopen_threshold": 0.5,
        }
        for v, p, s, m in itertools.product(tri, tri, tri, tri)
        for c in (0.1, 0.5, 0.9)
    ]


def a4_grid(interventions: tuple[str, ...]) -> list[dict]:
    """Every field the routers actually read, and majority/prediction varied
    INDEPENDENTLY -- tying them together makes MAJORITY_DEVELOPMENT and
    LEARNED_ROUTER_DEVELOPMENT_ONLY look collapsed when they are not."""
    grid = []
    for size in range(1, len(interventions) + 1):
        for allowed in itertools.combinations(interventions, size):
            for score in (0.1, 0.9):
                for majority in interventions:
                    for prediction in interventions:
                        grid.append({
                            "allowed_interventions": list(allowed),
                            "task_id": f"T{len(grid):05d}",
                            "development_majority_intervention": majority,
                            "declared_intervention_cost_vectors":
                                {x: [float(i + 1)] for i, x in enumerate(interventions)},
                            "uncertainty_score": score,
                            "development_uncertainty_compute_threshold": 0.5,
                            "learned_router_training_split": "development_only",
                            "learned_router_model_sha256": "a" * 64,
                            "learned_router_prediction": prediction,
                        })
    return grid


def audit(lane: str, fns: dict, grid: list[dict], constant_by_design: set[str]) -> dict:
    outputs = {name: [fn(rec) for rec in grid] for name, fn in fns.items()}
    collapsed = [
        [a, b] for a, b in itertools.combinations(sorted(outputs), 2)
        if outputs[a] == outputs[b]
    ]
    degenerate = [
        name for name, vals in outputs.items()
        if len(set(vals)) <= 1 and name not in constant_by_design
    ]
    return {
        "lane": lane, "records": len(grid),
        "distinct_outputs": {n: len(set(v)) for n, v in sorted(outputs.items())},
        "collapsed_pairs": collapsed, "degenerate": sorted(degenerate),
    }


def main() -> int:
    if not A3.is_file() or not A4.is_file():
        print("CANNOT CHECK: a Tier-A baseline module is missing")
        return 3
    a3 = load("a3_baselines", A3)
    a4 = load("a4_routers", A4)

    reports = [
        audit("A3", {
            "ALWAYS_REUSE": a3.always_reuse, "ALWAYS_REOPEN": a3.always_reopen,
            "VERSION_PROVENANCE_ONLY": a3.version_provenance_only,
            "SEMANTIC_DIFF_ONLY": a3.semantic_diff_only,
            "CONFIDENCE_ONLY": a3.confidence_only,
        }, a3_grid(), {"ALWAYS_REUSE", "ALWAYS_REOPEN"}),
        audit("A4", dict(a4.OUTCOME_BLIND), a4_grid(tuple(a4.INTERVENTIONS)), set()),
    ]
    print(json.dumps({"record": "TIER_A_BASELINE_DEGENERACY_V1", "lanes": reports},
                     indent=2, sort_keys=True))

    # The oracle must exist for regret analysis and must NOT be outcome-blind.
    if not callable(getattr(a4, "intervention_oracle", None)):
        print("FINDING: A4 declares an intervention oracle for regret analysis but none is implemented")
        return 2
    if "INTERVENTION_ORACLE" in a4.OUTCOME_BLIND:
        print("FINDING: the intervention oracle is exposed in the outcome-blind router set")
        return 2

    findings = [r for r in reports if r["collapsed_pairs"] or r["degenerate"]]
    if findings:
        for r in findings:
            print(f"FINDING: {r['lane']} collapsed={r['collapsed_pairs']} degenerate={r['degenerate']}")
        return 2
    print("every Tier-A baseline is distinguishable and non-degenerate over its pre-gold alphabet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
