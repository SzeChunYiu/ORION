#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG14C_COMPOSITION_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg14c-composition.json'; TOKEN='ORIONQG_QG14C='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def separable():
 controls=[([3,1,4],[2,5]),([0,7],[6,2,3]),([5],[4,4,1])]; failures=0; rows=[]
 for a,b in controls:
  local=(min(a),min(b)); global_min=min(x+y for x in a for y in b); failures+=int(sum(local)!=global_min); rows.append({'A':a,'B':b,'local_min_sum':sum(local),'global_min':global_min})
 algebra='for every choices a_i, c_i(a_i)>=m_i:=min c_i, hence sum c_i(a_i)>=sum m_i; independent argmins attain equality'
 return {'algebraic_proof':algebra,'controls':rows,'failures':failures,'holds':failures==0}
def coupled():
 opts={'A':{'local':0,'demand':1},'B':{'local':1,'demand':0}}; rows=[]
 for x,y in itertools.product(opts,repeat=2):
  demand=opts[x]['demand']+opts[y]['demand']; penalty=5 if demand>=2 else 0; cost=opts[x]['local']+opts[y]['local']+penalty; rows.append({'choice':[x,y],'local_sum':opts[x]['local']+opts[y]['local'],'demand':demand,'penalty':penalty,'global_cost':cost})
 independent=['A','A']; mon=min(r['global_cost'] for r in rows); winners=[r['choice'] for r in rows if r['global_cost']==mon]; aware=min(rows,key=lambda r:(r['global_cost'],r['choice']))
 return {'rows':rows,'independent_local_choice':independent,'independent_global_cost':next(r['global_cost'] for r in rows if r['choice']==independent),'monolithic_optimum':mon,'monolithic_winners':winners,'independent_wrong':independent not in winners,'coupling_aware_summary':'total shared-resource demand','coupling_aware_chosen':aware['choice'],'coupling_aware_cost':aware['global_cost'],'coupling_aware_recovers_optimum':aware['global_cost']==mon}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args(); s=separable(); c=coupled(); gates={'protocol':PROTOCOL.exists(),'separable':s['holds'],'hidden_coupling_refutes':c['independent_wrong'],'summary_recovers':c['coupling_aware_recovers_optimum'],'expected_costs':{tuple(r['choice']):r['global_cost'] for r in c['rows']}=={('A','A'):5,('A','B'):1,('B','A'):1,('B','B'):2}}
 terminal='QG14_SEPARABLE_COMPOSITION_PROVED__HIDDEN_COUPLING_REFUTES_LOCAL_SELECTION__COUPLING_AWARE_SUMMARY_RECOVERS_CONTROL' if all(gates.values()) else 'QG14_COMPOSITION_CLOSURE_REFUTED_OR_BINDING_FAILED'; out={'schema':'ORION.QG.QG14C.CompositionClosure.v1','issue':'SzeChunYiu/ORION#844','terminal':terminal,'protocol_sha256':sha(PROTOCOL),'separable_theorem':s,'shared_resource_counterexample':c,'claim_boundary':'bounded theorem/counterexample control only; no universal interface compression claim','gates':gates,'all_gates':all(gates.values()),'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False}; u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'result_digest':out['result_digest'],'winners':c['monolithic_winners']})); return 0
if __name__=='__main__': raise SystemExit(main())
