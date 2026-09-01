#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PAPERS=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(PAPERS/"publication_closure"))
from tier_a_analysis_common_v1 import bootstrap_mean_interval, mean  # noqa: E402

ARMS=(
 "COMPILED_QUERY_CONDITIONED_STATE","HYBRID_DENSE_BM25_RERANK","FULL_CONTEXT_NO_RETRIEVAL","REASON_ONLY",
 "STATE_RETRIEVAL_ONLY","FIXED_STATE_REASON_SPLITS","SIMPLE_UNCERTAINTY_ROUTING","CURRENT_ADAPTIVE_ALLOCATOR",
 "LEARNED_JOINT_ALLOCATOR_DEV_ONLY","HINDSIGHT_ORACLE_ANALYSIS_ONLY",
)
BENCHMARKS=("LONGMEMEVAL_CLEANED","LONGMEMEVAL_V2")

def _metric(rec:dict[str,Any],arm:str)->tuple[float,float]:
    m=rec["arm_metrics"][arm]
    if not isinstance(m,dict) or set(m)!={"quality","total_charged_cost","cannot_check_reason"}: raise ValueError(f"bad metric shape for {arm}")
    if m["cannot_check_reason"] not in (None,""): raise ValueError(f"CANNOT_CHECK arm in final broad gate: {arm}: {m['cannot_check_reason']}")
    q=m["quality"]; c=m["total_charged_cost"]
    if isinstance(q,bool) or not isinstance(q,(int,float)) or not math.isfinite(float(q)) or not 0<=float(q)<=1: raise ValueError("quality must be finite in 0..1")
    if isinstance(c,bool) or not isinstance(c,(int,float)) or not math.isfinite(float(c)) or float(c)<=0: raise ValueError("total charged cost must be finite >0")
    return float(q),float(c)
def analyze(p:dict[str,Any],resamples:int=10000)->dict[str,Any]:
    if p.get("schema")!="ORION.A2.P11ExternalResultInput.v1": raise ValueError("wrong schema")
    if p.get("protected_outcomes_unsealed") is not True: raise ValueError("explicit post-run unseal required")
    if p.get("candidate_and_baseline_selected_before_protected_scoring") is not True: raise ValueError("candidate/baseline were not frozen before protected scoring")
    candidate=p.get("candidate_arm_id"); baseline=p.get("strongest_baseline_arm_id")
    if candidate not in ARMS or baseline not in ARMS or candidate==baseline: raise ValueError("candidate/baseline ids invalid")
    if candidate=="HINDSIGHT_ORACLE_ANALYSIS_ONLY" or baseline=="HINDSIGHT_ORACLE_ANALYSIS_ONLY": raise ValueError("hindsight oracle cannot enter primary comparison")
    if not isinstance(p.get("execution_manifest_validation_sha256"),str) or not p["execution_manifest_validation_sha256"]: raise ValueError("GREEN execution-manifest validation binding missing")
    rows=p.get("blocks")
    if not isinstance(rows,list) or not rows: raise ValueError("blocks missing")
    seen=set(); benchmarks=Counter(); models=Counter(); diffs=[]; cand_cost=[]; base_cost=[]; by_bench=defaultdict(list); by_cell=defaultdict(list)
    for r in rows:
        if not isinstance(r,dict): raise ValueError("block must be object")
        bid=r.get("block_id"); bench=r.get("benchmark"); model=r.get("model_family_id")
        if not isinstance(bid,str) or not bid or bid in seen: raise ValueError("duplicate/missing block_id")
        seen.add(bid)
        if bench not in BENCHMARKS: raise ValueError("unexpected benchmark")
        if not isinstance(model,str) or not model: raise ValueError("model_family_id missing")
        if not isinstance(r.get("arm_metrics"),dict) or set(r["arm_metrics"])!=set(ARMS): raise ValueError("all 10 frozen arms must be present in every block")
        cq,cc=_metric(r,candidate); bq,bc=_metric(r,baseline)
        diff=cq-bq; diffs.append(diff); cand_cost.append(cc); base_cost.append(bc); benchmarks[bench]+=1; models[model]+=1; by_bench[bench].append((diff,cc,bc)); by_cell[(bench,model)].append((diff,cc,bc))
    scope_ok=set(benchmarks)==set(BENCHMARKS) and len(models)>=3 and all(benchmarks[b]>0 for b in BENCHMARKS)
    avg=mean(diffs); lo,hi=bootstrap_mean_interval(diffs,"A2|P11|quality-diff",resamples)
    ratio=sum(base_cost)/sum(cand_cost)
    quality_route=lo>0
    resource_route=ratio>=2.0 and avg>=-0.02
    benchmark_stats={}
    benchmark_harm_ok=True
    for b in BENCHMARKS:
        vals=by_bench[b]; bd=mean(x[0] for x in vals); br=sum(x[2] for x in vals)/sum(x[1] for x in vals)
        benchmark_stats[b]={"mean_quality_diff":bd,"cost_ratio_baseline_over_candidate":br}; benchmark_harm_ok &= bd>=-0.05-1e-12
    cell_stats={}; stable=True
    for (b,m),vals in sorted(by_cell.items()):
        d=mean(x[0] for x in vals); rr=sum(x[2] for x in vals)/sum(x[1] for x in vals); ok=d>0 or (rr>=2.0 and d>=-0.02)
        cell_stats[f"{b}|{m}"]={"mean_quality_diff":d,"cost_ratio_baseline_over_candidate":rr,"direction_or_resource_noninferiority":ok}; stable &= ok
    if not scope_ok: terminal="CANNOT_CHECK_SCOPE_OR_BINDING"
    elif not (quality_route or resource_route): terminal="NOT_SUPPORTED_PRIMARY_GATE"
    elif not benchmark_harm_ok: terminal="NOT_SUPPORTED_BENCHMARK_HARM"
    elif not stable: terminal="NOT_SUPPORTED_MODEL_BENCHMARK_STABILITY"
    else: terminal="SUPPORTED_FROZEN_P11_EXTERNAL_GATE"
    return {"schema":"ORION.A2.P11ExternalFinalAnalysisResult.v1","candidate_arm_id":candidate,"strongest_baseline_arm_id":baseline,"blocks":len(rows),"benchmarks":dict(benchmarks),"model_families":len(models),"scope_ok":scope_ok,"mean_quality_diff":avg,"quality_diff_ci95":[lo,hi],"total_cost_ratio_baseline_over_candidate":ratio,"quality_route_pass":quality_route,"resource_route_pass":resource_route,"benchmark_stats":benchmark_stats,"benchmark_harm_ok":benchmark_harm_ok,"model_benchmark_cells":cell_stats,"direction_stable":stable,"terminal":terminal}
