#!/usr/bin/env python3
"""Independent verifier for MAX-R4E QG-derived real-compiler replay calibration."""
from __future__ import annotations
import argparse,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/"artifacts/orion-q-max-r4e-qg-skill-replay.json";QG15B=ROOT/"research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json";QG9=ROOT/"artifacts/max-r4e-qg9-v6.json";OUT=ROOT/"artifacts/orion-q-max-r4e-qg-skill-replay-generic.json";TOKEN="ORIONQ_MAX_R4E_QG_REPLAY_GENERIC=";POS="MAX_R4E_QG_SKILLS_HAVE_REAL_COMPILER_OPERATIONAL_VALUE__REPLAY_CALIBRATED";BITS=((0,0),(1,0),(1,1),(0,1))
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def sy(a,b):ax,az=BITS[a];bx,bz=BITS[b];return (ax*bz+az*bx)&1
def symp(a,b):return sum(sy(x,y) for x,y in zip(a,b))&1
def count(n,k):
 arr=[x for x in itertools.product(range(4),repeat=n) if sum(v!=0 for v in x)<=k];return {"strings":len(arr),"ordered_symplectic_one_pairs":sum(1 for a in arr for b in arr if symp(a,b)==1)}
def walk(o):
 dfs=tr=0
 if isinstance(o,dict):
  if isinstance(o.get("dfs_nodes"),int):dfs+=o["dfs_nodes"]
  if o.get("truncated") is True:tr+=1
  for v in o.values():a,b=walk(v);dfs+=a;tr+=b
 elif isinstance(o,list):
  for v in o:a,b=walk(v);dfs+=a;tr+=b
 return dfs,tr
def high(surface):
 dfs=tr=0
 if isinstance(surface,dict):
  for k,v in surface.items():
   if str(k).startswith("K1_"):continue
   a,b=walk(v);dfs+=a;tr+=b
 return dfs,tr
def conj(arm):
 return {k:{"raw_conjunctions":int(v.get("raw_conjunctions",0)),"distinct_vectors":int(v.get("distinct_vectors",0))} for k,v in arm.get("conjunction_stats",{}).items() if isinstance(v,dict)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=SRC);ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args();s=json.loads(ns.input.read_text());q15=json.loads(QG15B.read_text());q9=json.loads(QG9.read_text())
 rows=[]
 for n in range(2,7):
  c1,c2=count(n,1),count(n,2);rows.append({"n":n,"cap1":c1,"cap2":c2,"pair_count_ratio_cap2_over_cap1":c2["ordered_symplectic_one_pairs"]/c1["ordered_symplectic_one_pairs"]})
 six=q15.get("sixlcu",{});sp=q15.get("stabprep",{});six_c=conj(six);six_raw=sum(v["raw_conjunctions"] for k,v in six_c.items() if k in {"K2","K3"});six_dist=sum(v["distinct_vectors"] for k,v in six_c.items() if k in {"K2","K3"});six_dfs,six_tr=high(six.get("minerr_surface",{}));sp_dfs,sp_tr=walk(sp.get("minerr_surface",sp));sp_c=conj(sp)
 source={"digest":valid(s),"positive":s.get("terminal")==POS,"r6i_rows":s.get("r6i_support_localization",{}).get("rows")==rows,"six_raw":s.get("sixlcu_minimal_predicate",{}).get("higher_order_raw_conjunctions_avoidable_for_minimal_exact_classifier_task")==six_raw,"six_dist":s.get("sixlcu_minimal_predicate",{}).get("higher_order_distinct_vectors_avoidable_for_minimal_exact_classifier_task")==six_dist,"six_dfs":s.get("sixlcu_minimal_predicate",{}).get("higher_order_dfs_nodes_avoidable_for_minimal_exact_classifier_task")==six_dfs,"sp_dfs":s.get("stabprep_information_barrier",{}).get("predicate_search_dfs_nodes_avoidable_for_binary_zero_error_existence_question")==sp_dfs,"sp_conj":s.get("stabprep_information_barrier",{}).get("conjunction_surface")==sp_c,"actions":s.get("required_actions")=={"R6I":"RESTRICT_TO_PROVED_SUPPORT1","SixLCU":"USE_MINIMAL_EXACT_K1D1_PREDICATE","StabPrep":"REJECT_ZERO_ERROR_IN_FROZEN_VOCAB__ESCALATE_REPRESENTATION"},"authority":all(s.get(k) is False for k in ("MAX_R4E_QG_SKILLS_COMPILER_GENERAL","MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE","MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER","REAL_QUANTUM_SUPERIORITY_AUTHORIZED","NOVELTY_AUTHORIZED"))}
 parents={"qg9":q9.get("terminal")=="QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED" and q9.get("support_bound")==1 and q9.get("intrinsic_support_number")==1 and all(q9.get("gates",{}).values()),"six":six.get("cell_table",{}).get("mixed_cells")==0 and q15.get("q3",{}).get("E_floor")==0 and q15.get("q3",{}).get("zero_error_cells",{}).get("minimal_cells")==[[1,1]],"sp":(sp.get("cell_table",{}).get("mixed_cells")==12 or q15.get("q2",{}).get("mixed_cell_count")==12) and q15.get("q2",{}).get("E_floor")==43 and q15.get("q2",{}).get("terminal")=="ZERO_UNACHIEVABLE_ANY_BUDGET"}
 ok=all(source.values()) and all(parents.values());out={"schema":"ORIONQ.MAXR4E.QGSkillReplayGeneric.v1","decision":"ACCEPT_REAL_COMPILER_REPLAY_VALUE" if ok else "REJECT","all_checks":bool(ok),"source_checks":source,"parent_checks":parents,"independent":{"r6i_rows":rows,"six_higher_raw":six_raw,"six_higher_distinct":six_dist,"six_higher_dfs":six_dfs,"six_truncated":six_tr,"stabprep_dfs":sp_dfs,"stabprep_truncated":sp_tr,"stabprep_conjunction_surface":sp_c},"source_result_digest":s.get("result_digest"),"MAX_R4E_QG_SKILLS_REAL_COMPILER_OPERATIONAL_VALUE_REPLAY":bool(ok),"MAX_R4E_QG_SKILLS_COMPILER_GENERAL":False,"MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE":False,"MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER":False,"REAL_QUANTUM_SUPERIORITY_AUTHORIZED":False,"NOVELTY_AUTHORIZED":False};ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"r6i_min_ratio":min(x["pair_count_ratio_cap2_over_cap1"] for x in rows),"r6i_max_ratio":max(x["pair_count_ratio_cap2_over_cap1"] for x in rows),"six_raw":six_raw,"stabprep_dfs":sp_dfs}));return 0
if __name__=="__main__":raise SystemExit(main())
