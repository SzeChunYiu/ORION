#!/usr/bin/env python3
import csv,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
LANE=Path(__file__).resolve().parent
ROOT=LANE.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  while b:=f.read(1<<20): h.update(b)
 return h.hexdigest()
def norm(v): return " ".join((v or "").split())
def content_id(t,a): return hashlib.sha256(norm(f"{t} {a}").encode()).hexdigest()
def value_receipt(v):
 b=norm(v).encode()
 return {"normalized_nonempty":bool(b),"normalized_bytes":len(b),"normalized_sha256":hashlib.sha256(b).hexdigest()}
def must(c,m):
 if not c: raise AssertionError(m)
def main():
 protocol=json.loads((LANE/"PROTOCOL_V12.json").read_text())
 contract=json.loads((LANE/"MATCHED_CONTRACT_FREEZE_V12.json").read_text())
 freeze=json.loads((LANE/"PROTOCOL_FREEZE_RECEIPT_V12.json").read_text())
 # Binding happens before any source row is parsed.
 binding=[]
 for x in protocol["predecessors"]:
  p=ROOT/x["path"]; actual=sha(p) if p.exists() else None
  binding.append({"path":x["path"],"expected":x["sha256"],"actual":actual,"passed":actual==x["sha256"]})
 source=(ROOT/protocol["public_source"]["path"]).resolve()
 ssha=sha(source) if source.exists() else None
 sb=source.stat().st_size if source.exists() else None
 source_binding={"path":str(source),"expected_sha256":protocol["public_source"]["expected_sha256"],"actual_sha256":ssha,"expected_bytes":protocol["public_source"]["expected_bytes"],"actual_bytes":sb,"passed":ssha==protocol["public_source"]["expected_sha256"] and sb==protocol["public_source"]["expected_bytes"]}
 bind_ok=all(x["passed"] for x in binding) and source_binding["passed"]
 rows={}
 header=[]
 schema_ok=False
 if bind_ok:
  with source.open(newline="",encoding="utf-8-sig",errors="strict") as f:
   reader=csv.reader(f)
   header=next(reader)
   allowed=["record_id","title","abstract","keywords"]
   schema_ok=all(k in header for k in allowed)
   if schema_ok:
    pos={k:header.index(k) for k in allowed}
    targets=set(protocol["smallest_target"]["record_ids"])
    for raw in reader:
     rid=norm(raw[pos["record_id"]])
     if rid in targets:
      must(rid not in rows,f"duplicate target record id {rid}")
      # Only the four allowlisted fields are selected. Label/outcome columns are never indexed, compared, counted, emitted or retained.
      rows[rid]={"record_id":rid,"title":raw[pos["title"]],"abstract":raw[pos["abstract"]],"keywords":raw[pos["keywords"]]}
 expected_ids=protocol["smallest_target"]["record_ids"]
 row_ids_ok=sorted(rows)==sorted(expected_ids)
 row_receipts={}
 if row_ids_ok:
  for rid in expected_ids:
   row_receipts[rid]={"content_identity":content_id(rows[rid]["title"],rows[rid]["abstract"]),"keyword":value_receipt(rows[rid]["keywords"])}
 expected_cid=protocol["smallest_target"]["expected_shared_content_identity"]
 same_donor_fibre=row_ids_ok and all(row_receipts[r]["content_identity"]==expected_cid for r in expected_ids)
 keyword_hashes=[row_receipts[r]["keyword"]["normalized_sha256"] for r in expected_ids] if row_ids_ok else []
 keyword_nonempty=[row_receipts[r]["keyword"]["normalized_nonempty"] for r in expected_ids] if row_ids_ok else []
 keyword_separates=row_ids_ok and len(set(keyword_hashes))==2 and any(keyword_nonempty)
 passed=bind_ok and schema_ok and row_ids_ok and same_donor_fibre and keyword_separates
 receipt={"schema_version":"orion.p2.state-expanding-acquisition.outcome-blind-gate-receipt.v12","identity":"P2_V12_PROVIDER_NATIVE_KEYWORD_FIBRE_SEPARATOR_GATE_RECEIPT","executed_at_utc":datetime.now(timezone.utc).isoformat(),"execution_number":1,"protocol_sha256":freeze["protocol_sha256"],"matched_contract_sha256":freeze["matched_contract_sha256"],"binding_receipts":binding,"source_binding":source_binding,"schema":{"header_sha256":hashlib.sha256(json.dumps(header,separators=(",",":"),ensure_ascii=False).encode()).hexdigest() if header else None,"allowlisted_fields_present":schema_ok,"value_fields_selected":["record_id","title","abstract","keywords"],"label_or_outcome_headers_may_exist":True,"label_or_outcome_values_interpreted_or_retained":False},"frozen_pair":{"review":protocol["smallest_target"]["review"],"record_ids":expected_ids,"row_ids_bound":row_ids_ok,"expected_shared_content_identity":expected_cid,"row_receipts":row_receipts,"same_exact_u4_donor_fibre":same_donor_fibre,"keyword_hashes_distinct":keyword_separates},"gate":{"id":"G1_PROVIDER_NATIVE_KEYWORD_FIBRE_SEPARATION","passed":passed},"actions":{"network_requests":0,"model_executions":0,"performance_arms":0,"rankings_computed":0,"label_values_interpreted_or_retained":False,"class_counts_computed":False,"performance_outcomes_computed":False,"retries":0},"scope":"OUTCOME_BLIND_SIGNAL_STATE_WITNESS_ONLY","terminal":"P2_V12_PROVIDER_NATIVE_KEYWORD_FIBRE_SEPARATION_PASS" if passed else "P2_V12_PROVIDER_NATIVE_KEYWORD_FIBRE_SEPARATION_FAIL_CLOSED"}
 (LANE/"OUTCOME_BLIND_GATE_RECEIPT_V12.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
 print(receipt["terminal"]); return 0
if __name__=="__main__": raise SystemExit(main())
