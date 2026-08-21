#!/usr/bin/env python3
"""QG-9 T1: exact n=4 cap-3 witness hunt for R6I support-four tightness."""
from __future__ import annotations

import argparse, hashlib, itertools, json, sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import __version__ as SCIPY_VERSION
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

ROOT=Path(__file__).resolve().parents[3];Q=ROOT/'research'/'extensions'/'orion-q';sys.path.insert(0,str(Q))
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa:E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa:E402
import max_r6b_tare_transformation_reuse_donor as reuse  # noqa:E402

BASE='afe7994bd5e362b2e8d40482f2dde9689e6ef708';ISSUE='SzeChunYiu/ORION#793';N=4
OUT=ROOT/'artifacts'/'orion-qg-qg9t1-support4-tightness.json';TOKEN='ORIONQG_QG9T1=';ACTS=('A','B','AB');PERMS=tuple(itertools.permutations(range(3)))

def can(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def wt(a):return int(r6i._LW[a])
def mul(a,b):return int(r6i._MUL[a,b])
def sy(a,b):return int(r6i._SYMP[a,b])
def syn(r0,r1,s0,s1):return (sy(r0,r1)<<4)|(sy(s0,r0)<<3)|(sy(s1,r0)<<2)|(sy(s0,r1)<<1)|sy(s1,r1)
def app(r0,r1,a):return (0,r1) if a=='A' else ((r0,0) if a=='B' else (0,0))
def block_local_cost(r0,r1,p0,p1,p2,c):
 rs=(r0,r1,mul(r0,r1));mm=[4,4,4];mm[c]=2;ps=(p0,p1,p2);return sum(mm[k]*wt(rs[k])+wt(mul(ps[k],rs[k])) for k in range(3))
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
  ss=syn(r0,r1,s0,s1);oc=block_local_cost(r0,r1,p0,p1,p2,c)
  for a in ACTS:
   x,y=app(r0,r1,a)
   if (x,y)==(r0,r1):continue
   sig=ss^syn(x,y,s0,s1);d=block_local_cost(x,y,p0,p1,p2,c)-oc;rec=st.setdefault((a,sig),-10**9);st[(a,sig)]=max(rec,d)
 return st

def safe_edits(st):
 s2=set();s3=set()
 for (ka,da),(kb,db) in itertools.product(st.items(),repeat=2):
  a,sa=ka;b,sb=kb
  if sa==sb and da+db<=0:s2.add((a,sa,b,sb))
 items=list(st.items())
 for (ka,da),(kb,db),(kc,dc) in itertools.product(items,repeat=3):
  a,sa=ka;b,sb=kb;c,sc=kc
  if sa^sb^sc==0 and da+db+dc<=0:s3.add((a,sa,b,sb,c,sc))
 return s2,s3

def struct_record(r0,r1,s0,s1):
 ss=syn(r0,r1,s0,s1);co=r0==r1 and r0!=0;al=sy(r0,r1);n0=None if r0==0 or co else ((al<<2)|(sy(s0,r0)<<1)|sy(s1,r0));n1=None if r1==0 or co else ((al<<2)|(sy(s0,r1)<<1)|sy(s1,r1));cc=None if not co else ((sy(s0,r0)<<1)|sy(s1,r0));acts=[]
 for a in ACTS:
  x,y=app(r0,r1,a)
  if (x,y)==(r0,r1):continue
  acts.append({'a':a,'sig':ss^syn(x,y,s0,s1),'d0':int(r0!=0 and x==0),'d1':int(r1!=0 and y==0)})
 return {'syn':ss,'u0':int(r0!=0),'u1':int(r1!=0),'n0':n0,'n1':n1,'c':cc,'acts':acts}

def type_table(g):
 u={}
 for vals in itertools.product(range(4),repeat=4):
  r=struct_record(*vals)
  if r['u0' if g==0 else 'u1']!=1:continue
  k=can(r);ent=u.setdefault(k,{'record':r,'reps':[]});ent['reps'].append(list(vals))
 out=[]
 for k in sorted(u):
  ent=u[k];ent['best_rep']=min(ent['reps'],key=lambda v:(int(v[2]!=0)+int(v[3]!=0),v));out.append(ent)
 return out

def eligible(p,tt,g):
 total=0;n0=[];n1=[];cc=[]
 for i in p:
  r=tt[i]['record'];total^=r['syn'];
  if r['n0'] is not None:n0.append(r['n0'])
  if r['n1'] is not None:n1.append(r['n1'])
  if r['c'] is not None:cc.append(r['c'])
 lab=2*((total>>(3 if g==0 else 1))&1)+((total>>(2 if g==0 else 0))&1)
 return ((total>>4)&1)==1 and lab!=0 and not zs(n0) and not zs(n1) and not zs(cc)
def covered(p,tt,g,s2,s3):
 rr=[tt[i]['record'] for i in p]
 for i,j in itertools.combinations(range(4),2):
  for a in rr[i]['acts']:
   for b in rr[j]['acts']:
    if a['sig']!=b['sig']:continue
    k=(a['a'],a['sig'],b['a'],b['sig']);rk=(b['a'],b['sig'],a['a'],a['sig'])
    if k not in s2 and rk not in s2:continue
    if a['d0' if g==0 else 'd1']+b['d0' if g==0 else 'd1']>=1:return True
 for i,j,kq in itertools.combinations(range(4),3):
  for a in rr[i]['acts']:
   for b in rr[j]['acts']:
    for c in rr[kq]['acts']:
     if a['sig']^b['sig']^c['sig']:continue
     if (a['a'],a['sig'],b['a'],b['sig'],c['a'],c['sig']) not in s3:continue
     if a['d0' if g==0 else 'd1']+b['d0' if g==0 else 'd1']+c['d0' if g==0 else 'd1']>=1:return True
 return False

def obstruction_patterns(g,s2,s3):
 tt=type_table(g);out=[]
 for p in itertools.combinations_with_replacement(range(len(tt)),4):
  if eligible(p,tt,g) and not covered(p,tt,g,s2,s3):out.append({'pattern':list(p),'reps':[tt[i]['best_rep'] for i in p]})
 return tt,out

def key_from_rep(reps,idx):return p10.key_from_codes([v[idx] for v in reps])
def labels(s0,s1,r0,r1):return (2*p10.symp(s0,r0)+p10.symp(s1,r0),2*p10.symp(s0,r1)+p10.symp(s1,r1))
def best_other_block(s0,s1,l0,l1,cache):
 ck=(s0,s1,l0,l1)
 if ck in cache:return cache[ck]
 keys=[p10.key_from_codes(c) for c in itertools.product(range(4),repeat=N)];nz=[k for k in keys if k!=(0,0)];best=None
 for r0 in nz:
  if 2*p10.symp(s0,r0)+p10.symp(s1,r0)!=l0:continue
  for r1 in nz:
   if p10.symp(r0,r1)!=1 or 2*p10.symp(s0,r1)+p10.symp(s1,r1)!=l1:continue
   r2=p10.mul(r0,r1);vals=[p10.uanti_support((r0,r1,r2),c) for c in range(3)];ua=min(vals);cen=vals.index(ua);row=(ua,p10.wt(r0)+p10.wt(r1)+p10.wt(r2),r0,r1,r2,cen)
   if best is None or row<best:best=row
 if best is None:raise AssertionError('no compatible other block')
 cache[ck]=best;return best

def make_candidates(s2,s3):
 cache={};rows=[]
 for g in (0,1):
  tt,obs=obstruction_patterns(g,s2,s3)
  for oi,o in enumerate(obs[:36]):
   reps=o['reps'];ra0=key_from_rep(reps,0);ra1=key_from_rep(reps,1);s0=key_from_rep(reps,2);s1=key_from_rep(reps,3);ra2=p10.mul(ra0,ra1);l0,l1=labels(s0,s1,ra0,ra1);ub=best_other_block(s0,s1,l0,l1,cache);ubc,_,rb0,rb1,rb2,cb=ub;uas=[p10.uanti_support((ra0,ra1,ra2),c) for c in range(3)];ca=uas.index(min(uas));u4=min(uas)+ubc+2*(p10.wt(s0)+p10.wt(s1));checks={'anti_A':p10.symp(ra0,ra1)==1,'anti_B':p10.symp(rb0,rb1)==1,'labels_equal':labels(s0,s1,ra0,ra1)==labels(s0,s1,rb0,rb1),'labels_valid':l0 in (1,2,3) and l1 in (1,2,3) and l0!=l1,'selected_support4':p10.wt(ra0 if g==0 else ra1)==4,'restore_zero':True}
   if not all(checks.values()):raise AssertionError({'candidate_invalid':checks})
   rows.append({'orientation':g,'obstruction_index':oi,'pattern':o['pattern'],'reps':reps,'targets_a':[list(ra0),list(ra1),list(ra2)],'targets_b':[list(rb0),list(rb1),list(rb2)],'tag':[list(s0),list(s1)],'labels':[l0,l1,l0^l1],'desired_centrals':[ca,cb],'U4':int(u4),'checks':checks})
 return rows

ACTIVITY=((r6i._RA0!=0).astype(np.int64)<<0)|((r6i._RA1!=0).astype(np.int64)<<1)|((r6i._RB0!=0).astype(np.int64)<<2)|((r6i._RB1!=0).astype(np.int64)<<3)
ACCEPT=[int(x[0]) for x in r6i.ACCEPTING]
def compressed_q(targets_a,targets_b,perm,cA,cB,q):
 ca=[p10.codes(tuple(t),N) for t in targets_a];cb0=[p10.codes(tuple(t),N) for t in targets_b];pb=[cb0[perm[k]] for k in range(3)];base=(r6i._FRAME_A[cA]+r6i._FRAME_B[cB]+r6i._TAG_LOCAL+r6i._LWMUL[ca[0][q],r6i._RA0]+r6i._LWMUL[ca[1][q],r6i._RA1]+r6i._LWMUL[ca[2][q],r6i._RA2]+r6i._LWMUL[pb[0][q],r6i._RB0]+r6i._LWMUL[pb[1][q],r6i._RB1]+r6i._LWMUL[pb[2][q],r6i._RB2]);key=r6i._DELTA*16+ACTIVITY;mins=np.full(1024*16,np.inf);np.minimum.at(mins,key,base);idx=np.flatnonzero(np.isfinite(mins));return idx//16,idx%16,mins[idx]
def cap3_fixed(candidate,perm,cA,cB,timeout=10.0):
 qd=[compressed_q(candidate['targets_a'],candidate['targets_b'],perm,cA,cB,q) for q in range(N)];offs=[];nv=0
 for d,a,c in qd:offs.append(nv);nv+=len(d)
 koff=nv;nv+=10;yoff=nv;nv+=6;obj=np.zeros(nv);lb=np.zeros(nv);ub=np.ones(nv);ub[koff:koff+10]=2;rows=[];lo=[];hi=[]
 for q,(ds,acts,costs) in enumerate(qd):
  off=offs[q];obj[off:off+len(ds)]=costs;rows.append({off+j:1.0 for j in range(len(ds))});lo.append(1.0);hi.append(1.0)
 rows.append({yoff+i:1.0 for i in range(6)});lo.append(1.0);hi.append(1.0)
 for b in range(10):
  row={koff+b:-2.0}
  for q,(ds,acts,costs) in enumerate(qd):
   off=offs[q]
   for j,d in enumerate(ds):
    if (int(d)>>b)&1:row[off+j]=1.0
  for i,state in enumerate(ACCEPT):
   if (state>>b)&1:row[yoff+i]=-1.0
  rows.append(row);lo.append(0.0);hi.append(0.0)
 for bit in range(4):
  row={}
  for q,(ds,acts,costs) in enumerate(qd):
   off=offs[q]
   for j,a in enumerate(acts):
    if (int(a)>>bit)&1:row[off+j]=1.0
  rows.append(row);lo.append(-np.inf);hi.append(3.0)
 rr=[];cc=[];vv=[]
 for i,row in enumerate(rows):
  for j,v in row.items():rr.append(i);cc.append(j);vv.append(v)
 mat=coo_matrix((vv,(rr,cc)),shape=(len(rows),nv)).tocsr();res=milp(obj,integrality=np.ones(nv,dtype=int),bounds=Bounds(lb,ub),constraints=LinearConstraint(mat,np.array(lo),np.array(hi)),options={'time_limit':timeout,'mip_rel_gap':0.0,'presolve':True})
 if not res.success or res.x is None:return None,{'success':False,'status':int(res.status),'message':str(res.message)}
 ax=mat@res.x;eq=np.max(np.abs(ax[:15]-np.array(lo[:15])));support=np.max(ax[-4:]-3);integ=float(np.max(np.abs(res.x-np.rint(res.x))));gap=float(getattr(res,'mip_gap',0.0) or 0.0);raw=int(round(float(res.fun)));return raw-r6i.UANTI_CONSTANT,{'success':True,'status':int(res.status),'message':str(res.message),'raw_objective':raw,'cost':raw-r6i.UANTI_CONSTANT,'mip_gap':gap,'max_integrality_residual':integ,'max_equality_residual':float(eq),'max_support_violation':float(max(0.0,support)),'variables':nv,'constraints':len(rows)}
def scan(candidates):
 rows=[];positive=None;unresolved=False
 for idx,c in enumerate(candidates):
  best=10**9;solved=0;reject=None;fail=None
  for perm in PERMS:
   for ca in range(3):
    for cb in range(3):
     v,meta=cap3_fixed(c,perm,ca,cb)
     if v is None:fail={'perm':list(perm),'cA':ca,'cB':cb,'solver':meta};unresolved=True;break
     solved+=1;best=min(best,v)
     if v<=c['U4']:reject={'perm':list(perm),'cA':ca,'cB':cb,'C_cap3_config':int(v),'solver':meta};break
    if reject or fail:break
   if reject or fail:break
  row={'candidate_index':idx,'orientation':c['orientation'],'obstruction_index':c['obstruction_index'],'U4':c['U4'],'configs_solved':solved,'best_cap3_seen':None if best==10**9 else int(best),'rejection':reject,'solver_failure':fail};rows.append(row)
  if not reject and not fail and solved==54 and best>c['U4']:
   exact=r6i.shared_tag_exact(tuple(tuple(x) for x in c['targets_a']),tuple(tuple(x) for x in c['targets_b']),N);positive={'candidate_index':idx,'candidate':c,'C_cap3':int(best),'strict_gap':int(best-c['U4']),'production_C_DP':int(exact['C_shared']),'production_witness_checks':exact['checks'],'configs_solved':54};break
 return rows,positive,unresolved

def run():
 st=action_resources();s2,s3=safe_edits(st);cands=make_candidates(s2,s3);gen={'candidate_count':len(cands),'orientation_counts':{'0':sum(c['orientation']==0 for c in cands),'1':sum(c['orientation']==1 for c in cands)},'digest':hashlib.sha256(can(cands).encode()).hexdigest(),'first_candidates':cands[:4]};rows,pos,unres=scan(cands)
 if pos:term='QG9T1_R6I_SUPPORT4_TIGHT_WITNESS_EXACT'
 elif unres:term='QG9T1_CAP3_SOLVER_CANNOT_CHECK'
 elif len(cands)!=72:term='QG9T1_CANDIDATE_BINDING_FAILURE'
 else:term='QG9T1_NO_SUPPORT4_TIGHT_WITNESS_IN_FROZEN_PANEL'
 out={'schema':'ORION.QG.QG9T1.Support4Tightness.v1','issue':ISSUE,'base_revision':BASE,'terminal':term,'solver':{'scipy_version':SCIPY_VERSION,'backend':'HiGHS via scipy.optimize.milp','mip_rel_gap':0.0},'candidate_generation':gen,'scan_rows':rows,'positive_witness':pos,'cap3_model':{'n':4,'fixed_configs':54,'accepting_states':ACCEPT,'support_cap':3,'production_option_count':4096,'compression_key':'(delta10,activity4)'},'chemistry_sources_read':False,'protected_subject_read':False,'network_access':False,'support3_theorem_authority':False,'novelty_authority':False,'physical_quantum_advantage_claim':False};u=dict(out);out['result_digest']=hashlib.sha256(can(u).encode()).hexdigest();return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',default=str(OUT));a=ap.parse_args();r=run();p=Path(a.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(TOKEN+can({'terminal':r['terminal'],'digest':r['result_digest'],'candidates':r['candidate_generation']['candidate_count'],'positive':None if not r['positive_witness'] else {'index':r['positive_witness']['candidate_index'],'gap':r['positive_witness']['strict_gap']}}));return 0
if __name__=='__main__':raise SystemExit(main())
