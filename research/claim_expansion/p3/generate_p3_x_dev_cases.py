from __future__ import annotations

import hashlib
import json
import sys

DOMAINS=("ENVIRONMENTAL_OBSERVABLE","CLINICAL_MEASUREMENT","MATERIALS_PROPERTY","SOCIAL_BEHAVIORAL_CONSTRUCT","PHYSICS_ENGINEERING_OBSERVABLE")
ARCHETYPES=("CLEAN_IDENTITY","CONSTRUCT_MISMATCH","MEASUREMENT_MISMATCH","CONTEXT_SCOPE_MISMATCH","PROVENANCE_STANCE_CONFLICT","ONE_TO_MANY_PLURAL","LOCAL_MATCH_GLOBAL_CYCLE_CONFLICT","MISSING_LOAD_BEARING_COORDINATE")

def h(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()

def build(domain:str, archetype:str, variant:int, authority:str="NON_AUTHORIZING_DEV"):
    cid=f"P3X-{authority}-{domain}-{archetype}-V{variant:02d}"
    x={"construct_equal":True,"measurement_equal":True,"context_equal":True,"provenance_stance_compatible":True,"plural_mapping":False,"global_cycle_consistent":True,"load_bearing_complete":True,"local_match_score":0.97}
    gold="GLUE"
    if archetype=="CONSTRUCT_MISMATCH": x["construct_equal"]=False; gold="OBSTRUCTION"
    elif archetype=="MEASUREMENT_MISMATCH": x["measurement_equal"]=False; gold="OBSTRUCTION"
    elif archetype=="CONTEXT_SCOPE_MISMATCH": x["context_equal"]=False; gold="OBSTRUCTION"
    elif archetype=="PROVENANCE_STANCE_CONFLICT": x["provenance_stance_compatible"]=False; gold="PLURAL_VIEW"
    elif archetype=="ONE_TO_MANY_PLURAL": x["plural_mapping"]=True; gold="PLURAL_VIEW"
    elif archetype=="LOCAL_MATCH_GLOBAL_CYCLE_CONFLICT": x["global_cycle_consistent"]=False; gold="OBSTRUCTION"
    elif archetype=="MISSING_LOAD_BEARING_COORDINATE": x["load_bearing_complete"]=False; x["local_match_score"]=0.83; gold="UNRESOLVED"
    return {"case_id":cid,"domain":domain,"archetype":archetype,"candidate_visible":x,"protected_gold":{"terminal":gold,"commitment":h(cid+":gold")},"seed_commitment":h(cid+":seed")}

def generate(n_variants:int=5, authority:str="NON_AUTHORIZING_DEV"):
    return [build(d,a,v,authority) for d in DOMAINS for a in ARCHETYPES for v in range(1,n_variants+1)]

def main():
    cases=generate(); json.dump({"authority":"NON_AUTHORIZING_DEV","case_count":len(cases),"cases":cases},sys.stdout,sort_keys=True,indent=2); print(); return 0
if __name__=="__main__": raise SystemExit(main())
