#!/usr/bin/env python3
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
LANE=Path(__file__).resolve().parent; ROOT=LANE.parents[1]
TERMINAL="P1_V12_VALIDATION_PASS__ZERO_OF_FOUR_AUTHORITY_ACTS_CLOSED__720_MAPS_UNCHANGED"
def load(n): return json.loads((LANE/n).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def must(c,m):
 if not c: raise AssertionError(m)
def verify():
 p=load("PROTOCOL_V12.json"); f=load("PROTOCOL_FREEZE_RECEIPT_V12.json"); s=load("SOURCE_CAPTURE_RECEIPT_V12.json"); d=load("DELEGATION_FIELD_AUDIT_V12.json"); a=load("RIGHTS_AND_ALGEBRA_AUDIT_V12.json"); n=load("NEXT_DELEGATION_EXECUTION_CONTRACT_V13.json"); r=load("RESULT_V12.json")
 must(sha(LANE/"PROTOCOL_V12.json")==f["protocol_sha256"],"protocol freeze")
 must(f["capture_started"] is False and f["source_outcomes_accessed"] is False,"freeze before capture")
 must(s["capture_count"]==s["frozen_route_count"]==3 and s["exactly_one_get_sequence_per_route"],"three one-shot routes")
 must([x["http_status"] for x in s["sources"]]==[200,404,404],"HTTP statuses")
 must(s["sources"][0]["response_bytes"]==11367 and s["sources"][0]["sha256"]=="23236d2dadd91bf84d0b7ca8ca7d4b53a78008a5721c6f3f843b8a33df38a508","issue bytes")
 must(d["chronology"]["created_before_cutoff"] is True and d["chronology"]["created_before_cutoff_seconds"]==136,"chronology")
 must(d["fields_passed"]==0 and d["fields_required"]==7 and d["formal_delegation_bound"] is False,"zero delegation fields")
 must(a["public_route_results"][0]["http_status"]==a["public_route_results"][1]["http_status"]==404,"raw routes 404")
 must(a["inherited_local_artifact_classification"]["classification"].endswith("NOT_COMPLETED_INSTANCE") and a["inherited_local_artifact_classification"]["completed_target_profiles"]==0,"schema not instance")
 must(r["authority_closure"]["acts_closed"]==0 and r["authority_closure"]["acts_total"]==4,"closure count")
 fc=r["frozen_counts"]; must(fc["map_space"]==117649 and fc["rejected_maps"]==116929 and fc["cannot_check_maps"]==720 and fc["certified_maps"]==0,"map counts")
 must(fc["scientific_action_gold_cells"]==0 and fc["named_custodian_or_delegation_groups"]==0 and fc["sufficient_owner_groups"]==0,"owner/gold counts")
 must(r["map_audit_authorized"] is False and r["actions"]["map_audit_rerun"] is False,"audit withheld")
 must(r["actions"]["same_workspace_authority_promoted"] is False and r["actions"]["external_custody_claimed"] is False,"no authority promotion")
 must(n["authority"].startswith("PROSPECTIVE_UNSIGNED_TEMPLATE_ONLY") and n["current_execution_authorized"] is False,"next contract not authority")
 for x in p["predecessors"]:
  q=ROOT/x["path"]; must(q.exists() and sha(q)==x["sha256"],f"predecessor {q}")
 return {"schema_version":"orion.p1.owner-custody-positive-successor.validation-receipt.v12","validated_at_utc":datetime.now(timezone.utc).isoformat(),"verifier_path":str(Path(__file__).relative_to(ROOT)),"verifier_sha256":sha(Path(__file__)),"checks_passed":16,"route_get_sequences":3,"authority_acts_closed":0,"map_audit_rerun":False,"case_or_outcome_accessed":False,"pytest_or_repository_ci_run":False,"terminal":TERMINAL}
if __name__=="__main__":
 try:
  x=verify()
  if "--write-receipt" in sys.argv: (LANE/"VALIDATION_RECEIPT_V12.json").write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
  print(TERMINAL)
 except Exception as e:
  print(f"P1_V12_VALIDATION_FAIL__{type(e).__name__}__{e}",file=sys.stderr); raise
