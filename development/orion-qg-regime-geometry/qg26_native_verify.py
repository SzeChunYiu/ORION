#!/usr/bin/env python3
"""Native ORION-Q responsibility gate for QG-26 histogram/tropical geometry theorem."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-qg-qg26-parikh-histogram.json";G=ROOT/"artifacts/orion-qg-qg26-generic-verification.json";PROTO=ROOT/"development/orion-qg-regime-geometry/QG26_PARIKH_HISTOGRAM_PROTOCOL_V1.md";OUT=ROOT/"artifacts/orion-qg-qg26-native-verification.json";TOKEN="ORIONQG_QG26_NATIVE=";POS="QG26_TARE_EXACT_COST_IS_FINITE_GUARDED_TROPICAL_FUNCTION_OF_4096_COLUMN_COUNTS_ALL_N"
def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def valid_digest(r):
 u={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(u).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();a=json.loads(x.analyzer.read_text());g=json.loads(x.generic.read_text())
 stronger=("EXPLICIT_TEMPLATE_BASIS_ENUMERATED","PRACTICAL_STATIC_FORECASTER","CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS","CHAIN_ALL_N","GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE")
 checks={
  "analyzer_positive":a.get("terminal")==POS and a.get("HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True and a.get("FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION") is True and a.get("COUNT_SPACE_REGIME_GEOMETRY_EXISTS") is True and valid_digest(a),
  "generic_positive":g.get("decision")=="ACCEPT_PARIKH_GUARDED_TROPICAL_GEOMETRY" and g.get("all_checks") is True,
  "digest_bound":g.get("source_result_digest")==a.get("result_digest"),
  "protocol_bound":a.get("protocol_sha256")==hashlib.sha256(PROTO.read_bytes()).hexdigest(),
  "qg23_six_active_parent":a.get("parent_checks",{}).get("qg23_green") is True and a.get("parent_checks",{}).get("m1_shape_support_definitions") is True,
  "qg24_exact_control":a.get("parent_checks",{}).get("qg24_exact_all_n_control") is True,
  "local_decomposition":a.get("one_active_decomposition_control",{}).get("rows")==1572864 and a.get("one_active_decomposition_control",{}).get("all_match") is True and a.get("structural_cost_control",{}).get("rows")==131072 and a.get("structural_cost_control",{}).get("all_match") is True,
  "realization_control":a.get("placement_realization_controls",{}).get("all_equal") is True and a.get("proof_audit",{}).get("configuration_to_template") is True and a.get("proof_audit",{}).get("template_to_configuration_if_guard_holds") is True,
  "histogram_commutativity":a.get("proof_audit",{}).get("histogram_sufficient_statistic_all_n") is True and a.get("proof_audit",{}).get("path_or_configuration_updates_commute_across_coordinates") is True,
  "finite_templates":a.get("template_finiteness",{}).get("finite") is True and a.get("template_finiteness",{}).get("max_active_coordinates")==6,
  "stronger_false_analyzer":all(a.get(k) is False for k in stronger),
  "stronger_false_generic":all(g.get(k) is False for k in stronger),
  "no_external_authority":all(a.get(k) is False for k in ("novelty_authority","r6_authority","physical_quantum_advantage_claim")) and all(g.get(k) is False for k in ("novelty_authority","r6_authority","physical_quantum_advantage_claim")),
 }
 ok=all(checks.values());out={"schema":"ORIONQG.QG26.NativeVerification.v1","decision":"ACCEPT_PARIKH_GUARDED_TROPICAL_GEOMETRY" if ok else "REJECT","responsibility":"HISTOGRAM_SUFFICIENT__FINITE_GUARDED_TROPICAL_TEMPLATE_GEOMETRY" if ok else "CANNOT_CHECK","all_checks":bool(ok),"checks":checks,"source_result_digest":a.get("result_digest"),"HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N":bool(ok),"FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION":bool(ok),"COUNT_SPACE_REGIME_GEOMETRY_EXISTS":bool(ok),"EXPLICIT_TEMPLATE_BASIS_ENUMERATED":False,"PRACTICAL_STATIC_FORECASTER":False,"CLOSED_FORM_BDOUBLEPRIME_COMPLETENESS":False,"CHAIN_ALL_N":False,"GLOBAL_FINITE_INSTANCE_PHASE_BOUNDARY_IN_OBJECTIVE_SPACE":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
 x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":out["decision"],"responsibility":out["responsibility"],"histogram":out["HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N"],"templates":out["FINITE_GUARDED_TROPICAL_TEMPLATE_REPRESENTATION"]}));return 0
if __name__=="__main__":raise SystemExit(main())
