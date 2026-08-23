#!/usr/bin/env python3
"""Run QG-37 production, QG-37b independent replica, generic and native gates."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts"
PROD = ART / "orion-qg-qg37-robust.json"
REPL = ART / "orion-qg-qg37b-pbsat.json"
GEN = ART / "orion-qg-qg37-generic-verification.json"
NAT = ART / "orion-qg-qg37-native-verification.json"
DUAL = ART / "orion-qg-qg37-dual-harness.json"
EXACT = "QG37_EXACT_ONE_CORRUPTION_CLASS_CONDITIONED_PROBE_CODE_MACHINE_CHECKED"


def run(path: str, *args: str):
    p = subprocess.run([sys.executable, str(ROOT / path), *args], cwd=ROOT, text=True, capture_output=True)
    print(p.stdout, end="")
    if p.returncode:
        print(p.stderr, end="", file=sys.stderr)
        raise SystemExit(p.returncode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class-seconds", type=float, default=60.0)
    ap.add_argument("--decision-seconds", type=float, default=90.0)
    a = ap.parse_args()
    ART.mkdir(exist_ok=True)
    run("research/extensions/orion-qg/qg37_one_corruption_robust.py", "--class-seconds", str(a.class_seconds), "--ablation-seconds", "2")
    run("research/extensions/orion-qg/qg37b_pbsat_replication.py", "--production", str(PROD), "--decision-seconds", str(a.decision_seconds))
    run("development/orion-qg-regime-geometry/qg37_generic_verify.py")
    run("development/orion-qg-regime-geometry/qg37_native_verify.py")
    p = json.loads(PROD.read_text())
    r = json.loads(REPL.read_text())
    g = json.loads(GEN.read_text())
    n = json.loads(NAT.read_text())
    ok = (
        p.get("terminal") == EXACT
        and r.get("terminal") == "QG37B_INDEPENDENT_EXACT_ROBUST_MINIMA_MACHINE_CHECKED"
        and g.get("terminal") == n.get("terminal") == EXACT
        and g.get("all_checks") is True
        and n.get("all_checks") is True
        and p.get("R1_star") == r.get("R1_star") == g.get("R1_star") == n.get("R1_star")
    )
    out = {
        "schema": "ORIONQG.QG37.DualHarness.v1",
        "terminal": EXACT if ok else "QG37_GENERIC_NATIVE_OR_REPLICA_DISAGREEMENT",
        "both_accept": bool(ok),
        "production_terminal": p.get("terminal"),
        "replica_terminal": r.get("terminal"),
        "generic_terminal": g.get("terminal"),
        "native_terminal": n.get("terminal"),
        "R1_star": p.get("R1_star") if ok else None,
        "strict_puncturing_exception_class_indices": p.get("strict_puncturing_exception_class_indices") if ok else None,
        "ONE_CORRUPTION_CLASS_CONDITIONED_IDENTITY_AUTHORITY": bool(ok),
        "HARDWARE_MEASUREMENT_NOISE_MODEL": False,
        "STOCHASTIC_PHYSICAL_ERROR_RATE": False,
        "FAULT_TOLERANCE_THRESHOLD": False,
        "MINIMUM_FULL_FINITE_OPTIMUM_PROBES": False,
        "GENERIC_CODING_NOVELTY": False,
        "COMPILER_RUNTIME_ADVANTAGE": False,
        "physical_quantum_advantage_claim": False,
        "novelty_authority": False,
    }
    DUAL.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
