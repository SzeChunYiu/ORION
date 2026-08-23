#!/usr/bin/env python3
"""MAX-R6P weight-2 frame donor closure test.

Frozen by MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_PROTOCOL.md (frozen before
outcome).

R6O refuted the enlarged weight-one donor family D+ on 486/9261 structured-n2
and 73/240 seeded random instances: the unrestricted R6M DP spends a weight-2
frame Pauli at the central multiplier to compress the shared Tag and improve
Restore-factor alignment. R6P tests the repair hypothesis:

    D++ = { three TARE-M2 frames whose six frame Paulis each have global
            support <= 2 (arbitrary support sets), one shared Tag of
            unrestricted support minimized subject to the common label
            constraints, per-block central choice, donor-owned all-three
            Restore factoring }

restores exact family closure: C_DP == C_D++ on every instance. Support
dominance (R6N, 0 violations over 688,041,472 local configurations) bounds
each frame-support unit's savings by its cost, so support beyond weight 2
should never strictly pay once weight-2 letters (the observed trade currency)
are admitted -- motivation only; the gate is empirical equality. Any instance
with C_DP < C_D++ is a THIRD regime and is reported verbatim.

The unrestricted optimum comes from the frozen R6M module unmodified (the DP
is the referee); the D+ reference from the frozen, machine-verified R6O
enumerator; the D++ enumerator below is written independently of the DP code
paths. Not R6; no novelty credit (weight-2 admission is bookkeeping over the
already-characterized trade); the protected stretched-N2 discriminator is
never read.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6b_tare_transformation_reuse_donor as reuse  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
INF = r6m.INF  # 10**12
MATCHING = r6m._SYNTHETIC_MATCHING  # ((0, 1), (2, 3), (4, 5))
LABEL_ORIENTATIONS = ((0, 1), (1, 0))
CENTRALS8 = tuple(itertools.product((0, 1), repeat=3))
RANDOM_SEED = 20260821
STRUCTURED_VERBATIM_CAP = 20
WITNESS_STORE_CAP = 12
EXPECTED_PAIR_COUNTS = {1: 6, 2: 120, 3: 666}

# ---- independent local algebra (bound to the frozen tables below) -----------
LW = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
F3 = np.zeros((4, 4, 4), dtype=np.int32)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            if _a == _b == _c != 0:
                F3[_a, _b, _c] = 1
            else:
                F3[_a, _b, _c] = int(LW[_a] + LW[_b] + LW[_c])
# letter code from (x bit, z bit): matches the frozen h.BITS_CODE map.
LCODE = np.zeros((2, 2), dtype=np.int64)
for _bx in (0, 1):
    for _bz in (0, 1):
        LCODE[_bx, _bz] = h.BITS_CODE[(_bx, _bz)]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---- independent D++ enumerator ---------------------------------------------


class _DxxTables:
    """Per-(n, max_weight) frame-pair / Tag / pattern tables (target-free)."""

    def __init__(self, n: int, max_weight: int):
        self.n = n
        self.max_weight = max_weight
        self.npos_bits = 2 * n
        self.M = 4 ** (2 * n)
        keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)]
        pop = np.zeros(2 ** n, dtype=np.int64)
        for v in range(2 ** n):
            pop[v] = bin(v).count("1")
        self.pop = pop
        # ordered anticommuting frame-Pauli pairs, each nonzero with wt<=max.
        small = [k for k in keys if k != (0, 0) and p10.wt(k) <= max_weight]
        pairs = [
            (a, b) for a in small for b in small if p10.symp(a, b) == 1
        ]
        self.P = len(pairs)
        if max_weight == 2 and self.P != EXPECTED_PAIR_COUNTS[n]:
            raise AssertionError(
                {"r6p_pair_count_mismatch": [n, self.P, EXPECTED_PAIR_COUNTS[n]]}
            )
        self.R0X = np.array([a[0] for a, _ in pairs], dtype=np.int64)
        self.R0Z = np.array([a[1] for a, _ in pairs], dtype=np.int64)
        self.R1X = np.array([b[0] for _, b in pairs], dtype=np.int64)
        self.R1Z = np.array([b[1] for _, b in pairs], dtype=np.int64)
        w0 = pop[self.R0X | self.R0Z]
        w1 = pop[self.R1X | self.R1Z]
        # frozen central tie-break: central (multiplier 2) on the heavier
        # frame Pauli; central=0 on equal weights.
        self.central = (w0 < w1).astype(np.int64)
        self.uanti = 4 * (np.minimum(w0, w1) - 1) + 2 * (np.maximum(w0, w1) - 1)
        self.pairs = pairs
        # Tag sweep order: all nonzero Paulis ascending by (weight, x, z).
        s_list = sorted(
            (k for k in keys if k != (0, 0)), key=lambda k: (p10.wt(k), k[0], k[1])
        )
        self.s_keys = s_list
        self.s_wt = np.array([p10.wt(k) for k in s_list], dtype=np.int64)
        # symplectic products <S, R_pair_k> for every Tag and pair.
        sx = np.array([k[0] for k in s_list], dtype=np.int64)[:, None]
        sz = np.array([k[1] for k in s_list], dtype=np.int64)[:, None]
        self.sy0 = (
            pop[sx & self.R0Z[None, :]] + pop[sz & self.R0X[None, :]]
        ) & 1
        self.sy1 = (
            pop[sx & self.R1Z[None, :]] + pop[sz & self.R1X[None, :]]
        ) & 1
        # pattern non-don't-care digit counts.
        digs = (
            np.arange(self.M, dtype=np.int64)[:, None]
            >> (2 * np.arange(2 * n, dtype=np.int64))[None, :]
        ) & 3
        self.npos = (digs != 0).sum(axis=1).astype(np.int64)


_dxx_tables: dict[tuple[int, int], _DxxTables] = {}


def _tables(n: int, max_weight: int) -> _DxxTables:
    key = (n, max_weight)
    if key not in _dxx_tables:
        _dxx_tables[key] = _DxxTables(n, max_weight)
    return _dxx_tables[key]


def _block_arrays(tb: _DxxTables, target_pair):
    """Choice arrays (perm-0 then perm-1) for one block: base cost + T code."""
    n = tb.n
    bases = []
    codes = []
    for perm in (0, 1):
        t0, t1 = target_pair if perm == 0 else (target_pair[1], target_pair[0])
        t0x = t0[0] ^ tb.R0X
        t0z = t0[1] ^ tb.R0Z
        t1x = t1[0] ^ tb.R1X
        t1z = t1[1] ^ tb.R1Z
        base = tb.uanti + tb.pop[t0x | t0z] + tb.pop[t1x | t1z]
        code = np.zeros(tb.P, dtype=np.int64)
        for q in range(n):
            code |= LCODE[(t0x >> q) & 1, (t0z >> q) & 1] << (2 * q)
            code |= LCODE[(t1x >> q) & 1, (t1z >> q) & 1] << (2 * (n + q))
        bases.append(base)
        codes.append(code)
    return np.concatenate(bases), np.concatenate(codes)


def _zeta_min(f: np.ndarray, positions: int) -> np.ndarray:
    """Exact don't-care min-transform: digit 0 of each position = min over 4."""
    g = f.copy()
    for pos in range(positions):
        view = g.reshape(-1, 4, 4 ** pos)
        np.minimum(
            np.minimum(view[:, 0], view[:, 1]),
            np.minimum(view[:, 2], view[:, 3]),
            out=view[:, 0],
        )
    return g


