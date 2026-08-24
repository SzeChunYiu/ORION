#!/usr/bin/env python3
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
LANE=Path(__file__).resolve().parent; ROOT=LANE.parents[1]
TERMINAL="P2_V13_VALIDATION_PASS__KEYWORD_NONSIMULATION_GATE_POSITIVE__4_OF_7_SUPPORT_CEILING__NO_PERFORMANCE_RUN"
def load(n): return json.loads((LANE/n).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def must(c,m):
 if not c: raise AssertionError(m)
def verify():
 p=load("PROTOCOL_V13.json"); f=load("PROTOCOL_FREEZE_RECEIPT_V13.json"); c=load("MATCHED_CONTRACT_AND_SUPPORT_FREEZE_V13.json"); g=load("OUTCOME_BLIND_GATE_RECEIPT_V13.json"); s=load("KEYWORD_SUPPORT_CEILING_V13.json"); n=load("NEXT_DISCRIMINATOR_V14.json"); r=load("RESULT_V13.json")
 must(sha(LANE/"PROTOCOL_V13.json")==f["protocol_sha256"],"protocol freeze")
 must(sha(LANE/"MATCHED_CONTRACT_AND_SUPPORT_FREEZE_V13.json")==f["contract_sha256"],"contract freeze")
 must(sha(LANE/"run_outcome_blind_gate_v13.py")==f["runner_sha256"],"runner freeze")
 must(f["gate_started"] is False and f["v13_result_exists"] is False,"frozen before gate")
 must(len(g["bindings"])==8 and all(x["passed"] for x in g["bindings"]) and g["source_binding"]["passed"],"nine bindings")
 must(g["execution_number"]==1 and g["actions"]["retries"]==0 and g["actions"]["alternate_pair_search"] is False,"one gate no search/retry")
 w=g["witness"]; must(w["record_ids_bound"] and w["exact_imported_v10_content_identity_passed"] and w["separate_exact_u4_model_text_tie_passed"] and w["provider_keyword_difference_passed"],"witness conjuncts")
 rr=w["row_receipts"]; must({rr[x]["imported_v9_content_identity"] for x in rr}=={"d1b054eda2f1fb8dea2e3ad78c9d32aba9819f9d2465b6509949ec11f4117bd4"},"v10 identity")
 must({rr[x]["exact_u4_model_text_sha256"] for x in rr}=={"77baa6675fd97c3c630fdd971baddd5250d864260d31cf2ac6632fa2a93943fa"},"u4 tie")
 must(len({rr[x]["keyword"]["normalized_sha256"] for x in rr})==2,"keyword separation")
 must(g["gate"]["passed"] is True,"gate pass")
 must(s["provider_native_keyword_capable_count"]==4 and s["review_count"]==7 and s["unchanged_positive_sign_requirement"]==6 and s["maximum_possible_strictly_positive_reviews_for_keyword_only_change_with_exact_u4_fallback"]==4,"support ceiling")
 must(s["matched_v10_performance_execution_authorized"] is False and r["performance_run_authorized"] is False,"performance withheld")
 a=r["actions"]; must(a["model_runs"]==a["performance_arms"]==a["rankings"]==0 and a["label_values_interpreted_or_retained"] is False and a["performance_outcomes"] is False,"outcome boundary")
 must(r["preserved_v12_failure"]==p["preserved_v12_terminal"],"V12 preserved")
 must(n["minimum_support"]=={"review_units":7,"keyword_capable_units":7,"why_seven":"Seven of seven avoids a structural sign ceiling and preserves the unchanged 6/7 sign gates without threshold relaxation."},"next support")
 for x in p["predecessors"]:
  q=ROOT/x["path"]; must(q.exists() and sha(q)==x["sha256"],f"predecessor {q}")
 return {"schema_version":"orion.p2.state-expanding-acquisition.validation-receipt.v13","validated_at_utc":datetime.now(timezone.utc).isoformat(),"verifier_path":str(Path(__file__).relative_to(ROOT)),"verifier_sha256":sha(Path(__file__)),"checks_passed":17,"outcome_blind_gate_executions":1,"gate_passed":True,"model_or_performance_runs":0,"label_values_interpreted_or_retained":False,"pytest_or_repository_ci_run":False,"terminal":TERMINAL}
if __name__=="__main__":
 try:
  x=verify()
  if "--write-receipt" in sys.argv: (LANE/"VALIDATION_RECEIPT_V13.json").write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
  print(TERMINAL)
 except Exception as e:
  print(f"P2_V13_VALIDATION_FAIL__{type(e).__name__}__{e}",file=sys.stderr); raise
