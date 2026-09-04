#!/usr/bin/env python3
"""Regression for the a=2 maximal-overlap standard-family theorem."""
from __future__ import annotations

import hashlib
import json
from math import gcd


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def envelope(p: int, w: int, C: int) -> int:
    H = (p - 1) // 2
    if w <= H - 1:
        if C <= 2:
            return p + w
        if C <= p - 2:
            return p + w + C - 2
        return 2 * p - 2 if w == 0 else 2 * p + w - 3
    if w == H:
        if C == 0:
            return p + H
        if C <= p - 2:
            return H + C
        return 2 * p + H - 3
    if w <= p - 2:
        if C == 0:
            return p + w
        if C <= 2:
            return w + 1
        return w + C - 1
    if C == 0:
        return p - 1
    if C <= 2:
        return p
    return p + C - 2


def exact_depth(p: int, P: int, Q: int, C: int) -> int:
    H = (p - 1) // 2
    u = H + 1
    values: list[int] = []
    for k in (0, 1, 2):
        g_count = (C - k) % p
        if g_count > p - 2:
            continue
        values.append((P - k * u) % p + (Q - k * u) % p + g_count + k)
    assert values
    return min(values)


def inverse_quarter_selector(p: int, b: int) -> tuple[str, int, int, int, int]:
    H = (p - 1) // 2
    q, a = divmod(p, b)
    if q == 2 and b % 4 == 1:
        k = (b + 1) // 2
        w = (k * p + b - 1) // b
        j = b * w - k * p
        assert w == H + 2
        assert j == (b - a) // 2
        case = "q2_b1_half"
    elif q == 2 and b % 4 == 3:
        k = (b + 1) // 4
        w = (k * p + b - 1) // b
        j = b * w - k * p
        assert w == H // 2 + 1
        assert j == (b - a) // 4
        case = "q2_b3_quarter"
    else:
        k = (b + 3) // 4
        w0 = (k * p + b - 1) // b
        j0 = b * w0 - k * p
        j = b - j0
        w = p + 1 - w0
        case = "qge3_complement"
    return case, q, a, j, w


def mutated_complement(p: int, b: int, k: int | None = None) -> tuple[int, int]:
    if k is None:
        k = (b + 3) // 4
    w0 = (k * p + b - 1) // b
    j0 = b * w0 - k * p
    return b - j0, p + 1 - w0


def mutated_primary(p: int, b: int) -> tuple[int, int]:
    k = (b + 3) // 4
    w = (k * p + b - 1) // b
    return b * w - k * p, w


def selected_score_valid(p: int, b: int, j: int, w: int) -> bool:
    H = (p - 1) // 2
    r = (p - b) // 2
    m = 3 * H + 1
    if not (1 <= j <= r and 0 <= w < p):
        return False
    C = (w - 2 * j) % p
    return j + envelope(p, w, C) < m


def selector_sweep(limit: int, require_prime: bool) -> dict[str, object]:
    moduli = 0
    rows = 0
    case_counts: dict[str, int] = {}
    min_availability = 10**9
    min_score_margin = 10**9
    no_half_failures = 0
    primary_failures = 0
    floor_failures = 0
    transcript = hashlib.sha256()

    for p in range(5, limit + 1, 4):
        if require_prime and not is_prime(p):
            continue
        moduli += 1
        H = (p - 1) // 2
        m = 3 * H + 1
        for b in range(3, H, 2):
            if gcd(p, b) != 1:
                continue
            r = (p - b) // 2
            delta = pow(b, -1, p)
            case, q, a, j, w = inverse_quarter_selector(p, b)
            assert w == (j * delta) % p
            C = w - 2 * j
            assert 1 <= j <= r
            assert 0 <= C < p
            score = j + envelope(p, w, C)
            assert score < m, (p, b, case, q, a, j, w, C, score, m)

            rows += 1
            case_counts[case] = case_counts.get(case, 0) + 1
            min_availability = min(min_availability, r - j)
            min_score_margin = min(min_score_margin, m - score)
            transcript.update(f"{p},{b},{case},{q},{a},{j},{w},{C},{score}\n".encode())

            # Hostile 1: omit the exceptional half-step and always complement.
            jm, wm = mutated_complement(p, b)
            if not selected_score_valid(p, b, jm, wm):
                no_half_failures += 1

            if q >= 3:
                # Hostile 2: use the primary quarter point, not its complement.
                jm, wm = mutated_primary(p, b)
                if not selected_score_valid(p, b, jm, wm):
                    primary_failures += 1

                # Hostile 3: round b/4 down.
                k_floor = b // 4
                if k_floor >= 1:
                    jm, wm = mutated_complement(p, b, k_floor)
                    if not selected_score_valid(p, b, jm, wm):
                        floor_failures += 1

    assert no_half_failures > 0
    assert primary_failures > 0
    assert floor_failures > 0
    return {
        "moduli": moduli,
        "rows": rows,
        "case_counts": case_counts,
        "minimum_power_availability_slack": min_availability,
        "minimum_score_margin": min_score_margin,
        "transcript_sha256": transcript.hexdigest(),
        "no_half_mutation_failures": no_half_failures,
        "primary_quarter_mutation_failures": primary_failures,
        "floor_quarter_mutation_failures": floor_failures,
    }


