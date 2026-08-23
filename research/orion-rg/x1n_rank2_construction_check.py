from itertools import product
def min_zs_multiset(n, mult):
    """mult: dict elt(tuple)->count over C_n^2. Return min length of nonempty zero-sum."""
    elts=list(mult.items()); best=None
    # brute force over multiplicity choices
    ranges=[range(c+1) for _,c in elts]
    for pick in product(*ranges):
        L=sum(pick)
        if L==0: continue
        if best is not None and L>=best: continue
        s=[0,0]
        for (e,_),k in zip(elts,pick):
            s[0]=(s[0]+k*e[0])%n; s[1]=(s[1]+k*e[1])%n
        if s==[0,0]:
            best=L
    return best
print(f"{'n':>3} {'len':>4} {'minZS':>6} {'m=n':>4} {'D_2-2=3n-3':>11} {'ok':>4}")
for n in (2,3,4,5,6,7,8,9,11):
    mult={(1,0):n-1,(0,1):n-1,(1,1):n-1}
    L=3*(n-1); mz=min_zs_multiset(n,mult); m=n
    ok = (mz is not None and mz>m and L==3*n-3)
    print(f"{n:>3} {L:>4} {mz:>6} {m:>4} {3*n-3:>11} {str(ok):>4}")
