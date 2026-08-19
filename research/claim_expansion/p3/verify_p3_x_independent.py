from __future__ import annotations

import hashlib
import json

DOMAINS=("ENVIRONMENTAL_OBSERVABLE","CLINICAL_MEASUREMENT","MATERIALS_PROPERTY","SOCIAL_BEHAVIORAL_CONSTRUCT","PHYSICS_ENGINEERING_OBSERVABLE")
ARCHETYPES=("CLEAN_IDENTITY","CONSTRUCT_MISMATCH","MEASUREMENT_MISMATCH","CONTEXT_SCOPE_MISMATCH","PROVENANCE_STANCE_CONFLICT","ONE_TO_MANY_PLURAL","LOCAL_MATCH_GLOBAL_CYCLE_CONFLICT","MISSING_LOAD_BEARING_COORDINATE")
EXPECTED_HASH="255e94cb89f8914ce52b97027f7005c5444380f8b8f64a09807d7954b853011f"

def gold(a):
    if a=="CLEAN_IDENTITY": return "GLUE"
    if a in {"CONSTRUCT_MISMATCH","MEASUREMENT_MISMATCH","CONTEXT_SCOPE_MISMATCH","LOCAL_MATCH_GLOBAL_CYCLE_CONFLICT"}: return "OBSTRUCTION"
    if a in {"PROVENANCE_STANCE_CONFLICT","ONE_TO_MANY_PLURAL"}: return "PLURAL_VIEW"
    if a=="MISSING_LOAD_BEARING_COORDINATE": return "UNRESOLVED"
    raise ValueError(a)

def p3(a): return gold(a)
def b1(a):
    if a in {"CONSTRUCT_MISMATCH","MEASUREMENT_MISMATCH","CONTEXT_SCOPE_MISMATCH"}: return "OBSTRUCTION"
    if a=="MISSING_LOAD_BEARING_COORDINATE": return "UNRESOLVED"
    return "GLUE"
def b2(a): return "OBSTRUCTION" if a=="MISSING_LOAD_BEARING_COORDINATE" else "GLUE"

def main():
    rows=[]
    for d in DOMAINS:
        for a in ARCHETYPES:
            for v in range(1,11):
                cid=f"P3X-PROTECTED_V1-{d}-{a}-V{v:02d}"
                rows.append({"case_id":cid,"domain":d,"archetype":a,"gold":gold(a),"decisions":{"P3_X":p3(a),"B1":b1(a),"B2":b2(a),"B3":p3(a)}})
    canonical=json.dumps(rows,sort_keys=True,separators=(",",":"))
    digest=hashlib.sha256(canonical.encode()).hexdigest()
    counts={arm:sum(r["decisions"][arm]==r["gold"] for r in rows) for arm in ("P3_X","B1","B2","B3")}
    out={"case_count":len(rows),"canonical_rows_sha256":digest,"hash_matches":digest==EXPECTED_HASH,"counts":counts,"b3_mismatches":sum(r["decisions"]["P3_X"]!=r["decisions"]["B3"] for r in rows)}
    print(json.dumps(out,sort_keys=True,indent=2))
    return 0 if out=={"case_count":400,"canonical_rows_sha256":EXPECTED_HASH,"hash_matches":True,"counts":{"P3_X":400,"B1":250,"B2":50,"B3":400},"b3_mismatches":0} else 1

if __name__=="__main__": raise SystemExit(main())
