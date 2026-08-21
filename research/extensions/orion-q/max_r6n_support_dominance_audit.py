#!/usr/bin/env python3
"""MAX-R6N support-dominance lemma audit.

Frozen by MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL.md (frozen before outcome).

Machine-verifies the support-dominance lemma candidate that explains the
R6I/R6K/R6M collapses onto weight-one donor families:

1. exhaustive per-qubit local exchange inequalities for the frozen R6M
   three-M2 shared-Tag/factor grammar (primary + letterwise-monotone form)
   and the frozen R6I two-block rank-2 shared-Tag grammar;
2. equality of the weight-one-restricted optima with the recorded exact DP
   optima on both frozen open subjects, using only the existing receipts
   (no chemistry source is read, no heavy DP re-run);
3. a deterministic synthetic n=1 / n=2 joint panel comparing unrestricted DP
   optima against weight-one-restricted optima, importing the frozen R6I and
   R6M modules' machinery unmodified.

Honest outcome either way: any violating configuration or strict
unrestricted-beats-weight-one gap is a discovery and is reported verbatim.
Not R6; no novelty credit; the protected stretched-N2 discriminator is never
read.
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

import max_r6i_exact_rank2_shared_tag_dp as r6i  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
VERBATIM_CAP = 20

# ---- independent local algebra (bound to the frozen tables below) -----------
LW = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
LM = np.array([[h.local_mul(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
SY = np.array([[h.local_symp(a, b) for b in range(4)] for a in range(4)], dtype=np.int64)
F3 = np.zeros((4, 4, 4), dtype=np.int64)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            if _a == _b == _c != 0:
                F3[_a, _b, _c] = 1
            else:
                F3[_a, _b, _c] = LW[_a] + LW[_b] + LW[_c]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _dig3(i: int) -> tuple[int, int, int]:
    return ((i >> 4) & 3, (i >> 2) & 3, i & 3)


def _letters3(i: int) -> str:
    return "".join(LETTERS[d] for d in _dig3(i))


# ---- Lemma N-M: R6M primary local support-dominance inequality --------------

def verify_r6m_primary() -> dict[str, Any]:
    idx = np.arange(64)
    dA, dB, dC = (idx >> 4) & 3, (idx >> 2) & 3, idx & 3
    # FK[f, t]: branch factor cost of targets t modified by frame letters f.
    FK = F3[LM[dA[None, :], dA[:, None]], LM[dB[None, :], dB[:, None]], LM[dC[None, :], dC[:, None]]]
    # sanity of orientation: FK[f=0, t] must equal F3 of the raw targets.
    assert np.array_equal(FK[0], F3[dA, dB, dC])
    SAV = FK[0][None, :] - FK  # savings[f, t]
    max_sav = SAV.max(axis=1)  # decoupled per-branch maximum over targets

    violations = 0
    checked = 0
    max_ratio = -1.0
    ratio_config = None
    verbatim = []
    for centrals in itertools.product((0, 1), repeat=3):
        mults = np.array(
            [[2 if c == k else 4 for c in centrals] for k in range(2)], dtype=np.int64
        )  # mults[branch k][block j]
        FC0 = mults[0][0] * LW[dA] + mults[0][1] * LW[dB] + mults[0][2] * LW[dC]
        FC1 = mults[1][0] * LW[dA] + mults[1][1] * LW[dB] + mults[1][2] * LW[dC]
        D0 = (SAV - FC0[:, None]).astype(np.int16)
        D1 = (SAV - FC1[:, None]).astype(np.int16)
        for s in range(4):
            # The tag term 2w(s) is additive and cancels between L(F,...) and
            # L(0,...); the domain is still swept per protocol.
            V = D0[:, :, None, None] + D1[None, None, :, :]
            checked += V.size
            bad = np.argwhere(V > 0)
            if bad.size:
                violations += int((V > 0).sum())
                for f0, t0, f1, t1 in bad[: max(0, VERBATIM_CAP - len(verbatim))]:
                    verbatim.append(
                        {
                            "grammar": "R6M",
                            "centrals": list(centrals),
                            "tag_letter": LETTERS[s],
                            "branch0": {"frames_ABC": _letters3(int(f0)), "targets_ABC": _letters3(int(t0))},
                            "branch1": {"frames_ABC": _letters3(int(f1)), "targets_ABC": _letters3(int(t1))},
                            "savings": int(SAV[f0, t0] + SAV[f1, t1]),
                            "frame_cost": int(FC0[f0] + FC1[f1]),
                        }
                    )
        # exact max savings/cost ratio: numerator decouples per branch.
        cost = FC0[:, None] + FC1[None, :]
        num = max_sav[:, None] + max_sav[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(cost > 0, num / np.maximum(cost, 1), -np.inf)
        best = int(np.argmax(ratio))
        f0, f1 = divmod(best, 64)
        if ratio[f0, f1] > max_ratio:
            max_ratio = float(ratio[f0, f1])
            t0 = int(np.argmax(SAV[f0]))
            t1 = int(np.argmax(SAV[f1]))
            ratio_config = {
                "centrals": list(centrals),
                "branch0": {"frames_ABC": _letters3(f0), "targets_ABC": _letters3(t0)},
                "branch1": {"frames_ABC": _letters3(f1), "targets_ABC": _letters3(t1)},
                "savings": int(SAV[f0, t0] + SAV[f1, t1]),
                "frame_cost": int(cost[f0, f1]),
            }
    return {
        "domain_size": checked,
        "violations": violations,
        "holds": violations == 0,
        "max_savings_over_cost_ratio": max_ratio,
        "max_ratio_config": ratio_config,
        "violating_configs_verbatim": verbatim,
    }


# ---- Lemma N-M': R6M letterwise exchange monotonicity -----------------------

def verify_r6m_letterwise() -> dict[str, Any]:
    idx = np.arange(64)
    dA, dB, dC = (idx >> 4) & 3, (idx >> 2) & 3, idx & 3
    FK = F3[LM[dA[None, :], dA[:, None]], LM[dB[None, :], dB[:, None]], LM[dC[None, :], dC[:, None]]]
    pairs = set()
    violations = 0
    verbatim = []
    checked = 0
    for f in range(64):
        fd = _dig3(f)
        for mask in range(8):
            gd = tuple(fd[j] if (mask >> (2 - j)) & 1 else 0 for j in range(3))
            g = (gd[0] << 4) | (gd[1] << 2) | gd[2]
            pairs.add((f, g))
    for f, g in sorted(pairs):
        fd, gd = _dig3(f), _dig3(g)
        removed = [j for j in range(3) if gd[j] == 0 and fd[j] != 0]
        diff = FK[g] - FK[f]  # over all 64 targets
        for m in itertools.product((2, 4), repeat=3):
            refund = sum(m[j] for j in removed)
            checked += 64
            bad = np.argwhere(diff > refund)
            if bad.size:
                violations += int((diff > refund).sum())
                for (t,) in bad[: max(0, VERBATIM_CAP - len(verbatim))]:
                    verbatim.append(
                        {
                            "grammar": "R6M_letterwise",
                            "frames_ABC": _letters3(f),
                            "sub_frames_ABC": _letters3(g),
                            "multipliers_ABC": list(m),
                            "targets_ABC": _letters3(int(t)),
                            "savings_delta": int(diff[t]),
                            "refund": refund,
                        }
                    )
    assert len(pairs) == 343, len(pairs)
    assert checked == 343 * 64 * 8
    return {
        "domain_size": checked,
        "letterwise_pairs": len(pairs),
        "violations": violations,
        "holds": violations == 0,
        "violating_configs_verbatim": verbatim,
    }


# ---- Lemma N-I: R6I primary local support-dominance inequality --------------

def verify_r6i_primary() -> dict[str, Any]:
    fidx = np.arange(16)
    r0, r1 = (fidx >> 2) & 3, fidx & 3
    r2 = LM[r0, r1]
    tidx = np.arange(64)
    p0, p1, p2 = (tidx >> 4) & 3, (tidx >> 2) & 3, tidx & 3
    # SavB[f, t] = sum_k w(p_k) - w(p_k * r_k)
    SAV = (
        (LW[p0][None, :] - LW[LM[p0[None, :], r0[:, None]]])
        + (LW[p1][None, :] - LW[LM[p1[None, :], r1[:, None]]])
        + (LW[p2][None, :] - LW[LM[p2[None, :], r2[:, None]]])
    )
    COST = np.zeros((3, 16), dtype=np.int64)
    for c in range(3):
        m = [4, 4, 4]
        m[c] = 2
        COST[c] = m[0] * LW[r0] + m[1] * LW[r1] + m[2] * LW[r2]
    max_sav = SAV.max(axis=1)

    violations = 0
    checked = 0
    max_ratio = -1.0
    ratio_config = None
    verbatim = []

    def _fb(i: int) -> str:
        return LETTERS[(i >> 2) & 3] + LETTERS[i & 3]

    for ca in range(3):
        DA = (SAV - COST[ca][:, None]).astype(np.int16)
        for cb in range(3):
            DB = (SAV - COST[cb][:, None]).astype(np.int16)
            for s0 in range(4):
                for s1 in range(4):
                    # tag letters cancel between L(F,...) and L(0,...); swept per protocol.
                    V = DA[:, :, None, None] + DB[None, None, :, :]
                    checked += V.size
                    bad = np.argwhere(V > 0)
                    if bad.size:
                        violations += int((V > 0).sum())
                        for fa, ta, fb, tb in bad[: max(0, VERBATIM_CAP - len(verbatim))]:
                            verbatim.append(
                                {
                                    "grammar": "R6I",
                                    "centrals": [ca, cb],
                                    "tag_letters": [LETTERS[s0], LETTERS[s1]],
                                    "block_A": {"frame_pair": _fb(int(fa)), "targets": _letters3(int(ta))},
                                    "block_B": {"frame_pair": _fb(int(fb)), "targets": _letters3(int(tb))},
                                    "savings": int(SAV[fa, ta] + SAV[fb, tb]),
                                    "frame_cost": int(COST[ca][fa] + COST[cb][fb]),
                                }
                            )
            cost = COST[ca][:, None] + COST[cb][None, :]
            num = max_sav[:, None] + max_sav[None, :]
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = np.where(cost > 0, num / np.maximum(cost, 1), -np.inf)
            best = int(np.argmax(ratio))
            fa, fb = divmod(best, 16)
            if ratio[fa, fb] > max_ratio:
                max_ratio = float(ratio[fa, fb])
                ta = int(np.argmax(SAV[fa]))
                tb = int(np.argmax(SAV[fb]))
                ratio_config = {
                    "centrals": [ca, cb],
                    "block_A": {"frame_pair": _fb(fa), "targets": _letters3(ta)},
                    "block_B": {"frame_pair": _fb(fb), "targets": _letters3(tb)},
                    "savings": int(SAV[fa, ta] + SAV[fb, tb]),
                    "frame_cost": int(cost[fa, fb]),
                }
    return {
        "domain_size": checked,
        "violations": violations,
        "holds": violations == 0,
        "max_savings_over_cost_ratio": max_ratio,
        "max_ratio_config": ratio_config,
        "violating_configs_verbatim": verbatim,
    }


# ---- implementation binding to the frozen module tables ---------------------

def verify_binding() -> dict[str, Any]:
    rng = np.random.default_rng(20260821)
    # F3 table binds to the frozen R6M module table.
    f3_exact = bool(np.array_equal(F3, r6m._F3))
    # R6M: reconstruct the frozen per-option raw cost arrays independently.
    r6m_keys = 0
    r6m_exact = True
    dig = r6m._DIG
    tag_exact = bool(np.array_equal(r6m._TAG_COST, 2 * LW[dig[6]]))
    frame_exact = True
    for centrals in itertools.product((0, 1), repeat=3):
        mine = np.zeros(r6m.OPTIONS, dtype=np.int64)
        for j, c in enumerate(centrals):
            m0 = 2 if c == 0 else 4
            m1 = 2 if c == 1 else 4
            mine = mine + m0 * LW[dig[2 * j]] + m1 * LW[dig[2 * j + 1]]
        frame_exact = frame_exact and bool(np.array_equal(mine, r6m._FRAME_COST[centrals]))
    for _ in range(64):
        p6 = tuple(int(x) for x in rng.integers(0, 4, size=6))
        centrals = tuple(int(x) for x in rng.integers(0, 2, size=3))
        frozen = (
            r6m._FRAME_COST[centrals]
            + r6m._TAG_COST
            + r6m._F3[r6m._LM[p6[0], dig[0]], r6m._LM[p6[2], dig[2]], r6m._LM[p6[4], dig[4]]]
            + r6m._F3[r6m._LM[p6[1], dig[1]], r6m._LM[p6[3], dig[3]], r6m._LM[p6[5], dig[5]]]
        )
        mults = []
        for c in centrals:
            mults.extend((2 if c == 0 else 4, 2 if c == 1 else 4))
        mine = sum(mults[t] * LW[dig[t]] for t in range(6)) + 2 * LW[dig[6]]
        mine = mine + F3[LM[p6[0], dig[0]], LM[p6[2], dig[2]], LM[p6[4], dig[4]]]
        mine = mine + F3[LM[p6[1], dig[1]], LM[p6[3], dig[3]], LM[p6[5], dig[5]]]
        r6m_exact = r6m_exact and bool(np.array_equal(frozen, mine))
        r6m_keys += 1
    # R6I: reconstruct the frozen per-option base cost arrays independently.
    r6i_keys = 0
    r6i_exact = True
    RA0, RA1, RB0, RB1, S0, S1 = r6i._RA0, r6i._RA1, r6i._RB0, r6i._RB1, r6i._S0, r6i._S1
    RA2, RB2 = LM[RA0, RA1], LM[RB0, RB1]
    for _ in range(64):
        key = tuple(int(x) for x in rng.integers(0, 4, size=6)) + (
            int(rng.integers(0, 3)),
            int(rng.integers(0, 3)),
        )
        pa0, pa1, pa2, pb0, pb1, pb2, ca, cb = key
        frozen = r6i._local_table(key)[0]
        ma = [4, 4, 4]
        ma[ca] = 2
        mb = [4, 4, 4]
        mb[cb] = 2
        mine = (
            ma[0] * LW[RA0] + ma[1] * LW[RA1] + ma[2] * LW[RA2]
            + mb[0] * LW[RB0] + mb[1] * LW[RB1] + mb[2] * LW[RB2]
            + 2 * (LW[S0] + LW[S1])
            + LW[LM[pa0, RA0]] + LW[LM[pa1, RA1]] + LW[LM[pa2, RA2]]
            + LW[LM[pb0, RB0]] + LW[LM[pb1, RB1]] + LW[LM[pb2, RB2]]
        )
        # frozen table is per-delta minimum; rebuild it from my per-option cost.
        order = np.argsort(mine, kind="stable")
        uniq, first = np.unique(r6i._DELTA[order], return_index=True)
        rebuilt = np.full(r6i.STATES, r6i.INF, dtype=np.int64)
        rebuilt[uniq] = mine[order][first]
        r6i_exact = r6i_exact and bool(np.array_equal(frozen, rebuilt))
        r6i_keys += 1
    out = {
        "f3_table_exact": f3_exact,
        "r6m_tag_cost_exact": tag_exact,
        "r6m_frame_cost_tables_exact": frame_exact,
        "r6m_sampled_keys": r6m_keys,
        "r6m_sampled_cost_arrays_exact": r6m_exact,
        "r6i_sampled_keys": r6i_keys,
        "r6i_sampled_cost_tables_exact": r6i_exact,
    }
    out["all_exact"] = all(bool(v) for k, v in out.items() if k.endswith("exact"))
    return out


# ---- R6I weight-one-restricted optimum --------------------------------------

_NONID = (1, 2, 3)
_ORDERED_PAIRS = tuple(itertools.permutations(_NONID, 2))
_PERM3 = tuple(itertools.permutations(range(3)))


def _lkey(letter: int, q: int):
    bx, bz = h.CODE_BITS[letter]
    return (bx << q, bz << q)


def _forced_letter(a0: int, a1: int, bits: tuple[int, int]) -> int:
    """Unique letter with syndromes `bits` against the ordered basis (a0,a1)."""
    if bits == (0, 1):
        return a0
    if bits == (1, 0):
        return a1
    if bits == (1, 1):
        return 6 - a0 - a1
    raise AssertionError({"r6n_forced_letter_zero_syndrome": bits})


def _selfcheck_forced_letters() -> bool:
    for a0, a1 in _ORDERED_PAIRS:
        for bits in ((0, 1), (1, 0), (1, 1)):
            s = _forced_letter(a0, a1, bits)
            if (h.local_symp(s, a0), h.local_symp(s, a1)) != bits:
                return False
    return True


def r6i_weight_one_restricted(targets_a, targets_b, n: int) -> int:
    """Exact optimum of the frozen R6I weight-one-restricted family.

    All three frame Paulis weight one per block (forced to a single anchor
    qubit by <R0,R1>=1), zero Uanti support, all 6 relative B-target
    permutations, all 6 shared label assignments, unique minimum-weight
    shared Tag (weight 1 per bit at a compatible common anchor, else 2).
    """
    targets_a = tuple(tuple(t) for t in targets_a)
    targets_b = tuple(tuple(t) for t in targets_b)

    def frame(q, u0, u1):
        return (_lkey(u0, q), _lkey(u1, q), _lkey(6 - u0 - u1, q))

    rest_a = {}
    rest_b = {}
    for q in range(n):
        for u0, u1 in _ORDERED_PAIRS:
            rs = frame(q, u0, u1)
            rest_a[(q, u0, u1)] = sum(p10.wt(p10.mul(targets_a[k], rs[k])) for k in range(3))
            rest_b[(q, u0, u1)] = min(
                sum(p10.wt(p10.mul(targets_b[perm[k]], rs[k])) for k in range(3))
                for perm in _PERM3
            )
    best = None
    # Different anchor qubits: both Tag bits forced at both anchors, tag = 8.
    if n >= 2:
        min_a = [min(rest_a[(q, u0, u1)] for u0, u1 in _ORDERED_PAIRS) for q in range(n)]
        min_b = [min(rest_b[(q, u0, u1)] for u0, u1 in _ORDERED_PAIRS) for q in range(n)]
        for qa in range(n):
            for qb in range(n):
                if qa == qb:
                    continue
                cost = 8 + min_a[qa] + min_b[qb]
                if best is None or cost < best:
                    best = cost
    # Common anchor qubit: tag = 4 when the forced letters are consistent.
    labels = [(l0, l1) for l0 in _NONID for l1 in _NONID if l0 != l1]
    for q in range(n):
        for a0, a1 in _ORDERED_PAIRS:
            for b0, b1 in _ORDERED_PAIRS:
                feasible = False
                for l0, l1 in labels:
                    hi = ((l0 >> 1) & 1, (l1 >> 1) & 1)
                    lo = (l0 & 1, l1 & 1)
                    if _forced_letter(a0, a1, hi) != _forced_letter(b0, b1, hi):
                        continue
                    if _forced_letter(a0, a1, lo) != _forced_letter(b0, b1, lo):
                        continue
                    feasible = True
                    break
                if not feasible:
                    continue
                cost = 4 + rest_a[(q, a0, a1)] + rest_b[(q, b0, b1)]
                if best is None or cost < best:
                    best = cost
    if best is None:
        raise AssertionError("r6n restricted R6I family produced no feasible point")
    return int(best)


# ---- frozen-subject receipt audits ------------------------------------------

def _load(name: str) -> dict[str, Any]:
    return json.loads(Path(__file__).with_name(name).read_text())


def audit_r6m_receipt() -> dict[str, Any]:
    rec = _load("MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json")
    rows = []
    reconstructed = {}
    for subject, sub in sorted(rec["subjects"].items()):
        n = int(sub["n_qubits"])
        term_map: dict[int, tuple[int, int]] = {}
        for row in sub["candidate_points"]:
            w = row["witness"]
            pairs = [tuple(int(i) for i in p) for p in row["matching"]]
            perms = (0, int(w["relative_permutation_B"]), int(w["relative_permutation_C"]))
            for j, block in enumerate("ABC"):
                tpair = [tuple(int(x) for x in t) for t in w["targets"][block]]
                order = (0, 1) if perms[j] == 0 else (1, 0)
                for slot in range(2):
                    idx = pairs[j][order[slot]]
                    if idx in term_map and term_map[idx] != tpair[slot]:
                        raise AssertionError({"r6n_r6m_target_reconstruction_conflict": [subject, idx]})
                    term_map[idx] = tpair[slot]
        six = sorted(term_map)
        if len(six) != 6:
            raise AssertionError({"r6n_r6m_reconstruction_not_six_terms": [subject, six]})
        terms: list[tuple[tuple[int, int], float]] = [((0, 0), 0.0)] * (max(six) + 1)
        for idx in six:
            terms[idx] = (term_map[idx], 0.0)
        reconstructed[subject] = {"n": n, "targets": dict(term_map)}
        for row in sub["candidate_points"]:
            pairs = tuple(tuple(int(i) for i in p) for p in row["matching"])
            donor = r6m.donor_r6l_matching(terms, pairs, n, six)
            rows.append(
                {
                    "subject": subject,
                    "matching": [list(p) for p in pairs],
                    "C_R6M": int(row["C_R6M"]),
                    "C_R6L_receipt": int(row["C_R6L_same_matching"]),
                    "C_R6L_recomputed": int(donor["C_R6L"]),
                    "equal": int(row["C_R6M"]) == int(row["C_R6L_same_matching"]) == int(donor["C_R6L"]),
                }
            )
    return {
        "receipt_authority": rec["authority"],
        "matchings_checked": len(rows),
        "rows": rows,
        "all_equal": all(r["equal"] for r in rows),
        "reconstructed": reconstructed,
    }


def audit_r6i_receipt(r6m_reconstructed: dict[str, Any]) -> dict[str, Any]:
    rec = _load("MAX_R6I_EXACT_RANK2_SHARED_TAG_DP_RESULTS.json")
    rows = []
    cross_consistent = True
    for subject, sub in sorted(rec["subjects"].items()):
        n = int(r6m_reconstructed[subject]["n"])
        r6m_targets = r6m_reconstructed[subject]["targets"]
        term_map: dict[int, tuple[int, int]] = {}
        for row in sub["partitions"]:
            w = row["witness"]
            a = [int(i) for i in row["partition"][0]]
            b = [int(i) for i in row["partition"][1]]
            perm = [int(x) for x in w["relative_B_permutation"]]
            ra = [tuple(int(x) for x in r) for r in w["RA"]]
            rb = [tuple(int(x) for x in r) for r in w["RB"]]
            ta = [tuple(int(x) for x in e["T"]) for e in w["signed_T_A"]]
            tb = [tuple(int(x) for x in e["T"]) for e in w["signed_T_B"]]
            recomputed = (
                int(w["uanti_support_A"]) + int(w["uanti_support_B"])
                + int(w["tag_support_twice_shared"])
                + int(w["restore_support_A"]) + int(w["restore_support_B"])
            )
            if recomputed != int(w["C_shared"]) or int(w["C_shared"]) != int(row["C_shared"]):
                raise AssertionError({"r6n_r6i_receipt_cost_mismatch": [subject, row["partition"]]})
            for k in range(3):
                term_map.setdefault(a[k], p10.mul(ta[k], ra[k]))
                if term_map[a[k]] != p10.mul(ta[k], ra[k]):
                    raise AssertionError({"r6n_r6i_target_conflict": [subject, a[k]]})
                idx = b[perm[k]]
                term_map.setdefault(idx, p10.mul(tb[k], rb[k]))
                if term_map[idx] != p10.mul(tb[k], rb[k]):
                    raise AssertionError({"r6n_r6i_target_conflict": [subject, idx]})
        cross_consistent = cross_consistent and all(
            term_map.get(i) == t for i, t in r6m_targets.items()
        ) and sorted(term_map) == sorted(r6m_targets)
        for row in sub["partitions"]:
            a = [int(i) for i in row["partition"][0]]
            b = [int(i) for i in row["partition"][1]]
            targets_a = [term_map[i] for i in a]
            targets_b = [term_map[i] for i in b]
            restricted = r6i_weight_one_restricted(targets_a, targets_b, n)
            c_shared = int(row["C_shared"])
            if restricted < c_shared:
                raise AssertionError(
                    {"r6n_restricted_below_exact_dp": [subject, row["partition"], restricted, c_shared]}
                )
            rows.append(
                {
                    "subject": subject,
                    "partition": [a, b],
                    "C_shared": c_shared,
                    "C_weight_one_restricted": restricted,
                    "equal": restricted == c_shared,
                }
            )
    return {
        "receipt_authority": rec["authority"],
        "partitions_checked": len(rows),
        "rows": rows,
        "all_equal": all(r["equal"] for r in rows),
        "cross_receipt_target_consistency": cross_consistent,
    }


# ---- post-gate diagnostic: weight-one frames with unrestricted Tag ----------

def r6m_weight_one_frames_any_tag(terms, pairs, n: int) -> int:
    """Diagnostic optimum: weight-one M2 frames, Tag unrestricted (minimal).

    Mirrors the frozen R6M grammar (block A target order canonical, B/C
    permuted, both label orientations) but restricts every frame Pauli to a
    single anchor letter; the shared Tag is the unique minimum-weight Pauli
    forced at the anchor qubits (weight = number of distinct anchors). This is
    NOT a frozen gate: it exists to characterize any G7 gap as Tag-anchor
    coupling versus genuine spread-frame support.
    """
    targets = [
        (tuple(terms[i][0]), tuple(terms[j][0])) for i, j in pairs
    ]
    best = None
    for perm_b in (0, 1):
        for perm_c in (0, 1):
            ordered = [
                targets[0],
                targets[1] if perm_b == 0 else (targets[1][1], targets[1][0]),
                targets[2] if perm_c == 0 else (targets[2][1], targets[2][0]),
            ]
            for labels in ((0, 1), (1, 0)):
                for anchors in itertools.product(range(n), repeat=3):
                    for lp in itertools.product(_ORDERED_PAIRS, repeat=3):
                        # forced S letter per block: u0 for labels (0,1), u1 for (1,0)
                        forced = {}
                        ok = True
                        for j in range(3):
                            u = lp[j][0] if labels == (0, 1) else lp[j][1]
                            if anchors[j] in forced and forced[anchors[j]] != u:
                                ok = False
                                break
                            forced[anchors[j]] = u
                        if not ok:
                            continue
                        tag = 2 * len(forced)
                        restores = []
                        for j in range(3):
                            row = []
                            for k in range(2):
                                r = _lkey(lp[j][k], anchors[j])
                                row.append(p10.mul(ordered[j][k], r))
                            restores.append(row)
                        factored = 0
                        for k in range(2):
                            ta, tb, tc = restores[0][k], restores[1][k], restores[2][k]
                            for q in range(n):
                                la = h.BITS_CODE[((ta[0] >> q) & 1, (ta[1] >> q) & 1)]
                                lb = h.BITS_CODE[((tb[0] >> q) & 1, (tb[1] >> q) & 1)]
                                lc = h.BITS_CODE[((tc[0] >> q) & 1, (tc[1] >> q) & 1)]
                                factored += int(F3[la, lb, lc])
                        cost = tag + factored
                        if best is None or cost < best:
                            best = cost
    if best is None:
        raise AssertionError("r6n weight-one-frames-any-tag family empty")
    return int(best)


# ---- deterministic synthetic joint panels -----------------------------------

def synthetic_panels() -> dict[str, Any]:
    r6i_rows = []
    for name, (n, targets_a, targets_b) in sorted(r6i.HOSTILE_PANELS.items()):
        witness = r6i.shared_tag_exact(targets_a, targets_b, n)
        unrestricted = int(witness["C_shared"])
        restricted = r6i_weight_one_restricted(targets_a, targets_b, n)
        if restricted < unrestricted:
            raise AssertionError({"r6n_synthetic_restricted_below_dp": name})
        r6i_rows.append(
            {
                "panel": name,
                "n": n,
                "C_unrestricted_dp": unrestricted,
                "C_weight_one_restricted": restricted,
                "equal": restricted == unrestricted,
            }
        )
    r6m_rows = []
    n1 = {
        name: tuple((r6m._N1_LETTER_KEY[a], r6m._N1_LETTER_KEY[b]) for a, b in pairs)
        for name, pairs in r6m._HOSTILE_N1_PANELS.items()
    }
    instances = [(name, 1, pairs) for name, pairs in sorted(n1.items())]
    instances += [(name, 2, pairs) for name, pairs in sorted(r6m._HOSTILE_N2_PANELS.items())]
    for name, n, target_pairs in instances:
        terms = r6m._synthetic_terms(target_pairs)
        witness = r6m.exact_r6m_matching(terms, r6m._SYNTHETIC_MATCHING, n, list(range(6)))
        unrestricted = int(witness["C_R6M"])
        restricted = int(
            r6m.donor_r6l_matching(terms, r6m._SYNTHETIC_MATCHING, n, list(range(6)))["C_R6L"]
        )
        if restricted < unrestricted:
            raise AssertionError({"r6n_synthetic_restricted_below_dp": name})
        dp_max_frame_weight = max(
            p10.wt(tuple(r)) for block in "ABC" for r in witness["R"][block]
        )
        row = {
            "panel": name,
            "n": n,
            "C_unrestricted_dp": unrestricted,
            "C_weight_one_restricted": restricted,
            "equal": restricted == unrestricted,
            "dp_witness_max_frame_weight": int(dp_max_frame_weight),
            "dp_witness_tag_weight": int(p10.wt(tuple(witness["S"]))),
        }
        if not row["equal"]:
            # Post-gate diagnostic only (not a frozen gate): locate the gap.
            diag = r6m_weight_one_frames_any_tag(terms, r6m._SYNTHETIC_MATCHING, n)
            row["C_weight_one_frames_any_tag_diagnostic"] = diag
        r6m_rows.append(row)
    return {
        "r6i": r6i_rows,
        "r6m": r6m_rows,
        "instances": len(r6i_rows) + len(r6m_rows),
        "all_sound": True,
        "all_equal": all(r["equal"] for r in r6i_rows + r6m_rows),
    }


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "Frozen R6I two-block rank-2 dependent TARE-3 shared-two-bit-Tag grammar with plain "
        "Restore support, and frozen R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar "
        "with the donor-owned all-three Restore common-factor rule, under the frozen raw "
        "support-count objectives (4 non-central / 2 central multiplicities, frozen constants)."
    ),
    "explains": (
        "The empirical collapses of the R6I, R6K and R6M exact DP optima onto the weight-one "
        "R6H/R6J/R6L donor families on both frozen open subjects; R6K combines the two "
        "verified mechanisms (rank-2 frame costs as in Lemma N-I, common-factor savings "
        "bounded as in Lemma N-M') although its specific local table is not separately "
        "enumerated here."
    ),
    "does_not_cover": (
        "Other objectives (coefficient-weighted or non-support cost models), rotation-count "
        "trade-offs beyond the frozen fixed counts, larger Tag ranks, grammars outside the "
        "frozen families, or qubit counts beyond the finite equality domains: the local "
        "inequalities hold per qubit for every n, but the joint Tag-coupling closure is "
        "verified only on the recorded instances (30 matchings, 20 partitions, 12 synthetic "
        "panels). No novelty credit, no donor credit, no R6 authority."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()
    if not _selfcheck_forced_letters():
        raise AssertionError("r6n forced-letter syndrome map self-check failed")

    binding = verify_binding()
    if not binding["all_exact"]:
        raise AssertionError({"r6n_frozen_table_binding_failed": binding})

    r6m_primary = verify_r6m_primary()
    r6m_letterwise = verify_r6m_letterwise()
    r6i_primary = verify_r6i_primary()

    r6m_subjects = audit_r6m_receipt()
    r6i_subjects = audit_r6i_receipt(r6m_subjects["reconstructed"])
    r6m_subjects.pop("reconstructed")
    panels = synthetic_panels()

    gates = {
        "r6m_local_inequality_holds": r6m_primary["holds"],
        "r6m_letterwise_monotonicity_holds": r6m_letterwise["holds"],
        "r6i_local_inequality_holds": r6i_primary["holds"],
        "frozen_table_binding_exact": binding["all_exact"],
        "r6m_weight_one_equality_on_frozen_subjects": r6m_subjects["all_equal"],
        "r6i_weight_one_equality_on_frozen_subjects": r6i_subjects["all_equal"],
        "cross_receipt_target_consistency": r6i_subjects["cross_receipt_target_consistency"],
        "synthetic_joint_equality": panels["all_equal"],
        "no_new_subject_data": True,
    }
    integrity = {
        k: gates[k]
        for k in ("frozen_table_binding_exact", "cross_receipt_target_consistency", "no_new_subject_data")
    }
    if not all(integrity.values()):
        raise AssertionError({"r6n_integrity_gate_failure": integrity})

    violations = (
        int(r6m_primary["violations"]) + int(r6m_letterwise["violations"]) + int(r6i_primary["violations"])
    )
    joint_gaps = [
        row
        for row in (r6m_subjects["rows"] + r6i_subjects["rows"] + panels["r6i"] + panels["r6m"])
        if not row["equal"]
    ]
    verified = violations == 0 and not joint_gaps and all(gates.values())
    if verified:
        authority = "MAX_R6N_SUPPORT_DOMINANCE_VERIFIED__FAMILY_CLOSURE_EVIDENCE__NOT_R6"
        responsibility = (
            "RESP:WEIGHT_ONE_DONOR_FAMILY_OPTIMAL_ON_ALL_VERIFIED_FINITE_DOMAINS__"
            "R6B_TO_R6M_RESIDUAL_LANES_EXPLAINED_ANALYTICALLY"
        )
        discovery = None
    else:
        authority = "MAX_R6N_SUPPORT_DOMINANCE_REFUTED__NEW_REGIME_FOUND__NOT_R6"
        responsibility = "RESP:SPREAD_SUPPORT_REGIME_DISCOVERED__REPORT_VERBATIM_AND_RE_FREEZE"
        gap_frames_all_weight_one = all(
            row.get("dp_witness_max_frame_weight", 1) == 1 for row in joint_gaps
        )
        discovery = {
            "local_violation_count": violations,
            "violating_local_configs": (
                r6m_primary["violating_configs_verbatim"]
                + r6m_letterwise["violating_configs_verbatim"]
                + r6i_primary["violating_configs_verbatim"]
            ),
            "joint_gaps_unrestricted_beats_weight_one": joint_gaps,
            "characterization": {
                "frame_support_dominance_violated": violations > 0
                or not gap_frames_all_weight_one,
                "donor_family_tag_anchor_coupling_violated": bool(joint_gaps)
                and gap_frames_all_weight_one,
                "note": (
                    "Every joint-gap DP witness with dp_witness_max_frame_weight == 1 uses "
                    "weight-one frames outside the donor family: blocks anchored at "
                    "different qubits with a spread (weight >= 2) shared Tag, which the "
                    "R6L common-weight-one-Tag donor grammar cannot express. In that case "
                    "the per-unit frame support-dominance component of the lemma survives "
                    "all checks and the refuted component is exactly the declared "
                    "Tag-anchor coupling gap. The diagnostic "
                    "C_weight_one_frames_any_tag_diagnostic column locates the gap: "
                    "equality with C_unrestricted_dp confirms Tag-anchor coupling as the "
                    "sole broken mechanism. This characterization is post-gate diagnosis, "
                    "not a frozen gate; the frozen outcome mapping stands."
                ),
            },
        }

    total_checked = (
        int(r6m_primary["domain_size"]) + int(r6m_letterwise["domain_size"]) + int(r6i_primary["domain_size"])
    )
    runtime = time.monotonic() - start
    result = {
        "schema": "ORIONQ.MAXR6N.SupportDominanceAudit.v1",
        "authority": authority,
        "scope": (
            "SUPPORT_DOMINANCE_LEMMA_AUDIT_OVER_FROZEN_R6I_R6M_GRAMMARS_AND_RECEIPTS__"
            "EXPLANATORY_FAMILY_CLOSURE__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "MAX_R6N_SUPPORT_DOMINANCE_PROTOCOL",
        "lemma": {
            "statement": (
                "Within the frozen TARE frame-grammar families and support-count objectives, "
                "each unit of frame support costs >=2 (central) or 4 (non-central) in the raw "
                "Uanti term while its maximum achievable Restore/factor savings is <=2 per "
                "unit; hence exact optima are attained by minimal-support (weight-one) frames "
                "and the weight-one donor family is optimal within the full grammar."
            ),
            "N_M": "R6M per-qubit TotalSavings(F,T) <= FrameCost_c(F) over 4^6 x 4 x 8 x 4^6 configs",
            "N_M_prime": "R6M letterwise exchange monotonicity over 343 x 64 x 8 configs",
            "N_I": "R6I per-qubit TotalSavings <= FrameCost over 4^4 x 16 x 9 x 4^6 configs",
            "declared_gap": (
                "Tag-repair coupling after frame truncation is not bounded by the local "
                "inequalities; it is closed on finite domains by the joint equality checks "
                "(frozen subjects and synthetic n=1/n=2 panels) only."
            ),
        },
        "local_verification": {
            "r6m_primary": r6m_primary,
            "r6m_letterwise_monotone": r6m_letterwise,
            "r6i_primary": r6i_primary,
            "total_local_configurations_checked": total_checked,
        },
        "implementation_binding": binding,
        "frozen_subject_equality": {"r6m": r6m_subjects, "r6i": r6i_subjects},
        "synthetic_panels": panels,
        "gates": gates,
        "discovery": discovery,
        "claim_boundary": CLAIM_BOUNDARY,
        "runtime_seconds": round(runtime, 3),
        "chemistry_sources_read": False,
        "heavy_subject_dp_rerun": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("R6N authority ceiling violated")
    Path(__file__).with_name("MAX_R6N_SUPPORT_DOMINANCE_RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("ORIONQ_MAX_R6N_SUPPORT_DOMINANCE=" + canonical_json(result))
    return result


if __name__ == "__main__":
    main()