def dxx_search(target_pairs, n: int, max_weight: int = 2,
               want_witness: bool = False) -> dict[str, Any]:
    """Exact D++ optimum (or its weight-restricted sub-family) for one instance."""
    tb = _tables(n, max_weight)
    target_pairs = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    blocks = [_block_arrays(tb, tp) for tp in target_pairs]
    minb_sum = int(sum(int(base.min()) for base, _ in blocks))
    positions = 2 * n
    best_val = INF
    best_loc = None
    for l_idx, (l0, l1) in enumerate(LABEL_ORIENTATIONS):
        for s_idx in range(len(tb.s_keys)):
            sw = int(tb.s_wt[s_idx])
            if 2 * sw + minb_sum - 2 * positions >= best_val:
                continue
            mask = (tb.sy0[s_idx] == l0) & (tb.sy1[s_idx] == l1)
            if not mask.any():
                continue
            maskc = np.concatenate([mask, mask])
            gs = []
            feasible = True
            for base, code in blocks:
                sel = maskc
                f = np.full(tb.M, INF, dtype=np.int64)
                np.minimum.at(f, code[sel], base[sel])
                if int(f.min()) >= INF:
                    feasible = False
                    break
                gs.append(_zeta_min(f, positions))
            if not feasible:
                continue
            tot = gs[0] + gs[1] + gs[2] - 2 * tb.npos + 2 * sw
            pat = int(np.argmin(tot))
            val = int(tot[pat])
            if val < best_val:
                best_val = val
                best_loc = (l_idx, s_idx, pat)
    if best_loc is None or best_val >= INF // 2:
        raise AssertionError("r6p D++ family produced no feasible point")
    out = {"C_Dxx": int(best_val)}
    if want_witness:
        out["witness"] = _dxx_backtrack(tb, blocks, target_pairs, best_val, best_loc)
    return out


def _dxx_backtrack(tb: _DxxTables, blocks, target_pairs, best_val, best_loc):
    l_idx, s_idx, pat = best_loc
    l0, l1 = LABEL_ORIENTATIONS[l_idx]
    n = tb.n
    positions = 2 * n
    s_key = tb.s_keys[s_idx]
    mask = (tb.sy0[s_idx] == l0) & (tb.sy1[s_idx] == l1)
    maskc = np.concatenate([mask, mask])
    chosen = []
    for base, code in blocks:
        f = np.full(tb.M, INF, dtype=np.int64)
        np.minimum.at(f, code[maskc], base[maskc])
        g = _zeta_min(f, positions)
        target_base = int(g[pat])
        compat = maskc.copy()
        for pos in range(positions):
            digit = (pat >> (2 * pos)) & 3
            if digit:
                compat &= ((code >> (2 * pos)) & 3) == digit
        cand = np.nonzero(compat & (base == target_base))[0]
        if cand.size == 0:
            raise AssertionError("r6p backtrack found no compatible choice")
        chosen.append(int(cand[0]))
    # direct cost recomputation from the chosen triple.
    codes3 = [int(blocks[j][1][chosen[j]]) for j in range(3)]
    bases3 = [int(blocks[j][0][chosen[j]]) for j in range(3)]
    match = 0
    for pos in range(positions):
        letters = [(codes3[j] >> (2 * pos)) & 3 for j in range(3)]
        if letters[0] == letters[1] == letters[2] != 0:
            match += 1
    actual = sum(bases3) - 2 * match + 2 * p10.wt(s_key)
    if actual != best_val:
        raise AssertionError(
            {"r6p_backtrack_cost_mismatch": [actual, best_val]}
        )
    wit_blocks = []
    for j, c in enumerate(chosen):
        perm, pidx = divmod(c, tb.P)
        r0 = (int(tb.R0X[pidx]), int(tb.R0Z[pidx]))
        r1 = (int(tb.R1X[pidx]), int(tb.R1Z[pidx]))
        wit_blocks.append(
            {
                "block": "ABC"[j],
                "R0": list(r0),
                "R1": list(r1),
                "support": [int(p10.wt(r0)), int(p10.wt(r1))],
                "central": int(tb.central[pidx]),
                "uanti": int(tb.uanti[pidx]),
                "target_permutation": int(perm),
            }
        )
    return {
        "C_Dxx": int(best_val),
        "labels": [l0, l1],
        "S": list(s_key),
        "tag_weight": int(p10.wt(s_key)),
        "blocks": wit_blocks,
        "max_frame_support": max(
            max(b["support"]) for b in wit_blocks
        ),
    }


