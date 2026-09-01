#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tier_a_analysis_common_v1 import bootstrap_mean_interval, mean, require_disjoint  # noqa: E402

INTERVENTIONS=("INFORMATION","ACCESSIBILITY","COMPUTATION","RECONSTRUCTION")
FIXED=("COMPUTE_FIRST","INFORMATION_FIRST","ACCESSIBILITY_FIRST","RESTART_REFORMULATE_FIRST")
METHOD="METHOD/CANNOT_CHECK"

def _nonneg(v:Any,name:str)->float:
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(float(v)) or float(v)<0: raise ValueError(f"{name} must be finite nonnegative")
    return float(v)
def validate_row(r:dict[str,Any])->None:
    required=("task_id","split","domain","source_family_id","gold_cause","leakage_check_passed","candidate_selected_action","strongest_fixed_selected_action","compute_first_selected_action","candidate_final_success","strongest_fixed_final_success","candidate_charged_regret","strongest_fixed_charged_regret")
    missing=[k for k in required if k not in r]
    if missing: raise ValueError(f"missing fields: {missing}")
    if r["split"] not in ("primary","replication"): raise ValueError("bad split")
    for k in ("task_id","domain","source_family_id"):
        if not isinstance(r[k],str) or not r[k]: raise ValueError(f"{k} missing")
    if r["gold_cause"] not in INTERVENTIONS+(METHOD,): raise ValueError("bad causal gold")
    if r["candidate_selected_action"] not in INTERVENTIONS+(METHOD,): raise ValueError("bad candidate action")
    if r["strongest_fixed_selected_action"] not in INTERVENTIONS+(METHOD,): raise ValueError("bad fixed action")
    if r["compute_first_selected_action"]!="COMPUTATION": raise ValueError("compute-first must be executable as COMPUTATION for broad false-compute gate")
    if type(r["candidate_final_success"]) is not bool or type(r["strongest_fixed_final_success"]) is not bool: raise ValueError("final success must be boolean")
    if type(r["leakage_check_passed"]) is not bool: raise ValueError("leakage flag must be boolean")
    r["candidate_charged_regret"]=_nonneg(r["candidate_charged_regret"],"candidate_charged_regret")
    r["strongest_fixed_charged_regret"]=_nonneg(r["strongest_fixed_charged_regret"],"strongest_fixed_charged_regret")
