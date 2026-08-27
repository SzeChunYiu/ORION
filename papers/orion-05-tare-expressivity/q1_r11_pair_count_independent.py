#!/usr/bin/env python3
"""Independent finite checks for the Q1 R11 direct-search theorem candidate.

No ORION imports. Phase-ignored Pauli letters are encoded as (x,z) in F_2^2.
The script corroborates, but does not by itself prove:

* exact support<=2 ordered anticommuting-pair count;
* per-weight partner degrees;
* <=3-coordinate union for one anticommuting support-two pair;
* Tag restriction to the six-frame active union;
* agreement of full Tag brute force and a 64-state active-union syndrome DP;
* the rank/support upper bound on a compatible Tag;
* baseline-plus-active-union evaluation of the frozen three-way Restore cost.
"""
from itertools import product

LETTER = {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (1, 1)}
BITS_TO_LETTER = {v: k for k, v in LETTER.items()}
INF = 10**9


def support(p): return sum(v != 0 for v in p)

def local_symp(a, b):
    x, z = LETTER[a]; xp, zp = LETTER[b]
    return (x & zp) ^ (z & xp)

def symp(a, b):
    s = 0
    for u, v in zip(a, b): s ^= local_symp(u, v)
    return s

def mul(a, b):
    x, z = LETTER[a]; xp, zp = LETTER[b]
    return BITS_TO_LETTER[(x ^ xp, z ^ zp)]

def support2_paulis(n): return [p for p in product(range(4), repeat=n) if 1 <= support(p) <= 2]

def ordered_pairs(n):
    ps = support2_paulis(n)
    return [(a, b) for a in ps for b in ps if symp(a, b) == 1]

def pair_formula(n): return 54 * n**3 - 108 * n**2 + 60 * n

def wt1_partner_count(n): return 6 * n - 4

def wt2_partner_count(n): return 12 * n - 16

def union_support(frames):
    out = set()
    for frame in frames: out.update(q for q, letter in enumerate(frame) if letter != 0)
    return tuple(sorted(out))

def tag_syndrome(tag, frames): return tuple(symp(tag, frame) for frame in frames)

def full_tag_minimum(n, frames, rhs):
    best = None
    for tag in product(range(4), repeat=n):
        if tag_syndrome(tag, frames) == rhs:
            w = support(tag); best = w if best is None else min(best, w)
    return best

def restricted_tag_minimum(n, frames, rhs, active):
    best = None
    for letters in product(range(4), repeat=len(active)):
        tag = [0] * n
        for q, letter in zip(active, letters): tag[q] = letter
        tag = tuple(tag)
        if tag_syndrome(tag, frames) == rhs:
            w = support(tag); best = w if best is None else min(best, w)
    return best

def tag_dp_minimum(n, frames, rhs, active):
    zero = (0,) * len(frames); dp = {zero: 0}
    for q in active:
        nxt = {}
        for state, cost in dp.items():
            for letter in range(4):
                one = [0] * n; one[q] = letter
                delta = tag_syndrome(tuple(one), frames)
                state2 = tuple(a ^ b for a, b in zip(state, delta))
                cost2 = cost + int(letter != 0)
                if cost2 < nxt.get(state2, INF): nxt[state2] = cost2
        dp = nxt
    return dp.get(rhs)

def gf2_rank(rows):
    rows = [row for row in rows if row]; rank = 0
    bit = max((row.bit_length() for row in rows), default=0) - 1
    while bit >= 0:
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None: bit -= 1; continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1): rows[i] ^= rows[rank]
        rank += 1; bit -= 1
    return rank

def tag_constraint_rank(frames, active):
    rows = []
    for frame in frames:
        row = 0
        for j, q in enumerate(active):
            fx, fz = LETTER[frame[q]]
            if fz: row |= 1 << (2 * j)
            if fx: row |= 1 << (2 * j + 1)
        rows.append(row)
    return gf2_rank(rows)

def f3(a, b, c):
    if a == b == c != 0: return 1
    return int(a != 0) + int(b != 0) + int(c != 0)