def verify_dxx_witness(target_pairs, n: int, wit: dict[str, Any]) -> bool:
    """Independent re-verification through the frozen donor factor machinery."""
    labels = tuple(wit["labels"])
    s_key = tuple(wit["S"])
    frames = []
    ordered_targets = []
    for j, blk in enumerate(wit["blocks"]):
        r0, r1 = tuple(blk["R0"]), tuple(blk["R1"])
        frames.append((r0, r1))
        tp = tuple(tuple(t) for t in target_pairs[j])
        ordered_targets.append(tp if blk["target_permutation"] == 0 else (tp[1], tp[0]))
    checks = {
        "support_le_2_nonzero_anticommuting_frames": all(
            1 <= p10.wt(r0) <= 2 and 1 <= p10.wt(r1) <= 2 and p10.symp(r0, r1) == 1
            for r0, r1 in frames
        ),
        "labels_common_and_distinct": labels[0] != labels[1]
        and all(
            (p10.symp(s_key, r0), p10.symp(s_key, r1)) == labels for r0, r1 in frames
        ),
        "uanti_binds_to_frozen_rule": all(
            int(blk["uanti"]) == r6m._uanti_m2(frames[j], int(blk["central"]))
            for j, blk in enumerate(wit["blocks"])
        ),
    }
    # exhaustive Tag-minimality brute over all 4^n Paulis (n <= 3 here).
    min_wt = None
    s_feasible = False
    for x in range(2 ** n):
        for z in range(2 ** n):
            key = (x, z)
            if all(
                (p10.symp(key, r0), p10.symp(key, r1)) == labels for r0, r1 in frames
            ):
                w = p10.wt(key)
                if min_wt is None or w < min_wt:
                    min_wt = w
                if key == s_key:
                    s_feasible = True
    checks["tag_is_minimum_weight_feasible"] = (
        s_feasible and min_wt is not None and p10.wt(s_key) == min_wt
    )
    signed = []
    for j in range(3):
        row = []
        for k in range(2):
            t = p10.mul(ordered_targets[j][k], frames[j][k])
            phase = reuse.correction_phase(ordered_targets[j][k], frames[j][k], t, n)
            row.append((int(phase), t))
        signed.append(row)
    branch_factors = [
        r6m.factor_restore_triple(signed[0][k], signed[1][k], signed[2][k], n)
        for k in range(2)
    ]
    checks["factor_checks"] = all(all(bf["checks"].values()) for bf in branch_factors)
    checks["cost_recomputed"] = (
        int(
            sum(int(blk["uanti"]) for blk in wit["blocks"])
            + 2 * p10.wt(s_key)
            + sum(bf["support"] for bf in branch_factors)
        )
        == int(wit["C_Dxx"])
    )
    return all(checks.values())


# ---- frozen DP readers (bound to the frozen module by sampling) --------------


def _permute6(t6, perm_b: int, perm_c: int):
    a0, a1, b0, b1, c0, c1 = t6
    if perm_b:
        b0, b1 = b1, b0
    if perm_c:
        c0, c1 = c1, c0
    return (a0, a1, b0, b1, c0, c1)


def _local_code(key, q: int) -> int:
    return h.BITS_CODE[((key[0] >> q) & 1, (key[1] >> q) & 1)]


def dp_cost_n1_reader(p6) -> int:
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            q6 = _permute6(p6, perm_b, perm_c)
            for centrals in CENTRALS8:
                cost, _ = r6m._local_table(q6, centrals)
                for state in r6m.ACCEPTING_STATES:
                    v = int(cost[state])
                    if v < INF and (best is None or v < best):
                        best = v
    if best is None:
        raise AssertionError("r6p n=1 DP reader found no accepting option")
    return best - 18


def dp_cost_n2_reader(target_pairs) -> int:
    flat = tuple(t for pair in target_pairs for t in pair)
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            t6 = _permute6(flat, perm_b, perm_c)
            p60 = tuple(_local_code(t, 0) for t in t6)
            p61 = tuple(_local_code(t, 1) for t in t6)
            for centrals in CENTRALS8:
                c0, _ = r6m._local_table(p60, centrals)
                c1, _ = r6m._local_table(p61, centrals)
                for state in r6m.ACCEPTING_STATES:
                    v = int((c0 + c1[r6m.XOR512[state]]).min())
                    if v < INF and (best is None or v < best):
                        best = v
    if best is None:
        raise AssertionError("r6p n=2 DP reader found no accepting option")
    return best - 18


def dp_cost_frozen_configs(terms, n: int) -> int:
    values = []
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            for centrals in CENTRALS8:
                v = r6m._dp_config_cost(terms, MATCHING, perm_b, perm_c, centrals, n)
                if v is not None:
                    values.append(int(v))
    if not values:
        raise AssertionError("r6p frozen config sweep found no accepting state")
    return min(values)


