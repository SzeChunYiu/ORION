#!/usr/bin/env python3
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/'artifacts/orion-qg-qg14c-composition.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG14C_COMPOSITION_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg14c-generic.json'; TOKEN='ORIONQG_QG14C_GENERIC='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None); opts={'A':(0,1),'B':(1,0)}; rows={}
 for x,y in itertools.product(opts,repeat=2):
  local=opts[x][0]+opts[y][0]; demand=opts[x][1]+opts[y][1]; rows[(x,y)]=local+(5 if demand>=2 else 0)
 checks={'schema':a.get('schema')=='ORION.QG.QG14C.CompositionClosure.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'separable_controls':a['separable_theorem']['failures']==0 and a['separable_theorem']['holds'] is True,'coupled_costs':rows=={('A','A'):5,('A','B'):1,('B','A'):1,('B','B'):2},'independent_wrong':a['shared_resource_counterexample']['independent_wrong'] is True,'summary_recovers':a['shared_resource_counterexample']['coupling_aware_recovers_optimum'] is True,'bounded':a['claim_boundary'].startswith('bounded'),'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}; decision='ACCEPT_MIXED_CLOSURE' if all(checks.values()) and a.get('terminal')=='QG14_SEPARABLE_COMPOSITION_PROVED__HIDDEN_COUPLING_REFUTES_LOCAL_SELECTION__COUPLING_AWARE_SUMMARY_RECOVERS_CONTROL' else 'REJECT'; out={'schema':'ORION.QG.QG14C.Generic.v1','issue':'SzeChunYiu/ORION#844','decision':decision,'checks':checks,'all_checks':all(checks.values()),'terminal':a.get('terminal'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
