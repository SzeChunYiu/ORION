#!/usr/bin/env python3
"""MAX-R4E-B1 prospective different-family adjudicator for QG-33 SixLCU.

Frozen before any accepted QG-33 result receipt exists.  It adjudicates only
authority/action class, never a predicted gap histogram or witness.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[3]
PROTO=ROOT/"development/orion-q-max-r0/MAX_R4EB1_SIXLCU_LABEL_VALUE_FORECAST_PROTOCOL.md"
SKILL=ROOT/"research/extensions/orion-q/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_RESULTS.json"
PRIOR=ROOT/"research/extensions/orion-q/MAX_R4EB0_HELDOUT_QG32_RESULTS.json"
TARGET=ROOT/"research/extensions/orion-qg/QG33_SIXLCU_LABEL_VALUE_RESULTS.json"
OUT=ROOT/"artifacts/orion-q-max-r4eb1-sixlcu-label-value.json";TOKEN="ORIONQ_MAX_R4EB1="
POS="MAX_R4EB1_QG_DERIVED_AUTHORITY_SKILL_TRANSFERS_PROSPECTIVELY_TO_DIFFERENT_COMPILER_FAMILY"
def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args()
 if not TARGET.exists():
  print(TOKEN+canon({"terminal":"MAX_R4EB1_TARGET_RECEIPT_MISSING__CANNOT_CHECK"}));return 2
 skill=json.loads(SKILL.read_text());prior=json.loads(PRIOR.read_text());t=json.loads(TARGET.read_text())
 skill_ok=skill.get("both_accept") is True and skill.get("AUTHORITY_INDEXED_ROUTER_REAL_RECEIPT_CALIBRATION") is True and skill.get("HELD_OUT_TRANSFER_AUTHORITY") is False
 prior_ok=prior.get("both_accept") is True and prior.get("MAX_R4EB0_HELDOUT_TARE_TRANSFER") is True
 target_green=t.get("both_accept") is True
 complete_n2=t.get("COMPLETE_N2_DOMAIN") is True
 no_feature_invention=t.get("NO_POST_OUTCOME_FEATURE_INVENTION") is True
 stronger=("ALL_N_VALUE_THEOREM","GLOBAL_PREDICATE_MINIMALITY","NEW_FEATURE_VOCABULARY_AUTHORITY","novelty_authority","physical_quantum_advantage_claim")
 boundary=all(t.get(k) is False for k in stronger)
 label=t.get("LABEL_QUOTIENT_VALUE_SUFFICIENT")
 full=t.get("FULL_FEATURE_VECTOR_VALUE_SUFFICIENT")
 if skill_ok and prior_ok and target_green and complete_n2 and no_feature_invention and boundary and label is False:
  adjudication="BORNE_OUT_LABEL_VALUE_SEPARATION"
 elif skill_ok and prior_ok and target_green and complete_n2 and no_feature_invention and boundary and label is True:
  adjudication="BORNE_OUT_LABEL_VALUE_SUFFICIENCY"
 else:
  adjudication="CANNOT_CHECK"
 secondary="FULL_FEATURE_VALUE_SUFFICIENT" if full is True else ("FULL_FEATURE_VALUE_INSUFFICIENT_AND_ESCALATION_REQUIRED" if full is False else "FULL_FEATURE_STATUS_UNKNOWN")
 positive=adjudication.startswith("BORNE_OUT_")
 actions=["USE_ONE_LITERAL_FOR_DONOR_OPTIMAL_LABEL_ONLY","DO_NOT_AUTHORIZE_EXACT_DELTA_FROM_LABEL_AUTHORITY_ALONE","RUN_EXACT_VALUE_FIBER_TEST_BEFORE_REUSING_LABEL_QUOTIENT_FOR_VALUE","ESCALATE_FROM_LABEL_STATE_FOR_VALUE_QUERY_IF_MIXED","BOUND_VALUE_AUTHORITY_TO_FROZEN_N2_IF_SUFFICIENT","TEST_FULL_FROZEN_FEATURE_VECTOR_SEPARATELY_FOR_VALUE_SUFFICIENCY","ESCALATE_BEYOND_FROZEN_FEATURE_VOCABULARY_IF_MIXED","PRESERVE_STRONGER_AUTHORITY_NEGATIVES"]
 out={"schema":"ORIONQ.MAXR4EB1.SixLCULabelValueHeldout.v1","issue":"SzeChunYiu/ORION#921","terminal":POS if positive else f"MAX_R4EB1_{adjudication}","adjudication":adjudication,"secondary_full_feature_adjudication":secondary,"protocol_sha256":shaf(PROTO),"source_hashes":{"skill":shaf(SKILL),"prior_same_domain":shaf(PRIOR),"target":shaf(TARGET)},"skill_source_green":skill_ok,"prior_same_domain_green":prior_ok,"target_green":target_green,"target_complete_n2":complete_n2,"target_label_value_sufficient":label,"target_full_feature_value_sufficient":full,"forecast_actions":actions,"forecast_number_present":False,"forecast_outcome_guess_present":False,"hidden_outcome_dependency_count":0,"false_authority_count":0 if boundary else 1,"post_outcome_feature_invention":not no_feature_invention,"information_layer_action_correct":bool(positive),"MAX_R4E_QG_SKILLS_COMPILER_GENERAL":bool(positive),"MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE":False,"MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER":False,"AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False,"physical_quantum_advantage_claim":False}
 raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"terminal":out["terminal"],"adjudication":adjudication,"secondary":secondary,"compiler_general":out["MAX_R4E_QG_SKILLS_COMPILER_GENERAL"],"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
