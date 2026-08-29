#!/usr/bin/env python3
"""ORION-05 V2 Stage 0: the three same-domain controls that gate Stage 1.

COMPUTE_PLAN_V2 step 2: r6o-16, r6o-17 and r6o-19 must return 4/4, 5/5 and 6/6
under the all-matchings estimand, demonstrating that the historical
fixed-matching gap is erased. Any deviation stops the stage at
CANNOT_CHECK_CONTROL_FAILURE and Stage 1 carries no authority.

Why this exists as a v2 artifact instead of a citation. The v1 census already
solved these three instances with the same solver and recorded 4/4, 5/5, 6/6 with
gap 0. But that file's own verdict is control_gate_passed=false, because the v1
checker treated them as POSITIVE controls and expected a gap to appear. The v2
plan inverts the criterion: absence of the gap is the required outcome. Reading a
recorded "false" as a pass would be a reinterpretation of someone else's verdict,
so this re-derives the numbers natively under the v2 estimand and reports both
what it measured and what v1 recorded.

Estimand, identical to the Stage 1 runner: min cost over all 15 perfect matchings
at max_support=1 (C1) and max_support=2 (C2); gap = C1 - C2.

Exit codes: 0 controls pass, 1 a control deviates (CANNOT_CHECK_CONTROL_FAILURE),
3 the solver could not be loaded.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

SOLVER_REL = "papers/orion-05-tare-expressivity/orion05_r11_sparse_direct_solver.py"

# Targets verbatim from the v1 census record CONTROL_GATE.json, with the cost
# pair the v2 compute plan requires and the pair v1 actually recorded.
CONTROLS = {
    "control:r6o-16": {
        "targets": [[1, 0], [1, 0], [1, 0], [1, 0], [2, 0], [2, 2]],
        "required_c1_c2": [4, 4],
        "v1_recorded_c1_c2": [4, 4],
    },
    "control:r6o-17": {
        "targets": [[1, 0], [1, 0], [1, 0], [1, 0], [2, 0], [0, 2]],
        "required_c1_c2": [5, 5],
        "v1_recorded_c1_c2": [5, 5],
    },
    "control:r6o-19": {
        "targets": [[1, 0], [1, 0], [1, 0], [1, 0], [2, 2], [0, 2]],
        "required_c1_c2": [6, 6],
        "v1_recorded_c1_c2": [6, 6],
    },
}
V1_SOLVER_SHA256 = "642cc67a280abb2ca06089ae01510040f1f598ec638d525ddcc29fae8c6b25d3"


def load_solver(repo_root: str):
    path = Path(repo_root) / SOLVER_REL
    if not path.is_file():
        print(f"solver not found at {path}", file=sys.stderr)
        return None, None
    import hashlib

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("orion05_solver", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["orion05_solver"] = mod
    spec.loader.exec_module(mod)
    return mod, digest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--emit", default="STAGE0_CONTROLS.json")
    ap.add_argument("--only", default="", help="run a single control id")
    a = ap.parse_args()

    mod, solver_sha = load_solver(a.repo_root)
    if mod is None:
        return 3

    results, all_pass = [], True
    for cid, spec in CONTROLS.items():
        if a.only and cid != a.only:
            continue
        t0 = time.time()
        _, w1 = mod.solve_six_targets(spec["targets"], max_support=1)
        t1 = time.time()
        _, w2 = mod.solve_six_targets(spec["targets"], max_support=2)
        t2 = time.time()
        got = [w1.cost, w2.cost]
        ok = got == spec["required_c1_c2"]
        all_pass &= ok
        results.append({
            "control": cid,
            "targets": spec["targets"],
            "required_c1_c2": spec["required_c1_c2"],
            "measured_c1_c2": got,
            "gap": w1.cost - w2.cost,
            "matches_required": ok,
            "v1_recorded_c1_c2": spec["v1_recorded_c1_c2"],
            "agrees_with_v1": got == spec["v1_recorded_c1_c2"],
            "t_solve1_s": round(t1 - t0, 3),
            "t_solve2_s": round(t2 - t1, 3),
        })
        print(f"{cid}: measured {got} required {spec['required_c1_c2']} "
              f"gap={w1.cost - w2.cost} ok={ok} ({t2 - t0:.0f}s)", flush=True)

    partial = bool(a.only)
    terminal = ("PARTIAL_SINGLE_CONTROL" if partial
                else ("STAGE0_CONTROLS_PASS" if all_pass else "CANNOT_CHECK_CONTROL_FAILURE"))
    out = {
        "schema": "ORION05.GLOBAL_OBSTRUCTION_BASIS.v2.stage0",
        "estimand": "min cost over all 15 perfect matchings; gap = C1 - C2",
        "criterion": "r6o-16/17/19 must return 4/4, 5/5, 6/6 (gap erased)",
        "solver_sha256": solver_sha,
        "solver_matches_v1_census": solver_sha == V1_SOLVER_SHA256,
        "controls": results,
        "all_pass": all_pass and not partial,
        "terminal": terminal,
        "gates": "Stage 1 carries no authority unless terminal is STAGE0_CONTROLS_PASS",
        "v1_note": (
            "the v1 census recorded these same three cost pairs but reports "
            "control_gate_passed=false, because the v1 checker expected a gap; the v2 "
            "criterion requires its absence"
        ),
    }
    with open(a.emit, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({k: out[k] for k in
                      ("solver_matches_v1_census", "all_pass", "terminal")}, indent=2))
    return 0 if (all_pass or partial) else 1


if __name__ == "__main__":
    raise SystemExit(main())
