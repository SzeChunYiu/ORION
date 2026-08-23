#!/usr/bin/env python3
"""Native ORION-Q responsibility gate for QG-27 bulk-defect / thermodynamic-limit theorem."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-qg-qg27-bulk-defect.json";G=ROOT/"artifacts/orion-qg-qg27-generic-verification.json";PROTO=ROOT/"development/orion-qg-regime-geometry/QG27_BULK_DEFECT_PROTOCOL_V1.md";OUT=ROOT/"artifacts/orion-qg-qg27-native-verification.json";TOKEN="ORIONQG_QG27_NATIVE=";POS="QG27_TARE_BULK_DEFECT_LAW_AND_EXACT_ASYMPTOTIC_COST_DENSITY_ALL_N_MACHINE_CHECKED"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();a=json.loads(x.analyzer.read_text());g=json.loads(x.generic.read_text())
 stronger=("DEFECT_CONSTANTS_SHARP","FINITE_N_GLOBAL_PHASE_BOUNDARY","PHYSICAL_PHASE_TRANSITION","CHAIN_ALL_N","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS")
 checks={
  "analyzer_positive":a.get("terminal")==POS and a.get("BULK_DEFECT_UNIFORM_BOUND_ALL_N") is True and a.get("ASYMPTOTIC_COST_DENSITY_EXACT") is True and a.get("PURE_SCALING_RAY_EVENTUALLY_AFFINE") is True and a.get("ASYMPTOTIC_COUNT_SPACE_PHASE_GEOMETRY") is True and valid(a),
  "generic_positive":g.get("decision")=="ACCEPT_BULK_DEFECT_THERMODYNAMIC_LIMIT" and g.get("all_checks") is True,
  "digest_bound":g.get("source_result_digest")==a.get("result_digest"),
  "protocol_bound":a.get("protocol_sha256")==hashlib.sha256(PROTO.read_bytes()).hexdigest(),
  "parents":a.get("parent_checks",{}).get("qg23") is True and a.get("parent_checks",{}).get("qg26") is True and a.get("parent_checks",{}).get("four_baselines") is True,
  "local_ranges":a.get("local_bounds",{}).get("spectator_range")==[0,6] and a.get("local_bounds",{}).get("two_branch_active_range")==[0,6] and a.get("local_bounds",{}).get("two_branch_correction_range")==[-6,6],
  "uniform_band":a.get("local_bounds",{}).get("lower_defect_constant")==-34 and a.get("local_bounds",{}).get("upper_defect_constant")==8 and a.get("proof_audit",{}).get("uniform_band")=="B_min(N)-34 <= C_DP(N) <= B_min(N)+8",
  "one_active_upper":a.get("local_bounds",{}).get("one_active_rows")==48 and a.get("local_bounds",{}).get("one_active_structural_values")==[2] and a.get("proof_audit",{}).get("upper_one_active_universal") is True,
  "scaling_ray":a.get("proof_audit",{}).get("finite_guarded_lines_on_scaling_ray") is True and a.get("proof_audit",{}).get("eventual_period_one_affinity") is True and a.get("proof_audit",{}).get("scaling_ray_slope_equals_B_min") is True,
  "bulk_geometry":a.get("baseline",{}).get("distinct_vectors")==4 and a.get("proof_audit",{}).get("four_form_bulk_phase_geometry") is True and len(a.get("bulk_tie_forms",[]))==6,
  "motifs":len(a.get("frozen_motif_controls",{}))==6 and all(v.get("match") is True and v.get("valid_six_targets") is True for v in a.get("frozen_motif_controls",{}).values()),
  "stronger_false_analyzer":all(a.get(k) is False for k in stronger),
  "stronger_false_generic":all(g.get(k) is False for k in stronger),
  "no_external_authority":all(a.get(k) is False for k in ("novelty_authority","r6_authority","physical_quantum_advantage_claim")) and all(g.get(k) is False for k in ("novelty_authority","r6_authority","physical_quantum_advantage_claim")),
 }
 ok=all(checks.values());out={"schema":"ORIONQG.QG27.NativeVerification.v1","decision":"ACCEPT_BULK_DEFECT_THERMODYNAMIC_LIMIT" if ok else "REJECT","responsibility":"BULK_DEFECT__ASYMPTOTIC_COST_DENSITY__PERIOD1_SCALING_RAYS" if ok else "CANNOT_CHECK","all_checks":bool(ok),"checks":checks,"source_result_digest":a.get("result_digest"),"BULK_DEFECT_UNIFORM_BOUND_ALL_N":bool(ok),"ASYMPTOTIC_COST_DENSITY_EXACT":bool(ok),"PURE_SCALING_RAY_EVENTUALLY_AFFINE":bool(ok),"ASYMPTOTIC_COUNT_SPACE_PHASE_GEOMETRY":bool(ok),"DEFECT_CONSTANTS_SHARP":False,"FINITE_N_GLOBAL_PHASE_BOUNDARY":False,"PHYSICAL_PHASE_TRANSITION":False,"CHAIN_ALL_N":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"responsibility":out["responsibility"],"band":[-34,8],"asymptotic":out["ASYMPTOTIC_COST_DENSITY_EXACT"]}));return 0
if __name__=="__main__":raise SystemExit(main())
