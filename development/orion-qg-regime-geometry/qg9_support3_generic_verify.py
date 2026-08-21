#!/usr/bin/env python3
"""Independent QG-9 V3 verifier: no production R6I import and no candidate-code import."""
from __future__ import annotations
import hashlib,itertools,json
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'artifacts/orion-qg-qg9-support3-relabel-exchange.json';OUT=ROOT/'artifacts/orion-qg-qg9-support3-generic-verification.json';TOKEN='ORIONQG_QG9_SUPPORT3_GENERIC='
bits={0:(0,0),1:(1,0),2:(1,1),3:(0,1)};code={v:k for k,v in bits.items()}
def mul(a,b):xa,za=bits[a];xb,zb=bits[b];return code[(xa^xb,za^zb)]
def symp(a,b):xa,za=bits[a];xb,zb=bits[b];return (xa*zb+za*xb)&1
def wt(x):return int(x!=0)
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def desc(a,b,s0,s1):return (int(a!=0),int(b!=0),int(a==b and a!=0),symp(a,b),symp(s0,a),symp(s1,a),symp(s0,b),symp(s1,b))
def sig(a,b,s0,s1):return (symp(a,b),symp(s0,a),symp(s1,a),symp(s0,b),symp(s1,b))
def sx(x,y):return sum((a^b)<<i for i,(a,b) in enumerate(zip(x,y)))
def cost(a,b,p0,p1,p2,c):
 r2=mul(a,b);m=[4,4,4];m[c]=2
 return m[0]*wt(a)+m[1]*wt(b)+m[2]*wt(r2)+wt(mul(p0,a))+wt(mul(p1,b))+wt(mul(p2,r2))
def old_action(a,b,s0,s1,act):
 na,nb=(0,b) if act=='d0' else ((a,0) if act=='d1' else (0,0));ss=sx(sig(a,b,s0,s1),sig(na,nb,s0,s1));cs=tuple(max(cost(na,nb,*p,c)-cost(a,b,*p,c) for p in itertools.product(range(4),repeat=3)) for c in range(3));return ss,cs,int(a!=0 and na==0),int(b!=0 and nb==0)
def old_profiles():
 reps=defaultdict(list)
 for a,b,s0,s1 in itertools.product(range(4),repeat=4):
  if a or b:reps[desc(a,b,s0,s1)].append((a,b,s0,s1))
 prof={}
 for d,rows in reps.items():
  am={}
  for act in ('d0','d1','db'):
   sigs=set();mx=[-999]*3;have=False
   for st in rows:
    a,b,s0,s1=st
    if act=='d0' and not a:continue
    if act=='d1' and not b:continue
    have=True;ss,cs,d0,d1=old_action(*st,act);sigs.add(ss)
    for c in range(3):mx[c]=max(mx[c],cs[c])
   if have:
    if len(sigs)!=1:raise AssertionError((d,act,sigs))
    am[act]=(next(iter(sigs)),tuple(mx),int(d[0] and act in ('d0','db')),int(d[1] and act in ('d1','db')))
  prof[d]=am
 return reps,prof
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
def old_safe(co,prof):
 opts=[]
 for d in co:
  row=[(0,(0,0,0),0,0)] + list(prof[d].values());opts.append(row)
 for ch in itertools.product(*opts):
  if all(x[2]==x[3]==0 and x[0]==0 for x in ch):continue
  ss=d0=0;cc=[0,0,0]
  for x in ch:
   ss^=x[0];d0+=x[2]
   for c in range(3):cc[c]+=x[1][c]
  if ss==0 and d0>0 and max(cc)<=0:return True
 return False
def rich_actions(a,b,s0,s1):
 old=sig(a,b,s0,s1);cand=[];aa=(0,) if a==0 else range(4);bb=(0,) if b==0 else range(4)
 for na in aa:
  for nb in bb:
   if (na,nb)==(a,b):continue
   ss=sx(old,sig(na,nb,s0,s1));d0=int(a!=0 and na==0);d1=int(b!=0 and nb==0);cs=tuple(max(cost(na,nb,*p,c)-cost(a,b,*p,c) for p in itertools.product(range(4),repeat=3)) for c in range(3));cand.append((ss,cs,d0,d1,na,nb))
 kept=[]
 for x in cand:
  dom=False
  for y in cand:
   if x==y or (x[0],x[2],x[3])!=(y[0],y[2],y[3]):continue
   if all(y[1][i]<=x[1][i] for i in range(3)) and (y[1]!=x[1] or (y[4],y[5])<(x[4],x[5])):dom=True;break
  if not dom:kept.append(x)
 return tuple(sorted(set(kept)))
