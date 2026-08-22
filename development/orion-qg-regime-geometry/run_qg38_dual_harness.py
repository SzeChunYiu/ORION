#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts';SRC=ART/'orion-qg-qg38-observation-hierarchy.json';G=ART/'orion-qg-qg38-generic-verification.json';N=ART/'orion-qg-qg38-native-verification.json';D=ART/'orion-qg-qg38-dual-harness.json'
def run(path,*args):
 p=subprocess.run([sys.executable,str(ROOT/path),*map(str,args)],cwd=ROOT,text=True,capture_output=True);print(p.stdout,end='');
 if p.returncode: print(p.stderr,end='',file=sys.stderr);raise SystemExit(p.returncode)
def main():
 ART.mkdir(exist_ok=True);run(Path('research/extensions/orion-qg/qg38_observation_hierarchy.py'));run(Path('development/orion-qg-regime-geometry/qg38_generic_verify.py'));run(Path('development/orion-qg-regime-geometry/qg38_native_verify.py'));s=json.loads(SRC.read_text());g=json.loads(G.read_text());n=json.loads(N.read_text());ok=g.get('all_checks') is True and n.get('all_checks') is True and g.get('terminal')==n.get('terminal')==s.get('terminal');o={'schema':'ORIONQG.QG38.DualHarness.v1','terminal':s.get('terminal') if ok else 'QG38_GENERIC_NATIVE_DISAGREEMENT','both_accept':ok,'D_star':s.get('models',{}).get('D_star',{}).get('value') if ok else None,'F_star':s.get('models',{}).get('F_star',{}).get('value') if ok else None,'U_star':s.get('models',{}).get('U_star',{}).get('value') if ok else None,'STRICT_THREE_LEVEL_HIERARCHY_AUTHORITY':bool(ok and s.get('STRICT_THREE_LEVEL_HIERARCHY_AUTHORITY')),'HARDWARE_MEASUREMENT_MINIMUM':False,'MINIMUM_FULL_FINITE_OPTIMUM_PROBES':False,'COMPILER_OPTIMIZATION_COST_ADVANTAGE':False,'COMPILER_RUNTIME_ADVANTAGE':False,'GENERIC_ACTIVE_LEARNING_NOVELTY':False,'AUTONOMOUS_SKILL_SELECTION_AUTHORITY':False,'physical_quantum_advantage_claim':False,'novelty_authority':False};D.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(json.dumps(o,sort_keys=True));return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
