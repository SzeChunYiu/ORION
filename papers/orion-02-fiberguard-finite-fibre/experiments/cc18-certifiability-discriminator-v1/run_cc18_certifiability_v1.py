#!/usr/bin/env python3
"""ORION-02 CC18 certifiability discriminator. Protocol cc18-certifiability-discriminator-v1."""
from __future__ import annotations
import json, os, sys, warnings
import numpy as np
warnings.filterwarnings("ignore")

SEED=20260830; K=4; GATE=0.90
STRATA={"binary_small":[31,37,44],"binary_wide":[1462,1471,1494],
        "multiclass_small":[11,54,187],"multiclass_wide":[14,16,18]}

def load(did):
    from sklearn.datasets import fetch_openml
    d=fetch_openml(data_id=did, as_frame=True, parser="auto")
    X=d.data.select_dtypes(include=[np.number])
    if X.shape[1]==0: return None
    X=X.fillna(X.median(numeric_only=True)).to_numpy(dtype=float)
    y=np.asarray(d.target)
    if X.shape[0]<80 or len(np.unique(y))<2: return None
    return X,y,d.details.get("name",str(did))

def split(X,y):
    from sklearn.model_selection import train_test_split
    return train_test_split(X,y,test_size=0.5,random_state=SEED,stratify=y)

def fibres_coarse(Xc,yc,Xt): return np.zeros(len(Xc),int), np.zeros(len(Xt),int)
def fibres_theorem(Xc,yc,Xt):
    from sklearn.feature_selection import mutual_info_classif
    mi=mutual_info_classif(Xc,yc,random_state=SEED)
    j=int(np.argmax(mi))
    qs=np.quantile(Xc[:,j], np.linspace(0,1,K+1)[1:-1])
    return np.digitize(Xc[:,j],qs), np.digitize(Xt[:,j],qs)
def fibres_distance(Xc,yc,Xt):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    s=StandardScaler().fit(Xc)
    km=KMeans(n_clusters=K,random_state=SEED,n_init=10).fit(s.transform(Xc))
    return km.labels_, km.predict(s.transform(Xt))
def fibres_learned(Xc,yc,Xt):
    from sklearn.tree import DecisionTreeClassifier
    t=DecisionTreeClassifier(max_depth=2,random_state=SEED).fit(Xc,yc)
    return t.apply(Xc), t.apply(Xt)
def fibres_oracle(Xc,yc,Xt):
    lab={v:i for i,v in enumerate(sorted(set(yc)))}
    return np.array([lab[v] for v in yc]), None  # oracle uses true test label

def evaluate(fc,ft,yc,yt,allmap):
    cert={}
    for f in set(fc.tolist()):
        cert[f]=set(yt.dtype.type(v) for v in yc[fc==f])
    cov=w=0; fallback=0
    for i,f in enumerate(ft.tolist()):
        c=cert.get(f)
        if c is None: c=allmap; fallback+=1
        cov += 1 if yt[i] in c else 0
        w += len(c)
    n=len(yt)
    # 0/1 loss from each fibre's majority calibration label
    maj={}
    for f in set(fc.tolist()):
        vals,cnts=np.unique(yc[fc==f],return_counts=True); maj[f]=vals[int(np.argmax(cnts))]
    err=sum(1 for i,f in enumerate(ft.tolist()) if maj.get(f, None)!=yt[i])/n
    return {"coverage":round(cov/n,4),"width":round(w/n,4),"error":round(err,4),
            "fibres":len(cert),"fallback_rate":round(fallback/n,4)}

