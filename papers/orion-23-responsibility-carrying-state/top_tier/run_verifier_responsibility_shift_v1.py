#!/usr/bin/env python3
from __future__ import annotations
from itertools import product
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=HERE/"p13_verifier_responsibility_cases_v1.json"
PROTOCOL=HERE/"P13_VERIFIER_RESPONSIBILITY_SHIFT_PROTOCOL_V1.md"

def base_cnf(case):
    clauses=[]
    for i,b in enumerate(case["old_model"]):
        if i==case["free_var"]: continue
        clauses.append([i+1 if b else -(i+1)])
    return clauses

def changed_cnf(case):
    clauses=base_cnf(case)
    f=case["free_var"]; old=case["old_model"][f]
    clauses.append([f+1 if old==0 else -(f+1)])
    return clauses

def sat(cnf,model):
    for clause in cnf:
        ok=False
        for lit in clause:
            v=abs(lit)-1; val=bool(model[v])
            if (lit>0 and val) or (lit<0 and not val): ok=True; break
        if not ok: return False
    return True

def solve(cnf,n):
    for bits in product((0,1), repeat=n):
        if sat(cnf,bits): return list(bits)
    return None

def raw_reads(cnf): return sum(len(c) for c in cnf)

def main():
    spec=json.loads(CASES.read_text()); rows=[]
    costs={"RCS":0,"ALWAYS_RAW":0,"CONFIDENCE_ONLY":0,"PROVENANCE_ONLY":0}
    correct={k:0 for k in costs}; stale={k:0 for k in costs}
    episodes=0
    for case in spec["cases"]:
        old=list(case["old_model"]); b=base_cnf(case); n=changed_cnf(case)
        assert sat(b,old); assert not sat(n,old)
        sats_old=[list(x) for x in product((0,1),repeat=case["n_vars"]) if sat(b,x)]
        sats_new=[list(x) for x in product((0,1),repeat=case["n_vars"]) if sat(n,x)]
        assert len(sats_old)==2 and len(sats_new)==1
        # Old responsibility: RCS reuses the independently verified certificate.
        for arm in costs:
            if arm=="ALWAYS_RAW": pred=solve(b,case["n_vars"]); costs[arm]+=raw_reads(b)
            else: pred=old
            correct[arm]+=int(pred is not None and sat(b,pred)); episodes+=1
        # New responsibility/epoch.
        for arm in costs:
            if arm in ("RCS","ALWAYS_RAW"):
                pred=solve(n,case["n_vars"]); costs[arm]+=raw_reads(n)
            else:
                pred=old; stale[arm]+=1
            correct[arm]+=int(pred is not None and sat(n,pred)); episodes+=1
        rows.append({"id":case["id"],"old_certificate_valid":True,"old_certificate_transport_after_change":False,"old_sat_count":2,"new_sat_count":1})
    per_arm_episodes=len(spec["cases"])*2
    reduction=1-(costs["RCS"]/costs["ALWAYS_RAW"])
    positive=(correct["RCS"]==correct["ALWAYS_RAW"]==per_arm_episodes and stale["RCS"]==0 and correct["CONFIDENCE_ONLY"]<per_arm_episodes and correct["PROVENANCE_ONLY"]<per_arm_episodes and costs["RCS"]<costs["ALWAYS_RAW"])
    receipt={"schema":"P13.VerifierResponsibilityShiftResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"cases_sha256":hashlib.sha256(CASES.read_bytes()).hexdigest(),"case_count":len(spec["cases"]),"episodes_per_arm":per_arm_episodes,"correct":correct,"stale_reuse":stale,"raw_literal_reads":costs,"rcs_raw_read_reduction":reduction,"rows":rows,"terminal":"P13_VERIFIER_RESPONSIBILITY_SHIFT_V1_SUPPORTED" if positive else "P13_VERIFIER_RESPONSIBILITY_SHIFT_V1_GATE_NOT_MET"}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode(); receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest(); print(json.dumps(receipt,indent=2,sort_keys=True)); assert positive,receipt; return 0
if __name__=="__main__": raise SystemExit(main())
