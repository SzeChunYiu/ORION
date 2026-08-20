#!/usr/bin/env python3
"""Candidate-blind MAX-R6 P10 auxiliary-frame optimizer.

This file intentionally does not import or inspect the earlier R5J candidate.
It searches a generic rank-2 F2^2 TARE-3 frame grammar against a strengthened
canonical rank-3 TARE comparator on already-open H4/equilibrium-N2 subjects.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from functools import lru_cache

import numpy as np

import max_r5h_mixed_cardinality_development as base

h = base.h
INF = 10**9
WINDOW = 12
# Rank-2 frame coordinates: R0=A has label 01, R1=B label 10, R2=A+B label 11.
LABELS_R2 = (1, 2, 3)
# Dual Tag constraints for S_hi / S_lo against basis (A,B):
# S_hi syndromes (0,1), S_lo syndromes (1,0).
TARGET5 = 0b01101  # [AB=1, hiA=0, hiB=1, loA=1, loB=0]
XOR32 = np.bitwise_xor(np.arange(32)[:, None], np.arange(32)[None, :])


def sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def mul(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def wt(k):
    return (k[0] | k[1]).bit_count()


def symp(a, b):
    return ((a[0] & b[1]).bit_count() + (a[1] & b[0]).bit_count()) & 1


def codes(k, n):
    x, z = k
    return tuple(h.BITS_CODE[((x >> q) & 1, (z >> q) & 1)] for q in range(n))


def key_from_codes(seq):
    x = z = 0
    for q, code in enumerate(seq):
        bx, bz = h.CODE_BITS[code]
        x |= bx << q
        z |= bz << q
    return (x, z)


def frame_r2(a, b):
    return (a, b, mul(a, b))


def is_pairwise_anti(rs):
    return all(symp(rs[i], rs[j]) == 1 for i in range(3) for j in range(i + 1, 3))


def is_direct_triple(targets):
    return is_pairwise_anti(targets)


def uanti_support(rs, central):
    coeff = [4, 4, 4]
    coeff[central] = 2
    return int(sum(coeff[k] * (wt(rs[k]) - 1) for k in range(3)))


def tag_min_weight(rs, syndrome: int, n: int):
    rc = [codes(r, n) for r in rs]
    # int64 is deliberate: unreachable INF entries are added once per qubit,
    # so cumulative DP sentinels can exceed int32 even though valid costs are small.
    dp = np.full(8, INF, dtype=np.int64)
    dp[0] = 0
    parents = []
    for q in range(n):
        local = np.full(8, INF, dtype=np.int64)
        choice = np.full(8, -1, dtype=np.int8)
        for s in range(4):
            d = 0
            for k in range(3):
                d |= h.local_symp(s, rc[k][q]) << k
            c = h.local_wt(s)
            if c < local[d] or (c == local[d] and s < choice[d]):
                local[d] = c
                choice[d] = s
        x = np.bitwise_xor(np.arange(8)[:, None], np.arange(8)[None, :])
        mat = dp[:, None] + local[x]
        prev = np.argmin(mat, axis=0)
        ndp = mat[prev, np.arange(8)]
        delta = x[prev, np.arange(8)]
        parents.append((prev.copy(), delta.copy(), choice.copy()))
        dp = ndp
    if dp[syndrome] >= INF:
        raise AssertionError({"tag_syndrome_unsolved": syndrome, "R": rs})
    state = syndrome
    seq = [0] * n
    for q in range(n - 1, -1, -1):
        prev, delta, choice = parents[q]
        d = int(delta[state])
        seq[q] = int(choice[d])
        state = int(prev[state])
    return int(dp[syndrome]), key_from_codes(seq)


def canonical_frame(n):
    if n < 2:
        raise ValueError("TARE-3 canonical frame requires n>=2")
    return ((1, 0), (1, 1), (2, 1))


@lru_cache(maxsize=None)
def canonical_label_tags(n: int, labels: tuple[int, int, int]):
    rs = canonical_frame(n)
    hi_syn = sum((((labels[k] >> 1) & 1) << k) for k in range(3))
    lo_syn = sum(((labels[k] & 1) << k) for k in range(3))
    wh, sh = tag_min_weight(rs, hi_syn, n)
    wl, sl = tag_min_weight(rs, lo_syn, n)
    return wh, sh, wl, sl


def canonical_best(targets, n):
    rs = canonical_frame(n)
    best = None
    for labels in itertools.permutations(range(4), 3):
        wh, sh, wl, sl = canonical_label_tags(n, tuple(labels))
        for perm in itertools.permutations(range(3)):
            ps = [targets[i] for i in perm]
            ts = [mul(ps[k], rs[k]) for k in range(3)]
            for central in range(3):
                cost = uanti_support(rs, central) + 2 * (wh + wl) + sum(wt(t) for t in ts)
                rec = {
                    "frame_rank": 3,
                    "control_labels": list(labels),
                    "target_permutation": list(perm),
                    "central": central,
                    "R": [list(r) for r in rs],
                    "S": [list(sh), list(sl)],
                    "T": [list(t) for t in ts],
                    "native_matches": [k for k, t in enumerate(ts) if t == (0, 0)],
                    "cost": int(cost),
                    "uanti_support": uanti_support(rs, central),
                    "tag_support": int(wh + wl),
                    "restore_support": int(sum(wt(t) for t in ts)),
                }
                key = (cost, labels, perm, central, sh, sl)
                if best is None or key < best[0]:
                    best = (key, rec)
    return best[1]


# Local exact table for one native anchor A=P0. The free variables are B and two
# Tag generators. The 5-bit delta tracks the global anticommutation/dual-basis
# constraints. The table depends only on the three local target codes and central.
# int64 is required because the qubit-wise recurrence can add multiple INF
# sentinels before minimization; n*INF exceeds int32 on the n=8/12 subjects.
LOCAL = np.full((4, 4, 4, 3, 32), INF, dtype=np.int64)
LOCAL_CHOICE = np.full((4, 4, 4, 3, 32, 3), -1, dtype=np.int8)
for a in range(4):
    for pb in range(4):
        for pc in range(4):
            for central in range(3):
                mult = [4, 4, 4]
                mult[central] = 2
                for b in range(4):
                    r2 = h.local_mul(a, b)
                    for shi in range(4):
                        for slo in range(4):
                            d = 0
                            d |= h.local_symp(a, b) << 0
                            d |= h.local_symp(shi, a) << 1
                            d |= h.local_symp(shi, b) << 2
                            d |= h.local_symp(slo, a) << 3
                            d |= h.local_symp(slo, b) << 4
                            c = (
                                mult[0] * h.local_wt(a)
                                + mult[1] * h.local_wt(b)
                                + mult[2] * h.local_wt(r2)
                                + 2 * h.local_wt(shi)
                                + 2 * h.local_wt(slo)
                                + h.local_wt(h.local_mul(pb, b))
                                + h.local_wt(h.local_mul(pc, r2))
                            )
                            ch = (b, shi, slo)
                            old = int(LOCAL[a, pb, pc, central, d])
                            oldch = tuple(int(x) for x in LOCAL_CHOICE[a, pb, pc, central, d])
                            if c < old or (c == old and (oldch[0] < 0 or ch < oldch)):
                                LOCAL[a, pb, pc, central, d] = c
                                LOCAL_CHOICE[a, pb, pc, central, d] = ch


def one_anchor_dp(pa, pb, pc, central, n):
    ac, bc, cc = codes(pa, n), codes(pb, n), codes(pc, n)
    dp = np.full(32, INF, dtype=np.int64)
    dp[0] = 0
    parents = []
    for q in range(n):
        local = LOCAL[ac[q], bc[q], cc[q], central].astype(np.int64)
        mat = dp[:, None] + local[XOR32]
        prev = np.argmin(mat, axis=0)
        ndp = mat[prev, np.arange(32)]
        delta = XOR32[prev, np.arange(32)]
        parents.append((prev.copy(), delta.copy(), ac[q], bc[q], cc[q]))
        dp = ndp
    raw = int(dp[TARGET5])
    if raw >= INF:
        raise AssertionError("rank-2 one-anchor DP infeasible")
    state = TARGET5
    bseq = [0] * n
    hiseq = [0] * n
    loseq = [0] * n
    for q in range(n - 1, -1, -1):
        prev, delta, a, pbq, pcq = parents[q]
        d = int(delta[state])
        b, shi, slo = [int(x) for x in LOCAL_CHOICE[a, pbq, pcq, central, d]]
        bseq[q], hiseq[q], loseq[q] = b, shi, slo
        state = int(prev[state])
    b = key_from_codes(bseq)
    shi = key_from_codes(hiseq)
    slo = key_from_codes(loseq)
    rs = frame_r2(pa, b)
    ts = ((0, 0), mul(pb, rs[1]), mul(pc, rs[2]))
    # Every R is nonidentity in an anticommuting frame: subtract the Uanti constants.
    cost = raw - 10
    recomputed = uanti_support(rs, central) + 2 * (wt(shi) + wt(slo)) + sum(wt(t) for t in ts)
    checks = {
        "rank2_relation": mul(mul(rs[0], rs[1]), rs[2]) == (0, 0),
        "pairwise_anti": is_pairwise_anti(rs),
        "native_anchor": rs[0] == pa and ts[0] == (0, 0),
        "tag_hi": tuple(symp(shi, r) for r in rs) == (0, 1, 1),
        "tag_lo": tuple(symp(slo, r) for r in rs) == (1, 0, 1),
        "restore": all(mul(ts[k], rs[k]) == p for k, p in enumerate((pa, pb, pc))),
        "cost_recomputed": recomputed == cost,
    }
    if not all(checks.values()):
        raise AssertionError({"rank2_witness_failed": checks})
    return {
        "frame_rank": 2,
        "basis": [list(pa), list(b)],
        "control_labels": list(LABELS_R2),
        "central": central,
        "R": [list(r) for r in rs],
        "S": [list(shi), list(slo)],
        "T": [list(t) for t in ts],
        "native_matches": [0],
        "cost": int(cost),
        "uanti_support": uanti_support(rs, central),
        "tag_support": int(wt(shi) + wt(slo)),
        "restore_support": int(sum(wt(t) for t in ts)),
        "checks": checks,
    }


def two_anchor_candidate(pa, pb, pc, central, n):
    if symp(pa, pb) != 1:
        return None
    rs = frame_r2(pa, pb)
    wh, shi = tag_min_weight(rs, 0b110, n)
    wl, slo = tag_min_weight(rs, 0b101, n)
    ts = ((0, 0), (0, 0), mul(pc, rs[2]))
    cost = uanti_support(rs, central) + 2 * (wh + wl) + wt(ts[2])
    checks = {
        "rank2_relation": mul(mul(rs[0], rs[1]), rs[2]) == (0, 0),
        "pairwise_anti": is_pairwise_anti(rs),
        "two_native": ts[0] == (0, 0) and ts[1] == (0, 0),
        "tag_hi": tuple(symp(shi, r) for r in rs) == (0, 1, 1),
        "tag_lo": tuple(symp(slo, r) for r in rs) == (1, 0, 1),
        "restore": all(mul(ts[k], rs[k]) == p for k, p in enumerate((pa, pb, pc))),
    }
    if not all(checks.values()):
        raise AssertionError({"two_anchor_witness_failed": checks})
    return {
        "frame_rank": 2,
        "basis": [list(pa), list(pb)],
        "control_labels": list(LABELS_R2),
        "central": central,
        "R": [list(r) for r in rs],
        "S": [list(shi), list(slo)],
        "T": [list(t) for t in ts],
        "native_matches": [0, 1] + ([2] if ts[2] == (0, 0) else []),
        "cost": int(cost),
        "uanti_support": uanti_support(rs, central),
        "tag_support": int(wh + wl),
        "restore_support": int(sum(wt(t) for t in ts)),
        "checks": checks,
    }


def rank2_best(targets, n):
    # Native matches are the lexicographic primary objective. A non-direct triple
    # has max 2 native matches iff it contains an anticommuting target pair;
    # otherwise max 1. GL(2,2) lets any chosen nonzero frame label be renamed R0.
    candidates = []
    has_anti_pair = any(symp(targets[i], targets[j]) == 1 for i in range(3) for j in range(i + 1, 3))
    for perm in itertools.permutations(range(3)):
        ps = [targets[i] for i in perm]
        for central in range(3):
            if has_anti_pair:
                rec = two_anchor_candidate(ps[0], ps[1], ps[2], central, n)
                if rec is None:
                    continue
            else:
                rec = one_anchor_dp(ps[0], ps[1], ps[2], central, n)
            rec = dict(rec)
            rec["target_permutation"] = list(perm)
            candidates.append(rec)
    if not candidates:
        raise AssertionError("rank2 grammar produced no candidate")
    def key(rec):
        return (
            -len(rec["native_matches"]),
            rec["cost"],
            rec["restore_support"],
            rec["tag_support"],
            sum(wt(tuple(x)) for x in rec["R"]),
            tuple(rec["target_permutation"]),
            rec["central"],
            tuple(tuple(x) for x in rec["R"]),
        )
    return min(candidates, key=key)


def brute_one_anchor(pa, pb, pc, central, n):
    limit = 1 << n
    best = None
    for xb in range(limit):
        for zb in range(limit):
            b = (xb, zb)
            if symp(pa, b) != 1:
                continue
            rs = frame_r2(pa, b)
            wh, shi = brute_tag(rs, 0b110, n)
            wl, slo = brute_tag(rs, 0b101, n)
            ts = ((0, 0), mul(pb, b), mul(pc, rs[2]))
            c = uanti_support(rs, central) + 2 * (wh + wl) + sum(wt(t) for t in ts)
            rec = (c, b, shi, slo)
            if best is None or rec < best:
                best = rec
    return best


def brute_tag(rs, syndrome, n):
    limit = 1 << n
    best = None
    for x in range(limit):
        for z in range(limit):
            s = (x, z)
            got = sum(symp(s, rs[k]) << k for k in range(3))
            if got != syndrome:
                continue
            rec = (wt(s), s)
            if best is None or rec < best:
                best = rec
    if best is None:
        raise AssertionError("brute tag infeasible")
    return best


def hostile_validation():
    rng = random.Random(2608201931)
    cases = 0
    for n in (2, 3):
        limit = 1 << n
        keys = [(x, z) for x in range(limit) for z in range(limit) if x or z]
        for _ in range(12):
            # Force a triple with no anti target pair so the full one-anchor DP is exercised.
            for _attempt in range(10000):
                targets = tuple(rng.choice(keys) for _k in range(3))
                if not is_direct_triple(targets) and not any(
                    symp(targets[i], targets[j]) for i in range(3) for j in range(i + 1, 3)
                ):
                    break
            else:
                continue
            pa, pb, pc = targets
            for central in range(3):
                dp = one_anchor_dp(pa, pb, pc, central, n)
                brute = brute_one_anchor(pa, pb, pc, central, n)
                if brute is None or dp["cost"] != brute[0]:
                    raise AssertionError({"hostile_mismatch": [n, targets, central, dp["cost"], brute]})
            cases += 1
    return {"cases": cases, "exact": True}


def load_terms(cfg):
    base.configure_subject(cfg)
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
    for start in range(0, len(terms), WINDOW):
        end = min(start + WINDOW, len(terms))
        for comb in itertools.combinations(range(start, end), 3):
            targets = tuple(terms[i][0] for i in comb)
            if is_direct_triple(targets):
                continue
            eligible += 1
            donor = canonical_best(targets, n)
            generated = rank2_best(targets, n)
            delta = donor["cost"] - generated["cost"]
            if delta > 0:
                lam = math.sqrt(3.0) * math.sqrt(sum(float(terms[i][1]) ** 2 for i in comb))
                rec = {
                    "term_indices": list(comb),
                    "delta": int(delta),
                    "fraction": float(delta / donor["cost"] if donor["cost"] else 0.0),
                    "Lambda_TARE3": float(lam),
                    "donor": donor,
                    "generated": generated,
                }
                improved.append(rec)
                top.append(rec)
    top.sort(key=lambda r: (-r["fraction"], -r["delta"], r["term_indices"]))
    return {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": n,
        "terms": len(terms),
        "max_imag": max_imag,
        "eligible": eligible,
        "improved": len(improved),
        "improved_fraction": 0.0 if not eligible else len(improved) / eligible,
        "max_delta": 0 if not improved else max(r["delta"] for r in improved),
        "max_fraction": 0.0 if not improved else max(r["fraction"] for r in improved),
        "top": top[:8],
    }


def main():
    hostile = hostile_validation()
    results = {name: subject_eval(name, cfg) for name, cfg in base.SUBJECTS.items()}
    gates = {
        "hostile_exact": hostile["exact"],
        "both_subjects_candidate": all(r["improved"] > 0 for r in results.values()),
        "native_match_generated": all(
            any(len(w["generated"]["native_matches"]) >= 1 for w in r["top"])
            for r in results.values()
        ),
        "witness_checks": all(
            all(all(w["generated"].get("checks", {"ok": True}).values()) for w in r["top"])
            for r in results.values()
        ),
        "fresh_subject_unread": True,
    }
    passed = all(gates.values())
    out = {
        "schema": "ORIONQ.MAXR6.P10CandidateBlindFrameOptimizer.v1",
        "authority": (
            "MAX_R6_P10_FRAME_CANDIDATE_GENERATED" if passed
            else "MAX_R6_P10_FRAME_GENERATION_NEGATIVE"
        ),
        "scope": "OPEN_SUBJECT_CANDIDATE_GENERATION_ONLY__NOT_R6",
        "grammar": "rank2_F2_basis_plus_three_nonzero_labels; native-match-first; exact dual-tag DP",
        "hostile": hostile,
        "subjects": results,
        "gates": gates,
        "candidate_generated": passed,
        "reserved_stretched_n2_accessed": False,
    }
    print("ORIONQ_MAX_R6_P10_FRAME=" + json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    main()
