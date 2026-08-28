#!/usr/bin/env python3
"""Independent structural/result checker for ORION-02 R22 PMLB proposal ordering.

Recomputes arm statistics, the paired bootstrap, and the terminal from the
stored RESULTS.json fields without trusting the executor summary, and replays
the frozen policy decisions from the stored outcome/meta tables.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
SCHEMA = "ORION.FiberGuard.PMLBProposalOrdering.R22.v1"
TOL = 1e-9
MATERIAL_FRACTION = 0.05
VALIDITY_GATE = 0.10
COVERAGE_GATE = 0.05


def load(path: Path):
    return json.loads(path.read_text())


def load_executor():
    spec = importlib.util.spec_from_file_location("orion02_r22_executor", HERE / "fiberguard_pmlb_proposal_ordering_r22.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(label: str, ok: bool, detail: str = "") -> bool:
    suffix = " :: " + detail if detail and not ok else ""
    print(("[PASS] " if ok else "[FAIL] ") + label + suffix)
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=HERE / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_RESULTS.json")
    parser.add_argument("--terminal", type=Path, default=HERE / "FIBERGUARD_PMLB_PROPOSAL_ORDERING_R22_TERMINAL.txt")
    args = parser.parse_args()
    payload = load(args.result)
    failures = 0

    failures += not check("schema", payload.get("schema") == SCHEMA)
    failures += not check("terminal file matches payload", args.terminal.read_text().strip() == payload.get("terminal", ""))
    failures += not check("hostile controls all true", all(payload.get("hostile_controls", {}).values()))

    freeze = load(HERE / "FIBERGUARD_PMLB_R22_DATASET_FREEZE.json")["datasets"]
    failures += not check("frozen dataset count", payload["corpus"]["frozen_datasets"] == len(freeze))
    audit_ok = all(v["bytes_match_freeze_sha256"] and v["rows_features_classes_match"] for v in payload["corpus"]["audit"].values())
    failures += not check("corpus audit flags", audit_ok)
    failures += not check("fold assignment covers admissible corpus", len(set(payload["corpus"]["fold_assignment"])) == payload["corpus"]["admissible"])

    # 1. recompute arm summaries from stored per-fold test rows
    pooled = {}
    for arm in list(payload["arms_summary"]):
        if arm == "PRIMARY_LEARNED":
            continue
        pooled[arm] = {}
        for t in range(9):
            pooled[arm].update(payload["folds"][str(t)]["test"][arm])
    pooled["PRIMARY_LEARNED"] = {}
    for t in range(9):
        prim = payload["folds"][str(t)]["primary"]
        pooled["PRIMARY_LEARNED"].update(payload["folds"][str(t)]["test"][prim])
    for arm, rows in pooled.items():
        ex = np.array([r["excess"] for r in rows.values()], float)
        s = payload["arms_summary"][arm]
        ok = (len(rows) == s["n"] and abs(ex.mean() - s["mean_excess"]) <= TOL
              and abs(float(np.percentile(ex, 95.0)) - s["p95_excess"]) <= TOL
              and abs(ex.max() - s["max_excess"]) <= TOL
              and s["violations_strict"] == sum(1 for r in rows.values() if r["violation_strict"]))
        failures += not check("arm summary recomputed: " + arm, ok)

    # 2. paired diff + bootstrap replay with the frozen seed
    names = sorted(pooled["STATIC_ADAPTIVE"])
    diffs = np.array([pooled["PRIMARY_LEARNED"][n]["excess"] - pooled["STATIC_ADAPTIVE"][n]["excess"] for n in names], float)
    pt = payload["primary_test"]
    failures += not check("mean diff recomputed", abs(float(diffs.mean()) - pt["mean_diff"]) <= TOL)
    stored_diffs = np.array([pt["diffs"][n] for n in names], float)
    failures += not check("stored diff vector matches recomputation", bool(np.allclose(diffs, stored_diffs, atol=1e-9, rtol=0)))
    seed = int.from_bytes(hashlib.sha256(b"ORION02_R22_PMLB_PROPOSAL_ORDERING_BOOTSTRAP_V1").digest()[:8], "big") % (2**31 - 1)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, diffs.size, size=(20000, diffs.size))
    means = diffs[idx].mean(axis=1)
    lo, hi = (float(x) for x in np.percentile(means, [2.5, 97.5]))
    failures += not check("bootstrap CI replay", abs(lo - pt["ci_lower"]) <= 1e-9 and abs(hi - pt["ci_upper"]) <= 1e-9)

    # 3. independent terminal precedence
    hostile_ok = all(payload["hostile_controls"].values())
    cov = payload["coverage"]["primary_tau_full_state"]
    prim = payload["arms_summary"]["PRIMARY_LEARNED"]
    static = payload["arms_summary"]["STATIC_ADAPTIVE"]
    viol_rate = prim["violations_strict"] / prim["n"]
    md, cu = pt["mean_diff"], pt["ci_upper"]
    ratio_ok = pt["primary_mean_excess"] <= (1.0 - MATERIAL_FRACTION) * static["mean_excess"] + TOL
    cost_ok = pt["mean_groups_acquired_primary"] <= pt["mean_groups_acquired_static"] + TOL
    if not hostile_ok:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_HOSTILE_CONTROL_FAILED"
    elif cov < 1.0 - COVERAGE_GATE - TOL:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_NO_CERTIFIED_COVERAGE"
    elif viol_rate > VALIDITY_GATE + TOL:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_CERTIFICATE_INVALID"
    elif md < -1e-9 and ratio_ok and cu < 0.0 and cost_ok:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_VALUE"
    elif md < -1e-9:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_STRICT_BUT_NOT_MATERIAL"
    elif abs(md) <= 1e-9:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_NULL"
    else:
        derived = "C_R22_PMLB_PROPOSAL_ORDERING_ADVERSE"
    failures += not check("terminal independently re-derived", derived == payload["terminal"], "derived=" + derived + " stored=" + str(payload.get("terminal")))

    # 4. policy replay from stored outcome/meta tables (uses frozen executor machinery)
    module = load_executor()
    meta = payload["meta_features"]
    outcomes = payload["outcomes"]
    replay_ok, replay_n = True, 0
    for t in range(9):
        roles = payload["folds"][str(t)]["roles"]
        ctx = module.FoldContext(t, roles, meta, outcomes)
        prim_arm = payload["folds"][str(t)]["primary"]
        for arm in ("STATIC_ADAPTIVE", prim_arm):
            for name in roles["test"]:
                dec = module.walk(ctx, name, arm, module.TAU)
                stored = payload["folds"][str(t)]["test"][arm][name]
                got = (dec["committed"], dec["acquired"], dec["certified"])
                if got != (stored["committed"], stored["acquired"], stored["certified"]):
                    replay_ok = False
                replay_n += 1
    failures += not check("policy replay ({} decisions)".format(replay_n), replay_ok)

    print("VERIFY_OK" if failures == 0 else "VERIFY_FAILED failures={}".format(failures))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
