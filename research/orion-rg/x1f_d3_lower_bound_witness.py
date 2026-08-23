"""Independently establish D_3(C_5^3) >= 25 by exhibiting a length-24 sequence
with no three pairwise disjoint nonempty zero-sum subsequences.
Search: extend the Freeze--Schmid 19-term k=2 witness by 5 elements."""
from itertools import product, combinations_with_replacement
P=5
def vadd(a,b): return tuple((a[i]+b[i])%P for i in range(3))
def has_k_disjoint(seq,k):
    states={(((0,0,0),)*k,(False,)*k)}
    for e in seq:
        new=set(states)
        for sums,flags in states:
            for i in range(k):
                s2=list(sums); f2=list(flags); s2[i]=vadd(sums[i],e); f2[i]=True
                new.add((tuple(s2),tuple(f2)))
        states=new
    return (((0,0,0),)*k,(True,)*k) in states
def minzs(seq):
    reach={0:{(0,0,0)}}
    for e in seq:
        new={}
        for w,S in reach.items():
            new.setdefault(w,set()).update(S)
            new.setdefault(w+1,set()).update(vadd(s,e) for s in S)
        reach=new
    return next((w for w in sorted(reach) if w>0 and (0,0,0) in reach[w]),None)
e1,e2,e3=(1,0,0),(0,1,0),(0,0,1)
FS19=[e1]*4+[e2]*4+[e3]*4+[(1,1,0)]*2+[(1,0,1)]*2+[(0,1,1)]*3
assert not has_k_disjoint(FS19,2)
allv=[v for v in product(range(P),repeat=3) if v!=(0,0,0)]
# Lemma A at length 24 with D_2=20: min zero-sum >= 24-20+1 = 5.
found=None
for add5 in combinations_with_replacement(allv,5):
    M=FS19+list(add5)
    z=minzs(M)
    if z is None or z<5: continue
    if not has_k_disjoint(M,3): found=M; break
print("length-24 witness with no three disjoint zero-sums found:", found is not None)
if found:
    print("witness:",found)
    print("length:",len(found),"min zero-sum:",minzs(found))
    print("two disjoint? ",has_k_disjoint(found,2))
    print("three disjoint?",has_k_disjoint(found,3))
    import json; open("lb24_witness.json","w").write(json.dumps([list(v) for v in found]))