def _sandwich(where, c_dp, c_dxx, c_dplus, c_r6l=None):
    if not (c_dp <= c_dxx <= c_dplus):
        raise AssertionError(
            {"r6p_sandwich_violated": [where, c_dp, c_dxx, c_dplus]}
        )
    if c_r6l is not None and not (c_dplus <= c_r6l):
        raise AssertionError(
            {"r6p_r6l_sandwich_violated": [where, c_dplus, c_r6l]}
        )


# ---- domain (e): R6N synthetic R6M-grammar panels ---------------------------


def domain_r6n_panels() -> dict[str, Any]:
    rows = []
    weight1_binding_ok = True
    instances = [
        (name, 1, tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in pairs))
        for name, pairs in sorted(r6m._HOSTILE_N1_PANELS.items())
    ]
    instances += [
        (name, 2, tuple((tuple(a), tuple(b)) for a, b in pairs))
        for name, pairs in sorted(r6m._HOSTILE_N2_PANELS.items())
    ]
    for name, n, target_pairs in instances:
        terms = r6m._synthetic_terms(target_pairs)
        dp_wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
        c_dp = int(dp_wit["C_R6M"])
        c_dplus = int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"])
        dxx = dxx_search(target_pairs, n, want_witness=True)
        c_dxx = int(dxx["C_Dxx"])
        c_r6l = int(r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"])
        _sandwich(["panel", name], c_dp, c_dxx, c_dplus, c_r6l)
        if not verify_dxx_witness(target_pairs, n, dxx["witness"]):
            raise AssertionError({"r6p_panel_dxx_witness_failed": name})
        if int(dxx_search(target_pairs, n, max_weight=1)["C_Dxx"]) != c_dplus:
            weight1_binding_ok = False
        rows.append(
            {
                "panel": name,
                "n": n,
                "C_unrestricted_dp": c_dp,
                "C_Dxx": c_dxx,
                "C_Dplus": c_dplus,
                "C_R6L_weight_one_donor": c_r6l,
                "equal": c_dp == c_dxx,
                "was_r6n_refuting_instance": name == "n2_b",
                "dxx_witness": dxx["witness"],
                "dp_witness_checks_pass": all(dp_wit["checks"].values()),
            }
        )
    return {
        "instances": len(rows),
        "equal_count": sum(r["equal"] for r in rows),
        "rows": rows,
        "all_equal": all(r["equal"] for r in rows),
        "weight1_restricted_binding_ok": weight1_binding_ok,
    }


# ---- domain (c): exhaustive n=1 ---------------------------------------------


def domain_exhaustive_n1() -> dict[str, Any]:
    def letter_key(letter, q):
        bx, bz = h.CODE_BITS[letter]
        return (bx << q, bz << q)

    violations = []
    equal = 0
    dplus_gap = 0
    binding_rows = 0
    binding_ok = True
    exact_binding_ok = True
    weight1_binding_rows = 0
    weight1_binding_ok = True
    witness_rows = 0
    for idx in range(4096):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        p6 = tuple((idx >> (2 * (5 - t))) & 3 for t in range(6))
        target_pairs = tuple(
            (letter_key(p6[2 * j], 0), letter_key(p6[2 * j + 1], 0)) for j in range(3)
        )
        c_dp = dp_cost_n1_reader(p6)
        c_dplus = int(r6o.dplus_pairs(target_pairs, 1)["C_Dplus"])
        want = idx % 64 == 0
        dxx = dxx_search(target_pairs, 1, want_witness=want)
        c_dxx = int(dxx["C_Dxx"])
        _sandwich(["n1", idx], c_dp, c_dxx, c_dplus)
        if c_dplus > c_dp:
            dplus_gap += 1
        if idx % 32 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            binding_rows += 1
            if dp_cost_frozen_configs(terms, 1) != c_dp:
                binding_ok = False
        if idx % 512 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            wit = r6m.exact_r6m_matching(terms, MATCHING, 1, list(range(6)))
            if int(wit["C_R6M"]) != c_dp:
                exact_binding_ok = False
        if idx % 128 == 0:
            weight1_binding_rows += 1
            if int(dxx_search(target_pairs, 1, max_weight=1)["C_Dxx"]) != c_dplus:
                weight1_binding_ok = False
        if want:
            witness_rows += 1
            if not verify_dxx_witness(target_pairs, 1, dxx["witness"]):
                raise AssertionError({"r6p_n1_dxx_witness_failed": idx})
        if c_dp == c_dxx:
            equal += 1
        else:
            violations.append(
                {
                    "instance_index": idx,
                    "targets_A0A1B0B1C0C1": "".join(LETTERS[x] for x in p6),
                    "C_unrestricted_dp": c_dp,
                    "C_Dxx": c_dxx,
                    "C_Dplus": c_dplus,
                }
            )
    r6m._local_table.cache_clear()
    return {
        "instances": 4096,
        "equal_count": equal,
        "all_equal": equal == 4096,
        "dplus_gap_count": dplus_gap,
        "binding_sample_rows": binding_rows,
        "binding_exact": binding_ok,
        "exact_matcher_binding_rows": 8,
        "exact_matcher_binding_exact": exact_binding_ok,
        "weight1_restricted_binding_rows": weight1_binding_rows,
        "weight1_restricted_binding_ok": weight1_binding_ok,
        "witness_verified_rows": witness_rows,
        "violating_instances_verbatim": violations,
    }


# ---- domain (b): exhaustive structured n=2 + structured critical set --------


def domain_structured_n2(receipt_n2: dict[str, Any]) -> dict[str, Any]:
    def letter_key(letter, q):
        bx, bz = h.CODE_BITS[letter]
        return (bx << q, bz << q)

    wt1 = [letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    violations = []
    critical_rows = []
    critical_witnesses = []
    equal = 0
    dplus_equal = 0
    binding_rows = 0
    binding_ok = True
    exact_binding_rows = 0
    exact_binding_ok = True
    swap_rows = 0
    swap_ok = True
    weight1_binding_rows = 0
    weight1_binding_ok = True
    witness_rows = 0
    idx = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        target_pairs = tuple(
            (wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic)
        )
        c_dp = dp_cost_n2_reader(target_pairs)
        c_dplus = int(r6o.dplus_pairs(target_pairs, 2)["C_Dplus"])
        is_critical = c_dplus > c_dp
        want = is_critical or idx % 97 == 0
        dxx = dxx_search(target_pairs, 2, want_witness=want)
        c_dxx = int(dxx["C_Dxx"])
        _sandwich(["structured_n2", idx], c_dp, c_dxx, c_dplus)
        if c_dplus == c_dp:
            dplus_equal += 1
        if idx % 97 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            binding_rows += 1
            if dp_cost_frozen_configs(terms, 2) != c_dp:
                binding_ok = False
        if idx % 1153 == 0:
            terms = r6m._synthetic_terms(target_pairs)
            exact_binding_rows += 1
            wit = r6m.exact_r6m_matching(terms, MATCHING, 2, list(range(6)))
            if int(wit["C_R6M"]) != c_dp:
                exact_binding_ok = False
        if idx % 290 == 0:
            swapped = ((target_pairs[0][1], target_pairs[0][0]),) + target_pairs[1:]
            swap_rows += 1
            if dp_cost_n2_reader(swapped) != c_dp:
                swap_ok = False
        if idx % 210 == 0:
            weight1_binding_rows += 1
            if int(dxx_search(target_pairs, 2, max_weight=1)["C_Dxx"]) != c_dplus:
                weight1_binding_ok = False
        if want:
            witness_rows += 1
            if not verify_dxx_witness(target_pairs, 2, dxx["witness"]):
                raise AssertionError({"r6p_n2_dxx_witness_failed": idx})
        if is_critical:
            row = {
                "instance_index": idx,
                "C_unrestricted_dp": c_dp,
                "C_Dplus": c_dplus,
                "C_Dxx": c_dxx,
                "closed_at_weight_two": c_dxx == c_dp,
            }
            if len(critical_rows) < STRUCTURED_VERBATIM_CAP:
                row = {
                    **row,
                    "block_pairs": [list(upairs[s]) for s in (ia, ib, ic)],
                    "targets": [[list(a), list(b)] for a, b in target_pairs],
                }
            critical_rows.append(row)
            if len(critical_witnesses) < WITNESS_STORE_CAP:
                critical_witnesses.append(
                    {
                        "instance_index": idx,
                        "targets": [[list(a), list(b)] for a, b in target_pairs],
                        "C_unrestricted_dp": c_dp,
                        "C_Dplus": c_dplus,
                        "dxx_witness": dxx["witness"],
                    }
                )
        if c_dp == c_dxx:
            equal += 1
        else:
            violations.append(
                {
                    "instance_index": idx,
                    "block_pairs": [list(upairs[s]) for s in (ia, ib, ic)],
                    "targets": [[list(a), list(b)] for a, b in target_pairs],
                    "C_unrestricted_dp": c_dp,
                    "C_Dxx": c_dxx,
                    "C_Dplus": c_dplus,
                }
            )
        idx += 1
    r6m._local_table.cache_clear()
    r6o._block_cache.clear()
    # receipt cross-check for the frozen critical set.
    receipt_equal = int(receipt_n2["equal_count"])
    expected_gap = int(receipt_n2["instances"]) - receipt_equal
    my_gap_by_index = {
        row["instance_index"]: row for row in critical_rows
    }
    verbatim_matched = 0
    verbatim_ok = True
    for rec in receipt_n2["violating_instances_verbatim"]:
        row = my_gap_by_index.get(int(rec["instance_index"]))
        if (
            row is None
            or int(rec["C_unrestricted_dp"]) != row["C_unrestricted_dp"]
            or int(rec["C_Dplus"]) != row["C_Dplus"]
        ):
            verbatim_ok = False
        else:
            verbatim_matched += 1
    crosscheck = {
        "receipt_equal_count": receipt_equal,
        "expected_critical_count": expected_gap,
        "observed_critical_count": len(critical_rows),
        "critical_count_matches_receipt": len(critical_rows) == expected_gap
        and dplus_equal == receipt_equal,
        "receipt_verbatim_rows_matched": verbatim_matched,
        "receipt_verbatim_rows_ok": verbatim_ok
        and verbatim_matched == len(receipt_n2["violating_instances_verbatim"]),
    }
    return {
        "instances": 21 ** 3,
        "equal_count": equal,
        "all_equal": equal == 21 ** 3,
        "dplus_equal_count": dplus_equal,
        "critical_instances": len(critical_rows),
        "critical_closed_at_weight_two": sum(
            r["closed_at_weight_two"] for r in critical_rows
        ),
        "critical_rows": critical_rows,
        "critical_witness_samples": critical_witnesses,
        "receipt_crosscheck": crosscheck,
        "binding_sample_rows": binding_rows,
        "binding_exact": binding_ok,
        "exact_matcher_binding_rows": exact_binding_rows,
        "exact_matcher_binding_exact": exact_binding_ok,
        "block_a_swap_invariance_rows": swap_rows,
        "block_a_swap_invariance_ok": swap_ok,
        "weight1_restricted_binding_rows": weight1_binding_rows,
        "weight1_restricted_binding_ok": weight1_binding_ok,
        "witness_verified_rows": witness_rows,
        "violating_instances_verbatim": violations,
    }


# ---- domain (d): seeded random panel + random critical set ------------------


def domain_random_panel(receipt_random: dict[str, Any]) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    rows = []
    violations = []
    critical_rows = []
    critical_witnesses = []
    weight1_binding_rows = 0
    weight1_binding_ok = True
    witness_rows = 0
    receipt_rows = receipt_random["rows"]
    receipt_row_match = True
    for n in (2, 3):
        for i in range(120):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            target_pairs = tuple(
                (targets[2 * j], targets[2 * j + 1]) for j in range(3)
            )
            terms = r6m._synthetic_terms(target_pairs)
            r6m._local_table.cache_clear()
            c_dp = dp_cost_frozen_configs(terms, n)
            c_dplus = int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"])
            c_r6l = int(
                r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"]
            )
            is_critical = c_dplus > c_dp
            want = is_critical or i % 10 == 0
            dxx = dxx_search(target_pairs, n, want_witness=want)
            c_dxx = int(dxx["C_Dxx"])
            _sandwich(["random", n, i], c_dp, c_dxx, c_dplus, c_r6l)
            rec = receipt_rows[len(rows)]
            if (
                int(rec["n"]) != n
                or int(rec["index"]) != i
                or int(rec["C_unrestricted_dp"]) != c_dp
                or int(rec["C_Dplus"]) != c_dplus
                or int(rec["C_R6L_weight_one_donor"]) != c_r6l
                or bool(rec["equal"]) != (c_dplus == c_dp)
            ):
                receipt_row_match = False
            if i % 15 == 0:
                weight1_binding_rows += 1
                if int(dxx_search(target_pairs, n, max_weight=1)["C_Dxx"]) != c_dplus:
                    weight1_binding_ok = False
            if want:
                witness_rows += 1
                if not verify_dxx_witness(target_pairs, n, dxx["witness"]):
                    raise AssertionError({"r6p_random_dxx_witness_failed": [n, i]})
            row = {
                "n": n,
                "index": i,
                "C_unrestricted_dp": c_dp,
                "C_Dxx": c_dxx,
                "C_Dplus": c_dplus,
                "C_R6L_weight_one_donor": c_r6l,
                "equal": c_dp == c_dxx,
            }
            rows.append(row)
            if is_critical:
                critical_rows.append(
                    {
                        **row,
                        "targets": [list(t) for t in targets],
                        "closed_at_weight_two": c_dxx == c_dp,
                    }
                )
                if len(critical_witnesses) < WITNESS_STORE_CAP:
                    critical_witnesses.append(
                        {
                            "n": n,
                            "index": i,
                            "targets": [list(t) for t in targets],
                            "C_unrestricted_dp": c_dp,
                            "C_Dplus": c_dplus,
                            "dxx_witness": dxx["witness"],
                        }
                    )
            if not row["equal"]:
                violations.append({**row, "targets": [list(t) for t in targets]})
    r6o._block_cache.clear()
    receipt_critical = {
        (int(r["n"]), int(r["index"])) for r in receipt_rows if not r["equal"]
    }
    my_critical = {(r["n"], r["index"]) for r in critical_rows}
    return {
        "instances": len(rows),
        "equal_count": sum(r["equal"] for r in rows),
        "all_equal": all(r["equal"] for r in rows),
        "critical_instances": len(critical_rows),
        "critical_closed_at_weight_two": sum(
            r["closed_at_weight_two"] for r in critical_rows
        ),
        "critical_rows": critical_rows,
        "critical_witness_samples": critical_witnesses,
        "receipt_crosscheck": {
            "all_240_rows_match_receipt": receipt_row_match,
            "receipt_critical_count": len(receipt_critical),
            "observed_critical_count": len(my_critical),
            "critical_sets_identical": receipt_critical == my_critical,
        },
        "dxx_strictly_below_dplus_count": sum(
            r["C_Dxx"] < r["C_Dplus"] for r in rows
        ),
        "weight1_restricted_binding_rows": weight1_binding_rows,
        "weight1_restricted_binding_ok": weight1_binding_ok,
        "witness_verified_rows": witness_rows,
        "rows": rows,
        "violating_instances_verbatim": violations,
    }


# ---- domain (f): frozen chemistry subjects (pinched D++) --------------------


def domain_chemistry(receipt_r6o_chem: dict[str, Any]) -> dict[str, Any]:
    receipt_r6m = json.loads(
        Path(__file__)
        .with_name("MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json")
        .read_text()
    )
    subjects = {}
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        terms, source_indices, _champions, _max_imag, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"r6p_chemistry_blob_mismatch": name})
        n = int(cfg["n_qubits"])
        six = [int(i) for i in source_indices]
        rec_sub = receipt_r6m["subjects"][name]
        if sorted(six) != sorted(int(i) for i in rec_sub["frozen_source_indices"]):
            raise AssertionError({"r6p_chemistry_source_indices_mismatch": name})
        rec_rows = {
            canonical_json(row["matching"]): row for row in rec_sub["candidate_points"]
        }
        r6o_rows = {
            canonical_json(row["matching"]): row
            for row in receipt_r6o_chem["subjects"][name]["rows"]
        }
        matchings = r6m.perfect_matchings(six)
        rows = []
        for pairs in matchings:
            key = canonical_json([list(p) for p in pairs])
            if key not in rec_rows or key not in r6o_rows:
                raise AssertionError({"r6p_chemistry_receipt_matching_missing": [name, key]})
            rec_row = rec_rows[key]
            c_dp = int(rec_row["C_R6M"])
            c_r6l_receipt = int(rec_row["C_R6L_same_matching"])
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            c_dplus = int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"])
            if c_dplus != int(r6o_rows[key]["C_Dplus"]):
                raise AssertionError(
                    {"r6p_chemistry_dplus_receipt_mismatch": [name, key, c_dplus]}
                )
            c_r6l = int(r6m.donor_r6l_matching(terms, pairs, n, six)["C_R6L"])
            if c_r6l != c_r6l_receipt:
                raise AssertionError(
                    {"r6p_chemistry_r6l_receipt_mismatch": [name, key, c_r6l, c_r6l_receipt]}
                )
            if not (c_dp <= c_dplus <= c_r6l):
                raise AssertionError(
                    {"r6p_chemistry_sandwich_violated": [name, key, c_dp, c_dplus, c_r6l]}
                )
            # exact pinch: C_DP <= C_D++ <= C_D+; equality of the endpoints
            # forces C_D++ == C_DP == C_D+ without the (infeasible) direct
            # sweep at n=8/12.
            pinched = c_dplus == c_dp
            rows.append(
                {
                    "matching": [list(p) for p in pairs],
                    "C_R6M_receipt_dp": c_dp,
                    "C_Dplus_recomputed": c_dplus,
                    "C_Dxx_pinched": c_dp if pinched else None,
                    "C_R6L_recomputed": c_r6l,
                    "C_R6L_receipt": c_r6l_receipt,
                    "dxx_pinched_equal": pinched,
                    "quadruple_tie": pinched and c_dplus == c_r6l,
                }
            )
        subjects[name] = {
            "n_qubits": n,
            "source_blob_verified": True,
            "matchings": len(rows),
            "rows": rows,
            "all_pinched_equal": all(r["dxx_pinched_equal"] for r in rows),
            "all_quadruple_tie": all(r["quadruple_tie"] for r in rows),
        }
        r6o._block_cache.clear()
    return {
        "r6m_receipt_authority": receipt_r6m["authority"],
        "dxx_direct_sweep_run": False,
        "dxx_obtained_by_exact_containment_pinch": True,
        "subjects": subjects,
        "matchings_checked": sum(s["matchings"] for s in subjects.values()),
        "all_pinched_equal": all(s["all_pinched_equal"] for s in subjects.values()),
        "all_quadruple_tie": all(s["all_quadruple_tie"] for s in subjects.values()),
    }


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "Frozen R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar with the "
        "donor-owned all-three Restore common-factor rule under the frozen raw "
        "support-count objective; the further-enlarged donor family D++ (frames "
        "of global support <= 2 per frame Pauli with arbitrary support sets, "
        "minimum-weight shared Tag, per-block central choice, donor-owned "
        "factoring) satisfies C_DP <= C_Dxx <= C_Dplus <= C_R6L on every "
        "instance."
    ),
    "machine_evidenced_only": (
        "Equality C_DP == C_Dxx is machine-evidenced on the stated finite "
        "domains only: exhaustively at n=1 (4096 instances) and on the "
        "structured weight-one n=2 slice (9261 instances, including all 486 "
        "R6O critical instances), the 5 R6N R6M-grammar panels, the 240 seeded "
        "random n=2/n=3 instances (including all 73 R6O critical instances), "
        "and all 30 recorded chemistry matchings (via the exact containment "
        "pinch C_DP <= C_Dxx <= C_Dplus with equal endpoints). It is NOT a "
        "theorem for all n; support dominance (R6N) motivates but does not "
        "prove the closure, which is repaired empirically by family "
        "enlargement."
    ),
    "does_not_cover": (
        "Other objectives, rotation-count trade-offs beyond the frozen fixed "
        "counts, larger Tag ranks, grammars outside the frozen family, "
        "support-3+ frame families, or any fresh subject data. No novelty "
        "credit, no donor credit, no R6 authority: D++ is donor-owned "
        "machinery and the support-2 admission is bookkeeping over the trade "
        "the R6O refutation already characterized."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    f3_binding = bool(np.array_equal(F3.astype(np.int64), r6m._F3))
    if not f3_binding:
        raise AssertionError("r6p independent F3 table does not bind to frozen r6m._F3")
    pair_counts = {
        n: _tables(n, 2).P for n in (1, 2, 3)
    }
    if pair_counts != EXPECTED_PAIR_COUNTS:
        raise AssertionError({"r6p_pair_counts_failed": pair_counts})

    receipt_r6o = json.loads(
        Path(__file__)
        .with_name("MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json")
        .read_text()
    )
    if "REFUTED" not in receipt_r6o["authority"]:
        raise AssertionError("r6p expects the frozen refuted R6O receipt")

    panels = domain_r6n_panels()
    n1 = domain_exhaustive_n1()
    n2 = domain_structured_n2(receipt_r6o["domains"]["structured_n2"])
    random_panel = domain_random_panel(receipt_r6o["domains"]["random_panel"])
    chemistry = domain_chemistry(receipt_r6o["domains"]["chemistry"])

    critical_total = n2["critical_instances"] + random_panel["critical_instances"]
    critical_closed = (
        n2["critical_closed_at_weight_two"]
        + random_panel["critical_closed_at_weight_two"]
    )
    gates = {
        "dp_dxx_equal_r6n_panels": panels["all_equal"],
        "dp_dxx_equal_exhaustive_n1": n1["all_equal"],
        "dp_dxx_equal_structured_n2": n2["all_equal"],
        "dp_dxx_equal_random_panel": random_panel["all_equal"],
        "critical_set_receipt_crosscheck": (
            n2["receipt_crosscheck"]["critical_count_matches_receipt"]
            and n2["receipt_crosscheck"]["receipt_verbatim_rows_ok"]
            and random_panel["receipt_crosscheck"]["all_240_rows_match_receipt"]
            and random_panel["receipt_crosscheck"]["critical_sets_identical"]
        ),
        "critical_set_closed_at_weight_two": critical_total == critical_closed
        and critical_total == 486 + 73,
        "chemistry_pinched_quadruple_tie": chemistry["all_pinched_equal"]
        and chemistry["all_quadruple_tie"],
        "dxx_enumerator_binding": f3_binding
        and pair_counts == EXPECTED_PAIR_COUNTS
        and panels["weight1_restricted_binding_ok"]
        and n1["weight1_restricted_binding_ok"]
        and n2["weight1_restricted_binding_ok"]
        and random_panel["weight1_restricted_binding_ok"],
        "dp_reader_binding_exact": n1["binding_exact"]
        and n1["exact_matcher_binding_exact"]
        and n2["binding_exact"]
        and n2["exact_matcher_binding_exact"]
        and n2["block_a_swap_invariance_ok"],
        "tag_minimality_verified": True,  # enforced inside every witness check
        "witness_reverification_pass": all(
            row["dp_witness_checks_pass"] for row in panels["rows"]
        ),
        "no_new_subject_data": True,
    }
    integrity = {
        k: gates[k]
        for k in (
            "dxx_enumerator_binding",
            "dp_reader_binding_exact",
            "tag_minimality_verified",
            "no_new_subject_data",
        )
    }
    if not all(integrity.values()):
        raise AssertionError({"r6p_integrity_gate_failure": integrity})

    all_violations = (
        [row for row in panels["rows"] if not row["equal"]]
        + n1["violating_instances_verbatim"]
        + n2["violating_instances_verbatim"]
        + random_panel["violating_instances_verbatim"]
    )
    verified = not all_violations and all(gates.values())
    if verified:
        authority = (
            "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_VERIFIED__"
            "FAMILY_CLOSURE_RESTORED_AT_SUPPORT_TWO_ON_VERIFIED_DOMAINS__NOT_R6"
        )
        responsibility = (
            "RESP:WEIGHT2_FRAME_DONOR_FAMILY_MATCHES_EXACT_DP_ON_ALL_VERIFIED_FINITE_DOMAINS__"
            "R6O_WEIGHT2_TRADE_GAP_REPAIRED_BY_FAMILY_ENLARGEMENT"
        )
        discovery = None
    else:
        authority = (
            "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_REFUTED__"
            "THIRD_REGIME_BEYOND_SUPPORT_TWO_FOUND__NOT_R6"
        )
        responsibility = "RESP:THIRD_SPREAD_REGIME_DISCOVERED__REPORT_VERBATIM_AND_RE_FREEZE"
        discovery = {
            "instances_with_dp_strictly_below_dxx": all_violations,
            "note": (
                "Support-2 frames with unrestricted minimal shared Tag are "
                "still insufficient: some DP optimum requires a frame Pauli of "
                "support >= 3, a third coupling mechanism beyond the R6N "
                "Tag-anchor coupling and the R6O weight-2 trade."
            ),
        }

    result = {
        "schema": "ORIONQ.MAXR6P.Weight2FrameDonorClosure.v1",
        "authority": authority,
        "scope": (
            "WEIGHT2_FRAME_DONOR_FAMILY_CLOSURE_TEST_OVER_FROZEN_R6M_GRAMMAR__"
            "EXPLANATORY_FAMILY_CLOSURE__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_PROTOCOL",
        "dxx_definition": {
            "family": (
                "Three TARE-M2 frames whose six frame Paulis are nonzero with "
                "global support <= 2 (arbitrary support sets), ordered "
                "anticommuting per block, per-block target permutation and "
                "central bit (frozen tie: central on the heavier frame Pauli, "
                "0 on ties), common label orientation across blocks, and a "
                "minimum-weight shared Tag; cost = sum Uanti + 2 w(S) + "
                "donor-owned all-three factored Restore support."
            ),
            "enumeration": (
                "2 labels x all nonzero Tags (Tag relaxation identity: S "
                "enters only via 2 w(S), so sweeping all feasible S realizes "
                "the minimal-Tag family exactly) x per-block all ordered "
                "anticommuting support-<=2 pairs (6/120/666 at n=1/2/3) x 2 "
                "permutations; joint minimum per (S, labels) via the exact "
                "don't-care pattern min-transform over the 4^(2n) branch-qubit "
                "letter-code space."
            ),
            "containments": "C_DP <= C_Dxx <= C_Dplus <= C_R6L (hard assertions).",
            "anticommuting_pair_counts": {str(k): v for k, v in pair_counts.items()},
        },
        "domains": {
            "r6n_panels": panels,
            "exhaustive_n1": n1,
            "structured_n2": n2,
            "random_panel": random_panel,
            "chemistry": chemistry,
        },
        "critical_set_summary": {
            "structured_n2_critical": n2["critical_instances"],
            "random_critical": random_panel["critical_instances"],
            "total_critical": critical_total,
            "closed_at_weight_two": critical_closed,
            "all_critical_closed": critical_total == critical_closed,
        },
        "f3_table_binding_exact": f3_binding,
        "random_seed": RANDOM_SEED,
        "gates": gates,
        "discovery": discovery,
        "claim_boundary": CLAIM_BOUNDARY,
        "chemistry_sources_read_via_frozen_batch_only": True,
        "heavy_subject_dp_rerun": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("R6P authority ceiling violated")
    print("ORIONQ_MAX_R6P_WEIGHT2_FRAME_DONOR=" + canonical_json(result))
    runtime = time.monotonic() - start
    file_result = dict(result)
    file_result["runtime_seconds"] = round(runtime, 3)
    Path(__file__).with_name(
        "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json"
    ).write_text(json.dumps(file_result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    main()
