#!/usr/bin/env python3
"""Execute the prospectively frozen P11 query-family phase study V1."""
from __future__ import annotations
from collections import defaultdict
import hashlib, json, math
from pathlib import Path
import numpy as np
import sklearn
from sklearn.datasets import load_digits
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/"P11_QUERY_FAMILY_PHASE_PROTOCOL_V1.md"
D=64; K=16; QUERIES=list(range(10)); U_GRID=list(range(1,11)); H_GRID=[100,500,1000,2500,5000,10000,25000]
ARMS=("LINEAR","RBF","KNN")

def model(kind,seed):
    if kind=="LINEAR": return LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=seed)
    if kind=="RBF": return SVC(C=1.0,kernel="rbf",gamma="scale")
    if kind=="KNN": return KNeighborsClassifier(n_neighbors=7,weights="distance")
    raise ValueError(kind)

def resource(m,kind,dim,n_train):
    if kind=="LINEAR":
        return {"coefficient_count":int(m.coef_.size+m.intercept_.size),"prediction_feature_touches":dim}
    if kind=="RBF":
        sv=int(m.support_vectors_.shape[0]); coords=int(m.support_vectors_.size)
        return {"support_vector_count":sv,"support_vector_coordinate_count":coords,"prediction_feature_touches":coords}
    stored=int(n_train*dim)
    return {"stored_training_vector_coordinate_count":stored,"prediction_feature_touches":dim}

def main():
    bunch=load_digits(); X=np.asarray(bunch.data,dtype=np.float64); y=np.asarray(bunch.target)
    cv=StratifiedKFold(n_splits=5,shuffle=True,random_state=20261121)
    rows=[]; selections=[]; train_sizes=[]; test_sizes=[]
    for fold,(tr,te) in enumerate(cv.split(X,y)):
        train_sizes.append(len(tr)); test_sizes.append(len(te))
        scaler=StandardScaler().fit(X[tr]); xf_tr=scaler.transform(X[tr]); xf_te=scaler.transform(X[te])
        for q in QUERIES:
            yt=(y[tr]==q).astype(int); ye=(y[te]==q).astype(int)
            comp=SelectKBest(score_func=f_classif,k=K).fit(xf_tr,yt)
            sel=np.flatnonzero(comp.get_support()).tolist(); assert len(sel)==K
            xc_tr=comp.transform(xf_tr); xc_te=comp.transform(xf_te)
            selections.append({"fold":fold,"query":q,"selected_features":sel,"compiler_fit_inspections":int(len(tr)*D),"compiler_transform_inspections_test":int(len(te)*D)})
            for kind in ARMS:
                seed=2026112100+fold*10+q
                for state,xt,xv in (("UNIVERSAL",xf_tr,xf_te),("COMPILED",xc_tr,xc_te)):
                    m=model(kind,seed); m.fit(xt,yt); pred=m.predict(xv)
                    rows.append({"fold":fold,"query":q,"access":kind,"state":state,"balanced_accuracy":float(balanced_accuracy_score(ye,pred)),"state_dimension":int(xt.shape[1]),"resource":resource(m,kind,int(xt.shape[1]),len(tr))})
    by=defaultdict(list)
    for r in rows: by[(r["query"],r["access"],r["state"])].append(r)
    support_counts={}; query_results={}
    for kind in ARMS:
        n=0
        for q in QUERIES:
            u=[r["balanced_accuracy"] for r in by[(q,kind,"UNIVERSAL")]]; c=[r["balanced_accuracy"] for r in by[(q,kind,"COMPILED")]]
            um=float(np.mean(u)); cm=float(np.mean(c)); supported=cm>=um-0.02; n+=int(supported)
            query_results[f"{kind}:{q}"]={"universal_mean":um,"compiled_mean":cm,"delta":cm-um,"quality_supported":supported}
        support_counts[kind]=n
    mean_n_train=float(np.mean(train_sizes))
    phases=[]
    for u in U_GRID:
        mem_comp=K*u; mem_uni=D; mem_pred=(mem_comp<=mem_uni)==(u<=4); assert mem_pred
        fit=u*mean_n_train*D
        service_saving=D-K
        break_even=math.floor(fit/service_saving)+1
        for h in H_GRID:
            comp_touch=fit+h*K; uni_touch=h*D
            phases.append({"U":u,"H":h,"universal_state_floats":mem_uni,"compile_cache_state_floats":mem_comp,"memory_prediction_correct":True,"compiler_fit_inspections":fit,"linear_universal_service_touches":h*D,"linear_compiled_total_touches":comp_touch,"compiled_less_total_touches":comp_touch<uni_touch,"break_even_horizon":break_even,"future_query_recovery_fit_inspections":mean_n_train*D if u<10 else 0,"universal_state_reconstruction_cost":0})
    positive=(support_counts["LINEAR"]>=8 and max(support_counts["RBF"],support_counts["KNN"])>=8 and all(p["memory_prediction_correct"] for p in phases) and all(p["future_query_recovery_fit_inspections"]>0 for p in phases if p["U"]<10))
    receipt={"schema":"P11.QueryFamilyPhaseResult.v1","protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"environment":{"numpy":np.__version__,"scikit_learn":sklearn.__version__},"dataset":"digits","row_count":len(rows),"query_count":10,"support_counts":support_counts,"query_results":query_results,"mean_train_size":mean_n_train,"phase_rows":phases,"selections":selections,"terminal":"P11_QUERY_FAMILY_PHASE_V1_SUPPORTED" if positive else "P11_QUERY_FAMILY_PHASE_V1_GATE_NOT_MET","rows":rows}
    raw=json.dumps(receipt,sort_keys=True,separators=(",", ":")).encode(); receipt["receipt_sha256"]=hashlib.sha256(raw).hexdigest(); print(json.dumps(receipt,indent=2,sort_keys=True)); assert positive,receipt; return 0
if __name__=="__main__": raise SystemExit(main())
