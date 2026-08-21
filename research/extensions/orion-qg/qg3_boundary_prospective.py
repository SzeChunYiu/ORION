#!/usr/bin/env python3
"""ORION-QG lane QG-3: boundary-engineered prospective forecast.

Frozen by development/orion-qg-regime-geometry/QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md
(frozen BEFORE any prediction subject of this lane was generated or selected).

The R6R escalation: positive trade-regime predictions. Track A scans additional
real Hamiltonian batches from the pinned public DUCC library (subjects not in any
committed receipt) under the committed R6R admission machinery; Track B runs a
frozen deterministic generator (seed 20260824) of engineered pairwise-commuting
six-term batches. For every staged row the committed R6Q predicate P1 and the
two-trade completeness identity predict the regime AND the exact DP cost
min(C_R6L, C_Dplus, f_B); the predictions are digest-printed BEFORE the
unrestricted committed R6M DP referee runs.

Honest outcome space: POSITIVE_REGIME_PREDICTIONS_CONFIRMED /
POSITIVE_REGIME_PREDICTIONS_REFUTED / TRACKB_QUOTA_UNMET. Not R6; no novelty or
donor credit; the protected stretched-N2 discriminator is never read (the N2
molecule is excluded from candidacy entirely). All frozen machinery is imported
unmodified from research/extensions/orion-q.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orion-q"))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6f_donor_clifford_preconditioned_tare3 as r6f  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6q_regime_predicate as r6q  # noqa: E402
import max_r6r_prospective_fresh_subject as r6r  # noqa: E402

INF = r6q.INF
MATCHING = r6m._SYNTHETIC_MATCHING  # ((0, 1), (2, 3), (4, 5))
SEED = 20260824
STREAM_CAP = 400
QUOTAS = {"split": 4, "borrow": 4, "donor_exact": 4}
GATE_MIN_TOTAL = 10
GATE_MIN_SPLIT = 3
GATE_MIN_BORROW = 3
TRACKA_SCAN_CAP = 6
TRACKA_TERM_CAP = 1200
R6R_SUBJECT_BLOB = "5c02c72b88e12b391ea1d8f77eb6b3e04fc2a915"  # committed R6R subject
COMMITTED_BLOBS = tuple(r6r.COMMITTED_SUBJECT_BLOBS) + (R6R_SUBJECT_BLOB,)
PROTOCOL_NAME = "QG3_BOUNDARY_PROSPECTIVE_PROTOCOL.md"
# Section-0.3 pre-freeze timing instance (n=14): never a subject of this lane.
TIMING_INSTANCE = (((1, 0), (1, 0)), ((8, 0), (8, 0)), (((96, 0)), ((96, 96))))

_STAGE1_EMITTED = False


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _norm_tp(tp) -> tuple:
    return tuple((tuple(a), tuple(b)) for a, b in tp)


def _committed_verbatim_targets() -> set:
    """Target-pair tuples with recorded targets in the committed R6O receipt."""
    receipt = json.loads(
        (
            Path(__file__).resolve().parent.parent
            / "orion-q"
            / "MAX_R6O_ENLARGED_TAG_DONOR_RESULTS.json"
        ).read_text()
    )
    out = set()
    for row in receipt["domains"]["structured_n2"]["violating_instances_verbatim"]:
        out.add(_norm_tp(row["targets"]))
    for row in receipt["domains"]["random_panel"]["violating_instances_verbatim"]:
        flat = [tuple(t) for t in row["targets"]]
        out.add(tuple((flat[2 * j], flat[2 * j + 1]) for j in range(3)))
    return out


# ---- Track B generator (frozen, seed 20260824) ------------------------------

def _distinct_pair(rng) -> tuple[int, int]:
    perm = rng.permutation(3)
    return int(perm[0]) + 1, int(perm[1]) + 1


def _letter(letter: int, q: int):
    return r6o._letter_key(letter, q)


def draw_instance(rng, i: int):
    """One stream draw; returns (family, n, target_pairs) or None (F3 reject)."""
    fam = ("F1", "F2", "F3")[i % 3]
    if fam == "F1":
        n = 3 if (i // 3) % 2 == 0 else 4
        qperm = rng.permutation(n)
        q0, qh, qk = int(qperm[0]), int(qperm[1]), int(qperm[2])
        u = int(rng.integers(1, 4))
        p1, r1 = _distinct_pair(rng)
        p2, r2 = _distinct_pair(rng)
        heavy = (
            p10.mul(_letter(p1, qh), _letter(p2, qk)),
            p10.mul(_letter(r1, qh), _letter(r2, qk)),
        )
        tag_block = (_letter(u, q0), _letter(u, q0))
        blocks = [tag_block, tag_block]
        slot = int(rng.integers(0, 3))
        blocks.insert(slot, heavy)
        return fam, n, tuple(blocks)
    if fam == "F2":
        n = 5
        qperm = rng.permutation(5)
        q0 = int(qperm[0])
        a, b = int(qperm[1]), int(qperm[2])
        c, d = int(qperm[3]), int(qperm[4])
        u = int(rng.integers(1, 4))
        p1, r1 = _distinct_pair(rng)
        p2, r2 = _distinct_pair(rng)
        s1, t1 = _distinct_pair(rng)
        s2, t2 = _distinct_pair(rng)
        heavy1 = (
            p10.mul(_letter(p1, a), _letter(p2, b)),
            p10.mul(_letter(r1, a), _letter(r2, b)),
        )
        heavy2 = (
            p10.mul(_letter(s1, c), _letter(s2, d)),
            p10.mul(_letter(t1, c), _letter(t2, d)),
        )
        light = (_letter(u, q0), _letter(u, q0))
        base = [light, heavy1, heavy2]
        slotperm = rng.permutation(3)
        arr: list = [None, None, None]
        for j in range(3):
            arr[int(slotperm[j])] = base[j]
        return fam, n, tuple(arr)
    # F3: random pairwise-commuting weight<=2 targets at n=3
    n = 3
    targets: list[tuple[int, int]] = []
    for _t in range(6):
        for _attempt in range(200):
            x = int(rng.integers(0, 8))
            z = int(rng.integers(0, 8))
            key = (x, z)
            if key == (0, 0) or p10.wt(key) > 2:
                continue
            if all(p10.symp(key, prev) == 0 for prev in targets):
                targets.append(key)
                break
        else:
            return None
    return fam, n, tuple((targets[2 * j], targets[2 * j + 1]) for j in range(3))


def predict_instance(tp, n: int) -> dict[str, Any]:
    """Staged prediction for one synthetic instance (canonical matching, no DP)."""
    r6m._local_table.cache_clear()
    terms = r6m._synthetic_terms(tp)
    c_r6l = int(r6m.donor_r6l_matching(terms, MATCHING, n, list(range(6)))["C_R6L"])
    c_dplus = int(r6o.dplus_pairs(tp, n)["C_Dplus"])
    if not c_dplus <= c_r6l:
        raise AssertionError({"qg3_dplus_r6l_order_violated": [c_dplus, c_r6l]})
    f_b = r6q.borrow_family_min(tp, n)
    f_b_eff = INF if f_b is None else int(f_b)
    feats = r6q.simple_features(tp, n)
    predicate_p1 = (c_dplus == c_r6l) and (f_b_eff >= c_r6l)
    predicted_c_dp = min(c_r6l, c_dplus, f_b_eff)
    if (predicted_c_dp == c_r6l) != predicate_p1:
        raise AssertionError({"qg3_predicate_identity_violated": list(tp)})
    if predicted_c_dp == c_r6l:
        predicted_regime = "donor_exact"
    elif predicted_c_dp == c_dplus:
        predicted_regime = "split"
    else:
        predicted_regime = "borrow"
    r6q._borrow_block_cache.clear()
    r6o._block_cache.clear()
    return {
        "targets": [[list(a), list(b)] for a, b in tp],
        "C_R6L": c_r6l,
        "C_Dplus": c_dplus,
        "f_B": f_b_eff,
        "Gsplit": c_r6l - c_dplus,
        "predicate_P1": predicate_p1,
        "predicted_C_DP": int(predicted_c_dp),
        "predicted_regime": predicted_regime,
        **feats,
    }


def track_b_stage1(forbidden: set) -> dict[str, Any]:
    rng = np.random.default_rng(SEED)
    staged = []
    counts = {"split": 0, "borrow": 0, "donor_exact": 0}
    excluded_census = {"split": 0, "borrow": 0, "donor_exact": 0}
    draws = 0
    rejected_draws = 0
    for i in range(STREAM_CAP):
        if all(counts[k] >= QUOTAS[k] for k in QUOTAS):
            break
        draws += 1
        drawn = draw_instance(rng, i)
        if drawn is None:
            rejected_draws += 1
            continue
        fam, n, tp = drawn
        tp = _norm_tp(tp)
        six = [t for pair in tp for t in pair]
        if not all(
            p10.symp(six[a], six[b]) == 0 for a in range(6) for b in range(a + 1, 6)
        ):
            raise AssertionError({"qg3_trackb_not_pairwise_commuting": [i, list(tp)]})
        if tp == _norm_tp(TIMING_INSTANCE) or tp in forbidden:
            raise AssertionError({"qg3_trackb_freshness_violated": [i, list(tp)]})
        pred = predict_instance(tp, n)
        regime = pred["predicted_regime"]
        if counts[regime] < QUOTAS[regime]:
            counts[regime] += 1
            staged.append(
                {"stream_index": i, "family": fam, "n": n, **pred}
            )
        else:
            excluded_census[regime] += 1
    return {
        "seed": SEED,
        "stream_cap": STREAM_CAP,
        "quotas": QUOTAS,
        "draws_processed": draws,
        "f3_rejected_draws": rejected_draws,
        "staged_instances": staged,
        "staged_predicted_counts": counts,
        "excluded_predicted_census": excluded_census,
        "quota_gate_met": (
            len(staged) >= GATE_MIN_TOTAL
            and counts["split"] >= GATE_MIN_SPLIT
            and counts["borrow"] >= GATE_MIN_BORROW
        ),
    }


# ---- Track A (frozen library scan via committed R6R machinery) --------------

def track_a_stage1() -> dict[str, Any]:
    listing = r6r.pinned_tree_listing()
    ducc_listing = [(p, b) for p, b in listing if p.endswith(".ducc.results.txt")]
    listing_digest = sha256_text("\n".join(f"{b} {p}" for p, b in ducc_listing) + "\n")
    eligible = r6r.eligible_candidates(listing)
    qg3_candidates = [c for c in eligible if c["blob"] not in COMMITTED_BLOBS]
    attempts = []
    admitted_batches = []
    for cfg in qg3_candidates[:TRACKA_SCAN_CAP]:
        if cfg["path"].split("/")[0] in r6r.EXCLUDED_MOLECULES:
            raise AssertionError("qg3 exclusion breached in candidate order")
        terms0, _max_imag, observed_blob = r6f._load_terms_verified(cfg)
        if observed_blob != cfg["blob"]:
            raise AssertionError({"qg3_blob_mismatch": cfg["path"]})
        record = {
            "path": cfg["path"],
            "blob": cfg["blob"],
            "n_qubits": cfg["n_qubits"],
            "terms": len(terms0),
        }
        if len(terms0) > TRACKA_TERM_CAP:
            attempts.append(
                {**record, "admitted": False, "reason": "SKIPPED_TERM_BUDGET"}
            )
            continue
        result = r6r.try_admit(cfg)
        if not result["admitted"]:
            attempts.append(
                {**record, "admitted": False, "reason": result["reason"]}
            )
            continue
        attempts.append({**record, "admitted": True, "reason": None})
        n = int(cfg["n_qubits"])
        terms = result["terms"]
        six = result["six"]
        matchings, rows = r6r.stage1_predict(terms, six, n)
        admitted_batches.append(
            {
                "subject": {
                    "path": cfg["path"],
                    "commit": r6r.PINNED_COMMIT,
                    "blob": cfg["blob"],
                    "n_qubits": n,
                    "n_occ": cfg["n_occ"],
                    "n_virt": cfg["n_virt"],
                    "n_orb": cfg["n_orb"],
                    "terms": len(terms),
                    "max_imag": float(result["max_imag"]),
                    "frozen_source_indices": six,
                    "champion_windows": result["champion_windows"],
                    "window_champions_available": result[
                        "window_champions_available"
                    ],
                },
                "rows": rows,
                "_terms": terms,
                "_six": six,
                "_matchings": matchings,
            }
        )
    stretched_fetched = any(
        a["path"] == r6r.PROTECTED_STRETCHED_N2_PATH for a in attempts
    )
    if stretched_fetched:
        raise AssertionError("qg3 protected stretched-N2 fetched")
    if any(a["path"].split("/")[0] in r6r.EXCLUDED_MOLECULES for a in attempts):
        raise AssertionError("qg3 excluded molecule fetched")
    return {
        "library": {
            "repo": r6r.REPO,
            "commit": r6r.PINNED_COMMIT,
            "ducc_results_files_at_commit": len(ducc_listing),
            "ducc_listing_sha256": listing_digest,
        },
        "selection_rule": {
            "base_rule": "committed_R6R_eligibility_and_order",
            "excluded_molecules": list(r6r.EXCLUDED_MOLECULES),
            "committed_subject_blobs_excluded": list(COMMITTED_BLOBS),
            "scan_cap": TRACKA_SCAN_CAP,
            "term_cap": TRACKA_TERM_CAP,
            "eligible_candidate_count_after_committed_exclusion": len(
                qg3_candidates
            ),
            "scanned_candidates_in_order": [
                {"path": c["path"], "blob": c["blob"], "n_qubits": c["n_qubits"]}
                for c in qg3_candidates[:TRACKA_SCAN_CAP]
            ],
        },
        "attempts": attempts,
        "admitted_batches": admitted_batches,
    }


# ---- staging ----------------------------------------------------------------

def emit_stage1(payload: dict[str, Any]) -> str:
    global _STAGE1_EMITTED
    blob = canonical_json(payload)
    digest = sha256_text(blob)
    print("ORIONQ_QG3_STAGE1_PREDICTION=" + blob)
    print("ORIONQ_QG3_STAGE1_DIGEST=" + digest)
    sys.stdout.flush()
    _STAGE1_EMITTED = True
    return digest


# ---- referee ----------------------------------------------------------------

def _truth_row(wit, pred) -> dict[str, Any]:
    if not all(wit["checks"].values()):
        raise AssertionError({"qg3_dp_witness_failed": pred})
    c_dp = int(wit["C_R6M"])
    c_dplus = int(pred["C_Dplus"])
    c_r6l = int(pred["C_R6L"])
    f_b_eff = int(pred["f_B"])
    if not (c_dp <= c_dplus <= c_r6l):
        raise AssertionError({"qg3_sandwich_violated": [c_dp, c_dplus, c_r6l]})
    if c_dp > f_b_eff:
        raise AssertionError({"qg3_borrow_soundness_violated": [c_dp, f_b_eff]})
    if c_dp == c_r6l:
        truth_regime = "donor_exact"
    elif c_dp == c_dplus:
        truth_regime = "split"
    else:
        truth_regime = "borrow"
    pinched = c_dp == c_dplus
    return {
        "C_DP": c_dp,
        "truth_regime": truth_regime,
        "C_Dxx_pinched": c_dp if pinched else None,
        "dxx_pinched_equal": pinched,
        "dp_witness_checks_pass": True,
        "cost_match": c_dp == int(pred["predicted_C_DP"]),
        "regime_match": truth_regime == pred["predicted_regime"],
    }


def referee_track_a(admitted_batches) -> None:
    for batch in admitted_batches:
        terms = batch.pop("_terms")
        six = batch.pop("_six")
        matchings = batch.pop("_matchings")
        n = int(batch["subject"]["n_qubits"])
        merged = []
        for pairs, pred in zip(matchings, batch["rows"], strict=True):
            if not _STAGE1_EMITTED:
                raise AssertionError("qg3 staging violated: referee before prediction")
            r6m._local_table.cache_clear()
            wit = r6m.exact_r6m_matching(terms, pairs, n, six)
            merged.append({**pred, **_truth_row(wit, pred)})
        batch["rows"] = merged


def referee_track_b(staged_instances) -> None:
    for row in staged_instances:
        if not _STAGE1_EMITTED:
            raise AssertionError("qg3 staging violated: referee before prediction")
        tp = _norm_tp(row["targets"])
        n = int(row["n"])
        terms = r6m._synthetic_terms(tp)
        r6m._local_table.cache_clear()
        wit = r6m.exact_r6m_matching(terms, MATCHING, n, list(range(6)))
        row.update(_truth_row(wit, row))


# ---- main -------------------------------------------------------------------

CLAIM_BOUNDARY = {
    "covers": (
        "One prospective test of the committed R6Q predicate P1 and the two-trade "
        "completeness identity C_DP == min(C_R6L, C_Dplus, f_B), including "
        "POSITIVE split- and borrow-regime membership with exact predicted DP "
        "cost, on (a) all 15 frozen-grammar matchings of every real DUCC-library "
        "batch admitted by the frozen Track-A scan rule and (b) the staged "
        "instances of the frozen seed-20260824 engineered commuting generator, "
        "with every prediction digest-printed before the unrestricted R6M DP "
        "referee was run."
    ),
    "machine_evidenced_only": (
        "Any confirmation is machine-evidenced only on the staged rows of this "
        "run, in addition to the domains already recorded in the committed "
        "R6Q/R6R receipts. It is NOT a theorem for all n or all targets; the D++ "
        "value is recorded only via the exact containment pinch where C_DP == "
        "C_Dplus, exactly as the committed R6P/R6R lanes. If the Track-A census "
        "finds no trade-regime real batch, the positive trade-regime claim is "
        "synthetic-only (engineered instances), and the real-library finding is "
        "the census itself."
    ),
    "does_not_cover": (
        "Other objectives, other grammars, rotation-count trade-offs, other "
        "batches or subjects, or any claim of donor or R6 novelty credit. A "
        "refutation claims exactly the mismatches reported verbatim."
    ),
}


def main() -> dict[str, Any]:
    start = time.monotonic()

    f3_binding = bool(np.array_equal(r6q.F3.astype(np.int64), r6m._F3))
    if not f3_binding:
        raise AssertionError("qg3 F3 table binding to frozen r6m._F3 failed")

    protocol_path = (
        Path(__file__).resolve().parents[3]
        / "development"
        / "orion-qg-regime-geometry"
        / PROTOCOL_NAME
    )
    protocol_sha = sha256_text(protocol_path.read_text())

    forbidden = _committed_verbatim_targets()

    # ---- stage 1 (no DP anywhere before emit_stage1) ----
    track_a = track_a_stage1()
    track_b = track_b_stage1(forbidden)

    stage1_payload = {
        "protocol": "QG3_BOUNDARY_PROSPECTIVE_PROTOCOL",
        "protocol_sha256": protocol_sha,
        "predicate": (
            "P1(t) := [C_R6L(t) == C_Dplus(t)] AND [f_B(t) >= C_R6L(t)]; "
            "predicted_C_DP := min(C_R6L, C_Dplus, f_B)"
        ),
        "track_a": {
            "library": track_a["library"],
            "selection_rule": track_a["selection_rule"],
            "attempts": track_a["attempts"],
            "admitted_batches": [
                {"subject": b["subject"], "rows": b["rows"]}
                for b in track_a["admitted_batches"]
            ],
        },
        "track_b": {
            key: value
            for key, value in track_b.items()
            if key != "staged_instances"
        }
        | {"staged_instances": track_b["staged_instances"]},
    }
    stage1_digest = emit_stage1(stage1_payload)

    # ---- stage 2: unrestricted DP referee ----
    referee_track_a(track_a["admitted_batches"])
    referee_track_b(track_b["staged_instances"])

    a_rows = [
        {**row, "subject_path": batch["subject"]["path"]}
        for batch in track_a["admitted_batches"]
        for row in batch["rows"]
    ]
    b_rows = track_b["staged_instances"]
    all_rows = a_rows + b_rows
    mismatches = [
        row for row in all_rows if not (row["cost_match"] and row["regime_match"])
    ]
    all_match = not mismatches

    def _census(rows, key):
        out = {"donor_exact": 0, "split": 0, "borrow": 0}
        for row in rows:
            out[row[key]] += 1
        return out

    track_a_predicted = _census(a_rows, "predicted_regime")
    track_a_truth = _census(a_rows, "truth_regime")
    track_b_truth = _census(b_rows, "truth_regime")
    any_real_trade = (track_a_predicted["split"] + track_a_predicted["borrow"]) > 0
    if any_real_trade:
        track_a_finding = "REAL_TRADE_REGIME_BATCH_FOUND"
    elif track_a["admitted_batches"]:
        track_a_finding = "LIBRARY_SCAN_ALL_DONOR_EXACT"
    else:
        track_a_finding = "NO_ADMITTED_REAL_BATCH"

    quota_met = bool(track_b["quota_gate_met"])
    if not all_match:
        outcome = "POSITIVE_REGIME_PREDICTIONS_REFUTED"
        authority = (
            "ORIONQG_QG3_BOUNDARY_PROSPECTIVE_POSITIVE_REGIME_PREDICTIONS_REFUTED__"
            "PREDICATE_DOMAIN_BOUNDARY_LOCALIZED__NOT_R6"
        )
        responsibility = (
            "RESP:MISMATCHING_ROWS_REPORTED_VERBATIM__"
            "VERIFIED_DOMAIN_BOUNDARY_LOCALIZED"
        )
    elif not quota_met:
        outcome = "TRACKB_QUOTA_UNMET"
        authority = "ORIONQG_QG3_BOUNDARY_PROSPECTIVE_TRACKB_QUOTA_UNMET__NOT_R6"
        responsibility = (
            "RESP:FROZEN_GENERATOR_DID_NOT_FILL_TRADE_QUOTAS__RULE_NOT_WEAKENED__"
            "ALL_STAGED_PREDICTIONS_STILL_REFEREED"
        )
    else:
        outcome = "POSITIVE_REGIME_PREDICTIONS_CONFIRMED"
        authority = (
            "ORIONQG_QG3_BOUNDARY_PROSPECTIVE_POSITIVE_REGIME_PREDICTIONS_"
            "CONFIRMED__SPLIT_AND_BORROW_PREDICTED_BEFORE_DP__NOT_R6"
        )
        responsibility = (
            "RESP:TRADE_REGIME_MEMBERSHIP_AND_EXACT_DP_COST_PREDICTED_BEFORE_"
            "COMPUTATION_ON_ALL_STAGED_ROWS"
        )

    gates = {
        "f3_table_binding_exact": f3_binding,
        "protocol_frozen_and_hashed": True,
        "pinned_commit_and_blobs": True,
        "all_candidate_blobs_outside_committed_subject_blobs": all(
            a["blob"] not in COMMITTED_BLOBS for a in track_a["attempts"]
        ),
        "no_excluded_molecule_fetched": all(
            a["path"].split("/")[0] not in r6r.EXCLUDED_MOLECULES
            for a in track_a["attempts"]
        ),
        "reserved_stretched_n2_unread": True,
        "trackb_pairwise_commuting_all_instances": True,  # hard-asserted inline
        "trackb_freshness_asserts": True,  # hard-asserted inline
        "trackb_quota_gate": quota_met,
        "stage1_digest_printed_before_ground_truth": _STAGE1_EMITTED,
        "sandwich_and_borrow_soundness_all_rows": True,  # hard-asserted
        "dp_witness_checks_all_rows": all(
            row["dp_witness_checks_pass"] for row in all_rows
        ),
        "prediction_matches_ground_truth_every_row": all_match,
    }

    result = {
        "schema": "ORIONQG.QG3.BoundaryProspective.v1",
        "authority": authority,
        "scope": (
            "POSITIVE_TRADE_REGIME_PREDICTION_BEFORE_COMPUTATION_OVER_FROZEN_"
            "R6M_GRAMMAR__LIBRARY_SCAN_PLUS_ENGINEERED_SYNTHETIC__NOT_R6"
        ),
        "responsibility": responsibility,
        "protocol": "QG3_BOUNDARY_PROSPECTIVE_PROTOCOL",
        "protocol_sha256": protocol_sha,
        "outcome": outcome,
        "stage1_digest": stage1_digest,
        "track_a": {
            "library": track_a["library"],
            "selection_rule": track_a["selection_rule"],
            "attempts": track_a["attempts"],
            "batches_scanned": len(track_a["attempts"]),
            "batches_admitted": len(track_a["admitted_batches"]),
            "batches_skipped_term_budget": sum(
                1
                for a in track_a["attempts"]
                if a["reason"] == "SKIPPED_TERM_BUDGET"
            ),
            "admitted_batches": [
                {"subject": b["subject"], "rows": b["rows"]}
                for b in track_a["admitted_batches"]
            ],
            "matchings_refereed": len(a_rows),
            "predicted_regime_census": track_a_predicted,
            "truth_regime_census": track_a_truth,
            "finding": track_a_finding,
        },
        "track_b": {
            key: value
            for key, value in track_b.items()
            if key != "staged_instances"
        }
        | {
            "staged_instances": b_rows,
            "truth_regime_census": track_b_truth,
        },
        "rows_staged_total": len(all_rows),
        "match_count": sum(
            1 for row in all_rows if row["cost_match"] and row["regime_match"]
        ),
        "mismatches_verbatim": mismatches,
        "dxx_direct_sweep_run": False,
        "dxx_obtained_by_exact_containment_pinch_where_applicable": True,
        "gates": gates,
        "claim_boundary": CLAIM_BOUNDARY,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    if "NOT_R6" not in result["authority"]:
        raise AssertionError("QG3 authority ceiling violated")
    Path(__file__).with_name("QG3_BOUNDARY_PROSPECTIVE_RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("ORIONQ_QG3_BOUNDARY_PROSPECTIVE=" + canonical_json(result))
    print(
        "qg3_runtime_seconds=%.3f" % (time.monotonic() - start),
        file=sys.stderr,
    )
    return result


if __name__ == "__main__":
    main()
