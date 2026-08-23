#!/usr/bin/env python3
"""ORION-QG QG-7b: the frozen hybrid-family closed form B'' — weight-2-Tag +
phantom-borrow support-two configurations.

Frozen by development/orion-qg-regime-geometry/QG7B_HYBRID_FAMILY_PROTOCOL_V1.md
(frozen BEFORE any outcome under that protocol was computed).

Q1: the closed-form family B''(t) — two distinct weight-1 tag anchors
(weight-2 Tag) plus phantom blocks whose support-two label-1 frames borrow
their syndrome at an existing tag qubit — exactly the mechanism of QG-7's 64
fourth-regime witnesses, as delimited by the L4a non-consolidatability
classification, with a proof-carrying witness verifier.

Q2: completeness re-test C_DP == C_D++ == min(C_D+, f_B', f_B'') on
(W) the 64 QG-7 witnesses bound verbatim, (H) the full QG-7 H1-H5 panels
re-evaluated, (S) the QG-5b structured n=2 slice, (F) the QG-5b fresh seeded
panel, and (X) a NEW frozen adversarial panel designed against B'' itself
(weight-3 Tags, non-tag chain borrows, tag-supported phantoms, double-borrow
phantoms). A referee-confirmed instance with C_D++ < min(C_D+, f_B', f_B'')
is terminal QG7B_FIFTH_CONFIGURATION_FOUND; zero gap everywhere is terminal
QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS.

Q3: the remaining normalization obligations (L4b weight-<=2-Tag
consolidation; L4c tag-weight bound), stated with QG-7's L1/L2 receipt
values bound exactly. No new proof is claimed.

All frozen machinery imported UNMODIFIED. Authority ceiling NOT_R6.
No chemistry data is read; the protected stretched-N2 subject is never
touched. The only RNG is the digit-frozen QG-5b fresh-panel stream.
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
import qg7_bprime_completeness as qg7  # noqa: E402

# qg7 already declares the committed n=4 pair-count guard extension at import
# (r6p.EXPECTED_PAIR_COUNTS.setdefault(4, r6s.PAIR_COUNTS_SUPPORT2[4])).

INF = 10 ** 9
BIG = np.int32(INF)
MATCHING = r6m._SYNTHETIC_MATCHING
PROTOCOL_NAME = "QG7B_HYBRID_FAMILY_PROTOCOL_V1.md"
BASE_REVISION = "e633a4619624de01bec639a804dce02ca0be277a"
VERBATIM_CAP = 50
SEED_FRESH = 20260826
X, Y, Z = 1, 2, 3

K = qg7.K
kmul = qg7.kmul
anch = qg7.anchored
ph = qg7.phantom


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---- Q1: the frozen family B''(t) -------------------------------------------

_bsecond_block_cache: dict[tuple, tuple] = {}


def _bsecond_block_options(tp_j, n: int, tag: tuple, rel: tuple, homes: tuple):
    """Per-block option arrays for B'' at Tag (v_a@q_a) . (v_b@q_b).

    Mirrors the committed qg5b._bprime_block_options structure: rows are
    (extra, t_comm, t_anti, meta); anchored options (extra 0) precede
    phantom options (extra 2); per-class letter-signature dedupe.
    """
    key = (tp_j, n, tag, rel, homes)
    hit = _bsecond_block_cache.get(key)
    if hit is not None:
        return hit
    (qa, va), (qb, vb) = tag
    rows = []
    for q_t, v in ((qa, va), (qb, vb)):
        v_key = r6o._letter_key(v, q_t)
        for c in (1, 2, 3):
            if c == v:
                continue
            c_key = r6o._letter_key(c, q_t)
            for sigma in (0, 1):
                t_comm = p10.mul(tp_j[sigma], v_key)
                t_anti = p10.mul(tp_j[1 - sigma], c_key)
                rows.append(
                    (0, t_comm, t_anti, ("anchored", sigma, v_key, c_key, 0)))
    n_anchored = len(rows)
    for q_h in homes:
        if q_h in (qa, qb):
            raise AssertionError("qg7b home pool must exclude the tag qubits")
        for q_x, vx in ((qa, va), (qb, vb)):
            for ell in (1, 2, 3):
                if ell == vx:
                    continue
                ell_key = r6o._letter_key(ell, q_x)
                for m0 in (1, 2, 3):
                    m0_key = r6o._letter_key(m0, q_h)
                    for m1 in (1, 2, 3):
                        if m1 == m0:
                            continue
                        anti = p10.mul(ell_key, r6o._letter_key(m1, q_h))
                        for sigma in (0, 1):
                            t_comm = p10.mul(tp_j[sigma], m0_key)
                            t_anti = p10.mul(tp_j[1 - sigma], anti)
                            rows.append(
                                (2, t_comm, t_anti,
                                 ("phantom", sigma, m0_key, anti, 2)))
    extra = np.array([r[0] for r in rows], dtype=np.int32)
    letters = np.empty((len(rows), 2, len(rel)), dtype=np.int8)
    for i, (_, tc, ta, _meta) in enumerate(rows):
        for qi, q in enumerate(rel):
            letters[i, 0, qi] = r6o._local_code(tc, q)
            letters[i, 1, qi] = r6o._local_code(ta, q)
    keep: list[int] = []
    for lo, hi in ((0, n_anchored), (n_anchored, len(rows))):
        seen = set()
        for i in range(lo, hi):
            sig = letters[i].tobytes()
            if sig not in seen:
                seen.add(sig)
                keep.append(i)
    keep_arr = np.array(keep, dtype=np.int64)
    extra = extra[keep_arr]
    letters = letters[keep_arr]
    meta = tuple(rows[i][3] for i in keep)
    n_anchored = int((extra == 0).sum())
    out = (extra, letters, meta, n_anchored)
    _bsecond_block_cache[key] = out
    return out


def bsecond_family_min(target_pairs, n: int, want_witness: bool = False):
    """f_B'': exact minimum over the frozen weight-2-Tag hybrid family.

    Returns (value_or_None, witness_or_None). Deterministic: frozen sweep
    order, strict-improvement updates, flat argmin tie-break.
    """
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= (pair[0][0] | pair[0][1] | pair[1][0] | pair[1][1])
    pool = [q for q in range(n) if (union >> q) & 1]
    added = 0
    for q in range(n):
        if not (union >> q) & 1:
            pool.append(q)  # up to two empty representatives
            added += 1
            if added == 2:
                break
    pool = sorted(pool)
    rel = tuple(pool)
    best = None
    best_wit = None
    for qa, qb in itertools.combinations(pool, 2):
        homes = tuple(q for q in pool if q not in (qa, qb))
        if not homes:
            continue
        for va in (1, 2, 3):
            for vb in (1, 2, 3):
                tag = ((qa, va), (qb, vb))
                per_block = [
                    _bsecond_block_options(tp[j], n, tag, rel, homes)
                    for j in range(3)
                ]
                (ea, la, ma, naa), (eb, lb, mb, nab), (ec, lc, mc, nac) = \
                    per_block
                tot = (ea[:, None, None].astype(np.int32)
                       + eb[None, :, None] + ec[None, None, :])
                for k in range(2):
                    for qi in range(len(rel)):
                        tot = tot + r6p.F3[
                            la[:, k, qi][:, None, None],
                            lb[:, k, qi][None, :, None],
                            lc[:, k, qi][None, None, :],
                        ]
                # exclude the all-anchored corner (inside D+, not a borrow)
                tot[:naa, :nab, :nac] = BIG
                value = int(tot.min())
                if value < INF:
                    value += 4  # weight-two Tag
                    if best is None or value < best:
                        best = value
                        if want_witness:
                            flat = int(np.argmin(tot))
                            ia, ib, ic = np.unravel_index(flat, tot.shape)
                            best_wit = {
                                "q_ta": int(qa), "v_a": int(va),
                                "q_tb": int(qb), "v_b": int(vb),
                                "value": int(value),
                                "blocks": [
                                    {"block": "ABC"[j], "kind": mr[0],
                                     "sigma": int(mr[1]),
                                     "frame_comm": list(mr[2]),
                                     "frame_anti": list(mr[3]),
                                     "extra": int(mr[4])}
                                    for j, mr in enumerate(
                                        (ma[int(ia)], mb[int(ib)],
                                         mc[int(ic)]))
                                ],
                            }
    return best, best_wit


def verify_bsecond_witness(target_pairs, n: int, wit: dict[str, Any]) -> bool:
    """Proof-carrying referee: the B'' argmin member re-checked through the
    committed R6S config machinery plus the frozen B'' shape predicate."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    qa, qb = int(wit["q_ta"]), int(wit["q_tb"])
    va, vb = int(wit["v_a"]), int(wit["v_b"])
    if qa == qb or not (0 <= qa < n and 0 <= qb < n):
        return False
    if va not in (1, 2, 3) or vb not in (1, 2, 3):
        return False
    s = p10.mul(r6o._letter_key(va, qa), r6o._letter_key(vb, qb))
    if p10.wt(s) != 2:
        return False
    tag_letters = {qa: va, qb: vb}
    frames6: list = []
    t6: list = []
    any_phantom = False
    for j, blk in enumerate(wit["blocks"]):
        fc = tuple(blk["frame_comm"])
        fa = tuple(blk["frame_anti"])
        frames6.extend([fc, fa])
        t6.extend([tp[j][blk["sigma"]], tp[j][1 - blk["sigma"]]])
        mc = fc[0] | fc[1]
        ma = fa[0] | fa[1]
        if blk["kind"] == "anchored":
            if p10.wt(fc) != 1 or p10.wt(fa) != 1 or mc != ma:
                return False
            q = mc.bit_length() - 1
            if q not in tag_letters:
                return False
            if fc != r6o._letter_key(tag_letters[q], q):
                return False
        elif blk["kind"] == "phantom":
            any_phantom = True
            if p10.wt(fc) != 1 or p10.wt(fa) != 2:
                return False
            if ((mc >> qa) & 1) or ((mc >> qb) & 1):
                return False  # phantom home must be off the tag support
            if not (((ma >> qa) & 1) or ((ma >> qb) & 1)):
                return False  # the label-1 frame must borrow at a tag qubit
        else:
            return False
    if not any_phantom:
        return False
    ok, labels = r6s.config_labels(tuple(frames6), s)
    if not ok or labels != (0, 1):
        return False
    cost = r6s.config_cost(tuple(t6), tuple(frames6), s, (1, 1, 1), n)
    return int(cost) == int(wit["value"])


