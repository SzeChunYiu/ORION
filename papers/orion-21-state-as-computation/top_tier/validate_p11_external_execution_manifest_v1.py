#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

MODEL_CLASSES=("GPT_CLASS","CLAUDE_OR_GEMINI_CLASS","OPEN_WEIGHT")
ARMS=(
 "COMPILED_QUERY_CONDITIONED_STATE","HYBRID_DENSE_BM25_RERANK","FULL_CONTEXT_NO_RETRIEVAL","REASON_ONLY",
 "STATE_RETRIEVAL_ONLY","FIXED_STATE_REASON_SPLITS","SIMPLE_UNCERTAINTY_ROUTING","CURRENT_ADAPTIVE_ALLOCATOR",
 "LEARNED_JOINT_ALLOCATOR_DEV_ONLY","HINDSIGHT_ORACLE_ANALYSIS_ONLY",
)
BENCHMARKS={
 "LONGMEMEVAL_CLEANED":"98d7416c24c778c2fee6e6f3006e7a073259d48f",
 "LONGMEMEVAL_V2":"f152293e235517d504809563c833d7190b8c713b",
}
RESOURCE_FIELDS=(
 "input_tokens","output_tokens","wall_latency_ms","peak_memory_bytes","embedding_calls","sparse_retrieval_calls",
 "dense_retrieval_calls","reranking_calls","compilation_calls","materialization_calls","preprocessing_time_ms",
 "state_construction_time_ms","explicit_vendor_or_local_cost",
)
FORBIDDEN={"protected_score","gold_answer","test_metric","observed_gain","winner","selected_after_outcomes"}

def req(r:dict[str,Any],k:str)->str:
    v=r.get(k)
    if not isinstance(v,str) or not v: raise ValueError(f"{k} must be nonempty string")
    return v

def validate(p:dict[str,Any])->dict[str,Any]:
    if p.get("schema")!="ORION.A2.P11ExternalExecutionManifest.v1": raise ValueError("wrong schema")
    if p.get("protected_outcomes_accessed") is not False: raise ValueError("manifest must be sealed before protected outcomes")
    bad=FORBIDDEN&set(p)
    if bad: raise ValueError(f"protected result field present: {sorted(bad)}")
    models=p.get("models")
    if not isinstance(models,list) or len(models)<3: raise ValueError("need >=3 exact model identities")
    seen=set(); classes=set()
    for m in models:
        mid=req(m,"identity_id")
        if mid in seen: raise ValueError(f"duplicate model identity: {mid}")
        seen.add(mid)
        cls=m.get("family_class")
        if cls not in MODEL_CLASSES: raise ValueError(f"bad model family class: {cls}")
        classes.add(cls)
        for k in ("exact_model_id","revision_or_release","provider_or_runtime","access_plan_id","decoding_config_sha256","context_limit_receipt_id"): req(m,k)
        if m.get("executable_access_verified") is not True: raise ValueError(f"model access not executable: {mid}")
    if set(MODEL_CLASSES)-classes: raise ValueError(f"missing required model classes: {sorted(set(MODEL_CLASSES)-classes)}")
    arms=p.get("arms")
    if not isinstance(arms,dict) or set(arms)!=set(ARMS): raise ValueError("arm manifest must contain exactly the 10 frozen arms")
    for aid in ARMS:
        a=arms[aid]; req(a,"entrypoint"); req(a,"config_sha256"); req(a,"implementation_revision")
        if aid=="LEARNED_JOINT_ALLOCATOR_DEV_ONLY" and a.get("tuning_data")!="development_only": raise ValueError("learned joint allocator must be development-only")
        if aid=="HINDSIGHT_ORACLE_ANALYSIS_ONLY":
            if a.get("analysis_only") is not True or a.get("candidate_selectable") is not False: raise ValueError("hindsight oracle boundary violated")
        elif a.get("candidate_selectable") is not True: raise ValueError(f"non-oracle arm unexpectedly non-selectable: {aid}")
    benchmarks=p.get("benchmarks")
    if not isinstance(benchmarks,dict) or set(benchmarks)!=set(BENCHMARKS): raise ValueError("both frozen benchmarks required")
    for bid,rev in BENCHMARKS.items():
        b=benchmarks[bid]
        if b.get("dataset_revision")!=rev: raise ValueError(f"wrong frozen revision for {bid}")
        for k in ("development_registry_sha256","primary_registry_sha256","fresh_query_registry_sha256","compilation_receipt_sha256"): req(b,k)
        if b.get("state_compiled_before_fresh_query_registry_reveal") is not True: raise ValueError(f"optionality seal missing for {bid}")
        if b.get("fresh_queries_source_disjoint") is not True: raise ValueError(f"fresh query set not source-disjoint for {bid}")
    if tuple(p.get("resource_vector_fields",()))!=RESOURCE_FIELDS: raise ValueError("resource vector fields differ from frozen harness")
    schedule=p.get("leave_one_benchmark_out_schedule")
    if not isinstance(schedule,list) or {x.get("held_out") for x in schedule}!=set(BENCHMARKS): raise ValueError("leave-one-benchmark-out schedule incomplete")
    for x in schedule:
        if x.get("protected_retuning_allowed") is not False: raise ValueError("held-out schedule permits protected retuning")
        req(x,"training_development_registry_sha256")
    if p.get("arm_order_rule")!="SHA256_DETERMINISTIC_PER_SESSION": raise ValueError("arm order rule not frozen")
    return {"schema":"ORION.A2.P11ExternalExecutionManifestValidation.v1","decision":"GREEN","models":len(models),"model_family_classes":sorted(classes),"arms":len(arms),"benchmarks":sorted(benchmarks),"resource_fields":len(RESOURCE_FIELDS),"optionality_bound":True,"leave_one_benchmark_out_bound":True}

