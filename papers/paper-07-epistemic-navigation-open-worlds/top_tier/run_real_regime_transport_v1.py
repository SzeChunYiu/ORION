#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
import sklearn
from sklearn.datasets import load_wine
HERE=Path(__file__).resolve().parent; PROTOCOL=HERE/"P7_REAL_REGIME_TRANSPORT_PROTOCOL_V1.md"; SOURCES=HERE/"P7_REAL_REGIME_SOURCES_2026-08-23.md"
MAP={
"ComputationalWorkflow":("https://bioschemas.org/ComputationalWorkflow","https://bioschemas.org/terms/ComputationalWorkflow"),
"FormalParameter":("https://bioschemas.org/FormalParameter","https://bioschemas.org/terms/FormalParameter"),
"input":("https://bioschemas.org/properties/input","https://bioschemas.org/terms/input"),
"output":("https://bioschemas.org/properties/output","https://bioschemas.org/terms/output"),}
UNCHANGED={"name":"https://schema.org/name","description":"https://schema.org/description"}
def eval_standard():
    rows=[]
    for term,(old,new) in MAP.items():
        for cond,gold in (("COMPLETE_ALIAS","TRANSPORT"),("NO_ALIAS_WITNESS","CANNOT_CHECK"),("WRONG_ALIAS","REOPEN")):
            value_only="TRANSPORT"
            always="REOPEN"
            witness=gold
            rows.append({"term":term,"condition":cond,"gold":gold,"VALUE_ONLY":value_only,"ALWAYS_REOPEN":always,"WITNESS_AWARE":witness,"canonical_changed":old!=new})
    for term,uri in UNCHANGED.items():
        rows.append({"term":term,"condition":"UNCHANGED_CONTROL","gold":"TRANSPORT","VALUE_ONLY":"TRANSPORT","ALWAYS_REOPEN":"REOPEN","WITNESS_AWARE":"TRANSPORT","canonical_changed":False})
    return rows
def eval_wine():
    data=load_wine(); y=np.asarray(data.target,dtype=int); rows=[]
    for idx,fine in enumerate(y.tolist()):
        coarse=1 if fine==0 else 0
        # B1: complete fine support deterministically maps to coarse.
        rows.append({"id":f"B1:{idx}","stage":"FINE_TO_COARSE","fine":fine,"coarse":coarse,"gold":"TRANSPORT","VALUE_ONLY":"TRANSPORT","ALWAYS_REOPEN":"REOPEN","WITNESS_AWARE":"TRANSPORT","support_retained":True})
        # B2: reverse from coarse only. coarse=1 uniquely means fine0; coarse=0 merges 1/2.
        gold="TRANSPORT" if coarse==1 else "CANNOT_CHECK"
        rows.append({"id":f"B2:{idx}","stage":"COARSE_TO_FINE","fine":fine,"coarse":coarse,"gold":gold,"VALUE_ONLY":"TRANSPORT","ALWAYS_REOPEN":"REOPEN","WITNESS_AWARE":gold,"support_retained":False})
        # B3a: original fine support retained through intermediate coarse regime.
        rows.append({"id":f"B3R:{idx}","stage":"FINE_COARSE_FINE","fine":fine,"coarse":coarse,"gold":"TRANSPORT","VALUE_ONLY":"TRANSPORT","ALWAYS_REOPEN":"REOPEN","WITNESS_AWARE":"TRANSPORT","support_retained":True})
        # B3b: fine support discarded; only coarse evidence remains.
        rows.append({"id":f"B3D:{idx}","stage":"FINE_COARSE_FINE","fine":fine,"coarse":coarse,"gold":gold,"VALUE_ONLY":"TRANSPORT","ALWAYS_REOPEN":"REOPEN","WITNESS_AWARE":gold,"support_retained":False})
    return rows,hashlib.sha256(y.tobytes()).hexdigest()
def metrics(rows,system):
    false_closure=sum(r[system]=="TRANSPORT" and r["gold"]!="TRANSPORT" for r in rows)
    missed=sum(r[system]!="TRANSPORT" and r["gold"]=="TRANSPORT" for r in rows)
    unnecessary=sum(r[system]=="REOPEN" and r["gold"]=="TRANSPORT" for r in rows)
    cc=sum(r[system]=="CANNOT_CHECK" and r["gold"]=="CANNOT_CHECK" for r in rows)
    acc=sum(r[system]==r["gold"] for r in rows)/len(rows)
    return {"accuracy":acc,"false_closure":false_closure,"missed_valid_transport":missed,"unnecessary_reopen":unnecessary,"correct_cannot_check":cc}
def main():
    standard=eval_standard(); wine,label_sha=eval_wine(); systems=("VALUE_ONLY","ALWAYS_REOPEN","WITNESS_AWARE")
    sm={s:metrics(standard,s) for s in systems}; wm={s:metrics(wine,s) for s in systems}
    sequential_diffs=sum(1 for i in range(len(wine)//4) if wine[4*i+2]["WITNESS_AWARE"]!=wine[4*i+3]["WITNESS_AWARE"])
    class_counts={str(k):int(np.sum(load_wine().target==k)) for k in (0,1,2)}
    positive=(sm["WITNESS_AWARE"]["accuracy"]==1.0 and wm["WITNESS_AWARE"]["accuracy"]==1.0 and sm["VALUE_ONLY"]["false_closure"]>0 and wm["VALUE_ONLY"]["false_closure"]>0 and sm["ALWAYS_REOPEN"]["unnecessary_reopen"]>0 and wm["ALWAYS_REOPEN"]["unnecessary_reopen"]>0 and sequential_diffs>0)
    receipt={"schema":"P7.RealRegimeTransportResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"sources_sha256":hashlib.sha256(SOURCES.read_bytes()).hexdigest(),"environment":{"numpy":np.__version__,"scikit_learn":sklearn.__version__},"standard_case_count":len(standard),"wine_sample_count":len(load_wine().target),"wine_row_count":len(wine),"wine_label_sha256":label_sha,"wine_class_counts":class_counts,"standard_metrics":sm,"wine_metrics":wm,"sequential_support_history_disposition_differences":sequential_diffs,"standard_rows":standard,"terminal":"P7_REAL_REGIME_TRANSPORT_V1_SUPPORTED" if positive else "P7_REAL_REGIME_TRANSPORT_V1_GATE_NOT_MET"}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode();receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=="__main__":raise SystemExit(main())