# ---- shared per-instance evaluation ------------------------------------------

def _clear_instance_caches() -> None:
    r6o._block_cache.clear()
    qg5b._bprime_block_cache.clear()
    _bsecond_block_cache.clear()


def _new_counters() -> dict[str, Any]:
    return {
        "dxx_witness_rows": 0, "dxx_witness_failures": [],
        "bprime_witness_rows": 0, "bprime_witness_failures": [],
        "bprime_witness_exempt_infeasible": 0,
        "bsecond_witness_rows": 0, "bsecond_witness_failures": [],
        "bsecond_witness_exempt_infeasible": 0,
        "exact_matcher_rows": 0, "exact_matcher_failures": [],
        "containment_rows": 0, "containment_failures": [],
        "replay_rows": 0, "replay_failures": [],
    }


class Ledger:
    """Cross-panel accounting: coverage, contradictions, failures, fifths."""

    def __init__(self) -> None:
        self.counters = _new_counters()
        self.contradictions: list = []
        self.hard_failures: list = []
        self.fifth_candidates: list = []
        self.covered_without_bsecond = 0
        self.covered_by_bsecond = 0
        self.uncovered = 0
        self.bsecond_exact_rows = 0
        self.bsecond_pinched_rows = 0
        self.instances_total = 0


def _verify_bsecond(tp, n, fbpp, wit, where, counters):
    if fbpp is None:
        counters["bsecond_witness_exempt_infeasible"] += 1
        return
    counters["bsecond_witness_rows"] += 1
    if not verify_bsecond_witness(tp, n, wit):
        counters["bsecond_witness_failures"].append(where)


