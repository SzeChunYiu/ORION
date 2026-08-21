#!/usr/bin/env python3
"""Independent QG-13 verifier: reconstruct DP state equations without production _DELTA."""
from __future__ import annotations
import hashlib, itertools, json, sys
from pathlib import Path
from typing import Iterable

REPO_ROOT=Path(__file__).resolve().parents[2]
ORION_Q=REPO_ROOT/'research/extensions/orion-q'; sys.path.insert(0,str(ORION_Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa:E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa:E402

RESULT=REPO_ROOT/'artifacts/orion-qg-qg13-theorem-miner.json'; OUT=REPO_ROOT/'artifacts/orion-qg-qg13-generic-verification.json'
TOKEN='ORIONQG_QG13_GENERIC_VERIFY='

def canon(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def rank(vals:Iterable[int]):
    b={}
    for raw in sorted(set(int(x) for x in vals)):
        x=raw
        while x:
            p=x.bit_length()-1
            if p in b: x^=b[p]
            else: b[p]=x; break
    return len(b)

def mdelta(v):
    a0,a1,b0,b1,c0,c1,s=v; sy=p10.h.local_symp
    return ((sy(a0,a1)<<0)|(sy(b0,b1)<<1)|(sy(c0,c1)<<2)|((sy(s,a0)^sy(s,b0))<<3)|((sy(s,a0)^sy(s,c0))<<4)|((sy(s,a1)^sy(s,b1))<<5)|((sy(s,a1)^sy(s,c1))<<6)|(sy(s,a0)<<7)|(sy(s,a1)<<8))
def idelta(v):
    a0,a1,b0,b1,s0,s1=v; sy=p10.h.local_symp
    return ((sy(a0,a1)<<0)|(sy(b0,b1)<<1)|((sy(s0,a0)^sy(s0,b0))<<2)|((sy(s1,a0)^sy(s1,b0))<<3)|((sy(s0,a1)^sy(s0,b1))<<4)|((sy(s1,a1)^sy(s1,b1))<<5)|(sy(s0,a0)<<6)|(sy(s1,a0)<<7)|(sy(s0,a1)<<8)|(sy(s1,a1)<<9))
def transitions():
    ms=[set() for _ in range(6)]
    for v in itertools.product(range(4),repeat=7):
        old=mdelta(v)
        for i in range(6):
            w=list(v); w[i]=0; ms[i].add(old^mdelta(tuple(w)))
    isets=[set(),set()]
    for v in itertools.product(range(4),repeat=6):
        old=idelta(v)
        a=(0,0,v[2],v[3],v[4],v[5]); b=(v[0],v[1],0,0,v[4],v[5])
        isets[0].add(old^idelta(a)); isets[1].add(old^idelta(b))
    return [rank(x) for x in ms],[rank(x) for x in isets]
def r6m_resource():
    F3=[[[0]*4 for _ in range(4)] for _ in range(4)]
    wt=p10.h.local_wt; mul=p10.h.local_mul
    for a,b,c in itertools.product(range(4),repeat=3): F3[a][b][c]=1 if a==b==c and a!=0 else wt(a)+wt(b)+wt(c)
    mx={'central':-99,'noncentral':-99}; count=0
    for kind in mx:
      for pos in range(3):
       for f in (1,2,3):
        for partner,tag,p,u,v in itertools.product(range(4),repeat=5):
         count+=1; old=mul(p,f)
         if pos==0: d=F3[p][u][v]-F3[old][u][v]
         elif pos==1: d=F3[u][p][v]-F3[u][old][v]
         else: d=F3[u][v][p]-F3[u][v][old]
         mx[kind]=max(mx[kind],d)
    return count,mx,[f"t_c >= {mx['central']}*t_r",f"t_nc >= {mx['noncentral']}*t_r"]
def r6i_resource():
    wt=p10.h.local_wt; mul=p10.h.local_mul; mx=-10**9; n=0; bad=0
    for central in range(3):
      m=[4,4,4];m[central]=2
      for a,b in itertools.product(range(4),repeat=2):
       if a==0 and b==0: continue
       r2=mul(a,b)
       for p0,p1,p2,s0,s1 in itertools.product(range(4),repeat=5):
        n+=1; old=m[0]*wt(a)+m[1]*wt(b)+m[2]*wt(r2)+wt(mul(p0,a))+wt(mul(p1,b))+wt(mul(p2,r2)); new=wt(p0)+wt(p1)+wt(p2); d=new-old; mx=max(mx,d); bad+=d>0
    return n,mx,bad
def main():
    a=json.loads(RESULT.read_text()); d=dict(a); observed=d.pop('result_digest'); digest=hashlib.sha256(canon(d).encode()).hexdigest()==observed
    mr,ir=transitions(); mc,mx,facets=r6m_resource(); ic,im,ib=r6i_resource()
    checks={
      'schema':a.get('schema')=='ORION.QG.QG13.TheoremMiner.v1','digest':digest,
      'm_transition_rows':a['r6m_transition']['rows']==4**7,'i_transition_rows':a['r6i_transition']['rows']==4**6,
      'm_ranks':mr==[x['rank'] for x in a['r6m_transition']['slots'].values()],
      'i_ranks':ir==[a['r6i_transition']['blocks'][x]['rank'] for x in ('A','B')],
      'm_resource_count':mc==a['r6m_resource']['domain_size']==18432,'m_resource_max':mx==a['r6m_resource']['max_delta_f3'],
      'm_facets':facets==a['r6m_theorem_candidate']['objective_cone'],
      'i_resource_count':ic==a['r6i_resource']['domain_size']==46080,'i_resource_max':im==a['r6i_resource']['max_delta'],'i_no_positive':ib==0,
      'parent_open_after':a['parent_recovery']['opened_after_synthesis'] is True,
      'no_new_authority':a['new_theorem_authority'] is False and a['novelty_authority'] is False,
    }
    out={'schema':'ORION.QG.QG13.GenericVerification.v1','decision':'ACCEPT' if all(checks.values()) else 'REJECT','checks':checks,'independent_r6m_ranks':mr,'independent_r6i_ranks':ir,'independent_r6m_facets':facets,'independent_r6i_max_delta':im,'source_result_digest':observed,'novelty_authority':False}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__': raise SystemExit(main())
