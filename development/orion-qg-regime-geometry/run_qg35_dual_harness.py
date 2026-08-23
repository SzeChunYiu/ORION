#!/usr/bin/env python3
"""Protected production/generic/native harness for QG-35 fair fixed baseline."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run(path,timeout=120):
 p=subprocess.run([sys.executable,path],cwd=ROOT,text=True,capture_output=True,timeout=timeout);print(p.stderr,end='',file=sys.stderr)
 if p.returncode:raise RuntimeError({'path':path,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 return p.stdout
def main():
 run('research/extensions/orion-qg/qg35_summary_conditioned_fixed.py');run('development/orion-qg-regime-geometry/qg35_generic_verify.py');run('development/orion-qg-regime-geometry/qg35_native_verify.py');s=json.loads((ROOT/'artifacts/orion-qg-qg35-summary-conditioned-fixed.json').read_text());g=json.loads((ROOT/'artifacts/orion-qg-qg35-generic-verification.json').read_text());n=json.loads((ROOT/'artifacts/orion-qg-qg35-native-verification.json').read_text());both=g.get('all_checks') is True and n.get('all_checks') is True;out={'schema':'ORIONQG.QG35.DualHarness.v1','terminal':s.get('terminal') if both else 'QG35_GENERIC_NATIVE_DISAGREEMENT','both_accept':both,'class_minima':s.get('class_minima') if both else None,'minimum_histogram':s.get('minimum_histogram') if both else None,'orbit_mass_minimum_histogram':s.get('orbit_mass_minimum_histogram') if both else None,'F_star':s.get('worst_case_class_conditioned_fixed_minimum') if both else None,'EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY':bool(both and s.get('EXACT_SUMMARY_CONDITIONED_FIXED_AUTHORITY') is True),'ADAPTIVE_MINIMAX_AUTHORITY':False,'STRICT_ADAPTIVITY_ADVANTAGE_AUTHORITY':False,'UNIVERSAL_FIXED_MINIMUM_REDERIVED':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'QG28_GLOBAL_STATE_MINIMALITY':False,'novelty_authority':False,'physical_quantum_advantage_claim':False};(ROOT/'artifacts/orion-qg-qg35-dual-harness.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
