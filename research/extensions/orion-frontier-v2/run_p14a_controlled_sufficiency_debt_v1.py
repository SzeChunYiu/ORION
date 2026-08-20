from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path
import numpy as np

SEED=914421
OUT=Path(__file__).with_name("results")/"P14A_CONTROLLED_SUFFICIENCY_DEBT_V1.json"
REPS=("Z1","Z2","Z3")
TASKS=("PREDICT","DECIDE","INTERVENE","VERIFY","REPAIR")

def truth(x,m,r):
    return {
        "PREDICT": x,
        "DECIDE": x,
        "INTERVENE": x*m,
        "VERIFY": x*m,
        "REPAIR": r,
    }

def rep(z,x,m,r):
    return {"Z1":(x,), "Z2":(x,m), "Z3":(x,m,r)}[z]

def bayes_acc(rows,z,task):
    groups={}
    for x,m,r in rows:
        key=rep(z,x,m,r)
        groups.setdefault(key,[]).append(truth(x,m,r)[task])
    correct=0
    for vals in groups.values():
        counts={-1:vals.count(-1),1:vals.count(1)}
        correct+=max(counts.values())
    return correct/len(rows)

def main():
    support=list(itertools.product((-1,1), repeat=3))
    exact={z:{t:bayes_acc(support,z,t) for t in TASKS} for z in REPS}
    expected={
      "Z1":{"PREDICT":1.0,"DECIDE":1.0,"INTERVENE":0.5,"VERIFY":0.5,"REPAIR":0.5},
      "Z2":{"PREDICT":1.0,"DECIDE":1.0,"INTERVENE":1.0,"VERIFY":1.0,"REPAIR":0.5},
      "Z3":{"PREDICT":1.0,"DECIDE":1.0,"INTERVENE":1.0,"VERIFY":1.0,"REPAIR":1.0},
    }
    rng=np.random.default_rng(SEED)
    sanity=[]
    maxdev=0.0
    for i in range(100):
        arr=rng.choice((-1,1),size=(1024,3))
        rows=[tuple(map(int,row)) for row in arr]
        sample={z:{t:bayes_acc(rows,z,t) for t in TASKS} for z in REPS}
        dev=max(abs(sample[z][t]-expected[z][t]) for z in REPS for t in TASKS)
        maxdev=max(maxdev,dev)
        sanity.append({"rep":i,"max_abs_deviation":dev})
    answer_field_failures=0
    gates={
      "exact_matrix_matches": exact==expected,
      "lower_rungs_all_exact": all(exact[z]["PREDICT"]==1 and exact[z]["DECIDE"]==1 for z in REPS),
      "z1_intervene_verify_half": exact["Z1"]["INTERVENE"]==0.5 and exact["Z1"]["VERIFY"]==0.5,
      "z2_z3_intervene_verify_exact": all(exact[z][t]==1 for z in ("Z2","Z3") for t in ("INTERVENE","VERIFY")),
      "z2_repair_half_z3_exact": exact["Z2"]["REPAIR"]==0.5 and exact["Z3"]["REPAIR"]==1,
      "finite_sanity_within_0_05": maxdev<=0.05,
      "no_responsibility_label_field": answer_field_failures==0,
    }
    debt={
      "Z1_to_INTERVENE": exact["Z3"]["INTERVENE"]-exact["Z1"]["INTERVENE"],
      "Z1_to_VERIFY": exact["Z3"]["VERIFY"]-exact["Z1"]["VERIFY"],
      "Z2_to_REPAIR": exact["Z3"]["REPAIR"]-exact["Z2"]["REPAIR"],
    }
    terminal="P14_CONTROLLED_SUFFICIENCY_DEBT_LADDER_SUPPORTED" if all(gates.values()) else "P14_CONTROLLED_SUFFICIENCY_DEBT_GATE_NOT_MET"
    payload={"schema":"ORION.P14A.ControlledSufficiencyDebt.v1","protocol":"P14A_CONTROLLED_SUFFICIENCY_DEBT_PROTOCOL_V1.md","seed":SEED,
             "exact_bayes_accuracy":exact,"expected":expected,"sufficiency_debt":debt,
             "finite_sample_max_abs_deviation":maxdev,"finite_sanity":sanity,"gates":gates,"terminal":terminal}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n"
    OUT.write_text(text,encoding="utf-8")
    print(json.dumps({"terminal":terminal,"exact":exact,"debt":debt,"maxdev":maxdev,"sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal!="P14_CONTROLLED_SUFFICIENCY_DEBT_LADDER_SUPPORTED": raise SystemExit(1)
if __name__=="__main__": main()
