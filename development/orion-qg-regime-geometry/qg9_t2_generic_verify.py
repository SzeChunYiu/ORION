#!/usr/bin/env python3
"""Independent generic-ORION verification for QG-9 T2.

This implementation does not import production R6I algebra or the production
cap1 helper. Static support1 Tag compatibility is cached once; scientific
search semantics are unchanged.
"""
from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
S1=ROOT/'artifacts/orion-qg-qg9-t2-stage1.json';RES=ROOT/'artifacts/orion-qg-qg9-t2-result.json';OUT=ROOT/'artifacts/orion-qg-qg9-t2-generic-verification.json';TOKEN='ORIONQG_QG9_T2_GENERIC='
def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def K(x):return tuple(int(v) for v in x)
def mul(a,b):return (a[0]^b[0],a[1]^b[1])
def wt(a):return (a[0]|a[1]).bit_count()
def symp(a,b):return (((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count())&1)
KEYS=tuple((x,z) for x in range(4) for z in range(4))
def uanti(a,b,c):
 r=(a,b,mul(a,b));m=[4,4,4];m[c]=2;return sum(m[i]*wt(r[i]) for i in range(3))-10
def frame_pairs():
 nz=[k for k in KEYS if k!=(0,0) and wt(k)<=1]
 ps=tuple((a,b) for a in nz for b in nz if symp(a,b)==1)
 if len(ps)!=12:raise AssertionError(len(ps))
 return ps
PAIRS=frame_pairs()
def labels(s0,s1,a,b):return 2*symp(s0,a)+symp(s1,a),2*symp(s0,b)+symp(s1,b)
def build_tag_table():
 rows=[]
 for pa in PAIRS:
  out=[]
  for pb in PAIRS:
   best=None
   for s0 in KEYS:
    for s1 in KEYS:
     la=labels(s0,s1,*pa);lb=labels(s0,s1,*pb)
     if la!=lb or la[0] not in (1,2,3) or la[1] not in (1,2,3) or la[0]==la[1]:continue
     z=(2*(wt(s0)+wt(s1)),s0,s1,la)
     if best is None or z<best:best=z
   out.append(best)
  rows.append(tuple(out))
 return tuple(rows)
TAG_TABLE=build_tag_table()
def block_cost(pair,targets,permute):
 a,b=pair;r=(a,b,mul(a,b));best=None;perms=itertools.permutations(range(3)) if permute else ((0,1,2),)
 for p in perms:
  ts=tuple(targets[p[i]] for i in range(3));rest=sum(wt(mul(ts[i],r[i])) for i in range(3))
  for c in range(3):
   row=(uanti(a,b,c)+rest,tuple(p),c)
   if best is None or row<best:best=row
 return best
def cap1(targets_a,targets_b):
 A=[block_cost(p,targets_a,False) for p in PAIRS];B=[block_cost(p,targets_b,True) for p in PAIRS];best=None
 for i in range(12):
  for j in range(12):
   t=TAG_TABLE[i][j]
   if t is None:continue
   row=(A[i][0]+B[j][0]+t[0],i,j,A[i],B[j],t)
   if best is None or row<best:best=row
 return best
def candidate_u2(c):
 r0=K(c['R0']);r1=K(c['R1']);s0=K(c['S0']);s1=K(c['S1']);r2=mul(r0,r1)
 if list(r2)!=c['R2']:return None
 labs=labels(s0,s1,r0,r1)
 if labs[0] not in (1,2,3) or labs[1] not in (1,2,3) or labs[0]==labs[1]:return None
 return 2*min(uanti(r0,r1,k) for k in range(3))+2*(wt(s0)+wt(s1))
def verify_dp_witness(cand,pos):
 w=pos['production_witness'];ta=tuple(K(x) for x in cand['targets_A']);tb=tuple(K(x) for x in cand['targets_B']);RA=tuple(K(x) for x in w['RA']);RB=tuple(K(x) for x in w['RB']);s0=K(w['S0']);s1=K(w['S1']);perm=tuple(w['relative_B_permutation']);ca=int(w['central_A']);cb=int(w['central_B'])
 if RA[2]!=mul(RA[0],RA[1]) or RB[2]!=mul(RB[0],RB[1]) or symp(RA[0],RA[1])!=1 or symp(RB[0],RB[1])!=1:return False,None
 la=labels(s0,s1,RA[0],RA[1]);lb=labels(s0,s1,RB[0],RB[1])
 if la!=lb or la[0] not in (1,2,3) or la[1] not in (1,2,3) or la[0]==la[1]:return False,None
 rb_targets=tuple(tb[perm[i]] for i in range(3));cost=uanti(RA[0],RA[1],ca)+uanti(RB[0],RB[1],cb)+2*(wt(s0)+wt(s1))+sum(wt(mul(ta[i],RA[i])) for i in range(3))+sum(wt(mul(rb_targets[i],RB[i])) for i in range(3));return cost==int(pos['C_DP'])==int(w['C_shared']),cost
def main():
 s1=json.loads(S1.read_text());res=json.loads(RES.read_text());su=dict(s1);sd=su.pop('result_digest');ru=dict(res);rd=ru.pop('result_digest')
 checks={'stage1_digest':sd==hashlib.sha256(canonical(su).encode()).hexdigest(),'result_digest':rd==hashlib.sha256(canonical(ru).encode()).hexdigest(),'candidate_digest':s1.get('candidate_digest')==hashlib.sha256(canonical(s1['candidates']).encode()).hexdigest(),'candidate_count_positive':s1.get('canonical_candidate_count',0)>0,'cap1_pair_count_12':len(PAIRS)==12,'stage1_no_ground_truth':s1.get('cap1_opened') is False and s1.get('unrestricted_dp_opened') is False,'authority_ceiling':res.get('support1_authority') is False and res.get('novelty_authority') is False and res.get('physical_quantum_advantage_claim') is False}
 candidate_by={c['candidate_index']:c for c in s1['candidates']};cache={};row_checks=[]
 for row in res['rows']:
  c=candidate_by[row['candidate_index']];u2=candidate_u2(c);ta=tuple(K(x) for x in c['targets_A']);tb=tuple(K(x) for x in c['targets_B']);ck=(ta,tb)
  if ck not in cache:cache[ck]=cap1(ta,tb)
  b=cache[ck];row_checks.append(u2==int(c['U2']) and int(b[0])==int(row['C_cap1']) and (u2<int(b[0]))==bool(row['strict_gap']))
 checks['all_evaluated_rows_independent']=all(row_checks) and len(row_checks)==len(res['rows']);checks['unique_target_cache_not_larger_than_rows']=len(cache)<=len(res['rows'])
 pos=res.get('positive_witness');witness_ok=True;strict_ok=True
 if pos is not None:
  c=pos['candidate'];ta=tuple(K(x) for x in c['targets_A']);tb=tuple(K(x) for x in c['targets_B']);ck=(ta,tb)
  if ck not in cache:cache[ck]=cap1(ta,tb)
  b=cache[ck];strict_ok=int(pos['C_DP'])<=int(c['U2'])<int(b[0]);witness_ok,_=verify_dp_witness(c,pos)
 checks['positive_strict_gap_independent']=strict_ok;checks['production_witness_independent']=witness_ok;decision='ACCEPT' if all(checks.values()) else 'REJECT'
 out={'schema':'ORION.QG.QG9.T2.GenericVerification.v1','issue':'SzeChunYiu/ORION#803','decision':decision,'checks':checks,'terminal':res.get('terminal'),'positive':pos is not None,'independent_cap1_pair_count':len(PAIRS),'unique_target_pair_classes_checked':len(cache),'support1_authority':False,'novelty_authority':False};OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canonical(out));return 0
if __name__=='__main__':raise SystemExit(main())
