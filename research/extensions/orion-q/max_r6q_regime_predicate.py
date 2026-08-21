#!/usr/bin/env python3
"""MAX-R6Q regime predicate induction.

Frozen by MAX_R6Q_REGIME_PREDICATE_PROTOCOL.md (frozen BEFORE any ground-truth
label was computed under that protocol).

Induces and tests a decidable predicate P(targets), computable from the six
per-block target Paulis alone (no DP call), meant to hold exactly on the
instances where the weight-one-Tag donor family (R6L) is DP-optimal
(donor-exact: C_DP == C_R6L), separating them from the two committed trade
regimes: anchor splitting (R6N; C_D+ < C_R6L) and Tag-borrow (R6O;
C_DP < C_D+ via a weight-2 central-branch frame that buys the label
anticommutation at the existing Tag qubit).

Ground truth comes only from the committed R6O/R6M machinery, imported and
unmodified. Honest outcome space: EXACT_PREDICATE_FOUND /
SUFFICIENT_CONDITION_ONLY / NO_CLEAN_PREDICATE. Not R6; no novelty credit;
the protected stretched-N2 discriminator is never read.
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
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402

h = p10.h
LETTERS = "IXYZ"
INF = 10 ** 9
BIG = np.int32(INF)
MATCHING = r6m._SYNTHETIC_MATCHING  # ((0, 1), (2, 3), (4, 5))
SEED_H1 = 20260821
SEED_H2 = 20260822
VERBATIM_CAP = 20

# ---- independent local F3 factoring table, bound to the frozen r6m table ----
LW = np.array([h.local_wt(a) for a in range(4)], dtype=np.int64)
F3 = np.zeros((4, 4, 4), dtype=np.int32)
for _a in range(4):
    for _b in range(4):
        for _c in range(4):
            if _a == _b == _c != 0:
                F3[_a, _b, _c] = 1
            else:
                F3[_a, _b, _c] = int(LW[_a] + LW[_b] + LW[_c])


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


# ---- frozen borrow family B(t) ----------------------------------------------

_borrow_block_cache: dict[tuple, tuple] = {}


def _borrow_block_options(tp_j, n: int, q_t: int, v: int, rel: tuple):
    """Per-block option arrays for the frozen borrow family at Tag v@q_t.

    Returns (extra, letters, n_anchored): extra (m,) int32 uanti surcharge,
    letters (m, 2, len(rel)) int8 local codes of the two branch restores at the
    relevant qubits, with the anchored options first.
    """
    key = (tp_j, n, q_t, v, rel)
    hit = _borrow_block_cache.get(key)
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
            rows.append((0, t_comm, t_anti))
    n_anchored = len(rows)
    # phantom with home in the block's own support
    supp_j = _qubits(_supp_mask(tp_j[0]) | _supp_mask(tp_j[1]))
    for q_h in supp_j:
        if q_h == q_t:
            continue
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
                        rows.append((2, t_comm, t_anti))
    extra = np.array([r[0] for r in rows], dtype=np.int32)
    letters = np.empty((len(rows), 2, len(rel)), dtype=np.int8)
    for i, (_, t_comm, t_anti) in enumerate(rows):
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
    n_anchored = int((extra == 0).sum())
    out = (extra, letters, n_anchored)
    _borrow_block_cache[key] = out
    return out


def borrow_family_min(target_pairs, n: int):
    """f_B: exact minimum over the frozen borrow family (>=1 phantom block)."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    union = 0
    for pair in tp:
        union |= _supp_mask(pair[0]) | _supp_mask(pair[1])
    u_qubits = _qubits(union)
    q_tags = list(u_qubits)
    for q in range(n):
        if not (union >> q) & 1:
            q_tags.append(q)  # single empty representative
            break
    best = None
    for q_t in q_tags:
        rel = tuple(sorted(set(u_qubits) | {q_t}))
        for v in (1, 2, 3):
            per_block = [_borrow_block_options(tp[j], n, q_t, v, rel) for j in range(3)]
            if all(opt[0].shape[0] == opt[2] for opt in per_block):
                continue  # no phantom option in any block is impossible; but
                # if no block has a phantom option, skip this (q_t, v)
            (ea, la, naa), (eb, lb, nab), (ec, lc, nac) = per_block
            tot = (
                ea[:, None, None].astype(np.int32)
                + eb[None, :, None]
                + ec[None, None, :]
            )
            for k in range(2):
                for qi in range(len(rel)):
                    tot = tot + F3[
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
    return best


# ---- simple structural features ---------------------------------------------

def simple_features(target_pairs, n: int) -> dict[str, int]:
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    supp = [_supp_mask(pair[0]) | _supp_mask(pair[1]) for pair in tp]
    s1 = int((supp[0] & supp[1] & supp[2]) != 0)
    s2 = int(any(supp[j] & (supp[(j + 1) % 3] | supp[(j + 2) % 3]) == 0 for j in range(3)))
    s3 = int(any(pair[0] == pair[1] for pair in tp))
    a3 = 0
    a2 = [0, 0, 0]
    for q in range(n):
        codes = [
            {r6o._local_code(pair[0], q), r6o._local_code(pair[1], q)} - {0}
            for pair in tp
        ]
        if codes[0] & codes[1] & codes[2]:
            a3 += 1
        for pi, (x, y) in enumerate(((0, 1), (0, 2), (1, 2))):
            if codes[x] & codes[y]:
                a2[pi] += 1
    return {"s1": s1, "s2": s2, "s3": s3, "a3": a3, "a2max": max(a2)}


# ---- instance evaluation ------------------------------------------------------

def evaluate_instance(target_pairs, n: int, c_dp: int) -> dict[str, Any]:
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    c_dplus = int(r6o.dplus_pairs(tp, n)["C_Dplus"])
    terms = r6m._synthetic_terms(tp)
    c_r6l = int(r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"])
    if not (c_dp <= c_dplus <= c_r6l):
        raise AssertionError({"r6q_sandwich_violated": [c_dp, c_dplus, c_r6l]})
    f_b = borrow_family_min(tp, n)
    if f_b is not None and c_dp > f_b:
        raise AssertionError({"r6q_borrow_soundness_violated": [c_dp, f_b]})
    feats = simple_features(tp, n)
    f_b_eff = INF if f_b is None else f_b
    return {
        "C_DP": c_dp,
        "C_Dplus": c_dplus,
        "C_R6L": c_r6l,
        "f_B": f_b_eff,
        "donor_exact": c_dp == c_r6l,
        "regime_split": c_dp == c_dplus < c_r6l,
        "regime_borrow": c_dp < c_dplus,
        "Gsplit": c_r6l - c_dplus,
        "identity_two_trade": c_dp == min(c_r6l, c_dplus, f_b_eff),
        **feats,
    }


# ---- frozen literals and predicate candidates --------------------------------

LITERALS = (
    ("s1", lambda r: r["s1"] == 1),
    ("not_s1", lambda r: r["s1"] == 0),
    ("s2", lambda r: r["s2"] == 1),
    ("not_s2", lambda r: r["s2"] == 0),
    ("s3", lambda r: r["s3"] == 1),
    ("not_s3", lambda r: r["s3"] == 0),
    ("a3_eq_0", lambda r: r["a3"] == 0),
    ("a3_ge_1", lambda r: r["a3"] >= 1),
    ("a3_ge_2", lambda r: r["a3"] >= 2),
    ("a2max_eq_0", lambda r: r["a2max"] == 0),
    ("a2max_ge_1", lambda r: r["a2max"] >= 1),
    ("a2max_ge_2", lambda r: r["a2max"] >= 2),
    ("Gsplit_eq_0", lambda r: r["Gsplit"] == 0),
    ("fB_ge_CR6L", lambda r: r["f_B"] >= r["C_R6L"]),
)


def predicate_p1(row) -> bool:
    return row["Gsplit"] == 0 and row["f_B"] >= row["C_R6L"]


def predicate_p0(row) -> bool:
    return row["Gsplit"] == 0


def confusion(rows, pred) -> dict[str, int]:
    tp = fp = fn = tn = 0
    for row in rows:
        p = pred(row)
        if p and row["donor_exact"]:
            tp += 1
        elif p and not row["donor_exact"]:
            fp += 1
        elif not p and row["donor_exact"]:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "errors": fp + fn}


def fit_p2(rows) -> dict[str, Any]:
    """Frozen fallback: best conjunction of <=3 literals, deterministic order."""
    values = {name: np.array([fn(r) for r in rows], dtype=bool) for name, fn in LITERALS}
    truth = np.array([r["donor_exact"] for r in rows], dtype=bool)
    names = [name for name, _ in LITERALS]
    best = None
    for size in (1, 2, 3):
        for combo in itertools.combinations(range(len(names)), size):
            mask = values[names[combo[0]]].copy()
            for idx in combo[1:]:
                mask &= values[names[idx]]
            err = int((mask != truth).sum())
            key = (err, size, combo)
            if best is None or key < best[0]:
                best = (key, combo)
    (err, size, combo), combo_idx = best[0], best[1]
    return {
        "literals": [names[i] for i in combo_idx],
        "training_errors": int(err),
    }


def make_p2_pred(literal_names):
    fns = [fn for name, fn in LITERALS if name in set(literal_names)]
    return lambda row: all(fn(row) for fn in fns)


# ---- panels -------------------------------------------------------------------

def training_panel() -> list[dict[str, Any]]:
    wt1 = [r6o._letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    rows = []
    idx = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        target_pairs = tuple(
            (wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic)
        )
        c_dp = r6o.dp_cost_n2_reader(target_pairs)
        row = evaluate_instance(target_pairs, 2, c_dp)
        row["instance_index"] = idx
        rows.append(row)
        idx += 1
    r6m._local_table.cache_clear()
    return rows


def random_panel(seed: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    rows = []
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
            target_pairs = tuple(
                (targets[2 * j], targets[2 * j + 1]) for j in range(3)
            )
            terms = r6m._synthetic_terms(target_pairs)
            r6m._local_table.cache_clear()
            c_dp = r6o.dp_cost_frozen_configs(terms, n)
            row = evaluate_instance(target_pairs, n, c_dp)
            row["n"] = n
            row["index"] = i
            rows.append(row)
            _borrow_block_cache.clear()
    r6o._block_cache.clear()
    return rows


def bind_h1_to_receipt(rows) -> dict[str, Any]:
    receipt = json.loads(
        Path(__file__)
        .with_name("MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json")
        .read_text()
    )
    rec_rows = receipt["domains"]["random_panel"]["rows"]
    if len(rec_rows) != len(rows):
        raise AssertionError("r6q H1 row count does not match R6O receipt")
    mismatches = []
    for mine, rec in zip(rows, rec_rows):
        ok = (
            mine["n"] == rec["n"]
            and mine["index"] == rec["index"]
            and mine["C_DP"] == rec["C_unrestricted_dp"]
            and mine["C_Dplus"] == rec["C_Dplus"]
            and mine["C_R6L"] == rec["C_R6L_weight_one_donor"]
        )
        if not ok:
            mismatches.append([mine["n"], mine["index"]])
    return {
        "rows_bound": len(rows),
        "mismatches": mismatches,
        "bound_exact": not mismatches,
        "receipt_equal_count": int(receipt["domains"]["random_panel"]["equal_count"]),
    }


def bind_training_to_receipt(rows) -> dict[str, Any]:
    receipt = json.loads(
        Path(__file__)
        .with_name("MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json")
        .read_text()
    )
    dom = receipt["domains"]["structured_n2"]
    my_equal = sum(1 for r in rows if r["C_DP"] == r["C_Dplus"])
    verbatim_ok = True
    by_idx = {r["instance_index"]: r for r in rows}
    for rec in dom["violating_instances_verbatim"]:
        mine = by_idx[rec["instance_index"]]
        if (
            mine["C_DP"] != rec["C_unrestricted_dp"]
            or mine["C_Dplus"] != rec["C_Dplus"]
        ):
            verbatim_ok = False
    return {
        "receipt_equal_count": int(dom["equal_count"]),
        "recomputed_equal_count": int(my_equal),
        "equal_count_bound": my_equal == int(dom["equal_count"]),
        "verbatim_rows_bound": verbatim_ok,
    }


def chemistry_panel() -> dict[str, Any]:
    r6m_receipt = json.loads(
        Path(__file__)
        .with_name("MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json")
        .read_text()
    )
    r6o_receipt = json.loads(
        Path(__file__)
        .with_name("MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json")
        .read_text()
    )
    subjects = {}
    rows_flat = []
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        terms, source_indices, _champions, _max_imag, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"r6q_chemistry_blob_mismatch": name})
        n = int(cfg["n_qubits"])
        six = [int(i) for i in source_indices]
        rec_sub = r6m_receipt["subjects"][name]
        if sorted(six) != sorted(int(i) for i in rec_sub["frozen_source_indices"]):
            raise AssertionError({"r6q_chemistry_source_indices_mismatch": name})
        rec_rows = {
            canonical_json(row["matching"]): row for row in rec_sub["candidate_points"]
        }
        r6o_rows = {
            canonical_json(row["matching"]): row
            for row in r6o_receipt["domains"]["chemistry"]["subjects"][name]["rows"]
        }
        matchings = r6m.perfect_matchings(six)
        sub_rows = []
        for pairs in matchings:
            key = canonical_json([list(p) for p in pairs])
            rec_row = rec_rows[key]
            c_dp = int(rec_row["C_R6M"])
            c_r6l_receipt = int(rec_row["C_R6L_same_matching"])
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            c_dplus = int(r6o.dplus_pairs(target_pairs, n)["C_Dplus"])
            c_r6l = int(r6m.donor_r6l_matching(terms, pairs, n, six)["C_R6L"])
            if c_r6l != c_r6l_receipt:
                raise AssertionError({"r6q_chemistry_r6l_receipt_mismatch": [name, key]})
            if int(r6o_rows[key]["C_Dplus"]) != c_dplus:
                raise AssertionError({"r6q_chemistry_dplus_receipt_mismatch": [name, key]})
            if not (c_dp <= c_dplus <= c_r6l):
                raise AssertionError({"r6q_chemistry_sandwich_violated": [name, key]})
            f_b = borrow_family_min(target_pairs, n)
            if f_b is not None and c_dp > f_b:
                raise AssertionError({"r6q_chemistry_borrow_soundness": [name, key]})
            f_b_eff = INF if f_b is None else f_b
            feats = simple_features(target_pairs, n)
            row = {
                "C_DP": c_dp,
                "C_Dplus": c_dplus,
                "C_R6L": c_r6l,
                "f_B": f_b_eff,
                "donor_exact": c_dp == c_r6l,
                "regime_split": c_dp == c_dplus < c_r6l,
                "regime_borrow": c_dp < c_dplus,
                "Gsplit": c_r6l - c_dplus,
                "identity_two_trade": c_dp == min(c_r6l, c_dplus, f_b_eff),
                **feats,
            }
            sub_rows.append({"matching": [list(p) for p in pairs], **row})
            rows_flat.append(row)
            _borrow_block_cache.clear()
        r6o._block_cache.clear()
        subjects[name] = {
            "n_qubits": n,
            "source_blob_verified": True,
            "matchings": len(sub_rows),
            "rows": sub_rows,
        }
    return {"subjects": subjects, "rows_flat": rows_flat}


# ---- summaries ---------------------------------------------------------------

def panel_summary(rows, preds: dict[str, Any]) -> dict[str, Any]:
    out = {
        "instances": len(rows),
        "donor_exact_count": sum(r["donor_exact"] for r in rows),
        "regime_split_count": sum(r["regime_split"] for r in rows),
        "regime_borrow_count": sum(r["regime_borrow"] for r in rows),
        "identity_two_trade_count": sum(r["identity_two_trade"] for r in rows),
        "confusion": {name: confusion(rows, fn) for name, fn in preds.items()},
    }
    return out


def misclassified_verbatim(rows, pred, n_field=None):
    out = []
    for row in rows:
        if pred(row) != row["donor_exact"] and len(out) < VERBATIM_CAP:
            keep = {
                k: row[k]
                for k in (
                    "C_DP", "C_Dplus", "C_R6L", "f_B", "donor_exact",
                    "Gsplit", "instance_index", "n", "index",
                )
                if k in row
            }
            out.append(keep)
    return out


CLAIM_BOUNDARY = {
    "covers": (
        "Classification of frozen-grammar instances (three ordered blocks of "
        "target Pauli pairs) into donor-exact (C_DP == C_R6L) versus the R6N "
        "anchor-splitting and R6O Tag-borrow trade regimes, by a structural "
        "predicate over the targets with no DP call: profitability tests for "
        "the two known elementary trades (the D+ split family and the frozen "
        "weight-one-Tag borrow family B(t))."
    ),
    "machine_evidenced_only": (
        "Any exactness claim is machine-evidenced only on the stated finite "
        "domains (the 9261-instance structured-n2 training panel, the two "
        "240-instance seeded random panels at n=2..3, and the 30 recorded "
        "chemistry matchings). It is NOT a theorem for all n or all targets; "
        "the borrow family is a frozen restricted enlargement (weight-1 Tag, "
        "one weight-2 central branch, home qubits inside the block's own "
        "target support), not a proof of DP-mechanism completeness."
    ),
    "does_not_cover": (
        "Other objectives, other grammars (including the R6I rank-2 grammar), "
        "rotation-count trade-offs, Tag ranks above the enumerated families, "
        "fresh subject data, or any claim of donor or R6 novelty credit."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    f3_binding = bool(np.array_equal(F3.astype(np.int64), r6m._F3))
    if not f3_binding:
        raise AssertionError("r6q F3 table does not bind to frozen r6m._F3")

    # ---- training fit (structured n2 panel ONLY) ----
    train_rows = training_panel()
    train_binding = bind_training_to_receipt(train_rows)
    p2_fit = fit_p2(train_rows)
    p2_pred = make_p2_pred(p2_fit["literals"])
    preds = {"P1": predicate_p1, "P0": predicate_p0, "P2": p2_pred}
    train_summary = panel_summary(train_rows, preds)

    # frozen selection rule
    if train_summary["confusion"]["P1"]["errors"] == 0:
        selected_name = "P1"
    elif train_summary["confusion"]["P0"]["errors"] == 0:
        selected_name = "P0"
    else:
        selected_name = "P2"
    selected_pred = preds[selected_name]

    # ---- held-out panels (after the predicate is fixed) ----
    h1_rows = random_panel(SEED_H1)
    h1_binding = bind_h1_to_receipt(h1_rows)
    h1_summary = panel_summary(h1_rows, preds)

    h2_rows = random_panel(SEED_H2)
    h2_summary = panel_summary(h2_rows, preds)

    chem = chemistry_panel()
    chem_rows = chem["rows_flat"]
    chem_summary = panel_summary(chem_rows, preds)
    chem_all_pred_exact = all(selected_pred(r) for r in chem_rows)
    chem_all_truth_exact = all(r["donor_exact"] for r in chem_rows)

    # ---- frozen outcome mapping ----
    sel_conf = {
        "training": train_summary["confusion"][selected_name],
        "heldout_20260821": h1_summary["confusion"][selected_name],
        "heldout_20260822": h2_summary["confusion"][selected_name],
        "chemistry": chem_summary["confusion"][selected_name],
    }
    zero_error_everywhere = all(c["errors"] == 0 for c in sel_conf.values())
    zero_fp_everywhere = all(c["fp"] == 0 for c in sel_conf.values())
    all_panels = {
        "training": train_rows,
        "heldout_20260821": h1_rows,
        "heldout_20260822": h2_rows,
        "chemistry": chem_rows,
    }
    regimes_excluded = all(
        not selected_pred(r)
        for rows in all_panels.values()
        for r in rows
        if r["regime_split"] or r["regime_borrow"]
    )
    if zero_error_everywhere and chem_all_pred_exact and chem_all_truth_exact:
        outcome = "EXACT_PREDICATE_FOUND"
        authority = (
            "MAX_R6Q_REGIME_PREDICATE_EXACT__"
            "TWO_TRADE_CHARACTERIZATION_ON_VERIFIED_DOMAINS__NOT_R6"
        )
        responsibility = (
            "RESP:DONOR_EXACTNESS_DECIDED_BY_STRUCTURAL_NONPROFITABILITY_OF_"
            "SPLIT_AND_BORROW_TRADES_ON_ALL_VERIFIED_FINITE_DOMAINS"
        )
    elif zero_fp_everywhere and chem_all_pred_exact and chem_all_truth_exact and regimes_excluded:
        outcome = "SUFFICIENT_CONDITION_ONLY"
        authority = "MAX_R6Q_REGIME_PREDICATE_SUFFICIENT_CONDITION_ONLY__NOT_R6"
        responsibility = (
            "RESP:SOUND_SUFFICIENT_CONDITION_WITH_PARTIAL_COVERAGE__"
            "EXACT_CHARACTERIZATION_OPEN"
        )
    else:
        outcome = "NO_CLEAN_PREDICATE"
        authority = "MAX_R6Q_REGIME_PREDICATE_NO_CLEAN_PREDICATE__NOT_R6"
        responsibility = (
            "RESP:NEGATIVE_RESULT__BEST_CANDIDATE_CONFUSION_REPORTED_VERBATIM"
        )

    coverage = {
        name: (
            None
            if summary["donor_exact_count"] == 0
            else summary["confusion"][selected_name]["tp"] / summary["donor_exact_count"]
        )
        for name, summary in (
            ("training", train_summary),
            ("heldout_20260821", h1_summary),
            ("heldout_20260822", h2_summary),
            ("chemistry", chem_summary),
        )
    }

    gates = {
        "f3_table_binding_exact": f3_binding,
        "training_receipt_binding": train_binding["equal_count_bound"]
        and train_binding["verbatim_rows_bound"],
        "h1_receipt_binding_exact": h1_binding["bound_exact"],
        "sandwich_and_borrow_soundness_asserted": True,  # hard-asserted inline
        "chemistry_receipt_bound": True,  # hard-asserted inline
        "chemistry_all_truth_donor_exact": chem_all_truth_exact,
        "chemistry_all_predicted_donor_exact": chem_all_pred_exact,
        "known_regime_instances_all_excluded_by_predicate": regimes_excluded,
        "selected_predicate_zero_error_everywhere": zero_error_everywhere,
        "no_new_subject_data": True,
    }

    result = {
        "schema": "ORIONQ.MAXR6Q.RegimePredicate.v1",
        "authority": authority,
        "scope": (
            "STRUCTURAL_PREDICATE_INDUCTION_OVER_FROZEN_R6M_GRAMMAR_REGIMES__"
            "EXPLANATORY_CLASSIFICATION__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "MAX_R6Q_REGIME_PREDICATE_PROTOCOL",
        "outcome": outcome,
        "predicate": {
            "selected": selected_name,
            "statement_prose": (
                "P(targets) holds iff neither known trade is profitable: "
                "(i) Gsplit = C_R6L - C_D+ = 0, i.e. allowing the three "
                "weight-one frames to anchor at different qubits with the "
                "unique minimum-weight spread Tag does not beat the common "
                "weight-one-Tag donor family; and (ii) f_B >= C_R6L, i.e. no "
                "member of the frozen borrow family -- Tag fixed at weight one "
                "(v at q_t), some block un-anchored with a weight-two central "
                "branch frame l@q_t * m1@q_h (q_h in its own target support, "
                "l anticommuting with v) purchasing the label constraint at "
                "the Tag qubit for +2 support while re-aligning the factored "
                "Restore triple -- costs less than the donor family."
            ),
            "statement_formal": (
                "P(t) := [C_R6L(t) == C_Dplus(t)] AND [f_B(t) >= C_R6L(t)], "
                "with C_R6L, C_Dplus the frozen closed-form family minima and "
                "f_B the frozen borrow-family minimum defined in the protocol; "
                "all three are bounded explicit minimizations over target-"
                "derived letter choices; no DP is invoked."
            ),
            "p2_fallback_fit": p2_fit,
        },
        "panels": {
            "training_structured_n2": {
                **train_summary,
                "receipt_binding": train_binding,
                "misclassified_selected_verbatim": misclassified_verbatim(
                    train_rows, selected_pred
                ),
            },
            "heldout_random_20260821": {
                **h1_summary,
                "receipt_binding": h1_binding,
                "misclassified_selected_verbatim": misclassified_verbatim(
                    h1_rows, selected_pred
                ),
            },
            "heldout_random_20260822": {
                **h2_summary,
                "misclassified_selected_verbatim": misclassified_verbatim(
                    h2_rows, selected_pred
                ),
            },
            "chemistry": {
                **chem_summary,
                "subjects": {
                    name: {
                        k: v for k, v in sub.items() if k != "rows"
                    }
                    for name, sub in chem["subjects"].items()
                },
                "rows": {
                    name: sub["rows"] for name, sub in chem["subjects"].items()
                },
            },
        },
        "coverage_recall_on_donor_exact": coverage,
        "selected_confusion": sel_conf,
        "gates": gates,
        "random_seeds": {"heldout_1": SEED_H1, "heldout_2": SEED_H2},
        "claim_boundary": CLAIM_BOUNDARY,
        "chemistry_sources_read_via_frozen_batch_only": True,
        "heavy_subject_dp_rerun": False,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("R6Q authority ceiling violated")
    Path(__file__).with_name("MAX_R6Q_REGIME_PREDICATE_RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("ORIONQ_MAX_R6Q_REGIME_PREDICATE=" + canonical_json(result))
    print(
        "r6q_runtime_seconds=%.3f" % (time.monotonic() - start),
        file=sys.stderr,
    )
    return result


if __name__ == "__main__":
    main()
