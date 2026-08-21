#!/usr/bin/env python3
"""MAX-R6K exact rank-2 shared-Tag / Restore-factor joint DP.

Frozen by development/orion-q-max-r0/MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_PROTOCOL.md.

Inherited frozen machinery:
- MAX_R6_EXACT_TARE3_JOINT_FRAME_DP_PROTOCOL.md + errata 1-3 (exact Uanti
  parity-support accounting, deterministic tie-break discipline);
- MAX_R6J_PARTIAL_RESTORE_FACTOR_DONOR_PROTOCOL.md (donor-owned branchwise
  Restore common-factor rule, embedded here INSIDE the joint exact objective);
- MAX_R6H_PARTIAL_TAG_SHARING_DONOR_PROTOCOL.md (common-Tag machinery);
- MAX_R6B_TARE_TRANSFORMATION_REUSE_DONOR_ABSORPTION_PROTOCOL.md (frozen
  six-term batch loading and signed Hermitian Pauli phase algebra).

Uses only already-open H4 and equilibrium-N2 evidence through the frozen R6B
six-term batch loader. It must never read the protected stretched-N2
prospective discriminator. A positive result remains below R6: the common-Tag
and common-Restore-factor circuit identities are donor-owned with zero novelty
credit; only the residual exact coupled representation optimization is tested.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6b_tare_transformation_reuse_donor as reuse
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6j_partial_restore_factor_donor as r6j

TOL = 1e-12
INF = 10**12
LOCAL_INF = 10**9
PARITY_STATES = 1024
UANTI_CONSTANT_TWO_BLOCKS = 20
PROTOCOL_PATH = (
    "development/orion-q-max-r0/"
    "MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_PROTOCOL.md"
)

XOR1024 = np.bitwise_xor(
    np.arange(PARITY_STATES, dtype=np.int32)[:, None],
    np.arange(PARITY_STATES, dtype=np.int32)[None, :],
)

# ---------------------------------------------------------------------------
# Frozen local option enumeration.  The base-4 option code orders the six
# local Pauli letters exactly as (rA0, rA1, rB0, rB1, s0, s1); the array index
# IS the option code, so ascending-index scans realize the protocol tie-break.
# ---------------------------------------------------------------------------
_MUL4 = np.array(
    [[p10.h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64
)
_SYMP4 = np.array(
    [[p10.h.local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int64
)
_WT4 = np.array([p10.h.local_wt(a) for a in range(4)], dtype=np.int64)
# Donor-owned R6J branchwise factor rule: one common support unit for equal
# non-identity local Restore letters, otherwise both residual units.
_F44 = np.array(
    [
        [
            1 if (a == b and a != 0) else p10.h.local_wt(a) + p10.h.local_wt(b)
            for b in range(4)
        ]
        for a in range(4)
    ],
    dtype=np.int64,
)

_OPT = np.arange(4096)
_RA0 = (_OPT >> 10) & 3
_RA1 = (_OPT >> 8) & 3
_RB0 = (_OPT >> 6) & 3
_RB1 = (_OPT >> 4) & 3
_S0 = (_OPT >> 2) & 3
_S1 = _OPT & 3
_RA2 = _MUL4[_RA0, _RA1]
_RB2 = _MUL4[_RB0, _RB1]

# Frozen 10-bit parity delta, protocol bit order 1..10 -> bit index 0..9.
_DELTA = (
    (_SYMP4[_RA0, _RA1] << 0)
    | (_SYMP4[_RB0, _RB1] << 1)
    | ((_SYMP4[_S0, _RA0] ^ _SYMP4[_S0, _RB0]) << 2)
    | ((_SYMP4[_S1, _RA0] ^ _SYMP4[_S1, _RB0]) << 3)
    | ((_SYMP4[_S0, _RA1] ^ _SYMP4[_S0, _RB1]) << 4)
    | ((_SYMP4[_S1, _RA1] ^ _SYMP4[_S1, _RB1]) << 5)
    | (_SYMP4[_S0, _RA0] << 6)
    | (_SYMP4[_S1, _RA0] << 7)
    | (_SYMP4[_S0, _RA1] << 8)
    | (_SYMP4[_S1, _RA1] << 9)
).astype(np.int64)

_TAG_RAW = 2 * (_WT4[_S0] + _WT4[_S1])
_FRAME_RAW = {}
for _ca in range(3):
    _multa = [4, 4, 4]
    _multa[_ca] = 2
    for _cb in range(3):
        _multb = [4, 4, 4]
        _multb[_cb] = 2
        _FRAME_RAW[(_ca, _cb)] = (
            _multa[0] * _WT4[_RA0]
            + _multa[1] * _WT4[_RA1]
            + _multa[2] * _WT4[_RA2]
            + _multb[0] * _WT4[_RB0]
            + _multb[1] * _WT4[_RB1]
            + _multb[2] * _WT4[_RB2]
            + _TAG_RAW
        ).astype(np.int64)


def _labels_from_parity(parity: int) -> tuple[int, int]:
    c0 = 2 * ((parity >> 6) & 1) + ((parity >> 7) & 1)
    c1 = 2 * ((parity >> 8) & 1) + ((parity >> 9) & 1)
    return c0, c1


def _accepting(parity: int) -> bool:
    if parity & 0b11 != 0b11:
        return False
    if (parity >> 2) & 0b1111 != 0:
        return False
    c0, c1 = _labels_from_parity(parity)
    return c0 != 0 and c1 != 0 and c0 != c1


ACCEPT_STATES = tuple(
    parity for parity in range(PARITY_STATES) if _accepting(parity)
)
if len(ACCEPT_STATES) != 6:
    raise AssertionError({"accepting_state_count_not_six": ACCEPT_STATES})


@lru_cache(maxsize=None)
def _local_table(
    pa0: int, pa1: int, pa2: int, pb0: int, pb1: int, pb2: int, ca: int, cb: int
):
    """Exact local table over all 4096 option codes for one qubit.

    Local raw cost = both blocks' frame multiplicities + shared Tag pair paid
    twice + the R6J-factored local Restore support for the three branches.
    Per delta keep the minimum raw cost, tie-broken by the base-4 option code
    (ascending index order via the stable sort).
    """
    factored = (
        _F44[_MUL4[pa0, _RA0], _MUL4[pb0, _RB0]]
        + _F44[_MUL4[pa1, _RA1], _MUL4[pb1, _RB1]]
        + _F44[_MUL4[pa2, _RA2], _MUL4[pb2, _RB2]]
    )
    cost = _FRAME_RAW[(ca, cb)] + factored
    order = np.argsort(cost, kind="stable")
    deltas_sorted = _DELTA[order]
    finite, first = np.unique(deltas_sorted, return_index=True)
    selected = order[first]
    full = np.full(PARITY_STATES, LOCAL_INF, dtype=np.int32)
    choice = np.full(PARITY_STATES, -1, dtype=np.int16)
    full[finite] = cost[selected]
    choice[finite] = selected
    return full, choice, finite.astype(np.int16), cost[selected].astype(np.int64)


def _advance(dp: np.ndarray, finite: np.ndarray, finite_costs: np.ndarray):
    return (dp[XOR1024[:, finite]] + finite_costs[None, :]).min(axis=1)


def _solve_fixed(codes_a, codes_b, permutation, central_a, central_b, n: int):
    dp = np.full(PARITY_STATES, INF, dtype=np.int64)
    dp[0] = 0
    histories = [dp.copy()]
    tables = []
    for q in range(n):
        table = _local_table(
            codes_a[0][q],
            codes_a[1][q],
            codes_a[2][q],
            codes_b[permutation[0]][q],
            codes_b[permutation[1]][q],
            codes_b[permutation[2]][q],
            central_a,
            central_b,
        )
        dp = _advance(dp, table[2], table[3])
        histories.append(dp.copy())
        tables.append(table)
    best = None
    for state in ACCEPT_STATES:
        raw = int(dp[state])
        if raw >= INF:
            continue
        key = (
            raw - UANTI_CONSTANT_TWO_BLOCKS,
            tuple(permutation),
            central_a,
            central_b,
            state,
        )
        if best is None or key < best:
            best = key
    return best, histories, tables


def _backtrack(histories, tables, final_state: int, n: int):
    """Frozen backtrack tie rule: local option code, then predecessor state."""
    parity = final_state
    sequences = [[0] * n for _ in range(6)]
    states = np.arange(PARITY_STATES)
    for q in range(n - 1, -1, -1):
        full, choice, _finite, _costs = tables[q]
        previous = histories[q]
        current_cost = int(histories[q + 1][parity])
        deltas = states ^ parity
        local = full[deltas].astype(np.int64)
        ok = (previous < INF) & (local < LOCAL_INF) & (previous + local == current_cost)
        if not bool(ok.any()):
            raise AssertionError({"r6k_backtrack_failed": {"q": q, "state": parity}})
        codes_ok = choice[deltas][ok]
        states_ok = states[ok]
        pick = np.lexsort((states_ok, codes_ok))[0]
        code = int(codes_ok[pick])
        parity = int(states_ok[pick])
        values = (
            (code >> 10) & 3,
            (code >> 8) & 3,
            (code >> 6) & 3,
            (code >> 4) & 3,
            (code >> 2) & 3,
            code & 3,
        )
        for i, value in enumerate(values):
            sequences[i][q] = value
    if parity != 0:
        raise AssertionError("r6k backtrack did not return to zero parity state")
    return tuple(p10.key_from_codes(sequence) for sequence in sequences)


def _witness(targets_a, targets_b, n, permutation, central_a, central_b, letters, cost):
    ra0, ra1, rb0, rb1, s0, s1 = letters
    rsa = (ra0, ra1, p10.mul(ra0, ra1))
    rsb = (rb0, rb1, p10.mul(rb0, rb1))
    labels_a = tuple(2 * p10.symp(s0, r) + p10.symp(s1, r) for r in rsa)
    labels_b = tuple(2 * p10.symp(s0, r) + p10.symp(s1, r) for r in rsb)
    permuted_b = tuple(targets_b[permutation[k]] for k in range(3))
    ta = tuple(p10.mul(targets_a[k], rsa[k]) for k in range(3))
    tb = tuple(p10.mul(permuted_b[k], rsb[k]) for k in range(3))
    phases_a = tuple(reuse.correction_phase(targets_a[k], rsa[k], ta[k], n) for k in range(3))
    phases_b = tuple(reuse.correction_phase(permuted_b[k], rsb[k], tb[k], n) for k in range(3))
    branches = [
        r6j.factor_restore_pair((phases_a[k], ta[k]), (phases_b[k], tb[k]), n)
        for k in range(3)
    ]
    uanti_a = int(p10.uanti_support(rsa, central_a))
    uanti_b = int(p10.uanti_support(rsb, central_b))
    tag = int(2 * (p10.wt(s0) + p10.wt(s1)))
    factored = int(sum(row["support"] for row in branches))
    recomputed = uanti_a + uanti_b + tag + factored
    checks = {
        "rank2_A": rsa[2] == p10.mul(rsa[0], rsa[1]) and p10.symp(rsa[0], rsa[1]) == 1,
        "rank2_B": rsb[2] == p10.mul(rsb[0], rsb[1]) and p10.symp(rsb[0], rsb[1]) == 1,
        "pairwise_anti_A": p10.is_pairwise_anti(rsa),
        "pairwise_anti_B": p10.is_pairwise_anti(rsb),
        "labels_equal_blocks": labels_a == labels_b,
        "labels_hit_all_nonzero": sorted(labels_a) == [1, 2, 3],
        "target_identity_A": all(p10.mul(ta[k], rsa[k]) == targets_a[k] for k in range(3)),
        "target_identity_B": all(p10.mul(tb[k], rsb[k]) == permuted_b[k] for k in range(3)),
        "branch_factor_checks": all(all(row["checks"].values()) for row in branches),
        "cost_recomputed": recomputed == int(cost),
    }
    if not all(checks.values()):
        raise AssertionError({"r6k_witness_failed": checks})
    return {
        "R_A": [list(r) for r in rsa],
        "R_B": [list(r) for r in rsb],
        "S": [list(s0), list(s1)],
        "labels": list(labels_a),
        "relative_B_target_permutation": list(permutation),
        "central_A": int(central_a),
        "central_B": int(central_b),
        "signed_T_A": [{"phase": int(phases_a[k]), "T": list(ta[k])} for k in range(3)],
        "signed_T_B": [{"phase": int(phases_b[k]), "T": list(tb[k])} for k in range(3)],
        "branches": branches,
        "uanti_support_A": uanti_a,
        "uanti_support_B": uanti_b,
        "tag_support_twice_shared": tag,
        "factored_restore_support": factored,
        "C_R6K": int(cost),
        "checks": checks,
    }


def exact_r6k_joint(targets_a, targets_b, n: int) -> dict[str, Any]:
    """Exact joint optimum over the frozen R6K rank-2 shared-Tag grammar.

    Block A target order is frozen to source-index order; all six relative B
    permutations and both independent central Uanti branches are enumerated.
    Global tie break: total cost, relative B target permutation, central A,
    central B, final state (realized by ascending enumeration order).
    """
    codes_a = tuple(p10.codes(tuple(t), n) for t in targets_a)
    codes_b = tuple(p10.codes(tuple(t), n) for t in targets_b)
    best = None
    payload = None
    for permutation in itertools.permutations(range(3)):
        for central_a in range(3):
            for central_b in range(3):
                candidate, histories, tables = _solve_fixed(
                    codes_a, codes_b, permutation, central_a, central_b, n
                )
                if candidate is None:
                    continue
                if best is None or candidate < best:
                    best = candidate
                    payload = (histories, tables)
    if best is None:
        raise AssertionError("exact R6K joint DP produced no accepting state")
    cost, permutation, central_a, central_b, state = best
    letters = _backtrack(payload[0], payload[1], state, n)
    witness = _witness(
        tuple(tuple(t) for t in targets_a),
        tuple(tuple(t) for t in targets_b),
        n,
        tuple(permutation),
        central_a,
        central_b,
        letters,
        int(cost),
    )
    witness["final_parity_state"] = int(state)
    return witness


# ---------------------------------------------------------------------------
# Independent witness verification (mandatory post-solve proof gate).
# ---------------------------------------------------------------------------


def verify_witness(witness: dict[str, Any], targets_a, targets_b, n: int) -> dict[str, bool]:
    rsa = tuple(tuple(int(v) for v in r) for r in witness["R_A"])
    rsb = tuple(tuple(int(v) for v in r) for r in witness["R_B"])
    s0, s1 = (tuple(int(v) for v in s) for s in witness["S"])
    labels = tuple(int(x) for x in witness["labels"])
    permutation = tuple(int(x) for x in witness["relative_B_target_permutation"])
    central_a = int(witness["central_A"])
    central_b = int(witness["central_B"])
    ta = tuple(tuple(int(v) for v in row["T"]) for row in witness["signed_T_A"])
    tb = tuple(tuple(int(v) for v in row["T"]) for row in witness["signed_T_B"])
    phases_a = tuple(int(row["phase"]) for row in witness["signed_T_A"])
    phases_b = tuple(int(row["phase"]) for row in witness["signed_T_B"])
    branches = witness["branches"]
    permuted_b = tuple(tuple(targets_b[permutation[k]]) for k in range(3))
    checks: dict[str, bool] = {}
    checks["rank2_dependency"] = (
        rsa[2] == p10.mul(rsa[0], rsa[1]) and rsb[2] == p10.mul(rsb[0], rsb[1])
    )
    checks["basis_anticommutation"] = (
        p10.symp(rsa[0], rsa[1]) == 1 and p10.symp(rsb[0], rsb[1]) == 1
    )
    checks["pairwise_anticommutation"] = p10.is_pairwise_anti(rsa) and p10.is_pairwise_anti(rsb)
    got_a = tuple(2 * p10.symp(s0, r) + p10.symp(s1, r) for r in rsa)
    got_b = tuple(2 * p10.symp(s0, r) + p10.symp(s1, r) for r in rsb)
    checks["label_equality"] = got_a == labels and got_b == labels
    checks["label_distinct_nonzero"] = sorted(labels) == [1, 2, 3]
    checks["permutation_valid"] = sorted(permutation) == [0, 1, 2]
    target_ok = True
    phase_ok = True
    for k in range(3):
        got_pa, exp_a = reuse.mul_phase(ta[k], rsa[k], n)
        got_pb, exp_b = reuse.mul_phase(tb[k], rsb[k], n)
        target_ok = target_ok and got_pa == tuple(targets_a[k]) and got_pb == permuted_b[k]
        phase_ok = (
            phase_ok
            and (phases_a[k] + exp_a) % 4 == 0
            and (phases_b[k] + exp_b) % 4 == 0
        )
    checks["target_identity"] = target_ok
    checks["restore_phase_identity"] = phase_ok
    factor_ok = True
    support_ok = True
    residual_phase_ok = True
    factored_total = 0
    for k, row in enumerate(branches):
        g = tuple(int(v) for v in row["G"])
        ua = tuple(int(v) for v in row["U_A"])
        ub = tuple(int(v) for v in row["U_B"])
        expected_g = (0, 0)
        local_sum = 0
        for q in range(n):
            la = ((ta[k][0] >> q) & 1, (ta[k][1] >> q) & 1)
            lb = ((tb[k][0] >> q) & 1, (tb[k][1] >> q) & 1)
            if la == lb and la != (0, 0):
                expected_g = (expected_g[0] | (la[0] << q), expected_g[1] | (la[1] << q))
                local_sum += 1
            else:
                local_sum += (la[0] | la[1]) + (lb[0] | lb[1])
        factor_ok = (
            factor_ok
            and g == expected_g
            and ua == p10.mul(g, ta[k])
            and ub == p10.mul(g, tb[k])
        )
        support_ok = (
            support_ok
            and int(row["support"]) == p10.wt(g) + p10.wt(ua) + p10.wt(ub) == local_sum
        )
        back_a, ga = reuse.mul_phase(g, ua, n)
        back_b, gb = reuse.mul_phase(g, ub, n)
        residual_phase_ok = (
            residual_phase_ok
            and back_a == ta[k]
            and back_b == tb[k]
            and (int(row["residual_phase_A"]) + ga) % 4 == phases_a[k]
            and (int(row["residual_phase_B"]) + gb) % 4 == phases_b[k]
        )
        factored_total += int(row["support"])
    checks["r6j_common_factor_rule"] = factor_ok
    checks["r6j_factor_support"] = support_ok
    checks["r6j_residual_phase_identity"] = residual_phase_ok
    uanti_a = int(p10.uanti_support(rsa, central_a))
    uanti_b = int(p10.uanti_support(rsb, central_b))
    tag = 2 * (p10.wt(s0) + p10.wt(s1))
    checks["uanti_recomputed"] = (
        uanti_a == int(witness["uanti_support_A"]) and uanti_b == int(witness["uanti_support_B"])
    )
    checks["tag_recomputed"] = tag == int(witness["tag_support_twice_shared"])
    checks["factored_recomputed"] = factored_total == int(witness["factored_restore_support"])
    checks["cost_recomputed"] = (
        uanti_a + uanti_b + tag + factored_total == int(witness["C_R6K"])
    )
    return checks


# ---------------------------------------------------------------------------
# Structurally independent brute-force over the identical frozen grammar.
# ---------------------------------------------------------------------------


def brute_r6k_cost(targets_a, targets_b, n: int, fixed=None) -> int:
    """Global enumeration over the identical frozen grammar.

    With ``fixed=(permutation, central_a, central_b)`` the scan restricts to
    one relative B target permutation and one central pair, so the hostile
    panel can bind the DP to brute force separately for every configuration.
    """
    limit = 1 << n
    keys = [(x, z) for x in range(limit) for z in range(limit)]
    nonid = [k for k in keys if k != (0, 0)]
    pairs = [
        (r0, r1)
        for r0 in nonid
        for r1 in nonid
        if p10.symp(r0, r1) == 1
    ]
    factor_support = {}
    for a in keys:
        for b in keys:
            total = 0
            for q in range(n):
                la = ((a[0] >> q) & 1, (a[1] >> q) & 1)
                lb = ((b[0] >> q) & 1, (b[1] >> q) & 1)
                if la == lb and la != (0, 0):
                    total += 1
                else:
                    total += (la[0] | la[1]) + (lb[0] | lb[1])
            factor_support[(a, b)] = total

    def frame(pair):
        return (pair[0], pair[1], p10.mul(pair[0], pair[1]))

    if fixed is None:
        perms = tuple(itertools.permutations(range(3)))
        centrals_a = centrals_b = (0, 1, 2)
    else:
        perms = (tuple(int(x) for x in fixed[0]),)
        centrals_a = (int(fixed[1]),)
        centrals_b = (int(fixed[2]),)
    uanti_a = {
        pair: min(p10.uanti_support(frame(pair), central) for central in centrals_a)
        for pair in pairs
    }
    uanti_b = {
        pair: min(p10.uanti_support(frame(pair), central) for central in centrals_b)
        for pair in pairs
    }
    ta_by_pair = {
        pair: tuple(p10.mul(tuple(targets_a[k]), frame(pair)[k]) for k in range(3))
        for pair in pairs
    }
    tb_matrix_by_pair = {
        pair: tuple(
            tuple(p10.mul(tuple(targets_b[j]), frame(pair)[k]) for k in range(3))
            for j in range(3)
        )
        for pair in pairs
    }
    best = INF
    for s0 in keys:
        for s1 in keys:
            tag = 2 * (p10.wt(s0) + p10.wt(s1))
            if tag >= best:
                continue
            label = {
                r: 2 * p10.symp(s0, r) + p10.symp(s1, r) for r in nonid
            }
            grouped: dict[tuple[int, int], list] = {}
            for pair in pairs:
                c0, c1 = label[pair[0]], label[pair[1]]
                if c0 == 0 or c1 == 0 or c0 == c1:
                    continue
                grouped.setdefault((c0, c1), []).append(pair)
            for pool in grouped.values():
                for pair_a in pool:
                    base = tag + uanti_a[pair_a]
                    if base >= best:
                        continue
                    ta = ta_by_pair[pair_a]
                    for pair_b in pool:
                        partial = base + uanti_b[pair_b]
                        if partial >= best:
                            continue
                        matrix = tb_matrix_by_pair[pair_b]
                        restore = min(
                            factor_support[(ta[0], matrix[perm[0]][0])]
                            + factor_support[(ta[1], matrix[perm[1]][1])]
                            + factor_support[(ta[2], matrix[perm[2]][2])]
                            for perm in perms
                        )
                        total = partial + restore
                        if total < best:
                            best = total
    if best >= INF:
        raise AssertionError("brute R6K solver produced no admissible configuration")
    return int(best)


HOSTILE_PANELS = {
    # Deterministic synthetic two-block target pairs; no chemistry content and
    # no protected-subject content.  (x,z) integer bit-mask Pauli keys.
    "n1_a": (1, ((1, 0), (1, 1), (0, 1)), ((0, 1), (1, 0), (1, 1))),
    "n1_b": (1, ((1, 0), (1, 0), (0, 1)), ((1, 1), (0, 1), (0, 1))),
    "n1_c": (1, ((0, 1), (0, 1), (0, 1)), ((1, 0), (1, 1), (0, 1))),
    "n2_a": (
        2,
        ((0b01, 0b00), (0b00, 0b10), (0b11, 0b01)),
        ((0b10, 0b01), (0b01, 0b11), (0b11, 0b10)),
    ),
    "n2_b": (
        2,
        ((0b10, 0b01), (0b01, 0b11), (0b11, 0b10)),
        ((0b01, 0b00), (0b00, 0b10), (0b11, 0b01)),
    ),
    "n2_c": (
        2,
        ((0b11, 0b00), (0b00, 0b11), (0b11, 0b11)),
        ((0b11, 0b00), (0b00, 0b11), (0b11, 0b11)),
    ),
    "n2_d": (
        2,
        ((0b01, 0b10), (0b10, 0b10), (0b11, 0b01)),
        ((0b10, 0b11), (0b01, 0b01), (0b01, 0b11)),
    ),
}


# Panels whose 6 x 3 x 3 fixed-(permutation, central A, central B) sub-problems
# are each independently bound to a restricted brute force, so the hostile
# equality explicitly includes different relative target permutations and
# different central choices, not only the global optimum path.
PER_CONFIG_PANELS = ("n1_a", "n1_b", "n2_a", "n2_d")


def _fixed_config_cost(targets_a, targets_b, n, permutation, central_a, central_b):
    codes_a = tuple(p10.codes(tuple(t), n) for t in targets_a)
    codes_b = tuple(p10.codes(tuple(t), n) for t in targets_b)
    candidate, _histories, _tables = _solve_fixed(
        codes_a, codes_b, tuple(permutation), central_a, central_b, n
    )
    if candidate is None:
        raise AssertionError("fixed-configuration R6K DP produced no accepting state")
    return int(candidate[0])


def hostile_validation() -> dict[str, Any]:
    inherited_tare3 = exact.hostile_exactness()
    inherited_r6j = r6j.hostile_validation()
    panels = {}
    seen_permutations = set()
    for name, (n, targets_a, targets_b) in sorted(HOSTILE_PANELS.items()):
        joint = exact_r6k_joint(targets_a, targets_b, n)
        verification = verify_witness(joint, targets_a, targets_b, n)
        brute = brute_r6k_cost(targets_a, targets_b, n)
        passed = (
            joint["C_R6K"] == brute
            and all(joint["checks"].values())
            and all(verification.values())
        )
        seen_permutations.add(tuple(joint["relative_B_target_permutation"]))
        per_config = None
        if name in PER_CONFIG_PANELS:
            mismatches = 0
            checked = 0
            for permutation in itertools.permutations(range(3)):
                for central_a in range(3):
                    for central_b in range(3):
                        checked += 1
                        dp_cost = _fixed_config_cost(
                            targets_a, targets_b, n, permutation, central_a, central_b
                        )
                        brute_cost = brute_r6k_cost(
                            targets_a, targets_b, n,
                            fixed=(permutation, central_a, central_b),
                        )
                        if dp_cost != brute_cost:
                            mismatches += 1
            per_config = {"configurations": checked, "mismatches": mismatches}
            passed = passed and checked == 54 and mismatches == 0
        panels[name] = {
            "n": n,
            "dp_cost": int(joint["C_R6K"]),
            "brute_cost": int(brute),
            "relative_B_target_permutation": joint["relative_B_target_permutation"],
            "central_A": joint["central_A"],
            "central_B": joint["central_B"],
            "per_configuration_equality": per_config,
            "witness_checks_pass": all(joint["checks"].values()),
            "independent_verification_pass": all(verification.values()),
            "pass": passed,
        }
        if not passed:
            raise AssertionError({"r6k_hostile_exactness_failed": name, **panels[name]})
    gates = {
        "dp_vs_brute_exact": all(row["pass"] for row in panels.values()),
        "per_configuration_dp_vs_brute_exact": all(
            row["per_configuration_equality"] is not None
            and row["per_configuration_equality"]["configurations"] == 54
            and row["per_configuration_equality"]["mismatches"] == 0
            for row in panels.values()
            if row["per_configuration_equality"] is not None
        )
        and any(row["per_configuration_equality"] is not None for row in panels.values()),
        "distinct_relative_permutations_exercised": len(seen_permutations) >= 2,
        "inherited_exact_tare3_hostile_pass": inherited_tare3["all_exact"] is True,
        "inherited_r6j_factor_phase_hostile_pass": inherited_r6j["all_pass"] is True,
    }
    if not all(gates.values()):
        raise AssertionError({"r6k_hostile_failure": gates})
    return {
        "panels": panels,
        "observed_optimal_permutations": sorted(list(p) for p in seen_permutations),
        "per_configuration_panels": list(PER_CONFIG_PANELS),
        "inherited_exact_tare3": inherited_tare3["panels"],
        "inherited_r6j_gates": inherited_r6j["gates"],
        "gates": gates,
        "all_pass": True,
        "brute_solver": (
            "global Pauli-string enumeration over (RA0,RA1,RB0,RB1,S0,S1) with "
            "label grouping, central minimization and permutation scan; "
            "additionally restricted per fixed (permutation, central A, central B)"
        ),
    }


# ---------------------------------------------------------------------------
# Frozen chemistry evaluation.
# ---------------------------------------------------------------------------


def _lambda(terms, triple) -> float:
    return float((3.0 * sum(float(terms[i][1]) ** 2 for i in triple)) ** 0.5)


def _incumbent_stack(terms, source_indices, n: int):
    """Full absorbed donor stack: frame-only, R6B reuse, R6H, R6J per partition."""
    r6d_eval, base_rows = r6j._incumbent_rows(terms, source_indices, n)
    rows = []
    for row in base_rows:
        a = tuple(int(x) for x in row["partition"][0])
        b = tuple(int(x) for x in row["partition"][1])
        candidate = r6j.best_restore_factor(r6j._block(terms, a), r6j._block(terms, b), n)
        best = candidate["best"]
        c_r6j = None if best is None else int(best["C_restore_factor"])
        known = {"FRAME_ONLY": int(row["C_frame_only"])}
        if row.get("C_reuse") is not None:
            known["R6B_REUSE"] = int(row["C_reuse"])
        if row.get("C_R6H") is not None:
            known["R6H_PARTIAL_TAG"] = int(row["C_R6H"])
        if c_r6j is not None:
            known["R6J_RESTORE_FACTOR"] = c_r6j
        incumbent = min(known.values())
        source = min(name for name, value in known.items() if value == incumbent)
        rows.append(
            {
                "partition": row["partition"],
                "Lambda_batch": float(row["Lambda_batch"]),
                "C_frame_only": int(row["C_frame_only"]),
                "C_reuse": row.get("C_reuse"),
                "C_R6H": row.get("C_R6H"),
                "C_R6J": c_r6j,
                "C_incumbent": int(incumbent),
                "incumbent_source": source,
                "r6j_witness_checks_pass": best is None or all(best["checks"].values()),
            }
        )
    replay_pass = (
        len(r6d_eval.get("all_partitions", [])) == 10
        and r6d_eval.get("all_witnesses_valid") is True
        and all(row["r6j_witness_checks_pass"] for row in rows)
    )
    return r6d_eval, rows, replay_pass


def _envelope(rows, lam: float):
    eligible = [row for row in rows if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"r6k_empty_incumbent_envelope": lam})
    best = min(
        eligible,
        key=lambda row: (int(row["C_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )
    return int(best["C_incumbent"]), best


def run_subject(name: str, cfg) -> dict[str, Any]:
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    base_summary = {
        "subject": name,
        "source_blob_expected": cfg["blob"],
        "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"],
        "n_qubits": n,
        "max_imag": float(max_imag),
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": list(source_indices),
    }
    if len(source_indices) != 6:
        return {
            **base_summary,
            "batch_complete": False,
            "partition_count": 0,
            "eligible_partition_count": 0,
            "incumbent_replay_pass": False,
            "all_witnesses_independently_verified": False,
            "strict_count": 0,
            "strict_budget_matched_improvement_exists": False,
            "best_strict": None,
            "partitions": [],
            "incumbent_rows": [],
        }

    r6d_eval, incumbent_rows, replay_pass = _incumbent_stack(terms, source_indices, n)
    rows = []
    all_verified = True
    for partition in r6d_eval["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        targets_a = tuple(terms[i][0] for i in a)
        targets_b = tuple(terms[i][0] for i in b)
        witness = exact_r6k_joint(targets_a, targets_b, n)
        verification = verify_witness(witness, targets_a, targets_b, n)
        verified = all(verification.values())
        all_verified = all_verified and verified
        if not verified:
            raise AssertionError(
                {"r6k_independent_verification_failed": [list(a), list(b)], "checks": verification}
            )
        lam = float(_lambda(terms, a) + _lambda(terms, b))
        incumbent, incumbent_witness = _envelope(incumbent_rows, lam)
        cost = int(witness["C_R6K"])
        delta = int(incumbent - cost)
        rows.append(
            {
                "partition": [list(a), list(b)],
                "Lambda_batch": lam,
                "C_R6K": cost,
                "witness": witness,
                "independent_verification": verification,
                "independently_verified": verified,
                "C_incumbent_envelope": int(incumbent),
                "incumbent_envelope_witness": incumbent_witness,
                "delta_vs_incumbent": delta,
                "strict_budget_matched_improvement": delta > 0,
            }
        )
    strict = sorted(
        (row for row in rows if row["strict_budget_matched_improvement"]),
        key=lambda row: (-int(row["delta_vs_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )
    return {
        **base_summary,
        "batch_complete": True,
        "partition_count": len(r6d_eval["all_partitions"]),
        "eligible_partition_count": len(rows),
        "incumbent_replay_pass": replay_pass,
        "all_witnesses_independently_verified": all_verified and bool(rows),
        "strict_count": len(strict),
        "strict_budget_matched_improvement_exists": bool(strict),
        "best_strict": None if not strict else {
            "partition": strict[0]["partition"],
            "Lambda_batch": strict[0]["Lambda_batch"],
            "C_R6K": strict[0]["C_R6K"],
            "C_incumbent_envelope": strict[0]["C_incumbent_envelope"],
            "delta_vs_incumbent": strict[0]["delta_vs_incumbent"],
        },
        "partitions": rows,
        "incumbent_rows": incumbent_rows,
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-json",
        type=Path,
        default=Path(__file__).with_name(
            "MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_RESULTS.json"
        ),
    )
    args = parser.parse_args()
    started = time.time()
    hostile = hostile_validation()
    subjects = {name: run_subject(name, cfg) for name, cfg in p10.base.SUBJECTS.items()}
    h4 = subjects["H4"]["strict_budget_matched_improvement_exists"]
    n2 = subjects["N2"]["strict_budget_matched_improvement_exists"]

    gates = {
        "hostile_dp_vs_brute_exact": hostile["gates"]["dp_vs_brute_exact"],
        "hostile_per_configuration_dp_vs_brute_exact": hostile["gates"][
            "per_configuration_dp_vs_brute_exact"
        ],
        "hostile_distinct_relative_permutations_exercised": hostile["gates"][
            "distinct_relative_permutations_exercised"
        ],
        "inherited_exact_tare3_hostile_pass": hostile["gates"][
            "inherited_exact_tare3_hostile_pass"
        ],
        "inherited_r6j_factor_phase_hostile_pass": hostile["gates"][
            "inherited_r6j_factor_phase_hostile_pass"
        ],
        "source_blobs_observed_match": all(
            row["source_blob_verified"] for row in subjects.values()
        ),
        "frozen_sixterm_batches_complete": all(
            row["batch_complete"] for row in subjects.values()
        ),
        "exactly_ten_partitions": all(
            row["partition_count"] == 10 for row in subjects.values()
        ),
        "all_strict_witnesses_independently_verified": all(
            row["all_witnesses_independently_verified"] for row in subjects.values()
        ),
        "full_donor_incumbent_replay_pass": all(
            row["incumbent_replay_pass"] for row in subjects.values()
        ),
        "strict_budget_matched_h4": h4,
        "strict_budget_matched_eq_n2": n2,
        "fresh_stretched_n2_unread": True,
    }
    integrity_gates = {
        key: value
        for key, value in gates.items()
        if key not in ("strict_budget_matched_h4", "strict_budget_matched_eq_n2")
    }
    if not all(integrity_gates.values()):
        raise AssertionError({"r6k_integrity_gate_failure": gates})

    supported = all(gates.values())
    if supported:
        authority = "MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_SUPPORTED__NOT_R6"
        responsibility = "RESP:RESIDUAL_COUPLED_OPTIMIZATION_ELIGIBLE_FOR_INSTANTIATION_AND_DONOR_REPLAY"
    elif h4 or n2:
        authority = "MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_PARTIAL__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_SINGLE_SUBJECT_ONLY"
    else:
        authority = "MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR_DP_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_JOINT_TAG_RESTORE_FACTOR_CLOSURE"

    result = {
        "schema": "ORIONQ.MAXR6K.ExactRank2SharedTagRestoreFactorDP.v1",
        "protocol": PROTOCOL_PATH,
        "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_RANK2_SHARED_TAG_RESTORE_FACTOR__NOT_R6",
        "responsibility": responsibility,
        "development_supported": supported,
        "hostile": hostile,
        "subjects": subjects,
        "gates": gates,
        "incumbent_stack": [
            "FRAME_ONLY",
            "R6B_REUSE",
            "R6H_PARTIAL_TAG",
            "R6J_RESTORE_FACTOR",
        ],
        "concurrent_r6f_r6g_stronger_positive_artifact_present": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
        "fresh_r6_subject_coefficients_accessed": False,
        "runtime_seconds": float(round(time.time() - started, 3)),
    }
    print(
        "ORIONQ_MAX_R6K_EXACT_RANK2_SHARED_TAG_RESTORE_FACTOR="
        + json.dumps(result, sort_keys=True)
    )
    if args.results_json is not None:
        args.results_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    main()
