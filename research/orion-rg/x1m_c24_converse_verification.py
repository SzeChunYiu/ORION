from itertools import combinations
# C_2^4 : nonzero vectors of F_2^4 as ints 1..15
V=list(range(1,16))
def zs_subsets(S):
    """all nonempty zero-sum subsets of S (xor==0)"""
    out=[]
    for k in range(1,len(S)+1):
        for c in combinations(S,k):
            x=0
            for e in c: x^=e
            if x==0: out.append(c)
    return out
def two_disjoint(S):
    Z=zs_subsets(S)
    for i in range(len(Z)):
        for j in range(i+1,len(Z)):
            if not (set(Z[i])&set(Z[j])): return True
    return False
def min_zs(S):
    for k in range(1,len(S)+1):
        for c in combinations(S,k):
            x=0
            for e in c: x^=e
            if x==0: return k
    return None

# 1. enumerate ALL extremal D_2 witnesses (length 7, no two disjoint zero-sums)
wit=[]
for S in combinations(V,7):
    if not two_disjoint(S): wit.append(S)
from collections import Counter
hist=Counter(min_zs(S) for S in wit)
print("C_2^4 witnesses:",len(wit)," min-ZS histogram:",dict(hist))

# 2. the converse construction: affine hyperplanes {v: phi(v)=1}, drop one element
def par(x,phi): 
    return bin(x&phi).count("1")&1
constructed=set()
for phi in V:                       # 15 nonzero functionals
    H=[v for v in V if par(v,phi)==1]
    assert len(H)==8, len(H)
    for drop in range(8):
        constructed.add(tuple(sorted(H[:drop]+H[drop+1:])))
print("converse construction yields:",len(constructed),"distinct 7-sets")

anom=set(S for S in wit if min_zs(S)>3)     # min ZS > m=3
print("observed anomalous witnesses (min ZS > m):",len(anom))
print("construction == anomalous set:", constructed==anom)

# 3. f_3(C_2^4): max length with no zero-sum of length <= 3
best=0
for k in range(1,10):
    found=False
    for S in combinations(V,k):
        ok=True
        for j in range(1,min(3,k)+1):
            for c in combinations(S,j):
                x=0
                for e in c: x^=e
                if x==0: ok=False;break
            if not ok: break
        if ok: found=True;break
    if found: best=k
    else: break
print("f_3(C_2^4) =",best,"   D_2-1 =",7,"   D_2-2 =",6)
