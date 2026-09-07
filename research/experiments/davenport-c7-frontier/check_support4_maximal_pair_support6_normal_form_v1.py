#!/usr/bin/env python3
"""Regression for the exact support-six normal form in support-four maximal corridors."""

from __future__ import annotations

import json


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


def main() -> None:
    primes = [p for p in range(5, 402) if is_prime(p)]
    checked = 0
    first_corridor_rows = 0
    heavy_projective_rows = 0
    light_endpoint_rows = 0

    for p in primes:
        for j in range(1, (p + 1) // 4 + 1):
            b = (p + 1) // 2 - j
            vlen = p + b
            H = p + b - 1
            pair_plane_cap = 4 * p - 3 - H
            u_plane_budget = pair_plane_cap - vlen

            assert j <= b
            assert u_plane_budget == p + 2 * j - 3
            assert H >= p

            for a in range(1, (p - 1) // 2 + 1):
                checked += 1
                light = a
                heavy = p - a

                # Exact support-six overlap capacities.
                cap_light = p - 1 - a
                cap_heavy = a - 1
                assert cap_light >= 0 and cap_heavy >= 0
                assert cap_light + cap_heavy == p - 2

                new_if_light = vlen - cap_light
                new_if_heavy = vlen - cap_heavy
                new_if_both = vlen - (cap_light + cap_heavy)
                assert new_if_light == b + a + 1
                assert new_if_heavy == p + b - a + 1
                assert new_if_both == b + 2

                # Heavy-share-only rank-two plane cannot contain a saturated U point.
                assert heavy > 2 * j - 2
                assert heavy + (p - 1) > u_plane_budget

                # Light-share-only saturated incidence threshold is exact.
                assert (light + (p - 1) <= u_plane_budget) == (a <= 2 * j - 2)

                # A rank-two plane containing both low U points needs j>=2.
                assert (p <= u_plane_budget) == (j >= 2)

                # Heavy-share-only new mass forces two distinct projective directions for j<=2.
                assert new_if_heavy >= p + 2 - j
                if j <= 2:
                    heavy_projective_rows += 1
                    assert new_if_heavy >= p

                # Light-share endpoint in j=1 reaches the same p-term threshold exactly at max a.
                if j == 1 and a == (p - 1) // 2:
                    light_endpoint_rows += 1
                    assert new_if_light == p

                if j == 1:
                    first_corridor_rows += 1
                    assert u_plane_budget == p - 1
                    assert light + heavy == p > u_plane_budget
                    assert light + (p - 1) > u_plane_budget
                    assert heavy + (p - 1) > u_plane_budget

    print(
        json.dumps(
            {
                "status": "SUPPORT4_MAXIMAL_PAIR_SUPPORT6_NORMAL_FORM_GREEN",
                "checked_primes": len(primes),
                "max_prime": primes[-1],
                "checked_type_corridor_rows": checked,
                "first_corridor_rows": first_corridor_rows,
                "heavy_share_j_le_2_rows": heavy_projective_rows,
                "light_share_endpoint_rows": light_endpoint_rows,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
