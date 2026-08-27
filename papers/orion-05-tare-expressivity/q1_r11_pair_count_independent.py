#!/usr/bin/env python3
"""Independent finite check for the Q1 support<=2 anticommuting-pair count.

No ORION imports. Phase-ignored Pauli letters are encoded as (x,z) in F_2^2.
This corroborates, but does not prove, the analytic formula.
"""
from itertools import product

LETTER = {
    0: (0, 0),  # I
    1: (1, 0),  # X
    2: (0, 1),  # Z
    3: (1, 1),  # Y
}


def support(p):
    return sum(v != 0 for v in p)


def symp(a, b):
    s = 0
    for u, v in zip(a, b):
        x, z = LETTER[u]
        xp, zp = LETTER[v]
        s ^= (x & zp) ^ (z & xp)
    return s


def support2_paulis(n):
    return [p for p in product(range(4), repeat=n) if 1 <= support(p) <= 2]


def pair_formula(n):
    return 54 * n**3 - 108 * n**2 + 60 * n


def wt1_partner_count(n):
    return 6 * n - 4


def wt2_partner_count(n):
    return 12 * n - 16


def main():
    for n in range(1, 7):
        ps = support2_paulis(n)
        total = sum(symp(a, b) == 1 for a in ps for b in ps)
        assert total == pair_formula(n), (n, total, pair_formula(n))

        for a in ps:
            partners = sum(symp(a, b) == 1 for b in ps)
            expected = wt1_partner_count(n) if support(a) == 1 else wt2_partner_count(n)
            assert partners == expected, (n, a, partners, expected)

        # Hostile wrong-count controls.
        m = 3 * n + 9 * n * (n - 1) // 2
        assert total != m * m  # anticommutation is a real constraint
        assert total % 2 == 0  # ordered relation is symmetric
        assert total // 2 != total  # unordered count is not the registered object

        print(
            f"n={n} support<=2={len(ps)} ordered_anticommuting={total} "
            f"formula={pair_formula(n)}"
        )

    print("Q1_PAIR_COUNT_FINITE_CHECK_PASS")


if __name__ == "__main__":
    main()
