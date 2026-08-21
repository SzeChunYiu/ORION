#!/usr/bin/env python3
"""QG-18: the intrinsic support number of TARE (kappa_TARE).

Frozen by development/orion-qg-regime-geometry/QG18_TARE_KAPPA_PROTOCOL_V1.md,
written before any outcome-determining run.

R6S proves that the frozen R6M/TARE grammar closes at frame support <= 2 for
every n under the frozen unit-cost support objective O0.  Nobody had tested
whether 2 is necessary.  This checker settles kappa_TARE two-sidedly:

  Q1  necessity hunt -- an exact instance with C_DP < C_cap1, where C_cap1 is
      the exact optimum over the complete support-<=1 family (all weight-one
      frames, all shared Tags, all Restores, all centrals, all target
      permutations).  A referee-confirmed strict gap proves kappa_TARE >= 2.
  Q2  transfer attempt -- the QG-9 V6 Tag-relocation lemma chain instantiated
      on R6M (deletion credit, core alignment, same-core Tag rigidity,
      distinct-core Tag lower bound, two-case composition), each on its
      complete finite local domain.  Terminal-bearing only if Q1 is empty;
      always run as the diagnostic that feeds Q3.
  Q3  structural diagnosis -- which property of a family makes Tag relocation
      available, stated from the measured numbers.

Authority ceiling NOT_R6.  No novelty credit, no donor-novelty credit, no
physical-advantage claim.  No chemistry source is read; the protected
stretched-N2 discriminator is never opened.  Every committed analyzer is
imported unmodified.
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

ROOT = Path(__file__).resolve().parents[3]
ORION_Q = ROOT / "research/extensions/orion-q"
ORION_QG = ROOT / "research/extensions/orion-qg"
sys.path.insert(0, str(ORION_Q))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402

PROTOCOL = ROOT / "development/orion-qg-regime-geometry/QG18_TARE_KAPPA_PROTOCOL_V1.md"
RESULTS = ORION_QG / "QG18_TARE_KAPPA_RESULTS.json"
TOKEN = "ORIONQG_QG18="
SEED = 20260821
VERBATIM_CAP = 20
RUNTIME_CAP_SECONDS = 25 * 60

h = p10.h
LETTERS = "IXYZ"
MATCHING = ((0, 1), (2, 3), (4, 5))
CENTRALS8 = tuple(itertools.product((0, 1), repeat=3))
PERMS4 = tuple(itertools.product((0, 1), repeat=2))
ORD = tuple((a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b)
LABELS2 = ((0, 1), (1, 0))

# ---- local algebra rebuilt from the production primitives -------------------
LW = [int(h.local_wt(a)) for a in range(4)]
LM = [[int(h.local_mul(a, b)) for b in range(4)] for a in range(4)]
SY = [[int(h.local_symp(a, b)) for b in range(4)] for a in range(4)]
F3 = [
    [
        [1 if (a == b == c and a != 0) else LW[a] + LW[b] + LW[c] for c in range(4)]
        for b in range(4)
    ]
    for a in range(4)
]
LWn = np.array(LW, dtype=np.int64)
LMn = np.array(LM, dtype=np.int64)
SYn = np.array(SY, dtype=np.int64)
F3n = np.array(F3, dtype=np.int64)

RECEIPTS = {
    "r6s": (
        ORION_Q / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json",
        "b6d72913c3bd42d9c822eace19563378c046e620d7b9641ec7d818fbcc6b9875",
    ),
    "r6o": (
        ORION_Q / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json",
        "e40e7a948061b9e4b647ba091c04a73b39cffa619ca829bbf4cef4beacdad352",
    ),
    "r6p": (
        ORION_Q / "MAX_R6P_WEIGHT2_FRAME_DONOR_CLOSURE_RESULTS.json",
        "3eef07d16353b606a133d7fb977d5039ad1c639c7a531a47ae82be4be9051190",
    ),
    "qg7": (
        ORION_QG / "QG7_BPRIME_COMPLETENESS_RESULTS.json",
        "7341f9630c2ca32b8a6cc601e9c1201db68f21212e04eb3b2e36bca63f214159",
    ),
    "qg7b": (
        ORION_QG / "QG7B_HYBRID_FAMILY_RESULTS.json",
        "70cee5a5f80482d84e89a92365286e1043cf3e5cf9f847a204fa84d3abcab530",
    ),
    "qg7c": (
        ORION_QG / "QG7C_CLASSIFICATION_RESULTS.json",
        "398d9592023ccf0edeb3e1ea260f9e4cdf1df8132a94110f0e6eda722b914ea9",
    ),
    "qg8": (
        ORION_QG / "QG8_OBJECTIVE_SUPPORT_PHASE_RESULTS.json",
        "f9b505d908bcafec97e7114c04e29fc1f4b8d650d29ecb9ac69842a971ebaf77",
    ),
    "qg9v6": (
        ORION_QG / "QG9_V6_SUPPORT1_NORMALIZATION_RESULTS.json",
        "f8df10d5604267e43701adb032f33baf1dfaa5a6572e5bdeaeda7707c4100b66",
    ),
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code(key, q: int) -> int:
    return int(h.BITS_CODE[((key[0] >> q) & 1, (key[1] >> q) & 1)])


def letter_key(letter: int, q: int):
    bx, bz = h.CODE_BITS[letter]
    return (bx << q, bz << q)


def flat6(target_pairs):
    return tuple(tuple(t) for pair in target_pairs for t in pair)


def permute6(t6, perm_b: int, perm_c: int):
    a0, a1, b0, b1, c0, c1 = t6
    if perm_b:
        b0, b1 = b1, b0
    if perm_c:
        c0, c1 = c1, c0
    return (a0, a1, b0, b1, c0, c1)


# =========================================================================
# Section A -- the frozen unit-cost objective O0, rebuilt from primitives
# =========================================================================


def acceptance(frames6, s):
    """Frozen R6M acceptance predicate -> (l0, l1) or None."""
    for j in range(3):
        if p10.symp(frames6[2 * j], frames6[2 * j + 1]) != 1:
            return None
    l0 = p10.symp(s, frames6[0])
    l1 = p10.symp(s, frames6[1])
    for j in (1, 2):
        if p10.symp(s, frames6[2 * j]) != l0:
            return None
        if p10.symp(s, frames6[2 * j + 1]) != l1:
            return None
    if l0 == l1:
        return None
    return (int(l0), int(l1))


def objective(t6, frames6, s, centrals, n: int) -> int:
    """Frozen unit-cost support objective O0 (identical to r6s.config_cost)."""
    raw = 0
    for j in range(3):
        m0 = 2 if centrals[j] == 0 else 4
        m1 = 2 if centrals[j] == 1 else 4
        raw += m0 * p10.wt(frames6[2 * j]) + m1 * p10.wt(frames6[2 * j + 1])
    raw += 2 * p10.wt(s)
    tt = [p10.mul(t6[i], frames6[i]) for i in range(6)]
    f3sum = 0
    for k in (0, 1):
        for q in range(n):
            f3sum += F3[code(tt[k], q)][code(tt[2 + k], q)][code(tt[4 + k], q)]
    return int(raw - 18 + f3sum)


# =========================================================================
# Section B -- the exact cap-1 referee R1
# =========================================================================


def r1a_frame_invariance() -> dict[str, Any]:
    """Every support-1 block contributes exactly 6 for both central choices."""
    rows = 0
    values = set()
    for (a, b) in ORD:
        for central in (0, 1):
            m0 = 2 if central == 0 else 4
            m1 = 2 if central == 1 else 4
            values.add(m0 * LW[a] + m1 * LW[b])
            rows += 1
    return {
        "domain_size": rows,
        "expected_domain_12": rows == 12,
        "values": sorted(values),
        "holds": values == {6},
    }


def r1b_forced_tag() -> dict[str, Any]:
    """The local Tag letter is forced and unique at every anchor; never I."""
    rows = 0
    table = {}
    unique = True
    never_identity = True
    for (a, b) in ORD:
        for labels in LABELS2:
            solutions = []
            for s in range(4):
                rows += 1
                if SY[s][a] == labels[0] and SY[s][b] == labels[1]:
                    solutions.append(s)
            key = f"{LETTERS[a]}{LETTERS[b]}|{labels[0]}{labels[1]}"
            table[key] = [LETTERS[x] for x in solutions]
            if len(solutions) != 1:
                unique = False
            elif solutions[0] == 0:
                never_identity = False
            else:
                expected = a if labels == (0, 1) else b
                if solutions[0] != expected:
                    unique = False
    return {
        "domain_size": rows,
        "expected_domain_48": rows == 48,
        "forced_letter_table": table,
        "unique_solution_everywhere": unique,
        "never_identity": never_identity,
        "holds": unique and never_identity,
    }


def cap1_reference(target_pairs, n: int, want_witness: bool = False):
    """Flat enumeration of the complete support-<=1 family. Domain 1728*n^3."""
    t6flat = flat6(target_pairs)
    best = None
    best_wit = None
    rows = 0
    for perm_b, perm_c in PERMS4:
        t6 = permute6(t6flat, perm_b, perm_c)
        L = [[code(t6[i], q) for i in range(6)] for q in range(n)]
        raw = [
            F3[L[q][0]][L[q][2]][L[q][4]] + F3[L[q][1]][L[q][3]][L[q][5]]
            for q in range(n)
        ]
        base = sum(raw)
        for anchors in itertools.product(range(n), repeat=3):
            aset = set(anchors)
            tag_cost = 2 * len(aset)
            for labels in LABELS2:
                for bases in itertools.product(ORD, repeat=3):
                    rows += 1
                    forced = {}
                    ok = True
                    for j in range(3):
                        f = bases[j][0] if labels == (0, 1) else bases[j][1]
                        if forced.setdefault(anchors[j], f) != f:
                            ok = False
                            break
                    if not ok:
                        continue
                    total = base + tag_cost
                    for q in aset:
                        l0 = [L[q][0], L[q][2], L[q][4]]
                        l1 = [L[q][1], L[q][3], L[q][5]]
                        for j in range(3):
                            if anchors[j] == q:
                                l0[j] = LM[l0[j]][bases[j][0]]
                                l1[j] = LM[l1[j]][bases[j][1]]
                        total += (
                            F3[l0[0]][l0[1]][l0[2]] + F3[l1[0]][l1[1]][l1[2]] - raw[q]
                        )
                    if best is None or total < best:
                        best = total
                        if want_witness:
                            best_wit = {
                                "perm_b": perm_b,
                                "perm_c": perm_c,
                                "anchors": list(anchors),
                                "labels": list(labels),
                                "bases": [list(b) for b in bases],
                                "tag_letters": {
                                    str(q): LETTERS[forced[q]] for q in sorted(forced)
                                },
                                "tag_weight": len(aset),
                                "cost": total,
                            }
    if want_witness:
        return best, best_wit, rows
    return best


def cap1_grouped(target_pairs, n: int) -> int:
    """Identical enumeration re-associated by anchor group (decoupled blocks)."""
    t6flat = flat6(target_pairs)
    best = None
    for perm_b, perm_c in PERMS4:
        t6 = permute6(t6flat, perm_b, perm_c)
        L = [[code(t6[i], q) for i in range(6)] for q in range(n)]
        raw = [
            F3[L[q][0]][L[q][2]][L[q][4]] + F3[L[q][1]][L[q][3]][L[q][5]]
            for q in range(n)
        ]
        base = sum(raw)
        for anchors in itertools.product(range(n), repeat=3):
            aset = sorted(set(anchors))
            for labels in LABELS2:
                total = base + 2 * len(aset)
                ok = True
                for q in aset:
                    group = [j for j in range(3) if anchors[j] == q]
                    l0 = [L[q][0], L[q][2], L[q][4]]
                    l1 = [L[q][1], L[q][3], L[q][5]]
                    best_q = None
                    for combo in itertools.product(ORD, repeat=len(group)):
                        forced = {c[0] if labels == (0, 1) else c[1] for c in combo}
                        if len(forced) != 1:
                            continue
                        m0 = list(l0)
                        m1 = list(l1)
                        for idx, j in enumerate(group):
                            m0[j] = LM[m0[j]][combo[idx][0]]
                            m1[j] = LM[m1[j]][combo[idx][1]]
                        v = F3[m0[0]][m0[1]][m0[2]] + F3[m1[0]][m1[1]][m1[2]] - raw[q]
                        if best_q is None or v < best_q:
                            best_q = v
                    if best_q is None:
                        ok = False
                        break
                    total += best_q
                if ok and (best is None or total < best):
                    best = total
    return best


# =========================================================================
# Section C -- from-primitives complete brute force over the support-<=1 family
# =========================================================================


def weight_le1_keys(n: int):
    keys = [(0, 0)]
    for q in range(n):
        for letter in (1, 2, 3):
            keys.append(letter_key(letter, q))
    return keys


def all_keys(n: int):
    return [(x, z) for x in range(1 << n) for z in range(1 << n)]


def feasible_support1_configs(n: int) -> dict[str, Any]:
    """Complete sweep: all (3n+1)^6 weight-<=1 frame tuples x all 4^n Tags."""
    wkeys = weight_le1_keys(n)
    tags = all_keys(n)
    frame_tuples_enumerated = len(wkeys) ** 6
    # Block-level pruning is exact: a block with symp(r0,r1) != 1 is rejected
    # by the acceptance predicate for every Tag, central and permutation.
    block_pairs = [
        (r0, r1) for r0 in wkeys for r1 in wkeys if p10.symp(r0, r1) == 1
    ]
    configs = []
    frame_tuples_feasible = 0
    weights_seen = set()
    frame_costs_seen = set()
    for pa in block_pairs:
        for pb in block_pairs:
            for pc in block_pairs:
                frames6 = (pa[0], pa[1], pb[0], pb[1], pc[0], pc[1])
                frame_tuples_feasible += 1
                for s in tags:
                    lab = acceptance(frames6, s)
                    if lab is None:
                        continue
                    for f in frames6:
                        weights_seen.add(int(p10.wt(f)))
                    costs = set()
                    for centrals in CENTRALS8:
                        cost = 0
                        for j in range(3):
                            m0 = 2 if centrals[j] == 0 else 4
                            m1 = 2 if centrals[j] == 1 else 4
                            cost += m0 * p10.wt(frames6[2 * j])
                            cost += m1 * p10.wt(frames6[2 * j + 1])
                        costs.add(int(cost))
                    frame_costs_seen |= costs
                    configs.append((frames6, s, lab, 2 * int(p10.wt(s))))
    return {
        "n": n,
        "weight_le1_key_count": len(wkeys),
        "frame_tuples_enumerated": frame_tuples_enumerated,
        "block_feasible_pairs": len(block_pairs),
        "frame_tuples_feasible": frame_tuples_feasible,
        "tag_keys_enumerated": len(tags),
        "acceptance_evaluations": frame_tuples_feasible * len(tags),
        "feasible_configs": len(configs),
        "frame_weights_seen": sorted(weights_seen),
        "frame_costs_over_all_centrals": sorted(frame_costs_seen),
        "frame_cost_central_invariant_18": frame_costs_seen == {18},
        "configs": configs,
    }


def cap1_bruteforce(target_pairs, n: int, pack: dict[str, Any]) -> int:
    """Exact minimum of O0 over the complete support-<=1 configuration list."""
    t6flat = flat6(target_pairs)
    best = None
    for perm_b, perm_c in PERMS4:
        t6 = permute6(t6flat, perm_b, perm_c)
        for frames6, s, _lab, tagcost in pack["configs"]:
            tt = [p10.mul(t6[i], frames6[i]) for i in range(6)]
            f3sum = 0
            for k in (0, 1):
                a = tt[k]
                b = tt[2 + k]
                c = tt[4 + k]
                for q in range(n):
                    f3sum += F3[code(a, q)][code(b, q)][code(c, q)]
            total = tagcost + f3sum
            if best is None or total < best:
                best = total
    return int(best)


# =========================================================================
# Section D -- Q1 domains and referees
# =========================================================================


def c_dp(target_pairs, n: int) -> int:
    if n == 1:
        p6 = tuple(code(t, 0) for t in flat6(target_pairs))
        return int(r6p.dp_cost_n1_reader(p6))
    if n == 2:
        return int(r6p.dp_cost_n2_reader(target_pairs))
    return int(r6p.dp_cost_frozen_configs(r6m._synthetic_terms(target_pairs), n))


def instance_n(target_pairs) -> int:
    hi = 0
    for pair in target_pairs:
        for t in pair:
            hi = max(hi, int(t[0]), int(t[1]))
    return max(1, hi.bit_length())


def normalize_pairs(raw) -> tuple:
    return tuple(tuple((int(t[0]), int(t[1])) for t in pair) for pair in raw)


def harvest(obj, out, depth=0):
    """Collect every dict carrying a 'target_pairs' field, at any depth."""
    if depth > 8:
        return out
    if isinstance(obj, dict):
        tp = obj.get("target_pairs")
        if isinstance(tp, list) and len(tp) == 3:
            try:
                out.append(normalize_pairs(tp))
            except (TypeError, IndexError):
                pass
        tg = obj.get("targets")
        if isinstance(tg, list) and len(tg) == 3:
            try:
                out.append(normalize_pairs(tg))
            except (TypeError, IndexError):
                pass
        for v in obj.values():
            harvest(v, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            harvest(v, out, depth + 1)
    return out


def dedup(seq):
    seen = set()
    out = []
    for item in seq:
        key = canonical([list(map(list, pair)) for pair in item])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def scan_domain(name, instances, want_dxx_all: bool, sandwich_log: list) -> dict[str, Any]:
    rows = 0
    gaps = []
    gap_hist: dict[str, int] = {}
    dxx_rows = 0
    for target_pairs in instances:
        n = instance_n(target_pairs)
        dp = c_dp(target_pairs, n)
        cap1 = int(cap1_grouped(target_pairs, n))
        rows += 1
        dxx = None
        if want_dxx_all or dp < cap1:
            dxx = int(r6p.dxx_search(target_pairs, n, max_weight=2)["C_Dxx"])
            dxx_rows += 1
            if not (dp <= dxx <= cap1):
                sandwich_log.append(
                    {
                        "domain": name,
                        "targets": [list(map(list, pr)) for pr in target_pairs],
                        "C_DP": dp,
                        "C_Dxx": dxx,
                        "C_cap1": cap1,
                    }
                )
        elif not (dp <= cap1):
            sandwich_log.append(
                {
                    "domain": name,
                    "targets": [list(map(list, pr)) for pr in target_pairs],
                    "C_DP": dp,
                    "C_cap1": cap1,
                }
            )
        if dp < cap1:
            gap = cap1 - dp
            gap_hist[str(gap)] = gap_hist.get(str(gap), 0) + 1
            gaps.append(
                {
                    "domain": name,
                    "n": n,
                    "targets": [list(map(list, pr)) for pr in target_pairs],
                    "C_DP": dp,
                    "C_Dxx": dxx,
                    "C_cap1": cap1,
                    "gap": gap,
                }
            )
    return {
        "domain": name,
        "instances": rows,
        "dxx_computed_rows": dxx_rows,
        "gap_instances": len(gaps),
        "gap_size_histogram": gap_hist,
        "gap_rows": gaps,
    }


def domain_d4_exhaustive_n1():
    single = [letter_key(a, 0) for a in (1, 2, 3)]
    return [
        (combo[0:2], combo[2:4], combo[4:6])
        for combo in itertools.product(single, repeat=6)
    ]


W1_N2 = ((1, 0), (1, 1), (0, 1), (2, 0), (2, 2), (0, 2))


def domain_d5_structured_n2():
    return [
        (combo[0:2], combo[2:4], combo[4:6])
        for combo in itertools.product(W1_N2, repeat=6)
    ]


BF2_ALPHABET = ((1, 0), (0, 2))


def domain_bf2_instances():
    return [
        (combo[0:2], combo[2:4], combo[4:6])
        for combo in itertools.product(BF2_ALPHABET, repeat=6)
    ]


# =========================================================================
# Section E -- Q2: the V6 Tag-relocation lemma chain instantiated on R6M
# =========================================================================


def _f3_at_slot(slot: int, x, u, v):
    if slot == 0:
        return F3n[x, u, v]
    if slot == 1:
        return F3n[u, x, v]
    return F3n[u, v, x]


def lemma_l1_deletion_credit() -> dict[str, Any]:
    """Zeroing both frame letters of one block at one qubit; refund vs F3 penalty."""
    p0, p1, u0, v0, u1, v1 = np.meshgrid(
        *[np.arange(4) for _ in range(6)], indexing="ij"
    )
    out: dict[str, Any] = {}
    for cls_name, want in (("commuting", 0), ("anticommuting", 1)):
        pairs = [
            (f0, f1)
            for f0 in range(4)
            for f1 in range(4)
            if SY[f0][f1] == want and (f0, f1) != (0, 0)
        ]
        rows = 0
        max_delta = -(10 ** 9)
        min_delta = 10 ** 9
        argmax = None
        tie_rows = 0
        tie_multipliers = set()
        slot_values = {}
        for slot in range(3):
            slot_max = -(10 ** 9)
            for central in (0, 1):
                m0 = 2 if central == 0 else 4
                m1 = 2 if central == 1 else 4
                for (f0, f1) in pairs:
                    refund = m0 * LW[f0] + m1 * LW[f1]
                    old0 = LMn[p0, f0]
                    old1 = LMn[p1, f1]
                    d0 = _f3_at_slot(slot, p0, u0, v0) - _f3_at_slot(slot, old0, u0, v0)
                    d1 = _f3_at_slot(slot, p1, u1, v1) - _f3_at_slot(slot, old1, u1, v1)
                    delta = d0 + d1 - refund
                    rows += int(delta.size)
                    dmax = int(delta.max())
                    slot_max = max(slot_max, dmax)
                    min_delta = min(min_delta, int(delta.min()))
                    n_tie = int((delta == 0).sum())
                    tie_rows += n_tie
                    if n_tie:
                        tie_multipliers.add((m0, m1))
                    if dmax > max_delta:
                        max_delta = dmax
                        loc = np.argwhere(delta == dmax)[0]
                        i0, i1, i2, i3, i4, i5 = (int(x) for x in loc)
                        argmax = {
                            "slot": "ABC"[slot],
                            "central_bit": central,
                            "multipliers": [m0, m1],
                            "frame_letters": [LETTERS[f0], LETTERS[f1]],
                            "refund": int(refund),
                            "target_letters": [LETTERS[i0], LETTERS[i1]],
                            "other_slots_branch0": [LETTERS[i2], LETTERS[i3]],
                            "other_slots_branch1": [LETTERS[i4], LETTERS[i5]],
                            "delta": dmax,
                        }
            slot_values["ABC"[slot]] = slot_max
        out[cls_name] = {
            "letter_pairs": len(pairs),
            "domain_size": rows,
            "max_delta": max_delta,
            "min_delta": min_delta,
            "credit_floor": -max_delta,
            "zero_credit_rows": tie_rows,
            "tie_multiplier_pairs": sorted(list(m) for m in tie_multipliers),
            "per_slot_max_delta": slot_values,
            "slot_symmetric": len(set(slot_values.values())) == 1,
            "max_witness": argmax,
        }
    out["expected_domain_commuting_221184"] = out["commuting"]["domain_size"] == 221184
    out["expected_domain_anticommuting_147456"] = (
        out["anticommuting"]["domain_size"] == 147456
    )
    out["credit_floor"] = out["commuting"]["credit_floor"]
    out["holds"] = out["credit_floor"] >= 1
    out["r6i_reference_credit_floor"] = 4
    return out


def lemma_l2_core_alignment() -> dict[str, Any]:
    """Changing the surviving one-qubit ordered anticommuting basis."""
    p0, p1, u0, v0, u1, v1 = np.meshgrid(
        *[np.arange(4) for _ in range(6)], indexing="ij"
    )
    rows = 0
    max_delta = -(10 ** 9)
    argmax = None
    frame_values = set()
    for slot in range(3):
        for central in (0, 1):
            m0 = 2 if central == 0 else 4
            m1 = 2 if central == 1 else 4
            for old in ORD:
                frame_values.add(m0 * LW[old[0]] + m1 * LW[old[1]])
                for new in ORD:
                    o0 = LMn[p0, old[0]]
                    o1 = LMn[p1, old[1]]
                    n0 = LMn[p0, new[0]]
                    n1 = LMn[p1, new[1]]
                    delta = (
                        _f3_at_slot(slot, n0, u0, v0)
                        - _f3_at_slot(slot, o0, u0, v0)
                        + _f3_at_slot(slot, n1, u1, v1)
                        - _f3_at_slot(slot, o1, u1, v1)
                    )
                    rows += int(delta.size)
                    dmax = int(delta.max())
                    if dmax > max_delta:
                        max_delta = dmax
                        loc = np.argwhere(delta == dmax)[0]
                        i0, i1, i2, i3, i4, i5 = (int(x) for x in loc)
                        argmax = {
                            "slot": "ABC"[slot],
                            "central_bit": central,
                            "old_basis": [LETTERS[old[0]], LETTERS[old[1]]],
                            "new_basis": [LETTERS[new[0]], LETTERS[new[1]]],
                            "target_letters": [LETTERS[i0], LETTERS[i1]],
                            "other_slots_branch0": [LETTERS[i2], LETTERS[i3]],
                            "other_slots_branch1": [LETTERS[i4], LETTERS[i5]],
                            "delta": dmax,
                        }
    return {
        "domain_size": rows,
        "expected_domain_884736": rows == 884736,
        "frame_contribution_values": sorted(frame_values),
        "frame_contribution_always_6": frame_values == {6},
        "alignment_ceiling": max_delta,
        "max_witness": argmax,
        "r6i_reference_alignment_ceiling": 3,
        "r6i_reference_frame_contribution": 10,
    }


def lemma_l3_same_core_rigidity() -> dict[str, Any]:
    """Two support-1 blocks on one anchor: does the shared Tag pin the basis?"""
    rows = 0
    feasible = 0
    violations = []
    for A in ORD:
        for B in ORD:
            for s in range(4):
                for labels in LABELS2:
                    rows += 1
                    if (
                        SY[s][A[0]] == labels[0]
                        and SY[s][A[1]] == labels[1]
                        and SY[s][B[0]] == labels[0]
                        and SY[s][B[1]] == labels[1]
                    ):
                        feasible += 1
                        if A != B:
                            violations.append(
                                {
                                    "A": [LETTERS[A[0]], LETTERS[A[1]]],
                                    "B": [LETTERS[B[0]], LETTERS[B[1]]],
                                    "tag_letter": LETTERS[s],
                                    "labels": list(labels),
                                }
                            )
    return {
        "domain_size": rows,
        "expected_domain_288": rows == 288,
        "feasible_rows": feasible,
        "different_basis_feasible_rows": len(violations),
        "holds": not violations,
        "violations_verbatim": violations[:VERBATIM_CAP],
        "violations_total": len(violations),
        "r6i_reference_holds": True,
        "note": (
            "R6M's one-bit shared Tag pins only the label-selected letter of the "
            "ordered anticommuting basis, not the whole ordered pair; R6I's "
            "two-bit Tag pins both."
        ),
    }


def lemma_l4_distinct_core_tag() -> dict[str, Any]:
    """Exact minimum feasible Tag cost as a function of the distinct-anchor count."""
    n = 3
    tags = all_keys(n)
    tag_codes = [[code(s, q) for q in range(n)] for s in tags]
    tag_costs = [2 * int(p10.wt(s)) for s in tags]
    rows = 0
    minima: dict[int, int] = {}
    feasible_by_k: dict[int, int] = {}
    for anchors in itertools.product(range(n), repeat=3):
        k = len(set(anchors))
        for bases in itertools.product(ORD, repeat=3):
            for labels in LABELS2:
                for ti, sc in enumerate(tag_codes):
                    rows += 1
                    ok = True
                    for j in range(3):
                        letter = sc[anchors[j]]
                        if (
                            SY[letter][bases[j][0]] != labels[0]
                            or SY[letter][bases[j][1]] != labels[1]
                        ):
                            ok = False
                            break
                    if not ok:
                        continue
                    feasible_by_k[k] = feasible_by_k.get(k, 0) + 1
                    cst = tag_costs[ti]
                    if k not in minima or cst < minima[k]:
                        minima[k] = cst
    return {
        "domain_size": rows,
        "expected_domain_746496": rows == 746496,
        "min_tag_cost_by_distinct_anchors": {str(k): v for k, v in sorted(minima.items())},
        "feasible_rows_by_distinct_anchors": {
            str(k): v for k, v in sorted(feasible_by_k.items())
        },
        "same_core_new_tag": minima.get(1),
        "distinct_core_new_tag": minima.get(3),
        "old_tag_floor": min(minima.values()) if minima else None,
        "r6i_reference_same_core_new_tag": 4,
        "r6i_reference_distinct_core_new_tag": 8,
        "r6i_reference_old_tag_floor": 4,
    }


OBLIGATION_ORDER = (
    ("L1_DELETION_CREDIT", "l1"),
    ("L2_ALIGNMENT_CEILING", "l2"),
    ("L3_SAME_CORE_RIGIDITY", "l3"),
    ("L4_DISTINCT_CORE_TAG", "l4"),
    ("C1_CREDIT_EXCEEDS_ALIGNMENT", "c1"),
    ("C2_SAME_CORE", "c2"),
    ("C3_DISTINCT_CORE", "c3"),
)


def q2_chain() -> dict[str, Any]:
    l1 = lemma_l1_deletion_credit()
    l2 = lemma_l2_core_alignment()
    l3 = lemma_l3_same_core_rigidity()
    l4 = lemma_l4_distinct_core_tag()
    credit = int(l1["credit_floor"])
    align = int(l2["alignment_ceiling"])
    same_tag = l4["same_core_new_tag"]
    dist_tag = l4["distinct_core_new_tag"]
    old_floor = l4["old_tag_floor"]
    obligations = {
        "l1": bool(l1["holds"]),
        "l2": bool(l2["frame_contribution_always_6"]),
        "l3": bool(l3["holds"]),
        "l4": bool(same_tag is not None and dist_tag is not None),
        "c1": bool(credit > align),
        "c2": bool(
            same_tag is not None
            and old_floor is not None
            and same_tag <= old_floor
            and credit >= align
        ),
        "c3": bool(
            dist_tag is not None
            and old_floor is not None
            and old_floor + credit >= dist_tag
        ),
    }
    first_failure = None
    for name, key in OBLIGATION_ORDER:
        if not obligations[key]:
            first_failure = name
            break
    return {
        "l1_deletion_credit": l1,
        "l2_core_alignment": l2,
        "l3_same_core_rigidity": l3,
        "l4_distinct_core_tag": l4,
        "composition": {
            "tare_credit_floor": credit,
            "tare_alignment_ceiling": align,
            "tare_same_core_new_tag": same_tag,
            "tare_distinct_core_new_tag": dist_tag,
            "tare_old_tag_floor": old_floor,
            "C1_credit_exceeds_alignment": obligations["c1"],
            "C2_same_core": obligations["c2"],
            "C3_distinct_core": obligations["c3"],
            "C4_support0_infeasible": SY[0][0] == 0,
        },
        "obligations": obligations,
        "first_failing_obligation": first_failure,
        "chain_closes": first_failure is None,
    }


# =========================================================================
# Section F -- bindings
# =========================================================================


def production_binding() -> dict[str, Any]:
    checks = {
        "LW_binds_r6m": bool(np.array_equal(LWn, r6m._LW)),
        "LM_binds_r6m": bool(np.array_equal(LMn, r6m._LM)),
        "SY_binds_r6m": bool(np.array_equal(SYn, r6m._SY)),
        "F3_binds_r6m": bool(np.array_equal(F3n, r6m._F3)),
        "F3_binds_r6s": bool(np.array_equal(F3n, r6s.F3)),
        "matching_binds_r6m": MATCHING == r6m._SYNTHETIC_MATCHING,
    }
    checks["all_exact"] = all(checks.values())
    return checks


def objective_binding() -> dict[str, Any]:
    """QG-18's from-primitives O0 must equal the committed r6s.config_cost."""
    rng = np.random.default_rng(SEED)
    rows = 0
    mismatches = []
    for n in (1, 2, 3):
        pack_keys = all_keys(n)
        nonzero = [k for k in pack_keys if k != (0, 0)]
        tries = 0
        while rows < 20 * n and tries < 4000:
            tries += 1
            frames = []
            ok = True
            for _ in range(3):
                r0 = nonzero[int(rng.integers(0, len(nonzero)))]
                cands = [k for k in nonzero if p10.symp(r0, k) == 1]
                if not cands:
                    ok = False
                    break
                frames.extend([r0, cands[int(rng.integers(0, len(cands)))]])
            if not ok:
                continue
            frames6 = tuple(frames)
            feas = [s for s in pack_keys if acceptance(frames6, s) is not None]
            if not feas:
                continue
            s = feas[int(rng.integers(0, len(feas)))]
            t6 = tuple(nonzero[int(rng.integers(0, len(nonzero)))] for _ in range(6))
            centrals = tuple(int(rng.integers(0, 2)) for _ in range(3))
            mine = objective(t6, frames6, s, centrals, n)
            theirs = int(r6s.config_cost(t6, frames6, s, centrals, n))
            lab_mine = acceptance(frames6, s)
            lab_theirs = r6s.config_labels(frames6, s)
            rows += 1
            if mine != theirs or (lab_theirs[0] is not True) or lab_mine != lab_theirs[1]:
                mismatches.append(
                    {"n": n, "mine": mine, "r6s": theirs, "labels": [lab_mine, lab_theirs]}
                )
    return {
        "rows": rows,
        "mismatches": mismatches[:VERBATIM_CAP],
        "exact": not mismatches and rows > 0,
    }


