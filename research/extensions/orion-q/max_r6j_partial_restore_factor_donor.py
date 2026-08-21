#!/usr/bin/env python3
"""MAX-R6J donor-owned partial Restore common-factor search."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import max_r6b_tare_transformation_reuse_donor as reuse
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6h_partial_tag_sharing_donor as r6h
import max_r6_p10_candidate_blind_frame_optimizer as p10

TOL = 1e-12


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _local_letter(key: tuple[int, int], q: int) -> tuple[int, int]:
    return ((key[0] >> q) & 1, (key[1] >> q) & 1)


def _set_local(key: tuple[int, int], q: int, bits: tuple[int, int]) -> tuple[int, int]:
    x, z = key
    x &= ~(1 << q)
    z &= ~(1 << q)
    x |= int(bits[0]) << q
    z |= int(bits[1]) << q
    return int(x), int(z)


def factor_restore_pair(
    signed_a: tuple[int, tuple[int, int]],
    signed_b: tuple[int, tuple[int, int]],
    n: int,
) -> dict[str, Any]:
    phase_a, ta = int(signed_a[0]), tuple(signed_a[1])
    phase_b, tb = int(signed_b[0]), tuple(signed_b[1])
    g = (0, 0)
    matching_nonidentity = 0
    for q in range(n):
        la = _local_letter(ta, q)
        lb = _local_letter(tb, q)
        if la == lb and la != (0, 0):
            g = _set_local(g, q, la)
            matching_nonidentity += 1

    # Binary Pauli residual because G is self-inverse in the phase-free quotient.
    ua = p10.mul(g, ta)
    ub = p10.mul(g, tb)
    got_a, exponent_a = reuse.mul_phase(g, ua, n)
    got_b, exponent_b = reuse.mul_phase(g, ub, n)
    if got_a != ta or got_b != tb:
        raise AssertionError({"R6J_binary_factor_identity_failed": [ta, tb, g, ua, ub]})

    # The original signed Restore is i^phase T.  With common Hermitian G and
    # Hermitian residual U, store the residual phase needed so
    # i^residual_phase * (G U) == i^phase * T.
    residual_phase_a = (phase_a - int(exponent_a)) % 4
    residual_phase_b = (phase_b - int(exponent_b)) % 4
    support = int(p10.wt(g) + p10.wt(ua) + p10.wt(ub))
    formula = int(p10.wt(ta) + p10.wt(tb) - matching_nonidentity)
    rec = {
        "G": list(g),
        "U_A": list(ua),
        "U_B": list(ub),
        "original_phase_A": phase_a,
        "original_phase_B": phase_b,
        "G_times_U_phase_A": int(exponent_a),
        "G_times_U_phase_B": int(exponent_b),
        "residual_phase_A": int(residual_phase_a),
        "residual_phase_B": int(residual_phase_b),
        "matching_nonidentity_local_letters": matching_nonidentity,
        "support": support,
        "checks": {
            "binary_identity_A": got_a == ta,
            "binary_identity_B": got_b == tb,
            "phase_identity_A": (residual_phase_a + int(exponent_a)) % 4 == phase_a,
            "phase_identity_B": (residual_phase_b + int(exponent_b)) % 4 == phase_b,
            "support_formula": support == formula,
        },
    }
    if not all(rec["checks"].values()):
        raise AssertionError({"R6J_factor_witness_failed": rec})
    return rec


def _tag_key(signature: reuse.ReuseSignature):
    return signature.s0, signature.s1, signature.labels


def _block(terms, indices):
    return {"targets": [list(terms[i][0]) for i in indices], "term_indices": list(indices)}


def _all_by_tag(block: dict[str, Any], n: int):
    raw = reuse.complete_source_signatures(block, n)
    groups: dict[Any, list[reuse.ReuseSignature]] = {}
    for signature in raw.values():
        if not r6h._representation_valid(signature, block, n):
            raise AssertionError({"R6J_invalid_R6H_signature": signature.provenance})
        groups.setdefault(_tag_key(signature), []).append(signature)
    for key in groups:
        groups[key].sort(key=lambda s: (s.provenance, s.corrections))
    return raw, groups


def best_restore_factor(a: dict[str, Any], b: dict[str, Any], n: int):
    raw_a, groups_a = _all_by_tag(a, n)
    raw_b, groups_b = _all_by_tag(b, n)
    common = sorted(set(groups_a) & set(groups_b))
    best = None
    evaluated_pairs = 0
    for tag in common:
        s0, s1, labels = tag
        tag_support = int(2 * (p10.wt(s0) + p10.wt(s1)))
        for sa in groups_a[tag]:
            for sb in groups_b[tag]:
                evaluated_pairs += 1
                branches = [
                    factor_restore_pair(sa.corrections[k], sb.corrections[k], n)
                    for k in range(3)
                ]
                factor_support = int(sum(row["support"] for row in branches))
                total = int(tag_support + factor_support)
                checks = {
                    "same_tag_key": _tag_key(sa) == _tag_key(sb),
                    "blocks_disjoint": set(a["term_indices"]).isdisjoint(b["term_indices"]),
                    "A_valid": r6h._representation_valid(sa, a, n),
                    "B_valid": r6h._representation_valid(sb, b, n),
                    "branch_factor_checks": all(all(row["checks"].values()) for row in branches),
                    "cost_recomputed": total == tag_support + sum(row["support"] for row in branches),
                }
                if not all(checks.values()):
                    raise AssertionError({"R6J_pair_checks_failed": checks})
                rec = {
                    "C_restore_factor": total,
                    "tag_support_twice_shared": tag_support,
                    "factorized_restore_support": factor_support,
                    "original_restore_support_A": r6h._restore_support(sa),
                    "original_restore_support_B": r6h._restore_support(sb),
                    "restore_support_saved": int(
                        r6h._restore_support(sa) + r6h._restore_support(sb) - factor_support
                    ),
                    "tag_key": {"S0": list(s0), "S1": list(s1), "labels": list(labels)},
                    "block_A_provenance": [
                        sa.provenance[0], [list(x) for x in sa.provenance[1]], list(sa.provenance[2])
                    ],
                    "block_B_provenance": [
                        sb.provenance[0], [list(x) for x in sb.provenance[1]], list(sb.provenance[2])
                    ],
                    "block_A_signed_T": [
                        {"phase": int(x[0]), "T": list(x[1])} for x in sa.corrections
                    ],
                    "block_B_signed_T": [
                        {"phase": int(x[0]), "T": list(x[1])} for x in sb.corrections
                    ],
                    "branches": branches,
                    "checks": checks,
                }
                order = (
                    total,
                    -rec["restore_support_saved"],
                    tag_support,
                    rec["original_restore_support_A"] + rec["original_restore_support_B"],
                    tag,
                    sa.provenance,
                    sb.provenance,
                )
                if best is None or order < best[0]:
                    best = order, rec
    return {
        "source_signature_count_A": len(raw_a),
        "source_signature_count_B": len(raw_b),
        "common_tag_key_count": len(common),
        "representation_pair_count": evaluated_pairs,
        "best": None if best is None else best[1],
    }


def _lambda(terms, triple):
    return float((3.0 * sum(float(terms[i][1]) ** 2 for i in triple)) ** 0.5)


def _incumbent_rows(terms, source_indices, n: int):
    r6d_eval = r6d._evaluate_fixed_batch(terms, source_indices, n)
    if len(r6d_eval.get("all_partitions", [])) != 10 or r6d_eval.get("all_witnesses_valid") is not True:
        raise AssertionError("R6J R6D incumbent replay failed")
    rows = []
    for partition in r6d_eval["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        block_a, block_b = _block(terms, a), _block(terms, b)
        h = r6h.best_partial_tag(block_a, block_b, n)
        h_cost = None if h["best"] is None else int(h["best"]["C_partial_tag"])
        base = next(
            row for row in r6d_eval["eligible_points"] if row["partition"] == [list(a), list(b)]
        )
        known = [int(base["C_frame_only"])]
        if base.get("C_reuse") is not None:
            known.append(int(base["C_reuse"]))
        if h_cost is not None:
            known.append(h_cost)
        rows.append({
            "partition": [list(a), list(b)],
            "Lambda_batch": float(_lambda(terms, a) + _lambda(terms, b)),
            "C_incumbent": min(known),
            "C_frame_only": int(base["C_frame_only"]),
            "C_reuse": base.get("C_reuse"),
            "C_R6H": h_cost,
        })
    return r6d_eval, rows


def _envelope(rows, lam: float):
    eligible = [row for row in rows if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"R6J_empty_incumbent_envelope": lam})
    best = min(eligible, key=lambda row: (int(row["C_incumbent"]), float(row["Lambda_batch"]), row["partition"]))
    return int(best["C_incumbent"]), best


def hostile_validation():
    if r6h.hostile_validation()["all_pass"] is not True:
        raise AssertionError("R6J inherited R6H hostile failure")
    x, y, z = (1, 0), (1, 1), (0, 1)
    same = factor_restore_pair((0, x), (0, x), 1)
    different = factor_restore_pair((0, x), (0, z), 1)
    gates = {
        "r6b_phase_hostile_pass": reuse.hostile_validation()["all_pass"],
        "r6h_partial_tag_hostile_pass": r6h.hostile_validation()["all_pass"],
        "identical_nonidentity_saves_one": same["support"] == 1 and same["matching_nonidentity_local_letters"] == 1,
        "different_nonidentity_saves_zero": different["support"] == 2 and different["matching_nonidentity_local_letters"] == 0,
        "exact_phase_reconstruction_same": all(same["checks"].values()),
        "exact_phase_reconstruction_different": all(different["checks"].values()),
    }
    if not all(gates.values()):
        raise AssertionError({"R6J_hostile_failure": gates})
    return {"gates": gates, "all_pass": True, "same_letter": same, "different_letter": different}


def run_subject(name: str, cfg):
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    if len(source_indices) != 6:
        return {
            "subject": name, "source_blob_expected": cfg["blob"], "source_blob_observed": observed_blob,
            "source_blob_verified": observed_blob == cfg["blob"], "batch_complete": False,
            "r6b_window_champions_available": len(champions), "frozen_source_indices": list(source_indices),
            "partition_count": 0, "strict_count": 0, "strict_budget_matched_improvement_exists": False,
            "best_strict": None, "max_imag": float(max_imag),
        }, {"subject": name, "partitions": []}

    r6d_eval, incumbent_rows = _incumbent_rows(terms, source_indices, n)
    rows = []
    for partition in r6d_eval["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        candidate = best_restore_factor(_block(terms, a), _block(terms, b), n)
        cost = None if candidate["best"] is None else int(candidate["best"]["C_restore_factor"])
        lam = float(_lambda(terms, a) + _lambda(terms, b))
        inc, witness = _envelope(incumbent_rows, lam)
        delta = None if cost is None else int(inc - cost)
        rows.append({
            "partition": [list(a), list(b)], "Lambda_batch": lam,
            "restore_factor": candidate, "C_R6J": cost,
            "C_incumbent_envelope": inc,
            "incumbent_envelope_witness": witness,
            "delta_vs_incumbent": delta,
            "strict_budget_matched_improvement": delta is not None and delta > 0,
        })
    strict = sorted(
        (row for row in rows if row["strict_budget_matched_improvement"]),
        key=lambda row: (-int(row["delta_vs_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )
    return {
        "subject": name, "source_blob_expected": cfg["blob"], "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"], "batch_complete": True,
        "r6b_window_champions_available": len(champions), "frozen_source_indices": list(source_indices),
        "partition_count": len(r6d_eval["all_partitions"]), "eligible_partition_count": len(rows),
        "strict_count": len(strict), "strict_budget_matched_improvement_exists": bool(strict),
        "best_strict": None if not strict else strict[0], "max_imag": float(max_imag),
    }, {"subject": name, "incumbent_rows": incumbent_rows, "partitions": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detail-json", type=Path, default=None)
    args = parser.parse_args()
    hostile = hostile_validation()
    summaries, details = {}, {}
    for name, cfg in p10.base.SUBJECTS.items():
        summaries[name], details[name] = run_subject(name, cfg)
    h4 = summaries["H4"]["strict_budget_matched_improvement_exists"]
    n2 = summaries["N2"]["strict_budget_matched_improvement_exists"]
    if h4 and n2:
        authority = "MAX_R6J_PARTIAL_RESTORE_FACTOR_DONOR_POSITIVE__ABSORB__NOT_R6"
        responsibility = "RESP:ABSORB_PARTIAL_RESTORE_FACTOR_DONOR"
        supported = True
    elif h4 or n2:
        authority = "MAX_R6J_PARTIAL_RESTORE_FACTOR_DONOR_PARTIAL__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_DONOR_SPLIT"
        supported = False
    else:
        authority = "MAX_R6J_PARTIAL_RESTORE_FACTOR_DONOR_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_RESTORE_FACTOR_CLOSURE"
        supported = False
    gates = {
        "hostile_pass": hostile["all_pass"],
        "source_blobs_observed_match": all(row["source_blob_verified"] for row in summaries.values()),
        "frozen_sixterm_batches_complete": all(row["batch_complete"] for row in summaries.values()),
        "exactly_ten_partitions": all(row["partition_count"] == 10 for row in summaries.values()),
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"R6J_integrity_gate_failure": gates})
    detail_bundle = {"schema": "ORIONQ.MAXR6J.PartialRestoreFactorDetail.v1", "subjects": details}
    detail_sha = digest(detail_bundle)
    persisted_ok = True
    if args.detail_json is not None:
        args.detail_json.write_text(canonical_json(detail_bundle) + "\n")
        persisted_ok = digest(json.loads(args.detail_json.read_text())) == detail_sha
        if not persisted_ok:
            raise AssertionError("R6J persisted detail digest mismatch")
    result = {
        "schema": "ORIONQ.MAXR6J.PartialRestoreFactorDonor.v1", "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_WEIGHT_ONE_TAG_RESTORE_FACTOR__NOT_R6",
        "responsibility": responsibility, "development_supported": supported,
        "subjects": summaries, "hostile": hostile, "gates": gates,
        "detail_bundle_sha256": detail_sha, "detail_persisted_digest_match": persisted_ok,
        "donor_novelty_credit": False, "novelty_credit": False, "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    print("ORIONQ_MAX_R6J_PARTIAL_RESTORE_FACTOR=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
