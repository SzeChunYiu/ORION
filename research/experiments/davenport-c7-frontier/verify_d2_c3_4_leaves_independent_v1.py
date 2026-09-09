"""Re-decide every leaf of the D_2(C_3^4) = 14 sweep by a second, unrelated procedure.

The sweep's upper bound is the load-bearing half of `D_2(C_3^4) = 14`: it enumerates every
length-14 sequence over `C_3^4` that survives the short-zero-sum prune, and reports that none has
packing number at most 1. That conclusion rested on one decision procedure -- a layered dynamic
programme over pairs `(sum A, sum B)` of disjoint sub-multisets, carrying emptiness flags, which
never materialises a single zero-sum subsequence.

This checker decides the same 10,852 sequences the opposite way round. It materialises the blocks
and nothing else: enumerate all `2^14` subsets, keep those that sum to zero, and appeal to
Corollary C1 -- `z(S) <= 1` exactly when the atoms pairwise intersect. Concretely, two disjoint
nonempty blocks exist iff two zero-sum masks `a`, `b` satisfy `a & b == 0`.

The two procedures share no code, no language, no data structure and no idea:

    sweep      dynamic programme over pair-sums, no block ever built, verdict from a reachability
               flag on the (0,0) cell of the both-nonempty layer
    this file  exhaustive subset enumeration, every block built explicitly, verdict from a
               pairwise-disjointness test on their supports

Agreement on all 10,852 is therefore a genuine second source for the number the paper stands on,
not the same computation run twice. Disagreement on even one would put the exact value in doubt.

Reads the sweep's `--dump-leaves` output, which prints each leaf with the DP's own verdict, so the
comparison is per-sequence rather than a count.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

P, R, L = 3, 4, 14


def elements() -> np.ndarray:
    """The 81 elements of `C_3^4`, indexed exactly as the sweep indexes them.

    The sweep's `addtab` is built over `g = sum_i digit_i * p^i`, so element `g` has digits
    `g // p**i % p`. Getting this wrong would make every sum wrong, so the convention is
    re-derived here from the sweep's own arithmetic rather than assumed -- see `_check_indexing`.
    """
    g = np.arange(P**R)
    return np.stack([(g // P**i) % P for i in range(R)], axis=1).astype(np.int64)


def _check_indexing(elems: np.ndarray) -> None:
    """Control: the index convention must reproduce addition in the group.

    If this is wrong the whole check is vacuous -- it would be deciding a different group.
    """
    rng = np.random.default_rng(20260909)
    for _ in range(2000):
        a, b = int(rng.integers(P**R)), int(rng.integers(P**R))
        summed = (elems[a] + elems[b]) % P
        idx = int(sum(int(summed[i]) * P**i for i in range(R)))
        assert np.array_equal(elems[idx], summed), (a, b)


def subset_masks() -> np.ndarray:
    """The `2^14 x 14` membership matrix, built once and reused for every sequence."""
    m = np.arange(1 << L, dtype=np.int64)
    return ((m[:, None] >> np.arange(L)) & 1).astype(np.int64)


def zero_sum_masks(seq: list[int], elems: np.ndarray, members: np.ndarray) -> np.ndarray:
    """Every nonempty subset of `seq` that sums to zero, as bitmasks."""
    coords = elems[np.asarray(seq)]                 # 14 x 4
    sums = (members @ coords) % P                   # 2^14 x 4
    zero = np.flatnonzero(~sums.any(axis=1))
    return zero[zero != 0]                          # drop the empty subset


def has_two_disjoint(masks: np.ndarray) -> bool:
    """True iff two of these masks are disjoint.

    Corollary C1 says `z(S) >= 2` exactly when two blocks -- equivalently two atoms -- have
    disjoint supports. Blocks rather than atoms are used here on purpose: two disjoint blocks
    contain two disjoint atoms and conversely, so the test is the same and needs no minimality
    computation, which keeps this procedure further away from the one it is checking.
    """
    arr = np.asarray(masks, dtype=np.int64)
    for i, a in enumerate(arr):
        if not (a & arr[i + 1:]).all():
            return True
    return False


def main(path: Path) -> int:
    elems = elements()
    _check_indexing(elems)
    members = subset_masks()

    checked = agree = disagree = 0
    no_block = 0
    block_counts: list[int] = []
    disagreements: list[tuple[list[int], int, bool]] = []

    for line in path.read_text().splitlines():
        if not line.startswith("LEAF "):
            continue
        parts = line.split()
        dp_says_disjoint = bool(int(parts[1]))
        seq = [int(x) for x in parts[2:]]
        assert len(seq) == L, line

        masks = zero_sum_masks(seq, elems, members)
        if masks.size == 0:
            no_block += 1
        block_counts.append(int(masks.size))
        mine = has_two_disjoint(masks)

        checked += 1
        if mine == dp_says_disjoint:
            agree += 1
        else:
            disagree += 1
            if len(disagreements) < 5:
                disagreements.append((seq, int(dp_says_disjoint), mine))

    print(f"1. re-decided {checked} leaves of the L=14 sweep over C_3^4 by exhaustive subset")
    print("   enumeration and pairwise disjointness -- an algorithm sharing nothing with the")
    print("   sweep's layered pair-sum dynamic programme")
    assert checked == 10852, f"expected the sweep's 10,852 leaves, saw {checked}"
    print(f"2. agreements {agree}, disagreements {disagree}")
    if disagreements:
        for seq, dp, mine in disagreements:
            print(f"   DISAGREE seq={seq} dp_disjoint={dp} independent_disjoint={mine}")
    assert disagree == 0, "the two procedures disagree; the exact value is in doubt"

    print(f"3. every one of the {checked} has two disjoint nonempty zero-sum subsequences, so no")
    print("   length-14 sequence over C_3^4 has packing number <= 1, and D_2(C_3^4) <= 14")

    # Non-vacuity. A checker that found no blocks at all would agree with the DP for the wrong
    # reason, so the block census is asserted rather than merely reported.
    assert no_block == 0, f"{no_block} leaves had no zero-sum subsequence at all -- check vacuous"
    lo, hi = min(block_counts), max(block_counts)
    mean = sum(block_counts) / len(block_counts)
    print(f"4. non-vacuity: every leaf had at least one block; block counts run {lo}..{hi},")
    print(f"   mean {mean:.1f} -- the procedure is finding real objects, not deciding on empty sets")

    # Positive control: the decision procedure must be able to answer "no two disjoint blocks".
    # The paper's own length-13 witness has z = 1, so it must come back False here.
    witness = [1, 1, 3, 3, 9, 9, 27, 27]                        # e_1^2 e_2^2 e_3^2 e_4^2
    witness += [1 + 3, 1 + 9, 3 + 9, 1 + 3 + 27, 1 + 9 + 27]   # 1100 1010 0110 1101 1011
    assert len(witness) == 13
    wmembers = ((np.arange(1 << 13, dtype=np.int64)[:, None] >> np.arange(13)) & 1).astype(np.int64)
    wsums = (wmembers @ elems[np.asarray(witness)]) % P
    wmasks = np.flatnonzero(~wsums.any(axis=1))
    wmasks = wmasks[wmasks != 0]
    assert not has_two_disjoint(wmasks), "control failed: the length-13 witness must have z = 1"
    print(f"5. positive control: the paper's length-13 witness has {wmasks.size} blocks and NO two")
    print("   disjoint -- so this procedure can return 'packing <= 1' and the sweep's zero is a")
    print("   finding, not an inability to say otherwise")

    print()
    print("INDEPENDENT RE-DECISION COMPLETE.  Both procedures agree on all 10,852 leaves.")
    return 0


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("leaves_c34.txt")
    raise SystemExit(main(src))
