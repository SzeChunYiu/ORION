#!/usr/bin/env python3
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def enc(v):return 25*v[0]+5*v[1]+v[2]
def mul(a,v):return tuple((a*x)%5 for x in v)
def rep(v):
 for x in v:
  if x:return mul(pow(x,-1,5),v)
 raise ValueError
def line_ok(s):
 for take in itertools.product(*(range(m+1) for m in s)):
  n=sum(take)
  if 1<=n<=5 and sum((i+1)*take[i] for i in range(4))%5==0:return False
 return True
def expected_atlas():
 reps=sorted({rep(v) for v in itertools.product(range(5),repeat=3) if any(v)},key=enc)
 states=[list(s) for s in itertools.product((0,1,2,4),repeat=4) if line_ok(s)]
 obj={'schema':'ORION.ORION04.ProjectiveLineAtlas.v2','line_count':len(reps),'allowed_multiplicities':[0,1,2,4],'local_state_count':len(states),'states':states,'lines':[{'id':i,'representative':list(v),'points':[enc(mul(c,v)) for c in range(1,5)]} for i,v in enumerate(reps)],'derived_rules':{'mult4_isolated':True,'two_mult2_collinear_forbidden':True,'high_points_pairwise_projectively_distinct':True}}
 obj['digest']=hashlib.sha256(canon(obj).encode()).hexdigest();return obj
def pats():
 z=[]
 for s in range(23,32):
  for c in range(8):
   b=31-s-3*c;a=2*s-31+2*c
   if min(a,b)>=0 and a+b+c==s and a+2*b+4*c==31:z.append({'support':s,'a1':a,'b2':b,'c4':c})
 return z
def bs(p):
 s,a,b,c=p['support'],p['a1'],p['b2'],p['c4'];h=b+c;z=[]
 if h>=3 and ((c==0 and b>=3)or(c==1 and b>=2)or(c==2 and b>=1)):
  z.append({**p,'branch':'HIGH_RANK3','seed_multiplicities':{0:[2,2,2],1:[4,2,2],2:[4,4,2]}[c],'plane_doubletons':False,'normalization':'high-multiplicity basis -> e1,e2,e3'})
 L=2*b+4*c
 if h>=2:
  if L<=13:z.append({**p,'branch':'HIGH_RANK2_SINGLETON_OUTSIDE','seed_multiplicities':{0:[2,2,1],1:[4,2,1],2:[4,4,1]}[c],'plane_doubletons':True,'normalization':'two independent high points -> e1,e2; outside singleton -> e3'})
 elif h==1:z.append({**p,'branch':'ONE_HIGH_FULL_BASIS','seed_multiplicities':[4,1,1] if c else [2,1,1],'plane_doubletons':False,'normalization':'unique high point extended by two singleton points to a basis'})
 else:z.append({**p,'branch':'ALL_SINGLETON_FULL_BASIS','seed_multiplicities':[1,1,1],'plane_doubletons':False,'normalization':'three singleton support points form a basis'})
 return z
def expected_cover():
 p=pats();b=[q for x in p for q in bs(x)]
 obj={'schema':'ORION.ORION04.Support23To31BranchCover.v1','support_interval':[23,31],'pattern_equations':['a1+b2+c4=support','a1+2*b2+4*c4=31'],'pattern_count':len(p),'branch_count':len(b),'patterns':p,'branches':b,'lemmas':{'full_rank':'length 31 short-free candidate cannot lie in rank <=2 because eta(C_5^2)=13','high_pair_independence':'the projective-line atlas forbids collinear pairs among multiplicity-2/4 support points','rank3_basis_profiles':'matroid basis extension gives (2,2,2), (4,2,2), or (4,4,2)','rank2_outside_type':'when all high points lie in their plane, full rank forces an outside singleton','final_singleton':'the largest nonseed singleton is uniquely forced by total sum after all other points are selected'}}
 obj['digest']=hashlib.sha256(canon(obj).encode()).hexdigest();return obj
def main():
 a=json.loads((ROOT/'PROJECTIVE_LINE_ATLAS.json').read_text());c=json.loads((ROOT/'CUBE_COVER.json').read_text());ea=expected_atlas();ec=expected_cover()
 points=[p for row in a['lines'] for p in row['points']]
 checks={'atlas_exact':a==ea,'cover_exact':c==ec,'line_partition':len(points)==124 and sorted(points)==list(range(1,125)),'state_count_21':a['local_state_count']==21,'pattern_count_18':c['pattern_count']==18,'branch_count_27':c['branch_count']==27}
 ma=json.loads(json.dumps(a));ma['states'].pop();mc=json.loads(json.dumps(c));mc['branches'].pop();checks['hostile_missing_state_rejected']=ma!=ea;checks['hostile_missing_branch_rejected']=mc!=ec
 r={'schema':'ORION.ORION04.StaticIndependentCheck.v1','checks':checks,'decision':'STATIC_COVER_ACCEPT' if all(checks.values()) else 'STATIC_COVER_REJECT'};r['digest']=hashlib.sha256(canon(r).encode()).hexdigest();(ROOT/'STATIC_CHECK_RESULT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(canon({'decision':r['decision'],'digest':r['digest']}));return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(main())
