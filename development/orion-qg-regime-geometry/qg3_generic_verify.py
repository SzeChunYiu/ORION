#!/usr/bin/env python3
"""Independent QG-3 verifier: rebuilds the boundary-prospective forecast from
primitives and re-decides it against
research/extensions/orion-qg/QG3_BOUNDARY_PROSPECTIVE_RESULTS.json.

Nothing from research/extensions/orion-q is imported. In particular r6m / r6o /
r6q / r6r / r6f / p10 and the analyzer qg3_boundary_prospective.py are never
imported, and none of their tables are re-used. Everything this file checks is
rebuilt from:

  * a numerically derived local Pauli algebra (products, phases, commutation and
    weights read off the 2x2 matrices I, X, Y, Z rather than written down as
    symplectic bit rules), and
  * the frozen cost model of QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md sections 2-5.

Internal representation is deliberately different from the analyzer's. Paulis
are tuples of local letter codes (0=I, 1=X, 2=Y, 3=Z), not (x, z) bitmask pairs;
(x, z) keys are produced only at the boundary where receipt values are compared.
The exact R6M referee is re-implemented with a different parity-state encoding:
the analyzer tracks four XOR-difference bits and accepts two states out of 512,
this file tracks the nine raw constraint parities

    (<rA0,rA1>, <rB0,rB1>, <rC0,rC1>, <s,rA0>, <s,rB0>, <s,rC0>,
     <s,rA1>, <s,rB1>, <s,rC1>)

and accepts the single state (1,1,1,c0,c0,c0,c1,c1,c1) for each of the two label
orientations (c0, c1). The two encodings cut the same feasible set; agreeing on
the optimum is therefore evidence and not a tautology. The rebuilt referee is
additionally cross-checked against exhaustive enumeration at n=1 and against an
independent global-Pauli enumeration at n=2 before it is used.

Coverage is complete, not sampled: every staged row of both tracks is checked,
all 15 canonical matchings of every admitted batch, the full seed-20260824 draw
stream up to the receipt's own stop point, and the whole pinned library listing.

Prints exactly one canonical stdout token line
ORIONQG_QG3_GENERIC_VERIFY={...}; the per-row agreement table goes to stderr.
Exit status 0 on ACCEPT, 1 on REJECT.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROTOCOL = REPO / "development" / "orion-qg-regime-geometry" / (
    "QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md"
)
RESULTS = REPO / "research" / "extensions" / "orion-qg" / (
    "QG3_BOUNDARY_PROSPECTIVE_RESULTS.json"
)
R6O_RECEIPT = REPO / "research" / "extensions" / "orion-q" / (
    "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json"
)

LIBRARY_REPO = "npbauman/DUCC-Hamiltonian-Library"
CLONE_URL = f"https://github.com/{LIBRARY_REPO}"
RAW_BASE = f"https://raw.githubusercontent.com/{LIBRARY_REPO}"
PROTECTED_PATH = "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
ACTIVE_SPACE_RE = re.compile(r"^(?:FrozenCoreCCSD_)?(\d+)Elec_(\d+)Orbs$")

INF_SENTINEL = 10 ** 9          # protocol f_B sentinel
BIG = 10 ** 9                   # internal unreachable marker
SEED = 20260824
QUOTAS = {"split": 4, "borrow": 4, "donor_exact": 4}
STREAM_CAP = 400
GATE_MIN_TOTAL, GATE_MIN_SPLIT, GATE_MIN_BORROW = 10, 3, 3
WINDOW = 12
PRINT_THRESH = 5e-11
PAULI_THRESH = 1e-9
# Protocol section 0.3 pre-freeze timing instance; never a subject of the lane.
TIMING_INSTANCE = (((1, 0), (1, 0)), ((8, 0), (8, 0)), ((96, 0), (96, 96)))
# Protocol section 4 hand-derived closed forms, a priori, per engineered family.
FAMILY_CLOSED_FORM = {
    "F1": {"C_R6L": 8, "C_Dplus": 8, "f_B": 7, "C": 7, "regime": "borrow"},
    "F2": {"C_R6L": 13, "C_Dplus": 11, "f_B": 11, "C": 11, "regime": "split"},
}
# Fields the stage-2 referee adds; the stage-1 stamped object must contain none.
STAGE2_FIELDS = frozenset(
    {
        "C_DP",
        "truth_regime",
        "truth_donor_exact",
        "C_Dxx_pinched",
        "dxx_pinched_equal",
        "dp_witness_checks_pass",
        "cost_match",
        "regime_match",
    }
)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def note(*args) -> None:
    print(*args, file=sys.stderr)


# --------------------------------------------------------------------------
# 1. local Pauli algebra, derived numerically from the 2x2 matrices
# --------------------------------------------------------------------------
_MAT = [
    np.array([[1, 0], [0, 1]], dtype=complex),
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
]
_UNITS = (1 + 0j, 1j, -1 + 0j, -1j)


def _identify(mat):
    for letter in range(4):
        for power, unit in enumerate(_UNITS):
            if np.allclose(mat, unit * _MAT[letter]):
                return letter, power
    raise AssertionError("matrix is not a phased Pauli")


LMUL = [[0] * 4 for _ in range(4)]
LPOW = [[0] * 4 for _ in range(4)]
LSYMP = [[0] * 4 for _ in range(4)]
for _a in range(4):
    for _b in range(4):
        _letter, _power = _identify(_MAT[_a] @ _MAT[_b])
        LMUL[_a][_b] = _letter
        LPOW[_a][_b] = _power
        LSYMP[_a][_b] = int(
            not np.allclose(_MAT[_a] @ _MAT[_b], _MAT[_b] @ _MAT[_a])
        )
LWT = [0, 1, 1, 1]
# (x, z) bits per letter, taken from the matrix identity P(x,z) = i^(xz) X^x Z^z.
LBITS = []
for _l in range(4):
    _x = int(np.allclose(_MAT[_l], _MAT[1]) or np.allclose(_MAT[_l], _MAT[2]))
    _z = int(np.allclose(_MAT[_l], _MAT[3]) or np.allclose(_MAT[_l], _MAT[2]))
    LBITS.append((_x, _z))
BITS_LETTER = {bits: letter for letter, bits in enumerate(LBITS)}

NMUL = np.array(LMUL, dtype=np.int64)
NSYMP = np.array(LSYMP, dtype=np.int64)
NWT = np.array(LWT, dtype=np.int64)
# Donor-owned all-three common-factor rule as a local letter-triple cost.
FACTOR3 = np.zeros((4, 4, 4), dtype=np.int64)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            FACTOR3[_a, _b, _c] = (
                1 if (_a == _b == _c != 0) else LWT[_a] + LWT[_b] + LWT[_c]
            )

ORDERED_LETTER_PAIRS = tuple(itertools.permutations((1, 2, 3), 2))
LABEL_ORIENTATIONS = ((0, 1), (1, 0))


# --------------------------------------------------------------------------
# 2. word helpers (a word is a tuple of n local letter codes)
# --------------------------------------------------------------------------
def key_to_word(key, n):
    x, z = int(key[0]), int(key[1])
    return tuple(BITS_LETTER[((x >> q) & 1, (z >> q) & 1)] for q in range(n))


def word_to_key(word):
    x = z = 0
    for q, letter in enumerate(word):
        bx, bz = LBITS[letter]
        x |= bx << q
        z |= bz << q
    return (x, z)


def wmul(a, b):
    return tuple(LMUL[x][y] for x, y in zip(a, b))


def wwt(word):
    return sum(1 for letter in word if letter)


def wsymp(a, b):
    out = 0
    for x, y in zip(a, b):
        out ^= LSYMP[x][y]
    return out


def unit(letter, q, n):
    return tuple(letter if i == q else 0 for i in range(n))


def factor_support(ta, tb, tc):
    """Support of the donor-factored restore triple, letter by letter."""
    total = 0
    for x, y, z in zip(ta, tb, tc):
        if x == y == z != 0:
            total += 1
        else:
            total += LWT[x] + LWT[y] + LWT[z]
    return total


def letter_masks(word, out, k):
    for q, letter in enumerate(word):
        if letter:
            out[k, letter - 1] |= 1 << q


# --------------------------------------------------------------------------
# 3. the four frozen family costs, rebuilt
# --------------------------------------------------------------------------
def cost_r6l(blocks, n):
    """C_R6L: three weight-one TARE-M2 frames sharing one weight-one Tag.

    The shared key is (Tag Pauli, label orientation). A weight-one Tag at qubit q
    with letter u forces one member of every block's ordered frame-letter pair;
    the other member and the target order stay free, so each block contributes
    exactly four representations per key. All 6n keys are enumerated.
    """
    best = None
    for q in range(n):
        for u in (1, 2, 3):
            others = [c for c in (1, 2, 3) if c != u]
            for labels in LABEL_ORIENTATIONS:
                per_block = []
                for pair in blocks:
                    options = []
                    for other in others:
                        a, b = (u, other) if labels == (0, 1) else (other, u)
                        r0, r1 = unit(a, q, n), unit(b, q, n)
                        for perm in (0, 1):
                            ordered = pair if perm == 0 else (pair[1], pair[0])
                            options.append(
                                (wmul(ordered[0], r0), wmul(ordered[1], r1))
                            )
                    per_block.append(options)
                for oa in per_block[0]:
                    for ob in per_block[1]:
                        for oc in per_block[2]:
                            value = (
                                2
                                + factor_support(oa[0], ob[0], oc[0])
                                + factor_support(oa[1], ob[1], oc[1])
                            )
                            if best is None or value < best:
                                best = value
    if best is None:
        raise AssertionError("R6L family is empty")
    return int(best)


def _dplus_block(pair, n, labels):
    anchors, forced, base, masks = [], [], [], []
    for q in range(n):
        for letters in ORDERED_LETTER_PAIRS:
            r0, r1 = unit(letters[0], q, n), unit(letters[1], q, n)
            for perm in (0, 1):
                ordered = pair if perm == 0 else (pair[1], pair[0])
                t0, t1 = wmul(ordered[0], r0), wmul(ordered[1], r1)
                anchors.append(q)
                forced.append(letters[0] if labels == (0, 1) else letters[1])
                base.append(wwt(t0) + wwt(t1))
                row = np.zeros((2, 3), dtype=np.int64)
                letter_masks(t0, row, 0)
                letter_masks(t1, row, 1)
                masks.append(row)
    return (
        np.array(anchors, dtype=np.int64),
        np.array(forced, dtype=np.int64),
        np.array(base, dtype=np.int64),
        np.stack(masks),
    )


def cost_dplus(blocks, n):
    """C_Dplus: enlarged-Tag donor closure, anchors free per block.

    Each block picks an anchor qubit, an ordered weight-one frame-letter pair and
    a target order. Blocks sharing an anchor must force the same Tag letter there;
    the Tag weight is the number of distinct anchors. The restore cost is written
    as sum-of-weights minus twice the all-three letter coincidences, and the
    coincidences are counted by population count on per-letter qubit bitmasks
    rather than by a per-qubit table lookup.
    """
    best = None
    for labels in LABEL_ORIENTATIONS:
        (aa, fa, ba, ma), (ab, fb, bb, mb), (ac, fc, bc, mc) = (
            _dplus_block(pair, n, labels) for pair in blocks
        )
        total = ba[:, None, None] + bb[None, :, None] + bc[None, None, :]
        for k in range(2):
            for v in range(3):
                total -= 2 * np.bitwise_count(
                    ma[:, k, v][:, None, None]
                    & mb[:, k, v][None, :, None]
                    & mc[:, k, v][None, None, :]
                )
        same_ab = aa[:, None] == ab[None, :]
        same_ac = aa[:, None] == ac[None, :]
        same_bc = ab[:, None] == ac[None, :]
        distinct = (
            3
            - same_ab[:, :, None].astype(np.int64)
            - same_ac[:, None, :].astype(np.int64)
            - same_bc[None, :, :].astype(np.int64)
            + (same_ab[:, :, None] & same_ac[:, None, :]).astype(np.int64)
        )
        total += 2 * distinct
        feasible = (
            ((~same_ab) | (fa[:, None] == fb[None, :]))[:, :, None]
            & ((~same_ac) | (fa[:, None] == fc[None, :]))[:, None, :]
            & ((~same_bc) | (fb[:, None] == fc[None, :]))[None, :, :]
        )
        value = int(np.where(feasible, total, BIG).min())
        if value >= BIG:
            continue
        if best is None or value < best:
            best = value
    if best is None:
        raise AssertionError("D+ family produced no feasible point")
    return int(best)


def _borrow_block(pair, n, q_tag, v):
    """Frozen borrow family options for one block at Tag letter v on q_tag."""
    others = [c for c in (1, 2, 3) if c != v]
    v_key = unit(v, q_tag, n)
    anchored, phantom = [], []
    for c in others:
        c_key = unit(c, q_tag, n)
        for sigma in (0, 1):
            anchored.append(
                (wmul(pair[sigma], v_key), wmul(pair[1 - sigma], c_key))
            )
    support = [q for q in range(n) if pair[0][q] or pair[1][q]]
    for q_home in support:
        if q_home == q_tag:
            continue
        for ell in others:
            ell_key = unit(ell, q_tag, n)
            for m0 in (1, 2, 3):
                m0_key = unit(m0, q_home, n)
                for m1 in (1, 2, 3):
                    if m1 == m0:
                        continue
                    anti = wmul(ell_key, unit(m1, q_home, n))
                    for sigma in (0, 1):
                        phantom.append(
                            (wmul(pair[sigma], m0_key), wmul(pair[1 - sigma], anti))
                        )
    rows, extra = [], []
    for group, surcharge in ((anchored, 0), (phantom, 2)):
        seen = set()
        for row in group:
            if row in seen:
                continue
            seen.add(row)
            rows.append(row)
            extra.append(surcharge)
    n_anchored = sum(1 for e in extra if e == 0)
    base = np.array([wwt(r[0]) + wwt(r[1]) + e for r, e in zip(rows, extra)],
                    dtype=np.int64)
    masks = np.zeros((len(rows), 2, 3), dtype=np.int64)
    for i, row in enumerate(rows):
        letter_masks(row[0], masks[i], 0)
        letter_masks(row[1], masks[i], 1)
    return base, masks, n_anchored


def cost_borrow(blocks, n):
    """f_B: exact minimum over the frozen borrow family (>= 1 phantom block).

    Candidate Tag qubits are the union support plus one empty representative;
    the all-anchored corner is excluded because that corner is R6L, not a borrow.
    Returns None when the family is empty at every candidate.
    """
    union = set()
    for pair in blocks:
        for k in (0, 1):
            union |= {q for q in range(n) if pair[k][q]}
    tag_qubits = sorted(union)
    for q in range(n):
        if q not in union:
            tag_qubits.append(q)
            break
    best = None
    for q_tag in tag_qubits:
        for v in (1, 2, 3):
            per_block = [_borrow_block(pair, n, q_tag, v) for pair in blocks]
            if all(len(b) == na for b, _m, na in per_block):
                continue
            (ba, ma, na), (bb, mb, nb), (bc, mc, nc) = per_block
            total = ba[:, None, None] + bb[None, :, None] + bc[None, None, :]
            for k in range(2):
                for v2 in range(3):
                    total -= 2 * np.bitwise_count(
                        ma[:, k, v2][:, None, None]
                        & mb[:, k, v2][None, :, None]
                        & mc[:, k, v2][None, None, :]
                    )
            total[:na, :nb, :nc] = BIG
            value = int(total.min())
            if value >= BIG:
                continue
            value += 2  # the weight-one Tag itself
            if best is None or value < best:
                best = value
    return None if best is None else int(best)


# ---- exact frozen-grammar referee (raw nine-parity encoding) ---------------
_OPTIONS = np.arange(4 ** 7, dtype=np.int64)
_DIGITS = [((_OPTIONS >> (2 * (6 - t))) & 3) for t in range(7)]
_S, _A0, _A1, _B0, _B1, _C0, _C1 = _DIGITS
_PARITY = (
    (NSYMP[_A0, _A1] << 0)
    | (NSYMP[_B0, _B1] << 1)
    | (NSYMP[_C0, _C1] << 2)
    | (NSYMP[_S, _A0] << 3)
    | (NSYMP[_S, _B0] << 4)
    | (NSYMP[_S, _C0] << 5)
    | (NSYMP[_S, _A1] << 6)
    | (NSYMP[_S, _B1] << 7)
    | (NSYMP[_S, _C1] << 8)
)
_ORDER = np.argsort(_PARITY, kind="stable")
_PARITY_VALUES, _GROUP_START = np.unique(_PARITY[_ORDER], return_index=True)
_TAG_COST = 2 * NWT[_S]
_FRAME_COST = {}
for _centrals in itertools.product((0, 1), repeat=3):
    _acc = np.zeros(4 ** 7, dtype=np.int64)
    for _j, _central in enumerate(_centrals):
        _acc = (
            _acc
            + (2 if _central == 0 else 4) * NWT[_DIGITS[1 + 2 * _j]]
            + (2 if _central == 1 else 4) * NWT[_DIGITS[2 + 2 * _j]]
        )
    _FRAME_COST[_centrals] = _acc
_XOR512 = np.bitwise_xor(np.arange(512)[:, None], np.arange(512)[None, :])
# Accepting parity per label orientation: all three frames anticommuting, and the
# Tag reproducing (c0, c1) against every block's ordered frame pair.
ACCEPTING = {
    (c0, c1): 0b111 | (c0 * 0b111 << 3) | (c1 * 0b111 << 6)
    for c0, c1 in LABEL_ORIENTATIONS
}
_LOCAL_CACHE: dict = {}
# The R6M raw frame cost charges 4 + 2 per block for a weight-one frame pair;
# the frozen rule measures support above weight one, hence the constant 18.
FRAME_OFFSET = 18


def _local_table(six_letters, centrals):
    hit = _LOCAL_CACHE.get((six_letters, centrals))
    if hit is not None:
        return hit
    branch0 = FACTOR3[
        NMUL[six_letters[0], _A0],
        NMUL[six_letters[2], _B0],
        NMUL[six_letters[4], _C0],
    ]
    branch1 = FACTOR3[
        NMUL[six_letters[1], _A1],
        NMUL[six_letters[3], _B1],
        NMUL[six_letters[5], _C1],
    ]
    cost = _FRAME_COST[centrals] + _TAG_COST + branch0 + branch1
    table = np.full(512, BIG, dtype=np.int64)
    table[_PARITY_VALUES] = np.minimum.reduceat(cost[_ORDER], _GROUP_START)
    _LOCAL_CACHE[(six_letters, centrals)] = table
    return table


def cost_dp(blocks, n):
    """C_DP: exact unrestricted optimum of the frozen R6M grammar."""
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            ordered = (
                blocks[0],
                blocks[1] if perm_b == 0 else (blocks[1][1], blocks[1][0]),
                blocks[2] if perm_c == 0 else (blocks[2][1], blocks[2][0]),
            )
            six = (
                ordered[0][0], ordered[0][1],
                ordered[1][0], ordered[1][1],
                ordered[2][0], ordered[2][1],
            )
            for centrals in itertools.product((0, 1), repeat=3):
                dp = np.full(512, BIG, dtype=np.int64)
                dp[0] = 0
                for q in range(n):
                    letters = tuple(int(six[t][q]) for t in range(6))
                    dp = (dp[_XOR512] + _local_table(letters, centrals)[:, None]).min(
                        axis=0
                    )
                for state in ACCEPTING.values():
                    raw = int(dp[state])
                    if raw >= BIG:
                        continue
                    value = raw - FRAME_OFFSET
                    if best is None or value < best:
                        best = value
    if best is None:
        raise AssertionError("R6M grammar has no accepting configuration")
    return int(best)


# --------------------------------------------------------------------------
# 4. self-validation of the rebuilt referee (exhaustive at n=1, global at n=2)
# --------------------------------------------------------------------------
def _relative_orders(blocks):
    """The four block-order configurations the grammar allows (A stays fixed)."""
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            yield (
                blocks[0],
                blocks[1] if perm_b == 0 else (blocks[1][1], blocks[1][0]),
                blocks[2] if perm_c == 0 else (blocks[2][1], blocks[2][0]),
            )


def _referee_brute_n1(blocks):
    """Full 4^7 enumeration of the identical grammar at n=1, no DP."""
    best = None
    for ordered in _relative_orders(blocks):
        for option in itertools.product(range(4), repeat=7):
            s, ra0, ra1, rb0, rb1, rc0, rc1 = option
            frames = ((ra0, ra1), (rb0, rb1), (rc0, rc1))
            if not all(LSYMP[f[0]][f[1]] for f in frames):
                continue
            c0, c1 = LSYMP[s][ra0], LSYMP[s][ra1]
            if c0 == c1:
                continue
            if any(LSYMP[s][f[0]] != c0 or LSYMP[s][f[1]] != c1 for f in frames):
                continue
            for centrals in itertools.product((0, 1), repeat=3):
                raw = 2 * LWT[s]
                for j, central in enumerate(centrals):
                    raw += (2 if central == 0 else 4) * LWT[frames[j][0]]
                    raw += (2 if central == 1 else 4) * LWT[frames[j][1]]
                for k in (0, 1):
                    triple = tuple(
                        LMUL[ordered[j][k][0]][frames[j][k]] for j in range(3)
                    )
                    raw += int(FACTOR3[triple[0], triple[1], triple[2]])
                value = raw - FRAME_OFFSET
                if best is None or value < best:
                    best = value
    return best


def _referee_brute_n2(blocks):
    """Independent global two-qubit Pauli enumeration of the same grammar."""
    n = 2
    words = [key_to_word((x, z), n) for x in range(4) for z in range(4)]
    best = None
    for ordered in _relative_orders(blocks):
        for s in words:
            if wwt(s) == 0:
                continue
            for c0, c1 in LABEL_ORIENTATIONS:
                pairs = [
                    (r0, r1)
                    for r0 in words
                    for r1 in words
                    if wsymp(r0, r1) == 1
                    and wsymp(s, r0) == c0
                    and wsymp(s, r1) == c1
                ]
                if not pairs:
                    continue
                for centrals in itertools.product((0, 1), repeat=3):
                    per_block = []
                    for j in range(3):
                        m0 = 2 if centrals[j] == 0 else 4
                        m1 = 2 if centrals[j] == 1 else 4
                        per_block.append(
                            [
                                (
                                    m0 * wwt(r0) + m1 * wwt(r1),
                                    wmul(ordered[j][0], r0),
                                    wmul(ordered[j][1], r1),
                                )
                                for r0, r1 in pairs
                            ]
                        )
                    tag = 2 * wwt(s)
                    for ra in per_block[0]:
                        for rb in per_block[1]:
                            for rc in per_block[2]:
                                value = (
                                    ra[0] + rb[0] + rc[0] + tag
                                    + factor_support(ra[1], rb[1], rc[1])
                                    + factor_support(ra[2], rb[2], rc[2])
                                    - FRAME_OFFSET
                                )
                                if best is None or value < best:
                                    best = value
    return best


_SELFTEST_N1 = (
    (("X", "Z"), ("X", "Z"), ("X", "Z")),
    (("X", "Z"), ("Z", "X"), ("Y", "X")),
    (("X", "Y"), ("Z", "Y"), ("Z", "X")),
)
_SELFTEST_N2 = (
    (((1, 0), (0, 1)), ((3, 0), (0, 3)), ((1, 2), (2, 1))),
    (((3, 1), (1, 3)), ((2, 3), (3, 2)), ((1, 0), (2, 2))),
)
_LETTER_OF = {"X": 1, "Y": 2, "Z": 3}


def referee_selftest():
    """Fixed hand-chosen panels; no sampling. Returns (ok, rows)."""
    rows = []
    ok = True
    for panel in _SELFTEST_N1:
        blocks = tuple(
            ((_LETTER_OF[a],), (_LETTER_OF[b],)) for a, b in panel
        )
        mine, brute = cost_dp(blocks, 1), _referee_brute_n1(blocks)
        ok &= mine == brute
        rows.append({"n": 1, "panel": list(panel), "dp": mine, "brute": brute})
    for panel in _SELFTEST_N2:
        blocks = tuple(
            tuple(key_to_word(key, 2) for key in pair) for pair in panel
        )
        mine, brute = cost_dp(blocks, 2), _referee_brute_n2(blocks)
        ok &= mine == brute
        rows.append(
            {"n": 2, "panel": [[list(k) for k in p] for p in panel],
             "dp": mine, "brute": brute}
        )
    return ok, rows


# --------------------------------------------------------------------------
# 5. the frozen Track-B generator, re-implemented from protocol section 4
# --------------------------------------------------------------------------
def _distinct_pair(rng):
    perm = rng.permutation(3)
    return int(perm[0]) + 1, int(perm[1]) + 1


def draw_instance(rng, i):
    family = ("F1", "F2", "F3")[i % 3]
    if family == "F1":
        n = 3 if (i // 3) % 2 == 0 else 4
        qperm = rng.permutation(n)
        q0, qh, qk = int(qperm[0]), int(qperm[1]), int(qperm[2])
        u = int(rng.integers(1, 4))
        p1, r1 = _distinct_pair(rng)
        p2, r2 = _distinct_pair(rng)
        heavy = (
            wmul(unit(p1, qh, n), unit(p2, qk, n)),
            wmul(unit(r1, qh, n), unit(r2, qk, n)),
        )
        tag_block = (unit(u, q0, n), unit(u, q0, n))
        blocks = [tag_block, tag_block]
        blocks.insert(int(rng.integers(0, 3)), heavy)
        return family, n, tuple(blocks)
    if family == "F2":
        n = 5
        qperm = rng.permutation(5)
        q0 = int(qperm[0])
        a, b = int(qperm[1]), int(qperm[2])
        c, d = int(qperm[3]), int(qperm[4])
        u = int(rng.integers(1, 4))
        p1, r1 = _distinct_pair(rng)
        p2, r2 = _distinct_pair(rng)
        s1, t1 = _distinct_pair(rng)
        s2, t2 = _distinct_pair(rng)
        heavy1 = (
            wmul(unit(p1, a, n), unit(p2, b, n)),
            wmul(unit(r1, a, n), unit(r2, b, n)),
        )
        heavy2 = (
            wmul(unit(s1, c, n), unit(s2, d, n)),
            wmul(unit(t1, c, n), unit(t2, d, n)),
        )
        light = (unit(u, q0, n), unit(u, q0, n))
        base = [light, heavy1, heavy2]
        slotperm = rng.permutation(3)
        slots = [None, None, None]
        for j in range(3):
            slots[int(slotperm[j])] = base[j]
        return family, n, tuple(slots)
    n = 3
    targets = []
    for _t in range(6):
        for _attempt in range(200):
            x = int(rng.integers(0, 8))
            z = int(rng.integers(0, 8))
            if (x, z) == (0, 0):
                continue
            word = key_to_word((x, z), n)
            if wwt(word) > 2:
                continue
            if all(wsymp(word, prev) == 0 for prev in targets):
                targets.append(word)
                break
        else:
            return None
    return family, n, tuple(
        (targets[2 * j], targets[2 * j + 1]) for j in range(3)
    )


# --------------------------------------------------------------------------
# 6. pinned library: tree metadata, DUCC parse, Jordan-Wigner
# --------------------------------------------------------------------------
def _cache_root() -> Path:
    root = Path(os.environ.get("ORIONQG_QG3_VERIFY_CACHE") or tempfile.gettempdir())
    root.mkdir(parents=True, exist_ok=True)
    return root


def _git(args, cwd=None) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
        timeout=600,
    ).stdout


def pinned_listing(commit):
    """[(path, blob)] at the pinned commit. Metadata only: no blob is fetched."""
    clone = _cache_root() / "orionqg_qg3_verify_tree"
    usable = clone.is_dir()
    if usable:
        try:
            usable = _git(["cat-file", "-t", commit], cwd=clone).strip() == "commit"
        except (subprocess.SubprocessError, OSError):
            usable = False
    if not usable:
        _git(["clone", "--quiet", "--filter=blob:none", "--no-checkout",
              CLONE_URL, str(clone)])
        if _git(["cat-file", "-t", commit], cwd=clone).strip() != "commit":
            raise AssertionError({"pinned_commit_unreachable": commit})
    rows = []
    for line in _git(["ls-tree", "-r", "--full-tree", commit], cwd=clone).splitlines():
        meta, path = line.split("\t", 1)
        _mode, otype, sha1 = meta.split()
        if otype == "blob":
            rows.append((path, sha1))
    rows.sort()
    if not rows:
        raise AssertionError("pinned tree listing is empty")
    return rows


def blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def fetch_verified(commit, path, expected_blob, excluded_molecules):
    """Fetch one library file. Refuses excluded molecules and the reserved path."""
    if path == PROTECTED_PATH:
        raise AssertionError("verifier refused to fetch the reserved discriminator")
    if path.split("/")[0] in excluded_molecules:
        raise AssertionError({"excluded_molecule_fetch_refused": path})
    cache = _cache_root() / "orionqg_qg3_verify_src"
    cache.mkdir(parents=True, exist_ok=True)
    slot = cache / expected_blob
    if slot.is_file():
        raw = slot.read_bytes()
        if blob_sha1(raw) == expected_blob:
            return raw.decode("utf-8")
    with urllib.request.urlopen(f"{RAW_BASE}/{commit}/{path}", timeout=90) as handle:
        raw = handle.read()
    observed = blob_sha1(raw)
    if observed != expected_blob:
        raise AssertionError({"blob_mismatch": [path, observed, expected_blob]})
    slot.write_bytes(raw)
    return raw.decode("utf-8")


def active_space(path):
    for segment in path.split("/"):
        matched = ACTIVE_SPACE_RE.match(segment)
        if matched:
            electrons, orbitals = int(matched.group(1)), int(matched.group(2))
            occupied = electrons // 2
            return occupied, orbitals - occupied, orbitals
    raise AssertionError({"no_active_space_segment": path})


def parse_ducc(text, n_occ, n_virt, n_orb):
    """Sparse read of the published DUCC active-space integral blocks."""
    one = np.zeros((n_orb, n_orb))
    two = {}
    mode = ""
    blocks = ("IJ", "IA", "AB", "IJKL", "ABCD", "IJAB", "AIJB", "IJKA", "IABC")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if mode == "":
            if fields[0] == "Begin" and len(fields) >= 3 and fields[2] == "Block":
                if fields[1] in blocks:
                    mode = fields[1]
            continue
        if fields[0] == "End":
            mode = ""
            continue
        if fields[0] == "Begin":
            continue
        idx = [int(t) for t in fields[:-1]]
        v = float(fields[-1])
        if mode == "IJ":
            i, j = idx[0] - 1, idx[1] - 1
            one[i, j] = one[j, i] = v
        elif mode == "IA":
            i, a = idx[0] - 1, idx[1] - 1 + n_occ
            one[i, a] = one[a, i] = v
        elif mode == "AB":
            a, b = idx[0] - 1 + n_occ, idx[1] - 1 + n_occ
            one[a, b] = one[b, a] = v
        elif mode == "IJKL":
            i, j = idx[0] - 1, idx[1] - 1 - n_occ
            k, l = idx[2] - 1, idx[3] - 1 - n_occ
            two[(i, k, j, l)] = v
        elif mode == "ABCD":
            a = idx[0] - 1 + n_occ
            b = idx[1] - 1 - n_virt + n_occ
            c = idx[2] - 1 + n_occ
            d = idx[3] - 1 - n_virt + n_occ
            two[(a, c, b, d)] = v
        elif mode == "IJAB":
            i = idx[0] - 1
            j = idx[1] - 1 - n_occ
            a = idx[2] - 1 + n_occ
            b = idx[3] - 1 - n_virt + n_occ
            two[(i, a, j, b)] = v
            two[(a, i, b, j)] = v
        elif mode == "AIJB":
            if idx[2] > n_occ:
                a = idx[0] - 1 + n_occ
                i = idx[1] - 1 - n_occ
                j = idx[2] - 1 - n_occ
                b = idx[3] - 1 + n_occ
                two[(a, b, i, j)] = -v
                two[(i, j, a, b)] = -v
            else:
                a = idx[0] - 1 + n_occ
                i = idx[1] - 1 - n_occ
                j = idx[2] - 1
                b = idx[3] - 1 - n_virt + n_occ
                two[(a, j, i, b)] = v
                two[(j, a, b, i)] = v
        elif mode == "IJKA":
            i = idx[0] - 1
            j = idx[1] - 1 - n_occ
            k = idx[2] - 1
            a = idx[3] - 1 - n_virt + n_occ
            two[(i, k, j, a)] = v
            two[(j, a, i, k)] = v
            two[(k, i, a, j)] = v
            two[(a, j, k, i)] = v
        elif mode == "IABC":
            i = idx[0] - 1
            a = idx[1] - 1 - n_virt + n_occ
            b = idx[2] - 1 + n_occ
            c = idx[3] - 1 - n_virt + n_occ
            two[(i, b, a, c)] = v
            two[(b, i, c, a)] = v
            two[(a, c, i, b)] = v
            two[(c, a, b, i)] = v
    if mode:
        raise AssertionError({"unterminated_block": mode})
    return one, two


def _phased_product(a, b):
    word_a, power_a = a
    word_b, power_b = b
    letters = []
    power = (power_a + power_b) % 4
    for x, y in zip(word_a, word_b):
        letters.append(LMUL[x][y])
        power = (power + LPOW[x][y]) % 4
    return (tuple(letters), power)


def _ladder(j, dagger, nq):
    """a_j (dagger=False) or a_j^+ as Z-string times (X -/+ iY) / 2."""
    zstring = tuple(3 if m < j else 0 for m in range(nq))
    with_x = tuple(1 if m == j else zstring[m] for m in range(nq))
    with_y = tuple(2 if m == j else zstring[m] for m in range(nq))
    return (
        ((with_x, 0), 0.5 + 0j),
        ((with_y, 0), (-0.5j if dagger else 0.5j)),
    )


def jordan_wigner(one, two, n_orb):
    nq = 2 * n_orb

    @lru_cache(maxsize=None)
    def monomial(ops):
        poly = {(tuple([0] * nq), 0): 1 + 0j}
        for j, dagger in ops:
            nxt = defaultdict(complex)
            for word, coeff in poly.items():
                for factor, amplitude in _ladder(j, dagger, nq):
                    product = _phased_product(word, factor)
                    nxt[(product[0], 0)] += coeff * amplitude * _UNITS[product[1]]
            poly = dict(nxt)
        return tuple(poly.items())

    acc = defaultdict(complex)

    def emit(coeff, ops):
        if abs(coeff) <= PRINT_THRESH:
            return
        for (word, _), amplitude in monomial(tuple(ops)):
            acc[word] += coeff * amplitude

    spatial = range(n_orb)
    for w in spatial:
        for x in spatial:
            for y in spatial:
                for z in spatial:
                    direct = two.get((w, x, y, z), 0.0)
                    exchange = two.get((w, z, y, x), 0.0)
                    v = 0.25 * (direct - exchange)
                    if abs(v) > PRINT_THRESH:
                        emit(v, ((w, True), (y, True), (z, False), (x, False)))
                        emit(v, ((w + n_orb, True), (y + n_orb, True),
                                 (z + n_orb, False), (x + n_orb, False)))
    for w in spatial:
        for x in spatial:
            for y in spatial:
                for z in spatial:
                    g = two.get((w, x, y, z), 0.0)
                    if abs(g) <= PRINT_THRESH:
                        continue
                    v = 0.25 * g
                    a, b = w, x
                    c, d = y + n_orb, z + n_orb
                    emit(v, ((a, True), (c, True), (d, False), (b, False)))
                    emit(v, ((c, True), (a, True), (b, False), (d, False)))
                    emit(-v, ((c, True), (a, True), (d, False), (b, False)))
                    emit(-v, ((a, True), (c, True), (b, False), (d, False)))
    for w in spatial:
        for x in spatial:
            v = float(one[w, x])
            if abs(v) > PRINT_THRESH:
                emit(v, ((w, True), (x, False)))
                emit(v, ((w + n_orb, True), (x + n_orb, False)))
    out = {}
    max_imag = 0.0
    for word, coeff in acc.items():
        max_imag = max(max_imag, abs(coeff.imag))
        if abs(coeff) > PAULI_THRESH:
            if abs(coeff.imag) > 5e-8:
                raise AssertionError({"non_hermitian_coefficient": list(word)})
            out[word] = float(coeff.real)
    return out, max_imag


def subject_terms(commit, path, blob, excluded_molecules):
    n_occ, n_virt, n_orb = active_space(path)
    text = fetch_verified(commit, path, blob, excluded_molecules)
    one, two = parse_ducc(text, n_occ, n_virt, n_orb)
    paulis, max_imag = jordan_wigner(one, two, n_orb)
    paulis.pop(tuple([0] * (2 * n_orb)), None)
    ordered = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), word_to_key(kv[0])))
    return ordered, max_imag, (n_occ, n_virt, n_orb)


def fragile_sort_positions(ordered, tolerance=1e-12):
    """Adjacent positions where the |coefficient| ordering is arithmetic-fragile.

    The term list is sorted by descending |coefficient| and then by the integer
    Pauli key. Exact ties are therefore decided arithmetic-free. A pair whose
    magnitudes differ by less than `tolerance` in relative terms is the only way
    a different summation order could permute the list, so those positions are
    reported and checked against the batch indices actually used.
    """
    fragile = []
    for i in range(len(ordered) - 1):
        a, b = abs(ordered[i][1]), abs(ordered[i + 1][1])
        if a == b or a == 0:
            continue
        if (a - b) < tolerance * a:
            fragile.append(i)
    return fragile


def perfect_matchings(indices):
    idx = tuple(sorted(int(i) for i in indices))
    if len(idx) != 6 or len(set(idx)) != 6:
        raise AssertionError({"batch_not_six_unique": list(idx)})

    def rec(rest):
        if not rest:
            return [()]
        out = []
        for j in range(1, len(rest)):
            remaining = rest[1:j] + rest[j + 1:]
            for tail in rec(remaining):
                out.append(((rest[0], rest[j]),) + tail)
        return out

    matchings = sorted(
        {tuple(sorted(tuple(sorted(p)) for p in m)) for m in rec(idx)}
    )
    if len(matchings) != 15:
        raise AssertionError({"matching_count_not_15": len(matchings)})
    return tuple(matchings)


# --------------------------------------------------------------------------
# 7. verification
# --------------------------------------------------------------------------
def normalise_targets(targets):
    return tuple(tuple(tuple(int(x) for x in t) for t in pair) for pair in targets)


def committed_forbidden_targets():
    """Targets recorded verbatim in the committed R6O receipt (freshness bar)."""
    if not R6O_RECEIPT.is_file():
        return None
    receipt = json.loads(R6O_RECEIPT.read_text())
    out = set()
    for row in receipt["domains"]["structured_n2"]["violating_instances_verbatim"]:
        out.add(normalise_targets(row["targets"]))
    for row in receipt["domains"]["random_panel"]["violating_instances_verbatim"]:
        flat = [tuple(int(x) for x in t) for t in row["targets"]]
        out.add(tuple((flat[2 * j], flat[2 * j + 1]) for j in range(3)))
    return out


def classify(c_r6l, c_dplus, f_b_eff):
    predicted = min(c_r6l, c_dplus, f_b_eff)
    if predicted == c_r6l:
        return predicted, "donor_exact"
    if predicted == c_dplus:
        return predicted, "split"
    return predicted, "borrow"


def truth_regime_of(c_dp, c_r6l, c_dplus):
    if c_dp == c_r6l:
        return "donor_exact"
    if c_dp == c_dplus:
        return "split"
    return "borrow"


def evaluate(blocks, n):
    c_r6l = cost_r6l(blocks, n)
    c_dplus = cost_dplus(blocks, n)
    f_b = cost_borrow(blocks, n)
    f_b_eff = INF_SENTINEL if f_b is None else f_b
    c_dp = cost_dp(blocks, n)
    return c_r6l, c_dplus, f_b_eff, c_dp


def compare_row(track, row_id, blocks, n, receipt_row, mismatches, table):
    """Recompute one staged row and record field-by-field agreement."""
    c_r6l, c_dplus, f_b_eff, c_dp = evaluate(blocks, n)
    predicted, predicted_regime = classify(c_r6l, c_dplus, f_b_eff)
    truth = truth_regime_of(c_dp, c_r6l, c_dplus)
    mine = {
        "C_R6L": c_r6l,
        "C_Dplus": c_dplus,
        "f_B": f_b_eff,
        "C_DP": c_dp,
        "Gsplit": c_r6l - c_dplus,
        "predicate_P1": (c_dplus == c_r6l) and (f_b_eff >= c_r6l),
        "predicted_C_DP": predicted,
        "predicted_regime": predicted_regime,
        "truth_regime": truth,
        "C_Dxx_pinched": c_dp if c_dp == c_dplus else None,
        "dxx_pinched_equal": c_dp == c_dplus,
        "cost_match": c_dp == predicted,
        "regime_match": truth == predicted_regime,
    }
    theirs = {field: receipt_row.get(field) for field in mine}
    differing = sorted(f for f in mine if mine[f] != theirs[f])
    # frozen structural obligations, re-derived rather than read
    algebra = {
        "predicate_identity": mine["predicate_P1"] == (predicted == c_r6l),
        "sandwich": c_dp <= c_dplus <= c_r6l,
        "borrow_soundness": c_dp <= f_b_eff,
        "two_trade_identity": c_dp == predicted,
        "regime_agreement": truth == predicted_regime,
    }
    broken = sorted(k for k, v in algebra.items() if not v)
    table.append(
        {
            "track": track,
            "row": row_id,
            "n": n,
            "mine": mine,
            "receipt": theirs,
            "differing_fields": differing,
            "algebra_violations": broken,
        }
    )
    if differing or broken:
        mismatches.append(
            {
                "track": track,
                "row": row_id,
                "n": n,
                "targets": [[list(word_to_key(t)) for t in pair] for pair in blocks],
                "verifier": mine,
                "receipt": theirs,
                "differing_fields": differing,
                "algebra_violations": broken,
            }
        )
    return not differing and not broken


def main() -> int:
    started = time.monotonic()
    raw = json.loads(RESULTS.read_text())
    checks: dict[str, bool] = {}
    counts: dict[str, object] = {}
    mismatches: list = []
    table: list = []
    taken_as_given: list[str] = []

    # ---- identity, protocol binding, terminal ----------------------------
    checks["schema"] = raw.get("schema") == "ORIONQG.QG3.BoundaryProspective.v1"
    checks["protocol_sha256"] = raw.get("protocol_sha256") == sha256_text(
        PROTOCOL.read_text()
    )
    checks["authority_ceiling"] = (
        "NOT_R6" in str(raw.get("authority", ""))
        and raw.get("r6_authority") is False
        and raw.get("novelty_credit") is False
        and raw.get("donor_novelty_credit") is False
        and raw.get("reserved_stretched_n2_accessed") is False
    )

    # ---- referee self-validation before it is trusted --------------------
    selftest_ok, selftest_rows = referee_selftest()
    checks["referee_selftest_n1_n2"] = selftest_ok
    counts["referee_selftest"] = selftest_rows

    # ---- stage-1 digest discipline ---------------------------------------
    track_a, track_b = raw["track_a"], raw["track_b"]

    def strip_stage2(row):
        return {k: v for k, v in row.items() if k not in STAGE2_FIELDS}

    stage1_payload = {
        "protocol": "QG3_BOUNDARY_PROSPECTIVE_PROTOCOL",
        "protocol_sha256": raw["protocol_sha256"],
        "predicate": (
            "P1(t) := [C_R6L(t) == C_Dplus(t)] AND [f_B(t) >= C_R6L(t)]; "
            "predicted_C_DP := min(C_R6L, C_Dplus, f_B)"
        ),
        "track_a": {
            "library": track_a["library"],
            "selection_rule": track_a["selection_rule"],
            "attempts": track_a["attempts"],
            "admitted_batches": [
                {"subject": b["subject"], "rows": [strip_stage2(r) for r in b["rows"]]}
                for b in track_a["admitted_batches"]
            ],
        },
        "track_b": {
            k: v
            for k, v in track_b.items()
            if k not in ("staged_instances", "truth_regime_census")
        }
        | {"staged_instances": [strip_stage2(r) for r in track_b["staged_instances"]]},
    }
    rebuilt_digest = sha256_text(canonical(stage1_payload))
    checks["stage1_digest_rebuilt"] = rebuilt_digest == raw.get("stage1_digest")
    stamped_rows = [
        row
        for batch in stage1_payload["track_a"]["admitted_batches"]
        for row in batch["rows"]
    ] + list(stage1_payload["track_b"]["staged_instances"])
    checks["stage1_payload_free_of_referee_output"] = not any(
        field in row for row in stamped_rows for field in STAGE2_FIELDS
    )
    counts["stage1_digest"] = {"rebuilt": rebuilt_digest,
                               "receipt": raw.get("stage1_digest")}

    # ---- Track B: replay the frozen generator, then referee every row ----
    forbidden = committed_forbidden_targets()
    if forbidden is None:
        taken_as_given.append(
            "committed R6O verbatim violation lists unavailable; Track-B freshness "
            "against them not re-checked"
        )
    rng = np.random.default_rng(SEED)
    staged = []
    tally = {k: 0 for k in QUOTAS}
    excluded = {k: 0 for k in QUOTAS}
    draws = rejected = 0
    replay_ok = True
    for i in range(STREAM_CAP):
        if all(tally[k] >= QUOTAS[k] for k in QUOTAS):
            break
        draws += 1
        drawn = draw_instance(rng, i)
        if drawn is None:
            rejected += 1
            continue
        family, n, blocks = drawn
        c_r6l = cost_r6l(blocks, n)
        c_dplus = cost_dplus(blocks, n)
        f_b = cost_borrow(blocks, n)
        f_b_eff = INF_SENTINEL if f_b is None else f_b
        _, regime = classify(c_r6l, c_dplus, f_b_eff)
        if tally[regime] < QUOTAS[regime]:
            tally[regime] += 1
            staged.append({"i": i, "family": family, "n": n, "blocks": blocks})
        else:
            excluded[regime] += 1

    receipt_b = track_b["staged_instances"]
    checks["trackb_stream_shape"] = (
        draws == track_b["draws_processed"]
        and rejected == track_b["f3_rejected_draws"]
        and tally == track_b["staged_predicted_counts"]
        and excluded == track_b["excluded_predicted_census"]
        and len(staged) == len(receipt_b)
    )
    for mine, theirs in zip(staged, receipt_b):
        same = (
            mine["i"] == theirs["stream_index"]
            and mine["family"] == theirs["family"]
            and mine["n"] == theirs["n"]
            and [[list(word_to_key(t)) for t in pair] for pair in mine["blocks"]]
            == theirs["targets"]
        )
        if not same:
            replay_ok = False
            mismatches.append(
                {
                    "track": "B",
                    "row": theirs["stream_index"],
                    "kind": "generator_replay",
                    "verifier": {
                        "stream_index": mine["i"],
                        "family": mine["family"],
                        "n": mine["n"],
                        "targets": [
                            [list(word_to_key(t)) for t in pair]
                            for pair in mine["blocks"]
                        ],
                    },
                    "receipt": {
                        "stream_index": theirs["stream_index"],
                        "family": theirs["family"],
                        "n": theirs["n"],
                        "targets": theirs["targets"],
                    },
                }
            )
    checks["trackb_generator_replay"] = replay_ok
    checks["trackb_quota_gate"] = (
        len(staged) >= GATE_MIN_TOTAL
        and tally["split"] >= GATE_MIN_SPLIT
        and tally["borrow"] >= GATE_MIN_BORROW
    ) == bool(track_b["quota_gate_met"])

    commuting_b = fresh_b = closed_form_ok = True
    b_agree = 0
    for mine, theirs in zip(staged, receipt_b):
        blocks, n = mine["blocks"], mine["n"]
        six = [t for pair in blocks for t in pair]
        commuting_b &= all(
            wsymp(six[a], six[b]) == 0 for a in range(6) for b in range(a + 1, 6)
        )
        norm = normalise_targets(
            [[word_to_key(t) for t in pair] for pair in blocks]
        )
        fresh_b &= norm != normalise_targets(TIMING_INSTANCE)
        if forbidden is not None:
            fresh_b &= norm not in forbidden
        ok = compare_row("B", theirs["stream_index"], blocks, n, theirs,
                         mismatches, table)
        b_agree += int(ok)
        expected = FAMILY_CLOSED_FORM.get(mine["family"])
        if expected is not None:
            closed_form_ok &= (
                theirs["C_R6L"] == expected["C_R6L"]
                and theirs["C_Dplus"] == expected["C_Dplus"]
                and theirs["f_B"] == expected["f_B"]
                and theirs["C_DP"] == expected["C"]
                and theirs["truth_regime"] == expected["regime"]
                and theirs["predicted_regime"] == expected["regime"]
            )
    checks["trackb_pairwise_commuting"] = commuting_b
    checks["trackb_freshness"] = fresh_b
    checks["trackb_rows_rederived"] = b_agree == len(receipt_b) == 12
    checks["trackb_protocol_closed_forms"] = closed_form_ok
    counts["track_b_rows"] = {"total": len(receipt_b), "agreeing": b_agree}

    # ---- Track A: pinned listing, frozen scan order, then every matching --
    library = track_a["library"]
    rule = track_a["selection_rule"]
    excluded_molecules = tuple(rule["excluded_molecules"])
    committed_blobs = set(rule["committed_subject_blobs_excluded"])
    listing = pinned_listing(library["commit"])
    ducc = [(p, b) for p, b in listing if p.endswith(".ducc.results.txt")]
    listing_digest = sha256_text("\n".join(f"{b} {p}" for p, b in ducc) + "\n")
    checks["tracka_library_listing"] = (
        len(ducc) == library["ducc_results_files_at_commit"]
        and listing_digest == library["ducc_listing_sha256"]
        and library["repo"] == LIBRARY_REPO
    )

    candidates = []
    for path, blob in ducc:
        parts = path.split("/")
        if parts[0] in excluded_molecules:
            continue
        if not any(seg in ("DUCC2", "DUCC3") for seg in parts):
            continue
        space = None
        for seg in parts:
            matched = ACTIVE_SPACE_RE.match(seg)
            if matched:
                space = (int(matched.group(1)), int(matched.group(2)))
                break
        if space is None:
            continue
        electrons, orbitals = space
        if electrons % 2:
            continue
        occupied = electrons // 2
        if not 1 <= occupied < orbitals:
            continue
        candidates.append({"path": path, "blob": blob, "n_qubits": 2 * orbitals})
    candidates.sort(key=lambda c: (c["n_qubits"], c["path"]))
    fresh = [c for c in candidates if c["blob"] not in committed_blobs]
    scanned = fresh[: int(rule["scan_cap"])]
    checks["tracka_scan_order"] = (
        len(fresh) == rule["eligible_candidate_count_after_committed_exclusion"]
        and scanned == rule["scanned_candidates_in_order"]
        and [
            {"path": a["path"], "blob": a["blob"], "n_qubits": a["n_qubits"]}
            for a in track_a["attempts"]
        ]
        == scanned
    )
    checks["tracka_exclusions_honoured"] = (
        all(a["path"] != PROTECTED_PATH for a in track_a["attempts"])
        and all(
            a["path"].split("/")[0] not in excluded_molecules
            for a in track_a["attempts"]
        )
        and all(a["blob"] not in committed_blobs for a in track_a["attempts"])
    )

    a_rows = a_agree = 0
    subjects_ok = commuting_a = matchings_ok = windows_ok = order_robust = True
    fragile_report = []
    predicted_census = {"donor_exact": 0, "split": 0, "borrow": 0}
    truth_census = {"donor_exact": 0, "split": 0, "borrow": 0}
    for batch in track_a["admitted_batches"]:
        subject = batch["subject"]
        n = int(subject["n_qubits"])
        terms, max_imag, space = subject_terms(
            library["commit"], subject["path"], subject["blob"], excluded_molecules
        )
        subjects_ok &= (
            len(terms) == subject["terms"]
            and abs(max_imag - float(subject["max_imag"])) <= 1e-24
            and space == (subject["n_occ"], subject["n_virt"], subject["n_orb"])
            and 2 * space[2] == n
        )
        six = [int(i) for i in subject["frozen_source_indices"]]
        fragile = fragile_sort_positions(terms)
        touching = [i for i in fragile if i in six or i + 1 in six]
        order_robust &= not touching
        fragile_report.append(
            {
                "blob": subject["blob"][:8],
                "fragile_adjacent_positions": fragile,
                "touching_batch_indices": touching,
            }
        )
        six_words = [terms[i][0] for i in six]
        commuting_a &= all(
            wsymp(six_words[a], six_words[b]) == 0
            for a in range(6)
            for b in range(a + 1, 6)
        )
        # the recorded batch must be two disjoint 12-term window champions
        starts = sorted(int(w) for w in subject["champion_windows"])
        grouped = sorted(
            len([i for i in six if start <= i < start + WINDOW]) for start in starts
        )
        windows_ok &= len(starts) == 2 and starts[0] != starts[1] and grouped == [3, 3]
        matchings = perfect_matchings(six)
        matchings_ok &= [[list(p) for p in m] for m in matchings] == [
            r["matching"] for r in batch["rows"]
        ]
        for pairs, receipt_row in zip(matchings, batch["rows"]):
            blocks = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            ok = compare_row(
                "A", f"{subject['blob'][:8]}:{list(pairs)}", blocks, n,
                receipt_row, mismatches, table,
            )
            a_rows += 1
            a_agree += int(ok)
            entry = table[-1]["mine"]
            predicted_census[entry["predicted_regime"]] += 1
            truth_census[entry["truth_regime"]] += 1
        note(
            f"  track A {subject['path'][:52]:54s} n={n} "
            f"rows={len(batch['rows'])} agree={a_agree}/{a_rows}"
        )
    checks["tracka_subject_reconstruction"] = subjects_ok
    checks["tracka_pairwise_commuting"] = commuting_a
    checks["tracka_matchings_complete"] = matchings_ok
    checks["tracka_batch_window_structure"] = windows_ok
    checks["tracka_term_order_robust_at_batch_indices"] = order_robust
    counts["tracka_term_order_fragility"] = fragile_report
    checks["tracka_rows_rederived"] = a_agree == a_rows == 90
    checks["tracka_census"] = (
        predicted_census == track_a["predicted_regime_census"]
        and truth_census == track_a["truth_regime_census"]
        and track_a["matchings_refereed"] == a_rows
        and track_a["batches_scanned"] == len(track_a["attempts"])
        and track_a["batches_admitted"] == len(track_a["admitted_batches"])
        and track_a["batches_skipped_term_budget"]
        == sum(1 for a in track_a["attempts"] if a["reason"] == "SKIPPED_TERM_BUDGET")
    )
    trade = predicted_census["split"] + predicted_census["borrow"]
    expected_finding = (
        "REAL_TRADE_REGIME_BATCH_FOUND"
        if trade
        else ("LIBRARY_SCAN_ALL_DONOR_EXACT" if track_a["admitted_batches"]
              else "NO_ADMITTED_REAL_BATCH")
    )
    checks["tracka_finding"] = track_a["finding"] == expected_finding
    counts["track_a_rows"] = {"total": a_rows, "agreeing": a_agree}
    counts["track_a_census"] = {"predicted": predicted_census, "truth": truth_census}
    counts["track_b_census"] = {
        "truth": {
            regime: sum(
                1 for r in table if r["track"] == "B" and r["mine"]["truth_regime"] == regime
            )
            for regime in ("donor_exact", "split", "borrow")
        }
    }
    checks["trackb_census"] = (
        counts["track_b_census"]["truth"] == track_b["truth_regime_census"]
    )

    # ---- headline counts and frozen verdict precedence --------------------
    total_rows = a_rows + len(receipt_b)
    agreeing = a_agree + b_agree
    checks["headline_counts"] = (
        raw.get("rows_staged_total") == total_rows == 102
        and raw.get("match_count") == agreeing == 102
        and raw.get("mismatches_verbatim") == []
    )
    quota_met = bool(track_b["quota_gate_met"])
    if mismatches:
        expected_outcome = "POSITIVE_REGIME_PREDICTIONS_REFUTED"
    elif not quota_met:
        expected_outcome = "TRACKB_QUOTA_UNMET"
    else:
        expected_outcome = "POSITIVE_REGIME_PREDICTIONS_CONFIRMED"
    checks["verdict_precedence"] = raw.get("outcome") == expected_outcome
    checks["gates_all_true"] = all(
        v is True for v in raw.get("gates", {}).values() if isinstance(v, bool)
    )
    checks["dxx_discipline"] = (
        raw.get("dxx_direct_sweep_run") is False
        and raw.get("dxx_obtained_by_exact_containment_pinch_where_applicable") is True
    )

    # ---- disclosure: what this verifier did not rebuild -------------------
    taken_as_given.extend(
        [
            "frozen_source_indices per admitted batch (the R6B window-champion "
            "six-term selection is not re-derived; the recorded indices are only "
            "checked for six-uniqueness, pairwise commutation and a 3+3 split "
            "across the two recorded 12-term windows)",
            "the published DUCC block index semantics (the file format itself); "
            "everything downstream of the parsed integrals is rebuilt here",
            "temporal ordering of stage 1 before stage 2 (only content binding is "
            "checkable offline: the stage-1 digest is shown to cover exactly the "
            "prediction fields and no referee output)",
            "the receipt's own gate booleans and claim-boundary prose",
        ]
    )

    # ---- row table to stderr, digest into the token -----------------------
    note("")
    note(f"{'track':<6}{'n':<4}{'row':<46}"
         f"{'C_R6L':>7}{'C_D+':>7}{'f_B':>11}{'C_DP':>7}  {'regime':<12}{'':<3}status")
    for row in table:
        mine, theirs = row["mine"], row["receipt"]
        status = "agree" if not row["differing_fields"] and not row[
            "algebra_violations"] else "DIFFER:" + ",".join(
            row["differing_fields"] + row["algebra_violations"])
        note(
            f"{row['track']:<6}{row['n']:<4}{str(row['row'])[:44]:<46}"
            f"{mine['C_R6L']:>7}{mine['C_Dplus']:>7}{mine['f_B']:>11}"
            f"{mine['C_DP']:>7}  {mine['truth_regime']:<12}"
            f"{'':<3}{status}"
            + ("" if status == "agree" else f"  receipt={canonical(theirs)}")
        )
    row_table_sha = sha256_text(canonical(table))
    note("")

    decision = "ACCEPT" if all(checks.values()) and not mismatches else "REJECT"
    runtime = time.monotonic() - started
    token = {
        "decision": decision,
        "checks": checks,
        "counts": counts,
        "rows": {
            "total": total_rows,
            "agreeing": agreeing,
            "track_a": {"total": a_rows, "agreeing": a_agree},
            "track_b": {"total": len(receipt_b), "agreeing": b_agree},
        },
        "mismatches": mismatches,
        "row_table_sha256": row_table_sha,
        "receipt_outcome": raw.get("outcome"),
        "receipt_stage1_digest": raw.get("stage1_digest"),
        "taken_from_receipt_as_given": taken_as_given,
        "sampling": "none; all domains enumerated completely",
        "runtime_seconds": round(runtime, 3),
    }
    print("ORIONQG_QG3_GENERIC_VERIFY=" + canonical(token))
    return 0 if decision == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
