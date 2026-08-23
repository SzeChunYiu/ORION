#!/usr/bin/env python3
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; RESULT=ROOT/'artifacts/orion-qg-qg7d-information-closure.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG7D_INFORMATION_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg7d-information-generic.json'; TOKEN='ORIONQG_QG7D_INFO_GENERIC='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def mul(a,b):
 if a==0:return b
 if b==0:return a
 if a==b:return 0
 return 6-a-b
def w(a): return 0 if a==0 else 1
def f3(a,b,c): return 1 if a==b==c!=0 else w(a)+w(b)+w(c)
def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None); hist={}; examples={}; total=0
 for vals in itertools.product(range(4),repeat=6):
  a0,b0,c0,a1,b1,c1=vals; before=f3(a0,mul(b0,3),c0)+f3(a1,mul(b1,1),c1); after=f3(a0,b0,c0)+f3(a1,b1,c1); d=after-before; hist[d]=hist.get(d,0)+1; examples.setdefault(d,list(vals)); total+=1
 checks={'schema':a.get('schema')=='ORION.QG.QG7D.InformationClosure.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'pp_failures':a.get('pp_parent_failures')==32556,'domain':total==4096==a['hidden_home_test']['domain_size'],'histogram':{str(k):v for k,v in sorted(hist.items())}==a['hidden_home_test']['delta_histogram'],'range':min(hist)==-4 and max(hist)==4 and a['hidden_home_test']['delta_min']==-4 and a['hidden_home_test']['delta_max']==4,'all_values':set(hist)==set(range(-4,5)),'visible_state_no_home':a.get('visible_t4b_state_fields')==['case','ja','R_b','R_a','p','coreB','envB','coreA','envA'],'cannot_check_scope':a['scientific_disposition']['all_n_identity']=='UNPROVED_CANNOT_CHECK_FROM_CURRENT_PARENT_QUOTIENT','no_theorem':a.get('all_n_theorem_authority') is False,'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 decision='ACCEPT_CANNOT_CHECK' if all(checks.values()) and a.get('terminal')=='QG7D_CANNOT_CHECK_ALL_N_PINNED_CLOSURE__PP_HIDDEN_HOME_ENVIRONMENT_NOT_IN_PARENT_STATE__PADDING_ABLATION_NEGATIVE' else 'REJECT'; out={'schema':'ORION.QG.QG7D.InformationGeneric.v1','issue':'SzeChunYiu/ORION#836','decision':decision,'checks':checks,'all_checks':all(checks.values()),'reconstructed_delta_histogram':{str(k):v for k,v in sorted(hist.items())},'terminal':a.get('terminal'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
