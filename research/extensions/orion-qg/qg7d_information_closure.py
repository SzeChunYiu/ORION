#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,inspect,itertools,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; QG=ROOT/'research/extensions/orion-qg'; sys.path.insert(0,str(QG))
import qg7c_classification as q7c  # noqa:E402
PARENT=QG/'QG7C_CLASSIFICATION_RESULTS.json'; PAD=QG/'QG7D_PADDING_ABLATION_RESULTS.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG7D_INFORMATION_CLOSURE_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg7d-information-closure.json'; TOKEN='ORIONQG_QG7D_INFO='
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args(); parent=json.loads(PARENT.read_text()); pad=json.loads(PAD.read_text())
 src_t4=inspect.getsource(q7c.t4b_pinned); src_real=inspect.getsource(q7c._realize_row)
 deltas={}; examples={}; total=0
 for vals in itertools.product(range(4),repeat=6):
  a0,b0,c0,a1,b1,c1=vals
  before=q7c.lf3(a0,q7c.lmul(b0,q7c.Z),c0)+q7c.lf3(a1,q7c.lmul(b1,q7c.X),c1)
  after=q7c.lf3(a0,b0,c0)+q7c.lf3(a1,b1,c1)
  d=after-before; deltas[d]=deltas.get(d,0)+1; examples.setdefault(d,list(vals)); total+=1
 pp_fail=parent['t4b_pinned']['failing_census']['PP_ja0_delta1']+parent['t4b_pinned']['failing_census']['PP_ja0_delta2']+parent['t4b_pinned']['failing_census']['PP_ja1_delta1']
 visible_fields=['case','ja','R_b','R_a','p','coreB','envB','coreA','envA']
 gates={'protocol':PROTOCOL.exists(),'parent_terminal':parent.get('terminal')=='QG7C_PARTIAL__L4B_OPEN','parent_total_failures':parent['t4b_pinned']['failures_total']==135604,'parent_worst2':parent['t4b_pinned']['worst_delta']==2,'pp_failures_32556':pp_fail==32556,'t4b_tensor_no_home_dimension':'np.full((64, 64, 64, 64)' in src_t4,'pp_realization_has_q2_home':'r6o._letter_key(Z, 2)' in src_real and 'r6o._letter_key(X, 2)' in src_real,'hidden_domain_4096':total==4096,'delta_span_pm4':min(deltas)==-4 and max(deltas)==4 and set(deltas)==set(range(-4,5)),'both_signs':any(d<0 for d in deltas) and any(d>0 for d in deltas),'padding_parent_negative':pad.get('terminal')=='QG7D_PADDING_ABLATION_NO_BTRIPLEPRIME_IN_FROZEN_ROWS__J5_REQUIRED' and pad.get('both_accept') is True and pad.get('total_instances')==160}
 terminal='QG7D_CANNOT_CHECK_ALL_N_PINNED_CLOSURE__PP_HIDDEN_HOME_ENVIRONMENT_NOT_IN_PARENT_STATE__PADDING_ABLATION_NEGATIVE' if all(gates.values()) else 'QG7D_INFORMATION_CLOSURE_BINDING_FAILED'
 out={'schema':'ORION.QG.QG7D.InformationClosure.v1','issue':'SzeChunYiu/ORION#836','terminal':terminal,'protocol_sha256':sha(PROTOCOL),'parent_sha256':sha(PARENT),'padding_sha256':sha(PAD),'visible_t4b_state_fields':visible_fields,'pp_parent_failures':pp_fail,'hidden_home_test':{'domain_size':total,'delta_histogram':{str(k):v for k,v in sorted(deltas.items())},'delta_min':min(deltas),'delta_max':max(deltas),'example_by_delta':{str(k):v for k,v in sorted(examples.items())}},'scientific_disposition':{'all_n_identity':'UNPROVED_CANNOT_CHECK_FROM_CURRENT_PARENT_QUOTIENT','btripleprime':'UNFOUND_IN_FROZEN_PADDING_ABLATION','future_reopen_requires':['expanded PP phantom-home environment in state quotient','or independent worst-case J5 bound dominating full hidden-home delta range']},'gates':gates,'all_gates':all(gates.values()),'scientifically_closed_under_stop_rules':all(gates.values()),'all_n_theorem_authority':False,'novelty_authority':False,'r6_authority':False,'physical_quantum_advantage_claim':False}; u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'pp_failures':pp_fail,'delta_range':[min(deltas),max(deltas)],'result_digest':out['result_digest']})); return 0
if __name__=='__main__': raise SystemExit(main())
