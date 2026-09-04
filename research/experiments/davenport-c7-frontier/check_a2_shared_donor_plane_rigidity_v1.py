#!/usr/bin/env python3
"""Independent bounded-occurrence regression for shared-donor plane rigidity.

The proofs, not these finite checks, establish the all-prime statements.
No network, external packages, repository imports, or floating-point arithmetic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path

INF = 10**9


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def primes(limit: int) -> list[int]:
    result: list[int] = []
    for n in range(2, limit + 1):
        if all(n % d for d in range(2, isqrt(n) + 1)):
            result.append(n)
    return result


def encode(p: int, v: tuple[int, int, int]) -> int:
    return ((v[0] % p) * p + v[1] % p) * p + v[2] % p


def translation(p: int, v: tuple[int, int, int]) -> list[int]:
    return [encode(p, (a + v[0], b + v[1], c + v[2]))
            for a in range(p) for b in range(p) for c in range(p)]


def add_occurrence(dp: list[int], shift: list[int], zero_best: int) -> tuple[list[int], int]:
    """0/1 update: read only the previous table, never reuse this occurrence."""
    new = dp.copy()
    for source, target in enumerate(shift):
        candidate = dp[source] + 1
        if target == 0 and candidate < zero_best:
            zero_best = candidate
        if candidate < new[target]:
            new[target] = candidate
    return new, zero_best


def donor_tables(p: int):
    """Yield exact depths and shortest NONEMPTY zero-sum after each s count."""
    h = (p - 1) // 2
    dp = [INF] * (p**3)
    dp[0] = 0
    zero_best = INF
    for v, count in [((1, 0, 0), p-1), ((0, 1, 0), p-1), ((0, 0, 1), p-2)]:
        shift = translation(p, v)
        for _ in range(count):
            dp, zero_best = add_occurrence(dp, shift, zero_best)
    shift = translation(p, (h+1, h+1, 1))
    for k in range(1, h+3):
        dp, zero_best = add_occurrence(dp, shift, zero_best)
        if k >= 3:
            yield k, dp, zero_best


def envelope(p: int, k: int, c: int) -> int:
    if c <= 2:
        return p
    if c <= k:
        return p+1
    return p+c-k+1


def certificate(p: int, a: int) -> tuple[int, tuple[int, int, int, int]]:
    """Counts ordered e1,e2,s,g; for y=(a,-a,1), a nonzero."""
    require(p >= 13 and p % 4 == 1, "certificate modulus outside theorem")
    a %= p
    require(a != 0, "use the g^p certificate for a=0")
    q = (p-1)//4
    alpha = min(a, p-a)
    j = 1 if alpha > q else q//alpha+1
    big_p = (-j*a) % p
    counts = (big_p-q-1, p-big_p-q-1, 2*q+2, 2*q-j-1)
    return j, counts


def valid_certificate(p: int, a: int, j: int, counts: tuple[int, int, int, int],
                      s_cap: int | None = None) -> bool:
    q = (p-1)//4
    e1, e2, s, g = counts
    cap = 2*q+2 if s_cap is None else s_cap
    if not (1 <= j <= q+1 and 0 <= e1 <= p-1 and 0 <= e2 <= p-1
            and 0 <= s <= cap and 0 <= g <= p-2):
        return False
    u = (p+1)//2
    return ((e1+s*u+j*a) % p == 0 and (e2+s*u-j*a) % p == 0
            and (s+g+j) % p == 0 and j+sum(counts) == 6*q)


def run(dp_limit: int, certificate_limit: int) -> dict:
    digest = hashlib.sha256()
    counts = {"fiber_maxima": 0, "plane_depth_points": 0, "singleton_rows": 0,
              "one_value_extension_rows": 0, "explicit_certificates": 0,
              "sharp_extension_controls": 0, "missing_s_rejected": 0,
              "wrong_rounding_rejected": 0, "wrong_envelope_detected": 0, "capacity_bound_rows": 0,
              "lower_overlap_survivor_families": 0}
    moduli = [p for p in primes(dp_limit) if p >= 7]
    require(any(p >= 13 and p % 4 == 1 for p in moduli), "DP domain misses sharp theorem")
    for p in moduli:
        h = (p-1)//2
        m = 3*h+1
        for k, dp, zero_best in donor_tables(p):
            for c in range(p):
                actual = max(dp[encode(p, (a, -a, c))] for a in range(p))
                expected = envelope(p, k, c)
                require(actual == expected, f"fiber mismatch {(p,k,c,actual,expected)}")
                counts["fiber_maxima"] += 1
                counts["plane_depth_points"] += p
                digest.update(f"E:{p},{k},{c}:{actual}\n".encode())
                if c == p-1:
                    counts["wrong_envelope_detected"] += actual != 2*p-k+1
            overlap = k-2
            for a in range(p):
                for kap in range(p):
                    depth = dp[encode(p, (-a, a, -kap))]
                    if 1+depth >= m:
                        require(1 <= kap <= h+1-overlap, f"singleton mismatch {(p,k,a,kap)}")
                    counts["singleton_rows"] += 1
            require(zero_best >= 2*p-k, f"pure donor lower bound {(p,k,zero_best)}")
            for a in range(1, p):
                least = min(j+dp[encode(p, (-j*a, j*a, -j))] for j in range(1, p))
                require(least >= 2*p-k, f"capacity lower bound {(p,k,a,least)}")
                counts["capacity_bound_rows"] += p-1
                if k <= h+1:
                    require(min(least, zero_best) >= m, "lower-overlap barrier failure")
                    counts["lower_overlap_survivor_families"] += 1
                digest.update(f"L:{p},{k},{a}:{least}\n".encode())
            if p % 4 != 1 or p < 13 or k != h+2:
                continue
            q = (p-1)//4
            require(zero_best == m, f"donor min-zero-sum mismatch {p}:{zero_best}")
            for a in range(p):
                alpha = min(a, p-a)
                for kap in range(p):
                    shortest = zero_best
                    for t in range(1, p):
                        shortest = min(shortest, t+dp[encode(p, (-t*a, t*a, -t*kap))])
                        predicted = (kap == 1 and ((a == 0 and t == 1)
                                     or (a != 0 and t*alpha <= q)))
                        require((shortest >= m) == predicted,
                                f"extension mismatch {(p,a,kap,t,shortest,predicted)}")
                        counts["one_value_extension_rows"] += 1
                        digest.update(f"X:{p},{a},{kap},{t}:{shortest}\n".encode())
            # Positive controls: the boundary extension really is allowed;
            # adding one occurrence crosses it and must create a short zero-sum.
            scores = [j+dp[encode(p, (-j, j, -j))] for j in range(1, q+2)]
            require(min([zero_best]+scores[:q]) == m, f"sharp positive control {p}")
            require(min([zero_best]+scores) == m-1, f"one-extra-copy control {p}")
            counts["sharp_extension_controls"] += 1
    cert_moduli = [p for p in primes(certificate_limit) if p >= 13 and p % 4 == 1]
    for p in cert_moduli:
        q = (p-1)//4
        for a in range(1, p):
            j, resource = certificate(p, a)
            require(valid_certificate(p, a, j, resource), f"bad certificate {(p,a,j,resource)}")
            counts["explicit_certificates"] += 1
            digest.update(f"W:{p},{a},{j}:{resource}\n".encode())
            require(not valid_certificate(p, a, j, resource, s_cap=2*q+1),
                    "resource mutation unexpectedly accepted")
            counts["missing_s_rejected"] += 1
        # a=1: dropping +1 from floor(q/alpha)+1 leaves a negative e2 count.
        j_bad = q
        big_p = (-j_bad) % p
        bad = (big_p-q-1, p-big_p-q-1, 2*q+2, 2*q-j_bad-1)
        require(not valid_certificate(p, 1, j_bad, bad), "rounding mutation accepted")
        counts["wrong_rounding_rejected"] += 1
    require(all(counts[name] > 0 for name in counts), "vacuous test family")
    return {"status": "PASS", "authority": "bounded regression; proofs in companion note",
            "dp_prime_limit": dp_limit, "dp_primes": moduli,
            "certificate_prime_limit": certificate_limit,
            "certificate_prime_count": len(cert_moduli), "counts": counts,
            "transcript_sha256": digest.hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dp-limit", type=int, default=31)
    parser.add_argument("--certificate-limit", type=int, default=1009)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(13 <= args.dp_limit <= 101, "dp-limit must lie in [13,101]")
    require(args.certificate_limit >= 13, "certificate-limit must be >=13")
    report = run(args.dp_limit, args.certificate_limit)
    if args.dp_limit == 31 and args.certificate_limit == 1009:
        require(report["transcript_sha256"] ==
                "02f6e745444639728c6389482d2bf43fe287e1c8f269f5ffab76cece4961d331",
                "default regression transcript changed")
        require(report["counts"]["fiber_maxima"] == 1585 and
                report["counts"]["one_value_extension_rows"] == 30200 and
                report["counts"]["explicit_certificates"] == 37552,
                "default coverage counts changed")
    text = json.dumps(report, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
