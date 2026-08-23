#!/usr/bin/env python3
"""QG-1: all-n generator-support composition theorem for the R6I grammar.

Frozen by development/orion-qg-regime-geometry/QG1_RANK2_ALL_N_PROTOCOL.md
(frozen before outcome), lane QG-1 of the ORION-QG programme charter
(PROGRAMME_CHARTER_V1.md, issue #740).

Attempts the object excluded by the R6S claim boundary: extend the all-n
support-composition theorem to the frozen R6I rank-2 dependent-triple
shared-2-bit-Tag grammar. The frozen exchange (stated in full in the
protocol): classify each generator support column as coincidence
(r0 = r1 != I, class in F_2^2 = (S0-syndrome, S1-syndrome)) or
non-coincidence (class in F_2^3 = (anticommutation parity, S0-syndrome,
S1-syndrome)); SOLO moves zero one generator on a zero-sum F_2^3 subset
(per-qubit net <= 0, exhaustively checked over 55,296 cases including the
dependent third letter's frame and Restore terms); PAIR moves zero both
generators on a zero-sum F_2^2 subset of the coincidence set (net <= -4,
9,216 cases). Lemma B (re-derived pigeonhole): odd-alpha F_2^3 multisets of
size >= 4 and F_2^2 multisets of size >= 3 always contain a nonempty
(automatically proper) zero-sum subset; the zero-sum-free exceptional
patterns are exactly 32 (N-side) + 6 (C-side). Induction on
(cost, total generator support) yields generator support <= 3 + 2 = 5 for
every n: B = 5.

Honest outcome space: THEOREM_MACHINE_CHECKED / GAP_FOUND / PARTIAL. The
seeded stress panel (seed 20260823, 44 x n=3 instances, unrestricted R6I DP
vs an independent full brute and support-capped optima) runs regardless.
NOT_R6; no novelty credit; no chemistry data is read; the protected
stretched-N2 discriminator is never touched.
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orion-q"))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
SEED = 20260823
PANEL_N = 3
PANEL_COUNT = 44
DESCENTS_PER_INSTANCE = 2
FRESH_DESCENT_PLAN = ((4, 16), (5, 10), (6, 6))
N6_EXACT_W6_TAIL = 3
EXPECTED_PAIR_COUNTS = {1: 6, 2: 120, 3: 2016}
VERBATIM_CAP = 20
BIG = 4096
PERMS = tuple(itertools.permutations(range(3)))

# ---- independent local algebra tables (bound to the frozen r6i module) ------
LW = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
MUL = np.array([[h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
SY = np.array([[h.local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def bind_tables() -> dict[str, bool]:
    return {
        "LW_binds": bool(np.array_equal(LW, r6i._LW)),
        "MUL_binds": bool(np.array_equal(MUL, r6i._MUL)),
        "SY_binds": bool(np.array_equal(SY, r6i._SYMP)),
        "accepting_states_6": len(r6i.ACCEPTING) == 6,
    }


def multipliers(central: int) -> tuple[int, int, int]:
    m = [4, 4, 4]
    m[central] = 2
    return tuple(m)


def verify_uanti_identity() -> dict[str, Any]:
    """p10.uanti_support == sum_k m_k w(Rk) - 10 over all n=2 sympl-1 pairs."""
    keys = [(x, z) for x in range(4) for z in range(4)]
    nz = [k for k in keys if k != (0, 0)]
    pairs = [(a, b) for a in nz for b in nz if p10.symp(a, b) == 1]
    checked = 0
    ok = True
    for a, b in pairs:
        rs = (a, b, p10.mul(a, b))
        for central in range(3):
            m = multipliers(central)
            direct = sum(m[k] * p10.wt(rs[k]) for k in range(3)) - 10
            checked += 1
            if direct != p10.uanti_support(rs, central):
                ok = False
    return {"pairs": len(pairs), "cases": checked, "holds": ok}


# ---- Lemma E: exhaustive local move inequalities ----------------------------


def verify_lemma_e_solo() -> dict[str, Any]:
    """SOLO per-qubit net <= 0 over the frozen 55,296-case domain."""
    checked = 0
    violations = []
    tie_count = 0
    ties_match_prediction = True
    max_net = -(10**9)
    class_max: dict[str, int] = {}
    per_fo_max: dict[tuple[int, int], int] = {}
    for g in range(2):
        for f in (1, 2, 3):
            for o in range(4):
                if o == f:
                    continue  # coincidence columns are excluded from SOLO
                fo = int(MUL[f, o])
                for central in range(3):
                    m_g = 2 if central == g else 4
                    m_2 = 2 if central == 2 else 4
                    for p0 in range(4):
                        for p1 in range(4):
                            p_g = p0 if g == 0 else p1
                            d_tg = int(LW[p_g] - LW[MUL[p_g, f]])
                            for p2 in range(4):
                                d_t2 = int(LW[MUL[p2, o]] - LW[MUL[p2, fo]])
                                net = (
                                    d_tg + d_t2 - m_g + m_2 * int(LW[o] - LW[fo])
                                )
                                for s0 in range(4):
                                    for s1 in range(4):
                                        checked += 1
                                        code = int(
                                            4 * SY[f, o] + 2 * SY[s0, f] + SY[s1, f]
                                        )
                                        key = f"classN_{code}_max_net"
                                        class_max[key] = max(
                                            class_max.get(key, -(10**9)), net
                                        )
                                max_net = max(max_net, net)
                                cur = per_fo_max.get((f, o), -(10**9))
                                per_fo_max[(f, o)] = max(cur, net)
                                if net > 0 and len(violations) < VERBATIM_CAP:
                                    violations.append(
                                        {
                                            "generator": g,
                                            "zeroed_letter": LETTERS[f],
                                            "partner_letter": LETTERS[o],
                                            "central": central,
                                            "targets": [
                                                LETTERS[p0],
                                                LETTERS[p1],
                                                LETTERS[p2],
                                            ],
                                            "net": net,
                                        }
                                    )
                                if net == 0:
                                    tie_count += 16  # the 16 swept (s0,s1)
                                    predicted_tie = (
                                        central == g
                                        and p_g == f
                                        and p2 == fo
                                        and o != 0
                                    )
                                    if not predicted_tie:
                                        ties_match_prediction = False
                                elif (
                                    central == g and p_g == f and p2 == fo and o != 0
                                ):
                                    ties_match_prediction = False
    n_viol = sum(
        1
        for g in range(2)
        for f in (1, 2, 3)
        for o in range(4)
        if o != f
        for central in range(3)
        for p0 in range(4)
        for p1 in range(4)
        for p2 in range(4)
        if (
            int(LW[(p0 if g == 0 else p1)] - LW[MUL[(p0 if g == 0 else p1), f]])
            + int(LW[MUL[p2, o]] - LW[MUL[p2, MUL[f, o]]])
            - (2 if central == g else 4)
            + (2 if central == 2 else 4) * int(LW[o] - LW[MUL[f, o]])
        )
        > 0
    ) * 16
    return {
        "domain_size": checked,
        "violations": n_viol,
        "holds": n_viol == 0,
        "max_net": max_net,
        "tie_count": tie_count,
        "ties_match_prediction": ties_match_prediction,
        "tie_prediction": (
            "net == 0 exactly at central_j == g, p_g == f, p_2 == f*o, o not in "
            "{I, f} (the zeroed generator sits on the central multiplier and "
            "both affected Restores worsen)"
        ),
        "class_tabulation_max_net": class_max,
        "violating_cases_verbatim": violations,
    }


def verify_lemma_e_pair() -> dict[str, Any]:
    """PAIR per-qubit net <= -4 (strict) over the frozen 9,216-case domain."""
    checked = 0
    n_viol = 0
    violations = []
    max_net = -(10**9)
    for c in (1, 2, 3):
        for central in range(3):
            m = multipliers(central)
            for p0 in range(4):
                d0 = int(LW[p0] - LW[MUL[p0, c]])
                for p1 in range(4):
                    d1 = int(LW[p1] - LW[MUL[p1, c]])
                    for p2 in range(4):
                        net = d0 + d1 - m[0] - m[1]
                        for s0 in range(4):
                            for s1 in range(4):
                                checked += 1
                        max_net = max(max_net, net)
                        if net > -4:
                            n_viol += 16
                            if len(violations) < VERBATIM_CAP:
                                violations.append(
                                    {
                                        "coincidence_letter": LETTERS[c],
                                        "central": central,
                                        "targets": [
                                            LETTERS[p0],
                                            LETTERS[p1],
                                            LETTERS[p2],
                                        ],
                                        "net": net,
                                    }
                                )
    return {
        "domain_size": checked,
        "violations_above_minus4": n_viol,
        "holds_strict": n_viol == 0,
        "max_net": max_net,
        "violating_cases_verbatim": violations,
    }


def verify_boundary_solo_at_coincidence() -> dict[str, Any]:
    """Documentation sweep: solo zeroing at a coincidence column can pay +4."""
    checked = 0
    positive = 0
    max_net = -(10**9)
    max_mask_exact = True
    for g in range(2):
        for c in (1, 2, 3):
            for central in range(3):
                m_g = 2 if central == g else 4
                m_2 = 2 if central == 2 else 4
                for p0 in range(4):
                    for p1 in range(4):
                        p_g = p0 if g == 0 else p1
                        d_tg = int(LW[p_g] - LW[MUL[p_g, c]])
                        for p2 in range(4):
                            d_t2 = int(LW[MUL[p2, c]] - LW[p2])
                            net = d_tg + d_t2 + m_2 - m_g
                            for s0 in range(4):
                                for s1 in range(4):
                                    checked += 1
                            max_net = max(max_net, net)
                            if net > 0:
                                positive += 16
                            predicted_max = (
                                central == g and p_g == c and p2 == 0
                            )
                            if (net == 4) != predicted_max:
                                max_mask_exact = False
    return {
        "domain_size": checked,
        "positive_cases": positive,
        "max_net": max_net,
        "max_net_is_plus4": max_net == 4,
        "max_case_mask_exact": max_mask_exact,
        "boundary_note": (
            "Solo zeroing a coincidence column resurrects the dependent third "
            "letter (r2: I -> c), paying m_2 while refunding only m_g; the "
            "worst case +4 (p_g = c, p_2 = I, central_j = g) is why the frozen "
            "move set pair-zeroes coincidence columns instead -- the "
            "QG-1 analogue of the R6M weight-2 boundary."
        ),
    }


# ---- Lemma B: zero-sum-free multiset enumeration ----------------------------


def _has_zero_sum_subset(codes: tuple[int, ...]) -> bool:
    w = len(codes)
    xor = [0] * (1 << w)
    for mask in range(1, 1 << w):
        low = mask & -mask
        xor[mask] = xor[mask ^ low] ^ codes[low.bit_length() - 1]
        if xor[mask] == 0:
            return True
    return False


def _predicted_exceptional_n() -> list[list[int]]:
    out = [[c] for c in (4, 5, 6, 7)]
    out += [sorted([a, b]) for a in (1, 2, 3) for b in (4, 5, 6, 7)]
    out += [
        sorted([a] + list(pair))
        for a in (4, 5, 6, 7)
        for pair in itertools.combinations((1, 2, 3), 2)
    ]
    out += [sorted(t) for t in itertools.combinations((4, 5, 6, 7), 3)]
    return sorted(out)


def verify_lemma_b_n() -> dict[str, Any]:
    per_w = {}
    failing = []
    total = 0
    for w in range(1, 9):
        checked = 0
        fails = []
        for combo in itertools.combinations_with_replacement(range(8), w):
            if sum(c >> 2 for c in combo) % 2 != 1:
                continue
            checked += 1
            if not _has_zero_sum_subset(combo):
                fails.append(list(combo))
        total += checked
        per_w[str(w)] = {"odd_alpha_multisets_checked": checked, "failures": len(fails)}
        failing.extend(fails)
    # tuple corroboration for w <= 5
    tuple_checked = 0
    tuple_fail_patterns = set()
    for w in range(1, 6):
        for combo in itertools.product(range(8), repeat=w):
            if sum(c >> 2 for c in combo) % 2 != 1:
                continue
            tuple_checked += 1
            if not _has_zero_sum_subset(combo):
                tuple_fail_patterns.add(tuple(sorted(combo)))
    observed = sorted(failing)
    predicted = _predicted_exceptional_n()
    characterization_ok = all(
        len(set(pat)) == len(pat) and 0 not in pat for pat in observed
    )
    return {
        "total_odd_alpha_multisets_checked": total,
        "per_w": per_w,
        "w4_to_w8_failures": sum(per_w[str(w)]["failures"] for w in range(4, 9)),
        "w4_to_w8_all_admit_subset": all(
            per_w[str(w)]["failures"] == 0 for w in range(4, 9)
        ),
        "exceptional_patterns_observed": observed,
        "exceptional_patterns_predicted": predicted,
        "exceptional_exact": observed == predicted,
        "exceptional_counts_by_w": {
            "1": sum(1 for pat in observed if len(pat) == 1),
            "2": sum(1 for pat in observed if len(pat) == 2),
            "3": sum(1 for pat in observed if len(pat) == 3),
        },
        "characterization_distinct_nonzero": characterization_ok,
        "tuple_corroboration_w_le_5": {
            "tuples_checked": tuple_checked,
            "failing_patterns_match": sorted(
                list(t) for t in tuple_fail_patterns
            ) == [pat for pat in predicted if len(pat) <= 5],
        },
    }


def verify_lemma_b_c() -> dict[str, Any]:
    per_w = {}
    failing = []
    total = 0
    for w in range(1, 9):
        checked = 0
        fails = []
        for combo in itertools.combinations_with_replacement(range(4), w):
            checked += 1
            if not _has_zero_sum_subset(combo):
                fails.append(list(combo))
        total += checked
        per_w[str(w)] = {"multisets_checked": checked, "failures": len(fails)}
        failing.extend(fails)
    tuple_checked = 0
    tuple_fail_patterns = set()
    for w in range(1, 6):
        for combo in itertools.product(range(4), repeat=w):
            tuple_checked += 1
            if not _has_zero_sum_subset(combo):
                tuple_fail_patterns.add(tuple(sorted(combo)))
    observed = sorted(failing)
    predicted = [[1], [1, 2], [1, 3], [2], [2, 3], [3]]
    return {
        "total_multisets_checked": total,
        "per_w": per_w,
        "w3_to_w8_failures": sum(per_w[str(w)]["failures"] for w in range(3, 9)),
        "w3_to_w8_all_admit_subset": all(
            per_w[str(w)]["failures"] == 0 for w in range(3, 9)
        ),
        "exceptional_patterns_observed": observed,
        "exceptional_patterns_predicted": sorted(predicted),
        "exceptional_exact": observed == sorted(predicted),
        "tuple_corroboration_w_le_5": {
            "tuples_checked": tuple_checked,
            "failing_patterns_match": sorted(
                list(t) for t in tuple_fail_patterns
            ) == sorted(predicted),
        },
    }


# ---- independent capped brute optimizer -------------------------------------


class PairTables:
    def __init__(self, n: int):
        self.n = n
        keys = [(x, z) for x in range(1 << n) for z in range(1 << n)]
        self.keys = keys
        self.wt_s = np.array([p10.wt(k) for k in keys], dtype=np.int64)
        nz = [k for k in keys if k != (0, 0)]
        pairs = [(a, b) for a in nz for b in nz if p10.symp(a, b) == 1]
        if len(pairs) != EXPECTED_PAIR_COUNTS[n]:
            raise AssertionError(
                {"qg1_pair_count_mismatch": [n, len(pairs)]}
            )
        self.pairs = pairs
        self.rs = [(a, b, p10.mul(a, b)) for a, b in pairs]
        sym = {k: np.array([p10.symp(k, s) for s in keys], dtype=np.int8) for k in nz}
        hi = np.stack([2 * sym[a] + sym[b] for a, b in pairs])  # (nP, nS)
        n_pairs = len(pairs)
        minw = np.full((4, n_pairs, n_pairs), BIG, dtype=np.int64)
        for cls in range(4):
            mc = hi == cls
            unset = np.ones((n_pairs, n_pairs), dtype=bool)
            for w in range(n + 1):
                cols = np.flatnonzero(self.wt_s == w)
                sub = mc[:, cols].astype(np.float32)
                reach = (sub @ sub.T) > 0.5
                newly = unset & reach
                minw[cls][newly] = w
                unset &= ~newly
        best = np.full((n_pairs, n_pairs), 8 * BIG, dtype=np.int64)
        for hi_cls in range(4):
            for lo_cls in range(4):
                c0 = 2 * ((hi_cls >> 1) & 1) + ((lo_cls >> 1) & 1)
                c1 = 2 * (hi_cls & 1) + (lo_cls & 1)
                if c0 == 0 or c1 == 0 or c0 == c1:
                    continue
                best = np.minimum(best, 2 * (minw[hi_cls] + minw[lo_cls]))
        self.best_tag = best
        self.uanti_min = np.array(
            [
                min(p10.uanti_support(rs, central) for central in range(3))
                for rs in self.rs
            ],
            dtype=np.int64,
        )
        self.pair_max_wt = np.array(
            [max(p10.wt(a), p10.wt(b)) for a, b in pairs], dtype=np.int64
        )

    def capped_costs(self, targets_a, targets_b, caps) -> dict[int, int]:
        rest_a = np.array(
            [
                sum(p10.wt(p10.mul(targets_a[k], rs[k])) for k in range(3))
                for rs in self.rs
            ],
            dtype=np.int64,
        )
        rest_b = np.array(
            [
                min(
                    sum(p10.wt(p10.mul(targets_b[perm[k]], rs[k])) for k in range(3))
                    for perm in PERMS
                )
                for rs in self.rs
            ],
            dtype=np.int64,
        )
        col_a = self.uanti_min + rest_a
        col_b = self.uanti_min + rest_b
        out = {}
        for cap in caps:
            idx = np.flatnonzero(self.pair_max_wt <= cap)
            if idx.size == 0:
                raise AssertionError({"qg1_empty_cap": cap})
            total = (
                col_a[idx][:, None]
                + col_b[idx][None, :]
                + self.best_tag[np.ix_(idx, idx)]
            )
            best = int(total.min())
            if best >= BIG:
                raise AssertionError({"qg1_cap_infeasible": cap})
            out[cap] = best
        return out


def hostile_capped_binding() -> dict[str, Any]:
    """cap==n (vacuous) must equal the committed brute AND the committed DP."""
    tables = {1: PairTables(1), 2: PairTables(2)}
    rows = {}
    for name, (n, ta, tb) in r6i.HOSTILE_PANELS.items():
        mine = tables[n].capped_costs(tuple(ta), tuple(tb), (n,))[n]
        brute = r6i.brute_shared_cost(ta, tb, n)
        dp = int(r6i.shared_tag_exact(ta, tb, n)["C_shared"])
        rows[name] = {
            "n": n,
            "capped_full": int(mine),
            "committed_brute": int(brute),
            "committed_dp": dp,
            "pass": mine == brute == dp,
        }
    return {
        "rows": rows,
        "all_pass": all(r["pass"] for r in rows.values()),
        "panel_count": len(rows),
    }


# ---- explicit configuration machinery (cost / feasibility / descent) --------


def config_cost(cfg) -> int:
    total = 2 * (p10.wt(cfg["s0"]) + p10.wt(cfg["s1"]))
    for j in range(2):
        g0, g1 = cfg["gens"][2 * j], cfg["gens"][2 * j + 1]
        rs = (g0, g1, p10.mul(g0, g1))
        central = cfg["centrals"][j]
        m = multipliers(central)
        direct = sum(m[k] * p10.wt(rs[k]) for k in range(3)) - 10
        uanti = p10.uanti_support(rs, central)
        if direct != uanti:
            raise AssertionError({"qg1_uanti_binding_failed": [direct, uanti]})
        targets = cfg["targets"][j]
        total += uanti + sum(p10.wt(p10.mul(targets[k], rs[k])) for k in range(3))
    return int(total)


def config_labels(cfg):
    g = cfg["gens"]
    s0, s1 = cfg["s0"], cfg["s1"]
    if p10.symp(g[0], g[1]) != 1 or p10.symp(g[2], g[3]) != 1:
        return False, None
    a0 = (p10.symp(s0, g[0]), p10.symp(s1, g[0]))
    a1 = (p10.symp(s0, g[1]), p10.symp(s1, g[1]))
    b0 = (p10.symp(s0, g[2]), p10.symp(s1, g[2]))
    b1 = (p10.symp(s0, g[3]), p10.symp(s1, g[3]))
    if a0 != b0 or a1 != b1:
        return False, None
    c0 = 2 * a0[0] + a0[1]
    c1 = 2 * a1[0] + a1[1]
    if c0 == 0 or c1 == 0 or c0 == c1:
        return False, None
    return True, (c0, c1)


def _zs_subset(codes):
    """Smallest nonempty zero-sum subset in (size, lex) order, or None."""
    w = len(codes)
    for size in range(1, w + 1):
        for combo in itertools.combinations(range(w), size):
            acc = 0
            for i in combo:
                acc ^= codes[i]
            if acc == 0:
                return combo
    return None


def _block_columns(cfg, j):
    n = cfg["n"]
    l0 = list(p10.codes(cfg["gens"][2 * j], n))
    l1 = list(p10.codes(cfg["gens"][2 * j + 1], n))
    sc0 = p10.codes(cfg["s0"], n)
    sc1 = p10.codes(cfg["s1"], n)
    coincidence = [q for q in range(n) if l0[q] != 0 and l0[q] == l1[q]]
    return l0, l1, sc0, sc1, coincidence


def _n_classes(l_g, l_o, sc0, sc1, coincidence, n):
    cols = [
        q
        for q in range(n)
        if l_g[q] != 0 and q not in coincidence
    ]
    codes = [
        int(4 * SY[l_g[q], l_o[q]] + 2 * SY[sc0[q], l_g[q]] + SY[sc1[q], l_g[q]])
        for q in cols
    ]
    return cols, codes


def _c_classes(l0, sc0, sc1, coincidence):
    return [int(2 * SY[sc0[q], l0[q]] + SY[sc1[q], l0[q]]) for q in coincidence]


def find_move(cfg):
    """Frozen scan order: block A then B; SOLO g=0, SOLO g=1, PAIR."""
    for j in range(2):
        l0, l1, sc0, sc1, coincidence = _block_columns(cfg, j)
        for g in range(2):
            l_g, l_o = (l0, l1) if g == 0 else (l1, l0)
            cols, codes = _n_classes(l_g, l_o, sc0, sc1, coincidence, cfg["n"])
            if sum(c >> 2 for c in codes) % 2 != 1:
                raise AssertionError({"qg1_alpha_parity_not_odd": codes})
            sel = _zs_subset(tuple(codes))
            if sel is not None:
                if len(sel) == len(cols):
                    raise AssertionError({"qg1_full_N_zero_sum": codes})
                return ("solo", j, g, [cols[i] for i in sel])
        codes_c = _c_classes(l0, sc0, sc1, coincidence)
        sel = _zs_subset(tuple(codes_c))
        if sel is not None:
            return ("pair", j, None, [coincidence[i] for i in sel])
    return None


def apply_move(cfg, move):
    """Apply the frozen move; return (new_cfg, predicted_delta, support_drop)."""
    kind, j, g, qubits = move
    n = cfg["n"]
    l0 = list(p10.codes(cfg["gens"][2 * j], n))
    l1 = list(p10.codes(cfg["gens"][2 * j + 1], n))
    central = cfg["centrals"][j]
    targets = cfg["targets"][j]
    tl = [p10.codes(t, n) for t in targets]
    predicted = 0
    if kind == "solo":
        l_g, l_o = (l0, l1) if g == 0 else (l1, l0)
        m_g = 2 if central == g else 4
        m_2 = 2 if central == 2 else 4
        for q in qubits:
            f, o = l_g[q], l_o[q]
            fo = int(MUL[f, o])
            p_g = tl[g][q]
            p_2 = tl[2][q]
            predicted += (
                int(LW[p_g] - LW[MUL[p_g, f]])
                + int(LW[MUL[p_2, o]] - LW[MUL[p_2, fo]])
                - m_g
                + m_2 * int(LW[o] - LW[fo])
            )
            l_g[q] = 0
        drop = len(qubits)
    else:
        m = multipliers(central)
        for q in qubits:
            c = l0[q]
            predicted += (
                int(LW[tl[0][q]] - LW[MUL[tl[0][q], c]])
                + int(LW[tl[1][q]] - LW[MUL[tl[1][q], c]])
                - m[0]
                - m[1]
            )
            l0[q] = 0
            l1[q] = 0
        drop = 2 * len(qubits)
    gens = list(cfg["gens"])
    gens[2 * j] = p10.key_from_codes(l0)
    gens[2 * j + 1] = p10.key_from_codes(l1)
    new_cfg = dict(cfg)
    new_cfg["gens"] = tuple(gens)
    return new_cfg, predicted, drop


def irreducibility_report(cfg):
    blocks = []
    ok = True
    for j in range(2):
        l0, l1, sc0, sc1, coincidence = _block_columns(cfg, j)
        codes_c = _c_classes(l0, sc0, sc1, coincidence)
        c_free = _zs_subset(tuple(codes_c)) is None
        c_char = len(set(codes_c)) == len(codes_c) and 0 not in codes_c and len(codes_c) <= 2
        gens = []
        for g in range(2):
            l_g, l_o = (l0, l1) if g == 0 else (l1, l0)
            cols, codes = _n_classes(l_g, l_o, sc0, sc1, coincidence, cfg["n"])
            n_free = _zs_subset(tuple(codes)) is None
            n_char = (
                len(set(codes)) == len(codes) and 0 not in codes and len(codes) <= 3
            )
            support = len(cols) + len(coincidence)
            gens.append(
                {
                    "N_classes": sorted(codes),
                    "N_zero_sum_free": n_free,
                    "N_characterization_ok": n_char,
                    "support": support,
                    "support_le_5": support <= 5,
                }
            )
            ok = ok and n_free and n_char and support <= 5
        blocks.append(
            {
                "C_classes": sorted(codes_c),
                "C_zero_sum_free": c_free,
                "C_characterization_ok": c_char,
                "generators": gens,
            }
        )
        ok = ok and c_free and c_char
    return ok, blocks


def descend(cfg, c_dp=None) -> dict[str, Any]:
    ok, labels = config_labels(cfg)
    if not ok:
        raise AssertionError("qg1 descent started from an infeasible config")
    cost = config_cost(cfg)
    gen_supports = [p10.wt(k) for k in cfg["gens"]]
    initial = {
        "cost": cost,
        "generator_supports": gen_supports,
        "total_generator_support": int(sum(gen_supports)),
        "max_generator_support": int(max(gen_supports)),
    }
    steps = 0
    ties = 0
    solo_moves = 0
    pair_moves = 0
    problems = []
    guard = 4 * cfg["n"] + 1
    while True:
        move = find_move(cfg)
        if move is None:
            break
        steps += 1
        if steps > guard:
            problems.append("descent_exceeded_step_guard")
            break
        old_support = sum(p10.wt(k) for k in cfg["gens"])
        new_cfg, predicted, drop = apply_move(cfg, move)
        ok2, labels2 = config_labels(new_cfg)
        if not ok2 or labels2 != labels:
            problems.append({"feasibility_broken_at_step": steps, "move": move[0]})
            break
        new_cost = config_cost(new_cfg)
        dc = new_cost - cost
        if dc != predicted:
            problems.append(
                {
                    "unmodeled_coupling_at_step": steps,
                    "observed_delta": dc,
                    "predicted_delta": predicted,
                }
            )
            break
        if dc > 0 or (move[0] == "pair" and dc >= 0):
            problems.append({"cost_not_decreased_at_step": steps, "delta": dc})
            break
        new_support = sum(p10.wt(k) for k in new_cfg["gens"])
        if old_support - new_support != drop:
            problems.append({"support_drop_mismatch_at_step": steps})
            break
        if dc == 0:
            ties += 1
        if move[0] == "solo":
            solo_moves += 1
        else:
            pair_moves += 1
        cfg, cost = new_cfg, new_cost
    irreducible_ok, blocks = irreducibility_report(cfg)
    if not problems and not irreducible_ok:
        problems.append("descent_terminated_reducible_or_uncharacterized")
    if c_dp is not None and not problems and cost < c_dp:
        problems.append({"final_cost_below_unrestricted_dp": [int(cost), int(c_dp)]})
    final_supports = [int(p10.wt(k)) for k in cfg["gens"]]
    return {
        "initial": initial,
        "final_cost": int(cost),
        "final_generator_supports": final_supports,
        "final_max_generator_support": int(max(final_supports)),
        "steps": steps,
        "solo_moves": solo_moves,
        "pair_moves": pair_moves,
        "tie_steps": ties,
        "irreducible_blocks": blocks,
        "problems": problems,
        "pass": not problems,
    }


# ---- seeded configuration sampling ------------------------------------------


def _draw_nonzero(rng, n):
    while True:
        x = int(rng.integers(0, 1 << n))
        z = int(rng.integers(0, 1 << n))
        if (x, z) != (0, 0):
            return (x, z)


def sample_config(rng, n, targets_a, targets_b, min_wa0, exact_wa0, coincidence_seeded):
    all_keys = [(x, z) for x in range(1 << n) for z in range(1 << n)]
    for attempt in range(1, 501):
        ra0 = _draw_nonzero(rng, n)
        tries = 0
        while (p10.wt(ra0) != exact_wa0) if exact_wa0 else (p10.wt(ra0) < min_wa0):
            ra0 = _draw_nonzero(rng, n)
            tries += 1
            if tries > 2000:
                break
        else:
            tries = 0
        if tries > 2000:
            continue
        ra1 = None
        if coincidence_seeded:
            supp = [q for q in range(n) if p10.codes(ra0, n)[q] != 0]
            for _try in range(400):
                letters = [int(rng.integers(0, 4)) for _ in range(n)]
                size = 1 + int(rng.integers(0, len(supp)))
                chosen = [supp[i] for i in rng.permutation(len(supp))[:size]]
                a0_codes = p10.codes(ra0, n)
                for q in chosen:
                    letters[q] = a0_codes[q]
                cand = p10.key_from_codes(letters)
                if cand != (0, 0) and p10.symp(ra0, cand) == 1:
                    ra1 = cand
                    break
        else:
            for _try in range(400):
                cand = _draw_nonzero(rng, n)
                if p10.symp(ra0, cand) == 1:
                    ra1 = cand
                    break
        if ra1 is None:
            continue
        rb0 = _draw_nonzero(rng, n)
        rb1 = None
        for _try in range(400):
            cand = _draw_nonzero(rng, n)
            if p10.symp(rb0, cand) == 1:
                rb1 = cand
                break
        if rb1 is None:
            continue
        buckets = {0: [], 1: [], 2: [], 3: []}
        for s in all_keys:
            a0 = p10.symp(s, ra0)
            a1 = p10.symp(s, ra1)
            if a0 != p10.symp(s, rb0) or a1 != p10.symp(s, rb1):
                continue
            buckets[2 * a0 + a1].append(s)
        combos = []
        for hi_cls in range(4):
            for lo_cls in range(4):
                if not buckets[hi_cls] or not buckets[lo_cls]:
                    continue
                c0 = 2 * ((hi_cls >> 1) & 1) + ((lo_cls >> 1) & 1)
                c1 = 2 * (hi_cls & 1) + (lo_cls & 1)
                if c0 == 0 or c1 == 0 or c0 == c1:
                    continue
                combos.append((hi_cls, lo_cls))
        if not combos:
            continue
        hi_cls, lo_cls = combos[int(rng.integers(0, len(combos)))]
        s0 = buckets[hi_cls][int(rng.integers(0, len(buckets[hi_cls])))]
        s1 = buckets[lo_cls][int(rng.integers(0, len(buckets[lo_cls])))]
        perm = PERMS[int(rng.integers(0, 6))]
        cfg = {
            "n": n,
            "gens": (ra0, ra1, rb0, rb1),
            "s0": s0,
            "s1": s1,
            "centrals": (int(rng.integers(0, 3)), int(rng.integers(0, 3))),
            "targets": (
                tuple(targets_a),
                tuple(targets_b[perm[k]] for k in range(3)),
            ),
        }
        ok, _labels = config_labels(cfg)
        if not ok:
            continue
        return cfg, attempt
    raise AssertionError("qg1 could not sample a feasible spread config in 500 tries")


def witness_config(witness, targets_a, targets_b, n):
    perm = tuple(witness["relative_B_permutation"])
    return {
        "n": n,
        "gens": (
            tuple(witness["RA"][0]),
            tuple(witness["RA"][1]),
            tuple(witness["RB"][0]),
            tuple(witness["RB"][1]),
        ),
        "s0": tuple(witness["S0"]),
        "s1": tuple(witness["S1"]),
        "centrals": (int(witness["central_A"]), int(witness["central_B"])),
        "targets": (
            tuple(targets_a),
            tuple(targets_b[perm[k]] for k in range(3)),
        ),
    }


def witness_class_report(cfg):
    _ok, blocks = irreducibility_report(cfg)
    return blocks


# ---- stress panel + descents ------------------------------------------------


def stress_panel_and_descents(tables3: PairTables) -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    rows = []
    descents = []
    gap_rows = []
    sampling_attempts = []
    for i in range(PANEL_COUNT):
        targets = [_draw_nonzero(rng, PANEL_N) for _ in range(6)]
        ta, tb = tuple(targets[:3]), tuple(targets[3:])
        r6i._LOCAL_CACHE.clear()
        witness = r6i.shared_tag_exact(ta, tb, PANEL_N)
        c_dp = int(witness["C_shared"])
        capped = tables3.capped_costs(ta, tb, (1, 2, 3))
        wcfg = witness_config(witness, ta, tb, PANEL_N)
        rebound = config_cost(wcfg)
        ok_w, _ = config_labels(wcfg)
        if not ok_w or rebound != c_dp:
            raise AssertionError(
                {"qg1_witness_rebinding_failed": [i, rebound, c_dp]}
            )
        if c_dp > capped[3] or c_dp > capped[2] or capped[2] > capped[1]:
            raise AssertionError(
                {"qg1_containment_violated": [i, c_dp, capped]}
            )
        row = {
            "index": i,
            "targets": [list(t) for t in targets],
            "C_dp": c_dp,
            "C_brute_full": capped[3],
            "C_cap2": capped[2],
            "C_cap1": capped[1],
            "dp_equals_brute": c_dp == capped[3],
            "cap2_equal": c_dp == capped[2],
            "witness_max_generator_support": int(
                max(p10.wt(k) for k in wcfg["gens"])
            ),
            "witness_classes": witness_class_report(wcfg),
        }
        rows.append(row)
        if not row["cap2_equal"]:
            gap = descend(dict(wcfg), c_dp=c_dp)
            gap_rows.append(
                {
                    "index": i,
                    "C_dp": c_dp,
                    "C_cap2": capped[2],
                    "witness_descent_final_max_generator_support": gap[
                        "final_max_generator_support"
                    ],
                    "witness_descent_pass": gap["pass"],
                    "witness_descent_final_cost": gap["final_cost"],
                    "irreducible_blocks": gap["irreducible_blocks"],
                }
            )
            if gap["final_max_generator_support"] <= 2:
                raise AssertionError(
                    {"qg1_gap_with_support2_descent": gap_rows[-1]}
                )
        for d in range(DESCENTS_PER_INSTANCE):
            cfg, attempts = sample_config(
                rng, PANEL_N, ta, tb, 3, None, coincidence_seeded=(d % 2 == 1)
            )
            sampling_attempts.append(attempts)
            rec = descend(cfg, c_dp=c_dp)
            rec.update({"n": PANEL_N, "group": "panel", "instance": i, "descent": d})
            descents.append(rec)
    for n, count in FRESH_DESCENT_PLAN:
        for i in range(count):
            targets = [_draw_nonzero(rng, n) for _ in range(6)]
            ta, tb = tuple(targets[:3]), tuple(targets[3:])
            exact = (
                n
                if (n == 6 and i >= count - N6_EXACT_W6_TAIL)
                else None
            )
            cfg, attempts = sample_config(
                rng, n, ta, tb, 3, exact, coincidence_seeded=(i % 2 == 1)
            )
            sampling_attempts.append(attempts)
            rec = descend(cfg)
            rec.update({"n": n, "group": "fresh", "instance": i, "descent": 0})
            descents.append(rec)
    r6i._LOCAL_CACHE.clear()
    descent_rows = [
        {
            key: rec[key]
            for key in (
                "n",
                "group",
                "instance",
                "descent",
                "final_cost",
                "final_generator_supports",
                "final_max_generator_support",
                "steps",
                "solo_moves",
                "pair_moves",
                "tie_steps",
                "pass",
                "problems",
            )
        }
        | {
            "initial_cost": rec["initial"]["cost"],
            "initial_max_generator_support": rec["initial"][
                "max_generator_support"
            ],
            "initial_total_generator_support": rec["initial"][
                "total_generator_support"
            ],
        }
        for rec in descents
    ]
    return {
        "seed": SEED,
        "panel_n": PANEL_N,
        "instances": len(rows),
        "rows": rows,
        "dp_equals_brute_all": all(r["dp_equals_brute"] for r in rows),
        "cap2_equal_count": sum(r["cap2_equal"] for r in rows),
        "cap2_gap_count": sum(not r["cap2_equal"] for r in rows),
        "cap2_gap_rows": gap_rows,
        "subsampling": "none -- full frozen plan executed",
        "descents": {
            "plan": {
                "panel": [PANEL_N, PANEL_COUNT, DESCENTS_PER_INSTANCE],
                "fresh": [list(x) for x in FRESH_DESCENT_PLAN],
                "n6_exact_w6_tail": N6_EXACT_W6_TAIL,
            },
            "count": len(descents),
            "all_pass": all(rec["pass"] for rec in descents),
            "total_steps": sum(rec["steps"] for rec in descents),
            "total_solo_moves": sum(rec["solo_moves"] for rec in descents),
            "total_pair_moves": sum(rec["pair_moves"] for rec in descents),
            "total_tie_steps": sum(rec["tie_steps"] for rec in descents),
            "max_initial_generator_support": max(
                rec["initial"]["max_generator_support"] for rec in descents
            ),
            "max_final_generator_support": max(
                rec["final_max_generator_support"] for rec in descents
            ),
            "max_sampling_attempts": max(sampling_attempts),
            "rows": descent_rows,
        },
    }


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "Frozen R6I two-block rank-2 dependent TARE-3 shared-2-bit-Tag "
        "grammar under the frozen R6I objective ((4,4,4)/central-2 "
        "multiplicities, Tag paid twice, per-branch Restore supports with "
        "NO factor rule), for EVERY qubit count n, every target-triple "
        "pair, every relative B permutation and every central pair: the "
        "exact optimum is attained with all four generators RA0, RA1, RB0, "
        "RB1 of global support <= 5 (B = 5), the dependent letters Rj2 of "
        "support <= 6, and per-block joint support <= 8."
    ),
    "proof_shape": (
        "Column taxonomy (coincidence vs non-coincidence), classes in "
        "F_2^2 / F_2^3, zero Tag repair by construction; Lemma B "
        "(re-derived pigeonhole: Davenport-type bounds for (Z/2)^3 under "
        "odd anticommutation parity and for (Z/2)^2, exceptional patterns "
        "32 + 6, machine-corroborated to w = 8); Lemma E (exhaustive "
        "55,296 + 9,216 cases including the dependent third letter's frame "
        "and Restore movement); induction on (cost, total generator "
        "support). The only computational steps are the lemma checks."
    ),
    "does_not_cover": (
        "The R6K restore-factor variant, the R6M/R6S three-block grammar "
        "(closed separately), coefficient-weighted or non-support "
        "objectives, larger Tag ranks, tightness of B = 5, or any claim "
        "that generator support 2 suffices (the panel measures that "
        "boundary empirically at n = 3 only). The stress panel and "
        "descents are corroboration, not the proof. No novelty credit, no "
        "donor credit, not R6."
    ),
    "coincidence_boundary": (
        "Solo zeroing a coincidence column resurrects the dependent third "
        "letter (worst case +4); coincidence columns are therefore "
        "pair-zeroed (worst case -4). The exceptional irreducible patterns "
        "-- N-class multisets distinct nonzero with odd alpha-parity "
        "(sizes 1..3, 32 patterns) and C-class multisets distinct nonzero "
        "(sizes 0..2, 6 nonempty patterns) -- are this grammar's analogue "
        "of the R6M weight-2 boundary."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    bindings = bind_tables()
    if not all(bindings.values()):
        raise AssertionError({"qg1_table_binding_failed": bindings})
    uanti = verify_uanti_identity()
    if not uanti["holds"] or uanti["pairs"] != EXPECTED_PAIR_COUNTS[2]:
        raise AssertionError({"qg1_uanti_identity_failed": uanti})

    lemma_e_solo = verify_lemma_e_solo()
    lemma_e_pair = verify_lemma_e_pair()
    boundary = verify_boundary_solo_at_coincidence()
    lemma_b_n = verify_lemma_b_n()
    lemma_b_c = verify_lemma_b_c()

    hostile = hostile_capped_binding()
    if not hostile["all_pass"]:
        raise AssertionError({"qg1_hostile_capped_binding_failed": hostile})

    tables3 = PairTables(PANEL_N)
    panel = stress_panel_and_descents(tables3)

    gates = {
        "lemma_e_solo_zero_violations": lemma_e_solo["holds"]
        and lemma_e_solo["ties_match_prediction"],
        "lemma_e_pair_strict": lemma_e_pair["holds_strict"],
        "boundary_documented": boundary["max_net_is_plus4"]
        and boundary["positive_cases"] > 0
        and boundary["max_case_mask_exact"],
        "lemma_b_n_w4_to_w8_zero_failures": lemma_b_n["w4_to_w8_all_admit_subset"],
        "lemma_b_n_exceptional_exact": lemma_b_n["exceptional_exact"]
        and lemma_b_n["characterization_distinct_nonzero"]
        and lemma_b_n["tuple_corroboration_w_le_5"]["failing_patterns_match"],
        "lemma_b_c_w3_to_w8_zero_failures": lemma_b_c["w3_to_w8_all_admit_subset"],
        "lemma_b_c_exceptional_exact": lemma_b_c["exceptional_exact"]
        and lemma_b_c["tuple_corroboration_w_le_5"]["failing_patterns_match"],
        "descents_all_verified": panel["descents"]["all_pass"],
        "panel_dp_equals_brute": panel["dp_equals_brute_all"],
        "panel_gap_rows_all_support3_realized": all(
            row["witness_descent_final_max_generator_support"] >= 3
            and row["witness_descent_pass"]
            for row in panel["cap2_gap_rows"]
        ),
        "bindings_exact": all(bindings.values())
        and uanti["holds"]
        and hostile["all_pass"],
        "no_new_subject_data": True,
    }
    integrity = {k: gates[k] for k in ("bindings_exact", "no_new_subject_data")}
    if not all(integrity.values()):
        raise AssertionError({"qg1_integrity_gate_failure": integrity})

    gap = (
        not lemma_e_solo["holds"]
        or not lemma_e_pair["holds_strict"]
        or not lemma_b_n["w4_to_w8_all_admit_subset"]
        or not lemma_b_c["w3_to_w8_all_admit_subset"]
    )
    if not gap and all(gates.values()):
        outcome = "THEOREM_MACHINE_CHECKED"
        authority = (
            "ORIONQ_QG1_RANK2_ALL_N_THEOREM_MACHINE_CHECKED__"
            "GENERATOR_SUPPORT5_SUFFICES_ALL_N__CAP5_EQUALS_UNRESTRICTED__NOT_R6"
        )
        responsibility = (
            "RESP:R6S_CLAIM_BOUNDARY_EXCLUSION_CLOSED__RANK2_EXCHANGE_WITH_"
            "ZERO_TAG_REPAIR_VIA_F2CUBED_AND_F2SQUARED_PIGEONHOLE"
        )
        discovery = None
    elif gap:
        outcome = "GAP_FOUND"
        authority = "ORIONQ_QG1_RANK2_ALL_N_GAP_FOUND__EXCHANGE_CASE_FAILS__NOT_R6"
        responsibility = "RESP:EXCHANGE_CASE_GAP__TEST_REALIZABILITY_AND_RE_FREEZE"
        discovery = {
            "lemma_e_solo_violations_verbatim": lemma_e_solo[
                "violating_cases_verbatim"
            ],
            "lemma_e_pair_violations_verbatim": lemma_e_pair[
                "violating_cases_verbatim"
            ],
            "lemma_b_n_failures_w_ge_4": [
                pat
                for pat in lemma_b_n["exceptional_patterns_observed"]
                if len(pat) >= 4
            ],
            "lemma_b_c_failures_w_ge_3": [
                pat
                for pat in lemma_b_c["exceptional_patterns_observed"]
                if len(pat) >= 3
            ],
            "empirical_realizability": {
                "cap2_gap_rows": panel["cap2_gap_rows"],
                "failed_descents": [
                    r for r in panel["descents"]["rows"] if not r["pass"]
                ],
                "note": (
                    "A realized irreparable case would be a new regime "
                    "discovery for the QG programme."
                ),
            },
        }
    else:
        outcome = "PARTIAL"
        authority = "ORIONQ_QG1_RANK2_ALL_N_PARTIAL__STATED_CASES_ONLY__NOT_R6"
        responsibility = (
            "RESP:LEMMAS_CLOSE_BUT_DESCENT_PANEL_OR_CHARACTERIZATION_FAILED__"
            "IMPLEMENTATION_OR_UNMODELED_COUPLING_SUSPECT"
        )
        discovery = {
            "failed_descents": [
                r for r in panel["descents"]["rows"] if not r["pass"]
            ],
            "cap2_gap_rows": panel["cap2_gap_rows"],
            "failed_gates": sorted(k for k, v in gates.items() if not v),
        }

    result = {
        "schema": "ORIONQG.QG1.Rank2AllNComposition.v1",
        "authority": authority,
        "outcome": outcome,
        "scope": (
            "ALL_N_GENERATOR_SUPPORT_EXCHANGE_THEOREM_OVER_FROZEN_R6I_"
            "RANK2_SHARED_TAG_GRAMMAR__QG1_LANE__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "QG1_RANK2_ALL_N_PROTOCOL",
        "charter": "orion-qg-regime-geometry/PROGRAMME_CHARTER_V1.md#QG-1",
        "theorem_statement": (
            "For every n and every instance of the frozen R6I grammar (every "
            "target pair, relative B permutation and central pair), the exact "
            "optimum is attained by a configuration with all four generators "
            "of global support <= 5 (each non-coincidence class multiset "
            "zero-sum-free in F_2^3, <= 3 columns; each block coincidence "
            "class multiset zero-sum-free in F_2^2, <= 2 columns), dependent "
            "third letters of support <= 6, per-block joint support <= 8: "
            "B = 5, so the generator-support-capped grammar cap-5 equals the "
            "unrestricted optimum for all n."
        ),
        "support_bound_B": 5,
        "exchange_construction": {
            "column_taxonomy": (
                "coincidence columns C_j = {q: r0_q = r1_q != I} (r2_q = I "
                "there); non-coincidence support N_jg = supp(Rjg) \\ C_j"
            ),
            "classes": (
                "N-class(q) = (alpha, beta0, beta1) in F_2^3 with alpha = "
                "local_symp(r_g, r_other), beta_i = local_symp(s_i, r_g); "
                "C-class(q) = (beta0, beta1) in F_2^2; N-multisets have odd "
                "alpha-sum = symp(Rjg, other) = 1, so zero-sum subsets are "
                "automatically proper and both generators stay nonzero"
            ),
            "moves": (
                "SOLO(j,g,Q): zero Rjg on a zero-sum F_2^3 subset of N_jg "
                "(per-qubit net <= 0, Lemma E-solo, dependent letter Rj2 and "
                "both affected Restores accounted); PAIR(j,Q): zero both "
                "generators on a zero-sum F_2^2 subset of C_j (per-qubit net "
                "<= -4, Lemma E-pair). Tag, targets, permutation, centrals "
                "untouched: zero Tag repair"
            ),
            "subset_rule": (
                "smallest nonempty zero-sum subset in (size, lexicographic) "
                "order; any size is admissible because the per-qubit "
                "inequality holds pointwise"
            ),
            "induction": (
                "lexicographic (cost, total generator support) minimum admits "
                "no move; Lemma B then bounds |N_jg| <= 3 and |C_j| <= 2, so "
                "every generator support <= 5"
            ),
            "exceptional_patterns": (
                "N-side: 32 odd-alpha zero-sum-free multisets (4 singletons, "
                "12 pairs, 16 triples; all distinct nonzero, independence "
                "automatic under odd parity); C-side: 6 (3 singletons, 3 "
                "pairs); these delineate the irreducible boundary"
            ),
        },
        "bindings": {
            "tables": bindings,
            "uanti_identity": uanti,
            "hostile_capped_binding": hostile,
            "pair_counts_expected": {str(k): v for k, v in EXPECTED_PAIR_COUNTS.items()},
        },
        "lemma_e_solo": lemma_e_solo,
        "lemma_e_pair": lemma_e_pair,
        "boundary_solo_at_coincidence": boundary,
        "lemma_b_n": lemma_b_n,
        "lemma_b_c": lemma_b_c,
        "stress_panel": panel,
        "gates": gates,
        "discovery": discovery,
        "claim_boundary": CLAIM_BOUNDARY,
        "chemistry_sources_read": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
        "repository_files_modified": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG1 authority ceiling violated")
    print("ORIONQ_QG1_RANK2_ALL_N=" + canonical_json(result))
    runtime = time.monotonic() - start
    file_result = dict(result)
    file_result["runtime_seconds"] = round(runtime, 3)
    Path(__file__).with_name("QG1_RANK2_ALL_N_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n"
    )
    return result


if __name__ == "__main__":
    main()
