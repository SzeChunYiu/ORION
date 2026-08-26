#!/usr/bin/env python3
"""Build the frozen post-outcome P9 I/A/C/M resource ledger."""
from __future__ import annotations
import hashlib,json,random
from pathlib import Path
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/"P9_UNIFIED_RESOURCE_LEDGER_PROTOCOL_V1.md"
SOURCE=HERE/"P9_CAUSAL_DIAGNOSTIC_RESULT_RECEIPT_V1.md"
COST={"INFORMATION":8.0,"ACCESSIBILITY":2.0,"COMPUTATION":12.0}
DECISIONS={
    "D-A":("ACCESSIBILITY","CANNOT_CHECK"),
    "D-I":("INFORMATION","INFORMATION"),
    "B-I":("INFORMATION","INFORMATION"),
    "B-A":("ACCESSIBILITY","ACCESSIBILITY"),
    "B-C":("COMPUTATION","COMPUTATION"),
}

def logistic(seed):return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=seed)
def row(task,intervention,**v):
    required=("I_sem","A_dim","A_transform","M_state","C_fit","C_infer","C_explicit")
    assert all(k in v for k in required)
    return {"task":task,"intervention":intervention,**v,"R_registered":COST[intervention]}

def digits_rows():
    b=load_digits();X=np.asarray(b.data,dtype=np.float64);y=np.asarray(b.target,dtype=int)
    Xtr,Xrem,ytr,yrem=train_test_split(X,y,test_size=0.4,random_state=20260901,stratify=y)
    Xpr,Xte,ypr,yte=train_test_split(Xrem,yrem,test_size=0.5,random_state=20260902,stratify=yrem)
    sc=StandardScaler().fit(Xtr);ntr=sc.transform(Xtr)
    ctr=ntr**3
    m_da_i=logistic(901);m_da_i.fit(ctr,ytr)
    m_da_a=logistic(902);m_da_a.fit(np.cbrt(ctr),ytr)
    m_da_c=SVC(C=1.0,kernel="rbf",gamma="scale");m_da_c.fit(ctr,ytr)
    sums=Xtr.sum(axis=1).reshape(-1,1);ss=StandardScaler().fit(sums);s=ss.transform(sums)
    m_di_i=logistic(904);m_di_i.fit(ntr,ytr)
    m_di_a=logistic(905);m_di_a.fit(np.arcsinh(s),ytr)
    m_di_c=SVC(C=1.0,kernel="rbf",gamma="scale");m_di_c.fit(s,ytr)
    n=len(ytr)
    rows=[
        row("D-A","INFORMATION",I_sem=64,A_dim=64,A_transform=0,M_state=int(m_da_i.coef_.size+m_da_i.intercept_.size),C_fit=n*64,C_infer=64,C_explicit=0),
        row("D-A","ACCESSIBILITY",I_sem=64,A_dim=64,A_transform=64,M_state=int(m_da_a.coef_.size+m_da_a.intercept_.size),C_fit=n*64,C_infer=64,C_explicit=0),
        row("D-A","COMPUTATION",I_sem=64,A_dim=64,A_transform=0,M_state=int(m_da_c.support_vectors_.size),C_fit=n*64,C_infer=int(m_da_c.support_vectors_.size),C_explicit=0),
        row("D-I","INFORMATION",I_sem=64,A_dim=64,A_transform=0,M_state=int(m_di_i.coef_.size+m_di_i.intercept_.size),C_fit=n*64,C_infer=64,C_explicit=0),
        row("D-I","ACCESSIBILITY",I_sem=1,A_dim=1,A_transform=1,M_state=int(m_di_a.coef_.size+m_di_a.intercept_.size),C_fit=n,C_infer=1,C_explicit=0),
        row("D-I","COMPUTATION",I_sem=1,A_dim=1,A_transform=0,M_state=int(m_di_c.support_vectors_.size),C_fit=n,C_infer=int(m_di_c.support_vectors_.size),C_explicit=0),
    ]
    return rows,{"train":len(ytr),"probe":len(ypr),"protected":len(yte)}

def exact_rows():
    return [
        row("B-I","INFORMATION",I_sem=4,A_dim=4,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=4),
        row("B-I","ACCESSIBILITY",I_sem=3,A_dim=3,A_transform=3,M_state=0,C_fit=0,C_infer=0,C_explicit=3),
        row("B-I","COMPUTATION",I_sem=3,A_dim=3,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=8),
        row("B-A","INFORMATION",I_sem=2,A_dim=2,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=0),
        row("B-A","ACCESSIBILITY",I_sem=2,A_dim=2,A_transform=1,M_state=0,C_fit=0,C_infer=0,C_explicit=0),
        row("B-A","COMPUTATION",I_sem=2,A_dim=2,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=1),
        row("B-C","INFORMATION",I_sem=7,A_dim=7,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=0),
        row("B-C","ACCESSIBILITY",I_sem=7,A_dim=7,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=0),
        row("B-C","COMPUTATION",I_sem=7,A_dim=7,A_transform=0,M_state=0,C_fit=0,C_infer=0,C_explicit=7),
    ]

def main():
    text=SOURCE.read_text()
    for token in ("diagnostic accuracy: `0.8`","generic `UNCERTAINTY_ESCALATE_COMPUTE` accuracy: `0.2`","protected causal gold is therefore `CANNOT_CHECK`"):
        assert token in text,token
    rows,split=digits_rows();rows+=exact_rows()
    assert len(rows)==15 and {(r['task'],r['intervention']) for r in rows}=={(t,i) for t in DECISIONS for i in COST}
    by={(r['task'],r['intervention']):r for r in rows}
    # Frozen information-preservation relations.
    for task in DECISIONS:
        base_i=by[(task,"COMPUTATION")]["I_sem"]
        assert by[(task,"ACCESSIBILITY")]["I_sem"]==base_i
        assert by[(task,"COMPUTATION")]["I_sem"]==base_i
    assert by[("D-I","INFORMATION")]["I_sem"]>by[("D-I","COMPUTATION")]["I_sem"]
    assert by[("B-I","INFORMATION")]["I_sem"]>by[("B-I","COMPUTATION")]["I_sem"]
    assert all(r['C_fit']>0 and r['M_state']>0 for r in rows if r['task'].startswith('D-'))
    assert by[("B-I","COMPUTATION")]['C_explicit']>0 and by[("B-A","COMPUTATION")]['C_explicit']>0 and by[("B-C","COMPUTATION")]['C_explicit']>0
    receipt={"schema":"P9.UnifiedResourceLedger.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"source_receipt_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),"digits_split":split,"decisions":{k:{"predicted":v[0],"protected_gold":v[1]} for k,v in DECISIONS.items()},"row_count":len(rows),"rows":rows,"scalarization":"PROHIBITED","terminal":"P9_UNIFIED_RESOURCE_LEDGER_V1_GREEN"}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
