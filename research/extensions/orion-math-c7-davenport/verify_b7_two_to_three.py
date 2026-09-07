#!/usr/bin/env python3
"""Exact B7-S2 closure for the canonical C_7^3 Freeze--Schmid-derived B43.

Bounded neighbourhood:
    remove two source terms v,w from B43 and add three nonzero terms a,b,c
    with a+b+c=v+w.

There are 27 legal labelled source-pair types and 19,608 unordered nonzero
triples for every nonzero target, hence 529,416 labelled moves.

The main certificate is a refinement cover.  If a zero-sum base block U
contains the two removed terms and B43-U has a three-block zero-sum partition,
then a modified U splits into two zero-sum blocks whenever, after removing v,w
from U, one can reach the negative of any one of a,b,c as a submultiset sum.
This produces five zero-sum blocks in the modified length-44 sequence.

The finite cover resolves 529,414 moves.  Exactly two moves survive that cover;
a separate generic compressed-state packing engine proves each has exact zz=5.
Thus none of the 529,416 moves is a B7 witness with zz<=4.  Global B7 remains
open: this file closes only the two-to-three edit neighbourhood of this B43.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
from typing import Iterator, Sequence

P = 7
ZERO = (0, 0, 0)
Vec = tuple[int, int, int]
Counts = tuple[int, ...]

SUPPORT: tuple[Vec, ...] = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1),
    (2, 1, 1),
)
CAPS: Counts = (6, 6, 20, 3, 3, 4, 1)
LABELS = ("e1", "e2", "e3", "e1+e2", "e1+e3", "e2+e3", "completion")
ALL_GROUP: tuple[Vec, ...] = tuple(itertools.product(range(P), repeat=3))
NONZERO: tuple[Vec, ...] = tuple(v for v in ALL_GROUP if v != ZERO)


def add(a: Vec, b: Vec) -> Vec:
    return tuple((x + y) % P for x, y in zip(a, b))  # type: ignore[return-value]


def sub(a: Vec, b: Vec) -> Vec:
    return tuple((x - y) % P for x, y in zip(a, b))  # type: ignore[return-value]


def neg(a: Vec) -> Vec:
    return tuple((-x) % P for x in a)  # type: ignore[return-value]


def scale(c: int, a: Vec) -> Vec:
    return tuple((c * x) % P for x in a)  # type: ignore[return-value]


def encode(a: Vec) -> int:
    return 49 * a[0] + 7 * a[1] + a[2]


def sum_counts(counts: Sequence[int]) -> Vec:
    out = ZERO
    for count, value in zip(counts, SUPPORT):
        out = add(out, scale(count, value))
    return out


def subtract_counts(a: Sequence[int], b: Sequence[int]) -> Counts:
    out = tuple(x - y for x, y in zip(a, b))
    if any(value < 0 for value in out):
        raise ValueError("negative count")
    return out


def leq(a: Sequence[int], b: Sequence[int]) -> bool:
    return all(x <= y for x, y in zip(a, b))


def base_counter(counts: Sequence[int] = CAPS) -> Counter[Vec]:
    out: Counter[Vec] = Counter()
    for value, count in zip(SUPPORT, counts):
        if count:
            out[value] += count
    return out


def counter_sum(counter: Counter[Vec]) -> Vec:
    out = ZERO
    for value, count in counter.items():
        out = add(out, scale(count, value))
    return out


def all_zero_states(caps: Counts) -> tuple[Counts, ...]:
    out: list[Counts] = []
    for state in itertools.product(*(range(cap + 1) for cap in caps)):
        state = tuple(state)
        if any(state) and sum_counts(state) == ZERO:
            out.append(state)
    return tuple(sorted(out, key=lambda state: (sum(state), state)))


def atoms_from_zero_states(zero_states: Sequence[Counts]) -> tuple[Counts, ...]:
    atoms: list[Counts] = []
    for state in zero_states:
        if not any(leq(atom, state) for atom in atoms):
            atoms.append(state)
    return tuple(atoms)


def make_factorizer(blocks: Sequence[Counts]):
    @lru_cache(maxsize=None)
    def factor(state: Counts, target: int) -> tuple[int, ...] | None:
        if target == 0:
            return ()
        for index, block in enumerate(blocks):
            if leq(block, state):
                suffix = factor(subtract_counts(state, block), target - 1)
                if suffix is not None:
                    return (index,) + suffix
        return None

    return factor


def reach_map(caps: Counts) -> dict[Vec, Counts]:
    witnesses: dict[Vec, Counts] = {}
    for state in itertools.product(*(range(cap + 1) for cap in caps)):
        state = tuple(state)
        witnesses.setdefault(sum_counts(state), state)
        if len(witnesses) == P**3:
            break
    return witnesses


def source_pairs() -> tuple[tuple[int, int], ...]:
    out: list[tuple[int, int]] = []
    for i in range(len(SUPPORT)):
        for j in range(i, len(SUPPORT)):
            if i == j and CAPS[i] < 2:
                continue
            out.append((i, j))
    return tuple(out)


def unordered_nonzero_triples(target: Vec) -> Iterator[tuple[Vec, Vec, Vec]]:
    values = tuple(sorted(NONZERO, key=encode))
    for ai, a in enumerate(values):
        for bi in range(ai, len(values)):
            b = values[bi]
            c = sub(sub(target, a), b)
            if c == ZERO or encode(c) < encode(b):
                continue
            yield a, b, c


def counts_counter(counts: Sequence[int]) -> Counter[Vec]:
    return base_counter(counts)


def modified_counter(i: int, j: int, triple: Sequence[Vec]) -> Counter[Vec]:
    out = base_counter()
    out[SUPPORT[i]] -= 1
    out[SUPPORT[j]] -= 1
    for value in list(out):
        if out[value] == 0:
            del out[value]
    for value in triple:
        out[value] += 1
    return out


def validate_cover_certificate(
    i: int,
    j: int,
    triple: tuple[Vec, Vec, Vec],
    chosen_position: int,
    U: Counts,
    X: Counts,
    complement_atom_indices: Sequence[int],
    atoms: Sequence[Counts],
) -> list[int]:
    residual = list(U)
    residual[i] -= 1
    residual[j] -= 1
    if any(value < 0 for value in residual):
        raise AssertionError("source removal exceeds U")
    residual_counts = tuple(residual)
    Y = subtract_counts(residual_counts, X)

    chosen = triple[chosen_position]
    others = [triple[k] for k in range(3) if k != chosen_position]

    first = counts_counter(X)
    first[chosen] += 1
    second = counts_counter(Y)
    for value in others:
        second[value] += 1

    blocks: list[Counter[Vec]] = [first, second]
    for atom_index in complement_atom_indices:
        blocks.append(counts_counter(atoms[atom_index]))

    if len(blocks) != 5:
        raise AssertionError("cover certificate is not five blocks")
    used: Counter[Vec] = Counter()
    lengths: list[int] = []
    for block in blocks:
        if not block or counter_sum(block) != ZERO:
            raise AssertionError("invalid zero-sum block")
        used += block
        lengths.append(sum(block.values()))

    candidate = modified_counter(i, j, triple)
    if sum(candidate.values()) != 44 or counter_sum(candidate) != ZERO:
        raise AssertionError("modified candidate fails length/total-sum gate")
    if used != candidate:
        raise AssertionError("five-block certificate does not exactly cover candidate")
    return lengths


def generic_exact_zz(counter: Counter[Vec], max_target: int = 7) -> dict[str, object]:
    support = tuple(sorted(counter, key=encode))
    caps = tuple(counter[value] for value in support)

    def state_sum(state: Sequence[int]) -> Vec:
        out = ZERO
        for count, value in zip(state, support):
            out = add(out, scale(count, value))
        return out

    zero_states: list[Counts] = []
    for state in itertools.product(*(range(cap + 1) for cap in caps)):
        state = tuple(state)
        if any(state) and state_sum(state) == ZERO:
            zero_states.append(state)
    zero_states.sort(key=lambda state: (sum(state), state))

    atoms: list[Counts] = []
    for state in zero_states:
        if not any(leq(atom, state) for atom in atoms):
            atoms.append(state)

    @lru_cache(maxsize=None)
    def can_pack(state: Counts, target: int) -> tuple[int, ...] | None:
        if target == 0:
            return ()
        for index, atom in enumerate(atoms):
            if leq(atom, state):
                suffix = can_pack(subtract_counts(state, atom), target - 1)
                if suffix is not None:
                    return (index,) + suffix
        return None

    exact = 0
    certificates: dict[int, tuple[int, ...]] = {}
    for target in range(1, max_target + 1):
        certificate = can_pack(caps, target)
        if certificate is None:
            break
        exact = target
        certificates[target] = certificate

    return {
        "support": [list(value) for value in support],
        "multiplicities": list(caps),
        "zero_sum_states": len(zero_states),
        "minimal_atoms": len(atoms),
        "exact_zz_up_to_target": exact,
        "pack5_found": 5 in certificates,
        "pack6_found": 6 in certificates,
        "pack7_found": 7 in certificates,
    }


def canonical_digest_update(hasher: "hashlib._Hash", payload: object) -> None:
    hasher.update(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    hasher.update(b"\n")


def verify() -> dict[str, object]:
    if sum(CAPS) != 43 or sum_counts(CAPS) != ZERO:
        raise AssertionError("B43 reconstruction failed")

    zero_states = all_zero_states(CAPS)
    atoms = atoms_from_zero_states(zero_states)
    if len(zero_states) != 479 or len(atoms) != 159:
        raise AssertionError("base finite lattice census drifted")

    factor_atoms = make_factorizer(atoms)
    if factor_atoms(CAPS, 4) is None or factor_atoms(CAPS, 5) is not None:
        raise AssertionError("base zz=4 gate failed")

    pairs = source_pairs()
    if len(pairs) != 27:
        raise AssertionError("unexpected legal source-pair count")

    pair_witness_maps: dict[
        tuple[int, int], dict[Vec, tuple[Counts, tuple[int, ...], Counts]]
    ] = {}
    eligible_counts: dict[str, int] = {}
    cover_counts: dict[str, int] = {}

    for i, j in pairs:
        witness_map: dict[Vec, tuple[Counts, tuple[int, ...], Counts]] = {}
        eligible = 0
        for U in zero_states:
            if i == j:
                if U[i] < 2:
                    continue
            elif U[i] < 1 or U[j] < 1:
                continue

            complement = subtract_counts(CAPS, U)
            pack3 = factor_atoms(complement, 3)
            if pack3 is None:
                continue

            # Because B43 itself has no five-pack, the three chosen complement
            # atoms must cover the whole complement; otherwise the nonempty
            # zero-sum leftover would be a fifth base block.
            used = [0] * len(CAPS)
            for atom_index in pack3:
                for k, value in enumerate(atoms[atom_index]):
                    used[k] += value
            if tuple(used) != complement:
                raise AssertionError("complement 3-pack left a forbidden base zero-sum remainder")

            eligible += 1
            residual = list(U)
            residual[i] -= 1
            residual[j] -= 1
            for total, X in reach_map(tuple(residual)).items():
                witness_map.setdefault(total, (U, pack3, X))

        key = f"{LABELS[i]}+{LABELS[j]}"
        pair_witness_maps[(i, j)] = witness_map
        eligible_counts[key] = eligible
        cover_counts[key] = len(witness_map)

    # Exact sweep of every labelled source-pair / unordered triple move.
    total_moves = 0
    covered_moves = 0
    residual_moves: list[tuple[int, int, Vec, Vec, Vec]] = []
    per_pair_moves: dict[str, int] = {}
    certificate_hasher = hashlib.sha256()

    for i, j in pairs:
        target = add(SUPPORT[i], SUPPORT[j])
        triples = tuple(unordered_nonzero_triples(target))
        key = f"{LABELS[i]}+{LABELS[j]}"
        per_pair_moves[key] = len(triples)
        if len(triples) != 19_608:
            raise AssertionError(f"unexpected triple count for {key}: {len(triples)}")

        witness_map = pair_witness_maps[(i, j)]
        for triple in triples:
            total_moves += 1
            chosen_certificate = None
            for position, value in enumerate(triple):
                certificate = witness_map.get(neg(value))
                if certificate is not None:
                    chosen_certificate = (position, certificate)
                    break
            if chosen_certificate is None:
                residual_moves.append((i, j, *triple))
                continue

            position, (U, pack3, X) = chosen_certificate
            lengths = validate_cover_certificate(i, j, triple, position, U, X, pack3, atoms)
            covered_moves += 1
            canonical_digest_update(
                certificate_hasher,
                {
                    "source_pair": [i, j],
                    "triple": [list(value) for value in triple],
                    "chosen_position": position,
                    "U": list(U),
                    "X": list(X),
                    "pack3": list(pack3),
                    "block_lengths": lengths,
                },
            )

    if total_moves != 529_416 or covered_moves != 529_414:
        raise AssertionError(
            f"two-to-three census mismatch: total={total_moves}, covered={covered_moves}"
        )

    expected_residual = {
        (5, 5, (1, 0, 1), (1, 1, 0), (5, 1, 1)),
        (5, 6, (0, 1, 1), (1, 0, 1), (1, 1, 0)),
    }
    if set(residual_moves) != expected_residual:
        raise AssertionError(f"unexpected cover residuals: {residual_moves}")

    residual_results: list[dict[str, object]] = []
    for i, j, a, b, c in residual_moves:
        candidate = modified_counter(i, j, (a, b, c))
        exact = generic_exact_zz(candidate, max_target=7)
        if exact["exact_zz_up_to_target"] != 5:
            raise AssertionError(f"residual candidate is not exact zz=5: {(i,j,a,b,c)} {exact}")
        residual_results.append(
            {
                "source_pair": [i, j],
                "triple": [list(a), list(b), list(c)],
                "generic_exact": exact,
            }
        )

    # Positive polarity: the generic engine must also recognize a nearby
    # two-to-three move with six disjoint zero-sum blocks, so a hard-coded
    # five ceiling cannot masquerade as a verifier.
    six_control_triple = ((0, 0, 1), (0, 1, 0), (2, 6, 6))
    six_control = generic_exact_zz(modified_counter(0, 0, six_control_triple), max_target=7)
    if six_control["exact_zz_up_to_target"] != 6:
        raise AssertionError(f"six-pack polarity control failed: {six_control}")

    # General merge-back upper bound for this edit class: if the three new terms
    # occupy r<=3 blocks of any packing, merging those r blocks and restoring
    # v,w gives one base block, hence a packing of size k-r+1 in B43.  Since
    # zz(B43)=4, k<=r+3<=6.  The sweep proves every move has k>=5.
    return {
        "schema": "ORION.C7CubedDavenportB7TwoToThree.v1",
        "bounded_atom": "B7-S2",
        "base_exact_zz": 4,
        "base_zero_sum_states": len(zero_states),
        "base_minimal_atoms": len(atoms),
        "source_pair_types": len(pairs),
        "unordered_nonzero_triples_per_pair": 19_608,
        "moves_checked": total_moves,
        "cover_resolved_moves": covered_moves,
        "generic_residual_moves": len(residual_moves),
        "eligible_U_counts": eligible_counts,
        "residual_sum_cover_counts": cover_counts,
        "residual_exact_results": residual_results,
        "six_pack_polarity_control": {
            "source_pair": [0, 0],
            "triple": [list(value) for value in six_control_triple],
            "generic_exact": six_control,
        },
        "all_moves_have_zz_at_least_5": True,
        "all_moves_have_zz_at_most_6_by_merge_back": True,
        "no_B7_witness_in_two_to_three_neighbourhood": True,
        "cover_certificate_stream_sha256": certificate_hasher.hexdigest(),
        "disposition": "NO_B7_WITNESS_IN_CANONICAL_B43_TWO_TO_THREE_NEIGHBOURHOOD",
        "global_B7_status": "OPEN",
        "authority": {
            "bounded_two_to_three_result": "EXACT_FINITE_CERTIFICATE_SWEEP_WITH_GENERIC_RESIDUAL_CHECKS",
            "freeze_schmid_construction": "DONOR_OWNED",
            "D4_C7cubed": "OPEN",
            "novelty_priority": "CANNOT_CHECK",
        },
    }


def main() -> int:
    print(json.dumps(verify(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
