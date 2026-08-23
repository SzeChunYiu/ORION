#!/usr/bin/env python3
"""Execute the frozen P7 objective-change transport study."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/"P7_OBJECTIVE_CHANGE_PROTOCOL_V1.md"
OLD_ACC=0.95; NEW_MALIGNANT_RECALL=0.95

def facts(y,p):
    tp0=int(np.sum((y==0)&(p==0))); fn0=int(np.sum((y==0)&(p!=0)))
    correct=int(np.sum(y==p)); n=len(y); acc=correct/n; rec0=tp0/(tp0+fn0)
    return {'n':n,'correct':correct,'accuracy':acc,'malignant_tp':tp0,'malignant_fn':fn0,'malignant_recall':rec0}
def gold(kind,f):
    if kind=='ACCURACY_ONLY': return 'CANNOT_CHECK'
    return 'PRESERVE' if f['malignant_recall']>=NEW_MALIGNANT_RECALL else 'REOPEN'
def value_only(f): return 'PRESERVE' if f['accuracy']>=OLD_ACC else 'REOPEN'
def always_reopen(_f): return 'REOPEN'
def witness(kind,f): return gold(kind,f)
def score(cells,fn):
    correct=false_closure=unnecessary_reopen=cannot=0;rows=[]
    for c in cells:
        pred=fn(c['evidence_kind'],c['facts']) if fn is witness else fn(c['facts'])
        g=c['gold']; correct+=int(pred==g);false_closure+=int(pred=='PRESERVE' and g!='PRESERVE');unnecessary_reopen+=int(pred=='REOPEN' and g=='PRESERVE');cannot+=int(pred=='CANNOT_CHECK' and g=='CANNOT_CHECK');rows.append({'id':c['id'],'gold':g,'predicted':pred})
    return {'accuracy':correct/len(cells),'false_closure':false_closure,'unnecessary_reopen':unnecessary_reopen,'correct_cannot_check':cannot,'rows':rows}
def main():
    b=load_breast_cancer();X=np.asarray(b.data,float);y=np.asarray(b.target,int)
    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=20261217);cells=[];full_counts={'PRESERVE':0,'REOPEN':0};old_obligation_counts={'SATISFIED':0,'NOT_SATISFIED':0}
    for fold,(tr,te) in enumerate(cv.split(X,y)):
        sc=StandardScaler().fit(X[tr]);m=LogisticRegression(C=1.0,solver='lbfgs',max_iter=5000).fit(sc.transform(X[tr]),y[tr]);p=m.predict(sc.transform(X[te]));f=facts(y[te],p)
        old_obligation_counts['SATISFIED' if f['accuracy']>=OLD_ACC else 'NOT_SATISFIED']+=1
        for kind in ('FULL_CLASS_WITNESS','ACCURACY_ONLY'):
            exposed=dict(f) if kind=='FULL_CLASS_WITNESS' else {'n':f['n'],'correct':f['correct'],'accuracy':f['accuracy']}
            g=gold(kind,f);cells.append({'id':f'BC-{fold}-{kind}','fold':fold,'evidence_kind':kind,'facts':exposed,'gold':g})
            if kind=='FULL_CLASS_WITNESS': full_counts[g]+=1
    systems={'WITNESS_AWARE':score(cells,witness),'VALUE_ONLY':score(cells,value_only),'ALWAYS_REOPEN':score(cells,always_reopen)}
    positive=(len(cells)==10 and full_counts['PRESERVE']>0 and full_counts['REOPEN']>0 and systems['WITNESS_AWARE']['accuracy']==1.0 and systems['WITNESS_AWARE']['correct_cannot_check']==5 and systems['VALUE_ONLY']['false_closure']>0 and systems['ALWAYS_REOPEN']['unnecessary_reopen']>0)
    receipt={'schema':'P7.ObjectiveChangeTransportResult.v1','protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'case_count':len(cells),'old_obligation_counts':old_obligation_counts,'full_witness_counts':full_counts,'systems':systems,'cells':cells,'terminal':'P7_OBJECTIVE_CHANGE_TRANSPORT_V1_SUPPORTED' if positive else 'P7_OBJECTIVE_CHANGE_TRANSPORT_V1_GATE_NOT_MET'}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=='__main__':raise SystemExit(main())
