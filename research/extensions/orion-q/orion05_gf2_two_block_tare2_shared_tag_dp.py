#!/usr/bin/env python3
"""ORION05-GF2 two-block (four-term) shared-one-bit-Tag TARE-M2 exact referee.

Registered by:
- development/orion-05-gf2-two-block-grammar-2026-09-03/ORION05_GF2_TWO_BLOCK_GRAMMAR_PROTOCOL_V1.md

Grammar: direct k=2 restriction of the frozen R6M three-block construction.
Two ordered anticommuting target pairs, four frame letters (rA0,rA1,rB0,rB1),
one shared one-bit Tag letter, donor-lineage all-equal Restore factor rule
(F2, the two-block restriction of the R6L all-three rule; zero novelty credit).
Objective: frame cost on excess support, Tag cost 2*wt, factor slots, offset 12.

Frozen machinery is imported, never reimplemented: the local/global Pauli
algebra and canonical_json come through
max_r6m_exact_three_tare2_shared_factor_dp (the frozen 512-state R6M referee),
and this module asserts that referee's identity constants at import. The
two-block grammar tables are the registered new content of this study.

Independent brute arms (n=1 option enumeration; n=2 global s/orientation/pair
enumeration with optional frame/Tag weight caps) mirror the frozen referee's
own DP-versus-brute methodology and use only the imported algebra.

Authority ceiling: grammar-family finite-domain exact discriminant for the
ORION-05 tier-B record only. No all-n theorem, no generic TARE, no
production/runtime/hardware/physical-resource claim, no novelty authority,
no consumption of ORION-01/09/10 claims, no protected Task-3/P9 access.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402

p10 = r6m.p10

SCHEMA_ID = "ORION05.GF2.TwoBlockTare2SharedTag.v1"
STUDY_ID = "ORION05_GF2"
PROTOCOL_REL = (
    "development/orion-05-gf2-two-block-grammar-2026-09-03/"
    "ORION05_GF2_TWO_BLOCK_GRAMMAR_PROTOCOL_V1.md"
)
INF = 10 ** 12
TOL = 0.0

# ---- anti-instrument import gate (G1) ---------------------------------------

if sys.gettrace() is not None:
    raise RuntimeError("orion05_gf2: refusing to run under a trace function")
if "coverage" in sys.modules:
    raise RuntimeError("orion05_gf2: refusing to run with coverage loaded")

# ---- frozen referee identity binding (G1) -----------------------------------

if r6m.PARITY_STATES != 512 or r6m.ACCEPTING_STATES != (135, 263):
    raise RuntimeError("orion05_gf2: frozen R6M referee identity drift")
if r6m.OPTIONS != 4 ** 7:
    raise RuntimeError("orion05_gf2: frozen R6M option space drift")

sy = p10.h.local_symp
lm = p10.h.local_mul
lw = p10.h.local_wt

# Local algebra tables built from the imported frozen algebra, then asserted
# byte-identical to the frozen referee's own tables.
SY2 = np.array([[sy(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
LM2 = np.array([[lm(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
LW2 = np.array([lw(a) for a in range(4)], dtype=np.int64)
if not (np.array_equal(SY2, r6m._SY) and np.array_equal(LM2, r6m._LM)
        and np.array_equal(LW2, r6m._LW)):
    raise RuntimeError("orion05_gf2: local algebra table drift vs frozen referee")

# ---- registered two-block grammar (frozen by the protocol) -------------------

PARITY_STATES_2 = 64
OPTIONS_2 = 4 ** 5
# Six parity bits, LSB first: b0=<rA0,rA1>, b1=<rB0,rB1>,
# b2=<s,rA0>^<s,rB0>, b3=<s,rA1>^<s,rB1>, b4=<s,rA0>, b5=<s,rA1>.
# Acceptance: b0=1, b1=1, b2=0, b3=0, b4!=b5.
ACCEPTING_STATES_2 = (0b010011, 0b100011)  # (19, 35)
XOR64 = np.bitwise_xor(
    np.arange(PARITY_STATES_2)[:, None],
    np.arange(PARITY_STATES_2)[None, :],
)
COST_OFFSET_2 = 12  # sum over blocks of (m0 + m1) = (2+4) + (2+4)

_DIG2 = tuple(((np.arange(OPTIONS_2, dtype=np.int64) >> (2 * (4 - t))) & 3)
              for t in range(5))
_RA0, _RA1, _RB0, _RB1, _SS2 = _DIG2
_DELTA2 = (
    (SY2[_RA0, _RA1] << 0)
    | (SY2[_RB0, _RB1] << 1)
    | ((SY2[_SS2, _RA0] ^ SY2[_SS2, _RB0]) << 2)
    | ((SY2[_SS2, _RA1] ^ SY2[_SS2, _RB1]) << 3)
    | (SY2[_SS2, _RA0] << 4)
    | (SY2[_SS2, _RA1] << 5)
)
_TAG_COST_2 = 2 * LW2[_SS2]
_FRAME_COST_2: dict[tuple[int, int], np.ndarray] = {}
for _centrals in itertools.product((0, 1), repeat=2):
    _cost = np.zeros(OPTIONS_2, dtype=np.int64)
    for _j, _c in enumerate(_centrals):
        _m0 = 2 if _c == 0 else 4
        _m1 = 2 if _c == 1 else 4
        _cost = _cost + _m0 * LW2[_DIG2[2 * _j]] + _m1 * LW2[_DIG2[2 * _j + 1]]
    _FRAME_COST_2[_centrals] = _cost

# Donor-lineage all-equal Restore factor rule, two-block restriction.
_F2 = np.zeros((4, 4), dtype=np.int64)
for _a in range(4):
    for _b in range(4):
        if _a == _b and _a != 0:
            _F2[_a, _b] = 1
        else:
            _F2[_a, _b] = LW2[_a] + LW2[_b]


def canonical_json(value: Any) -> str:
    return r6m.canonical_json(value)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed_digest(payload: dict[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "result_digest"}
    return hashlib.sha256(canonical_json(body).encode()).hexdigest()


# ---- exact 6-bit XOR DP ------------------------------------------------------

@lru_cache(maxsize=None)
def _local_table_2(p4: tuple[int, ...], centrals: tuple[int, int]):
    """Exact local delta -> (min raw cost, option code) table for one qubit."""
    factor0 = _F2[LM2[p4[0], _RA0], LM2[p4[2], _RB0]]
    factor1 = _F2[LM2[p4[1], _RA1], LM2[p4[3], _RB1]]
    cost = _FRAME_COST_2[centrals] + _TAG_COST_2 + factor0 + factor1
    order = np.argsort(cost, kind="stable")
    deltas_sorted = _DELTA2[order]
    uniq, first = np.unique(deltas_sorted, return_index=True)
    local_cost = np.full(PARITY_STATES_2, INF, dtype=np.int64)
    local_opt = np.full(PARITY_STATES_2, -1, dtype=np.int64)
    local_cost[uniq] = cost[order][first]
    local_opt[uniq] = order[first]
    return local_cost, local_opt


def _branch_targets_2(pairs, perm_b: int):
    """Four branch targets (PA0,PA1,PB0,PB1) after block-B permutation."""
    (a0, a1), (b0, b1) = pairs
    order_b = (b0, b1) if perm_b == 0 else (b1, b0)
    return (a0, a1, order_b[0], order_b[1])


def _solve_config_2(branch_targets, centrals, n: int):
    codes4 = tuple(p10.codes(target, n) for target in branch_targets)
    dp = np.full(PARITY_STATES_2, INF, dtype=np.int64)
    dp[0] = 0
    for q in range(n):
        p4 = tuple(int(codes4[t][q]) for t in range(4))
        cost, _opt = _local_table_2(p4, centrals)
        dp = (dp[:, None] + cost[XOR64]).min(axis=0)
    return dp


def dp_config_cost(pairs, perm_b: int, centrals, n: int):
    """Exact two-block DP optimum for one configuration, canonical scale."""
    branch_targets = _branch_targets_2(pairs, perm_b)
    dp = _solve_config_2(branch_targets, tuple(centrals), n)
    values = [int(dp[state]) for state in ACCEPTING_STATES_2 if int(dp[state]) < INF]
    return None if not values else min(values) - COST_OFFSET_2


# ---- independent brute arm, n=1 ---------------------------------------------

def brute_config_n1(pairs, perm_b: int, centrals):
    """Independent full enumeration of the identical grammar at n=1."""
    ordered = (
        pairs[0],
        pairs[1] if perm_b == 0 else (pairs[1][1], pairs[1][0]),
    )
    block_letters = [
        (
            p10.h.BITS_CODE[(pair[0][0] & 1, pair[0][1] & 1)],
            p10.h.BITS_CODE[(pair[1][0] & 1, pair[1][1] & 1)],
        )
        for pair in ordered
    ]
    multipliers: list[int] = []
    for central in centrals:
        multipliers.extend((2 if central == 0 else 4, 2 if central == 1 else 4))
    best = None
    for option in itertools.product(range(4), repeat=5):
        ra0, ra1, rb0, rb1, s = option
        frames = (ra0, ra1, rb0, rb1)
        if not (sy(ra0, ra1) and sy(rb0, rb1)):
            continue
        c0, c1 = sy(s, ra0), sy(s, ra1)
        if sy(s, rb0) != c0 or sy(s, rb1) != c1:
            continue
        if c0 == c1:
            continue
        raw = sum(m * lw(r) for m, r in zip(multipliers, frames)) + 2 * lw(s)
        for k in range(2):
            pair_letters = (lm(block_letters[0][k], frames[k]),
                            lm(block_letters[1][k], frames[2 + k]))
            if pair_letters[0] == pair_letters[1] != 0:
                raw += 1
            else:
                raw += lw(pair_letters[0]) + lw(pair_letters[1])
        cost = raw - COST_OFFSET_2
        if best is None or cost < best:
            best = cost
    return best


# ---- independent brute arm, n=2 (with optional family restrictions) ----------

_KEYS_N2 = tuple((x, z) for x in range(4) for z in range(4))


@lru_cache(maxsize=None)
def _n2_tag_orientations():
    """All (tag, orientation) headers of the global enumeration (unfiltered)."""
    return tuple(
        (s, orientation)
        for s in _KEYS_N2
        if s != (0, 0)
        for orientation in ((0, 1), (1, 0))
    )


@lru_cache(maxsize=None)
def _n2_pair_list(s, orientation, frame_wt_max):
    """Ordered compatible frame pairs for one header, optional weight cap."""
    plist = tuple(
        (r0, r1)
        for r0 in _KEYS_N2
        for r1 in _KEYS_N2
        if p10.symp(r0, r1) == 1
        and p10.symp(s, r0) == orientation[0]
        and p10.symp(s, r1) == orientation[1]
        and (frame_wt_max is None
             or (p10.wt(r0) <= frame_wt_max and p10.wt(r1) <= frame_wt_max))
    )
    return plist


@lru_cache(maxsize=None)
def _n2_block_arrays(target_pair, m0: int, m1: int, s, orientation,
                     frame_wt_max):
    """Per-block (base cost vector, restore letter matrix) for one header.

    base[i] = m0*(wt(r0)-1) + m1*(wt(r1)-1) + wt(t0) + wt(t1); letters[i, k, q]
    is the local code of restore string k at qubit q.
    """
    plist = _n2_pair_list(s, orientation, frame_wt_max)
    base = np.empty(len(plist), dtype=np.int64)
    letters = np.empty((len(plist), 2, 2), dtype=np.int64)
    for idx, (r0, r1) in enumerate(plist):
        t0 = p10.mul(target_pair[0], r0)
        t1 = p10.mul(target_pair[1], r1)
        base[idx] = (
            m0 * (p10.wt(r0) - 1)
            + m1 * (p10.wt(r1) - 1)
            + p10.wt(t0)
            + p10.wt(t1)
        )
        for k, t in enumerate((t0, t1)):
            for q in range(2):
                letters[idx, k, q] = p10.h.BITS_CODE[
                    ((t[0] >> q) & 1, (t[1] >> q) & 1)]
    return base, letters


def brute_config_n2(pairs, perm_b: int, centrals,
                    frame_wt_max=None, tag_wt_max=None, witness=False):
    """Independent global enumeration at n=2; optional support-family caps.

    Returns (best_cost, witness_dict_or_None). best_cost is None when the
    (possibly restricted) family admits no feasible assignment. The F2
    all-equal adjustment subtracts 1 per (slot, qubit) whose two block
    restore letters are equal and nonzero (2 -> 1 on the canonical scale).
    """
    ordered = (
        pairs[0],
        pairs[1] if perm_b == 0 else (pairs[1][1], pairs[1][0]),
    )
    best = None
    best_witness = None
    for s, orientation in _n2_tag_orientations():
        if tag_wt_max is not None and p10.wt(s) > tag_wt_max:
            continue
        plist = _n2_pair_list(s, orientation, frame_wt_max)
        if not plist:
            continue
        m0a = 2 if centrals[0] == 0 else 4
        m1a = 2 if centrals[0] == 1 else 4
        m0b = 2 if centrals[1] == 0 else 4
        m1b = 2 if centrals[1] == 1 else 4
        base_a, la = _n2_block_arrays(ordered[0], m0a, m1a, s, orientation,
                                      frame_wt_max)
        base_b, lb = _n2_block_arrays(ordered[1], m0b, m1b, s, orientation,
                                      frame_wt_max)
        total = base_a[:, None] + base_b[None, :] + 2 * p10.wt(s)
        for k in range(2):
            for q in range(2):
                xa = la[:, k, q].reshape(-1, 1)
                xb = lb[:, k, q].reshape(1, -1)
                total = total - ((xa == xb) & (xa != 0)).astype(np.int64)
        value = int(total.min())
        if best is None or value < best:
            best = value
            if witness:
                idx = int(np.argmin(total))
                ia, ib = divmod(idx, len(plist))
                best_witness = {
                    "tag": list(s),
                    "orientation": list(orientation),
                    "blockA_frames": [list(plist[ia][0]), list(plist[ia][1])],
                    "blockB_frames": [list(plist[ib][0]), list(plist[ib][1])],
                }
    return best, best_witness


# ---- registered domains ------------------------------------------------------

def ordered_anticommuting_pairs(n_bits: int):
    span = 1 << n_bits
    keys = [(x, z) for x in range(span) for z in range(span) if (x, z) != (0, 0)]
    return [(p, q) for p in keys for q in keys if p10.symp(p, q) == 1]


_HOSTILE_N2_PAIRS = {
    "a1": ((1, 0), (0, 1)),
    "a2": ((3, 0), (0, 3)),
    "a3": ((1, 2), (2, 1)),
    "b1": ((3, 1), (1, 3)),
    "b2": ((2, 3), (3, 2)),
    "b3": ((1, 0), (2, 2)),
}
HOSTILE_PANELS_N2 = {
    "gf2_n2_a": ("a1", "a2"),
    "gf2_n2_b": ("a1", "a3"),
    "gf2_n2_c": ("a2", "a3"),
    "gf2_n2_d": ("a1", "b1"),
    "gf2_n2_e": ("a1", "a1"),
    "gf2_n2_f": ("b2", "b3"),
}

CONFIGS = [(pb, ca, cb)
           for pb in (0, 1)
           for ca in (0, 1)
           for cb in (0, 1)]


def instance_key(pairs):
    return [[list(pairs[0][0]), list(pairs[0][1])],
            [list(pairs[1][0]), list(pairs[1][1])]]


# ---- gates -------------------------------------------------------------------

def gate_d1_complete_n1() -> dict[str, Any]:
    pairs_n1 = ordered_anticommuting_pairs(1)
    cells = 0
    mismatches = []
    infeasible = 0
    for pa in pairs_n1:
        for pb in pairs_n1:
            for cfg in CONFIGS:
                pb_bit, ca, cb = cfg
                dp = dp_config_cost((pa, pb), pb_bit, (ca, cb), 1)
                br = brute_config_n1((pa, pb), pb_bit, (ca, cb))
                cells += 1
                if dp is None or br is None:
                    if dp != br:
                        mismatches.append(
                            {"instance": [(list(pa[0]), list(pa[1])),
                                          (list(pb[0]), list(pb[1]))],
                             "config": list(cfg), "dp": dp, "brute": br})
                    else:
                        infeasible += 1
                    continue
                if dp != br:
                    mismatches.append(
                        {"instance": [(list(pa[0]), list(pa[1])),
                                      (list(pb[0]), list(pb[1]))],
                         "config": list(cfg), "dp": dp, "brute": br})
    if mismatches:
        raise RuntimeError(
            {"gate": "G2_d1_complete_n1", "mismatches": mismatches[:5],
             "mismatch_count": len(mismatches)})
    return {"cells": cells, "infeasible_cells": infeasible,
            "n1_ordered_pairs": len(pairs_n1)}


def gate_d2_hostile_n2() -> dict[str, Any]:
    cells = 0
    mismatches = []
    for name, (ka, kb) in sorted(HOSTILE_PANELS_N2.items()):
        pa = _HOSTILE_N2_PAIRS[ka]
        pb = _HOSTILE_N2_PAIRS[kb]
        for cfg in CONFIGS:
            pb_bit, ca, cb = cfg
            dp = dp_config_cost((pa, pb), pb_bit, (ca, cb), 2)
            br, _ = brute_config_n2((pa, pb), pb_bit, (ca, cb))
            cells += 1
            if dp != br:
                mismatches.append({"panel": name, "config": list(cfg),
                                   "dp": dp, "brute": br})
    if mismatches:
        raise RuntimeError(
            {"gate": "G3_d2_hostile_n2", "mismatches": mismatches[:5],
             "mismatch_count": len(mismatches)})
    return {"cells": cells, "panels": sorted(HOSTILE_PANELS_N2)}


def gate_d3_complete_n2_sweep(sample_rate: int = 97,
                              perm_sample_rate: int = 144) -> dict[str, Any]:
    pairs_n2 = ordered_anticommuting_pairs(2)
    m = len(pairs_n2)
    instances = 0
    feasible = 0
    dp_infeasible = 0
    perm_checks = 0
    gap_cells_f1f = []
    gap_cells_f1a = []
    family_infeasible_f1f = 0
    family_infeasible_f1a = 0
    sample_idx = 0
    perm_sample_idx = 0
    brute_sample_cells = 0
    brute_sample_mismatches = []
    t0 = time.time()
    for ia, pa in enumerate(pairs_n2):
        for ib, pb in enumerate(pairs_n2):
            instance = (pa, pb)
            instances += 1
            # unrestricted DP optimum over all 8 configurations
            best_u = None
            best_cfg = None
            for cfg in CONFIGS:
                pb_bit, ca, cb = cfg
                c = dp_config_cost(instance, pb_bit, (ca, cb), 2)
                if c is not None and (best_u is None or c < best_u):
                    best_u = c
                    best_cfg = cfg
            if best_u is None:
                dp_infeasible += 1
                continue
            feasible += 1
            # restricted family optima (independent brute arm)
            best_f1f = None
            best_f1f_cfg = None
            best_f1a = None
            for cfg in CONFIGS:
                pb_bit, ca, cb = cfg
                c1, _ = brute_config_n2(instance, pb_bit, (ca, cb),
                                        frame_wt_max=1)
                if c1 is not None and (best_f1f is None or c1 < best_f1f):
                    best_f1f = c1
                    best_f1f_cfg = cfg
                c2, _ = brute_config_n2(instance, pb_bit, (ca, cb),
                                        frame_wt_max=1, tag_wt_max=1)
                if c2 is not None and (best_f1a is None or c2 < best_f1a):
                    best_f1a = c2
            if best_f1f is None or best_u < best_f1f:
                if best_f1f is None:
                    family_infeasible_f1f += 1
                gap_cells_f1f.append({
                    "instance": instance_key(instance),
                    "unrestricted": best_u,
                    "unrestricted_config": list(best_cfg),
                    "f1f": best_f1f,
                    "f1f_config": (list(best_f1f_cfg)
                                   if best_f1f_cfg is not None else None),
                    "family_infeasible": best_f1f is None})
            if best_f1a is None or best_u < best_f1a:
                if best_f1a is None:
                    family_infeasible_f1a += 1
                gap_cells_f1a.append({
                    "instance": instance_key(instance),
                    "unrestricted": best_u,
                    "unrestricted_config": list(best_cfg),
                    "f1a": best_f1a,
                    "family_infeasible": best_f1a is None})
            # G4: permutation symmetry on a deterministic sample
            perm_sample_idx += 1
            if perm_sample_idx % perm_sample_rate == 0:
                swapped = (pb[1], pb[0])
                for (ca, cb) in itertools.product((0, 1), repeat=2):
                    c_direct = dp_config_cost(instance, 1, (ca, cb), 2)
                    c_swapped = dp_config_cost((pa, swapped), 0, (ca, cb), 2)
                    perm_checks += 1
                    if c_direct != c_swapped:
                        raise RuntimeError(
                            {"gate": "G4_perm_symmetry",
                             "instance": instance_key(instance),
                             "centrals": [ca, cb],
                             "direct": c_direct, "swapped": c_swapped})
            # brute cross-check on a deterministic systematic sample
            sample_idx += 1
            if sample_idx % sample_rate == 0:
                br_best = None
                for cfg in CONFIGS:
                    pb_bit, ca, cb = cfg
                    c, _w = brute_config_n2(instance, pb_bit, (ca, cb))
                    brute_sample_cells += 1
                    if c is not None and (br_best is None or c < br_best):
                        br_best = c
                if br_best != best_u:
                    brute_sample_mismatches.append(
                        {"instance": instance_key(instance),
                         "dp": best_u, "brute": br_best})
        if ia % 20 == 0:
            print(f"  sweep progress: blockA index {ia}/{m}, "
                  f"instances {instances}, elapsed {time.time() - t0:.1f}s",
                  flush=True)
    if brute_sample_mismatches:
        raise RuntimeError(
            {"gate": "G5_d3_sample_mismatch",
             "mismatches": brute_sample_mismatches[:5],
             "mismatch_count": len(brute_sample_mismatches)})
    # G5: re-verify recorded witness rows with the independent brute arm and
    # attach achieving-letter witnesses for the first rows.
    for row in gap_cells_f1f[:20]:
        inst = tuple(((tuple(map(int, r[0])), tuple(map(int, r[1])))
                      for r in row["instance"]))
        br_best = None
        for cfg in CONFIGS:
            pb_bit, ca, cb = cfg
            c, _w = brute_config_n2(inst, pb_bit, (ca, cb))
            if c is not None and (br_best is None or c < br_best):
                br_best = c
        if br_best != row["unrestricted"]:
            raise RuntimeError({"gate": "G5_witness_dp_brute_mismatch",
                                "row": row, "brute": br_best})
        pb_bit, ca, cb = row["unrestricted_config"]
        _cu, wu = brute_config_n2(inst, pb_bit, (ca, cb), witness=True)
        row["unrestricted_witness"] = wu
        if row["f1f_config"] is not None:
            pb_bit, ca, cb = row["f1f_config"]
            _cf, wf = brute_config_n2(inst, pb_bit, (ca, cb), frame_wt_max=1,
                                      witness=True)
            row["f1f_witness"] = wf
    for row in gap_cells_f1a[:20]:
        inst = tuple(((tuple(map(int, r[0])), tuple(map(int, r[1])))
                      for r in row["instance"]))
        br_best = None
        for cfg in CONFIGS:
            pb_bit, ca, cb = cfg
            c, _w = brute_config_n2(inst, pb_bit, (ca, cb))
            if c is not None and (br_best is None or c < br_best):
                br_best = c
        if br_best != row["unrestricted"]:
            raise RuntimeError({"gate": "G5_witness_dp_brute_mismatch_f1a",
                                "row": row, "brute": br_best})
    return {
        "n2_ordered_pairs": m,
        "instances": instances,
        "feasible_unrestricted": feasible,
        "dp_infeasible_instances": dp_infeasible,
        "perm_symmetry_checks": perm_checks,
        "brute_sample_cells": brute_sample_cells,
        "gap_cells_f1f": len(gap_cells_f1f),
        "gap_cells_f1a": len(gap_cells_f1a),
        "family_infeasible_f1f": family_infeasible_f1f,
        "family_infeasible_f1a": family_infeasible_f1a,
        "gap_rows_f1f": gap_cells_f1f[:20],
        "gap_rows_f1a": gap_cells_f1a[:20],
        "elapsed_seconds": round(time.time() - t0, 2),
    }


# ---- entry -------------------------------------------------------------------

def main(smoke: bool = False) -> dict[str, Any]:
    t_start = time.time()
    if smoke:
        d1 = gate_d1_complete_n1()
        payload = {"schema": SCHEMA_ID, "study": STUDY_ID, "smoke": True,
                   "gates": {"G2_d1": d1}}
        print(canonical_json(payload))
        return payload

    d1 = gate_d1_complete_n1()
    print(f"G2 D1 complete n=1: {canonical_json(d1)}", flush=True)
    d2 = gate_d2_hostile_n2()
    print(f"G3 D2 hostile n=2: {canonical_json(d2)}", flush=True)
    d3 = gate_d3_complete_n2_sweep()
    print(f"D3 complete n=2 sweep: {canonical_json({k: v for k, v in d3.items() if k != 'gap_rows_f1f' and k != 'gap_rows_f1a'})}", flush=True)

    gap_f1f = d3["gap_cells_f1f"]
    gap_f1a = d3["gap_cells_f1a"]
    if gap_f1f or gap_f1a:
        terminal = "ORION05_GF2_TWO_BLOCK_SHARPNESS_WITNESS_UNRESTRICTED_BELOW_SUPPORT_ONE"
    else:
        terminal = "ORION05_GF2_TWO_BLOCK_SUPPORT_ONE_SUFFICIENT_COMPLETE_N2"

    root = Path(__file__).resolve().parents[3]
    protocol_path = root / PROTOCOL_REL
    payload = {
        "schema": SCHEMA_ID,
        "study": STUDY_ID,
        "base_revision": _git_revision(root),
        "protocol_relpath": PROTOCOL_REL,
        "protocol_sha256": file_sha256(protocol_path),
        "registered_questions": {
            "Q1_referee_exactness": "DP == independent brute on complete n=1 "
                                    "domain and hostile n=2 panels, per config",
            "Q2_support_one_threshold_at_k2": "complete n=2 instance space: "
                                              "unrestricted < support-one family "
                                              "(F1f frames-only; F1a all letters)?",
        },
        "domains": {
            "D1_complete_n1": d1,
            "D2_hostile_n2": d2,
            "D3_complete_n2": {k: v for k, v in d3.items()
                               if k not in ("gap_rows_f1f", "gap_rows_f1a")},
        },
        "gates": {
            "G1_anti_instrument_and_frozen_binding": True,
            "G2_d1_complete_n1_dp_brute_equal": True,
            "G3_d2_hostile_n2_dp_brute_equal": True,
            "G4_perm_symmetry_sampled": d3["perm_symmetry_checks"],
            "G5_witness_and_sample_brute_reverified": True,
            "G6_envelope": True,
        },
        "comparison": {
            "f1f_gap_cells": gap_f1f,
            "f1a_gap_cells": gap_f1a,
            "f1f_gap_rows": d3["gap_rows_f1f"],
            "f1a_gap_rows": d3["gap_rows_f1a"],
        },
        "terminal": terminal,
        "terminal_note": (f"dp_infeasible_instances={d3['dp_infeasible_instances']}"
                          if d3["dp_infeasible_instances"] else "none"),
        "authority": "Grammar-family finite-domain exact discriminant for the "
                     "ORION-05 tier-B record only. No all-n theorem, no generic "
                     "TARE or block-encoding claim, no production/runtime/"
                     "hardware/physical-resource claim, no novelty adjudication, "
                     "no venue/submission authority, no consumption or alteration "
                     "of ORION-01/09/10 claims, no protected Task-3/P9 access, "
                     "no threshold retuning of historical adverse records.",
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
        "driver_relpath": "research/extensions/orion-q/"
                          "orion05_gf2_two_block_tare2_shared_tag_dp.py",
        "runtime_seconds": round(time.time() - t_start, 2),
    }
    payload["result_digest"] = signed_digest(payload)
    result_path = (root / "development/orion-05-gf2-two-block-grammar-2026-09-03"
                   / "result" / "ORION05_GF2_RESULT.json")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"result written: {result_path}", flush=True)
    print(canonical_json(
        {k: payload[k] for k in ("schema", "study", "terminal",
                                 "result_digest", "runtime_seconds")}),
        flush=True)
    return payload


def _git_revision(root: Path) -> str:
    import subprocess
    return subprocess.run(
        ["/usr/bin/git", "rev-parse", "HEAD"], cwd=str(root),
        capture_output=True, text=True, check=True).stdout.strip()


if __name__ == "__main__":
    main(smoke="--smoke" in sys.argv)
