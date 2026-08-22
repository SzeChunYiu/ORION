import numpy as np, subprocess, random, collections, json, itertools
A=np.load("wit.npy"); rng=random.Random(20260822)
CAN="./canon"

def to_json(codes):
    return "["+",".join("[%d,%d,%d]"%(c//25,(c//5)%5,c%5) for c in codes)+"]"
def canon_batch(list_of_codeseqs):
    inp="\n".join(to_json(s) for s in list_of_codeseqs)+"\n"
    r=subprocess.run([CAN,"canon",str(len(list_of_codeseqs[0]))],input=inp,capture_output=True,text=True)
    assert r.returncode==0, r.stderr
    return [tuple(int(x) for x in l.split()) for l in r.stdout.strip().split("\n")]

def randgl(rng):
    while True:
        M=[[rng.randrange(5) for _ in range(3)] for _ in range(3)]
        d=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
          -M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
          +M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))%5
        if d: return M
def apply(M,codes):
    out=[]
    for c in codes:
        v=(c//25,(c//5)%5,c%5)
        a=sum(v[i]*M[i][0] for i in range(3))%5
        b=sum(v[i]*M[i][1] for i in range(3))%5
        d=sum(v[i]*M[i][2] for i in range(3))%5
        out.append(25*a+5*b+d)
    return out

# ---- independent zero-sum length distribution (sub-multiset enumeration) ----
def zs_profile(codes):
    cnt=collections.Counter(codes); items=list(cnt.items())
    # DP over (sum, size) counting distinct sub-multisets
    from collections import defaultdict
    cur={(0,0):1}
    for code,m in items:
        v=(code//25,(code//5)%5,code%5)
        nxt=defaultdict(int)
        for (s,k),n in cur.items():
            sv=(s//25,(s//5)%5,s%5)
            for t in range(m+1):
                ns=25*((sv[0]+t*v[0])%5)+5*((sv[1]+t*v[1])%5)+((sv[2]+t*v[2])%5)
                nxt[(ns,k+t)]+=n
        cur=nxt
    prof=collections.Counter()
    for (s,k),n in cur.items():
        if s==0 and k>0: prof[k]+=n
    return tuple(sorted(prof.items()))

# ================= TEST A: GL-invariance round trip =================
idx=[rng.randrange(len(A)) for _ in range(400)]
origs=[A[i].tolist() for i in idx]
imgs=[apply(randgl(rng),s) for s in origs]
ca=canon_batch(origs); cb=canon_batch(imgs)
failA=sum(1 for x,y in zip(ca,cb) if x!=y)
# how many images actually lost e1/e2/e3 (proves support-genericity was exercised)
lost=sum(1 for s in imgs if not({25,5,1} <= set(s)))
print("TEST A  GL round-trip failures: %d / 400   (images lacking {e1,e2,e3}: %d)"%(failA,lost))

# ================= TEST B: idempotence =================
cc=canon_batch([list(x) for x in ca])
failB=sum(1 for x,y in zip(ca,cc) if x!=y)
print("TEST B  idempotence failures: %d / 400"%failB)

# ================= TEST D: canonical form preserves zero-sum structure =================
failD=0
for s,c in list(zip(origs,ca))[:120]:
    if zs_profile(s)!=zs_profile(list(c)): failD+=1
print("TEST D  zero-sum-profile mismatch orig vs canon: %d / 120"%failD)

# ============ TEST C: negative test with teeth ============
# inside ONE multiplicity profile, find pairs whose zero-sum length distribution differs
target=(1,1,1,2,2,4,4,4)
pool=[]
for i in range(0,len(A),7):
    r=A[i].tolist()
    if tuple(sorted(collections.Counter(r).values()))==target:
        pool.append((i,r))
    if len(pool)>=300: break
byprof=collections.defaultdict(list)
for i,r in pool: byprof[zs_profile(r)].append((i,r))
print("TEST C  within profile %s: %d distinct zero-sum length distributions among %d sampled"%(target,len(byprof),len(pool)))
reps=[v[0] for v in byprof.values()]
cr=canon_batch([r for _,r in reps])
distinct=len(set(cr))
print("TEST C  -> %d distinct canonical forms for %d provably-inequivalent sequences (must be equal)"%(distinct,len(reps)))
# also: same-profile pairs that ARE equivalent must collapse
same=0; coll=0
for prof,v in byprof.items():
    if len(v)>=2:
        c2=canon_batch([v[0][1],v[1][1]])
        same+=1; coll+= (c2[0]==c2[1])
print("TEST C' same-zs-profile pairs tested: %d, of which canonically equal: %d (informational)"%(same,coll))

json.dump({"testA_failures":failA,"testA_images_lacking_e123":lost,"testB_failures":failB,
           "testD_failures":failD,"testC_inequivalent_reps":len(reps),"testC_distinct_canon":distinct},
          open("validation.json","w"),indent=1)
