#!/usr/bin/env python3
"""ORION-QG QG-5b: exact support-<=2-family forecaster + enlarged borrow family.

Frozen by development/orion-qg-regime-geometry/QG5B_EXACT_FORECASTER_PROTOCOL.md
(frozen BEFORE any outcome under that protocol was computed).

Q1: the theorem-backed exact forecaster F2(t) := C_Dxx(t), the exact minimum
over the FULL support-<=2 family D++ (frozen independent enumerator
r6p.dxx_search; no unrestricted DP call), tested for F2 == C_DP on the QG-5
refuting instance, the exhaustive structured n=2 slice, the QG-5 fresh seeded
panel (seed 20260826) and the receipted chemistry rows (via the R6P exact
containment pinch at n >= 8). Expected exact everywhere by the machine-checked
MAX-R6S theorem (C_DP == C_Dxx for all n); any violation is a first-class
refutation and is serialized verbatim.

Q2: the enlarged closed-form borrow family B'(t) -- identical to the frozen
R6Q family B(t) except that each phantom block's borrow home qubit ranges over
the UNION target support (plus one empty representative), admitting the
out-of-support borrow homes the QG-5 counterexample exposed. Tested for
min(C_R6L, C_Dplus, f_Bprime) == C_DP on the same panels; a residual gap is a
FOURTH-configuration discovery, serialized verbatim.

Q3: forecast-vs-DP timing on the fresh panel (timing on stderr / RESULTS only,
excluded from the canonical stdout line per the R6P convention).

All frozen machinery imported UNMODIFIED. Authority ceiling NOT_R6.
"""
from __future__ import annotations

