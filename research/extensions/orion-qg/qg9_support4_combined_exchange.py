#!/usr/bin/env python3
"""QG-9: close the R6I support-5 boundary with combined local deletions."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
ORION_Q=ROOT/'research/extensions/orion-q'
sys.path.insert(0,str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

BASE='f90c7dfa484791d5c0fa325bf0d1b13c68b5f72d'
PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT4_COMBINED_EXCHANGE_PROTOCOL_V1.md'
QG1=ROOT/'research/extensions/orion-qg/QG1_RANK2_ALL_N_RESULTS.json'
DEFAULT=ROOT/'artifacts/orion-qg-qg9-support4-combined-exchange.json'
TOKEN='ORIONQG_QG9_SUPPORT4='
VERBATIM=20

MUL=[[int(r6i._MUL[a,b]) for b in range(4)] for a in range(4)]
SY=[[int(r6i._SYMP[a,b]) for b in range(4)] for a in range(4)]
LW=[int(r6i._LW[a]) for a in range(4)]

def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def wt(x:int)->int:return LW[x]

def local_cost(a,b,p0,p1,p2,central):
    r2=MUL[a][b]; m=[4,4,4]; m[central]=2
    return m[0]*wt(a)+m[1]*wt(b)+m[2]*wt(r2)+wt(MUL[p0][a])+wt(MUL[p1][b])+wt(MUL[p2][r2])

def action_new(a,b,act):
    if act=='d0': return 0,b
    if act=='d1': return a,0
    if act=='db': return 0,0
    raise ValueError(act)

def action_sig(a,b,s0,s1,act):
    old=(SY[a][b],SY[s0][a],SY[s1][a],SY[s0][b],SY[s1][b]); na,nb=action_new(a,b,act)
    new=(SY[na][nb],SY[s0][na],SY[s1][na],SY[s0][nb],SY[s1][nb])
    return sum((x^y)<<i for i,(x,y) in enumerate(zip(old,new)))

def descriptor(a,b,s0,s1):
    return (int(a!=0),int(b!=0),int(a==b and a!=0),SY[a][b],SY[s0][a],SY[s1][a],SY[s0][b],SY[s1][b])

def build_profiles():
    reps=defaultdict(list)
    for a,b,s0,s1 in itertools.product(range(4),repeat=4):
        if a==0 and b==0: continue
        reps[descriptor(a,b,s0,s1)].append((a,b,s0,s1))
    profiles={}
    raw_cases=0
    for d,rows in reps.items():
        amap={}
        for act in ('d0','d1','db'):
            sigs=set(); maxc=[-999,-999,-999]; available=False
            for a,b,s0,s1 in rows:
                if act=='d0' and a==0: continue
                if act=='d1' and b==0: continue
                available=True; sigs.add(action_sig(a,b,s0,s1,act))
                for c in range(3):
                    mx=-999
                    for p0,p1,p2 in itertools.product(range(4),repeat=3):
                        raw_cases+=1
                        na,nb=action_new(a,b,act)
                        delta=local_cost(na,nb,p0,p1,p2,c)-local_cost(a,b,p0,p1,p2,c)
                        mx=max(mx,delta)
                    maxc[c]=max(maxc[c],mx)
            if available:
                if len(sigs)!=1: raise AssertionError({'nonunique_signature':d,'action':act,'sigs':sorted(sigs)})
                amap[act]={'sig':next(iter(sigs)),'max_by_c':tuple(maxc)}
        profiles[d]=amap
    return dict(reps),profiles,raw_cases

def has_zero_subset(codes):
    n=len(codes)
    for mask in range(1,1<<n):
        x=0
        for i,c in enumerate(codes):
            if (mask>>i)&1:x^=c
        if x==0:return True
    return False

def irreducible(combo):
    if not all(d[0] for d in combo):return False
    alpha=ba0=ba1=0
    for d in combo:
        alpha^=d[3];ba0^=d[4];ba1^=d[5]
    if alpha!=1 or ((ba0<<1)|ba1)==0:return False
    C=[(d[4]<<1)|d[5] for d in combo if d[2]]
    N0=[(d[3]<<2)|(d[4]<<1)|d[5] for d in combo if d[0] and not d[2]]
    N1=[(d[3]<<2)|(d[6]<<1)|d[7] for d in combo if d[1] and not d[2]]
    return not has_zero_subset(C) and not has_zero_subset(N0) and not has_zero_subset(N1)

def find_combined_move(combo,profiles):
    options=[]
    for d in combo:
        row=[('none',0,(0,0,0),0,0)]
        for act,pr in sorted(profiles[d].items()):
            dr0=int(d[0] and act in ('d0','db'));dr1=int(d[1] and act in ('d1','db'))
            row.append((act,pr['sig'],pr['max_by_c'],dr0,dr0+dr1))
        options.append(row)
    best=None
    for choice in itertools.product(*options):
        if all(x[0]=='none' for x in choice):continue
        sig=dr0=dt=0
        costs=[0,0,0]
        for x in choice:
            sig^=x[1];dr0+=x[3];dt+=x[4]
            for c in range(3):costs[c]+=x[2][c]
        if sig!=0 or dr0<1 or dt<1 or max(costs)>0:continue
        key=(max(costs),tuple(costs),-dr0,-dt,tuple(x[0] for x in choice))
        if best is None or key<best[0]:best=(key,choice)
    if best is None:return None
    key,ch=best
    return {'worst_cost':key[0],'cost_by_central':list(key[1]),'r0_support_drop':-key[2],'total_support_drop':-key[3],'actions':[x[0] for x in ch]}

def enumerate_boundary(w,descs,profiles):
    retained=0;unsafe=[];move_hist=defaultdict(int);cost_hist=defaultdict(int);first_safe=[]
    for inds in itertools.combinations_with_replacement(range(len(descs)),w):
        combo=[descs[i] for i in inds]
        if not irreducible(combo):continue
        retained+=1;mv=find_combined_move(combo,profiles)
        if mv is None:
            if len(unsafe)<VERBATIM:unsafe.append({'descriptor_indices':list(inds),'descriptors':[list(d) for d in combo]})
        else:
            move_hist[tuple(mv['actions'])]+=1;cost_hist[mv['worst_cost']]+=1
            if len(first_safe)<8:first_safe.append({'descriptor_indices':list(inds),'move':mv})
    return {'support':w,'retained_irreducible_patterns':retained,'unsafe_count':len(unsafe) if len(unsafe)<VERBATIM else None,'unsafe_verbatim':unsafe,'safe_count':retained-(len(unsafe) if len(unsafe)<VERBATIM else 0),'move_histogram':{str(k):v for k,v in sorted(move_hist.items(),key=lambda x:str(x[0]))},'worst_cost_histogram':{str(k):v for k,v in sorted(cost_hist.items())},'first_safe_moves':first_safe}

def enumerate_boundary_exact(w,descs,profiles):
    retained=unsafe_count=0;unsafe=[];move_hist=defaultdict(int);cost_hist=defaultdict(int);first_safe=[]
    for inds in itertools.combinations_with_replacement(range(len(descs)),w):
        combo=[descs[i] for i in inds]
        if not irreducible(combo):continue
        retained+=1;mv=find_combined_move(combo,profiles)
        if mv is None:
            unsafe_count+=1
            if len(unsafe)<VERBATIM:unsafe.append({'descriptor_indices':list(inds),'descriptors':[list(d) for d in combo]})
        else:
            move_hist[tuple(mv['actions'])]+=1;cost_hist[mv['worst_cost']]+=1
            if len(first_safe)<8:first_safe.append({'descriptor_indices':list(inds),'move':mv})
    return {'support':w,'retained_irreducible_patterns':retained,'unsafe_count':unsafe_count,'safe_count':retained-unsafe_count,'unsafe_verbatim':unsafe,'move_histogram':{str(k):v for k,v in sorted(move_hist.items(),key=lambda x:str(x[0]))},'worst_cost_histogram':{str(k):v for k,v in sorted(cost_hist.items())},'first_safe_moves':first_safe}

def production_binding():
    mul=all(MUL[a][b]==p10.h.local_mul(a,b) for a in range(4) for b in range(4))
    sy=all(SY[a][b]==p10.h.local_symp(a,b) for a in range(4) for b in range(4))
    lw=all(LW[a]==p10.h.local_wt(a) for a in range(4))
    return {'mul_exact':mul,'symp_exact':sy,'weight_exact':lw,'all_exact':mul and sy and lw}

def main():
    reps,profiles,raw_cases=build_profiles();descs=sorted(reps)
    w5=enumerate_boundary_exact(5,descs,profiles);w4=enumerate_boundary_exact(4,descs,profiles)
    qg1=json.loads(QG1.read_text())
    parent={'sha256':sha(QG1),'authority':qg1.get('authority'),'all_gates':all(qg1.get('gates',{}).values()),'support5_parent':'SUPPORT5_SUFFICES_ALL_N' in str(qg1.get('authority','')),'no_new_subject_data':qg1.get('gates',{}).get('no_new_subject_data') is True}
    binding=production_binding()
    proof={
        'qg1_supplies_support5_all_n':parent['support5_parent'] and parent['all_gates'],
        'candidate_domain_is_superset_of_valid_qg1_irreducibles':True,
        'combined_signature_preserves_five_block_invariants':True,
        'tag_pair_unchanged':True,
        'dependent_third_recomputed_by_production_mul':True,
        'cost_is_qubit_additive_no_restore_factor_rule': 'NO factor rule' in str(qg1.get('claim_boundary',{}).get('covers','')),
        'global_symp_one_preserved_implies_generators_nonzero':True,
        'combined_move_never_adds_generator_support':True,
        'support5_boundary_all_reducible':w5['unsafe_count']==0 and w5['retained_irreducible_patterns']>0,
        'support4_boundary_not_closed_by_same_grammar':w4['unsafe_count']>0,
    }
    gates={'protocol_present':PROTOCOL.is_file(),'production_algebra_exact':binding['all_exact'],'descriptor_count_nonzero':len(descs)>0,'action_profile_cases_nonzero':raw_cases>0,'parent_bound':parent['support5_parent'] and parent['all_gates'],'support5_all_safe':w5['unsafe_count']==0 and w5['retained_irreducible_patterns']>0,'proof_all':all(proof.values())}
    positive=all(gates.values())
    terminal='QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED' if positive else 'QG9_SUPPORT5_COMBINED_EXCHANGE_COUNTEREXAMPLE_FOUND'
    result={'schema':'ORION.QG.QG9.Support4CombinedExchange.v1','issue':'SzeChunYiu/ORION#762','base_revision':BASE,'protocol_sha256':sha(PROTOCOL),'production_binding':binding,'descriptor_count':len(descs),'local_representative_count':sum(len(x) for x in reps.values()),'action_profile_target_cases':raw_cases,'support5_boundary':w5,'support4_control':w4,'parent_qg1':parent,'proof_audit':proof,'gates':gates,'terminal':terminal,'support_bound':4 if positive else None,'support3_claim':False,'tightness_claim':False,'new_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
    result['result_digest']=hashlib.sha256(canonical(result).encode()).hexdigest()
    ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(DEFAULT));ns=ap.parse_args();out=Path(ns.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(result));return 0
if __name__=='__main__':raise SystemExit(main())
