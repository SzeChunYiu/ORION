#!/usr/bin/env python3
"""Protected production/generic/native harness for QG-34 adaptive minimax depth."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run(path,timeout=120):
 p=subprocess.run([sys.executable,path],cwd=ROOT,text=True,capture_output=True,timeout=timeout);print(p.stderr,end='',file=sys.stderr)
 if p.returncode:raise RuntimeError({'path':path,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 return p.stdout
def main():
 run('research/extensions/orion-qg/qg34_adaptive_probe_tree.py');run('development/orion-qg-regime-geometry/qg34_generic_verify.py');run('development/orion-qg-regime-geometry/qg34_native_verify.py');s=json.loads((ROOT/'artifacts/orion-qg-qg34-adaptive-probe-tree.json').read_text());g=json.loads((ROOT/'artifacts/orion-qg-qg34-generic-verification.json').read_text());n=json.loads((ROOT/'artifacts/orion-qg-qg34-native-verification.json').read_text());both=g.get('all_checks') is True and n.get('all_checks') is True;out={'schema':'ORIONQG.QG34.DualHarness.v1','terminal':s.get('terminal') if both else 'QG34_GENERIC_NATIVE_DISAGREEMENT','both_accept':both,'worst_case_depth':s.get('worst_case_depth') if both else None,'depth_histogram':s.get('depth_histogram') if both else None,'orbit_mass_depth_histogram':s.get('orbit_mass_depth_histogram') if both else None,'ADAPTIVE_DEPTH_BELOW_QG32_CERTIFIED_FIXED_BASIS_LENGTH':s.get('ADAPTIVE_DEPTH_BELOW_QG32_CERTIFIED_FIXED_BASIS_LENGTH') if both else None,'EXACT_ADAPTIVE_MINIMAX_AUTHORITY':bool(both and s.get('EXACT_ADAPTIVE_MINIMAX_AUTHORITY') is True),'EXACT_FIXED_PROBE_MINIMUM_BOUND':False,'ADAPTIVITY_ADVANTAGE_OVER_EXACT_FIXED_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'QG28_GLOBAL_STATE_MINIMALITY':False,'novelty_authority':False,'physical_quantum_advantage_claim':False};(ROOT/'artifacts/orion-qg-qg34-dual-harness.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
