"""Decisive test: is there a length-30 sequence over C_5^3 with packing number <= 3?
If yes, D_4(C_5^3) >= 31 and the arithmetic conjecture D_k = 5k+10 FAILS at k=4.
Stage 1: extend the known length-29 pk=3 witnesses by one element, every possible way."""
from functools import lru_cache
from itertools import product

n=5
def pk_of(pts,m,cutoff=8):
    k=len(pts)
    def zs(b): return all(sum(b[i]*pts[i][j] for i in range(k))%n==0 for j in range(3))
    zero=[b for b in product(*[range(x+1) for x in m]) if any(b) and zs(b)]
    leq=lambda a,b: all(a[i]<=b[i] for i in range(k))
    atoms=[b for b in zero if not any(c!=b and leq(c,b) for c in zero)]
    @lru_cache(maxsize=None)
    def pa(r,t):
        if t==0: return True
        return any(leq(b,r) and pa(tuple(r[i]-b[i] for i in range(k)),t-1) for b in atoms)
    j=0
    while j<cutoff and pa(tuple(m),j+1): j+=1
    return j

Q=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,1,1)]
# the two known length-29 pk=3 families
S4  = (Q+[(1,1,2)], [4,4,4,4,3,2,4,4])           # cube + g   (c_3 optimum on 8 points)
T4  = (Q[:6],       [4*5-1-5, 4,4,3,2,2])        # T_4(5) = e1^14 e2^4 e3^4 e12^3 e13^2 e23^2
for name,(pts,m) in (("S_4",S4),("T_4",T4)):
    print(name, "len", sum(m), "pk", pk_of(pts,m))

print("\nStage 1: add one element x to each length-29 witness; report any with pk <= 3 (=> D_4 >= 31)")
hits=[]
for name,(pts,m) in (("S_4",S4),("T_4",T4)):
    for x in product(range(n),repeat=3):
        if x==(0,0,0): continue
        if x in pts:
            i=pts.index(x); m2=list(m); m2[i]+=1; p2=pts
        else:
            p2=pts+[x]; m2=list(m)+[1]
        g=pk_of(p2,m2)
        if g<=3: hits.append((name,x,sum(m2),g))
    print(f"  {name}: {sum(1 for h in hits if h[0]==name)} single-element extensions keep pk <= 3")
for h in hits[:10]: print("   ",h)
if not hits: print("  none: neither length-29 witness extends to a length-30 obstruction")
