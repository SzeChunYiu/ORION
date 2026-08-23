#!/usr/bin/env python3
"""Third generic verifier for the frozen QG-37c replication closure."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development/orion-qg-regime-geometry"
SRC = ROOT / "artifacts/orion-qg-qg37c-closure.json"
PROD = ROOT / "artifacts/orion-qg-qg37-robust.json"
REPL = ROOT / "artifacts/orion-qg-qg37b-pbsat.json"
Q35 = ROOT / "research/extensions/orion-qg/QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg37c-generic-verification.json"
TOKEN = "ORIONQG_QG37C_GENERIC="
SUCCESS = "QG37C_EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_CLOSED_BY_INDEPENDENT_REPLICATION"
RESIDUAL = (39, 40, 63)


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def valid(d: dict[str, Any]) -> bool:
    x = d.get("result_digest")
    return isinstance(x, str) and x == hashlib.sha256(canon({k: v for k, v in d.items() if k != "result_digest"}).encode()).hexdigest()


def load_generic_universe():
    p = DEV / "qg32_generic_verify.py"
    s = importlib.util.spec_from_file_location("qg32generic_for_qg37c", p)
    if s is None or s.loader is None:
        raise RuntimeError("cannot import generic QG32 primitives")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.construct()


def min_distance(group, mat, selected):
    if len(group) <= 1:
        return None
    return min(sum(int(mat[a, p] != mat[b, p]) for p in selected) for a, b in itertools.combinations(group, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=SRC)
    ap.add_argument("--production", type=Path, default=PROD)
    ap.add_argument("--replica", type=Path, default=REPL)
    ap.add_argument("--qg35", type=Path, default=Q35)
    ap.add_argument("--output", type=Path, default=OUT)
    a = ap.parse_args()
    s = json.loads(a.input.read_text())
    p = json.loads(a.production.read_text())
    r = json.loads(a.replica.read_text())
    q = json.loads(a.qg35.read_text())
    z = load_generic_universe()
    mat, joint = z["mat"], z["joint"]

    checks = {
        "closure_digest": valid(s),
        "production_digest": valid(p),
        "replica_digest": valid(r),
        "closure_success": s.get("terminal") == SUCCESS and s.get("EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_AUTHORITY") is True,
        "universe": len(z["reps"]) == 715 and mat.shape == (715, 384) and len(joint) == 92,
        "row_counts": len(p.get("classes", [])) == len(r.get("classes", [])) == 92,
        "qg35": q.get("EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY") is True and len(q.get("class_minima", [])) == 92,
    }
    row_checks = []
    exact_match = checks["row_counts"]
    residual_bound = checks["row_counts"]
    witness_ok = checks["row_counts"]
    minima = []
    if checks["row_counts"]:
        for i, group in enumerate(joint):
            pr = p["classes"][i]
            rr = r["classes"][i]
            rm = rr.get("D3_minimum")
            minima.append(rm)
            sel = [int(x) for x in rr.get("selected_probe_indices", [])]
            md = min_distance(group, mat, sel)
            good = (len(group) <= 1 and rm == 0 and not sel) or (isinstance(rm, int) and len(sel) == rm and md is not None and md >= 3)
            witness_ok &= bool(good)
            if pr.get("D3_status") == "EXACT":
                exact_match &= pr.get("D3_minimum") == rm
            elif i in RESIDUAL:
                residual_bound &= isinstance(rm, int) and rm <= pr.get("D3_upper_bound")
            else:
                residual_bound = False
            row_checks.append({"class_index": i, "production_status": pr.get("D3_status"), "production_minimum": pr.get("D3_minimum"), "production_upper": pr.get("D3_upper_bound"), "replica_minimum": rm, "replica_min_distance": md, "replica_witness_valid": bool(good)})
    checks["production_exact_rows_match"] = bool(exact_match)
    checks["residual_respects_production_upper"] = bool(residual_bound)
    checks["replica_witnesses_rederived"] = bool(witness_ok)
    checks["minima_vector"] = minima == s.get("exact_D3_minima")
    if all(isinstance(x, int) for x in minima) and len(minima) == 92:
        d1 = [int(x) for x in q["class_minima"]]
        overhead = [minima[i] - d1[i] for i in range(92)]
        checks["overhead_vector"] = overhead == s.get("robustness_overhead_D3_minus_D1")
        checks["R1_star"] = max(minima) == s.get("R1_star")
    else:
        checks["overhead_vector"] = False
        checks["R1_star"] = False
    checks["hard_false"] = all(s.get(k) is False for k in (
        "UNIVERSAL_ROBUST_MINIMUM_AUTHORITY", "HARDWARE_MEASUREMENT_NOISE_MODEL", "STOCHASTIC_PHYSICAL_ERROR_RATE",
        "FAULT_TOLERANCE_THRESHOLD", "HARDWARE_MEASUREMENT_MINIMUM", "MINIMUM_FULL_FINITE_OPTIMUM_PROBES",
        "GENERIC_CODING_PBSAT_NOVELTY", "COMPILER_RUNTIME_ADVANTAGE", "physical_quantum_advantage_claim", "novelty_authority"
    ))
    ok = all(checks.values())
    out = {
        "schema": "ORIONQG.QG37C.GenericVerification.v1",
        "decision": "ACCEPT_REPLICATION_CLOSURE" if ok else "REJECT",
        "terminal": SUCCESS if ok else "QG37C_CANNOT_CHECK",
        "all_checks": bool(ok),
        "checks": checks,
        "R1_star": s.get("R1_star") if ok else None,
        "row_checks": row_checks,
        "EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_AUTHORITY": bool(ok),
        "EXACT_ROBUSTNESS_OVERHEAD_AUTHORITY": bool(ok),
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"decision": out["decision"], "R1_star": out["R1_star"], "witnesses": checks["replica_witnesses_rederived"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
