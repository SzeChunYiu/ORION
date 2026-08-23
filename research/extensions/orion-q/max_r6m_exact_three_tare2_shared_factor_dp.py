#!/usr/bin/env python3
"""MAX-R6M exact three-TARE2 shared-Tag / Restore-factor joint DP.

Frozen by:
- MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_PROTOCOL.md
- MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_PROTOCOL.md (donor-owned factor rule)
- MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_ERRATUM_1.md (conservative comparator)

Jointly optimizes three arbitrary anticommuting TARE-M2 auxiliary frames, one
common one-bit Tag and the donor-owned all-three Restore common factor in one
exact 9-bit XOR DP over the frozen R6B six-term batches of the already-open H4
and equilibrium-N2 subjects. The protected stretched-N2 discriminator remains
unread. A positive result is open-subject method development only; it is not
R6 and carries no novelty authority.
"""
from __future__ import annotations

import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6b_tare_transformation_reuse_donor as reuse
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6h_partial_tag_sharing_donor as r6h
import max_r6j_partial_restore_factor_donor as r6j

TOL = 1e-12
INF = 10 ** 12
PARITY_STATES = 512
OPTIONS = 4 ** 7
ROTATIONS_R6M = 9
ROTATIONS_TWO_M3 = 10
# Nine parity bits, LSB first in protocol order:
# b0=<rA0,rA1>, b1=<rB0,rB1>, b2=<rC0,rC1>,
# b3=<s,rA0>^<s,rB0>, b4=<s,rA0>^<s,rC0>, b5=<s,rA1>^<s,rB1>, b6=<s,rA1>^<s,rC1>,
# b7=<s,rA0>, b8=<s,rA1>.
# Acceptance: b0..b2 all 1, b3..b6 all 0, b7 != b8.
ACCEPTING_STATES = (0b010000111, 0b100000111)  # (135, 263): b7=1,b8=0 and b7=0,b8=1
XOR512 = np.bitwise_xor(
    np.arange(PARITY_STATES)[:, None],
    np.arange(PARITY_STATES)[None, :],
)

