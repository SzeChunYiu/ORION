#!/usr/bin/env python3
"""QG-9 V5: prospectively search obstruction-derived n=2 instances for support-2 tightness."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT=Path(__file__).resolve().parents[3]
ORION_Q=ROOT/'research/extensions/orion-q'
ORION_QG=ROOT/'research/extensions/orion-qg'
sys.path.insert(0,str(ORION_Q));sys.path.insert(0,str(ORION_QG))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import qg1_rank2_all_n as qg1  # noqa: E402
import qg9_support4_combined_exchange as v2  # noqa: E402
import qg9_support3_relabel_exchange as v3  # noqa: E402
import qg9_support2_full_acceptance as v4  # noqa: E402

BASE='a80dbd57d9124f058de7465a13de8c69416c368b'
PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT2_TIGHTNESS_PROTOCOL_V1.md'
PARENT_RESULT=ROOT/'research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json'
PARENT_RECEIPT=ROOT/'development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json'
DEFAULT=ROOT/'artifacts/orion-qg-qg9-support2-tightness.json'
TOKEN='ORIONQG_QG9_TIGHTNESS='
N=2
FAST_BIND_SAMPLE=16

def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def keyj(k):return [int(k[0]),int(k[1])]
def keytuple(k):return (int(k[0]),int(k[1]))
def labels(s0,s1,r0,r1):return (2*p10.symp(s0,r0)+p10.symp(s1,r0),2*p10.symp(s0,r1)+p10.symp(s1,r1))
def frame_triple(r0,r1):return (r0,r1,p10.mul(r0,r1))

def obstruction_blocks():
    states,actions,by_desc,_=v3.build_types();parent_reps,parent_profiles,_=v2.build_profiles();descs=sorted(parent_reps)
    _ret,surv=v3.parent_survivors(2,descs,parent_profiles)
    blocks={};type_cases=0;concrete_cases=0
    for inds in surv:
        combo=[descs[i] for i in inds]
        if not v4.descriptor_acceptance(combo)['accepted']:continue
        for type_keys in itertools.product(*[by_desc[d] for d in combo]):
            if v3.safe_profile_move(type_keys,actions) is not None:continue
            type_cases+=1
            for cols in itertools.product(*[sorted(states[k]) for k in type_keys]):
                concrete_cases+=1
                r0=p10.key_from_codes([cols[q][0] for q in range(N)]);r1=p10.key_from_codes([cols[q][1] for q in range(N)])
                s0=p10.key_from_codes([cols[q][2] for q in range(N)]);s1=p10.key_from_codes([cols[q][3] for q in range(N)])
                c0,c1=labels(s0,s1,r0,r1)
                if p10.symp(r0,r1)!=1 or c0 not in (1,2,3) or c1 not in (1,2,3) or c0==c1:raise AssertionError({'invalid_concrete_obstruction':[cols,c0,c1]})
                bkey=(keytuple(r0),keytuple(r1),keytuple(s0),keytuple(s1))
                blocks[bkey]={'R0':keyj(r0),'R1':keyj(r1),'S0':keyj(s0),'S1':keyj(s1),'labels':[c0,c1],'frame_support':[p10.wt(r0),p10.wt(r1)],'source_descriptor_indices':list(inds)}
    ordered=[blocks[k] for k in sorted(blocks)]
    return ordered,{'accepted_unsafe_type_cases':type_cases,'concrete_realizations_before_dedup':concrete_cases,'unique_blocks':len(ordered)}

def block_key(b):return (tuple(b['R0']),tuple(b['R1']),tuple(b['S0']),tuple(b['S1']))
def group_key(b):return (tuple(b['S0']),tuple(b['S1']),tuple(b['labels']))
def askey(v):return (int(v[0]),int(v[1]))

def candidate_pairs(blocks):
    pairs=[]
    for i in range(len(blocks)):pairs.append((i,i,'SELF'))
    groups=defaultdict(list)
    for i,b in enumerate(blocks):groups[group_key(b)].append(i)
    for g in sorted(groups):
        ids=sorted(groups[g],key=lambda i:block_key(blocks[i]))
        for i,j in itertools.combinations(ids,2):pairs.append((i,j,'CROSS'))
    return pairs

def defect_key(q,letter):
    codes=[0,0];codes[q]=letter;return p10.key_from_codes(codes)
def apply_defect(targets,branch,q,letter):
    out=list(targets);out[branch]=p10.mul(out[branch],defect_key(q,letter));return tuple(out)
def nonzero_targets(ts):return all(t!=(0,0) for t in ts)

def template_instances(ba,bb,family):
    ra0,ra1=askey(ba['R0']),askey(ba['R1']);rb0,rb1=askey(bb['R0']),askey(bb['R1']);ta=frame_triple(ra0,ra1);tb=frame_triple(rb0,rb1)
    if family=='IDENTITY_RESTORE':
        yield ta,tb,{'family':family};return
    for branch in range(3):
        for q in range(2):
            for letter in (1,2,3):
                if family=='ONE_DEFECT_A':ca,cb=apply_defect(ta,branch,q,letter),tb
                elif family=='ONE_DEFECT_B':ca,cb=ta,apply_defect(tb,branch,q,letter)
                elif family=='MATCHED_DEFECT':ca,cb=apply_defect(ta,branch,q,letter),apply_defect(tb,branch,q,letter)
                else:raise ValueError(family)
                if nonzero_targets(ca) and nonzero_targets(cb):yield ca,cb,{'family':family,'branch':branch,'qubit':q,'letter':letter}

def serialize_targets(ts):return [keyj(t) for t in ts]
def pairtables_binding(tables):
    rows={}
    for name,(n,ta,tb) in r6i.HOSTILE_PANELS.items():
        if n!=2:continue
        c=tables.capped_costs(tuple(ta),tuple(tb),(2,))[2];dp=int(r6i.shared_tag_exact(ta,tb,2)['C_shared']);rows[name]={'cap2':int(c),'production_dp':dp,'pass':int(c)==dp}
    return {'rows':rows,'all_pass':bool(rows) and all(x['pass'] for x in rows.values())}

class FastCaps:
    """Exact cached min-plus evaluation over canonical QG-1 PairTables data."""
    def __init__(self,tables):
        self.t=tables
        self.idx={cap:np.flatnonzero(tables.pair_max_wt<=cap) for cap in (1,2)}
        self.tag={cap:tables.best_tag[np.ix_(self.idx[cap],self.idx[cap])] for cap in (1,2)}
        self.a_cache={};self.b_cache={}
    @staticmethod
    def _key(ts):return tuple((int(t[0]),int(t[1])) for t in ts)
    def _a(self,ts,cap):
        k=(cap,self._key(ts))
        if k not in self.a_cache:
            rest=np.array([sum(p10.wt(p10.mul(ts[i],rs[i])) for i in range(3)) for rs in self.t.rs],dtype=np.int64)
            self.a_cache[k]=(self.t.uanti_min+rest)[self.idx[cap]]
        return self.a_cache[k]
    def _bh(self,ts,cap):
        k=(cap,self._key(ts))
        if k not in self.b_cache:
            rest=np.array([min(sum(p10.wt(p10.mul(ts[perm[i]],rs[i])) for i in range(3)) for perm in qg1.PERMS) for rs in self.t.rs],dtype=np.int64)
            b=(self.t.uanti_min+rest)[self.idx[cap]]
            self.b_cache[k]=(self.tag[cap]+b[None,:]).min(axis=1)
        return self.b_cache[k]
    def caps(self,ta,tb):
        return {cap:int((self._a(ta,cap)+self._bh(tb,cap)).min()) for cap in (1,2)}

def main():
    parent=json.loads(PARENT_RESULT.read_text());receipt=json.loads(PARENT_RECEIPT.read_text())
    if parent.get('terminal')!='QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED' or receipt.get('terminal')!=parent.get('terminal') or receipt.get('both_accept') is not True:raise AssertionError('parent support2 theorem not protected')
    blocks,bmeta=obstruction_blocks();pairs=candidate_pairs(blocks)
    generator={'blocks':blocks,'block_metadata':bmeta,'pair_count':len(pairs),'pairs':pairs,'template_families':['IDENTITY_RESTORE','ONE_DEFECT_A','ONE_DEFECT_B','MATCHED_DEFECT']}
    generator_digest=hashlib.sha256(canonical(generator).encode()).hexdigest()
    tables=qg1.PairTables(2);binding=pairtables_binding(tables)
    if not binding['all_pass']:raise AssertionError({'qg1_pairtables_binding_failed':binding})
    fast=FastCaps(tables);fast_bind_rows=[]
    tested=0;selected=None;family_counts={}
    for family in generator['template_families']:
        fc=0
        for i,j,kind in pairs:
            for ta,tb,tmeta in template_instances(blocks[i],blocks[j],family):
                tested+=1;fc+=1;caps=fast.caps(ta,tb);c1=int(caps[1]);c2=int(caps[2])
                if len(fast_bind_rows)<FAST_BIND_SAMPLE:
                    ref=tables.capped_costs(ta,tb,(1,2));row={'candidate_index':tested,'fast':[c1,c2],'canonical':[int(ref[1]),int(ref[2])],'pass':c1==int(ref[1]) and c2==int(ref[2])};fast_bind_rows.append(row)
                    if not row['pass']:raise AssertionError({'fast_cap_binding_failed':row})
                if c2<c1:
                    ref=tables.capped_costs(ta,tb,(1,2))
                    if c1!=int(ref[1]) or c2!=int(ref[2]):raise AssertionError({'selected_fast_cap_binding_failed':[c1,c2,int(ref[1]),int(ref[2])]})
                    selected={'block_indices':[i,j],'pair_kind':kind,'block_A':blocks[i],'block_B':blocks[j],'targets_A':serialize_targets(ta),'targets_B':serialize_targets(tb),'template':tmeta,'C_cap1':c1,'C_cap2':c2,'gap':c1-c2,'canonical_caps_confirmed':True};break
            if selected:break
        family_counts[family]=fc
        if selected:break
    production=None
    if selected:
        ta=tuple(askey(x) for x in selected['targets_A']);tb=tuple(askey(x) for x in selected['targets_B']);w=r6i.shared_tag_exact(ta,tb,2)
        production={'C_shared':int(w['C_shared']),'relative_B_permutation':w['relative_B_permutation'],'central_A':w['central_A'],'central_B':w['central_B'],'RA':w['RA'],'RB':w['RB'],'S0':w['S0'],'S1':w['S1'],'labels':w['labels'],'checks':w['checks'],'independent_generator_supports':[p10.wt(tuple(w['RA'][0])),p10.wt(tuple(w['RA'][1])),p10.wt(tuple(w['RB'][0])),p10.wt(tuple(w['RB'][1]))]}
    positive=selected is not None and production is not None and production['C_shared']==selected['C_cap2'] and all(production['checks'].values()) and selected['C_cap2']<selected['C_cap1']
    terminal='QG9_SUPPORT2_TIGHT_WITNESS_MACHINE_VERIFIED' if positive else 'QG9_NO_SUPPORT2_TIGHT_WITNESS_IN_FROZEN_INVERSE_PANEL'
    acceleration={'method':'EXACT_MIN_PLUS_CACHE_OVER_QG1_PAIRTABLES','canonical_bind_sample':fast_bind_rows,'canonical_bind_all_pass':all(r['pass'] for r in fast_bind_rows),'a_cache_entries':len(fast.a_cache),'b_cache_entries':len(fast.b_cache),'scientific_order_unchanged':True}
    result={'schema':'ORION.QG.QG9.Support2Tightness.v1','issue':'SzeChunYiu/ORION#795','base_revision':BASE,'protocol_sha256':sha(PROTOCOL),'parent_result_sha256':sha(PARENT_RESULT),'parent_receipt_sha256':sha(PARENT_RECEIPT),'candidate_generator_digest_before_scoring':generator_digest,'candidate_generator_summary':{'block_metadata':bmeta,'unique_blocks':len(blocks),'pair_count':len(pairs),'template_families':generator['template_families']},'qg1_pairtables_binding':binding,'exact_acceleration':acceleration,'candidates_tested':tested,'family_candidates_tested':family_counts,'selected':selected,'production_referee':production,'terminal':terminal,'tightness_authority':bool(positive),'support1_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False}
    result['result_digest']=hashlib.sha256(canonical(result).encode()).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(DEFAULT));ns=ap.parse_args();p=Path(ns.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(result));return 0
if __name__=='__main__':raise SystemExit(main())
