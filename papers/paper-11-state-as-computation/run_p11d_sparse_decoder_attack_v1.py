from __future__ import annotations
import hashlib,itertools,json
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
SEED=2026082116
CELLS=((17,4,5),(19,3,7)); NS=(64,128,256,512,1024,2048); TEST=8192; Q=5
OUT=Path(__file__).with_name("P11D_SPARSE_DECODER_RESULT_V1.json")
def bank(x,subs):
    idx=np.asarray(subs,dtype=np.int16); return np.prod(x[:,idx],axis=2,dtype=np.int8)
def threshold(curve):
    for n in NS:
        if curve[n]>=.95:return n
    return None
def main():
    rng=np.random.default_rng(SEED); cells=[]; laund=[]
    for ci,(d,s,r) in enumerate(CELLS):
        subs=list(itertools.combinations(range(d),s)); nb=len(subs)
        qs=[rng.choice(nb,size=r,replace=False).tolist() for _ in range(Q)]
        tx=rng.choice((-1,1),size=(TEST,d)).astype(np.int8); tb=bank(tx,subs); tys=[]
        for qi,a in enumerate(qs):
            v=tb[:,a]; signed=np.where(v.sum(1)>0,1,-1).astype(np.int8); tys.append((signed>0).astype(np.int8))
            for j in range(r):
                if np.array_equal(v[:,j],signed):laund.append([ci,qi,j,"equals"])
                if np.array_equal(v[:,j],-signed):laund.append([ci,qi,j,"negates"])
        curves={"UNIVERSAL_L1":{},"COMPILED_L2":{}}
        for n in NS:
            x=rng.choice((-1,1),size=(n,d)).astype(np.int8); b=bank(x,subs)
            scores={k:[] for k in curves}
            for qi,a in enumerate(qs):
                y=(b[:,a].sum(1)>0).astype(np.int8)
                m=LogisticRegression(C=.1,penalty="l1",solver="liblinear",max_iter=1000);m.fit(b,y);scores["UNIVERSAL_L1"].append(m.score(tb,tys[qi]))
                m=LogisticRegression(C=1,solver="liblinear",max_iter=1000);m.fit(b[:,a],y);scores["COMPILED_L2"].append(m.score(tb[:,a],tys[qi]))
            for k in curves:curves[k][n]=float(np.mean(scores[k]))
        th={k:threshold(v) for k,v in curves.items()}; ct=th["COMPILED_L2"]; ut=th["UNIVERSAL_L1"]
        ratio=(ct is not None and (ut is None or ut>=4*ct))
        cells.append({"cell":[d,s,r],"universal_dimension":nb,"compiled_dimension":r,
                      "curves":{k:{str(n):v for n,v in c.items()} for k,c in curves.items()},
                      "threshold_0_95":th,"ratio_gate":ratio,
                      "delta64":curves["COMPILED_L2"][64]-curves["UNIVERSAL_L1"][64]})
    gates={"no_laundering":not laund,
           "compiled_by_64":all(c["threshold_0_95"]["COMPILED_L2"] is not None and c["threshold_0_95"]["COMPILED_L2"]<=64 for c in cells),
           "threshold_ratio_ge_4":all(c["ratio_gate"] for c in cells),
           "delta64_ge_0_20":all(c["delta64"]>=.20 for c in cells)}
    terminal="P11D_SPARSE_DECODER_GAP_SUPPORTED" if all(gates.values()) else "P11D_SPARSE_DECODER_GAP_NOT_MET"
    payload={"schema":"ORION.P11D.SparseDecoderAttack.v1","protocol":"P11D_SPARSE_DECODER_ATTACK_PROTOCOL_V1.md",
             "seed":SEED,"cells":cells,"laundering_failures":laund,"gates":gates,"terminal":terminal}
    text=json.dumps(payload,indent=2,sort_keys=True)+"\n";OUT.write_text(text)
    print(json.dumps({"terminal":terminal,"cells":[{"cell":c["cell"],"thresholds":c["threshold_0_95"],"delta64":c["delta64"]} for c in cells],
                      "gates":gates,"sha256":hashlib.sha256(text.encode()).hexdigest()},indent=2,sort_keys=True))
    if terminal!="P11D_SPARSE_DECODER_GAP_SUPPORTED":raise SystemExit(1)
if __name__=="__main__":main()
