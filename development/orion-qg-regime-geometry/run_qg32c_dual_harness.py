#!/usr/bin/env python3
"""Protected dual/native harness for QG-32c independent MITM replication."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run(args):
 p=subprocess.run([sys.executable,*args],cwd=ROOT,text=True,capture_output=True,timeout=120);print(p.stderr,end="",file=sys.stderr)
 if p.returncode:raise RuntimeError({"args":args,"returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr})
 return p.stdout

def main():
 run(["research/extensions/orion-qg/qg32c_mitm_replication.py"]);run(["development/orion-qg-regime-geometry/qg32c_generic_verify.py"]);run(["development/orion-qg-regime-geometry/qg32c_native_verify.py"])
 s=json.loads((ROOT/"artifacts/orion-qg-qg32c-mitm-replication.json").read_text());g=json.loads((ROOT/"artifacts/orion-qg-qg32c-generic-verification.json").read_text());n=json.loads((ROOT/"artifacts/orion-qg-qg32c-native-verification.json").read_text());both=g.get("all_checks") is True and n.get("all_checks") is True;out={"schema":"ORIONQG.QG32C.DualHarness.v1","terminal":s.get("terminal") if both else "QG32C_GENERIC_NATIVE_DISAGREEMENT","both_accept":both,"EXISTS_SEPARATOR_AT_MOST_4":s.get("EXISTS_SEPARATOR_AT_MOST_4") if both else None,"MINIMUM_FIXED_PROBE_CARDINALITY":5 if both and s.get("terminal")=="QG32C_INDEPENDENT_REPLICATION_CONFIRMS_NO_FOUR_PROBE_SEPARATOR" else None,"MINIMUM_FIXED_PROBE_CARDINALITY_AUTHORITY":bool(both and s.get("terminal")=="QG32C_INDEPENDENT_REPLICATION_CONFIRMS_NO_FOUR_PROBE_SEPARATOR"),"ADAPTIVE_TREE_OPTIMALITY":False,"MINIMUM_FULL_FINITE_OPTIMUM_PROBES":False,"HARDWARE_MEASUREMENT_MINIMUM":False,"QG28_GLOBAL_STATE_MINIMALITY":False,"novelty_authority":False,"physical_quantum_advantage_claim":False};(ROOT/"artifacts/orion-qg-qg32c-dual-harness.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
