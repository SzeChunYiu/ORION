#!/usr/bin/env python3
"""Independent check of ORION-19's invariant-orbit coverage gate.

Recomputes the orbit partition of the frozen D1 v1.2 splits from the frozen
colouring, and checks four things the gate analysis asserts:

  A  orbit-majority ceiling on the protected split is 112/128 = 0.875
  B  the frozen model scores 96/128 = 0.750 and is constant within every cell
  C  dev is 100% in-orbit and protected is 0% in-orbit w.r.t. training
  D  the coverage/floor tradeoff: refinement never raises coverage and never
     raises the floor; coarsening never lowers the floor

Nothing is trained and no frozen record is rewritten; the recorded result is
read as data. Negative controls must fire or the check reports failure --
a check that cannot fail proves nothing.

Exit 0 PASS, 1 FAIL, 3 CANNOT_CHECK.
"""
from __future__ import annotations

import collections
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
RESULT = (REPO / "papers/orion-19-structured-epistemic-learning/evidence/"
          "P9_U_T4_SUCCESSOR_INVARIANT_PROFILE_RESULT_2026-08-24.json")


def cannot_check(msg: str):
    print(f"CANNOT_CHECK: {msg}")
    sys.exit(3)


def cells_of(keys, labels):
    c = collections.defaultdict(list)
    for k, y in zip(keys, labels):
        c[k].append(y)
    return c


def floor_mass(cells) -> int:
    """Cases no invariant rule can get right: per cell, all but the plurality."""
    return sum(len(v) - max(collections.Counter(v).values()) for v in cells.values())


def coverage(keys, seen) -> int:
    return sum(1 for k in keys if k in seen)


def main() -> int:
    sys.path.insert(0, str(REPO / "src"))
    try:
        from orion.study.p9 import hostile_representation_attacks as A
        from orion.study.p9.invariant_profile_battery import _bag_dicts, _profile_dicts
        from orion.study.p9.invariant_profile_representation import build_colouring
    except Exception as exc:                                  # pragma: no cover
        cannot_check(f"frozen representation modules unavailable: {exc}")

    if not RESULT.exists():
        cannot_check(f"frozen result absent: {RESULT}")
    rec = json.loads(RESULT.read_text())

    ds = A.build_datasets()
    d = ds[A.DATASET_BASE]
    bags = _bag_dicts(d)
    col = build_colouring(bags[0], bags[1])
    key = lambda p: json.dumps(p, sort_keys=True, default=str)
    lab = lambda rows: [str(getattr(r, "label", r)).split(".")[-1].strip("'>") for r in rows]

    names = ("train", "dev", "protected")
    K = {n: [key(p) for p in _profile_dicts(bags[i], col)] for i, n in enumerate(names)}
    L = {n: lab(rows) for n, rows in zip(names, (d.train, d.dev, d.test))}

    prot = cells_of(K["protected"], L["protected"])
    n = len(L["protected"])
    fl = floor_mass(prot)
    ceiling = (n - fl) / n

    gold = rec["arms"]["BASE"]["gold"]
    pred = rec["arms"]["BASE"]["predictions"]
    if len(gold) != n:
        cannot_check(f"frozen result has {len(gold)} cases, splits give {n}")
    model_ok = sum(1 for g, p in zip(gold, pred) if g == p)

    pc = cells_of(K["protected"], pred)
    constant = all(len(set(v)) == 1 for v in pc.values())

    seen = set(K["train"])
    cov_dev = coverage(K["dev"], seen) / len(K["dev"])
    cov_prot = coverage(K["protected"], seen) / n

    checks = {
        "A_ceiling_is_112_of_128": (n - fl == 112 and abs(ceiling - 0.875) < 1e-9),
        "B_model_scores_96_of_128": model_ok == 96,
        "B_predictions_constant_within_every_orbit_cell": constant,
        "C_dev_fully_in_orbit": abs(cov_dev - 1.0) < 1e-9,
        "C_protected_fully_out_of_orbit": cov_prot == 0.0,
    }

    # D: tradeoff, checked on the real partition by random refinement/coarsening.
    rng = random.Random(20260828)
    refine_ok = coarsen_ok = True
    for _ in range(400):
        refined = [f"{k}|{rng.randrange(3)}" for k in K["protected"]]
        rk = {k: f"{k}|{rng.randrange(3)}" for k in set(K["train"])}
        seen_r = {v for v in rk.values()}
        if floor_mass(cells_of(refined, L["protected"])) > fl:
            refine_ok = False
        if coverage(refined, seen_r) > coverage(K["protected"], seen):
            refine_ok = False
        merge = {k: f"m{i % 2}" for i, k in enumerate(sorted(set(K['protected'])))}
        coarse = [merge[k] for k in K["protected"]]
        if floor_mass(cells_of(coarse, L["protected"])) < fl:
            coarsen_ok = False
    checks["D_refinement_never_raises_floor_or_coverage"] = refine_ok
    checks["D_coarsening_never_lowers_floor"] = coarsen_ok

    # Negative controls: each must FIRE, else the check is vacuous.
    controls = {
        "shuffled_labels_break_the_ceiling": (
            floor_mass(cells_of(K["protected"], rng.sample(L["protected"], n))) != fl),
        "a_mixed_cell_exists_so_floor_is_not_trivially_zero": fl > 0,
        "model_score_differs_from_ceiling": model_ok != n - fl,
        "train_cells_are_nonempty_so_coverage_is_testable": len(seen) > 0,
    }

    ok = all(checks.values()) and all(controls.values())
    report = {
        "schema": "ORION.ORION19.OrbitCoverageGate.CheckerReport.v1",
        "successor_id": "ORION19.INVARIANT_ORBIT_COVERAGE_GATE.v1",
        "independence": "no ORION-19 scoring path imported; partition recomputed "
                        "from the frozen colouring; recorded result read as data",
        "protected_cases": n,
        "orbit_cells_protected": len(prot),
        "irreducible_floor_cases": fl,
        "orbit_majority_ceiling": round(ceiling, 6),
        "model_correct": model_ok,
        "model_accuracy": round(model_ok / n, 6),
        "recoverable_gap_cases": (n - fl) - model_ok,
        "orbit_coverage_dev": round(cov_dev, 6),
        "orbit_coverage_protected": round(cov_prot, 6),
        "cells": {"train": len(set(K["train"])), "dev": len(set(K["dev"])),
                  "protected": len(prot),
                  "protected_cap_train": len(set(K["protected"]) & seen)},
        "checks": checks,
        "negative_controls": controls,
        "status": "PASS" if ok else "FAIL",
    }
    out = Path(__file__).resolve().parents[1] / "RESULT.json"
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("orbit_majority_ceiling", "model_accuracy", "irreducible_floor_cases",
                       "recoverable_gap_cases", "orbit_coverage_dev",
                       "orbit_coverage_protected", "status")}, indent=1))
    for k, v in {**checks, **controls}.items():
        print(f"  {'ok  ' if v else 'FAIL'} {k}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
