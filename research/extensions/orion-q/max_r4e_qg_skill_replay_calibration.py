#!/usr/bin/env python3
"""MAX-R4E replay calibration for QG-derived ORION-Q research skills on real compiler families."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PROTO=ROOT/"development/orion-q-max-r0/MAX_R4E_QG_SKILL_REPLAY_CALIBRATION_PROTOCOL_V1.md"
QG15B=ROOT/"research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json"
QG9=ROOT/"artifacts/max-r4e-qg9-v6.json"
OUT=ROOT/"artifacts/orion-q-max-r4e-qg-skill-replay.json"
TOKEN="ORIONQ_MAX_R4E_QG_REPLAY="
POS="MAX_R4E_QG_SKILLS_HAVE_REAL_COMPILER_OPERATIONAL_VALUE__REPLAY_CALIBRATED"
BITS=((0,0),(1,0),(1,1),(0,1))
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sy(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def symp_str(a,b):return sum(sy(x,y) for x,y in zip(a,b))&1
def support(xs):return sum(x!=0 for x in xs)
def pair_counts(n,k):
 arr=[x for x in itertools.product(range(4),repeat=n) if support(x)<=k]
 pairs=sum(1 for a in arr for b in arr if symp_str(a,b)==1)
 return {"strings":len(arr),"ordered_symplectic_one_pairs":pairs}
def walk_dfs(obj):
 total=0;trunc=0
 if isinstance(obj,dict):
  if isinstance(obj.get("dfs_nodes"),int):total+=obj["dfs_nodes"]
  if obj.get("truncated") is True:trunc+=1
  for v in obj.values():
   a,b=walk_dfs(v);total+=a;trunc+=b
 elif isinstance(obj,list):
  for v in obj:
   a,b=walk_dfs(v);total+=a;trunc+=b
 return total,trunc
def higher_dfs(surface):
 total=0;trunc=0
 if not isinstance(surface,dict):return 0,0
 for key,v in surface.items():
  if str(key).startswith("K1_"):continue
  a,b=walk_dfs(v);total+=a;trunc+=b
 return total,trunc
def conj_surface(arm):
 stats=arm.get("conjunction_stats",{})
 return {k:{"raw_conjunctions":int(v.get("raw_conjunctions",0)),"distinct_vectors":int(v.get("distinct_vectors",0))} for k,v in stats.items() if isinstance(v,dict)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--qg9",type=Path,default=QG9);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();q9=json.loads(ns.qg9.read_text());q15=json.loads(QG15B.read_text())
 r6i_ok=q9.get("terminal")=="QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED" and q9.get("support_bound")==1 and q9.get("intrinsic_support_number")==1 and q9.get("gates") and all(q9["gates"].values())
 r6i=[]
 for n in range(2,7):
  c1=pair_counts(n,1);c2=pair_counts(n,2);r6i.append({"n":n,"cap1":c1,"cap2":c2,"pair_count_ratio_cap2_over_cap1":c2["ordered_symplectic_one_pairs"]/c1["ordered_symplectic_one_pairs"]})
 six=q15.get("sixlcu",{});sp=q15.get("stabprep",{})
 six_zero=six.get("cell_table",{}).get("mixed_cells")==0 and q15.get("q3",{}).get("E_floor")==0 and q15.get("q3",{}).get("zero_error_cells",{}).get("headline_cell")==[1,1] and q15.get("q3",{}).get("zero_error_cells",{}).get("minimal_cells")==[[1,1]]
 six_conj=conj_surface(six);six_higher_raw=sum(v["raw_conjunctions"] for k,v in six_conj.items() if k in {"K2","K3"});six_higher_dist=sum(v["distinct_vectors"] for k,v in six_conj.items() if k in {"K2","K3"});six_higher_dfs,six_trunc=higher_dfs(six.get("minerr_surface",{}))
 sp_mixed=(sp.get("cell_table",{}).get("mixed_cells")==12 or q15.get("q2",{}).get("mixed_cell_count")==12);sp_floor=q15.get("q2",{}).get("E_floor")==43;sp_terminal=q15.get("q2",{}).get("terminal")=="ZERO_UNACHIEVABLE_ANY_BUDGET";sp_dfs,sp_trunc=walk_dfs(sp.get("minerr_surface",sp));sp_conj=conj_surface(sp);sp_raw=sum(v["raw_conjunctions"] for v in sp_conj.values());sp_dist=sum(v["distinct_vectors"] for v in sp_conj.values())
 actions={"R6I":"RESTRICT_TO_PROVED_SUPPORT1" if r6i_ok else "CANNOT_CHECK","SixLCU":"USE_MINIMAL_EXACT_K1D1_PREDICATE" if six_zero else "CANNOT_CHECK","StabPrep":"REJECT_ZERO_ERROR_IN_FROZEN_VOCAB__ESCALATE_REPRESENTATION" if sp_mixed and sp_floor and sp_terminal else "CANNOT_CHECK"}
 gates={"r6i_replay":r6i_ok,"r6i_pair_reduction_all_n2_n6":all(x["cap1"]["ordered_symplectic_one_pairs"]<x["cap2"]["ordered_symplectic_one_pairs"] for x in r6i),"sixlcu_exact_minimal":six_zero,"stabprep_mixed_barrier":sp_mixed and sp_floor and sp_terminal,"actions_exact":actions=={"R6I":"RESTRICT_TO_PROVED_SUPPORT1","SixLCU":"USE_MINIMAL_EXACT_K1D1_PREDICATE","StabPrep":"REJECT_ZERO_ERROR_IN_FROZEN_VOCAB__ESCALATE_REPRESENTATION"}}
 ok=all(gates.values());term=POS if ok else "MAX_R4E_QG_SKILL_REPLAY_CANNOT_CHECK"
 out={"schema":"ORIONQ.MAXR4E.QGSkillReplayCalibration.v1","issue":"SzeChunYiu/ORION#903","terminal":term,"protocol_sha256":sha_file(PROTO),"parent_hashes":{"qg15b":sha_file(QG15B),"qg9_replay":sha_file(ns.qg9)},"gates":gates,"required_actions":actions,"r6i_support_localization":{"rows":r6i,"minimum_pair_reduction_ratio":min(x["pair_count_ratio_cap2_over_cap1"] for x in r6i),"maximum_pair_reduction_ratio":max(x["pair_count_ratio_cap2_over_cap1"] for x in r6i)},"sixlcu_minimal_predicate":{"conjunction_surface":six_conj,"higher_order_raw_conjunctions_avoidable_for_minimal_exact_classifier_task":six_higher_raw,"higher_order_distinct_vectors_avoidable_for_minimal_exact_classifier_task":six_higher_dist,"higher_order_dfs_nodes_avoidable_for_minimal_exact_classifier_task":six_higher_dfs,"higher_order_truncated_cells":six_trunc},"stabprep_information_barrier":{"mixed_cells":12 if sp_mixed else None,"E_floor":q15.get("q2",{}).get("E_floor"),"zero_error_terminal":q15.get("q2",{}).get("terminal"),"predicate_search_dfs_nodes_avoidable_for_binary_zero_error_existence_question":sp_dfs,"truncated_lattice_cells":sp_trunc,"conjunction_surface":sp_conj,"raw_conjunctions_constructed":sp_raw,"distinct_conjunction_vectors_constructed":sp_dist},"interpretation":"Replay calibration only: exact theorem/certificate-aware skill contracts remove or preempt real compiler search work without changing scientific answers. Historical search may remain useful for richer questions such as minimum error or predicate complexity.","MAX_R4E_QG_SKILLS_REAL_COMPILER_OPERATIONAL_VALUE_REPLAY":bool(ok),"MAX_R4E_QG_SKILLS_COMPILER_GENERAL":False,"MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE":False,"MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER":False,"REAL_QUANTUM_SUPERIORITY_AUTHORIZED":False,"NOVELTY_AUTHORIZED":False};raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":term,"actions":actions,"r6i_min_ratio":out["r6i_support_localization"]["minimum_pair_reduction_ratio"],"r6i_max_ratio":out["r6i_support_localization"]["maximum_pair_reduction_ratio"],"six_higher_raw":six_higher_raw,"stabprep_dfs":sp_dfs,"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
