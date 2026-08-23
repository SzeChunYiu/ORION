#!/usr/bin/env python3
"""Independent verifier for QG-13 V3."""
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'artifacts'/'orion-qg-qg13v3-three-column.json';O=ROOT/'artifacts'/'orion-qg-qg13v3-generic-verification.json';TOKEN='ORIONQG_QG13V3_GENERIC=';ACTS=('A','B','AB')
def can(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def w(a):return 0 if a==0 else 1
def m(a,b):return a^b
def s(a,b):return int(a!=0 and b!=0 and a!=b)
def syn(r0,r1,s0,s1):return (s(r0,r1)<<4)|(s(s0,r0)<<3)|(s(s1,r0)<<2)|(s(s0,r1)<<1)|s(s1,r1)
def app(r0,r1,a):return (0,r1) if a=='A' else ((r0,0) if a=='B' else (0,0))
def cost(r0,r1,p0,p1,p2,c):
 rs=(r0,r1,m(r0,r1));mm=[4,4,4];mm[c]=2;ps=(p0,p1,p2);return sum(mm[k]*w(rs[k])+w(m(ps[k],rs[k])) for k in range(3))
def resources():
 st={};rows=0
 for r0,r1,s0,s1,p0,p1,p2,c in itertools.product(range(4),range(4),range(4),range(4),range(4),range(4),range(4),range(3)):
  old=syn(r0,r1,s0,s1);oc=cost(r0,r1,p0,p1,p2,c)
  for a in ACTS:
   nr0,nr1=app(r0,r1,a)
   if (nr0,nr1)==(r0,r1):continue
   sig=old^syn(nr0,nr1,s0,s1);d=cost(nr0,nr1,p0,p1,p2,c)-oc;rec=st.setdefault((a,sig),[-10**9,10**9,0]);rec[0]=max(rec[0],d);rec[1]=min(rec[1],d);rec[2]+=1;rows+=1
 return st,rows
def pair(st):
 safe=set();tot=unsafe=0
 for (ka,ra),(kb,rb) in itertools.product(st.items(),repeat=2):
  a,sa=ka;b,sb=kb
  if sa!=sb:continue
  tot+=1
  if ra[0]+rb[0]<=0:safe.add((a,sa,b,sb))
  else:unsafe+=1
 return safe,(tot,len(safe),unsafe)
def triple(st):
 safe=set();tot=unsafe=0;items=list(st.items())
 for (ka,ra),(kb,rb),(kc,rc) in itertools.product(items,repeat=3):
  a,sa=ka;b,sb=kb;c,sc=kc
  if sa^sb^sc:continue
  tot+=1
  if ra[0]+rb[0]+rc[0]<=0:safe.add((a,sa,b,sb,c,sc))
  else:unsafe+=1
 return safe,(tot,len(safe),unsafe)
def zs(v):
 for mask in range(1,1<<len(v)):
  x=0
  for i,z in enumerate(v):
   if (mask>>i)&1:x^=z
  if x==0:return True
 return False
def acc(x):
 a=(x>>4)&1;l0=2*((x>>3)&1)+((x>>2)&1);l1=2*((x>>1)&1)+(x&1);return a==1 and l0 in(1,2,3) and l1 in(1,2,3) and l0!=l1
def struct(r0,r1,s0,s1):
 ss=syn(r0,r1,s0,s1);co=r0==r1 and r0!=0;al=s(r0,r1);n0=None if r0==0 or co else ((al<<2)|(s(s0,r0)<<1)|s(s1,r0));n1=None if r1==0 or co else ((al<<2)|(s(s0,r1)<<1)|s(s1,r1));cc=None if not co else ((s(s0,r0)<<1)|s(s1,r0));aa=[]
 for a in ACTS:
  x,y=app(r0,r1,a)
  if (x,y)==(r0,r1):continue
  aa.append({'a':a,'sig':ss^syn(x,y,s0,s1),'d0':int(r0!=0 and x==0),'d1':int(r1!=0 and y==0)})
 return {'syn':ss,'u0':int(r0!=0),'u1':int(r1!=0),'n0':n0,'n1':n1,'c':cc,'a':aa}
def types():
 u={}
 for vals in itertools.product(range(4),repeat=4):
  r=struct(*vals);u.setdefault(can(r),{'r':r,'rep':list(vals)})
 return [u[k] for k in sorted(u)]
def irr(p,tt):
 a=[];b=[];c=[]
 for i in p:
  r=tt[i]['r']
  if r['n0'] is not None:a.append(r['n0'])
  if r['n1'] is not None:b.append(r['n1'])
  if r['c'] is not None:c.append(r['c'])
 return not zs(a) and not zs(b) and not zs(c)
def m2(p,tt,safe):
 rr=[tt[i]['r'] for i in p];u0=sum(x['u0'] for x in rr);u1=sum(x['u1'] for x in rr);before=(max(u0,u1),u0+u1)
 for i,j in itertools.combinations(range(5),2):
  for a in rr[i]['a']:
   for b in rr[j]['a']:
    if a['sig']!=b['sig']:continue
    k=(a['a'],a['sig'],b['a'],b['sig']);rk=(b['a'],b['sig'],a['a'],a['sig'])
    if k not in safe and rk not in safe:continue
    v0=u0-a['d0']-b['d0'];v1=u1-a['d1']-b['d1']
    if (max(v0,v1),v0+v1)<before:return True
 return False
def m3(p,tt,safe):
 rr=[tt[i]['r'] for i in p];u0=sum(x['u0'] for x in rr);u1=sum(x['u1'] for x in rr);before=(max(u0,u1),u0+u1)
 for i,j,k in itertools.combinations(range(5),3):
  for a in rr[i]['a']:
   for b in rr[j]['a']:
    for c in rr[k]['a']:
     if a['sig']^b['sig']^c['sig']:continue
     if (a['a'],a['sig'],b['a'],b['sig'],c['a'],c['sig']) not in safe:continue
     v0=u0-a['d0']-b['d0']-c['d0'];v1=u1-a['d1']-b['d1']-c['d1']
     if (max(v0,v1),v0+v1)<before:return True
 return False
def census(s2,s3):
 tt=types();ac=ir=s5=e2=e3=union=v2u=v3v2=0;first=None
 for p in itertools.combinations_with_replacement(range(len(tt)),5):
  total=0
  for i in p:total^=tt[i]['r']['syn']
  if not acc(total):continue
  ac+=1
  if not irr(p,tt):continue
  ir+=1;u0=sum(tt[i]['r']['u0'] for i in p);u1=sum(tt[i]['r']['u1'] for i in p)
  if max(u0,u1)!=5:continue
  s5+=1;a=m2(p,tt,s2);b=m3(p,tt,s3);e2+=int(a);e3+=int(b);union+=int(a or b)
  if not a:
   v2u+=1;v3v2+=int(b)
  if not b and first is None:first={'pattern':list(p),'supports':[u0,u1],'reps':[tt[i]['rep'] for i in p]}
 return {'types':len(tt),'accepted':ac,'irreducible':ir,'support5':s5,'e2':e2,'e3':e3,'e3_uncovered':s5-e3,'v2_uncovered':v2u,'v3_closes_v2':v3v2,'v2_survive':v2u-v3v2,'union':union,'union_uncovered':s5-union,'first':first}
def main():
 a=json.loads(A.read_text());u=dict(a);obs=u.pop('result_digest');digest=obs==hashlib.sha256(can(u).encode()).hexdigest();st,rows=resources();s2,p2=pair(st);s3,p3=triple(st);c=census(s2,s3);ar=a['census'];checks={'schema':a.get('schema')=='ORION.QG.QG13V3.ThreeColumn.v1','digest':digest,'rows':rows==a['action_resource']['enumerated_action_rows'],'classes':len(st)==a['action_resource']['action_signature_classes'],'triple':list(p3)==[a['triple_safety']['classes'],a['triple_safety']['safe'],a['triple_safety']['unsafe']],'types':c['types']==ar['structural_type_count'],'accepted':c['accepted']==ar['accepted'],'irreducible':c['irreducible']==ar['irreducible'],'support5':c['support5']==ar['support5'],'e3':c['e3']==ar['e3_covered'],'v2':c['v2_uncovered']==ar['v2_uncovered_recomputed'],'v3closes':c['v3_closes_v2']==ar['v3_closes_v2'],'union':c['union']==ar['cumulative_e2_e3_covered'],'first':(c['first'] or {}).get('pattern')==(ar.get('first_e3_uncovered') or {}).get('pattern_indices'),'noauth':a.get('new_theorem_authority') is False and a.get('novelty_authority') is False,'nosensitive':a.get('network_access') is False and a.get('chemistry_sources_read') is False and a.get('protected_subject_read') is False};d='ACCEPT' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG13V3.GenericVerification.v1','decision':d,'checks':checks,'independent':{'action_rows':rows,'action_classes':len(st),'pair':p2,'triple':p3,'census':c}};O.parent.mkdir(parents=True,exist_ok=True);O.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+can({'decision':d,'all':all(checks.values()),'e3':c['e3'],'v3closes':c['v3_closes_v2'],'union':c['union']}));return 0
if __name__=='__main__':raise SystemExit(main())
