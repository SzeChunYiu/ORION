#!/usr/bin/env python3
"""MAX-R6I exact rank-2 dependent TARE-3 shared-Tag joint DP.

Frozen by MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_PROTOCOL.md, which incorporates by
reference the frozen Uanti parity-support accounting of
MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md and its three errata.

Residual under test: jointly choose two arbitrary rank-2 dependent TARE-3
frames under one common Tag pair (paid once), with block-specific Uanti
realizations, target-to-label assignments and Restore strings. The common-Tag
circuit identity itself is donor-owned (R6H) and receives zero novelty credit.

Uses only already-open H4 and equilibrium-N2 evidence through the frozen R6B
six-term batches. The protected stretched-N2 prospective discriminator is
never read. A positive result remains below R6.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6b_tare_transformation_reuse_donor as reuse
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6h_partial_tag_sharing_donor as r6h

TOL = 1e-12
INF = 10**12
STATES = 1024
OPTIONS = 4096
UANTI_CONSTANT = 20
CONFIG_COUNT = 54
# Positive identity pin: only the already-open H4 and equilibrium-N2 sources may
# be configured. The protected stretched-N2 prospective discriminator is never
# named, read, or referenced by this lane.
FROZEN_OPEN_SUBJECT_BLOBS = {
    "H4": "b98792b1055dbac0ebf2a7576f72412e3e4ac6c5",
    "N2": "15369e8e886efbb3d32f3b2dfe2cfbb96ddebeba",
}

XOR1024 = np.bitwise_xor(np.arange(STATES)[:, None], np.arange(STATES)[None, :])

# ---- Frozen local option enumeration ---------------------------------------
# Protocol option order (rA0,rA1,rB0,rB1,s0,s1); the base-4 option code equals
# the enumeration index with rA0 as the most significant digit.
_OPT = np.arange(OPTIONS)
_RA0 = (_OPT >> 10) & 3
_RA1 = (_OPT >> 8) & 3
_RB0 = (_OPT >> 6) & 3
_RB1 = (_OPT >> 4) & 3
_S0 = (_OPT >> 2) & 3
_S1 = _OPT & 3

_MUL = np.array([[p10.h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
_SYMP = np.array([[p10.h.local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
_LW = np.array([p10.h.local_wt(a) for a in range(4)], dtype=np.int64)
_LWMUL = np.array([[p10.h.local_wt(p10.h.local_mul(a, b)) for b in range(4)] for a in range(4)], dtype=np.int64)

_RA2 = _MUL[_RA0, _RA1]
_RB2 = _MUL[_RB0, _RB1]

# Frozen 10-bit parity delta:
# 0: <RA0,RA1>; 1: <RB0,RB1>;
# 2-5: A/B Tag-syndrome differences for (S0,R0),(S1,R0),(S0,R1),(S1,R1);
# 6-9: actual A Tag-syndrome bits in the same (S0,R0),(S1,R0),(S0,R1),(S1,R1) order.
_DELTA = (
    (_SYMP[_RA0, _RA1] << 0)
    | (_SYMP[_RB0, _RB1] << 1)
    | ((_SYMP[_S0, _RA0] ^ _SYMP[_S0, _RB0]) << 2)
    | ((_SYMP[_S1, _RA0] ^ _SYMP[_S1, _RB0]) << 3)
    | ((_SYMP[_S0, _RA1] ^ _SYMP[_S0, _RB1]) << 4)
    | ((_SYMP[_S1, _RA1] ^ _SYMP[_S1, _RB1]) << 5)
    | (_SYMP[_S0, _RA0] << 6)
    | (_SYMP[_S1, _RA0] << 7)
    | (_SYMP[_S0, _RA1] << 8)
    | (_SYMP[_S1, _RA1] << 9)
)

_TAG_LOCAL = 2 * (_LW[_S0] + _LW[_S1])
_FRAME_A = []
_FRAME_B = []
for _central in range(3):
    _mult = [4, 4, 4]
    _mult[_central] = 2
    _FRAME_A.append(_mult[0] * _LW[_RA0] + _mult[1] * _LW[_RA1] + _mult[2] * _LW[_RA2])
    _FRAME_B.append(_mult[0] * _LW[_RB0] + _mult[1] * _LW[_RB1] + _mult[2] * _LW[_RB2])

_LOCAL_CACHE: dict[tuple[int, ...], tuple[np.ndarray, np.ndarray]] = {}


def _local_table(key: tuple[int, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Per-delta minimum raw local cost with base-4 option-code tie-break."""
    cached = _LOCAL_CACHE.get(key)
    if cached is not None:
        return cached
    pa0, pa1, pa2, pb0, pb1, pb2, central_a, central_b = key
    base = (
        _FRAME_A[central_a]
        + _FRAME_B[central_b]
        + _TAG_LOCAL
        + _LWMUL[pa0, _RA0]
        + _LWMUL[pa1, _RA1]
        + _LWMUL[pa2, _RA2]
        + _LWMUL[pb0, _RB0]
        + _LWMUL[pb1, _RB1]
        + _LWMUL[pb2, _RB2]
    )
    order = np.argsort(base, kind="stable")
    unique_delta, first = np.unique(_DELTA[order], return_index=True)
    costs = np.full(STATES, INF, dtype=np.int64)
    codes = np.full(STATES, 1 << 30, dtype=np.int64)
    costs[unique_delta] = base[order][first]
    codes[unique_delta] = order[first]
    _LOCAL_CACHE[key] = (costs, codes)
    return costs, codes


