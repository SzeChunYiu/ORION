#!/usr/bin/env python3
"""P15 provenance interoperability V1 runner.

Requires `prov` 3.x. Scientific fields are held outside donor provenance records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any

from prov.model import ProvDocument

HERE = Path(__file__).resolve().parent
FAULTS = HERE / "sei_fault_cases_v1.jsonl"
GOLD = HERE / "sei_fault_gold_v1.json"
REAL = HERE / "p15_real_workflow_receipts_v1.json"
PROTOCOL = HERE / "P15_PROVENANCE_INTEROP_PROTOCOL_V1.md"

EXEC_FIELDS = (
    "execution_id", "occurrence_id", "tool_id", "input_digest", "output_digest",
    "spawn_ok", "host_ok", "timeout", "exit_zero", "output_present", "output_complete",
    "reaped", "finalized_after_reap", "cleanup_complete", "retry_accounting_valid",
    "invocation_match", "input_digest_match", "result_digest_match", "occurrence_unique",
    "fresh", "coverage_complete", "replay_match", "lane_applicable", "lane_agree",
)
SCI_FIELDS = (
    "scientific_contract_available", "scientific_contract_valid",
    "claim_authority_available", "claim_authority", "scientific_disposition",
)
NS = "https://orion.example/ns#"
RO_CONTEXT = "https://w3id.org/ro/crate/1.3/context"


def enc(v: Any) -> str:
    if v is None: return "null"
    if v is True: return "true"
    if v is False: return "false"
    return str(v)


def dec(v: Any) -> Any:
    s = str(v)
    if s == "null": return None
    if s == "true": return True
    if s == "false": return False
    return s


def execution_integrity(c: dict[str, Any]) -> bool:
    return all((c["spawn_ok"], c["host_ok"], not c["timeout"], c["exit_zero"],
                c["output_present"], c["output_complete"], c["reaped"],
                c["finalized_after_reap"], c["cleanup_complete"],
                c["retry_accounting_valid"], c["invocation_match"],
                c["input_digest_match"], c["result_digest_match"],
                c["occurrence_unique"], c["fresh"], c["coverage_complete"]))


def sei(exec_facts: dict[str, Any], science: dict[str, Any] | None) -> str:
    if not execution_integrity(exec_facts): return "EXECUTION_INVALID"
    if science is None: return "CANNOT_CHECK"
    if not science["scientific_contract_available"]: return "CANNOT_CHECK"
    if not science["scientific_contract_valid"]: return "INVALID_SCIENCE"
    if not science["claim_authority_available"]: return "CANNOT_CHECK"
    if not science["claim_authority"]: return "VALID_BUT_NOT_AUTHORIZED"
    return "AUTHORIZED_SCIENCE"


def normalize_fault(c: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    x = {k: c[k] for k in c if k not in SCI_FIELDS and k not in ("id", "case_type")}
    x.update({
        "execution_id": f"fault:{c['id']}", "occurrence_id": f"fault:{c['id']}:1",
        "tool_id": "p15-sei-fault-fixture",
        "input_digest": "sha256:" + hashlib.sha256((c["id"]+":input").encode()).hexdigest(),
        "output_digest": "sha256:" + hashlib.sha256((c["id"]+":output").encode()).hexdigest(),
    })
    science = {k: c[k] for k in SCI_FIELDS if k in c}
    return {k: x[k] for k in EXEC_FIELDS}, science


def normalize_real(c: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return ({k: c[k] for k in EXEC_FIELDS}, {k: c[k] for k in SCI_FIELDS if k in c})


def prov_roundtrip(facts: dict[str, Any]) -> tuple[dict[str, Any], int]:
    doc = ProvDocument(); doc.add_namespace("orion", NS)
    attrs = {f"orion:{k}": enc(facts[k]) for k in EXEC_FIELDS}
    inp = doc.entity("orion:input", {"orion:digest": facts["input_digest"]})
    out = doc.entity("orion:output", {"orion:digest": facts["output_digest"]})
    agent = doc.agent("orion:software", {"orion:tool_id": facts["tool_id"]})
    act = doc.activity("orion:execution", None, None, attrs)
    doc.used(act, inp); doc.wasGeneratedBy(out, act); doc.wasAssociatedWith(act, agent)
    payload = doc.serialize(format="json")
    loaded = ProvDocument.deserialize(content=payload, format="json")
    record = loaded.get_record("orion:execution")[0]
    recovered = {}
    for k in EXEC_FIELDS:
        vals = record.get_attribute(f"orion:{k}")
        assert len(vals) == 1, (k, vals)
        recovered[k] = dec(next(iter(vals)))
    return recovered, len(payload.encode())


def rocrate_roundtrip(facts: dict[str, Any]) -> tuple[dict[str, Any], int, dict[str, Any]]:
    action = {
        "@id": "#execution", "@type": "CreateAction",
        "instrument": {"@id": "#software"}, "object": {"@id": "input.json"},
        "result": {"@id": "output.json"},
    }
    for k in EXEC_FIELDS:
        action[NS + k] = enc(facts[k])
    crate = {
        "@context": RO_CONTEXT,
        "@graph": [
            {"@id": "ro-crate-metadata.json", "@type": "CreativeWork", "about": {"@id": "./"}},
            {"@id": "./", "@type": "Dataset", "mentions": {"@id": "#execution"}},
            {"@id": "input.json", "@type": "File", "sha256": facts["input_digest"]},
            {"@id": "output.json", "@type": "File", "sha256": facts["output_digest"]},
            {"@id": "#software", "@type": "SoftwareApplication", "name": facts["tool_id"]},
            action,
        ]
    }
    payload = json.dumps(crate, sort_keys=True, separators=(",", ":"))
    loaded = json.loads(payload)
    assert loaded["@context"] == RO_CONTEXT
    actions = [r for r in loaded["@graph"] if r.get("@type") == "CreateAction"]
    assert len(actions) == 1
    a = actions[0]
    assert a["instrument"]["@id"] == "#software" and a["object"]["@id"] == "input.json" and a["result"]["@id"] == "output.json"
    recovered = {k: dec(a[NS+k]) for k in EXEC_FIELDS}
    return recovered, len(payload.encode()), loaded


def main() -> int:
    faults = [json.loads(x) for x in FAULTS.read_text().splitlines() if x.strip()]
    gold = json.loads(GOLD.read_text())
    real = json.loads(REAL.read_text())["receipts"]
    cases = []
    for c in faults:
        e,s = normalize_fault(c); cases.append(("fault", c["id"], e, s, gold[c["id"]]))
    for c in real:
        e,s = normalize_real(c); cases.append(("real", c["id"], e, s, c["expected_disposition"]))

    rows=[]; prov_bytes=[]; ro_bytes=[]
    t0=time.perf_counter()
    for group,cid,e,s,expected in cases:
        native=sei(e,s)
        pr,pb=prov_roundtrip(e)
        rr,rb,crate=rocrate_roundtrip(e)
        prov_bytes.append(pb); ro_bytes.append(rb)
        assert pr == e, (cid,"prov",pr,e)
        assert rr == e, (cid,"rocrate",rr,e)
        prov_text=json.dumps({k:enc(v) for k,v in pr.items()},sort_keys=True)
        ro_text=json.dumps(crate,sort_keys=True)
        leakage=sum(name in prov_text or name in ro_text for name in SCI_FIELDS)
        pdisp=sei(pr,s); rdisp=sei(rr,s); donor_only=sei(pr,None)
        rows.append({"group":group,"id":cid,"expected":expected,"native":native,"prov":pdisp,"rocrate":rdisp,"provenance_only":donor_only,"leakage":leakage})
    elapsed=time.perf_counter()-t0
    print(f"P15 interop informational wall_seconds={elapsed:.6f}", file=sys.stderr)

    assert all(r["native"]==r["expected"] for r in rows), rows
    disagreements=sum(not (r["native"]==r["prov"]==r["rocrate"]) for r in rows)
    leakage=sum(r["leakage"] for r in rows)
    false_success=sum(r["provenance_only"]=="AUTHORIZED_SCIENCE" for r in rows)
    real_rows=[r for r in rows if r["group"]=="real"]
    false_reject=sum(r["expected"]=="AUTHORIZED_SCIENCE" and r["prov"]!="AUTHORIZED_SCIENCE" for r in real_rows)
    false_promote=sum(r["expected"]!="AUTHORIZED_SCIENCE" and r["prov"]=="AUTHORIZED_SCIENCE" for r in real_rows)
    byid={r["id"]:r for r in rows}
    assert byid["SEI-COMPLETE-INVALID-SCIENCE"]["prov"]=="INVALID_SCIENCE"
    assert byid["SEI-DUAL-AGREE-WRONG"]["prov"]=="INVALID_SCIENCE"
    positive=(disagreements==0 and leakage==0 and false_success==0 and false_reject==0 and false_promote==0)
    receipt={
        "schema":"P15.ProvenanceInteropResult.v1",
        "protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "real_fixture_sha256":hashlib.sha256(REAL.read_bytes()).hexdigest(),
        "case_count":len(rows),"fault_case_count":len(faults),"real_receipt_count":len(real),
        "prov_roundtrip_rate":1.0,"rocrate_roundtrip_rate":1.0,
        "scientific_field_leakage_count":leakage,"native_import_disagreement_count":disagreements,
        "provenance_only_false_scientific_success_count":false_success,
        "real_false_rejection_count":false_reject,"real_false_promotion_count":false_promote,
        "mean_prov_json_bytes":sum(prov_bytes)/len(prov_bytes),
        "mean_rocrate_jsonld_bytes":sum(ro_bytes)/len(ro_bytes),
        "rows":rows,
        "terminal":"P15_PROVENANCE_INTEROP_V1_SUPPORTED" if positive else "P15_PROVENANCE_INTEROP_V1_GATE_NOT_MET",
    }
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode(); receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt,indent=2,sort_keys=True)); assert positive, receipt
    return 0

if __name__=="__main__": raise SystemExit(main())
