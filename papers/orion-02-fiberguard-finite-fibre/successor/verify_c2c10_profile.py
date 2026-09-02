#!/usr/bin/env python3
"""Profile-formula Kmin vs exhaustive Kmin (certification harness).

Reduction claim: the instance families ({0}+odd-S vs {0}+even-S, S subseteq
[q]) are invariant under permutations of the q variables, and w/f terms
depend only on (block size, anchor membership), so C_Pi(0) depends only on
(block-size multiset, which size class holds the anchor, instance eps).

Closed form per block of size s:
  w_i = N*[anchor] + (s - [anchor])*N/2
  f_i = N/2^(s-1)     anchor block, any size 1..m-1 (holds at boundary too)
  f_i = N/2^s         variable block, s <= q-1
  f_i = eps*L         variable block of size q = all variables
d(1)=0, d(s)=d(ceil s/2)+d(floor s/2)+s-2; b(s)=ceil(log2 s), b(1)=0.
C_one(0) = (b+1)W + m-1+d+b - (m(b+1)-1)*eps*L,  W = N(m+1)/2, N=2^(m-2)*L.
Kmin = max over proper integer profiles (k>=2), anchor class, eps in {0,1}
       of floor(G/(2k-1))+1 where G = C_one(0) - C_Pi(0) > 0.
"""
import math
import sys
from functools import lru_cache


@lru_cache(maxsize=None)
def bf(s):
    return 0 if s == 1 else math.ceil(math.log2(s))


@lru_cache(maxsize=None)
def df(s):
    return 0 if s == 1 else df((s + 1) // 2) + df(s // 2) + s - 2


def int_partitions(n, max_part=None):
    """All multisets of parts summing to n, as sorted-desc tuples."""
    if max_part is None:
        max_part = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, max_part), 0, -1):
        for rest in int_partitions(n - first, first):
            yield (first,) + rest


def block_term(anchor, s, epsL, N, q):
    if anchor:
        w = N + (s - 1) * N / 2.0
        f = N / float(2 ** (s - 1))
    elif s == q:  # all variables in one block: only eps*L columns contain them
        w = s * N / 2.0
        f = float(epsL)
    else:
        w = s * N / 2.0
        f = N / float(2 ** s)
    return 2 * f + (bf(s) + 2) * (w - s * f)


def profile_cost(profile, a_size, eps, N, L, m):
    """Cost of the partition profile with the anchor in a size-a_size block."""
    q = m - 1
    k = len(profile)
    cost = 2 * m + k - 3
    ds = bm = 0
    used_anchor = False
    for s in profile:
        ds += df(s)
        bm = max(bm, bf(s))
        anchor = (s == a_size) and not used_anchor
        used_anchor = used_anchor or anchor
        cost += block_term(anchor, s, eps * L, N, q)
    return cost + ds + bm


def kmin_profile(m, L):
    N = (1 << (m - 2)) * L
    b, d = bf(m), df(m)
    best, best_prof = 0, None
    for eps in (0, 1):
        W = N * (m + 1) / 2.0
        C_one = (b + 1) * W + m - 1 + d + b - (m * (b + 1) - 1) * eps * L
        for profile in int_partitions(m):
            k = len(profile)
            if k < 2:
                continue
            for a_size in sorted(set(profile)):
                c = profile_cost(profile, a_size, eps, N, L, m)
                G = C_one - c
                if G > 0:
                    t = math.floor(G / (2 * k - 1)) + 1
                    if t > best:
                        best, best_prof = t, (profile, a_size, eps)
    return best, best_prof


KNOWN = {(5, 1): 13, (5, 2): 26, (6, 1): 25, (6, 2): 49, (7, 1): 44,
         (7, 2): 87, (8, 1): 88, (8, 2): 175, (9, 1): 273, (10, 1): 552}

if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    ok = True
    if args:  # ad-hoc: m L pairs
        for spec in args:
            m, L = map(int, spec.split(","))
            got, prof = kmin_profile(m, L)
            print(f"m={m:2d} L={L}: profile-Kmin={got:8d}  {prof}")
        raise SystemExit(0)
    for (m, L), want in sorted(KNOWN.items()):
        got, prof = kmin_profile(m, L)
        status = "OK " if got == want else "MISMATCH"
        if got != want:
            ok = False
        print(f"m={m:2d} L={L}: profile={got:6d} exhaustive={want:6d} {status}  {prof}")
    print("ALL MATCH" if ok else "FAILURE")
    raise SystemExit(0 if ok else 1)
