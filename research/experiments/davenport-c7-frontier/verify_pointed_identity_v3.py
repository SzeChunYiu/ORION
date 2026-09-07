"""HOSTILE VALIDATION of the pointed identity, before any claim rests on it.

(1) Brute force: for random zero-sum sequences over C_3^3 and EVERY index i, check
        sum_{I ∋ i, sigma(I)=0} (-1)^{|I|} C(|I|-1,d) == 0 (mod p)   for d <= N-D-1.
(2) Real object: the packing-number-3 sequence over C_5^3 (length 25). Compute, for every
    index i, the true counts of zero-sum index sets of each size through i, and verify the
    pointed congruence with those counts.  If the machinery is sound it must hold exactly.
"""
import random
from math import comb
from itertools import product

def brute_pointed(p, r, T):
    D = r*(p-1)+1
    n = len(T)
    # counts[i][l] = # zero-sum index sets of size l containing i
    counts=[[0]*(n+1) for _ in range(n)]
    for mask in range(1<<n):
        s=[0]*r; c=0; mm=mask; j=0
        while mm:
            if mm&1:
                c+=1
                for k in range(r): s[k]=(s[k]+T[j][k])%p
            mm>>=1; j+=1
        if not any(s):
            for j in range(n):
                if mask>>j & 1: counts[j][c]+=1
    bad=[]
    for i in range(n):
        for d in range(0, n-D):          # deg h = d+1 <= n-D
            v=sum(((-1)**l)*counts[i][l]*comb(l-1,d) for l in range(1,n+1))%p
            if v: bad.append((i,d,v))
    return bad

random.seed(11)
print("(1) brute-force pointed identity over C_3^3:")
for t in range(3):
    T=[tuple(random.randrange(3) for _ in range(3)) for _ in range(14)]
    T.append(tuple((-sum(x[j] for x in T))%3 for j in range(3)))
    bad=brute_pointed(3,3,T)
    print(f"    trial {t}: violations = {len(bad)}")
    assert not bad, bad[:3]

print("\n(2) real packing-number-3 object over C_5^3, length 25:")
p,r=5,3; D=r*(p-1)+1
Q=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1)]
a,hi,lo=p-1,(p+1)//2,(p-1)//2
pts=list(Q); mult=[2*p-1,a,a,hi,lo,lo]
sig=tuple(sum(mult[i]*pts[i][j] for i in range(len(pts)))%p for j in range(3))
cm=tuple((-x)%p for x in sig)
if cm in pts: mult[pts.index(cm)]+=1
else: pts.append(cm); mult.append(1)
# expand to a flat sequence of 25 terms
T=[]
for i,g in enumerate(pts): T += [g]*mult[i]
N=len(T); assert N==25
# counts by (index, size) via DP over subsets is 2^25 = too big; use multiset DP with weights.
# For each index i, count zero-sum subsets containing i = (subsets of T\{i} summing to -T[i]).
# Do it by a size-graded convolution over the other 24 terms.
def counts_through(i):
    rest=[T[j] for j in range(N) if j!=i]
    # dp[size][sum] over rest
    dp=[dict() for _ in range(len(rest)+1)]
    dp[0][(0,0,0)]=1
    for g in rest:
        for sz in range(len(rest)-1,-1,-1):
            if not dp[sz]: continue
            tgt=dp[sz+1]
            for s,c in dp[sz].items():
                ns=tuple((s[k]+g[k])%p for k in range(3))
                tgt[ns]=tgt.get(ns,0)+c
    need=tuple((-T[i][k])%p for k in range(3))
    return [dp[sz].get(need,0) for sz in range(len(rest)+1)]
bad=[]
for i in range(N):
    c=counts_through(i)     # c[sz] = # subsets of size sz of T\{i} summing to -T[i]
    for d in range(0, N-D):
        v=sum(((-1)**(sz+1))*c[sz]*comb(sz,d) for sz in range(len(c)))%p
        if v: bad.append((i,d,v))
print(f"    violations over all 25 indices and d <= {N-D-1}: {len(bad)}")
assert not bad, bad[:3]
print("\nBOTH CONTROLS PASS: the pointed identity is correctly implemented and holds on a real object.")
