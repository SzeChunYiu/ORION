import sys, json, time
sys.path.insert(0,'research/extensions/orion-qg')
import qg15_third_family as q15, qg15c_vocabulary as v15c
from qg15c_enlarged_vocab import donor_path_features
WITNESS=[15,30,39,42]
def state_block(state,n):
    rows=[(q15._sof(e,n),q15._xof(e,n),q15._zof(e,n)) for e in state]
    neg=sum(1 for s,_,_ in rows if s); W=4
    pw=[0]*(W+1); nw=[0]*(W+1); py=[0]*(W+1); ny=[0]*(W+1); pq=[0]*4; nq=[0]*4
    for s,x,z in rows:
        w=bin(x|z).count("1"); y=bin(x&z).count("1")
        (nw if s else pw)[w]+=1; (ny if s else py)[y]+=1
        (nq if s else pq)[(x&1)|((z&1)<<1)]+=1
    cx=[];cy=[];cz=[]
    for j in range(n):
        cx.append(sum(1 for _,x,z in rows if (x>>j)&1 and not ((z>>j)&1)))
        cy.append(sum(1 for _,x,z in rows if (x>>j)&1 and ((z>>j)&1)))
        cz.append(sum(1 for _,x,z in rows if ((z>>j)&1) and not ((x>>j)&1)))
    def st4(xs): return (min(xs) if xs else 0,max(xs) if xs else 0,sum(v*v for v in xs),sum(1 for v in xs if v==0))
    vec=[neg]+pw+nw+py+ny+pq+nq
    for cs in (cx,cy,cz): vec.extend(st4(cs))
    return tuple(vec)
t=time.perf_counter(); out={}
for n in (3,4):
    dist=q15.referee(n)
    vecs=[]
    for state in sorted(dist):
        v1,v2,cd,lb,costs=v15c.feature_vectors(state,n)
        vec=v2+tuple(donor_path_features(q15.donor(state,n)[3],n))+state_block(state,n)
        vecs.append(tuple(vec[j] for j in WITNESS))
    ranges=[len({v[i] for v in vecs}) for i in range(4)]
    cells=len(set(vecs)); cap=1
    for r in ranges: cap*=r
    out[n]={"instances":len(vecs),"witness_ranges":ranges,"capacity_product":cap,
            "realized_cells":cells,"capacity_ratio":round(cap/len(vecs),4),
            "compression":round(cells/len(vecs),6)}
    print(f"n={n}: {json.dumps(out[n])}  ({time.perf_counter()-t:.0f}s)",flush=True)
json.dump(out,open('/tmp/o09_stage1.json','w'),indent=1)
print("LABELS NOT CONSULTED IN THIS STAGE")
