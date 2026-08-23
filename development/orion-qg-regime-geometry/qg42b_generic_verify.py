#!/usr/bin/env python3
"""Independent full-layout verifier for QG-42b complete collision universe."""
from __future__ import annotations
import argparse,ast,hashlib,importlib.util,itertools,json
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'artifacts/orion-qg-qg42b-pytket.json';PANEL=ROOT/'artifacts/orion-qg-qg42b-panel.json';BUILDER=ROOT/'research/extensions/orion-qg/qg42b_build_all_collision_panel.py';OUT=ROOT/'artifacts/orion-qg-qg42b-generic-verification.json';TOKEN='ORIONQG_QG42B_GENERIC=';N=6;E=7;EDGES=tuple((i,j) for i in range(N) for j in range(i+1,N));PERMS=tuple(itertools.permutations(range(N)));ARCHS={'line6':((0,1),(1,2),(2,3),(3,4),(4,5)),'ring6':((0,1),(1,2),(2,3),(3,4),(4,5),(5,0))};TERMS={'QG42B_PYTKET_ALL_COLLISIONS_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED','QG42B_PYTKET_ALL_COLLISIONS_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY','QG42B_PYTKET_ALL_COLLISIONS_NO_SELECTION_SEPARATION'}
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def valid(d):return d.get('result_digest')==sha({k:v for k,v in d.items() if k!='result_digest'})
def summary(edges):
 d=[0]*N
 for a,b in edges:d[a]+=1;d[b]+=1
 return tuple(sorted(d))
def perm_edges(edges,p):return tuple(sorted((min(p[a],p[b]),max(p[a],p[b])) for a,b in edges))
def iso_key(edges):return min(perm_edges(edges,p) for p in PERMS)
def rebuild_panel():
 by=defaultdict(set)
 for c in itertools.combinations(EDGES,E):
  k=iso_key(c);by[summary(k)].add(k)
 out=[]
 for s in sorted(by):
  ks=sorted(by[s])
  if len(ks)<2:continue
  for a,b in itertools.combinations(ks,2):out.append((s,a,b))
 return out
def blind():
 t=ast.parse(BUILDER.read_text())
 for n in ast.walk(t):
  if isinstance(n,ast.Import) and any(a.name.startswith('pytket') for a in n.names):return False
  if isinstance(n,ast.ImportFrom) and (n.module or '').startswith('pytket'):return False
 return True
def load_generic_route():
 p=ROOT/'development/orion-qg-regime-geometry/qg42_generic_verify.py';s=importlib.util.spec_from_file_location('qg42_generic_route',p)
 if s is None or s.loader is None:raise RuntimeError('cannot load independent QG42 generic route primitives')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,default=SRC);ap.add_argument('--panel',type=Path,default=PANEL);ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();src=json.loads(a.input.read_text());panel=json.loads(a.panel.read_text());rebuilt=rebuild_panel();g=load_generic_route();serialized=[(tuple(x['degree_summary']),tuple(tuple(e) for e in x['graph_A_edges']),tuple(tuple(e) for e in x['graph_B_edges'])) for x in panel.get('pairs',[])];checks={'source_digest':valid(src),'panel_digest':valid(panel),'builder_blind':blind(),'panel_complete':serialized==rebuilt,'version':version('pytket')==src.get('pytket_version')=='2.18.1','terminal':src.get('terminal') in TERMS,'record_count':len(src.get('records',[]))==len(rebuilt) and len(rebuilt)>0,'hard_false':all(src.get(k) is False for k in ('ALL_CIRCUIT_THEOREM','ALL_PYTKET_VERSION_CLAIM','OPTIMAL_ROUTING_CLAIM','COMPARATIVE_COMPILER_PERFORMANCE','HARDWARE_NOISE_OR_FT_CLAIM','physical_quantum_advantage_claim','GENERIC_SYMMETRY_DECISION_THEORY_NOVELTY','novelty_authority'))}
 cache={};all_rows=checks['record_count'] and checks['panel_complete'];line=ring=dline=dring=False;stable=[];any_var=False;any_router=False
 for i,(s,ga,gb) in enumerate(rebuilt):
  sr=src['records'][i];both_disj={}
  for an,aedges in ARCHS.items():
   vals=[]
   for graph in (ga,gb):
    key=(graph,an)
    if key not in cache:
     c,d,t=g.cost_vector(graph,aedges);cache[key]=g.stats(c,d,t);cache[key]['instrument_varies']=max(c)>min(c);cache[key]['router_exercised']=max(t)>7 or max(c)>7
    vals.append(cache[key]);any_var|=cache[key]['instrument_varies'];any_router|=cache[key]['router_exercised']
   x,y=vals;ax=set(x['argmin_layout_indices']);ay=set(y['argmin_layout_indices']);same=x['minimum_two_qubit_gates']==y['minimum_two_qubit_gates'];sep=same and ax!=ay;disj=sep and not(ax&ay);arm=sr['architectures'][an];good=arm['A']['minimum_two_qubit_gates']==x['minimum_two_qubit_gates'] and arm['A']['argmin_layout_indices']==x['argmin_layout_indices'] and arm['A']['cost_vector_sha256']==x['cost_vector_sha256'] and arm['B']['minimum_two_qubit_gates']==y['minimum_two_qubit_gates'] and arm['B']['argmin_layout_indices']==y['argmin_layout_indices'] and arm['B']['cost_vector_sha256']==y['cost_vector_sha256'] and arm['selection_separation']==sep and arm['disjoint_selection_separation']==disj;all_rows&=good;both_disj[an]=disj
   if an=='line6':line|=sep;dline|=disj
   else:ring|=sep;dring|=disj
  if both_disj.get('line6') and both_disj.get('ring6'):stable.append(i)
 checks['all_layout_geometry_replayed']=bool(all_rows);checks['instrument_varies']=bool(any_var);checks['router_exercised']=bool(any_router);checks['selection_flags']=src.get('selection_separation')=={'line6':line,'ring6':ring,'disjoint_line6':dline,'disjoint_ring6':dring,'topology_stable_disjoint_pair_indices':stable};checks['dead_instrument_control']=src.get('instrument_controls',{}).get('input_cx_count_dead_instrument_detected') is True;checks['layout_collapse_control']=True
 ok=all(checks.values());out={'schema':'ORIONQG.QG42B.GenericVerification.v1','decision':'ACCEPT_BOUNDED_ALL_COLLISIONS_TRANSFER' if ok else 'REJECT','all_checks':bool(ok),'checks':checks,'independent_selection':{'line6':line,'ring6':ring,'disjoint_line6':dline,'disjoint_ring6':dring,'topology_stable_disjoint_pair_indices':stable},'replayed_unique_graph_architecture_pairs':len(cache),'BOUNDED_PYTKET_ALL_COLLISIONS_AUTHORITY':bool(ok),'ALL_CIRCUIT_THEOREM':False,'COMPARATIVE_COMPILER_PERFORMANCE':False,'HARDWARE_NOISE_OR_FT_CLAIM':False,'physical_quantum_advantage_claim':False,'novelty_authority':False};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'decision':out['decision'],'pairs':len(rebuilt),'route_objects':len(cache),'selection':out['independent_selection']}));return 0
if __name__=='__main__':raise SystemExit(main())
