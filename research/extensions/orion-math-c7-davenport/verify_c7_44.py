#!/usr/bin/env python3
"""Exact bounded verification for the first C_7^3 Davenport frontier atom.

This file deliberately uses two different exact short-zero tests:

1. a term-by-term dynamic program of reachable sums by weight;
2. a support-multiplicity enumeration of all submultisets of size at most 7.

It also reconstructs the witness from the Edel--Elsholtz--Geroldinger--
Kubertin--Rackham V3 support, checks hostile controls, and certifies an explicit
five-block zero-sum packing.  No claim of literature priority is made here.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from typing import Iterable, Iterator, Sequence

P = 7
ZERO = (0, 0, 0)
Vec = tuple[int, int, int]

# Lemma 3.4 support in Edel--Elsholtz--Geroldinger--Kubertin--Rackham.
DONOR_V3_SUPPORT: tuple[Vec, ...] = (
    (1, 0, 0),
    (1, 0, 2),
    (1, 2, 0),
    (1, 2, 2),
    (2, 0, 1),
    (2, 1, 0),
    (2, 1, 2),
    (2, 2, 1),
    (3, 1, 1),
)
ANCHOR: Vec = (2, 0, 1)

# Delete the anchor's six copies from V3=(V3_support)^6 and translate the
# remaining terms by -ANCHOR, as in the donor translation lemma.
EXPECTED_TRANSLATED_SUPPORT: tuple[Vec, ...] = (
    (6, 0, 6),
    (6, 0, 1),
    (6, 2, 6),
    (6, 2, 1),
    (0, 1, 6),
    (0, 1, 1),
    (0, 2, 0),
    (1, 1, 0),
)
DONOR_DERIVED_48_COUNTS: tuple[int, ...] = (6, 6, 6, 6, 6, 6, 6, 6)

# Remove one copy of (0,2,0) and three copies of (1,1,0).  Their sum is
# (3,5,0), exactly the sum of the 48-term translated sequence, so the remainder
# is total-zero and has length 44.
WITNESS_44_COUNTS: tuple[int, ...] = (6, 6, 6, 6, 6, 6, 5, 3)

# Five disjoint nonempty zero-sum subsequences, represented as multiplicities
# against EXPECTED_TRANSLATED_SUPPORT.  Their lengths are 8,8,8,8,12 and they
# cover WITNESS_44_COUNTS exactly.
PACKING_5: tuple[tuple[int, ...], ...] = (
    (0, 0, 0, 1, 1, 0, 5, 1),
    (0, 1, 0, 0, 0, 6, 0, 1),
    (0, 4, 3, 0, 1, 0, 0, 0),
    (3, 1, 0, 3, 1, 0, 0, 0),
    (3, 0, 3, 2, 3, 0, 0, 1),
)


def add(a: Vec, b: Vec) -> Vec:
    return tuple((x + y) % P for x, y in zip(a, b))  # type: ignore[return-value]


def neg(a: Vec) -> Vec:
    return tuple((-x) % P for x in a)  # type: ignore[return-value]


def scale(c: int, a: Vec) -> Vec:
    return tuple((c * x) % P for x in a)  # type: ignore[return-value]


def sequence_sum(sequence: Iterable[Vec]) -> Vec:
    out = ZERO
    for v in sequence:
        out = add(out, v)
    return out


def expand(support: Sequence[Vec], counts: Sequence[int]) -> list[Vec]:
    if len(support) != len(counts):
        raise ValueError("support/count length mismatch")
    out: list[Vec] = []
    for v, count in zip(support, counts):
        if count < 0:
            raise ValueError("negative multiplicity")
        out.extend([v] * count)
    return out


def translate(v: Vec, anchor: Vec) -> Vec:
    return add(v, neg(anchor))


def short_zero_free_dp(sequence: Sequence[Vec], threshold: int = 7) -> bool:
    """Term-level exact DP: reachable group sums at each exact weight."""
    reachable: list[set[Vec]] = [set() for _ in range(threshold + 1)]
    reachable[0].add(ZERO)
    seen = 0
    for v in sequence:
        seen += 1
        for weight in range(min(threshold, seen), 0, -1):
            additions = {add(s, v) for s in reachable[weight - 1]}
            reachable[weight].update(additions)
    return all(ZERO not in reachable[weight] for weight in range(1, threshold + 1))


def _bounded_count_vectors(caps: Sequence[int], threshold: int) -> Iterator[tuple[int, ...]]:
    current = [0] * len(caps)

    def rec(i: int, used: int) -> Iterator[tuple[int, ...]]:
        if i == len(caps):
            if 1 <= used <= threshold:
                yield tuple(current)
            return
        for take in range(min(caps[i], threshold - used) + 1):
            current[i] = take
            yield from rec(i + 1, used + take)
        current[i] = 0

    yield from rec(0, 0)


def compressed(sequence: Sequence[Vec]) -> tuple[tuple[Vec, ...], tuple[int, ...]]:
    counts = Counter(sequence)
    support = tuple(sorted(counts))
    return support, tuple(counts[v] for v in support)


def short_zero_free_counts(sequence: Sequence[Vec], threshold: int = 7) -> bool:
    """Independent support-count enumeration of every small submultiset."""
    support, caps = compressed(sequence)
    for take in _bounded_count_vectors(caps, threshold):
        total = ZERO
        for v, count in zip(support, take):
            total = add(total, scale(count, v))
        if total == ZERO:
            return False
    return True


def multiset_sum(support: Sequence[Vec], counts: Sequence[int]) -> Vec:
    total = ZERO
    for v, count in zip(support, counts):
        total = add(total, scale(count, v))
    return total


def packing_certificate() -> dict[str, object]:
    block_lengths: list[int] = []
    block_sums: list[Vec] = []
    used = [0] * len(WITNESS_44_COUNTS)
    for block in PACKING_5:
        if len(block) != len(WITNESS_44_COUNTS):
            raise AssertionError("packing block width mismatch")
        length = sum(block)
        total = multiset_sum(EXPECTED_TRANSLATED_SUPPORT, block)
        if length <= 0 or total != ZERO:
            raise AssertionError("invalid zero-sum packing block")
        block_lengths.append(length)
        block_sums.append(total)
        for i, value in enumerate(block):
            used[i] += value
    if tuple(used) != WITNESS_44_COUNTS:
        raise AssertionError("packing does not exactly cover the witness")
    # The two independent short-zero checks certify that every nonempty
    # zero-sum subsequence has length >=8.  Hence six disjoint ones would require
    # at least 48 terms, impossible in length 44.  The explicit packing gives 5.
    return {
        "block_lengths": block_lengths,
        "block_sums": [list(v) for v in block_sums],
        "covers_witness": True,
        "lower_bound": 5,
        "upper_bound_from_min_block_length": 44 // 8,
        "exact_zz": 5,
    }


def canonical_witness() -> list[dict[str, object]]:
    return [
        {"vector": list(v), "multiplicity": m}
        for v, m in zip(EXPECTED_TRANSLATED_SUPPORT, WITNESS_44_COUNTS)
    ]


def verify() -> dict[str, object]:
    translated = tuple(
        translate(v, ANCHOR) for v in DONOR_V3_SUPPORT if v != ANCHOR
    )
    if translated != EXPECTED_TRANSLATED_SUPPORT:
        raise AssertionError("donor-derived translated support mismatch")

    seq48 = expand(EXPECTED_TRANSLATED_SUPPORT, DONOR_DERIVED_48_COUNTS)
    seq44 = expand(EXPECTED_TRANSLATED_SUPPORT, WITNESS_44_COUNTS)

    checks = {
        "derived_48_length": len(seq48) == 48,
        "derived_48_short_zero_free_dp": short_zero_free_dp(seq48),
        "derived_48_short_zero_free_counts": short_zero_free_counts(seq48),
        "witness_44_length": len(seq44) == 44,
        "witness_44_sum_zero": sequence_sum(seq44) == ZERO,
        "witness_44_short_zero_free_dp": short_zero_free_dp(seq44),
        "witness_44_short_zero_free_counts": short_zero_free_counts(seq44),
    }
    if not all(checks.values()):
        raise AssertionError(f"primary verification failed: {checks}")

    # Arithmetic provenance of the four deleted terms.
    sum48 = sequence_sum(seq48)
    deleted = [(0, 2, 0)] + [(1, 1, 0)] * 3
    deletion_check = {
        "sum_48": list(sum48),
        "deleted_sum": list(sequence_sum(deleted)),
        "matches": sum48 == sequence_sum(deleted) == (3, 5, 0),
    }
    if not deletion_check["matches"]:
        raise AssertionError("deletion arithmetic mismatch")

    # Hostile / polarity controls: each intentional corruption must be caught.
    seven_equal = [(6, 0, 6)] * 7
    opposite_pair = [(1, 0, 0), (6, 0, 0)]
    bad44_counts = (6, 6, 6, 6, 6, 6, 6, 2)  # length 44, wrong deletion/sum
    bad44 = expand(EXPECTED_TRANSLATED_SUPPORT, bad44_counts)
    hostile_controls = {
        "seven_equal_rejected_dp": not short_zero_free_dp(seven_equal),
        "seven_equal_rejected_counts": not short_zero_free_counts(seven_equal),
        "opposite_pair_rejected_dp": not short_zero_free_dp(opposite_pair),
        "opposite_pair_rejected_counts": not short_zero_free_counts(opposite_pair),
        "wrong_deletion_has_length_44": len(bad44) == 44,
        "wrong_deletion_rejected_by_sum": sequence_sum(bad44) != ZERO,
    }
    if not all(hostile_controls.values()):
        raise AssertionError(f"hostile control failed: {hostile_controls}")

    packing = packing_certificate()
    if packing["exact_zz"] != 5:
        raise AssertionError("packing diagnosis failed")

    witness = canonical_witness()
    witness_digest = hashlib.sha256(
        json.dumps(witness, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "schema": "ORION.C7CubedDavenportFrontierWitness.v1",
        "group": "C_7^3",
        "atom": "A7",
        "claim": (
            "There exists a length-44 total-zero sequence over C_7^3 with no "
            "nonempty zero-sum subsequence of length at most 7."
        ),
        "witness": witness,
        "witness_sha256": witness_digest,
        "checks": checks,
        "deletion_arithmetic": deletion_check,
        "hostile_controls": hostile_controls,
        "packing": packing,
        "derived_consequences": {
            "44_not_in_C0_C7cubed": True,
            "p5_length31_short_zero_reduction_direct_analogue_fails_at_p7": True,
            "this_witness_does_not_raise_D4_lower_bound": True,
            "reason": "the witness has exact zero-sum packing number zz=5",
        },
        "authority": {
            "bounded_fact": "MACHINE_CHECKED_BY_TWO_EXACT_ALGORITHMS",
            "donor_construction_priority": "DONOR_OWNED",
            "literature_priority_of_44_not_in_C0": "CANNOT_CHECK",
            "D4_C7cubed_exact_value": "OPEN",
        },
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
