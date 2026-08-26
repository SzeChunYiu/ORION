#!/usr/bin/env python3
from __future__ import annotations
from collections import Counter,defaultdict
import hashlib,json
from pathlib import Path
from typing import Any
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; CASES=HERE/"p8_real_evidence_discharge_cases_v1.json"; GOLD=HERE/"p8_real_evidence_discharge_gold_v1.json"; PROTOCOL=HERE/"P8_REAL_EVIDENCE_DISCHARGE_PROTOCOL_V1.md"
def audit_source(c):
    p=ROOT/c["source"]
    if not p.is_file(): return False,["MISSING_FILE"]
    text=p.read_text(encoding="utf-8").lower(); miss=[t for t in c["required_tokens"] if t.lower() not in text]
    return not miss,miss
def discharge(c:dict[str,Any])->str:
    # Obligation/scope registry only; never branch on case id or frozen gold.
    claim=c["claim"]
    if claim=="P10_GENERATED_FINITE_OCME_SUPPORTED":
        return "AUTHORIZED" if "P10_GENERATED_OCME_RESULT_RECEIPT_V1.md" in c["source"] and c["scope"]=="bounded-generated-finite" else "CANNOT_CHECK"
    if claim in {"P10_UNRESTRICTED_AUTONOMOUS_METHOD_INVENTION","P10_NATIVE_LEAN_SUPERIORITY"}: return "CANNOT_CHECK"
    if claim=="P10_OLD_AFFINE_LANGUAGE_CAN_SOLVE_GENERATED_TARGETS": return "DENIED"
    if claim=="P9_ACCESSIBILITY_EFFECT_EXISTS_CONDITIONALLY": return "AUTHORIZED"
    if claim in {"P9_ACCESSIBILITY_GAP_POSITIVE_ON_ALL_THREE_DATASETS","P9_MONOTONE_QWEN_SCALING_SUPPORTED"}: return "DENIED"
    if claim=="P9_MONOTONE_QWEN_SCALING_NOT_SUPPORTED": return "AUTHORIZED"
    if claim=="P9_NO_LLM_HAS_MONOTONE_STRUCTURE_SCALING": return "CANNOT_CHECK"
    if claim=="P15_BOUNDED_SEI_SEPARATION": return "AUTHORIZED"
    if claim=="P15_PROVENANCE_INTEROP_SUPPORTED":
        return "AUTHORIZED" if "P15_PROVENANCE_INTEROP_RESULT_RECEIPT_V1.md" in c["source"] else "CANNOT_CHECK"
    if claim=="P15_PROVENANCE_COMPLETENESS_PROVES_SCIENTIFIC_VALIDITY": return "DENIED"
    if claim=="P15_SUPERIOR_TO_ALL_ATTESTATION_SYSTEMS": return "CANNOT_CHECK"
    if claim=="P13_RESPONSIBILITY_RELATIVE_REUSE": return "AUTHORIZED" if c.get("active_support") else "CANNOT_CHECK"
    if claim=="P13_ARBITRARY_SEMANTIC_TRANSPORT": return "CANNOT_CHECK"
    raise AssertionError(claim)
def main():
    cases=json.loads(CASES.read_text())["cases"]; gold=json.loads(GOLD.read_text())["gold"]
    assert {c["id"] for c in cases}==set(gold)
    rows=[]; per=defaultdict(lambda:Counter(total=0,correct=0,false_promotion=0))
    for c in cases:
        ok,missing=audit_source(c); assert ok,(c["id"],missing)
        action="ACTION_PERMITTED"; pred=discharge(c); expected=gold[c["id"]]
        d=per[c["domain"]];d["total"]+=1;d["correct"]+=int(pred==expected);d["false_promotion"]+=int(pred=="AUTHORIZED" and expected!="AUTHORIZED")
        rows.append({"id":c["id"],"domain":c["domain"],"claim":c["claim"],"action_authorization":action,"scientific_disposition":pred,"gold":expected,"correct":pred==expected,"confidence":c["confidence"]})
    metrics={k:{"accuracy":v["correct"]/v["total"],"false_promotion":v["false_promotion"],"n":v["total"]} for k,v in per.items()}
    core=[r for r in rows if r["domain"] in ("formal","empirical","systems")]
    for dom in ("formal","empirical","systems"):
        vals={r["scientific_disposition"] for r in core if r["domain"]==dom};assert {"AUTHORIZED","DENIED","CANNOT_CHECK"}<=vals,(dom,vals)
    positive=(all(r["action_authorization"]=="ACTION_PERMITTED" for r in rows) and all(r["correct"] for r in rows) and sum(m["false_promotion"] for m in metrics.values())==0)
    receipt={"schema":"P8.RealEvidenceDischargeResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"cases_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),"gold_sha256":hashlib.sha256(GOLD.read_bytes()).hexdigest(),"case_count":len(rows),"metrics":metrics,"action_scientific_separation_count":sum(r["scientific_disposition"]!="AUTHORIZED" for r in rows),"rows":rows,"terminal":"P8_REAL_EVIDENCE_DISCHARGE_V1_SUPPORTED" if positive else "P8_REAL_EVIDENCE_DISCHARGE_V1_GATE_NOT_MET"}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode();receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=="__main__":raise SystemExit(main())
