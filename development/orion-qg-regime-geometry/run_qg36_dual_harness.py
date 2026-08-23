#!/usr/bin/env python3
"""Protected receipt-only production/generic/native harness for QG-36."""
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def run(path):
 p=subprocess.run([sys.executable,path],cwd=ROOT,text=True,capture_output=True,timeout=60);print(p.stderr,end='',file=sys.stderr)
 if p.returncode:raise RuntimeError({'path':path,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 return p.stdout
def main():
 run('research/extensions/orion-qg/qg36_fair_adaptivity_composition.py');run('development/orion-qg-regime-geometry/qg36_generic_verify.py');run('development/orion-qg-regime-geometry/qg36_native_verify.py');s=json.loads((ROOT/'artifacts/orion-qg-qg36-fair-adaptivity-composition.json').read_text());g=json.loads((ROOT/'artifacts/orion-qg-qg36-generic-verification.json').read_text());n=json.loads((ROOT/'artifacts/orion-qg-qg36-native-verification.json').read_text());both=g.get('all_checks') is True and n.get('all_checks') is True;out={'schema':'ORIONQG.QG36.DualHarness.v1','terminal':s.get('terminal') if both else 'QG36_GENERIC_NATIVE_DISAGREEMENT','both_accept':both,'D_star':s.get('D_star') if both else None,'F_star':s.get('F_star') if both else None,'pointwise_violation_count':s.get('pointwise_violation_count') if both else None,'strict_improvement_class_count':len(s.get('strict_improvement_class_indices',[])) if both else None,'TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT':bool(both and s.get('TARE_POSTSUMMARY_ADAPTIVITY_STRICTLY_REDUCES_WORST_CASE_OBSERVATION_COUNT') is True),'EXACT_FAIR_FIXED_VS_ADAPTIVE_COMPARISON_AUTHORITY':bool(both and s.get('EXACT_FAIR_FIXED_VS_ADAPTIVE_COMPARISON_AUTHORITY') is True),'COMPILER_OPTIMIZATION_COST_ADVANTAGE':False,'HARDWARE_MEASUREMENT_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'GENERIC_ADAPTIVE_TESTING_NOVELTY':False,'AUTONOMOUS_SKILL_SELECTION_AUTHORITY':False,'physical_quantum_advantage_claim':False};(ROOT/'artifacts/orion-qg-qg36-dual-harness.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
