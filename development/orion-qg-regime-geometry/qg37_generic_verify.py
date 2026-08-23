#!/usr/bin/env python3
"""Independent frontier-harness verifier for QG-37/QG-37b robust probe minima."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / "development/orion-qg-regime-geometry"
PROD = ROOT / "artifacts/orion-qg-qg37-robust.json"
REPL = ROOT / "artifacts/orion-qg-qg37b-pbsat.json"
OUT = ROOT / "artifacts/orion-qg-qg37-generic-verification.json"
TOKEN = "ORIONQG_QG37_GENERIC="
EXACT = "QG37_EXACT_ONE_CORRUPTION_CLASS_CONDITIONED_PROBE_CODE_MACHINE_CHECKED"
DISAGREE = "QG37_GENERIC_PRODUCTION_REPLICA_DISAGREEMENT"
CANNOT = "QG37_CANNOT_CHECK"
FROZEN_BLOB = "c99f6ee73ab8e44e588a14ad0ab79b3fe426311c"


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def valid_digest(d: dict[str, Any]) -> bool:
    got = d.get("result_digest")
    if not isinstance(got, str):
        return False
    base = {k: v for k, v in d.items() if k != "result_digest"}
    return got == hashlib.sha256(canon(base).encode()).hexdigest()


def load_qg32_generic():
    p = DEV / "qg32_generic_verify.py"
    spec = importlib.util.spec_from_file_location("qg32generic_for_qg37", p)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generic QG-32 primitives")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def universe():
    m = load_qg32_generic()
    z = m.construct()
    return z["reps"], z["mat"], z["joint"]


def hist(groups):
    return {str(k): int(v) for k, v in sorted(Counter(len(g) for g in groups).items())}


def distance(group, mat, selected):
    if len(group) <= 1:
        return None
    return min(sum(int(mat[a, p] != mat[b, p]) for p in selected) for a, b in itertools.combinations(group, 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--production", type=Path, default=PROD)
    ap.add_argument("--replica", type=Path, default=REPL)
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()

    prod = json.loads(args.production.read_text())
    repl = json.loads(args.replica.read_text())
    reps, mat, joint = universe()
    expected_hist = hist(joint)

    checks: dict[str, bool] = {
        "production_digest": valid_digest(prod),
        "replica_digest": valid_digest(repl),
        "frozen_protocol_binding": prod.get("frozen_protocol_blob_sha") == FROZEN_BLOB,
        "universe": len(reps) == 715 and mat.shape == (715, 384) and len(joint) == 92,
        "production_universe": prod.get("universe") == {
            "orbits": 715,
            "physical_probes": 384,
            "joint_classes": 92,
            "joint_class_size_histogram": expected_hist,
        },
        "replica_universe": repl.get("universe") == {
            "orbits": 715,
            "physical_probes": 384,
            "joint_classes": 92,
            "joint_class_size_histogram": expected_hist,
        },
        "production_exact": prod.get("terminal") == EXACT and prod.get("all_92_class_conditioned_exact") is True,
        "replica_exact": repl.get("terminal") == "QG37B_INDEPENDENT_EXACT_ROBUST_MINIMA_MACHINE_CHECKED" and repl.get("all_92_exact") is True and repl.get("INDEPENDENT_ROBUST_MINIMA_AUTHORITY") is True,
        "hard_false_production": all(prod.get(k) is False for k in (
            "HARDWARE_MEASUREMENT_NOISE_MODEL", "STOCHASTIC_PHYSICAL_ERROR_RATE", "FAULT_TOLERANCE_THRESHOLD",
            "MINIMUM_FULL_FINITE_OPTIMUM_PROBES", "GENERIC_CODING_NOVELTY", "physical_quantum_advantage_claim", "novelty_authority"
        )),
        "hard_false_replica": all(repl.get(k) is False for k in (
            "HARDWARE_MEASUREMENT_NOISE_MODEL", "STOCHASTIC_PHYSICAL_ERROR_RATE", "FAULT_TOLERANCE_THRESHOLD",
            "MINIMUM_FULL_FINITE_OPTIMUM_PROBES", "GENERIC_CODING_SAT_NOVELTY", "COMPILER_RUNTIME_ADVANTAGE",
            "physical_quantum_advantage_claim", "novelty_authority"
        )),
    }

    prod_rows = prod.get("classes", [])
    repl_rows = repl.get("classes", [])
    minima_equal = len(prod_rows) == len(repl_rows) == 92
    production_witnesses = minima_equal
    replica_witnesses = minima_equal
    row_checks = []
    if minima_equal:
        for i, group in enumerate(joint):
            pr, rr = prod_rows[i], repl_rows[i]
            pm = pr.get("D3_minimum")
            rm = rr.get("D3_minimum")
            minima_equal &= pr.get("class_index") == rr.get("class_index") == i and pm == rm
            ps = [int(x) for x in pr.get("selected_probe_indices", [])]
            rs = [int(x) for x in rr.get("selected_probe_indices", [])]
            pd = distance(group, mat, ps)
            rd = distance(group, mat, rs)
            pgood = (len(group) <= 1 and pm == 0 and not ps) or (pm == len(ps) and pd is not None and pd >= 3)
            rgood = (len(group) <= 1 and rm == 0 and not rs) or (rm == len(rs) and rd is not None and rd >= 3)
            production_witnesses &= bool(pgood)
            replica_witnesses &= bool(rgood)
            row_checks.append({"class_index": i, "production_minimum": pm, "replica_minimum": rm, "production_distance": pd, "replica_distance": rd, "agree": pm == rm, "production_witness": bool(pgood), "replica_witness": bool(rgood)})
    checks["minima_equal"] = bool(minima_equal)
    checks["production_witnesses"] = bool(production_witnesses)
    checks["replica_witnesses"] = bool(replica_witnesses)
    checks["R1_star_equal"] = prod.get("R1_star") == repl.get("R1_star") and isinstance(prod.get("R1_star"), int)
    checks["exception_set_equal"] = prod.get("strict_puncturing_exception_class_indices") == repl.get("strict_puncturing_exception_class_indices")

    if checks["production_exact"] and checks["replica_exact"] and not checks["minima_equal"]:
        terminal = DISAGREE
    elif all(checks.values()):
        terminal = EXACT
    else:
        terminal = CANNOT
    ok = terminal == EXACT
    out = {
        "schema": "ORIONQG.QG37.GenericVerification.v1",
        "decision": "ACCEPT_EXACT_ROBUST_AUTHORITY" if ok else "REJECT_OR_CANNOT_CHECK",
        "terminal": terminal,
        "all_checks": bool(ok),
        "checks": checks,
        "R1_star": prod.get("R1_star") if ok else None,
        "row_checks": row_checks,
        "ONE_CORRUPTION_CLASS_CONDITIONED_IDENTITY_AUTHORITY": bool(ok),
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "STOCHASTIC_PHYSICAL_ERROR_RATE": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "GENERIC_CODING_NOVELTY": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + canon({"decision": out["decision"], "terminal": terminal, "R1_star": out["R1_star"], "minima_equal": checks["minima_equal"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
