#!/usr/bin/env python3
"""QG-24 — is the rotation count a regime-geometry object, or structurally fixed?

Frozen by ``development/orion-qg-regime-geometry/QG24_ROTATION_REGIME_PROTOCOL_V1.md``
(commit bece8910, sha256 asserted in-run). Authority ceiling NOT_R6:
``novelty_authority: false``, ``physical_quantum_advantage_claim: false``. The
protected stretched-N2 subject is never opened; an audited guard raises on any
attempt.

QG-21 measured ``ROTATIONS_R6M == 9`` on every member of the frozen family menu
and concluded that TARE regime geometry can only move Clifford structure, i.e.
under 1 % of fault-tolerant cost. This lane asks whether that 9 is a property of
the FAMILY MENU or of the GRAMMAR. It answers by enumerating the complete
grammar configuration space -- not the family-optimal points -- and computing the
rotation count of every configuration under the merge relation frozen in
protocol section 2.

The merge relation is donor mathematics and carries ZERO novelty credit in this
lane; see QG24_DONOR_SEARCH.md, whose verdicts are embedded verbatim below and
validated by ``orion_research_harness.donor_search.validate_donor_search``.
"""
from __future__ import annotations

import builtins
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PROTOCOL = "development/orion-qg-regime-geometry/QG24_ROTATION_REGIME_PROTOCOL_V1.md"
QG21_RESULTS = REPO / "research/extensions/orion-qg/QG21_FT_CHEMISTRY_RESULTS.json"
RESULTS_PATH = HERE / "QG24_ROTATION_REGIME_RESULTS.json"
STAGE1_PATH = HERE / "QG24_STAGE1_PREDICTIONS.json"
DONOR_MD = REPO / "development/orion-qg-regime-geometry/QG24_DONOR_SEARCH.md"

PROTECTED = "N2/cc-pVTZ/6Elec_6Orbs/1.5_Eq-3.1020au/DUCC2/N2.cc-pvtz.ducc.results.txt"
_PROTECTED_HITS = {"count": 0}
_real_open = builtins.open


def _guarded_open(file, *args, **kwargs):  # pragma: no cover - guard
    if PROTECTED in str(file):
        _PROTECTED_HITS["count"] += 1
        raise PermissionError(f"QG-24 refuses to open the protected subject: {file}")
    return _real_open(file, *args, **kwargs)


builtins.open = _guarded_open

# ---------------------------------------------------------------------------
# 0. Binary-symplectic Pauli primitives (self-contained; letters I,X,Y,Z=0,1,2,3)
# ---------------------------------------------------------------------------
CODE_BITS = ((0, 0), (1, 0), (1, 1), (0, 1))


def local_symp(a: int, b: int) -> int:
    xa, za = CODE_BITS[a]
    xb, zb = CODE_BITS[b]
    return (xa & zb) ^ (za & xb)


def local_mul(a: int, b: int) -> int:
    xa, za = CODE_BITS[a]
    xb, zb = CODE_BITS[b]
    return CODE_BITS.index((xa ^ xb, za ^ zb))


def local_wt(a: int) -> int:
    return 0 if a == 0 else 1


