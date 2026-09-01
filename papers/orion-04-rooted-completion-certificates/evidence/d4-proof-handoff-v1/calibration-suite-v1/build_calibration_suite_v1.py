#!/usr/bin/env python3
"""Freeze the small-instance calibration suite required before any D4 execution.

`PROOF_OBJECT_CONTRACT_V1.md` requires both lower-bound routes and the
construction verifier to be exercised on "a frozen suite of smaller instances
whose exact answers are already independently established", covering four control
kinds, with identities and expected answers frozen *before* the D4 outcome is
accessed.

The independently established answers are the published closed forms for rank
<= 2, which this file treats as ground truth and never re-derives from any ORION
search:

    D_k(C_n)          = k*n
    D_k(C_m (+) C_n)  = m + k*n - 1        for m | n

That is the whole point of the suite: the expected values come from outside every
implementation under test, so a route that agrees with them agrees with something
it could not have produced.

This script accesses no D4 outcome and grants no authority.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

SCHEMA = "ORION04.D4.CalibrationSuite.v1"


def d_k_cyclic(k: int, n: int) -> int:
    """D_k(C_n) = k*n. Published closed form; not derived here."""
    return k * n


def d_k_rank2(k: int, m: int, n: int) -> int:
    """D_k(C_m (+) C_n) = m + k*n - 1 for m | n. Published closed form."""
    if n % m:
        raise ValueError(f"closed form requires m | n, got m={m}, n={n}")
    return m + k * n - 1


def group_elements(orders: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [tuple(e) for e in itertools.product(*(range(o) for o in orders))]


def add(a: tuple[int, ...], b: tuple[int, ...], orders: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((x + y) % o for x, y, o in zip(a, b, orders))


def max_disjoint_zero_sums(seq: list[tuple[int, ...]], orders: tuple[int, ...]) -> int:
    """Exact maximum number of disjoint nonempty zero-sum subsequences.

    Brute force over subset partitions, deliberately: this is a *control*
    implementation for tiny instances, and its correctness must be obvious by
    inspection rather than argued. It is not used on D4 and must never be.
    """
    n = len(seq)
    if n > 12:
        raise ValueError("control implementation is for tiny instances only")
    zero = tuple(0 for _ in orders)

    zero_sum_masks = []
    for mask in range(1, 1 << n):
        total = zero
        for i in range(n):
            if mask >> i & 1:
                total = add(total, seq[i], orders)
        if total == zero:
            zero_sum_masks.append(mask)

    best = 0
    # depth-first packing of pairwise-disjoint zero-sum masks
    def pack(used: int, count: int, start: int) -> None:
        nonlocal best
        best = max(best, count)
        for j in range(start, len(zero_sum_masks)):
            m = zero_sum_masks[j]
            if m & used:
                continue
            pack(used | m, count + 1, j + 1)

    pack(0, 0, 0)
    return best


def build() -> dict:
    controls: list[dict] = []

    # --- known_constructible -------------------------------------------------
    # D_2(C_3) = 6, so a length-5 sequence exists with at most 1 disjoint
    # zero-sum subsequence. Witness: five copies of the generator 1.
    orders = (3,)
    seq = [(1,)] * 5
    observed = max_disjoint_zero_sums(seq, orders)
    controls.append({
        "control_kind": "known_constructible",
        "group": "C_3",
        "orders": list(orders),
        "k": 2,
        "closed_form_value": d_k_cyclic(2, 3),
        "closed_form": "D_k(C_n) = k*n",
        "sequence": [list(x) for x in seq],
        "length": len(seq),
        "expected_max_disjoint_zero_sums": 1,
        "observed_max_disjoint_zero_sums": observed,
        "agrees": observed == 1,
        "why": "length 5 = D_2(C_3) - 1, so some sequence achieves at most k-1 = 1.",
    })

    # --- known_impossible ----------------------------------------------------
    # At length D_k every sequence has k disjoint zero-sums. D_2(C_3) = 6, so no
    # length-6 sequence over C_3 can have fewer than 2. Six generators is the
    # hardest such sequence and must still reach 2.
    seq = [(1,)] * 6
    observed = max_disjoint_zero_sums(seq, orders)
    controls.append({
        "control_kind": "known_impossible",
        "group": "C_3",
        "orders": list(orders),
        "k": 2,
        "closed_form_value": d_k_cyclic(2, 3),
        "closed_form": "D_k(C_n) = k*n",
        "sequence": [list(x) for x in seq],
        "length": len(seq),
        "expected_min_disjoint_zero_sums": 2,
        "observed_max_disjoint_zero_sums": observed,
        "agrees": observed >= 2,
        "why": "length 6 = D_2(C_3); a witness with fewer than 2 is impossible.",
    })

    # --- symmetry_rich -------------------------------------------------------
    # C_2 (+) C_2: every non-identity element is an involution and the
    # automorphism group permutes them fully, so canonicalization has real work.
    # D_1(C_2 (+) C_2) = 2 + 1*2 - 1 = 3.
    orders = (2, 2)
    seq = [(1, 0), (0, 1)]
    observed = max_disjoint_zero_sums(seq, orders)
    controls.append({
        "control_kind": "symmetry_rich",
        "group": "C_2 (+) C_2",
        "orders": list(orders),
        "k": 1,
        "closed_form_value": d_k_rank2(1, 2, 2),
        "closed_form": "D_k(C_m (+) C_n) = m + k*n - 1",
        "sequence": [list(x) for x in seq],
        "length": len(seq),
        "expected_max_disjoint_zero_sums": 0,
        "observed_max_disjoint_zero_sums": observed,
        "agrees": observed == 0,
        "why": "length 2 = D_1 - 1; the two distinct involutions sum to the third "
               "non-identity element, so no nonempty subsequence sums to zero.",
    })

    # --- malformed_proof_object ---------------------------------------------
    # A proof object asserting a value that contradicts the closed form. A route
    # that accepts this is broken; the suite exists to make that visible.
    controls.append({
        "control_kind": "malformed_proof_object",
        "group": "C_3",
        "orders": [3],
        "k": 2,
        "closed_form_value": d_k_cyclic(2, 3),
        "closed_form": "D_k(C_n) = k*n",
        "asserted_value_in_malformed_object": 7,
        "expected_verdict": "REJECT",
        "why": "asserts D_2(C_3) = 7 against the closed form's 6. Any route that "
               "accepts it is not checking the value it claims to check.",
    })

    suite = {
        "schema": SCHEMA,
        "paper_id": "ORION-04",
        "purpose": "Frozen small-instance calibration required by PROOF_OBJECT_CONTRACT_V1 "
                   "before any D4 execution.",
        "ground_truth_source": "Published closed forms for rank <= 2. Not derived from any "
                               "ORION search implementation, which is what makes them external.",
        "d4_outcome_accessed": False,
        "scientific_authority_delta": "NONE",
        "controls": controls,
        "all_controls_agree": all(c.get("agrees", True) for c in controls),
    }
    payload = json.dumps(suite, indent=2, sort_keys=True)
    suite["suite_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    return suite


if __name__ == "__main__":
    s = build()
    out = Path(__file__).with_name("CALIBRATION_SUITE_V1.json")
    out.write_text(json.dumps(s, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "controls": len(s["controls"]),
        "all_controls_agree": s["all_controls_agree"],
        "d4_outcome_accessed": s["d4_outcome_accessed"],
        "suite_sha256": s["suite_sha256"],
    }, indent=2, sort_keys=True))