def _h(x:str)->str: return hashlib.sha256(x.encode()).hexdigest()
def fixture()->dict[str,Any]:
    models=[]
    for i,cls in enumerate(MODEL_CLASSES): models.append({"identity_id":f"model-{i}","family_class":cls,"exact_model_id":f"fixture/{cls}","revision_or_release":"r1","provider_or_runtime":"fixture","access_plan_id":"fixture-access","decoding_config_sha256":_h("decode"+cls),"context_limit_receipt_id":"ctx","executable_access_verified":True})
    arms={}
    for aid in ARMS:
        arms[aid]={"entrypoint":f"run::{aid}","config_sha256":_h(aid),"implementation_revision":"fixture-r1","candidate_selectable":aid!="HINDSIGHT_ORACLE_ANALYSIS_ONLY"}
    arms["LEARNED_JOINT_ALLOCATOR_DEV_ONLY"]["tuning_data"]="development_only"
    arms["HINDSIGHT_ORACLE_ANALYSIS_ONLY"].update({"analysis_only":True,"candidate_selectable":False})
    benchmarks={bid:{"dataset_revision":rev,"development_registry_sha256":_h(bid+"dev"),"primary_registry_sha256":_h(bid+"primary"),"fresh_query_registry_sha256":_h(bid+"fresh"),"compilation_receipt_sha256":_h(bid+"compile"),"state_compiled_before_fresh_query_registry_reveal":True,"fresh_queries_source_disjoint":True} for bid,rev in BENCHMARKS.items()}
    schedule=[{"held_out":bid,"training_development_registry_sha256":_h("train-without-"+bid),"protected_retuning_allowed":False} for bid in BENCHMARKS]
    return {"schema":"ORION.A2.P11ExternalExecutionManifest.v1","protected_outcomes_accessed":False,"models":models,"arms":arms,"benchmarks":benchmarks,"resource_vector_fields":list(RESOURCE_FIELDS),"leave_one_benchmark_out_schedule":schedule,"arm_order_rule":"SHA256_DETERMINISTIC_PER_SESSION"}
def self_test()->dict[str,Any]:
    result=validate(fixture())
    bad=fixture(); bad["models"][0]["executable_access_verified"]=False
    try: validate(bad)
    except ValueError as e: assert "not executable" in str(e)
    else: raise AssertionError("inaccessible model mutant accepted")
    bad2=fixture(); bad2["benchmarks"]["LONGMEMEVAL_V2"]["state_compiled_before_fresh_query_registry_reveal"]=False
    try: validate(bad2)
    except ValueError as e: assert "optionality" in str(e)
    else: raise AssertionError("query-leak mutant accepted")
    bad3=fixture(); bad3["arms"].pop("HINDSIGHT_ORACLE_ANALYSIS_ONLY")
    try: validate(bad3)
    except ValueError as e: assert "10 frozen arms" in str(e)
    else: raise AssertionError("missing-arm mutant accepted")
    return {"decision":"GREEN","validated":result}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(validate(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