def _accepting_states() -> tuple[tuple[int, tuple[int, int, int]], ...]:
    rows = []
    for parity in range(STATES):
        if parity & 0b11 != 0b11:
            continue
        if parity & 0b111100:
            continue
        c0 = 2 * ((parity >> 6) & 1) + ((parity >> 7) & 1)
        c1 = 2 * ((parity >> 8) & 1) + ((parity >> 9) & 1)
        if c0 == 0 or c1 == 0 or c0 == c1:
            continue
        rows.append((parity, (c0, c1, c0 ^ c1)))
    if len(rows) != 6:
        raise AssertionError({"accepting_state_count_not_6": rows})
    return tuple(rows)


ACCEPTING = _accepting_states()


def _config_tables(
    codes_a: tuple[tuple[int, ...], ...],
    codes_b_permuted: tuple[tuple[int, ...], ...],
    central_a: int,
    central_b: int,
    n: int,
):
    return [
        _local_table(
            (
                codes_a[0][q], codes_a[1][q], codes_a[2][q],
                codes_b_permuted[0][q], codes_b_permuted[1][q], codes_b_permuted[2][q],
                central_a, central_b,
            )
        )
        for q in range(n)
    ]


def _solve_config(tables, n: int, keep_history: bool):
    dp = np.full(STATES, INF, dtype=np.int64)
    dp[0] = 0
    histories = [dp.copy()] if keep_history else None
    for q in range(n):
        costs = tables[q][0]
        dp = (dp[:, None] + costs[XOR1024]).min(axis=0)
        if keep_history:
            histories.append(dp.copy())
    return dp, histories


