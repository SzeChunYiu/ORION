#!/usr/bin/env python3
"""QG-21 exact certificate-margin calibration for QG-8 and QG-16."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
QG8 = ROOT / "research/extensions/orion-qg/QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json"
QG16 = ROOT / "research/extensions/orion-qg/QG16_R6I_SUPPORT1_PHASE_RESULTS.json"
OUT = ROOT / "artifacts/orion-qg-qg21-regime-robustness.json"
TOKEN = "ORIONQG_QG21="
POS = "QG21_CERTIFIED_REGIME_ROBUSTNESS_RADIUS_MACHINE_CHECKED"
EPS = [F(0), F(1,20), F(1,10), F(1,5)]


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def rat(x: Any) -> F:
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x, 1)
    return F(str(x))


def rs(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def digest(obj: dict[str, Any]) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def qg8_slacks(theta: dict[str, F]) -> dict[str, F]:
    return {
        "central": theta["t_c"] - 2*theta["t_r"],
        "noncentral": theta["t_nc"] - 2*theta["t_r"],
    }


def qg16_slacks(theta: dict[str, F]) -> dict[str, F]:
    return {
        "2nc_minus_5r": 2*theta["t_nc"] - 5*theta["t_r"],
        "c_plus_nc_minus_5r": theta["t_c"] + theta["t_nc"] - 5*theta["t_r"],
        "2nc_minus_2r_minus_2tag": 2*theta["t_nc"] - 2*theta["t_r"] - 2*theta["t_tag"],
        "c_plus_nc_minus_2r_minus_2tag": theta["t_c"] + theta["t_nc"] - 2*theta["t_r"] - 2*theta["t_tag"],
    }


def worst_box(slack: F, coeffs: list[F], eps: F) -> F:
    # G1: t_r fixed; symmetric absolute L_infinity box on remaining coefficients.
    return slack - eps * sum(abs(c) for c in coeffs)


def radius(slacks: dict[str,F], coeffs: dict[str,list[F]]) -> tuple[F,str]:
    candidates=[]
    for name,s in slacks.items():
        norm=sum(abs(c) for c in coeffs[name])
        if norm:
            candidates.append((s/norm,name))
    return min(candidates, key=lambda x:(x[0],x[1]))


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output", type=Path, default=OUT); args=ap.parse_args()
    q8=json.loads(QG8.read_text()); q16=json.loads(QG16.read_text())
    parent={
        "qg8_terminal": q8.get("terminal")=="QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED",
        "qg8_halfspaces": q8.get("support2_cone",{}).get("conditions")==["t_c >= 2*t_r","t_nc >= 2*t_r"],
        "qg8_global_sharpness_open": q8.get("support2_cone",{}).get("global_boundary_sharpness")=="OPEN",
        "qg16_terminal": q16.get("terminal")=="QG16_R6I_OBJECTIVE_INDEXED_SUPPORT1_CONE_ALL_N_MACHINE_CHECKED",
        "qg16_full_halfspaces": q16.get("full_cone_halfspaces")==[
            "2*t_nc >= 5*t_r","t_c+t_nc >= 5*t_r","2*t_nc >= 2*t_r+2*t_tag","t_c+t_nc >= 2*t_r+2*t_tag"],
        "qg16_both_accept": q16.get("both_accept") is True,
        "qg16_global_sharpness_open": q16.get("global_phase_boundary_sharpness")=="OPEN",
    }

    q8_coeff={"central":[F(0),F(1)],"noncentral":[F(1),F(0)]} # [t_nc,t_c]
    q16_coeff={
        "2nc_minus_5r":[F(2),F(0),F(0)],
        "c_plus_nc_minus_5r":[F(1),F(1),F(0)],
        "2nc_minus_2r_minus_2tag":[F(2),F(0),F(-2)],
        "c_plus_nc_minus_2r_minus_2tag":[F(1),F(1),F(-2)],
    } # [t_nc,t_c,t_tag], t_r fixed

    q8_points={}
    for name in ("O0","O2"):
        w=q8["qg2_binding"]["objectives"][name]["weights"]
        th={k:rat(w[k]) for k in ("t_nc","t_c","t_tag","t_r")}
        sl=qg8_slacks(th); r,active=radius(sl,q8_coeff)
        boxes={rs(e): {"worst_slacks":{k:rs(worst_box(sl[k],q8_coeff[k],e)) for k in sl},
                       "contained": all(worst_box(sl[k],q8_coeff[k],e)>=0 for k in sl)} for e in EPS}
        q8_points[name]={"theta":{k:rs(v) for k,v in th.items()},"slacks":{k:rs(v) for k,v in sl.items()},
                         "linf_fixed_tr_radius":rs(r),"active_facet":active,"boxes":boxes}

    q16_points={}
    for name, rec in q16["controls"].items():
        vals=rec["theta"]; th={"t_nc":rat(vals[0]),"t_c":rat(vals[1]),"t_tag":rat(vals[2]),"t_r":rat(vals[3])}
        sl=qg16_slacks(th); inside=all(v>=0 for v in sl.values())
        r,active=radius(sl,q16_coeff)
        boxes={rs(e): {"worst_slacks":{k:rs(worst_box(sl[k],q16_coeff[k],e)) for k in sl},
                       "contained": all(worst_box(sl[k],q16_coeff[k],e)>=0 for k in sl)} for e in EPS} if inside else {}
        q16_points[name]={"theta":{k:rs(v) for k,v in th.items()},"inside":inside,
                          "slacks":{k:rs(v) for k,v in sl.items()},"minimum_slack":rs(min(sl.values())),
                          "linf_fixed_tr_radius":rs(r),"active_facet":active,"boxes":boxes}

    gates={
        "parents_bound": all(parent.values()),
        "qg8_equalities_zero": all(q8_points[x]["linf_fixed_tr_radius"]=="0" for x in ("O0","O2")),
        "qg16_oin_radius_half": q16_points["O_in"]["linf_fixed_tr_radius"]=="1/2",
        "qg16_oin_active_tag_facet": q16_points["O_in"]["active_facet"]=="c_plus_nc_minus_2r_minus_2tag",
        "qg16_oin_eps_panel_contained": all(q16_points["O_in"]["boxes"][rs(e)]["contained"] for e in EPS),
        "qg16_o0_positive_boxes_fail": all(not q16_points["O0"]["boxes"][rs(e)]["contained"] for e in EPS[1:]),
        "outside_controls_not_promoted": all(not q16_points[x]["inside"] for x in ("O_tag_out","O_restore_out","O_nc_out")),
    }
    ok=all(gates.values())
    out={
        "schema":"ORIONQG.QG21.RegimeRobustness.v1","issue":"SzeChunYiu/ORION#864",
        "gauge":"G1_t_r_fixed","perturbation_norm":"L_infinity_absolute_box_on_non_r_coefficients",
        "epsilon_panel":[rs(e) for e in EPS],"parent_bindings":parent,
        "qg8":q8_points,"qg16":q16_points,"gates":gates,
        "certificate_margin_authority":bool(ok),"true_phase_boundary":"OPEN",
        "true_phase_bracket":"NOT_CLAIMED_IN_QG21_V1_CALIBRATION",
        "outside_cone_semantics":"CERTIFICATE_NOT_APPLICABLE__NOT_REGIME_CHANGE",
        "novelty_authority":False,"r6_authority":False,"physical_quantum_advantage_claim":False,
        "terminal":POS if ok else "QG21_CALIBRATION_GATE_FAILED",
    }
    out["result_digest"]=digest(out)
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"terminal":out["terminal"],"qg8_O0_radius":q8_points["O0"]["linf_fixed_tr_radius"],
                       "qg16_Oin_radius":q16_points["O_in"]["linf_fixed_tr_radius"],"all_gates":ok,"result_digest":out["result_digest"]}))
    return 0

if __name__=="__main__": raise SystemExit(main())
