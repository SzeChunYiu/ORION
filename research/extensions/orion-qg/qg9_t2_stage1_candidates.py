#!/usr/bin/env python3
"""QG-9 T2 stage 1: generate support-2 tightness candidates without cap1/DP access."""
from __future__ import annotations

import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
sys.path.insert(0, str(ORION_Q)); sys.path.insert(0, str(ROOT / "research/extensions/orion-qg"))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import qg9_support3_relabel_exchange as v3  # noqa: E402

ISSUE="SzeChunYiu/ORION#803"
BASE="a80dbd57d9124f058de7465a13de8c69416c368b"
PROTOCOL=ROOT/"development/orion-qg-regime-geometry/QG9_T2_SUPPORT2_TIGHTNESS_PROTOCOL_V1.md"
PARENT_RECEIPT=ROOT/"development/orion-qg-regime-geometry/QG9_SUPPORT2_PROTECTED_RUN_RECEIPT_2026-08-21.json"
PARENT_RESULT=ROOT/"research/extensions/orion-qg/QG9_SUPPORT2_FULL_ACCEPTANCE_RESULTS.json"
DEFAULT=ROOT/"artifacts/orion-qg-qg9-t2-stage1.json"
TOKEN="ORIONQG_QG9_T2_STAGE1="


def canonical(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def wt(k):return p10.wt(k)

def global_from_columns(cols):
    r0=p10.key_from_codes([cols[0][0],cols[1][0]])
    r1=p10.key_from_codes([cols[0][1],cols[1][1]])
    s0=p10.key_from_codes([cols[0][2],cols[1][2]])
    s1=p10.key_from_codes([cols[0][3],cols[1][3]])
    return r0,r1,s0,s1

def accepted(r0,r1,s0,s1):
    if p10.symp(r0,r1)!=1:return False,None
    c0=2*p10.symp(s0,r0)+p10.symp(s1,r0)
    c1=2*p10.symp(s0,r1)+p10.symp(s1,r1)
    ok=c0 in (1,2,3) and c1 in (1,2,3) and c0!=c1
    return ok,(c0,c1,c0^c1)

def candidate_row(cols,type_keys):
    r0,r1,s0,s1=global_from_columns(cols); ok,labels=accepted(r0,r1,s0,s1)
    if not ok:return None
    if max(wt(r0),wt(r1))!=2:return None
    rs=(r0,r1,p10.mul(r0,r1))
    uvals=[p10.uanti_support(rs,c) for c in range(3)]
    umin=min(uvals); central=next(i for i,v in enumerate(uvals) if v==umin)
    tag=2*(wt(s0)+wt(s1)); u2=2*umin+tag
    return {
        "columns":[list(x) for x in cols],
        "type_keys_digest":hashlib.sha256(canonical([str(k) for k in type_keys]).encode()).hexdigest(),
        "R0":list(r0),"R1":list(r1),"R2":list(rs[2]),"S0":list(s0),"S1":list(s1),
        "labels":list(labels),"supports":[wt(r0),wt(r1)],
        "central_min":central,"uanti_single_block":int(umin),"tag_cost":int(tag),"U2":int(u2),
        "targets_A":[list(x) for x in rs],"targets_B":[list(x) for x in rs],
        "restore_cost_desired":0,
    }

def main():
    pr=json.loads(PARENT_RECEIPT.read_text()); pres=json.loads(PARENT_RESULT.read_text())
    if pr.get("terminal")!="QG9_RANK2_ALL_N_SUPPORT2_SUFFICIENCY_MACHINE_CHECKED" or pr.get("both_accept") is not True:
        raise AssertionError("parent support2 receipt not bound")
    if pres.get("support2_boundary_control",{}).get("full_accepted_unsafe_type_cases")!=36:
        raise AssertionError("parent accepted support2 unsafe count drift")
    states,actions_by_type,_by_desc,concrete=v3.build_types()
    reverse={tuple(row):key for key,rows in states.items() for row in rows}
    local=sorted(reverse); unsafe_cache={}
    seen={}; raw_accepted_unsafe=0
    for q0 in local:
        for q1 in local:
            k0,k1=reverse[q0],reverse[q1]
            r0,r1,s0,s1=global_from_columns((q0,q1)); ok,_=accepted(r0,r1,s0,s1)
            if not ok or max(wt(r0),wt(r1))!=2:continue
            ck_pair=(k0,k1)
            if ck_pair not in unsafe_cache:
                unsafe_cache[ck_pair]=v3.safe_profile_move(ck_pair,actions_by_type) is None
            if not unsafe_cache[ck_pair]:continue
            raw_accepted_unsafe+=1
            cols=min((q0,q1),(q1,q0)); ck=canonical(cols)
            if ck in seen:continue
            row=candidate_row(cols,(reverse[cols[0]],reverse[cols[1]]))
            if row is None:raise AssertionError("canonical candidate lost acceptance")
            seen[ck]=row
    rows=[seen[k] for k in sorted(seen)]
    for i,r in enumerate(rows):r["candidate_index"]=i
    candidate_digest=hashlib.sha256(canonical(rows).encode()).hexdigest()
    out={
      "schema":"ORION.QG.QG9.T2.Stage1.v1","issue":ISSUE,"base_revision":BASE,
      "protocol_sha256":sha(PROTOCOL),"parent_receipt_sha256":sha(PARENT_RECEIPT),"parent_result_sha256":sha(PARENT_RESULT),
      "parent_terminal":pr.get("terminal"),"parent_both_accept":pr.get("both_accept"),
      "parent_accepted_unsafe_type_cases":36,"concrete_local_state_count":concrete,
      "profile_pair_safety_cache_entries":len(unsafe_cache),
      "raw_concrete_accepted_unsafe_ordered_pairs":raw_accepted_unsafe,
      "canonical_candidate_count":len(rows),"candidate_digest":candidate_digest,"candidates":rows,
      "cap1_opened":False,"unrestricted_dp_opened":False,"network_access":False,
      "chemistry_sources_read":False,"protected_subject_read":False,
      "support1_authority":False,"novelty_authority":False,"physical_quantum_advantage_claim":False,
    }
    out["result_digest"]=hashlib.sha256(canonical(out).encode()).hexdigest()
    ap=argparse.ArgumentParser();ap.add_argument("--output",default=str(DEFAULT));ns=ap.parse_args();p=Path(ns.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    summary={"schema":out["schema"],"result_digest":out["result_digest"],"candidate_digest":candidate_digest,"canonical_candidate_count":len(rows),"cap1_opened":False,"unrestricted_dp_opened":False}
    print(TOKEN+canonical(summary));return 0
if __name__=="__main__":raise SystemExit(main())
