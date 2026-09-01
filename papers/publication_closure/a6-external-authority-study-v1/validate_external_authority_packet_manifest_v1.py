#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

STRATA=(
 "scientific_software_release_provenance_attestation",
 "workflowhub_rocrate_versioned_workflow",
 "scientific_record_transition",
)
FORBIDDEN={"gold","scientific_gold","local_authority_gold","candidate_prediction","baseline_prediction","adjudication_outcome"}

def req(r:dict[str,Any],k:str)->str:
    v=r.get(k)
    if not isinstance(v,str) or not v: raise ValueError(f"{k} must be nonempty string")
    return v

def validate(p:dict[str,Any])->dict[str,Any]:
    if p.get("schema")!="ORION.A6.ExternalAuthorityPacketIntakeManifest.v1": raise ValueError("wrong schema")
    if p.get("protected_outcomes_accessed") is not False: raise ValueError("intake must precede outcomes")
    target=p.get("replication_target_n")
    if isinstance(target,bool) or not isinstance(target,int) or target<3: raise ValueError("replication_target_n must be frozen integer >=3")
    if p.get("replication_n_frozen_before_predictions") is not True: raise ValueError("replication N not frozen before predictions")
    rows=p.get("packets")
    if not isinstance(rows,list): raise ValueError("packets must be list")
    seen=set(); primary=[]; repl=[]
    for r in rows:
        if not isinstance(r,dict): raise ValueError("packet must be object")
        bad=FORBIDDEN&set(r)
        if bad: raise ValueError(f"gold/output field present at intake: {sorted(bad)}")
        pid=req(r,"packet_id")
        if pid in seen: raise ValueError(f"duplicate packet: {pid}")
        seen.add(pid)
        if r.get("split") not in ("primary","replication"): raise ValueError("bad split")
        if r.get("stratum") not in STRATA: raise ValueError("bad stratum")
        for k in (
            "source_family_id","normalized_organization_lineage","artifact_lineage_id",
            "before_version_id","after_version_id","before_sha256","after_sha256",
            "license_or_rights_receipt_id","external_custody_receipt_id","adjudicator_assignment_receipt_id",
            "candidate_visible_packet_sha256",
        ): req(r,k)
        if r["before_sha256"]==r["after_sha256"]: raise ValueError("transition bytes must differ")
        if r.get("candidate_blind_gold_process_frozen") is not True: raise ValueError("candidate-blind gold process not frozen")
        (primary if r["split"]=="primary" else repl).append(r)
    pc=Counter(r["stratum"] for r in primary); rc=Counter(r["stratum"] for r in repl)
    if len(primary)!=60 or any(pc[s]!=20 for s in STRATA): raise ValueError("primary 20x3 quota mismatch")
    if len(repl)!=target: raise ValueError(f"replication N mismatch: manifest={len(repl)} frozen={target}")
    if any(rc[s]==0 for s in STRATA): raise ValueError("replication must cover all three strata")
    for k in ("source_family_id","normalized_organization_lineage","artifact_lineage_id"):
        overlap=sorted({r[k] for r in primary}&{r[k] for r in repl})
        if overlap: raise ValueError(f"primary/replication {k} overlap: {overlap[:5]}")
    return {"schema":"ORION.A6.ExternalAuthorityPacketIntakeValidation.v1","decision":"GREEN","primary_n":60,"replication_n":target,"primary_counts":{s:pc[s] for s in STRATA},"replication_counts":{s:rc[s] for s in STRATA},"source_disjoint":True,"gold_or_outputs_present":False}

def fixture()->dict[str,Any]:
    rows=[]; n=0
    for split,per in (("primary",20),("replication",2)):
        for s in STRATA:
            for _ in range(per):
                pid=f"{split}-{n}"; rows.append({
                    "packet_id":pid,"split":split,"stratum":s,"source_family_id":f"sf-{pid}","normalized_organization_lineage":f"org-{pid}","artifact_lineage_id":f"art-{pid}",
                    "before_version_id":f"b-{pid}","after_version_id":f"a-{pid}","before_sha256":f"before-{pid}","after_sha256":f"after-{pid}","license_or_rights_receipt_id":f"rights-{pid}",
                    "external_custody_receipt_id":f"custody-{pid}","adjudicator_assignment_receipt_id":f"adj-{pid}","candidate_visible_packet_sha256":f"visible-{pid}","candidate_blind_gold_process_frozen":True,
                }); n+=1
    return {"schema":"ORION.A6.ExternalAuthorityPacketIntakeManifest.v1","protected_outcomes_accessed":False,"replication_target_n":6,"replication_n_frozen_before_predictions":True,"packets":rows}

def self_test()->dict[str,Any]:
    result=validate(fixture())
    bad=fixture(); bad["packets"][0]["scientific_gold"]="ADMIT"
    try: validate(bad)
    except ValueError as e: assert "gold/output" in str(e)
    else: raise AssertionError("gold mutant accepted")
    bad2=fixture(); bad2["replication_target_n"]=7
    try: validate(bad2)
    except ValueError as e: assert "replication N mismatch" in str(e)
    else: raise AssertionError("replication-N mutant accepted")
    return {"decision":"GREEN","validated":result}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(validate(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