def analyze(p:dict[str,Any],resamples:int=10000)->dict[str,Any]:
    if p.get("schema")!="ORION.A4.HiddenCauseFinalResultInput.v1": raise ValueError("wrong schema")
    if p.get("protected_outcomes_unsealed") is not True: raise ValueError("post-run unseal flag required")
    strongest=p.get("strongest_fixed_policy_id")
    if strongest not in FIXED: raise ValueError("strongest fixed policy id invalid")
    if p.get("strongest_fixed_selected_on_development_before_protected_runs") is not True: raise ValueError("strongest fixed policy was not selected before protected runs")
    if not isinstance(p.get("causal_gold_result_sha256"),str) or not p["causal_gold_result_sha256"]: raise ValueError("causal-gold result binding missing")
    rows=p.get("tasks")
    if not isinstance(rows,list) or not rows: raise ValueError("tasks missing")
    seen=set(); primary=[]; repl=[]
    for r in rows:
        if not isinstance(r,dict): raise ValueError("task must be object")
        validate_row(r)
        if r["task_id"] in seen: raise ValueError(f"duplicate task: {r['task_id']}")
        seen.add(r["task_id"]); (primary if r["split"]=="primary" else repl).append(r)
    require_disjoint((r["source_family_id"] for r in primary),(r["source_family_id"] for r in repl),"source_family_id")
    domains=sorted({r["domain"] for r in primary}); scope_ok=len(domains)>=4 and len(primary)>0 and len(repl)>0
    leakage_ok=all(r["leakage_check_passed"] for r in rows)
    pdiff=[float(r["candidate_final_success"])-float(r["strongest_fixed_final_success"]) for r in primary]
    rdiff=[float(r["candidate_final_success"])-float(r["strongest_fixed_final_success"]) for r in repl]
    gain=mean(pdiff); lo,hi=bootstrap_mean_interval(pdiff,"A4|primary|success-diff",resamples)
    cand_reg=mean(r["candidate_charged_regret"] for r in primary); fixed_reg=mean(r["strongest_fixed_charged_regret"] for r in primary); regret_ok=cand_reg<=0.5*fixed_reg+1e-12
    cand_false=mean(int(r["candidate_selected_action"]=="COMPUTATION" and r["gold_cause"]!="COMPUTATION") for r in primary)
    compute_false=mean(int(r["gold_cause"]!="COMPUTATION") for r in primary)
    false_compute_ok=cand_false<compute_false
    by_domain=defaultdict(list)
    for r,d in zip(primary,pdiff): by_domain[r["domain"]].append(d)
    domain_direction={d:mean(v) for d,v in sorted(by_domain.items())}; required_positive=math.ceil(0.75*len(domains)); positive_domains=sum(v>0 for v in domain_direction.values())
    repl_direction=mean(rdiff)
    if not scope_ok: terminal="CANNOT_CHECK_SCOPE_OR_REGRET"
    elif not leakage_ok: terminal="LEAKAGE_INVALID"
    elif gain<0.05 or lo<=0: terminal="NOT_SUPPORTED_FINAL_SUCCESS"
    elif not regret_ok: terminal="NOT_SUPPORTED_CHARGED_REGRET"
    elif not false_compute_ok: terminal="NOT_SUPPORTED_FALSE_COMPUTE"
    elif positive_domains<required_positive: terminal="HETEROGENEOUS_DOMAIN_FAILURE"
    elif repl_direction<=0: terminal="REPLICATION_DIRECTION_FAILURE"
    else: terminal="SUPPORTED_FROZEN_A4_GATE"
    return {"schema":"ORION.A4.HiddenCauseFinalAnalysisResult.v1","strongest_fixed_policy_id":strongest,"primary_n":len(primary),"replication_n":len(repl),"domains":len(domains),"scope_ok":scope_ok,"leakage_ok":leakage_ok,"mean_final_success_gain":gain,"success_gain_ci95":[lo,hi],"candidate_mean_charged_regret":cand_reg,"strongest_fixed_mean_charged_regret":fixed_reg,"charged_regret_gate_pass":regret_ok,"candidate_false_compute_rate":cand_false,"compute_first_false_compute_rate":compute_false,"false_compute_gate_pass":false_compute_ok,"domain_direction":domain_direction,"positive_domains":positive_domains,"required_positive_domains":required_positive,"replication_success_direction":repl_direction,"terminal":terminal}
def fixture()->dict[str,Any]:
    rows=[]; n=0
    for split,per in (("primary",20),("replication",5)):
        for d in range(4):
            for i in range(per):
                tid=f"{split}-d{d}-{i}-{n}"; gold="INFORMATION" if i%2==0 else "ACCESSIBILITY"; rows.append({"task_id":tid,"split":split,"domain":f"domain-{d}","source_family_id":f"source-{tid}","gold_cause":gold,"leakage_check_passed":True,"candidate_selected_action":gold,"strongest_fixed_selected_action":"RECONSTRUCTION","compute_first_selected_action":"COMPUTATION","candidate_final_success":True,"strongest_fixed_final_success":False,"candidate_charged_regret":0.25,"strongest_fixed_charged_regret":1.0}); n+=1
    return {"schema":"ORION.A4.HiddenCauseFinalResultInput.v1","protected_outcomes_unsealed":True,"strongest_fixed_policy_id":"RESTART_REFORMULATE_FIRST","strongest_fixed_selected_on_development_before_protected_runs":True,"causal_gold_result_sha256":"fixture-gold","tasks":rows}
def self_test()->dict[str,Any]:
    good=analyze(fixture(),128); assert good["terminal"]=="SUPPORTED_FROZEN_A4_GATE"
    bad=fixture(); bad["tasks"][0]["leakage_check_passed"]=False
    fail=analyze(bad,32); assert fail["terminal"]=="LEAKAGE_INVALID"
    bad2=fixture(); bad2["strongest_fixed_selected_on_development_before_protected_runs"]=False
    try: analyze(bad2,16)
    except ValueError as e: assert "before protected" in str(e)
    else: raise AssertionError("post-outcome fixed-baseline selection accepted")
    return {"decision":"GREEN","positive_terminal":good["terminal"],"leakage_terminal":fail["terminal"]}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(analyze(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
