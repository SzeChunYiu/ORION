#!/usr/bin/env python3
"""Deterministically allocate eligible A3 change clusters before predictions/gold."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

STRATA = (
    "representation_schema",
    "responsibility_output_contract",
    "objective_acceptance_criterion",
    "evidence_dependency",
)
FORBIDDEN = {
    "gold", "reuse_gold", "candidate_prediction", "baseline_prediction", "outcome",
    "protected_outcome", "adjudicated_target", "reuse_reopen_target",
}
LINEAGES = ("source_family_id", "normalized_organization_lineage", "artifact_lineage_id")


def nonempty(row: dict[str, Any], key: str) -> str:
    v=row.get(key)
    if not isinstance(v,str) or not v:
        raise ValueError(f"{key} must be nonempty string")
    return v


def key(row: dict[str, Any]) -> str:
    payload="A3-ALLOCATION-V1|" + "|".join(
        [row["stratum"], row["cluster_id"], row["source_family_id"], row["normalized_organization_lineage"], row["artifact_lineage_id"]]
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def validate_pool(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("schema") != "ORION.A3.EligibleChangeClusterPool.v1":
        raise ValueError("wrong eligible-pool schema")
    if payload.get("protected_outcomes_accessed") is not False:
        raise ValueError("pool must precede protected outcomes")
    if payload.get("candidate_predictions_accessed") is not False:
        raise ValueError("pool must precede candidate predictions")
    if payload.get("stratum_adjudication_completed_before_candidate_predictions") is not True:
        raise ValueError("stratum adjudication timing is not frozen before predictions")
    rows=payload.get("clusters")
    if not isinstance(rows,list):
        raise ValueError("clusters must be list")
    seen=set(); out=[]
    for raw in rows:
        if not isinstance(raw,dict):
            raise ValueError("cluster must be object")
        bad=FORBIDDEN & set(raw)
        if bad:
            raise ValueError(f"forbidden gold/prediction fields in eligible pool: {sorted(bad)}")
        cid=nonempty(raw,"cluster_id")
        if cid in seen: raise ValueError(f"duplicate cluster_id: {cid}")
        seen.add(cid)
        if raw.get("eligible") is not True:
            continue
        if raw.get("stratum") not in STRATA:
            raise ValueError(f"bad stratum for {cid}")
        for field in (*LINEAGES,"before_version_id","after_version_id","before_sha256","after_sha256","license_or_rights_receipt_id","curator_assignment_receipt_id"):
            nonempty(raw,field)
        if raw["before_sha256"]==raw["after_sha256"]:
            raise ValueError(f"unchanged bytes cannot be eligible change cluster: {cid}")
        if raw.get("candidate_visible_packet_frozen") is not True:
            raise ValueError(f"candidate visible packet not frozen: {cid}")
        row=dict(raw); row["allocation_key_sha256"]=key(raw); out.append(row)
    return out


def allocate(payload: dict[str, Any]) -> dict[str, Any]:
    rows=validate_pool(payload)
    selected=[]; used={f:set() for f in LINEAGES}
    counts={s:{"primary":0,"replication":0} for s in STRATA}
    shortfalls=[]
    for s in STRATA:
        pool=sorted((r for r in rows if r["stratum"]==s), key=lambda r:(r["allocation_key_sha256"],r["cluster_id"]))
        chosen_ids=set()
        for split,target in (("primary",24),("replication",8)):
            for r in pool:
                if r["cluster_id"] in chosen_ids: continue
                if any(r[f] in used[f] for f in LINEAGES): continue
                rr=dict(r); rr["split"]=split
                selected.append(rr); chosen_ids.add(r["cluster_id"])
                for f in LINEAGES: used[f].add(r[f])
                counts[s][split]+=1
                if counts[s][split]==target: break
            if counts[s][split] != target:
                shortfalls.append({"stratum":s,"split":split,"required":target,"selected":counts[s][split]})
    terminal="A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN" if not shortfalls else "CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
    selected_sorted=sorted(selected,key=lambda r:(STRATA.index(r["stratum"]),0 if r["split"]=="primary" else 1,r["allocation_key_sha256"],r["cluster_id"]))
    digest=hashlib.sha256(json.dumps(selected_sorted,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "schema":"ORION.A3.ChangeClusterPreOutcomeAllocation.v1",
        "terminal":terminal,
        "selected_n":len(selected_sorted),
        "counts":counts,
        "shortfalls":shortfalls,
        "selection_manifest_sha256":digest,
        "clusters":selected_sorted,
        "source_org_artifact_unique_across_all_selected": not shortfalls,
        "candidate_predictions_accessed":False,
        "protected_outcomes_accessed":False,
        "gold_present":False,
        "scientific_authority_delta":"NONE__ALLOCATION_FREEZE_ONLY",
    }


def fixture(per_stratum:int=40) -> dict[str,Any]:
    rows=[]
    for s in STRATA:
        for i in range(per_stratum):
            token=f"{s}-{i}"
            rows.append({
                "cluster_id":token,"eligible":True,"stratum":s,
                "source_family_id":f"sf-{token}","normalized_organization_lineage":f"org-{token}","artifact_lineage_id":f"art-{token}",
                "before_version_id":f"b-{token}","after_version_id":f"a-{token}",
                "before_sha256":f"before-{token}","after_sha256":f"after-{token}",
                "license_or_rights_receipt_id":f"rights-{token}","curator_assignment_receipt_id":f"curator-{token}",
                "candidate_visible_packet_frozen":True,
            })
    return {"schema":"ORION.A3.EligibleChangeClusterPool.v1","protected_outcomes_accessed":False,"candidate_predictions_accessed":False,"stratum_adjudication_completed_before_candidate_predictions":True,"clusters":rows}


def self_test() -> dict[str,Any]:
    good=allocate(fixture())
    assert good["terminal"]=="A3_PREOUTCOME_PRIMARY_REPLICATION_ALLOCATION_FROZEN"
    assert good["selected_n"]==128
    assert all(good["counts"][s]=={"primary":24,"replication":8} for s in STRATA)
    # Determinism under input permutation.
    rev=fixture(); rev["clusters"].reverse()
    assert allocate(rev)["selection_manifest_sha256"]==good["selection_manifest_sha256"]
    # Gold leakage must reject.
    bad=fixture(); bad["clusters"][0]["gold"]="REOPEN"
    try: allocate(bad)
    except ValueError as exc: assert "forbidden" in str(exc)
    else: raise AssertionError("gold-bearing eligible pool accepted")
    # Collapse every organization in one stratum: quota must fail, not rebalance.
    short=fixture()
    for r in short["clusters"]:
        if r["stratum"]==STRATA[0]: r["normalized_organization_lineage"]="same-org"
    out=allocate(short)
    assert out["terminal"]=="CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL"
    assert out["counts"][STRATA[0]]["primary"]<24
    return {"decision":"GREEN","deterministic":True,"gold_mutant_rejected":True,"lineage_shortfall_fails_closed":True,"good_manifest_sha256":good["selection_manifest_sha256"]}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    if args.self_test: result=self_test()
    else:
        if args.input is None: ap.error("input required unless --self-test")
        result=allocate(json.loads(args.input.read_text()))
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(text)
    print(text,end="")
    return 0 if result.get("terminal") != "CANNOT_CHECK_A3_PREOUTCOME_QUOTA_OR_DISJOINTNESS_SHORTFALL" else 2

if __name__=="__main__": raise SystemExit(main())
