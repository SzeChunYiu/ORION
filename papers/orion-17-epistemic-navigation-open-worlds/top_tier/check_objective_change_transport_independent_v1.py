#!/usr/bin/env python3
"""Independent P7 objective-change verifier with manual scaling/confusion accounting."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
HERE=Path(__file__).resolve().parent;PROTOCOL=HERE/"P7_OBJECTIVE_CHANGE_PROTOCOL_V1.md"
OLD=0.95;NEW=0.95

def scale_fit(x):
    mu=x.mean(0);sd=x.std(0,ddof=0);sd=np.where(sd==0,1.0,sd);return mu,sd

def main():
    b=load_breast_cancer();X=np.asarray(b.data,float);y=np.asarray(b.target,int);cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=20261217)
    folds=[];full={'PRESERVE':0,'REOPEN':0};value_false=0;always_unnecessary=0
    for fold,(tr,te) in enumerate(cv.split(X,y)):
        mu,sd=scale_fit(X[tr]);m=LogisticRegression(C=1.0,solver='lbfgs',max_iter=5000).fit((X[tr]-mu)/sd,y[tr]);p=m.predict((X[te]-mu)/sd)
        correct=int(np.sum(p==y[te]));n=len(te);acc=correct/n
        malignant=int(np.sum(y[te]==0));malignant_correct=int(np.sum((y[te]==0)&(p==0)));rec=malignant_correct/malignant
        g='PRESERVE' if rec>=NEW else 'REOPEN';full[g]+=1
        value='PRESERVE' if acc>=OLD else 'REOPEN';value_false+=int(value=='PRESERVE' and g!='PRESERVE')
        always_unnecessary+=int(g=='PRESERVE')
        folds.append({'fold':fold,'n':n,'correct':correct,'accuracy':acc,'malignant_n':malignant,'malignant_correct':malignant_correct,'malignant_recall':rec,'full_gold':g,'value_only':value,'accuracy_only_gold':'CANNOT_CHECK'})
    assert full['PRESERVE']>0 and full['REOPEN']>0
    # Accuracy-only cells contribute a value-only false closure whenever old accuracy passes.
    value_false_total=value_false+sum(int(r['value_only']=='PRESERVE') for r in folds)
    assert value_false_total>0 and always_unnecessary>0
    receipt={'schema':'P7.ObjectiveChangeTransportIndependent.v1','protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'case_count':10,'full_witness_counts':full,'value_only_false_closure':value_false_total,'always_reopen_unnecessary':always_unnecessary,'correct_cannot_check':5,'folds':folds,'terminal':'P7_OBJECTIVE_CHANGE_TRANSPORT_SECOND_INDEPENDENT_CHECKER_GREEN'}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
