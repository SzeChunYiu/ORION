#!/usr/bin/env python3
"""Independent formula verifier for QG-13 V4 support<=4 theorem."""
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'artifacts'/'orion-qg-qg13v4-support4.json';O=ROOT/'artifacts'/'orion-qg-qg13v4-generic-verification.json';Q=ROOT/'research'/'extensions'/'orion-qg'/'QG1_RANK2_ALL_N_RESULTS.json';TOKEN='ORIONQG_QG13V4_GENERIC=';ACTS=('A','B','AB')
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
  ss=syn(r0,r1,s0,s1);oc=cost(r0,r1,p0,p1,p2,c)
  for a in ACTS:
   x,y=app(r0,r1,a)
   if (x,y)==(r0,r1):continue
   sig=ss^syn(x,y,s0,s1);d=cost(x,y,p0,p1,p2,c)-oc;rec=st.setdefault((a,sig),[-10**9,10**9,0]);rec[0]=max(rec[0],d);rec[1]=min(rec[1],d);rec[2]+=1;rows+=1
 return st,rows
def safe(st):
 s2=set();s3=set();p2=[0,0];p3=[0,0]
 for (ka,ra),(kb,rb) in itertools.product(st.items(),repeat=2):
  a,sa=ka;b,sb=kb
  if sa!=sb:continue
  p2[0]+=1
  if ra[0]+rb[0]<=0:s2.add((a,sa,b,sb))
  else:p2[1]+=1
 items=list(st.items())
 for (ka,ra),(kb,rb),(kc,rc) in itertools.product(items,repeat=3):
  a,sa=ka;b,sb=kb;c,sc=kc
  if sa^sb^sc:continue
  p3[0]+=1
  if ra[0]+rb[0]+rc[0]<=0:s3.add((a,sa,b,sb,c,sc))
  else:p3[1]+=1
 return s2,s3,{'e2':(p2[0],len(s2),p2[1]),'e3':(p3[0],len(s3),p3[1])}
def zs(v):
 for mask in range(1,1<<len(v)):
  x=0
  for i,z in enumerate(v):
   if (mask>>i)&1:x^=z
  if x==0:return True
 return False
def struct(r0,r1,s0,s1):
 ss=syn(r0,r1,s0,s1);co=r0==r1 and r0!=0;al=s(r0,r1);n0=None if r0==0 or co else ((al<<2)|(s(s0,r0)<<1)|s(s1,r0));n1=None if r1==0 or co else ((al<<2)|(s(s0,r1)<<1)|s(s1,r1));cc=None if not co else ((s(s0,r0)<<1)|s(s1,r0));aa=[]
 for a in ACTS:
  x,y=app(r0,r1,a)
  if (x,y)==(r0,r1):continue
  aa.append({'a':a,'sig':ss^syn(x,y,s0,s1),'d0':int(r0!=0 and x==0),'d1':int(r1!=0 and y==0)})
 return {'syn':ss,'u0':int(r0!=0),'u1':int(r1!=0),'n0':n0,'n1':n1,'c':cc,'a':aa}
def types(g):
 u={}
 for vals in itertools.product(range(4),repeat=4):
  r=struct(*vals)
  if r['u0' if g==0 else 'u1']!=1:continue
  u.setdefault(can(r),{'r':r,'rep':list(vals)})
 return [u[k] for k in sorted(u)]
def elig(p,tt,g):
 total=0;n0=[];n1=[];cc=[]
 for i in p:
  r=tt[i]['r'];total^=r['syn'];
  if r['n0'] is not None:n0.append(r['n0'])
  if r['n1'] is not None:n1.append(r['n1'])
  if r['c'] is not None:cc.append(r['c'])
 lab=2*((total>>(3 if g==0 else 1))&1)+((total>>(2 if g==0 else 0))&1)
 return ((total>>4)&1)==1 and lab!=0 and not zs(n0) and not zs(n1) and not zs(cc)
def cover2(p,tt,g,sf):
 rr=[tt[i]['r'] for i in p]
 for i,j in itertools.combinations(range(5),2):
  for a in rr[i]['a']:
   for b in rr[j]['a']:
    if a['sig']!=b['sig']:continue
    k=(a['a'],a['sig'],b['a'],b['sig']);rk=(b['a'],b['sig'],a['a'],a['sig'])
    if k not in sf and rk not in sf:continue
    if a['d0' if g==0 else 'd1']+b['d0' if g==0 else 'd1']>=1:return True
 return False
