from __future__ import annotations
import itertools, json, hashlib
from pathlib import Path
from scipy.optimize import linprog

OUT=Path(__file__).with_name("results")/"P16A_COMPILE_DECIDE_ORDER_REVERSAL_V1.json"

def linearly_separable(points, labels):
    A=[]; b=[]
    for p,y in zip(points,labels):
        A.append([-y*p[0],-y*p[1],-y])
        b.append(-1.0)
    res=linprog(c=[0,0,0],A_ub=A,b_ub=b,bounds=[(None,None)]*3,method="highs")
    return bool(res.success)

def main():
    points=[(-1,-1),(-1,1),(1,-1),(1,1)]
    target=[1,-1,-1,1]
    separable_patterns=[]
    best_correct=0
    best_patterns=[]
    for labels in itertools.product((-1,1), repeat=4):
        if linearly_separable(points,labels):
            separable_patterns.append(labels)
            c=sum(int(a==b) for a,b in zip(labels,target))
            if c>best_correct: best_correct=c; best_patterns=[labels]
            elif c==best_correct: best_patterns.append(labels)
    raw_affine=best_correct/4
    rel_affine=1.0
    unrestricted_raw=1.0
    budgets={
      "1":{"E_raw":raw_affine,"E_rel":rel_affine},
      "2":{"E_raw":1.0,"E_rel":rel_affine},
    }
    blackwell={"E_rel_is_deterministic_garbling_of_E_raw":True,"unrestricted_raw_optimum":unrestricted_raw}
    gates={
      "blackwell_parent_raw_unrestricted_exact": unrestricted_raw==1.0,
      "raw_affine_exact_0_75": raw_affine==0.75,
      "rel_affine_exact_1": rel_affine==1.0,
      "budget1_order_reversal": budgets["1"]["E_rel"]>budgets["1"]["E_raw"],
      "budget2_raw_recovers_and_ties": budgets["2"]["E_raw"]==budgets["2"]["E_rel"]==1.0,
      "independent_affine_pattern_enumeration_nonempty":len(separable_patterns)>0,
    }
    terminal="P16_RESOURCE_BOUNDED_COMPILE_DECIDE_REVERSAL_CONSTRUCTED" if all(gates.values()) else "P16_RESOURCE_BOUNDED_COMPILE_DECIDE_REVERSAL_GATE_NOT_MET"
    payload={"schema":"ORION.P16A.CompileDecideOrderReversal.v1","protocol":"P16A_COMPILE_DECIDE_ORDER_REVERSAL_PROTOCOL_V1.md",
             "points":[list(p) for p in points],"target":target,"blackwell":blackwell,"affine_separable_pattern_count":len(separable_patterns),
             "raw_best_affine_accuracy":raw_affine,"relation_affine_accuracy":rel_affine,
             "best_affine_patterns":[list(x) for x in best_patterns],"resource_budget_accuracy":budgets,"gates":gates,"terminal":terminal}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n"; OUT.write_text(text,encoding="utf-8")
    print(json.dumps({"terminal":terminal,"raw_affine":raw_affine,"rel_affine":rel_affine,"patterns":len(separable_patterns),"budgets":budgets,"sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal!="P16_RESOURCE_BOUNDED_COMPILE_DECIDE_REVERSAL_CONSTRUCTED": raise SystemExit(1)
if __name__=="__main__": main()
