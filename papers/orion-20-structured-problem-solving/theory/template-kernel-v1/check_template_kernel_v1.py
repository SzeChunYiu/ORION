#!/usr/bin/env python3
"""Exhaustive regression for ORION20.TEMPLATE_KERNEL_QUOTIENT.v1."""
from itertools import product

TRIPLES = list(product((0, 1), repeat=3))


def bit(code, x, y):
    return (code >> ((x << 1) | y)) & 1


def template_code(code):
    out = 0
    for i, (x, y, z) in enumerate(TRIPLES):
        value = bit(code, x, y) ^ bit(code, x, z) ^ bit(code, y, z)
        out |= value << i
    return out


def majority_code():
    out = 0
    for i, (x, y, z) in enumerate(TRIPLES):
        out |= (1 if x + y + z >= 2 else 0) << i
    return out


def main():
    # Linearity over F_2.
    for p in range(16):
        for q in range(16):
            assert template_code(p ^ q) == (template_code(p) ^ template_code(q))

    kernel = [p for p in range(16) if template_code(p) == 0]
    assert kernel == [0, 6]  # 6 is x XOR y in the frozen truth-table convention.

    fibres = {}
    for p in range(16):
        fibres.setdefault(template_code(p), []).append(p)
    assert len(fibres) == 8
    expected = [[0, 6], [1, 7], [2, 4], [3, 5], [8, 14], [9, 15], [10, 12], [11, 13]]
    assert sorted(fibres.values()) == expected
    assert all(template_code(p) == template_code(p ^ 6) for p in range(16))

    preimage = [p for p in range(16) if template_code(p) == majority_code()]
    assert preimage == [8, 14]

    print(
        "ORION20_TEMPLATE_KERNEL_V1_PASS "
        "functions=16 image=8 kernel=0,6 fibres=8 majority_preimage=8,14"
    )


if __name__ == "__main__":
    main()
