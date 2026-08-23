#!/usr/bin/env python3
"""MAX-R5J anchored dependent TARE-3 (ADT3) development on open H4/N2.

This implements the frozen construction in
MAX_R5J_ANCHORED_DEPENDENT_TARE3_DEVELOPMENT_PROTOCOL.md. It compares an
exact native-anchor dependent frame against a strengthened reconstruction of
the canonical TARE-v4 three-generator donor.
"""
from __future__ import annotations

import itertools
import json
import math
import random
import statistics
from dataclasses import dataclass

import max_r5h_mixed_cardinality_development as b

h = b.h
INF = 10**9
LABELS = (1, 2, 3)  # 01, 10, 11; XOR is zero.
TAG_HIGH_SYNDROME = 0b110
TAG_LOW_SYNDROME = 0b101


def mul(a, c):
    return (a[0] ^ c[0], a[1] ^ c[1])


def wt(k):
    return (k[0] | k[1]).bit_count()


def symp(a, c):
    return ((a[0] & c[1]).bit_count() + (a[1] & c[0]).bit_count()) & 1


def codes(k, n):
    x, z = k
    return tuple(h.BITS_CODE[((x >> q) & 1, (z >> q) & 1)] for q in range(n))


def key_from_codes(cs):
    x = z = 0
    for q, code in enumerate(cs):
        bx, bz = h.CODE_BITS[code]
        x |= bx << q
        z |= bz << q
    return (x, z)


def canonical_frame(n):
    # TARE v4 Eq. (31): R_0=X0, R_1=Y0, R_2=Z0 X1.
    if n < 2:
        raise ValueError("ADT3/canonical TARE3 requires at least two qubits")
    return ((1, 0), (1, 1), (2, 1))


def tag_min_weight(rs, target_syndrome, n):
    rc = [codes(r, n) for r in rs]
    states = {0: (0, tuple())}
    for q in range(n):
        nxt = {}
        for old, (old_cost, old_seq) in states.items():
            for s in range(4):
                d = 0
                for k in range(3):
                    d |= (h.local_symp(s, rc[k][q]) << k)
                new = old ^ d
                cand = (old_cost + h.local_wt(s), old_seq + (s,))
                if new not in nxt or cand < nxt[new]:
                    nxt[new] = cand
        states = nxt
    if target_syndrome not in states:
        raise AssertionError({"unsolved_tag_syndrome": target_syndrome, "rs": rs})
    cost, seq = states[target_syndrome]
    return int(cost), key_from_codes(seq)


def uanti_support(rs, central):
    return int(sum((2 if j == central else 4) * (wt(r) - 1) for j, r in enumerate(rs)))


def canonical_best(targets, n):
    rs = canonical_frame(n)
    assert all(symp(rs[i], rs[j]) == 1 for i in range(3) for j in range(i + 1, 3))
    s_hi_w, s_hi = tag_min_weight(rs, TAG_HIGH_SYNDROME, n)
    s_lo_w, s_lo = tag_min_weight(rs, TAG_LOW_SYNDROME, n)
    best = None
    for perm in itertools.permutations(range(3)):
        ps = [targets[i] for i in perm]
        ts = [mul(ps[j], rs[j]) for j in range(3)]
        for central in range(3):
            c = uanti_support(rs, central) + 2 * (s_hi_w + s_lo_w) + sum(wt(t) for t in ts)
            rec = {
                "cost": int(c),
                "target_permutation": list(perm),
                "central": central,
                "R": [list(r) for r in rs],
                "S_high": list(s_hi),
                "S_low": list(s_lo),
                "T": [list(t) for t in ts],
                "tag_weight": int(s_hi_w + s_lo_w),
                "uanti_support": uanti_support(rs, central),
                "restore_support": int(sum(wt(t) for t in ts)),
            }
            key = (rec["cost"], tuple(perm), central, tuple(rs), s_hi, s_lo)
            if best is None or key < best[0]:
                best = (key, rec)
    return best[1]


