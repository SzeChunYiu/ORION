#!/usr/bin/env python3
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

LANE=Path(__file__).resolve().parent
ROOT=LANE.parents[1]
FILES=[
 "PROTOCOL_V11.json","PROTOCOL_FREEZE_RECEIPT_V11.json","SOURCE_CAPTURE_RECEIPT_V11.json",
 "OWNER_DELEGATION_AUDIT_V11.json","HISTORICAL_SEMANTIC_COMPONENTS_V11.json",
 "RESULT_V11.json","NEGATIVE_RESULT_LEDGER_V11.md","SCIENTIFIC_REPORT_V11.md","verify_v11.py"
]
TERMINAL="P1_V11_VALIDATION_PASS__HISTORICAL_COMPONENT_POSITIVE__OWNER_CUSTODY_GATES_FAIL_CLOSED__MAP_COUNTS_UNCHANGED"
def load(n): return json.loads((LANE/n).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def must(c,m):
 if not c: raise AssertionError(m)

def verify():
 p=load("PROTOCOL_V11.json"); f=load("PROTOCOL_FREEZE_RECEIPT_V11.json")
 s=load("SOURCE_CAPTURE_RECEIPT_V11.json"); a=load("OWNER_DELEGATION_AUDIT_V11.json")
 c=load("HISTORICAL_SEMANTIC_COMPONENTS_V11.json"); r=load("RESULT_V11.json")
 must(sha(LANE/"PROTOCOL_V11.json")==f["protocol_sha256"],"protocol freeze hash")
 must(f["capture_started"] is False,"protocol frozen before capture")
 must(s["capture_count"]==s["frozen_route_count"]==2,"two frozen captures")
 must(s["exactly_one_get_sequence_per_route"] is True,"one GET sequence per route")
 must(all(x["http_status"]==200 for x in s["sources"]),"all routes HTTP 200")
 must([x["response_bytes"] for x in s["sources"]]==[1591347,24780],"exact source bytes")
 must([x["sha256"] for x in s["sources"]]==["110ff6008091aea1535d6242e2cb5ab1c56b353b932ac30afc4b075133ca86a1","bc8e23ad13d11a47fd849435595bcb1470d901cdd5b0888282b0d69c35aa1dbc"],"exact source hashes")
 must(all(x["historical_date_evaluation"]["strictly_before_cutoff"] for x in s["sources"]),"pre-cutoff chronology")
 must(all(sum(x["exact_r7_target_token_counts"].values())==0 for x in s["sources"]),"zero exact R7 target ids")
 must(c["component_gate_verdict"]=="PASS" and c["historical_standards_action_records"]==1,"positive historical component")
 must(c["crosswalk_to_r7_created"] is False and c["owner_gold_created"] is False,"no relabelling")
 cc=a["candidate_class_counts"]
 must(cc=={"historical_direct_owner_authored_exact_algebra":0,"explicit_formal_delegation":0,"historical_standards_action_record":1,"source_standard_semantic_component_sources":2},"candidate counts")
 must(a["owner_requirement_counts"]=={"groups":12,"structural_analogue_groups":9,"named_custodian_or_delegation_groups":0,"sufficient_groups":0},"owner group counts")
 fc=r["frozen_counts"]
 must(fc["map_space"]==117649 and fc["rejected_maps"]==116929 and fc["cannot_check_maps"]==720 and fc["certified_maps"]==0,"map counts")
 must(fc["scientific_action_gold_cells"]==0,"zero gold")
 must(r["map_audit_authorized"] is False and r["actions"]["map_audit_rerun"] is False,"audit not authorized/rerun")
 must(r["actions"]["manuscript_updated"] is False and r["actions"]["claim_ledger_updated"] is False,"no manuscript/ledger update")
 for pred in p["predecessors"]:
  q=ROOT/pred["path"]
  must(q.exists(),f"predecessor exists: {q}")
  must(sha(q)==pred["sha256"],f"predecessor hash: {q}")
 must(set(FILES).issubset({x.name for x in LANE.iterdir()}),"expected files exist")
 return {"schema_version":"orion.p1.owner-custody-positive-successor.validation-receipt.v11","validated_at_utc":datetime.now(timezone.utc).isoformat(),"verifier_path":str(Path(__file__).relative_to(ROOT)),"verifier_sha256":sha(Path(__file__)),"checks_passed":17,"pytest_or_repository_ci_run":False,"network_accessed_by_verifier":False,"case_or_outcome_accessed":False,"map_audit_rerun":False,"map_audit_authorized":False,"terminal":TERMINAL}
if __name__=="__main__":
 try:
  receipt=verify()
  if "--write-receipt" in sys.argv:
   (LANE/"VALIDATION_RECEIPT_V11.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
  print(TERMINAL)
 except Exception as e:
  print(f"P1_V11_VALIDATION_FAIL__{type(e).__name__}__{e}",file=sys.stderr)
  raise
