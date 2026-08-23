#!/usr/bin/env python3
"""Native ORION-Q authority gate for QG-21 certificate robustness."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"artifacts/orion-qg-qg21-regime-robustness.json"
G=ROOT/"artifacts/orion-qg-qg21-generic-verification.json"
P=ROOT/"development/orion-qg-regime-geometry/QG21_REGIME_ROBUSTNESS_PROTOCOL_V1.md"
OUT=ROOT/"artifacts/orion-qg-qg21-native-verification.json"
TOKEN="ORIONQG_QG21_NATIVE="

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def vd(r):
 d={k:v for k,v in r.items() if k!="result_digest"};return r.get("result_digest")==hashlib.sha256(canon(d).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--analyzer",type=Path,default=A);ap.add_argument("--generic",type=Path,default=G);ap.add_argument("--output",type=Path,default=OUT);x=ap.parse_args();a=json.loads(x.analyzer.read_text());g=json.loads(x.generic.read_text())
 c={"analyzer":a.get("terminal")=="QG21_CERTIFIED_REGIME_ROBUSTNESS_RADIUS_MACHINE_CHECKED" and a.get("certificate_margin_authority") is True and vd(a),
    "generic":g.get("decision")=="ACCEPT_CERTIFICATE_ROBUSTNESS" and g.get("all_checks") is True,
    "bound":g.get("source_result_digest")==a.get("result_digest"),"protocol_present":P.exists(),
    "qg8_boundary_zero":a["qg8"]["O0"]["linf_fixed_tr_radius"]=="0" and a["qg8"]["O2"]["linf_fixed_tr_radius"]=="0",
    "qg16_interior_half":a["qg16"]["O_in"]["linf_fixed_tr_radius"]=="1/2",
    "no_true_phase_promotion":a.get("true_phase_boundary")=="OPEN" and a.get("true_phase_bracket")=="NOT_CLAIMED_IN_QG21_V1_CALIBRATION",
    "outside_fail_closed":a.get("outside_cone_semantics")=="CERTIFICATE_NOT_APPLICABLE__NOT_REGIME_CHANGE",
    "authority":a.get("novelty_authority") is False and a.get("r6_authority") is False and a.get("physical_quantum_advantage_claim") is False}
 ok=all(c.values());o={"schema":"ORIONQG.QG21.NativeVerification.v1","decision":"ACCEPT_CERTIFICATE_ROBUSTNESS" if ok else "REJECT","responsibility":"CERTIFICATE_MARGIN" if ok else "CANNOT_CHECK","all_checks":ok,"checks":c,"source_result_digest":a.get("result_digest"),"CERTIFICATE_MARGIN":ok,"TRUE_PHASE_BOUNDARY":False,"TRUE_PHASE_BRACKET":False,"novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False};x.output.parent.mkdir(parents=True,exist_ok=True);x.output.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n");print(TOKEN+canon({"decision":o["decision"],"all_checks":ok,"certificate_margin":ok,"true_phase_boundary":False}));return 0
if __name__=="__main__":raise SystemExit(main())
