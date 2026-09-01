#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any

STRATA=("scientific_software_release_provenance_attestation","workflowhub_rocrate_versioned_workflow","scientific_record_transition")
LINEAGES=("source_family_id","normalized_organization_lineage","artifact_lineage_id")
FORBIDDEN={"gold","scientific_gold","local_authority_gold","candidate_prediction","baseline_prediction","adjudication_outcome","outcome"}

def req(r:dict[str,Any],k:str)->str:
    v=r.get(k)
    if not isinstance(v,str) or not v: raise ValueError(f"{k} must be nonempty string")
    return v

def akey(r:dict[str,Any])->str:
    return hashlib.sha256(("A6-ALLOCATION-V1|"+"|".join([r["stratum"],r["packet_id"],r["source_family_id"],r["normalized_organization_lineage"],r["artifact_lineage_id"]])).encode()).hexdigest()

def validate_pool(p:dict[str,Any])->tuple[list[dict[str,Any]],dict[str,int],int]:
    if p.get("schema")!="ORION.A6.EligibleExternalAuthorityPacketPool.v1": raise ValueError("wrong pool schema")
    if p.get("protected_outcomes_accessed") is not False or p.get("candidate_predictions_accessed") is not False: raise ValueError("pool must precede outcomes/predictions")
    if p.get("replication_n_frozen_before_predictions") is not True or p.get("replication_quota_by_stratum_frozen_before_predictions") is not True: raise ValueError("replication N/stratum quotas not frozen")
    target=p.get("replication_target_n"); quotas=p.get("replication_quota_by_stratum")
    if isinstance(target,bool) or not isinstance(target,int) or target<3: raise ValueError("replication_target_n must be integer >=3")
    if not isinstance(quotas,dict) or set(quotas)!=set(STRATA) or any(isinstance(quotas[s],bool) or not isinstance(quotas[s],int) or quotas[s]<1 for s in STRATA): raise ValueError("invalid replication quota by stratum")
    if sum(quotas.values())!=target: raise ValueError("replication stratum quotas do not sum to target")
    rows=p.get("packets")
    if not isinstance(rows,list): raise ValueError("packets must be list")
    out=[]; seen=set()
    for raw in rows:
        if not isinstance(raw,dict): raise ValueError("packet must be object")
        bad=FORBIDDEN&set(raw)
        if bad: raise ValueError(f"gold/output field present before allocation: {sorted(bad)}")
        pid=req(raw,"packet_id")
        if pid in seen: raise ValueError(f"duplicate packet_id: {pid}")
        seen.add(pid)
        if raw.get("eligible_preterminal") is not True: continue
        if raw.get("stratum") not in STRATA: raise ValueError("bad stratum")
        for k in (*LINEAGES,"before_version_id","after_version_id","before_sha256","after_sha256","license_or_rights_receipt_id","external_custody_receipt_id","adjudicator_assignment_receipt_id","candidate_visible_packet_sha256"):
            req(raw,k)
        if raw["before_sha256"]==raw["after_sha256"]: raise ValueError("transition bytes identical")
        if raw.get("candidate_blind_gold_process_frozen") is not True: raise ValueError("candidate-blind gold process not frozen")
        r=dict(raw); r["allocation_key_sha256"]=akey(r); out.append(r)
    return out,{s:int(quotas[s]) for s in STRATA},target

def allocate(p:dict[str,Any])->dict[str,Any]:
    rows,quotas,target=validate_pool(p); used={k:set() for k in LINEAGES}; selected=[]; counts={s:{"primary":0,"replication":0} for s in STRATA}; short=[]
    for s in STRATA:
        pool=sorted((r for r in rows if r["stratum"]==s),key=lambda r:(r["allocation_key_sha256"],r["packet_id"]))
        for split,n in (("primary",20),("replication",quotas[s])):
            for r in pool:
                if any(x["packet_id"]==r["packet_id"] for x in selected): continue
                if any(r[k] in used[k] for k in LINEAGES): continue
                rr=dict(r); rr["split"]=split; selected.append(rr); counts[s][split]+=1
                for k in LINEAGES: used[k].add(r[k])
                if counts[s][split]==n: break
            if counts[s][split]!=n: short.append({"stratum":s,"split":split,"required":n,"selected":counts[s][split]})
    selected.sort(key=lambda r:(STRATA.index(r["stratum"]),0 if r["split"]=="primary" else 1,r["allocation_key_sha256"],r["packet_id"]))
    dig=hashlib.sha256(json.dumps(selected,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    term="A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN" if not short else "CANNOT_CHECK_A6_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
    return {"schema":"ORION.A6.ExternalAuthorityPreOutcomeAllocation.v1","terminal":term,"primary_n":sum(x["primary"] for x in counts.values()),"replication_n":sum(x["replication"] for x in counts.values()),"replication_target_n":target,"replication_quota_by_stratum":quotas,"counts":counts,"shortfalls":short,"selection_manifest_sha256":dig,"packets":selected,"protected_outcomes_accessed":False,"candidate_predictions_accessed":False,"scientific_authority_delta":"NONE__ALLOCATION_FREEZE_ONLY"}

def fixture(per=30,quotas=None)->dict[str,Any]:
    quotas=quotas or {s:2 for s in STRATA}; rows=[]; n=0
    for s in STRATA:
        for i in range(per):
            pid=f"p{n}"; token=f"{s}-{i}"; n+=1
            rows.append({"packet_id":pid,"eligible_preterminal":True,"stratum":s,"source_family_id":f"sf-{token}","normalized_organization_lineage":f"org-{token}","artifact_lineage_id":f"art-{token}","before_version_id":f"b-{token}","after_version_id":f"a-{token}","before_sha256":f"before-{token}","after_sha256":f"after-{token}","license_or_rights_receipt_id":f"rights-{token}","external_custody_receipt_id":f"custody-{token}","adjudicator_assignment_receipt_id":f"adj-{token}","candidate_visible_packet_sha256":f"visible-{token}","candidate_blind_gold_process_frozen":True})
    return {"schema":"ORION.A6.EligibleExternalAuthorityPacketPool.v1","protected_outcomes_accessed":False,"candidate_predictions_accessed":False,"replication_target_n":sum(quotas.values()),"replication_n_frozen_before_predictions":True,"replication_quota_by_stratum":quotas,"replication_quota_by_stratum_frozen_before_predictions":True,"packets":rows}

def self_test()->dict[str,Any]:
    a=allocate(fixture()); assert a["terminal"]=="A6_EXTERNAL_PRIMARY_REPLICATION_ALLOCATION_FROZEN" and a["primary_n"]==60 and a["replication_n"]==6
    r=fixture(); r["packets"].reverse(); assert allocate(r)["selection_manifest_sha256"]==a["selection_manifest_sha256"]
    bad=fixture(); bad["packets"][0]["scientific_gold"]="ADMIT"
    try: allocate(bad)
    except ValueError as e: assert "gold/output" in str(e)
    else: raise AssertionError("gold mutant accepted")
    mismatch=fixture(); mismatch["replication_target_n"]+=1
    try: allocate(mismatch)
    except ValueError as e: assert "sum" in str(e)
    else: raise AssertionError("quota/target mismatch accepted")
    short=fixture(per=20); o=allocate(short); assert o["terminal"]=="CANNOT_CHECK_A6_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
    return {"decision":"GREEN","deterministic":True,"gold_mutant_rejected":True,"replication_target_mismatch_rejected":True,"shortfall_fails_closed":True}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: result=self_test()
    elif a.input: result=allocate(json.loads(a.input.read_text()))
    else: ap.error("input required unless --self-test")
    print(json.dumps(result,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
