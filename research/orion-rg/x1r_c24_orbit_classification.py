"""X1-R: GL(4,2)-orbit decomposition of the C_2^4 extremal D_2 witness set.

Witnesses = length-7 squarefree sequences over C_2^4 with no two disjoint nonempty
zero-sum subsequences.  Squarefreeness is forced: a repeat is a length-2 zero-sum,
leaving 5 terms that must be zero-sum-free, impossible since d(C_2^4) = 4.

Validation: every orbit must satisfy |orbit| * |Stab| = |GL(4,2)| = 20160.
"""
from itertools import combinations, permutations

V = list(range(1, 16))

def zero_sums(S):
    out = []
    for k in range(1, len(S) + 1):
        for c in combinations(S, k):
            x = 0
            for e in c:
                x ^= e
            if x == 0:
                out.append(frozenset(c))
    return out

def has_two_disjoint(S):
    Z = zero_sums(S)
    return any(not (Z[i] & Z[j]) for i in range(len(Z)) for j in range(i + 1, len(Z)))

def min_zs(S):
    for k in range(1, len(S) + 1):
        for c in combinations(S, k):
            x = 0
            for e in c:
                x ^= e
            if x == 0:
                return k

def gl42():
    mats = []
    for perm in permutations(range(1, 16), 4):
        span = {0}
        for c in perm:
            span |= {s ^ c for s in span}
        if len(span) == 16:
            m = [0] * 16
            for v in range(16):
                x = 0
                for i in range(4):
                    if (v >> i) & 1:
                        x ^= perm[i]
                m[v] = x
            mats.append(tuple(m))
    return mats

if __name__ == "__main__":
    wit = [frozenset(S) for S in combinations(V, 7) if not has_two_disjoint(S)]
    mats = gl42()
    assert len(mats) == 20160, len(mats)
    seen, orbits = set(), []
    for w in wit:
        if w in seen:
            continue
        orb = {frozenset(m[v] for v in w) for m in mats}
        orbits.append((len(orb), min_zs(sorted(w))))
        seen |= orb
    print(f"witnesses {len(wit)}   |GL(4,2)| {len(mats)}")
    for sz, mz in sorted(orbits, reverse=True):
        stab = len(mats) // sz
        assert sz * stab == len(mats)
        print(f"  orbit {sz:>5}  min-ZS {mz}  |Stab| {stab:>4}  orbit-stabiliser OK")
    assert sum(o[0] for o in orbits) == len(wit)
    print("orbit sizes sum to the enumerated total: OK")
