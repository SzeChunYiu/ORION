#!/usr/bin/env python3
"""Deterministic A5 24+8+16 panel allocation before terminal/comparator outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DOMAINS=("EARTH_ENVIRONMENT","LIFE_BIOMEDICAL","SCIENTIFIC_SOFTWARE","PHYSICAL_ENGINEERING")
MECHANISMS=(
    "M1_ABSTRACT_TO_FULLTEXT","M2_EARLIER_TO_LATER_VERSION","M3_PROTOCOL_TO_RESULTS",
    "M4_ARTICLE_TO_CORRECTION","M5_ARTICLE_TO_DATA_DOCUMENTATION","M6_ARTICLE_TO_CODE_RELEASE",
    "M7_CONFERENCE_ABSTRACT_TO_FULL_PAPER","M8_ARTICLE_TO_LICENSED_SUPPLEMENT",
)
LINEAGES=("source_family_id","normalized_author_lineage","doi_or_artifact_lineage_id","exact_artifact_id","provider_capture_id")
FORBIDDEN={"gold","gold_restricted","gold_resolving","candidate_output","comparator_output","adjudication_outcome","protected_terminal","score","success"}
ROLE_TARGETS=(("primary",24),("replication",8),("screening_reserve",16))


def req(row:dict[str,Any],key:str)->str:
    v=row.get(key)
    if not isinstance(v,str) or not v: raise ValueError(f"{key} must be nonempty string")
    return v


def alloc_key(row:dict[str,Any])->str:
    fields=[row["domain"],row["mechanism"],row["candidate_id"],row["source_family_id"],row["normalized_author_lineage"],row["doi_or_artifact_lineage_id"],row["provider_capture_id"]]
    return hashlib.sha256(("A5-PANEL-ALLOCATION-V1|"+"|".join(fields)).encode()).hexdigest()


def validate_pool(payload:dict[str,Any])->list[dict[str,Any]]:
    if payload.get("schema")!="ORION.A5.PreTerminalEligibleCandidatePool.v1": raise ValueError("wrong candidate-pool schema")
    for flag in ("protected_outcomes_accessed","comparator_outputs_accessed","terminal_gold_accessed"):
        if payload.get(flag) is not False: raise ValueError(f"{flag} must be false")
    if payload.get("external_eligibility_and_mechanism_screen_complete") is not True:
        raise ValueError("external eligibility/mechanism screen must be complete")
    rows=payload.get("candidates")
    if not isinstance(rows,list): raise ValueError("candidates must be list")
    seen=set(); out=[]
    for raw in rows:
        if not isinstance(raw,dict): raise ValueError("candidate must be object")
        bad=FORBIDDEN & set(raw)
        if bad: raise ValueError(f"outcome/gold field present before allocation: {sorted(bad)}")
        cid=req(raw,"candidate_id")
        if cid in seen: raise ValueError(f"duplicate candidate_id: {cid}")
        seen.add(cid)
        if raw.get("eligible_preterminal") is not True: continue
        if raw.get("domain") not in DOMAINS or raw.get("mechanism") not in MECHANISMS: raise ValueError("bad domain/mechanism")
        for k in (*LINEAGES,"restricted_source_sha256","resolving_source_sha256","rights_receipt_id","natural_origin_receipt_id","external_eligibility_receipt_id"):
            req(raw,k)
        if raw["restricted_source_sha256"]==raw["resolving_source_sha256"]: raise ValueError(f"identical pair bytes: {cid}")
        if raw.get("same_exact_target_claim_predeclared") is not True: raise ValueError(f"target-claim wording not frozen: {cid}")
        if raw.get("one_information_coordinate_candidate") is not True: raise ValueError(f"one-coordinate screen failed: {cid}")
        if raw.get("restricted_state_existed_independently") is not True: raise ValueError(f"restricted state not independently pre-existing: {cid}")
        row=dict(raw); row["allocation_key_sha256"]=alloc_key(raw); out.append(row)
    return out


def allocate(payload:dict[str,Any])->dict[str,Any]:
    rows=validate_pool(payload)
    selected=[]; shortfalls=[]; cell_counts={}
    # Preserve disjointness at the scientific-unit level globally, not just per cell.
    used={k:set() for k in LINEAGES}
    for d in DOMAINS:
        for m in MECHANISMS:
            cell=(d,m); pool=sorted((r for r in rows if r["domain"]==d and r["mechanism"]==m),key=lambda r:(r["allocation_key_sha256"],r["candidate_id"]))
            counts={role:0 for role,_ in ROLE_TARGETS}
            cell_selected=[]
            for role,target in ROLE_TARGETS:
                for r in pool:
                    if any(x["candidate_id"]==r["candidate_id"] for x in cell_selected): continue
                    if any(r[k] in used[k] for k in LINEAGES): continue
                    rr=dict(r); rr["panel_role"]=role
                    if role=="screening_reserve": rr["reserve_rank"]=counts[role]+1
                    cell_selected.append(rr); selected.append(rr)
                    for k in LINEAGES: used[k].add(r[k])
                    counts[role]+=1
                    if counts[role]==target: break
                if counts[role]!=target:
                    shortfalls.append({"domain":d,"mechanism":m,"role":role,"required":target,"selected":counts[role]})
            cell_counts[f"{d}|{m}"]=counts
    selected.sort(key=lambda r:(DOMAINS.index(r["domain"]),MECHANISMS.index(r["mechanism"]),{"primary":0,"replication":1,"screening_reserve":2}[r["panel_role"]],r["allocation_key_sha256"],r["candidate_id"]))
    digest=hashlib.sha256(json.dumps(selected,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    terminal="A5_PANEL_24_8_16_ALLOCATION_FROZEN_BEFORE_OUTCOMES" if not shortfalls else "CANNOT_CHECK_A5_PANEL_CELL_QUOTA_OR_DISJOINTNESS_SHORTFALL"
    return {
        "schema":"ORION.A5.PreOutcomePanelAllocation.v1","terminal":terminal,"selected_n":len(selected),"cell_counts":cell_counts,"shortfalls":shortfalls,
        "selection_manifest_sha256":digest,"candidates":selected,"protected_outcomes_accessed":False,"comparator_outputs_accessed":False,"terminal_gold_accessed":False,
        "scientific_authority_delta":"NONE__PANEL_ALLOCATION_FREEZE_ONLY",
    }


def apply_preoutcome_attrition(allocation:dict[str,Any],attrition:dict[str,Any])->dict[str,Any]:
    if allocation.get("schema")!="ORION.A5.PreOutcomePanelAllocation.v1" or allocation.get("terminal")!="A5_PANEL_24_8_16_ALLOCATION_FROZEN_BEFORE_OUTCOMES": raise ValueError("allocation is not a complete frozen 24+8+16 panel")
    if attrition.get("schema")!="ORION.A5.PreOutcomeAttritionManifest.v1": raise ValueError("wrong attrition schema")
    for flag in ("protected_outcomes_accessed","comparator_outputs_accessed","terminal_gold_accessed"):
        if attrition.get(flag) is not False: raise ValueError(f"late attrition/replacement forbidden: {flag}")
    items=attrition.get("vacancies")
    if not isinstance(items,list): raise ValueError("vacancies must be list")
    rows=[dict(r) for r in allocation["candidates"]]
    by_id={r["candidate_id"]:r for r in rows}
    log=[]
    for vac in items:
        if not isinstance(vac,dict): raise ValueError("vacancy must be object")
        cid=req(vac,"vacated_candidate_id"); reason=req(vac,"pre_outcome_attrition_reason_code"); receipt=req(vac,"proof_no_comparator_or_terminal_outcome_accessed")
        old=by_id.get(cid)
        if old is None or old["panel_role"] not in ("primary","replication"): raise ValueError("only frozen primary/replication roles may be vacated")
        if old.get("vacated") is True: raise ValueError("candidate vacated twice")
        reserves=sorted((r for r in rows if r["domain"]==old["domain"] and r["mechanism"]==old["mechanism"] and r["panel_role"]=="screening_reserve" and not r.get("promoted") and not r.get("vacated")),key=lambda r:r["reserve_rank"])
        if not reserves: raise ValueError("reserve exhausted; cell becomes CANNOT_CHECK rather than borrowing")
        replacement=reserves[0]
        old["vacated"]=True; old["vacated_reason_code"]=reason
        replacement["promoted"]=True; replacement["promoted_to_role"]=old["panel_role"]; replacement["replaces_candidate_id"]=cid
        log.append({"vacated_candidate_id":cid,"vacated_role":old["panel_role"],"pre_outcome_attrition_reason_code":reason,"replacement_candidate_id":replacement["candidate_id"],"replacement_reserve_rank":replacement["reserve_rank"],"proof_no_comparator_or_terminal_outcome_accessed":receipt})
    digest=hashlib.sha256(json.dumps(log,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"schema":"ORION.A5.PreOutcomeAttritionApplication.v1","terminal":"A5_PREOUTCOME_RESERVE_REPLACEMENTS_FROZEN","replacement_log":log,"replacement_log_sha256":digest,"protected_outcomes_accessed":False,"comparator_outputs_accessed":False,"terminal_gold_accessed":False}


def fixture(per_cell:int=55)->dict[str,Any]:
    rows=[]
    n=0
    for d in DOMAINS:
        for m in MECHANISMS:
            for i in range(per_cell):
                cid=f"c{n}"; token=f"{d}-{m}-{i}"; n+=1
                rows.append({"candidate_id":cid,"eligible_preterminal":True,"domain":d,"mechanism":m,"source_family_id":f"sf-{token}","normalized_author_lineage":f"au-{token}","doi_or_artifact_lineage_id":f"do-{token}","exact_artifact_id":f"ex-{token}","provider_capture_id":f"pc-{token}","restricted_source_sha256":f"r-{token}","resolving_source_sha256":f"z-{token}","rights_receipt_id":f"rights-{token}","natural_origin_receipt_id":f"origin-{token}","external_eligibility_receipt_id":f"elig-{token}","same_exact_target_claim_predeclared":True,"one_information_coordinate_candidate":True,"restricted_state_existed_independently":True})
    return {"schema":"ORION.A5.PreTerminalEligibleCandidatePool.v1","protected_outcomes_accessed":False,"comparator_outputs_accessed":False,"terminal_gold_accessed":False,"external_eligibility_and_mechanism_screen_complete":True,"candidates":rows}


def self_test()->dict[str,Any]:
    p=fixture(); a=allocate(p)
    assert a["terminal"]=="A5_PANEL_24_8_16_ALLOCATION_FROZEN_BEFORE_OUTCOMES" and a["selected_n"]==1536
    rev=fixture(); rev["candidates"].reverse(); assert allocate(rev)["selection_manifest_sha256"]==a["selection_manifest_sha256"]
    primary=next(r for r in a["candidates"] if r["panel_role"]=="primary")
    at={"schema":"ORION.A5.PreOutcomeAttritionManifest.v1","protected_outcomes_accessed":False,"comparator_outputs_accessed":False,"terminal_gold_accessed":False,"vacancies":[{"vacated_candidate_id":primary["candidate_id"],"pre_outcome_attrition_reason_code":"RIGHTS_WITHDRAWN_BEFORE_OUTCOMES","proof_no_comparator_or_terminal_outcome_accessed":"receipt-1"}]}
    rep=apply_preoutcome_attrition(a,at); assert rep["replacement_log"][0]["replacement_reserve_rank"]==1
    late=dict(at); late["comparator_outputs_accessed"]=True
    try: apply_preoutcome_attrition(a,late)
    except ValueError as exc: assert "late" in str(exc)
    else: raise AssertionError("post-outcome replacement accepted")
    bad=fixture(); bad["candidates"][0]["gold_resolving"]="ResolvedTrue"
    try: allocate(bad)
    except ValueError as exc: assert "outcome/gold" in str(exc)
    else: raise AssertionError("gold-bearing pool accepted")
    short=fixture(47); out=allocate(short); assert out["terminal"]=="CANNOT_CHECK_A5_PANEL_CELL_QUOTA_OR_DISJOINTNESS_SHORTFALL"
    return {"decision":"GREEN","selected_n":a["selected_n"],"deterministic":True,"reserve_replacement_rank1":True,"late_replacement_rejected":True,"gold_mutant_rejected":True,"short_cell_fails_closed":True}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--output",type=Path); a=ap.parse_args()
    result=self_test() if a.self_test else allocate(json.loads(a.input.read_text()) if a.input else (_ for _ in ()).throw(ValueError("input required")))
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"; print(text,end="")
    if a.output:a.output.write_text(text)
    return 0

if __name__=="__main__": raise SystemExit(main())
