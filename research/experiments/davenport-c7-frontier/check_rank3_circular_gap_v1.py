#!/usr/bin/env python3
"""Regression for the circular-gap proof, not an exhaustive Davenport search.

No repository modules or precomputed depth tables are imported. The proof note,
not this finite regression, supplies the all-prime mathematical argument.
Python 3.10+; no third-party dependencies. All checks remain active under python -O.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from itertools import product
from math import gcd, isqrt
from pathlib import Path


def require(ok: bool, context: object) -> None:
    if not ok:
        raise AssertionError(context)


def primes(limit: int) -> list[int]:
    return [p for p in range(2, limit + 1)
            if all(p % d for d in range(2, isqrt(p) + 1))]


def gaps(p: int, points: set[int]) -> list[int]:
    q = sorted(points)
    require(bool(q), 'empty circular set')
    return [y - x for x, y in zip(q, q[1:])] + [p + q[0] - q[-1]]


def gap(p: int, u: int, length: int) -> int:
    return max(gaps(p, {(j * u) % p for j in range(length + 1)}))


def direct_plane_depth(p: int, a: int) -> dict[tuple[int, int], int]:
    """Raw capacity enumeration, independent of the interval identity.

    The two saturated counts must be equal in this plane. Their joint
    contribution is e*(e1+e2)=a*e*(s-g), with occurrence cost 2*e.
    """
    out: dict[tuple[int, int], int] = {}
    for e in range(p):
        for s in range(a + 1):
            for g in range(p - a + 1):
                key = ((s + a * e) % p, (g - a * e) % p)
                cost = 2 * e + s + g
                out[key] = min(out.get(key, 10**9), cost)
    require(len(out) == p * p, ('plane coverage', p, a))
    return out


def occurrence_depth(p: int, a: int) -> dict[tuple[int, int, int], int]:
    """Independent 0/1 DP: consume each actual occurrence exactly once."""
    u = pow(a, -1, p)
    support = [(1, 0, 0), (0, 1, 0), (u, u, 1), (0, 0, 1)]
    dp = {(0, 0, 0): 0}
    for v, copies in zip(support, (p - 1, p - 1, a, p - a)):
        for _ in range(copies):
            nxt = dict(dp)
            for z, cost in dp.items():
                target = tuple((z[i] + v[i]) % p for i in range(3))
                nxt[target] = min(nxt.get(target, 10**9), cost + 1)
            dp = nxt
    return dp


# Only a>L: a<=L is covered by the full-block gap formula.
# Entries are a:largest_gap({0,u,...,L*u}); one exception remains.
SMALL = {
    7: {}, 11: {}, 13: {5: 3}, 17: {7: 5},
    19: {7: 5, 8: 5}, 23: {7: 4, 10: 5},
    29: {9: 4, 11: 5, 12: 5, 13: 7},
    31: {11: 5, 12: 5, 13: 5, 14: 7},
    37: {11: 4, 13: 5, 17: 7},
    41: {12: 4, 13: 7, 15: 5, 16: 5, 17: 5, 18: 7, 19: 9},
    43: {12: 4, 15: 8, 18: 5, 20: 9},
    47: {13: 4, 15: 7, 18: 5, 22: 9},
}
# c,d,k,n, (e1,e2,s,g,x,y), length, at p=17,a=7.
EXCEPTION = [
    (1, 3, 3, 7, (0, 0, 7, 4, 1, 10), 22),
    (2, 2, 3, 7, (1, 1, 7, 4, 1, 10), 24),
    (2, 3, 3, 7, (2, 2, 0, 1, 1, 3), 9),
    (2, 3, 4, 9, (0, 0, 1, 10, 2, 8), 21),
]


def certificate_ok(p: int, a: int, c: int, d: int, r: int, t: int,
                   n: int, counts: tuple[int, ...]) -> bool:
    e1, e2, s, g, x, y = counts
    caps = (p - 1, p - 1, a + c, p - a + d, r, t)
    return (all(0 <= b <= cap for b, cap in zip(counts, caps))
            and 0 < sum(counts) < c + d + r + t and e1 == e2
            and (a * e1 + s - n * c) % p == 0
            and (g - a * e1 - n * d) % p == 0
            and x == n * r % p and y == n * t % p)


def run() -> dict[str, object]:
    counts: dict[str, int] = {}
    digest = hashlib.sha256()

    def record(label: str, row: object) -> None:
        counts[label] = counts.get(label, 0) + 1
        digest.update((json.dumps([label, row], separators=(',', ':')) + '\n').encode())

    for p in range(5, 102):
        for a in range(2, (p - 1) // 2 + 1):
            if gcd(a, p) != 1:
                continue
            u = pow(a, -1, p)
            require(gap(p, u, a) == (p + a - 2) // a, ('full block', p, a))
            record('full_block_modulus_rows', [p, a, gap(p, u, a)])

    for p in primes(43):
        if p < 5:
            continue
        for a in range(1, (p - 1) // 2 + 1):
            u = pow(a, -1, p)
            dp = direct_plane_depth(p, a)
            for C in range(p):
                for D in range(p):
                    z = (C + D) % p
                    if z == 0:
                        continue  # deliberately excluded singular slice
                    lo, hi = max(0, z - (p - a)), min(a, z)
                    R = [(u * (C - j)) % p for j in range(lo, hi + 1)]
                    predicted = p + 2 * (p - 1 - max(R) + min(R))
                    actual = dp[C, D] + dp[-C % p, -D % p]
                    require(actual == predicted, ('antipodal identity', p, a, C, D))
                    ell = min(a, z, p - z)
                    require(actual <= p + 2 * (gap(p, u, ell) - 1),
                            ('slice envelope', p, a, C, D))
                    record('antipodal_plane_points', [p, a, C, D, actual])
            if p <= 11:
                full = occurrence_depth(p, a)
                for (C, D), value in dp.items():
                    target = (u * C % p, u * C % p, (C + D) % p)
                    require(full[target] == value, ('occurrence DP', p, a, C, D))
                    record('occurrence_dp_plane_points', [p, a, C, D, value])

    for p in primes(43):
        for v in range(1, p):
            for q in (2, 3):
                delta = q * v % p
                if not delta:
                    continue
                e = min(delta, p - delta)
                bases = {(j * v) % p for j in range(q)}
                G0 = max(gaps(p, bases))
                for N in range(1, 5):
                    ell = q * N + q - 1
                    require(gap(p, v, ell) <= max(e, G0 - N * e),
                            ('chain inequality', p, v, q, N))
                    record('directed_chain_rows', [p, v, q, N])

    exception_rows = []
    for p, expected in SMALL.items():
        H = (p - 1) // 2
        h, L = (H + 1) // 2, (H + 2) // 2
        actual = {}
        for a in range(max(4, L + 1), H + 1):
            u = pow(a, -1, p)
            if h + 1 <= u <= p - h - 1:
                actual[a] = gap(p, u, L)
                if actual[a] > h:
                    exception_rows.append([p, a])
        require(actual == expected, ('small table', p, actual, expected))
        record('small_prime_tables', [p, actual])
    require(exception_rows == [[17, 7]], ('small exceptions', exception_rows))

    for p in primes(1009):
        if p < 7:
            continue
        H = (p - 1) // 2
        h, L = (H + 1) // 2, (H + 2) // 2
        for a in range(4, H + 1):
            u = pow(a, -1, p)
            if not h + 1 <= u <= p - h - 1:
                continue
            ell = min(a, L)
            G = gap(p, u, ell)
            require(G <= h or (p, a) == (17, 7), ('rotation cover', p, a, G, h))
            if p >= 53 and a > L:
                v = min(u, p - u)
                if 2 * v >= p - h:
                    e, N = p - 2 * v, (L - 1) // 2
                    require(3 <= e <= h, ('two chain step', p, a))
                    require(2 * h >= p + 3 - 6 * N, ('two chain margin', p, a))
                else:
                    e, N = abs(3 * v - p), (L - 2) // 3
                    require(2 <= e <= h, ('three chain step', p, a))
                    require(3 * h >= p + 4 - 6 * N, ('three chain margin', p, a))
            record('rotation_type_rows', [p, a, ell, G])

    for p in primes(43):
        if p < 5:
            continue
        m, H = (3 * p - 1) // 2, (p - 1) // 2
        for r in range(1, p):
            for t in range(1, p):
                S = m - r - t
                if not 1 <= S <= p - 2:
                    continue
                Q = {q for q in range(p) if q * r % p <= r and q * t % p <= t}
                B = {-q * S % p for q in Q}
                expanded = {(b + j) % p for b in B for j in range(S + 1)}
                require(len(Q) >= r + t + 2 - p, ('scalar intersection', p, r, t))
                require(len(B) == len(Q), ('nonzero overlap dilation', p, S))
                require(len(expanded) >= min(p, len(B) + S) >= H + 2,
                        ('interval growth', p, r, t, S))
                record('scalar_interval_rows', [p, r, t, S, len(Q), len(expanded)])

    special = {(c, d, k): (n, v, size) for c, d, k, n, v, size in EXCEPTION}
    for c in (1, 2):
        for d in (1, 2, 3):
            S = c + d
            for r in range(1, 17):
                t = 25 - S - r
                if not r <= t <= 16:
                    continue
                if r >= 9:
                    n, v = 2, (0, 0, 2*c, 2*d, 2*r-17, 2*t-17)
                else:
                    k = 8 - r
                    require(0 <= k <= S - 1, ('exception boundary', c, d, r, t))
                    if k <= 2:
                        n, v = 3, (0, 0, 3*c, 3*d, 7-3*k, 17-3*(S-k))
                    else:
                        n, v, size = special[c, d, k]
                        require(sum(v) == size, ('exception certificate size', c, d, k))
                require(certificate_ok(17, 7, c, d, r, t, n, v),
                        ('exception certificate', c, d, r, t, n, v))
                record('exception_multiplicity_rows', [c, d, r, t, n, v])

    # Actual compatible p=5 pair outside the theorem (only light overlap).
    p, a, c, d, r, t = 5, 2, 2, 0, 2, 3
    support = [(3, 3, 1), (0, 0, 1), (1, 3, 0), (4, 1, 1)]
    dep = occurrence_depth(p, a)
    require(all(sum(n * v[i] for n, v in zip((c,d,r,t),support)) % p == 0
                for i in range(3)), 'positive control total sum')
    for ns in product(*(range(n+1) for n in (c,d,r,t))):
        k = sum(ns)
        if not 0 < k < 7:
            continue
        z = tuple(sum(n*v[i] for n,v in zip(ns,support)) % p for i in range(3))
        require(z != (0,0,0), ('positive control atomicity', ns))
        require(k + dep[tuple(-z0 % p for z0 in z)] >= 7,
                ('positive control short-freeness', ns))
        record('positive_control_proper_subsequences', list(ns))

    mutations = {}
    audit_depth = direct_plane_depth(17, 7)
    actual_delta = audit_depth[2, 3] + audit_depth[15, 14]
    require(actual_delta == 25, 'sharp antipodal control')
    mutations['erase_antipodal_minus_one'] = actual_delta != 17 + 2*gap(17,5,5)
    mutations['erase_cyclic_wrap_gap'] = max([3,3,3]) != max(gaps(13,{0,3,6,9}))
    mutations['weaken_strict_gap_threshold'] = gap(17,5,5) > 4
    mutations['extend_full_block_cover_to_a3'] = gap(13,pow(3,-1,13),3) > 3
    v = list(EXCEPTION[-1][4]); v[-1] += 1
    mutations['corrupt_exception_occurrence'] = not certificate_ok(17,7,2,3,4,16,9,tuple(v))
    mutations['erase_nonzero_overlap_hypothesis'] = len({-q*0 % 17 for q in range(17)}) != 17
    require(all(mutations.values()), ('mutation control failed', mutations))

    expected_counts = {
        'full_block_modulus_rows':1472, 'antipodal_plane_points':132492,
        'occurrence_dp_plane_points':802, 'directed_chain_rows':2124,
        'small_prime_tables':12, 'rotation_type_rows':18866,
        'scalar_interval_rows':5646, 'exception_multiplicity_rows':36,
        'positive_control_proper_subsequences':34,
    }
    require(counts == expected_counts, ('regression coverage changed', counts))
    require(digest.hexdigest() == 'c3c787f6e2d6b32cfff96f6c3c764661980a10ab57750663345a4268621b20ef',
            'regression transcript changed')
    return {
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'status': 'RANK3_CIRCULAR_GAP_V1_GREEN',
        'proof_authority': 'symbolic proof plus displayed finite-prime arithmetic and four explicit certificates',
        'regression_only': True, 'counts': counts,
        'transcript_sha256': digest.hexdigest(),
        'small_cover_exceptions': exception_rows,
        'explicit_exception_certificates': len(EXCEPTION),
        'hostile_mutations_rejected': len(mutations), 'mutation_controls': mutations,
        'positive_control': {'p':5,'a':2,'c':2,'d':0,'r':2,'t':3,
                             'x':[1,3,0],'y':[4,1,1],'minimum_allowed_zero_sum_length':7},
        'claim_ceiling': {'rank3_a_ge4':'proved in accompanying note',
                          'rank3_a2_a3':'not settled by this argument',
                          'all_prime_support7':'not claimed', 'D3_C7':'not claimed',
                          'novelty_priority':'not certified'},
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write the deterministic JSON receipt')
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output is not None:
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')