SY = np.array([[local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int8)
LM = np.array([[local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int8)
LW = np.array([local_wt(a) for a in range(4)], dtype=np.int8)


def pmul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def pwt(a) -> int:
    return bin(a[0] | a[1]).count("1")


def psymp(a, b) -> int:
    return (bin(a[0] & b[1]).count("1") + bin(a[1] & b[0]).count("1")) & 1


def pcodes(a, n: int):
    return tuple(CODE_BITS.index((((a[0] >> q) & 1), ((a[1] >> q) & 1))) for q in range(n))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(_real_open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------------------
# 1. The frozen rotation model and the frozen merge relation (protocol s.2)
# ---------------------------------------------------------------------------
# MAX_R4D / QG-21 s.2.1: the TARE-M2 Uanti circuit is the three-exponential
# sandwich  exp(i.t0/2 R_nc) . exp(i.t1 R_c) . exp(i.t0/2 R_nc)  -- outer
# (non-central) axis applied twice, central axis once. Three blocks A,B,C run in
# sequence under one shared Tag, so a compilation is a length-9 sequence of
# arbitrary-angle Pauli rotations. Slots index the six frame axes.
SLOT_NAMES = ("aA", "bA", "aB", "bB", "aC", "bC")
POSITION_SLOT = (0, 1, 0, 2, 3, 2, 4, 5, 4)  # nine rotations -> slot index
# The branch-controlled Restore of block A sits after position 2 (0-indexed) and
# of block B after position 5. Block C's Restore is after the last rotation and
# can never intervene.
INTERVENER_AFTER = {2: "IA", 5: "IB"}

MODELS = ("R6L_RESTORE_IN_PLACE", "R6M_RESTORE_FACTORED")
MODEL_NOTE = {
    "R6L_RESTORE_IN_PLACE": (
        "each block's branch-controlled Restore is charged where the donor R6L "
        "composition writes it -- immediately after that block's Uanti -- so it "
        "is a Clifford intervener between the blocks it separates"),
    "R6M_RESTORE_FACTORED": (
        "R6M's committed cost model extracts an all-three common Restore factor "
        "(factor_restore_triple), which requires the three Restores to be "
        "composed together; read literally that places every Restore after the "
        "last Uanti, so no Clifford intervenes between blocks"),
}


def rotation_count_general(eq, sp, comm_IA, comm_IB, in_place: bool):
    """Exact minimum rotation count by direct search over the merge relation.

    ``eq[i][j]`` / ``sp[i][j]`` are equality / symplectic product of frame slots
    i and j; ``comm_IA[i]`` is 1 when BOTH branch letters of block A's Restore
    commute with slot i. No closed form is assumed: every one of the 36 position
    pairs is tested, and the optimum over merge schedules is searched exactly.
    """
    pairs = []
    for i in range(9):
        for j in range(i + 1, 9):
            si, sj = POSITION_SLOT[i], POSITION_SLOT[j]
            if not eq[si][sj]:
                continue
            if any(sp[POSITION_SLOT[k]][si] for k in range(i + 1, j)):
                continue
            if in_place:
                blocked = False
                for p, tag in INTERVENER_AFTER.items():
                    if i <= p < j:
                        vec = comm_IA if tag == "IA" else comm_IB
                        if not vec[si]:
                            blocked = True
                            break
                if blocked:
                    continue
            pairs.append((i, j))
    best = 0

    def rec(used: int, idx: int, cnt: int) -> None:
        nonlocal best
        if cnt > best:
            best = cnt
        for t in range(idx, len(pairs)):
            i, j = pairs[t]
            if (used >> i) & 1 or (used >> j) & 1:
                continue
            rec(used | (1 << i) | (1 << j), t + 1, cnt + 1)

    rec(0, 0, 0)
    return 9 - best, tuple(pairs)


def rotation_count_closed_form(bits: dict, in_place: bool) -> int:
    """Closed form used for the exact lifting to n qubits (Lemma L1).

    Lemma L1. In the frozen grammar the ONLY position pairs that the merge
    relation can ever admit are (3,4), (6,7) and (3,7) (1-indexed).
    Proof. Within a block the axis sequence is (nc, c, nc) and the grammar forces
    symp(nc, c) = 1, so positions 1-2 and 2-3 carry different axes and positions
    1-3 are separated by a rotation about an anticommuting axis: no intra-block
    merge. Any pair whose first element is position 1 or 2 of its block is
    separated by a rotation about that block's other axis, which anticommutes
    with it, and any pair whose second element is position 2 or 3 of its block is
    preceded inside that block by a rotation about the other axis; both are
    blocked by the same anticommutation. Only the last rotation of one block and
    the first rotation of a later block survive, i.e. (3,4), (6,7), (3,7). QED
    The lemma is additionally checked exhaustively against
    ``rotation_count_general`` over the complete n=1 domain and over every
    equality/symplectic pattern realizable at n=2.
    """
    p1 = bool(bits["e_ab"])
    p2 = bool(bits["e_bc"])
    p3 = bool(bits["e_ac"]) and bits["s_aB_aA"] == 0 and bits["s_bB_aA"] == 0
    if in_place:
        p1 = p1 and bool(bits["ia_aA"])
        p2 = p2 and bool(bits["ib_aB"])
        p3 = p3 and bool(bits["ia_aA"]) and bool(bits["ib_aA"])
    if p1 and p2:
        return 7
    if p1 or p2 or p3:
        return 8
    return 9


# ---------------------------------------------------------------------------
# 2. Local-letter algebra for the complete enumeration
# ---------------------------------------------------------------------------
# A configuration of the frozen grammar is
#   x = (centrals cA,cB,cC ; frames RA0,RA1,RB0,RB1,RC0,RC1 ; Tag S ;
#        targets PA0,PA1,PB0,PB1,PC0,PC1)
# admissible when  symp(Rj0,Rj1)=1 for every block, the Tag labels
# (symp(S,Rj0), symp(S,Rj1)) agree across all three blocks, and the two branch
# labels differ -- exactly R6M's nine-bit accepting condition.
# Restore letters T_{j,k} = P_{j,k}.R_{j,k} are in bijection with the targets at
# fixed frames, so the enumeration is carried out over T. T_{C,0}, T_{C,1} never
# intervene between two rotations, so they are carried as a free factor 16**n.
N_LETTERS = 11  # rA0 rA1 rB0 rB1 rC0 rC1 s tA0 tA1 tB0 tB1
LOCAL_SPACE = 4 ** N_LETTERS
XBITS = 17


def _digits(space: int, k: int) -> list[np.ndarray]:
    idx = np.arange(space, dtype=np.int64)
    return [((idx >> (2 * (k - 1 - t))) & 3).astype(np.int8) for t in range(k)]


_LOCAL_DIGITS = _digits(LOCAL_SPACE, N_LETTERS)


def local_bits(centrals):
    """(17-bit XOR code, 3 local-equality bits) for every local letter tuple."""
    cA, cB, cC = centrals
    rA0, rA1, rB0, rB1, rC0, rC1, s, tA0, tA1, tB0, tB1 = _LOCAL_DIGITS
    aA, bA = (rA0, rA1) if cA == 1 else (rA1, rA0)
    aB, bB = (rB0, rB1) if cB == 1 else (rB1, rB0)
    aC, bC = (rC0, rC1) if cC == 1 else (rC1, rC0)
    sA0, sB0, sC0 = SY[s, rA0], SY[s, rB0], SY[s, rC0]
    sA1, sB1, sC1 = SY[s, rA1], SY[s, rB1], SY[s, rC1]
    bits = [
        SY[rA0, rA1], SY[rB0, rB1], SY[rC0, rC1],
        sA0 ^ sB0, sA0 ^ sC0, sA1 ^ sB1, sA1 ^ sC1, sA0, sA1,
        SY[aB, aA], SY[bB, aA],
        SY[tA0, aA], SY[tA1, aA], SY[tB0, aB], SY[tB1, aB],
        SY[tB0, aA], SY[tB1, aA],
    ]
    code = np.zeros(LOCAL_SPACE, dtype=np.int32)
    for i, b in enumerate(bits):
        code |= b.astype(np.int32) << i
    eq = np.stack([(aA == aB), (aB == aC), (aA == aC)]).astype(np.int8)
    return code, eq, (aA, bA, aB, bB, aC, bC)


def class_of(code: int, eq_pattern: tuple, in_place: bool) -> int:
    """Rotation count of a global configuration, or 0 when inadmissible."""
    g = [(code >> i) & 1 for i in range(XBITS)]
    if not (g[0] == 1 and g[1] == 1 and g[2] == 1):
        return 0
    if g[3] or g[4] or g[5] or g[6]:
        return 0
    if g[7] == g[8]:
        return 0
    bits = {
        "e_ab": eq_pattern[0], "e_bc": eq_pattern[1], "e_ac": eq_pattern[2],
        "s_aB_aA": g[9], "s_bB_aA": g[10],
        "ia_aA": (g[11] == 0 and g[12] == 0),
        "ib_aB": (g[13] == 0 and g[14] == 0),
        "ib_aA": (g[15] == 0 and g[16] == 0),
    }
    return rotation_count_closed_form(bits, in_place)


# ---------------------------------------------------------------------------
# 3. Lemma L1, checked against the general merge search
# ---------------------------------------------------------------------------

def _pattern_key(slots6, tA0, tA1, tB0, tB1, symp_fn, eq_fn):
    eq = [[1 if eq_fn(slots6[i], slots6[j]) else 0 for j in range(6)] for i in range(6)]
    sp = [[symp_fn(slots6[i], slots6[j]) for j in range(6)] for i in range(6)]
    cIA = [1 if (symp_fn(tA0, slots6[k]) == 0 and symp_fn(tA1, slots6[k]) == 0) else 0
           for k in range(6)]
    cIB = [1 if (symp_fn(tB0, slots6[k]) == 0 and symp_fn(tB1, slots6[k]) == 0) else 0
           for k in range(6)]
    return eq, sp, cIA, cIB


def lemma_l1_check_n1():
    """Complete n=1 check: general search vs closed form, and the pair support."""
    seen_pairs, mismatches, checked = set(), [], 0
    dist = {m: {7: 0, 8: 0, 9: 0} for m in MODELS}
    for centrals in itertools.product((0, 1), repeat=3):
        cA, cB, cC = centrals
        for r in itertools.product(range(4), repeat=6):
            rA0, rA1, rB0, rB1, rC0, rC1 = r
            if local_symp(rA0, rA1) != 1 or local_symp(rB0, rB1) != 1:
                continue
            if local_symp(rC0, rC1) != 1:
                continue
            aA, bA = (rA0, rA1) if cA == 1 else (rA1, rA0)
            aB, bB = (rB0, rB1) if cB == 1 else (rB1, rB0)
            aC, bC = (rC0, rC1) if cC == 1 else (rC1, rC0)
            slots = (aA, bA, aB, bB, aC, bC)
            for s in range(4):
                l0 = local_symp(s, rA0)
                if local_symp(s, rB0) != l0 or local_symp(s, rC0) != l0:
                    continue
                l1 = local_symp(s, rA1)
                if local_symp(s, rB1) != l1 or local_symp(s, rC1) != l1:
                    continue
                if l0 == l1:
                    continue
                for tA0, tA1, tB0, tB1 in itertools.product(range(4), repeat=4):
                    eq, sp, cIA, cIB = _pattern_key(
                        slots, tA0, tA1, tB0, tB1, local_symp, lambda u, v: u == v)
                    bits = {
                        "e_ab": eq[0][2], "e_bc": eq[2][4], "e_ac": eq[0][4],
                        "s_aB_aA": sp[2][0], "s_bB_aA": sp[3][0],
                        "ia_aA": cIA[0], "ib_aB": cIB[2], "ib_aA": cIB[0],
                    }
                    for in_place in (True, False):
                        rc, prs = rotation_count_general(eq, sp, cIA, cIB, in_place)
                        seen_pairs.update(prs)
                        cf = rotation_count_closed_form(bits, in_place)
                        model = MODELS[0] if in_place else MODELS[1]
                        dist[model][rc] += 1
                        checked += 1
                        if rc != cf and len(mismatches) < 5:
                            mismatches.append([centrals, r, s, tA0, tA1, tB0, tB1,
                                               in_place, rc, cf])
    return {
        "configurations_checked": checked,
        "ever_feasible_pairs_1indexed": sorted([i + 1, j + 1] for i, j in seen_pairs),
        "closed_form_agrees_everywhere": not mismatches,
        "mismatches": mismatches,
        "brute_force_distribution_n1_reduced": {
            m: {str(k): v for k, v in dist[m].items()} for m in MODELS},
    }


def lemma_l1_check_n2_patterns():
    """Complete n=2 check of Lemma L1 at the pattern level.

    Enumerates EVERY equality/symplectic pattern of the six frame slots that is
    realizable by two-qubit Paulis under the grammar constraint symp(a_j,b_j)=1,
    then, for every pattern that admits any cross-slot equality (patterns without
    one can admit no merge at all under either function), every one of the 2**12
    Restore-commutation vectors. Not a sample.
    """
    paulis = [(x, z) for x in range(4) for z in range(4)]
    blocks = [(u, v) for u in paulis for v in paulis if psymp(u, v) == 1]
    pat = {}
    for (aA, bA) in blocks:
        for (aB, bB) in blocks:
            for (aC, bC) in blocks:
                slots = (aA, bA, aB, bB, aC, bC)
                eqk = spk = 0
                b = 0
                for i in range(6):
                    for j in range(6):
                        if slots[i] == slots[j]:
                            eqk |= 1 << b
                        spk |= psymp(slots[i], slots[j]) << b
                        b += 1
                pat[(eqk, spk)] = slots
    mismatches, checked, cross = [], 0, 0
    for eqk, spk in sorted(pat):
        eq = [[(eqk >> (6 * i + j)) & 1 for j in range(6)] for i in range(6)]
        sp = [[(spk >> (6 * i + j)) & 1 for j in range(6)] for i in range(6)]
        has_cross = any(eq[i][j] for i in range(6) for j in range(6) if i != j)
        masks = range(1 << 12) if has_cross else (0, (1 << 12) - 1)
        if has_cross:
            cross += 1
        for cmask in masks:
            cIA = [(cmask >> k) & 1 for k in range(6)]
            cIB = [(cmask >> (6 + k)) & 1 for k in range(6)]
            bits = {
                "e_ab": eq[0][2], "e_bc": eq[2][4], "e_ac": eq[0][4],
                "s_aB_aA": sp[2][0], "s_bB_aA": sp[3][0],
                "ia_aA": cIA[0], "ib_aB": cIB[2], "ib_aA": cIB[0],
            }
            for in_place in (True, False):
                rc, _ = rotation_count_general(eq, sp, cIA, cIB, in_place)
                cf = rotation_count_closed_form(bits, in_place)
                checked += 1
                if rc != cf and len(mismatches) < 5:
                    mismatches.append([eqk, spk, cmask, in_place, rc, cf])
    return {
        "n2_slot_patterns_realizable": len(pat),
        "n2_patterns_with_cross_slot_equality": cross,
        "checks": checked,
        "closed_form_agrees_everywhere": not mismatches,
        "mismatches": mismatches,
    }


# ---------------------------------------------------------------------------
# 4. Q1 — exact complete enumeration at n qubits
# ---------------------------------------------------------------------------
# Global equality of two frame axes holds iff it holds on every qubit (an AND),
# every other predicate is a symplectic product (an XOR over qubits). So the
# exact count of admissible configurations carrying each rotation count is
#   count(rot) = sum_S sum_{Q subset S} (-1)^{|S|-|Q|} <f_S, I_{Q,rot}>
# with f_S the n-fold XOR-convolution of the local 17-bit histogram restricted to
# local tuples satisfying the equalities in S, evaluated through the
# Walsh-Hadamard transform. Exact integers are recovered by CRT over 31-bit
# primes; nothing is sampled and nothing is approximated.
SUBSETS = [tuple(sorted(c)) for k in range(4)
           for c in itertools.combinations((0, 1, 2), k)]
PRIMES = (2147483647, 2147483629, 2147483587, 2147483579, 2147483563,
          2147483549, 2147483543, 2147483497, 2147483489, 2147483477,
          2147483423, 2147483399, 2147483353, 2147483323, 2147483269,
          2147483249, 2147483237, 2147483179, 2147483171, 2147483137)


def wht(vec: np.ndarray) -> np.ndarray:
    out = vec.astype(np.int64).copy()
    h = 1
    m = out.shape[0]
    while h < m:
        out = out.reshape(-1, 2, h)
        a = out[:, 0, :].copy()
        b = out[:, 1, :].copy()
        out[:, 0, :] = a + b
        out[:, 1, :] = a - b
        out = out.reshape(m)
        h *= 2
    return out


def _modpow_vec(vec: np.ndarray, n: int, p: int) -> np.ndarray:
    base = np.mod(vec, p).astype(np.int64)
    acc = np.ones_like(base)
    e = n
    while e:
        if e & 1:
            acc = (acc * base) % p
        base = (base * base) % p
        e >>= 1
    return acc


def _crt(residues, primes):
    total, mod = 0, 1
    for r, p in zip(residues, primes):
        g = (r - total) % p
        total += mod * (g * pow(mod, -1, p) % p)
        mod *= p
    return total % mod, mod


def class_vectors():
    """Indicator of each (equality pattern Q, model, rotation count) over codes."""
    codes = np.arange(1 << XBITS, dtype=np.int64)
    g = [((codes >> i) & 1) for i in range(XBITS)]
    admissible = ((g[0] == 1) & (g[1] == 1) & (g[2] == 1) & (g[3] == 0) &
                  (g[4] == 0) & (g[5] == 0) & (g[6] == 0) & (g[7] != g[8]))
    ia = (g[11] == 0) & (g[12] == 0)
    ib_aB = (g[13] == 0) & (g[14] == 0)
    ib_aA = (g[15] == 0) & (g[16] == 0)
    p3_axis = (g[9] == 0) & (g[10] == 0)
    out = {}
    for Q in SUBSETS:
        e_ab, e_bc, e_ac = (0 in Q), (1 in Q), (2 in Q)
        for model in MODELS:
            in_place = model == "R6L_RESTORE_IN_PLACE"
            p1 = np.full(codes.shape, e_ab)
            p2 = np.full(codes.shape, e_bc)
            p3 = np.full(codes.shape, e_ac) & p3_axis
            if in_place:
                p1 = p1 & ia
                p2 = p2 & ib_aB
                p3 = p3 & ia & ib_aA
            rot = np.where(p1 & p2, 7, np.where(p1 | p2 | p3, 8, 9))
            for r in (7, 8, 9):
                out[(Q, model, r)] = ((rot == r) & admissible).astype(np.int64)
    return out


def q1_exact_counts(n_values, checks: dict):
    """Exact rotation-count distribution over the complete configuration space."""
    ind_hat = {k: wht(v) for k, v in class_vectors().items()}
    weight = {}
    for S in SUBSETS:
        for model in MODELS:
            for r in (7, 8, 9):
                acc = np.zeros(1 << XBITS, dtype=np.int64)
                for Q in SUBSETS:
                    if not set(Q).issubset(S):
                        continue
                    sign = -1 if (len(S) - len(Q)) % 2 else 1
                    acc = acc + sign * ind_hat[(Q, model, r)]
                weight[(S, model, r)] = acc

    hhat = {}
    for centrals in itertools.product((0, 1), repeat=3):
        code, eq, _ = local_bits(centrals)
        for S in SUBSETS:
            keep = np.ones(LOCAL_SPACE, dtype=bool)
            for i in S:
                keep &= eq[i].astype(bool)
            hist = np.bincount(code[keep].astype(np.int64), minlength=1 << XBITS)
            hhat[(centrals, S)] = wht(hist)

    keys = [(m, r) for m in MODELS for r in (7, 8, 9)]
    results, mod = {}, 1
    for n in n_values:
        residues = {k: [] for k in keys}
        for p in PRIMES:
            wmod = {(S, m, r): np.mod(weight[(S, m, r)], p)
                    for S in SUBSETS for m, r in keys}
            tot = {k: 0 for k in keys}
            for centrals in itertools.product((0, 1), repeat=3):
                for S in SUBSETS:
                    hn = _modpow_vec(hhat[(centrals, S)], n, p)
                    for m, r in keys:
                        prod = (hn * wmod[(S, m, r)]) % p
                        tot[(m, r)] = (tot[(m, r)] + int(prod.sum() % p)) % p
            inv2m = pow(1 << XBITS, -1, p)
            for k in keys:
                residues[k].append(tot[k] * inv2m % p)
        per_model = {m: {} for m in MODELS}
        for (m, r) in keys:
            value, mod = _crt(residues[(m, r)], PRIMES)
            per_model[m][r] = value
        results[n] = per_model
    checks["crt_modulus_bits"] = mod.bit_length()
    return results


def admissible_count_dp(n_values):
    """Independent count of admissible (frame, Tag) assignments -- no WHT, no
    Moebius, no modular arithmetic: a direct 9-bit XOR dynamic program."""
    space = 4 ** 7
    d = _digits(space, 7)
    rA0, rA1, rB0, rB1, rC0, rC1, s = d
    sA0, sB0, sC0 = SY[s, rA0], SY[s, rB0], SY[s, rC0]
    sA1, sB1, sC1 = SY[s, rA1], SY[s, rB1], SY[s, rC1]
    delta = (SY[rA0, rA1].astype(np.int64)
             | (SY[rB0, rB1].astype(np.int64) << 1)
             | (SY[rC0, rC1].astype(np.int64) << 2)
             | ((sA0 ^ sB0).astype(np.int64) << 3)
             | ((sA0 ^ sC0).astype(np.int64) << 4)
             | ((sA1 ^ sB1).astype(np.int64) << 5)
             | ((sA1 ^ sC1).astype(np.int64) << 6)
             | (sA0.astype(np.int64) << 7)
             | (sA1.astype(np.int64) << 8))
    local9 = [int(v) for v in np.bincount(delta, minlength=512)]
    nz = [(d_, c) for d_, c in enumerate(local9) if c]
    dp = [0] * 512
    dp[0] = 1
    out = {}
    for q in range(1, max(n_values) + 1):
        nxt = [0] * 512
        for t, cur in enumerate(dp):
            if not cur:
                continue
            for d_, c in nz:
                nxt[t ^ d_] += cur * c
        dp = nxt
        if q in n_values:
            out[q] = dp[0b010000111] + dp[0b100000111]
    return out