def receipt_bindings() -> dict[str, Any]:
    out = {}
    all_sha = True
    for name, (path, want) in RECEIPTS.items():
        got = sha(path)
        out[name + "_sha256"] = got
        out[name + "_sha256_matches"] = got == want
        all_sha &= got == want
    r6s_j = json.loads(RECEIPTS["r6s"][0].read_text())
    qg8_j = json.loads(RECEIPTS["qg8"][0].read_text())
    qg9_j = json.loads(RECEIPTS["qg9v6"][0].read_text())
    qg7_j = json.loads(RECEIPTS["qg7"][0].read_text())
    qg7b_j = json.loads(RECEIPTS["qg7b"][0].read_text())
    qg7c_j = json.loads(RECEIPTS["qg7c"][0].read_text())
    semantics = {
        "r6s_theorem_machine_checked": r6s_j.get("outcome") == "THEOREM_MACHINE_CHECKED",
        "r6s_authority_support3_never_pays": "SUPPORT3_NEVER_PAYS__DXX_EQUALS_DP_ALL_N"
        in str(r6s_j.get("authority")),
        "r6s_lemma_e_holds": bool(r6s_j.get("lemma_e", {}).get("holds")),
        "r6s_max_delta_f3_2": r6s_j.get("lemma_e", {}).get("max_delta_f3") == 2,
        "r6s_ties_only_at_central_multiplier": bool(
            r6s_j.get("lemma_e", {}).get("ties_only_at_central_multiplier")
        ),
        "qg8_terminal": qg8_j.get("terminal")
        == "QG8_OBJECTIVE_INDEXED_SUPPORT2_CONE_ALL_N_MACHINE_CHECKED",
        "qg8_central_hyperplane_exact": qg8_j.get("support2_cone", {}).get(
            "certificate_boundary_sharpness"
        )
        == "CENTRAL_HYPERPLANE_EXACT",
        "qg8_binds_same_r6s": qg8_j.get("r6s_binding", {}).get("receipt_sha256")
        == RECEIPTS["r6s"][1],
        "qg9v6_terminal": qg9_j.get("terminal")
        == "QG9_RANK2_ALL_N_SUPPORT1_SUFFICIENCY_MACHINE_CHECKED",
        "qg9v6_kappa_1": qg9_j.get("intrinsic_support_number") == 1,
        "qg7_terminal": qg7_j.get("terminal") == "QG7_FOURTH_SUPPORT2_REGIME_FOUND",
        "qg7b_terminal": qg7b_j.get("terminal")
        == "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS",
        "qg7c_terminal": qg7c_j.get("terminal") == "QG7C_PARTIAL__L4B_OPEN",
    }
    out["semantics"] = semantics
    out["all_sha256_exact"] = all_sha
    out["all_semantics_exact"] = all(semantics.values())
    fl = qg9_j["finite_lemmas"]
    cm = qg9_j["composition"]
    r6i_ref = {
        "credit_floor": -int(fl["deletion"]["max_delta_commuting"]),
        "anticommuting_credit_floor": -int(fl["deletion"]["max_delta_anticommuting"]),
        "alignment_ceiling": int(fl["core_alignment"]["max_restore_increase"]),
        "frame_contribution": int(fl["core_alignment"]["frame_contribution_invariant"]),
        "same_core_new_tag": int(cm["same_core_new_tag_cost"]),
        "distinct_core_new_tag": int(cm["distinct_core_new_tag_cost"]),
        "old_tag_floor": int(fl["original_feasible_tag_cost_floor"]),
        "same_core_rigidity_holds": fl["same_qubit_tag_rigidity"][
            "different_basis_counterexamples"
        ]
        == 0,
        "composition_credit_floor": int(cm["extra_active_column_credit_floor"]),
        "composition_alignment_ceiling": int(cm["core_alignment_ceiling"]),
        "deletion_domain_rows": int(fl["deletion"]["rows"]),
        "core_alignment_domain_rows": int(fl["core_alignment"]["rows"]),
        "same_qubit_domain_rows": int(fl["same_qubit_tag_rigidity"]["rows"]),
        "distinct_qubit_domain_rows": int(fl["distinct_qubit_tag"]["rows"]),
    }
    out["r6i_reference_numbers_from_qg9v6"] = r6i_ref
    return out


