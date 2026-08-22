#!/usr/bin/env python3
"""QG-42 production compiler transfer on the prebuilt compiler-blind panel."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter
from importlib.metadata import version
from pathlib import Path
from typing import Any
from pytket import Circuit
from pytket.architecture import Architecture
from pytket.mapping import LexiRouteRoutingMethod,MappingManager
from pytket.placement import place_with_map
from pytket.unit_id import Node
ROOT=Path(__file__).resolve().parents[3];PANEL=ROOT/'artifacts/orion-qg-qg42-panel.json';PROTO=ROOT/'development/orion-qg-regime-geometry/QG42_PYTKET_HELDOUT_SELECTION_TRANSFER_PROTOCOL_V1.md';OUT=ROOT/'artifacts/orion-qg-qg42-pytket.json';TOKEN='ORIONQG_QG42=';N=6;LAYOUTS=tuple(itertools.permutations(range(N)));ARCHS={'line6':((0,1),(1,2),(2,3),(3,4),(4,5)),'ring6':((0,1),(1,2),(2,3),(3,4),(4,5),(5,0))}
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(v:Any)->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(d):return d.get('result_digest')==sha({k:v for k,v in d.items() if k!='result_digest'})
def build(edges):
 c=Circuit(N)
 for a,b in edges:c.CX(int(a),int(b))
 return c
def route_cost(edges,arch_edges,p):
 c=build(edges);arc=Architecture(list(arch_edges));qmap={c.qubits[q]:Node(int(p[q])) for q in range(N)};place_with_map(c,qmap);ok=MappingManager(arc).route_circuit(c,[LexiRouteRoutingMethod(10)])
 if not ok:raise RuntimeError('routing failed')
 invalid=[]
 for cmd in c.get_commands():
  if len(cmd.qubits)==2 and not arc.valid_operation(cmd.qubits,True):invalid.append(str(cmd))
 if invalid:raise RuntimeError('architecture-invalid routed operation: '+invalid[0])
 return int(c.n_2qb_gates()),int(c.depth_2q()),int(c.n_gates),bool(c.has_implicit_wireswaps)
def eval_graph(edges,arch_edges):
 costs=[];depths=[];total=[];implicit=0
 for p in LAYOUTS:
  c,d,g,w=route_cost(edges,arch_edges,p);costs.append(c);depths.append(d);total.append(g);implicit+=int(w)
 m=min(costs);arg=[i for i,x in enumerate(costs) if x==m]
 return {'minimum_two_qubit_gates':m,'argmin_layout_indices':arg,'argmin_count':len(arg),'cost_range':[min(costs),max(costs)],'cost_histogram':{str(k):int(v) for k,v in sorted(Counter(costs).items())},'cost_vector_sha256':sha(costs),'depth2q_vector_sha256':sha(depths),'total_gate_vector_sha256':sha(total),'implicit_wireswap_layout_count':implicit,'instrument_varies':max(costs)>min(costs)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--panel',type=Path,default=PANEL);ap.add_argument('--output',type=Path,default=OUT);a=ap.parse_args();panel=json.loads(a.panel.read_text());pkg=version('pytket');parent={'panel_digest':valid(panel),'panel_terminal':panel.get('terminal')=='QG42_PANEL_FROZEN_BEFORE_ROUTING','panel_count':len(panel.get('pairs',[]))==12,'panel_compiler_blind':panel.get('PYTKET_IMPORTED') is False,'protocol':panel.get('protocol_sha256')==shaf(PROTO),'pytket_version':pkg=='2.18.1'}
 graph_cache={};records=[];any_var=False;any_router=False
 for pr in panel.get('pairs',[]):
  rec={'pair_index':pr['pair_index'],'degree_summary':pr['degree_summary'],'graph_A_edges':pr['graph_A_edges'],'graph_B_edges':pr['graph_B_edges'],'architectures':{}}
  for aname,aedges in ARCHS.items():
   vals=[]
   for side in ('A','B'):
    edges=tuple(tuple(x) for x in pr[f'graph_{side}_edges']);key=(edges,aname)
    if key not in graph_cache:graph_cache[key]=eval_graph(edges,aedges)
    vals.append(graph_cache[key]);any_var |= graph_cache[key]['instrument_varies'];any_router |= graph_cache[key]['cost_range'][1]>7
   x,y=vals;sa=set(x['argmin_layout_indices']);sb=set(y['argmin_layout_indices']);inter=sorted(sa&sb);same=x['minimum_two_qubit_gates']==y['minimum_two_qubit_gates'];sep=same and sa!=sb;disj=sep and not inter
   rec['architectures'][aname]={'A':x,'B':y,'same_optimum_value':same,'argmin_sets_differ':sa!=sb,'argmin_intersection_count':len(inter),'argmin_intersection_indices':inter,'jaccard':len(inter)/len(sa|sb) if sa|sb else 1.0,'selection_separation':sep,'disjoint_selection_separation':disj}
  records.append(rec)
 line=any(r['architectures']['line6']['selection_separation'] for r in records);ring=any(r['architectures']['ring6']['selection_separation'] for r in records);dline=any(r['architectures']['line6']['disjoint_selection_separation'] for r in records);dring=any(r['architectures']['ring6']['disjoint_selection_separation'] for r in records);stable=[r['pair_index'] for r in records if r['architectures']['line6']['disjoint_selection_separation'] and r['architectures']['ring6']['disjoint_selection_separation']];dead_cost=[7]*len(LAYOUTS);dead_rejected=(max(dead_cost)==min(dead_cost));layout_collapse_rejected=any((r['architectures'][a]['argmin_sets_differ'] for r in records for a in ARCHS))
 if not all(parent.values()) or not any_var or not any_router:term='QG42_CANNOT_CHECK'
 elif line and ring:term='QG42_PYTKET_SELECTION_SEPARATION_BOTH_TOPOLOGIES_MACHINE_CHECKED'
 elif line or ring:term='QG42_PYTKET_SELECTION_SEPARATION_ONE_TOPOLOGY_ONLY'
 else:term='QG42_PYTKET_NO_SELECTION_SEPARATION_ON_FROZEN_PANEL'
 out={'schema':'ORIONQG.QG42.PytketSelectionTransfer.v1','terminal':term,'protocol_sha256':shaf(PROTO),'panel_result_digest':panel.get('result_digest'),'panel_digest':panel.get('panel_digest'),'pytket_version':pkg,'parent_checks':parent,'universe':{'pairs':len(records),'graphs':len(graph_cache)//2,'layouts_per_graph_per_architecture':len(LAYOUTS),'architectures':list(ARCHS),'primary_cost':'post-routing n_2qb_gates','routing_method':'LexiRouteRoutingMethod(10)'},'records':records,'selection_separation':{'line6':line,'ring6':ring,'disjoint_line6':dline,'disjoint_ring6':dring,'topology_stable_disjoint_pair_indices':stable},'instrument_controls':{'any_layout_dependent_cost':any_var,'router_exercised':any_router,'input_cx_count_dead_instrument_rejected':dead_rejected,'layout_identity_collapse_rejected':layout_collapse_rejected},'BOUNDED_PYTKET_SELECTION_INFORMATION_AUTHORITY':term.startswith('QG42_PYTKET_'),'ALL_CIRCUIT_THEOREM':False,'ALL_PYTKET_VERSION_CLAIM':False,'OPTIMAL_ROUTING_CLAIM':False,'COMPARATIVE_COMPILER_PERFORMANCE':False,'HARDWARE_NOISE_OR_FT_CLAIM':False,'physical_quantum_advantage_claim':False,'GENERIC_SYMMETRY_DECISION_THEORY_NOVELTY':False,'novelty_authority':False};out['result_digest']=sha(out);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(TOKEN+canon({'terminal':term,'line':line,'ring':ring,'dline':dline,'dring':dring,'stable':stable,'instrument':out['instrument_controls'],'result_digest':out['result_digest']}));return 0
if __name__=='__main__':raise SystemExit(main())
