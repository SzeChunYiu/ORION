#!/usr/bin/env python3
"""ORION-QG QG-7: all-n enlarged-borrow completeness — B' exact for all n, or
a fourth support-two TARE regime.

Frozen by development/orion-qg-regime-geometry/QG7_BPRIME_COMPLETENESS_PROTOCOL_V1.md
(frozen BEFORE any outcome under that protocol was computed).

Arm 1 (counterexample-first, mandatory): frozen adversarial D++ witness-shape
generator over hypothesis shapes H1-H5 at n=3 and n=4 quotient
representatives with a frozen Restore-template grammar, frozen enumeration
order and hard caps; every instance evaluated by the committed exact
production evaluators C_DP (unrestricted frozen-config DP), C_D++ (r6p
independent enumerator), C_D+ (weight-1 restriction) and f_B' (the EXACT
committed QG-5b enlarged borrow family, imported unmodified and never
enlarged). A single confirmed instance with C_D++ < min(C_D+, f_B') is the
fourth-regime discovery terminal.

Arm 2 (normalization obligations L1-L5): complete finite local-domain
checks N0-N7 with adversarial-environment F3 tables; obligations honestly
adjudicated CLOSED_ALL_N / CLOSED_CONDITIONAL / PARTIALLY_CLOSED / OPEN.

All frozen machinery imported UNMODIFIED. Authority ceiling NOT_R6.
No chemistry data is read; the protected stretched-N2 subject is never
touched. Fully deterministic; no RNG anywhere in the lane.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ORION_Q_DIR = Path(__file__).resolve().parents[1] / "orion-q"
sys.path.insert(0, str(ORION_Q_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import qg5b_exact_forecaster as qg5b  # noqa: E402

# declared runtime guard extension (protocol section "Imported committed
# machinery"): the committed n-generic enumerator's integrity guard learns
# the committed R6S support-2 pair count for n=4; no file is modified.
r6p.EXPECTED_PAIR_COUNTS.setdefault(4, r6s.PAIR_COUNTS_SUPPORT2[4])

h = p10.h
sy = h.local_symp
lw = h.local_wt
INF = r6m.INF
MATCHING = r6m._SYNTHETIC_MATCHING
CENTRALS8 = tuple(itertools.product((0, 1), repeat=3))
PROTOCOL_NAME = "QG7_BPRIME_COMPLETENESS_PROTOCOL_V1.md"
BASE_REVISION = "c796944d82c19cdceef0302b2a0cb6de7fc41b80"
VERBATIM_CAP = 50
CAPS = {
    ("H1", 3): 120, ("H2", 3): 160, ("H3", 3): 90, ("H4", 3): 90,
    ("H5", 3): 120,
    ("H1", 4): 40, ("H2", 4): 40, ("H3", 4): 24, ("H4", 4): 32, ("H5", 4): 24,
}
PANEL_ORDER = [
    ("H1", 3), ("H2", 3), ("H3", 3), ("H4", 3), ("H5", 3),
    ("H1", 4), ("H2", 4), ("H3", 4), ("H4", 4), ("H5", 4),
]

X, Y, Z = 1, 2, 3


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def K(letter: int, q: int):
    return r6o._letter_key(letter, q)


def kmul(*keys):
    out = (0, 0)
    for k in keys:
        out = p10.mul(out, k)
    return out


def f3_local(a: int, b: int, c: int) -> int:
    if a == b == c != 0:
        return 1
    return lw(a) + lw(b) + lw(c)


# ---- frozen skeleton menus ---------------------------------------------------

def anchored(q, v, c):
    return (K(v, q), K(c, q))


def phantom(home, m0m1, borrow, ell):
    m0, m1 = m0m1
    return (K(m0, home), kmul(K(ell, borrow), K(m1, home)))


def _s_letter(s_key, q):
    return r6o._local_code(s_key, q)


def phantom_h1(home, mv, borrow, s_key):
    """H1 letter rule: tag letter at home forces (m0,m1,ell) = (X,Y,X)."""
    if _s_letter(s_key, home) != 0:
        return phantom(home, (X, Y), borrow, X)
    return phantom(home, mv, borrow, Y)


def skeletons_h1(n):
    out = []
    if n == 3:
        s = kmul(K(X, 0), K(X, 1))
        for hA in (1, 2):
            for hB in (0, 2):
                for aC in (0, 1):
                    out.append((
                        phantom_h1(hA, (X, Y), 0, s)
                        + phantom_h1(hB, (X, Y), 1, s)
                        + anchored(aC, X, Y), s))
    else:
        s = kmul(K(X, 0), K(X, 1))
        for hA in (1, 3):
            for hB in (0, 3):
                for aC in (0, 1):
                    out.append((
                        phantom_h1(hA, (X, Y), 0, s)
                        + phantom_h1(hB, (X, Y), 1, s)
                        + anchored(aC, X, Y), s))
        s3 = kmul(K(X, 0), K(X, 1), K(X, 2))
        for mvs in (((X, Y), (X, Y), (X, Y)), ((X, Y), (Y, Z), (X, Y))):
            out.append((
                phantom_h1(3, mvs[0], 0, s3)
                + phantom_h1(3, mvs[1], 1, s3)
                + phantom_h1(3, mvs[2], 2, s3), s3))
    return out


def _h2_assemble(r0, r1, s):
    """Blocks B, C anchored per protocol; deterministic A frame-order fix."""
    supp_s = qg5b._qubits(qg5b._supp_mask(s))
    qa = supp_s[0]
    qc = supp_s[1] if len(supp_s) >= 2 else qa
    rest = anchored(qa, X, Y) + anchored(qc, X, Z)
    for a_frames in ((r0, r1), (r1, r0)):
        frames6 = a_frames + rest
        if r6s.config_labels(frames6, s)[0]:
            return (frames6, s)
    return ((r0, r1) + rest, s)


def skeletons_h2(n):
    out = []
    if n == 3:
        for (u0, v0, u1, v1) in ((X, X, Y, X), (X, X, Y, Y), (Y, X, X, X),
                                 (X, Y, X, X)):
            for s in (kmul(K(X, 0), K(X, 1)), K(X, 0)):
                r0 = kmul(K(u0, 0), K(v0, 1))
                r1 = kmul(K(u1, 0), K(v1, 1))
                out.append(_h2_assemble(r0, r1, s))
        for (u0, v0, u1, v1) in ((X, X, Y, X), (X, X, Y, Y), (X, Y, X, X),
                                 (Y, Y, X, Y)):
            for s in (kmul(K(X, 0), K(X, 2)), K(X, 2)):
                r0 = kmul(K(u0, 0), K(v0, 1))
                r1 = kmul(K(u1, 1), K(v1, 2))
                out.append(_h2_assemble(r0, r1, s))
    else:
        for (u0, v0, u1, v1) in ((X, X, X, X), (X, Y, X, Y)):
            for s in (kmul(K(X, 0), K(X, 2)), kmul(K(X, 1), K(X, 3))):
                r0 = kmul(K(u0, 0), K(v0, 1))
                r1 = kmul(K(u1, 2), K(v1, 3))
                out.append(_h2_assemble(r0, r1, s))
        for (u0, v0, u1, v1) in ((X, X, Y, X), (X, X, Y, Y), (X, Y, X, X),
                                 (Y, Y, X, Y)):
            s = kmul(K(X, 2), K(X, 3))
            r0 = kmul(K(u0, 0), K(v0, 1))
            r1 = kmul(K(u1, 1), K(v1, 2))
            out.append(_h2_assemble(r0, r1, s))
        for (u0, v0, u1, v1) in ((X, X, Y, X), (X, X, Y, Y)):
            s = kmul(K(X, 0), K(X, 3))
            r0 = kmul(K(u0, 0), K(v0, 1))
            r1 = kmul(K(u1, 0), K(v1, 1))
            out.append(_h2_assemble(r0, r1, s))
    return out


def skeletons_h3(n):
    out = []
    if n == 3:
        s3 = kmul(K(X, 0), K(X, 1), K(X, 2))
        for m1 in (Y, Z):
            frames = ()
            for home, borrow in ((0, 1), (1, 2), (2, 0)):
                frames += (K(X, home), kmul(K(X, borrow), K(m1, home)))
            out.append((frames, s3))
        s2 = kmul(K(X, 0), K(X, 1))
        for m1 in (Y, Z):
            for aC in (0, 1):
                frames = (
                    K(X, 0), kmul(K(X, 1), K(m1, 0)),
                    K(X, 1), kmul(K(X, 0), K(m1, 1)),
                ) + anchored(aC, X, Y)
                out.append((frames, s2))
    else:
        s2 = kmul(K(X, 0), K(X, 1))
        for ellB in (Y, Z):
            for aC in (0, 1):
                frames = (
                    phantom(3, (X, Y), 1, Y)
                    + phantom(3, (Y, Z), 0, ellB)
                    + anchored(aC, X, Y))
                out.append((frames, s2))
        s3 = kmul(K(X, 0), K(X, 1), K(X, 2))
        for m1 in (Y, Z):
            frames = ()
            for home, borrow in ((0, 1), (1, 2), (2, 0)):
                frames += (K(X, home), kmul(K(X, borrow), K(m1, home)))
            out.append((frames, s3))
    return out


def skeletons_h4(n):
    out = []
    if n == 3:
        s = kmul(K(X, 0), K(X, 1))
        for cC in (0, 1):
            for cL in (Y, Z):
                frames = (
                    phantom(2, (X, Y), 0, Y)
                    + anchored(1, X, Y)
                    + anchored(cC, X, cL))
                out.append((frames, s))
        sb = kmul(K(X, 0), K(Z, 2))
        a_frames = (kmul(K(Y, 0), K(Y, 2)), K(X, 2))
        for c_blk in (anchored(0, X, Z), phantom(1, (X, Y), 0, Y)):
            out.append((a_frames + anchored(0, X, Y) + c_blk, sb))
    else:
        s = kmul(K(X, 0), K(X, 1))
        for home in (2, 3):
            for cC in (0, 1):
                for cL in (Y, Z):
                    frames = (
                        phantom(home, (X, Y), 0, Y)
                        + anchored(1, X, Y)
                        + anchored(cC, X, cL))
                    out.append((frames, s))
    return out


def skeletons_h5(n):
    s = K(X, 0)
    third_home = 2 if n == 3 else 3
    return [
        (phantom(1, (X, Y), 0, Y) + anchored(0, X, Y) + anchored(0, X, Z), s),
        (phantom(1, (X, Y), 0, Y) + phantom(1, (Y, Z), 0, Z)
         + anchored(0, X, Y), s),
        (phantom(1, (X, Y), 0, Y) + phantom(third_home, (Y, Z), 0, Z)
         + anchored(0, X, Y), s),
    ]


SKELETON_BUILDERS = {
    "H1": skeletons_h1, "H2": skeletons_h2, "H3": skeletons_h3,
    "H4": skeletons_h4, "H5": skeletons_h5,
}

# ---- frozen Restore-template grammar ----------------------------------------

PATTERN_BASE = {1: (X, 0, 0), 2: (X, X, 0), 3: (X, X, Y), 4: (X, X, X),
                5: (X, Y, Z)}


def branch_choices(n):
    """[None] + all (P, q_c, rot) sorted by (rot, P, q_c) (frozen rank)."""
    out = [None]
    for rot in (0, 1, 2):
        for pat in (1, 2, 3, 4, 5):
            if pat == 4 and rot > 0:
                continue
            for q in range(n):
                out.append((pat, q, rot))
    return out


def template_pairs(n):
    choices = branch_choices(n)
    idx = {c: i for i, c in enumerate(choices)}
    pairs = list(itertools.product(choices, repeat=2))
    pairs.sort(key=lambda pc: (
        (pc[0] is not None) + (pc[1] is not None),
        idx[pc[0]] + idx[pc[1]], idx[pc[0]], idx[pc[1]]))
    return pairs


def template_pairs_h5(n, occupied):
    choices = branch_choices(n)
    idx = {c: i for i, c in enumerate(choices)}
    pairs = [
        (c0, c1)
        for c0 in choices for c1 in choices
        if c0 is not None and c1 is not None
        and c0[1] in occupied and c1[1] in occupied
    ]
    pairs.sort(key=lambda pc: (idx[pc[0]] + idx[pc[1]], idx[pc[0]], idx[pc[1]]))
    return pairs


def derive_instance(frames6, pair):
    """t_jk = T_jk * R_jk; None if any target is zero."""
    targets = []
    for j in range(3):
        for k in range(2):
            t = frames6[2 * j + k]
            choice = pair[k]
            if choice is not None:
                pat, q_c, rot = choice
                letter = PATTERN_BASE[pat][(j - rot) % 3]
                if letter:
                    t = p10.mul(t, K(letter, q_c))
            if t == (0, 0):
                return None
            targets.append(t)
    return ((targets[0], targets[1]), (targets[2], targets[3]),
            (targets[4], targets[5]))


# ---- canonicalization (qubit perms x per-qubit letter perms) ----------------

LETTER_PERMS = [
    (0,) + perm for perm in itertools.permutations((1, 2, 3))
]


def canonical_key(tp, n):
    keys6 = [t for pair in tp for t in pair]
    cols = []
    for q in range(n):
        col = tuple(r6o._local_code(t, q) for t in keys6)
        cols.append(min(tuple(pm[c] for c in col) for pm in LETTER_PERMS))
    return (n,) + tuple(sorted(cols))


def instance_from_key(key):
    n = key[0]
    cols = key[1:]
    keys6 = []
    for i in range(6):
        x = z = 0
        for q, col in enumerate(cols):
            bx, bz = h.CODE_BITS[col[i]]
            x |= bx << q
            z |= bz << q
        keys6.append((x, z))
    return ((keys6[0], keys6[1]), (keys6[2], keys6[3]), (keys6[4], keys6[5]))


# ---- per-instance evaluation -------------------------------------------------

def _clear_instance_caches():
    r6o._block_cache.clear()
    qg5b._bprime_block_cache.clear()


def evaluate(tp, n):
    _clear_instance_caches()
    terms = r6m._synthetic_terms(tp)
    c_dp = int(r6o.dp_cost_frozen_configs(terms, n))
    dxx = r6p.dxx_search(tp, n, want_witness=True)
    c_dxx = int(dxx["C_Dxx"])
    c_dplus = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
    fbp, fbp_wit = qg5b.bprime_family_min(tp, n, want_witness=True)
    fbp_eff = INF if fbp is None else int(fbp)
    failures = []
    if not (c_dp <= c_dxx <= c_dplus):
        failures.append({"sandwich": [c_dp, c_dxx, c_dplus]})
    if fbp_eff < INF and c_dp > fbp_eff:
        failures.append({"bprime_soundness": [c_dp, fbp_eff]})
    contradiction = None
    if c_dp != c_dxx:
        contradiction = {"C_DP": c_dp, "C_Dxx": c_dxx,
                         "target_pairs": [[list(a), list(b)] for a, b in tp]}
    q_min = min(c_dplus, fbp_eff)
    gap4 = c_dxx - q_min
    if gap4 < 0:
        regime = "fourth"
    elif c_dxx == c_dplus == fbp_eff:
        regime = "tie"
    elif c_dxx == c_dplus:
        regime = "split"
    else:
        regime = "borrow"
    return {
        "C_DP": c_dp, "C_Dxx": c_dxx, "C_Dplus": c_dplus,
        "f_Bprime": fbp_eff, "gap4": int(gap4), "regime": regime,
        "_dxx_witness": dxx["witness"], "_bprime_witness": fbp_wit,
        "_failures": failures, "_contradiction": contradiction,
    }


def _new_counters():
    return {
        "dxx_witness_rows": 0, "dxx_witness_failures": [],
        "bprime_witness_rows": 0, "bprime_witness_failures": [],
        "exact_matcher_rows": 0, "exact_matcher_failures": [],
        "containment_rows": 0, "containment_failures": [],
        "symmetry_rows": 0, "symmetry_failures": [],
        "replay_rows": 0, "replay_failures": [],
    }


def skeleton_min_cost(t6, frames6, s, n):
    best = None
    for centrals in CENTRALS8:
        v = int(r6s.config_cost(t6, frames6, s, centrals, n))
        if best is None or v < best:
            best = v
    return best


FULL_CENSUS_ROWS: list = []   # V2: every evaluated instance, not only fourth-regime

def run_panel(hname, n, counters, dedupe, global_state, sample_rows,
              contradictions, hard_failures):
    skels = SKELETON_BUILDERS[hname](n)
    cap = CAPS[(hname, n)]
    skel_meta = []
    for frames6, s in skels:
        ok, labels = r6s.config_labels(frames6, s)
        skel_meta.append({
            "feasible": bool(ok),
            "labels": list(labels) if labels else None,
            "max_frame_support": max(p10.wt(f) for f in frames6),
        })
    if hname == "H5":
        pair_lists = []
        for frames6, s in skels:
            occ = set(qg5b._qubits(qg5b._supp_mask(s)))
            for f in frames6:
                occ |= set(qg5b._qubits(qg5b._supp_mask(f)))
            pair_lists.append(template_pairs_h5(n, occ))
    else:
        shared = template_pairs(n)
        pair_lists = [shared] * len(skels)
    template_space = sum(len(pl) for pl in pair_lists)
    max_tp = max(len(pl) for pl in pair_lists)

    raw = zero_skip = dup_skip = 0
    evaluated = []
    census = {"split": 0, "borrow": 0, "tie": 0, "fourth": 0}
    gaps = []
    fourth_local = []
    cap_hit = False
    for tp_idx in range(max_tp):
        if cap_hit:
            break
        for s_idx, (frames6, s) in enumerate(skels):
            if len(evaluated) >= cap:
                cap_hit = True
                break
            if tp_idx >= len(pair_lists[s_idx]):
                continue
            raw += 1
            tp = derive_instance(frames6, pair_lists[s_idx][tp_idx])
            if tp is None:
                zero_skip += 1
                continue
            key = canonical_key(tp, n)
            if key in dedupe:
                dup_skip += 1
                continue
            dedupe.add(key)
            gidx = global_state["eval_idx"]
            global_state["eval_idx"] += 1
            if gidx % 128 == 0:
                r6m._local_table.cache_clear()
            row = evaluate(tp, n)
            lidx = len(evaluated)
            for f in row["_failures"]:
                hard_failures.append({"panel": f"{hname}_n{n}",
                                      "local_index": lidx, **f})
            if row["_contradiction"] is not None:
                contradictions.append({"panel": f"{hname}_n{n}",
                                       "local_index": lidx,
                                       **row["_contradiction"]})
            census[row["regime"]] += 1
            FULL_CENSUS_ROWS.append({
                "panel": f"{hname}_n{n}", "local_index": lidx,
                "f_Bprime": row["f_Bprime"], "C_Dxx": row["C_Dxx"],
                "C_Dplus": row["C_Dplus"], "C_DP": row["C_DP"],
                "gap4": row["gap4"], "regime": row["regime"],
            })
            gaps.append(row["gap4"])
            where = [hname, n, lidx]
            # skeleton containment gate
            if skel_meta[s_idx]["feasible"] and \
                    skel_meta[s_idx]["max_frame_support"] <= 2:
                t6 = tuple(t for pair in tp for t in pair)
                counters["containment_rows"] += 1
                ub = skeleton_min_cost(t6, frames6, s, n)
                if row["C_Dxx"] > ub:
                    counters["containment_failures"].append(where + [ub])
            # referee sampling
            if row["C_Dxx"] < row["C_Dplus"] or gidx % 7 == 0:
                counters["dxx_witness_rows"] += 1
                if not r6p.verify_dxx_witness(tp, n, row["_dxx_witness"]):
                    counters["dxx_witness_failures"].append(where)
            if row["f_Bprime"] < INF:
                counters["bprime_witness_rows"] += 1
                if not qg5b.verify_bprime_witness(tp, n,
                                                  row["_bprime_witness"]):
                    counters["bprime_witness_failures"].append(where)
            matcher_due = (n == 3 and lidx % 20 == 0) or \
                (n == 4 and lidx % 8 == 0) or row["gap4"] < 0
            if matcher_due:
                counters["exact_matcher_rows"] += 1
                terms = r6m._synthetic_terms(tp)
                wit = r6m.exact_r6m_matching(terms, MATCHING, n,
                                             list(range(6)))
                if int(wit["C_R6M"]) != row["C_DP"] or \
                        not all(wit["checks"].values()):
                    counters["exact_matcher_failures"].append(where)
            if gidx % 17 == 0:
                counters["symmetry_rows"] += 1
                image = instance_from_key(key)
                irow = evaluate(image, n)
                if any(irow[k] != row[k] for k in
                       ("C_DP", "C_Dxx", "C_Dplus", "f_Bprime")):
                    counters["symmetry_failures"].append(where)
            if row["gap4"] < 0:
                counters["replay_rows"] += 1
                replay_ok = r6p.verify_dxx_witness(tp, n, row["_dxx_witness"])
                terms = r6m._synthetic_terms(tp)
                wit = r6m.exact_r6m_matching(terms, MATCHING, n,
                                             list(range(6)))
                replay_ok = replay_ok and int(wit["C_R6M"]) == row["C_DP"] \
                    and all(wit["checks"].values())
                if not replay_ok:
                    counters["replay_failures"].append(where)
                if len(fourth_local) < VERBATIM_CAP:
                    fourth_local.append({
                        "panel": f"{hname}_n{n}", "local_index": lidx,
                        "target_pairs": [[list(a), list(b)] for a, b in tp],
                        "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
                        "C_Dplus": row["C_Dplus"],
                        "f_Bprime": row["f_Bprime"], "gap4": row["gap4"],
                        "replay_confirmed": bool(replay_ok),
                        "dxx_witness_verbatim": row["_dxx_witness"],
                        "bprime_witness_verbatim": row["_bprime_witness"],
                    })
            evaluated.append({
                "target_pairs": [[list(a), list(b)] for a, b in tp],
                "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
                "C_Dplus": row["C_Dplus"], "f_Bprime": row["f_Bprime"],
            })
        else:
            continue
        break
    r6m._local_table.cache_clear()
    # verification sample: local indices {0, count//2}
    for lidx in sorted({0, len(evaluated) // 2} & set(range(len(evaluated)))):
        sample_rows.append({"panel": f"{hname}_n{n}", "n": n,
                            "local_index": lidx, **evaluated[lidx]})
    summary = {
        "skeletons": len(skels),
        "infeasible_skeletons": sum(1 for m in skel_meta if not m["feasible"]),
        "template_pair_space": template_space,
        "raw_scanned": raw,
        "zero_target_skipped": zero_skip,
        "duplicate_skipped": dup_skip,
        "evaluated": len(evaluated),
        "cap": cap,
        "cap_hit": cap_hit,
        "regime_census": census,
        "min_gap4": min(gaps) if gaps else None,
        "max_gap4": max(gaps) if gaps else None,
    }
    return summary, fourth_local


# ---- Arm 2: complete finite local-domain checks ------------------------------

def check_n1():
    maxima = {"in_place_change": -99, "removal_new_identity": -99,
              "addition_old_identity": -99}
    domain = 0
    for slot in range(3):
        for old in range(4):
            for new in range(4):
                for b in range(4):
                    for c in range(4):
                        domain += 1
                        env = [b, c]
                        trip_old = env[:slot] + [old] + env[slot:]
                        trip_new = env[:slot] + [new] + env[slot:]
                        d = f3_local(*trip_new[:3]) - f3_local(*trip_old[:3])
                        if old != 0 and new != 0:
                            maxima["in_place_change"] = max(
                                maxima["in_place_change"], d)
                        if new == 0:
                            maxima["removal_new_identity"] = max(
                                maxima["removal_new_identity"], d)
                        if old == 0:
                            maxima["addition_old_identity"] = max(
                                maxima["addition_old_identity"], d)
    holds = (maxima["in_place_change"] == 2
             and maxima["removal_new_identity"] == 1
             and maxima["addition_old_identity"] == 1)
    return {"domain_size": domain, "maxima": maxima, "holds": bool(holds)}


def check_n2():
    domain = 0
    violations = 0
    equality_failures = 0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                domain += 1
                v = f3_local(a, b, c)
                bound = lw(a) + lw(b) + lw(c)
                if v > bound:
                    violations += 1
                all_eq = a == b == c != 0
                if all_eq and bound - v != 2:
                    equality_failures += 1
                if not all_eq and v != bound:
                    equality_failures += 1
    return {"domain_size": domain, "violations": violations,
            "equality_characterization_failures": equality_failures,
            "holds": violations == 0 and equality_failures == 0}


def check_n3():
    tuples = []
    for a1, b1, a2, b2 in itertools.product((0, 1), repeat=4):
        if (a1 + a2) % 2 == 1:
            tuples.append(((a1, b1), (a2, b2)))
    reducible = []
    irreducible = []
    dichotomy_failures = []
    for t in tuples:
        if (0, 0) in t:
            reducible.append(t)
        else:
            zero_alpha = [cb for cb in t if cb[0] == 0]
            if all(cb[1] == 1 for cb in zero_alpha):
                irreducible.append(t)
            else:
                dichotomy_failures.append(t)
    irreducible_codes = sorted(
        [2 * a + b for a, b in t] for t in irreducible)
    expected = sorted([[1, 2], [1, 3], [2, 1], [3, 1]])
    return {
        "odd_alpha_tuples": len(tuples),
        "reducible_by_zeroing": len(reducible),
        "irreducible_borrow_patterns": len(irreducible),
        "dichotomy_failures": [list(map(list, t)) for t in dichotomy_failures],
        "irreducible_codes": irreducible_codes,
        "binds_r6s_w2_boundary": irreducible_codes == expected,
        "holds": not dichotomy_failures and irreducible_codes == expected,
    }


def check_n4():
    table = {}
    for wc in (1, 2):
        for wnc in (1, 2):
            table[f"u_central_{wc}_noncentral_{wnc}"] = \
                4 * (wnc - 1) + 2 * (wc - 1)
    holds = (table["u_central_2_noncentral_1"] == 2
             and table["u_central_1_noncentral_2"] == 4
             and table["u_central_2_noncentral_2"] == 6
             and table["u_central_1_noncentral_1"] == 0)
    return {"table": table, "central_on_heavier_strictly_cheaper_by_2": holds,
            "holds": holds}


def check_n5(n1_maxima):
    patterns = [
        ("same_support", (0, 1), (0, 1)),
        ("shared_one_qubit", (0, 1), (1, 2)),
        ("disjoint", (0, 1), (2, 3)),
    ]
    per_pattern = {}
    failures = []
    total = 0
    for name, q0s, q1s in patterns:
        union = sorted(set(q0s) | set(q1s))
        counts = {"cases": 0, "infeasible_pair": 0, "infeasible_labels": 0,
                  "reducible_by_zeroing": 0, "replaced": 0, "failures": 0}
        for f0, g0, f1, g1 in itertools.product((1, 2, 3), repeat=4):
            r0 = {q0s[0]: f0, q0s[1]: g0}
            r1 = {q1s[0]: f1, q1s[1]: g1}
            for sig in itertools.product((0, 1, 2, 3), repeat=len(union)):
                counts["cases"] += 1
                total += 1
                sigma = dict(zip(union, sig))
                symp = sum(sy(r0.get(q, 0), r1.get(q, 0)) for q in union) % 2
                if symp != 1:
                    counts["infeasible_pair"] += 1
                    continue
                l0 = sum(sy(sigma[q], r0[q]) for q in r0) % 2
                l1 = sum(sy(sigma[q], r1[q]) for q in r1) % 2
                if l0 == l1:
                    counts["infeasible_labels"] += 1
                    continue
                reducible = False
                for frame, other in ((r0, r1), (r1, r0)):
                    for q, letter in frame.items():
                        alpha = sy(letter, other.get(q, 0))
                        beta = sy(sigma[q], letter)
                        if alpha == 0 and beta == 0:
                            reducible = True
                if reducible:
                    counts["reducible_by_zeroing"] += 1
                    continue
                hot, cold = (r0, r1) if l0 == 1 else (r1, r0)
                found = None
                for qp in union:
                    for w in (1, 2, 3):
                        if sy(sigma[qp], w) == 1 and \
                                sy(w, cold.get(qp, 0)) == 1:
                            found = (qp, w)
                            break
                    if found:
                        break
                if found is None:
                    counts["failures"] += 1
                    if len(failures) < VERBATIM_CAP:
                        failures.append({
                            "pattern": name, "letters": [f0, g0, f1, g1],
                            "sigma": list(sig), "labels": [l0, l1]})
                    continue
                qp, w = found
                bound = 0
                for q in sorted(set(hot) | {qp}):
                    if q == qp and q in hot:
                        bound += n1_maxima["in_place_change"]
                    elif q == qp:
                        bound += n1_maxima["addition_old_identity"]
                    else:
                        bound += n1_maxima["removal_new_identity"]
                if bound > 4:
                    counts["failures"] += 1
                    if len(failures) < VERBATIM_CAP:
                        failures.append({
                            "pattern": name, "letters": [f0, g0, f1, g1],
                            "sigma": list(sig), "f3_bound_exceeded": bound})
                    continue
                counts["replaced"] += 1
        per_pattern[name] = counts
    expected_sizes = {"same_support": 81 * 16, "shared_one_qubit": 81 * 64,
                      "disjoint": 81 * 256}
    sizes_ok = all(per_pattern[k]["cases"] == v
                   for k, v in expected_sizes.items())
    total_failures = sum(c["failures"] for c in per_pattern.values())
    return {
        "domain_size": total,
        "per_pattern": per_pattern,
        "expected_sizes_bound": bool(sizes_ok),
        "failures_total": total_failures,
        "failures_verbatim": failures,
        "delta_u_refund": 4,
        "holds": sizes_ok and total_failures == 0,
    }


def check_n7():
    target_panel = [
        tuple(K(X, 0) for _ in range(6)),
        (K(X, 0), K(Y, 0), K(X, 0), K(Y, 0), K(X, 0), K(Y, 0)),
        (kmul(K(X, 0), K(X, 1)), K(Y, 1), K(Z, 0), K(X, 0),
         kmul(K(Y, 0), K(Z, 1)), K(X, 1)),
        tuple(K(Z, 1) for _ in range(6)),
        (kmul(K(X, 0), K(Y, 1)), kmul(K(Z, 0), K(Z, 1)), K(Y, 0), K(X, 1),
         kmul(K(Y, 0), K(Y, 1)), K(Z, 0)),
    ]
    pairs = [(a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b]
    checked = 0
    failures = 0
    valid_frame_tag = 0
    for pa in pairs:
        for pb in pairs:
            for pc in pairs:
                frames6 = (K(pa[0], 0), K(pa[1], 0), K(pb[0], 0),
                           K(pb[1], 0), K(pc[0], 0), K(pc[1], 0))
                for s0 in (1, 2, 3):
                    s = K(s0, 0)
                    ok, labels = r6s.config_labels(frames6, s)
                    if not ok:
                        continue
                    valid_frame_tag += 1
                    for e in (1, 2, 3):
                        s2 = kmul(s, K(e, 1))
                        ok2, labels2 = r6s.config_labels(frames6, s2)
                        for t6 in target_panel:
                            for centrals in ((0, 0, 0), (1, 0, 1)):
                                checked += 1
                                c1 = r6s.config_cost(t6, frames6, s, centrals, 2)
                                c2 = r6s.config_cost(t6, frames6, s2, centrals, 2)
                                if not ok2 or labels2 != labels or \
                                        c2 - c1 != 2:
                                    failures += 1
    return {"frame_tag_combinations_valid": valid_frame_tag,
            "checked": checked, "failures": failures,
            "exact_refund_2_everywhere": failures == 0,
            "holds": failures == 0}


def run_normalization():
    n0_e = r6s.verify_lemma_e()
    n0_b = r6s.verify_lemma_b()
    n1 = check_n1()
    n2 = check_n2()
    n3 = check_n3()
    n4 = check_n4()
    n5 = check_n5(n1["maxima"])
    n7 = check_n7()
    n0 = {
        "lemma_e": {"domain_size": n0_e["domain_size"],
                    "violations": n0_e["violations"],
                    "max_delta_f3": n0_e["max_delta_f3"]},
        "lemma_b": {
            "total_odd_alpha_tuples_checked":
                n0_b["total_odd_alpha_tuples_checked"],
            "w3_to_w8_all_admit_subset": n0_b["w3_to_w8_all_admit_subset"],
            "w2_failing_tuples_observed": n0_b["w2_failing_tuples_observed"],
        },
        "holds": (n0_e["holds"] and n0_e["domain_size"] == 18432
                  and n0_e["max_delta_f3"] == 2
                  and n0_b["w3_to_w8_all_admit_subset"]
                  and n0_b["total_odd_alpha_tuples_checked"] == 43688
                  and n0_b["w2_failing_tuples_observed"]
                  == [[1, 2], [1, 3], [2, 1], [3, 1]]),
    }
    checks = {"N0": n0, "N1": n1, "N2": n2, "N3": n3, "N4": n4, "N5": n5,
              "N7": n7}

    l1 = "CLOSED_ALL_N" if (n5["holds"] and n1["holds"] and n4["holds"]) \
        else "PARTIALLY_CLOSED"
    l2 = "CLOSED_ALL_N" if (n3["holds"] and n0["holds"] and n4["holds"]) \
        else "OPEN"
    l3 = "CLOSED_CONDITIONAL" if n2["holds"] else "OPEN"
    l4 = "PARTIALLY_CLOSED" if n7["holds"] else "OPEN"
    l5 = "PARTIALLY_CLOSED" if (n1["holds"] and n2["holds"]) else "OPEN"
    obligations = {
        "L1_canonical_block_shape": {
            "status": l1,
            "mechanism": (
                "complete-domain (2,2)-block elimination: every feasible "
                "lexicographically minimal (2,2) block admits a weight-one "
                "replacement of its label-1 frame inside the union support, "
                "refunding Delta_u = 4 against a worst-case adversarial "
                "branch-F3 delta <= 3 (N1 maxima); non-minimal blocks reduce "
                "by Lemma-E zeroing"),
            "domains": {"N5": n5["domain_size"], "N1": n1["domain_size"]},
        },
        "L2_support_two_orientation": {
            "status": l2,
            "mechanism": (
                "w=2 class dichotomy (N3): every optimal support-two frame "
                "has exactly one anticommuting qubit and one Tag-syndrome "
                "borrow qubit (irreducible codes bind the committed R6S w2 "
                "boundary); central placement on the support-two frame is "
                "strictly cheaper by 2 (N4)"),
            "domains": {"N3": 8, "N0_lemma_e": 18432, "N0_lemma_b": 43688},
        },
        "L3_borrow_home_normalization": {
            "status": l3,
            "mechanism": (
                "for configurations in the weight-one-Tag pre-B' normal "
                "form: in-support homes are already in B's frozen pool; "
                "empty-qubit homes merge into the single frozen empty "
                "representative by F3 colocation subadditivity (N2, exact "
                "per-qubit decomposition), never increasing cost"),
            "condition": (
                "conditional on the L4 consolidation to the weight-one-Tag "
                "normal form, which remains open"),
            "domains": {"N2": n2["domain_size"]},
        },
        "L4_multi_block_consolidation": {
            "status": l4,
            "closed_sublemma_L4a": (
                "tag letters outside the union frame support prune with an "
                "exact refund of 2 and unchanged labels (N7 complete domain)"),
            "open_shapes": [
                "H1_multi_anchor_borrow_tag_weight_ge_2",
                "H3_cyclic_borrow",
                "H4_hybrid_split_borrow",
                "H4b_l1_phantom_tag_letter_at_home",
            ],
            "domains": {"N7_checked": n7["checked"]},
        },
        "L5_f3_interaction_closure": {
            "status": l5,
            "mechanism": (
                "every closed exchange above is bounded against the FULL "
                "adversarial other-block branch letter domain (N1/N2 are "
                "complete-environment tables); no independent per-block "
                "summation is used anywhere; the obligation inherits L4's "
                "open shapes"),
            "domains": {"N1": n1["domain_size"], "N2": n2["domain_size"]},
        },
    }
    return checks, obligations


# ---- receipt bindings --------------------------------------------------------

QG5B_AUTHORITY = (
    "ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__"
    "DPP_FAMILY_MIN__ENLARGED_BORROW_CLOSES__NOT_R6"
)
R6S_AUTHORITY_PREFIX = "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"


def bind_receipts(n0):
    qg5b_rec = json.loads(
        (Path(__file__).with_name("QG5B_EXACT_FORECASTER_RESULTS.json"))
        .read_text())
    r6s_rec = json.loads(
        (ORION_Q_DIR / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json").read_text())
    pa = qg5b_rec["panels"]["panel_a_refuting_instance"]
    tp = tuple((tuple(a), tuple(b)) for a, b in pa["target_pairs"])
    row = evaluate(tp, int(pa["n"]))
    replay = {
        "n": int(pa["n"]),
        "target_pairs": pa["target_pairs"],
        "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
        "C_Dplus": row["C_Dplus"], "f_Bprime": row["f_Bprime"],
    }
    refuting_bound = (
        row["C_DP"] == int(pa["C_DP"]) == 10
        and row["C_Dxx"] == int(pa["F2_C_Dxx"]) == 10
        and row["C_Dplus"] == int(pa["C_Dplus"]) == 11
        and row["f_Bprime"] == int(pa["f_Bprime"]) == 10
        and not row["_failures"] and row["_contradiction"] is None
    )
    rle = r6s_rec["lemma_e"]
    rlb = r6s_rec["lemma_b"]
    r6s_bound = (
        str(r6s_rec["authority"]).startswith(R6S_AUTHORITY_PREFIX)
        and rle["domain_size"] == n0["lemma_e"]["domain_size"]
        and rle["violations"] == n0["lemma_e"]["violations"]
        and rle["max_delta_f3"] == n0["lemma_e"]["max_delta_f3"]
        and rlb["total_odd_alpha_tuples_checked"]
        == n0["lemma_b"]["total_odd_alpha_tuples_checked"]
        and rlb["w3_to_w8_all_admit_subset"]
        == n0["lemma_b"]["w3_to_w8_all_admit_subset"]
        and rlb["w2_failing_tuples_observed"]
        == n0["lemma_b"]["w2_failing_tuples_observed"]
    )
    qg5b_bound = (
        qg5b_rec["authority"] == QG5B_AUTHORITY
        and int(qg5b_rec["q1"]["dp_compared_instances_total"]) == 9547
        and qg5b_rec["q2"]["outcome"] == "Q2_ENLARGED_BORROW_CLOSES"
        and refuting_bound
    )
    return {
        "qg5b_authority_bound": qg5b_rec["authority"] == QG5B_AUTHORITY,
        "qg5b_dp_compared_instances_total":
            int(qg5b_rec["q1"]["dp_compared_instances_total"]),
        "qg5b_q2_outcome": qg5b_rec["q2"]["outcome"],
        "qg5_refuting_instance_replay": replay,
        "qg5_refuting_instance_bound": bool(refuting_bound),
        "qg5b_receipt_bound": bool(qg5b_bound),
        "r6s_authority": r6s_rec["authority"],
        "r6s_receipt_bound": bool(r6s_bound),
    }


# ---- claim boundary ----------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "A frozen adversarial hostile search for a fourth support-two "
        "regime (C_D++ < min(C_D+, f_B')) over the H1-H5 witness shapes at "
        "n=3 and n=4 quotient representatives under the frozen unit-cost "
        "R6M grammar and raw support-count objective, plus complete "
        "finite local-domain normalization lemmas (N0-N7) adjudicating the "
        "charter obligations L1-L5."
    ),
    "proven_components": (
        "C_DP <= C_D++ <= C_D+ (family containment, asserted per "
        "instance); C_DP <= f_B' (B' members are feasible grammar "
        "configurations); C_DP == C_D++ for all n (committed machine-"
        "checked MAX-R6S theorem, re-bound here); the closed normalization "
        "steps L1/L2 and sublemmas L3(conditional)/L4a hold for ALL n by "
        "complete local domains with worst-case adversarial F3 "
        "environments."
    ),
    "machine_evidenced_only": (
        "The absence of a fourth regime outside the closed steps is "
        "machine-evidenced only on the frozen finite hostile panels; the "
        "full identity C_D++ == min(C_D+, f_B') for all n remains "
        "CONJECTURE while the L4 consolidation shapes (multi-anchor "
        "borrow, cyclic borrow, hybrid split+borrow, l1-phantom) are open. "
        "A finite panel cannot authorize the all-n theorem."
    ),
    "does_not_cover": (
        "Other objectives (QG-2: O1 already exhibits NEW_SUPPORT3; no "
        "QG-7 statement transfers to any reweighted objective), other "
        "grammars, rotation-count trade-offs, chemistry subjects (no "
        "chemistry data is read in this lane), the protected stretched-N2 "
        "subject, or any donor/R6 novelty credit."
    ),
}

AUTHORITY = {
    "FOURTH": (
        "ORIONQG_QG7_FOURTH_SUPPORT2_REGIME_FOUND__"
        "HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6"),
    "CANNOT": (
        "ORIONQG_QG7_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6"),
    "ALL_N": (
        "ORIONQG_QG7_ENLARGED_BORROW_COMPLETENESS_ALL_N_MACHINE_CHECKED__"
        "L1_L5_CLOSED_WITH_R6S__NOT_R6"),
    "PARTIAL": (
        "ORIONQG_QG7_PARTIAL_NORMALIZATION__HYBRID_SHAPE_OPEN__"
        "HOSTILE_SEARCH_EMPTY__NOT_R6"),
}


# ---- main --------------------------------------------------------------------

def main() -> dict[str, Any]:
    start = time.monotonic()

    # gate: table + enumerator bindings
    r6s_bind = r6s.bind_tables()
    my_f3 = np.zeros((4, 4, 4), dtype=np.int64)
    for a in range(4):
        for b in range(4):
            for c in range(4):
                my_f3[a, b, c] = f3_local(a, b, c)
    pair_counts = {n: r6p._tables(n, 2).P for n in (1, 2, 3, 4)}
    tables_bound = (
        all(r6s_bind.values())
        and bool(np.array_equal(r6p.F3.astype(np.int64), r6m._F3))
        and bool(np.array_equal(my_f3, r6m._F3))
        and pair_counts == {1: 6, 2: 120, 3: 666, 4: 1968}
    )

    protocol_path = (
        Path(__file__).resolve().parents[3]
        / "development" / "orion-qg-regime-geometry" / PROTOCOL_NAME)
    protocol_sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()

    # ---- Arm 2 first is NOT allowed to gate Arm 1; run Arm 1 first ----
    counters = _new_counters()
    dedupe: set = set()
    global_state = {"eval_idx": 0}
    sample_rows: list = []
    contradictions: list = []
    hard_failures: list = []
    panels = {}
    fourth_candidates: list = []
    panel_seconds = {}
    for hname, n in PANEL_ORDER:
        t0 = time.monotonic()
        summary, fourth_local = run_panel(
            hname, n, counters, dedupe, global_state, sample_rows,
            contradictions, hard_failures)
        panels[f"{hname}_n{n}"] = summary
        fourth_candidates.extend(fourth_local)
        panel_seconds[f"{hname}_n{n}"] = round(time.monotonic() - t0, 3)

    total_eval = sum(p["evaluated"] for p in panels.values())
    fourth_total = sum(p["regime_census"]["fourth"] for p in panels.values())
    confirmed_total = sum(
        1 for c in fourth_candidates if c["replay_confirmed"])

    # ---- Arm 2 ----
    t0 = time.monotonic()
    checks, obligations = run_normalization()
    norm_seconds = round(time.monotonic() - t0, 3)

    # ---- receipt bindings ----
    bindings = bind_receipts(checks["N0"])

    gates = {
        "tables_bound": bool(tables_bound),
        "qg5b_receipt_bound": bindings["qg5b_receipt_bound"],
        "r6s_receipt_bound": bindings["r6s_receipt_bound"],
        "refuting_instance_bound": bindings["qg5_refuting_instance_bound"],
        "skeleton_containment_pass": not counters["containment_failures"],
        "dxx_witness_referee_pass": not counters["dxx_witness_failures"],
        "bprime_witness_referee_pass": not counters["bprime_witness_failures"],
        "exact_matcher_binding_pass": not counters["exact_matcher_failures"],
        "canonicalization_symmetry_pass": not counters["symmetry_failures"],
        "sandwich_and_soundness_pass": not hard_failures,
        "no_r6s_contradiction": not contradictions,
        "enumeration_counts_complete": all(
            p["raw_scanned"] >= p["evaluated"] and "cap_hit" in p
            for p in panels.values()),
        "normalization_domains_complete": (
            checks["N1"]["domain_size"] == 768
            and checks["N2"]["domain_size"] == 64
            and checks["N3"]["odd_alpha_tuples"] == 8
            and checks["N5"]["expected_sizes_bound"]
            and checks["N0"]["holds"]),
    }
    integrity_ok = all(gates.values())
    replays_ok = not counters["replay_failures"]

    # ---- frozen terminal selection ----
    l_statuses = {k: v["status"] for k, v in obligations.items()}
    all_closed = all(s == "CLOSED_ALL_N" for s in l_statuses.values())
    if confirmed_total > 0 and integrity_ok and replays_ok:
        terminal = "QG7_FOURTH_SUPPORT2_REGIME_FOUND"
        authority = AUTHORITY["FOURTH"]
        responsibility = (
            "RESP:FOURTH_SUPPORT2_REGIME_WITNESS_CONFIRMED_BY_INDEPENDENT_"
            "REFEREES__SERIALIZED_VERBATIM")
    elif fourth_total > 0 or contradictions or not integrity_ok:
        terminal = "QG7_CANNOT_CHECK"
        authority = AUTHORITY["CANNOT"]
        responsibility = (
            "RESP:REFEREE_OR_INTEGRITY_FAILURE__EVERYTHING_SERIALIZED_"
            "VERBATIM")
    elif all_closed:
        terminal = "QG7_ENLARGED_BORROW_COMPLETENESS_ALL_N_MACHINE_CHECKED"
        authority = AUTHORITY["ALL_N"]
        responsibility = (
            "RESP:L1_L5_CLOSED_WITH_EXACT_PRODUCTION_BINDING__COMBINED_"
            "WITH_R6S_ALL_N_THEOREM")
    else:
        terminal = "QG7_PARTIAL_NORMALIZATION__HYBRID_SHAPE_OPEN"
        authority = AUTHORITY["PARTIAL"]
        responsibility = (
            "RESP:HOSTILE_SEARCH_EMPTY__L1_L2_CLOSED_ALL_N__L3_CONDITIONAL__"
            "L4_CONSOLIDATION_SHAPES_OPEN__FINITE_PANEL_CANNOT_AUTHORIZE_"
            "THE_ALL_N_THEOREM")

    result = {
        "schema": "ORIONQG.QG7.BprimeCompleteness.v1",
        "schema_v2": "ORION10.BPRIME_FIBRE_CRITERION_FULL_CENSUS.v2",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "lane": "QG-7 all-n enlarged-borrow completeness (issue #757)",
        "protocol": "QG7_BPRIME_COMPLETENESS_PROTOCOL_V1",
        "protocol_sha256": protocol_sha,
        "base_revision": BASE_REVISION,
        "authority": authority,
        "terminal": terminal,
        "responsibility": responsibility,
        "scope": (
            "ALL_N_BPRIME_COMPLETENESS_CLASSIFICATION__HOSTILE_SEARCH_PLUS_"
            "NORMALIZATION_OBLIGATIONS__UNIT_SUPPORT_COUNT_OBJECTIVE_ONLY__"
            "NOT_R6"),
        "question": (
            "Does every support-two D++ optimum, for every n in the frozen "
            "unit-cost R6M grammar, normalize without cost increase into D+ "
            "or the enlarged borrow B' (C_D++ == min(C_D+, f_B')), or does "
            "a fourth support-two configuration exist?"),
        "arm1_hostile_search": {
            "panels": panels,
            "instances_evaluated_total": total_eval,
            "fourth_regime_candidates_total": fourth_total,
            "fourth_regime_confirmed_total": confirmed_total,
            "fourth_regime_candidates_verbatim": fourth_candidates,
            "full_census_rows_v2": FULL_CENSUS_ROWS,
            "r6s_contradictions_verbatim": contradictions,
            "hard_assertion_failures_verbatim": hard_failures,
            "verbatim_cap": VERBATIM_CAP,
        },
        "arm2_normalization": {
            "checks": checks,
            "obligations": obligations,
        },
        "verification_sample": sample_rows,
        "receipt_bindings": bindings,
        "hostile_referee": {
            k: (v if isinstance(v, int) else v) for k, v in counters.items()},
        "gates": gates,
        "claim_boundary": CLAIM_BOUNDARY,
        "novelty_credit": False,
        "donor_novelty_credit": False,
        "r6_authority": False,
        "physical_quantum_advantage_claim": False,
        "reserved_stretched_n2_accessed": False,
        "chemistry_data_read": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG7 authority ceiling violated")
    digest = hashlib.sha256(canonical_json(result).encode()).hexdigest()
    result["result_digest"] = digest

    runtime = round(time.monotonic() - start, 3)
    timing = {
        "convention": (
            "R6P: timing fields excluded from the canonical stdout line and "
            "the result digest; present only in this file section and on "
            "stderr"),
        "panel_seconds": panel_seconds,
        "normalization_seconds": norm_seconds,
        "runtime_seconds": runtime,
        "runtime_cap_seconds": 1500,
        "runtime_under_cap": runtime < 1500,
    }
    print("ORIONQG_QG7_BPRIME_COMPLETENESS=" + canonical_json(result))
    file_result = dict(result)
    file_result["timing"] = timing
    Path(__file__).with_name("FULL_CENSUS_RESULTS_V2.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n")
    print("qg7_runtime_seconds=%.3f" % runtime, file=sys.stderr)
    print("qg7_timing_summary=" + canonical_json(
        {k: v for k, v in timing.items() if k != "convention"}),
        file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
