#!/usr/bin/env python3
"""Independent sparse exact solver for the frozen six-slot R6M grammar.

This module is intentionally standard-library-only.  In particular it does
not import, call, or reproduce the frozen 512-state production XOR DP.  It
implements the direct support-two normal-form algorithm whose mathematical
input is the already-established R6S theorem.

Scope: exactly three ordered anticommuting frame pairs, one common one-bit Tag,
two relative target permutations, three binary central choices, and the
frozen local three-way Restore-factor support objective.

Local phase-ignored Pauli codes follow the production convention
``I=0, X=1, Y=2, Z=3`` with binary symplectic coordinates
``((0,0), (1,0), (1,1), (0,1))``.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Iterable, Iterator, Sequence

CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
BITS_CODE = {bits: code for code, bits in enumerate(CODE_BITS)}
NONIDENTITY = (1, 2, 3)
ORIENTATIONS = ((0, 1), (1, 0))
CENTRALS = tuple(product((0, 1), repeat=3))
INF = 10**18

SparsePauli = tuple[tuple[int, int], ...]
DensePauli = tuple[int, ...]


def local_symp(a: int, b: int) -> int:
    """Binary local symplectic product of two phase-ignored Pauli letters."""
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    return (ax & bz) ^ (az & bx)


def local_mul(a: int, b: int) -> int:
    """Phase-ignored local Pauli product."""
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    return BITS_CODE[(ax ^ bx, az ^ bz)]


def local_product_phase(a: int, b: int) -> int:
    """Exponent e in ``P(a) P(b) = i**e P(a*b)`` for Hermitian Paulis."""
    ax, az = CODE_BITS[a]
    bx, bz = CODE_BITS[b]
    cx, cz = ax ^ bx, az ^ bz
    # P(x,z)=i^(xz) X^x Z^z.  Commuting Z^az through X^bx adds 2*az*bx.
    return (ax * az + bx * bz + 2 * az * bx - cx * cz) % 4


def dense_mul(a: Sequence[int], b: Sequence[int]) -> DensePauli:
    if len(a) != len(b):
        raise ValueError("Pauli lengths differ")
    return tuple(local_mul(int(x), int(y)) for x, y in zip(a, b))


def dense_mul_phase(a: Sequence[int], b: Sequence[int]) -> tuple[DensePauli, int]:
    """Phase-free product and Hermitian i-phase exponent for dense Paulis."""
    if len(a) != len(b):
        raise ValueError("Pauli lengths differ")
    product_pauli = dense_mul(a, b)
    exponent = sum(local_product_phase(int(x), int(y)) for x, y in zip(a, b)) % 4
    return product_pauli, int(exponent)


def f3(a: int, b: int, c: int) -> int:
    """Frozen donor-owned three-way local Restore-factor support cost."""
    if a == b == c != 0:
        return 1
    return int(a != 0) + int(b != 0) + int(c != 0)


def sparse_letter(pauli: SparsePauli, q: int) -> int:
    """Read one coordinate in O(1) for the support-at-most-two representation."""
    for coordinate, letter in pauli:
        if coordinate == q:
            return letter
    return 0


def sparse_symp(a: SparsePauli, b: SparsePauli) -> int:
    """Global symplectic product; both operands have constant support here."""
    coordinates = {q for q, _ in a}
    coordinates.update(q for q, _ in b)
    parity = 0
    for q in coordinates:
        parity ^= local_symp(sparse_letter(a, q), sparse_letter(b, q))
    return parity


def sparse_to_dense(pauli: SparsePauli, n: int) -> DensePauli:
    dense = [0] * n
    for q, letter in pauli:
        if not (0 <= q < n and letter in NONIDENTITY):
            raise ValueError({"invalid_sparse_pauli_entry": [q, letter], "n": n})
        if dense[q] != 0:
            raise ValueError({"duplicate_sparse_coordinate": q})
        dense[q] = letter
    return tuple(dense)


def dense_to_sparse(pauli: Sequence[int]) -> SparsePauli:
    return tuple((q, int(letter)) for q, letter in enumerate(pauli) if letter != 0)


@dataclass(frozen=True, slots=True)
class FramePair:
    """One ordered anticommuting pair with each member of support one or two."""

    r0: SparsePauli
    r1: SparsePauli

    @property
    def w0(self) -> int:
        return len(self.r0)

    @property
    def w1(self) -> int:
        return len(self.r1)

    @property
    def active(self) -> tuple[int, ...]:
        return tuple(sorted({q for q, _ in self.r0} | {q for q, _ in self.r1}))


def _frame(entries: Iterable[tuple[int, int]]) -> SparsePauli:
    out = tuple(sorted((int(q), int(letter)) for q, letter in entries))
    if not (1 <= len(out) <= 2):
        raise AssertionError({"frame_support_outside_one_two": out})
    if len({q for q, _ in out}) != len(out):
        raise AssertionError({"frame_duplicate_coordinate": out})
    if any(letter not in NONIDENTITY for _, letter in out):
        raise AssertionError({"frame_identity_letter": out})
    return out


def support_at_most_two_paulis(n: int, max_support: int = 2) -> Iterator[SparsePauli]:
    """Canonical direct generator for nonidentity Paulis of support <= max_support."""
    if n < 1:
        raise ValueError("n must be positive")
    if max_support not in (1, 2):
        raise ValueError("max_support must be 1 or 2")
    for q in range(n):
        for letter in NONIDENTITY:
            yield ((q, letter),)
    if max_support == 2:
        for q0, q1 in combinations(range(n), 2):
            for a, b in product(NONIDENTITY, repeat=2):
                yield ((q0, a), (q1, b))


def ordered_anticommuting_pairs(n: int, max_support: int = 2) -> Iterator[FramePair]:
    """Duplicate-free constructive ordered-pair generator.

    For max_support=2 this emits exactly
    ``54*n**3 - 108*n**2 + 60*n`` pairs in O(n^3) time.  It never scans the
    quadratic cross-product of the support-two Pauli family.
    """
    if n < 1:
        raise ValueError("n must be positive")
    if max_support not in (1, 2):
        raise ValueError("max_support must be 1 or 2")

    # Weight-one first frame.
    for q in range(n):
        for a in NONIDENTITY:
            r0 = ((q, a),)
            for b in NONIDENTITY:
                if local_symp(a, b):
                    yield FramePair(r0, ((q, b),))
            if max_support == 2:
                for outside in range(n):
                    if outside == q:
                        continue
                    for b in NONIDENTITY:
                        if not local_symp(a, b):
                            continue
                        for c in NONIDENTITY:
                            yield FramePair(r0, _frame(((q, b), (outside, c))))

    if max_support == 1:
        return

    # Weight-two first frame.
    for q0, q1 in combinations(range(n), 2):
        for a0, a1 in product(NONIDENTITY, repeat=2):
            r0 = ((q0, a0), (q1, a1))

            # Weight-one partner on either active coordinate.
            for shared, a in ((q0, a0), (q1, a1)):
                for b in NONIDENTITY:
                    if local_symp(a, b):
                        yield FramePair(r0, ((shared, b),))

            # Weight-two partner on the same support, with exactly one local
            # anticommutation.
            for b0, b1 in product(NONIDENTITY, repeat=2):
                if local_symp(a0, b0) ^ local_symp(a1, b1):
                    yield FramePair(r0, ((q0, b0), (q1, b1)))

            # Weight-two partner overlapping in exactly one coordinate.
            for shared, a in ((q0, a0), (q1, a1)):
                for outside in range(n):
                    if outside in (q0, q1):
                        continue
                    for b in NONIDENTITY:
                        if not local_symp(a, b):
                            continue
                        for c in NONIDENTITY:
                            yield FramePair(r0, _frame(((shared, b), (outside, c))))


def pair_count_formula(n: int) -> int:
    return 54 * n**3 - 108 * n**2 + 60 * n


def active_union(pairs: Sequence[FramePair]) -> tuple[int, ...]:
    coordinates: set[int] = set()
    for pair in pairs:
        coordinates.update(pair.active)
    return tuple(sorted(coordinates))


def _rhs_mask(orientation: tuple[int, int]) -> int:
    if orientation not in ORIENTATIONS:
        raise ValueError({"invalid_orientation": orientation})
    out = 0
    for block in range(3):
        out |= orientation[0] << (2 * block)
        out |= orientation[1] << (2 * block + 1)
    return out


def _six_frames(pairs: Sequence[FramePair]) -> tuple[SparsePauli, ...]:
    if len(pairs) != 3:
        raise ValueError("the frozen grammar requires exactly three frame pairs")
    return tuple(frame for pair in pairs for frame in (pair.r0, pair.r1))


def tag_constraint_rank(pairs: Sequence[FramePair]) -> int:
    """Rank of the six Tag equations on the active-union binary variables."""
    frames = _six_frames(pairs)
    active = active_union(pairs)
    rows: list[int] = []
    for frame in frames:
        row = 0
        for j, q in enumerate(active):
            fx, fz = CODE_BITS[sparse_letter(frame, q)]
            if fz:
                row |= 1 << (2 * j)
            if fx:
                row |= 1 << (2 * j + 1)
        rows.append(row)
    rank = 0
    bit = 2 * len(active) - 1
    while bit >= 0:
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            bit -= 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[rank]
        rank += 1
        bit -= 1
    return rank


def minimum_tag(
    pairs: Sequence[FramePair], orientation: tuple[int, int]
) -> tuple[int, SparsePauli] | None:
    """Exact 64-syndrome minimum-weight Tag solve on at most nine coordinates."""
    frames = _six_frames(pairs)
    active = active_union(pairs)
    if len(active) > 9:
        raise AssertionError({"active_union_exceeds_nine": active})
    desired = _rhs_mask(orientation)

    # state -> (weight, active-coordinate letter prefix).  There are at most
    # 64 states and nine coordinates; neither grows with n.
    dp: dict[int, tuple[int, tuple[int, ...]]] = {0: (0, ())}
    for q in active:
        deltas = []
        for letter in range(4):
            delta = 0
            for slot, frame in enumerate(frames):
                delta |= local_symp(letter, sparse_letter(frame, q)) << slot
            deltas.append(delta)
        nxt: dict[int, tuple[int, tuple[int, ...]]] = {}
        for state, (weight, prefix) in dp.items():
            for letter, delta in enumerate(deltas):
                state2 = state ^ delta
                candidate = (weight + int(letter != 0), prefix + (letter,))
                if state2 not in nxt or candidate < nxt[state2]:
                    nxt[state2] = candidate
        dp = nxt
    if desired not in dp:
        return None
    weight, letters = dp[desired]
    tag = tuple((q, letter) for q, letter in zip(active, letters) if letter != 0)
    return int(weight), tag


@dataclass(frozen=True, slots=True)
class TargetPreprocessing:
    targets: tuple[DensePauli, ...]
    baseline_by_coordinate: tuple[int, ...]
    baseline_total: int
    n: int


def preprocess_targets(targets: Sequence[Sequence[int]]) -> TargetPreprocessing:
    """O(n) identity-frame Restore baseline for one ordered six-target tuple."""
    dense = tuple(tuple(int(letter) for letter in target) for target in targets)
    if len(dense) != 6:
        raise ValueError("the frozen grammar requires six ordered targets")
    n = len(dense[0])
    if n < 1 or any(len(target) != n for target in dense):
        raise ValueError("all targets must have the same positive length")
    if any(letter not in range(4) for target in dense for letter in target):
        raise ValueError("target letters must be in {0,1,2,3}")
    baseline = tuple(
        f3(dense[0][q], dense[2][q], dense[4][q]) + f3(dense[1][q], dense[3][q], dense[5][q])
        for q in range(n)
    )
    return TargetPreprocessing(dense, baseline, sum(baseline), n)


def restore_cost_sparse(preprocessing: TargetPreprocessing, pairs: Sequence[FramePair]) -> int:
    """Exact baseline-plus-active-union Restore score."""
    frames = _six_frames(pairs)
    total = preprocessing.baseline_total
    for q in active_union(pairs):
        new = f3(
            local_mul(preprocessing.targets[0][q], sparse_letter(frames[0], q)),
            local_mul(preprocessing.targets[2][q], sparse_letter(frames[2], q)),
            local_mul(preprocessing.targets[4][q], sparse_letter(frames[4], q)),
        )
        new += f3(
            local_mul(preprocessing.targets[1][q], sparse_letter(frames[1], q)),
            local_mul(preprocessing.targets[3][q], sparse_letter(frames[3], q)),
            local_mul(preprocessing.targets[5][q], sparse_letter(frames[5], q)),
        )
        total += new - preprocessing.baseline_by_coordinate[q]
    return int(total)


def restore_cost_full_scan(targets: Sequence[Sequence[int]], pairs: Sequence[FramePair]) -> int:
    """Independent O(n) recomputation used only for final-witness verification."""
    prep = preprocess_targets(targets)
    frames = _six_frames(pairs)
    total = 0
    for q in range(prep.n):
        total += f3(
            local_mul(prep.targets[0][q], sparse_letter(frames[0], q)),
            local_mul(prep.targets[2][q], sparse_letter(frames[2], q)),
            local_mul(prep.targets[4][q], sparse_letter(frames[4], q)),
        )
        total += f3(
            local_mul(prep.targets[1][q], sparse_letter(frames[1], q)),
            local_mul(prep.targets[3][q], sparse_letter(frames[3], q)),
            local_mul(prep.targets[5][q], sparse_letter(frames[5], q)),
        )
    return int(total)


def frame_cost(pairs: Sequence[FramePair], centrals: tuple[int, int, int]) -> int:
    """Frozen normalized Uanti support cost (the production raw cost minus 18)."""
    if centrals not in CENTRALS:
        raise ValueError({"invalid_centrals": centrals})
    total = 0
    for pair, central in zip(pairs, centrals):
        m0, m1 = (2, 4) if central == 0 else (4, 2)
        total += m0 * (pair.w0 - 1) + m1 * (pair.w1 - 1)
    return int(total)


def optimal_centrals(pairs: Sequence[FramePair]) -> tuple[int, int, int]:
    """Put the multiplier two on the heavier frame; choose zero on a tie."""
    return tuple(0 if pair.w0 >= pair.w1 else 1 for pair in pairs)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class SparseWitness:
    cost: int
    pairs: tuple[FramePair, FramePair, FramePair]
    tag: SparsePauli
    orientation: tuple[int, int]
    centrals: tuple[int, int, int]
    permutations: tuple[int, int]
    frame_cost: int
    tag_cost: int
    restore_cost: int

    def as_dict(self) -> dict[str, object]:
        return {
            "cost": self.cost,
            "frames": [
                [[list(item) for item in pair.r0], [list(item) for item in pair.r1]]
                for pair in self.pairs
            ],
            "tag": [list(item) for item in self.tag],
            "orientation": list(self.orientation),
            "centrals": list(self.centrals),
            "relative_permutation_B": self.permutations[0],
            "relative_permutation_C": self.permutations[1],
            "frame_cost": self.frame_cost,
            "tag_cost": self.tag_cost,
            "restore_cost": self.restore_cost,
            "active_union": list(active_union(self.pairs)),
            "tag_constraint_rank": tag_constraint_rank(self.pairs),
        }


class SparseGrammar:
    """Target-independent support-two frame-pair universe for one n."""

    def __init__(self, n: int, max_support: int = 2):
        self.n = int(n)
        self.max_support = int(max_support)
        self.pairs = tuple(ordered_anticommuting_pairs(n, max_support=max_support))
        if max_support == 2 and len(self.pairs) != pair_count_formula(n):
            raise AssertionError(
                {"pair_count_formula_mismatch": [n, len(self.pairs), pair_count_formula(n)]}
            )
        self._small_tag_data = self._build_small_tag_data() if n <= 2 else None

    def _build_small_tag_data(self):
        """Constant-domain acceleration for exhaustive n<=2 verification only."""
        dense_tags = tuple(product(range(4), repeat=self.n))
        order = tuple(
            sorted(
                range(len(dense_tags)),
                key=lambda i: (
                    sum(letter != 0 for letter in dense_tags[i]),
                    dense_tags[i],
                ),
            )
        )
        masks: list[tuple[int, int]] = []
        for pair in self.pairs:
            row = []
            for orientation in ORIENTATIONS:
                mask = 0
                for bit, index in enumerate(order):
                    tag = dense_to_sparse(dense_tags[index])
                    if (
                        sparse_symp(tag, pair.r0),
                        sparse_symp(tag, pair.r1),
                    ) == orientation:
                        mask |= 1 << bit
                row.append(mask)
            masks.append((row[0], row[1]))
        ordered_tags = tuple(dense_to_sparse(dense_tags[index]) for index in order)
        ordered_weights = tuple(len(tag) for tag in ordered_tags)
        return masks, ordered_tags, ordered_weights

    def minimum_tag_indices(
        self, indices: tuple[int, int, int], orientation: tuple[int, int]
    ) -> tuple[int, SparsePauli] | None:
        if self._small_tag_data is None:
            return minimum_tag(tuple(self.pairs[i] for i in indices), orientation)
        orientation_index = ORIENTATIONS.index(orientation)
        masks, tags, weights = self._small_tag_data
        mask = (
            masks[indices[0]][orientation_index]
            & masks[indices[1]][orientation_index]
            & masks[indices[2]][orientation_index]
        )
        if mask == 0:
            return None
        bit = (mask & -mask).bit_length() - 1
        return int(weights[bit]), tags[bit]


def _witness_key(witness: SparseWitness):
    frame_key = tuple((pair.r0, pair.r1) for pair in witness.pairs)
    return (
        witness.cost,
        witness.permutations,
        witness.centrals,
        witness.orientation,
        frame_key,
        witness.tag,
    )


def _ordered_variants(target_pairs: Sequence[Sequence[Sequence[int]]]):
    if len(target_pairs) != 3 or any(len(pair) != 2 for pair in target_pairs):
        raise ValueError("target_pairs must contain three ordered pairs")
    base = tuple(tuple(tuple(int(x) for x in target) for target in pair) for pair in target_pairs)
    for perm_b, perm_c in product((0, 1), repeat=2):
        a = base[0]
        b = base[1] if perm_b == 0 else (base[1][1], base[1][0])
        c = base[2] if perm_c == 0 else (base[2][1], base[2][0])
        yield (perm_b, perm_c), preprocess_targets(a + b + c)


def solve_matching(
    target_pairs: Sequence[Sequence[Sequence[int]]],
    *,
    grammar: SparseGrammar | None = None,
    max_support: int = 2,
) -> SparseWitness:
    """Exact direct optimizer for one canonical matching of six targets.

    The four relative target orders are preprocessed in O(n).  The only
    n-growing search is the Cartesian cube of the O(n^3) pair universe.
    """
    first = target_pairs[0][0]
    n = len(first)
    grammar = grammar or SparseGrammar(n, max_support=max_support)
    if grammar.n != n or grammar.max_support != max_support:
        raise ValueError("grammar does not match target size/support cap")
    variants = tuple(_ordered_variants(target_pairs))
    pair_pool = grammar.pairs
    best: SparseWitness | None = None

    for ia, pair_a in enumerate(pair_pool):
        for ib, pair_b in enumerate(pair_pool):
            for ic, pair_c in enumerate(pair_pool):
                pairs = (pair_a, pair_b, pair_c)
                indices = (ia, ib, ic)
                tag_candidates = []
                for orientation in ORIENTATIONS:
                    solved = grammar.minimum_tag_indices(indices, orientation)
                    if solved is not None:
                        tag_candidates.append((solved[0], orientation, solved[1]))
                if not tag_candidates:
                    continue
                tag_weight, orientation, tag = min(tag_candidates)
                centrals = optimal_centrals(pairs)
                c_frame = frame_cost(pairs, centrals)
                c_tag = 2 * tag_weight
                for permutations, prep in variants:
                    c_restore = restore_cost_sparse(prep, pairs)
                    witness = SparseWitness(
                        c_frame + c_tag + c_restore,
                        pairs,
                        tag,
                        orientation,
                        centrals,
                        permutations,
                        c_frame,
                        c_tag,
                        c_restore,
                    )
                    if best is None or _witness_key(witness) < _witness_key(best):
                        best = witness
    if best is None:
        raise AssertionError("frozen grammar produced no feasible sparse witness")
    return best


def solve_ordered_targets(
    targets: Sequence[Sequence[int]],
    *,
    grammar: SparseGrammar | None = None,
    max_support: int = 2,
    centrals: tuple[int, int, int] | None = None,
    orientation: tuple[int, int] | None = None,
) -> SparseWitness:
    """Exact solver for one already-ordered target/configuration slice.

    This helper is used by the complete n=1 configuration-by-configuration
    verifier.  If centrals or orientation are omitted, their complete frozen
    constant families are optimized.
    """
    prep = preprocess_targets(targets)
    grammar = grammar or SparseGrammar(prep.n, max_support=max_support)
    if grammar.n != prep.n or grammar.max_support != max_support:
        raise ValueError("grammar does not match target size/support cap")
    central_choices = (centrals,) if centrals is not None else CENTRALS
    orientation_choices = (orientation,) if orientation is not None else ORIENTATIONS
    best: SparseWitness | None = None
    pool = grammar.pairs
    for ia, pair_a in enumerate(pool):
        for ib, pair_b in enumerate(pool):
            for ic, pair_c in enumerate(pool):
                pairs = (pair_a, pair_b, pair_c)
                for orient in orientation_choices:
                    solved = grammar.minimum_tag_indices((ia, ib, ic), orient)
                    if solved is None:
                        continue
                    tag_weight, tag = solved
                    c_tag = 2 * tag_weight
                    c_restore = restore_cost_sparse(prep, pairs)
                    for central in central_choices:
                        c_frame = frame_cost(pairs, central)
                        witness = SparseWitness(
                            c_frame + c_tag + c_restore,
                            pairs,
                            tag,
                            orient,
                            central,
                            (0, 0),
                            c_frame,
                            c_tag,
                            c_restore,
                        )
                        if best is None or _witness_key(witness) < _witness_key(best):
                            best = witness
    if best is None:
        raise AssertionError("configuration has no feasible sparse witness")
    return best


def verify_witness(target_pairs, witness: SparseWitness) -> dict[str, bool]:
    """Full-scan verifier for a final sparse witness."""
    variants = dict(_ordered_variants(target_pairs))
    prep = variants[witness.permutations]
    labels = tuple(
        (sparse_symp(witness.tag, pair.r0), sparse_symp(witness.tag, pair.r1))
        for pair in witness.pairs
    )
    minimum = minimum_tag(witness.pairs, witness.orientation)
    rank = tag_constraint_rank(witness.pairs)
    recomputed_restore = restore_cost_full_scan(prep.targets, witness.pairs)
    recomputed_frame = frame_cost(witness.pairs, witness.centrals)
    checks = {
        "three_anticommuting_pairs": all(
            sparse_symp(pair.r0, pair.r1) == 1 for pair in witness.pairs
        ),
        "support_cap": all(
            1 <= len(frame) <= 2 for pair in witness.pairs for frame in (pair.r0, pair.r1)
        ),
        "active_union_at_most_nine": len(active_union(witness.pairs)) <= 9,
        "tag_confined_to_active_union": set(q for q, _ in witness.tag).issubset(
            active_union(witness.pairs)
        ),
        "common_distinct_labels": all(label == witness.orientation for label in labels)
        and witness.orientation in ORIENTATIONS,
        "tag_is_minimum_weight": minimum is not None and len(witness.tag) == minimum[0],
        "tag_support_at_most_rank_at_most_six": len(witness.tag) <= rank <= 6,
        "restore_full_scan_matches_sparse": recomputed_restore == witness.restore_cost,
        "frame_cost_recomputed": recomputed_frame == witness.frame_cost,
        "tag_cost_recomputed": 2 * len(witness.tag) == witness.tag_cost,
        "total_cost_recomputed": (
            recomputed_frame + 2 * len(witness.tag) + recomputed_restore == witness.cost
        ),
    }
    return checks


def build_phase_certificate(target_pairs, witness: SparseWitness) -> dict[str, object]:
    """Reconstruct the frozen exact Restore/common-factor phase witness in O(n).

    Candidate enumeration remains sparse and O(1) per frame triple after target
    preprocessing.  This routine runs only once for the selected optimum; its
    linear work is absorbed by the mandatory O(n) input/output pass.
    """
    variants = dict(_ordered_variants(target_pairs))
    prep = variants[witness.permutations]
    frames = tuple(
        sparse_to_dense(frame, prep.n) for pair in witness.pairs for frame in (pair.r0, pair.r1)
    )
    restores: list[tuple[int, DensePauli]] = []
    restore_checks = []
    for target, frame in zip(prep.targets, frames):
        restore = dense_mul(target, frame)
        got, exponent = dense_mul_phase(restore, frame)
        phase = (-exponent) % 4
        restores.append((phase, restore))
        restore_checks.append(got == target and (phase + exponent) % 4 == 0)

    branch_factors = []
    factor_checks = []
    factor_support = 0
    for branch in (0, 1):
        signed = tuple(restores[2 * block + branch] for block in range(3))
        ts = tuple(row[1] for row in signed)
        g = tuple(
            letters[0] if letters[0] == letters[1] == letters[2] != 0 else 0 for letters in zip(*ts)
        )
        residuals = tuple(dense_mul(g, t) for t in ts)
        exponents = []
        residual_phases = []
        identities = []
        for (original_phase, t), residual in zip(signed, residuals):
            got, exponent = dense_mul_phase(g, residual)
            residual_phase = (original_phase - exponent) % 4
            exponents.append(exponent)
            residual_phases.append(residual_phase)
            identities.append(got == t and (residual_phase + exponent) % 4 == original_phase)
        support = sum(letter != 0 for letter in g) + sum(
            sum(letter != 0 for letter in residual) for residual in residuals
        )
        local_rule = sum(f3(ts[0][q], ts[1][q], ts[2][q]) for q in range(prep.n))
        factor_support += support
        checks = {
            "binary_and_phase_identities": all(identities),
            "support_matches_local_f3_rule": support == local_rule,
        }
        factor_checks.append(all(checks.values()))
        branch_factors.append(
            {
                "branch": branch,
                "G": [list(item) for item in dense_to_sparse(g)],
                "residuals": [
                    [list(item) for item in dense_to_sparse(residual)] for residual in residuals
                ],
                "original_restore_phases": [row[0] for row in signed],
                "G_times_residual_phases": exponents,
                "residual_phases": residual_phases,
                "support": support,
                "checks": checks,
            }
        )

    checks = {
        "restore_binary_and_phase_identities": all(restore_checks),
        "branch_factor_binary_phase_and_support_identities": all(factor_checks),
        "factor_support_matches_witness": factor_support == witness.restore_cost,
        "total_cost_matches_witness": (
            witness.frame_cost + witness.tag_cost + factor_support == witness.cost
        ),
    }
    return {
        "restores": [
            {
                "phase": phase,
                "T": [list(item) for item in dense_to_sparse(restore)],
            }
            for phase, restore in restores
        ],
        "branch_factors": branch_factors,
        "checks": checks,
    }


def perfect_matchings(indices: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], ...]:
    """The 15 canonical unordered perfect matchings of six indices."""
    ordered = tuple(sorted(int(i) for i in indices))
    if len(ordered) != 6 or len(set(ordered)) != 6:
        raise ValueError("exactly six distinct indices are required")

    def rec(rest: tuple[int, ...]):
        if not rest:
            return ((),)
        first = rest[0]
        out = []
        for j in range(1, len(rest)):
            pair = (first, rest[j])
            remaining = rest[1:j] + rest[j + 1 :]
            for tail in rec(remaining):
                out.append((pair,) + tail)
        return tuple(out)

    return tuple(sorted(set(tuple(sorted(row)) for row in rec(ordered))))


def solve_six_targets(
    targets: Sequence[Sequence[int]], *, max_support: int = 2
) -> tuple[tuple[tuple[int, int], ...], SparseWitness]:
    """Exact direct optimizer including the frozen constant 15 matchings."""
    if len(targets) != 6:
        raise ValueError("exactly six targets are required")
    n = len(targets[0])
    grammar = SparseGrammar(n, max_support=max_support)
    best = None
    for matching in perfect_matchings(range(6)):
        target_pairs = tuple((targets[i], targets[j]) for i, j in matching)
        witness = solve_matching(target_pairs, grammar=grammar, max_support=max_support)
        key = (witness.cost, matching, _witness_key(witness))
        if best is None or key < best[0]:
            best = (key, matching, witness)
    if best is None:
        raise AssertionError("no matching produced a sparse witness")
    return best[1], best[2]