def _backtrack(histories, tables, final_state: int, n: int):
    """Frozen tie rule: local option code, then predecessor state."""
    state = final_state
    sequences = [[0] * n for _ in range(6)]
    for q in range(n - 1, -1, -1):
        costs, codes = tables[q]
        current_cost = int(histories[q + 1][state])
        previous = histories[q]
        candidates = []
        for predecessor in range(STATES):
            predecessor_cost = int(previous[predecessor])
            if predecessor_cost >= INF:
                continue
            delta = predecessor ^ state
            local_cost = int(costs[delta])
            if local_cost >= INF:
                continue
            if predecessor_cost + local_cost != current_cost:
                continue
            candidates.append((int(codes[delta]), predecessor))
        if not candidates:
            raise AssertionError({"r6i_backtrack_failed": True, "q": q, "state": state})
        code, state = min(candidates)
        letters = (
            (code >> 10) & 3, (code >> 8) & 3, (code >> 6) & 3,
            (code >> 4) & 3, (code >> 2) & 3, code & 3,
        )
        for i, letter in enumerate(letters):
            sequences[i][q] = letter
    if state != 0:
        raise AssertionError("r6i backtrack did not return to the zero state")
    return tuple(p10.key_from_codes(sequence) for sequence in sequences)


def _witness(
    targets_a,
    targets_b,
    n: int,
    permutation_b: tuple[int, int, int],
    central_a: int,
    central_b: int,
    globals_,
    cost: int,
    final_state: int,
) -> dict[str, Any]:
    ra0, ra1, rb0, rb1, s0, s1 = globals_
    rs_a = (ra0, ra1, p10.mul(ra0, ra1))
    rs_b = (rb0, rb1, p10.mul(rb0, rb1))
    labels_a = reuse._labels(s0, s1, rs_a)
    labels_b = reuse._labels(s0, s1, rs_b)
    # Block A target assignment is frozen to source-index order.
    permuted_b = tuple(targets_b[permutation_b[k]] for k in range(3))
    restores_a = tuple(p10.mul(targets_a[k], rs_a[k]) for k in range(3))
    restores_b = tuple(p10.mul(permuted_b[k], rs_b[k]) for k in range(3))
    phases_a = tuple(reuse.correction_phase(targets_a[k], rs_a[k], restores_a[k], n) for k in range(3))
    phases_b = tuple(reuse.correction_phase(permuted_b[k], rs_b[k], restores_b[k], n) for k in range(3))
    uanti_a = p10.uanti_support(rs_a, central_a)
    uanti_b = p10.uanti_support(rs_b, central_b)
    tag = 2 * (p10.wt(s0) + p10.wt(s1))
    restore_support_a = sum(p10.wt(t) for t in restores_a)
    restore_support_b = sum(p10.wt(t) for t in restores_b)
    recomputed = uanti_a + uanti_b + tag + restore_support_a + restore_support_b

    recomputed_state = (
        (p10.symp(ra0, ra1) << 0)
        | (p10.symp(rb0, rb1) << 1)
        | ((p10.symp(s0, ra0) ^ p10.symp(s0, rb0)) << 2)
        | ((p10.symp(s1, ra0) ^ p10.symp(s1, rb0)) << 3)
        | ((p10.symp(s0, ra1) ^ p10.symp(s0, rb1)) << 4)
        | ((p10.symp(s1, ra1) ^ p10.symp(s1, rb1)) << 5)
        | (p10.symp(s0, ra0) << 6)
        | (p10.symp(s1, ra0) << 7)
        | (p10.symp(s0, ra1) << 8)
        | (p10.symp(s1, ra1) << 9)
    )

    checks = {
        "pairwise_anti_A": p10.is_pairwise_anti(rs_a),
        "pairwise_anti_B": p10.is_pairwise_anti(rs_b),
        "symplectic_basis_A": p10.symp(ra0, ra1) == 1,
        "symplectic_basis_B": p10.symp(rb0, rb1) == 1,
        "rank2_dependent_A": (
            p10.mul(p10.mul(rs_a[0], rs_a[1]), rs_a[2]) == (0, 0)
            and exact._gf2_rank(rs_a, n) == 2
        ),
        "rank2_dependent_B": (
            p10.mul(p10.mul(rs_b[0], rs_b[1]), rs_b[2]) == (0, 0)
            and exact._gf2_rank(rs_b, n) == 2
        ),
        "labels_equal_across_blocks": labels_a == labels_b,
        "labels_exactly_123": sorted(labels_a) == [1, 2, 3],
        "dependent_third_label": labels_a[2] == labels_a[0] ^ labels_a[1],
        "tag_label_formula": all(
            labels_a[k] == 2 * p10.symp(s0, rs_a[k]) + p10.symp(s1, rs_a[k])
            and labels_b[k] == 2 * p10.symp(s0, rs_b[k]) + p10.symp(s1, rs_b[k])
            for k in range(3)
        ),
        "restore_A": all(p10.mul(restores_a[k], rs_a[k]) == targets_a[k] for k in range(3)),
        "restore_B": all(p10.mul(restores_b[k], rs_b[k]) == permuted_b[k] for k in range(3)),
        "restore_phase_A_exact": all(
            reuse.mul_phase(restores_a[k], rs_a[k], n)
            == (targets_a[k], (-phases_a[k]) % 4)
            for k in range(3)
        ),
        "restore_phase_B_exact": all(
            reuse.mul_phase(restores_b[k], rs_b[k], n)
            == (permuted_b[k], (-phases_b[k]) % 4)
            for k in range(3)
        ),
        "final_state_recomputed": recomputed_state == final_state,
        "cost_recomputed": recomputed == cost,
    }
    if not all(checks.values()):
        raise AssertionError({"r6i_witness_failed": checks})
    return {
        "RA": [list(r) for r in rs_a],
        "RB": [list(r) for r in rs_b],
        "S0": list(s0),
        "S1": list(s1),
        "labels": list(labels_a),
        "relative_B_permutation": list(permutation_b),
        "central_A": int(central_a),
        "central_B": int(central_b),
        "signed_T_A": [
            {"phase": int(phases_a[k]), "T": list(restores_a[k])} for k in range(3)
        ],
        "signed_T_B": [
            {"phase": int(phases_b[k]), "T": list(restores_b[k])} for k in range(3)
        ],
        "uanti_support_A": int(uanti_a),
        "uanti_support_B": int(uanti_b),
        "tag_support_twice_shared": int(tag),
        "restore_support_A": int(restore_support_a),
        "restore_support_B": int(restore_support_b),
        "C_shared": int(cost),
        "final_parity_state": int(final_state),
        "checks": checks,
    }


