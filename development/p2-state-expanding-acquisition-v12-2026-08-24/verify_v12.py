#!/usr/bin/env python3
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
LANE=Path(__file__).resolve().parent; ROOT=LANE.parents[1]
TERMINAL="P2_V12_VALIDATION_PASS__ONE_OUTCOME_BLIND_GATE_FAIL_CLOSED__KEYWORD_DIFFERENCE_DIAGNOSTIC_ONLY__NO_PERFORMANCE_RUN"
def load(n): return json.loads((LANE/n).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def must(c,m):
 if not c: raise AssertionError(m)
def verify():
 p=load("PROTOCOL_V12.json"); f=load("PROTOCOL_FREEZE_RECEIPT_V12.json"); i=load("IMPLEMENTATION_FREEZE_V12.json"); c=load("MATCHED_CONTRACT_FREEZE_V12.json"); g=load("OUTCOME_BLIND_GATE_RECEIPT_V12.json"); d=load("POST_GATE_DIAGNOSIS_V12.json"); r=load("RESULT_V12.json")
 must(sha(LANE/"PROTOCOL_V12.json")==f["protocol_sha256"],"protocol freeze")
 must(sha(LANE/"MATCHED_CONTRACT_FREEZE_V12.json")==f["matched_contract_sha256"],"contract freeze")
 must(sha(LANE/"run_outcome_blind_gate_v12.py")==f["runner_sha256"],"runner freeze")
 must(f["outcome_blind_gate_started"] is False and f["successor_keyword_values_accessed"] is False,"freeze before signal values")
 must(all(x["passed"] for x in g["binding_receipts"]) and g["source_binding"]["passed"],"bindings")
 must(g["execution_number"]==1 and g["actions"]["retries"]==0,"one execution no retries")
 must(g["frozen_pair"]["row_ids_bound"] is True,"row ids")
 rr=g["frozen_pair"]["row_receipts"]
 must(rr["1003"]["content_identity"]==rr["1018"]["content_identity"]=="77baa6675fd97c3c630fdd971baddd5250d864260d31cf2ac6632fa2a93943fa","same computed donor text")
 must(g["frozen_pair"]["keyword_hashes_distinct"] is True,"keywords distinct")
 must(g["frozen_pair"]["same_exact_u4_donor_fibre"] is False and g["gate"]["passed"] is False,"gate fail closed")
 must(d["mismatch"]["frozen_v10_content_identity"]=="d1b054eda2f1fb8dea2e3ad78c9d32aba9819f9d2465b6509949ec11f4117bd4","v10 identity")
 must(d["scientific_interpretation"]["signal_admitted"] is False and d["authority"].startswith("POST_GATE_DIAGNOSIS_ONLY"),"no promotion")
 a=g["actions"]
 must(a["model_executions"]==a["performance_arms"]==a["rankings_computed"]==0,"no model/performance")
 must(a["label_values_interpreted_or_retained"] is False and a["class_counts_computed"] is False and a["performance_outcomes_computed"] is False,"outcome blind")
 must(r["gate"]["passed"] is False and r["actions"]["gate_retries"]==0,"result fail/no retry")
 for x in p["predecessors"]:
  q=ROOT/x["path"]; must(q.exists() and sha(q)==x["sha256"],f"predecessor {q}")
 return {"schema_version":"orion.p2.state-expanding-acquisition.validation-receipt.v12","validated_at_utc":datetime.now(timezone.utc).isoformat(),"verifier_path":str(Path(__file__).relative_to(ROOT)),"verifier_sha256":sha(Path(__file__)),"checks_passed":16,"outcome_blind_gate_executions":1,"gate_passed":False,"model_or_performance_runs":0,"label_values_interpreted_or_retained":False,"pytest_or_repository_ci_run":False,"terminal":TERMINAL}
if __name__=="__main__":
 try:
  x=verify()
  if "--write-receipt" in sys.argv: (LANE/"VALIDATION_RECEIPT_V12.json").write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
  print(TERMINAL)
 except Exception as e:
  print(f"P2_V12_VALIDATION_FAIL__{type(e).__name__}__{e}",file=sys.stderr); raise
