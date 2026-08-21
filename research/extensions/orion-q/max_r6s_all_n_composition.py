#!/usr/bin/env python3
"""MAX-R6S all-n composition: support >= 3 exchange theorem with Tag repair.

Frozen by MAX_R6S_ALL_N_COMPOSITION_PROTOCOL.md (frozen before outcome).

Attempts the open object named by the R6P receipt: convert R6P's bounded
machine evidence (C_DP == C_D++ on all verified finite domains) into an all-n
theorem for the frozen R6M grammar -- frame Paulis of global support >= 3
never strictly pay.

The frozen exchange construction (stated in full in the protocol): given any
feasible configuration containing a frame Pauli R of support w >= 3, classify
each support qubit q by class(q) = (alpha, beta) in F_2^2 with
alpha = local_symp(R letter, partner letter) and
beta = local_symp(Tag letter, R letter). The class multiset has odd
alpha-sum (= symp(R, partner) = 1). Lemma B (pigeonhole): any such multiset
with w >= 3 contains a class-(0,0) singleton or an equal-class pair -- a
nonempty PROPER subset Q, |Q| <= 2, with even alpha- and beta-sums. Zeroing
R's letters on Q preserves every acceptance bit with ZERO Tag repair, and by
Lemma E (exhaustive, 18,432 cases) the branch-F3 increase per qubit never
exceeds the frame refund m in {2,4}. Induction on (cost, total support)
closes the theorem; support 2 differs from support 3 exactly because the
failing class pattern {(1,*),(0,1)} is realizable only at w = 2 (the R6O
weight-2 trade).

Honest outcome space: THEOREM_MACHINE_CHECKED / GAP_FOUND / PARTIAL. The
seeded stress panel (seed 20260822, 40 x n=3 + 30 x n=4) runs regardless.
Not R6; no novelty credit; no chemistry data is read; the protected
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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
SEED = 20260822
MATCHING = ((0, 1), (2, 3), (4, 5))
PAIR_COUNTS_SUPPORT2 = {1: 6, 2: 120, 3: 666, 4: 1968}
PANEL_PLAN = ((3, 40), (4, 30))
DESCENTS_PER_INSTANCE = 3
VERBATIM_CAP = 20

# ---- independent local algebra tables (bound to frozen r6m below) -----------
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


def bind_tables() -> dict[str, bool]:
    return {
        "LW_binds": bool(np.array_equal(LW, r6m._LW)),
        "LM_binds": bool(np.array_equal(LM, r6m._LM)),
        "SY_binds": bool(np.array_equal(SY, r6m._SY)),
        "F3_binds": bool(np.array_equal(F3, r6m._F3)),
    }


# ---- Lemma E: single-zeroing local exchange inequality ----------------------


def verify_lemma_e() -> dict[str, Any]:
    """F3(new) - F3(old) - m <= 0 over the full 18,432-case zeroing domain.

    Domain per protocol: zeroed letter f in {X,Y,Z}; partner letter fp,
    tag letter sigma, target letter p, other-slot letters u, v in
    {I,X,Y,Z}; multiplier m in {2,4}; zeroed-slot position in {A,B,C}.
    fp and sigma do not enter the inequality; they define the class
    tabulation and are swept as declared.
    """
    fi, fp, sg, pp, uu, vv = np.meshgrid(
        np.arange(1, 4), np.arange(4), np.arange(4), np.arange(4),
        np.arange(4), np.arange(4), indexing="ij",
    )
    old = LM[pp, fi]  # old slot letter = p * f (T = P * R); new slot letter = p
    alpha = SY[fi, fp]
    beta = SY[sg, fi]
    checked = 0
    violations = []
    tie_count = 0
    ties_only_central = True
    max_df3 = -(10 ** 9)
    max_ratio = -1.0
    class_tab: dict[str, int] = {}
    for slot in range(3):
        if slot == 0:
            new_f3, old_f3 = F3[pp, uu, vv], F3[old, uu, vv]
        elif slot == 1:
            new_f3, old_f3 = F3[uu, pp, vv], F3[uu, old, vv]
        else:
            new_f3, old_f3 = F3[uu, vv, pp], F3[uu, vv, old]
        df3 = new_f3 - old_f3
        max_df3 = max(max_df3, int(df3.max()))
        for m in (2, 4):
            net = df3 - m
            checked += net.size
            max_ratio = max(max_ratio, float(df3.max()) / float(m))
            n_tie = int((net == 0).sum())
            tie_count += n_tie
            if n_tie and m != 2:
                ties_only_central = False
            bad = np.argwhere(net > 0)
            for row in bad[: max(0, VERBATIM_CAP - len(violations))]:
                i0, i1, i2, i3, i4, i5 = (int(x) for x in row)
                violations.append(
                    {
                        "zeroed_letter": LETTERS[i0 + 1],
                        "partner_letter": LETTERS[i1],
                        "tag_letter": LETTERS[i2],
                        "target_letter": LETTERS[i3],
                        "other_slots": [LETTERS[i4], LETTERS[i5]],
                        "multiplier": m,
                        "slot": "ABC"[slot],
                        "delta_f3": int(df3[i0, i1, i2, i3, i4, i5]),
                        "net": int(net[i0, i1, i2, i3, i4, i5]),
                    }
                )
            n_viol = int((net > 0).sum())
            if n_viol > len(bad[:VERBATIM_CAP]):
                pass  # count kept below; verbatim capped
            # class tabulation: worst net per class over this (slot, m) sheet
            for a_bit in (0, 1):
                for b_bit in (0, 1):
                    mask = (alpha == a_bit) & (beta == b_bit)
                    key = f"class_{a_bit}{b_bit}_max_net"
                    val = int(net[mask].max())
                    class_tab[key] = max(class_tab.get(key, -(10 ** 9)), val)
    total_violations = 0
    for slot in range(3):
        if slot == 0:
            df3 = F3[pp, uu, vv] - F3[old, uu, vv]
        elif slot == 1:
            df3 = F3[uu, pp, vv] - F3[uu, old, vv]
        else:
            df3 = F3[uu, vv, pp] - F3[uu, vv, old]
        for m in (2, 4):
            total_violations += int((df3 - m > 0).sum())
    return {
        "domain_size": checked,
        "violations": total_violations,
        "holds": total_violations == 0,
        "max_delta_f3": max_df3,
        "max_savings_over_refund_ratio": max_ratio,
        "tie_count": tie_count,
        "ties_only_at_central_multiplier": ties_only_central,
        "class_tabulation_max_net": class_tab,
        "violating_cases_verbatim": violations,
    }


# ---- Lemma B: zero-sum subset existence over class multisets ----------------


def _zero_sum_subset(codes: tuple[int, ...]):
    """Nonempty PROPER subset of size <= 2 with zero class sum, or None.

    Classes are coded alpha*2 + beta; each class is self-inverse in F_2^2,
    so zero-sum singletons are class (0,0) and zero-sum pairs are equal
    pairs. Frozen deterministic rule: lowest (0,0) singleton, else
    lexicographically lowest equal pair.
    """
    w = len(codes)
    for i, c in enumerate(codes):
        if c == 0 and w > 1:
            return (i,)
    for i in range(w):
        for j in range(i + 1, w):
            if codes[i] == codes[j] and w > 2:
                return (i, j)
    return None


def verify_lemma_b() -> dict[str, Any]:
    per_w = {}
    predicted_w2_failures = sorted([(1, 2), (1, 3), (2, 1), (3, 1)])
    w2_failures = []
    total_checked = 0
    for w in range(2, 9):
        checked = 0
        failures = 0
        fail_examples = []
        for combo in itertools.product(range(4), repeat=w):
            if sum(c >> 1 for c in combo) % 2 != 1:
                continue  # support alpha-sum is always odd
            checked += 1
            if _zero_sum_subset(combo) is None:
                failures += 1
                if w == 2:
                    w2_failures.append(combo)
                elif len(fail_examples) < VERBATIM_CAP:
                    fail_examples.append(list(combo))
        total_checked += checked
        per_w[str(w)] = {
            "odd_alpha_tuples_checked": checked,
            "failures": failures,
            "failure_examples": fail_examples,
        }
    w2_observed = sorted(w2_failures)
    return {
        "total_odd_alpha_tuples_checked": total_checked,
        "per_w": per_w,
        "w3_to_w8_failures": sum(per_w[str(w)]["failures"] for w in range(3, 9)),
        "w3_to_w8_all_admit_subset": all(
            per_w[str(w)]["failures"] == 0 for w in range(3, 9)
        ),
        "w2_failing_tuples_observed": [list(t) for t in w2_observed],
        "w2_failing_tuples_predicted": [list(t) for t in predicted_w2_failures],
        "w2_boundary_exact": w2_observed == predicted_w2_failures,
        "w2_boundary_note": (
            "Class code = 2*alpha + beta. The failing w=2 patterns are exactly "
            "the odd-alpha tuples whose alpha=0 qubit has beta=1: zeroing the "
            "locally-commuting qubit must flip the Tag syndrome -- the R6O "
            "weight-2 trade. At w >= 3 the pattern is unrealizable (Lemma B)."
        ),
    }


# ---- explicit configuration machinery (descent verification) ----------------


def _letter(key, q: int) -> int:
    return h.BITS_CODE[((key[0] >> q) & 1, (key[1] >> q) & 1)]


def config_cost(t6, frames6, s, centrals, n: int) -> int:
    raw = 0
    for j in range(3):
        m0 = 2 if centrals[j] == 0 else 4
        m1 = 2 if centrals[j] == 1 else 4
        raw += m0 * p10.wt(frames6[2 * j]) + m1 * p10.wt(frames6[2 * j + 1])
    raw += 2 * p10.wt(s)
    tt = [p10.mul(t6[i], frames6[i]) for i in range(6)]
    f3sum = 0
    for k in (0, 1):
        per_qubit = sum(
            int(F3[_letter(tt[k], q), _letter(tt[2 + k], q), _letter(tt[4 + k], q)])
            for q in range(n)
        )
        fast = r6m._factor_support_fast(tt[k], tt[2 + k], tt[4 + k])
        if per_qubit != fast:
            raise AssertionError(
                {"r6s_factor_support_binding_failed": [per_qubit, int(fast)]}
            )
        f3sum += per_qubit
    return int(raw - 18 + f3sum)


def config_labels(frames6, s):
    """(ok, labels): full acceptance predicate of the frozen R6M grammar."""
    for j in range(3):
        if p10.symp(frames6[2 * j], frames6[2 * j + 1]) != 1:
            return False, None
    l0 = p10.symp(s, frames6[0])
    l1 = p10.symp(s, frames6[1])
    for j in (1, 2):
        if p10.symp(s, frames6[2 * j]) != l0 or p10.symp(s, frames6[2 * j + 1]) != l1:
            return False, None
    if l0 == l1:
        return False, None
    if any(f == (0, 0) for f in frames6):
        return False, None
    return True, (l0, l1)


def exchange_step(t6, frames6, s, centrals, n: int):
    """One frozen exchange: zero a support->=3 frame Pauli on its subset Q."""
    i = next(idx for idx in range(6) if p10.wt(frames6[idx]) >= 3)
    j, k = divmod(i, 2)
    m = 2 if centrals[j] == k else 4
    partner = frames6[i ^ 1]
    r = frames6[i]
    supp = [q for q in range(n) if _letter(r, q) != 0]
    codes = []
    for q in supp:
        f = _letter(r, q)
        alpha = int(SY[f, _letter(partner, q)])
        beta = int(SY[_letter(s, q), f])
        codes.append(2 * alpha + beta)
    if sum(c >> 1 for c in codes) % 2 != 1:
        raise AssertionError({"r6s_support_alpha_parity_not_odd": codes})
    sel = _zero_sum_subset(tuple(codes))
    if sel is None:
        raise AssertionError({"r6s_lemma_b_subset_missing_in_realized_config": codes})
    qubits = [supp[a] for a in sel]
    mask = 0
    for q in qubits:
        mask |= 1 << q
    new_r = (r[0] & ~mask, r[1] & ~mask)
    # predicted local decomposition of the cost change
    branch = [k, 2 + k, 4 + k]  # branch-k slots of blocks A, B, C
    tt = [p10.mul(t6[b], frames6[b]) for b in range(6)]
    predicted = 0
    for q in qubits:
        letters_old = [_letter(tt[b], q) for b in branch]
        letters_new = list(letters_old)
        letters_new[j] = _letter(t6[i], q)  # slot letter reverts to raw target
        predicted += int(
            F3[tuple(letters_new)] - F3[tuple(letters_old)] - m
        )
    new_frames = list(frames6)
    new_frames[i] = new_r
    return tuple(new_frames), qubits, predicted, i


def descend(t6, frames6, s, centrals, n: int) -> dict[str, Any]:
    ok, labels = config_labels(frames6, s)
    if not ok:
        raise AssertionError("r6s descent started from an infeasible config")
    cost = config_cost(t6, frames6, s, centrals, n)
    initial = {
        "cost": cost,
        "total_support": int(sum(p10.wt(f) for f in frames6)),
        "max_support": int(max(p10.wt(f) for f in frames6)),
    }
    steps = 0
    ties = 0
    problems = []
    guard = 6 * n + 1
    while any(p10.wt(f) >= 3 for f in frames6):
        steps += 1
        if steps > guard:
            problems.append("descent_exceeded_step_guard")
            break
        old_support = sum(p10.wt(f) for f in frames6)
        new_frames, qubits, predicted, i = exchange_step(t6, frames6, s, centrals, n)
        ok2, labels2 = config_labels(new_frames, s)
        if not ok2 or labels2 != labels:
            problems.append(
                {"feasibility_broken_at_step": steps, "frame_index": i}
            )
            break
        new_cost = config_cost(t6, new_frames, s, centrals, n)
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
        if dc > 0:
            problems.append({"cost_increased_at_step": steps, "delta": dc})
            break
        new_support = sum(p10.wt(f) for f in new_frames)
        if old_support - new_support != len(qubits):
            problems.append({"support_drop_mismatch_at_step": steps})
            break
        if dc == 0:
            ties += 1
        frames6, cost = new_frames, new_cost
    final_max = int(max(p10.wt(f) for f in frames6))
    if not problems and final_max > 2:
        problems.append("descent_terminated_above_support_two")
    return {
        "initial": initial,
        "final_cost": int(cost),
        "final_max_support": final_max,
        "steps": steps,
        "tie_steps": ties,
        "problems": problems,
        "pass": not problems,
    }


def random_spread_config(rng, n: int, t6):
    """Seeded feasible configuration with at least one support->=3 frame."""
    keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)]
    nonzero = keys[1:]

    def draw():
        return nonzero[int(rng.integers(0, len(nonzero)))]

    for _attempt in range(500):
        frames = []
        bad = False
        for j in range(3):
            r0 = draw()
            if j == 0:
                tries = 0
                while p10.wt(r0) < 3:
                    r0 = draw()
                    tries += 1
                    if tries > 400:
                        bad = True
                        break
            if bad:
                break
            r1 = draw()
            tries = 0
            while p10.symp(r0, r1) != 1:
                r1 = draw()
                tries += 1
                if tries > 400:
                    bad = True
                    break
            if bad:
                break
            frames.extend([r0, r1])
        if bad or len(frames) != 6:
            continue
        feas = []
        for key in keys:
            s0 = p10.symp(key, frames[0])
            s1 = p10.symp(key, frames[1])
            if s0 == s1:
                continue
            if all(
                p10.symp(key, frames[2 * j]) == s0
                and p10.symp(key, frames[2 * j + 1]) == s1
                for j in (1, 2)
            ):
                feas.append(key)
        if not feas:
            continue
        s = feas[int(rng.integers(0, len(feas)))]
        centrals = tuple(int(rng.integers(0, 2)) for _ in range(3))
        ok, _ = config_labels(tuple(frames), s)
        if not ok:
            raise AssertionError("r6s sampled config failed its own predicate")
        return tuple(frames), s, centrals
    raise AssertionError("r6s could not sample a feasible spread config in 500 tries")


# ---- stress panel (seed 20260822) + descents --------------------------------


def independent_pair_counts() -> dict[int, int]:
    out = {}
    for n in (1, 2, 3, 4):
        keys = [(x, z) for x in range(2 ** n) for z in range(2 ** n)]
        small = [k for k in keys if k != (0, 0) and p10.wt(k) <= 2]
        out[n] = sum(1 for a in small for b in small if p10.symp(a, b) == 1)
    return out


def stress_panel_and_descents() -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    rows = []
    descents = []
    violations = []
    witness_rows = 0
    witness_ok = True
    weight1_rows = 0
    weight1_ok = True
    idx = 0
    for n, count in PANEL_PLAN:
        for i in range(count):
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
            r6m._local_table.cache_clear()
            c_dp = int(r6p.dp_cost_frozen_configs(terms, n))
            want = idx % 5 == 0
            dxx = r6p.dxx_search(target_pairs, n, want_witness=want)
            c_dxx = int(dxx["C_Dxx"])
            if c_dp > c_dxx:
                raise AssertionError(
                    {"r6s_containment_violated": [n, i, c_dp, c_dxx]}
                )
            if want:
                witness_rows += 1
                if not r6p.verify_dxx_witness(target_pairs, n, dxx["witness"]):
                    witness_ok = False
            if idx % 7 == 0:
                weight1_rows += 1
                w1 = int(r6p.dxx_search(target_pairs, n, max_weight=1)["C_Dxx"])
                dplus = int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"])
                if w1 != dplus:
                    weight1_ok = False
            row = {
                "n": n,
                "index": i,
                "targets": [list(t) for t in targets],
                "C_unrestricted_dp": c_dp,
                "C_Dxx": c_dxx,
                "equal": c_dp == c_dxx,
            }
            rows.append(row)
            if not row["equal"]:
                violations.append(row)
            # three seeded spread-frame descents on the same targets
            t6 = tuple(targets)
            for d in range(DESCENTS_PER_INSTANCE):
                frames, s, centrals = random_spread_config(rng, n, t6)
                rec = descend(t6, frames, s, centrals, n)
                rec.update({"n": n, "instance": i, "descent": d})
                if rec["pass"] and rec["final_cost"] < c_dxx:
                    rec["pass"] = False
                    rec["problems"].append(
                        {
                            "final_cost_below_C_Dxx": [rec["final_cost"], c_dxx],
                            "note": "support-<=2 config below the D++ optimum",
                        }
                    )
                descents.append(rec)
            idx += 1
        r6o._block_cache.clear()
    r6m._local_table.cache_clear()
    return {
        "seed": SEED,
        "plan": [list(p) for p in PANEL_PLAN],
        "instances": len(rows),
        "equal_count": sum(r["equal"] for r in rows),
        "all_equal": all(r["equal"] for r in rows),
        "subsampling": "none -- full frozen plan executed",
        "rows": rows,
        "violating_instances_verbatim": violations,
        "witness_verified_rows": witness_rows,
        "witness_all_ok": witness_ok,
        "weight1_binding_rows": weight1_rows,
        "weight1_binding_ok": weight1_ok,
        "descents": {
            "count": len(descents),
            "all_pass": all(r["pass"] for r in descents),
            "total_steps": sum(r["steps"] for r in descents),
            "total_tie_steps": sum(r["tie_steps"] for r in descents),
            "max_initial_support": max(r["initial"]["max_support"] for r in descents),
            "rows": [
                {
                    "n": r["n"],
                    "instance": r["instance"],
                    "descent": r["descent"],
                    "initial_cost": r["initial"]["cost"],
                    "initial_total_support": r["initial"]["total_support"],
                    "initial_max_support": r["initial"]["max_support"],
                    "final_cost": r["final_cost"],
                    "final_max_support": r["final_max_support"],
                    "steps": r["steps"],
                    "tie_steps": r["tie_steps"],
                    "pass": r["pass"],
                    "problems": r["problems"],
                }
                for r in descents
            ],
        },
    }


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "Frozen R6L/R6M three-block TARE-M2 shared-one-bit-Tag grammar with "
        "the donor-owned all-three Restore common-factor rule under the "
        "frozen raw support-count objective (multipliers 4 non-central / 2 "
        "central), for EVERY qubit count n, every target six-tuple, every "
        "matching, every relative permutation and every central choice: the "
        "unrestricted exact optimum is attained by frames of global support "
        "<= 2, hence C_DP == C_D++."
    ),
    "proof_shape": (
        "Qubit-local exchange with zero Tag repair: classes (alpha, beta) "
        "over the support of any support->=3 frame Pauli have odd alpha-sum; "
        "Lemma B (pigeonhole, written proof, machine-corroborated w<=8) "
        "yields a proper zero-sum subset of size <= 2; Lemma E (exhaustive, "
        "18,432 cases) bounds the per-qubit F3 increase by the frame refund. "
        "Induction on (cost, total frame support). The only computational "
        "steps are the two lemma checks."
    ),
    "does_not_cover": (
        "The R6I rank-2 dependent-triple grammar (zeroing one letter moves "
        "the dependent third letter between multiplier classes; no claim), "
        "coefficient-weighted or non-support objectives, rotation-count "
        "trade-offs beyond the frozen fixed counts, larger Tag ranks, or "
        "grammars outside the frozen family. The stress panel is "
        "corroboration, not the proof. No novelty credit, no donor credit, "
        "not R6."
    ),
    "support_2_boundary": (
        "The exchange fails exactly at w = 2 with class pattern "
        "{(1,*),(0,1)}: the locally-commuting qubit anticommutes with the "
        "Tag, so removal forces a Tag-syndrome flip -- the R6O weight-2 "
        "trade, realized by 559 recorded DP optima. At w >= 3 the pattern "
        "is unrealizable; the per-unit price of support is identical."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    bindings = bind_tables()
    if not all(bindings.values()):
        raise AssertionError({"r6s_table_binding_failed": bindings})

    pair_counts = independent_pair_counts()
    if pair_counts != PAIR_COUNTS_SUPPORT2:
        raise AssertionError({"r6s_pair_count_mismatch": pair_counts})
    # runtime injection only (no repository file modified): let the frozen
    # R6P enumerator run at n=4 with the independently recomputed count.
    r6p.EXPECTED_PAIR_COUNTS[4] = pair_counts[4]

    lemma_e = verify_lemma_e()
    lemma_b = verify_lemma_b()
    panel = stress_panel_and_descents()

    gates = {
        "lemma_e_zero_violations": lemma_e["holds"],
        "lemma_b_w3_to_w8_zero_failures": lemma_b["w3_to_w8_all_admit_subset"],
        "lemma_b_w2_boundary_exact": lemma_b["w2_boundary_exact"],
        "exchange_descents_all_verified": panel["descents"]["all_pass"],
        "stress_panel_equality": panel["all_equal"],
        "bindings_exact": all(bindings.values())
        and pair_counts == PAIR_COUNTS_SUPPORT2
        and panel["witness_all_ok"]
        and panel["weight1_binding_ok"],
        "no_new_subject_data": True,
    }
    integrity = {k: gates[k] for k in ("bindings_exact", "no_new_subject_data")}
    if not all(integrity.values()):
        raise AssertionError({"r6s_integrity_gate_failure": integrity})

    gap = (not gates["lemma_e_zero_violations"]) or (
        not gates["lemma_b_w3_to_w8_zero_failures"]
    )
    if not gap and all(gates.values()):
        outcome = "THEOREM_MACHINE_CHECKED"
        authority = (
            "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED__"
            "SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N__NOT_R6"
        )
        responsibility = (
            "RESP:R6P_BOUNDED_EVIDENCE_CONVERTED_TO_ALL_N_THEOREM__"
            "EXCHANGE_WITH_ZERO_TAG_REPAIR_VIA_F2SQUARED_PIGEONHOLE"
        )
        discovery = None
    elif gap:
        outcome = "GAP_FOUND"
        authority = "MAX_R6S_ALL_N_COMPOSITION_GAP_FOUND__EXCHANGE_CASE_FAILS__NOT_R6"
        responsibility = "RESP:EXCHANGE_CASE_GAP__TEST_REALIZABILITY_AND_RE_FREEZE"
        discovery = {
            "lemma_e_violations_verbatim": lemma_e["violating_cases_verbatim"],
            "lemma_b_failures": {
                w: lemma_b["per_w"][w]["failure_examples"]
                for w in lemma_b["per_w"]
                if lemma_b["per_w"][w]["failures"] and w != "2"
            },
            "empirical_realizability": {
                "stress_panel_gap_instances": panel["violating_instances_verbatim"],
                "realized_as_dp_optimum": bool(
                    panel["violating_instances_verbatim"]
                ),
                "note": (
                    "A realized C_DP < C_Dxx instance would be a THIRD regime "
                    "beyond R6N Tag-anchor coupling and the R6O weight-2 trade."
                ),
            },
        }
    else:
        outcome = "PARTIAL"
        authority = "MAX_R6S_ALL_N_COMPOSITION_PARTIAL__STATED_CASES_ONLY__NOT_R6"
        responsibility = (
            "RESP:LEMMAS_CLOSE_BUT_DESCENT_OR_PANEL_ASSERTION_FAILED__"
            "IMPLEMENTATION_OR_UNMODELED_COUPLING_SUSPECT"
        )
        discovery = {
            "failed_descents": [
                r for r in panel["descents"]["rows"] if not r["pass"]
            ],
            "stress_panel_gap_instances": panel["violating_instances_verbatim"],
            "w2_boundary_mismatch": not gates["lemma_b_w2_boundary_exact"],
        }

    result = {
        "schema": "ORIONQ.MAXR6S.AllNComposition.v1",
        "authority": authority,
        "outcome": outcome,
        "scope": (
            "ALL_N_SUPPORT3_EXCHANGE_THEOREM_OVER_FROZEN_R6M_GRAMMAR__"
            "EXPLANATORY_FAMILY_CLOSURE__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "MAX_R6S_ALL_N_COMPOSITION_PROTOCOL",
        "theorem_statement": (
            "For every n and every target configuration of the frozen R6M "
            "grammar (any matching, relative permutations and centrals), the "
            "unrestricted exact DP optimum equals the D++ optimum: frame "
            "Paulis of global support >= 3 never strictly pay."
        ),
        "exchange_construction": {
            "classes": (
                "class(q) = (local_symp(frame letter, partner letter), "
                "local_symp(tag letter, frame letter)) in F_2^2 for q in "
                "supp(R); the multiset has odd alpha-sum = symp(R, partner)."
            ),
            "subset_rule": (
                "lowest class-(0,0) singleton, else lexicographically lowest "
                "equal-class pair; |Q| <= 2 < w, so R stays nonzero; even "
                "alpha-/beta-sums preserve the anticommutation bit and the "
                "Tag syndrome with ZERO Tag repair."
            ),
            "cost_bound": (
                "Delta C = sum_{q in Q} [F3(new)-F3(old)-m] <= 0 by Lemma E; "
                "m in {2,4} is the zeroed Pauli's multiplier."
            ),
            "induction": (
                "lexicographic (cost, total frame support) minimum admits no "
                "support->=3 frame; D++ equality follows via the frozen R6P "
                "Tag-relaxation identity."
            ),
        },
        "lemma_e": lemma_e,
        "lemma_b": lemma_b,
        "stress_panel": panel,
        "anticommuting_support2_pair_counts": {
            str(k): v for k, v in pair_counts.items()
        },
        "expected_pair_count_injection": {
            "module": "max_r6p_weight2_frame_donor_closure",
            "key": 4,
            "value": pair_counts[4],
            "repository_files_modified": False,
        },
        "gates": gates,
        "discovery": discovery,
        "claim_boundary": CLAIM_BOUNDARY,
        "chemistry_sources_read": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("R6S authority ceiling violated")
    print("ORIONQ_MAX_R6S_ALL_N_COMPOSITION=" + canonical_json(result))
    runtime = time.monotonic() - start
    file_result = dict(result)
    file_result["runtime_seconds"] = round(runtime, 3)
    Path(__file__).with_name("MAX_R6S_ALL_N_COMPOSITION_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n"
    )
    return result


if __name__ == "__main__":
    main()