def shared_tag_exact(targets_a, targets_b, n: int) -> dict[str, Any]:
    """Exact 10-bit shared-Tag DP over all 54 (relative B perm, cA, cB) configs."""
    targets_a = tuple(tuple(t) for t in targets_a)
    targets_b = tuple(tuple(t) for t in targets_b)
    codes_a = tuple(p10.codes(t, n) for t in targets_a)
    codes_b = tuple(p10.codes(t, n) for t in targets_b)
    candidates = []
    config_count = 0
    for permutation_b in itertools.permutations(range(3)):
        codes_b_permuted = tuple(codes_b[permutation_b[k]] for k in range(3))
        for central_a in range(3):
            for central_b in range(3):
                config_count += 1
                tables = _config_tables(codes_a, codes_b_permuted, central_a, central_b, n)
                dp, _ = _solve_config(tables, n, keep_history=False)
                for parity, _labels_acc in ACCEPTING:
                    raw = int(dp[parity])
                    if raw >= INF:
                        continue
                    candidates.append(
                        (
                            raw - UANTI_CONSTANT,
                            tuple(permutation_b),
                            central_a,
                            central_b,
                            parity,
                        )
                    )
    if config_count != CONFIG_COUNT:
        raise AssertionError({"r6i_config_count_drift": config_count})
    if not candidates:
        raise AssertionError("r6i exact shared-Tag DP produced no accepting state")
    best = min(candidates)
    cost, permutation_b, central_a, central_b, final_state = best
    optimal_candidate_count = sum(1 for row in candidates if row[0] == cost)

    codes_b_permuted = tuple(codes_b[permutation_b[k]] for k in range(3))
    tables = _config_tables(codes_a, codes_b_permuted, central_a, central_b, n)
    dp, histories = _solve_config(tables, n, keep_history=True)
    if int(dp[final_state]) - UANTI_CONSTANT != cost:
        raise AssertionError("r6i final state bookkeeping mismatch")
    globals_ = _backtrack(histories, tables, final_state, n)
    witness = _witness(
        targets_a,
        targets_b,
        n,
        permutation_b,
        central_a,
        central_b,
        globals_,
        int(cost),
        int(final_state),
    )
    witness["config_count"] = config_count
    witness["optimal_candidate_count"] = int(optimal_candidate_count)
    return witness


