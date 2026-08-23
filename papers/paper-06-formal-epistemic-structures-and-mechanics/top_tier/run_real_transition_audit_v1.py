#!/usr/bin/env python3
from __future__ import annotations
from collections import Counter,defaultdict
import hashlib,json
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CASES=HERE/"p6_real_transition_cases_v1.json";GOLD=HERE/"p6_real_transition_gold_v1.json";PROTOCOL=HERE/"P6_REAL_TRANSITION_AUDIT_PROTOCOL_V1.md"
def audit_source(c):
    p=ROOT/c["source"]
    if not p.is_file(): return False,["MISSING_FILE"]
    text=p.read_text(encoding="utf-8").lower(); miss=[t for t in c["required_tokens"] if t.lower() not in text]
    return not miss,miss
def donor(c:dict[str,Any])->str:
    if not c["execution_support"] or not c["provenance_binding"] or not c["source_current"]: return "CANNOT_CHECK"
    if not c["generic_permission"]: return "DENIED"
    return "ADMISSIBLE"
def ets(c:dict[str,Any])->str:
    if not c["execution_support"] or not c["provenance_binding"] or not c["source_current"]: return "CANNOT_CHECK"
    if not c["generic_permission"]: return "DENIED"
    if not c["evidence_transport_known"]: return "CANNOT_CHECK"
    if not c["evidence_transport_valid"]: return "REOPEN"
    if not c["obligations_clear"]: return "REOPEN"
    if not c["commit_authority"]: return "DENIED"
    return "ADMISSIBLE"
def evaluate(cases,gold,fn):
    rows=[]; fam=defaultdict(lambda:Counter(total=0,correct=0,unsafe=0,unnecessary=0,launder=0))
    for c in cases:
        pred=fn(c); expected=gold[c["id"]]; d=fam[c["family"]];d["total"]+=1;d["correct"]+=int(pred==expected);d["unsafe"]+=int(pred=="ADMISSIBLE" and expected!="ADMISSIBLE");d["unnecessary"]+=int(pred=="REOPEN" and expected=="ADMISSIBLE");d["launder"]+=int(pred=="ADMISSIBLE" and expected=="DENIED")
        rows.append({"id":c["id"],"family":c["family"],"predicted":pred,"gold":expected,"correct":pred==expected})
    return {"accuracy":sum(r["correct"] for r in rows)/len(rows),"unsafe_false_admissible":sum(d["unsafe"] for d in fam.values()),"unnecessary_reopen":sum(d["unnecessary"] for d in fam.values()),"authority_laundering":sum(d["launder"] for d in fam.values()),"family":{k:{"accuracy":v["correct"]/v["total"],"unsafe":v["unsafe"],"unnecessary":v["unnecessary"],"laundering":v["launder"]} for k,v in sorted(fam.items())},"rows":rows}
def main():
    cases=json.loads(CASES.read_text())["cases"];gold=json.loads(GOLD.read_text())["gold"];assert set(gold)=={c["id"] for c in cases}
    for c in cases:
        ok,miss=audit_source(c);assert ok,(c["id"],miss)
    d=evaluate(cases,gold,donor);e=evaluate(cases,gold,ets)
    unsafe_fams=sum(v["unsafe"]>0 for v in d["family"].values()); positive=(e["accuracy"]==1.0 and e["unsafe_false_admissible"]==0 and e["unnecessary_reopen"]==0 and unsafe_fams>=3 and d["unsafe_false_admissible"]>0)
    receipt={"schema":"P6.RealTransitionAuditResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"cases_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),"gold_sha256":hashlib.sha256(GOLD.read_bytes()).hexdigest(),"case_count":len(cases),"source_token_audit":"GREEN","donor":d,"ets":e,"donor_unsafe_family_count":unsafe_fams,"terminal":"P6_REAL_TRANSITION_AUDIT_V1_SUPPORTED" if positive else "P6_REAL_TRANSITION_AUDIT_V1_GATE_NOT_MET"}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode();receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=="__main__":raise SystemExit(main())
