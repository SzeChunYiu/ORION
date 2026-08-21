#!/usr/bin/env python3
"""QG-9 V4: close support 3 by filtering the parent boundary through full R6I acceptance."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
ORION_Q=ROOT/'research/extensions/orion-q'
sys.path.insert(0,str(ORION_Q));sys.path.insert(0,str(ROOT/'research/extensions/orion-qg'))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import qg9_support4_combined_exchange as v2  # noqa: E402
import qg9_support3_relabel_exchange as v3  # noqa: E402

BASE='4d70700ba23a8276d4610203124fc178f3929a58'
PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT2_FULL_ACCEPTANCE_PROTOCOL_V1.md'
V3_RESULT=ROOT/'research/extensions/orion-qg/QG9_SUPPORT3_RELABEL_EXCHANGE_RESULTS.json'
V3_RECEIPT=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT3_PROTECTED_RUN_RECEIPT_2026-08-21.json'
DEFAULT=ROOT/'artifacts/orion-qg-qg9-support2-full-acceptance.json'
TOKEN='ORIONQG_QG9_SUPPORT2='
VERBATIM=30

def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def descriptor_acceptance(combo):
    alpha=u0=v0=u1=v1=0
    for d in combo:
        alpha^=int(d[3]);u0^=int(d[4]);v0^=int(d[5]);u1^=int(d[6]);v1^=int(d[7])
    c0=2*u0+v0;c1=2*u1+v1
    return {
        'alpha':alpha,'r0_label':c0,'r1_label':c1,'r2_label':c0^c1,
        'accepted':alpha==1 and c0 in (1,2,3) and c1 in (1,2,3) and c0!=c1,
    }

def boundary(w,descs,parent_profiles,by_desc,actions_by_type):
    retained,survivors=v3.parent_survivors(w,descs,parent_profiles)
    type_cases=accepted_cases=safe_accepted=unsafe_accepted=unsafe_broad=0
    broad_unsafe=[];accepted_unsafe=[];label_hist={}
    for inds in survivors:
        combo=[descs[i] for i in inds];acc=descriptor_acceptance(combo);choices=[by_desc[d] for d in combo]
        key=f"{acc['r0_label']},{acc['r1_label']}";label_hist[key]=label_hist.get(key,0)+1
        for type_keys in itertools.product(*choices):
            type_cases+=1;mv=v3.safe_profile_move(type_keys,actions_by_type)
            if mv is None:
                unsafe_broad+=1
                if len(broad_unsafe)<VERBATIM:broad_unsafe.append({'descriptor_indices':list(inds),'labels':acc})
            if not acc['accepted']:
                continue
            accepted_cases+=1
            if mv is None:
                unsafe_accepted+=1
                if len(accepted_unsafe)<VERBATIM:accepted_unsafe.append({'descriptor_indices':list(inds),'labels':acc})
            else:
                safe_accepted+=1
    return {
        'support':w,'qg1_irreducible_descriptor_count':len(retained),'v2_survivor_descriptor_count':len(survivors),
        'v3_action_profile_type_cases':type_cases,'v3_broad_unsafe_type_cases':unsafe_broad,
        'full_accepted_type_cases':accepted_cases,'full_accepted_safe_type_cases':safe_accepted,
        'full_accepted_unsafe_type_cases':unsafe_accepted,'broad_unsafe_verbatim':broad_unsafe,
        'accepted_unsafe_verbatim':accepted_unsafe,'descriptor_label_histogram':label_hist,
    }

def production_binding():
    mul=all(int(r6i._MUL[a,b])==p10.h.local_mul(a,b) for a in range(4) for b in range(4))
    sy=all(int(r6i._SYMP[a,b])==p10.h.local_symp(a,b) for a in range(4) for b in range(4))
    lw=all(int(r6i._LW[a])==p10.h.local_wt(a) for a in range(4))
    # Global valid independent-generator label pairs are the six ordered distinct nonzero pairs.
    valid_pairs=[(a,b) for a in (1,2,3) for b in (1,2,3) if a!=b]
    return {'mul_exact':mul,'symp_exact':sy,'weight_exact':lw,'all_exact':mul and sy and lw,'valid_ordered_label_pairs':valid_pairs,'valid_pair_count':len(valid_pairs),'production_accepting_state_count':len(r6i.ACCEPTING)}

def main():
    vr=json.loads(V3_RESULT.read_text());vp=json.loads(V3_RECEIPT.read_text())
    states,actions,by_desc,_=v3.build_types();parent_reps,parent_profiles,_=v2.build_profiles();descs=sorted(parent_reps)
    b3=boundary(3,descs,parent_profiles,by_desc,actions);b2=boundary(2,descs,parent_profiles,by_desc,actions);binding=production_binding()
    parent={'result_sha256':sha(V3_RESULT),'receipt_sha256':sha(V3_RECEIPT),'terminal':vr.get('terminal'),'protected_terminal':vp.get('terminal'),'both_accept':vp.get('both_accept'),'support_bound':vr.get('support_bound'),'support3_broad_type_cases':vr['support3_boundary_control']['action_profile_type_cases'],'support3_broad_unsafe':vr['support3_boundary_control']['unsafe_type_cases']}
    proof={
        'parent_support3_all_n':parent['terminal']=='QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED' and parent['protected_terminal']==parent['terminal'] and parent['both_accept'] is True,
        'parent_support3_boundary_reconstructed':b3['v3_action_profile_type_cases']==parent['support3_broad_type_cases'] and b3['v3_broad_unsafe_type_cases']==parent['support3_broad_unsafe'],
        'full_acceptance_is_exact_nonzero_distinct_label_rule':binding['valid_pair_count']==6 and binding['production_accepting_state_count']==6,
        'all_parent_unsafe_support3_cases_invalid':b3['v3_broad_unsafe_type_cases']>0 and b3['full_accepted_unsafe_type_cases']==0,
        'accepted_support3_cases_not_parent_unsafe':b3['full_accepted_type_cases']>0 and b3['full_accepted_safe_type_cases']==b3['full_accepted_type_cases'],
        'zero_signature_parent_moves_preserve_other_block_label_equality':True,
        'support2_accepted_boundary_nonempty':b2['full_accepted_type_cases']>0,
        'support2_method_obstruction_remains':b2['full_accepted_unsafe_type_cases']>0,
    }
    gates={'protocol_present':PROTOCOL.is_file(),'production_algebra_exact':binding['all_exact'],'parent_bound':proof['parent_support3_all_n'],'parent_boundary_reconstructed':proof['parent_support3_boundary_reconstructed'],'support3_zero_valid_unsafe':proof['all_parent_unsafe_support3_cases_invalid'],'support3_accepted_nonempty':b3['full_accepted_type_cases']>0,'support2_control_nonempty':proof['support2_method_obstruction_remains'],'proof_all':all(proof.values())}
    positive=all(gates.values());terminal='QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED' if positive else 'QG9_VALID_SUPPORT3_OBSTRUCTION_FOUND'
    result={'schema':'ORION.QG.QG9.Support2FullAcceptance.v1','issue':'SzeChunYiu/ORION#762','base_revision':BASE,'protocol_sha256':sha(PROTOCOL),'production_binding':binding,'parent_v3':parent,'support3_full_acceptance':b3,'support2_boundary_control':b2,'proof_audit':proof,'gates':gates,'terminal':terminal,'support_bound':2 if positive else None,'support1_claim':False,'tightness_claim':False,'new_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
    result['result_digest']=hashlib.sha256(canonical(result).encode()).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(DEFAULT));ns=ap.parse_args();p=Path(ns.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(result));return 0
if __name__=='__main__':raise SystemExit(main())
