#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SPLITS=("development","primary","replication")
FORBIDDEN={"answer","answer_key","gold","gold_cause","scorer_output","intervention_outcome","protected_outcome"}

def req(r:dict[str,Any],k:str)->str:
    v=r.get(k)
    if not isinstance(v,str) or not v: raise ValueError(f"{k} must be nonempty string")
    return v

def frozen_split(domain:str,source_family:str)->str:
    h=hashlib.sha256(f"A4-SPLIT-V2|{domain}|{source_family}".encode()).hexdigest()
    b=int(h,16)%10
    return "development" if b<=1 else ("primary" if b<=7 else "replication")

def validate(p:dict[str,Any])->dict[str,Any]:
    if p.get("schema")!="ORION.A4.SciAgentArenaExecutableTaskManifest.v2": raise ValueError("wrong schema")
    if p.get("protected_agent_outcomes_accessed") is not False: raise ValueError("manifest must precede protected runs")
    if p.get("gated_access_condition_accepted") is not True: raise ValueError("exact gated task bytes not authorized/materialized")
    revision=req(p,"dataset_revision")
    rows=p.get("tasks")
    if not isinstance(rows,list): raise ValueError("tasks must be list")
    seen=set(); source_split={}; domains=Counter(); split_domains=defaultdict(set)
    for r in rows:
        if not isinstance(r,dict): raise ValueError("task must be object")
        bad=FORBIDDEN&set(r)
        if bad: raise ValueError(f"protected/gold field present in pre-run manifest: {sorted(bad)}")
        tid=req(r,"task_id")
        if tid in seen: raise ValueError(f"duplicate task_id: {tid}")
        seen.add(tid)
        for k in ("task_path","task_sha256","scientific_domain_id","domain_rubric_id","source_family_id","license_or_rights_receipt_id","scorer_path","scorer_sha256","scorer_provenance","success_threshold_provenance","container_or_environment_sha256","split"): req(r,k)
        if r["split"] not in SPLITS: raise ValueError("bad split")
        expected=frozen_split(r["scientific_domain_id"],r["source_family_id"])
        if r["split"]!=expected: raise ValueError(f"split does not match frozen hash rule for {tid}: expected {expected}")
        if r.get("task_container_preflight_passed") is not True or r.get("scorer_executable_preflight_passed") is not True: raise ValueError("task/scorer executable preflight not passed")
        if r.get("candidate_can_read_scorer_or_answer") is not False: raise ValueError("candidate visibility leak")
        key=(r["scientific_domain_id"],r["source_family_id"])
        prior=source_split.get(key)
        if prior is not None and prior!=r["split"]: raise ValueError("source family crossed splits")
        source_split[key]=r["split"]
        domains[r["scientific_domain_id"]]+=1; split_domains[r["split"]].add(r["scientific_domain_id"])
    eligible=len(rows)
    if eligible<120: raise ValueError(f"eligible executable task universe below 120: {eligible}")
    if len(domains)<4: raise ValueError(f"scientific domain universe below 4: {len(domains)}")
    counted=set(domains)
    for split in SPLITS:
        missing=sorted(counted-split_domains[split])
        if missing: raise ValueError(f"domain-stratified partition missing {split} families for domains: {missing}")
    split_counts=Counter(r["split"] for r in rows)
    return {"schema":"ORION.A4.SciAgentArenaExecutableTaskManifestValidation.v2","decision":"GREEN","dataset_revision":revision,"eligible_tasks":eligible,"scientific_domains":len(domains),"domain_counts":dict(sorted(domains.items())),"split_counts":{s:split_counts[s] for s in SPLITS},"source_family_disjoint_splits":True,"protected_fields_present":False}

def _hex(x:str)->str: return hashlib.sha256(x.encode()).hexdigest()
def _family_for(domain:str,desired:str,index:int)->str:
    j=0
    while True:
        f=f"{domain}-family-{index}-{j}"
        if frozen_split(domain,f)==desired: return f
        j+=1

def fixture()->dict[str,Any]:
    rows=[]
    for d in ("domain-a","domain-b","domain-c","domain-d"):
        plan=(("development",6),("primary",18),("replication",6))
        idx=0
        for split,count in plan:
            for _ in range(count):
                sf=_family_for(d,split,idx); tid=f"{d}-{idx}"; idx+=1
                rows.append({"task_id":tid,"task_path":f"tasks/{tid}","task_sha256":_hex("task|"+tid),"scientific_domain_id":d,"domain_rubric_id":"rubric-v1","source_family_id":sf,"license_or_rights_receipt_id":"cc-by-4.0","scorer_path":f"scorers/{tid}.py","scorer_sha256":_hex("scorer|"+tid),"scorer_provenance":"benchmark-owned fixture","success_threshold_provenance":"frozen benchmark/package fixture","container_or_environment_sha256":_hex("env|"+tid),"task_container_preflight_passed":True,"scorer_executable_preflight_passed":True,"candidate_can_read_scorer_or_answer":False,"split":split})
    return {"schema":"ORION.A4.SciAgentArenaExecutableTaskManifest.v2","protected_agent_outcomes_accessed":False,"gated_access_condition_accepted":True,"dataset_revision":"fixture-rev","tasks":rows}
def self_test()->dict[str,Any]:
    result=validate(fixture()); assert result["eligible_tasks"]==120 and result["scientific_domains"]==4
    bad=fixture(); bad["tasks"][0]["gold_cause"]="COMPUTATION"
    try: validate(bad)
    except ValueError as e: assert "protected/gold" in str(e)
    else: raise AssertionError("gold mutant accepted")
    bad2=fixture(); bad2["tasks"][0]["split"]="primary"
    try: validate(bad2)
    except ValueError as e: assert "frozen hash rule" in str(e)
    else: raise AssertionError("split mutant accepted")
    return {"decision":"GREEN","validated":result}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(validate(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
