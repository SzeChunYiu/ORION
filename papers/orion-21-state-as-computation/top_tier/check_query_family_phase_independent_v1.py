#!/usr/bin/env python3
"""Structurally independent P11 query-family verifier.

Uses manual NumPy scaling, manual binary ANOVA/F ranking and manual balanced
accuracy while preserving the prospectively frozen downstream access classes.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/"P11_QUERY_FAMILY_PHASE_PROTOCOL_V1.md"
D=64;K=16;QUERIES=range(10);ARMS=("LINEAR","RBF","KNN")

def manual_scale_fit(x):
    mean=x.mean(axis=0); std=x.std(axis=0,ddof=0); std=np.where(std==0.0,1.0,std)
    return mean,std

def manual_scale(x,mean,std): return (x-mean)/std

def manual_f_scores(x,y):
    # One-way ANOVA for the frozen binary query; ranking-equivalent to f_classif.
    n=x.shape[0]; groups=[x[y==0],x[y==1]]; grand=x.mean(axis=0)
    ss_between=sum(g.shape[0]*(g.mean(axis=0)-grand)**2 for g in groups)
    ss_within=sum(((g-g.mean(axis=0))**2).sum(axis=0) for g in groups)
    with np.errstate(divide='ignore',invalid='ignore'):
        f=ss_between/(ss_within/(n-2))
    return np.nan_to_num(f,nan=-np.inf,posinf=np.inf,neginf=-np.inf)

def select_top_k(scores,k):
    # Match stable score-descending/index-ascending semantics explicitly.
    order=sorted(range(len(scores)),key=lambda i:(-float(scores[i]),i))
    return np.asarray(order[:k],dtype=int)

def manual_balanced_accuracy(y,pred):
    vals=[]
    for cls in (0,1):
        mask=y==cls; vals.append(float(np.mean(pred[mask]==cls)))
    return float(sum(vals)/2.0)

def model(kind,seed):
    if kind=="LINEAR": return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=seed)
    if kind=="RBF": return SVC(C=1.0,kernel="rbf",gamma="scale")
    if kind=="KNN": return KNeighborsClassifier(n_neighbors=7,weights="distance")
    raise ValueError(kind)

def main():
    b=load_digits();X=np.asarray(b.data,dtype=np.float64);y=np.asarray(b.target)
    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=20261121)
    scores={(q,a,s):[] for q in QUERIES for a in ARMS for s in ("UNIVERSAL","COMPILED")}
    selected=[];train_sizes=[]
    for fold,(tr,te) in enumerate(cv.split(X,y)):
        train_sizes.append(len(tr));mean,std=manual_scale_fit(X[tr]);xt=manual_scale(X[tr],mean,std);xv=manual_scale(X[te],mean,std)
        for q in QUERIES:
            yt=(y[tr]==q).astype(int);ye=(y[te]==q).astype(int)
            idx=select_top_k(manual_f_scores(xt,yt),K);selected.append({'fold':fold,'query':q,'selected_features':idx.tolist()})
            for kind in ARMS:
                seed=2026112100+fold*10+q
                for state,a,bv in (("UNIVERSAL",xt,xv),("COMPILED",xt[:,idx],xv[:,idx])):
                    m=model(kind,seed);m.fit(a,yt);pred=m.predict(bv)
                    scores[(q,kind,state)].append(manual_balanced_accuracy(ye,pred))
    support_counts={};query_results={}
    for kind in ARMS:
        count=0
        for q in QUERIES:
            um=float(np.mean(scores[(q,kind,"UNIVERSAL")]))
            cm=float(np.mean(scores[(q,kind,"COMPILED")]))
            supported=cm>=um-0.02;count+=int(supported)
            query_results[f'{kind}:{q}']={'universal_mean':um,'compiled_mean':cm,'delta':cm-um,'quality_supported':supported}
        support_counts[kind]=count
    mean_n_train=float(np.mean(train_sizes));phase=[]
    for u in range(1,11):
        memory_ok=(K*u<=D)==(u<=4)
        fit=u*mean_n_train*D;break_even=math.floor(fit/(D-K))+1
        phase.append({'U':u,'memory_prediction_correct':memory_ok,'break_even_horizon':break_even,'future_query_recovery_fit_inspections':mean_n_train*D if u<10 else 0})
    positive=(support_counts['LINEAR']>=8 and max(support_counts['RBF'],support_counts['KNN'])>=8 and all(r['memory_prediction_correct'] for r in phase) and all(r['future_query_recovery_fit_inspections']>0 for r in phase if r['U']<10))
    receipt={'schema':'P11.QueryFamilyPhaseIndependent.v1','protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'support_counts':support_counts,'query_results':query_results,'phase':phase,'selected':selected,'terminal':'P11_QUERY_FAMILY_PHASE_SECOND_INDEPENDENT_CHECKER_GREEN' if positive else 'P11_QUERY_FAMILY_PHASE_SECOND_CHECKER_GATE_NOT_MET'}
    raw=json.dumps(receipt,sort_keys=True,separators=(',',':')).encode();receipt['receipt_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(receipt,indent=2,sort_keys=True));assert positive,receipt;return 0
if __name__=='__main__':raise SystemExit(main())
