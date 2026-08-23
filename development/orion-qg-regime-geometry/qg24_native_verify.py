#!/usr/bin/env python3
"""Native ORION-Q responsibility gate for QG-24 exact tropical weighted automaton."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-qg-qg24-tropical-wfa.json"
G=ROOT/"artifacts/orion-qg-qg24-generic-verification.json"
PROTO=ROOT/"development/orion-qg-regime-geometry/QG24_TROPICAL_WFA_PROTOCOL_V1.md"
OUT=ROOT/"artifacts/orion-qg-qg24-native-verification.json"
TOKEN="ORIONQG_QG24_NATIVE="
POS="QG24_TARE_UNRESTRICTED_EXACT_OPTIMUM_RECOGNIZED_BY_FINITE_TROPICAL_AUTOMATON_ALL_N"


def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid_digest(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args()
 a=json.loads(x.analyzer.read_text());g=json.loads(x.generic.read_text())
 stronger=("AUTOMATON_MINIMALITY","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","CHAIN_ALL_N","ASYMPTOTIC_PHASE_BOUNDARY","GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY")
 checks={
  "analyzer_positive":a.get("terminal")==POS and a.get("FINITE_STATE_EXACT_COMPILER") is True and a.get("UNRESTRICTED_DP_EQUALITY_ALL_N") is True and valid_digest(a),
  "generic_positive":g.get("decision")=="ACCEPT_FINITE_TROPICAL_EXACT_COMPILER" and g.get("all_checks") is True and g.get("FINITE_STATE_EXACT_COMPILER") is True and g.get("UNRESTRICTED_DP_EQUALITY_ALL_N") is True,
  "digest_bound":g.get("source_result_digest")==a.get("result_digest"),
  "protocol_bound":a.get("protocol_sha256")==hashlib.sha256(PROTO.read_bytes()).hexdigest(),
  "state_contract":a.get("state_contract",{}).get("input_alphabet_size")==4096 and a.get("state_contract",{}).get("global_control_sectors")==64 and a.get("state_contract",{}).get("raw_states_per_sector")==2612736 and a.get("state_contract",{}).get("parity_bits_total")==9,
  "n1_complete":a.get("n1_calibration",{}).get("valid_target_words")==729 and a.get("n1_calibration",{}).get("all_formula_rows_match") is True and a.get("n1_calibration",{}).get("all_minima_match") is True and a.get("n1_calibration",{}).get("production_minimum_vector_sha256")==g.get("generic_n1_calibration",{}).get("minimum_vector_sha256"),
  "parent_existence":all(a.get("parent_checks",{}).get(k) is True for k in ("r6s_all_n_support2","r6s_claim_every_n","m1_exact_A_P_C","t1_nonincreasing_prune","t2_exact_occupancy","t2_tag_bound","open_chain_not_used")),
  "bijection":all(a.get("proof_audit",{}).get(k) is True for k in ("cost_is_qubit_local_plus_constant","pair_anticommutation_is_xor_of_local_symplectic_bits","tag_syndromes_are_xor_of_local_symplectic_bits","nonzero_and_caps_are_counter_determined","accepting_path_to_original_configuration","capped_original_configuration_to_accepting_path","path_configuration_cost_identity","support_capped_optimum_contains_unrestricted_optimum","t4b_chain_closure_not_assumed")),
  "fixed_matching_scope":a.get("proof_audit",{}).get("fixed_matching_only_v1") is True,
  "stronger_false_analyzer":all(a.get(k) is False for k in stronger),
  "stronger_false_generic":all(g.get(k) is False for k in stronger),
  "no_external_authority":all(a.get(k) is False for k in ("novelty_authority","r6_authority","physical_quantum_advantage_claim")) and all(g.get(k) is False for k in ("novelty_authority","r6_authority","physical_quantum_advantage_claim")),
 }
 ok=all(checks.values())
 out={
  "schema":"ORIONQG.QG24.NativeVerification.v1",
  "decision":"ACCEPT_FINITE_TROPICAL_EXACT_COMPILER" if ok else "REJECT",
  "responsibility":"FINITE_STATE_EXACT_COMPILER__UNRESTRICTED_DP_EQUALITY_ALL_N" if ok else "CANNOT_CHECK",
  "all_checks":bool(ok),
  "checks":checks,
  "source_result_digest":a.get("result_digest"),
  "FINITE_STATE_EXACT_COMPILER":bool(ok),
  "UNRESTRICTED_DP_EQUALITY_ALL_N":bool(ok),
  "AUTOMATON_MINIMALITY":False,
  "CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,
  "CHAIN_ALL_N":False,
  "ASYMPTOTIC_PHASE_BOUNDARY":False,
  "GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY":False,
  "novelty_authority":False,
  "r6_authority":False,
  "physical_quantum_advantage_claim":False,
 }
 x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(TOKEN+canon({"decision":out["decision"],"responsibility":out["responsibility"],"finite_state":out["FINITE_STATE_EXACT_COMPILER"],"all_n":out["UNRESTRICTED_DP_EQUALITY_ALL_N"]}))
 return 0

if __name__=="__main__":raise SystemExit(main())
