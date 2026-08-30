#!/usr/bin/env python3
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent

def canonical(x:Any)->str:return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def enc(v):return 25*v[0]+5*v[1]+v[2]
def scale(c,v):return tuple((c*x)%5 for x in v)
def norm(v):
    for x in v:
        if x:return scale(pow(x,-1,5),v)
    raise ValueError

def short_free_line(state):
    for k in itertools.product(*(range(m+1) for m in state)):
        n=sum(k)
        if 1<=n<=5 and sum((i+1)*k[i] for i in range(4))%5==0:return False
    return True

def atlas():
    reps=sorted({norm(v) for v in itertools.product(range(5),repeat=3) if v!=(0,0,0)},key=enc)
    states=[list(s) for s in itertools.product((0,1,2,4),repeat=4) if short_free_line(s)]
    obj={'schema':'ORION.ORION04.ProjectiveLineAtlas.v2','line_count':len(reps),'allowed_multiplicities':[0,1,2,4],
         'local_state_count':len(states),'states':states,
         'lines':[{'id':i,'representative':list(v),'points':[enc(scale(c,v)) for c in range(1,5)]} for i,v in enumerate(reps)],
         'derived_rules':{'mult4_isolated':True,'two_mult2_collinear_forbidden':True,'high_points_pairwise_projectively_distinct':True}}
    obj['digest']=hashlib.sha256(canonical(obj).encode()).hexdigest();return obj

def patterns(lo=23,hi=31):
    out=[]
    for s in range(lo,hi+1):
        for c4 in range(0,8):
            b2=31-s-3*c4;a1=2*s-31+2*c4
            if min(a1,b2)>=0 and a1+b2+c4==s and a1+2*b2+4*c4==31:
                out.append({'support':s,'a1':a1,'b2':b2,'c4':c4})
    return out

def branches_for(p):
    a,b,c,s=p['a1'],p['b2'],p['c4'],p['support'];h=b+c;out=[]
    # Rank-three high-multiplicity branch when possible.
    if h>=3 and ((c==0 and b>=3) or (c==1 and b>=2) or (c==2 and b>=1)):
        seed={0:[2,2,2],1:[4,2,2],2:[4,4,2]}[c]
        out.append({**p,'branch':'HIGH_RANK3','seed_multiplicities':seed,'plane_doubletons':False,
                    'normalization':'high-multiplicity basis -> e1,e2,e3'})
    # High-multiplicity rank-two branch only when eta(C_5^2)=13 does not force rank three.
    high_length=2*b+4*c
    if h>=2:
        if high_length<=13:
            seed={0:[2,2,1],1:[4,2,1],2:[4,4,1]}[c]
            out.append({**p,'branch':'HIGH_RANK2_SINGLETON_OUTSIDE','seed_multiplicities':seed,'plane_doubletons':True,
                        'normalization':'two independent high points -> e1,e2; outside singleton -> e3'})
    elif h==1:
        seed=[4,1,1] if c==1 else [2,1,1]
        out.append({**p,'branch':'ONE_HIGH_FULL_BASIS','seed_multiplicities':seed,'plane_doubletons':False,
                    'normalization':'unique high point extended by two singleton points to a basis'})
    else:
        out.append({**p,'branch':'ALL_SINGLETON_FULL_BASIS','seed_multiplicities':[1,1,1],'plane_doubletons':False,
                    'normalization':'three singleton support points form a basis'})
    return out

def cover():
    ps=patterns();bs=[b for p in ps for b in branches_for(p)]
    obj={'schema':'ORION.ORION04.Support23To31BranchCover.v1','support_interval':[23,31],
         'pattern_equations':['a1+b2+c4=support','a1+2*b2+4*c4=31'],
         'pattern_count':len(ps),'branch_count':len(bs),'patterns':ps,'branches':bs,
         'lemmas':{
             'full_rank':'length 31 short-free candidate cannot lie in rank <=2 because eta(C_5^2)=13',
             'high_pair_independence':'the projective-line atlas forbids collinear pairs among multiplicity-2/4 support points',
             'rank3_basis_profiles':'matroid basis extension gives (2,2,2), (4,2,2), or (4,4,2)',
             'rank2_outside_type':'when all high points lie in their plane, full rank forces an outside singleton',
             'final_singleton':'the largest nonseed singleton is uniquely forced by total sum after all other points are selected'}}
    obj['digest']=hashlib.sha256(canonical(obj).encode()).hexdigest();return obj

def main():
    a=atlas();c=cover()
    (ROOT/'PROJECTIVE_LINE_ATLAS.json').write_text(json.dumps(a,indent=2,sort_keys=True)+'\n')
    (ROOT/'CUBE_COVER.json').write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'lines':a['line_count'],'states':a['local_state_count'],'patterns':c['pattern_count'],'branches':c['branch_count']},sort_keys=True))
if __name__=='__main__':main()