# ---- Structurally independent hostile brute force ---------------------------


def brute_shared_cost(targets_a, targets_b, n: int) -> int:
    """Global Pauli-string exhaustive solver for the same frozen grammar."""
    targets_a = tuple(tuple(t) for t in targets_a)
    targets_b = tuple(tuple(t) for t in targets_b)
    limit = 1 << n
    keys = [(x, z) for x in range(limit) for z in range(limit)]
    nonzero = [k for k in keys if k != (0, 0)]
    pairs = [(r0, r1) for r0 in nonzero for r1 in nonzero if p10.symp(r0, r1) == 1]
    best = INF
    for ra0, ra1 in pairs:
        rs_a = (ra0, ra1, p10.mul(ra0, ra1))
        uanti_a = min(p10.uanti_support(rs_a, central) for central in range(3))
        restore_a = sum(p10.wt(p10.mul(targets_a[k], rs_a[k])) for k in range(3))
        for rb0, rb1 in pairs:
            rs_b = (rb0, rb1, p10.mul(rb0, rb1))
            min_weight = [INF] * 4
            for s in keys:
                if p10.symp(s, ra0) != p10.symp(s, rb0):
                    continue
                if p10.symp(s, ra1) != p10.symp(s, rb1):
                    continue
                syndrome_class = 2 * p10.symp(s, ra0) + p10.symp(s, ra1)
                weight = p10.wt(s)
                if weight < min_weight[syndrome_class]:
                    min_weight[syndrome_class] = weight
            best_tag = INF
            for hi in range(4):
                if min_weight[hi] >= INF:
                    continue
                for lo in range(4):
                    if min_weight[lo] >= INF:
                        continue
                    c0 = 2 * ((hi >> 1) & 1) + ((lo >> 1) & 1)
                    c1 = 2 * (hi & 1) + (lo & 1)
                    if c0 == 0 or c1 == 0 or c0 == c1:
                        continue
                    best_tag = min(best_tag, 2 * (min_weight[hi] + min_weight[lo]))
            if best_tag >= INF:
                continue
            uanti_b = min(p10.uanti_support(rs_b, central) for central in range(3))
            restore_b = min(
                sum(p10.wt(p10.mul(targets_b[perm[k]], rs_b[k])) for k in range(3))
                for perm in itertools.permutations(range(3))
            )
            total = uanti_a + uanti_b + best_tag + restore_a + restore_b
            if total < best:
                best = total
    if best >= INF:
        raise AssertionError("r6i brute solver produced no admissible frame pair")
    return int(best)


# Deterministic synthetic panel: no chemistry data, no protected subject content.
X, Y, Z = (1, 0), (1, 1), (0, 1)
HOSTILE_PANELS = {
    "n1_same_blocks": (1, (X, Y, Z), (X, Y, Z)),
    "n1_permuted_blocks": (1, (X, Y, Z), (Z, X, Y)),
    "n1_mixed": (1, (X, Z, X), (Y, Y, Z)),
    "n2_a": (2, ((0b01, 0b00), (0b00, 0b10), (0b11, 0b01)), ((0b10, 0b01), (0b01, 0b11), (0b11, 0b10))),
    "n2_b": (2, ((0b10, 0b01), (0b01, 0b11), (0b11, 0b10)), ((0b01, 0b10), (0b10, 0b00), (0b00, 0b11))),
    "n2_permuted_blocks": (2, ((0b01, 0b00), (0b11, 0b10), (0b00, 0b11)), ((0b00, 0b11), (0b01, 0b00), (0b11, 0b10))),
    "n2_tie": (2, ((0b01, 0b00), (0b00, 0b01), (0b01, 0b01)), ((0b01, 0b00), (0b00, 0b01), (0b01, 0b01))),
}


