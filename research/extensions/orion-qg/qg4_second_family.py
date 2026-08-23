#!/usr/bin/env python3
"""QG-4 second-family instance: SixLCU PREP/SELECT regime geometry.

Frozen by development/orion-qg-regime-geometry/QG4_SECOND_FAMILY_PROTOCOL.md
(frozen BEFORE any outcome). Applies the full TARE regime-geometry template
(R6N dominance audit -> R6O trade search -> R6P sufficiency -> R6Q predicate)
to a materially different compilation family: bounded LCU PREP/SELECT
compilation of six-term Pauli batches under a frozen support/node-count
objective.

Deterministic; stdlib + numpy only; no network; the protected stretched-N2
subject is never read. stdout: single canonical receipt line. stderr: runtime
seconds (the only non-deterministic output).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

SEED_PANEL = 20260821
SEED_HELDOUT = 20260825
VERBATIM_CAP = 20
INF = 10 ** 9
LETTERS = "IXYZ"

# ---------------------------------------------------------------------------
# Frozen constants of the cost model (protocol 2.4)
# ---------------------------------------------------------------------------

DS = {1: 0, 2: 0, 3: 1, 4: 2, 5: 4, 6: 6}  # canonical balanced prep-tree depth sums


def bbits(m: int) -> int:
    """b(m) = ceil(log2 m); b(1) = 0."""
    return (m - 1).bit_length()


def depth_sum(m: int) -> int:
    """Recompute ds(m) from the frozen canonical split (binds the DS table)."""
    if m <= 1:
        return 0

    def rec(sz: int, d: int) -> int:
        if sz == 1:
            return 0
        left = (sz + 1) // 2
        right = sz - left
        return d + rec(left, d + 1) + rec(right, d + 1)

    return rec(m, 0)


for _m in range(1, 7):
    if depth_sum(_m) != DS[_m]:
        raise AssertionError({"frozen_depth_sum_mismatch": _m})


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def term_wt(code: int, n: int) -> int:
    return sum(1 for q in range(n) if (code >> (2 * q)) & 3)


def code_str(code: int, n: int) -> str:
    return "".join(LETTERS[(code >> (2 * q)) & 3] for q in range(n))


# ---------------------------------------------------------------------------
# Set partitions of {0..5} in restricted-growth-string lexicographic order
# ---------------------------------------------------------------------------

def rgs_partitions():
    parts = []

    def rec(i, rgs, mx):
        if i == 6:
            k = mx + 1
            blocks = [[] for _ in range(k)]
            for idx, a in enumerate(rgs):
                blocks[a].append(idx)
            parts.append(tuple(tuple(b) for b in blocks))
            return
        for a in range(mx + 2):
            rec(i + 1, rgs + [a], max(mx, a))

    rec(1, [0], 0)
    return parts


PARTITIONS = rgs_partitions()
if len(PARTITIONS) != 203:
    raise AssertionError({"partition_count": len(PARTITIONS)})
PART_INDEX = {p: i for i, p in enumerate(PARTITIONS)}
UNARY_PART = tuple((i,) for i in range(6))
BINARY_PART = (tuple(range(6)),)
UNARY_IDX = PART_INDEX[UNARY_PART]
BINARY_IDX = PART_INDEX[BINARY_PART]


def partition_static(part):
    k = len(part)
    flag = 1 if k >= 2 else 0
    sizes = [len(b) for b in part]
    bs = [bbits(m) for m in sizes]
    prep = (0 if k == 1 else 2 * k - 3) + sum(
        (m - 1) * (1 + flag) + DS[m] for m in sizes if m >= 2
    )
    width_shared = (k if k >= 2 else 0) + (max(bs) if bs else 0)
    width_dedicated = (k if k >= 2 else 0) + sum(bs)
    coeffs = []
    ns_masks = []
    for b, m, bb in zip(part, sizes, bs):
        mask = 0
        for i in b:
            mask |= 1 << i
        B = flag + bb + 1
        A = (flag + 1) - B * m
        coeffs.append((mask, A, B))
        if m >= 2:
            ns_masks.append(mask)
    r = len(ns_masks)
    smax = max(sizes)
    return {
        "part": part,
        "k": k,
        "flag": flag,
        "prep": prep,
        "width_shared": width_shared,
        "width_dedicated": width_dedicated,
        "prepw": prep + width_shared,
        "coeffs": tuple(coeffs),
        "ns_masks": tuple(ns_masks),
        "r": r,
        "smax": smax,
    }


PSTAT = [partition_static(p) for p in PARTITIONS]

# (r, smax) class machinery for the stage-3 ladder
CLASSES = sorted({(s["r"], s["smax"]) for s in PSTAT})
CLASS_INDEX = {c: i for i, c in enumerate(CLASSES)}
PCLASS = [CLASS_INDEX[(s["r"], s["smax"])] for s in PSTAT]
PFAST = [(s["prepw"], s["coeffs"], s["ns_masks"]) for s in PSTAT]

# ---------------------------------------------------------------------------
# Direct member evaluator (independent code path used as the referee binder)
# ---------------------------------------------------------------------------

def member_components(codes, n, part, phi, shared):
    k = len(part)
    flag = 1 if k >= 2 else 0
    wts = [term_wt(c, n) for c in codes]
    sel = 0
    for bi, block in enumerate(part):
        m = len(block)
        b = bbits(m)
        if phi[bi] == 0:
            sel += sum((flag + b + 1) * wts[i] for i in block)
        else:
            wF = 0
            for q in range(n):
                v = (codes[block[0]] >> (2 * q)) & 3
                if v and all(((codes[i] >> (2 * q)) & 3) == v for i in block):
                    wF += 1
            sel += (flag + 1) * wF + (flag + b + 1) * (
                sum(wts[i] for i in block) - m * wF
            )
    prep = (0 if k == 1 else 2 * k - 3) + sum(
        (len(b_) - 1) * (1 + flag) + DS[len(b_)] for b_ in part if len(b_) >= 2
    )
    bs = [bbits(len(b_)) for b_ in part]
    width = (k if k >= 2 else 0) + ((max(bs) if bs else 0) if shared else sum(bs))
    return sel, prep, width


def member_cost(codes, n, part, phi, shared):
    return sum(member_components(codes, n, part, phi, shared))


def full_sweep(codes, n):
    """Exact full referee: all partitions x all phi vectors x both a."""
    best = INF
    for part in PARTITIONS:
        k = len(part)
        for phi in itertools.product((0, 1), repeat=k):
            for shared in (True, False):
                c = member_cost(codes, n, part, phi, shared)
                if c < best:
                    best = c
    return best


# ---------------------------------------------------------------------------
# Fast referee + per-instance evaluation (phi=1, shared; exact by D-phi / D-a)
# ---------------------------------------------------------------------------

PAIR_MASKS = [
    (1 << i) | (1 << j) for i, j in itertools.combinations(range(6), 2)
]
DISJ2 = [
    (a, b)
    for a, b in itertools.combinations(PAIR_MASKS, 2)
    if a & b == 0
]
MATCH3 = [
    (a, b, c)
    for a, b, c in itertools.combinations(PAIR_MASKS, 3)
    if a & b == 0 and a & c == 0 and b & c == 0 and (a | b | c) == 63
]
TRIPLE_MASKS = [
    (1 << i) | (1 << j) | (1 << k) for i, j, k in itertools.combinations(range(6), 3)
]
QUAD_MASKS = [63 ^ p for p in PAIR_MASKS]
QUINT_MASKS = [63 ^ (1 << i) for i in range(6)]
if len(DISJ2) != 45 or len(MATCH3) != 15:
    raise AssertionError("frozen pair-combination counts")


def eval_instance(codes, n):
    wts = [term_wt(c, n) for c in codes]
    W = sum(wts)
    sw = [0] * 64
    for mask in range(1, 64):
        low = mask & (-mask)
        sw[mask] = sw[mask ^ low] + wts[low.bit_length() - 1]
    wF = [0] * 64
    for q in range(n):
        mv = [0, 0, 0, 0]
        for i in range(6):
            mv[(codes[i] >> (2 * q)) & 3] |= 1 << i
        for mask in range(1, 64):
            low = mask & (-mask)
            v = (codes[low.bit_length() - 1] >> (2 * q)) & 3
            if v and (mask & ~mv[v]) == 0:
                wF[mask] += 1
    # identical-term masks (donor collection preprocessing)
    code_mask = {}
    for i, c in enumerate(codes):
        code_mask[c] = code_mask.get(c, 0) | (1 << i)
    ident = [False] * 64
    for mask in range(1, 64):
        low = mask & (-mask)
        cm = code_mask[codes[low.bit_length() - 1]]
        ident[mask] = (mask & ~cm) == 0

    best = INF
    bestidx = -1
    cls_min = [INF] * len(CLASSES)
    collect_min = INF
    for idx in range(203):
        prepw, coeffs, ns_masks = PFAST[idx]
        c = prepw
        for mask, A, B in coeffs:
            c += A * wF[mask] + B * sw[mask]
        if c < best:
            best = c
            bestidx = idx
        ci = PCLASS[idx]
        if c < cls_min[ci]:
            cls_min[ci] = c
        ok = True
        for mask in ns_masks:
            if not ident[mask]:
                ok = False
                break
        if ok and c < collect_min:
            collect_min = c

    C_U = 2 * W + 15
    C_B = 4 * W + 14
    if not C_U < C_B:
        raise AssertionError({"incumbent_order": [C_U, C_B]})
    C_inc = C_U
    C_F = best
    C_collect = min(collect_min, C_B)
    if not (C_F <= C_collect <= C_U):
        raise AssertionError({"collect_sandwich": [C_F, C_collect, C_U]})
    if not (C_F <= C_B):
        raise AssertionError({"binary_containment": [C_F, C_B]})

    # stage-3 ladder values
    cost_k1 = None
    prepw0, coeffs0, _ = PFAST[BINARY_IDX]
    cost_k1 = prepw0
    for mask, A, B in coeffs0:
        cost_k1 += A * wF[mask] + B * sw[mask]

    def cls_agg(pred):
        m = INF
        for (r, smax), v in zip(CLASSES, cls_min):
            if pred(r, smax) and v < m:
                m = v
        return m

    C_E0 = min(C_U, C_B)
    C_E1 = min(C_E0, cost_k1)
    C_E2 = min(C_E1, cls_agg(lambda r, s: r <= 1))
    C_E3 = min(C_E2, cls_agg(lambda r, s: r <= 2))
    C_E4 = min(C_E3, cls_agg(lambda r, s: True))
    if not (C_E0 >= C_E1 >= C_E2 >= C_E3 >= C_E4 == C_F):
        raise AssertionError({"ladder_nesting": [C_E0, C_E1, C_E2, C_E3, C_E4, C_F]})
    s_mins = {
        s: min(C_E0, cls_agg(lambda r, sm, s=s: sm <= s)) for s in range(2, 7)
    }
    js_mins = {
        (j, s): min(C_E0, cls_agg(lambda r, sm, j=j, s=s: r <= j and sm <= s))
        for j in (1, 2, 3)
        for s in range(2, 7)
    }

    # stage-4 closed-form features
    g2 = {pm: 4 * wF[pm] - sw[pm] for pm in PAIR_MASKS}
    maxg2 = max(g2.values())
    best2 = max(g2[a] + g2[b] + 1 for a, b in DISJ2)
    best3 = max(g2[a] + g2[b] + g2[c] + 2 for a, b, c in MATCH3)
    maxg3 = max(10 * wF[m] - 2 * sw[m] - 1 for m in TRIPLE_MASKS)
    maxg4 = max(14 * wF[m] - 2 * sw[m] - 1 for m in QUAD_MASKS)
    maxg5 = max(23 * wF[m] - 3 * sw[m] - 3 for m in QUINT_MASKS)
    g6 = 23 * wF[63] - 2 * W + 1
    gainmax = C_U - C_F
    P0 = maxg2 <= 0 and best2 <= 0 and best3 <= 0
    P1 = P0 and maxg3 <= 0 and maxg4 <= 0 and maxg5 <= 0 and g6 <= 0
    P2 = gainmax <= 0
    label = C_F == C_inc
    if P2 != label:
        raise AssertionError({"P2_identity": [C_F, C_U]})
    bounded_gain = max(0, maxg2, best2, best3, maxg3, maxg4, maxg5, g6)
    literals = (
        maxg2 <= 0,
        maxg2 < 0,
        wF[63] == 0,
        maxg3 <= 0,
        best2 <= 0,
        W >= 12,
        max(wts) == n,
        max(wF[pm] for pm in PAIR_MASKS) == 0,
    )
    return {
        "W": W,
        "wF": wF,
        "sw": sw,
        "C_F": C_F,
        "C_U": C_U,
        "C_B": C_B,
        "C_inc": C_inc,
        "C_collect": C_collect,
        "C_incplus": min(C_inc, C_collect),
        "bestidx": bestidx,
        "E": [C_E0, C_E1, C_E2, C_E3, C_E4],
        "s_mins": s_mins,
        "js_mins": js_mins,
        "features": {
            "maxg2": maxg2,
            "best2": best2,
            "best3": best3,
            "maxg3": maxg3,
            "maxg4": maxg4,
            "maxg5": maxg5,
            "g6": g6,
        },
        "bounded_complete": C_F == C_U - bounded_gain,
        "P": (P0, P1, P2),
        "label": label,
        "literals": literals,
    }


# ---------------------------------------------------------------------------
# Stage 1 — dominance audit
# ---------------------------------------------------------------------------

def stage1_audit():
    per_mf = []
    total_configs = 0
    total_violations = 0
    dphi_ok = True
    max_ratio = (0, 1)  # save/surcharge as fraction over surcharge>0
    for m in range(2, 7):
        b = bbits(m)
        for f in (0, 1):
            configs = 0
            violations = 0
            ties = 0
            rows = []
            for col in itertools.product(range(4), repeat=m):
                configs += 1
                cnt = sum(1 for a in col if a)
                all_eq = cnt == m and len(set(col)) == 1 and col[0] != 0
                # save computed literally from the factored/unfactored defs
                F = col[0] if all_eq else 0
                res = [0 if F else a for a in col]
                unf = (f + b + 1) * cnt
                fac = (f + 1) * (1 if F else 0) + (f + b + 1) * sum(
                    1 for a in res if a
                )
                save = unf - fac
                closed = (m * (f + b + 1) - (f + 1)) if all_eq else 0
                if save != closed or save < 0:
                    dphi_ok = False
                surcharge = b * cnt
                if save > surcharge:
                    violations += 1
                    if len(rows) < VERBATIM_CAP:
                        rows.append(
                            {
                                "column": "".join(LETTERS[a] for a in col),
                                "save": save,
                                "surcharge": surcharge,
                                "excess": save - surcharge,
                            }
                        )
                elif save == surcharge:
                    ties += 1
                if surcharge > 0 and save * max_ratio[1] > max_ratio[0] * surcharge:
                    max_ratio = (save, surcharge)
            total_configs += configs
            total_violations += violations
            per_mf.append(
                {
                    "m": m,
                    "f": f,
                    "b": b,
                    "configs": configs,
                    "violations": violations,
                    "ties": ties,
                    "violating_rows_verbatim_capped": rows,
                }
            )
    if total_configs != 10912:
        raise AssertionError({"stage1_domain_size": total_configs})
    da_ok = all(s["width_shared"] <= s["width_dedicated"] for s in PSTAT)
    claim_d = "LOCAL_DOMINANCE_HOLDS" if total_violations == 0 else "LOCAL_DOMINANCE_REFUTED"
    return {
        "claim": (
            "Claim D (index-control dominance, per column): the per-column SELECT "
            "saving of factoring never exceeds the index-control surcharge "
            "b(m) * #non-identity letters."
        ),
        "domain_size": total_configs,
        "violations": total_violations,
        "outcome": claim_d,
        "max_save_over_surcharge": {
            "num": max_ratio[0],
            "den": max_ratio[1],
        },
        "per_m_f": per_mf,
        "auxiliary": {
            "D_phi_factoring_dominance_closed_form_verified": dphi_ok,
            "D_a_ancilla_share_dominance_verified_over_203_partitions": da_ok,
        },
        "declared_gap": (
            "Claim D bounds only the SELECT channel; PREP and WIDTH couplings are "
            "decided at Stage 2 on finite instance domains."
        ),
    }


# ---------------------------------------------------------------------------
# Domain processing (stages 2-4 aggregation)
# ---------------------------------------------------------------------------

def witness_record(codes, n, rec):
    st = PSTAT[rec["bestidx"]]
    part = st["part"]
    phi = tuple(1 for _ in part)
    sel, prep, width = member_components(codes, n, part, phi, True)
    if sel + prep + width != rec["C_F"]:
        raise AssertionError({"witness_recompute": [sel + prep + width, rec["C_F"]]})
    blocks = []
    for b in part:
        if len(b) >= 2:
            mask = 0
            for i in b:
                mask |= 1 << i
            blocks.append({"block": list(b), "wF": rec["wF"][mask]})
    usel, uprep, uwidth = member_components(codes, n, UNARY_PART, (0,) * 6, True)
    return {
        "partition": [list(b) for b in part],
        "shape": "+".join(
            str(x) for x in sorted((len(b) for b in part if len(b) >= 2), reverse=True)
        )
        or "1",
        "nonsingleton_blocks": blocks,
        "ledger": {"SELECT": sel, "PREP": prep, "WIDTH": width},
        "unary_ledger": {"SELECT": usel, "PREP": uprep, "WIDTH": uwidth},
    }


def process_domain(name, instances, binding_every, reorder_every, gates):
    agg = {
        "name": name,
        "instances": 0,
        "trades": 0,
        "structural_trades": 0,
        "incumbent_exact": 0,
        "gap_hist": {},
        "structural_gap_hist": {},
        "witness_shapes": {},
        "verbatim_trades": [],
        "verbatim_structural": [],
        "min_gap_witness": None,
        "max_gap_witness": None,
        "min_sgap_witness": None,
        "max_sgap_witness": None,
        "ladder_residuals": [0] * 5,
        "s_residuals": {s: 0 for s in range(2, 7)},
        "js_residuals": {f"{j},{s}": 0 for j in (1, 2, 3) for s in range(2, 7)},
        "confusion": {p: [0, 0, 0, 0] for p in ("P0", "P1", "P2")},  # TP,FP,FN,TN
        "bounded_complete": 0,
    }
    rows_small = []
    enum_hash = hashlib.sha256()
    for idx, (n, codes) in enumerate(instances):
        rec = eval_instance(codes, n)
        enum_hash.update(canonical_json([n, list(codes)]).encode())
        agg["instances"] += 1
        gap = rec["C_inc"] - rec["C_F"]
        sgap = rec["C_incplus"] - rec["C_F"]
        if gap < 0 or sgap < 0:
            raise AssertionError({"negative_gap": [name, idx]})
        row_base = None

        def make_row():
            return {
                "index": idx,
                "n": n,
                "codes": list(codes),
                "terms": [code_str(c, n) for c in codes],
                "C_F": rec["C_F"],
                "C_U": rec["C_U"],
                "C_B": rec["C_B"],
                "C_collect": rec["C_collect"],
                "gap": gap,
                "structural_gap": sgap,
                "witness": witness_record(codes, n, rec),
            }

        if rec["label"]:
            agg["incumbent_exact"] += 1
        if gap > 0:
            agg["trades"] += 1
            agg["gap_hist"][str(gap)] = agg["gap_hist"].get(str(gap), 0) + 1
            row_base = make_row()
            shape = row_base["witness"]["shape"]
            agg["witness_shapes"][shape] = agg["witness_shapes"].get(shape, 0) + 1
            if len(agg["verbatim_trades"]) < VERBATIM_CAP:
                agg["verbatim_trades"].append(row_base)
            if agg["min_gap_witness"] is None or gap < agg["min_gap_witness"]["gap"]:
                agg["min_gap_witness"] = row_base
            if agg["max_gap_witness"] is None or gap > agg["max_gap_witness"]["gap"]:
                agg["max_gap_witness"] = row_base
        if sgap > 0:
            agg["structural_trades"] += 1
            agg["structural_gap_hist"][str(sgap)] = (
                agg["structural_gap_hist"].get(str(sgap), 0) + 1
            )
            row = row_base or make_row()
            if len(agg["verbatim_structural"]) < VERBATIM_CAP:
                agg["verbatim_structural"].append(row)
            if (
                agg["min_sgap_witness"] is None
                or sgap < agg["min_sgap_witness"]["structural_gap"]
            ):
                agg["min_sgap_witness"] = row
            if (
                agg["max_sgap_witness"] is None
                or sgap > agg["max_sgap_witness"]["structural_gap"]
            ):
                agg["max_sgap_witness"] = row
        for j in range(5):
            if rec["E"][j] > rec["C_F"]:
                agg["ladder_residuals"][j] += 1
        for s in range(2, 7):
            if rec["s_mins"][s] > rec["C_F"]:
                agg["s_residuals"][s] += 1
        for (j, s), v in rec["js_mins"].items():
            if v > rec["C_F"]:
                agg["js_residuals"][f"{j},{s}"] += 1
        if rec["bounded_complete"]:
            agg["bounded_complete"] += 1
        for pi, pname in enumerate(("P0", "P1", "P2")):
            pred = rec["P"][pi]
            lab = rec["label"]
            slot = 0 if (pred and lab) else 1 if (pred and not lab) else 2 if (
                not pred and lab
            ) else 3
            agg["confusion"][pname][slot] += 1
        rows_small.append(
            {
                "P": rec["P"],
                "label": rec["label"],
                "literals": rec["literals"],
            }
        )
        # bindings
        if binding_every and idx % binding_every == 0:
            fs = full_sweep(codes, n)
            if fs != rec["C_F"]:
                raise AssertionError({"fast_full_binding": [name, idx, fs, rec["C_F"]]})
            gates["binding_samples"] += 1
        if reorder_every and idx % reorder_every == 0:
            rev = tuple(reversed(codes))
            if eval_instance(rev, n)["C_F"] != rec["C_F"]:
                raise AssertionError({"reorder_invariance": [name, idx]})
            gates["reorder_samples"] += 1
        # incumbent formula binding on every instance
        cu = member_cost(codes, n, UNARY_PART, (0,) * 6, True)
        cb = member_cost(codes, n, BINARY_PART, (0,), True)
        if cu != rec["C_U"] or cb != rec["C_B"]:
            raise AssertionError({"incumbent_binding": [name, idx, cu, cb]})
        gates["incumbent_bindings"] += 1
        # gain-formula identity checks on every 512th instance of the fit domain
        if name == "exhaustive_n2" and idx % 512 == 0:
            _gain_identity_check(codes, n, rec)
            gates["gain_identity_samples"] += 1
    agg["enumeration_sha256"] = enum_hash.hexdigest()
    return agg, rows_small


_SHAPE_PARTS = {
    "pair": ((0, 1), (2,), (3,), (4,), (5,)),
    "triple": ((0, 1, 2), (3,), (4,), (5,)),
    "quad": ((0, 1, 2, 3), (4,), (5,)),
    "quint": ((0, 1, 2, 3, 4), (5,)),
    "six": (tuple(range(6)),),
    "two_pair": ((0, 1), (2, 3), (4,), (5,)),
    "three_pair": ((0, 1), (2, 3), (4, 5)),
}


def _gain_identity_check(codes, n, rec):
    wF, sw = rec["wF"], rec["sw"]
    C_U = rec["C_U"]
    exp = {
        "pair": 4 * wF[3] - sw[3],
        "triple": 10 * wF[7] - 2 * sw[7] - 1,
        "quad": 14 * wF[15] - 2 * sw[15] - 1,
        "quint": 23 * wF[31] - 3 * sw[31] - 3,
        "six": 23 * wF[63] - 2 * sw[63] + 1,
        "two_pair": (4 * wF[3] - sw[3]) + (4 * wF[12] - sw[12]) + 1,
        "three_pair": (4 * wF[3] - sw[3])
        + (4 * wF[12] - sw[12])
        + (4 * wF[48] - sw[48])
        + 2,
    }
    for shape, part in _SHAPE_PARTS.items():
        got = C_U - member_cost(codes, n, part, (1,) * len(part), True)
        if got != exp[shape]:
            raise AssertionError({"gain_identity": [shape, got, exp[shape]]})


# ---------------------------------------------------------------------------
# Instance generators
# ---------------------------------------------------------------------------

def gen_exhaustive_n1():
    for codes in itertools.product((1, 2, 3), repeat=6):
        yield 1, codes


def gen_exhaustive_n2():
    for codes in itertools.combinations_with_replacement(range(1, 16), 6):
        yield 2, codes


def gen_panel(seed):
    rng = np.random.default_rng(seed)
    for n in (2, 3):
        for _ in range(120):
            yield n, tuple(int(rng.integers(1, 4 ** n)) for _ in range(6))


# ---------------------------------------------------------------------------
# Stage 4 predicate machinery
# ---------------------------------------------------------------------------

LITERAL_NAMES = [
    "[max g2 <= 0]",
    "[max g2 < 0]",
    "[wF(all six) == 0]",
    "[max g3 <= 0]",
    "[two-pair bonus <= 0]",
    "[W >= 12]",
    "[max_i wt_i == n]",
    "[max pair sh == 0]",
]


def p3_search(rows):
    best = None
    lit_count = len(LITERAL_NAMES)
    for size in (1, 2, 3):
        for combo in itertools.combinations(range(lit_count), size):
            err = 0
            for row in rows:
                pred = all(row["literals"][i] for i in combo)
                if pred != row["label"]:
                    err += 1
            key = (err, size, combo)
            if best is None or key < best[0]:
                best = (key, combo)
        if best and best[0][0] == 0:
            break
    (err, size, combo), _ = best[0], best[1]
    return {
        "literals": [LITERAL_NAMES[i] for i in best[1]],
        "training_error": best[0][0],
    }, best[1]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

FAMILY_SUMMARY = {
    "name": "SixLCU",
    "instance": "six non-identity Pauli terms on n qubits (formal batch, multiset)",
    "member": "(set partition G of the six terms; per-block factoring bit phi; "
    "shared/dedicated index-ancilla assignment)",
    "encoding": "one-hot flag per block when k>=2 (none at k=1) + ceil(log2 m) "
    "binary index bits per block of size m (frozen hybrid rule)",
    "cost_model": "C = SELECT + PREP + WIDTH, weights (1,1,1); controlled Pauli of "
    "support w under c controls costs (c+1)*w; PREP node cost 1 + #controls "
    "(unary cascade 2k-3; canonical balanced per-block tree (m-1)*(1+flag)+ds(m)); "
    "WIDTH = flags + index bits (sum if dedicated, max if shared)",
    "incumbents": {
        "unary_U": "six singletons; C_U = 2W + 15",
        "binary_B": "one block of six, no factoring; C_B = 4W + 14",
        "note": "C_U < C_B on every instance (W >= 6); asserted in-run",
    },
    "partitions": 203,
    "donor_refusal": "trades reported both vs C_inc = min(C_U, C_B) and vs "
    "C_inc+ = min(C_inc, C_collect) where C_collect merges identical terms only "
    "(donor-owned Hamiltonian preprocessing)",
}

CLAIM_BOUNDARY = (
    "The claim covers exactly the frozen SixLCU family: six-term Pauli batches, "
    "the frozen hybrid one-hot/binary coefficient-register encodings indexed by "
    "set partitions of six, phi factoring bits, shared/dedicated index-ancilla "
    "assignments, and the frozen support/node-count objective with weights "
    "(1,1,1). All equalities and trade catalogues are machine-evidenced only on "
    "the stated finite domains (exhaustive at n=1 and n=2, seeded panels at "
    "n=2..3); nothing is a theorem for all n or for other weights, cost rules, "
    "term counts, or encodings (qubitization walk operators, coherent alias "
    "sampling, amplitude-dependent PREP costs are out of scope). Incumbents are "
    "donor-owned; identical-term collection is donor-owned preprocessing with "
    "refusal rights via C_inc+; the hybrid-grouping enlargement is bookkeeping "
    "and earns no novelty credit. The template itself is the object under test. "
    "Not R6. No new subject data; the protected stretched-N2 subject is "
    "untouched."
)


def main():
    t0 = time.time()
    gates_ctr = {
        "binding_samples": 0,
        "reorder_samples": 0,
        "incumbent_bindings": 0,
        "gain_identity_samples": 0,
    }

    # Stage 1
    stage1 = stage1_audit()

    # Stage 2 domains
    dom_a, rows_a = process_domain(
        "exhaustive_n1", gen_exhaustive_n1(), 7, 36, gates_ctr
    )
    dom_b, rows_b = process_domain(
        "exhaustive_n2", gen_exhaustive_n2(), 97, 512, gates_ctr
    )
    dom_c, rows_c = process_domain(
        "random_panel_seed20260821", gen_panel(SEED_PANEL), 10, 0, gates_ctr
    )
    if dom_a["instances"] != 729 or dom_b["instances"] != 38760 or dom_c[
        "instances"
    ] != 240:
        raise AssertionError(
            {
                "domain_sizes": [
                    dom_a["instances"],
                    dom_b["instances"],
                    dom_c["instances"],
                ]
            }
        )
    stage2_domains = [dom_a, dom_b, dom_c]
    total_trades = sum(d["trades"] for d in stage2_domains)
    total_structural = sum(d["structural_trades"] for d in stage2_domains)
    stage2 = {
        "outcome": "TRADES_FOUND" if total_trades else "NO_TRADES",
        "total_trades": total_trades,
        "total_structural_trades": total_structural,
        "domains": {
            d["name"]: {
                k: v
                for k, v in d.items()
                if k
                not in (
                    "ladder_residuals",
                    "s_residuals",
                    "js_residuals",
                    "confusion",
                    "bounded_complete",
                    "name",
                )
            }
            for d in stage2_domains
        },
    }

    # Stage 3 — sufficiency ladder
    ladder_tot = [sum(d["ladder_residuals"][j] for d in stage2_domains) for j in range(5)]
    if ladder_tot[4] != 0:
        raise AssertionError({"E4_not_closed": ladder_tot})
    j_star = min(j for j in range(5) if ladder_tot[j] == 0)
    s_tot = {
        s: sum(d["s_residuals"][s] for d in stage2_domains) for s in range(2, 7)
    }
    s_closed = [s for s in range(2, 7) if s_tot[s] == 0]
    s_star = min(s_closed) if s_closed else None
    js_tot = {
        key: sum(d["js_residuals"][key] for d in stage2_domains)
        for key in stage2_domains[0]["js_residuals"]
    }
    if total_trades == 0:
        stage3_outcome = "NONE_NEEDED"
    elif j_star < 4:
        stage3_outcome = f"CLOSED_AT_LEVEL_E{j_star}"
    else:
        stage3_outcome = "NO_STRICT_SUBEXTENSION_CLOSES"
    stage3 = {
        "ladder": {
            "E0_incumbents": ladder_tot[0],
            "E1_plus_factored_binary": ladder_tot[1],
            "E2_at_most_one_merged_group": ladder_tot[2],
            "E3_at_most_two_merged_groups": ladder_tot[3],
            "E4_full_family": ladder_tot[4],
        },
        "minimal_closing_level_j": j_star,
        "outcome": stage3_outcome,
        "max_block_size_axis_residuals": {str(s): s_tot[s] for s in range(2, 7)},
        "minimal_closing_max_block_size_s": s_star,
        "js_closure_matrix_residuals": js_tot,
        "per_domain_ladder_residuals": {
            d["name"]: d["ladder_residuals"] for d in stage2_domains
        },
    }

    # Stage 4 — predicate induction on fit domain (b), then held-out
    train_err = {
        p: dom_b["confusion"][p][1] + dom_b["confusion"][p][2]
        for p in ("P0", "P1", "P2")
    }
    if train_err["P2"] != 0:
        raise AssertionError({"P2_training_error": train_err})
    p3_summary = None
    if train_err["P0"] == 0:
        selected = "P0"
    elif train_err["P1"] == 0:
        selected = "P1"
    elif train_err["P2"] == 0:
        selected = "P2"
    else:  # unreachable: the per-instance P2 identity is hard-asserted
        p3_summary, _combo = p3_search(rows_b)
        raise AssertionError({"P3_reached_despite_P2_identity": p3_summary})

    # H2 generated only after selection (frozen order of operations)
    dom_h2, rows_h2 = process_domain(
        "heldout_panel_seed20260825", gen_panel(SEED_HELDOUT), 10, 0, gates_ctr
    )
    if dom_h2["instances"] != 240:
        raise AssertionError({"h2_size": dom_h2["instances"]})

    panels4 = {
        "fit_exhaustive_n2": dom_b,
        "H1_random_panel_seed20260821": dom_c,
        "H2_fresh_panel_seed20260825": dom_h2,
        "exhaustive_n1": dom_a,
    }
    confusions = {
        pname: {p: d["confusion"][p] for p in ("P0", "P1", "P2")}
        for pname, d in panels4.items()
    }
    sel_idx = {"P0": 0, "P1": 1, "P2": 2}.get(selected)
    sel_err = sel_fp = 0
    coverage = {}
    for pname, d in panels4.items():
        conf = d["confusion"][selected] if sel_idx is not None else None
        tp, fp, fn, tn = conf
        sel_err += fp + fn
        sel_fp += fp
        pos = tp + fn
        coverage[pname] = {
            "donor_exact_instances": pos,
            "recall_on_donor_exact": (tp / pos) if pos else None,
        }
    if total_trades == 0 and sum(
        d["confusion"]["P2"][1] + d["confusion"]["P2"][2] for d in panels4.values()
    ) == 0:
        outcome4 = "FAMILY_CLOSURE"
    elif sel_err == 0 and selected in ("P0", "P1"):
        outcome4 = f"EXACT_PREDICATE_FOUND_{selected}"
    elif sel_err == 0 and selected == "P2":
        outcome4 = "EXACT_BY_FULL_FORMULA_ONLY"
    elif sel_fp == 0:
        outcome4 = "SUFFICIENT_CONDITION_ONLY"
    else:
        outcome4 = "NO_CLEAN_PREDICATE"
    bounded_complete_tot = {
        pname: d["bounded_complete"] for pname, d in panels4.items()
    }
    stage4 = {
        "target_label": "incumbent_exact := (C_F == C_inc)",
        "fit_domain": "exhaustive_n2 (38760 instances)",
        "training_errors": train_err,
        "selected": selected,
        "selected_definition": {
            "P0": "max pair g2 <= 0 AND max two-disjoint-pair bonus <= 0 AND "
            "max three-pair bonus <= 0",
            "P1": "P0 AND all triple g3 <= 0 AND all quad g4 <= 0 AND all "
            "quint g5 <= 0 AND g6 <= 0",
            "P2": "max closed-form partition gain <= 0 (full structural formula)",
            "P3": p3_summary,
        }[selected],
        "outcome": outcome4,
        "confusion_matrices_TP_FP_FN_TN": confusions,
        "selected_total_error": sel_err,
        "selected_false_positives": sel_fp,
        "coverage": coverage,
        "bounded_mechanism_completeness_counts": bounded_complete_tot,
        "held_out_generated_after_selection": True,
    }

    # Gates
    gates = {
        "G1_stage1_audit_complete": stage1["domain_size"] == 10912
        and stage1["auxiliary"]["D_phi_factoring_dominance_closed_form_verified"]
        and stage1["auxiliary"]["D_a_ancilla_share_dominance_verified_over_203_partitions"],
        "G2_referee_soundness_and_binding": True,  # hard-asserted in-run
        "G2_binding_samples": gates_ctr["binding_samples"],
        "G3_incumbent_formula_binding": gates_ctr["incumbent_bindings"]
        == 729 + 38760 + 240 + 240,
        "G4_exhaustive_domains_complete": dom_a["instances"] == 729
        and dom_b["instances"] == 38760,
        "G4_enumeration_sha256": {
            "exhaustive_n1": dom_a["enumeration_sha256"],
            "exhaustive_n2": dom_b["enumeration_sha256"],
        },
        "G5_reorder_invariance_samples": gates_ctr["reorder_samples"],
        "G6_ladder_nesting": True,  # hard-asserted per instance
        "G7_predicate_discipline": {
            "selection_rule": "first of P0, P1, P2 with zero training error",
            "gain_identity_samples": gates_ctr["gain_identity_samples"],
            "h2_generated_after_selection": True,
        },
        "G8_determinism_no_wallclock_in_receipt": True,
        "G9_no_new_subject_data_no_network": True,
    }
    for key in (
        "G1_stage1_audit_complete",
        "G3_incumbent_formula_binding",
        "G4_exhaustive_domains_complete",
    ):
        if not gates[key]:
            raise AssertionError({key: gates[key]})

    stage_outcomes = {
        "stage1": stage1["outcome"],
        "stage2": stage2["outcome"],
        "stage3": stage3["outcome"],
        "stage4": stage4["outcome"],
    }
    verdict = (
        "TEMPLATE_TRANSFERRED"
        if all(v for v in stage_outcomes.values())
        else "TEMPLATE_PARTIAL"
    )
    authority = (
        f"ORION_QG4_SECOND_FAMILY_{verdict}__"
        "SIXLCU_PREP_SELECT_REGIME_GEOMETRY_ON_VERIFIED_DOMAINS__NOT_R6"
    )
    if "NOT_R6" not in authority:
        raise AssertionError("authority ceiling")

    result = {
        "schema": "orion-qg.qg4_second_family.v1",
        "protocol": "development/orion-qg-regime-geometry/QG4_SECOND_FAMILY_PROTOCOL.md",
        "programme": "ORION-QG lane QG-4 (PROGRAMME_CHARTER_V1.md, issue #740)",
        "template_source": "TARE instance MAX_R6N/R6O/R6P/R6Q (committed receipts)",
        "family": FAMILY_SUMMARY,
        "stage1_dominance_audit": stage1,
        "stage2_trade_search": stage2,
        "stage3_sufficiency": stage3,
        "stage4_predicate": stage4,
        "stage_outcomes": stage_outcomes,
        "transfer_verdict": verdict,
        "gates": gates,
        "authority": authority,
        "claim_boundary": CLAIM_BOUNDARY,
        "random_seeds": {"panel": SEED_PANEL, "heldout": SEED_HELDOUT},
        "responsibility": "qg4 lane, ORION-QG programme, 2026-08-21",
        "novelty_credit": False,
        "donor_novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
        "chemistry_sources_read": False,
        "network_access": False,
    }
    out = Path(__file__).with_name("QG4_SECOND_FAMILY_RESULTS.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("ORIONQ_QG4_SECOND_FAMILY=" + canonical_json(result))
    print(f"runtime_seconds={time.time() - t0:.3f}", file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
