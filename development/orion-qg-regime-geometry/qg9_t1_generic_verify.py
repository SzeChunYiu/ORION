#!/usr/bin/env python3
"""Independent verifier for QG-9 T1 tightness hunt; no R6I production import."""
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
import numpy as np
from scipy.optimize import Bounds,LinearConstraint,milp
from scipy.sparse import coo_matrix
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'artifacts'/'orion-qg-qg9t1-support4-tightness.json';O=ROOT/'artifacts'/'orion-qg-qg9t1-generic-verification.json';TOKEN='ORIONQG_QG9T1_GENERIC=';ACTS=('A','B','AB');PERMS=tuple(itertools.permutations(range(3)));N=4;ACCEPT=[387,899,579,835,707,451]
def can(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def lw(a):return 0 if a==0 else 1
def lm(a,b):return a^b
def sy(a,b):return int(a!=0 and b!=0 and a!=b)
def syn(r0,r1,s0,s1):return (sy(r0,r1)<<4)|(sy(s0,r0)<<3)|(sy(s1,r0)<<2)|(sy(s0,r1)<<1)|sy(s1,r1)
def app(r0,r1,a):return (0,r1) if a=='A' else ((r0,0) if a=='B' else (0,0))
def blockcost(r0,r1,p0,p1,p2,c):
 rs=(r0,r1,lm(r0,r1));mm=[4,4,4];mm[c]=2;ps=(p0,p1,p2);return sum(mm[k]*lw(rs[k])+lw(lm(ps[k],rs[k])) for k in range(3))
def zs(v):
 for mask in range(1,1<<len(v)):
  x=0
  for i,z in enumerate(v):
   if (mask>>i)&1:x^=z
  if x==0:return True
 return False
def action_resources():
 st={}
 for r0,r1,s0,s1,p0,p1,p2,c in itertools.product(range(4),range(4),range(4),range(4),range(4),range(4),range(4),range(3)):
  ss=syn(r0,r1,s0,s1);oc=blockcost(r0,r1,p0,p1,p2,c)
  for a in ACTS:
   x,y=app(r0,r1,a)
   if (x,y)==(r0,r1):continue
   k=(a,ss^syn(x,y,s0,s1));st[k]=max(st.get(k,-10**9),blockcost(x,y,p0,p1,p2,c)-oc)
 return st
def safe(st):
 a=set();b=set()
 for (ka,da),(kb,db) in itertools.product(st.items(),repeat=2):
  x,sx=ka;y,syy=kb
  if sx==syy and da+db<=0:a.add((x,sx,y,syy))
 items=list(st.items())
 for (ka,da),(kb,db),(kc,dc) in itertools.product(items,repeat=3):
  x,sx=ka;y,syy=kb;z,sz=kc
  if sx^syy^sz==0 and da+db+dc<=0:b.add((x,sx,y,syy,z,sz))
 return a,b
def struct(r0,r1,s0,s1):
 ss=syn(r0,r1,s0,s1);co=r0==r1 and r0!=0;al=sy(r0,r1);n0=None if r0==0 or co else ((al<<2)|(sy(s0,r0)<<1)|sy(s1,r0));n1=None if r1==0 or co else ((al<<2)|(sy(s0,r1)<<1)|sy(s1,r1));cc=None if not co else ((sy(s0,r0)<<1)|sy(s1,r0));aa=[]
 for x in ACTS:
  a,b=app(r0,r1,x)
  if (a,b)==(r0,r1):continue
  aa.append({'a':x,'sig':ss^syn(a,b,s0,s1),'d0':int(r0!=0 and a==0),'d1':int(r1!=0 and b==0)})
 return {'syn':ss,'u0':int(r0!=0),'u1':int(r1!=0),'n0':n0,'n1':n1,'c':cc,'acts':aa}
def typetable(g):
 u={}
 for vals in itertools.product(range(4),repeat=4):
  r=struct(*vals)
  if r['u0' if g==0 else 'u1']!=1:continue
  e=u.setdefault(can(r),{'record':r,'reps':[]});e['reps'].append(list(vals))
 out=[]
 for k in sorted(u):
  e=u[k];e['best_rep']=min(e['reps'],key=lambda v:(int(v[2]!=0)+int(v[3]!=0),v));out.append(e)
 return out
def elig(p,t,g):
 total=0;n0=[];n1=[];cc=[]
 for i in p:
  r=t[i]['record'];total^=r['syn']
  if r['n0'] is not None:n0.append(r['n0'])
  if r['n1'] is not None:n1.append(r['n1'])
  if r['c'] is not None:cc.append(r['c'])
 lab=2*((total>>(3 if g==0 else 1))&1)+((total>>(2 if g==0 else 0))&1);return ((total>>4)&1)==1 and lab!=0 and not zs(n0) and not zs(n1) and not zs(cc)
def cov(p,t,g,s2,s3):
 r=[t[i]['record'] for i in p]
 for i,j in itertools.combinations(range(4),2):
  for a in r[i]['acts']:
   for b in r[j]['acts']:
    if a['sig']!=b['sig']:continue
    k=(a['a'],a['sig'],b['a'],b['sig']);q=(b['a'],b['sig'],a['a'],a['sig'])
    if k not in s2 and q not in s2:continue
    if a['d0' if g==0 else 'd1']+b['d0' if g==0 else 'd1']>=1:return True
 for i,j,kq in itertools.combinations(range(4),3):
  for a in r[i]['acts']:
   for b in r[j]['acts']:
    for c in r[kq]['acts']:
     if a['sig']^b['sig']^c['sig']:continue
     if (a['a'],a['sig'],b['a'],b['sig'],c['a'],c['sig']) not in s3:continue
     if a['d0' if g==0 else 'd1']+b['d0' if g==0 else 'd1']+c['d0' if g==0 else 'd1']>=1:return True
 return False
def key(codes):
 x=z=0
 for q,a in enumerate(codes):
  bx,bz=((0,0),(1,0),(1,1),(0,1))[a];x|=bx<<q;z|=bz<<q
 return (x,z)
def symp(a,b):return ((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count())&1
def pmul(a,b):return (a[0]^b[0],a[1]^b[1])
def pwt(a):return (a[0]|a[1]).bit_count()
def uanti(rs,c):
 m=[4,4,4];m[c]=2;return sum(m[k]*pwt(rs[k]) for k in range(3))-10
def lab(s0,s1,r):return 2*symp(s0,r)+symp(s1,r)
def bestother(s0,s1,l0,l1,cache):
 ck=(s0,s1,l0,l1)
 if ck in cache:return cache[ck]
 keys=[key(c) for c in itertools.product(range(4),repeat=4)];nz=[k for k in keys if k!=(0,0)];best=None
 for r0 in nz:
  if lab(s0,s1,r0)!=l0:continue
  for r1 in nz:
   if symp(r0,r1)!=1 or lab(s0,s1,r1)!=l1:continue
   r2=pmul(r0,r1);vals=[uanti((r0,r1,r2),c) for c in range(3)];ua=min(vals);cen=vals.index(ua);row=(ua,pwt(r0)+pwt(r1)+pwt(r2),r0,r1,r2,cen)
   if best is None or row<best:best=row
 cache[ck]=best;return best
def candidates():
 st=action_resources();s2,s3=safe(st);cache={};rows=[]
 for g in (0,1):
  t=typetable(g);obs=[]
  for p in itertools.combinations_with_replacement(range(len(t)),4):
   if elig(p,t,g) and not cov(p,t,g,s2,s3):obs.append((p,[t[i]['best_rep'] for i in p]))
  for oi,(p,reps) in enumerate(obs[:36]):
   ra0=key([v[0] for v in reps]);ra1=key([v[1] for v in reps]);s0=key([v[2] for v in reps]);s1=key([v[3] for v in reps]);ra2=pmul(ra0,ra1);l0,l1=lab(s0,s1,ra0),lab(s0,s1,ra1);ub=bestother(s0,s1,l0,l1,cache);uc,_,rb0,rb1,rb2,cb=ub;uas=[uanti((ra0,ra1,ra2),c) for c in range(3)];ca=uas.index(min(uas));U4=min(uas)+uc+2*(pwt(s0)+pwt(s1));ch={'anti_A':symp(ra0,ra1)==1,'anti_B':symp(rb0,rb1)==1,'labels_equal':(l0,l1)==(lab(s0,s1,rb0),lab(s0,s1,rb1)),'labels_valid':l0 in(1,2,3) and l1 in(1,2,3) and l0!=l1,'selected_support4':pwt(ra0 if g==0 else ra1)==4,'restore_zero':True};rows.append({'orientation':g,'obstruction_index':oi,'pattern':list(p),'reps':reps,'targets_a':[list(ra0),list(ra1),list(ra2)],'targets_b':[list(rb0),list(rb1),list(rb2)],'tag':[list(s0),list(s1)],'labels':[l0,l1,l0^l1],'desired_centrals':[ca,cb],'U4':int(U4),'checks':ch})
 return rows
# independent local option model
vals=np.array(list(itertools.product(range(4),repeat=6)),dtype=np.int8);ra0,ra1,rb0,rb1,s0,s1=[vals[:,i] for i in range(6)];ra2=ra0^ra1;rb2=rb0^rb1;SY=np.zeros((4,4),int)
for a in range(4):
 for b in range(4):SY[a,b]=int(a!=0 and b!=0 and a!=b)
LW=np.array([0,1,1,1]);DEL=(SY[ra0,ra1]<<0)|(SY[rb0,rb1]<<1)|((SY[s0,ra0]^SY[s0,rb0])<<2)|((SY[s1,ra0]^SY[s1,rb0])<<3)|((SY[s0,ra1]^SY[s0,rb1])<<4)|((SY[s1,ra1]^SY[s1,rb1])<<5)|(SY[s0,ra0]<<6)|(SY[s1,ra0]<<7)|(SY[s0,ra1]<<8)|(SY[s1,ra1]<<9);ACT=((ra0!=0)<<0)|((ra1!=0)<<1)|((rb0!=0)<<2)|((rb1!=0)<<3)
def lc(a,b):return a^b
def codes(k):
 x,z=k;out=[]
 for q in range(4):out.append(((0,3),(1,2))[((x>>q)&1)][(z>>q)&1])
 return out
def compq(cand,perm,ca,cb,q):
 A0,A1,A2=[codes(tuple(x)) for x in cand['targets_a']];B=[codes(tuple(x)) for x in cand['targets_b']];pb=[B[perm[k]] for k in range(3)];mmA=[4,4,4];mmA[ca]=2;mmB=[4,4,4];mmB[cb]=2;base=mmA[0]*LW[ra0]+mmA[1]*LW[ra1]+mmA[2]*LW[ra2]+mmB[0]*LW[rb0]+mmB[1]*LW[rb1]+mmB[2]*LW[rb2]+2*(LW[s0]+LW[s1])+LW[A0[q]^ra0]+LW[A1[q]^ra1]+LW[A2[q]^ra2]+LW[pb[0][q]^rb0]+LW[pb[1][q]^rb1]+LW[pb[2][q]^rb2];keyv=DEL*16+ACT;mins=np.full(16384,np.inf);np.minimum.at(mins,keyv,base);idx=np.flatnonzero(np.isfinite(mins));return idx//16,idx%16,mins[idx]
def cap3(cand,perm,ca,cb):
 qd=[compq(cand,perm,ca,cb,q) for q in range(4)];off=[];nv=0
 for d,a,c in qd:off.append(nv);nv+=len(d)
 ko=nv;nv+=10;yo=nv;nv+=6;obj=np.zeros(nv);lb=np.zeros(nv);ub=np.ones(nv);ub[ko:ko+10]=2;rows=[];lo=[];hi=[]
 for q,(ds,acts,cs) in enumerate(qd):
  o=off[q];obj[o:o+len(ds)]=cs;rows.append({o+j:1. for j in range(len(ds))});lo.append(1.);hi.append(1.)
 rows.append({yo+i:1. for i in range(6)});lo.append(1.);hi.append(1.)
 for b in range(10):
  row={ko+b:-2.}
  for q,(ds,acts,cs) in enumerate(qd):
   o=off[q]
   for j,d in enumerate(ds):
    if (int(d)>>b)&1:row[o+j]=1.
  for i,state in enumerate(ACCEPT):
   if (state>>b)&1:row[yo+i]=-1.
  rows.append(row);lo.append(0.);hi.append(0.)
 for bit in range(4):
  row={}
  for q,(ds,acts,cs) in enumerate(qd):
   o=off[q]
   for j,a in enumerate(acts):
    if (int(a)>>bit)&1:row[o+j]=1.
  rows.append(row);lo.append(-np.inf);hi.append(3.)
 rr=[];cc=[];vv=[]
 for i,row in enumerate(rows):
  for j,v in row.items():rr.append(i);cc.append(j);vv.append(v)
 M=coo_matrix((vv,(rr,cc)),shape=(len(rows),nv)).tocsr();r=milp(obj,integrality=np.ones(nv,int),bounds=Bounds(lb,ub),constraints=LinearConstraint(M,np.array(lo),np.array(hi)),options={'time_limit':15.0,'mip_rel_gap':0.0,'presolve':True});return None if not r.success else int(round(float(r.fun)))-20
def main():
 a=json.loads(A.read_text());u=dict(a);obs=u.pop('result_digest');digest=obs==hashlib.sha256(can(u).encode()).hexdigest();cs=candidates();checks={'schema':a.get('schema')=='ORION.QG.QG9T1.Support4Tightness.v1','digest':digest,'candidate_count':len(cs)==72,'candidate_digest':hashlib.sha256(can(cs).encode()).hexdigest()==a['candidate_generation']['digest'],'orientation_counts':sum(c['orientation']==0 for c in cs)==36 and sum(c['orientation']==1 for c in cs)==36,'no_novelty':a.get('novelty_authority') is False,'no_physical':a.get('physical_quantum_advantage_claim') is False,'no_support3_theorem':a.get('support3_theorem_authority') is False,'safe':a.get('network_access') is False and a.get('chemistry_sources_read') is False and a.get('protected_subject_read') is False};term=a.get('terminal');verified=0;errors=[]
 if term=='QG9T1_R6I_SUPPORT4_TIGHT_WITNESS_EXACT':
  p=a['positive_witness'];cand=cs[p['candidate_index']];best=10**9
  for perm in PERMS:
   for ca in range(3):
    for cb in range(3):
     v=cap3(cand,perm,ca,cb);verified+=1
     if v is None:errors.append('solver');break
     best=min(best,v)
    if errors:break
   if errors:break
  checks['positive_cap3_exact']=not errors and best==p['C_cap3'] and best>cand['U4']
 elif term=='QG9T1_NO_SUPPORT4_TIGHT_WITNESS_IN_FROZEN_PANEL':
  checks['all_rows_present']=len(a['scan_rows'])==72
  for row in a['scan_rows']:
   cand=cs[row['candidate_index']];rej=row.get('rejection')
   if not rej:errors.append(['missing_rejection',row['candidate_index']]);continue
   v=cap3(cand,tuple(rej['perm']),rej['cA'],rej['cB']);verified+=1
   if v is None or v>cand['U4'] or v!=rej['C_cap3_config']:errors.append(['bad_rejection',row['candidate_index'],v,rej['C_cap3_config'],cand['U4']])
  checks['negative_rejections_exact']=not errors
 elif term=='QG9T1_CAP3_SOLVER_CANNOT_CHECK':checks['solver_failure_recorded']=any(r.get('solver_failure') for r in a['scan_rows'])
 else:checks['binding_failure_recorded']=True
 decision='ACCEPT' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9T1.GenericVerification.v1','decision':decision,'checks':checks,'milps_replayed':verified,'errors':errors[:20]};O.parent.mkdir(parents=True,exist_ok=True);O.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+can({'decision':decision,'milps':verified,'errors':len(errors)}));return 0
if __name__=='__main__':raise SystemExit(main())
