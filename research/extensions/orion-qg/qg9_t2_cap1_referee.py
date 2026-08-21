#!/usr/bin/env python3
"""QG-9 T2 stage 2: exact support<=1 referee after sealed stage-1 candidates."""
from __future__ import annotations
import argparse, hashlib, itertools, json, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[3]; ORION_Q=ROOT/'research/extensions/orion-q'; sys.path.insert(0,str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
ISSUE='SzeChunYiu/ORION#803'; TOKEN='ORIONQG_QG9_T2_REFEREE='
DEFAULT_STAGE1=ROOT/'artifacts/orion-qg-qg9-t2-stage1.json'; DEFAULT_OUT=ROOT/'artifacts/orion-qg-qg9-t2-result.json'
INF=10**9

def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def key(x):return tuple(int(v) for v in x)
def wt(x):return p10.wt(x)

def all_keys(n=2):return [(x,z) for x in range(1<<n) for z in range(1<<n)]
def cap1_pairs():
    nz=[k for k in all_keys() if k!=(0,0) and wt(k)<=1]
    pairs=[(a,b) for a in nz for b in nz if p10.symp(a,b)==1]
    if len(pairs)!=12:raise AssertionError({'cap1_pair_count':len(pairs)})
    return pairs

def labels(s0,s1,a,b):
    c0=2*p10.symp(s0,a)+p10.symp(s1,a); c1=2*p10.symp(s0,b)+p10.symp(s1,b)
    return c0,c1

def tag_min(pair_a,pair_b):
    a0,a1=pair_a;b0,b1=pair_b;best=INF;witness=None
    for s0 in all_keys():
      for s1 in all_keys():
        la=labels(s0,s1,a0,a1);lb=labels(s0,s1,b0,b1)
        if la!=lb or la[0] not in (1,2,3) or la[1] not in (1,2,3) or la[0]==la[1]:continue
        c=2*(wt(s0)+wt(s1))
        row=(c,s0,s1,la)
        if witness is None or row<witness:witness=row;best=c
    return best,witness

def block_cost(pair,targets,allow_perm):
    a,b=pair;rs=(a,b,p10.mul(a,b));best=None
    perms=itertools.permutations(range(3)) if allow_perm else ((0,1,2),)
    for perm in perms:
      t=tuple(targets[perm[k]] for k in range(3))
      rest=sum(wt(p10.mul(t[k],rs[k])) for k in range(3))
      for c in range(3):
        val=p10.uanti_support(rs,c)+rest;row=(val,tuple(perm),c,rs)
        if best is None or row<best:best=row
    return best

def cap1_exact(targets_a,targets_b):
    pairs=cap1_pairs();bc_a=[block_cost(p,targets_a,False) for p in pairs];bc_b=[block_cost(p,targets_b,True) for p in pairs]
    best=None
    for i,pa in enumerate(pairs):
      for j,pb in enumerate(pairs):
        tc,tw=tag_min(pa,pb)
        if tc>=INF:continue
        total=bc_a[i][0]+bc_b[j][0]+tc
        row=(total,i,j,bc_a[i],bc_b[j],tw)
        if best is None or row<best:best=row
    if best is None:raise AssertionError('cap1 no feasible configuration')
    return {
      'C_cap1':int(best[0]),'pair_A_index':best[1],'pair_B_index':best[2],
      'pair_A':[list(x) for x in pairs[best[1]]],'pair_B':[list(x) for x in pairs[best[2]]],
      'block_A':{'cost':int(best[3][0]),'permutation':list(best[3][1]),'central':int(best[3][2])},
      'block_B':{'cost':int(best[4][0]),'permutation':list(best[4][1]),'central':int(best[4][2])},
      'tag':{'cost':int(best[5][0]),'S0':list(best[5][1]),'S1':list(best[5][2]),'labels':list(best[5][3])},
      'cap1_pair_count':len(pairs),
    }

def recompute_production_witness(w):
    checks=w.get('checks',{});return bool(checks) and all(bool(v) for v in checks.values()) and int(w['C_shared'])>=0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage1',default=str(DEFAULT_STAGE1));ap.add_argument('--output',default=str(DEFAULT_OUT));ns=ap.parse_args()
    s1=json.loads(Path(ns.stage1).read_text());u=dict(s1);obs=u.pop('result_digest',None);calc=hashlib.sha256(canonical(u).encode()).hexdigest()
    if obs!=calc or s1.get('cap1_opened') is not False or s1.get('unrestricted_dp_opened') is not False:raise AssertionError('stage1 custody invalid')
    if hashlib.sha256(canonical(s1['candidates']).encode()).hexdigest()!=s1.get('candidate_digest'):raise AssertionError('candidate digest mismatch')
    results=[];positive=None
    for cand in s1['candidates']:
      ta=tuple(key(x) for x in cand['targets_A']);tb=tuple(key(x) for x in cand['targets_B']);cap=cap1_exact(ta,tb)
      row={'candidate_index':cand['candidate_index'],'U2':int(cand['U2']),'C_cap1':int(cap['C_cap1']),'strict_gap':int(cand['U2'])<int(cap['C_cap1']),'cap1':cap}
      results.append(row)
      if row['strict_gap']:
        dp=r6i.shared_tag_exact(ta,tb,2)
        if not (int(dp['C_shared'])<=int(cand['U2'])<int(cap['C_cap1'])):raise AssertionError({'strict_gap_not_confirmed':[dp['C_shared'],cand['U2'],cap['C_cap1']]})
        if not recompute_production_witness(dp):raise AssertionError('production witness checks failed')
        positive={'candidate':cand,'cap1':cap,'C_DP':int(dp['C_shared']),'production_witness':dp,'gap_cap1_minus_dp':int(cap['C_cap1'])-int(dp['C_shared']),'gap_cap1_minus_U2':int(cap['C_cap1'])-int(cand['U2'])}
        break
    terminal='QG9_SUPPORT2_TIGHT_WITNESS_FOUND__CAP1_STRICT_GAP' if positive else 'QG9_T2_NO_TIGHT_WITNESS_IN_FROZEN_INVERSE_DESIGN_DOMAIN'
    out={'schema':'ORION.QG.QG9.T2.Cap1Referee.v1','issue':ISSUE,'stage1_result_digest':s1['result_digest'],'candidate_digest':s1['candidate_digest'],'canonical_candidate_count':s1['canonical_candidate_count'],'candidates_evaluated':len(results),'rows':results,'positive_witness':positive,'terminal':terminal,'cap1_opened':True,'unrestricted_dp_opened':positive is not None,'support2_tightness_claim':positive is not None,'support1_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False,'network_access':False,'chemistry_sources_read':False,'protected_subject_read':False}
    out['result_digest']=hashlib.sha256(canonical(out).encode()).hexdigest();p=Path(ns.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(out));return 0
if __name__=='__main__':raise SystemExit(main())