def fixture()->dict[str,Any]:
    rows=[]
    for b in BENCHMARKS:
        for m in ("gpt","claude","open"):
            for i in range(4):
                metrics={a:{"quality":0.65,"total_charged_cost":3.0,"cannot_check_reason":None} for a in ARMS}
                metrics["COMPILED_QUERY_CONDITIONED_STATE"]={"quality":0.80,"total_charged_cost":1.0,"cannot_check_reason":None}
                rows.append({"block_id":f"{b}-{m}-{i}","benchmark":b,"model_family_id":m,"arm_metrics":metrics})
    return {"schema":"ORION.A2.P11ExternalResultInput.v1","protected_outcomes_unsealed":True,"candidate_and_baseline_selected_before_protected_scoring":True,"candidate_arm_id":"COMPILED_QUERY_CONDITIONED_STATE","strongest_baseline_arm_id":"HYBRID_DENSE_BM25_RERANK","execution_manifest_validation_sha256":"fixture-green","blocks":rows}
def self_test()->dict[str,Any]:
    good=analyze(fixture(),128); assert good["terminal"]=="SUPPORTED_FROZEN_P11_EXTERNAL_GATE"
    bad=fixture(); bad["candidate_and_baseline_selected_before_protected_scoring"]=False
    try: analyze(bad,16)
    except ValueError as e: assert "before protected" in str(e)
    else: raise AssertionError("post-outcome arm selection accepted")
    bad2=fixture(); bad2["blocks"][0]["arm_metrics"].pop("REASON_ONLY")
    try: analyze(bad2,16)
    except ValueError as e: assert "10 frozen arms" in str(e)
    else: raise AssertionError("missing required arm accepted")
    return {"decision":"GREEN","positive_terminal":good["terminal"],"quality_route":good["quality_route_pass"],"resource_route":good["resource_route_pass"]}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(analyze(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
