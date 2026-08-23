#!/usr/bin/env python3
from __future__ import annotations
from collections import defaultdict
import hashlib,json
from pathlib import Path
import random
import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
HERE=Path(__file__).resolve().parent;PROTOCOL=HERE/"P9_CAUSAL_DIAGNOSTIC_PROTOCOL_V1.md"
COST={"INFORMATION":8.0,"ACCESSIBILITY":2.0,"COMPUTATION":12.0}

def logistic(seed=0):return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=seed)
def choose(qualities,target):
    good=[(COST[k],k) for k,v in qualities.items() if v>=target]
    return min(good)[1] if good else "CANNOT_CHECK"
def resource_model(m,dim,kind):
    if kind=="logistic": return {"representation_dim":dim,"parameter_count":int(m.coef_.size+m.intercept_.size),"support_vector_coordinate_count":0}
    return {"representation_dim":dim,"parameter_count":0,"support_vector_coordinate_count":int(m.support_vectors_.size)}
def digits_tasks():
    b=load_digits();X=np.asarray(b.data,dtype=np.float64);y=np.asarray(b.target,dtype=int)
    Xtr,Xrem,ytr,yrem=train_test_split(X,y,test_size=0.4,random_state=20260901,stratify=y)
    Xpr,Xte,ypr,yte=train_test_split(Xrem,yrem,test_size=0.5,random_state=20260902,stratify=yrem)
    sc=StandardScaler().fit(Xtr); ntr=sc.transform(Xtr); npr=sc.transform(Xpr); nte=sc.transform(Xte)
    out=[]
    # D-A accessibility: cubic bijection.
    ctr,cpr,cte=ntr**3,npr**3,nte**3
    base=logistic(901);base.fit(ctr,ytr)
    access=logistic(902);access.fit(np.cbrt(ctr),ytr)
    comp=SVC(C=1.0,kernel="rbf",gamma="scale");comp.fit(ctr,ytr)
    qa_probe={"INFORMATION":accuracy_score(ypr,base.predict(cpr)),"ACCESSIBILITY":accuracy_score(ypr,access.predict(np.cbrt(cpr))),"COMPUTATION":accuracy_score(ypr,comp.predict(cpr))}
    qa_test={"INFORMATION":accuracy_score(yte,base.predict(cte)),"ACCESSIBILITY":accuracy_score(yte,access.predict(np.cbrt(cte))),"COMPUTATION":accuracy_score(yte,comp.predict(cte))}
    out.append({"task":"D-A","domain":"digits","target":0.965,"base_probe":qa_probe["INFORMATION"],"base_protected":qa_test["INFORMATION"],"probe":qa_probe,"protected":qa_test,"resource":{"INFORMATION":resource_model(base,64,"logistic"),"ACCESSIBILITY":{**resource_model(access,64,"logistic"),"transform_touches_per_example":64},"COMPUTATION":resource_model(comp,64,"svc")}})
    # D-I information: one scalar intensity.
    sums_tr=Xtr.sum(axis=1).reshape(-1,1);sums_pr=Xpr.sum(axis=1).reshape(-1,1);sums_te=Xte.sum(axis=1).reshape(-1,1)
    ss=StandardScaler().fit(sums_tr);str_=ss.transform(sums_tr);spr=ss.transform(sums_pr);ste=ss.transform(sums_te)
    base2=logistic(903);base2.fit(str_,ytr)
    info=logistic(904);info.fit(ntr,ytr)
    acc2=logistic(905);acc2.fit(np.arcsinh(str_),ytr)
    comp2=SVC(C=1.0,kernel="rbf",gamma="scale");comp2.fit(str_,ytr)
    qi_probe={"INFORMATION":accuracy_score(ypr,info.predict(npr)),"ACCESSIBILITY":accuracy_score(ypr,acc2.predict(np.arcsinh(spr))),"COMPUTATION":accuracy_score(ypr,comp2.predict(spr))}
    qi_test={"INFORMATION":accuracy_score(yte,info.predict(nte)),"ACCESSIBILITY":accuracy_score(yte,acc2.predict(np.arcsinh(ste))),"COMPUTATION":accuracy_score(yte,comp2.predict(ste))}
    basep=accuracy_score(ypr,base2.predict(spr));baset=accuracy_score(yte,base2.predict(ste))
    out.append({"task":"D-I","domain":"digits","target":0.95,"base_probe":basep,"base_protected":baset,"probe":qi_probe,"protected":qi_test,"resource":{"INFORMATION":resource_model(info,64,"logistic"),"ACCESSIBILITY":{**resource_model(acc2,1,"logistic"),"transform_touches_per_example":1},"COMPUTATION":resource_model(comp2,1,"svc")}})
    return out,{"train":len(ytr),"probe":len(ypr),"protected":len(yte),"label_sha256":hashlib.sha256(y.tobytes()).hexdigest()}
