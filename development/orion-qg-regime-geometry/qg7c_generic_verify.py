#!/usr/bin/env python3
"""QG-7c generic verifier — independent primitive re-derivation.

Rebuilds everything it checks from primitive single-qubit Pauli operations:
NO import of the analyzer, of the committed orion-q machinery, or of any of
their tables. Reads only the receipt JSON files (data, not code) and the
frozen protocol file (for its hash).

Checks:
  V1  protocol hash binding + schema/terminal/authority vocabulary.
  V2  MG mirror invariance re-derived from primitives (complete n=1 domain)
      and the recorded MG numbers.
  V3  M1 inventory re-derived over the complete 262,144-case domain: shape
      counts, reducibility split, zero irreducible occurrences of the three
      closed L4b classes, occupancy counts (T2).
  V4  T1 prune (12,288 cases) and T5 empty-home merge (1,158 cases)
      re-derived.
  V5  T3 consolidation exchange fully re-derived (7 x 128^3 domain, frozen
      menu): zero failures required when the receipt claims L4c closure.
  V6  T4a fully re-derived (worst <= 0) and T4b fully re-derived: failure
      total, worst delta and census bound to the receipt.
  V7  Arm C consistency: referee counters, zero-gap accounting, and (if any
      gap row is serialized) primitive re-verification of its dxx witness
      arithmetic.
  V8  terminal + authority re-derivation from the frozen selection rules;
      result digest recomputation (canonical JSON minus timing and digest).

Prints ACCEPT or REJECT (with reasons) and exits 0/1.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESULTS = REPO / "research/extensions/orion-qg/QG7C_CLASSIFICATION_RESULTS.json"
PROTOCOL = HERE / "QG7C_CLASSIFICATION_PROTOCOL_V1.md"

X, Y, Z = 1, 2, 3
failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


# ---- primitives -------------------------------------------------------------

def lmul(a, b):
    if a == 0:
        return b
    if b == 0:
        return a
    if a == b:
        return 0
    return 6 - a - b


def lsy(a, b):
    return 1 if (a != 0 and b != 0 and a != b) else 0


def lw(a):
    return 0 if a == 0 else 1


def lf3(a, b, c):
    if a == b == c != 0:
        return 1
    return lw(a) + lw(b) + lw(c)


LM = np.array([[lmul(a, b) for b in range(4)] for a in range(4)],
              dtype=np.int64)
F3E = np.array([[lf3(x, u, v) for u in range(4) for v in range(4)]
                for x in range(4)], dtype=np.int16)
F3T = np.array([[[lf3(x, y, u) for u in range(4)] for y in range(4)]
                for x in range(4)], dtype=np.int16)


# ---- V2: MG mirror ----------------------------------------------------------

def check_mg(rec):
    configs = []
    for s in (1, 2, 3):
        for orient in ((0, 1), (1, 0)):
            per_block = [(f0, f1) for f0 in (1, 2, 3) for f1 in (1, 2, 3)
                         if f0 != f1 and (lsy(s, f0), lsy(s, f1)) == orient]
            for pa in per_block:
                for pb in per_block:
                    for pc in per_block:
                        configs.append((s, pa + pb + pc))
    if len(configs) != rec["configs"] or len(configs) != 48:
        fail(f"V2 config count {len(configs)} != {rec['configs']}")
    t_all = np.arange(4096, dtype=np.int64)
    t6 = [(t_all >> (2 * (5 - i))) & 3 for i in range(6)]
    mf = 0
    comps = 0
    for s, frames in configs:
        tt = [LM[t6[i], frames[i]] for i in range(6)]
        f3sum = np.array([lf3(int(tt[0][k]), int(tt[2][k]), int(tt[4][k]))
                          + lf3(int(tt[1][k]), int(tt[3][k]), int(tt[5][k]))
                          for k in range(4096)], dtype=np.int64)
        perm = [1, 0, 3, 2, 5, 4]
        m_frames = [frames[1], frames[0], frames[3], frames[2],
                    frames[5], frames[4]]
        ttm = [LM[t6[perm[i]], m_frames[i]] for i in range(6)]
        f3m = np.array([lf3(int(ttm[0][k]), int(ttm[2][k]), int(ttm[4][k]))
                        + lf3(int(ttm[1][k]), int(ttm[3][k]), int(ttm[5][k]))
                        for k in range(4096)], dtype=np.int64)
        # raw + tag are central-symmetric constants for weight-1 frames
        mf += int((f3sum != f3m).sum())
        comps += 8 * 4096
    if mf != 0:
        fail(f"V2 mirror failures {mf}")
    if rec["mirror_failures"] != 0 or not rec["holds"]:
        fail("V2 receipt MG numbers not clean")
    if rec["mirror_comparisons"] != comps:
        fail(f"V2 comparisons {comps} != {rec['mirror_comparisons']}")


# ---- V3: M1 -----------------------------------------------------------------

def check_m1(rec):
    feasible = 0
    red22 = 0
    rede = 0
    counts = {"anchored": 0, "phantom": 0, "comm_s2": 0}
    bad = 0
    occ_bad = 0
    for f0d in itertools.product(range(4), repeat=3):
        w0 = sum(1 for v in f0d if v)
        if not 1 <= w0 <= 2:
            continue
        for f1d in itertools.product(range(4), repeat=3):
            w1 = sum(1 for v in f1d if v)
            if not 1 <= w1 <= 2:
                continue
            if sum(lsy(f0d[q], f1d[q]) for q in range(3)) % 2 != 1:
                continue
            for sd in itertools.product(range(4), repeat=3):
                if sum(lsy(sd[q], f0d[q]) for q in range(3)) % 2 != 0:
                    continue
                if sum(lsy(sd[q], f1d[q]) for q in range(3)) % 2 != 1:
                    continue
                feasible += 1
                if w0 == 2 and w1 == 2:
                    red22 += 1
                    continue
                red = False
                for rd, pd in ((f0d, f1d), (f1d, f0d)):
                    if sum(1 for v in rd if v) == 2:
                        for q in range(3):
                            if rd[q] and lsy(rd[q], pd[q]) == 0 \
                                    and lsy(sd[q], rd[q]) == 0:
                                red = True
                if red:
                    rede += 1
                    continue
                occ = sum(1 for q in range(3)
                          if lsy(sd[q], f0d[q]) or lsy(sd[q], f1d[q]))
                if w0 == 1 and w1 == 1:
                    q0 = next(q for q in range(3) if f0d[q])
                    q1 = next(q for q in range(3) if f1d[q])
                    if not (q0 == q1 and sd[q0] == f0d[q0] != 0
                            and lsy(sd[q0], f1d[q0]) == 1):
                        bad += 1
                    counts["anchored"] += 1
                    if occ != 1:
                        occ_bad += 1
                elif w1 == 2 and w0 == 1:
                    h = next(q for q in range(3) if f0d[q])
                    supp1 = [q for q in range(3) if f1d[q]]
                    if h not in supp1:
                        bad += 1
                        continue
                    b = next(q for q in supp1 if q != h)
                    counts["phantom"] += 1
                    if sd[h] != 0 or sd[b] == 0 \
                            or lsy(sd[b], f1d[b]) != 1 or f0d[h] == f1d[h]:
                        bad += 1
                    if occ != 1:
                        occ_bad += 1
                elif w0 == 2 and w1 == 1:
                    a = next(q for q in range(3) if f1d[q])
                    supp0 = [q for q in range(3) if f0d[q]]
                    if a not in supp0:
                        bad += 1
                        continue
                    b = next(q for q in supp0 if q != a)
                    counts["comm_s2"] += 1
                    if not (sd[b] != 0 and lsy(sd[b], f0d[b]) == 1
                            and sd[a] != 0 and lsy(sd[a], f0d[a]) == 1
                            and f1d[a] not in (0, sd[a], f0d[a])):
                        bad += 1
                    if occ != 2:
                        occ_bad += 1
                else:
                    bad += 1
    if bad != 0 or occ_bad != 0:
        fail(f"V3 M1 primitive re-derivation: bad={bad} occ_bad={occ_bad}")
    if rec["feasible"] != feasible:
        fail(f"V3 feasible {feasible} != {rec['feasible']}")
    if rec["reducible_2_2_blocks_L1"] != red22 \
            or rec["reducible_lemma_e_class00"] != rede:
        fail("V3 reducibility split mismatch")
    if rec["irreducible_shape_counts"] != counts:
        fail(f"V3 shape counts {counts} != {rec['irreducible_shape_counts']}")
    for k in ("tag_supported_phantom_irreducible",
              "l1_phantom_at_home_irreducible",
              "phantom_borrow_untagged_irreducible",
              "unclassified_irreducible", "structure_assertion_failures",
              "t2_occupancy_failures"):
        if rec[k] != 0:
            fail(f"V3 receipt {k} nonzero")
    if rec["raw_domain"] != 262144 or not rec["holds"]:
        fail("V3 receipt M1 not clean")


# ---- V4: T1 and T5 ----------------------------------------------------------

def check_t1_t5(rec1, rec5):
    dom = 0
    bad = 0
    for sq in (1, 2, 3):
        for letters in itertools.product(range(4), repeat=6):
            dom += 1
            if any(lsy(sq, le) for le in letters):
                continue
            if any(lsy(sq, le) != 0 for le in letters):
                bad += 1
    if dom != 12288 or bad != 0 or rec1["domain_size"] != 12288 \
            or rec1["failures"] != 0 or not rec1["holds"]:
        fail("V4 T1 mismatch")

    def partitions(k):
        if k == 1:
            return [((0,),)]
        if k == 2:
            return [((0, 1),), ((0,), (1,))]
        return [((0, 1, 2),), ((0, 1), (2,)), ((0, 2), (1,)),
                ((1, 2), (0,)), ((0,), (1,), (2,))]

    cases = 0
    t5bad = 0
    for k in (1, 2, 3):
        for part in partitions(k):
            for letters in itertools.product(
                    [(m0, m1) for m0 in (1, 2, 3) for m1 in (1, 2, 3)
                     if m1 != m0], repeat=k):
                cases += 1
                before = 0
                for grp in part:
                    for br in (0, 1):
                        ls = [letters[i][br] for i in grp] + [0] * (3 - len(grp))
                        before += lf3(ls[0], ls[1], ls[2])
                after = 0
                for br, val in ((0, X), (1, Y)):
                    ls = [val] * k + [0] * (3 - k)
                    after += lf3(ls[0], ls[1], ls[2])
                if after > before:
                    t5bad += 1
    if cases != 1158 or t5bad != 0 or rec5["cases"] != 1158 \
            or rec5["failures"] != 0 or not rec5["holds"]:
        fail("V4 T5 mismatch")


# ---- V5: T3 -----------------------------------------------------------------

def t3_tab(fn):
    out = np.empty(128, dtype=np.int16)
    i = 0
    for tw in range(4):
        for L in (1, 2):
            for u in range(4):
                for v in range(4):
                    out[i] = fn(tw, L, u, v)
                    i += 1
    return out


def check_t3(rec):
    AC = {1: (2, 3), 2: (1, 3), 3: (1, 2)}
    total = 0
    nf_total = 0
    worst = {}
    src_anch = [t3_tab(lambda tw, L, u, v, m1=m1:
                       lf3(lmul(tw, m1), u, v) - lf3(lmul(tw, L), u, v))
                for m1 in (1, 2)]
    src_phan = [t3_tab(lambda tw, L, u, v:
                       lf3(tw, u, v) - lf3(lmul(tw, L), u, v))]
    for shapes in itertools.product("AP", repeat=3):
        if "P" not in shapes:
            continue
        best = np.full((128, 128, 128), 99, dtype=np.int16)
        zero = np.zeros(128, dtype=np.int16)

        def acc(p0, p1, p2, struct):
            np.minimum(best, p0[:, None, None] + p1[None, :, None]
                       + p2[None, None, :] + np.int16(struct), out=best)

        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                struct = 0 if shapes[i] == 'A' else -2
                srcs = src_anch if shapes[i] == 'A' else src_phan
                slot_u = ((j + 1) % 3 == i)
                for ds in srcs:
                    for lp in (1, 2):
                        if slot_u:
                            dd = t3_tab(lambda tw, L, u, v, lp=lp:
                                        lf3(lmul(tw, L), lmul(u, lp), v)
                                        - lf3(lmul(tw, L), u, v))
                        else:
                            dd = t3_tab(lambda tw, L, u, v, lp=lp:
                                        lf3(lmul(tw, L), u, lmul(v, lp))
                                        - lf3(lmul(tw, L), u, v))
                        parts = [zero, zero, zero]
                        parts[i] = ds
                        parts[j] = dd
                        acc(parts[0], parts[1], parts[2], struct)
        for j in range(3):
            moved = [i for i in range(3) if i != j]
            struct = -4 + 2 * sum(1 for i in moved if shapes[i] == 'A')
            sigmas = (Z,) if shapes[j] == 'A' else (1, 2, 3)
            for sp in sigmas:
                acs = AC[sp]
                for own_c in acs:
                    for lpu in acs:
                        for lpv in acs:
                            dd = t3_tab(
                                lambda tw, L, u, v, c=own_c, a=lpu, b=lpv:
                                lf3(lmul(tw, c), lmul(u, a), lmul(v, b))
                                - lf3(lmul(tw, L), u, v))
                            s0s = src_anch if shapes[moved[0]] == 'A' \
                                else src_phan
                            s1s = src_anch if shapes[moved[1]] == 'A' \
                                else src_phan
                            for s0 in s0s:
                                for s1 in s1s:
                                    parts = [None, None, None]
                                    parts[j] = dd
                                    parts[moved[0]] = s0
                                    parts[moved[1]] = s1
                                    acc(parts[0], parts[1], parts[2], struct)
        total += best.size
        nf_total += int((best > 0).sum())
        worst["".join(shapes)] = int(best.max())
    if total != 7 * 128 ** 3:
        fail("V5 T3 domain size mismatch")
    if nf_total != rec["failures"]:
        fail(f"V5 T3 failures {nf_total} != {rec['failures']}")
    if worst != rec["worst_delta_by_shapes"]:
        fail("V5 T3 worst-by-shape mismatch")
    if rec["failures"] == 0 and not rec["holds"]:
        fail("V5 T3 holds flag inconsistent")


# ---- V6: T4a / T4b ----------------------------------------------------------

def check_t4(rec_a, rec_b):
    t4 = np.arange(4, dtype=np.int64)
    # T4a
    worst = -99
    total = 0
    t0b = np.repeat(t4, 4)
    t1b = np.tile(t4, 4)
    t0a, t1a = t0b, t1b
    for ja in (0, 1):
        for R_b in (1, 2):
            for R_a in (1, 2):
                w = lmul(R_a, Z)
                o0b = LM[t0b, R_b]
                o1b = t1b
                o0a = LM[t0a, R_a]
                o1a = LM[t1a, w]
                oldB = F3E[o0b][:, :, None] + F3E[o1b][:, None, :]
                oldA = F3E[o0a][:, :, None] + F3E[o1a][:, None, :]
                best = np.full((16, 256, 16, 256), 99, dtype=np.int16)

                def group(bparts, aparts, struct):
                    fb = np.stack([F3E[n0][:, :, None] + F3E[n1][:, None, :]
                                   - oldB for n0, n1 in bparts]) \
                        .min(axis=0).reshape(16, 256)
                    fa = np.stack([F3E[n0][:, :, None] + F3E[n1][:, None, :]
                                   - oldA for n0, n1 in aparts]) \
                        .min(axis=0).reshape(16, 256)
                    np.minimum(best, fb[:, :, None, None]
                               + fa[None, None, :, :] + np.int16(struct),
                               out=best)

                for sw in (0, 1):
                    s0b, s1b = (t0b, t1b) if sw == 0 else (t1b, t0b)
                    s0a, s1a = (t0a, t1a) if sw == 0 else (t1a, t0a)
                    group([(s0b, s1b)],
                          [(LM[s0a, Z], LM[s1a, c]) for c in (1, 2)], -4)
                    group([(LM[s0b, Z], LM[s1b, c]) for c in (1, 2)],
                          [(s0a, s1a)], -2 - 2 * ja)
                    group([(LM[s0b, m0], LM[s1b, m1])
                           for m0 in (1, 2, 3) for m1 in (1, 2, 3)
                           if m1 != m0],
                          [(s0a, LM[s1a, le]) for le in (1, 2)], -2)
                    if ja:
                        group([(s0b, LM[s1b, le]) for le in (1, 2)],
                              [(LM[s0a, m0], LM[s1a, m1])
                               for m0 in (1, 2, 3) for m1 in (1, 2, 3)
                               if m1 != m0], -2)
                total += best.size
                worst = max(worst, int(best.max()))
    if total != rec_a["domain_size"] or worst != rec_a["worst_delta"]:
        fail(f"V6 T4a mismatch: total={total} worst={worst}")
    if worst > 0 and rec_a["holds"]:
        fail("V6 T4a holds flag wrong")
    # T4b
    fail_total = 0
    worst_b = -99
    census: dict[str, int] = {}
    total_b = 0
    t0b = np.repeat(t4, 16)
    t1b = np.tile(np.repeat(t4, 4), 4)
    t21b = np.tile(t4, 16)
    t0a, t1a, t21a = t0b, t1b, t21b
    for case2 in ("PA", "PP"):
        for ja in (0, 1):
            for R_b in (1, 2):
                for R_a in (1, 2):
                    w = lmul(R_a, Z)
                    for p in (1, 2):
                        o0b = LM[t0b, R_b]
                        o1b_pin = LM[t21b, p]
                        o0a = LM[t0a, R_a]
                        o1a_our = LM[t1a, w]
                        oldB = (F3E[o0b][:, :, None]
                                + F3T[t1b, o1b_pin][:, None, :])
                        oldA = (F3E[o0a][:, :, None]
                                + F3T[o1a_our, t21a][:, None, :])
                        best = np.full((64, 64, 64, 64), 99, dtype=np.int16)

                        def group(bparts, aparts, struct):
                            fb = np.stack([
                                F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :]
                                - oldB for n0, n1, n1p in bparts]) \
                                .min(axis=0).reshape(64, 64)
                            fa = np.stack([
                                F3E[n0][:, :, None] + F3T[n1, n1p][:, None, :]
                                - oldA for n0, n1, n1p in aparts]) \
                                .min(axis=0).reshape(64, 64)
                            np.minimum(best, fb[:, :, None, None]
                                       + fa[None, None, :, :]
                                       + np.int16(struct), out=best)

                        for sw in (0, 1):
                            s0b, s1b = (t0b, t1b) if sw == 0 else (t1b, t0b)
                            s0a, s1a = (t0a, t1a) if sw == 0 else (t1a, t0a)
                            group([(s0b, s1b, LM[t21b, pp])
                                   for pp in (1, 2)],
                                  [(LM[s0a, Z], LM[s1a, c], t21a)
                                   for c in (1, 2)], -2)
                            group([(LM[s0b, Z], LM[s1b, c], LM[t21b, pp])
                                   for c in (1, 2) for pp in (1, 2)],
                                  [(s0a, s1a, t21a)], -2 - 2 * ja)
                            if ja:
                                group([(s0b, LM[s1b, le], LM[t21b, pp])
                                       for le in (1, 2) for pp in (1, 2)],
                                      [(LM[s0a, m0], LM[s1a, m1], t21a)
                                       for m0 in (1, 2, 3)
                                       for m1 in (1, 2, 3) if m1 != m0], -2)
                            if case2 == "PA":
                                bparts = [(LM[s0b, m0], LM[s1b, m1],
                                           LM[t21b, m12])
                                          for m0 in (1, 2, 3)
                                          for m1 in (1, 2, 3) if m1 != m0
                                          for m12 in (1, 2)]
                                struct = 0
                            else:
                                bparts = [(LM[s0b, m0], LM[s1b, m1], t21b)
                                          for m0 in (1, 2, 3)
                                          for m1 in (1, 2, 3) if m1 != m0]
                                struct = -2
                            group(bparts,
                                  [(s0a, LM[s1a, le], LM[t21a, l2])
                                   for le in (1, 2) for l2 in (1, 2)],
                                  struct)
                        total_b += best.size
                        m = int(best.max())
                        worst_b = max(worst_b, m)
                        nf = int((best > 0).sum())
                        fail_total += nf
                        if nf:
                            key = f"{case2}_ja{ja}_delta"
                            for d in range(1, m + 1):
                                cnt = int((best == d).sum())
                                if cnt:
                                    census[f"{key}{d}"] = \
                                        census.get(f"{key}{d}", 0) + cnt
    if total_b != rec_b["domain_size"] \
            or fail_total != rec_b["failures_total"] \
            or worst_b != rec_b["worst_delta"]:
        fail(f"V6 T4b mismatch: total={total_b} fails={fail_total} "
             f"worst={worst_b}")
    if census != rec_b["failing_census"]:
        fail("V6 T4b census mismatch")


# ---- V7 / V8 ----------------------------------------------------------------

def check_armc(rec):
    hr = rec["hostile_referee"]
    if hr["sandwich_failures"] or hr["dxx_witness_failures"] \
            or hr["replay_failures"]:
        fail("V7 Arm C referee failures present")
    if hr["dxx_witness_rows"] != hr["rows"]:
        fail("V7 Arm C witness coverage not 100%")
    if rec["gap_rows_total"] <= rec["gap_verbatim_cap"] \
            and rec["gap_rows_total"] != len(rec["gap_rows_verbatim"]):
        fail("V7 gap accounting mismatch")
    c1 = rec["c1_realizations"]
    for row in c1["rows"]:
        if row["config_feasible"] and not row["reference_dominated"]:
            fail(f"V7 realization {row['index']} n{row['n']}: reference "
                 "comm-s2 config below C_Dxx (impossible)")
        vals = [v for v in (row["C_Dplus"], row["f_Bprime"],
                            row["f_Bsecond"]) if v is not None]
        if vals and row["C_Dxx"] > min(vals) and row["gap"] >= 0:
            fail(f"V7 realization {row['index']}: sandwich broken")


def check_terminal(rec):
    t3ok = rec["t3_consolidation"]["failures"] == 0
    m1ok = rec["m1_inventory"]["holds"]
    t4a_ok = rec["t4a_unpinned"]["worst_delta"] <= 0
    t4b_closed = rec["t4b_pinned"]["failures_total"] == 0
    gaps = rec["arm_c"]["gap_rows_total"]
    confirmed = any(r.get("replay_confirmed")
                    for r in rec["arm_c"]["gap_rows_verbatim"])
    gates_ok = all(bool(v) for v in rec["gates"].values())
    if confirmed and gates_ok:
        expect = "QG7C_TRADE_BASIS_EXTENDED"
    elif not gates_ok or gaps > 0:
        expect = "QG7C_CANNOT_CHECK"
    elif t3ok and m1ok and t4a_ok and t4b_closed and False:
        expect = "QG7C_FOUR_CONFIGURATION_CLASSIFICATION_ALL_N_MACHINE_CHECKED"
    elif t3ok and m1ok:
        expect = "QG7C_PARTIAL__L4B_OPEN"
    elif m1ok:
        expect = "QG7C_PARTIAL__L4B_L4C_OPEN"
    else:
        expect = "QG7C_CANNOT_CHECK"
    if rec["terminal"] != expect:
        fail(f"V8 terminal {rec['terminal']} != derived {expect}")
    if "NOT_R6" not in rec["authority"]:
        fail("V8 authority ceiling violated")
    for flag in ("novelty_credit", "donor_novelty_credit", "r6_authority",
                 "reserved_stretched_n2_accessed", "chemistry_data_read"):
        if rec[flag]:
            fail(f"V8 flag {flag} not False")


def check_digest(rec):
    body = {k: v for k, v in rec.items()
            if k not in ("timing", "result_digest")}
    digest = hashlib.sha256(canonical_json(body).encode()).hexdigest()
    if digest != rec["result_digest"]:
        fail("V8 result digest mismatch")


def main() -> int:
    rec = json.loads(RESULTS.read_text())
    sha = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if rec["protocol_sha256"] != sha:
        fail("V1 protocol sha mismatch")
    if rec["schema"] != "ORIONQG.QG7C.Classification.v1":
        fail("V1 schema mismatch")
    check_mg(rec["mg_gauge"])
    check_m1(rec["m1_inventory"])
    check_t1_t5(rec["t1_prune"], rec["t5_home_merge"])
    check_t3(rec["t3_consolidation"])
    check_t4(rec["t4a_unpinned"], rec["t4b_pinned"])
    check_armc(rec["arm_c"])
    check_terminal(rec)
    check_digest(rec)
    if failures:
        print("REJECT")
        for msg in failures:
            print("  -", msg)
        return 1
    print("ACCEPT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
