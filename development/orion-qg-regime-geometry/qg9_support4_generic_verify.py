#!/usr/bin/env python3
from __future__ import annotations
import hashlib,itertools,json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'artifacts/orion-qg-qg9-support4-combined-exchange.json'
OUT=ROOT/'artifacts/orion-qg-qg9-support4-generic-verification.json'
TOKEN='ORIONQG_QG9_SUPPORT4_GENERIC='
bits={0:(0,0),1:(1,0),2:(1,1),3:(0,1)};code={v:k for k,v in bits.items()}
def mul(a,b):
 xa,za=bits[a];xb,zb=bits[b];return code[(xa^xb,za^zb)]
def symp(a,b):
 xa,za=bits[a];xb,zb=bits[b];return (xa*zb+za*xb)%2
def wt(a):return int(a!=0)
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def cost(a,b,p0,p1,p2,c):
 r2=mul(a,b);m=[4,4,4];m[c]=2
 return m[0]*wt(a)+m[1]*wt(b)+m[2]*wt(r2)+wt(mul(p0,a))+wt(mul(p1,b))+wt(mul(p2,r2))
def anew(a,b,act):
 if act=='d0':return 0,b
 if act=='d1':return a,0
 return 0,0
def sig(a,b,s0,s1,act):
 na,nb=anew(a,b,act);old=(symp(a,b),symp(s0,a),symp(s1,a),symp(s0,b),symp(s1,b));new=(symp(na,nb),symp(s0,na),symp(s1,na),symp(s0,nb),symp(s1,nb));return sum((x^y)<<i for i,(x,y) in enumerate(zip(old,new)))
def desc(a,b,s0,s1):return (int(a!=0),int(b!=0),int(a==b and a!=0),symp(a,b),symp(s0,a),symp(s1,a),symp(s0,b),symp(s1,b))
def profiles():
 reps=defaultdict(list)
 for a,b,s0,s1 in itertools.product(range(4),repeat=4):
  if a or b:reps[desc(a,b,s0,s1)].append((a,b,s0,s1))
 pr={}
 for d,rows in reps.items():
  amap={}
  for act in ('d0','d1','db'):
   ss=set();mx=[-999]*3;have=False
   for a,b,s0,s1 in rows:
    if act=='d0' and not a:continue
    if act=='d1' and not b:continue
    have=True;ss.add(sig(a,b,s0,s1,act))
    for c in range(3):
     mm=max(cost(*anew(a,b,act),p0,p1,p2,c)-cost(a,b,p0,p1,p2,c) for p0,p1,p2 in itertools.product(range(4),repeat=3));mx[c]=max(mx[c],mm)
   if have:
    if len(ss)!=1:raise AssertionError((d,act,ss))
    amap[act]=(next(iter(ss)),tuple(mx))
  pr[d]=amap
 return reps,pr
def zsubset(cs):
 for mask in range(1,1<<len(cs)):
  x=0
  for i,c in enumerate(cs):
   if mask>>i&1:x^=c
  if x==0:return True
 return False
def irred(co):
 if not all(d[0] for d in co):return False
 a=b0=b1=0
 for d in co:a^=d[3];b0^=d[4];b1^=d[5]
 if a!=1 or ((b0<<1)|b1)==0:return False
 C=[(d[4]<<1)|d[5] for d in co if d[2]];N0=[(d[3]<<2)|(d[4]<<1)|d[5] for d in co if d[0] and not d[2]];N1=[(d[3]<<2)|(d[6]<<1)|d[7] for d in co if d[1] and not d[2]]
 return not zsubset(C) and not zsubset(N0) and not zsubset(N1)
def move(co,pr):
 opts=[]
 for d in co:
  row=[('none',0,(0,0,0),0,0)]
  for act,(sg,mx) in sorted(pr[d].items()):row.append((act,sg,mx,int(d[0] and act in ('d0','db')),int(d[0] and act in ('d0','db'))+int(d[1] and act in ('d1','db'))))
  opts.append(row)
 for ch in itertools.product(*opts):
  if all(x[0]=='none' for x in ch):continue
  sg=dr=dt=0;cc=[0,0,0]
  for x in ch:
   sg^=x[1];dr+=x[3];dt+=x[4]
   for c in range(3):cc[c]+=x[2][c]
  if sg==0 and dr>0 and dt>0 and max(cc)<=0:return True
 return False
def enum(w,descs,pr):
 kept=unsafe=0
 for inds in itertools.combinations_with_replacement(range(len(descs)),w):
  co=[descs[i] for i in inds]
  if not irred(co):continue
  kept+=1;unsafe+=int(not move(co,pr))
 return kept,unsafe
def main():
 a=json.loads(ART.read_text());tmp=dict(a);obs=tmp.pop('result_digest',None);digest=hashlib.sha256(canon(tmp).encode()).hexdigest();reps,pr=profiles();ds=sorted(reps);k5,u5=enum(5,ds,pr);k4,u4=enum(4,ds,pr)
 checks={'digest':obs==digest,'descriptor_count':len(ds)==a['descriptor_count'],'local_representative_count':sum(map(len,reps.values()))==a['local_representative_count'],'support5_retained':k5==a['support5_boundary']['retained_irreducible_patterns'],'support5_unsafe':u5==a['support5_boundary']['unsafe_count'],'support4_retained':k4==a['support4_control']['retained_irreducible_patterns'],'support4_unsafe':u4==a['support4_control']['unsafe_count'],'support5_closed':u5==0 and k5>0,'support4_not_claimed':u4>0,'authority_false':a['new_theorem_authority'] is False and a['novelty_authority'] is False}
 dec='ACCEPT' if all(checks.values()) and a['terminal']=='QG9_RANK2_ALL_N_SUPPORT4_SUFFICIENCY_MACHINE_CHECKED' else 'REJECT';out={'schema':'ORION.QG.QG9.GenericVerification.v1','decision':dec,'checks':checks,'independent_counts':{'descriptor_count':len(ds),'support5_retained':k5,'support5_unsafe':u5,'support4_retained':k4,'support4_unsafe':u4},'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