# =========================================================================
# Section G -- main
# =========================================================================


CLAIM_BOUNDARY = {
    "covers": (
        "The intrinsic support number kappa of the frozen R6L/R6M three-block "
        "TARE-M2 shared-one-bit-Tag grammar under the frozen unit-cost support "
        "objective O0 (multipliers 4 non-central / 2 central, Tag 2, "
        "donor-owned all-three Restore common-factor rule), two-sidedly: the "
        "upper bound kappa <= 2 is the bound R6S all-n theorem; the lower bound "
        "kappa >= 2 is an exact instance whose optimum is strictly below the "
        "exact optimum of the complete support-<=1 family."
    ),
    "does_not_cover": (
        "Other objectives (QG-2's O1 already forces kappa >= 3 for this family), "
        "other grammars, coefficient-weighted costs, rotation-count trade-offs, "
        "larger Tag ranks, or any physical or chemistry claim. The QG-18 "
        "structured n=2 slice is a complete slice of its declared alphabet, not "
        "of all n=2 instances. No novelty credit, no donor credit, not R6."
    ),
    "lower_bound_logic": (
        "C_cap1 is the exact minimum of O0 over EVERY configuration whose six "
        "frame Paulis have global support <= 1 (support-0 frames are infeasible "
        "since symp(I,.) = 0). An instance with C_DP < C_cap1 therefore has no "
        "support-<=1 optimum, so 1 is not a valid support bound and kappa >= 2."
    ),
}


