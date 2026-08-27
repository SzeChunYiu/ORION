#!/usr/bin/env python3
"""Independent standard-library check for Q1 R11 pair-count candidate.

This file imports no ORION scientific implementation. It brute-forces the
phase-ignored Pauli alphabet for n <= 5 and compares the exact ordered
anticommuting-pair count with the closed form.
"""

from itertools import product


def support(p):
    return sum(x != 0 for x in p)


def anticommutes(p, q):
    # 0=I, 1=X, 2=Y, 3=Z. Distinct nonidentity one-qubit Paulis anticommute.
    return sum(1 for a, b in zip(p, q) if a and b and a != b) % 2 == 1


def paulis_support_le_2(n):
    return [
        p
        for p in product(range(4), repeat=n)
        if 1 <= support(p) <= 2
    ]


def brute_count(n):
    ps = paulis_support_le_2(n)
    return sum(1 for p in ps for q in ps if anticommutes(p, q))


def closed_form(n):
    return 54 * n**3 - 108 * n**2 + 60 * n


def raw_pauli_count(n):
    return 3 * n + 9 * n * (n - 1) // 2


def main():
    expected = {1: 6, 2: 120, 3: 666, 4: 1968, 5: 4350}
    for n in range(1, 6):
        m = raw_pauli_count(n)
        brute = brute_count(n)
        formula = closed_form(n)
        assert brute == formula == expected[n], (n, brute, formula, expected[n])
        assert brute <= m * m
        print(f"n={n} M2={m} ordered_anticommuting_pairs={brute} formula={formula}")

    # Edge/hostile checks: formula is positive and integral in the tested range;
    # anticommutation is symmetric but the registered object is ordered.
    assert closed_form(1) == 6
    assert closed_form(2) == 120
    print("Q1_R11_PAIR_COUNT_SMALL_N_EXHAUSTIVE_PASS")


if __name__ == "__main__":
    main()