def main():
    out={"schema":"ORION02.CC18_CERTIFIABILITY.v1","seed":SEED,"K":K,"gate":GATE,
         "strata":{}, "datasets":{}}
    for st,ids in STRATA.items():
        rows=[]
        for did in ids:
            try: d=load(did)
            except Exception as e:
                out["datasets"][str(did)]={"error":str(e)[:110]}; print(f"  {did}: ERR {str(e)[:60]}",flush=True); continue
            if d is None:
                out["datasets"][str(did)]={"error":"unusable"}; continue
            X,y,name=d
            Xc,Xt,yc,yt=split(X,y)
            allmap=set(yt.dtype.type(v) for v in yc)
            res={}
            for arm,fn in (("coarse",fibres_coarse),("theorem_minimal",fibres_theorem),
                           ("distance_proxy",fibres_distance),("learned",fibres_learned)):
                fc,ft=fn(Xc,yc,Xt); res[arm]=evaluate(fc,ft,yc,yt,allmap)
            res["oracle"]={"coverage":1.0,"width":1.0,"error":0.0,"fibres":len(allmap),"fallback_rate":0.0}
            # prediction from calibration alone: does any theorem fibre have a strict
            # subset of the global calibration label set?
            fc,_=fibres_theorem(Xc,yc,Xt)
            sub=any(set(yc[fc==f])<allmap for f in set(fc.tolist()))
            res["predicted_value"]=bool(sub)
            res["observed_value"]=res["theorem_minimal"]["width"]<res["coarse"]["width"]-1e-9
            res["name"]=name; res["n"]=int(len(y)); res["classes"]=int(len(allmap))
            out["datasets"][str(did)]=res; rows.append(res)
            print(f"  {st:<17}{did:<6}{name[:16]:<17} cov {res['theorem_minimal']['coverage']:.3f} "
                  f"w {res['theorem_minimal']['width']:.2f} vs coarse w {res['coarse']['width']:.2f} "
                  f"pred={res['predicted_value']} obs={res['observed_value']}",flush=True)
        if rows:
            out["strata"][st]={"n_datasets":len(rows),
                "predicted_value":any(r["predicted_value"] for r in rows),
                "observed_value":any(r["observed_value"] for r in rows),
                "min_coverage_theorem":round(min(r["theorem_minimal"]["coverage"] for r in rows),4),
                "mean_width_theorem":round(float(np.mean([r["theorem_minimal"]["width"] for r in rows])),4),
                "mean_width_proxy":round(float(np.mean([r["distance_proxy"]["width"] for r in rows])),4)}
    S=out["strata"]
    val=[k for k,v in S.items() if v["predicted_value"]]; nov=[k for k,v in S.items() if not v["predicted_value"]]
    dis=[k for k,v in S.items() if v["predicted_value"]!=v["observed_value"]]
    gate_ok=all(v["min_coverage_theorem"]>=GATE for v in S.values()) if S else False
    width_ok=all(v["mean_width_theorem"]<=v["mean_width_proxy"]+1e-9 for v in S.values()) if S else False
    out["strata_value"]=val; out["strata_no_value"]=nov; out["disagreements"]=dis
    out["gate_holds"]=gate_ok; out["width_no_worse_than_proxy"]=width_ok
    if not S: term="CANNOT_CHECK_DATA_UNAVAILABLE"
    elif not val or not nov: term="CANNOT_CHECK_NO_CONTRAST"
    elif gate_ok and width_ok and not dis: term="CERTIFIABILITY_DISCRIMINATOR_SUPPORTED"
    else: term="CERTIFIABILITY_DISCRIMINATOR_NOT_SUPPORTED"
    out["terminal"]=term
    json.dump(out,open(os.path.expanduser("~/o02_RESULTS.json"),"w"),indent=1,sort_keys=True)
    print(f"\n{'stratum':<18}{'pred':>6}{'obs':>6}{'minCov':>9}{'w_thm':>8}{'w_proxy':>9}")
    for k,v in S.items():
        print(f"{k:<18}{str(v['predicted_value'])[0]:>6}{str(v['observed_value'])[0]:>6}"
              f"{v['min_coverage_theorem']:>9.3f}{v['mean_width_theorem']:>8.2f}{v['mean_width_proxy']:>9.2f}")
    print(f"gate>=0.90 all strata: {gate_ok}   width<=proxy: {width_ok}   disagreements: {dis}")
    print("TERMINAL:",term)

if __name__=="__main__": sys.exit(main())
