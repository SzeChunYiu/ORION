#!/usr/bin/env python3
import csv,hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
LANE=Path(__file__).resolve().parent; ROOT=LANE.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  while b:=f.read(1<<20): h.update(b)
 return h.hexdigest()
def load_module(path,name):
 spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def must(c,m):
 if not c: raise AssertionError(m)
def main():
 p=json.loads((LANE/"PROTOCOL_V13.json").read_text()); f=json.loads((LANE/"PROTOCOL_FREEZE_RECEIPT_V13.json").read_text())
 bindings=[]
 for x in p["predecessors"]:
  q=ROOT/x["path"]; actual=sha(q) if q.exists() else None; bindings.append({"path":x["path"],"expected":x["sha256"],"actual":actual,"passed":actual==x["sha256"]})
 source=(ROOT/p["public_source"]["path"]).resolve(); actual_sha=sha(source) if source.exists() else None; actual_bytes=source.stat().st_size if source.exists() else None
 source_binding={"path":str(source),"expected_sha256":p["public_source"]["expected_sha256"],"actual_sha256":actual_sha,"expected_bytes":p["public_source"]["expected_bytes"],"actual_bytes":actual_bytes,"passed":actual_sha==p["public_source"]["expected_sha256"] and actual_bytes==p["public_source"]["expected_bytes"]}
 bind_ok=all(x["passed"] for x in bindings) and source_binding["passed"]
 v9_path=ROOT/p["exact_imports"]["content_identity_module"]["path"]
 v9=load_module(v9_path,"p2_v13_exact_v9") if bind_ok else None
 rows={}; header=[]; schema_ok=False
 if bind_ok:
  with source.open(newline="",encoding="utf-8-sig",errors="strict") as h:
   r=csv.reader(h); header=next(r); allowed=["record_id","title","abstract","keywords"]; schema_ok=all(k in header for k in allowed); pos={k:header.index(k) for k in allowed} if schema_ok else {}
   if schema_ok:
    targets=set(p["frozen_witness"]["record_ids"])
    for raw in r:
     rid=v9.normalize(raw[pos["record_id"]])
     if rid in targets:
      must(rid not in rows,f"duplicate target id {rid}"); rows[rid]={k:raw[pos[k]] for k in allowed}
 ids=p["frozen_witness"]["record_ids"]; row_ids_ok=sorted(rows)==sorted(ids); receipts={}
 if row_ids_ok:
  for rid in ids:
   raw=rows[rid]
   # Exact population identity is imported and called directly on the provider strings; no V13 recanonicalization.
   cid=v9.content_identity(raw["title"],raw["abstract"])
   title=v9.normalize(raw["title"]); abstract=v9.normalize(raw["abstract"]); model_text=f"{title} {abstract}".strip(); model_sha=hashlib.sha256(model_text.encode()).hexdigest()
   kw=v9.normalize(raw["keywords"]).encode(); receipts[rid]={"imported_v9_content_identity":cid,"exact_u4_model_text_sha256":model_sha,"keyword":{"normalized_bytes":len(kw),"normalized_sha256":hashlib.sha256(kw).hexdigest(),"normalized_nonempty":bool(kw)}}
 w=p["frozen_witness"]; identity_ok=row_ids_ok and all(receipts[r]["imported_v9_content_identity"]==w["expected_v10_content_identity"] for r in ids); text_ok=row_ids_ok and all(receipts[r]["exact_u4_model_text_sha256"]==w["expected_exact_u4_model_text_sha256"] for r in ids); keyword_ok=row_ids_ok and all(receipts[r]["keyword"]["normalized_sha256"]==w["expected_keyword_sha256_by_record"][r] and receipts[r]["keyword"]["normalized_bytes"]==w["expected_keyword_normalized_bytes_by_record"][r] for r in ids) and len({receipts[r]["keyword"]["normalized_sha256"] for r in ids})==2
 passed=bind_ok and schema_ok and row_ids_ok and identity_ok and text_ok and keyword_ok
 receipt={"schema_version":"orion.p2.state-expanding-acquisition.outcome-blind-gate-receipt.v13","identity":"P2_V13_IMPORTED_IDENTITY_SEPARATE_TEXT_KEYWORD_GATE_RECEIPT","executed_at_utc":datetime.now(timezone.utc).isoformat(),"execution_number":1,"protocol_sha256":f["protocol_sha256"],"contract_sha256":f["contract_sha256"],"bindings":bindings,"source_binding":source_binding,"schema":{"header_sha256":hashlib.sha256("\0".join(header).encode()).hexdigest() if header else None,"allowlisted_fields_present":schema_ok,"selected_value_fields":["record_id","title","abstract","keywords"],"label_or_outcome_values_interpreted_or_retained":False},"witness":{"record_ids_bound":row_ids_ok,"row_receipts":receipts,"exact_imported_v10_content_identity_passed":identity_ok,"separate_exact_u4_model_text_tie_passed":text_ok,"provider_keyword_difference_passed":keyword_ok},"gate":{"id":"G1_IMPORTED_IDENTITY_SEPARATE_TEXT_KEYWORD_NONSIMULATION","passed":passed},"actions":{"alternate_pair_search":False,"network_requests":0,"model_runs":0,"rankings":0,"label_values_interpreted_or_retained":False,"class_counts":False,"performance_outcomes":False,"retries":0},"scope":"PUBLIC_DEVELOPMENT_NONSIMULATION_WITNESS_ONLY","terminal":"P2_V13_IMPORTED_V10_IDENTITY_AND_SEPARATE_U4_TEXT_KEYWORD_NONSIMULATION_GATE_PASS" if passed else "P2_V13_IMPORTED_V10_IDENTITY_OR_KEYWORD_NONSIMULATION_GATE_FAIL_CLOSED"}
 (LANE/"OUTCOME_BLIND_GATE_RECEIPT_V13.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n"); print(receipt["terminal"]); return 0
if __name__=="__main__": raise SystemExit(main())
