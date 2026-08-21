#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/'artifacts/orion-qg-qg14c-composition.json'; GENERIC=ROOT/'artifacts/orion-qg-qg14c-generic.json'; OUT=ROOT/'artifacts/orion-qg-qg14c-native.json'; TOKEN='ORIONQG_QG14C_NATIVE='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); g=json.loads(GENERIC.read_text()); checks={'analyzer':a.get('all_gates') is True,'generic':g.get('decision')=='ACCEPT_MIXED_CLOSURE' and g.get('all_checks') is True,'terminal':a.get('terminal')=='QG14_SEPARABLE_COMPOSITION_PROVED__HIDDEN_COUPLING_REFUTES_LOCAL_SELECTION__COUPLING_AWARE_SUMMARY_RECOVERS_CONTROL','bounded':a.get('claim_boundary','').startswith('bounded'),'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}; decision='ACCEPT_MIXED_CLOSURE' if all(checks.values()) else 'REJECT'; out={'schema':'ORION.QG.QG14C.Native.v1','issue':'SzeChunYiu/ORION#844','decision':decision,'responsibility':'SEPARABLE_THEOREM_PLUS_COUPLING_REFUTATION' if decision.startswith('ACCEPT') else 'CANNOT_CHECK','checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'scientifically_closed':decision.startswith('ACCEPT'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