def fixed_adt3_dp(targets, anchor_i, b_i, c_i, central, n):
    r0 = targets[anchor_i]
    pb = targets[b_i]
    pc = targets[c_i]
    r0c, pbc, pcc = codes(r0, n), codes(pb, n), codes(pc, n)
    coef = [4, 4, 4]
    coef[central] = 2
    states = {0: (0, tuple())}
    for q in range(n):
        nxt = {}
        for old_parity, (old_cost, old_seq) in states.items():
            for r1 in range(4):
                r2 = h.local_mul(r0c[q], r1)
                d = h.local_symp(r0c[q], r1)
                # Uanti support before global -1 constants, explicit dual Tag
                # S_high=R0, S_low=R1, and Restore T0=I.
                local = (
                    (coef[0] + 2) * h.local_wt(r0c[q])
                    + (coef[1] + 2) * h.local_wt(r1)
                    + coef[2] * h.local_wt(r2)
                    + h.local_wt(h.local_mul(pbc[q], r1))
                    + h.local_wt(h.local_mul(pcc[q], r2))
                )
                new = old_parity ^ d
                cand = (old_cost + local, old_seq + (r1,))
                if new not in nxt or cand < nxt[new]:
                    nxt[new] = cand
        states = nxt
    if 1 not in states:
        raise AssertionError("no anticommuting ADT3 companion")
    raw, seq = states[1]
    r1 = key_from_codes(seq)
    r2 = mul(r0, r1)
    t0 = (0, 0)
    t1 = mul(pb, r1)
    t2 = mul(pc, r2)
    # Uanti has coefficients 4,4,2 on (w-1), so subtract 10.
    cost = int(raw - sum(coef))
    recomputed = (
        uanti_support((r0, r1, r2), central)
        + 2 * (wt(r0) + wt(r1))
        + wt(t1) + wt(t2)
    )
    checks = {
        "R0_anchor": r0 == targets[anchor_i],
        "R0_R1_anti": symp(r0, r1) == 1,
        "R0_R2_anti": symp(r0, r2) == 1,
        "R1_R2_anti": symp(r1, r2) == 1,
        "dependent_sum_zero": mul(mul(r0, r1), r2) == (0, 0),
        "labels_xor_zero": LABELS[0] ^ LABELS[1] ^ LABELS[2] == 0,
        "S_high_syndrome": tuple(symp(r0, r) for r in (r0, r1, r2)) == (0, 1, 1),
        "S_low_syndrome": tuple(symp(r1, r) for r in (r0, r1, r2)) == (1, 0, 1),
        "T0_identity": t0 == (0, 0),
        "T1_restore": mul(t1, r1) == pb,
        "T2_restore": mul(t2, r2) == pc,
        "cost_recomputed": recomputed == cost,
    }
    if not all(checks.values()):
        raise AssertionError({"adt3_checks": checks, "targets": targets})
    return {
        "cost": cost,
        "anchor_target": anchor_i,
        "remaining_assignment": [b_i, c_i],
        "central": central,
        "R": [list(r0), list(r1), list(r2)],
        "S_high": list(r0),
        "S_low": list(r1),
        "T": [list(t0), list(t1), list(t2)],
        "uanti_support": uanti_support((r0, r1, r2), central),
        "tag_weight": wt(r0) + wt(r1),
        "restore_support": wt(t1) + wt(t2),
        "checks": checks,
    }


def adt3_best(targets, n):
    best = None
    for anchor_i in range(3):
        rest = [i for i in range(3) if i != anchor_i]
        for b_i, c_i in (tuple(rest), tuple(reversed(rest))):
            for central in range(3):
                rec = fixed_adt3_dp(targets, anchor_i, b_i, c_i, central, n)
                rflat = tuple(tuple(x) for x in rec["R"])
                key = (rec["cost"], anchor_i, b_i, c_i, central, rflat)
                if best is None or key < best[0]:
                    best = (key, rec)
    return best[1]


def fixed_adt3_bruteforce(targets, anchor_i, b_i, c_i, central, n):
    r0 = targets[anchor_i]
    pb, pc = targets[b_i], targets[c_i]
    best = INF
    limit = 1 << n
    for x in range(limit):
        for z in range(limit):
            r1 = (x, z)
            if symp(r0, r1) != 1:
                continue
            r2 = mul(r0, r1)
            t1, t2 = mul(pb, r1), mul(pc, r2)
            c = uanti_support((r0, r1, r2), central) + 2 * (wt(r0) + wt(r1)) + wt(t1) + wt(t2)
            if c < best:
                best = c
    return int(best)


def hostile_validation():
    rng = random.Random(2601057403)
    cases = 0
    for n, count in ((2, 96), (3, 96)):
        lim = 1 << n
        keys = [(x, z) for x in range(lim) for z in range(lim) if x or z]
        for _ in range(count):
            targets = tuple(rng.choice(keys) for _j in range(3))
            for anchor_i in range(3):
                rest = [i for i in range(3) if i != anchor_i]
                for b_i, c_i in (tuple(rest), tuple(reversed(rest))):
                    for central in range(3):
                        dp = fixed_adt3_dp(targets, anchor_i, b_i, c_i, central, n)["cost"]
                        brute = fixed_adt3_bruteforce(targets, anchor_i, b_i, c_i, central, n)
                        if dp != brute:
                            raise AssertionError({"hostile_dp_mismatch": [n, targets, anchor_i, b_i, c_i, central, dp, brute]})
            cases += 1
    return {"cases": cases, "all_fixed_cases_exact": True}


