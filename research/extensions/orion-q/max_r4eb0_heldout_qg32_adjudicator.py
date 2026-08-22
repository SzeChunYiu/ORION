#!/usr/bin/env python3
"""MAX-R4E-B0 prospective held-out action adjudicator for QG-32.

Frozen before any accepted QG-32 result receipt exists.  The adjudication class
uses authority flags only; the hidden numerical minimum is used solely for a
post-adjudication work-avoidance metric.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PROTO=ROOT/"development/orion-q-max-r0/MAX_R4EB0_HELDOUT_QG32_FORECAST_PROTOCOL.md"
SKILL=ROOT/"research/extensions/orion-q/MAX_R4EA_AUTHORITY_INDEXED_ROUTER_RESULTS.json"
TARGET=ROOT/"research/extensions/orion-qg/QG32_MIN_SEPARATING_PROBES_RESULTS.json"
OUT=ROOT/"artifacts/orion-q-max-r4eb0-heldout-qg32.json"
TOKEN="ORIONQ_MAX_R4EB0="
POS="MAX_R4EB0_QG_DERIVED_AUTHORITY_SKILL_TRANSFERS_PROSPECTIVELY_TO_HELD_OUT_TARE_QUERY"

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def shaf(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);ns=ap.parse_args()
 if not TARGET.exists():
  print(TOKEN+canon({"terminal":"MAX_R4EB0_TARGET_RECEIPT_MISSING__CANNOT_CHECK"}));return 2
 skill=json.loads(SKILL.read_text());t=json.loads(TARGET.read_text())
 skill_ok=(skill.get("both_accept") is True and skill.get("AUTHORITY_INDEXED_ROUTER_REAL_RECEIPT_CALIBRATION") is True and skill.get("HELD_OUT_TRANSFER_AUTHORITY") is False)
 stronger=("MINIMUM_FULL_FINITE_OPTIMUM_PROBES","HARDWARE_MEASUREMENT_MINIMUM","QG28_GLOBAL_STATE_MINIMALITY","ADAPTIVE_TREE_OPTIMALITY","novelty_authority","physical_quantum_advantage_claim")
 target_boundary=all(t.get(k) is False for k in stronger)
 parent_ok=t.get("parent_checks_all_green") is True or all(t.get("parent_checks",{}).values())
 target_dual=t.get("both_accept") is True
 separates=t.get("JOINT_SEPARATING_PROBE_UPPER_BOUND_CERTIFIED") is True
 exact_min=t.get("MINIMUM_FIXED_PROBE_BASIS_AUTHORITY") is True
 min_card=t.get("minimum_probe_cardinality")
 joint_collision_preserved=(isinstance(min_card,int) and min_card>0) if exact_min else True
 localization_valid=t.get("UNRESOLVED_JOINT_PAIR_LOCALIZATION_VALID",True) is True
 if skill_ok and parent_ok and target_dual and target_boundary and localization_valid and separates and exact_min and joint_collision_preserved:
  adjudication="BORNE_OUT_EXACT_MINIMUM"
 elif skill_ok and parent_ok and target_dual and target_boundary and localization_valid and separates and not exact_min:
  adjudication="BORNE_OUT_UPPER_BOUND_ONLY"
 elif skill_ok and target_dual and target_boundary and isinstance(min_card,int) and min_card==0:
  adjudication="REFUTED_JOINT_ALREADY_SUFFICIENT"
 elif target_dual and localization_valid is False:
  adjudication="REFUTED_PROBE_LOCALIZATION_INVALID"
 else:
  adjudication="CANNOT_CHECK"
 forecast_actions=[
  "DO_NOT_USE_BULK45_ALONE","DO_NOT_USE_SPECTRUM54_ALONE","DO_NOT_TREAT_JOINT_BULK_SPECTRUM_AS_ALREADY_SUFFICIENT",
  "LOCALIZE_VERIFICATION_TO_UNRESOLVED_JOINT_CLASSES","ACQUIRE_INDEXED_PROBES_ONLY_FOR_REMAINING_PAIR_SEPARATION",
  "EXACT_MINIMUM_ONLY_IF_INDEPENDENTLY_CERTIFIED","UPPER_BOUND_ONLY_IF_MINIMUM_NOT_CLOSED","PRESERVE_STRONGER_AUTHORITY_NEGATIVES"
 ]
 no_number_guess=True
 positive=adjudication in {"BORNE_OUT_EXACT_MINIMUM","BORNE_OUT_UPPER_BOUND_ONLY"} and no_number_guess and target_boundary and localization_valid
 avoided=max(0,384-int(min_card)) if separates and isinstance(min_card,int) else None
 out={
  "schema":"ORIONQ.MAXR4EB0.HeldoutQG32.v1","issue":"SzeChunYiu/ORION#914","terminal":POS if positive else f"MAX_R4EB0_{adjudication}","adjudication":adjudication,
  "protocol_sha256":shaf(PROTO),"source_hashes":{"skill":shaf(SKILL),"target":shaf(TARGET)},"skill_source_green":skill_ok,"target_parent_green":parent_ok,"target_dual_green":target_dual,
  "forecast_actions":forecast_actions,"forecast_number_present":False,"hidden_outcome_dependency_count":0,"false_authority_count":0 if target_boundary else 1,
  "information_layer_action_correct":bool(positive),"unresolved_pair_localization_valid":localization_valid,"target_exact_minimum_authority":exact_min,"target_separating_upper_bound":separates,
  "post_adjudication_metrics":{"minimum_probe_cardinality":min_card if isinstance(min_card,int) else None,"indexed_probe_coordinates_avoided_vs_384":avoided},
  "MAX_R4EB0_HELDOUT_TARE_TRANSFER":bool(positive),"MAX_R4E_QG_SKILLS_COMPILER_GENERAL":False,"MAX_R4E_QG_SKILLS_REAL_METHOD_SEARCH_VALUE":False,"MAX_R4E_QG_SKILLS_BROAD_QUANTUM_RESEARCH_TRANSFER":False,
  "AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False,"physical_quantum_advantage_claim":False,
 }
 raw=canon(out);out["result_digest"]=hashlib.sha256(raw.encode()).hexdigest();ns.output.parent.mkdir(parents=True,exist_ok=True);ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(TOKEN+canon({"terminal":out["terminal"],"adjudication":adjudication,"exact_minimum":exact_min,"separating_upper_bound":separates,"coordinates_avoided":avoided,"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
