#!/usr/bin/env python3
"""QG-42 compiler-blind graph-panel builder. Deliberately has no pytket import."""
from __future__ import annotations
import hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];PROTO=ROOT/'development/orion-qg-regime-geometry/QG42_PYTKET_HELDOUT_SELECTION_TRANSFER_PROTOCOL_V1.md';OUT=ROOT/'artifacts/orion-qg-qg42-panel.json';N=6;E=7;PAIRS=tuple((i,j) for i in range(N) for j in range(i+1,N));PERMS=tuple(itertools.permutations(range(N)))
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v):return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def summary(edges):
 d=[0]*N
 for a,b in edges:d[a]+=1;d[b]+=1
 return tuple(sorted(d))
def perm_edges(edges,p):return tuple(sorted((min(p[a],p[b]),max(p[a],p[b])) for a,b in edges))
def iso_key(edges):return min(perm_edges(edges,p) for p in PERMS)
def main():
 by=defaultdict(set);enumerated=0
 for comb in itertools.combinations(PAIRS,E):
  enumerated+=1;k=iso_key(comb);by[summary(k)].add(k)
 candidates=[]
 for s in sorted(by):
  ks=sorted(by[s])
  if len(ks)<2:continue
  for j in range(0,len(ks)-1,2):candidates.append((s,ks[j],ks[j+1]))
 panel=candidates[:12]
 if len(panel)<12:terminal='QG42_CANNOT_CHECK_PANEL_CONSTRUCTION'
 else:terminal='QG42_PANEL_FROZEN_BEFORE_ROUTING'
 pairs=[{'pair_index':i,'degree_summary':list(s),'graph_A_edges':[list(e) for e in a],'graph_B_edges':[list(e) for e in b],'graph_A_iso_key_sha256':sha(a),'graph_B_iso_key_sha256':sha(b)} for i,(s,a,b) in enumerate(panel)]
 panel_digest=sha(pairs);out={'schema':'ORIONQG.QG42.Panel.v1','terminal':terminal,'protocol_sha256':shaf(PROTO),'n_qubits':N,'edge_count':E,'labelled_graphs_enumerated':enumerated,'expected_labelled_graphs':6435,'isomorphism_classes':sum(len(v) for v in by.values()),'summary_fibers_with_multiple_isomorphism_classes':sum(len(v)>1 for v in by.values()),'candidate_disjoint_pairs_before_quota':len(candidates),'pair_quota':12,'pairs':pairs,'panel_digest':panel_digest,'PYTKET_IMPORTED':False};out['result_digest']=sha(out);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('ORIONQG_QG42_PANEL='+canon({'terminal':terminal,'pairs':len(panel),'iso_classes':out['isomorphism_classes'],'fibers':out['summary_fibers_with_multiple_isomorphism_classes'],'panel_digest':panel_digest}));return 0
if __name__=='__main__':raise SystemExit(main())
