#!/usr/bin/env python3
"""Independent sanity checker for Q1's analytic R6S proof.

Deliberately imports no ORION quantum/compiler module.  It reconstructs the
phase-ignored one-qubit Pauli algebra from (x,z) bits and checks only the two
finite statements that underlie the human proof note:

1. changing one Restore slot by zeroing a nonidentity frame letter raises the
   frozen F3 cost by at most 2;
2. an odd-alpha F_2^2 class multiset of size >=3 always has a nonempty proper
   zero-sum subset of size <=2, while support 2 has exactly the four declared
   failing ordered patterns.

This is a regression/sanity check, not an independent external peer review.
"""

from __future__ import annotations

import itertools
import json

# I, X, Y, Z in a conventional binary symplectic encoding.  Multiplication
# below ignores the global Pauli phase, which is all the support/F3 argument
# requires.
BITS = ((0, 0), (1, 0), (1, 1), (0, 1))


def mul(a: int, b: int) -> int:
    xa, za = BITS[a]
    xb, zb = BITS[b]
    return BITS.index((xa ^ xb, za ^ zb))


def wt(a: int) -> int:
    return int(a != 0)


def f3(a: int, b: int, c: int) -> int:
    if a == b == c != 0:
        return 1
    return wt(a) + wt(b) + wt(c)


def check_restore_lemma() -> dict:
    # Relevant mathematical domain: f nonidentity; target p and the two other
    # Restore-slot letters u,v arbitrary.  The production 18,432-case sweep
    # multiplies this by partner/tag/slot/refund bookkeeping that does not
    # change delta_F3.
    hist: dict[int, int] = {}
    max_delta = -10**9
    max_cases = []
    checked = 0
    for f in (1, 2, 3):
        for p, u, v in itertools.product(range(4), repeat=3):
            old = mul(p, f)
            new = p
            delta = f3(new, u, v) - f3(old, u, v)
            checked += 1
            hist[delta] = hist.get(delta, 0) + 1
            max_delta = max(max_delta, delta)
            if delta == 2:
                max_cases.append((f, p, u, v, old, new))
    assert checked == 192
    assert max_delta == 2
    assert hist == {-2: 6, -1: 48, 0: 84, 1: 48, 2: 6}
    return {
        "relevant_cases": checked,
        "max_delta_f3": max_delta,
        "delta_histogram": {str(k): hist[k] for k in sorted(hist)},
        "max_delta_case_count": len(max_cases),
    }


def zero_sum_subset_exists(classes: tuple[int, ...]) -> bool:
    w = len(classes)
    # class code = 2*alpha + beta.  In F_2^2 a zero singleton is 0 and
    # equal pairs sum to zero.
    if w > 1 and any(c == 0 for c in classes):
        return True
    if w > 2:
        for i in range(w):
            for j in range(i + 1, w):
                if classes[i] == classes[j]:
                    return True
    return False


def check_class_lemma() -> dict:
    per_w = {}
    observed_w2 = []
    for w in range(2, 9):
        checked = 0
        failures = []
        for classes in itertools.product(range(4), repeat=w):
            alpha_sum = sum(c >> 1 for c in classes) % 2
            if alpha_sum != 1:
                continue
            checked += 1
            if not zero_sum_subset_exists(classes):
                failures.append(classes)
        if w == 2:
            observed_w2 = failures
        else:
            assert not failures
        per_w[str(w)] = {
            "odd_alpha_tuples": checked,
            "failures": len(failures),
        }
    predicted = [(1, 2), (1, 3), (2, 1), (3, 1)]
    assert sorted(observed_w2) == predicted
    return {
        "per_w": per_w,
        "w2_failures": [list(x) for x in sorted(observed_w2)],
        "w3_to_w8_failure_count": 0,
    }


def main() -> None:
    result = {
        "schema": "ORION.Q1.IndependentHumanProofSanity.v1",
        "date": "2026-08-22",
        "implementation": (
            "standalone phase-ignored one-qubit Pauli implementation in "
            "papers/orion-05-tare-expressivity/independent_human_proof_sanity.py"
        ),
        "orion_quantum_imports": False,
        "restore_lemma": check_restore_lemma(),
        "class_lemma": check_class_lemma(),
        "status": "PASS",
        "authority": (
            "standalone no-ORION-import finite-core sanity only; a matching CI "
            "result is not external peer review, novelty authority, or physical "
            "quantum authority"
        ),
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