import itertools
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ORION_Q_DIR = Path(__file__).resolve().parents[1] / "orion-q"
sys.path.insert(0, str(ORION_Q_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402
import max_r6r_prospective_fresh_subject as r6r  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import qg5_certified_forecast as qg5  # noqa: E402

INF = r6q.INF
BIG = np.int32(INF)
MATCHING = r6q.MATCHING
SEED_FRESH = qg5.SEED_FRESH  # 20260826
PANEL_PER_N = 120
VERBATIM_CAP = 100
PROTOCOL_NAME = "QG5B_EXACT_FORECASTER_PROTOCOL.md"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _supp_mask(key) -> int:
    return key[0] | key[1]


def _qubits(mask: int):
    out = []
    q = 0
    while mask >> q:
        if (mask >> q) & 1:
            out.append(q)
        q += 1
    return out


# ---- the enlarged borrow family B'(t) ---------------------------------------

_bprime_block_cache: dict[tuple, tuple] = {}


def _bprime_block_options(tp_j, n: int, q_t: int, v: int, rel: tuple, homes: tuple):
    """Per-block option arrays for the enlarged borrow family B' at Tag v@q_t.

    Structurally identical to the frozen r6q._borrow_block_options except that
    phantom homes range over the frozen `homes` tuple (union target support
    plus one empty representative, q_t excluded) instead of the block's own
    target support. Returns (extra, letters, meta, n_anchored) with the
    anchored options first; meta rows are
    (kind, sigma, frame_comm, frame_anti, extra).
    """
    key = (tp_j, n, q_t, v, rel, homes)
    hit = _bprime_block_cache.get(key)
    if hit is not None:
        return hit
    others = tuple(c for c in (1, 2, 3) if c != v)
    v_key = r6o._letter_key(v, q_t)
    rows = []
    # anchored at q_t: frames (v@q_t, c@q_t)
    for c in others:
        c_key = r6o._letter_key(c, q_t)
        for sigma in (0, 1):
            t_comm = p10.mul(tp_j[sigma], v_key)
            t_anti = p10.mul(tp_j[1 - sigma], c_key)
            rows.append((0, t_comm, t_anti, ("anchored", sigma, v_key, c_key, 0)))
    n_anchored = len(rows)
    # phantom with home anywhere in the frozen home pool (ENLARGEMENT)
    for q_h in homes:
        if q_h == q_t:
            raise AssertionError("qg5b home pool must exclude the Tag qubit")
        for ell in others:
            ell_key = r6o._letter_key(ell, q_t)
            for m0 in (1, 2, 3):
                m0_key = r6o._letter_key(m0, q_h)
                for m1 in (1, 2, 3):
                    if m1 == m0:
                        continue
                    anti_frame = p10.mul(ell_key, r6o._letter_key(m1, q_h))
                    for sigma in (0, 1):
                        t_comm = p10.mul(tp_j[sigma], m0_key)
                        t_anti = p10.mul(tp_j[1 - sigma], anti_frame)
                        rows.append(
                            (
                                2,
                                t_comm,
                                t_anti,
                                ("phantom", sigma, m0_key, anti_frame, 2),
                            )
                        )
    extra = np.array([r[0] for r in rows], dtype=np.int32)
    letters = np.empty((len(rows), 2, len(rel)), dtype=np.int8)
    for i, (_, t_comm, t_anti, _meta) in enumerate(rows):
        for qi, q in enumerate(rel):
            letters[i, 0, qi] = r6o._local_code(t_comm, q)
            letters[i, 1, qi] = r6o._local_code(t_anti, q)
    # dedupe within the anchored and phantom classes separately (extra is
    # constant per class, so duplicate letter signatures are exact duplicates)
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
    _bprime_block_cache[key] = out
    return out


def bprime_family_min(target_pairs, n: int, want_witness: bool = False):
    """f_B': exact minimum over the enlarged borrow family (>=1 phantom block).

    Returns (value_or_None, witness_or_None). Deterministic: strict-improvement
    updates over a frozen sweep order, flat argmin tie-break.
    """
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= _supp_mask(pair[0]) | _supp_mask(pair[1])
    u_qubits = _qubits(union)
    pool = list(u_qubits)
    for q in range(n):
        if not (union >> q) & 1:
            pool.append(q)  # single empty representative
            break
    pool = sorted(pool)
    q_tags = list(u_qubits) + [q for q in pool if q not in u_qubits]
    rel = tuple(pool)
    best = None
    best_wit = None
    for q_t in q_tags:
        homes = tuple(q for q in pool if q != q_t)
        if not homes:
            continue
        for v in (1, 2, 3):
            per_block = [
                _bprime_block_options(tp[j], n, q_t, v, rel, homes) for j in range(3)
            ]
            if all(opt[0].shape[0] == opt[3] for opt in per_block):
                continue  # no phantom option anywhere: not a borrow point
            (ea, la, ma, naa), (eb, lb, mb, nab), (ec, lc, mc, nac) = per_block
            tot = (
                ea[:, None, None].astype(np.int32)
                + eb[None, :, None]
                + ec[None, None, :]
            )
            for k in range(2):
                for qi in range(len(rel)):
                    tot = tot + r6q.F3[
                        la[:, k, qi][:, None, None],
                        lb[:, k, qi][None, :, None],
                        lc[:, k, qi][None, None, :],
                    ]
            # exclude the all-anchored corner (that is R6L at q_t, not borrow)
            tot[:naa, :nab, :nac] = BIG
            value = int(tot.min())
            if value < INF:
                value += 2  # weight-one Tag
                if best is None or value < best:
                    best = value
                    if want_witness:
                        flat = int(np.argmin(tot))
                        ia, ib, ic = np.unravel_index(
                            flat, (tot.shape[0], tot.shape[1], tot.shape[2])
                        )
                        best_wit = {
                            "q_t": int(q_t),
                            "v": int(v),
                            "value": int(value),
                            "blocks": [
                                {
                                    "block": "ABC"[j],
                                    "kind": meta_row[0],
                                    "sigma": int(meta_row[1]),
                                    "frame_comm": list(meta_row[2]),
                                    "frame_anti": list(meta_row[3]),
                                    "extra": int(meta_row[4]),
                                }
                                for j, meta_row in enumerate(
                                    (ma[int(ia)], mb[int(ib)], mc[int(ic)])
                                )
                            ],
                        }
    return best, best_wit


def verify_bprime_witness(target_pairs, n: int, wit: dict[str, Any]):
    """Referee the B' argmin member through the committed R6S config machinery."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    s = r6o._letter_key(wit["v"], wit["q_t"])
    frames6 = []
    t6 = []
    any_phantom = False
    for j, blk in enumerate(wit["blocks"]):
        frames6.extend([tuple(blk["frame_comm"]), tuple(blk["frame_anti"])])
        t6.extend([tp[j][blk["sigma"]], tp[j][1 - blk["sigma"]]])
        if blk["kind"] == "phantom":
            any_phantom = True
    if not any_phantom:
        return False
    ok, labels = r6s.config_labels(tuple(frames6), s)
    if not ok or labels != (0, 1):
        return False
    cost = r6s.config_cost(tuple(t6), tuple(frames6), s, (1, 1, 1), n)
    return int(cost) == int(wit["value"])


def _bprime_witness_homes(target_pairs, wit: dict[str, Any]):
    """Per phantom block: home qubit + whether it lies outside the block's
    own target support (the mechanism the QG-5 counterexample exposed)."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    out = []
    for j, blk in enumerate(wit["blocks"]):
        if blk["kind"] != "phantom":
            continue
        comm = tuple(blk["frame_comm"])
        homes = _qubits(_supp_mask(comm))
        supp_j = set(_qubits(_supp_mask(tp[j][0]) | _supp_mask(tp[j][1])))
        for q_h in homes:
            out.append(
                {
                    "block": blk["block"],
                    "home_qubit": int(q_h),
                    "outside_own_target_support": q_h not in supp_j,
                }
            )
    return out


# ---- per-instance evaluation -------------------------------------------------

def _clear_instance_caches() -> None:
    r6m._local_table.cache_clear()
    r6o._block_cache.clear()
    r6q._borrow_block_cache.clear()
    _bprime_block_cache.clear()


def evaluate(target_pairs, n: int, c_dp: int, where):
    """All QG-5b per-instance quantities + inline hard assertions."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    fc = qg5.forecast(tp, n)  # C_R6L, C_Dplus, f_B, regime, P1 -- verbatim QG-5
    dxx = r6p.dxx_search(tp, n, want_witness=True)
    f2 = int(dxx["C_Dxx"])
    fbp, fbp_wit = bprime_family_min(tp, n, want_witness=True)
    fbp_eff = INF if fbp is None else int(fbp)
    # sandwich + soundness (gate 8, hard-asserted)
    if not (c_dp <= f2 <= fc["C_Dplus"] <= fc["C_R6L"]):
        raise AssertionError(
            {"qg5b_sandwich_violated": [where, c_dp, f2, fc["C_Dplus"], fc["C_R6L"]]}
        )
    if c_dp > fbp_eff:
        raise AssertionError({"qg5b_bprime_soundness_violated": [where, c_dp, fbp_eff]})
    if fc["f_B"] < INF and fbp_eff > fc["f_B"]:
        raise AssertionError(
            {"qg5b_bprime_containment_violated": [where, fbp_eff, fc["f_B"]]}
        )
    q2_min = min(fc["C_R6L"], fc["C_Dplus"], fbp_eff)
    if f2 == fc["C_R6L"]:
        regime = "donor_exact"
    elif f2 == fc["C_Dplus"]:
        regime = "split"
    elif f2 == fbp_eff:
        regime = "borrow"
    else:
        regime = "beyond_enlarged_family"
    return {
        "C_DP": int(c_dp),
        "F2_C_Dxx": f2,
        "C_R6L": int(fc["C_R6L"]),
        "C_Dplus": int(fc["C_Dplus"]),
        "f_B": int(fc["f_B"]),
        "f_Bprime": fbp_eff,
        "q2_min": int(q2_min),
        "q1_error": f2 - int(c_dp),
        "q2_error": int(q2_min) - int(c_dp),
        "regime_f2": regime,
        "qg5_regime": fc["regime"],
        "qg5_predicted_C_DP": int(fc["predicted_C_DP"]),
        "predicate_P1": bool(fc["certificate"]["predicate_P1"]),
        "predicate_P1prime": (fc["C_Dplus"] == fc["C_R6L"])
        and (fbp_eff >= fc["C_R6L"]),
        "f2_donor_predicate": f2 == fc["C_R6L"],
        "truth_donor_exact": int(c_dp) == fc["C_R6L"],
        "_dxx_witness": dxx["witness"],
        "_bprime_witness": fbp_wit,
    }


def _row_public(row):
    return {k: v for k, v in row.items() if not k.startswith("_")}


def _verify_dxx(tp, n, row, where, counters):
    counters["dxx_witness_rows"] += 1
    if not r6p.verify_dxx_witness(tp, n, row["_dxx_witness"]):
        counters["dxx_witness_failures"].append(where)


def _verify_bprime(tp, n, row, where, counters):
    if row["f_Bprime"] >= INF:
        counters["bprime_witness_exempt_infeasible"] += 1
        return
    counters["bprime_witness_rows"] += 1
    if not verify_bprime_witness(tp, n, row["_bprime_witness"]):
        counters["bprime_witness_failures"].append(where)


def _new_counters():
    return {
        "dxx_witness_rows": 0,
        "dxx_witness_failures": [],
        "bprime_witness_rows": 0,
        "bprime_witness_failures": [],
        "bprime_witness_exempt_infeasible": 0,
        "weight1_rows": 0,
        "weight1_failures": [],
        "exact_matcher_rows": 0,
        "exact_matcher_failures": [],
    }


# ---- Panel A: the QG-5 refuting instance ------------------------------------

def load_refuting_receipt_row():
    receipt = json.loads(
        (Path(__file__).with_name("QG5_CERTIFIED_FORECAST_RESULTS.json")).read_text()
    )
    errs = receipt["benchmark"]["fresh_seeded_panel"]["nonzero_errors_verbatim"]
    if len(errs) != 1:
        raise AssertionError("qg5b expects exactly one QG-5 refuting instance")
    return receipt, errs[0]


def panel_a(rec_row, counters):
    tp = tuple(
        (tuple(int(x) for x in a), tuple(int(x) for x in b))
        for a, b in rec_row["target_pairs"]
    )
    n = int(rec_row["n"])
    _clear_instance_caches()
    terms = r6m._synthetic_terms(tp)
    c_dp_configs = int(r6o.dp_cost_frozen_configs(terms, n))
    dp_wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
    c_dp_exact = int(dp_wit["C_R6M"])
    dp_witness_checks = all(dp_wit["checks"].values())
    row = evaluate(tp, n, c_dp_configs, ["panel_a"])
    _verify_dxx(tp, n, row, ["panel_a"], counters)
    _verify_bprime(tp, n, row, ["panel_a"], counters)
    receipt_bound = (
        c_dp_configs == int(rec_row["C_DP"])
        and c_dp_exact == int(rec_row["C_DP"])
        and row["C_R6L"] == int(rec_row["C_R6L"])
        and row["C_Dplus"] == int(rec_row["C_Dplus"])
        and row["f_B"] == int(rec_row["f_B"])
        and row["qg5_predicted_C_DP"] == int(rec_row["predicted_C_DP"])
        and dp_witness_checks
    )
    bprime_wit = row["_bprime_witness"]
    summary = {
        "n": n,
        "index_in_fresh_panel": int(rec_row["index"]),
        "target_pairs": [[list(a), list(b)] for a, b in tp],
        "C_DP_frozen_configs": c_dp_configs,
        "C_DP_exact_witnessed_matcher": c_dp_exact,
        "dp_witness_checks_pass": dp_witness_checks,
        "receipt_row_bound": receipt_bound,
        **_row_public(row),
        "bprime_witness_verbatim": bprime_wit,
        "bprime_witness_homes": (
            _bprime_witness_homes(tp, bprime_wit) if bprime_wit is not None else []
        ),
        "dxx_witness_verbatim": row["_dxx_witness"],
    }
    return summary, row, tp


# ---- Panel B: exhaustive structured n=2 -------------------------------------

def panel_b(counters):
    wt1 = [r6o._letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    q1_errors, q2_errors = [], []
    census = {"donor_exact": 0, "split": 0, "borrow": 0, "beyond_enlarged_family": 0}
    f2_pred_mismatch = []
    bind_rows = []
    q1_zero = q2_zero = 0
    dp_times, f2_times = [], []
    idx = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        tp = tuple((wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic))
        t0 = time.perf_counter()
        c_dp = r6o.dp_cost_n2_reader(tp)
        t1 = time.perf_counter()
        row = evaluate(tp, 2, c_dp, ["panel_b", idx])
        t2 = time.perf_counter()
        dp_times.append(t1 - t0)
        f2_times.append(t2 - t1)
        if row["q1_error"] == 0:
            q1_zero += 1
        elif len(q1_errors) < VERBATIM_CAP:
            q1_errors.append(
                {
                    "instance_index": idx,
                    "target_pairs": [[list(a), list(b)] for a, b in tp],
                    **{
                        k: row[k]
                        for k in ("C_DP", "F2_C_Dxx", "C_R6L", "C_Dplus", "f_Bprime")
                    },
                }
            )
        if row["q2_error"] == 0:
            q2_zero += 1
        elif len(q2_errors) < VERBATIM_CAP:
            q2_errors.append(
                {
                    "instance_index": idx,
                    "target_pairs": [[list(a), list(b)] for a, b in tp],
                    **{
                        k: row[k]
                        for k in (
                            "C_DP", "F2_C_Dxx", "C_R6L", "C_Dplus", "f_B",
                            "f_Bprime", "q2_min",
                        )
                    },
                    "dxx_witness": row["_dxx_witness"],
                }
            )
        census[row["regime_f2"]] += 1
        if row["f2_donor_predicate"] != row["truth_donor_exact"] and len(
            f2_pred_mismatch
        ) < VERBATIM_CAP:
            f2_pred_mismatch.append({"instance_index": idx})
        if idx % 97 == 0 or row["F2_C_Dxx"] < row["C_Dplus"]:
            _verify_dxx(tp, 2, row, ["panel_b", idx], counters)
        if idx % 191 == 0 or row["f_Bprime"] < min(row["C_R6L"], row["C_Dplus"]):
            _verify_bprime(tp, 2, row, ["panel_b", idx], counters)
        if idx % 210 == 0:
            counters["weight1_rows"] += 1
            if int(r6p.dxx_search(tp, 2, max_weight=1)["C_Dxx"]) != row["C_Dplus"]:
                counters["weight1_failures"].append(["panel_b", idx])
        if idx % 1153 == 0:
            counters["exact_matcher_rows"] += 1
            terms = r6m._synthetic_terms(tp)
            wit = r6m.exact_r6m_matching(terms, MATCHING, 2, list(range(6)))
            if int(wit["C_R6M"]) != c_dp or not all(wit["checks"].values()):
                counters["exact_matcher_failures"].append(["panel_b", idx])
        bind_rows.append({"instance_index": idx, "C_DP": c_dp, "C_Dplus": row["C_Dplus"]})
        idx += 1
    r6m._local_table.cache_clear()
    binding = r6q.bind_training_to_receipt(bind_rows)
    summary = {
        "instances": idx,
        "dp_truth": "r6o.dp_cost_n2_reader (committed unrestricted DP reader)",
        "q1_zero_error_count": q1_zero,
        "q1_nonzero_error_count": idx - q1_zero,
        "q1_nonzero_errors_verbatim": q1_errors,
        "q2_zero_error_count": q2_zero,
        "q2_nonzero_error_count": idx - q2_zero,
        "q2_nonzero_errors_verbatim": q2_errors,
        "verbatim_cap": VERBATIM_CAP,
        "f2_regime_census": census,
        "f2_donor_predicate_mismatches": f2_pred_mismatch,
        "r6o_receipt_binding": binding,
    }
    return summary, dp_times, f2_times


# ---- Panel C: fresh seeded panel (seed 20260826) ----------------------------

def panel_c(rec_row, receipt, counters):
    rec_panel = receipt["benchmark"]["fresh_seeded_panel"]
    rng = np.random.default_rng(SEED_FRESH)
    q1_errors, q2_errors = [], []
    census = {"donor_exact": 0, "split": 0, "borrow": 0, "beyond_enlarged_family": 0}
    qg5_census = {"donor_exact": 0, "split": 0, "borrow": 0}
    f2_pred_mismatch = []
    qg5_nonzero_rows = []
    q1_zero = q2_zero = 0
    dp_times, f2_times, qg5_times = [], [], []
    refuting_seen_bound = False
    total = 0
    for n in (2, 3):
        for i in range(PANEL_PER_N):
            targets = []
            for _ in range(6):
                while True:
                    x = int(rng.integers(0, 2 ** n))
                    z = int(rng.integers(0, 2 ** n))
                    if (x, z) != (0, 0):
                        break
                targets.append((x, z))
            tp = tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))
            terms = r6m._synthetic_terms(tp)
            r6m._local_table.cache_clear()
            t0 = time.perf_counter()
            c_dp = int(r6o.dp_cost_frozen_configs(terms, n))
            t1 = time.perf_counter()
            t_f2a = time.perf_counter()
            f2_probe = int(r6p.dxx_search(tp, n)["C_Dxx"])
            t_f2b = time.perf_counter()
            _clear_instance_caches()
            t_qa = time.perf_counter()
            fc_probe = qg5.forecast(tp, n)
            t_qb = time.perf_counter()
            _clear_instance_caches()
            row = evaluate(tp, n, c_dp, ["panel_c", n, i])
            if f2_probe != row["F2_C_Dxx"] or int(
                fc_probe["predicted_C_DP"]
            ) != row["qg5_predicted_C_DP"]:
                raise AssertionError({"qg5b_panel_c_probe_mismatch": [n, i]})
            dp_times.append(t1 - t0)
            f2_times.append(t_f2b - t_f2a)
            qg5_times.append(t_qb - t_qa)
            where = ["panel_c", n, i]
            if row["q1_error"] == 0:
                q1_zero += 1
            elif len(q1_errors) < VERBATIM_CAP:
                q1_errors.append(
                    {
                        "n": n,
                        "index": i,
                        "target_pairs": [[list(a), list(b)] for a, b in tp],
                        **{
                            k: row[k]
                            for k in (
                                "C_DP", "F2_C_Dxx", "C_R6L", "C_Dplus", "f_Bprime",
                            )
                        },
                    }
                )
            if row["q2_error"] == 0:
                q2_zero += 1
            elif len(q2_errors) < VERBATIM_CAP:
                q2_errors.append(
                    {
                        "n": n,
                        "index": i,
                        "target_pairs": [[list(a), list(b)] for a, b in tp],
                        **{
                            k: row[k]
                            for k in (
                                "C_DP", "F2_C_Dxx", "C_R6L", "C_Dplus", "f_B",
                                "f_Bprime", "q2_min",
                            )
                        },
                        "dxx_witness": row["_dxx_witness"],
                    }
                )
            census[row["regime_f2"]] += 1
            qg5_census[row["qg5_regime"]] += 1
            if row["qg5_predicted_C_DP"] != c_dp:
                qg5_nonzero_rows.append(
                    {
                        "n": n,
                        "index": i,
                        "target_pairs": [[list(a), list(b)] for a, b in tp],
                        "C_DP": c_dp,
                        "C_R6L": row["C_R6L"],
                        "C_Dplus": row["C_Dplus"],
                        "f_B": row["f_B"],
                        "qg5_predicted_C_DP": row["qg5_predicted_C_DP"],
                    }
                )
            if row["f2_donor_predicate"] != row["truth_donor_exact"] and len(
                f2_pred_mismatch
            ) < VERBATIM_CAP:
                f2_pred_mismatch.append({"n": n, "index": i})
            if i % 10 == 0 or row["F2_C_Dxx"] < row["C_Dplus"]:
                _verify_dxx(tp, n, row, where, counters)
            if i % 10 == 0 or row["f_Bprime"] < min(row["C_R6L"], row["C_Dplus"]):
                _verify_bprime(tp, n, row, where, counters)
            if i % 15 == 0:
                counters["weight1_rows"] += 1
                if int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"]) != row["C_Dplus"]:
                    counters["weight1_failures"].append(where)
            if i % 24 == 0:
                counters["exact_matcher_rows"] += 1
                wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
                if int(wit["C_R6M"]) != c_dp or not all(wit["checks"].values()):
                    counters["exact_matcher_failures"].append(where)
            if n == int(rec_row["n"]) and i == int(rec_row["index"]):
                refuting_seen_bound = (
                    [[list(a), list(b)] for a, b in tp] == rec_row["target_pairs"]
                    and c_dp == int(rec_row["C_DP"])
                )
            total += 1
    qg5_receipt_bound = (
        len(qg5_nonzero_rows) == int(rec_panel["nonzero_error_count"])
        and total - len(qg5_nonzero_rows) == int(rec_panel["forecast_error_zero_count"])
        and qg5_census == rec_panel["predicted_regime_census"]
        and len(qg5_nonzero_rows) == 1
        and qg5_nonzero_rows[0]["n"] == int(rec_row["n"])
        and qg5_nonzero_rows[0]["index"] == int(rec_row["index"])
        and qg5_nonzero_rows[0]["target_pairs"] == rec_row["target_pairs"]
        and refuting_seen_bound
    )
    summary = {
        "seed": SEED_FRESH,
        "instances": total,
        "generator": "digit-frozen copy of the QG-5 fresh panel (120 per n, n in {2,3})",
        "dp_truth": "r6o.dp_cost_frozen_configs (unrestricted frozen-config DP)",
        "q1_zero_error_count": q1_zero,
        "q1_nonzero_error_count": total - q1_zero,
        "q1_nonzero_errors_verbatim": q1_errors,
        "q2_zero_error_count": q2_zero,
        "q2_nonzero_error_count": total - q2_zero,
        "q2_nonzero_errors_verbatim": q2_errors,
        "f2_regime_census": census,
        "f2_donor_predicate_mismatches": f2_pred_mismatch,
        "qg5_three_family_recomputed": {
            "regime_census": qg5_census,
            "nonzero_error_count": len(qg5_nonzero_rows),
            "nonzero_errors_verbatim": qg5_nonzero_rows[:VERBATIM_CAP],
        },
        "qg5_receipt_bound": qg5_receipt_bound,
    }
    return summary, dp_times, f2_times, qg5_times


# ---- Panel D: receipted chemistry rows --------------------------------------

def panel_d():
    r6m_receipt = json.loads(
        (ORION_Q_DIR / "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json")
        .read_text()
    )
    r6o_receipt = json.loads(
        (ORION_Q_DIR / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json").read_text()
    )
    r6r_receipt = json.loads(
        (ORION_Q_DIR / "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json").read_text()
    )
    subjects = {}
    binding_failures = []

    def add_rows(name, path, blob, n, terms, pairs_list, six, dp_by_key,
                 r6l_by_key, dplus_by_key, extra_bind_by_key):
        rows = []
        for pairs in pairs_list:
            key = canonical_json([list(p) for p in pairs])
            c_dp = int(dp_by_key[key])
            tp = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            r6m._local_table.cache_clear()
            qg5._clear_forecast_caches()
            fc = qg5.forecast(tp, n, terms=terms, pairs=pairs, six=six)
            if fc["C_R6L"] != int(r6l_by_key[key]):
                binding_failures.append([name, key, "C_R6L"])
            if fc["C_Dplus"] != int(dplus_by_key[key]):
                binding_failures.append([name, key, "C_Dplus"])
            if extra_bind_by_key is not None:
                rec = extra_bind_by_key[key]
                if fc["f_B"] != int(rec["f_B"]) or int(
                    fc["predicted_C_DP"]
                ) != int(rec["predicted_C_DP"]):
                    binding_failures.append([name, key, "r6r_fB_or_predicted"])
            if not (c_dp <= fc["C_Dplus"] <= fc["C_R6L"]):
                raise AssertionError({"qg5b_chemistry_sandwich": [name, key]})
            pinched = fc["C_Dplus"] == c_dp
            f2 = c_dp if pinched else None
            row = {
                "matching": [list(p) for p in pairs],
                "C_DP_from_receipt": c_dp,
                "C_R6L": int(fc["C_R6L"]),
                "C_Dplus": int(fc["C_Dplus"]),
                "f_B": int(fc["f_B"]),
                "F2_status": "PINCHED_EXACT" if pinched else "UNRESOLVED_PINCH_FAILED",
                "F2_C_Dxx_pinched": f2,
                "q1_error": 0 if pinched else None,
                "q2_pinched_by_r6l": int(fc["C_R6L"]) == c_dp,
                "f2_donor_predicate": (f2 == fc["C_R6L"]) if pinched else None,
                "truth_donor_exact": c_dp == int(fc["C_R6L"]),
            }
            rows.append(row)
        subjects[name] = {
            "path": path,
            "blob": blob,
            "n_qubits": n,
            "matchings": len(rows),
            "dp_truth": "committed receipt (heavy DP never re-run)",
            "f2_by": "exact containment pinch C_DP <= C_Dxx <= C_Dplus (R6P precedent)",
            "fbprime_computed": False,
            "fbprime_note": (
                "frozen runtime cap: Q2 identity decided by the R6L pinch "
                "(C_R6L == C_DP receipt-bound) plus the B' soundness gate"
            ),
            "pinched_exact_count": sum(
                1 for r in rows if r["F2_status"] == "PINCHED_EXACT"
            ),
            "unresolved_pinch_count": sum(
                1 for r in rows if r["F2_status"] != "PINCHED_EXACT"
            ),
            "q2_pinched_by_r6l_count": sum(1 for r in rows if r["q2_pinched_by_r6l"]),
            "rows": rows,
        }

    # H4 + eq-N2 via the frozen blob-pinned batch machinery
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        terms, source_indices, _champs, _mi, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"qg5b_chemistry_blob_mismatch": name})
        n = int(cfg["n_qubits"])
        six = [int(i) for i in source_indices]
        rec_sub = r6m_receipt["subjects"][name]
        if sorted(six) != sorted(int(i) for i in rec_sub["frozen_source_indices"]):
            raise AssertionError({"qg5b_chemistry_source_indices_mismatch": name})
        rec_rows = {
            canonical_json(row["matching"]): row for row in rec_sub["candidate_points"]
        }
        r6o_rows = {
            canonical_json(row["matching"]): row
            for row in r6o_receipt["domains"]["chemistry"]["subjects"][name]["rows"]
        }
        add_rows(
            name,
            cfg["path"],
            cfg["blob"],
            n,
            terms,
            r6m.perfect_matchings(six),
            six,
            {k: v["C_R6M"] for k, v in rec_rows.items()},
            {k: v["C_R6L_same_matching"] for k, v in rec_rows.items()},
            {k: v["C_Dplus"] for k, v in r6o_rows.items()},
            None,
        )

    # Benzene DUCC2 via the frozen R6R enumeration, receipt-bound
    r6r_subject = r6r_receipt["subject"]
    listing = r6r.pinned_tree_listing()
    ducc_listing = [(p, b) for p, b in listing if p.endswith(".ducc.results.txt")]
    listing_digest = r6r.sha256_text(
        "\n".join(f"{b} {p}" for p, b in ducc_listing) + "\n"
    )
    listing_bound = listing_digest == r6r_receipt["library"]["ducc_listing_sha256"]
    if not listing_bound:
        raise AssertionError("qg5b pinned tree listing digest does not bind to R6R")
    candidates = r6r.eligible_candidates(listing)
    for cfg in candidates:
        if cfg["path"].split("/")[0] in r6r.EXCLUDED_MOLECULES:
            raise AssertionError("qg5b exclusion breached in eligible candidates")
        if cfg["path"] == r6r.PROTECTED_STRETCHED_N2_PATH:
            raise AssertionError("qg5b protected stretched-N2 leaked into candidacy")
    matches = [c for c in candidates if c["blob"] == r6r_subject["blob"]]
    if len(matches) != 1 or matches[0]["path"] != r6r_subject["path"]:
        raise AssertionError({"qg5b_r6r_subject_not_unique": len(matches)})
    cfg = matches[0]
    admit = r6r.try_admit(cfg)
    if not admit["admitted"]:
        raise AssertionError({"qg5b_r6r_subject_not_admitted": admit.get("reason")})
    n = int(cfg["n_qubits"])
    six = admit["six"]
    if sorted(six) != sorted(int(i) for i in r6r_subject["frozen_source_indices"]):
        raise AssertionError({"qg5b_r6r_source_indices_mismatch": cfg["path"]})
    r6r_rows = {
        canonical_json(row["matching"]): row for row in r6r_receipt["matchings"]
    }
    add_rows(
        "Benzene_DUCC2",
        cfg["path"],
        cfg["blob"],
        n,
        admit["terms"],
        r6m.perfect_matchings(six),
        six,
        {k: v["C_DP"] for k, v in r6r_rows.items()},
        {k: v["C_R6L"] for k, v in r6r_rows.items()},
        {k: v["C_Dplus"] for k, v in r6r_rows.items()},
        r6r_rows,
    )
    all_rows = [r for sub in subjects.values() for r in sub["rows"]]
    return {
        "subjects": subjects,
        "rows_total": len(all_rows),
        "listing_bound_to_r6r_receipt": listing_bound,
        "binding_failures": binding_failures,
        "pinched_exact_total": sum(
            1 for r in all_rows if r["F2_status"] == "PINCHED_EXACT"
        ),
        "unresolved_pinch_rows": [
            r for r in all_rows if r["F2_status"] != "PINCHED_EXACT"
        ][:VERBATIM_CAP],
        "q2_unresolved_rows": [r for r in all_rows if not r["q2_pinched_by_r6l"]][
            :VERBATIM_CAP
        ],
        "f2_donor_predicate_mismatches": [
            r
            for r in all_rows
            if r["f2_donor_predicate"] is not None
            and r["f2_donor_predicate"] != r["truth_donor_exact"]
        ][:VERBATIM_CAP],
    }


# ---- timing helper -----------------------------------------------------------

def _speedup_stats(dp_times, fc_times) -> dict[str, Any]:
    ratios = sorted(d / f for d, f in zip(dp_times, fc_times, strict=True) if f > 0)
    if not ratios:
        return {}
    arr = np.array(ratios)
    return {
        "median_dp_seconds": statistics.median(dp_times),
        "median_forecast_seconds": statistics.median(fc_times),
        "speedup_min": float(arr[0]),
        "speedup_p10": float(np.percentile(arr, 10)),
        "speedup_median": float(np.percentile(arr, 50)),
        "speedup_p90": float(np.percentile(arr, 90)),
        "speedup_max": float(arr[-1]),
        "instances_timed": len(ratios),
    }


# ---- main --------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "The theorem-backed exact static forecaster F2(t) = C_Dxx(t) (exact "
        "minimum over the full support-<=2 family D++, frozen independent "
        "enumerator, no unrestricted DP call) and the enlarged closed-form "
        "borrow family B'(t) with out-of-support borrow homes, benchmarked "
        "against committed unrestricted-DP truth on the stated finite domains "
        "of the frozen R6L/R6M grammar under the frozen raw support-count "
        "objective."
    ),
    "proven_components": (
        "C_DP <= F2 <= C_Dplus <= C_R6L (family containment, hard-asserted); "
        "C_DP == C_Dxx for ALL n by the machine-checked MAX-R6S exchange "
        "theorem, so F2's exactness is theorem-backed (its empirical zero "
        "error here is a consistency check of the theorem's implementation, "
        "not the source of the claim); C_DP <= f_Bprime <= f_B (B' members "
        "are feasible grammar configurations; B subset-of B')."
    ),
    "machine_evidenced_only": (
        "The Q2 identity C_DP == min(C_R6L, C_Dplus, f_Bprime) is "
        "machine-evidenced only on the stated finite domains; for all n it "
        "remains CONJECTURE. Chemistry F2 values are obtained by the exact "
        "containment pinch (R6P precedent), never by a direct D++ sweep at "
        "n >= 8; chemistry f_Bprime is not computed (frozen runtime cap) and "
        "the chemistry Q2 identity is decided by the R6L pinch."
    ),
    "does_not_cover": (
        "Other objectives (QG-2 shows the support-2 world is the unit-cost "
        "objective's), other grammars, rotation-count trade-offs, Tag ranks "
        "above the enumerated families, the protected stretched-N2 subject, "
        "or any claim of donor or R6 novelty credit."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    # gate 1: table + enumerator bindings
    r6s_bind = r6s.bind_tables()
    tables_bound = (
        all(r6s_bind.values())
        and bool(np.array_equal(r6p.F3.astype(np.int64), r6m._F3))
        and bool(np.array_equal(r6q.F3.astype(np.int64), r6m._F3))
        and {n: r6p._tables(n, 2).P for n in (1, 2, 3)} == {1: 6, 2: 120, 3: 666}
    )
    if not tables_bound:
        raise AssertionError({"qg5b_table_binding_failed": r6s_bind})

    protocol_path = (
        Path(__file__).resolve().parents[3]
        / "development"
        / "orion-qg-regime-geometry"
        / PROTOCOL_NAME
    )
    protocol_sha = r6r.sha256_text(protocol_path.read_text())

    counters = _new_counters()
    qg5_receipt, rec_row = load_refuting_receipt_row()

    a_summary, a_row, a_tp = panel_a(rec_row, counters)
    b_summary, b_dp_t, b_f2_t = panel_b(counters)
    c_summary, c_dp_t, c_f2_t, c_qg5_t = panel_c(rec_row, qg5_receipt, counters)
    d_summary = panel_d()

    # ---- Q1 outcome ----
    q1_ac_errors = (
        (1 if a_summary["q1_error"] != 0 else 0)
        + b_summary["q1_nonzero_error_count"]
        + c_summary["q1_nonzero_error_count"]
    )
    d_unresolved = d_summary["rows_total"] - d_summary["pinched_exact_total"]
    d_pinch_resolved_errors = sum(
        1
        for sub in d_summary["subjects"].values()
        for r in sub["rows"]
        if r["q1_error"] not in (0, None)
    )
    if q1_ac_errors == 0 and d_pinch_resolved_errors == 0 and d_unresolved == 0:
        q1_outcome = "Q1_ZERO_ERROR"
    elif q1_ac_errors > 0 or d_pinch_resolved_errors > 0:
        q1_outcome = "Q1_REFUTED_R6S_CONTRADICTION"
    else:
        q1_outcome = "Q1_PARTIAL_CHEMISTRY_PINCH_UNRESOLVED"

    # ---- Q2 outcome ----
    q2_ac_gaps = (
        (1 if a_summary["q2_error"] != 0 else 0)
        + b_summary["q2_nonzero_error_count"]
        + c_summary["q2_nonzero_error_count"]
    )
    panel_a_repaired = (
        a_summary["q2_error"] == 0
        and a_summary["f_Bprime"] == a_summary["C_DP"]
        and a_summary["predicate_P1"] is True
        and a_summary["predicate_P1prime"] is False
    )
    q2_chem_unresolved = len(d_summary["q2_unresolved_rows"])
    if q2_ac_gaps == 0 and panel_a_repaired and q2_chem_unresolved == 0:
        q2_outcome = "Q2_ENLARGED_BORROW_CLOSES"
        smallest_counterexample = None
    elif q2_ac_gaps > 0 or not panel_a_repaired:
        q2_outcome = "Q2_RESIDUAL_GAP_FOURTH_CONFIGURATION"
        if a_summary["q2_error"] != 0 or not panel_a_repaired:
            smallest_counterexample = {"panel": "A", "row": _row_public(a_row)}
        elif b_summary["q2_nonzero_errors_verbatim"]:
            smallest_counterexample = {
                "panel": "B",
                "row": b_summary["q2_nonzero_errors_verbatim"][0],
            }
        else:
            smallest_counterexample = {
                "panel": "C",
                "row": c_summary["q2_nonzero_errors_verbatim"][0],
            }
    else:
        q2_outcome = "Q2_UNRESOLVED_CHEMISTRY"
        smallest_counterexample = None

    # ---- gates ----
    gates = {
        "tables_bound": tables_bound,
        "structured_receipt_bound": (
            b_summary["r6o_receipt_binding"]["equal_count_bound"]
            and b_summary["r6o_receipt_binding"]["verbatim_rows_bound"]
        ),
        "panel_bound_to_qg5_receipt": c_summary["qg5_receipt_bound"],
        "refuting_instance_bound": a_summary["receipt_row_bound"],
        "chemistry_receipts_bound": (
            not d_summary["binding_failures"]
            and d_summary["listing_bound_to_r6r_receipt"]
        ),
        "dxx_witness_referee_pass": not counters["dxx_witness_failures"],
        "bprime_witness_referee_pass": not counters["bprime_witness_failures"],
        "sandwich_and_soundness": True,  # hard-asserted inline per instance
        "weight1_binding": not counters["weight1_failures"],
        "dp_exact_matcher_binding": not counters["exact_matcher_failures"],
        "p1_false_positive_reclassified": (
            a_summary["predicate_P1"] is True
            and a_summary["truth_donor_exact"] is False
            and a_summary["F2_C_Dxx"] == a_summary["C_DP"] == 10
            and a_summary["f2_donor_predicate"] is False
        ),
        "f2_donor_predicate_exact": (
            not b_summary["f2_donor_predicate_mismatches"]
            and not c_summary["f2_donor_predicate_mismatches"]
            and not d_summary["f2_donor_predicate_mismatches"]
            and a_summary["f2_donor_predicate"] == a_summary["truth_donor_exact"]
        ),
        "no_dp_call_in_forecast_path": True,  # structural: F2 = r6p.dxx_search only
        "protected_stretched_n2_unreachable": True,  # hard-asserted inline
    }

    integrity = {
        k: gates[k]
        for k in (
            "tables_bound",
            "structured_receipt_bound",
            "panel_bound_to_qg5_receipt",
            "refuting_instance_bound",
            "chemistry_receipts_bound",
        )
    }
    if not all(integrity.values()):
        raise AssertionError({"qg5b_integrity_gate_failure": integrity})

    # ---- frozen authority selection ----
    if q1_outcome == "Q1_REFUTED_R6S_CONTRADICTION":
        authority = (
            "ORIONQG_QG5B_DPP_EXACTNESS_REFUTED__"
            "R6S_THEOREM_CONTRADICTION_REPORTED_VERBATIM__NOT_R6"
        )
        responsibility = (
            "RESP:F2_DIVERGES_FROM_DP_TRUTH__THEOREM_IMPLEMENTATION_CONTRADICTION_"
            "SERIALIZED_VERBATIM"
        )
    elif q1_outcome == "Q1_PARTIAL_CHEMISTRY_PINCH_UNRESOLVED":
        authority = (
            "ORIONQG_QG5B_EXACT_FORECASTER_PARTIAL__"
            "CHEMISTRY_PINCH_UNRESOLVED__NOT_R6"
        )
        responsibility = "RESP:ZERO_ERROR_AT_SMALL_N__CHEMISTRY_ROWS_UNRESOLVED"
    elif q2_outcome == "Q2_ENLARGED_BORROW_CLOSES":
        authority = (
            "ORIONQG_QG5B_EXACT_FORECASTER_THEOREM_BACKED_ZERO_ERROR__"
            "DPP_FAMILY_MIN__ENLARGED_BORROW_CLOSES__NOT_R6"
        )
        responsibility = (
            "RESP:R1_RESIDUAL_REPAIRED__F2_EXACT_EVERYWHERE_DP_COMPARED__"
            "BPRIME_RECOVERS_CLOSED_FORM_EXACTNESS_AND_REPAIRS_P1_FALSE_POSITIVE"
        )
    elif q2_outcome == "Q2_RESIDUAL_GAP_FOURTH_CONFIGURATION":
        authority = (
            "ORIONQG_QG5B_EXACT_FORECASTER_ZERO_ERROR__"
            "ENLARGED_BORROW_RESIDUAL_GAP_FOURTH_CONFIGURATION__NOT_R6"
        )
        responsibility = (
            "RESP:F2_EXACT_BUT_BPRIME_INCOMPLETE__SMALLEST_COUNTEREXAMPLE_"
            "SERIALIZED_VERBATIM__FOURTH_CONFIGURATION_LOCALIZED"
        )
    else:
        authority = (
            "ORIONQG_QG5B_EXACT_FORECASTER_ZERO_ERROR__"
            "ENLARGED_BORROW_CHEMISTRY_PINCH_UNRESOLVED__NOT_R6"
        )
        responsibility = (
            "RESP:F2_EXACT_AND_BPRIME_CLOSES_AT_SMALL_N__CHEMISTRY_Q2_ROWS_"
            "UNRESOLVED_SERIALIZED"
        )

    result = {
        "schema": "ORIONQG.QG5B.ExactForecaster.v1",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "lane": "QG-5b exact forecaster (wave-2 lead, residual R1)",
        "protocol": "QG5B_EXACT_FORECASTER_PROTOCOL",
        "protocol_sha256": protocol_sha,
        "authority": authority,
        "scope": (
            "THEOREM_BACKED_EXACT_DPP_FORECASTER_AND_ENLARGED_BORROW_FAMILY__"
            "BENCHMARKED_AGAINST_COMMITTED_UNRESTRICTED_DP__NOT_R6"
        ),
        "responsibility": responsibility,
        "q1": {
            "question": (
                "Does F2(t) = exact minimum over the full support-<=2 family "
                "(r6p.dxx_search, no unrestricted DP call) reproduce C_DP on "
                "the QG-5 refuting instance, the structured n=2 slice, the "
                "fresh seeded panel, and the receipted chemistry rows?"
            ),
            "outcome": q1_outcome,
            "theorem_backing": (
                "MAX_R6S_ALL_N_COMPOSITION_RESULTS.json: C_DP == C_Dxx for "
                "every n (support >= 3 never pays; machine-checked)"
            ),
            "dp_compared_instances_total": 1
            + b_summary["instances"]
            + c_summary["instances"]
            + d_summary["pinched_exact_total"],
            "nonzero_error_total": q1_ac_errors + d_pinch_resolved_errors,
            "chemistry_unresolved_rows": d_unresolved,
        },
        "q2": {
            "question": (
                "Does min(C_R6L, C_Dplus, f_Bprime) with the enlarged borrow "
                "family B' (out-of-support borrow homes) recover closed-form "
                "exactness on all panels, repairing the QG-5 counterexample "
                "and P1's false positive?"
            ),
            "outcome": q2_outcome,
            "bprime_definition": (
                "B'(t) = frozen R6Q borrow family B(t) with the single "
                "enlargement that each phantom block's home qubit q_h ranges "
                "over the union target support plus one empty representative "
                "(q_t excluded) instead of the block's own target support; "
                "weight-one Tag v@q_t, anchored/phantom options, all-anchored "
                "corner excluded, value = min(surcharges + branch F3) + 2."
            ),
            "residual_gap_total": q2_ac_gaps,
            "panel_a_repaired": panel_a_repaired,
            "chemistry_unresolved_rows": q2_chem_unresolved,
            "smallest_counterexample_verbatim": smallest_counterexample,
        },
        "panels": {
            "panel_a_refuting_instance": a_summary,
            "panel_b_structured_n2": b_summary,
            "panel_c_fresh_seeded": c_summary,
            "panel_d_chemistry": {
                "subjects": {
                    name: {k: v for k, v in sub.items() if k != "rows"}
                    for name, sub in d_summary["subjects"].items()
                },
                "rows": {
                    name: sub["rows"] for name, sub in d_summary["subjects"].items()
                },
                **{
                    k: v
                    for k, v in d_summary.items()
                    if k not in ("subjects",)
                },
            },
        },
        "hostile_referee": {
            "dxx_witness_rows_verified": counters["dxx_witness_rows"],
            "dxx_witness_failures": counters["dxx_witness_failures"],
            "bprime_witness_rows_verified": counters["bprime_witness_rows"],
            "bprime_witness_failures": counters["bprime_witness_failures"],
            "bprime_witness_exempt_infeasible": counters[
                "bprime_witness_exempt_infeasible"
            ],
            "weight1_binding_rows": counters["weight1_rows"],
            "weight1_binding_failures": counters["weight1_failures"],
            "exact_matcher_binding_rows": counters["exact_matcher_rows"],
            "exact_matcher_binding_failures": counters["exact_matcher_failures"],
        },
        "gates": gates,
        "claim_boundary": CLAIM_BOUNDARY,
        "random_seed_fresh_panel": SEED_FRESH,
        "chemistry_sources_read_via_frozen_batch_only": True,
        "heavy_subject_dp_rerun": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG5B authority ceiling violated")

    # ---- timing (excluded from the canonical line per the R6P convention) ---
    timing = {
        "convention": (
            "R6P: timing fields excluded from the canonical stdout line; "
            "present only in this file section and on stderr"
        ),
        "q3_panel_c_dp_vs_f2": _speedup_stats(c_dp_t, c_f2_t),
        "q3_panel_c_dp_vs_qg5_three_family": _speedup_stats(c_dp_t, c_qg5_t),
        "q3_panel_c_by_n": {
            "2": _speedup_stats(c_dp_t[:PANEL_PER_N], c_f2_t[:PANEL_PER_N]),
            "3": _speedup_stats(c_dp_t[PANEL_PER_N:], c_f2_t[PANEL_PER_N:]),
        },
        "panel_b_warm_cache_dp_vs_f2_plus_families": _speedup_stats(b_dp_t, b_f2_t),
        "runtime_seconds": round(time.monotonic() - start, 3),
    }

    print("ORIONQG_QG5B_EXACT_FORECASTER=" + canonical_json(result))
    file_result = dict(result)
    file_result["timing"] = timing
    Path(__file__).with_name("QG5B_EXACT_FORECASTER_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n"
    )
    print("qg5b_runtime_seconds=%.3f" % timing["runtime_seconds"], file=sys.stderr)
    print(
        "qg5b_timing_summary="
        + canonical_json({k: v for k, v in timing.items() if k != "convention"}),
        file=sys.stderr,
    )
    return result


if __name__ == "__main__":
    main()
