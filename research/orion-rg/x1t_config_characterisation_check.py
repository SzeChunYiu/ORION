"""X1-T: exhaustive verification of the configuration theorem.

Claim: W = B0 u A (A a 4-set of weight->=3 vectors XORing to 0) is a D_2-extremal
witness iff (C1) f>=1 or the pair-columns cover all six pairs, and (C2) every row
has >=2 distinct neighbours in the pair-column multigraph.
Verified: r=5 (65 candidates) and r=6 (1855 candidates), zero mismatches.
"""
from itertools import combinations, permutations

def run(r):
    N = 1 << r
    B0 = [1 << i for i in range(r)]
    pool = [v for v in range(1, N) if v not in set(B0) and bin(v).count("1") >= 3]
    ps = set(pool)
    cands = []
    for t in combinations(pool, 3):
        x = t[0] ^ t[1] ^ t[2]
        if x and x > t[-1] and x in ps:
            cands.append(t + (x,))

    def witness(A):
        W = B0 + list(A)
        n = len(W)
        xr = [0] * (1 << n)
        Z = []
        for s in range(1, 1 << n):
            low = s & -s
            xr[s] = xr[s ^ low] ^ W[low.bit_length() - 1]
            if xr[s] == 0:
                Z.append(s)
        return not any(not (Z[i] & Z[j]) for i in range(len(Z)) for j in range(i + 1, len(Z)))

    def pred(A):
        f, edges = 0, []
        for bit in range(r):
            T = tuple(i for i in range(4) if (A[i] >> bit) & 1)
            assert len(T) % 2 == 0
            if len(T) == 4:
                f += 1
            elif len(T) == 2:
                edges.append(tuple(sorted(T)))
        c1 = f >= 1 or len(set(edges)) == 6
        nb = {i: set() for i in range(4)}
        for i, j in edges:
            nb[i].add(j)
            nb[j].add(i)
        return c1 and all(len(nb[i]) >= 2 for i in range(4))

    mism = sum(1 for A in cands if witness(A) != pred(A))
    surv = sum(1 for A in cands if witness(A))
    print(f"r={r}: candidates={len(cands)} survivors={surv} mismatches={mism}")
    assert mism == 0

if __name__ == "__main__":
    run(5)
    run(6)
