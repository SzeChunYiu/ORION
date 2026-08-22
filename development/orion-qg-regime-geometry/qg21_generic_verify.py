#!/usr/bin/env python3
"""Independent generic ORION verifier for QG-21 robustness calibration."""
from __future__ import annotations
import argparse, hashlib, json
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
IN=ROOT/"artifacts/orion-qg-qg21-regime-robustness.json"
OUT=ROOT/"artifacts/orion-qg-qg21-generic-verification.json"
TOKEN="ORIONQG_QG21_GENERIC="

def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def rat(x): return x if isinstance(x,F) else F(str(x))
def rs(x): return str(x.numerator) if x.denominator==1 else f"{x.numerator}/{x.denominator}"
def valid_digest(r):
    d={k:v for k,v in r.items() if k!="result_digest"}
    return r.get("result_digest")==hashlib.sha256(canon(d).encode()).hexdigest()

def sl8(t): return {"central":t[1]-2*t[3],"noncentral":t[0]-2*t[3]}
def sl16(t):
    nc,c,tag,r=t
    return {"2nc_minus_5r":2*nc-5*r,"c_plus_nc_minus_5r":c+nc-5*r,
            "2nc_minus_2r_minus_2tag":2*nc-2*r-2*tag,
            "c_plus_nc_minus_2r_minus_2tag":c+nc-2*r-2*tag}
C8={"central":[F(0),F(1)],"noncentral":[F(1),F(0)]}
C16={"2nc_minus_5r":[F(2),F(0),F(0)],"c_plus_nc_minus_5r":[F(1),F(1),F(0)],
     "2nc_minus_2r_minus_2tag":[F(2),F(0),F(-2)],"c_plus_nc_minus_2r_minus_2tag":[F(1),F(1),F(-2)]}
EPS=[F(0),F(1,20),F(1,10),F(1,5)]
def rad(sl,c): return min((sl[k]/sum(abs(x) for x in c[k]),k) for k in sl)
def box(sl,c,e): return {k:sl[k]-e*sum(abs(x) for x in c[k]) for k in sl}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",type=Path,default=IN);ap.add_argument("--output",type=Path,default=OUT);a=ap.parse_args()
    src=json.loads(a.input.read_text())
    checks={"source_digest":valid_digest(src),"terminal":src.get("terminal")=="QG21_CERTIFIED_REGIME_ROBUSTNESS_RADIUS_MACHINE_CHECKED",
            "scope":src.get("true_phase_boundary")=="OPEN" and src.get("outside_cone_semantics")=="CERTIFICATE_NOT_APPLICABLE__NOT_REGIME_CHANGE"}
    for name in ("O0","O2"):
        rec=src["qg8"][name];t=[rat(rec["theta"][k]) for k in ("t_nc","t_c","t_tag","t_r")];sl=sl8(t);r,act=rad(sl,C8)
        checks[f"qg8_{name}"]=({k:rs(v) for k,v in sl.items()}==rec["slacks"] and rs(r)==rec["linf_fixed_tr_radius"] and act==rec["active_facet"])
        for e in EPS:
            wb=box(sl,C8,e);checks[f"qg8_{name}_box_{rs(e)}"]=(all(v>=0 for v in wb.values())==rec["boxes"][rs(e)]["contained"])
    for name,rec in src["qg16"].items():
        t=[rat(rec["theta"][k]) for k in ("t_nc","t_c","t_tag","t_r")];sl=sl16(t);inside=all(v>=0 for v in sl.values());r,act=rad(sl,C16)
        checks[f"qg16_{name}"]=({k:rs(v) for k,v in sl.items()}==rec["slacks"] and inside==rec["inside"] and rs(r)==rec["linf_fixed_tr_radius"] and act==rec["active_facet"])
        if inside:
            for e in EPS:
                wb=box(sl,C16,e);checks[f"qg16_{name}_box_{rs(e)}"]=(all(v>=0 for v in wb.values())==rec["boxes"][rs(e)]["contained"])
    checks["Oin_exact_half"]=src["qg16"]["O_in"]["linf_fixed_tr_radius"]=="1/2"
    checks["O0_zero"]=src["qg16"]["O0"]["linf_fixed_tr_radius"]=="0"
    ok=all(checks.values())
    out={"schema":"ORIONQG.QG21.GenericVerification.v1","decision":"ACCEPT_CERTIFICATE_ROBUSTNESS" if ok else "REJECT",
         "all_checks":ok,"checks":checks,"source_result_digest":src.get("result_digest"),"certificate_margin_authority":ok,
         "true_phase_boundary":"OPEN","novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"source_result_digest":out["source_result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