def hostile_validation() -> dict[str, Any]:
    inherited_r6h = r6h.hostile_validation()
    inherited_exact = exact.hostile_exactness()
    panels = {}
    for name, (n, targets_a, targets_b) in HOSTILE_PANELS.items():
        witness = shared_tag_exact(targets_a, targets_b, n)
        brute = brute_shared_cost(targets_a, targets_b, n)
        passed = witness["C_shared"] == brute and all(witness["checks"].values())
        panels[name] = {
            "n": n,
            "dp_cost": int(witness["C_shared"]),
            "brute_cost": int(brute),
            "witness_cost_recomputed": bool(witness["checks"]["cost_recomputed"]),
            "relative_B_permutation": witness["relative_B_permutation"],
            "optimal_candidate_count": int(witness["optimal_candidate_count"]),
            "pass": passed,
        }
        if not passed:
            raise AssertionError({"r6i_hostile_exactness_failed": name, **panels[name]})
    permuted_case_present = any(
        sorted(targets_a) == sorted(targets_b) and tuple(targets_a) != tuple(targets_b)
        for _n, targets_a, targets_b in HOSTILE_PANELS.values()
    )
    different_blocks_present = any(
        tuple(targets_a) != tuple(targets_b)
        for _n, targets_a, targets_b in HOSTILE_PANELS.values()
    )
    gates = {
        "dp_vs_brute_all_exact": all(row["pass"] for row in panels.values()),
        "n1_and_n2_panels_present": (
            any(row["n"] == 1 for row in panels.values())
            and any(row["n"] == 2 for row in panels.values())
        ),
        "different_block_target_case_present": different_blocks_present,
        "permuted_target_case_present": permuted_case_present,
        "tie_case_present": any(row["optimal_candidate_count"] >= 2 for row in panels.values()),
        "r6h_partial_tag_hostile_pass": inherited_r6h["all_pass"] is True,
        "exact_tare3_hostile_all_exact": inherited_exact["all_exact"] is True,
    }
    if not all(gates.values()):
        raise AssertionError({"r6i_hostile_gate_failure": gates})
    return {
        "gates": gates,
        "panels": panels,
        "inherited_r6h_gates": inherited_r6h["gates"],
        "inherited_exact_tare3_panels": inherited_exact["panels"],
        "brute_solver": "global rank-2 pair enumeration with shared-Tag syndrome-class scan",
        "all_pass": True,
    }


# ---- Frozen incumbent comparator (frame-only / R6B reuse / R6H donor) -------


def _block(terms, indices):
    return {
        "targets": [list(terms[i][0]) for i in indices],
        "term_indices": list(indices),
    }


def _lambda(terms, triple) -> float:
    return float((3.0 * sum(float(terms[i][1]) ** 2 for i in triple)) ** 0.5)