def is_direct_triple(keys):
    return all(symp(keys[i], keys[j]) == 1 for i in range(3) for j in range(i + 1, 3))


def load_terms(cfg):
    b.configure_subject(cfg)
    text = h.fetch_source()
    one, two = h.parse_ducc(text)
    paulis, max_imag = h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    return terms, max_imag


def subject_eval(name, cfg):
    terms, max_imag = load_terms(cfg)
    n = cfg["n_qubits"]
    eligible = 0
    improved = []
    top = []
    checked = 0
    for start in range(0, len(terms), b.WINDOW):
        end = min(start + b.WINDOW, len(terms))
        for comb in itertools.combinations(range(start, end), 3):
            keys = tuple(terms[i][0] for i in comb)
            if is_direct_triple(keys):
                continue
            eligible += 1
            can = canonical_best(keys, n)
            ad = adt3_best(keys, n)
            checked += 1
            delta = can["cost"] - ad["cost"]
            if delta > 0:
                frac = delta / can["cost"] if can["cost"] else 0.0
                improved.append((delta, frac))
                lam = math.sqrt(3.0) * math.sqrt(sum(float(terms[i][1]) ** 2 for i in comb))
                top.append((frac, delta, comb, lam, can, ad))
    top.sort(key=lambda x: (-x[0], -x[1], x[2]))
    imp_d = [x[0] for x in improved]
    imp_f = [x[1] for x in improved]
    result = {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": n,
        "terms": len(terms),
        "max_imag": max_imag,
        "eligible_non_direct_triples": eligible,
        "triples_checked": checked,
        "improved_triples": len(improved),
        "improved_fraction": 0.0 if eligible == 0 else len(improved) / eligible,
        "improved_support_mean": 0.0 if not imp_d else statistics.mean(imp_d),
        "improved_support_median": 0.0 if not imp_d else statistics.median(imp_d),
        "improved_fraction_mean": 0.0 if not imp_f else statistics.mean(imp_f),
        "max_fraction_reduction": 0.0 if not imp_f else max(imp_f),
        "max_support_reduction": 0 if not imp_d else max(imp_d),
        "at_least_one_ge_20pct": any(x >= 0.20 for x in imp_f),
        "top_witnesses": [
            {
                "fraction_reduction": frac,
                "support_reduction": delta,
                "term_indices": list(comb),
                "lambda_equal_for_both": lam,
                "canonical": can,
                "ADT3": ad,
            }
            for frac, delta, comb, lam, can, ad in top[:8]
        ],
    }
    return result


def main():
    hostile = hostile_validation()
    subjects = {name: subject_eval(name, cfg) for name, cfg in b.SUBJECTS.items()}
    total_eligible = sum(r["eligible_non_direct_triples"] for r in subjects.values())
    gates = {
        "hostile_exact": hostile["all_fixed_cases_exact"],
        "at_least_100_total_eligible": total_eligible >= 100,
        "both_subjects_ge_20pct_improved_fraction": all(r["improved_fraction"] >= 0.20 for r in subjects.values()),
        "median_improved_ge_1": all(r["improved_support_median"] >= 1 for r in subjects.values()),
        "each_subject_has_ge_20pct_case": all(r["at_least_one_ge_20pct"] for r in subjects.values()),
        "hermitian": all(r["max_imag"] <= 5e-8 for r in subjects.values()),
        "equal_lambda_T_block_ancilla_by_construction": True,
    }
    passed = all(gates.values())
    out = {
        "schema": "ORIONQ.MAXR5J.AnchoredDependentTARE3Development.v1",
        "authority": "R5J_ADT3_DEVELOPMENT_SUPPORTED" if passed else "R5J_ADT3_DEVELOPMENT_NEGATIVE",
        "scope": "OPEN_SUBJECT_METHOD_DEVELOPMENT_ONLY__NOT_R6",
        "construction": "R0=P_anchor; R2=R0*R1; labels=(01,10,11); dual tags=(R0,R1); exact 2-state R1 DP",
        "hostile_validation": hostile,
        "subjects": subjects,
        "gates": gates,
        "r5j_development_pass": passed,
    }
    print("ORIONQ_MAX_R5J_DEV=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
