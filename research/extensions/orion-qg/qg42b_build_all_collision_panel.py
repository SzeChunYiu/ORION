#!/usr/bin/env python3
"""QG-42b compiler-blind builder for every degree-summary collision pair."""
from __future__ import annotations
import hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[3]
PROTO=ROOT/'development/orion-qg-regime-geometry/QG42B_PYTKET_ALL_COLLISIONS_PROTOCOL_V1.md'
OUT=ROOT/'artifacts/orion-qg-qg42b-panel.json'
N=6;E=7
EDGES=tuple((i,j) for i in range(N) for j in range(i+1,N))
PERMS=tuple(itertools.permutations(range(N)))
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def summary(edges):
 d=[0]*N
 for a,b in edges:d[a]+=1;d[b]+=1
 return tuple(sorted(d))
def perm_edges(edges,p):return tuple(sorted((min(p[a],p[b]),max(p[a],p[b])) for a,b in edges))
def iso_key(edges):return min(perm_edges(edges,p) for p in PERMS)
def main():
 by=defaultdict(set)
 enumerated=0
 for comb in itertools.combinations(EDGES,E):
  enumerated+=1
  k=iso_key(comb)
  by[summary(k)].add(k)
 collision={s:tuple(sorted(v)) for s,v in by.items() if len(v)>=2}
 pairs=[]
 for s in sorted(collision):
  ks=collision[s]
  for a,b in itertools.combinations(ks,2):
   pairs.append({'pair_index':len(pairs),'degree_summary':list(s),'graph_A_edges':[list(e) for e in a],'graph_B_edges':[list(e) for e in b],'graph_A_iso_key_sha256':sha(a),'graph_B_iso_key_sha256':sha(b)})
 unique=sorted({tuple(tuple(e) for e in p[k]) for p in pairs for k in ('graph_A_edges','graph_B_edges')})
 terminal='QG42B_PANEL_FROZEN_BEFORE_ROUTING' if pairs else 'QG42B_CANNOT_CHECK_EMPTY_COLLISION_UNIVERSE'
 out={'schema':'ORIONQG.QG42B.Panel.v1','terminal':terminal,'protocol_sha256':shaf(PROTO),'n_qubits':N,'edge_count':E,'labelled_graphs_enumerated':enumerated,'expected_labelled_graphs':6435,'isomorphism_classes_total':sum(len(v) for v in by.values()),'collision_fiber_count':len(collision),'collision_fiber_sizes':{canon(s):len(collision[s]) for s in sorted(collision)},'complete_collision_pair_count':len(pairs),'unique_graphs_in_collision_universe':len(unique),'pairs':pairs,'panel_digest':sha(pairs),'PYTKET_IMPORTED':False}
 out['result_digest']=sha(out)
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('ORIONQG_QG42B_PANEL='+canon({'terminal':terminal,'iso_classes':out['isomorphism_classes_total'],'fibers':out['collision_fiber_count'],'fiber_sizes':out['collision_fiber_sizes'],'pairs':len(pairs),'unique_graphs':len(unique),'panel_digest':out['panel_digest']}));return 0
if __name__=='__main__':raise SystemExit(main())
