#!/usr/bin/env python3
"""Independent P15 provenance interoperability verifier.

Does not import the primary runner. Uses ProvRecord.extra_attributes rather than
per-attribute lookup and a separate explicit failure-set SEI formulation.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any
from prov.model import ProvDocument

HERE=Path(__file__).resolve().parent
FAULTS=HERE/"sei_fault_cases_v1.jsonl"; GOLD=HERE/"sei_fault_gold_v1.json"; REAL=HERE/"p15_real_workflow_receipts_v1.json"; PROTOCOL=HERE/"P15_PROVENANCE_INTEROP_PROTOCOL_V1.md"
NS="https://orion.example/ns#"; RO_CONTEXT="https://w3id.org/ro/crate/1.3/context"
EXEC_FIELDS=("execution_id","occurrence_id","tool_id","input_digest","output_digest","spawn_ok","host_ok","timeout","exit_zero","output_present","output_complete","reaped","finalized_after_reap","cleanup_complete","retry_accounting_valid","invocation_match","input_digest_match","result_digest_match","occurrence_unique","fresh","coverage_complete","replay_match","lane_applicable","lane_agree")
SCI_FIELDS=("scientific_contract_available","scientific_contract_valid","claim_authority_available","claim_authority","scientific_disposition")

def enc(v:Any)->str:
    return "null" if v is None else ("true" if v is True else ("false" if v is False else str(v)))
def dec(v:Any)->Any:
    s=str(v)
    return None if s=="null" else (True if s=="true" else (False if s=="false" else s))

def disposition(e:dict[str,Any], s:dict[str,Any]|None)->str:
    failures=[]
    for key in ("spawn_ok","host_ok","exit_zero","output_present","output_complete","reaped","finalized_after_reap","cleanup_complete","retry_accounting_valid","invocation_match","input_digest_match","result_digest_match","occurrence_unique","fresh","coverage_complete"):
        if not e[key]: failures.append(key)
    if e["timeout"]: failures.append("timeout")
    if failures: return "EXECUTION_INVALID"
    if s is None or not s["scientific_contract_available"]: return "CANNOT_CHECK"
    if not s["scientific_contract_valid"]: return "INVALID_SCIENCE"
    if not s["claim_authority_available"]: return "CANNOT_CHECK"
    return "AUTHORIZED_SCIENCE" if s["claim_authority"] else "VALID_BUT_NOT_AUTHORIZED"

def norm_fault(c):
    e={k:c[k] for k in EXEC_FIELDS if k in c}
    e.update(execution_id=f"fault:{c['id']}",occurrence_id=f"fault:{c['id']}:1",tool_id="p15-sei-fault-fixture",input_digest="sha256:"+hashlib.sha256((c['id']+':input').encode()).hexdigest(),output_digest="sha256:"+hashlib.sha256((c['id']+':output').encode()).hexdigest())
    return e,{k:c[k] for k in SCI_FIELDS if k in c}
def norm_real(c): return {k:c[k] for k in EXEC_FIELDS},{k:c[k] for k in SCI_FIELDS if k in c}

def prov_rt(e):
    d=ProvDocument(); d.add_namespace("orion",NS)
    act=d.activity("orion:execution",None,None,{f"orion:{k}":enc(e[k]) for k in EXEC_FIELDS})
    inp=d.entity("orion:input"); out=d.entity("orion:output"); ag=d.agent("orion:software")
    d.used(act,inp); d.wasGeneratedBy(out,act); d.wasAssociatedWith(act,ag)
    text=d.serialize(format="json"); loaded=ProvDocument.deserialize(content=text,format="json")
    records=[r for r in loaded.get_records() if getattr(r,"identifier",None) is not None and str(r.identifier)=="orion:execution"]
    assert len(records)==1
    attrs={str(k):dec(v) for k,v in records[0].extra_attributes}
    return {k:attrs[f"orion:{k}"] for k in EXEC_FIELDS},text

def ro_rt(e):
    action={"@id":"#execution","@type":"CreateAction","instrument":{"@id":"#software"},"object":{"@id":"input.json"},"result":{"@id":"output.json"}}
    action.update({NS+k:enc(e[k]) for k in EXEC_FIELDS})
    crate={"@context":RO_CONTEXT,"@graph":[{"@id":"./","@type":"Dataset"},{"@id":"#software","@type":"SoftwareApplication"},{"@id":"input.json","@type":"File"},{"@id":"output.json","@type":"File"},action]}
    text=json.dumps(crate,sort_keys=True,separators=(",", ":")); x=json.loads(text)
    a=next(r for r in x["@graph"] if r.get("@type")=="CreateAction")
    assert a["instrument"]["@id"]=="#software" and a["object"]["@id"]=="input.json" and a["result"]["@id"]=="output.json"
    return {k:dec(a[NS+k]) for k in EXEC_FIELDS},text

def main():
    faults=[json.loads(x) for x in FAULTS.read_text().splitlines() if x.strip()]; gold=json.loads(GOLD.read_text()); real=json.loads(REAL.read_text())["receipts"]
    rows=[]
    for c in faults:
        e,s=norm_fault(c); rows.append((c["id"],e,s,gold[c["id"]]))
    for c in real:
        e,s=norm_real(c); rows.append((c["id"],e,s,c["expected_disposition"]))
    for cid,e,s,expected in rows:
        p,pt=prov_rt(e); r,rt=ro_rt(e); assert p==e and r==e
        assert not any(name in pt or name in rt for name in SCI_FIELDS)
        assert disposition(e,s)==disposition(p,s)==disposition(r,s)==expected
        assert disposition(p,None)==("EXECUTION_INVALID" if disposition(e,s)=="EXECUTION_INVALID" else "CANNOT_CHECK")
    payload={"schema":"P15.ProvenanceInteropIndependent.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"case_count":len(rows),"prov_roundtrip_rate":1.0,"rocrate_roundtrip_rate":1.0,"disagreement_count":0,"scientific_field_leakage_count":0,"false_scientific_success_count":0,"terminal":"P15_PROVENANCE_INTEROP_SECOND_INDEPENDENT_CHECKER_GREEN"}
    raw=json.dumps(payload,sort_keys=True,separators=(",", ":")).encode(); payload["receipt_sha256"]=hashlib.sha256(raw).hexdigest(); print(json.dumps(payload,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
