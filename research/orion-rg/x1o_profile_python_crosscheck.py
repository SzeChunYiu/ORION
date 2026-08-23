from itertools import combinations_with_replacement, combinations
from collections import Counter
def run(p,r,T,L):
    N=p**r
    def dec(x): 
        v=[]
        for _ in range(r): v.append(x%p); x//=p
        return tuple(v)
    els=[dec(x) for x in range(1,N)]
    def add(a,b): return tuple((a[i]+b[i])%p for i in range(r))
    Z=tuple([0]*r)
    tot=0; profs=Counter()
    for seq in combinations_with_replacement(els,L):
        ok=True
        # any nonempty zero-sum subsequence of length <= T ?
        for k in range(1,T+1):
            for c in combinations(range(L),k):
                s=Z
                for i in c: s=add(s,seq[i])
                if s==Z: ok=False;break
            if not ok: break
        if ok:
            tot+=1
            profs[tuple(sorted(Counter(seq).values()))]+=1
    return tot,profs
t,pf=run(3,2,3,6)
print("C_3^2 T=3 L=6 : total",t,"profiles",dict(pf))
