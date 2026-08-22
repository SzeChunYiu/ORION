#!/usr/bin/env python3
"""QG-24 generic verifier — from primitives, no analyzer import, no numpy.

Re-derives, rather than re-reads, everything QG-24 claims:

1. every digest (protocol, QG-21 receipt, staged predictions, result digest);
2. the donor-search gate, re-implemented here from ``donor_search``'s stated
   rules, plus the stronger check that every verbatim passage actually occurs in
   the committed query log;
3. Lemma L1, by an independent implementation of the merge search over the
   COMPLETE n=1 configuration space of the frozen grammar -- including the
   claim that the only position pairs the relation ever admits are the two block
   seams;
4. the n=1 rotation-count distribution, by complete re-enumeration;
5. the domain-size identity at every declared n, from an independent nine-bit
   dynamic program that shares no code with the analyzer's transform-based count;
6. every panel row: the decidable predicate, and the serialized seven-rotation
   witness -- re-checked against the grammar constraints, re-counted under the
   merge relation, and its theta_FT cost recomputed from scratch;
7. the terminal, the gate block and the forecast tally, for consistency with the
   re-derived numbers.

What this verifier establishes is every UPPER bound (a seven-rotation
compilation of the stated cost exists), every complete-enumeration count it
recomputes, and every arithmetic and digest claim. The LOWER bound -- that no
cheaper seven-rotation member exists -- is the exact DP's claim and is reported
as such, not silently absorbed.

Usage: qg24_generic_verify.py [results.json]
Exit 0 on ACCEPT, 1 on REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_RESULTS = REPO / "research/extensions/orion-qg/QG24_ROTATION_REGIME_RESULTS.json"
QG21_RESULTS = REPO / "research/extensions/orion-qg/QG21_FT_CHEMISTRY_RESULTS.json"
DONOR_LOG = REPO / "development/orion-qg-regime-geometry/QG24_DONOR_SEARCH.md"

# ---- binary symplectic Pauli primitives, written out ------------------------
CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
BITS_CODE = {b: i for i, b in enumerate(CODE_BITS)}


def lsymp(a, b):
    xa, za = CODE_BITS[a]
    xb, zb = CODE_BITS[b]
    return (xa & zb) ^ (za & xb)


def lmul(a, b):
    xa, za = CODE_BITS[a]
    xb, zb = CODE_BITS[b]
    return BITS_CODE[(xa ^ xb, za ^ zb)]


def pmul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def pwt(a):
    return bin(a[0] | a[1]).count("1")


def psymp(a, b):
    return (bin(a[0] & b[1]).count("1") + bin(a[1] & b[0]).count("1")) & 1


def pcode(a, q):
    return BITS_CODE[(((a[0] >> q) & 1), ((a[1] >> q) & 1))]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---- independent merge search ----------------------------------------------
# Uanti for m=2 is exp(i.t/2 R_nc).exp(i.p R_c).exp(i.t/2 R_nc); three blocks in
# sequence give nine rotations. Slot order (aA,bA,aB,bB,aC,bC).
POS = (0, 1, 0, 2, 3, 2, 4, 5, 4)
SEAM = {2: 0, 5: 1}  # Clifford intervener after this position; 0 = block A, 1 = B


def merge_search(eq, sp, comm, in_place):
    """comm[b][s] = 1 iff both Restore branch letters of block b commute with s."""
    edges = []
    for i in range(9):
        for j in range(i + 1, 9):
            si = POS[i]
            if not eq[si][POS[j]]:
                continue
            if any(sp[POS[k]][si] for k in range(i + 1, j)):
                continue
            if in_place and any(not comm[b][si] for p, b in SEAM.items() if i <= p < j):
                continue
            edges.append((i, j))
    best = [0]

    def rec(used, idx, cnt):
        if cnt > best[0]:
            best[0] = cnt
        for t in range(idx, len(edges)):
            i, j = edges[t]
            if (used >> i) & 1 or (used >> j) & 1:
                continue
            rec(used | (1 << i) | (1 << j), t + 1, cnt + 1)

    rec(0, 0, 0)
    return 9 - best[0], edges


def slot_data(frames, centrals, restores):
    slots = []
    for j in range(3):
        r0, r1 = frames[j]
        a, c = (r0, r1) if centrals[j] == 1 else (r1, r0)
        slots.extend([a, c])
    eq = [[1 if slots[i] == slots[j] else 0 for j in range(6)] for i in range(6)]
    sp = [[psymp(slots[i], slots[j]) for j in range(6)] for i in range(6)]
    comm = [[1 if all(psymp(t, slots[k]) == 0 for t in restores[b]) else 0
             for k in range(6)] for b in range(3)]
    return slots, eq, sp, comm


# ---- complete n=1 re-enumeration -------------------------------------------
ACCEPT9 = (0b010000111, 0b100000111)


def _state9(r, s):
    rA0, rA1, rB0, rB1, rC0, rC1 = r
    sA0, sB0, sC0 = lsymp(s, rA0), lsymp(s, rB0), lsymp(s, rC0)
    sA1, sB1, sC1 = lsymp(s, rA1), lsymp(s, rB1), lsymp(s, rC1)
    return (lsymp(rA0, rA1)
            | (lsymp(rB0, rB1) << 1)
            | (lsymp(rC0, rC1) << 2)
            | ((sA0 ^ sB0) << 3)
            | ((sA0 ^ sC0) << 4)
            | ((sA1 ^ sB1) << 5)
            | ((sA1 ^ sC1) << 6)
            | (sA0 << 7)
            | (sA1 << 8))


def enumerate_n1():
    """Complete n=1 enumeration: distribution per model and the pair support."""
    dist = {"R6L_RESTORE_IN_PLACE": {7: 0, 8: 0, 9: 0},
            "R6M_RESTORE_FACTORED": {7: 0, 8: 0, 9: 0}}
    pair_support, total = set(), 0
    for centrals in itertools.product((0, 1), repeat=3):
        for r in itertools.product(range(4), repeat=6):
            for s in range(4):
                if _state9(r, s) not in ACCEPT9:
                    continue
                frames = [(r[0], r[1]), (r[2], r[3]), (r[4], r[5])]
                slots = []
                for j in range(3):
                    r0, r1 = frames[j]
                    a, c = (r0, r1) if centrals[j] == 1 else (r1, r0)
                    slots.extend([a, c])
                eq = [[1 if slots[i] == slots[j] else 0 for j in range(6)]
                      for i in range(6)]
                sp = [[lsymp(slots[i], slots[j]) for j in range(6)]
                      for i in range(6)]
                for tA0, tA1, tB0, tB1 in itertools.product(range(4), repeat=4):
                    comm = [
                        [1 if (lsymp(tA0, slots[k]) == 0 and lsymp(tA1, slots[k]) == 0)
                         else 0 for k in range(6)],
                        [1 if (lsymp(tB0, slots[k]) == 0 and lsymp(tB1, slots[k]) == 0)
                         else 0 for k in range(6)],
                        [1] * 6,
                    ]
                    total += 1
                    for model in dist:
                        rc, edges = merge_search(
                            eq, sp, comm, model == "R6L_RESTORE_IN_PLACE")
                        dist[model][rc] += 1
                        pair_support.update(edges)
    return dist, sorted([i + 1, j + 1] for i, j in pair_support), total


def admissible_frame_tag_counts(n_values):
    """Independent nine-bit DP counting admissible (frames, Tag) assignments."""
    local = [0] * 512
    for r in itertools.product(range(4), repeat=6):
        for s in range(4):
            local[_state9(r, s)] += 1
    nz = [(d, c) for d, c in enumerate(local) if c]
    dp = [0] * 512
    dp[0] = 1
    out = {}
    for q in range(1, max(n_values) + 1):
        nxt = [0] * 512
        for t, cur in enumerate(dp):
            if cur:
                for d, c in nz:
                    nxt[t ^ d] += cur * c
        dp = nxt
        if q in n_values:
            out[q] = dp[ACCEPT9[0]] + dp[ACCEPT9[1]]
    return out


# ---- panel witness re-derivation -------------------------------------------

def theta_ft_cost(a, bs, S, targets, centrals, n):
    """theta_FT Clifford cost (4,2,2,1) of a seven-rotation compilation."""
    frames = [((a, bs[j]) if centrals[j] == 1 else (bs[j], a)) for j in range(3)]
    cost = 0
    for j in range(3):
        nc, c = (1 - centrals[j]), centrals[j]
        cost += 4 * (pwt(frames[j][nc]) - 1) + 2 * (pwt(frames[j][c]) - 1)
    cost += 2 * pwt(S)
    restores = [(pmul(targets[j][0], frames[j][0]),
                 pmul(targets[j][1], frames[j][1])) for j in range(3)]
    for k in range(2):
        ta, tb, tc = (restores[0][k], restores[1][k], restores[2][k])
        for q in range(n):
            la, lb, lc = pcode(ta, q), pcode(tb, q), pcode(tc, q)
            if la == lb == lc and la != 0:
                cost += 1
            else:
                cost += (la != 0) + (lb != 0) + (lc != 0)
    return cost, frames, restores
