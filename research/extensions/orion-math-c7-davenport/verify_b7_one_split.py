#!/usr/bin/env python3
"""Exact finite closure of the first B7 neighbourhood around the canonical
Freeze--Schmid-derived C_7^3 extremal witness.

The bounded question here is *not* global B7.  It is the one-edit neighbourhood:
replace one term v of a fixed length-43 zero-sum sequence B43 with two nonzero
terms a,b satisfying a+b=v.  There are 7 support types and 171 unordered
nonzero splits per support type, hence 1197 labelled one-term split moves.

The verifier proves:

* B43 is total-zero and has exact zero-sum packing number zz(B43)=4;
* every one of the 1197 split sequences has an explicit 5-block zero-sum
  partition;
* no split sequence can have six blocks, because merging the two distinct
  blocks containing a and b would give five blocks in B43.

Hence every labelled one-term split has exact packing number five and none is a
B7 witness with zz<=4.

The speed-up is mathematical rather than heuristic.  We enumerate the complete
finite zero-sum substate lattice of B43 once, identify every zero-sum block U
whose complement admits three zero-sum blocks, and then certify that, after
removing each possible source occurrence v from such a U, the union of reachable
submultiset sums covers all 343 elements of C_7^3.  This supplies a constructive
5-pack for every split a+b=v.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from typing import Iterable, Iterator, Sequence

P = 7
ZERO = (0, 0, 0)
Vec = tuple[int, int, int]
Counts = tuple[int, ...]

# Specialized Freeze--Schmid lower-bound construction for k=4, followed by the
# standard total-sum completion term.  The first six support points form the
# length-42 lower-bound sequence; H=-sigma(S0) is appended to obtain B43.
SUPPORT: tuple[Vec, ...] = (
    (1, 0, 0),  # e1
    (0, 1, 0),  # e2
    (0, 0, 1),  # e3
    (1, 1, 0),  # e1+e2
    (1, 0, 1),  # e1+e3
    (0, 1, 1),  # e2+e3
    (2, 1, 1),  # -sigma(S0)
)
CAPS: Counts = (6, 6, 20, 3, 3, 4, 1)
SOURCE_LABELS = ("e1", "e2", "e3", "e1+e2", "e1+e3", "e2+e3", "completion")


def add(a: Vec, b: Vec) -> Vec:
    return tuple((x + y) % P for x, y in zip(a, b))  # type: ignore[return-value]


def neg(a: Vec) -> Vec:
    return tuple((-x) % P for x in a)  # type: ignore[return-value]


def sub(a: Vec, b: Vec) -> Vec:
    return tuple((x - y) % P for x, y in zip(a, b))  # type: ignore[return-value]


def scale(c: int, a: Vec) -> Vec:
    return tuple((c * x) % P for x in a)  # type: ignore[return-value]


def encode(a: Vec) -> int:
    return 49 * a[0] + 7 * a[1] + a[2]


def sum_counts(counts: Sequence[int]) -> Vec:
    total = ZERO
    for count, value in zip(counts, SUPPORT):
        total = add(total, scale(count, value))
    return total


def counter_from_counts(counts: Sequence[int]) -> Counter[Vec]:
    result: Counter[Vec] = Counter()
    for count, value in zip(counts, SUPPORT):
        if count:
            result[value] += count
    return result


def counter_sum(counter: Counter[Vec]) -> Vec:
    total = ZERO
    for value, count in counter.items():
        total = add(total, scale(count, value))
    return total


def leq(a: Sequence[int], b: Sequence[int]) -> bool:
    return all(x <= y for x, y in zip(a, b))


def subtract_counts(a: Sequence[int], b: Sequence[int]) -> Counts:
    out = tuple(x - y for x, y in zip(a, b))
    if any(value < 0 for value in out):
        raise ValueError("negative count in subtraction")
    return out


def all_zero_sum_substates(caps: Counts) -> tuple[Counts, ...]:
    out: list[Counts] = []
    for state in itertools.product(*(range(cap + 1) for cap in caps)):
        if any(state) and sum_counts(state) == ZERO:
            out.append(tuple(state))
    return tuple(sorted(out, key=lambda state: (sum(state), state)))


def minimal_zero_sum_atoms(zero_states: Sequence[Counts]) -> tuple[Counts, ...]:
    atoms: list[Counts] = []
    for state in zero_states:
        if not any(leq(atom, state) for atom in atoms):
            atoms.append(state)
    return tuple(atoms)


def factor_search(blocks: Sequence[Counts], state: Counts, target: int) -> tuple[int, ...] | None:
    """Return indices of target disjoint zero-sum blocks, if they exist."""

    @lru_cache(maxsize=None)
    def rec(current: Counts, remaining: int) -> tuple[int, ...] | None:
        if remaining == 0:
            return ()
        # Every nonempty zero-sum sequence over C_7^3 has at least 2 terms here;
        # the cheap length bound is only a prune, never an authority premise.
        if sum(current) < remaining:
            return None
        for index, block in enumerate(blocks):
            if leq(block, current):
                suffix = rec(subtract_counts(current, block), remaining - 1)
                if suffix is not None:
                    return (index,) + suffix
        return None

    return rec(state, target)


def residual_reachability(caps: Counts) -> dict[Vec, Counts]:
    """Map every reachable submultiset sum to one exact count-vector witness."""
    witnesses: dict[Vec, Counts] = {}
    for state in itertools.product(*(range(cap + 1) for cap in caps)):
        state = tuple(state)
        total = sum_counts(state)
        witnesses.setdefault(total, state)
        if len(witnesses) == P**3:
            break
    return witnesses


def unordered_nonzero_splits(v: Vec) -> Iterator[tuple[Vec, Vec]]:
    for a in itertools.product(range(P), repeat=3):
        a = tuple(a)  # type: ignore[assignment]
        if a == ZERO:
            continue
        b = sub(v, a)
        if b == ZERO:
            continue
        if encode(a) <= encode(b):
            yield a, b


def block_from_base_counts(counts: Counts) -> Counter[Vec]:
    block = counter_from_counts(counts)
    if not block or counter_sum(block) != ZERO:
        raise AssertionError("invalid base zero-sum block")
    return block


def validate_partition(candidate: Counter[Vec], blocks: Sequence[Counter[Vec]]) -> list[int]:
    used: Counter[Vec] = Counter()
    lengths: list[int] = []
    for block in blocks:
        if not block:
            raise AssertionError("empty zero-sum block")
        if counter_sum(block) != ZERO:
            raise AssertionError("non-zero block in certificate")
        used += block
        lengths.append(sum(block.values()))
    if used != candidate:
        raise AssertionError("certificate blocks do not exactly cover candidate")
    return lengths


def canonical_json_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify() -> dict[str, object]:
    if sum(CAPS) != 43 or sum_counts(CAPS) != ZERO:
        raise AssertionError("B43 length/total-sum reconstruction failed")
    if sum(CAPS[:-1]) != 42 or sum_counts(CAPS[:-1] + (0,)) != (5, 6, 6):
        raise AssertionError("Freeze--Schmid S0 arithmetic reconstruction failed")
    if SUPPORT[-1] != neg((5, 6, 6)):
        raise AssertionError("completion term is not -sigma(S0)")

    zero_states = all_zero_sum_substates(CAPS)
    atoms = minimal_zero_sum_atoms(zero_states)

    # Two exact factor searches with different block vocabularies.  The atom
    # route proves the maximal packing using the minimal zero-sum generators;
    # the all-zero-state route independently reaches the same 4/5 boundary
    # without relying on atom filtering.
    base_pack4_atoms = factor_search(atoms, CAPS, 4)
    base_pack5_atoms = factor_search(atoms, CAPS, 5)
    base_pack4_all = factor_search(zero_states, CAPS, 4)
    base_pack5_all = factor_search(zero_states, CAPS, 5)
    if base_pack4_atoms is None or base_pack4_all is None:
        raise AssertionError("B43 did not realize four disjoint zero-sums")
    if base_pack5_atoms is not None or base_pack5_all is not None:
        raise AssertionError("B43 unexpectedly realizes five disjoint zero-sums")

    # A zero-sum U containing source v is useful if B43-U admits three further
    # zero-sum blocks.  Since zz(B43)=4, every such U is automatically an atom:
    # a proper zero-sum inside U would make five disjoint blocks.
    eligible: dict[int, list[tuple[Counts, tuple[int, ...], dict[Vec, Counts]]]] = {
        index: [] for index in range(len(SUPPORT))
    }
    for U in zero_states:
        complement = subtract_counts(CAPS, U)
        pack3 = factor_search(atoms, complement, 3)
        if pack3 is None:
            continue
        for source_index, multiplicity in enumerate(U):
            if not multiplicity:
                continue
            residual = list(U)
            residual[source_index] -= 1
            residual_counts = tuple(residual)
            reach = residual_reachability(residual_counts)
            eligible[source_index].append((U, pack3, reach))

    atom_set = set(atoms)
    if not all(U in atom_set for rows in eligible.values() for U, _, _ in rows):
        raise AssertionError("eligible U must be a minimal zero-sum block")

    # Finite cover: for every source type the union of submultiset sums from
    # residuals U-v must cover C_7^3.  In particular -a is covered for every
    # nonzero split term a.  This is the load-bearing one-split closure fact.
    cover_counts: dict[str, int] = {}
    for source_index, rows in eligible.items():
        union: set[Vec] = set()
        for _, _, reach in rows:
            union.update(reach)
        cover_counts[SOURCE_LABELS[source_index]] = len(union)
        if len(union) != P**3:
            raise AssertionError(
                f"incomplete residual-sum cover for source {SOURCE_LABELS[source_index]}: {len(union)}"
            )

    base_counter = counter_from_counts(CAPS)
    certificate_rows: list[dict[str, object]] = []
    per_source: dict[str, int] = {label: 0 for label in SOURCE_LABELS}

    for source_index, source in enumerate(SUPPORT):
        splits = tuple(unordered_nonzero_splits(source))
        if len(splits) != 171:
            raise AssertionError("unexpected unordered nonzero split count")
        for a, b in splits:
            chosen: tuple[Counts, tuple[int, ...], Counts] | None = None
            target = neg(a)
            for U, pack3, reach in eligible[source_index]:
                X = reach.get(target)
                if X is not None:
                    chosen = (U, pack3, X)
                    break
            if chosen is None:
                raise AssertionError(f"cover claimed complete but split lacks certificate: {source=} {a=} {b=}")

            U, pack3, X = chosen
            residual = list(U)
            residual[source_index] -= 1
            residual_counts = tuple(residual)
            Y = subtract_counts(residual_counts, X)

            # U-v+a+b is split into A=(X+a) and C=(Y+b).
            A = counter_from_counts(X)
            A[a] += 1
            C = counter_from_counts(Y)
            C[b] += 1

            blocks: list[Counter[Vec]] = [A, C]
            blocks.extend(block_from_base_counts(atoms[index]) for index in pack3)

            candidate = base_counter.copy()
            candidate[source] -= 1
            if candidate[source] == 0:
                del candidate[source]
            candidate[a] += 1
            candidate[b] += 1
            if sum(candidate.values()) != 44 or counter_sum(candidate) != ZERO:
                raise AssertionError("split candidate does not preserve length/sum")

            lengths = validate_partition(candidate, blocks)
            if len(lengths) != 5:
                raise AssertionError("split certificate is not a five-block partition")

            # Upper bound zz<=5 is theorem-level, not searched candidate by
            # candidate: in any >=5 packing, a and b cannot be in the same block
            # (merging them back to v would give >=5 blocks in B43).  If they are
            # in different blocks, merge those two blocks and restore v, reducing
            # the packing by exactly one; zz(B43)=4 therefore forbids >=6.
            certificate_rows.append(
                {
                    "source_index": source_index,
                    "source": list(source),
                    "a": list(a),
                    "b": list(b),
                    "block_lengths": lengths,
                    "U": list(U),
                    "X": list(X),
                    "complement_atom_indices": list(pack3),
                }
            )
            per_source[SOURCE_LABELS[source_index]] += 1

    if len(certificate_rows) != 1197 or any(value != 171 for value in per_source.values()):
        raise AssertionError("one-split sweep cardinality mismatch")

    # Hostile controls for the theorem/certificate boundary.
    # 1. The unsplit B43 itself must not pass a five-pack test.
    # 2. Corrupting one declared split relation must fail total-sum preservation.
    bad_a = (1, 0, 0)
    bad_b = (1, 0, 0)
    bad_source = SUPPORT[0]
    bad_candidate = base_counter.copy()
    bad_candidate[bad_source] -= 1
    bad_candidate[bad_a] += 1
    bad_candidate[bad_b] += 1
    hostile = {
        "base_rejects_five_pack_atoms": base_pack5_atoms is None,
        "base_rejects_five_pack_all_zero_states": base_pack5_all is None,
        "corrupt_split_relation_detected": add(bad_a, bad_b) != bad_source,
        "corrupt_split_breaks_total_sum": counter_sum(bad_candidate) != ZERO,
    }
    if not all(hostile.values()):
        raise AssertionError(f"hostile control failure: {hostile}")

    return {
        "schema": "ORION.C7CubedDavenportB7OneSplit.v1",
        "bounded_atom": "B7-S1",
        "base": {
            "support": [list(value) for value in SUPPORT],
            "multiplicities": list(CAPS),
            "length": 43,
            "sum": list(sum_counts(CAPS)),
            "zero_sum_substates": len(zero_states),
            "minimal_zero_sum_atoms": len(atoms),
            "pack4_atoms_found": base_pack4_atoms is not None,
            "pack5_atoms_found": base_pack5_atoms is not None,
            "pack4_all_states_found": base_pack4_all is not None,
            "pack5_all_states_found": base_pack5_all is not None,
            "exact_zz": 4,
        },
        "eligible_U_counts": {
            SOURCE_LABELS[index]: len(rows) for index, rows in eligible.items()
        },
        "residual_sum_cover_counts": cover_counts,
        "group_size": P**3,
        "one_split_moves_checked": len(certificate_rows),
        "per_source_moves": per_source,
        "all_one_split_moves_have_explicit_five_pack": True,
        "upper_bound_argument": (
            "Any >=5 packing after v->a+b has a,b in distinct blocks; merging those two blocks "
            "and restoring v produces one fewer disjoint zero-sum block in B43. Since zz(B43)=4, "
            "every one-split sequence has zz<=5. Together with the explicit five-pack certificates, "
            "every checked split has exact zz=5."
        ),
        "all_one_split_moves_exact_zz": 5,
        "certificate_rows_sha256": canonical_json_digest(certificate_rows),
        "hostile_controls": hostile,
        "disposition": "NO_B7_WITNESS_IN_CANONICAL_B43_ONE_TERM_SPLIT_NEIGHBOURHOOD",
        "global_B7_status": "OPEN",
        "authority": {
            "bounded_one_split_result": "EXACT_FINITE_CERTIFICATE_SWEEP",
            "freeze_schmid_construction": "DONOR_OWNED",
            "global_D4_C7cubed": "OPEN",
            "novelty_priority": "CANNOT_CHECK",
        },
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