def standard_selector(p: int, kappa: int, r: int) -> tuple[str, int | None, int | None, int | None]:
    H = (p - 1) // 2
    delta = H * pow(r, -1, p) % p
    if kappa == 1:
        j = r if r < H else 1
        kind = "k1_r" if r < H else "k1_center"
    else:
        if r < H // 2:
            j, kind = r, "k2_lower"
        elif r == H // 2:
            j, kind = 1, "k2_half"
        elif r < H:
            b = p - 2 * r
            case, _, _, j, w = inverse_quarter_selector(p, b)
            assert w == j * delta % p
            return "k2_" + case, j, w, (w - 2 * j) % p
        else:
            return "k2_center", None, None, None
    w = j * delta % p
    return kind, j, w, (w - kappa * j) % p


def exact_standard_sweep(limit: int) -> dict[str, object]:
    primes = 0
    rows = 0
    parameters = 0
    kind_counts: dict[str, int] = {}
    minimum_margin = 10**9
    maximum_actual_minus_envelope = -10**9
    transcript = hashlib.sha256()

    for p in range(13, limit + 1, 4):
        if not is_prime(p):
            continue
        primes += 1
        H = (p - 1) // 2
        u = H + 1
        m = 3 * H + 1
        s = (u, u, 1)

        for kappa in (1, 2):
            for r in range(1, H + 1):
                kind, j, w, C = standard_selector(p, kappa, r)
                kind_counts[kind] = kind_counts.get(kind, 0) + 1
                rows += 1

                if kind != "k2_center":
                    assert j is not None and w is not None and C is not None
                    envelope_score = j + envelope(p, w, C)
                    assert envelope_score < m
                    minimum_margin = min(minimum_margin, m - envelope_score)

                    for A in range(p):
                        y = (A, (-A) % p, kappa)
                        delta = H * pow(r, -1, p) % p
                        x = tuple((y[i] - delta * s[i]) % p for i in range(3))
                        target = tuple((-j * x[i]) % p for i in range(3))
                        actual_score = j + exact_depth(p, *target)
                        assert actual_score <= envelope_score < m
                        maximum_actual_minus_envelope = max(
                            maximum_actual_minus_envelope,
                            actual_score - envelope_score,
                        )
                        parameters += 1
                        transcript.update(f"{p},{kappa},{r},{A},{j},{actual_score}\n".encode())
                else:
                    assert kappa == 2 and r == H
                    for A in range(p):
                        B = (A - u) % p
                        R = H * B % p
                        j0 = 2 if R in (0, u) else H
                        y = (A, (-A) % p, 2)
                        x = tuple((y[i] - s[i]) % p for i in range(3))
                        target = tuple((-j0 * x[i]) % p for i in range(3))
                        actual_score = j0 + exact_depth(p, *target)
                        assert actual_score < m
                        minimum_margin = min(minimum_margin, m - actual_score)
                        parameters += 1
                        transcript.update(f"{p},{kappa},{r},{A},{j0},{actual_score}\n".encode())

    return {
        "primes": primes,
        "rows": rows,
        "standard_parameters": parameters,
        "kind_counts": kind_counts,
        "minimum_score_margin": minimum_margin,
        "maximum_actual_minus_envelope": maximum_actual_minus_envelope,
        "transcript_sha256": transcript.hexdigest(),
    }


def main() -> None:
    prime_selector = selector_sweep(1009, True)
    broad_selector = selector_sweep(5001, False)
    standard = exact_standard_sweep(401)

    assert prime_selector == {
        "moduli": 81,
        "rows": 9308,
        "case_counts": {
            "qge3_complement": 6193,
            "q2_b1_half": 1557,
            "q2_b3_quarter": 1558,
        },
        "minimum_power_availability_slack": 2,
        "minimum_score_margin": 1,
        "transcript_sha256": "1ed8d8291eeb57ebfd245f52a9a405f9617609495e16c5fa0f566622458ae619",
        "no_half_mutation_failures": 2221,
        "primary_quarter_mutation_failures": 3167,
        "floor_quarter_mutation_failures": 1320,
    }
    assert broad_selector == {
        "moduli": 1250,
        "rows": 632434,
        "case_counts": {
            "qge3_complement": 421475,
            "q2_b1_half": 105484,
            "q2_b3_quarter": 105475,
        },
        "minimum_power_availability_slack": 2,
        "minimum_score_margin": 1,
        "transcript_sha256": "069873ab54fb05ea8b95ecfdcac5a9729fa3c7221272b0e545c75eddfaadf9a2",
        "no_half_mutation_failures": 150573,
        "primary_quarter_mutation_failures": 169937,
        "floor_quarter_mutation_failures": 42810,
    }
    assert standard == {
        "primes": 37,
        "rows": 7292,
        "standard_parameters": 1977484,
        "kind_counts": {
            "k1_r": 3609,
            "k1_center": 37,
            "k2_lower": 1786,
            "k2_half": 37,
            "k2_q2_b1_half": 301,
            "k2_qge3_complement": 1185,
            "k2_center": 37,
            "k2_q2_b3_quarter": 300,
        },
        "minimum_score_margin": 1,
        "maximum_actual_minus_envelope": 0,
        "transcript_sha256": "f73de308c16e89f6f031e3597ece14f80e8ad8101099fb4b55485fe11347604d",
    }

    print(json.dumps({
        "status": "A2_MAXIMAL_OVERLAP_STANDARD_FAMILIES_GREEN",
        "prime_selector": prime_selector,
        "broad_coprime_selector": broad_selector,
        "exact_standard_family_replay": standard,
        "authority": "exact fiber envelope plus inverse-quarter selector; exhaustive checks are regression and hostile controls",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
