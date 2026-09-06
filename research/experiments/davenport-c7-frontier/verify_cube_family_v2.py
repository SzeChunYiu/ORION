#!/usr/bin/env python3
"""Verify the binary-cube families S_2(p), S_3(p) of CUBE_FAMILY_LOWER_BOUNDS_V2.md.

pk(S_2(p)) = 1 and pk(S_3(p)) = 2 for p in {3,5,7,11} (11 optional, slower), by exhaustive
recursion over minimal zero-sum sub-multisets.  Exit code 0 iff every assertion holds."""
import sys
from functools import lru_cache
from itertools import product

Q = ((1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,1,1))

def packing_number(p, m):
    n = len(m)
    def zs(b): return all(sum(b[i]*Q[i][j] for i in range(n)) % p == 0 for j in range(3))
    zero = [b for b in product(*[range(x+1) for x in m]) if any(b) and zs(b)]
    leq = lambda a, b: all(a[i] <= b[i] for i in range(n))
    atoms = [b for b in zero if not any(c != b and leq(c, b) for c in zero)]
    @lru_cache(maxsize=None)
    def pack(r, t):
        if t == 0: return True
        return any(leq(b, r) and pack(tuple(r[i]-b[i] for i in range(n)), t-1) for b in atoms)
    k = 0
    while pack(tuple(m), k+1): k += 1
    return k, len(atoms)

def S2(p): return (p-1, p-1, p-1, (p+1)//2, (p-1)//2, (p-1)//2, 0)
def S3(p): return (p-1, p-1, p-1, p-1, (p+1)//2, (p-1)//2, (p+1)//2)

if __name__ == '__main__':
    primes = (3, 5, 7) if '--fast' in sys.argv else (3, 5, 7, 11)
    for p in primes:
        m2, m3 = S2(p), S3(p)
        assert sum(m2) == (9*p-7)//2 and sum(m3) == (11*p-7)//2
        k2, a2 = packing_number(p, m2)
        k3, a3 = packing_number(p, m3)
        print(f"p={p}: S_2 len={sum(m2)} atoms={a2} pk={k2}; S_3 len={sum(m3)} atoms={a3} pk={k3}")
        assert k2 == 1 and k3 == 2
    print("PASS: cube families realise D_2 >= (9p-5)/2 and D_3 >= (11p-5)/2 for p in", primes)