def evaluate_instance(tp, n, where, ledger, *, exact_bsecond: bool,
                      verify_dxx: bool, verify_bprime: bool,
                      run_matcher: bool):
    """Full evaluation of one instance under the frozen QG-7b identity."""
    c = ledger.counters
    _clear_instance_caches()
    terms = r6m._synthetic_terms(tp)
    c_dp = int(r6o.dp_cost_frozen_configs(terms, n))
    dxx = r6p.dxx_search(tp, n, want_witness=True)
    c_dxx = int(dxx["C_Dxx"])
    c_dplus = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
    fbp, fbp_wit = qg5b.bprime_family_min(tp, n, want_witness=True)
    fbp_eff = INF if fbp is None else int(fbp)
    ledger.instances_total += 1
    if c_dp != c_dxx:
        ledger.contradictions.append(
            {"where": where, "C_DP": c_dp, "C_Dxx": c_dxx,
             "target_pairs": [[list(a), list(b)] for a, b in tp]})
    if not (c_dp <= c_dxx <= c_dplus):
        ledger.hard_failures.append(
            {"where": where, "sandwich": [c_dp, c_dxx, c_dplus]})
    if fbp_eff < INF and c_dp > fbp_eff:
        ledger.hard_failures.append(
            {"where": where, "bprime_soundness": [c_dp, fbp_eff]})
    old_min = min(c_dplus, fbp_eff)
    gap_old = c_dxx - old_min
    need_exact = exact_bsecond or gap_old < 0
    fbpp = None
    fbpp_wit = None
    fbpp_eff = None
    status = "PINCHED_GE_C_DP"
    if need_exact:
        fbpp, fbpp_wit = bsecond_family_min(tp, n, want_witness=True)
        fbpp_eff = INF if fbpp is None else int(fbpp)
        status = "EXACT" if fbpp is not None else "INFEASIBLE"
        _verify_bsecond(tp, n, fbpp, fbpp_wit, where, c)
        if fbpp_eff < INF and c_dp > fbpp_eff:
            ledger.hard_failures.append(
                {"where": where, "bsecond_soundness": [c_dp, fbpp_eff]})
        ledger.bsecond_exact_rows += 1
    else:
        ledger.bsecond_pinched_rows += 1
    # coverage adjudication under the frozen pinch policy
    fifth = None
    if gap_old == 0:
        ledger.covered_without_bsecond += 1
        covered = True
    elif gap_old < 0:
        if fbpp_eff == c_dxx:
            ledger.covered_by_bsecond += 1
            covered = True
        else:
            covered = False
            ledger.uncovered += 1
            c["replay_rows"] += 1
            replay_ok = r6p.verify_dxx_witness(tp, n, dxx["witness"])
            wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
            replay_ok = replay_ok and int(wit["C_R6M"]) == c_dp \
                and all(wit["checks"].values())
            if not replay_ok:
                c["replay_failures"].append(where)
            fifth = {
                "where": where, "n": n,
                "target_pairs": [[list(a), list(b)] for a, b in tp],
                "C_DP": c_dp, "C_Dxx": c_dxx, "C_Dplus": c_dplus,
                "f_Bprime": fbp_eff,
                "f_Bsecond": None if fbpp is None else int(fbpp),
                "gap5": c_dxx - min(old_min,
                                    fbpp_eff if fbpp_eff is not None else INF),
                "replay_confirmed": bool(replay_ok),
                "dxx_witness_verbatim": dxx["witness"],
                "bprime_witness_verbatim": fbp_wit,
                "bsecond_witness_verbatim": fbpp_wit,
            }
            if len(ledger.fifth_candidates) < VERBATIM_CAP:
                ledger.fifth_candidates.append(fifth)
    else:  # gap_old > 0: containment/soundness breach, serialized above
        covered = False
        ledger.uncovered += 1
        ledger.hard_failures.append(
            {"where": where, "positive_gap_old": [c_dxx, c_dplus, fbp_eff]})
    # referee sampling
    if verify_dxx or gap_old < 0:
        c["dxx_witness_rows"] += 1
        if not r6p.verify_dxx_witness(tp, n, dxx["witness"]):
            c["dxx_witness_failures"].append(where)
    if (verify_bprime or gap_old < 0):
        if fbp is None:
            c["bprime_witness_exempt_infeasible"] += 1
        else:
            c["bprime_witness_rows"] += 1
            if not qg5b.verify_bprime_witness(tp, n, fbp_wit):
                c["bprime_witness_failures"].append(where)
    if run_matcher or gap_old < 0:
        c["exact_matcher_rows"] += 1
        wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
        if int(wit["C_R6M"]) != c_dp or not all(wit["checks"].values()):
            c["exact_matcher_failures"].append(where)
    # regime census, mirroring qg7.evaluate exactly (for receipt binding)
    if gap_old < 0:
        regime_old = "fourth"
    elif c_dxx == c_dplus == fbp_eff:
        regime_old = "tie"
    elif c_dxx == c_dplus:
        regime_old = "split"
    else:
        regime_old = "borrow"
    return {
        "C_DP": c_dp, "C_Dxx": c_dxx, "C_Dplus": c_dplus,
        "f_Bprime": fbp_eff, "f_Bsecond": fbpp,
        "f_Bsecond_status": status, "gap_old": int(gap_old),
        "covered": bool(covered), "regime_old": regime_old,
        "_dxx_witness": dxx["witness"], "_bprime_witness": fbp_wit,
        "_bsecond_witness": fbpp_wit,
    }


# ---- Panel W: the 64 QG-7 witnesses, verbatim --------------------------------

QG7_AUTHORITY = (
    "ORIONQG_QG7_FOURTH_SUPPORT2_REGIME_FOUND__"
    "HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6")
QG7_TERMINAL = "QG7_FOURTH_SUPPORT2_REGIME_FOUND"
QG7_PROTOCOL_SHA = (
    "04281622fdbf5a71436e60e3b3aaee66d1b7b0e025f14eafdf073e9b52373645")
QG5B_AUTHORITY = (
    "ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__"
    "DPP_FAMILY_MIN__ENLARGED_BORROW_CLOSES__NOT_R6")
R6S_AUTHORITY_PREFIX = "MAX_R6S_ALL_N_COMPOSITION_THEOREM_MACHINE_CHECKED"


def load_qg7_receipt() -> dict[str, Any]:
    return json.loads(
        Path(__file__).with_name("QG7_BPRIME_COMPLETENESS_RESULTS.json")
        .read_text())


def load_qg5b_receipt() -> dict[str, Any]:
    return json.loads(
        Path(__file__).with_name("QG5B_EXACT_FORECASTER_RESULTS.json")
        .read_text())


def panel_w(qg7_rec, ledger) -> dict[str, Any]:
    witnesses = qg7_rec["arm1_hostile_search"]["fourth_regime_candidates_verbatim"]
    rows = []
    binding_failures = []
    covered_count = 0
    for widx, rec in enumerate(witnesses):
        n = int(rec["panel"].rsplit("_n", 1)[1])
        tp = tuple((tuple(int(v) for v in a), tuple(int(v) for v in b))
                   for a, b in rec["target_pairs"])
        where = ["panel_w", widx]
        row = evaluate_instance(
            tp, n, where, ledger, exact_bsecond=True, verify_dxx=True,
            verify_bprime=True, run_matcher=True)
        bound = (
            row["C_DP"] == int(rec["C_DP"])
            and row["C_Dxx"] == int(rec["C_Dxx"])
            and row["C_Dplus"] == int(rec["C_Dplus"])
            and row["f_Bprime"] == int(rec["f_Bprime"])
            and row["gap_old"] == int(rec["gap4"])
            and bool(rec["replay_confirmed"])
        )
        if not bound:
            binding_failures.append({"index": widx, "panel": rec["panel"]})
        covered = row["covered"] and row["f_Bsecond"] == row["C_DP"]
        if covered:
            covered_count += 1
        rows.append({
            "index": widx, "panel": rec["panel"],
            "local_index": int(rec["local_index"]), "n": n,
            "target_pairs": [[list(a), list(b)] for a, b in tp],
            "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
            "C_Dplus": row["C_Dplus"], "f_Bprime": row["f_Bprime"],
            "f_Bsecond": row["f_Bsecond"],
            "receipt_row_bound": bool(bound),
            "covered_by_bsecond": bool(covered),
            "bsecond_witness_verbatim": row["_bsecond_witness"],
        })
    return {
        "witnesses_bound": len(witnesses),
        "expected_witnesses": 64,
        "receipt_binding_failures": binding_failures,
        "covered_count": covered_count,
        "all_covered": covered_count == len(witnesses) == 64,
        "rows": rows,
    }


# ---- Panels H and X: skeleton-panel enumeration ------------------------------

def skeletons_x2_n3():
    s2 = kmul(K(X, 0), K(X, 1))
    return [
        (ph(2, (X, Y), 0, Y) + (K(X, 1), kmul(K(Y, 2), K(Y, 1)))
         + anch(0, X, Y), s2),
        (ph(2, (X, Y), 0, Y) + (K(X, 1), kmul(K(Z, 2), K(Y, 1)))
         + anch(0, X, Z), s2),
        (ph(2, (X, Y), 0, Y) + (K(X, 0), kmul(K(Y, 2), K(Y, 0)))
         + anch(1, X, Y), s2),
        (ph(2, (X, Y), 1, Y) + (K(X, 1), kmul(K(Y, 2), K(Z, 1)))
         + anch(0, X, Y), s2),
    ]


def skeletons_x3_n3():
    s2 = kmul(K(X, 0), K(X, 1))
    return [
        (anch(0, X, Y) + (K(X, 1), kmul(K(X, 0), K(Y, 1)))
         + anch(0, X, Z), s2),
        (anch(0, X, Y) + (K(X, 1), kmul(K(X, 0), K(Z, 1)))
         + ph(2, (X, Y), 0, Y), s2),
        (anch(1, X, Y) + (K(X, 0), kmul(K(Y, 0), K(X, 1)))
         + anch(1, X, Z), s2),
        (ph(2, (X, Y), 0, Y) + (K(X, 1), kmul(K(X, 0), K(Y, 1)))
         + anch(1, X, Z), s2),
    ]