def build_rich_types():
 states=defaultdict(list);actions={};byd=defaultdict(list)
 for a,b,s0,s1 in itertools.product(range(4),repeat=4):
  if a==0 and b==0:continue
  acts=rich_actions(a,b,s0,s1);pk=tuple((x[0],x[1],x[2],x[3]) for x in acts);key=(desc(a,b,s0,s1),pk);states[key].append((a,b,s0,s1));actions[key]=acts
 for key in sorted(states,key=str):byd[key[0]].append(key)
 return states,actions,byd
def rich_safe(keys,actions):
 opts=[]
 for k in keys:opts.append([(0,(0,0,0),0,0)]+[(x[0],x[1],x[2],x[3]) for x in actions[k]])
 for ch in itertools.product(*opts):
  if all(x[0]==0 and x[2]==x[3]==0 and x[1]==(0,0,0) for x in ch):continue
  ss=d0=0;cc=[0,0,0]
  for x in ch:
   ss^=x[0];d0+=x[2]
   for c in range(3):cc[c]+=x[1][c]
  if ss==0 and d0>0 and max(cc)<=0:return True
 return False
def survivors(w,descs,prof):
 ret=[];surv=[]
 for inds in itertools.combinations_with_replacement(range(len(descs)),w):
  co=[descs[i] for i in inds]
  if not irred(co):continue
  ret.append(inds)
  if not old_safe(co,prof):surv.append(inds)
 return ret,surv
def close(surv,descs,byd,actions):
 tc=unsafe=0
 for inds in surv:
  for keys in itertools.product(*[byd[descs[i]] for i in inds]):tc+=1;unsafe+=int(not rich_safe(keys,actions))
 return tc,unsafe
def main():
 a=json.loads(ART.read_text());tmp=dict(a);obs=tmp.pop('result_digest',None);digest=hashlib.sha256(canon(tmp).encode()).hexdigest();reps,op=old_profiles();descs=sorted(reps);r4,s4=survivors(4,descs,op);r3,s3=survivors(3,descs,op);states,acts,byd=build_rich_types();t4,u4=close(s4,descs,byd,acts);t3,u3=close(s3,descs,byd,acts)
 checks={'digest':obs==digest,'descriptor_count':len(descs)==28,'action_profile_type_count':len(states)==a['action_profile_type_count'],'parent_support4_retained':len(r4)==a['parent_v2']['support4_retained'],'parent_support4_survivors':len(s4)==a['parent_v2']['support4_unsafe'],'support4_type_cases':t4==a['support4_parent_survivors']['action_profile_type_cases'],'support4_zero_unsafe':u4==0==a['support4_parent_survivors']['unsafe_type_cases'],'support3_type_cases':t3==a['support3_boundary_control']['action_profile_type_cases'],'support3_unsafe_exact':u3==a['support3_boundary_control']['unsafe_type_cases'] and u3>0,'authority_false':a['support2_claim'] is False and a['tightness_claim'] is False and a['novelty_authority'] is False}
 dec='ACCEPT' if all(checks.values()) and a['terminal']=='QG9_RANK2_ALL_N_SUPPORT3_SUFFICIENCY_MACHINE_CHECKED' else 'REJECT';out={'schema':'ORION.QG.QG9.Support3GenericVerification.v1','decision':dec,'checks':checks,'independent_counts':{'support4_retained':len(r4),'support4_parent_survivors':len(s4),'support4_type_cases':t4,'support4_unsafe_type_cases':u4,'support3_retained':len(r3),'support3_parent_survivors':len(s3),'support3_type_cases':t3,'support3_unsafe_type_cases':u3,'action_profile_types':len(states)},'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon(out));return 0
if __name__=='__main__':raise SystemExit(main())
