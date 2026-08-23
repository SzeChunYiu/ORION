#!/usr/bin/env python3
"""QG-37c: precommitted receipt composition for exact robust-geometry closure."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
QDIR = ROOT / "research/extensions/orion-qg"
DEV = ROOT / "development/orion-qg-regime-geometry"
PROD = ROOT / "artifacts/orion-qg-qg37-robust.json"
REPL = ROOT / "artifacts/orion-qg-qg37b-pbsat.json"
Q35 = QDIR / "QG35_SUMMARY_CONDITIONED_FIXED_RESULTS.json"
PROTO = DEV / "QG37C_REPLICATION_CLOSURE_PROTOCOL_V1.md"
OUT = ROOT / "artifacts/orion-qg-qg37c-closure.json"
TOKEN = "ORIONQG_QG37C="
SUCCESS = "QG37C_EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_CLOSED_BY_INDEPENDENT_REPLICATION"
DISAGREE = "QG37C_PRODUCTION_REPLICA_EXACT_CLASS_DISAGREEMENT"
CONTRADICTION = "QG37C_PRODUCTION_UPPER_BOUND_CONTRADICTION"
CANNOT = "QG37C_CANNOT_CHECK"
PROD_DIGEST = "12bf825a29710e5939642afe52f8645a70c120ca7461d6f61102853bc6eba566"
Q37_PROTO_BLOB = "c99f6ee73ab8e44e588a14ad0ab79b3fe426311c"
RESIDUAL = (39, 40, 63)


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def valid(d: dict[str, Any]) -> bool:
    x = d.get("result_digest")
    return isinstance(x, str) and x == hashlib.sha256(canon({k: v for k, v in d.items() if k != "result_digest"}).encode()).hexdigest()


def shaf(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--production", type=Path, default=PROD)
    ap.add_argument("--replica", type=Path, default=REPL)
    ap.add_argument("--qg35", type=Path, default=Q35)
    ap.add_argument("--output", type=Path, default=OUT)
    a = ap.parse_args()
    p = json.loads(a.production.read_text())
    r = json.loads(a.replica.read_text())
    q = json.loads(a.qg35.read_text())

    pc = p.get("classes", [])
    rc = r.get("classes", [])
    exact_prod = [x.get("class_index") for x in pc if x.get("D3_status") == "EXACT"]
    unresolved = [x.get("class_index") for x in pc if x.get("D3_status") != "EXACT"]
    parent = {
        "production_digest": valid(p) and p.get("result_digest") == PROD_DIGEST,
        "production_terminal": p.get("terminal") == "QG37_ROBUST_CLASS_CONDITIONED_UPPER_BOUND_ONLY",
        "production_protocol": p.get("frozen_protocol_blob_sha") == Q37_PROTO_BLOB,
        "production_89_exact": len(exact_prod) == 89 and unresolved == list(RESIDUAL),
        "replica_digest": valid(r),
        "replica_exact": r.get("terminal") == "QG37B_INDEPENDENT_EXACT_ROBUST_MINIMA_MACHINE_CHECKED" and r.get("all_92_exact") is True and r.get("INDEPENDENT_ROBUST_MINIMA_AUTHORITY") is True,
        "same_universe": p.get("universe") == r.get("universe") and p.get("universe", {}).get("orbits") == 715 and p.get("universe", {}).get("physical_probes") == 384 and p.get("universe", {}).get("joint_classes") == 92,
        "qg35": q.get("EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY") is True and q.get("terminal") == "QG35_EXACT_SUMMARY_CONDITIONED_FIXED_PROBE_COMPLEXITY_MACHINE_CHECKED" and len(q.get("class_minima", [])) == 92,
        "row_counts": len(pc) == len(rc) == 92,
    }

    exact_disagreements = []
    upper_contradictions = []
    replica_witness_invalid = []
    minima = []
    if all(parent.values()):
        for i, (pr, rr) in enumerate(zip(pc, rc)):
            pm = pr.get("D3_minimum")
            rm = rr.get("D3_minimum")
            minima.append(rm)
            if pr.get("D3_status") == "EXACT" and pm != rm:
                exact_disagreements.append({"class_index": i, "production": pm, "replica": rm})
            if i in RESIDUAL and (not isinstance(rm, int) or rm > pr.get("D3_upper_bound")):
                upper_contradictions.append({"class_index": i, "production_upper": pr.get("D3_upper_bound"), "replica": rm})
            cert = rr.get("distance_certificate")
            if len(rr.get("selected_probe_indices", [])) != rm or (rr.get("class_size", 0) > 1 and (not isinstance(cert, dict) or cert.get("minimum_distance", 0) < 3 or cert.get("radius1_unique") is not True)):
                replica_witness_invalid.append(i)

    if not all(parent.values()) or replica_witness_invalid:
        terminal = CANNOT
    elif exact_disagreements:
        terminal = DISAGREE
    elif upper_contradictions:
        terminal = CONTRADICTION
    else:
        terminal = SUCCESS

    success = terminal == SUCCESS
    d1 = [int(x) for x in q.get("class_minima", [])] if parent["qg35"] else []
    overhead = [int(m) - d1[i] for i, m in enumerate(minima)] if success else None
    ohist = {str(k): int(v) for k, v in sorted(Counter(overhead or []).items())} if success else None
    rstar = max(minima) if success else None
    worst = [i for i, m in enumerate(minima) if m == rstar] if success else None
    strict_floor = [i for i, m in enumerate(minima) if pc[i].get("class_size", 0) > 1 and m > d1[i] + 2] if success else None
    out = {
        "schema": "ORIONQG.QG37C.ReplicationClosure.v1",
        "terminal": terminal,
        "protocol_sha256": shaf(PROTO),
        "parent_checks": parent,
        "production_result_digest": p.get("result_digest"),
        "replica_result_digest": r.get("result_digest"),
        "qg35_result_digest": q.get("result_digest"),
        "production_exact_class_disagreements": exact_disagreements,
        "production_upper_bound_contradictions": upper_contradictions,
        "replica_witness_invalid_classes": replica_witness_invalid,
        "exact_D3_minima": minima if success else None,
        "D1_noiseless_minima": d1 if success else None,
        "robustness_overhead_D3_minus_D1": overhead,
        "robustness_overhead_histogram": ohist,
        "maximum_robustness_overhead": max(overhead) if success else None,
        "R1_star": rstar,
        "R1_star_class_indices": worst,
        "strict_puncturing_exception_class_indices": strict_floor,
        "EXACT_ONE_CORRUPTION_ROBUST_GEOMETRY_AUTHORITY": bool(success),
        "EXACT_ROBUSTNESS_OVERHEAD_AUTHORITY": bool(success),
        "UNIVERSAL_ROBUST_MINIMUM_AUTHORITY": False,
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "STOCHASTIC_PHYSICAL_ERROR_RATE": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "HARDWARE_MEASUREMENT_MINIMUM": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "GENERIC_CODING_PBSAT_NOVELTY": False,
        "COMPILER_RUNTIME_ADVANTAGE": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    out["result_digest"] = hashlib.sha256(canon(out).encode()).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"terminal": terminal, "R1_star": rstar, "max_overhead": out["maximum_robustness_overhead"], "strict_floor": strict_floor, "result_digest": out["result_digest"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
