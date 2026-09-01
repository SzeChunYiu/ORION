#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DOMAINS = ("EARTH_ENVIRONMENT", "LIFE_BIOMEDICAL", "SCIENTIFIC_SOFTWARE", "PHYSICAL_ENGINEERING")
MECHANISMS = (
    "M1_ABSTRACT_TO_FULLTEXT", "M2_EARLIER_TO_LATER_VERSION", "M3_PROTOCOL_TO_RESULTS",
    "M4_ARTICLE_TO_CORRECTION", "M5_ARTICLE_TO_DATA_DOCUMENTATION", "M6_ARTICLE_TO_CODE_RELEASE",
    "M7_CONFERENCE_ABSTRACT_TO_FULL_PAPER", "M8_ARTICLE_TO_LICENSED_SUPPLEMENT",
)
FORBIDDEN = {"gold", "gold_restricted", "gold_resolving", "candidate_output", "comparator_output", "adjudication_outcome"}


def req(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be nonempty string")
    return value


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "ORION.A5.NaturalisticPanelIntakeManifest.v1": raise ValueError("wrong schema")
    if payload.get("protected_outcomes_accessed") is not False: raise ValueError("manifest must precede outcomes")
    rows = payload.get("clusters")
    if not isinstance(rows, list): raise ValueError("clusters must be list")
    seen=set(); primary=[]; repl=[]
    for row in rows:
        if not isinstance(row, dict): raise ValueError("cluster must be object")
        bad = FORBIDDEN & set(row)
        if bad: raise ValueError(f"gold/output field present at intake: {sorted(bad)}")
        cid=req(row,"cluster_id")
        if cid in seen: raise ValueError(f"duplicate cluster_id: {cid}")
        seen.add(cid)
        if row.get("split") not in ("primary","replication"): raise ValueError("bad split")
        if row.get("domain") not in DOMAINS or row.get("mechanism") not in MECHANISMS: raise ValueError("bad domain/mechanism")
        for key in (
            "source_family_id","normalized_author_lineage","doi_or_artifact_lineage_id",
            "restricted_source_sha256","resolving_source_sha256","rights_receipt_id",
            "natural_origin_receipt_id","target_claim_sha256","external_custody_receipt_id",
        ): req(row,key)
        if row["restricted_source_sha256"] == row["resolving_source_sha256"]: raise ValueError("restricted/resolving bytes identical")
        if row.get("same_exact_target_claim") is not True: raise ValueError("target claim must be identical across pair")
        if row.get("one_information_coordinate_changed") is not True: raise ValueError("pair must change exactly one registered information coordinate")
        if row.get("restricted_state_existed_independently") is not True: raise ValueError("restricted state must pre-exist benchmark construction")
        if row.get("nuisance_probe_manifest_frozen") is not True: raise ValueError("nuisance probe manifest not frozen")
        (primary if row["split"]=="primary" else repl).append(row)
    pc=Counter((r["domain"],r["mechanism"]) for r in primary); rc=Counter((r["domain"],r["mechanism"]) for r in repl)
    if len(primary)!=768 or len(repl)!=256 or any(pc[(d,m)]!=24 or rc[(d,m)]!=8 for d in DOMAINS for m in MECHANISMS):
        raise ValueError("32-cell 24+8 quota mismatch")
    for key in ("source_family_id","normalized_author_lineage","doi_or_artifact_lineage_id"):
        overlap=sorted({r[key] for r in primary}&{r[key] for r in repl})
        if overlap: raise ValueError(f"primary/replication {key} overlap: {overlap[:5]}")
    return {"schema":"ORION.A5.NaturalisticPanelIntakeValidation.v1","decision":"GREEN","primary_n":768,"replication_n":256,"cells":32,"source_disjoint":True,"gold_or_outputs_present":False}


def fixture() -> dict[str, Any]:
    rows=[]; n=0
    for split,per in (("primary",24),("replication",8)):
        for d in DOMAINS:
            for m in MECHANISMS:
                for _ in range(per):
                    cid=f"{split}-{n}"; rows.append({
                        "cluster_id":cid,"split":split,"domain":d,"mechanism":m,
                        "source_family_id":f"sf-{cid}","normalized_author_lineage":f"author-{cid}","doi_or_artifact_lineage_id":f"lineage-{cid}",
                        "restricted_source_sha256":f"r-{cid}","resolving_source_sha256":f"z-{cid}","rights_receipt_id":f"rights-{cid}",
                        "natural_origin_receipt_id":f"origin-{cid}","target_claim_sha256":f"claim-{cid}","external_custody_receipt_id":f"custody-{cid}",
                        "same_exact_target_claim":True,"one_information_coordinate_changed":True,"restricted_state_existed_independently":True,"nuisance_probe_manifest_frozen":True,
                    }); n+=1
    return {"schema":"ORION.A5.NaturalisticPanelIntakeManifest.v1","protected_outcomes_accessed":False,"clusters":rows}


def self_test() -> dict[str, Any]:
    result=validate(fixture())
    bad=fixture(); bad["clusters"][0]["gold_resolving"]="ResolvedTrue"
    try: validate(bad)
    except ValueError as exc: assert "gold/output" in str(exc)
    else: raise AssertionError("gold mutant accepted")
    bad2=fixture(); bad2["clusters"][-1]["normalized_author_lineage"]=bad2["clusters"][0]["normalized_author_lineage"]
    try: validate(bad2)
    except ValueError as exc: assert "overlap" in str(exc)
    else: raise AssertionError("lineage overlap mutant accepted")
    return {"decision":"GREEN","validated":result}


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",type=Path); ap.add_argument("--self-test",action="store_true"); a=ap.parse_args()
    if a.self_test: print(json.dumps(self_test(),indent=2,sort_keys=True)); return 0
    if a.input is None: ap.error("input required unless --self-test")
    print(json.dumps(validate(json.loads(a.input.read_text())),indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