def restore_cost_full(targets, frames):
    n = len(targets[0]); total = 0
    for q in range(n):
        for k in (0, 1):
            letters = [mul(targets[2 * block + k][q], frames[2 * block + k][q]) for block in range(3)]
            total += f3(*letters)
    return total

def restore_cost_active(targets, frames, active):
    n = len(targets[0]); baseline = 0
    for q in range(n):
        baseline += f3(targets[0][q], targets[2][q], targets[4][q])
        baseline += f3(targets[1][q], targets[3][q], targets[5][q])
    total = baseline
    for q in active:
        old = f3(targets[0][q], targets[2][q], targets[4][q]) + f3(targets[1][q], targets[3][q], targets[5][q])
        new = f3(mul(targets[0][q], frames[0][q]), mul(targets[2][q], frames[2][q]), mul(targets[4][q], frames[4][q]))
        new += f3(mul(targets[1][q], frames[1][q]), mul(targets[3][q], frames[3][q]), mul(targets[5][q], frames[5][q]))
        total += new - old
    return total

def deterministic_targets(n, salt):
    return tuple(tuple(((q + 2 * t + salt * (t + 1)) % 4) for q in range(n)) for t in range(6))

def sample_indices(size):
    vals = {0, size - 1, size // 3, (2 * size) // 3}
    return tuple(sorted(v for v in vals if 0 <= v < size))

def check_pair_counts():
    observed = []
    for n in range(1, 7):
        ps = support2_paulis(n)
        total = sum(symp(a, b) == 1 for a in ps for b in ps)
        assert total == pair_formula(n), (n, total, pair_formula(n))
        for a in ps:
            partners = sum(symp(a, b) == 1 for b in ps)
            expected = wt1_partner_count(n) if support(a) == 1 else wt2_partner_count(n)
            assert partners == expected, (n, a, partners, expected)
        for a, b in ordered_pairs(n): assert len(union_support((a, b))) <= 3
        m = 3 * n + 9 * n * (n - 1) // 2
        assert total != m * m; assert total % 2 == 0; assert total // 2 != total
        observed.append(total)
        print(f"n={n} support<=2={len(ps)} ordered_anticommuting={total} formula={pair_formula(n)}")
    assert observed == [6, 120, 666, 1968, 4350, 8136]

def check_active_union_and_tag():
    checked = 0; feasible = 0
    for n in range(1, 5):
        pairs = ordered_pairs(n); idx = sample_indices(len(pairs))
        for ia in idx:
            for ib in idx:
                for ic in idx:
                    frames = pairs[ia] + pairs[ib] + pairs[ic]; active = union_support(frames)
                    assert len(active) <= min(n, 9)
                    for orientation in ((0, 1), (1, 0)):
                        rhs = orientation * 3
                        full = full_tag_minimum(n, frames, rhs)
                        restricted = restricted_tag_minimum(n, frames, rhs, active)
                        dp = tag_dp_minimum(n, frames, rhs, active)
                        assert full == restricted == dp, (n, active, rhs, full, restricted, dp)
                        if full is not None:
                            rank = tag_constraint_rank(frames, active)
                            assert full <= rank <= 6, (n, active, full, rank); feasible += 1
                        checked += 1
                    for salt in (0, 1, 3):
                        targets = deterministic_targets(n, salt)
                        assert restore_cost_full(targets, frames) == restore_cost_active(targets, frames, active)
    assert checked > 0 and feasible > 0
    print(f"tag_active_union_checks={checked} feasible_tag_cases={feasible}")
    n = 2; frames = ordered_pairs(n)[0] * 3; active = union_support(frames)
    outside = next((q for q in range(n) if q not in active), None)
    if outside is not None:
        tag = [0] * n; tag[outside] = 1; assert tuple(tag)[outside] != 0

def main():
    check_pair_counts(); check_active_union_and_tag(); print("Q1_R11_INDEPENDENT_FINITE_CHECK_PASS")

if __name__ == "__main__": main()
