#!/usr/bin/env python3
"""QG-7f F0: hostile audit of the proposed common-two-coordinate chain representation."""
from __future__ import annotations

import argparse, hashlib, json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
P7E=ROOT/"research/extensions/orion-qg/QG7E_V2_PP_SINGLE_PINNER_RESULTS.json"
P7C=ROOT/"research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
PROTO=ROOT/"development/orion-qg-regime-geometry/QG7F_CHAIN_REPRESENTATION_AUDIT_PROTOCOL_V1.md"
OUT=ROOT/"artifacts/orion-qg-qg7f-chain-representation-audit.json"
TOKEN="ORIONQG_QG7F="
POS="QG7F_TWO_COORD_REDUCTION_REFUTED__TAG3_MULTI_COMM_S2_CONFIGURATION"

I,X,Y,Z=0,1,2,3
S=(X,X,X)
FRAMES={
    "A":((X,I,I),(Y,I,I)),
    "B":((Y,Y,I),(Z,I,I)),
    "C":((I,Y,Y),(I,Z,I)),
}

def canon(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(v:dict[str,Any])->str:return hashlib.sha256(canon(v).encode()).hexdigest()
def lsy(a:int,b:int)->int:return int(a!=0 and b!=0 and a!=b)
def wt(p:tuple[int,...])->int:return sum(x!=0 for x in p)
def supp(p:tuple[int,...])->list[int]:return [i for i,x in enumerate(p) if x!=0]
def symp(a:tuple[int,...],b:tuple[int,...])->int:return sum(lsy(x,y) for x,y in zip(a,b))%2
def comm_s2(r0,r1,s):
    if wt(r0)!=2 or wt(r1)!=1:return {"holds":False,"reason":"weights"}
    a=supp(r1)[0]; sr0=supp(r0)
    if a not in sr0:return {"holds":False,"reason":"partner_off_support"}
    b=next(q for q in sr0 if q!=a)
    good=(s[b]!=0 and lsy(s[b],r0[b])==1 and s[a]!=0 and lsy(s[a],r0[a])==1 and r1[a] not in (0,s[a],r0[a]))
    class00=[q for q in sr0 if lsy(r0[q],r1[q])==0 and lsy(s[q],r0[q])==0]
    return {"holds":bool(good and not class00),"a":a,"b":b,"support":sr0,"class00_reducible_coordinates":class00,
            "tag_local_symp":{"a":lsy(s[a],r0[a]),"b":lsy(s[b],r0[b])},"partner_letter":r1[a]}

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);a=ap.parse_args()
    q7e=json.loads(P7E.read_text());q7c=json.loads(P7C.read_text())
    parent={
        "qg7e_terminal":q7e.get("terminal")=="QG7E_V2_PP_SINGLE_PINNER_CLOSED_ALL_HIDDEN_ENVIRONMENTS__CHAIN_OPEN",
        "qg7e_both_accept":q7e.get("both_accept") is True,
        "qg7e_pp_closed_chain_open":q7e.get("PP_SINGLE_PINNER_ALL_N") is True and q7e.get("CHAIN_ALL_N") is False,
        "qg7c_m1_complete":q7c.get("gates",{}).get("G5_m1_inventory_complete") is True and q7c.get("m1_inventory",{}).get("holds") is True,
        "qg7c_comm_s2_occupancy_two":q7c.get("t2_occupancy",{}).get("per_shape_anticommuting_tag_qubits",{}).get("comm_s2")==2,
    }
    block={}
    common=[]
    for name,(r0,r1) in FRAMES.items():
        labels=(symp(S,r0),symp(S,r1));pair=symp(r0,r1)
        common.append(labels)
        block[name]={"r0":list(r0),"r1":list(r1),"weights":[wt(r0),wt(r1)],"supports":[supp(r0),supp(r1)],
                     "pair_symp":pair,"tag_labels":list(labels),"nonzero":wt(r0)>0 and wt(r1)>0}
    block["A"]["anchored_shape"]=(block["A"]["weights"]==[1,1] and block["A"]["supports"]==[[0],[0]] and S[0]==FRAMES["A"][0][0] and lsy(S[0],FRAMES["A"][1][0])==1)
    for name in ("B","C"):
        block[name]["comm_s2_shape"]=comm_s2(FRAMES[name][0],FRAMES[name][1],S)
    bset=set(block["B"]["supports"][0]);cset=set(block["C"]["supports"][0]);sset=set(supp(S))
    gates={
        "parent_custody":all(parent.values()),
        "all_pairs_anticommute":all(block[x]["pair_symp"]==1 for x in ("A","B","C")),
        "all_frames_nonzero":all(block[x]["nonzero"] for x in ("A","B","C")),
        "shared_labels_01":all(tuple(block[x]["tag_labels"])==(0,1) for x in ("A","B","C")),
        "A_anchored":block["A"]["anchored_shape"] is True,
        "B_comm_s2_irreducible":block["B"]["comm_s2_shape"]["holds"] is True,
        "C_comm_s2_irreducible":block["C"]["comm_s2_shape"]["holds"] is True,
        "tag_weight_three":wt(S)==3,
        "different_comm_s2_support_pairs":bset!=cset,
        "each_pair_inside_tag_support":bset<=sset and cset<=sset,
        "protocol_bound":PROTO.exists(),
    }
    ok=all(gates.values())
    out={"schema":"ORIONQG.QG7F.ChainRepresentationAudit.v1","issue":"SzeChunYiu/ORION#874",
         "protocol_sha256":hashlib.sha256(PROTO.read_bytes()).hexdigest(),"parent_bindings":parent,
         "candidate":{"tag":list(S),"tag_weight":wt(S),"tag_support":supp(S),"blocks":block},
         "observed_comm_s2_support_pairs":{"B":sorted(bset),"C":sorted(cset)},"gates":gates,
         "representation_premise":"ALL_SIMULTANEOUS_IRREDUCIBLE_COMM_S2_BLOCKS_SHARE_ONE_TWO_COORDINATE_TAG_SUPPORT",
         "representation_premise_refuted":bool(ok),"CHAIN_REPRESENTATION_COMPLETE":False,"CHAIN_ALL_N":False,
         "GLOBAL_BDOUBLEPRIME_COMPLETENESS":False,"FIFTH_REGIME_FOUND":False,"novelty_authority":False,"r6_authority":False,
         "physical_quantum_advantage_claim":False,"terminal":POS if ok else "QG7F_F0_CANDIDATE_REJECTED__TWO_COORD_REDUCTION_UNRESOLVED"}
    out["result_digest"]=digest(out);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(TOKEN+canon({"terminal":out["terminal"],"premise_refuted":out["representation_premise_refuted"],"tag_weight":3,
                       "B_support":sorted(bset),"C_support":sorted(cset),"all_gates":ok,"result_digest":out["result_digest"]}));return 0
if __name__=="__main__":raise SystemExit(main())