# ---- frozen local algebra tables -------------------------------------------
_SY = np.array([[p10.h.local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
_LM = np.array([[p10.h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
_LW = np.array([p10.h.local_wt(a) for a in range(4)], dtype=np.int64)

# Option index i IS the frozen base-4 option code of the ordered local letters
# (rA0, rA1, rB0, rB1, rC0, rC1, s), rA0 most significant.
_DIG = tuple(((np.arange(OPTIONS, dtype=np.int64) >> (2 * (6 - t))) & 3) for t in range(7))
_RA0, _RA1, _RB0, _RB1, _RC0, _RC1, _SS = _DIG
_DELTA = (
    (_SY[_RA0, _RA1] << 0)
    | (_SY[_RB0, _RB1] << 1)
    | (_SY[_RC0, _RC1] << 2)
    | ((_SY[_SS, _RA0] ^ _SY[_SS, _RB0]) << 3)
    | ((_SY[_SS, _RA0] ^ _SY[_SS, _RC0]) << 4)
    | ((_SY[_SS, _RA1] ^ _SY[_SS, _RB1]) << 5)
    | ((_SY[_SS, _RA1] ^ _SY[_SS, _RC1]) << 6)
    | (_SY[_SS, _RA0] << 7)
    | (_SY[_SS, _RA1] << 8)
)
_TAG_COST = 2 * _LW[_SS]
_FRAME_COST = {}
for _centrals in itertools.product((0, 1), repeat=3):
    _cost = np.zeros(OPTIONS, dtype=np.int64)
    for _j, _c in enumerate(_centrals):
        _m0 = 2 if _c == 0 else 4
        _m1 = 2 if _c == 1 else 4
        _cost = _cost + _m0 * _LW[_DIG[2 * _j]] + _m1 * _LW[_DIG[2 * _j + 1]]
    _FRAME_COST[_centrals] = _cost

# Donor-owned all-three factor rule as a local letter-triple cost table.
_F3 = np.zeros((4, 4, 4), dtype=np.int64)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            if _a == _b == _c and _a != 0:
                _F3[_a, _b, _c] = 1
            else:
                _F3[_a, _b, _c] = int(_LW[_a] + _LW[_b] + _LW[_c])


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---- exact 9-bit XOR DP -----------------------------------------------------

@lru_cache(maxsize=None)
def _local_table(p6: tuple[int, ...], centrals: tuple[int, int, int]):
    """Exact local delta -> (min raw cost, option code) table for one qubit.

    Depends only on the six local target letters (after relative permutation)
    and the three central-branch bits; coefficients never enter the structural
    cost, so the table is shared across qubits and matchings.
    """
    factor0 = _F3[_LM[p6[0], _RA0], _LM[p6[2], _RB0], _LM[p6[4], _RC0]]
    factor1 = _F3[_LM[p6[1], _RA1], _LM[p6[3], _RB1], _LM[p6[5], _RC1]]
    cost = _FRAME_COST[centrals] + _TAG_COST + factor0 + factor1
    # Stable sort by cost keeps ascending option code among ties, so the first
    # occurrence per delta realizes the frozen base-4 option-code tie-break.
    order = np.argsort(cost, kind="stable")
    deltas_sorted = _DELTA[order]
    uniq, first = np.unique(deltas_sorted, return_index=True)
    local_cost = np.full(PARITY_STATES, INF, dtype=np.int64)
    local_opt = np.full(PARITY_STATES, -1, dtype=np.int64)
    local_cost[uniq] = cost[order][first]
    local_opt[uniq] = order[first]
    return local_cost, local_opt


def _branch_targets(terms, pairs, perm_b: int, perm_c: int):
    """Six branch targets (PA0,PA1,PB0,PB1,PC0,PC1) after relative permutations.

    Block A keeps its canonical pair order; B and C apply their 2x2 relative
    permutations.
    """
    (a0, a1), (b0, b1), (c0, c1) = pairs
    order_b = (b0, b1) if perm_b == 0 else (b1, b0)
    order_c = (c0, c1) if perm_c == 0 else (c1, c0)
    return (
        terms[a0][0], terms[a1][0],
        terms[order_b[0]][0], terms[order_b[1]][0],
        terms[order_c[0]][0], terms[order_c[1]][0],
    )


def _solve_config(branch_targets, centrals, n: int, keep_history: bool = False):
    codes6 = tuple(p10.codes(target, n) for target in branch_targets)
    dp = np.full(PARITY_STATES, INF, dtype=np.int64)
    dp[0] = 0
    histories = [dp.copy()] if keep_history else None
    tables = [] if keep_history else None
    for q in range(n):
        p6 = tuple(int(codes6[t][q]) for t in range(6))
        cost, opt = _local_table(p6, centrals)
        dp = (dp[:, None] + cost[XOR512]).min(axis=0)
        if keep_history:
            histories.append(dp.copy())
            tables.append((cost, opt))
    return dp, histories, tables


def _backtrack(histories, tables, final_state: int, n: int):
    """Frozen backtracking tie-break: local option code, then predecessor state."""
    parity = int(final_state)
    sequences = [[0] * n for _ in range(7)]
    for q in range(n - 1, -1, -1):
        prev_dp = histories[q]
        current = int(histories[q + 1][parity])
        cost, opt = tables[q]
        candidates = []
        for delta in range(PARITY_STATES):
            local_cost = int(cost[delta])
            if local_cost >= INF:
                continue
            predecessor = parity ^ delta
            predecessor_cost = int(prev_dp[predecessor])
            if predecessor_cost >= INF:
                continue
            if predecessor_cost + local_cost != current:
                continue
            candidates.append((int(opt[delta]), predecessor))
        if not candidates:
            raise AssertionError({"r6m_backtrack_failed_at_qubit": q})
        code, parity = min(candidates)
        for t in range(7):
            sequences[t][q] = (code >> (2 * (6 - t))) & 3
    if parity != 0:
        raise AssertionError("r6m backtrack did not return to zero state")
    return tuple(p10.key_from_codes(sequence) for sequence in sequences)


# ---- donor-owned all-three Restore factoring with exact phases --------------

def factor_restore_triple(signed_a, signed_b, signed_c, n: int) -> dict[str, Any]:
    """R6L all-three common-factor rule with exact Hermitian phase witness."""
    signed = (signed_a, signed_b, signed_c)
    phases = tuple(int(item[0]) for item in signed)
    ts = tuple(tuple(item[1]) for item in signed)
    g = (0, 0)
    matching = 0
    per_qubit = 0
    for q in range(n):
        letters = tuple((((t[0] >> q) & 1), ((t[1] >> q) & 1)) for t in ts)
        if letters[0] != (0, 0) and letters[0] == letters[1] == letters[2]:
            g = (g[0] | (letters[0][0] << q), g[1] | (letters[0][1] << q))
            matching += 1
            per_qubit += 1
        else:
            per_qubit += sum(1 for letter in letters if letter != (0, 0))
    residuals = tuple(p10.mul(g, t) for t in ts)
    exponents = []
    residual_phases = []
    for t, u, phase in zip(ts, residuals, phases):
        got, exponent = reuse.mul_phase(g, u, n)
        if got != t:
            raise AssertionError({"r6m_factor_binary_identity_failed": [list(g), list(u), list(t)]})
        exponents.append(int(exponent))
        residual_phases.append((phase - int(exponent)) % 4)
    support = int(p10.wt(g) + sum(p10.wt(u) for u in residuals))
    formula = int(sum(p10.wt(t) for t in ts) - 2 * matching)
    rec = {
        "G": list(g),
        "U": [list(u) for u in residuals],
        "original_phases": list(phases),
        "G_times_U_phases": exponents,
        "residual_phases": residual_phases,
        "matching_nonidentity_local_letters": matching,
        "support": support,
        "checks": {
            "binary_identities": all(p10.mul(g, u) == t for u, t in zip(residuals, ts)),
            "phase_identities": all(
                (residual_phases[i] + exponents[i]) % 4 == phases[i] for i in range(3)
            ),
            "support_formula": support == formula,
            "per_qubit_rule": support == per_qubit,
        },
    }
    if not all(rec["checks"].values()):
        raise AssertionError({"r6m_factor_witness_failed": rec})
    return rec


def _factor_support_fast(ta, tb, tc) -> int:
    """Support of the factored triple: sum of weights minus 2 per all-same qubit."""
    same = (~(ta[0] ^ tb[0])) & (~(ta[1] ^ tb[1])) & (~(ta[0] ^ tc[0])) & (~(ta[1] ^ tc[1]))
    nonid = ta[0] | ta[1]
    count = (same & nonid).bit_count()
    return int(p10.wt(ta) + p10.wt(tb) + p10.wt(tc) - 2 * count)


# ---- R6M witness ------------------------------------------------------------

def _uanti_m2(frame_pair, central: int) -> int:
    """Frozen M2 raw-frame rule: 4x non-central + 2x central support, minus 6."""
    weights = (p10.wt(frame_pair[0]), p10.wt(frame_pair[1]))
    non_central = 1 - central
    return int(4 * (weights[non_central] - 1) + 2 * (weights[central] - 1))


def _r6m_witness(terms, pairs, n, perm_b, perm_c, centrals, state, keys7, cost, six_indices):
    ra0, ra1, rb0, rb1, rc0, rc1, s = keys7
    frames = ((ra0, ra1), (rb0, rb1), (rc0, rc1))
    branch_targets = _branch_targets(terms, pairs, perm_b, perm_c)
    block_targets = tuple(
        (branch_targets[2 * j], branch_targets[2 * j + 1]) for j in range(3)
    )
    labels = (p10.symp(s, ra0), p10.symp(s, ra1))
    restores = []
    for j in range(3):
        signed = []
        for k in range(2):
            t = p10.mul(block_targets[j][k], frames[j][k])
            phase = reuse.correction_phase(block_targets[j][k], frames[j][k], t, n)
            signed.append((int(phase), t))
        restores.append(tuple(signed))
    branch_factors = [
        factor_restore_triple(restores[0][k], restores[1][k], restores[2][k], n)
        for k in range(2)
    ]
    uanti = [_uanti_m2(frames[j], centrals[j]) for j in range(3)]
    tag = int(2 * p10.wt(s))
    factored = int(sum(row["support"] for row in branch_factors))
    recomputed = int(sum(uanti) + tag + factored)
    covered = sorted(i for pair in pairs for i in pair)
    checks = {
        "anticommuting_frames": all(p10.symp(f[0], f[1]) == 1 for f in frames),
        "common_labels_all_blocks": all(
            (p10.symp(s, frames[j][0]), p10.symp(s, frames[j][1])) == labels
            for j in range(3)
        ),
        "distinct_branch_labels": labels[0] != labels[1],
        "state_matches_labels": state in ACCEPTING_STATES
        and ((state >> 7) & 1) == labels[0]
        and ((state >> 8) & 1) == labels[1],
        "restore_identities": all(
            p10.mul(restores[j][k][1], frames[j][k]) == block_targets[j][k]
            for j in range(3)
            for k in range(2)
        ),
        "restore_phases": all(
            reuse.correction_phase(
                block_targets[j][k], frames[j][k], restores[j][k][1], n
            )
            == restores[j][k][0]
            for j in range(3)
            for k in range(2)
        ),
        "factor_checks": all(
            all(row["checks"].values()) for row in branch_factors
        ),
        "six_term_conservation": covered == sorted(six_indices),
        "cost_recomputed": recomputed == int(cost),
        "rotation_count_nine": ROTATIONS_R6M == 9,
    }
    if not all(checks.values()):
        raise AssertionError({"r6m_witness_failed": checks})
    return {
        "matching": [list(pair) for pair in pairs],
        "relative_permutation_B": int(perm_b),
        "relative_permutation_C": int(perm_c),
        "centrals": list(centrals),
        "final_parity_state": int(state),
        "R": {
            "A": [list(ra0), list(ra1)],
            "B": [list(rb0), list(rb1)],
            "C": [list(rc0), list(rc1)],
        },
        "S": list(s),
        "common_labels": list(labels),
        "targets": {
            block: [list(block_targets[j][0]), list(block_targets[j][1])]
            for j, block in enumerate(("A", "B", "C"))
        },
        "restore": {
            block: [
                {"phase": restores[j][k][0], "T": list(restores[j][k][1])}
                for k in range(2)
            ]
            for j, block in enumerate(("A", "B", "C"))
        },
        "branch_factors": branch_factors,
        "uanti_support": {"A": uanti[0], "B": uanti[1], "C": uanti[2]},
        "tag_support_twice": tag,
        "factored_restore_support": factored,
        "C_R6M": int(cost),
        "rotation_count": ROTATIONS_R6M,
        "checks": checks,
    }


def exact_r6m_matching(terms, pairs, n: int, six_indices) -> dict[str, Any]:
    """Frozen global tie-break: cost, matching, perm B, perm C, centrals, state."""
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            branch_targets = _branch_targets(terms, pairs, perm_b, perm_c)
            for centrals in itertools.product((0, 1), repeat=3):
                dp, _, _ = _solve_config(branch_targets, centrals, n)
                for state in ACCEPTING_STATES:
                    raw = int(dp[state])
                    if raw >= INF:
                        continue
                    key = (raw - 18, pairs, perm_b, perm_c) + centrals + (state,)
                    if best is None or key < best:
                        best = key
    if best is None:
        raise AssertionError({"r6m_dp_no_accepting_state": [list(p) for p in pairs]})
    cost, _, perm_b, perm_c, ca, cb, cc, state = best
    branch_targets = _branch_targets(terms, pairs, perm_b, perm_c)
    dp, histories, tables = _solve_config(branch_targets, (ca, cb, cc), n, keep_history=True)
    if int(dp[state]) - 18 != cost:
        raise AssertionError("r6m re-solve disagrees with recorded optimum")
    keys7 = _backtrack(histories, tables, state, n)
    return _r6m_witness(
        terms, pairs, n, perm_b, perm_c, (ca, cb, cc), state, keys7, int(cost), six_indices
    )


def _dp_config_cost(terms, pairs, perm_b, perm_c, centrals, n: int):
    branch_targets = _branch_targets(terms, pairs, perm_b, perm_c)
    dp, _, _ = _solve_config(branch_targets, centrals, n)
    values = [int(dp[state]) for state in ACCEPTING_STATES if int(dp[state]) < INF]
    return None if not values else min(values) - 18


# ---- R6L weight-one donor (implemented per frozen R6L protocol + Erratum 1) --

def _letter_key(letter: int, q: int):
    bx, bz = p10.h.CODE_BITS[letter]
    return (bx << q, bz << q)


def _m2_weight_one_reps(target_pair, n: int):
    """Complete frozen weight-one ordered TARE-M2 representation grammar."""
    reps = []
    for q in range(n):
        for a, b in itertools.permutations((1, 2, 3), 2):
            r0, r1 = _letter_key(a, q), _letter_key(b, q)
            if p10.symp(r0, r1) != 1:
                raise AssertionError("weight-one M2 frame pair is not anticommuting")
            for labels in ((0, 1), (1, 0)):
                # Exact minimum-weight Tag: labels are distinct so S must
                # anticommute with one frame Pauli supported only at q, forcing
                # support at q and weight >= 1; the unique weight-one letter with
                # the required syndrome is a (labels (0,1)) or b (labels (1,0)).
                s = _letter_key(a if labels == (0, 1) else b, q)
                if (p10.symp(s, r0), p10.symp(s, r1)) != labels or p10.wt(s) != 1:
                    raise AssertionError("R6L minimum-weight Tag solve failed")
                for perm in (0, 1):
                    ordered = target_pair if perm == 0 else (target_pair[1], target_pair[0])
                    signed = []
                    for k, frame in enumerate((r0, r1)):
                        t = p10.mul(ordered[k], frame)
                        phase = reuse.correction_phase(ordered[k], frame, t, n)
                        signed.append((int(phase), t))
                    reps.append(
                        {
                            "q": q,
                            "frame_letters": (a, b),
                            "labels": labels,
                            "perm": perm,
                            "R": (r0, r1),
                            "S": s,
                            "signed_T": tuple(signed),
                        }
                    )
    return reps


def _rep_id(rep):
    return (rep["q"], rep["frame_letters"], rep["labels"], rep["perm"])


def _r6l_witness(reps, key, terms, pairs, n, total, six_indices):
    s, labels = key
    branch_factors = [
        factor_restore_triple(
            reps[0]["signed_T"][k], reps[1]["signed_T"][k], reps[2]["signed_T"][k], n
        )
        for k in range(2)
    ]
    factored = int(sum(row["support"] for row in branch_factors))
    tag = int(2 * p10.wt(s))
    covered = sorted(i for pair in pairs for i in pair)
    checks = {
        "weight_one_anticommuting_frames": all(
            p10.wt(rep["R"][0]) == 1 and p10.wt(rep["R"][1]) == 1
            and p10.symp(rep["R"][0], rep["R"][1]) == 1
            for rep in reps
        ),
        "zero_uanti_support": all(
            _uanti_m2(rep["R"], 0) == 0 and _uanti_m2(rep["R"], 1) == 0 for rep in reps
        ),
        "shared_tag_key": all(rep["S"] == s and rep["labels"] == labels for rep in reps),
        "labels_reproduced_by_S": all(
            (p10.symp(s, rep["R"][0]), p10.symp(s, rep["R"][1])) == labels for rep in reps
        ),
        "distinct_labels": labels[0] != labels[1],
        "restore_identities_and_phases": all(
            p10.mul(rep["signed_T"][k][1], rep["R"][k])
            == (
                (terms[pairs[j][0]][0], terms[pairs[j][1]][0])
                if rep["perm"] == 0
                else (terms[pairs[j][1]][0], terms[pairs[j][0]][0])
            )[k]
            and reuse.correction_phase(
                (
                    (terms[pairs[j][0]][0], terms[pairs[j][1]][0])
                    if rep["perm"] == 0
                    else (terms[pairs[j][1]][0], terms[pairs[j][0]][0])
                )[k],
                rep["R"][k],
                rep["signed_T"][k][1],
                n,
            )
            == rep["signed_T"][k][0]
            for j, rep in enumerate(reps)
            for k in range(2)
        ),
        "factor_checks": all(all(row["checks"].values()) for row in branch_factors),
        "six_term_conservation": covered == sorted(six_indices),
        "cost_recomputed": int(tag + factored) == int(total),
        "rotation_count_nine": ROTATIONS_R6M == 9,
    }
    if not all(checks.values()):
        raise AssertionError({"r6l_witness_failed": checks})
    return {
        "matching": [list(pair) for pair in pairs],
        "tag_key": {"S": list(s), "labels": list(labels)},
        "blocks": [
            {
                "q": rep["q"],
                "frame_letters": list(rep["frame_letters"]),
                "target_permutation": rep["perm"],
                "R": [list(rep["R"][0]), list(rep["R"][1])],
                "signed_T": [
                    {"phase": rep["signed_T"][k][0], "T": list(rep["signed_T"][k][1])}
                    for k in range(2)
                ],
            }
            for rep in reps
        ],
        "branch_factors": branch_factors,
        "tag_support_twice": tag,
        "factored_restore_support": factored,
        "C_R6L": int(total),
        "rotation_count": ROTATIONS_R6M,
        "checks": checks,
    }


def donor_r6l_matching(terms, pairs, n: int, six_indices) -> dict[str, Any]:
    groups_by_block = []
    for pair in pairs:
        target_pair = (terms[pair[0]][0], terms[pair[1]][0])
        groups: dict[Any, list] = {}
        for rep in _m2_weight_one_reps(target_pair, n):
            groups.setdefault((rep["S"], rep["labels"]), []).append(rep)
        for key in groups:
            groups[key].sort(key=_rep_id)
        groups_by_block.append(groups)
    common = sorted(set(groups_by_block[0]) & set(groups_by_block[1]) & set(groups_by_block[2]))
    if not common:
        raise AssertionError({"r6l_no_common_tag_key": [list(p) for p in pairs]})
    best = None
    combos = 0
    for key in common:
        s, _labels = key
        tag = 2 * p10.wt(s)
        for rep_a in groups_by_block[0][key]:
            for rep_b in groups_by_block[1][key]:
                for rep_c in groups_by_block[2][key]:
                    combos += 1
                    support = sum(
                        _factor_support_fast(
                            rep_a["signed_T"][k][1],
                            rep_b["signed_T"][k][1],
                            rep_c["signed_T"][k][1],
                        )
                        for k in range(2)
                    )
                    total = int(tag + support)
                    order = (total, key, _rep_id(rep_a), _rep_id(rep_b), _rep_id(rep_c))
                    if best is None or order < best[0]:
                        best = (order, (rep_a, rep_b, rep_c, key, total))
    rep_a, rep_b, rep_c, key, total = best[1]
    witness = _r6l_witness((rep_a, rep_b, rep_c), key, terms, pairs, n, total, six_indices)
    witness["common_tag_key_count"] = len(common)
    witness["representation_triple_count"] = combos
    return witness


# ---- matchings / normalization ----------------------------------------------

def perfect_matchings(indices):
    """The 15 canonical unordered perfect matchings frozen by R6L."""
    idx = tuple(sorted(int(i) for i in indices))
    if len(idx) != 6 or len(set(idx)) != 6:
        raise AssertionError({"matching_base_not_six_unique": idx})

    def rec(rest):
        if not rest:
            return [()]
        first = rest[0]
        out = []
        for j in range(1, len(rest)):
            pair = (first, rest[j])
            remaining = rest[1:j] + rest[j + 1:]
            for tail in rec(remaining):
                out.append((pair,) + tail)
        return out

    matchings = [
        tuple(sorted(tuple(sorted(pair)) for pair in matching))
        for matching in rec(idx)
    ]
    unique = sorted(set(matchings))
    if len(matchings) != 15 or len(unique) != 15:
        raise AssertionError({"matching_count_not_15": len(unique)})
    return tuple(unique)


def lambda_r6m(terms, pairs) -> float:
    return float(
        sum(
            math.sqrt(2.0) * math.sqrt(float(terms[i][1]) ** 2 + float(terms[j][1]) ** 2)
            for i, j in pairs
        )
    )


# ---- strongest incumbent comparator (donor stack + R6L, Erratum 1) ----------

def _stack_rows(terms, source_indices, n: int):
    """Recompute the frozen two-M3 donor stack: frame-only, R6B reuse, R6H, R6J."""
    r6d_eval, incumbent_rows = r6j._incumbent_rows(terms, source_indices, n)
    rows = []
    for row in incumbent_rows:
        a = tuple(int(x) for x in row["partition"][0])
        b = tuple(int(x) for x in row["partition"][1])
        candidate = r6j.best_restore_factor(
            r6j._block(terms, a), r6j._block(terms, b), n
        )
        c_r6j = None if candidate["best"] is None else int(candidate["best"]["C_restore_factor"])
        components = {"FRAME_ONLY": int(row["C_frame_only"])}
        if row.get("C_reuse") is not None:
            components["R6B_REUSE"] = int(row["C_reuse"])
        if row.get("C_R6H") is not None:
            components["R6H"] = int(row["C_R6H"])
        if c_r6j is not None:
            components["R6J"] = c_r6j
        source, cost = min(components.items(), key=lambda kv: (kv[1], kv[0]))
        rows.append(
            {
                "point_kind": "TWO_M3_STACK",
                "point_id": [list(a), list(b)],
                "Lambda": float(row["Lambda_batch"]),
                "C": int(cost),
                "component_costs": components,
                "source": source,
                "rotations": ROTATIONS_TWO_M3,
            }
        )
    return r6d_eval, rows


def _point_order(point):
    return (int(point["C"]), float(point["Lambda"]), point["point_kind"], canonical_json(point["point_id"]))


def _comparator(donor_points, lam_candidate: float):
    """R6L Erratum-1 comparator: matched lower envelope, else global cost floor."""
    eligible = [pt for pt in donor_points if float(pt["Lambda"]) <= lam_candidate + TOL]
    if eligible:
        mode = "MATCHED_LOWER_ENVELOPE"
        pool = eligible
    else:
        mode = "CONSERVATIVE_GLOBAL_COST_FLOOR"
        pool = donor_points
    best = min(pool, key=_point_order)
    return mode, best


# ---- hostile exactness ------------------------------------------------------

_N1_LETTER_KEY = {"X": (1, 0), "Y": (1, 1), "Z": (0, 1)}


def _synthetic_terms(target_pairs):
    """Deterministic synthetic six-term list; coefficients never enter the cost."""
    terms = []
    coefficient = 0.5
    for pair in target_pairs:
        for key in pair:
            terms.append((tuple(key), coefficient))
            coefficient *= 0.75
    if len(terms) != 6:
        raise AssertionError("synthetic instance must have exactly six terms")
    return terms


def _brute_config_n1(target_pairs, perm_b, perm_c, centrals):
    """Independent full enumeration of the identical grammar at n=1."""
    sy, lm, lw = p10.h.local_symp, p10.h.local_mul, p10.h.local_wt
    ordered = [
        target_pairs[0],
        target_pairs[1] if perm_b == 0 else (target_pairs[1][1], target_pairs[1][0]),
        target_pairs[2] if perm_c == 0 else (target_pairs[2][1], target_pairs[2][0]),
    ]
    # Convert the n=1 global keys into local letter codes.
    block_letters = [
        (
            p10.h.BITS_CODE[(pair[0][0] & 1, pair[0][1] & 1)],
            p10.h.BITS_CODE[(pair[1][0] & 1, pair[1][1] & 1)],
        )
        for pair in ordered
    ]
    multipliers = []
    for central in centrals:
        multipliers.extend((2 if central == 0 else 4, 2 if central == 1 else 4))
    best = None
    for option in itertools.product(range(4), repeat=7):
        ra0, ra1, rb0, rb1, rc0, rc1, s = option
        frames = (ra0, ra1, rb0, rb1, rc0, rc1)
        if not (sy(ra0, ra1) and sy(rb0, rb1) and sy(rc0, rc1)):
            continue
        c0, c1 = sy(s, ra0), sy(s, ra1)
        if sy(s, rb0) != c0 or sy(s, rc0) != c0:
            continue
        if sy(s, rb1) != c1 or sy(s, rc1) != c1:
            continue
        if c0 == c1:
            continue
        raw = sum(m * lw(r) for m, r in zip(multipliers, frames)) + 2 * lw(s)
        for k in range(2):
            triple = tuple(
                lm(block_letters[j][k], frames[2 * j + k]) for j in range(3)
            )
            if triple[0] == triple[1] == triple[2] != 0:
                raw += 1
            else:
                raw += lw(triple[0]) + lw(triple[1]) + lw(triple[2])
        cost = raw - 18
        if best is None or cost < best:
            best = cost
    return best


def _brute_config_n2(target_pairs, perm_b, perm_c, centrals):
    """Independent global-Pauli enumeration of the identical grammar at n=2."""
    n = 2
    keys = [(x, z) for x in range(4) for z in range(4)]
    ordered = [
        target_pairs[0],
        target_pairs[1] if perm_b == 0 else (target_pairs[1][1], target_pairs[1][0]),
        target_pairs[2] if perm_c == 0 else (target_pairs[2][1], target_pairs[2][0]),
    ]
    best = None
    for s in keys:
        if s == (0, 0):
            continue
        for orientation in ((0, 1), (1, 0)):
            pairs = [
                (r0, r1)
                for r0 in keys
                for r1 in keys
                if p10.symp(r0, r1) == 1
                and p10.symp(s, r0) == orientation[0]
                and p10.symp(s, r1) == orientation[1]
            ]
            if not pairs:
                continue
            per_block = []
            for j in range(3):
                m0 = 2 if centrals[j] == 0 else 4
                m1 = 2 if centrals[j] == 1 else 4
                base = np.empty(len(pairs), dtype=np.int64)
                letter = np.empty((len(pairs), 2, n), dtype=np.int64)
                for idx, (r0, r1) in enumerate(pairs):
                    t0 = p10.mul(ordered[j][0], r0)
                    t1 = p10.mul(ordered[j][1], r1)
                    base[idx] = (
                        m0 * (p10.wt(r0) - 1)
                        + m1 * (p10.wt(r1) - 1)
                        + p10.wt(t0)
                        + p10.wt(t1)
                    )
                    for q in range(n):
                        letter[idx, 0, q] = p10.h.BITS_CODE[((t0[0] >> q) & 1, (t0[1] >> q) & 1)]
                        letter[idx, 1, q] = p10.h.BITS_CODE[((t1[0] >> q) & 1, (t1[1] >> q) & 1)]
                per_block.append((base, letter))
            (base_a, la), (base_b, lb), (base_c, lc) = per_block
            total = (
                base_a[:, None, None]
                + base_b[None, :, None]
                + base_c[None, None, :]
                + 2 * p10.wt(s)
            )
            for k in range(2):
                for q in range(n):
                    xa = la[:, k, q][:, None, None]
                    xb = lb[:, k, q][None, :, None]
                    xc = lc[:, k, q][None, None, :]
                    total = total - 2 * ((xa == xb) & (xa == xc) & (xa != 0))
            value = int(total.min())
            if best is None or value < best:
                best = value
    return best


_HOSTILE_N1_PANELS = {
    "n1_identical": (("X", "Z"), ("X", "Z"), ("X", "Z")),
    "n1_swapped": (("X", "Z"), ("Z", "X"), ("Y", "X")),
    "n1_mixed": (("X", "Y"), ("Z", "Y"), ("Z", "X")),
}
_HOSTILE_N2_PANELS = {
    "n2_a": (((1, 0), (0, 1)), ((3, 0), (0, 3)), ((1, 2), (2, 1))),
    "n2_b": (((3, 1), (1, 3)), ((2, 3), (3, 2)), ((1, 0), (2, 2))),
}
_SYNTHETIC_MATCHING = ((0, 1), (2, 3), (4, 5))


def hostile_exactness() -> dict[str, Any]:
    panels = {}
    permutation_configs = set()
    central_configs = set()
    for name, letter_pairs in _HOSTILE_N1_PANELS.items():
        target_pairs = tuple(
            (_N1_LETTER_KEY[a], _N1_LETTER_KEY[b]) for a, b in letter_pairs
        )
        terms = _synthetic_terms(target_pairs)
        config_rows = []
        for perm_b, perm_c in itertools.product((0, 1), repeat=2):
            for centrals in itertools.product((0, 1), repeat=3):
                dp_cost = _dp_config_cost(terms, _SYNTHETIC_MATCHING, perm_b, perm_c, centrals, 1)
                brute_cost = _brute_config_n1(target_pairs, perm_b, perm_c, centrals)
                permutation_configs.add((perm_b, perm_c))
                central_configs.add(centrals)
                if dp_cost is None or brute_cost is None or dp_cost != brute_cost:
                    raise AssertionError(
                        {"hostile_n1_mismatch": [name, perm_b, perm_c, centrals, dp_cost, brute_cost]}
                    )
                config_rows.append(int(dp_cost))
        witness = exact_r6m_matching(terms, _SYNTHETIC_MATCHING, 1, list(range(6)))
        if witness["C_R6M"] != min(config_rows):
            raise AssertionError({"hostile_n1_global_mismatch": name})
        replay = exact_r6m_matching(terms, _SYNTHETIC_MATCHING, 1, list(range(6)))
        deterministic = canonical_json(witness) == canonical_json(replay)
        if not deterministic:
            raise AssertionError({"hostile_n1_nondeterministic": name})
        panels[name] = {
            "n": 1,
            "configs_verified": len(config_rows),
            "dp_cost": int(witness["C_R6M"]),
            "brute_cost": int(min(config_rows)),
            "optimal_config": [
                witness["relative_permutation_B"],
                witness["relative_permutation_C"],
                witness["centrals"],
            ],
            "deterministic_tie_replay": deterministic,
            "pass": True,
        }
    for name, target_pairs in _HOSTILE_N2_PANELS.items():
        terms = _synthetic_terms(target_pairs)
        config_rows = []
        for perm_b, perm_c in itertools.product((0, 1), repeat=2):
            for centrals in itertools.product((0, 1), repeat=3):
                dp_cost = _dp_config_cost(terms, _SYNTHETIC_MATCHING, perm_b, perm_c, centrals, 2)
                brute_cost = _brute_config_n2(target_pairs, perm_b, perm_c, centrals)
                permutation_configs.add((perm_b, perm_c))
                central_configs.add(centrals)
                if dp_cost is None or brute_cost is None or dp_cost != brute_cost:
                    raise AssertionError(
                        {"hostile_n2_mismatch": [name, perm_b, perm_c, centrals, dp_cost, brute_cost]}
                    )
                config_rows.append(int(dp_cost))
        witness = exact_r6m_matching(terms, _SYNTHETIC_MATCHING, 2, list(range(6)))
        if witness["C_R6M"] != min(config_rows):
            raise AssertionError({"hostile_n2_global_mismatch": name})
        replay = exact_r6m_matching(terms, _SYNTHETIC_MATCHING, 2, list(range(6)))
        deterministic = canonical_json(witness) == canonical_json(replay)
        if not deterministic:
            raise AssertionError({"hostile_n2_nondeterministic": name})
        panels[name] = {
            "n": 2,
            "configs_verified": len(config_rows),
            "dp_cost": int(witness["C_R6M"]),
            "brute_cost": int(min(config_rows)),
            "optimal_config": [
                witness["relative_permutation_B"],
                witness["relative_permutation_C"],
                witness["centrals"],
            ],
            "deterministic_tie_replay": deterministic,
            "pass": True,
        }

    # Inherited exact M2/TARE algebra and R6L factor-phase hostile tests.
    signed_phase = reuse.hostile_validation()
    x, z = (1, 0), (0, 1)
    same = factor_restore_triple((0, x), (0, x), (0, x), 1)
    mixed = factor_restore_triple((0, x), (0, x), (0, z), 1)
    partial = factor_restore_triple((0, x), (0, x), (0, (0, 0)), 1)
    factor_gates = {
        "all_three_identical_saves_two": same["support"] == 1
        and same["matching_nonidentity_local_letters"] == 1,
        "mixed_letter_no_false_saving": mixed["support"] == 3
        and mixed["matching_nonidentity_local_letters"] == 0,
        "two_of_three_no_false_saving": partial["support"] == 2
        and partial["matching_nonidentity_local_letters"] == 0,
        "factor_phases_exact": all(
            all(rec["checks"].values()) for rec in (same, mixed, partial)
        ),
    }

    # R6L synthetic: common Tag across three blocks with different Restores.
    q1z = (0, 2)
    synthetic_pairs = (
        ((1, 0), (0, 1)),
        (p10.mul((1, 0), q1z), p10.mul((0, 1), q1z)),
        ((3, 0), (2, 1)),
    )
    r6l_terms = _synthetic_terms(synthetic_pairs)
    r6l_donor = donor_r6l_matching(r6l_terms, _SYNTHETIC_MATCHING, 2, list(range(6)))
    restore_sets = [
        tuple(tuple(row["T"]) for row in block["signed_T"])
        for block in r6l_donor["blocks"]
    ]
    r6l_gates = {
        "common_tag_with_different_restores_accepted": all(r6l_donor["checks"].values())
        and len(set(restore_sets)) > 1,
        "r6l_min_tag_exact_brute": _r6l_min_tag_brute_check(),
    }

    stack_hostiles = {
        "r6b_signed_phase_hostile_pass": signed_phase["all_pass"],
        "r6d_hostile_pass": r6d.hostile_validation()["all_pass"],
        "r6h_hostile_pass": r6h.hostile_validation()["all_pass"],
        "r6j_hostile_pass": r6j.hostile_validation()["all_pass"],
    }
    gates = {
        "dp_vs_brute_exact_all_panels": all(row["pass"] for row in panels.values()),
        "all_four_relative_permutation_configs_exercised": len(permutation_configs) == 4,
        "all_eight_central_configs_exercised": len(central_configs) == 8,
        "deterministic_tie_replay": all(
            row["deterministic_tie_replay"] for row in panels.values()
        ),
        **factor_gates,
        **r6l_gates,
        **stack_hostiles,
    }
    if not all(gates.values()):
        raise AssertionError({"r6m_hostile_failure": gates})
    return {
        "panels": panels,
        "gates": gates,
        "all_pass": True,
        "brute_solver": "independent global Pauli-string enumeration (full 4^7 at n=1; "
        "anticommuting-pair times common-Tag scan over all 16^2 keys at n=2)",
    }


def _r6l_min_tag_brute_check() -> bool:
    """Exhaustively confirm the closed-form R6L minimum-weight Tag at n=2."""
    n = 2
    keys = [(xx, zz) for xx in range(4) for zz in range(4)]
    for q in range(n):
        for a, b in itertools.permutations((1, 2, 3), 2):
            r0, r1 = _letter_key(a, q), _letter_key(b, q)
            for labels in ((0, 1), (1, 0)):
                solutions = [
                    key
                    for key in keys
                    if (p10.symp(key, r0), p10.symp(key, r1)) == labels
                ]
                best = min(p10.wt(key) for key in solutions)
                closed = _letter_key(a if labels == (0, 1) else b, q)
                minimal = [key for key in solutions if p10.wt(key) == best]
                if best != 1 or closed not in minimal:
                    return False
    return True


# ---- subject evaluation -----------------------------------------------------

def run_subject(name: str, cfg) -> dict[str, Any]:
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    if len(source_indices) != 6:
        return {
            "subject": name,
            "source_blob_expected": cfg["blob"],
            "source_blob_observed": observed_blob,
            "source_blob_verified": observed_blob == cfg["blob"],
            "batch_complete": False,
            "r6b_window_champions_available": len(champions),
            "frozen_source_indices": list(source_indices),
            "matching_count": 0,
            "strict_count": 0,
            "strict_budget_matched_improvement_exists": False,
            "best_strict": None,
            "max_imag": float(max_imag),
        }
    six = [int(i) for i in source_indices]
    six_targets = [terms[i][0] for i in six]
    pairwise_commute = all(
        p10.symp(six_targets[i], six_targets[j]) == 0
        for i in range(6)
        for j in range(i + 1, 6)
    )
    if not pairwise_commute:
        raise AssertionError({"r6m_frozen_batch_not_pairwise_commuting": name})

    matchings = perfect_matchings(six)
    r6d_eval, stack_points = _stack_rows(terms, tuple(six), n)
    donor_replay_ok = (
        len(r6d_eval.get("all_partitions", [])) == 10
        and r6d_eval.get("all_witnesses_valid") is True
        and len(stack_points) > 0
    )

    r6l_rows = []
    for pairs in matchings:
        lam = lambda_r6m(terms, pairs)
        witness = donor_r6l_matching(terms, pairs, n, six)
        r6l_rows.append(
            {
                "point_kind": "R6L_THREE_M2",
                "point_id": [list(pair) for pair in pairs],
                "Lambda": lam,
                "C": int(witness["C_R6L"]),
                "rotations": ROTATIONS_R6M,
                "witness": witness,
            }
        )
    donor_points = stack_points + [
        {key: value for key, value in row.items() if key != "witness"}
        for row in r6l_rows
    ]
    global_floor = min(donor_points, key=_point_order)

    candidate_rows = []
    for pairs, r6l_row in zip(matchings, r6l_rows):
        lam = float(r6l_row["Lambda"])
        witness = exact_r6m_matching(terms, pairs, n, six)
        cost = int(witness["C_R6M"])
        if cost > int(r6l_row["C"]):
            raise AssertionError(
                {
                    "r6m_dp_worse_than_contained_r6l_grammar": [list(p) for p in pairs],
                    "C_R6M": cost,
                    "C_R6L": int(r6l_row["C"]),
                }
            )
        mode, incumbent = _comparator(donor_points, lam)
        delta = int(incumbent["C"]) - cost
        rotation_nonworse = ROTATIONS_R6M <= int(incumbent["rotations"])
        strict = delta > 0 and rotation_nonworse
        candidate_rows.append(
            {
                "matching": [list(pair) for pair in pairs],
                "Lambda_R6M": lam,
                "C_R6M": cost,
                "C_R6L_same_matching": int(r6l_row["C"]),
                "comparator_mode": mode,
                "C_incumbent": int(incumbent["C"]),
                "incumbent_witness": incumbent,
                "delta_vs_incumbent": delta,
                "rotation_count": ROTATIONS_R6M,
                "incumbent_rotations": int(incumbent["rotations"]),
                "rotation_nonworse": rotation_nonworse,
                "strict_budget_matched_improvement": strict,
                "witness": witness,
            }
        )
    strict_rows = sorted(
        (row for row in candidate_rows if row["strict_budget_matched_improvement"]),
        key=lambda row: (-int(row["delta_vs_incumbent"]), float(row["Lambda_R6M"]), row["matching"]),
    )
    best_candidate = min(
        candidate_rows,
        key=lambda row: (
            int(row["C_R6M"]),
            row["matching"],
            int(row["witness"]["relative_permutation_B"]),
            int(row["witness"]["relative_permutation_C"]),
            tuple(row["witness"]["centrals"]),
            int(row["witness"]["final_parity_state"]),
        ),
    )
    return {
        "subject": name,
        "source_blob_expected": cfg["blob"],
        "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"],
        "batch_complete": True,
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": six,
        "six_terms_pairwise_commute": pairwise_commute,
        "n_qubits": n,
        "max_imag": float(max_imag),
        "matching_count": len(matchings),
        "donor_stack_replay_ok": donor_replay_ok,
        "donor_stack_points": stack_points,
        "donor_r6l_points": r6l_rows,
        "donor_global_cost_floor": global_floor,
        "candidate_points": candidate_rows,
        "strict_count": len(strict_rows),
        "strict_budget_matched_improvement_exists": bool(strict_rows),
        "best_strict": None if not strict_rows else strict_rows[0],
        "best_candidate": {
            "matching": best_candidate["matching"],
            "Lambda_R6M": best_candidate["Lambda_R6M"],
            "C_R6M": best_candidate["C_R6M"],
            "C_incumbent": best_candidate["C_incumbent"],
            "delta_vs_incumbent": best_candidate["delta_vs_incumbent"],
            "comparator_mode": best_candidate["comparator_mode"],
        },
        "all_candidate_witnesses_valid": all(
            all(row["witness"]["checks"].values()) for row in candidate_rows
        ),
        "all_r6l_witnesses_valid": all(
            all(row["witness"]["checks"].values()) for row in r6l_rows
        ),
    }


def main() -> dict[str, Any]:
    hostile = hostile_exactness()
    summaries = {}
    for name, cfg in p10.base.SUBJECTS.items():
        summaries[name] = run_subject(name, cfg)

    strict_h4 = summaries["H4"]["strict_budget_matched_improvement_exists"]
    strict_n2 = summaries["N2"]["strict_budget_matched_improvement_exists"]
    if strict_h4 and strict_n2:
        authority = "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_SUPPORTED__NOT_R6"
        responsibility = "RESP:BOUNDED_COUPLED_THREE_M2_COMPILER_ELIGIBLE_FOR_PREOUTCOME_GATES"
        supported = True
    elif strict_h4 or strict_n2:
        authority = "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_PARTIAL__MATCHED_COUNTERFACTUAL__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_METHOD_SPLIT"
        supported = False
    else:
        authority = "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_NEGATIVE__NOT_R6"
        responsibility = "RESP:RESIDUAL_COUPLED_OPTIMIZATION_ADDS_NOTHING_BEYOND_R6L_DONOR"
        supported = False

    gates = {
        "hostile_dp_vs_brute_exact": hostile["all_pass"],
        "inherited_tare_factor_phase_gates_pass": all(
            hostile["gates"][key]
            for key in (
                "r6b_signed_phase_hostile_pass",
                "all_three_identical_saves_two",
                "mixed_letter_no_false_saving",
                "two_of_three_no_false_saving",
                "factor_phases_exact",
                "common_tag_with_different_restores_accepted",
                "r6l_min_tag_exact_brute",
            )
        ),
        "exactly_fifteen_matchings_per_subject": all(
            row["matching_count"] == 15 for row in summaries.values()
        ),
        "source_blobs_observed_match": all(
            row["source_blob_verified"] for row in summaries.values()
        ),
        "all_witnesses_independently_reconstructed": all(
            row.get("all_candidate_witnesses_valid") is True
            and row.get("all_r6l_witnesses_valid") is True
            for row in summaries.values()
        ),
        "donor_stack_and_r6l_replay_correct": all(
            row.get("donor_stack_replay_ok") is True for row in summaries.values()
        )
        and all(
            hostile["gates"][key]
            for key in ("r6d_hostile_pass", "r6h_hostile_pass", "r6j_hostile_pass")
        ),
        "strict_budget_matched_point_h4": strict_h4,
        "strict_budget_matched_point_eq_n2": strict_n2,
        "rotation_count_nine_and_nonworse": all(
            all(
                int(row["rotation_count"]) == 9 and row["rotation_nonworse"] is True
                for row in subject["candidate_points"]
            )
            for subject in summaries.values()
        ),
        "fresh_stretched_n2_unread": True,
    }
    integrity_gates = {
        key: value
        for key, value in gates.items()
        if key not in ("strict_budget_matched_point_h4", "strict_budget_matched_point_eq_n2")
    }
    if not all(integrity_gates.values()):
        raise AssertionError({"r6m_integrity_gate_failure": integrity_gates})

    result = {
        "schema": "ORIONQ.MAXR6M.ExactThreeTare2SharedFactorDP.v1",
        "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_THREE_TARE2_SHARED_TAG_RESTORE_FACTOR_JOINT_DP__NOT_R6",
        "responsibility": responsibility,
        "protocol": "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_PROTOCOL",
        "donor_protocols": [
            "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_PROTOCOL",
            "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_ERRATUM_1",
        ],
        "comparator": "R6L_ERRATUM_1_MATCHED_LOWER_ENVELOPE_OR_CONSERVATIVE_GLOBAL_COST_FLOOR",
        "development_supported": supported and all(gates.values()),
        "rotation_count": ROTATIONS_R6M,
        "hostile": hostile,
        "subjects": summaries,
        "gates": gates,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"] or "r6_earned" in result:
        raise AssertionError("R6M authority ceiling violated")
    print(
        "ORIONQ_MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR="
        + json.dumps(result, sort_keys=True)
    )
    results_path = Path(__file__).with_name(
        "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json"
    )
    results_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


if __name__ == "__main__":
    main()
