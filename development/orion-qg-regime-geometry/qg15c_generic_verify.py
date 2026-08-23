#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; QG=ROOT/'research/extensions/orion-qg'; sys.path.insert(0,str(QG))
import qg15_third_family as q15  # noqa:E402
RESULT=ROOT/'artifacts/orion-qg-qg15c-enlarged-vocab.json'; PROTOCOL=ROOT/'development/orion-qg-regime-geometry/QG15C_ENLARGED_VOCAB_PROTOCOL_V1.md'; OUT=ROOT/'artifacts/orion-qg-qg15c-generic.json'; TOKEN='ORIONQG_QG15C_GENERIC='; K=('H','S','SDG','CX'); KC={x:i for i,x in enumerate(K)}
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def stat(a): return min(a),max(a),sum(x*x for x in a),sum(x==0 for x in a)
def vec(state,n,dist):
 prep,cd,f,path=q15.donor(state,n); lb,rx,c=q15.lower_bound(state,n); b=[f['nCZ'],f['nY'],f['nSignX'],f['nSignZ'],f['nCN'],cd,rx,c,lb,cd-lb,n-c,f['nCN']-(n-1),cd-2*n]; tot=Counter(); loads={x:[0]*n for x in ('H','S','SDG','IN','OUT')}; edges=Counter(); kinds=[]
 for g in path:
  kind=g[0]; tot[kind]+=1; kinds.append(kind)
  if kind=='CX': edges[(g[1],g[2])]+=1; loads['OUT'][g[1]]+=1; loads['IN'][g[2]]+=1
  else: loads[kind][g[1]]+=1
 b += [tot[x] for x in K]
 for x in ('H','S','SDG','IN','OUT'): b += list(stat(loads[x]))
 indeg=[sum(edges[(c,t)]>0 for c in range(n) if c!=t) for t in range(n)]; outdeg=[sum(edges[(c,t)]>0 for t in range(n) if t!=c) for c in range(n)]; b += [len(edges),max(edges.values()) if edges else 0,sum(v*v for v in edges.values()),sum(edges[(a,z)]>0 and edges[(z,a)]>0 for a in range(n) for z in range(a+1,n)),max(indeg) if indeg else 0,max(outdeg) if outdeg else 0,sum(x*x for x in indeg),sum(x*x for x in outdeg)]
 tr=Counter((KC[a],KC[z]) for a,z in zip(kinds,kinds[1:])); b += [tr[(a,z)] for a in range(4) for z in range(4)]
 if kinds:
  runs=[]; cur=kinds[0]; size=1
  for x in kinds[1:]:
   if x==cur: size+=1
   else: runs.append(size); cur=x; size=1
  runs.append(size); b += [KC[kinds[0]],KC[kinds[-1]],len(runs),max(runs),len(set(kinds))]
 else: b += [4,4,0,0,0]
 return tuple(int(x) for x in b), dist[state]==cd

def main():
 a=json.loads(RESULT.read_text()); u=dict(a); obs=u.pop('result_digest',None); cells=defaultdict(lambda:[0,0]); per={}
 for n in (1,2,3):
  dist=q15.referee(n); exact=0
  for s in sorted(dist):
   v,l=vec(s,n,dist); cells[v][0 if l else 1]+=1; exact+=int(l)
  per[str(n)]={'instances':len(dist),'donor_exact':exact}
 mixed=[(v,p,n) for v,(p,n) in cells.items() if p and n]; floor=sum(min(p,n) for _v,p,n in mixed)
 per_n_match=all(per[k]['instances']==a['domain'][k]['instances'] and per[k]['donor_exact']==a['domain'][k]['donor_exact'] for k in per)
 checks={'schema':a.get('schema')=='ORION.QG.QG15C.EnlargedVocabulary.v1','digest':obs==hashlib.sha256(canonical(u).encode()).hexdigest(),'protocol':a.get('protocol_sha256')==hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'feature_count':all(len(v)==a.get('feature_count') for v in cells),'training_1146':sum(x['instances'] for x in per.values())==1146,'unique_cells':len(cells)==a.get('unique_feature_cells'),'mixed_count':len(mixed)==a.get('mixed_cell_count'),'floor':floor==a.get('irreducible_error_floor'),'per_n':per_n_match,'no_overclaim':a.get('novelty_authority') is False and a.get('physical_quantum_advantage_claim') is False}
 negative=a.get('terminal')=='QG15C_ENLARGED_DONOR_PATH_VOCABULARY_STILL_INSUFFICIENT__MIXED_CELLS_MACHINE_VERIFIED'; positive=a.get('terminal')=='QG15C_L2_FEATURE_DETERMINED_ON_COMPLETE_NLE3__HELDOUT_STAGE_REQUIRED'; consistent=(negative and len(mixed)>0) or (positive and len(mixed)==0); checks['terminal_consistent']=consistent; decision=('ACCEPT_INSUFFICIENT' if negative else 'ACCEPT_HELDOUT_REQUIRED') if all(checks.values()) else 'REJECT'; out={'schema':'ORION.QG.QG15C.Generic.v1','issue':'SzeChunYiu/ORION#840','decision':decision,'checks':checks,'all_checks':all(checks.values()),'mixed_cell_count':len(mixed),'irreducible_error_floor':floor,'terminal':a.get('terminal'),'novelty_authority':False}; OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(TOKEN+canonical(out)); return 0
if __name__=='__main__': raise SystemExit(main())
