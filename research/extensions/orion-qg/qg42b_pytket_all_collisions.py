#!/usr/bin/env python3
"""QG-42b production evaluation of every compiler-blind degree-summary collision pair."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json
from importlib.metadata import version
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[3]
PANEL=ROOT/'artifacts/orion-qg-qg42b-panel.json'
PROTO=ROOT/'development/orion-qg-regime-geometry/QG42B_PYTKET_ALL_COLLISIONS_PROTOCOL_V1.md'
OUT=ROOT/'artifacts/orion-qg-qg42b-pytket.json'
TOKEN='ORIONQG_QG42B='
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(d):return d.get('result_digest')==sha({k:v for k,v in d.items() if k!='result_digest'})
def load_route_primitives():
 p=ROOT/'research/extensions/orion-qg/qg42_pytket_selection_transfer.py';s=importlib.util.spec_from_file_location('qg42_route_primitives',p)
 if s is None or s.loader is None:raise RuntimeError('cannot load frozen QG42 route primitives')
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--panel',type=Path,default=PANEL);ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();panel=json.loads(a.panel.read_text());m=load_route_primitives();pkg=version('pytket')
 parent={'panel_digest':valid(panel),'panel_terminal':panel.get('terminal')=='QG42B_PANEL_FROZEN_BEFORE_ROUTING','nonempty':panel.get('complete_collision_pair_count',0)>0,'compiler_blind':panel.get('PYTKET_IMPORTED') is False,'protocol':panel.get('protocol_sha256')==shaf(PROTO),'pytket_version':pkg=='2.18.1'}
 graph_cache={};records=[];any_var=False;any_router=False
 for pr in panel.get('pairs',[]):
  rec={'pair_index':pr['pair_index'],'degree_summary':pr['degree_summary'],'graph_A_edges':pr['graph_A_edges'],'graph_B_edges':pr['graph_B_edges'],'architectures':{}}
  for aname,aedges in m.ARCHS.items():
   vals=[]
   for side in ('A','B'):
    edges=tuple(tuple(x) for x in pr[f'graph_{side}_edges']);key=(edges,aname)
    if key not in graph_cache:graph_cache[key]=m.eval_graph(edges,aedges)
    vals.append(graph_cache[key]);any_var|=graph_cache[key]['instrument_varies'];any_router|=graph_cache[key]['router_exercised']
   x,y=vals;sa=set(x['argmin_layout_indices']);sb=set(y['argmin_layout_indices']);inter=sorted(sa&sb);same=x['minimum_two_qubit_gates']==y['minimum_two_qubit_gates'];sep=same and sa!=sb;disj=sep and not inter
   rec['architectures'][aname]={'A':x,'B':y,'same_optimum_value':same,'argmin_sets_differ':sa!=sb,'argmin_intersection_count':len(inter),'argmin_intersection_indices':inter,'jaccard':len(inter)/len(sa|sb) if sa|sb else 1.0,'selection_separation':sep,'disjoint_selection_separation':disj}
  records.append(rec)
 line=any(r['architectures']['line6']['selection_separation'] for r in records);ring=any(r['architectures']['ring6']['selection_separation'] for r in records);dline=any(r['architectures']['line6']['disjoint_selection_separation'] for r in records);dring=any(r['architectures']['ring6']['disjoint_selection_separation'] for r in records);stable=[r['pair_index'] for r in records if r['architectures']['line6']['disjoint_selection_separation'] and r['architectures']['ring6']['disjoint_selection_separation']]
 dead_detected=len(set([7]*720))==1
 if not all(parent.values()) or not any_var or not any_router or not dead_detected:term='QG42B_CANNOT_CHECK'
 elif line and ring:term='QG42B_PYTKET_ALL_COLLISIONS_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED'
 elif line or ring:term='QG42B_PYTKET_ALL_COLLISIONS_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY'
 else:term='QG42B_PYTKET_ALL_COLLISIONS_NO_SELECTION_SEPARATION'
 out={'schema':'ORIONQG.QG42B.PytketAllCollisions.v1','terminal':term,'protocol_sha256':shaf(PROTO),'panel_result_digest':panel.get('result_digest'),'panel_digest':panel.get('panel_digest'),'pytket_version':pkg,'parent_checks':parent,'universe':{'collision_pairs':len(records),'unique_graphs':panel.get('unique_graphs_in_collision_universe'),'evaluated_graph_architecture_pairs':len(graph_cache),'layouts_per_graph_per_architecture':720,'architectures':['line6','ring6'],'primary_cost':'post-routing n_2qb_gates','routing_method':'LexiRouteRoutingMethod(10)'},'records':records,'selection_separation':{'line6':line,'ring6':ring,'disjoint_line6':dline,'disjoint_ring6':dring,'topology_stable_disjoint_pair_indices':stable},'instrument_controls':{'any_layout_dependent_cost':any_var,'router_exercised':any_router,'input_cx_count_dead_instrument_detected':dead_detected},'BOUNDED_PYTKET_ALL_COLLISIONS_AUTHORITY':term.startswith('QG42B_PYTKET_'),'ALL_CIRCUIT_THEOREM':False,'ALL_PYTKET_VERSION_CLAIM':False,'OPTIMAL_ROUTING_CLAIM':False,'COMPARATIVE_COMPILER_PERFORMANCE':False,'HARDWARE_NOISE_OR_FT_CLAIM':False,'physical_quantum_advantage_claim':False,'GENERIC_SYMMETRY_DECISION_THEORY_NOVELTY':False,'novelty_authority':False};out['result_digest']=sha(out);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':term,'pairs':len(records),'graphs':panel.get('unique_graphs_in_collision_universe'),'line':line,'ring':ring,'dline':dline,'dring':dring,'stable':stable,'result_digest':out['result_digest']}));return 0
if __name__=='__main__':raise SystemExit(main())