def skeletons_x4_n3():
    s2 = kmul(K(X, 0), K(X, 1))
    return [
        ((kmul(K(X, 0), K(X, 2)), kmul(K(Y, 1), K(Y, 2)))
         + anch(0, X, Y) + anch(1, X, Y), s2),
        ((kmul(K(X, 0), K(Y, 2)), kmul(K(Z, 1), K(Z, 2)))
         + anch(0, X, Z) + anch(1, X, Y), s2),
        ((kmul(K(X, 0), K(X, 2)), kmul(K(Y, 1), K(Y, 2)))
         + ph(2, (X, Y), 0, Y) + anch(1, X, Y), s2),
        ((kmul(K(X, 1), K(X, 2)), kmul(K(Y, 0), K(Y, 2)))
         + anch(0, X, Y) + anch(1, X, Z), s2),
    ]


def skeletons_x1_n4():
    s3 = kmul(K(X, 0), K(X, 1), K(X, 2))
    return [
        (anch(0, X, Y) + anch(1, X, Y) + ph(3, (X, Y), 2, Y), s3),
        (anch(0, X, Y) + anch(1, X, Z) + ph(3, (X, Y), 2, Z), s3),
        (anch(0, X, Y) + ph(3, (X, Y), 1, Y) + ph(3, (Y, Z), 2, Y), s3),
        (ph(3, (X, Y), 0, Y) + ph(3, (Y, Z), 1, Y) + ph(3, (X, Z), 2, Y), s3),
        (anch(0, X, Y) + anch(1, X, Y) + anch(2, X, Y), s3),
    ]


def skeletons_x2_n4():
    s2 = kmul(K(X, 0), K(X, 1))
    return [
        (ph(2, (X, Y), 0, Y) + (K(X, 3), kmul(K(Y, 2), K(Y, 3)))
         + anch(1, X, Y), s2),
        (ph(2, (X, Y), 0, Y) + (K(X, 3), kmul(K(Z, 2), K(Y, 3)))
         + anch(1, X, Z), s2),
    ]


def skeletons_x3_n4():
    s2 = kmul(K(X, 0), K(X, 1))
    return [
        (anch(0, X, Y) + (K(X, 1), kmul(K(X, 0), K(Y, 1)))
         + ph(3, (X, Y), 0, Y), s2),
        (ph(2, (X, Y), 0, Y) + (K(X, 1), kmul(K(X, 0), K(Z, 1)))
         + anch(0, X, Y), s2),
    ]


def skeletons_x4_n4():
    s2 = kmul(K(X, 0), K(X, 1))
    return [
        ((kmul(K(X, 0), K(X, 2)), kmul(K(Y, 1), K(Y, 2)))
         + anch(0, X, Y) + ph(3, (X, Y), 1, Y), s2),
        ((kmul(K(X, 0), K(Y, 3)), kmul(K(Z, 1), K(Z, 3)))
         + anch(0, X, Z) + anch(1, X, Y), s2),
    ]


X_SKELETON_BUILDERS = {
    "X1": skeletons_x1_n4, "X2_3": skeletons_x2_n3, "X2_4": skeletons_x2_n4,
    "X3_3": skeletons_x3_n3, "X3_4": skeletons_x3_n4,
    "X4_3": skeletons_x4_n3, "X4_4": skeletons_x4_n4,
}
X_PANEL_ORDER = [
    ("X2", 3), ("X3", 3), ("X4", 3), ("X1", 4), ("X2", 4), ("X3", 4),
    ("X4", 4),
]
X_CAPS = {
    ("X2", 3): 40, ("X3", 3): 40, ("X4", 3): 40,
    ("X1", 4): 20, ("X2", 4): 12, ("X3", 4): 12, ("X4", 4): 12,
}


