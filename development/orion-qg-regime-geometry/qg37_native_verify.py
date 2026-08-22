#!/usr/bin/env python3
"""Native ORION-Q authority gate for QG-37 robust probe identity."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "artifacts/orion-qg-qg37-robust.json"
REPL = ROOT / "artifacts/orion-qg-qg37b-pbsat.json"
GEN = ROOT / "artifacts/orion-qg-qg37-generic-verification.json"
OUT = ROOT / "artifacts/orion-qg-qg37-native-verification.json"
TOKEN = "ORIONQG_QG37_NATIVE="
EXACT = "QG37_EXACT_ONE_CORRUPTION_CLASS_CONDITIONED_PROBE_CODE_MACHINE_CHECKED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--production", type=Path, default=PROD)
    ap.add_argument("--replica", type=Path, default=REPL)
    ap.add_argument("--generic", type=Path, default=GEN)
    ap.add_argument("--output", type=Path, default=OUT)
    a = ap.parse_args()
    p = json.loads(a.production.read_text())
    r = json.loads(a.replica.read_text())
    g = json.loads(a.generic.read_text())
    checks = {
        "generic_accept": g.get("all_checks") is True and g.get("terminal") == EXACT,
        "production_authority": p.get("ONE_CORRUPTION_CLASS_CONDITIONED_IDENTITY_AUTHORITY") is True and p.get("all_92_class_conditioned_exact") is True,
        "replica_authority": r.get("INDEPENDENT_ROBUST_MINIMA_AUTHORITY") is True and r.get("all_92_exact") is True,
        "R1_star": isinstance(p.get("R1_star"), int) and p.get("R1_star") == r.get("R1_star") == g.get("R1_star"),
        "hard_false": all(p.get(k) is False for k in (
            "HARDWARE_MEASUREMENT_NOISE_MODEL", "STOCHASTIC_PHYSICAL_ERROR_RATE", "FAULT_TOLERANCE_THRESHOLD",
            "MINIMUM_FULL_FINITE_OPTIMUM_PROBES", "GENERIC_CODING_NOVELTY", "physical_quantum_advantage_claim", "novelty_authority"
        )) and all(r.get(k) is False for k in (
            "HARDWARE_MEASUREMENT_NOISE_MODEL", "STOCHASTIC_PHYSICAL_ERROR_RATE", "FAULT_TOLERANCE_THRESHOLD",
            "MINIMUM_FULL_FINITE_OPTIMUM_PROBES", "GENERIC_CODING_SAT_NOVELTY", "COMPILER_RUNTIME_ADVANTAGE",
            "physical_quantum_advantage_claim", "novelty_authority"
        )),
    }
    ok = all(checks.values())
    out = {
        "schema": "ORIONQG.QG37.NativeVerification.v1",
        "decision": "ACCEPT_ROBUST_IDENTITY_AUTHORITY" if ok else "REJECT_OR_CANNOT_CHECK",
        "terminal": EXACT if ok else "QG37_CANNOT_CHECK",
        "all_checks": bool(ok),
        "checks": checks,
        "R1_star": p.get("R1_star") if ok else None,
        "ONE_CORRUPTION_CLASS_CONDITIONED_IDENTITY_AUTHORITY": bool(ok),
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "STOCHASTIC_PHYSICAL_ERROR_RATE": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "GENERIC_CODING_NOVELTY": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(TOKEN + json.dumps({"decision": out["decision"], "terminal": out["terminal"], "R1_star": out["R1_star"]}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