def _incumbent_rows(terms, source_indices: tuple[int, ...], n: int):
    r6d_eval = r6d._evaluate_fixed_batch(terms, source_indices, n)
    if len(r6d_eval.get("all_partitions", [])) != 10 or r6d_eval.get("all_witnesses_valid") is not True:
        raise AssertionError("R6I R6D incumbent replay failed")
    rows = []
    for partition in r6d_eval["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        h = r6h.best_partial_tag(_block(terms, a), _block(terms, b), n)
        h_cost = None if h["best"] is None else int(h["best"]["C_partial_tag"])
        base = next(
            row for row in r6d_eval["eligible_points"] if row["partition"] == [list(a), list(b)]
        )
        known = [("FRAME_ONLY", int(base["C_frame_only"]))]
        if base.get("C_reuse") is not None:
            known.append(("R6B_REUSE", int(base["C_reuse"])))
        if h_cost is not None:
            known.append(("R6H_PARTIAL_TAG", h_cost))
        incumbent_cost = min(cost for _source, cost in known)
        incumbent_source = min(
            (source for source, cost in known if cost == incumbent_cost)
        )
        rows.append({
            "partition": [list(a), list(b)],
            "Lambda_batch": float(_lambda(terms, a) + _lambda(terms, b)),
            "C_incumbent": int(incumbent_cost),
            "incumbent_source": incumbent_source,
            "C_frame_only": int(base["C_frame_only"]),
            "C_reuse": base.get("C_reuse"),
            "C_R6H": h_cost,
        })
    return r6d_eval, rows


def _envelope(rows, lam: float):
    eligible = [row for row in rows if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"R6I_empty_incumbent_envelope": lam})
    best = min(
        eligible,
        key=lambda row: (int(row["C_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )
    return int(best["C_incumbent"]), best


def run_subject(name: str, cfg) -> dict[str, Any]:
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    if len(source_indices) != 6:
        return {
            "subject": name, "source_blob_expected": cfg["blob"], "source_blob_observed": observed_blob,
            "source_blob_verified": observed_blob == cfg["blob"], "batch_complete": False,
            "r6b_window_champions_available": len(champions), "frozen_source_indices": list(source_indices),
            "partition_count": 0, "eligible_partition_count": 0, "incumbent_replay_valid": False,
            "strict_count": 0, "strict_budget_matched_improvement_exists": False,
            "best_strict": None, "partitions": [], "max_imag": float(max_imag),
        }
    r6d_eval, incumbent_rows = _incumbent_rows(terms, source_indices, n)
    rows = []
    for partition in r6d_eval["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        targets_a = tuple(terms[i][0] for i in a)
        targets_b = tuple(terms[i][0] for i in b)
        witness = shared_tag_exact(targets_a, targets_b, n)
        lam = float(_lambda(terms, a) + _lambda(terms, b))
        incumbent_cost, incumbent_witness = _envelope(incumbent_rows, lam)
        delta = int(incumbent_cost - int(witness["C_shared"]))
        rows.append({
            "partition": [list(a), list(b)],
            "Lambda_batch": lam,
            "C_shared": int(witness["C_shared"]),
            "witness": witness,
            "C_incumbent_envelope": int(incumbent_cost),
            "incumbent_envelope_witness": incumbent_witness,
            "delta_vs_incumbent": delta,
            "strict_budget_matched_improvement": delta > 0,
        })
    strict = sorted(
        (row for row in rows if row["strict_budget_matched_improvement"]),
        key=lambda row: (-int(row["delta_vs_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )
    return {
        "subject": name,
        "source_blob_expected": cfg["blob"],
        "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"],
        "batch_complete": True,
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": list(source_indices),
        "partition_count": len(r6d_eval["all_partitions"]),
        "eligible_partition_count": len(rows),
        "incumbent_replay_valid": True,
        "incumbent_rows": incumbent_rows,
        "partitions": rows,
        "all_candidate_witnesses_valid": all(
            all(row["witness"]["checks"].values()) for row in rows
        ),
        "strict_count": len(strict),
        "strict_budget_matched_improvement_exists": bool(strict),
        "best_strict": None if not strict else strict[0],
        "max_imag": float(max_imag),
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-json",
        type=Path,
        default=Path(__file__).with_name("MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json"),
    )
    args = parser.parse_args()

    if set(p10.base.SUBJECTS) != set(FROZEN_OPEN_SUBJECT_BLOBS):
        raise AssertionError({"unexpected_subject_roster": sorted(p10.base.SUBJECTS)})
    for name, cfg in p10.base.SUBJECTS.items():
        if cfg["blob"] != FROZEN_OPEN_SUBJECT_BLOBS[name]:
            raise AssertionError({"unfrozen_subject_source_configured": name})

    hostile = hostile_validation()
    summaries = {name: run_subject(name, cfg) for name, cfg in p10.base.SUBJECTS.items()}

    h4 = summaries["H4"]["strict_budget_matched_improvement_exists"]
    n2 = summaries["N2"]["strict_budget_matched_improvement_exists"]
    if h4 and n2:
        authority = "MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_SUPPORTED__NOT_R6"
        responsibility = "RESP:CIRCUIT_INSTANTIATION_AND_DONOR_NOVELTY_AUDIT_BEFORE_ANY_PROSPECTIVE_FREEZE"
        supported = True
    elif h4 or n2:
        authority = "MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_PARTIAL__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_ONLY"
        supported = False
    else:
        authority = "MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_SHARED_TAG_RANK2_CLOSURE"
        supported = False

    gates = {
        "hostile_dp_vs_brute_exact": hostile["gates"]["dp_vs_brute_all_exact"],
        "r6h_partial_tag_hostile_pass": hostile["gates"]["r6h_partial_tag_hostile_pass"],
        "exact_tare3_hostile_all_exact": hostile["gates"]["exact_tare3_hostile_all_exact"],
        "source_blobs_observed_match": all(row["source_blob_verified"] for row in summaries.values()),
        "frozen_sixterm_batches_complete": all(row["batch_complete"] for row in summaries.values()),
        "exactly_ten_partitions": all(row["partition_count"] == 10 for row in summaries.values()),
        "incumbent_replay_valid": all(row["incumbent_replay_valid"] for row in summaries.values()),
        "all_candidate_witnesses_valid": all(
            row.get("all_candidate_witnesses_valid") is True for row in summaries.values()
        ),
        "strict_budget_matched_point_h4": h4,
        "strict_budget_matched_point_eq_n2": n2,
        "fresh_stretched_n2_unread": True,
    }
    integrity = {
        key: value
        for key, value in gates.items()
        if key not in ("strict_budget_matched_point_h4", "strict_budget_matched_point_eq_n2")
    }
    if not all(integrity.values()):
        raise AssertionError({"R6I_integrity_gate_failure": integrity})
    if supported is not all(gates.values()):
        raise AssertionError("R6I development conjunction bookkeeping mismatch")

    result = {
        "schema": "ORIONQ.MAXR6I.ExactRank2SharedTagDP.v1",
        "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_RANK2_SHARED_TAG_JOINT_DP__NOT_R6",
        "responsibility": responsibility,
        "development_supported": supported,
        "state_count": STATES,
        "config_count_per_partition": CONFIG_COUNT,
        "objective": (
            "C_SHARED = C_Uanti(A) + C_Uanti(B) + 2(w(S0)+w(S1)) + sum_k w(TAk) + sum_k w(TBk); "
            "raw (4,4,4)/central-2 multiplicities, constant-20 subtraction"
        ),
        "incumbent_definition": "min(FRAME_ONLY_STRONG, R6B_REUSE, R6H_PARTIAL_TAG) envelope at Lambda<=candidate+1e-12",
        "concurrent_lane_clause": (
            "any stronger positive R6F/R6G incumbent frozen pre-outcome must be absorbed and "
            "replayed against R6I before any prospective promotion"
        ),
        "subjects": summaries,
        "hostile": hostile,
        "gates": gates,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
        "fresh_r6_subject_coefficients_accessed": False,
    }
    args.results_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        "ORIONQ_MAX_R6I_EXACT_RANK2_SHARED_TAG="
        + json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    )
    return result


if __name__ == "__main__":
    main()