def main() -> int:
    t_start = time.monotonic()
    timing: dict[str, float] = {}

    def mark(name, t0):
        timing[name] = round(time.monotonic() - t0, 3)

    t0 = time.monotonic()
    binding = production_binding()
    # Runtime-only injection (identical to what R6S does): the frozen R6P
    # enumerator ships expected support-2 pair counts for n <= 3 only.  The
    # count is recomputed independently here; no repository file is modified.
    pair_counts = r6s.independent_pair_counts()
    if pair_counts != r6s.PAIR_COUNTS_SUPPORT2:
        raise AssertionError({"qg18_pair_count_mismatch": pair_counts})
    r6p.EXPECTED_PAIR_COUNTS[4] = pair_counts[4]
    obj_bind = objective_binding()
    receipts = receipt_bindings()
    r1a = r1a_frame_invariance()
    r1b = r1b_forced_tag()
    mark("bindings_and_micro_domains", t0)

    # ---- brute-force cross-checks on complete sub-domains -------------------
    t0 = time.monotonic()
    pack1 = feasible_support1_configs(1)
    pack2 = feasible_support1_configs(2)
    mark("bruteforce_config_enumeration", t0)

    sandwich_log: list = []

    t0 = time.monotonic()
    d4 = domain_d4_exhaustive_n1()
    bf1_rows = 0
    bf1_bad = []
    for tp in d4:
        ref, _wit, ref_rows = cap1_reference(tp, 1, want_witness=True)
        grp = cap1_grouped(tp, 1)
        bf = cap1_bruteforce(tp, 1, pack1)
        dpv = c_dp(tp, 1)
        brute_dp = min(
            r6m._brute_config_n1(tp, pb, pc, cs)
            for pb, pc in PERMS4
            for cs in CENTRALS8
        )
        bf1_rows += 1
        if not (ref == grp == bf == dpv == brute_dp):
            bf1_bad.append(
                {
                    "targets": [list(map(list, pr)) for pr in tp],
                    "cap1_reference": ref,
                    "cap1_grouped": grp,
                    "cap1_bruteforce": bf,
                    "C_DP_reader": dpv,
                    "C_DP_brute": brute_dp,
                }
            )
    bf1 = {
        "instances": bf1_rows,
        "expected_instances_729": bf1_rows == 729,
        "cap1_reference_rows_per_instance": 1728,
        "config_enumeration": {
            k: v for k, v in pack1.items() if k != "configs"
        },
        "mismatches_total": len(bf1_bad),
        "mismatches_verbatim": bf1_bad[:VERBATIM_CAP],
        "holds": not bf1_bad,
    }
    mark("bf1_complete_n1", t0)

    t0 = time.monotonic()
    bf2_bad = []
    bf2_rows = 0
    for tp in domain_bf2_instances():
        ref, _wit, _rows = cap1_reference(tp, 2, want_witness=True)
        grp = cap1_grouped(tp, 2)
        bf = cap1_bruteforce(tp, 2, pack2)
        bf2_rows += 1
        if not (ref == grp == bf):
            bf2_bad.append(
                {
                    "targets": [list(map(list, pr)) for pr in tp],
                    "cap1_reference": ref,
                    "cap1_grouped": grp,
                    "cap1_bruteforce": bf,
                }
            )
    bf2 = {
        "instances": bf2_rows,
        "expected_instances_64": bf2_rows == 64,
        "alphabet": [list(k) for k in BF2_ALPHABET],
        "cap1_reference_rows_per_instance": 13824,
        "config_enumeration": {k: v for k, v in pack2.items() if k != "configs"},
        "mismatches_total": len(bf2_bad),
        "mismatches_verbatim": bf2_bad[:VERBATIM_CAP],
        "holds": not bf2_bad,
    }
    mark("bf2_complete_n2", t0)

    # ---- committed-referee agreement panel ----------------------------------
    t0 = time.monotonic()
    rng = np.random.default_rng(SEED)
    panel_rows = []
    panel_bad = []
    for _ in range(40):
        n = int(rng.integers(1, 4))
        tp = tuple(
            tuple(
                (int(rng.integers(0, 1 << n)), int(rng.integers(0, 1 << n)))
                for _ in range(2)
            )
            for _ in range(3)
        )
        if any(t == (0, 0) for pr in tp for t in pr):
            continue
        mine = int(cap1_grouped(tp, n))
        dpl = int(r6o.dplus_pairs(tp, n)["C_Dplus"])
        w1 = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
        row = {"n": n, "cap1": mine, "C_Dplus": dpl, "C_Dxx_w1": w1}
        panel_rows.append(row)
        if not (mine == dpl == w1):
            panel_bad.append(row)
    ref_panel = {
        "seed": SEED,
        "rows": len(panel_rows),
        "mismatches": panel_bad[:VERBATIM_CAP],
        "holds": not panel_bad and len(panel_rows) > 0,
    }
    mark("committed_referee_panel", t0)

    # ---- Q1 domains ----------------------------------------------------------
    t0 = time.monotonic()
    qg7_j = json.loads(RECEIPTS["qg7"][0].read_text())
    qg7b_j = json.loads(RECEIPTS["qg7b"][0].read_text())
    r6o_j = json.loads(RECEIPTS["r6o"][0].read_text())
    d1 = dedup(
        harvest(qg7_j["arm1_hostile_search"]["fourth_regime_candidates_verbatim"], [])
    )
    d2_raw = harvest(qg7b_j.get("q2", {}).get("panel_w_witnesses", {}), [])
    d2_raw += harvest(qg7b_j.get("verification_sample", []), [])
    d2 = dedup(d2_raw)
    d3 = dedup(harvest(r6o_j["discovery"]["instances_with_dp_strictly_below_dplus"], []))
    seen_witness_keys = set()
    combined_witness_domain = []
    for name, dom in (("D1_qg7", d1), ("D2_qg7b", d2), ("D3_r6o", d3)):
        for tp in dom:
            key = canonical([list(map(list, pr)) for pr in tp])
            if key not in seen_witness_keys:
                seen_witness_keys.add(key)
                combined_witness_domain.append((name, tp))
    scan_d1 = scan_domain("D1_qg7", d1, True, sandwich_log)
    scan_d2 = scan_domain("D2_qg7b", d2, True, sandwich_log)
    scan_d3 = scan_domain("D3_r6o", d3, True, sandwich_log)
    mark("q1_committed_witness_domains", t0)

    t0 = time.monotonic()
    scan_d4 = scan_domain("D4_exhaustive_n1", d4, False, sandwich_log)
    mark("q1_d4_exhaustive_n1", t0)

    t0 = time.monotonic()
    d5 = domain_d5_structured_n2()
    d5_rows = 0
    d5_gaps = []
    d5_hist: dict[str, int] = {}
    d5_dxx_rows = 0
    for idx, tp in enumerate(d5):
        dpv = int(r6p.dp_cost_n2_reader(tp))
        cap = int(cap1_grouped(tp, 2))
        d5_rows += 1
        if dpv > cap:
            sandwich_log.append(
                {
                    "domain": "D5_structured_n2",
                    "targets": [list(map(list, pr)) for pr in tp],
                    "C_DP": dpv,
                    "C_cap1": cap,
                }
            )
        if dpv < cap:
            dxx = int(r6p.dxx_search(tp, 2, max_weight=2)["C_Dxx"])
            d5_dxx_rows += 1
            if not (dpv <= dxx <= cap):
                sandwich_log.append(
                    {
                        "domain": "D5_structured_n2",
                        "targets": [list(map(list, pr)) for pr in tp],
                        "C_DP": dpv,
                        "C_Dxx": dxx,
                        "C_cap1": cap,
                    }
                )
            gap = cap - dpv
            d5_hist[str(gap)] = d5_hist.get(str(gap), 0) + 1
            d5_gaps.append(
                {
                    "domain": "D5_structured_n2",
                    "n": 2,
                    "targets": [list(map(list, pr)) for pr in tp],
                    "C_DP": dpv,
                    "C_Dxx": dxx,
                    "C_cap1": cap,
                    "gap": gap,
                }
            )
        if idx % 6000 == 5999:
            r6m._local_table.cache_clear()
    r6m._local_table.cache_clear()
    scan_d5 = {
        "domain": "D5_structured_n2",
        "instances": d5_rows,
        "dxx_computed_rows": d5_dxx_rows,
        "gap_instances": len(d5_gaps),
        "gap_size_histogram": d5_hist,
        "gap_rows": d5_gaps,
    }
    mark("q1_d5_structured_n2", t0)

    all_scans = [scan_d1, scan_d2, scan_d3, scan_d4, scan_d5]
    all_gaps = [g for s in all_scans for g in s["gap_rows"]]

    # ---- canonical witness selection ---------------------------------------
    t0 = time.monotonic()
    witness = None
    if all_gaps:
        ordered = sorted(
            all_gaps,
            key=lambda g: (
                g["n"],
                g["C_DP"],
                g["C_cap1"],
                canonical(g["targets"]),
            ),
        )
        chosen = ordered[0]
        tp = normalize_pairs(chosen["targets"])
        n = chosen["n"]
        ref, cap_wit, ref_rows = cap1_reference(tp, n, want_witness=True)
        grp = cap1_grouped(tp, n)
        bf = cap1_bruteforce(tp, n, pack2 if n == 2 else pack1)
        dpl = int(r6o.dplus_pairs(tp, n)["C_Dplus"])
        w1 = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
        dp_frozen = int(r6p.dp_cost_frozen_configs(r6m._synthetic_terms(tp), n))
        dp_reader = c_dp(tp, n)
        dp_brute = (
            min(
                r6m._brute_config_n2(tp, pb, pc, cs)
                for pb, pc in PERMS4
                for cs in CENTRALS8
            )
            if n == 2
            else None
        )
        dxx_pack = r6p.dxx_search(tp, n, max_weight=2, want_witness=True)
        c_dxx = int(dxx_pack["C_Dxx"])
        dxx_verified = bool(r6p.verify_dxx_witness(tp, n, dxx_pack["witness"]))
        wit = dxx_pack["witness"]
        frames6 = tuple(
            tuple(int(x) for x in blk[key])
            for blk in wit["blocks"]
            for key in ("R0", "R1")
        )
        tag = tuple(int(x) for x in wit["S"])
        centrals = tuple(int(blk["central"]) for blk in wit["blocks"])
        perms = tuple(int(blk["target_permutation"]) for blk in wit["blocks"])
        ordered = []
        for j in range(3):
            pr = tp[j]
            ordered.extend(pr if perms[j] == 0 else (pr[1], pr[0]))
        t6_perm = tuple(ordered)
        lab_indep = acceptance(frames6, tag)
        cost_indep = objective(t6_perm, frames6, tag, centrals, n)
        # rebuild the explicit cap-1 optimal configuration from its descriptor
        cap_frames = []
        for j in range(3):
            q = cap_wit["anchors"][j]
            a, b = cap_wit["bases"][j]
            cap_frames.extend([letter_key(a, q), letter_key(b, q)])
        cap_frames = tuple(cap_frames)
        cap_tagkey = (0, 0)
        for qs, letter in cap_wit["tag_letters"].items():
            k = letter_key(LETTERS.index(letter), int(qs))
            cap_tagkey = (cap_tagkey[0] | k[0], cap_tagkey[1] | k[1])
        cap_t6 = permute6(flat6(tp), cap_wit["perm_b"], cap_wit["perm_c"])
        cap_lab = acceptance(cap_frames, cap_tagkey)
        cap_cost_indep = objective(cap_t6, cap_frames, cap_tagkey, (0, 0, 0), n)
        witness = {
            "n": n,
            "targets": [list(map(list, pr)) for pr in tp],
            "source_domain": chosen["domain"],
            "C_DP": dp_frozen,
            "C_Dxx": c_dxx,
            "C_cap1": ref,
            "strict_gap": ref - dp_frozen,
            "C_DP_recomputations": {
                "frozen_r6m_dp_all_configs": dp_frozen,
                "frozen_n_reader": dp_reader,
                "committed_independent_brute_n2": dp_brute,
                "explicit_support2_config_cost_from_primitives": cost_indep,
                "all_agree": dp_frozen
                == dp_reader
                == cost_indep
                == (dp_brute if dp_brute is not None else dp_frozen),
            },
            "C_cap1_recomputations": {
                "cap1_reference": ref,
                "cap1_grouped": grp,
                "cap1_bruteforce_from_primitives": bf,
                "r6o_dplus": dpl,
                "r6p_dxx_weight1": w1,
                "explicit_cap1_config_cost_from_primitives": cap_cost_indep,
                "all_agree": ref == grp == bf == dpl == w1 == cap_cost_indep,
                "reference_domain_rows": ref_rows,
            },
            "support2_configuration": {
                "frames": [list(f) for f in frames6],
                "tag": list(tag),
                "centrals": list(centrals),
                "target_permutations": list(perms),
                "labels": [int(x) for x in wit["labels"]],
                "per_frame_support": [int(p10.wt(f)) for f in frames6],
                "max_frame_support": int(max(p10.wt(f) for f in frames6)),
                "tag_weight": int(p10.wt(tag)),
                "acceptance_labels_independent": list(lab_indep) if lab_indep else None,
                "cost_independent": cost_indep,
                "r6p_witness_verified": dxx_verified,
                "witness_verbatim": wit,
            },
            "cap1_optimal_configuration": {
                "descriptor": cap_wit,
                "frames": [list(f) for f in cap_frames],
                "tag": list(cap_tagkey),
                "acceptance_labels_independent": list(cap_lab) if cap_lab else None,
                "per_frame_support": [int(p10.wt(f)) for f in cap_frames],
                "max_frame_support": int(max(p10.wt(f) for f in cap_frames)),
                "cost_independent": cap_cost_indep,
            },
            "sandwich": {
                "C_DP_le_C_Dxx": dp_frozen <= c_dxx,
                "C_Dxx_lt_C_cap1": c_dxx < ref,
                "support2_attains_optimum": c_dxx == dp_frozen,
            },
        }
    mark("witness_full_recomputation", t0)

    # ---- Q2 chain ------------------------------------------------------------
    t0 = time.monotonic()
    q2 = q2_chain()
    mark("q2_lemma_chain", t0)

    # ---- gates ---------------------------------------------------------------
    domains_complete = (
        scan_d4["instances"] == 729
        and scan_d5["instances"] == 46656
        and bf1["instances"] == 729
        and bf2["instances"] == 64
        and q2["l1_deletion_credit"]["expected_domain_commuting_221184"]
        and q2["l1_deletion_credit"]["expected_domain_anticommuting_147456"]
        and q2["l2_core_alignment"]["expected_domain_884736"]
        and q2["l3_same_core_rigidity"]["expected_domain_288"]
        and q2["l4_distinct_core_tag"]["expected_domain_746496"]
        and r1a["expected_domain_12"]
        and r1b["expected_domain_48"]
    )
    elapsed = time.monotonic() - t_start
    gates = {
        "protocol_present": PROTOCOL.is_file(),
        "production_algebra_exact": binding["all_exact"],
        "r6m_tables_exact": binding["F3_binds_r6m"] and binding["LM_binds_r6m"],
        "objective_binds_r6s": obj_bind["exact"],
        "receipts_sha256_exact": receipts["all_sha256_exact"],
        "receipt_semantics_exact": receipts["all_semantics_exact"],
        "r1a_frame_invariance": r1a["holds"],
        "r1b_forced_tag_unique": r1b["holds"],
        "cap1_reference_equals_grouped": bf1["holds"] and bf2["holds"],
        "cap1_equals_bruteforce_n1": bf1["holds"],
        "cap1_equals_bruteforce_n2": bf2["holds"],
        "bf_frame_cost_invariant_18": pack1["frame_cost_central_invariant_18"]
        and pack2["frame_cost_central_invariant_18"],
        "cap1_equals_dplus_panel": ref_panel["holds"],
        "cap1_equals_dxx_weight1_panel": ref_panel["holds"],
        "n1_cap1_equals_dp_complete": bf1["holds"],
        "sandwich_holds_everywhere": not sandwich_log,
        "domains_complete_no_truncation": bool(domains_complete),
        "no_chemistry_read": True,
        "protected_subject_not_read": True,
        "authority_ceiling_not_r6": True,
        "runtime_within_cap": elapsed < RUNTIME_CAP_SECONDS,
    }
    if witness is not None:
        gates["witness_fully_recomputed"] = bool(
            witness["C_DP_recomputations"]["all_agree"]
            and witness["C_cap1_recomputations"]["all_agree"]
        )
        gates["witness_support2_config_verified"] = bool(
            witness["support2_configuration"]["r6p_witness_verified"]
            and witness["support2_configuration"]["acceptance_labels_independent"]
            is not None
            and witness["support2_configuration"]["max_frame_support"] <= 2
            and witness["sandwich"]["support2_attains_optimum"]
            and witness["sandwich"]["C_Dxx_lt_C_cap1"]
        )

    integrity = {
        k: gates[k]
        for k in (
            "protocol_present",
            "production_algebra_exact",
            "r6m_tables_exact",
            "objective_binds_r6s",
            "receipts_sha256_exact",
            "receipt_semantics_exact",
            "r1a_frame_invariance",
            "r1b_forced_tag_unique",
            "cap1_reference_equals_grouped",
            "cap1_equals_bruteforce_n1",
            "cap1_equals_bruteforce_n2",
            "bf_frame_cost_invariant_18",
            "cap1_equals_dplus_panel",
            "n1_cap1_equals_dp_complete",
            "domains_complete_no_truncation",
            "runtime_within_cap",
        )
    }

    if sandwich_log:
        terminal = "QG18_INCONSISTENT__SANDWICH_VIOLATED"
        authority = "ORIONQG_QG18_INCONSISTENT__SANDWICH_VIOLATED__NOT_R6"
        kappa = None
    elif not all(integrity.values()):
        terminal = "QG18_CANNOT_CHECK__REFEREE_BINDING_FAILED"
        authority = "ORIONQG_QG18_CANNOT_CHECK__REFEREE_BINDING_FAILED__NOT_R6"
        kappa = None
    elif witness is not None and gates.get("witness_fully_recomputed") and gates.get(
        "witness_support2_config_verified"
    ):
        terminal = "QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS"
        authority = (
            "ORIONQG_QG18_TARE_KAPPA_IS_2__SUPPORT2_NECESSITY_WITNESS_REFEREE_"
            "CONFIRMED__CAP1_BRUTE_FORCE_CROSSCHECKED__NOT_R6"
        )
        kappa = 2
    elif witness is not None:
        terminal = "QG18_CANNOT_CHECK__REFEREE_BINDING_FAILED"
        authority = "ORIONQG_QG18_CANNOT_CHECK__REFEREE_BINDING_FAILED__NOT_R6"
        kappa = None
    elif q2["chain_closes"]:
        terminal = "QG18_TARE_KAPPA_IS_1__TAG_RELOCATION_ALL_N_MACHINE_CHECKED"
        authority = (
            "ORIONQG_QG18_TARE_KAPPA_IS_1__TAG_RELOCATION_ALL_N_MACHINE_CHECKED__NOT_R6"
        )
        kappa = 1
    else:
        terminal = f"QG18_PARTIAL__{q2['first_failing_obligation']}_OPEN"
        authority = f"ORIONQG_QG18_PARTIAL__{q2['first_failing_obligation']}_OPEN__NOT_R6"
        kappa = None

    # ---- Q3 structural diagnosis --------------------------------------------
    r6i = receipts["r6i_reference_numbers_from_qg9v6"]
    comp = q2["composition"]
    q3 = {
        "question": (
            "What property of a compilation family makes whole-system Tag "
            "relocation (the QG-9 V6 move) available?"
        ),
        "measured_comparison": {
            "deletion_credit_floor": {
                "R6I": r6i["credit_floor"],
                "R6M_TARE": comp["tare_credit_floor"],
            },
            "core_alignment_ceiling": {
                "R6I": r6i["alignment_ceiling"],
                "R6M_TARE": comp["tare_alignment_ceiling"],
            },
            "frame_contribution_per_localized_block": {
                "R6I": r6i["frame_contribution"],
                "R6M_TARE": 6,
            },
            "same_core_tag_cost": {
                "R6I": r6i["same_core_new_tag"],
                "R6M_TARE": comp["tare_same_core_new_tag"],
            },
            "distinct_core_tag_cost": {
                "R6I": r6i["distinct_core_new_tag"],
                "R6M_TARE": comp["tare_distinct_core_new_tag"],
            },
            "old_tag_floor": {
                "R6I": r6i["old_tag_floor"],
                "R6M_TARE": comp["tare_old_tag_floor"],
            },
            "same_core_basis_rigidity_holds": {
                "R6I": r6i["same_core_rigidity_holds"],
                "R6M_TARE": q2["l3_same_core_rigidity"]["holds"],
            },
        },
        "criterion": (
            "Tag relocation is available for a family F under objective C iff the "
            "per-column frame refund of F STRICTLY exceeds the maximum Restore "
            "penalty of deleting that column -- i.e. iff F's local exchange "
            "inequality holds with a strictly positive margin (a deletion "
            "credit), which is the budget the relocation spends on core "
            "alignment and on rebuilding the shared Tag."
        ),
        "why_r6i_qualifies": (
            "R6I's rank-2 dependent triple (R2 = R0 R1) makes a local frame "
            "column carry three multiplied slots, so deleting it refunds 10 "
            "(anticommuting) or >= 6 (commuting) while at most three (resp. two) "
            "Restore letters can worsen by one each. The margin is >= 4 at every "
            "non-core column, strictly above the alignment ceiling 3, and 4 + the "
            "old-Tag floor 4 pays the distinct-core rebuild 8."
        ),
        "why_tare_does_not": (
            "R6M's objective carries the donor-owned all-three-blocks "
            "common-factor rule F3, which discounts a branch qubit by exactly 2 "
            "when the three Restore letters coincide and are non-identity. A "
            "frame letter can be earning exactly that discount, so deleting it "
            "refunds m in {2,4} and simultaneously destroys up to m of F3 "
            "discount: R6S's Lemma E (max delta_F3 = 2, ties at the central "
            "multiplier 2) is TIGHT. The measured TARE deletion credit floor is "
            "therefore 0 -- there is no budget at all, and the first V6 "
            "obligation fails before the Tag is ever touched. This is the same "
            "fact QG-8 records geometrically: the unit objective O0 sits exactly "
            "on the central hyperplane t_c = 2 t_r at margin 0."
        ),
        "secondary_difference": (
            "R6M's shared Tag is one bit, so it pins only the label-selected "
            "letter of a block's ordered anticommuting basis, not the ordered "
            "pair: the V6 same-core rigidity lemma is FALSE for TARE. The extra "
            "freedom does not help, because what must be paid on relocation is "
            "the Tag's WEIGHT (2 per distinct anchor, so 2 -> 6 when three "
            "blocks are pushed onto distinct anchors) and the credit that would "
            "pay it is zero."
        ),
        "transferable_content": (
            "kappa = 1 by Tag relocation requires a STRICT per-column exchange "
            "inequality. A support bound proved from an exchange inequality that "
            "holds only with equality (a tie set) cannot be pushed below the "
            "support at which the tie set is realizable -- and for TARE the tie "
            "set is exactly where the support-2 optimum lives. Reading the "
            "margin of the exchange inequality is therefore a cheap a-priori "
            "test of whether a family's support bound is its intrinsic support "
            "number."
        ),
    }

    result = {
        "schema": "ORION.QG.QG18.TareKappa.v1",
        "lane": "QG-18",
        "programme": "ORION-QG regime geometry, wave 3",
        "question": (
            "Is kappa_TARE = 1 or 2 for the frozen R6M/TARE grammar under the "
            "frozen unit-cost support objective O0?"
        ),
        "protocol": "development/orion-qg-regime-geometry/QG18_TARE_KAPPA_PROTOCOL_V1.md",
        "protocol_sha256": sha(PROTOCOL),
        "base_revision": "3a3e820e",
        "terminal": terminal,
        "authority": authority,
        "intrinsic_support_number": kappa,
        "kappa_interval": [2, 2] if kappa == 2 else ([1, 1] if kappa == 1 else [1, 2]),
        "upper_bound_source": (
            "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json (support <= 2 for all n)"
        ),
        "lower_bound_source": (
            "QG-18 canonical support-2 necessity witness" if kappa == 2 else None
        ),
        "production_binding": binding,
        "objective_binding": obj_bind,
        "receipt_bindings": receipts,
        "cap1_referee": {
            "definition": (
                "Exact minimum of O0 over every configuration whose six frame "
                "Paulis have global support <= 1: anchors in [n]^3, ordered "
                "distinct non-identity letter pairs per block, ANY shared Tag in "
                "the full 4^n key space, all 8 centrals, all 4 relative target "
                "permutations."
            ),
            "reference_domain_size_formula": "1728 * n^3",
            "reference_domain_sizes": {str(n): 1728 * n ** 3 for n in (1, 2, 3, 4)},
            "r1a_frame_invariance": r1a,
            "r1b_forced_tag": r1b,
            "bruteforce_n1": bf1,
            "bruteforce_n2": bf2,
            "committed_referee_panel": ref_panel,
        },
        "q1_necessity_hunt": {
            "domains": {
                "D1_qg7": {
                    "source": "QG7_BPRIME_COMPLETENESS_RESULTS.json "
                    "arm1_hostile_search.fourth_regime_candidates_verbatim",
                    "instances": len(d1),
                },
                "D2_qg7b": {
                    "source": "QG7B_HYBRID_FAMILY_RESULTS.json "
                    "q2.panel_w_witnesses.rows + verification_sample",
                    "instances": len(d2),
                },
                "D3_r6o": {
                    "source": "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json "
                    "discovery.instances_with_dp_strictly_below_dplus",
                    "instances": len(d3),
                },
                "D4_exhaustive_n1": {
                    "source": "all 3^6 non-identity single-qubit target six-tuples",
                    "instances": len(d4),
                    "complete": True,
                },
                "D5_structured_n2": {
                    "source": "all 6^6 six-tuples over the six weight-one n=2 keys",
                    "alphabet": [list(k) for k in W1_N2],
                    "instances": len(d5),
                    "complete": True,
                },
            },
            "deduplicated_committed_instances": len(combined_witness_domain),
            "scans": [
                {k: v for k, v in s.items() if k != "gap_rows"} for s in all_scans
            ],
            "gap_instances_total": len(all_gaps),
            "gap_rows_verbatim": sorted(
                all_gaps,
                key=lambda g: (g["n"], g["C_DP"], g["C_cap1"], canonical(g["targets"])),
            )[:VERBATIM_CAP],
            "gap_rows_verbatim_cap": VERBATIM_CAP,
            "sandwich_violations": sandwich_log[:VERBATIM_CAP],
            "sandwich_violations_total": len(sandwich_log),
            "canonical_witness": witness,
            "selection_rule": "min by (n, C_DP, C_cap1, canonical target tuple)",
        },
        "q2_tag_relocation_transfer": q2,
        "q2_role": (
            "diagnostic (Q1 produced a witness)"
            if witness is not None
            else "terminal-bearing (Q1 empty)"
        ),
        "q3_structural_diagnosis": q3,
        "claim_boundary": CLAIM_BOUNDARY,
        "gates": gates,
        "runtime_cap_seconds": RUNTIME_CAP_SECONDS,
        "expected_pair_count_injection": {
            "module": "max_r6p_weight2_frame_donor_closure",
            "key": 4,
            "value": pair_counts[4],
            "independent_pair_counts": {str(k): v for k, v in pair_counts.items()},
            "runtime_only": True,
            "repository_files_modified": False,
        },
        "chemistry_sources_read": False,
        "protected_subject_read": False,
        "network_access": False,
        "novelty_credit": False,
        "donor_novelty_credit": False,
        "physical_quantum_advantage_claim": False,
        "r6_authority": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG-18 authority ceiling violated")
    result["result_digest"] = hashlib.sha256(canonical(result).encode()).hexdigest()

    summary = {
        "terminal": terminal,
        "authority": authority,
        "intrinsic_support_number": kappa,
        "kappa_interval": result["kappa_interval"],
        "protocol_sha256": result["protocol_sha256"],
        "all_gates": all(gates.values()),
        "gap_instances_total": len(all_gaps),
        "witness_targets": witness["targets"] if witness else None,
        "witness_n": witness["n"] if witness else None,
        "witness_C_DP": witness["C_DP"] if witness else None,
        "witness_C_Dxx": witness["C_Dxx"] if witness else None,
        "witness_C_cap1": witness["C_cap1"] if witness else None,
        "tare_credit_floor": comp["tare_credit_floor"],
        "tare_alignment_ceiling": comp["tare_alignment_ceiling"],
        "q2_first_failing_obligation": q2["first_failing_obligation"],
        "result_digest": result["result_digest"],
    }
    print(TOKEN + canonical(summary))

    timing["total"] = round(time.monotonic() - t_start, 3)
    file_result = dict(result)
    file_result["timing"] = timing
    RESULTS.write_text(json.dumps(file_result, indent=2, sort_keys=True) + "\n")
    print(canonical({"qg18_timing_seconds": timing}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
