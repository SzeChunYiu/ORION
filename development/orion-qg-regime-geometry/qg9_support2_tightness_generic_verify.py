#!/usr/bin/env python3
from __future__ import annotations
import itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'artifacts/orion-qg-qg9-support2-tightness.json';OUT=ROOT/'artifacts/orion-qg-qg9-support2-tightness-generic-verification.json';TOKEN='ORIONQG_QG9_TIGHT_GENERIC=';INF=10**9
N=2
keys=[(x,z) for x in range(1<<N) for z in range(1<<N)];nz=[k for k in keys if k!=(0,0)]
def mul(a,b):return (a[0]^b[0],a[1]^b[1])
def wt(a):return (a[0]|a[1]).bit_count()
def symp(a,b):return ((a[0]&b[1]).bit_count()+(a[1]&b[0]).bit_count())&1
pairs=[(a,b) for a in nz for b in nz if symp(a,b)==1]
def uanti(pair):
 r=(pair[0],pair[1],mul(*pair));return min(sum((2 if c==k else 4)*wt(r[k]) for k in range(3))-10 for c in range(3))
def best_tag(pa,pb):
 # For one S, class = 2< S,R0 > + < S,R1 >. Find same class on both blocks.
 minw=[INF]*4
 for s in keys:
  ca=2*symp(s,pa[0])+symp(s,pa[1]);cb=2*symp(s,pb[0])+symp(s,pb[1])
  if ca==cb:minw[ca]=min(minw[ca],wt(s))
 best=INF
 for hi in range(4):
  for lo in range(4):
   if minw[hi]>=INF or minw[lo]>=INF:continue
   c0=2*((hi>>1)&1)+((lo>>1)&1);c1=2*(hi&1)+(lo&1)
   if c0 and c1 and c0!=c1:best=min(best,2*(minw[hi]+minw[lo]))
 return best
def restore_a(pair,t):
 r=(pair[0],pair[1],mul(*pair));return sum(wt(mul(t[k],r[k])) for k in range(3))
def restore_b(pair,t):
 r=(pair[0],pair[1],mul(*pair));return min(sum(wt(mul(t[perm[k]],r[k])) for k in range(3)) for perm in itertools.permutations(range(3)))
def exact_caps(ta,tb):
 ua=[uanti(p)+restore_a(p,ta) for p in pairs];ub=[uanti(p)+restore_b(p,tb) for p in pairs];mw=[max(wt(p[0]),wt(p[1])) for p in pairs]
 bt=[[best_tag(pa,pb) for pb in pairs] for pa in pairs]
 out={}
 for cap in (1,2):
  best=INF;witness=None
  ia=[i for i,x in enumerate(mw) if x<=cap]
  for i in ia:
   for j in ia:
    c=ua[i]+ub[j]+bt[i][j]
    if c<best:best=c;witness=(i,j)
  out[cap]={'cost':best,'pair_indices':witness}
 return out
def kt(v):return (int(v[0]),int(v[1]))
def main():
 a=json.loads(ART.read_text());sel=a.get('selected')
 if sel is None:
  out={'schema':'ORION.QG.QG9.TightnessGenericVerification.v1','decision':'NEGATIVE_PANEL_NOT_INDEPENDENTLY_REPLAYED','checks':{'no_selected_witness':True,'tightness_authority_false':a.get('tightness_authority') is False},'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+json.dumps(out,sort_keys=True,separators=(',',':')));return 0
 ta=tuple(kt(x) for x in sel['targets_A']);tb=tuple(kt(x) for x in sel['targets_B']);caps=exact_caps(ta,tb)
 checks={'n2_pair_count_120':len(pairs)==120,'targets_nonzero':all(x!=(0,0) for x in ta+tb),'cap1_exact_match':caps[1]['cost']==sel['C_cap1'],'cap2_exact_match':caps[2]['cost']==sel['C_cap2'],'strict_gap':caps[2]['cost']<caps[1]['cost'],'production_matches_cap2':a.get('production_referee',{}).get('C_shared')==caps[2]['cost'],'parent_tightness_terminal':a.get('terminal')=='QG9_SUPPORT2_TIGHT_WITNESS_MACHINE_VERIFIED'}
 dec='ACCEPT_TIGHTNESS' if all(checks.values()) else 'REJECT';out={'schema':'ORION.QG.QG9.TightnessGenericVerification.v1','decision':dec,'checks':checks,'independent_caps':{'cap1':caps[1]['cost'],'cap2':caps[2]['cost'],'gap':caps[1]['cost']-caps[2]['cost']},'novelty_authority':False};OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+json.dumps(out,sort_keys=True,separators=(',',':')));return 0
if __name__=='__main__':raise SystemExit(main())