def parity(bits):return sum(bits)%2
def exec_quality(task,seeds):
    if task=="B-I":
        rows=[]
        for seed in seeds:
            r=random.Random(seed);bits=[r.randrange(2) for _ in range(4)];gold=parity(bits);guess=parity(bits[:3])
            rows.append((gold,gold,guess,guess))
        # tuple: gold, info, access, compute
        return {"INFORMATION":sum(g==i for g,i,a,c in rows)/len(rows),"ACCESSIBILITY":sum(g==a for g,i,a,c in rows)/len(rows),"COMPUTATION":sum(g==c for g,i,a,c in rows)/len(rows)}, {"semantic_information_bits":{"base":3,"INFORMATION":4,"ACCESSIBILITY":3,"COMPUTATION":3},"operation_count":{"INFORMATION":4,"ACCESSIBILITY":3,"COMPUTATION":8}}
    if task=="B-A":
        rows=[]
        for seed in seeds:
            r=random.Random(seed);a,b=r.randrange(2),r.randrange(2);z=a^b
            base=z # fixed single-coordinate readout
            info=base;access=b;comp=a^z
            rows.append((b,info,access,comp))
        return {"INFORMATION":sum(g==i for g,i,a,c in rows)/len(rows),"ACCESSIBILITY":sum(g==a for g,i,a,c in rows)/len(rows),"COMPUTATION":sum(g==c for g,i,a,c in rows)/len(rows)}, {"representation_bits":2,"operation_count":{"INFORMATION":0,"ACCESSIBILITY":1,"COMPUTATION":1}}
    if task=="B-C":
        rows=[]
        for seed in seeds:
            r=random.Random(seed);x=r.randint(-5,5);maps=[(r.choice((-2,-1,1,2)),r.randint(-3,3)) for _ in range(3)]
            v=x
            for s,o in maps:v=s*v+o
            gold=v;simple=maps[-1][0]*x+maps[-1][1]
            # info/access leave the frozen simple readout unchanged; compute composes.
            rows.append((gold,simple,simple,gold))
        return {"INFORMATION":sum(g==i for g,i,a,c in rows)/len(rows),"ACCESSIBILITY":sum(g==a for g,i,a,c in rows)/len(rows),"COMPUTATION":sum(g==c for g,i,a,c in rows)/len(rows)}, {"local_map_count":3,"operation_count":{"INFORMATION":0,"ACCESSIBILITY":0,"COMPUTATION":7}}
    raise ValueError(task)
def executable_tasks():
    out=[]
    for task,target in (("B-I",1.0),("B-A",1.0),("B-C",1.0)):
        probe,res=exec_quality(task,range(9100,9200));protected,_=exec_quality(task,range(9900,10000))
        out.append({"task":task,"domain":"executable","target":target,"base_probe":None,"base_protected":None,"probe":probe,"protected":protected,"resource":res})
    return out
def main():
    tasks,split=digits_tasks();tasks+=executable_tasks();rows=[]
    for t in tasks:
        pred=choose(t["probe"],t["target"]);gold=choose(t["protected"],t["target"]);generic="COMPUTATION" if (t["base_probe"] is None or t["base_probe"]<t["target"]) else "NO_INTERVENTION"
        predq=None if pred=="CANNOT_CHECK" else t["protected"][pred];goldcost=None if gold=="CANNOT_CHECK" else COST[gold];predcost=None if pred=="CANNOT_CHECK" else COST[pred]
        rows.append({**t,"predicted":pred,"protected_gold":gold,"diagnosis_correct":pred==gold,"generic_prediction":generic,"generic_correct":generic==gold,"false_compute_escalation":pred=="COMPUTATION" and gold!="COMPUTATION","generic_false_compute_escalation":generic=="COMPUTATION" and gold!="COMPUTATION","predicted_protected_quality":predq,"cost_regret":0.0 if gold=="CANNOT_CHECK" or pred=="CANNOT_CHECK" else predcost-goldcost})
    acc=sum(r["diagnosis_correct"] for r in rows)/len(rows);gacc=sum(r["generic_correct"] for r in rows)/len(rows);ex=[r for r in rows if r["domain"]=="executable"];dig=[r for r in rows if r["domain"]=="digits"]
    false=sum(r["false_compute_escalation"] for r in rows);gfalse=sum(r["generic_false_compute_escalation"] for r in rows);mean_regret=sum(r["cost_regret"] for r in rows)/len(rows)
    target_ok=all(r["protected_gold"]=="CANNOT_CHECK" or (r["predicted_protected_quality"] is not None and r["predicted_protected_quality"]>=r["target"]) for r in rows)
    positive=(sum(r["diagnosis_correct"] for r in rows)>=4 and acc>gacc and all(r["diagnosis_correct"] for r in ex) and any(r["diagnosis_correct"] for r in dig) and false*2<=gfalse and target_ok and mean_regret<=1.0)
    receipt={"schema":"P9.CausalDiagnosticResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"environment":{"numpy":np.__version__,"scikit_learn":sklearn.__version__},"digits_split":split,"task_count":len(rows),"diagnosis_accuracy":acc,"generic_accuracy":gacc,"executable_accuracy":sum(r["diagnosis_correct"] for r in ex)/len(ex),"digits_accuracy":sum(r["diagnosis_correct"] for r in dig)/len(dig),"false_compute_escalation":false,"generic_false_compute_escalation":gfalse,"mean_registered_cost_regret":mean_regret,"protected_target_reached_by_prediction":target_ok,"rows":rows,"terminal":"P9_CAUSAL_DIAGNOSTIC_V1_SUPPORTED" if positive else "P9_CAUSAL_DIAGNOSTIC_V1_GATE_NOT_MET"}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode();receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=="__main__":raise SystemExit(main())