def run_skeleton_panel(pname, n, skels, cap, pair_lists, dedupe, gstate,
                       ledger, sample_rows, bsecond_stride):
    """Frozen QG-7 run_panel control flow with the QG-7b evaluation."""
    c = ledger.counters
    skel_meta = []
    for frames6, s in skels:
        ok, labels = r6s.config_labels(frames6, s)
        skel_meta.append({
            "feasible": bool(ok),
            "labels": list(labels) if labels else None,
            "max_frame_support": max(p10.wt(f) for f in frames6),
        })
    template_space = sum(len(pl) for pl in pair_lists)
    max_tp = max(len(pl) for pl in pair_lists)
    raw = zero_skip = dup_skip = 0
    evaluated: list = []
    census = {"split": 0, "borrow": 0, "tie": 0, "fourth": 0}
    gaps: list = []
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
            tp = qg7.derive_instance(frames6, pair_lists[s_idx][tp_idx])
            if tp is None:
                zero_skip += 1
                continue
            key = qg7.canonical_key(tp, n)
            if key in dedupe:
                dup_skip += 1
                continue
            dedupe.add(key)
            gidx = gstate["eval_idx"]
            gstate["eval_idx"] += 1
            if gidx % 128 == 0:
                r6m._local_table.cache_clear()
            lidx = len(evaluated)
            where = [pname + "_n%d" % n, lidx]
            matcher_due = (n == 3 and lidx % 20 == 0) or \
                (n == 4 and lidx % 8 == 0)
            row = evaluate_instance(
                tp, n, where, ledger,
                exact_bsecond=(gidx % bsecond_stride == 0),
                verify_dxx=(gidx % 7 == 0),
                verify_bprime=(gidx % 13 == 0),
                run_matcher=matcher_due)
            census[row["regime_old"]] += 1
            gaps.append(row["gap_old"])
            # skeleton containment gate (frozen QG-7 rule)
            if skel_meta[s_idx]["feasible"] and \
                    skel_meta[s_idx]["max_frame_support"] <= 2:
                t6 = tuple(t for pair in tp for t in pair)
                c["containment_rows"] += 1
                ub = qg7.skeleton_min_cost(t6, frames6, s, n)
                if row["C_Dxx"] > ub:
                    c["containment_failures"].append(where + [ub])
            evaluated.append({
                "target_pairs": [[list(a), list(b)] for a, b in tp],
                "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
                "C_Dplus": row["C_Dplus"], "f_Bprime": row["f_Bprime"],
                "f_Bsecond": row["f_Bsecond"],
                "f_Bsecond_status": row["f_Bsecond_status"],
                "covered": row["covered"],
            })
        else:
            continue
        break
    r6m._local_table.cache_clear()
    for lidx in sorted({0, len(evaluated) // 2} & set(range(len(evaluated)))):
        sample_rows.append({"panel": f"{pname}_n{n}", "n": n,
                            "local_index": lidx, **evaluated[lidx]})
    return {
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
        "min_gap_old": min(gaps) if gaps else None,
        "max_gap_old": max(gaps) if gaps else None,
        "covered_count": sum(1 for e in evaluated if e["covered"]),
    }, evaluated


def panel_h(qg7_rec, ledger, sample_rows):
    dedupe: set = set()
    gstate = {"eval_idx": 0}
    panels = {}
    rows_by_panel = {}
    for hname, n in qg7.PANEL_ORDER:
        skels = qg7.SKELETON_BUILDERS[hname](n)
        if hname == "H5":
            pair_lists = []
            for frames6, s in skels:
                occ = set(qg5b._qubits(qg5b._supp_mask(s)))
                for f in frames6:
                    occ |= set(qg5b._qubits(qg5b._supp_mask(f)))
                pair_lists.append(qg7.template_pairs_h5(n, occ))
        else:
            shared = qg7.template_pairs(n)
            pair_lists = [shared] * len(skels)
        summary, evaluated = run_skeleton_panel(
            hname, n, skels, qg7.CAPS[(hname, n)], pair_lists, dedupe,
            gstate, ledger, sample_rows, bsecond_stride=32)
        panels[f"{hname}_n{n}"] = summary
        rows_by_panel[f"{hname}_n{n}"] = evaluated
    # ---- receipt bindings ----
    binding_failures = []
    rec_panels = qg7_rec["arm1_hostile_search"]["panels"]
    for pkey, summary in panels.items():
        rec = rec_panels[pkey]
        checks = (
            summary["evaluated"] == int(rec["evaluated"])
            and summary["raw_scanned"] == int(rec["raw_scanned"])
            and summary["zero_target_skipped"] == int(rec["zero_target_skipped"])
            and summary["duplicate_skipped"] == int(rec["duplicate_skipped"])
            and summary["regime_census"] == rec["regime_census"]
            and summary["min_gap_old"] == rec["min_gap4"]
            and summary["max_gap_old"] == rec["max_gap4"]
            and summary["cap_hit"] == bool(rec["cap_hit"])
        )
        if not checks:
            binding_failures.append({"panel": pkey, "kind": "summary"})
    for srow in qg7_rec["verification_sample"]:
        mine = rows_by_panel[srow["panel"]][int(srow["local_index"])]
        if not (mine["target_pairs"] == srow["target_pairs"]
                and mine["C_DP"] == int(srow["C_DP"])
                and mine["C_Dxx"] == int(srow["C_Dxx"])
                and mine["C_Dplus"] == int(srow["C_Dplus"])
                and mine["f_Bprime"] == int(srow["f_Bprime"])):
            binding_failures.append(
                {"panel": srow["panel"], "kind": "sample",
                 "local_index": int(srow["local_index"])})
    for rec in qg7_rec["arm1_hostile_search"]["fourth_regime_candidates_verbatim"]:
        mine = rows_by_panel[rec["panel"]][int(rec["local_index"])]
        if not (mine["target_pairs"] == rec["target_pairs"]
                and mine["C_DP"] == int(rec["C_DP"])
                and mine["C_Dxx"] == int(rec["C_Dxx"])
                and mine["C_Dplus"] == int(rec["C_Dplus"])
                and mine["f_Bprime"] == int(rec["f_Bprime"])):
            binding_failures.append(
                {"panel": rec["panel"], "kind": "fourth_row",
                 "local_index": int(rec["local_index"])})
    total_eval = sum(p["evaluated"] for p in panels.values())
    return {
        "panels": panels,
        "instances_evaluated_total": total_eval,
        "expected_total": 740,
        "covered_total": sum(p["covered_count"] for p in panels.values()),
        "fourth_rows_reencountered": sum(
            p["regime_census"]["fourth"] for p in panels.values()),
        "receipt_binding_failures": binding_failures,
    }


def panel_x(ledger, sample_rows):
    dedupe: set = set()
    gstate = {"eval_idx": 0}
    panels = {}
    for xname, n in X_PANEL_ORDER:
        key = "X1" if xname == "X1" else f"{xname}_{n}"
        skels = X_SKELETON_BUILDERS[key]()
        shared = qg7.template_pairs(n)
        pair_lists = [shared] * len(skels)
        summary, _rows = run_skeleton_panel(
            xname, n, skels, X_CAPS[(xname, n)], pair_lists, dedupe,
            gstate, ledger, sample_rows, bsecond_stride=32)
        panels[f"{xname}_n{n}"] = summary
    total_eval = sum(p["evaluated"] for p in panels.values())
    return {
        "panels": panels,
        "instances_evaluated_total": total_eval,
        "covered_total": sum(p["covered_count"] for p in panels.values()),
        "fourth_rows_found": sum(
            p["regime_census"]["fourth"] for p in panels.values()),
        "generator": (
            "frozen adversarial anti-Bsecond skeletons (X1 weight-3 Tag, "
            "X2 non-tag chain borrow, X3 tag-supported phantom, X4 "
            "double-borrow phantom) under the committed QG-7 "
            "Restore-template grammar"),
    }


# ---- Panel S: the QG-5b structured n=2 slice ---------------------------------

def panel_s(ledger, sample_rows):
    c = ledger.counters
    wt1 = [r6o._letter_key(l, q) for q in (0, 1) for l in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    covered = 0
    dxx_exact_rows = 0
    idx = 0
    n = 2
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        tp = tuple((wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic))
        where = ["panel_s", idx]
        _clear_instance_caches()
        c_dp = int(r6o.dp_cost_n2_reader(tp))
        c_dplus = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
        fbp, fbp_wit = qg5b.bprime_family_min(tp, n, want_witness=True)
        fbp_eff = INF if fbp is None else int(fbp)
        ledger.instances_total += 1
        if fbp_eff < INF and c_dp > fbp_eff:
            ledger.hard_failures.append(
                {"where": where, "bprime_soundness": [c_dp, fbp_eff]})
        old_min = min(c_dplus, fbp_eff)
        gap_row = old_min > c_dp
        dxx_due = gap_row or idx % 97 == 0
        if dxx_due:
            dxx = r6p.dxx_search(tp, n, want_witness=True)
            c_dxx = int(dxx["C_Dxx"])
            dxx_exact_rows += 1
            if c_dp != c_dxx:
                ledger.contradictions.append(
                    {"where": where, "C_DP": c_dp, "C_Dxx": c_dxx,
                     "target_pairs": [[list(a), list(b)] for a, b in tp]})
            if not (c_dp <= c_dxx <= c_dplus):
                ledger.hard_failures.append(
                    {"where": where, "sandwich": [c_dp, c_dxx, c_dplus]})
            c["dxx_witness_rows"] += 1
            if not r6p.verify_dxx_witness(tp, n, dxx["witness"]):
                c["dxx_witness_failures"].append(where)
        bsecond_due = gap_row or idx % 64 == 0
        if bsecond_due:
            fbpp, fbpp_wit = bsecond_family_min(tp, n, want_witness=True)
            fbpp_eff = INF if fbpp is None else int(fbpp)
            _verify_bsecond(tp, n, fbpp, fbpp_wit, where, c)
            if fbpp_eff < INF and c_dp > fbpp_eff:
                ledger.hard_failures.append(
                    {"where": where, "bsecond_soundness": [c_dp, fbpp_eff]})
            ledger.bsecond_exact_rows += 1
        else:
            fbpp = None
            fbpp_eff = None
            ledger.bsecond_pinched_rows += 1
        if not gap_row:
            covered += 1
            ledger.covered_without_bsecond += 1
        else:
            if fbpp_eff == c_dp:
                covered += 1
                ledger.covered_by_bsecond += 1
            else:
                ledger.uncovered += 1
                terms = r6m._synthetic_terms(tp)
                c["replay_rows"] += 1
                wit = r6m.exact_r6m_matching(terms, MATCHING, n,
                                             list(range(6)))
                replay_ok = int(wit["C_R6M"]) == c_dp and \
                    all(wit["checks"].values())
                if not replay_ok:
                    c["replay_failures"].append(where)
                fifth = {
                    "where": where, "n": n,
                    "target_pairs": [[list(a), list(b)] for a, b in tp],
                    "C_DP": c_dp, "C_Dxx": None, "C_Dplus": c_dplus,
                    "f_Bprime": fbp_eff,
                    "f_Bsecond": None if fbpp is None else int(fbpp),
                    "gap5": None,
                    "replay_confirmed": bool(replay_ok),
                    "dxx_witness_verbatim": None,
                    "bprime_witness_verbatim": fbp_wit,
                    "bsecond_witness_verbatim": fbpp_wit,
                }
                if len(ledger.fifth_candidates) < VERBATIM_CAP:
                    ledger.fifth_candidates.append(fifth)
        if idx % 191 == 0:
            if fbp is None:
                c["bprime_witness_exempt_infeasible"] += 1
            else:
                c["bprime_witness_rows"] += 1
                if not qg5b.verify_bprime_witness(tp, n, fbp_wit):
                    c["bprime_witness_failures"].append(where)
        if idx % 1153 == 0:
            terms = r6m._synthetic_terms(tp)
            c["exact_matcher_rows"] += 1
            wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
            if int(wit["C_R6M"]) != c_dp or not all(wit["checks"].values()):
                c["exact_matcher_failures"].append(where)
        if idx in (0, 4630):
            sample_rows.append({
                "panel": "panel_s", "n": n, "local_index": idx,
                "target_pairs": [[list(a), list(b)] for a, b in tp],
                "C_DP": c_dp, "C_Dxx": None, "C_Dplus": c_dplus,
                "f_Bprime": fbp_eff,
                "f_Bsecond": None,
                "f_Bsecond_status": "EXACT" if bsecond_due else
                "PINCHED_GE_C_DP",
                "covered": bool(not gap_row or fbpp_eff == c_dp),
            })
        idx += 1
    r6m._local_table.cache_clear()
    return {
        "instances": idx,
        "expected_instances": 9261,
        "dp_truth": "r6o.dp_cost_n2_reader (committed unrestricted DP reader)",
        "covered_count": covered,
        "dxx_exact_rows": dxx_exact_rows,
        "bsecond_note": (
            "B'' requires two distinct tag qubits plus a nonempty home pool "
            "and is therefore structurally infeasible for every n <= 2; "
            "exact stride rows confirm INFEASIBLE"),
    }


# ---- Panel F: the QG-5b fresh seeded panel -----------------------------------

def panel_f(qg5b_rec, ledger, sample_rows):
    rec_pa = qg5b_rec["panels"]["panel_a_refuting_instance"]
    rng = np.random.default_rng(SEED_FRESH)
    covered = 0
    refuting_bound = False
    total = 0
    for n in (2, 3):
        for i in range(120):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            r6m._local_table.cache_clear()
            where = ["panel_f", n, i]
            row = evaluate_instance(
                tp, n, where, ledger, exact_bsecond=(i % 64 == 0),
                verify_dxx=(i % 10 == 0), verify_bprime=(i % 10 == 0),
                run_matcher=(i % 24 == 0))
            if row["covered"]:
                covered += 1
            if n == int(rec_pa["n"]) and i == int(rec_pa["index_in_fresh_panel"]):
                refuting_bound = (
                    [[list(a), list(b)] for a, b in tp]
                    == rec_pa["target_pairs"]
                    and row["C_DP"] == int(rec_pa["C_DP"]) == 10
                    and row["C_Dxx"] == int(rec_pa["F2_C_Dxx"]) == 10
                    and row["C_Dplus"] == int(rec_pa["C_Dplus"]) == 11
                    and row["f_Bprime"] == int(rec_pa["f_Bprime"]) == 10
                )
            if i in (0, 60):
                sample_rows.append({
                    "panel": "panel_f", "n": n, "local_index": i,
                    "target_pairs": [[list(a), list(b)] for a, b in tp],
                    "C_DP": row["C_DP"], "C_Dxx": row["C_Dxx"],
                    "C_Dplus": row["C_Dplus"], "f_Bprime": row["f_Bprime"],
                    "f_Bsecond": row["f_Bsecond"],
                    "f_Bsecond_status": row["f_Bsecond_status"],
                    "covered": row["covered"],
                })
            total += 1
    r6m._local_table.cache_clear()
    return {
        "seed": SEED_FRESH,
        "instances": total,
        "expected_instances": 240,
        "generator": (
            "digit-frozen copy of the QG-5 fresh panel (120 per n, "
            "n in {2,3})"),
        "covered_count": covered,
        "refuting_instance_bound": bool(refuting_bound),
        "qg5b_q2_zero_expected": 240,
    }


# ---- Q3: remaining normalization obligations (receipt-bound statement) -------

def q3_obligations(qg7_rec) -> dict[str, Any]:
    ob = qg7_rec["arm2_normalization"]["obligations"]
    l1 = ob["L1_canonical_block_shape"]
    l2 = ob["L2_support_two_orientation"]
    l4 = ob["L4_multi_block_consolidation"]
    bound = (
        l1["status"] == "CLOSED_ALL_N"
        and l1["domains"] == {"N1": 768, "N5": 27216}
        and l2["status"] == "CLOSED_ALL_N"
        and l2["domains"] == {"N3": 8, "N0_lemma_e": 18432,
                              "N0_lemma_b": 43688}
        and l4["domains"] == {"N7_checked": 1440}
        and l4["open_shapes"] == [
            "H1_multi_anchor_borrow_tag_weight_ge_2",
            "H3_cyclic_borrow",
            "H4_hybrid_split_borrow",
            "H4b_l1_phantom_tag_letter_at_home",
        ]
    )
    return {
        "l1_l2_receipt_bound": bool(bound),
        "bound_values": {
            "L1_status": l1["status"], "L1_domains": l1["domains"],
            "L2_status": l2["status"], "L2_domains": l2["domains"],
            "L4a_domain_checked": l4["domains"]["N7_checked"],
            "L4_open_shapes_verbatim": l4["open_shapes"],
        },
        "now_covered_on_verified_domains_by_bsecond": [
            "H1_multi_anchor_borrow_tag_weight_ge_2 (two distinct tag "
            "anchors, weight-2 Tag)",
            "H4_hybrid_split_borrow (anchored + phantom mixtures)",
        ],
        "remaining_obligations": {
            "L4b_weight_le2_tag_consolidation": {
                "statement": (
                    "prove every support-two optimum with tag weight <= 2 "
                    "consolidates without cost increase into "
                    "D+ union B' union B''"),
                "open_shape_classes": [
                    "tag_supported_phantom (comm frame at a tag qubit; "
                    "grammar-feasible, probed by X2_n3/X3)",
                    "double_borrow_phantom (both frames support-two; "
                    "probed by X4)",
                    "H3_cyclic_borrow (bound verbatim from the QG-7 "
                    "open-shape list)",
                    "H4b_l1_phantom_tag_letter_at_home (bound verbatim "
                    "from the QG-7 open-shape list)",
                ],
            },
            "L4c_tag_weight_bound": {
                "statement": (
                    "L4a prunes only tag letters outside the union FRAME "
                    "support (complete 1,440-check domain, exact refund 2); "
                    "a weight->=3 Tag with all letters frame-supported is "
                    "not covered: owe an exchange lemma reducing it to "
                    "weight <= 2 without cost increase, or a further "
                    "family B'''"),
                "empirical_probe_only": "Panel X1 (weight-3 Tag skeletons)",
            },
        },
        "successor_definition": (
            "QG-7c := close L4b and L4c; if both close, L5 inherits closure "
            "and C_DP == min(C_D+, f_B', f_B'') becomes all-n; this section "
            "states the obligations and proves nothing new"),
    }


# ---- receipt bindings and gates ----------------------------------------------

def bind_receipts(qg7_rec, qg5b_rec) -> dict[str, Any]:
    qg7_protocol_path = (
        Path(__file__).resolve().parents[3]
        / "development" / "orion-qg-regime-geometry"
        / "QG7_BPRIME_COMPLETENESS_PROTOCOL_V1.md")
    qg7_sha_now = hashlib.sha256(qg7_protocol_path.read_bytes()).hexdigest()
    a1 = qg7_rec["arm1_hostile_search"]
    qg7_bound = (
        qg7_rec["authority"] == QG7_AUTHORITY
        and qg7_rec["terminal"] == QG7_TERMINAL
        and qg7_rec["protocol_sha256"] == QG7_PROTOCOL_SHA
        and qg7_sha_now == QG7_PROTOCOL_SHA
        and int(a1["instances_evaluated_total"]) == 740
        and int(a1["fourth_regime_candidates_total"]) == 64
        and int(a1["fourth_regime_confirmed_total"]) == 64
        and len(a1["fourth_regime_candidates_verbatim"]) == 64
    )
    pb = qg5b_rec["panels"]["panel_b_structured_n2"]
    pc = qg5b_rec["panels"]["panel_c_fresh_seeded"]
    qg5b_bound = (
        qg5b_rec["authority"] == QG5B_AUTHORITY
        and int(qg5b_rec["q1"]["dp_compared_instances_total"]) == 9547
        and qg5b_rec["q2"]["outcome"] == "Q2_ENLARGED_BORROW_CLOSES"
        and int(pb["instances"]) == 9261
        and int(pb["q2_zero_error_count"]) == 9261
        and int(pc["instances"]) == 240
        and int(pc["q2_zero_error_count"]) == 240
    )
    r6s_rec = json.loads(
        (ORION_Q_DIR / "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json").read_text())
    r6s_bound = str(r6s_rec["authority"]).startswith(R6S_AUTHORITY_PREFIX)
    return {
        "qg7_receipt_bound": bool(qg7_bound),
        "qg7_authority": qg7_rec["authority"],
        "qg7_protocol_sha256_recomputed": qg7_sha_now,
        "qg5b_receipt_bound": bool(qg5b_bound),
        "qg5b_authority": qg5b_rec["authority"],
        "r6s_receipt_bound": bool(r6s_bound),
        "r6s_authority": r6s_rec["authority"],
    }


CLAIM_BOUNDARY = {
    "covers": (
        "The frozen closed-form family B'' (weight-2-Tag + phantom-borrow "
        "hybrids, two distinct tag anchors, phantom support-two frames "
        "borrowing their label-1 syndrome at an existing tag qubit) with a "
        "proof-carrying witness verifier, and the identity C_DP == C_D++ == "
        "min(C_D+, f_B', f_B'') tested on the frozen finite domains: the 64 "
        "QG-7 witnesses verbatim, the re-evaluated QG-7 H1-H5 panels, the "
        "QG-5b structured n=2 slice and fresh seeded panel, and a frozen "
        "adversarial anti-B'' panel."
    ),
    "proven_components": (
        "C_DP <= C_D++ <= C_D+ (family containment, asserted per instance); "
        "C_DP <= f_B' and C_DP <= f_B'' (B'/B'' members are feasible frozen-"
        "grammar configurations; referee-asserted on every exactly computed "
        "row); C_DP == C_D++ for all n (committed machine-checked MAX-R6S "
        "theorem, re-bound here); the pinch min(C_D+, f_B') == C_D++ implies "
        "covered_min == C_D++ regardless of the exact f_B'' value."
    ),
    "machine_evidenced_only": (
        "The completeness of D+ union B' union B'' is machine-evidenced only "
        "on the frozen finite domains; the all-n identity remains CONJECTURE "
        "gated by the Q3 obligations L4b (weight-<=2-Tag consolidation of "
        "the tag-supported-phantom, double-borrow, cyclic-borrow and "
        "l1-phantom shapes) and L4c (tag-weight bound for weight->=3 Tags). "
        "A finite panel cannot authorize the all-n theorem."
    ),
    "does_not_cover": (
        "Other objectives, other grammars, rotation-count trade-offs, "
        "chemistry subjects (no chemistry data is read in this lane), the "
        "protected stretched-N2 subject, or any donor/R6 novelty credit."
    ),
}

AUTHORITY = {
    "CLOSES": (
        "ORIONQG_QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS__"
        "WEIGHT2_TAG_PHANTOM_BORROW_BSECOND__NOT_R6"),
    "FIFTH": (
        "ORIONQG_QG7B_FIFTH_CONFIGURATION_FOUND__"
        "HOSTILE_SEARCH_WITNESS_REFEREE_CONFIRMED__NOT_R6"),
    "CANNOT": (
        "ORIONQG_QG7B_CANNOT_CHECK__REFEREE_OR_INTEGRITY_FAILURE__NOT_R6"),
}


# ---- main --------------------------------------------------------------------

def main() -> dict[str, Any]:
    start = time.monotonic()

    # gate G1: table + enumerator bindings
    r6s_bind = r6s.bind_tables()
    my_f3 = np.zeros((4, 4, 4), dtype=np.int64)
    for a in range(4):
        for b in range(4):
            for cc in range(4):
                my_f3[a, b, cc] = qg7.f3_local(a, b, cc)
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

    qg7_rec = load_qg7_receipt()
    qg5b_rec = load_qg5b_receipt()
    bindings = bind_receipts(qg7_rec, qg5b_rec)

    ledger = Ledger()
    sample_rows: list = []
    seconds = {}

    t0 = time.monotonic()
    w_summary = panel_w(qg7_rec, ledger)
    seconds["panel_w"] = round(time.monotonic() - t0, 3)

    t0 = time.monotonic()
    h_summary = panel_h(qg7_rec, ledger, sample_rows)
    seconds["panel_h"] = round(time.monotonic() - t0, 3)

    t0 = time.monotonic()
    s_summary = panel_s(ledger, sample_rows)
    seconds["panel_s"] = round(time.monotonic() - t0, 3)

    t0 = time.monotonic()
    f_summary = panel_f(qg5b_rec, ledger, sample_rows)
    seconds["panel_f"] = round(time.monotonic() - t0, 3)

    t0 = time.monotonic()
    x_summary = panel_x(ledger, sample_rows)
    seconds["panel_x"] = round(time.monotonic() - t0, 3)

    q3 = q3_obligations(qg7_rec)

    c = ledger.counters
    fifth_total = ledger.uncovered
    fifth_confirmed = sum(
        1 for f in ledger.fifth_candidates if f["replay_confirmed"])

    gates = {
        "G1_tables_bound": bool(tables_bound),
        "G2_qg7_receipt_bound": (
            bindings["qg7_receipt_bound"]
            and not w_summary["receipt_binding_failures"]
            and not h_summary["receipt_binding_failures"]
            and h_summary["instances_evaluated_total"] == 740),
        "G3_qg5b_receipt_bound": (
            bindings["qg5b_receipt_bound"]
            and f_summary["refuting_instance_bound"]
            and s_summary["instances"] == 9261
            and f_summary["instances"] == 240),
        "G4_witness_referees_pass": (
            not c["dxx_witness_failures"]
            and not c["bprime_witness_failures"]
            and not c["bsecond_witness_failures"]),
        "G5_sandwich_and_soundness_pass": not ledger.hard_failures,
        "G6_exact_matcher_binding_pass": not c["exact_matcher_failures"],
        "G7_no_r6s_contradiction": not ledger.contradictions,
        "G8_enumeration_counts_complete": (
            s_summary["instances"] == 9261
            and f_summary["instances"] == 240
            and h_summary["instances_evaluated_total"] == 740
            and all("cap_hit" in p for p in h_summary["panels"].values())
            and all("cap_hit" in p for p in x_summary["panels"].values())
            and not c["containment_failures"]
            and not c["replay_failures"]),
        "G9_witness_coverage_accounted": (
            w_summary["witnesses_bound"] == 64
            and w_summary["covered_count"]
            + sum(1 for r in w_summary["rows"]
                  if not r["covered_by_bsecond"]) == 64),
    }
    integrity_ok = all(gates.values())

    all_covered = (
        ledger.uncovered == 0
        and w_summary["all_covered"]
        and s_summary["covered_count"] == s_summary["instances"]
        and f_summary["covered_count"] == f_summary["instances"]
        and h_summary["covered_total"] == h_summary["instances_evaluated_total"]
        and x_summary["covered_total"] == x_summary["instances_evaluated_total"]
    )

    if fifth_confirmed > 0 and integrity_ok:
        terminal = "QG7B_FIFTH_CONFIGURATION_FOUND"
        authority = AUTHORITY["FIFTH"]
        responsibility = (
            "RESP:FIFTH_SUPPORT2_CONFIGURATION_WITNESS_CONFIRMED_BY_"
            "INDEPENDENT_REFEREES__SERIALIZED_VERBATIM")
    elif fifth_total > 0 or ledger.contradictions or not integrity_ok \
            or not all_covered:
        terminal = "QG7B_CANNOT_CHECK"
        authority = AUTHORITY["CANNOT"]
        responsibility = (
            "RESP:REFEREE_OR_INTEGRITY_FAILURE__EVERYTHING_SERIALIZED_"
            "VERBATIM")
    else:
        terminal = "QG7B_HYBRID_FAMILY_CLOSES_ON_VERIFIED_DOMAINS"
        authority = AUTHORITY["CLOSES"]
        responsibility = (
            "RESP:BSECOND_COVERS_ALL_64_WITNESSES_AND_ALL_PANEL_GAPS__"
            "IDENTITY_MIN_DPLUS_BPRIME_BSECOND_EQUALS_CDP_ON_VERIFIED_"
            "DOMAINS__ALL_N_REMAINS_CONJECTURE_VIA_L4B_L4C")

    result = {
        "schema": "ORIONQG.QG7B.HybridFamily.v1",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "lane": "QG-7b frozen hybrid-family closed form (wave-2 successor)",
        "protocol": "QG7B_HYBRID_FAMILY_PROTOCOL_V1",
        "protocol_sha256": protocol_sha,
        "base_revision": BASE_REVISION,
        "authority": authority,
        "terminal": terminal,
        "responsibility": responsibility,
        "scope": (
            "FROZEN_HYBRID_FAMILY_BSECOND_COMPLETENESS_RETEST__"
            "WEIGHT2_TAG_PHANTOM_BORROW__UNIT_SUPPORT_COUNT_OBJECTIVE_ONLY__"
            "NOT_R6"),
        "question": (
            "Does the frozen closed-form family B'' (weight-2-Tag + phantom "
            "borrow, delimited by QG-7's L4a classification) restore the "
            "closed-form identity C_DP == C_D++ == min(C_D+, f_B', f_B'') "
            "on the QG-7 witness set, the re-evaluated QG-7 panels, the "
            "QG-5b domains, and a fresh frozen adversarial anti-B'' panel — "
            "or does a fifth support-two configuration exist?"),
        "q1_family": {
            "bsecond_definition": (
                "B''(t): Tag s = v_a@q_a . v_b@q_b over distinct qubits of "
                "the pool (union target support plus up to two empty "
                "representatives); per block, anchored (v@q, c@q) at a tag "
                "qubit (extra 0) or phantom (m0@q_h, ell@q_x . m1@q_h) with "
                "home q_h off the tag pair and borrow point q_x on it "
                "(extra 2); at least one phantom; centrals (1,1,1); value = "
                "min(sum extras + branch F3) + 4 == r6s.config_cost of the "
                "induced configuration; infeasible for every n <= 2"),
            "witness_verifier": (
                "verify_bsecond_witness: frozen shape predicate + "
                "r6s.config_labels == (0,1) + r6s.config_cost equality; "
                "run on 100% of exactly computed finite f_B'' values"),
            "soundness": (
                "structural (every member is a feasible frozen-grammar "
                "configuration) plus per-row referee assertion"),
        },
        "q2": {
            "panel_w_witnesses": w_summary,
            "panel_h_qg7_reevaluated": h_summary,
            "panel_s_structured_n2": s_summary,
            "panel_f_fresh_seeded": f_summary,
            "panel_x_adversarial": x_summary,
            "instances_total": ledger.instances_total,
            "covered_without_bsecond": ledger.covered_without_bsecond,
            "covered_by_bsecond": ledger.covered_by_bsecond,
            "uncovered_total": ledger.uncovered,
            "bsecond_exact_rows": ledger.bsecond_exact_rows,
            "bsecond_pinched_rows": ledger.bsecond_pinched_rows,
            "pinch_policy": (
                "f_B'' exact on every Panel W row, every gap row "
                "(C_D++ < min(C_D+, f_B')), and frozen strides (H/X gidx%32, "
                "S idx%64, F i%64); elsewhere the structural pinch "
                "C_D++ == C_DP <= f_B'' decides the identity (R6P/QG-5b "
                "precedent); counts disclosed above"),
            "fifth_configuration_candidates_total": int(fifth_total),
            "fifth_configuration_confirmed_total": int(fifth_confirmed),
            "fifth_candidates_verbatim": ledger.fifth_candidates,
            "r6s_contradictions_verbatim": ledger.contradictions,
            "hard_assertion_failures_verbatim": ledger.hard_failures,
            "verbatim_cap": VERBATIM_CAP,
        },
        "q3_toward_all_n": q3,
        "verification_sample": sample_rows,
        "receipt_bindings": bindings,
        "hostile_referee": dict(c),
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
        raise AssertionError("QG7B authority ceiling violated")
    digest = hashlib.sha256(canonical_json(result).encode()).hexdigest()
    result["result_digest"] = digest

    runtime = round(time.monotonic() - start, 3)
    timing = {
        "convention": (
            "R6P: timing fields excluded from the canonical stdout line and "
            "the result digest; present only in this file section and on "
            "stderr"),
        "panel_seconds": seconds,
        "runtime_seconds": runtime,
        "runtime_cap_seconds": 1500,
        "runtime_under_cap": runtime < 1500,
    }
    print("ORIONQG_QG7B_HYBRID_FAMILY=" + canonical_json(result))
    file_result = dict(result)
    file_result["timing"] = timing
    Path(__file__).with_name("QG7B_HYBRID_FAMILY_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n")
    print("qg7b_runtime_seconds=%.3f" % runtime, file=sys.stderr)
    print("qg7b_timing_summary=" + canonical_json(
        {k: v for k, v in timing.items() if k != "convention"}),
        file=sys.stderr)
    return result


if __name__ == "__main__":
    main()
