#!/usr/bin/env python3
"""Independent generic ORION verifier for MAX-R4E-A authority-indexed routing calibration."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "artifacts/orion-q-max-r4ea-authority-router.json"
QG31 = ROOT / "research/extensions/orion-qg/QG31_QUERY_INDEXED_ABSTRACTION_RESULTS.json"
QG28 = ROOT / "research/extensions/orion-qg/QG28_LOCAL_CLIFFORD_ORBIT_RESULTS.json"
QG15B = ROOT / "research/extensions/orion-qg/QG15B_PREDICATE_LANGUAGE_RESULTS.json"
QG9 = ROOT / "research/extensions/orion-qg/QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json"
R4B = ROOT / "research/extensions/orion-q/MAX_R4B_TARE_SPLIT_MAJORISATION_RESULTS.json"
R4D = ROOT / "research/extensions/orion-q/MAX_R4D_H2O_DUCC_CONFIRMATION_RESULTS.json"
OUT = ROOT / "artifacts/orion-q-max-r4ea-generic-verification.json"
TOKEN = "ORIONQ_MAX_R4EA_GENERIC="
POS = "MAX_R4EA_AUTHORITY_INDEXED_ROUTER_PARETO_DOMINATES_STATIC_ABSTRACTION_POLICIES_ON_REAL_RECEIPTS"

ORDER = ["ONE_LITERAL_PREDICATE","SUPPORT1_NORMAL_FORM","COEFFICIENT_THEOREM","BULK45","SPECTRUM54","ORBIT715","INDEXED715","EXACT_RICH_STATE","IMPLEMENTATION_AWARE_RESOURCE","CANNOT_AUTHORIZE"]
RANK = {x:i+1 for i,x in enumerate(ORDER)}


def canon(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False)


def valid_digest(r: dict[str, Any]) -> bool:
    u = {k:v for k,v in r.items() if k != "result_digest"}
    return r.get("result_digest") == hashlib.sha256(canon(u).encode()).hexdigest()


def r(name: str, supports: tuple[str, ...], kind: str = "ANSWER", size: int | None = None) -> dict[str, Any]:
    return {"name":name,"supports":set(supports),"kind":kind,"rank":RANK[name],"size":size}


def independent_receipt_checks() -> dict[str, bool]:
    q31=json.loads(QG31.read_text()); q28=json.loads(QG28.read_text()); q15=json.loads(QG15B.read_text()); q9=json.loads(QG9.read_text()); b=json.loads(R4B.read_text()); d=json.loads(R4D.read_text())
    return {
        "q31": q31.get("both_accept") is True and q31.get("class_counts",{}).get("bulk")==45 and q31.get("class_counts",{}).get("defect_spectrum")==54 and q31.get("class_counts",{}).get("indexed_local_response")==715 and q31.get("BULK_SPECTRUM_PARTITIONS_INCOMPARABLE") is True,
        "q28": q28.get("both_accept") is True and q28.get("LOCAL_CLIFFORD_ORBIT_COUNT")==715 and q28.get("ORBIT_HISTOGRAM_SUFFICIENT_STATISTIC_ALL_N") is True,
        "six": q15.get("q3",{}).get("E_floor")==0 and q15.get("q3",{}).get("zero_error_cells",{}).get("headline_cell")==[1,1],
        "stab": q15.get("q2",{}).get("E_floor")==43 and q15.get("q2",{}).get("mixed_cell_count")==12,
        "r6i": q9.get("both_accept") is True and q9.get("intrinsic_support_number")==1,
        "r4b": b.get("terminal")=="R4B_TARE_SPLIT_MAJORISATION_THEOREM_SUPPORTED__COEFFICIENT_COORDINATE_ONLY" and "not compiled-resource" in str(b.get("authority","")),
        "r4d": d.get("r4d_protocol_pass") is True and d.get("terminal")=="R4D_IMPLEMENTATION_AWARE_SPLIT_TARE_COMPILER_SUPPORTED__REAL_PUBLIC_HAMILTONIAN" and "does not authorize full-circuit" in str(d.get("nonclaim","")),
    }


def cases() -> list[dict[str, Any]]:
    A="ASYMPTOTIC_BULK_VALUE"; S="UNLABELED_LOCAL_DEFECT_SPECTRUM"; I="INDEXED_LOCAL_RESPONSE"; F="FULL_FINITE_OPTIMUM"; D="DONOR_OPTIMAL_LABEL"; N="SUPPORT_NORMAL_FORM"; C="COEFFICIENT_SUBNORMALIZATION"; T="TOTAL_COMPILED_RESOURCE"; X="FULL_CIRCUIT_OR_NOVELTY"
    return [
        {"id":"C1","q":A,"routes":[r("BULK45",(A,),size=45),r("ORBIT715",(A,F),size=715),r("EXACT_RICH_STATE",(A,F))]},
        {"id":"C2","q":S,"routes":[r("BULK45",(A,),size=45),r("SPECTRUM54",(S,),size=54),r("EXACT_RICH_STATE",(S,))]},
        {"id":"C3","q":I,"routes":[r("BULK45",(A,),size=45),r("SPECTRUM54",(S,),size=54),r("INDEXED715",(I,),size=715),r("EXACT_RICH_STATE",(I,))]},
        {"id":"C4","q":F,"routes":[r("BULK45",(A,),size=45),r("SPECTRUM54",(S,),size=54),r("ORBIT715",(A,F),size=715),r("EXACT_RICH_STATE",(F,))]},
        {"id":"C5","q":D,"routes":[r("ONE_LITERAL_PREDICATE",(D,)),r("EXACT_RICH_STATE",(D,))]},
        {"id":"C6","q":D,"routes":[r("ONE_LITERAL_PREDICATE",()),r("EXACT_RICH_STATE",(D,),kind="ESCALATE")]},
        {"id":"C7","q":N,"routes":[r("SUPPORT1_NORMAL_FORM",(N,)),r("EXACT_RICH_STATE",(N,))]},
        {"id":"C8","q":C,"routes":[r("COEFFICIENT_THEOREM",(C,)),r("IMPLEMENTATION_AWARE_RESOURCE",(C,T),kind="ESCALATE")]},
        {"id":"C9","q":T,"routes":[r("COEFFICIENT_THEOREM",(C,)),r("IMPLEMENTATION_AWARE_RESOURCE",(C,T),kind="ESCALATE")]},
        {"id":"C10","q":X,"routes":[r("IMPLEMENTATION_AWARE_RESOURCE",(C,T),kind="ESCALATE"),r("CANNOT_AUTHORIZE",(),kind="ABSTAIN")]},
    ]


def auth(c: dict[str, Any], x: dict[str, Any]) -> bool:
    return c["q"] in x["supports"]


def gold(c: dict[str, Any]) -> str:
    z=[x for x in c["routes"] if x["name"]!="CANNOT_AUTHORIZE" and auth(c,x)]
    return min(z,key=lambda x:(x["rank"],x["name"]))["name"] if z else "CANNOT_AUTHORIZE"


def chosen(c: dict[str, Any], b: str) -> str:
    offered=[x for x in c["routes"] if x["name"]!="CANNOT_AUTHORIZE"]; good=[x for x in offered if auth(c,x)]
    if b=="B0": return max(good,key=lambda x:(x["rank"],x["name"]))["name"] if good else "CANNOT_AUTHORIZE"
    if b=="B1": return min(offered,key=lambda x:(x["rank"],x["name"]))["name"] if offered else "CANNOT_AUTHORIZE"
    if b=="B2": return min(good,key=lambda x:(x["rank"],x["name"]))["name"] if good else "CANNOT_AUTHORIZE"
    raise ValueError(b)


def getroute(c: dict[str, Any], name: str) -> dict[str, Any]:
    if name=="CANNOT_AUTHORIZE": return r(name,(),kind="ABSTAIN")
    return next(x for x in c["routes"] if x["name"]==name)


def independent_score(cs: list[dict[str, Any]], b: str) -> dict[str, Any]:
    rows=[]; cor=fa=ov=rich=cap=esc=0; sizes=[]
    for c in cs:
        g=gold(c); s=chosen(c,b); sr=getroute(c,s); gr=getroute(c,g); au=s=="CANNOT_AUTHORIZE" or auth(c,sr)
        false=s!="CANNOT_AUTHORIZE" and sr["kind"]=="ANSWER" and not au
        over=s!="CANNOT_AUTHORIZE" and not au and sr["rank"]<gr["rank"]
        rr=au and s!=g and sr["rank"]>gr["rank"]
        opp=gr["kind"]=="ANSWER" and any(x["name"]!="CANNOT_AUTHORIZE" and auth(c,x) and x["rank"]>gr["rank"] for x in c["routes"])
        captured=opp and s==g; e=(g=="CANNOT_AUTHORIZE" or gr["kind"]=="ESCALATE") and s==g
        cor+=s==g; fa+=false; ov+=over; rich+=rr; cap+=captured; esc+=e
        if c["id"] in {"C1","C2","C3","C4"}: sizes.append(sr.get("size"))
        rows.append({"case_id":c["id"],"selected":s,"gold":g,"authorized":au,"correct":s==g,"false_authority":false,"overcompression":over,"avoidable_rich_state":rr,"captured":captured,"correct_escalation_or_abstention":e})
    return {"correct_route_count":int(cor),"false_authority_count":int(fa),"overcompression_count":int(ov),"avoidable_rich_state_count":int(rich),"compact_authorized_opportunities":sum(int(getroute(c,gold(c))["kind"]=="ANSWER" and any(x["name"]!="CANNOT_AUTHORIZE" and auth(c,x) and x["rank"]>getroute(c,gold(c))["rank"] for x in c["routes"])) for c in cs),"compact_authorized_captured":int(cap),"correct_escalation_abstention_count":int(esc),"tare_selected_representation_sizes":sizes,"rows":rows}


def normalize_source(s: dict[str, Any]) -> dict[str, Any]:
    return {b:{k:v for k,v in s.get("baselines",{}).get(b,{}).items() if k in {"correct_route_count","false_authority_count","overcompression_count","avoidable_rich_state_count","compact_authorized_opportunities","compact_authorized_captured","correct_escalation_abstention_count","tare_selected_representation_sizes","rows"}} for b in ("B0","B1","B2")}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,default=SRC); ap.add_argument("--output",type=Path,default=OUT); ns=ap.parse_args(); src=json.loads(ns.input.read_text()); rc=independent_receipt_checks(); cs=cases(); expected={b:independent_score(cs,b) for b in ("B0","B1","B2")}; source=normalize_source(src)
    compare={}
    for b in ("B0","B1","B2"):
        e=expected[b]; s=source[b]
        compare[b+"_summary"]={k:s.get(k)==e.get(k) for k in e if k!="rows"}
        srcrows={x.get("case_id"):{k:x.get(k) for k in ("selected","gold","authorized","correct","false_authority","overcompression","avoidable_rich_state","captured","correct_escalation_or_abstention")} for x in s.get("rows",[])}
        exprows={x["case_id"]:{k:x.get(k) for k in ("selected","gold","authorized","correct","false_authority","overcompression","avoidable_rich_state","captured","correct_escalation_or_abstention")} for x in e["rows"]}
        compare[b+"_rows"] = srcrows == exprows
    checks={"source_digest":valid_digest(src),"source_terminal":src.get("terminal")==POS,"receipt_checks":all(rc.values()),"case_count":src.get("case_count")==10,"comparisons":all((v if isinstance(v,bool) else all(v.values())) for v in compare.values()),"authority_boundary":src.get("HELD_OUT_TRANSFER_AUTHORITY") is False and src.get("AUTONOMOUS_SKILL_SELECTION_AUTHORITY") is False and src.get("GENERAL_QUANTUM_SCIENCE_IMPROVEMENT") is False and src.get("NOVELTY_AUTHORITY") is False}
    ok=all(checks.values())
    out={"schema":"ORIONQ.MAXR4EA.GenericVerification.v1","decision":"ACCEPT_AUTHORITY_INDEXED_ROUTER_CALIBRATION" if ok else "REJECT","all_checks":bool(ok),"checks":checks,"receipt_checks":rc,"comparison_checks":compare,"independent_expected":{b:{k:v for k,v in expected[b].items() if k!="rows"} for b in expected},"source_result_digest":src.get("result_digest"),"HELD_OUT_TRANSFER_AUTHORITY":False,"AUTONOMOUS_SKILL_SELECTION_AUTHORITY":False,"GENERAL_QUANTUM_SCIENCE_IMPROVEMENT":False,"NOVELTY_AUTHORITY":False}
    ns.output.parent.mkdir(parents=True,exist_ok=True); ns.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"decision":out["decision"],"all_checks":ok,"B0":out["independent_expected"]["B0"],"B1":out["independent_expected"]["B1"],"B2":out["independent_expected"]["B2"]})); return 0

if __name__=="__main__": raise SystemExit(main())
