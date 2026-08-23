#!/usr/bin/env python3
"""QG-7d counterexample-first spectator-padding ablation."""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
Q=ROOT/'research/extensions/orion-q'; QG=ROOT/'research/extensions/orion-qg'
sys.path.insert(0,str(Q)); sys.path.insert(0,str(QG))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa:E402
import qg7c_classification as q7c  # noqa:E402

PARENT=QG/'QG7C_CLASSIFICATION_RESULTS.json'
PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG7D_PADDING_ABLATION_PROTOCOL_V1.md'
OUT=ROOT/'artifacts/orion-qg-qg7d-padding-ablation.json'
TOKEN='ORIONQG_QG7D_PAD='
X,Y,Z=1,2,3
POLICIES=(('COMMON_Z',(Z,Z,Z,Z,Z,Z)),('NO_COMMON_FACTOR',(X,Y,Z,X,Y,Z)),('PAIRWISE_MISMATCH',(X,Y,X,Z,Y,Z)))

def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def strip_common_z(k): return p10.mul(k,r6o._letter_key(Z,2))
def set_pad(k,le):
    base=strip_common_z(k)
    return p10.mul(base,r6o._letter_key(le,2)) if le else base

def apply_policy(tp,name,pads=None):
    flat=[tp[0][0],tp[0][1],tp[1][0],tp[1][1],tp[2][0],tp[2][1]]
    stripped=[strip_common_z(k) for k in flat]
    if name=='MINIMAL_NONZERO':
        seq=(X,Y,Z,X,Y,Z)
        out=[p10.mul(k,r6o._letter_key(seq[i],2)) if k==(0,0) else k for i,k in enumerate(stripped)]
    else:
        out=[set_pad(flat[i],pads[i]) for i in range(6)]
    return ((out[0],out[1]),(out[2],out[3]),(out[4],out[5]))

def jtp(tp): return [[list(a),list(b)] for a,b in tp]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,default=OUT); args=ap.parse_args()
    parent=json.loads(PARENT.read_text())
    rows=parent['t4b_pinned']['failing_verbatim_capped']
    if len(rows)!=40: raise AssertionError({'expected_40_rows':len(rows)})
    policies=list(POLICIES)+[('MINIMAL_NONZERO',None)]
    counters={'rows':0,'sandwich_failures':[],'dxx_witness_rows':0,'dxx_witness_failures':[],'replay_rows':0,'replay_failures':[]}
    gaps=[]; summary={}
    for pname,pads in policies:
        n_gaps=0; first=None; min_gap=0
        for i,row in enumerate(rows):
            base,feas,ref=q7c._realize_row(row,3)
            if not feas: raise AssertionError({'parent_row_not_feasible':i})
            tp=apply_policy(base,pname,pads)
            before=len(gaps)
            cxx,cdp1,fbp,fbpp,gap=q7c._eval_instance(tp,3,['qg7d',pname,i],gaps,counters)
            if gap<0:
                n_gaps+=1; min_gap=min(min_gap,int(gap))
                rec={'policy':pname,'row_index':i,'parent_census_row':row,'target_pairs':jtp(tp),'C_Dxx':cxx,'C_Dplus':cdp1,'f_Bprime':None if fbp>=q7c.INF else fbp,'f_Bsecond':None if fbpp>=q7c.INF else fbpp,'gap':int(gap),'new_gap_recorded':len(gaps)>before}
                if first is None: first=rec
        summary[pname]={'instances':len(rows),'strict_gap_count':n_gaps,'min_gap':min_gap,'first':first}
    positive=any(v['strict_gap_count'] for v in summary.values())
    gates={
        'protocol_bound':PROTOCOL.exists(),
        'parent_terminal':parent.get('terminal')=='QG7C_PARTIAL__L4B_OPEN',
        'parent_digest':parent.get('result_digest')=='0b127438dac9dc844a52176873eb5769a99ff52b34851d9c82c4b1feded656b6',
        'parent_t4b_census':parent['t4b_pinned']['failures_total']==135604 and parent['t4b_pinned']['worst_delta']==2,
        'row_count_40':len(rows)==40,
        'instances_160':counters['rows']==160,
        'no_sandwich_failures':not counters['sandwich_failures'],
        'no_dxx_witness_failures':not counters['dxx_witness_failures'],
        'no_replay_failures':not counters['replay_failures'],
    }
    terminal='QG7D_BTRIPLEPRIME_REGIME_FOUND__PADDING_ABLATION_EXACT_WITNESS' if positive and all(gates.values()) else ('QG7D_PADDING_ABLATION_NO_BTRIPLEPRIME_IN_FROZEN_ROWS__J5_REQUIRED' if all(gates.values()) else 'QG7D_PADDING_ABLATION_BINDING_FAILURE')
    out={'schema':'ORION.QG.QG7D.PaddingAblation.v1','issue':'SzeChunYiu/ORION#836','terminal':terminal,'protocol_sha256':sha(PROTOCOL),'parent_result_sha256':sha(PARENT),'policies':summary,'strict_gap_records':gaps,'counters':counters,'gates':gates,'all_gates':all(gates.values()),'all_n_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False,'protected_subject_read':False,'chemistry_sources_read':False}
    u=dict(out); out['result_digest']=hashlib.sha256(canonical(u).encode()).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical({'terminal':terminal,'result_digest':out['result_digest'],'gap_counts':{k:v['strict_gap_count'] for k,v in summary.items()}})); return 0
if __name__=='__main__': raise SystemExit(main())
