#!/usr/bin/env python3
"""ORION-QG QG-5 certified static resource forecaster + benchmark.

Frozen by development/orion-qg-regime-geometry/QG5_FORECAST_THEORY_PROTOCOL.md
(frozen BEFORE any forecast error, timing number, or library admission result
was computed under that protocol).

Forecaster: six frozen target Paulis (+ coefficients for Lambda) ->
predicted exact optimal cost F(t) = min(C_R6L, C_Dplus, f_B), certified
regime, and a certificate built from the closed-form witness family plus the
two-trade profitability/non-profitability checks. NO DP call. Benchmarked
against the committed unrestricted DP on the exhaustive structured n=2 slice,
a fresh seeded panel (seed 20260826), and every receipted real library batch
(H4, eq-N2, Benzene; never the protected stretched-N2), plus an R6R-style
frozen library enumeration emitting a certified forecast table (predictions
only; grants no verification authority).

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

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402
import max_r6r_prospective_fresh_subject as r6r  # noqa: E402

INF = r6q.INF
MATCHING = r6q.MATCHING
SEED_FRESH = 20260826
PANEL_PER_N = 120
LIBRARY_ATTEMPT_CAP = 4
VERBATIM_ERROR_CAP = 100
PROTOCOL_NAME = "QG5_FORECAST_THEORY_PROTOCOL.md"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---- the certified static forecaster (NO DP call) ---------------------------

CERTIFICATE_BASIS = {
    "component_1_upper_bound": {
        "status": "PROVEN_CONSTRUCTIVE",
        "statement": (
            "C_R6L, C_Dplus and f_B are each the exact minimum of a complete "
            "enumeration of an explicitly constructible sub-family of the "
            "frozen R6M grammar, so C_DP <= F(t) = min(C_R6L, C_Dplus, f_B) "
            "always; additionally C_DP <= C_Dplus <= C_R6L (family "
            "containment) and C_DP <= f_B are hard-asserted on every "
            "DP-compared instance of this run."
        ),
        "backing": [
            "MAX_R6L_THREE_TARE2_SHARED_FACTOR_DONOR_RESULTS.json (+ Erratum 1)",
            "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json",
            "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json",
            "MAX_R6Q_REGIME_PREDICATE_PROTOCOL.md (borrow family B(t))",
        ],
    },
    "component_2_support2_sufficiency": {
        "status": "PROVEN_ALL_N_MACHINE_CHECKED_THEOREM",
        "statement": (
            "C_DP == C_Dxx for every qubit count n, every target six-tuple, "
            "every matching: frames of global support >= 3 never pay (Lemma B "
            "pigeonhole + Lemma E 18,432-case exhaustive check + exchange "
            "induction). Any gap between F(t) and C_DP can therefore only be "
            "realized by support-<=2 frames outside the three enumerated "
            "families."
        ),
        "backing": ["MAX_R6S_ALL_N_COMPOSITION_RESULTS.json"],
    },
    "component_3_exactness_identity": {
        "status": "MACHINE_EVIDENCED_ON_VERIFIED_DOMAINS__CONJECTURE_FOR_ALL_N",
        "statement": (
            "The two-trade completeness identity C_DP == min(C_R6L, C_Dplus, "
            "f_B) is machine-evidenced on the verified domains only (R6Q: "
            "9,261 exhaustive structured n=2 + 2x240 seeded n=2..3 + 30 "
            "receipted chemistry matchings, all zero-error; R6R: 15 further "
            "matchings of a fresh subject predicted before computation). For "
            "all n and all targets it is CONJECTURE; the forecaster's "
            "exactness claim inherits exactly this status."
        ),
        "backing": [
            "MAX_R6Q_REGIME_PREDICATE_RESULTS.json (EXACT_PREDICATE_FOUND)",
            "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json (PREDICTION_CONFIRMED)",
        ],
    },
    "component_4_regime_certificate": {
        "status": "MACHINE_EVIDENCED_ON_VERIFIED_DOMAINS",
        "statement": (
            "The regime label and the predicate P1(t) := [C_Dplus == C_R6L] "
            "AND [f_B >= C_R6L] (non-profitability of both elementary "
            "trades) are exact on all verified domains with zero confusion "
            "errors; P1 <-> donor_exact is hard-asserted per instance."
        ),
        "backing": [
            "MAX_R6Q_REGIME_PREDICATE_RESULTS.json",
            "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json",
        ],
    },
}

WITNESS_FAMILY = {
    "donor_exact": "R6L_WEIGHT_ONE_SHARED_TAG_DONOR_FAMILY",
    "split": "R6O_DPLUS_ANCHOR_SPLITTING_FAMILY",
    "borrow": "R6Q_FROZEN_TAG_BORROW_FAMILY_B",
}


def forecast(target_pairs, n: int, terms=None, pairs=None, six=None):
    """Certified static forecast for one instance. NO DP call."""
    tp = tuple((tuple(a), tuple(b)) for a, b in target_pairs)
    if terms is None:
        terms = r6m._synthetic_terms(tp)
        pairs = MATCHING
        six = list(range(6))
    c_r6l = int(r6m.donor_r6l_matching(terms, pairs, n, six)["C_R6L"])
    c_dplus = int(r6o.dplus_pairs(tp, n)["C_Dplus"])
    if not c_dplus <= c_r6l:
        raise AssertionError({"qg5_containment_violated": [c_dplus, c_r6l]})
    f_b = r6q.borrow_family_min(tp, n)
    f_b_eff = INF if f_b is None else int(f_b)
    predicted = min(c_r6l, c_dplus, f_b_eff)
    if predicted == c_r6l:
        regime = "donor_exact"
    elif predicted == c_dplus:
        regime = "split"
    else:
        regime = "borrow"
    predicate_p1 = (c_dplus == c_r6l) and (f_b_eff >= c_r6l)
    if predicate_p1 != (regime == "donor_exact"):
        raise AssertionError({"qg5_predicate_regime_mismatch": list(map(list, tp))})
    return {
        "C_R6L": c_r6l,
        "C_Dplus": c_dplus,
        "f_B": f_b_eff,
        "predicted_C_DP": int(predicted),
        "regime": regime,
        "certificate": {
            "witness_family": WITNESS_FAMILY[regime],
            "Gsplit": c_r6l - c_dplus,
            "split_trade_profitable": c_dplus < c_r6l,
            "borrow_trade_profitable": f_b_eff < min(c_r6l, c_dplus),
            "predicate_P1": predicate_p1,
        },
    }


def _clear_forecast_caches() -> None:
    r6o._block_cache.clear()
    r6q._borrow_block_cache.clear()


# ---- shared error/regime bookkeeping ----------------------------------------

def _regime_census(rows) -> dict[str, int]:
    census = {"donor_exact": 0, "split": 0, "borrow": 0}
    for row in rows:
        census[row["regime"]] += 1
    return census


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


# ---- domain A: exhaustive structured n=2 slice ------------------------------

def domain_structured_n2():
    wt1 = [r6o._letter_key(c, q) for q in (0, 1) for c in (1, 2, 3)]
    upairs = [(i, j) for i in range(6) for j in range(i, 6)]
    bind_rows = []
    errors = []
    census = {"donor_exact": 0, "split": 0, "borrow": 0}
    dp_times, fc_times = [], []
    zero = 0
    idx = 0
    for ia, ib, ic in itertools.product(range(21), repeat=3):
        if idx % 256 == 0:
            r6m._local_table.cache_clear()
        target_pairs = tuple(
            (wt1[upairs[s][0]], wt1[upairs[s][1]]) for s in (ia, ib, ic)
        )
        t0 = time.perf_counter()
        c_dp = r6o.dp_cost_n2_reader(target_pairs)
        t1 = time.perf_counter()
        fc = forecast(target_pairs, 2)
        t2 = time.perf_counter()
        dp_times.append(t1 - t0)
        fc_times.append(t2 - t1)
        if not (c_dp <= fc["C_Dplus"] <= fc["C_R6L"]):
            raise AssertionError({"qg5_sandwich_violated_structured": idx})
        if c_dp > fc["f_B"]:
            raise AssertionError({"qg5_borrow_soundness_violated_structured": idx})
        err = fc["predicted_C_DP"] - c_dp
        if err == 0:
            zero += 1
        elif len(errors) < VERBATIM_ERROR_CAP:
            errors.append(
                {
                    "instance_index": idx,
                    "target_pairs": [[list(a), list(b)] for a, b in target_pairs],
                    "C_DP": c_dp,
                    **{k: fc[k] for k in ("C_R6L", "C_Dplus", "f_B", "predicted_C_DP")},
                    "error": err,
                }
            )
        census[fc["regime"]] += 1
        bind_rows.append(
            {"instance_index": idx, "C_DP": c_dp, "C_Dplus": fc["C_Dplus"]}
        )
        idx += 1
    r6m._local_table.cache_clear()
    binding = r6q.bind_training_to_receipt(bind_rows)
    summary = {
        "instances": idx,
        "dp_truth": "r6o.dp_cost_n2_reader (committed unrestricted DP reader)",
        "forecast_error_zero_count": zero,
        "nonzero_error_count": idx - zero,
        "nonzero_errors_verbatim": errors,
        "verbatim_cap": VERBATIM_ERROR_CAP,
        "predicted_regime_census": census,
        "r6o_receipt_binding": binding,
    }
    return summary, dp_times, fc_times


# ---- domain B: fresh seeded panel (seed 20260826) ---------------------------

def domain_fresh_panel():
    rng = np.random.default_rng(SEED_FRESH)
    errors = []
    census = {"donor_exact": 0, "split": 0, "borrow": 0}
    dp_times, fc_times = [], []
    zero = 0
    total = 0
    per_n = {}
    for n in (2, 3):
        n_dp, n_fc = [], []
        for i in range(PANEL_PER_N):
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
            t0 = time.perf_counter()
            c_dp = r6o.dp_cost_frozen_configs(terms, n)
            t1 = time.perf_counter()
            _clear_forecast_caches()
            t2 = time.perf_counter()
            fc = forecast(target_pairs, n)
            t3 = time.perf_counter()
            n_dp.append(t1 - t0)
            n_fc.append(t3 - t2)
            if not (c_dp <= fc["C_Dplus"] <= fc["C_R6L"]):
                raise AssertionError({"qg5_sandwich_violated_panel": [n, i]})
            if c_dp > fc["f_B"]:
                raise AssertionError({"qg5_borrow_soundness_violated_panel": [n, i]})
            err = fc["predicted_C_DP"] - c_dp
            if err == 0:
                zero += 1
            elif len(errors) < VERBATIM_ERROR_CAP:
                errors.append(
                    {
                        "n": n,
                        "index": i,
                        "target_pairs": [
                            [list(a), list(b)] for a, b in target_pairs
                        ],
                        "C_DP": c_dp,
                        **{
                            k: fc[k]
                            for k in ("C_R6L", "C_Dplus", "f_B", "predicted_C_DP")
                        },
                        "error": err,
                    }
                )
            census[fc["regime"]] += 1
            total += 1
        per_n[str(n)] = (n_dp, n_fc)
        dp_times.extend(n_dp)
        fc_times.extend(n_fc)
    summary = {
        "seed": SEED_FRESH,
        "instances": total,
        "generator": "digit-frozen copy of r6q.random_panel (120 per n, n in {2,3})",
        "dp_truth": "r6o.dp_cost_frozen_configs (unrestricted frozen-config DP)",
        "forecast_error_zero_count": zero,
        "nonzero_error_count": total - zero,
        "nonzero_errors_verbatim": errors,
        "predicted_regime_census": census,
    }
    return summary, dp_times, fc_times, per_n


# ---- domain C1: receipted chemistry batches (H4, eq-N2) ---------------------

def domain_chemistry_receipted():
    r6m_receipt = json.loads(
        (ORION_Q_DIR / "MAX_R6M_EXACT_THREE_TARE2_SHARED_FACTOR_DP_RESULTS.json")
        .read_text()
    )
    r6o_receipt = json.loads(
        (ORION_Q_DIR / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json").read_text()
    )
    subjects = {}
    fc_times = {}
    for name, cfg in sorted(p10.base.SUBJECTS.items()):
        terms, source_indices, _champs, _mi, observed_blob = r6f._frozen_batch(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"qg5_chemistry_blob_mismatch": name})
        n = int(cfg["n_qubits"])
        six = [int(i) for i in source_indices]
        rec_sub = r6m_receipt["subjects"][name]
        if sorted(six) != sorted(int(i) for i in rec_sub["frozen_source_indices"]):
            raise AssertionError({"qg5_chemistry_source_indices_mismatch": name})
        rec_rows = {
            canonical_json(row["matching"]): row
            for row in rec_sub["candidate_points"]
        }
        r6o_rows = {
            canonical_json(row["matching"]): row
            for row in r6o_receipt["domains"]["chemistry"]["subjects"][name]["rows"]
        }
        rows = []
        times = []
        zero = 0
        for pairs in r6m.perfect_matchings(six):
            key = canonical_json([list(p) for p in pairs])
            rec_row = rec_rows[key]
            c_dp = int(rec_row["C_R6M"])
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            r6m._local_table.cache_clear()
            _clear_forecast_caches()
            t0 = time.perf_counter()
            fc = forecast(target_pairs, n, terms=terms, pairs=pairs, six=six)
            t1 = time.perf_counter()
            times.append(t1 - t0)
            if fc["C_R6L"] != int(rec_row["C_R6L_same_matching"]):
                raise AssertionError({"qg5_chemistry_r6l_receipt_mismatch": [name, key]})
            if fc["C_Dplus"] != int(r6o_rows[key]["C_Dplus"]):
                raise AssertionError({"qg5_chemistry_dplus_receipt_mismatch": [name, key]})
            if not (c_dp <= fc["C_Dplus"] <= fc["C_R6L"]):
                raise AssertionError({"qg5_chemistry_sandwich_violated": [name, key]})
            if c_dp > fc["f_B"]:
                raise AssertionError({"qg5_chemistry_borrow_soundness": [name, key]})
            err = fc["predicted_C_DP"] - c_dp
            if err == 0:
                zero += 1
            rows.append(
                {
                    "matching": [list(p) for p in pairs],
                    "C_DP_from_receipt": c_dp,
                    **{
                        k: fc[k]
                        for k in (
                            "C_R6L", "C_Dplus", "f_B", "predicted_C_DP", "regime",
                        )
                    },
                    "certificate": fc["certificate"],
                    "Lambda": r6m.lambda_r6m(terms, pairs),
                    "forecast_error": err,
                }
            )
        subjects[name] = {
            "path": cfg["path"],
            "commit": cfg["commit"],
            "blob": cfg["blob"],
            "n_qubits": n,
            "source_blob_verified": True,
            "dp_truth": "committed MAX_R6M receipt C_R6M (heavy DP never re-run)",
            "matchings": len(rows),
            "forecast_error_zero_count": zero,
            "nonzero_error_count": len(rows) - zero,
            "predicted_regime_census": _regime_census(rows),
            "certificate_status": (
                "DP_RECEIPT_COMMITTED__FORECAST_BOUND"
                if zero == len(rows)
                else "DP_RECEIPT_COMMITTED__FORECAST_MISMATCH"
            ),
            "rows": rows,
        }
        fc_times[name] = times
    return subjects, fc_times


# ---- domain C2 + (c): R6R-style frozen library enumeration ------------------

def domain_library_forecast():
    r6r_receipt = json.loads(
        (ORION_Q_DIR / "MAX_R6R_PROSPECTIVE_FRESH_SUBJECT_RESULTS.json").read_text()
    )
    r6r_subject = r6r_receipt["subject"]
    r6r_rows = {
        canonical_json(row["matching"]): row for row in r6r_receipt["matchings"]
    }
    listing = r6r.pinned_tree_listing()
    ducc_listing = [(p, b) for p, b in listing if p.endswith(".ducc.results.txt")]
    listing_digest = r6r.sha256_text(
        "\n".join(f"{b} {p}" for p, b in ducc_listing) + "\n"
    )
    if listing_digest != r6r_receipt["library"]["ducc_listing_sha256"]:
        raise AssertionError("qg5 pinned tree listing digest does not bind to R6R receipt")
    candidates = r6r.eligible_candidates(listing)
    for cfg in candidates:
        if cfg["path"].split("/")[0] in r6r.EXCLUDED_MOLECULES:
            raise AssertionError("qg5 exclusion breached in eligible candidates")
        if cfg["path"] == r6r.PROTECTED_STRETCHED_N2_PATH:
            raise AssertionError("qg5 protected stretched-N2 leaked into candidacy")
    table = []
    fc_times = {}
    for cfg in candidates[:LIBRARY_ATTEMPT_CAP]:
        admit = r6r.try_admit(cfg)
        entry = {
            "path": cfg["path"],
            "commit": cfg["commit"],
            "blob": cfg["blob"],
            "n_qubits": cfg["n_qubits"],
            "admitted": admit["admitted"],
        }
        if not admit["admitted"]:
            entry["reason"] = admit["reason"]
            entry["certificate_status"] = "NOT_ADMITTED__NO_FORECAST"
            table.append(entry)
            continue
        n = int(cfg["n_qubits"])
        terms = admit["terms"]
        six = admit["six"]
        has_receipt = cfg["blob"] == r6r_subject["blob"]
        if has_receipt and sorted(six) != sorted(
            int(i) for i in r6r_subject["frozen_source_indices"]
        ):
            raise AssertionError({"qg5_r6r_source_indices_mismatch": cfg["path"]})
        rows = []
        times = []
        zero_vs_receipt = 0
        for pairs in r6m.perfect_matchings(six):
            key = canonical_json([list(p) for p in pairs])
            target_pairs = tuple((terms[i][0], terms[j][0]) for i, j in pairs)
            r6m._local_table.cache_clear()
            _clear_forecast_caches()
            t0 = time.perf_counter()
            fc = forecast(target_pairs, n, terms=terms, pairs=pairs, six=six)
            t1 = time.perf_counter()
            times.append(t1 - t0)
            row = {
                "matching": [list(p) for p in pairs],
                **{
                    k: fc[k]
                    for k in ("C_R6L", "C_Dplus", "f_B", "predicted_C_DP", "regime")
                },
                "certificate": fc["certificate"],
                "Lambda": r6m.lambda_r6m(terms, pairs),
            }
            if has_receipt:
                rec = r6r_rows[key]
                for mine, theirs in (
                    (fc["C_R6L"], rec["C_R6L"]),
                    (fc["C_Dplus"], rec["C_Dplus"]),
                    (fc["f_B"], rec["f_B"]),
                    (fc["predicted_C_DP"], rec["predicted_C_DP"]),
                ):
                    if int(mine) != int(theirs):
                        raise AssertionError(
                            {"qg5_r6r_receipt_component_mismatch": [cfg["path"], key]}
                        )
                c_dp = int(rec["C_DP"])
                if not (c_dp <= fc["C_Dplus"] <= fc["C_R6L"]) or c_dp > fc["f_B"]:
                    raise AssertionError({"qg5_r6r_soundness_violated": key})
                row["C_DP_from_receipt"] = c_dp
                row["forecast_error"] = fc["predicted_C_DP"] - c_dp
                if row["forecast_error"] == 0:
                    zero_vs_receipt += 1
            rows.append(row)
        entry["six_term_source_indices"] = six
        entry["matchings"] = len(rows)
        entry["predicted_regime_census"] = _regime_census(rows)
        entry["predicted_C_DP_min"] = min(r["predicted_C_DP"] for r in rows)
        entry["predicted_C_DP_max"] = max(r["predicted_C_DP"] for r in rows)
        if has_receipt:
            entry["forecast_error_zero_count"] = zero_vs_receipt
            entry["nonzero_error_count"] = len(rows) - zero_vs_receipt
            entry["certificate_status"] = (
                "DP_RECEIPT_COMMITTED__FORECAST_BOUND"
                if zero_vs_receipt == len(rows)
                else "DP_RECEIPT_COMMITTED__FORECAST_MISMATCH"
            )
            entry["dp_truth"] = "committed MAX_R6R receipt C_DP (heavy DP never re-run)"
        else:
            entry["certificate_status"] = "UNVERIFIED_FORECAST__NO_DP_RECEIPT"
        entry["rows"] = rows
        table.append(entry)
        fc_times[cfg["path"]] = times
    meta = {
        "repo": r6r.REPO,
        "commit": r6r.PINNED_COMMIT,
        "ducc_results_files_at_commit": len(ducc_listing),
        "ducc_listing_sha256": listing_digest,
        "listing_bound_to_r6r_receipt": True,
        "eligible_candidate_count": len(candidates),
        "eligible_candidates_in_order": [
            {"path": c["path"], "blob": c["blob"], "n_qubits": c["n_qubits"]}
            for c in candidates
        ],
        "attempt_cap": LIBRARY_ATTEMPT_CAP,
        "enumeration_rule": (
            "frozen R6R eligibility reused verbatim (exclusion list, "
            "active-space rule, n_qubits-then-path order); the whole N2 "
            "molecule is excluded, so the protected stretched-N2 subject is "
            "unreachable"
        ),
        "verification_authority": (
            "NONE. Rows without a committed DP receipt are predictions only "
            "and verify nothing."
        ),
    }
    return meta, table, fc_times


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "A certified static resource forecaster for the frozen R6L/R6M "
        "three-block TARE-M2 shared-one-bit-Tag grammar under the frozen raw "
        "support-count objective: F(t) = min(C_R6L, C_Dplus, f_B) with "
        "certified regime and two-trade certificate, benchmarked against the "
        "committed unrestricted DP on the stated finite domains and emitted "
        "as an explicitly-labeled forecast table over the pinned library "
        "enumeration."
    ),
    "proven_components": (
        "Upper bound C_DP <= F(t) (constructive families); support-2 "
        "sufficiency C_DP == C_Dxx for all n (MAX_R6S machine-checked "
        "theorem, support >= 3 never pays)."
    ),
    "machine_evidenced_only": (
        "Exactness (the two-trade completeness identity) and the regime "
        "certificate are machine-evidenced only on the verified finite "
        "domains recorded in the R6Q/R6R receipts plus the DP-compared "
        "instances of this run; for all n and all targets the identity is "
        "CONJECTURE. Library-table rows without a committed DP receipt are "
        "unverified forecasts."
    ),
    "does_not_cover": (
        "Other objectives, other grammars (including the R6I rank-2 "
        "grammar), rotation-count trade-offs, Tag ranks above the enumerated "
        "families, the protected stretched-N2 subject, or any claim of donor "
        "or R6 novelty credit."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    f3_binding = bool(np.array_equal(r6q.F3.astype(np.int64), r6m._F3))
    if not f3_binding:
        raise AssertionError("qg5 F3 table binding to frozen r6m._F3 failed")

    protocol_path = (
        Path(__file__).resolve().parents[3]
        / "development"
        / "orion-qg-regime-geometry"
        / PROTOCOL_NAME
    )
    protocol_sha = r6r.sha256_text(protocol_path.read_text())

    structured, s_dp, s_fc = domain_structured_n2()
    panel, p_dp, p_fc, p_per_n = domain_fresh_panel()
    chem_subjects, chem_times = domain_chemistry_receipted()
    lib_meta, lib_table, lib_times = domain_library_forecast()

    dp_compared = (
        structured["instances"]
        + panel["instances"]
        + sum(s["matchings"] for s in chem_subjects.values())
        + sum(
            e.get("matchings", 0)
            for e in lib_table
            if e.get("certificate_status", "").startswith("DP_RECEIPT_COMMITTED")
        )
    )
    nonzero_total = (
        structured["nonzero_error_count"]
        + panel["nonzero_error_count"]
        + sum(s["nonzero_error_count"] for s in chem_subjects.values())
        + sum(
            e.get("nonzero_error_count", 0)
            for e in lib_table
            if "nonzero_error_count" in e
        )
    )

    if nonzero_total == 0:
        outcome = "FORECASTER_CERTIFIED_ON_VERIFIED_DOMAINS"
        authority = (
            "QG5_CERTIFIED_STATIC_FORECASTER__ZERO_ERROR_ON_ALL_DP_COMPARED_"
            "INSTANCES__LIBRARY_TABLE_IS_FORECAST_ONLY__NOT_R6"
        )
        responsibility = (
            "RESP:EXACT_COST_AND_REGIME_FORECAST_WITH_HONEST_PROVEN_VS_"
            "EVIDENCED_CERTIFICATE__NO_DP_CALL_IN_FORECAST_PATH"
        )
    else:
        outcome = "COMPLETENESS_IDENTITY_REFUTED_ON_NEW_INSTANCE"
        authority = (
            "QG5_FORECAST_IDENTITY_REFUTED__BOUNDARY_INSTANCES_REPORTED_"
            "VERBATIM__NOT_R6"
        )
        responsibility = (
            "RESP:NONZERO_FORECAST_ERRORS_REPORTED_VERBATIM__IDENTITY_"
            "BOUNDARY_LOCALIZED"
        )

    gates = {
        "f3_table_binding_exact": f3_binding,
        "protocol_frozen_and_hashed": True,
        "structured_n2_bound_to_r6o_receipt": (
            structured["r6o_receipt_binding"]["equal_count_bound"]
            and structured["r6o_receipt_binding"]["verbatim_rows_bound"]
        ),
        "chemistry_bound_to_r6m_and_r6o_receipts": True,  # hard-asserted inline
        "library_listing_bound_to_r6r_receipt": lib_meta[
            "listing_bound_to_r6r_receipt"
        ],
        "benzene_bound_to_r6r_receipt": any(
            e.get("certificate_status") == "DP_RECEIPT_COMMITTED__FORECAST_BOUND"
            and e["blob"] not in (c["blob"] for c in p10.base.SUBJECTS.values())
            for e in lib_table
        ),
        "sandwich_and_borrow_soundness_asserted": True,  # hard-asserted inline
        "no_dp_call_in_forecast_path": True,
        "all_fetches_blob_pinned": True,  # hard-asserted in r6f/r6r machinery
        "forecast_error_zero_everywhere": nonzero_total == 0,
        "protected_stretched_n2_unreachable": True,  # hard-asserted inline
    }

    result = {
        "schema": "ORIONQG.QG5.CertifiedForecast.v1",
        "programme": "ORION-QG (charter PROGRAMME_CHARTER_V1.md, issue #740)",
        "lane": "QG-5 forecast theory",
        "protocol": "QG5_FORECAST_THEORY_PROTOCOL",
        "protocol_sha256": protocol_sha,
        "authority": authority,
        "scope": (
            "CERTIFIED_STATIC_RESOURCE_FORECASTER_OVER_FROZEN_R6M_GRAMMAR__"
            "BENCHMARKED_AGAINST_COMMITTED_UNRESTRICTED_DP__NOT_R6"
        ),
        "responsibility": responsibility,
        "outcome": outcome,
        "forecaster": {
            "definition": (
                "F(t) := min(C_R6L(t), C_Dplus(t), f_B(t)) over the six "
                "frozen target Paulis; certified regime donor_exact/split/"
                "borrow by frozen R6R rule; certificate = closed-form witness "
                "family + Gsplit and borrow profitability checks + predicate "
                "P1; coefficients enter only the Lambda report field; no DP "
                "call."
            ),
            "certificate_basis": CERTIFICATE_BASIS,
        },
        "benchmark": {
            "structured_n2_exhaustive": structured,
            "fresh_seeded_panel": panel,
            "receipted_chemistry": {
                name: {k: v for k, v in sub.items() if k != "rows"}
                for name, sub in chem_subjects.items()
            },
            "receipted_chemistry_rows": {
                name: sub["rows"] for name, sub in chem_subjects.items()
            },
            "dp_compared_instances_total": dp_compared,
            "nonzero_forecast_errors_total": nonzero_total,
        },
        "library_forecast_table": {
            **lib_meta,
            "subjects": [
                {k: v for k, v in e.items() if k != "rows"} for e in lib_table
            ],
            "rows": {
                e["path"]: e["rows"] for e in lib_table if "rows" in e
            },
        },
        "gates": gates,
        "claim_boundary": CLAIM_BOUNDARY,
        "random_seed_fresh_panel": SEED_FRESH,
        "chemistry_sources_read_via_frozen_batch_only": True,
        "heavy_subject_dp_rerun": False,
        "library_forecast_table_verification_authority": "NONE",
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG5 authority ceiling violated")

    # ---- timing (excluded from the canonical line per the R6P convention) ---
    timing = {
        "convention": (
            "R6P: timing fields excluded from the canonical stdout line; "
            "present only in this file section and on stderr"
        ),
        "structured_n2_warm_cache": _speedup_stats(s_dp, s_fc),
        "fresh_panel_cold_per_instance": _speedup_stats(p_dp, p_fc),
        "fresh_panel_by_n": {
            n: _speedup_stats(dpt, fct) for n, (dpt, fct) in p_per_n.items()
        },
        "chemistry_forecast_only_median_seconds": {
            name: statistics.median(ts) for name, ts in chem_times.items()
        },
        "library_forecast_only_median_seconds": {
            path: statistics.median(ts) for path, ts in lib_times.items()
        },
        "runtime_seconds": round(time.monotonic() - start, 3),
    }

    print("ORIONQ_QG5_CERTIFIED_FORECAST=" + canonical_json(result))
    file_result = dict(result)
    file_result["timing"] = timing
    Path(__file__).with_name("QG5_CERTIFIED_FORECAST_RESULTS.json").write_text(
        json.dumps(file_result, indent=2, sort_keys=True) + "\n"
    )
    print("qg5_runtime_seconds=%.3f" % timing["runtime_seconds"], file=sys.stderr)
    print(
        "qg5_timing_summary=" + canonical_json({k: v for k, v in timing.items() if k != "convention"}),
        file=sys.stderr,
    )
    return result


if __name__ == "__main__":
    main()
