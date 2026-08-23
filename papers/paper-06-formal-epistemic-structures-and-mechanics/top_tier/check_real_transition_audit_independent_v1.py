#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];CASES=HERE/"p6_real_transition_cases_v1.json";GOLD=HERE/"p6_real_transition_gold_v1.json";PROTOCOL=HERE/"P6_REAL_TRANSITION_AUDIT_PROTOCOL_V1.md"
def classify(c):
    unknown={k for k in ("execution_support","provenance_binding","source_current","evidence_transport_known") if not c[k]}
    invalid={k for k in ("evidence_transport_valid","obligations_clear") if not c[k]}
    deny={k for k in ("generic_permission","commit_authority") if not c[k]}
    if unknown & {"execution_support","provenance_binding","source_current"}: return "CANNOT_CHECK"
    if "generic_permission" in deny:return "DENIED"
    if "evidence_transport_known" in unknown:return "CANNOT_CHECK"
    if invalid:return "REOPEN"
    if "commit_authority" in deny:return "DENIED"
    return "ADMISSIBLE"
def main():
    cases=json.loads(CASES.read_text())["cases"];gold=json.loads(GOLD.read_text())["gold"]
    fams={}; unsafe_lower={}
    for c in cases:
        text=(ROOT/c["source"]).read_text(encoding="utf-8").lower();assert all(t.lower() in text for t in c["required_tokens"]),(c["id"],c["required_tokens"])
        got=classify(c);assert got==gold[c["id"]],(c["id"],got,gold[c["id"]]);fams.setdefault(c["family"],0);fams[c["family"]]+=1
        lower=(c["execution_support"] and c["provenance_binding"] and c["generic_permission"] and c["source_current"])
        if lower and gold[c["id"]]!="ADMISSIBLE":unsafe_lower[c["family"]]=unsafe_lower.get(c["family"],0)+1
    assert set(fams)=={"rocrate-standard","p9-artifact-recovery","p10-native-coverage","p15-provenance-import"};assert all(v==4 for v in fams.values());assert len(unsafe_lower)>=3
    payload={"schema":"P6.RealTransitionAuditIndependent.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"cases_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),"gold_sha256":hashlib.sha256(GOLD.read_bytes()).hexdigest(),"case_count":len(cases),"family_counts":fams,"lower_layer_unsafe_families":unsafe_lower,"source_token_audit":"GREEN","exact_gold_agreement":True,"terminal":"P6_REAL_TRANSITION_AUDIT_SECOND_INDEPENDENT_CHECKER_GREEN"}
    raw=json.dumps(payload,sort_keys=True,separators=(",", ":")).encode();payload["receipt_sha256"]=hashlib.sha256(raw).hexdigest();print(json.dumps(payload,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