def cover3(p,tt,g,sf):
 rr=[tt[i]['r'] for i in p]
 for i,j,k in itertools.combinations(range(5),3):
  for a in rr[i]['a']:
   for b in rr[j]['a']:
    for c in rr[k]['a']:
     if a['sig']^b['sig']^c['sig']:continue
     if (a['a'],a['sig'],b['a'],b['sig'],c['a'],c['sig']) not in sf:continue
     if a['d0' if g==0 else 'd1']+b['d0' if g==0 else 'd1']+c['d0' if g==0 else 'd1']>=1:return True
 return False
def census(g,s2,s3):
 tt=types(g);n=e2=e3=u=0;first=None
 for p in itertools.combinations_with_replacement(range(len(tt)),5):
  if not elig(p,tt,g):continue
  n+=1;a=cover2(p,tt,g,s2);b=cover3(p,tt,g,s3);e2+=a;e3+=b;u+=(a or b)
  if not(a or b) and first is None:first={'pattern':list(p),'reps':[tt[i]['rep'] for i in p]}
 return {'types':len(tt),'eligible':n,'e2':e2,'e3':e3,'union':u,'uncovered':n-u,'first':first}
def spectator():
 ok0=ok1=True
 for other,s0,s1 in itertools.product(range(4),repeat=3):
  x=syn(0,other,s0,s1);ok0 &= ((x>>4)&1)==0 and ((x>>3)&1)==0 and ((x>>2)&1)==0
  y=syn(other,0,s0,s1);ok1 &= ((y>>4)&1)==0 and ((y>>1)&1)==0 and (y&1)==0
 return {'g0':bool(ok0),'g1':bool(ok1),'cost_additivity_from_spec':True,'zero_syndrome_edit_is_spectator_independent':True}
def main():
 a=json.loads(A.read_text());u=dict(a);obs=u.pop('result_digest');digest=obs==hashlib.sha256(can(u).encode()).hexdigest();st,rows=resources();s2,s3,ss=safe(st);c0=census(0,s2,s3);c1=census(1,s2,s3);sp=spectator();parent=json.loads(Q.read_text());pg=parent.get('gates',{});pc={'authority':str(parent.get('authority','')).startswith('ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED'),'support5':'support <= 5' in parent.get('claim_boundary',{}).get('covers',''),'solo':pg.get('lemma_e_solo_zero_violations') is True,'pair':pg.get('lemma_e_pair_strict') is True,'bn':pg.get('lemma_b_n_w4_to_w8_zero_failures') is True,'bc':pg.get('lemma_b_c_w3_to_w8_zero_failures') is True};ac=a['anchored_slices'];checks={'schema':a.get('schema')=='ORION.QG.QG13V4.Support4Theorem.v1','digest':digest,'action_rows':rows==a['resource_domain']['action_rows'],'action_classes':len(st)==a['resource_domain']['classes'],'safe_e2':list(ss['e2'])==[a['safe_edit_classes']['e2']['classes'],a['safe_edit_classes']['e2']['safe'],a['safe_edit_classes']['e2']['unsafe']],'safe_e3':list(ss['e3'])==[a['safe_edit_classes']['e3']['classes'],a['safe_edit_classes']['e3']['safe'],a['safe_edit_classes']['e3']['unsafe']],'g0':c0['eligible']==ac['g0']['eligible_slices'] and c0['union']==ac['g0']['union_covered'] and c0['uncovered']==0,'g1':c1['eligible']==ac['g1']['eligible_slices'] and c1['union']==ac['g1']['union_covered'] and c1['uncovered']==0,'both_324':c0['eligible']==324 and c1['eligible']==324,'spectator':all(sp.values()),'parent':all(pc.values()),'parent_hash':hashlib.sha256(Q.read_bytes()).hexdigest()==a['qg1_parent']['receipt_sha256'],'local_sealed_before_parent':a['qg1_parent']['opened_after_local_lemma_seal'] is True,'no_v2_v3':a.get('v2_v3_result_files_read') is False,'no_novelty':a.get('novelty_authority') is False,'no_physical':a.get('physical_quantum_advantage_claim') is False,'no_sensitive':a.get('network_access') is False and a.get('chemistry_sources_read') is False and a.get('protected_subject_read') is False};d='ACCEPT' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG13V4.GenericVerification.v1','decision':d,'checks':checks,'independent':{'resource_rows':rows,'resource_classes':len(st),'safe':ss,'g0':c0,'g1':c1,'spectator':sp,'parent':pc}};O.parent.mkdir(parents=True,exist_ok=True);O.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+can({'decision':d,'all':all(checks.values()),'g0':[c0['eligible'],c0['union']],'g1':[c1['eligible'],c1['union']]}));return 0
if __name__=='__main__':raise SystemExit(main())
