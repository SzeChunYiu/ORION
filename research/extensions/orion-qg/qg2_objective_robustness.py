#!/usr/bin/env python3
"""ORION-QG lane QG-2: objective robustness of the TARE regime geometry.

Frozen by development/orion-qg-regime-geometry/QG2_OBJECTIVE_ROBUSTNESS_PROTOCOL.md
(frozen BEFORE any QG-2 outcome was computed).

Re-maps the committed R6N..R6S regime geometry of the frozen R6M three-block
TARE-M2 shared-Tag grammar under two frozen alternative objectives:

  O1 (T-count-weighted):  (t_nc, t_c, t_tag, t_r, rho) = (7, 1, 4, 3, 0)
  O2 (rotation-coupled):  (t_nc, t_c, t_tag, t_r, rho) = (4, 2, 2, 1, 5)

with O0 = (4, 2, 2, 1, 0) computed only as the binding control against the
committed R6O/R6P/R6Q receipts. The committed modules are imported unmodified;
the DP local tables are rebuilt objective-parameterized (the committed option /
parity algebra is reused read-only). Honest outcome space per objective:
GEOMETRY_ROBUST / GEOMETRY_OBJECTIVE_DEPENDENT; overall MIXED when the
objectives disagree. Not R6; no novelty credit; the protected stretched-N2
discriminator is never read.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any, NamedTuple

import numpy as np

HERE = Path(__file__).resolve().parent
ORION_Q = HERE.parent / "orion-q"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6b_tare_transformation_reuse_donor as reuse  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
INF = 10 ** 9  # family sentinel, as frozen in R6Q
DPINF = r6m.INF  # 10**12, DP sentinel
MATCHING = r6m._SYNTHETIC_MATCHING  # ((0, 1), (2, 3), (4, 5))
CENTRALS8 = tuple(itertools.product((0, 1), repeat=3))
RANDOM_SEED = 20260823
RANDOM_PER_N = 60
WITNESS_CAP = 12
ROTATIONS_FAMILY = 9
ROTATIONS_STACK = 10
TOL = r6m.TOL


class Objective(NamedTuple):
    name: str
    t_nc: int
    t_c: int
    t_tag: int
    t_r: int
    rho: int

    @property
    def base_const(self) -> int:
        return 3 * (self.t_nc + self.t_c)

    @property
    def family_charge(self) -> int:
        return self.rho * ROTATIONS_FAMILY


OB_O0 = Objective("O0", 4, 2, 2, 1, 0)
OB_O1 = Objective("O1", 7, 1, 4, 3, 0)
OB_O2 = Objective("O2", 4, 2, 2, 1, 5)
ALT_OBJECTIVES = (OB_O1, OB_O2)
for _ob in (OB_O0, OB_O1, OB_O2):
    if _ob.t_c > _ob.t_nc:
        raise AssertionError("qg2 objective violates t_c <= t_nc")

O2_SHIFT = OB_O2.family_charge  # 45; O2 structural weights equal O0


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---- objective-parameterized DP tables --------------------------------------

_OBJ_TABLES: dict[str, tuple] = {}


def _obj_tables(ob: Objective):
    hit = _OBJ_TABLES.get(ob.name)
    if hit is not None:
        return hit
    f3 = np.zeros((4, 4, 4), dtype=np.int64)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                if a == b == c != 0:
                    f3[a, b, c] = ob.t_r
                else:
                    f3[a, b, c] = ob.t_r * int(r6m._LW[a] + r6m._LW[b] + r6m._LW[c])
    tag_cost = ob.t_tag * r6m._LW[r6m._SS]
    frame_cost = {}
    for centrals in CENTRALS8:
        cost = np.zeros(r6m.OPTIONS, dtype=np.int64)
        for j, central in enumerate(centrals):
            m0 = ob.t_c if central == 0 else ob.t_nc
            m1 = ob.t_c if central == 1 else ob.t_nc
            cost = cost + m0 * r6m._LW[r6m._DIG[2 * j]] + m1 * r6m._LW[r6m._DIG[2 * j + 1]]
        frame_cost[centrals] = cost
    out = (frame_cost, tag_cost, f3)
    _OBJ_TABLES[ob.name] = out
    return out


_LT_CACHE: dict[tuple, tuple] = {}


def local_table_ob(p6, centrals, ob: Objective):
    """Objective-parameterized clone of the frozen r6m._local_table."""
    key = (p6, centrals, ob.name)
    hit = _LT_CACHE.get(key)
    if hit is not None:
        return hit
    frame_cost, tag_cost, f3 = _obj_tables(ob)
    factor0 = f3[r6m._LM[p6[0], r6m._RA0], r6m._LM[p6[2], r6m._RB0], r6m._LM[p6[4], r6m._RC0]]
    factor1 = f3[r6m._LM[p6[1], r6m._RA1], r6m._LM[p6[3], r6m._RB1], r6m._LM[p6[5], r6m._RC1]]
    cost = frame_cost[centrals] + tag_cost + factor0 + factor1
    order = np.argsort(cost, kind="stable")
    deltas_sorted = r6m._DELTA[order]
    uniq, first = np.unique(deltas_sorted, return_index=True)
    local_cost = np.full(r6m.PARITY_STATES, DPINF, dtype=np.int64)
    local_opt = np.full(r6m.PARITY_STATES, -1, dtype=np.int64)
    local_cost[uniq] = cost[order][first]
    local_opt[uniq] = order[first]
    out = (local_cost, local_opt)
    _LT_CACHE[key] = out
    return out


def clear_caches():
    r6m._local_table.cache_clear()
    _LT_CACHE.clear()


def dp_cost_n2_ob(target_pairs, ob: Objective) -> int:
    flat = tuple(t for pair in target_pairs for t in pair)
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            t6 = r6o._permute6(flat, perm_b, perm_c)
            p60 = tuple(r6o._local_code(t, 0) for t in t6)
            p61 = tuple(r6o._local_code(t, 1) for t in t6)
            for centrals in CENTRALS8:
                c0, _ = local_table_ob(p60, centrals, ob)
                c1, _ = local_table_ob(p61, centrals, ob)
                for state in r6m.ACCEPTING_STATES:
                    v = int((c0 + c1[r6m.XOR512[state]]).min())
                    if v < DPINF and (best is None or v < best):
                        best = v
    if best is None:
        raise AssertionError("qg2 n=2 DP found no accepting option")
    return best - ob.base_const + ob.family_charge


def _solve_config_ob(branch_targets, centrals, n: int, ob: Objective, keep: bool = False):
    codes6 = tuple(p10.codes(target, n) for target in branch_targets)
    dp = np.full(r6m.PARITY_STATES, DPINF, dtype=np.int64)
    dp[0] = 0
    histories = [dp.copy()] if keep else None
    tables = [] if keep else None
    for q in range(n):
        p6 = tuple(int(codes6[t][q]) for t in range(6))
        cost, opt = local_table_ob(p6, centrals, ob)
        dp = (dp[:, None] + cost[r6m.XOR512]).min(axis=0)
        if keep:
            histories.append(dp.copy())
            tables.append((cost, opt))
    return dp, histories, tables


def dp_cost_pairs_ob(target_pairs, n: int, ob: Objective) -> int:
    flat = tuple(t for pair in target_pairs for t in pair)
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            t6 = r6o._permute6(flat, perm_b, perm_c)
            for centrals in CENTRALS8:
                dp, _, _ = _solve_config_ob(t6, centrals, n, ob)
                for state in r6m.ACCEPTING_STATES:
                    v = int(dp[state])
                    if v < DPINF and (best is None or v < best):
                        best = v
    if best is None:
        raise AssertionError("qg2 general DP found no accepting option")
    return best - ob.base_const + ob.family_charge


def dp_config_cost_ob(target_pairs, perm_b, perm_c, centrals, n: int, ob: Objective):
    flat = tuple(t for pair in target_pairs for t in pair)
    t6 = r6o._permute6(flat, perm_b, perm_c)
    dp, _, _ = _solve_config_ob(t6, centrals, n, ob)
    values = [int(dp[state]) for state in r6m.ACCEPTING_STATES if int(dp[state]) < DPINF]
    return None if not values else min(values) - ob.base_const


def dp_witness_ob(target_pairs, n: int, ob: Objective) -> dict[str, Any]:
    """Optimal DP witness under ob (frozen tie-break) + independent recompute."""
    flat = tuple(t for pair in target_pairs for t in pair)
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            t6 = r6o._permute6(flat, perm_b, perm_c)
            for centrals in CENTRALS8:
                dp, _, _ = _solve_config_ob(t6, centrals, n, ob)
                for state in r6m.ACCEPTING_STATES:
                    raw = int(dp[state])
                    if raw >= DPINF:
                        continue
                    key = (raw, perm_b, perm_c) + centrals + (state,)
                    if best is None or key < best:
                        best = key
    raw, perm_b, perm_c, ca, cb, cc, state = best
    t6 = r6o._permute6(flat, perm_b, perm_c)
    _, histories, tables = _solve_config_ob(t6, (ca, cb, cc), n, ob, keep=True)
    keys7 = r6m._backtrack(histories, tables, state, n)
    ra0, ra1, rb0, rb1, rc0, rc1, s = keys7
    frames = ((ra0, ra1), (rb0, rb1), (rc0, rc1))
    centrals = (ca, cb, cc)
    uanti = []
    for j, frame in enumerate(frames):
        weights = (p10.wt(frame[0]), p10.wt(frame[1]))
        non_central = 1 - centrals[j]
        uanti.append(
            ob.t_nc * (weights[non_central] - 1) + ob.t_c * (weights[centrals[j]] - 1)
        )
    signed = []
    for j in range(3):
        row = []
        for k in range(2):
            t = p10.mul(t6[2 * j + k], frames[j][k])
            phase = reuse.correction_phase(t6[2 * j + k], frames[j][k], t, n)
            row.append((int(phase), t))
        signed.append(row)
    factors = [
        r6m.factor_restore_triple(signed[0][k], signed[1][k], signed[2][k], n)
        for k in range(2)
    ]
    units = int(sum(f["support"] for f in factors))
    recomputed = int(sum(uanti) + ob.t_tag * p10.wt(s) + ob.t_r * units)
    cost = raw - ob.base_const + ob.family_charge
    if recomputed != raw - ob.base_const:
        raise AssertionError({"qg2_dp_witness_recompute_mismatch": [recomputed, raw - ob.base_const]})
    return {
        "objective": ob.name,
        "C_DP": int(cost),
        "relative_permutation_B": int(perm_b),
        "relative_permutation_C": int(perm_c),
        "centrals": list(centrals),
        "final_parity_state": int(state),
        "R": {"A": [list(ra0), list(ra1)], "B": [list(rb0), list(rb1)],
              "C": [list(rc0), list(rc1)]},
        "S": list(s),
        "tag_weight": int(p10.wt(s)),
        "frame_supports": [[int(p10.wt(f[0])), int(p10.wt(f[1]))] for f in frames],
        "max_frame_support": int(max(p10.wt(f[k]) for f in frames for k in range(2))),
        "uanti_ob": [int(u) for u in uanti],
        "restore_units_factored": units,
        "cost_recomputed_ok": True,
    }


# ---- objective-independent family primitives --------------------------------


def r6l_min_support(target_pairs, n: int) -> int:
    """Minimum factored-Restore unit support over the frozen R6L family."""
    groups_by_block = []
    for pair in target_pairs:
        groups: dict[Any, list] = {}
        for rep in r6m._m2_weight_one_reps((tuple(pair[0]), tuple(pair[1])), n):
            groups.setdefault((rep["S"], rep["labels"]), []).append(rep)
        groups_by_block.append(groups)
    common = sorted(set(groups_by_block[0]) & set(groups_by_block[1]) & set(groups_by_block[2]))
    if not common:
        raise AssertionError("qg2 r6l family empty")
    best = None
    for key in common:
        for rep_a in groups_by_block[0][key]:
            for rep_b in groups_by_block[1][key]:
                for rep_c in groups_by_block[2][key]:
                    support = sum(
                        r6m._factor_support_fast(
                            rep_a["signed_T"][k][1],
                            rep_b["signed_T"][k][1],
                            rep_c["signed_T"][k][1],
                        )
                        for k in range(2)
                    )
                    if best is None or support < best:
                        best = support
    return int(best)


def dplus_primitive(target_pairs, n: int):
    """u_d = min restore units over the frozen R6O D+ family with d anchors."""
    target_pairs = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    u = [INF, INF, INF]
    for labels in r6o.LABEL_ORIENTATIONS:
        per_block = [r6o._block_choices(tp, n, labels) for tp in target_pairs]
        (aa, fa, la), (ab, fb, lb), (ac, fc, lc) = per_block
        m = aa.shape[0]
        fc_units = np.zeros((m, m, m), dtype=np.int32)
        for k in range(2):
            for q in range(n):
                np.add(
                    fc_units,
                    r6o.F3[
                        la[:, k, q][:, None, None],
                        lb[:, k, q][None, :, None],
                        lc[:, k, q][None, None, :],
                    ],
                    out=fc_units,
                )
        s_ab = (aa[:, None] == ab[None, :])
        s_ac = (aa[:, None] == ac[None, :])
        s_bc = (ab[:, None] == ac[None, :])
        ok_ab = (~s_ab) | (fa[:, None] == fb[None, :])
        ok_ac = (~s_ac) | (fa[:, None] == fc[None, :])
        ok_bc = (~s_bc) | (fb[:, None] == fc[None, :])
        feas = ok_ab[:, :, None] & ok_ac[:, None, :] & ok_bc[None, :, :]
        all3 = s_ab[:, :, None] & s_ac[:, None, :]
        ndistinct = (
            3
            - s_ab[:, :, None].astype(np.int32)
            - s_ac[:, None, :].astype(np.int32)
            - s_bc[None, :, :].astype(np.int32)
            + all3.astype(np.int32)
        )
        for d in (1, 2, 3):
            mask = feas & (ndistinct == d)
            if mask.any():
                v = int(fc_units[mask].min())
                if v < u[d - 1]:
                    u[d - 1] = v
    if all(v >= INF for v in u):
        raise AssertionError("qg2 D+ family produced no feasible point")
    return tuple(u)


def borrow_primitive(target_pairs, n: int):
    """u_p = min restore units over the frozen R6Q borrow family, p phantoms.

    Returns None when the family is empty (no phantom option anywhere), else a
    3-tuple (u_1, u_2, u_3) with INF for unrealized phantom counts.
    """
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= r6q._supp_mask(pair[0]) | r6q._supp_mask(pair[1])
    u_qubits = r6q._qubits(union)
    q_tags = list(u_qubits)
    for q in range(n):
        if not (union >> q) & 1:
            q_tags.append(q)
            break
    u = [INF, INF, INF]
    seen_any = False
    for q_t in q_tags:
        rel = tuple(sorted(set(u_qubits) | {q_t}))
        for v in (1, 2, 3):
            per_block = [r6q._borrow_block_options(tp[j], n, q_t, v, rel) for j in range(3)]
            if all(opt[0].shape[0] == opt[2] for opt in per_block):
                continue
            seen_any = True
            (ea, la, _naa), (eb, lb, _nab), (ec, lc, _nac) = per_block
            pa = (ea != 0).astype(np.int32)
            pb = (eb != 0).astype(np.int32)
            pc = (ec != 0).astype(np.int32)
            pcount = pa[:, None, None] + pb[None, :, None] + pc[None, None, :]
            units = np.zeros(pcount.shape, dtype=np.int32)
            for k in range(2):
                for qi in range(len(rel)):
                    units = units + r6q.F3[
                        la[:, k, qi][:, None, None],
                        lb[:, k, qi][None, :, None],
                        lc[:, k, qi][None, None, :],
                    ]
            for p in (1, 2, 3):
                mask = pcount == p
                if mask.any():
                    v_min = int(units[mask].min())
                    if v_min < u[p - 1]:
                        u[p - 1] = v_min
    if not seen_any:
        return None
    return tuple(u)


class Primitives(NamedTuple):
    s_star: int
    u_d: tuple
    u_p: Any  # tuple or None


def compute_primitives(target_pairs, n: int) -> Primitives:
    return Primitives(
        s_star=r6l_min_support(target_pairs, n),
        u_d=dplus_primitive(target_pairs, n),
        u_p=borrow_primitive(target_pairs, n),
    )


def score_families(prim: Primitives, ob: Objective):
    fam = ob.family_charge
    c_r6l = ob.t_tag + ob.t_r * prim.s_star + fam
    c_dplus = min(
        ob.t_tag * d + ob.t_r * prim.u_d[d - 1]
        for d in (1, 2, 3)
        if prim.u_d[d - 1] < INF
    ) + fam
    if prim.u_p is None or all(v >= INF for v in prim.u_p):
        f_b = INF
    else:
        f_b = ob.t_tag + min(
            ob.t_c * p + ob.t_r * prim.u_p[p - 1]
            for p in (1, 2, 3)
            if prim.u_p[p - 1] < INF
        ) + fam
    return int(c_r6l), int(c_dplus), int(f_b)


# ---- objective-parameterized support-capped family (D++, support <= 2) ------


def dxx_cost_ob(target_pairs, n: int, ob: Objective) -> int:
    tb = r6p._tables(n, 2)
    target_pairs = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    w0 = tb.pop[tb.R0X | tb.R0Z]
    w1 = tb.pop[tb.R1X | tb.R1Z]
    uanti = ob.t_nc * (np.minimum(w0, w1) - 1) + ob.t_c * (np.maximum(w0, w1) - 1)
    positions = 2 * n
    blocks = []
    for tp in target_pairs:
        bases = []
        codes = []
        for perm in (0, 1):
            t0, t1 = tp if perm == 0 else (tp[1], tp[0])
            t0x = t0[0] ^ tb.R0X
            t0z = t0[1] ^ tb.R0Z
            t1x = t1[0] ^ tb.R1X
            t1z = t1[1] ^ tb.R1Z
            base = uanti + ob.t_r * (tb.pop[t0x | t0z] + tb.pop[t1x | t1z])
            code = np.zeros(tb.P, dtype=np.int64)
            for q in range(n):
                code |= r6p.LCODE[(t0x >> q) & 1, (t0z >> q) & 1] << (2 * q)
                code |= r6p.LCODE[(t1x >> q) & 1, (t1z >> q) & 1] << (2 * (n + q))
            bases.append(base)
            codes.append(code)
        blocks.append((np.concatenate(bases), np.concatenate(codes)))
    minb_sum = int(sum(int(base.min()) for base, _ in blocks))
    best_val = DPINF
    for l0, l1 in r6p.LABEL_ORIENTATIONS:
        for s_idx in range(len(tb.s_keys)):
            sw = int(tb.s_wt[s_idx])
            if ob.t_tag * sw + minb_sum - 2 * ob.t_r * positions >= best_val:
                continue
            mask = (tb.sy0[s_idx] == l0) & (tb.sy1[s_idx] == l1)
            if not mask.any():
                continue
            maskc = np.concatenate([mask, mask])
            gs = []
            feasible = True
            for base, code in blocks:
                f = np.full(tb.M, DPINF, dtype=np.int64)
                np.minimum.at(f, code[maskc], base[maskc])
                if int(f.min()) >= DPINF:
                    feasible = False
                    break
                gs.append(r6p._zeta_min(f, positions))
            if not feasible:
                continue
            tot = gs[0] + gs[1] + gs[2] - 2 * ob.t_r * tb.npos + ob.t_tag * sw
            val = int(tot.min())
            if val < best_val:
                best_val = val
    if best_val >= DPINF // 2:
        raise AssertionError("qg2 D++ family produced no feasible point")
    return int(best_val) + ob.family_charge


# ---- hostile parameterized brutes -------------------------------------------


def brute_config_n1_ob(target_pairs, perm_b, perm_c, centrals, ob: Objective):
    sy, lm, lw = h.local_symp, h.local_mul, h.local_wt
    ordered = [
        target_pairs[0],
        target_pairs[1] if perm_b == 0 else (target_pairs[1][1], target_pairs[1][0]),
        target_pairs[2] if perm_c == 0 else (target_pairs[2][1], target_pairs[2][0]),
    ]
    block_letters = [
        (
            h.BITS_CODE[(pair[0][0] & 1, pair[0][1] & 1)],
            h.BITS_CODE[(pair[1][0] & 1, pair[1][1] & 1)],
        )
        for pair in ordered
    ]
    multipliers = []
    for central in centrals:
        multipliers.extend(
            (ob.t_c if central == 0 else ob.t_nc, ob.t_c if central == 1 else ob.t_nc)
        )
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
        raw = sum(m * lw(r) for m, r in zip(multipliers, frames)) + ob.t_tag * lw(s)
        for k in range(2):
            triple = tuple(lm(block_letters[j][k], frames[2 * j + k]) for j in range(3))
            if triple[0] == triple[1] == triple[2] != 0:
                raw += ob.t_r
            else:
                raw += ob.t_r * (lw(triple[0]) + lw(triple[1]) + lw(triple[2]))
        cost = raw - ob.base_const
        if best is None or cost < best:
            best = cost
    return best


def brute_config_n2_ob(target_pairs, perm_b, perm_c, centrals, ob: Objective):
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
                m0 = ob.t_c if centrals[j] == 0 else ob.t_nc
                m1 = ob.t_c if centrals[j] == 1 else ob.t_nc
                base = np.empty(len(pairs), dtype=np.int64)
                letter = np.empty((len(pairs), 2, n), dtype=np.int64)
                for idx, (r0, r1) in enumerate(pairs):
                    t0 = p10.mul(ordered[j][0], r0)
                    t1 = p10.mul(ordered[j][1], r1)
                    base[idx] = (
                        m0 * (p10.wt(r0) - 1)
                        + m1 * (p10.wt(r1) - 1)
                        + ob.t_r * (p10.wt(t0) + p10.wt(t1))
                    )
                    for q in range(n):
                        letter[idx, 0, q] = h.BITS_CODE[((t0[0] >> q) & 1, (t0[1] >> q) & 1)]
                        letter[idx, 1, q] = h.BITS_CODE[((t1[0] >> q) & 1, (t1[1] >> q) & 1)]
                per_block.append((base, letter))
            (base_a, la), (base_b, lb), (base_c, lc) = per_block
            total = (
                base_a[:, None, None]
                + base_b[None, :, None]
                + base_c[None, None, :]
                + ob.t_tag * p10.wt(s)
            )
            for k in range(2):
                for q in range(n):
                    xa = la[:, k, q][:, None, None]
                    xb = lb[:, k, q][None, :, None]
                    xc = lc[:, k, q][None, None, :]
                    total = total - 2 * ob.t_r * ((xa == xb) & (xa == xc) & (xa != 0))
            value = int(total.min())
            if best is None or value < best:
                best = value
    return best


def hostile_gates() -> dict[str, Any]:
    frame_o0, tag_o0, f3_o0 = _obj_tables(OB_O0)
    f3_binds = bool(np.array_equal(f3_o0, r6m._F3))
    frame_binds = all(
        bool(np.array_equal(frame_o0[c], r6m._FRAME_COST[c])) for c in CENTRALS8
    )
    tag_binds = bool(np.array_equal(tag_o0, r6m._TAG_COST))
    # frozen deterministic (p6, centrals) sample: 64 configurations
    table_rows = 0
    table_ok = True
    for i in range(64):
        code = (i * 2654435761) % 4096
        p6 = tuple((code >> (2 * (5 - t))) & 3 for t in range(6))
        centrals = CENTRALS8[i % 8]
        mine, _ = local_table_ob(p6, centrals, OB_O0)
        theirs, _ = r6m._local_table(p6, centrals)
        table_rows += 1
        if not np.array_equal(mine, theirs):
            table_ok = False
    # DP vs independent brute, both objectives, all 32 configs per panel
    brute_ok = True
    configs = 0
    for name, letter_pairs in sorted(r6m._HOSTILE_N1_PANELS.items()):
        target_pairs = tuple(
            (r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in letter_pairs
        )
        for ob in (OB_O0, OB_O1):
            for perm_b, perm_c in itertools.product((0, 1), repeat=2):
                for centrals in CENTRALS8:
                    dp_v = dp_config_cost_ob(target_pairs, perm_b, perm_c, centrals, 1, ob)
                    br_v = brute_config_n1_ob(target_pairs, perm_b, perm_c, centrals, ob)
                    configs += 1
                    if dp_v is None or br_v is None or dp_v != br_v:
                        brute_ok = False
    for name, tp in sorted(r6m._HOSTILE_N2_PANELS.items()):
        target_pairs = tuple((tuple(a), tuple(b)) for a, b in tp)
        for ob in (OB_O0, OB_O1):
            for perm_b, perm_c in itertools.product((0, 1), repeat=2):
                for centrals in CENTRALS8:
                    dp_v = dp_config_cost_ob(target_pairs, perm_b, perm_c, centrals, 2, ob)
                    br_v = brute_config_n2_ob(target_pairs, perm_b, perm_c, centrals, ob)
                    configs += 1
                    if dp_v is None or br_v is None or dp_v != br_v:
                        brute_ok = False
    gates = {
        "f3_table_binds_at_baseline": f3_binds,
        "frame_cost_table_binds_at_baseline": frame_binds,
        "tag_cost_table_binds_at_baseline": tag_binds,
        "local_table_binding_rows": table_rows,
        "local_table_binds_at_baseline": table_ok,
        "dp_vs_brute_configs": configs,
        "dp_vs_brute_exact_O0_O1": brute_ok,
        "rotation_constant_is_nine": r6m.ROTATIONS_R6M == 9,
        "stack_rotation_constant_is_ten": r6m.ROTATIONS_TWO_M3 == 10,
    }
    if not all(v for v in gates.values() if isinstance(v, bool)):
        raise AssertionError({"qg2_hostile_failure": gates})
    return gates


# ---- instance evaluation ----------------------------------------------------


def evaluate_rows(target_pairs, n: int, c_dp_o0: int, c_dp_o1: int, prim: Primitives,
                  feats: dict) -> dict[str, dict]:
    rows = {}
    for ob, c_dp in ((OB_O0, c_dp_o0 + OB_O0.family_charge),
                     (OB_O1, c_dp_o1),
                     (OB_O2, c_dp_o0 + O2_SHIFT)):
        c_r6l, c_dplus, f_b = score_families(prim, ob)
        if not (c_dp <= c_dplus <= c_r6l):
            raise AssertionError(
                {"qg2_sandwich_violated": [ob.name, c_dp, c_dplus, c_r6l]}
            )
        if f_b < INF and c_dp > f_b:
            raise AssertionError({"qg2_borrow_soundness_violated": [ob.name, c_dp, f_b]})
        rows[ob.name] = {
            "C_DP": int(c_dp),
            "C_Dplus": int(c_dplus),
            "C_R6L": int(c_r6l),
            "f_B": int(f_b),
            "Gsplit": int(c_r6l - c_dplus),
            "donor_exact": c_dp == c_r6l,
            "regime_split": c_dp == c_dplus < c_r6l,
            "regime_borrow": c_dp < c_dplus,
            "identity_two_trade": c_dp == min(c_r6l, c_dplus, f_b),
            **feats,
        }
    return rows


def regime_of(row) -> str:
    if row["donor_exact"]:
        return "DONOR_EXACT"
    if row["regime_borrow"]:
        return "BORROW"
    if row["regime_split"]:
        return "SPLIT"
    return "OTHER"


def predicate_p1(row) -> bool:
    return row["Gsplit"] == 0 and row["f_B"] >= row["C_R6L"]


# ---- panels -----------------------------------------------------------------


def structured_panel(bindings: dict) -> dict[str, Any]:
    wt1 = [r6o._letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    rows_by_ob = {"O0": [], "O1": [], "O2": []}
    instance_meta = []
    dplus_bind_ok = True
    dplus_bind_rows = 0
    r6l_bind_ok = True
    r6l_bind_rows = 0
    borrow_bind_ok = True
    borrow_bind_rows = 0
    idx = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 512 == 0:
            clear_caches()
        target_pairs = tuple(
            (wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic)
        )
        c_dp_o0 = r6o.dp_cost_n2_reader(target_pairs)
        c_dp_o1 = dp_cost_n2_ob(target_pairs, OB_O1)
        prim = compute_primitives(target_pairs, 2)
        feats = r6q.simple_features(target_pairs, 2)
        rows = evaluate_rows(target_pairs, 2, c_dp_o0, c_dp_o1, prim, feats)
        for name in rows_by_ob:
            rows[name]["instance_index"] = idx
            rows_by_ob[name].append(rows[name])
        instance_meta.append((ia, ib, ic))
        if idx % 500 == 0:
            dplus_bind_rows += 1
            if int(r6o.dplus_pairs(target_pairs, 2)["C_Dplus"]) != rows["O0"]["C_Dplus"]:
                dplus_bind_ok = False
            r6l_bind_rows += 1
            terms = r6m._synthetic_terms(target_pairs)
            if int(r6m.donor_r6l_matching(terms, MATCHING, 2, list(range(6)))["C_R6L"]) \
                    != rows["O0"]["C_R6L"]:
                r6l_bind_ok = False
        if idx % 1000 == 0:
            borrow_bind_rows += 1
            fb_ref = r6q.borrow_family_min(target_pairs, 2)
            fb_mine = rows["O0"]["f_B"]
            if fb_ref is None:
                if fb_mine != INF:
                    borrow_bind_ok = False
            elif fb_ref != fb_mine:
                borrow_bind_ok = False
        idx += 1
    clear_caches()
    r6o._block_cache.clear()
    r6q._borrow_block_cache.clear()
    bindings["structured_dplus_binding"] = {"rows": dplus_bind_rows, "ok": dplus_bind_ok}
    bindings["structured_r6l_binding"] = {"rows": r6l_bind_rows, "ok": r6l_bind_ok}
    bindings["structured_borrow_binding"] = {"rows": borrow_bind_rows, "ok": borrow_bind_ok}
    return {
        "rows_by_ob": rows_by_ob,
        "instance_meta": instance_meta,
        "wt1": wt1,
        "upairs": upairs,
    }


def structured_instance_verbatim(meta, upairs, wt1, idx):
    ia, ib, ic = meta[idx]
    target_pairs = tuple((wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic))
    return {
        "instance_index": int(idx),
        "block_pairs": [list(upairs[s]) for s in (ia, ib, ic)],
        "targets": [[list(a), list(b)] for a, b in target_pairs],
    }, target_pairs


def random_panel(bindings: dict) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    rows_by_ob = {"O0": [], "O1": [], "O2": []}
    meta = []
    dplus_bind = [0, True]
    r6l_bind = [0, True]
    borrow_bind = [0, True]
    for n in (2, 3):
        for i in range(RANDOM_PER_N):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            target_pairs = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            terms = r6m._synthetic_terms(target_pairs)
            clear_caches()
            c_dp_o0 = r6o.dp_cost_frozen_configs(terms, n)
            if n == 2:
                c_dp_o1 = dp_cost_n2_ob(target_pairs, OB_O1)
            else:
                c_dp_o1 = dp_cost_pairs_ob(target_pairs, n, OB_O1)
            prim = compute_primitives(target_pairs, n)
            feats = r6q.simple_features(target_pairs, n)
            rows = evaluate_rows(target_pairs, n, c_dp_o0, c_dp_o1, prim, feats)
            for name in rows_by_ob:
                rows[name]["n"] = n
                rows[name]["index"] = i
                rows_by_ob[name].append(rows[name])
            meta.append((n, i, targets))
            if i % 10 == 0:
                dplus_bind[0] += 1
                if int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"]) != rows["O0"]["C_Dplus"]:
                    dplus_bind[1] = False
            if i % 20 == 0:
                r6l_bind[0] += 1
                if int(r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"]) \
                        != rows["O0"]["C_R6L"]:
                    r6l_bind[1] = False
            if i % 30 == 0:
                borrow_bind[0] += 1
                fb_ref = r6q.borrow_family_min(target_pairs, n)
                fb_mine = rows["O0"]["f_B"]
                if (fb_ref is None and fb_mine != INF) or (
                    fb_ref is not None and fb_ref != fb_mine
                ):
                    borrow_bind[1] = False
            r6q._borrow_block_cache.clear()
    r6o._block_cache.clear()
    bindings["random_dplus_binding"] = {"rows": dplus_bind[0], "ok": dplus_bind[1]}
    bindings["random_r6l_binding"] = {"rows": r6l_bind[0], "ok": r6l_bind[1]}
    bindings["random_borrow_binding"] = {"rows": borrow_bind[0], "ok": borrow_bind[1]}
    return {"rows_by_ob": rows_by_ob, "meta": meta}


def chemistry_panel(bindings: dict) -> dict[str, Any]:
    r6m_receipt = json.loads(
        (ORION_Q / "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json").read_text()
    )
    r6o_receipt = json.loads(
        (ORION_Q / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json").read_text()
    )
    r6q_receipt = json.loads(
        (ORION_Q / "MAX_R6Q_REGIME_PREDICATE_RESULTS.json").read_text()
    )
    rows_by_ob = {"O0": [], "O1": [], "O2": []}
    meta = []
    subjects = {}
    receipt_bind_ok = True
    o0_dp_bind = [0, True]
    o2_comparator = {}
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        terms, source_indices, _champ, _mi, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"qg2_chemistry_blob_mismatch": name})
        n = int(cfg["n_qubits"])
        six = [int(i) for i in source_indices]
        rec_sub = r6m_receipt["subjects"][name]
        if sorted(six) != sorted(int(i) for i in rec_sub["frozen_source_indices"]):
            raise AssertionError({"qg2_chemistry_source_indices_mismatch": name})
        rec_rows = {
            canonical_json(row["matching"]): row for row in rec_sub["candidate_points"]
        }
        r6o_rows = {
            canonical_json(row["matching"]): row
            for row in r6o_receipt["domains"]["chemistry"]["subjects"][name]["rows"]
        }
        r6q_rows = {
            canonical_json(row["matching"]): row
            for row in r6q_receipt["panels"]["chemistry"]["rows"][name]
        }
        matchings = r6m.perfect_matchings(six)
        sub_count = 0
        for m_idx, pairs in enumerate(matchings):
            key = canonical_json([list(p) for p in pairs])
            rec_row = rec_rows[key]
            c_dp_o0 = int(rec_row["C_R6M"])
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            clear_caches()
            prim = compute_primitives(target_pairs, n)
            feats = r6q.simple_features(target_pairs, n)
            c_dp_o1 = dp_cost_pairs_ob(target_pairs, n, OB_O1)
            rows = evaluate_rows(target_pairs, n, c_dp_o0, c_dp_o1, prim, feats)
            # receipt binding of the full baseline quadruple
            if (
                rows["O0"]["C_R6L"] != int(rec_row["C_R6L_same_matching"])
                or rows["O0"]["C_Dplus"] != int(r6o_rows[key]["C_Dplus"])
                or rows["O0"]["C_DP"] != int(r6q_rows[key]["C_DP"])
                or rows["O0"]["f_B"] != int(r6q_rows[key]["f_B"])
            ):
                receipt_bind_ok = False
            if m_idx < 3:
                o0_dp_bind[0] += 1
                if dp_cost_pairs_ob(target_pairs, n, OB_O0) != c_dp_o0:
                    o0_dp_bind[1] = False
            for ob_name in rows_by_ob:
                rows[ob_name]["subject"] = name
                rows[ob_name]["matching"] = [list(p) for p in pairs]
                rows_by_ob[ob_name].append(rows[ob_name])
            meta.append((name, [list(p) for p in pairs], n))
            sub_count += 1
            r6q._borrow_block_cache.clear()
        r6o._block_cache.clear()
        subjects[name] = {"n_qubits": n, "matchings": sub_count,
                          "source_blob_verified": True}
        # O2 cross-family comparator re-pricing from the committed receipt points
        donor_points = list(rec_sub["donor_stack_points"]) + [
            {k: v for k, v in row.items() if k != "witness"}
            for row in rec_sub["donor_r6l_points"]
        ]
        comp_rows = []
        for cand in rec_sub["candidate_points"]:
            lam = float(cand["Lambda_R6M"])
            eligible = [pt for pt in donor_points if float(pt["Lambda"]) <= lam + TOL]
            mode = "MATCHED_LOWER_ENVELOPE" if eligible else "CONSERVATIVE_GLOBAL_COST_FLOOR"
            pool = eligible if eligible else donor_points
            best = min(
                pool,
                key=lambda pt: (
                    int(pt["C"]) + OB_O2.rho * int(pt["rotations"]),
                    float(pt["Lambda"]),
                    pt["point_kind"],
                    canonical_json(pt["point_id"]),
                ),
            )
            priced_inc = int(best["C"]) + OB_O2.rho * int(best["rotations"])
            cand_priced = int(cand["C_R6M"]) + OB_O2.rho * ROTATIONS_FAMILY
            delta_o2 = priced_inc - cand_priced
            comp_rows.append(
                {
                    "matching": cand["matching"],
                    "delta_baseline": int(cand["delta_vs_incumbent"]),
                    "delta_O2": int(delta_o2),
                    "incumbent_kind_O2": best["point_kind"],
                    "incumbent_rotations_O2": int(best["rotations"]),
                    "comparator_mode": mode,
                    "strict_O2": delta_o2 > 0,
                }
            )
        o2_comparator[name] = {
            "rows": comp_rows,
            "strict_count_O2": sum(r["strict_O2"] for r in comp_rows),
            "strict_count_baseline": sum(
                bool(c["strict_budget_matched_improvement"])
                for c in rec_sub["candidate_points"]
            ),
            "deltas_changed_count": sum(
                r["delta_O2"] != r["delta_baseline"] for r in comp_rows
            ),
            "envelope_all_nine_rotation_O2": all(
                r["incumbent_rotations_O2"] == 9 for r in comp_rows
            ),
        }
    bindings["chemistry_receipt_binding_all_30"] = receipt_bind_ok
    bindings["chemistry_o0_general_dp_binding"] = {
        "rows": o0_dp_bind[0], "ok": o0_dp_bind[1]
    }
    return {
        "rows_by_ob": rows_by_ob,
        "meta": meta,
        "subjects": subjects,
        "o2_cross_family_comparator": o2_comparator,
    }


# ---- support-2 sufficiency (parameterized D++ on criticals) ------------------


def support2_analysis(structured, random_p, chem, witnesses: dict) -> dict[str, Any]:
    out = {}
    su = structured
    for ob in (OB_O0, OB_O1, OB_O2):
        crit_struct = [
            row["instance_index"]
            for row in su["rows_by_ob"][ob.name]
            if row["C_Dplus"] > row["C_DP"]
        ]
        crit_random = [
            k
            for k, row in enumerate(random_p["rows_by_ob"][ob.name])
            if row["C_Dplus"] > row["C_DP"]
        ]
        chem_unpinched = [
            k
            for k, row in enumerate(chem["rows_by_ob"][ob.name])
            if row["C_Dplus"] > row["C_DP"]
        ]
        entry = {
            "critical_structured": len(crit_struct),
            "critical_random": len(crit_random),
            "chemistry_unpinched": len(chem_unpinched),
            "chemistry_support2_unresolved": len(chem_unpinched),
        }
        if ob.name == "O2":
            # exact constant-shift lemma: O2 == O0 + 45 within family
            entry["closure_mode"] = "DERIVED_FROM_O0_BY_CONSTANT_SHIFT_LEMMA"
            entry["closed_count"] = out["O0"]["closed_count"]
            entry["failure_count"] = out["O0"]["failure_count"]
            entry["dxx_binding"] = None
            out[ob.name] = entry
            continue
        failures = []
        closed = 0
        dxx_bind_rows = 0
        dxx_bind_ok = True
        run_struct = crit_struct if ob.name != "O0" else crit_struct[:12]
        for pos, idx in enumerate(run_struct):
            verb, target_pairs = structured_instance_verbatim(
                su["instance_meta"], su["upairs"], su["wt1"], idx
            )
            c_dxx = dxx_cost_ob(target_pairs, 2, ob)
            row = su["rows_by_ob"][ob.name][idx]
            if not (row["C_DP"] <= c_dxx <= row["C_Dplus"]):
                raise AssertionError({"qg2_dxx_sandwich_violated": [ob.name, idx]})
            if ob.name == "O0":
                dxx_bind_rows += 1
                if c_dxx - ob.family_charge != int(
                    r6p.dxx_search(target_pairs, 2)["C_Dxx"]
                ):
                    dxx_bind_ok = False
            if c_dxx == row["C_DP"]:
                closed += 1
            else:
                failures.append(
                    {"panel": "structured", **verb, "C_DP": row["C_DP"],
                     "C_Dxx": int(c_dxx), "C_Dplus": row["C_Dplus"]}
                )
        for k in crit_random:
            n, i, targets = random_p["meta"][k]
            target_pairs = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            c_dxx = dxx_cost_ob(target_pairs, n, ob)
            row = random_p["rows_by_ob"][ob.name][k]
            if not (row["C_DP"] <= c_dxx <= row["C_Dplus"]):
                raise AssertionError({"qg2_dxx_sandwich_violated_random": [ob.name, n, i]})
            if c_dxx == row["C_DP"]:
                closed += 1
            else:
                failures.append(
                    {"panel": "random", "n": n, "index": i,
                     "targets": [list(t) for t in targets],
                     "C_DP": row["C_DP"], "C_Dxx": int(c_dxx),
                     "C_Dplus": row["C_Dplus"]}
                )
        entry["closure_mode"] = (
            "DXX_ON_FIRST_12_STRUCTURED_CRITICALS_PLUS_RANDOM__REST_BY_R6P_RECEIPT"
            if ob.name == "O0"
            else "DXX_ON_ALL_CRITICALS_N_LE_3__CHEMISTRY_BY_PINCH_OR_UNRESOLVED"
        )
        entry["closed_count"] = closed
        entry["failure_count"] = len(failures)
        entry["dxx_binding"] = (
            {"rows": dxx_bind_rows, "ok": dxx_bind_ok} if ob.name == "O0" else None
        )
        if failures:
            wl = witnesses.setdefault(ob.name, {}).setdefault("NEW_SUPPORT3", [])
            for f in failures[:WITNESS_CAP]:
                if f["panel"] == "structured":
                    _, tps = structured_instance_verbatim(
                        su["instance_meta"], su["upairs"], su["wt1"], f["instance_index"]
                    )
                else:
                    tps = tuple(
                        (tuple(f["targets"][2 * j]), tuple(f["targets"][2 * j + 1]))
                        for j in range(3)
                    )
                nn = 2 if f["panel"] == "structured" else f["n"]
                wl.append({**f, "dp_witness": dp_witness_ob(tps, nn, ob)})
        out[ob.name] = entry
    return out


# ---- summaries, predicate, verdicts -----------------------------------------


def panel_regime_summary(rows) -> dict[str, Any]:
    return {
        "instances": len(rows),
        "donor_exact_count": sum(r["donor_exact"] for r in rows),
        "regime_split_count": sum(r["regime_split"] for r in rows),
        "regime_borrow_count": sum(r["regime_borrow"] for r in rows),
        "identity_two_trade_count": sum(r["identity_two_trade"] for r in rows),
        "confusion_P1": r6q.confusion(rows, predicate_p1),
    }


def collect_identity_failures(panels_rows, ob: Objective, witnesses):
    total = 0
    for panel_name, rows, meta_fn in panels_rows:
        for k, row in enumerate(rows):
            if not row["identity_two_trade"]:
                total += 1
                wl = witnesses.setdefault(ob.name, {}).setdefault(
                    "NEW_BEYOND_TWO_TRADES", []
                )
                if len(wl) < WITNESS_CAP:
                    verb, target_pairs, nn = meta_fn(k)
                    wl.append(
                        {
                            "panel": panel_name,
                            **verb,
                            "C_DP": row["C_DP"],
                            "C_R6L": row["C_R6L"],
                            "C_Dplus": row["C_Dplus"],
                            "f_B": row["f_B"],
                            "dp_witness": dp_witness_ob(target_pairs, nn, ob),
                        }
                    )
    return total


def main() -> dict[str, Any]:
    start = time.monotonic()
    bindings: dict[str, Any] = {}
    hostile = hostile_gates()

    structured = structured_panel(bindings)
    random_p = random_panel(bindings)
    chem = chemistry_panel(bindings)

    # baseline binding to the committed R6Q receipt (frozen constants)
    o0_struct = panel_regime_summary(structured["rows_by_ob"]["O0"])
    baseline_counts_ok = (
        o0_struct["instances"] == 9261
        and o0_struct["donor_exact_count"] == 6453
        and o0_struct["regime_split_count"] == 2322
        and o0_struct["regime_borrow_count"] == 486
        and o0_struct["identity_two_trade_count"] == 9261
        and o0_struct["confusion_P1"]["errors"] == 0
    )
    bindings["baseline_structured_counts_match_r6q_receipt"] = baseline_counts_ok

    witnesses: dict[str, Any] = {}
    support2 = support2_analysis(structured, random_p, chem, witnesses)

    su = structured

    def struct_meta(k):
        verb, tps = structured_instance_verbatim(
            su["instance_meta"], su["upairs"], su["wt1"], k
        )
        return verb, tps, 2

    def random_meta(k):
        n, i, targets = random_p["meta"][k]
        tps = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
        return {"n": n, "index": i, "targets": [list(t) for t in targets]}, tps, n

    _batch_cache: dict[str, Any] = {}

    def chem_meta(k):
        name, matching, n = chem["meta"][k]
        pairs = tuple(tuple(p) for p in matching)
        if name not in _batch_cache:
            _batch_cache[name] = r6f._frozen_batch(p10.base.SUBJECTS[name])[0]
        terms = _batch_cache[name]
        tps = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
        return {"subject": name, "matching": matching}, tps, n

    objective_reports = {}
    verdicts = {}
    for ob in ALT_OBJECTIVES:
        name = ob.name
        panels = {
            "structured_n2": panel_regime_summary(structured["rows_by_ob"][name]),
            "random_20260823": panel_regime_summary(random_p["rows_by_ob"][name]),
            "chemistry": panel_regime_summary(chem["rows_by_ob"][name]),
        }
        identity_failures = collect_identity_failures(
            (
                ("structured", structured["rows_by_ob"][name], struct_meta),
                ("random", random_p["rows_by_ob"][name], random_meta),
                ("chemistry", chem["rows_by_ob"][name], chem_meta),
            ),
            ob,
            witnesses,
        )
        # membership transitions vs baseline
        transitions: dict[str, int] = {}
        transition_witnesses: dict[str, list] = {}
        for panel_name, rows, base_rows, meta_fn in (
            ("structured", structured["rows_by_ob"][name],
             structured["rows_by_ob"]["O0"], struct_meta),
            ("random", random_p["rows_by_ob"][name],
             random_p["rows_by_ob"]["O0"], random_meta),
            ("chemistry", chem["rows_by_ob"][name],
             chem["rows_by_ob"]["O0"], chem_meta),
        ):
            for k, (row, base) in enumerate(zip(rows, base_rows)):
                a, b = regime_of(base), regime_of(row)
                if a != b:
                    tkey = f"{a}->{b}"
                    transitions[tkey] = transitions.get(tkey, 0) + 1
                    wl = transition_witnesses.setdefault(tkey, [])
                    if len(wl) < WITNESS_CAP:
                        verb, _tps, _n = meta_fn(k)
                        wl.append(
                            {
                                "panel": panel_name,
                                **verb,
                                "baseline": {kk: base[kk] for kk in
                                             ("C_DP", "C_Dplus", "C_R6L", "f_B")},
                                name: {kk: row[kk] for kk in
                                       ("C_DP", "C_Dplus", "C_R6L", "f_B")},
                            }
                        )
        membership_identical = not transitions
        # trades alive/dead + minimal witnesses
        trade_report = {}
        for trade, pred in (
            ("SPLIT", lambda r: r["regime_split"]),
            ("BORROW", lambda r: r["regime_borrow"]),
        ):
            alive_struct = [
                k for k, r in enumerate(structured["rows_by_ob"][name]) if pred(r)
            ]
            alive_random = [
                k for k, r in enumerate(random_p["rows_by_ob"][name]) if pred(r)
            ]
            alive_chem = [
                k for k, r in enumerate(chem["rows_by_ob"][name]) if pred(r)
            ]
            rec = {
                "alive": bool(alive_struct or alive_random or alive_chem),
                "structured_count": len(alive_struct),
                "random_count": len(alive_random),
                "chemistry_count": len(alive_chem),
            }
            if alive_struct:
                verb, _tps, _n = struct_meta(alive_struct[0])
                row = structured["rows_by_ob"][name][alive_struct[0]]
                rec["minimal_witness"] = {
                    "panel": "structured",
                    **verb,
                    "costs": {kk: row[kk] for kk in ("C_DP", "C_Dplus", "C_R6L", "f_B")},
                }
            elif alive_random:
                verb, _tps, _n = random_meta(alive_random[0])
                row = random_p["rows_by_ob"][name][alive_random[0]]
                rec["minimal_witness"] = {
                    "panel": "random",
                    **verb,
                    "costs": {kk: row[kk] for kk in ("C_DP", "C_Dplus", "C_R6L", "f_B")},
                }
            else:
                rec["minimal_witness"] = None
            trade_report[trade] = rec
        new_trade_classes = sorted(witnesses.get(name, {}).keys())
        # predicate transfer
        p1_errors = sum(
            panels[p]["confusion_P1"]["errors"] for p in panels
        )
        reinduction = None
        if p1_errors > 0:
            fit = r6q.fit_p2(structured["rows_by_ob"][name])
            p2 = r6q.make_p2_pred(fit["literals"])
            reinduction = {
                "fit": fit,
                "confusion": {
                    p: r6q.confusion(rows, p2)
                    for p, rows in (
                        ("structured_n2", structured["rows_by_ob"][name]),
                        ("random_20260823", random_p["rows_by_ob"][name]),
                        ("chemistry", chem["rows_by_ob"][name]),
                    )
                },
            }
            reinduced_errors = sum(
                c["errors"] for c in reinduction["confusion"].values()
            )
            predicate_verdict = (
                "RE_INDUCED_EXACT" if reinduced_errors == 0 else "OBJECTIVE_SPECIFIC"
            )
        else:
            predicate_verdict = "TRANSFERS_EXACTLY"
        chem_rows = chem["rows_by_ob"][name]
        chem_donor_exact = sum(r["donor_exact"] for r in chem_rows)
        s2 = support2[name]
        support2_all_closed = s2["failure_count"] == 0
        chem_unresolved = s2["chemistry_support2_unresolved"]
        identity_all = identity_failures == 0
        robust = (
            membership_identical
            and identity_all
            and support2_all_closed
            and chem_unresolved == 0
            and p1_errors == 0
            and chem_donor_exact == 30
        )
        verdict = "GEOMETRY_ROBUST" if robust else "GEOMETRY_OBJECTIVE_DEPENDENT"
        verdicts[name] = verdict
        objective_reports[name] = {
            "weights": {"t_nc": ob.t_nc, "t_c": ob.t_c, "t_tag": ob.t_tag,
                        "t_r": ob.t_r, "rho_per_rotation": ob.rho},
            "verdict": verdict,
            "panels": panels,
            "membership_identical_to_baseline": membership_identical,
            "membership_transitions": transitions,
            "membership_transition_witnesses": transition_witnesses,
            "trades": trade_report,
            "identity_two_trade_failures": identity_failures,
            "new_trade_classes": new_trade_classes,
            "support2": s2,
            "chemistry_donor_exact_count": int(chem_donor_exact),
            "chemistry_donor_exact_all_30": chem_donor_exact == 30,
            "predicate": {
                "form": "P1_ob := [Gsplit_ob == 0] AND [f_B_ob >= C_R6L_ob]",
                "verdict": predicate_verdict,
                "errors_total": int(p1_errors),
                "confusion": {p: panels[p]["confusion_P1"] for p in panels},
                "reinduction": reinduction,
            },
            "new_trade_witnesses": witnesses.get(name, {}),
        }
    if all(v == "GEOMETRY_ROBUST" for v in verdicts.values()):
        overall = "GEOMETRY_ROBUST"
    elif all(v == "GEOMETRY_OBJECTIVE_DEPENDENT" for v in verdicts.values()):
        overall = "GEOMETRY_OBJECTIVE_DEPENDENT"
    else:
        overall = "MIXED"
    authority = (
        "ORIONQ_QG2_OBJECTIVE_ROBUSTNESS_"
        + overall
        + "__FROZEN_REWEIGHTED_OBJECTIVES__NOT_R6"
    )

    gates = {
        "hostile_all_pass": True,  # hard-asserted inside hostile_gates
        "baseline_structured_counts_match_r6q_receipt": baseline_counts_ok,
        "structured_dplus_binding": bindings["structured_dplus_binding"]["ok"],
        "structured_r6l_binding": bindings["structured_r6l_binding"]["ok"],
        "structured_borrow_binding": bindings["structured_borrow_binding"]["ok"],
        "random_dplus_binding": bindings["random_dplus_binding"]["ok"],
        "random_r6l_binding": bindings["random_r6l_binding"]["ok"],
        "random_borrow_binding": bindings["random_borrow_binding"]["ok"],
        "chemistry_receipt_binding_all_30": bindings["chemistry_receipt_binding_all_30"],
        "chemistry_o0_general_dp_binding": bindings["chemistry_o0_general_dp_binding"]["ok"],
        "o0_dxx_binding": support2["O0"]["dxx_binding"]["ok"],
        "o0_criticals_are_486": support2["O0"]["critical_structured"] == 486,
        "o0_support2_failures_zero": support2["O0"]["failure_count"] == 0,
        "sandwich_and_soundness_asserted": True,
        "o2_constant_shift_lemma_premises": hostile["rotation_constant_is_nine"]
        and hostile["stack_rotation_constant_is_ten"],
        "no_new_subject_data": True,
    }
    if not all(gates.values()):
        raise AssertionError({"qg2_integrity_gate_failure": gates})

    result = {
        "schema": "ORIONQG.QG2.ObjectiveRobustness.v1",
        "lane": "QG-2",
        "authority": authority,
        "scope": (
            "TARE_REGIME_GEOMETRY_REMAP_UNDER_FROZEN_REWEIGHTED_OBJECTIVES__"
            "EXPLANATORY_GEOMETRY_ONLY__NOT_R6"
        ),
        "responsibility": (
            "RESP:PER_OBJECTIVE_REGIME_MAPS_TRADE_PROFITABILITY_AND_PREDICATE_"
            "TRANSFER_REPORTED_WITH_WITNESSES"
        ),
        "protocol": "QG2_OBJECTIVE_ROBUSTNESS_PROTOCOL (development/orion-qg-regime-geometry)",
        "charter": "PROGRAMME_CHARTER_V1 lane QG-2",
        "outcome_overall": overall,
        "objectives": objective_reports,
        "baseline_control_O0": {
            "weights": {"t_nc": 4, "t_c": 2, "t_tag": 2, "t_r": 1,
                        "rho_per_rotation": 0},
            "role": "binding control only; not a new result",
            "structured_summary": o0_struct,
            "random_summary": panel_regime_summary(random_p["rows_by_ob"]["O0"]),
            "chemistry_summary": panel_regime_summary(chem["rows_by_ob"]["O0"]),
            "support2": support2["O0"],
        },
        "o2_within_family_note": (
            "Every member of the frozen grammar family carries exactly 9 rotations "
            "(committed constant), so O2 within-family costs are O0 costs plus the "
            "constant 45 and all within-family differences, regimes, trades and the "
            "predicate are exactly invariant; O2 rows are derived under this lemma. "
            "The substantive O2 content is the cross-family comparator re-pricing."
        ),
        "o2_cross_family_comparator": chem["o2_cross_family_comparator"],
        "chemistry_subjects": chem["subjects"],
        "hostile": hostile,
        "bindings": bindings,
        "gates": gates,
        "random_seed": RANDOM_SEED,
        "random_panel_size": 2 * RANDOM_PER_N,
        "witness_cap": WITNESS_CAP,
        "claim_boundary": {
            "covers": (
                "Re-mapping of the frozen R6M grammar regime geometry (donor "
                "optimality, split and borrow trades, support-2 sufficiency, R6Q "
                "predicate) under two frozen linear re-weightings of the structural "
                "cost coordinates plus a rotation charge, on the stated finite "
                "domains."
            ),
            "machine_evidenced_only": (
                "All per-objective claims are machine-evidenced only on the "
                "exhaustive structured n=2 slice, the 120-instance seeded random "
                "panel (seed 20260823, n=2..3), and the 30 recorded chemistry "
                "matchings; support-2 sufficiency at chemistry is resolved only by "
                "the containment pinch and reported UNRESOLVED where the pinch "
                "fails. Nothing here is a theorem for all n or all objectives."
            ),
            "does_not_cover": (
                "Objectives outside the frozen linear family, other grammars, "
                "re-derivation of the two-M3 donor stack under O1 weights (the O1 "
                "cross-family comparison is out of scope by protocol), fresh "
                "subject data, or any donor/R6 novelty claim."
            ),
        },
        "chemistry_sources_read_via_frozen_batch_only": True,
        "heavy_subject_dp_rerun_baseline": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG2 authority ceiling violated")
    (HERE / "QG2_OBJECTIVE_ROBUSTNESS_RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("ORIONQ_QG2_OBJECTIVE_ROBUSTNESS=" + canonical_json(result))
    print("qg2_runtime_seconds=%.3f" % (time.monotonic() - start), file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
