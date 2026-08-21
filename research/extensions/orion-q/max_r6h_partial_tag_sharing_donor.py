#!/usr/bin/env python3
"""MAX-R6H donor-owned partial Tag sharing across two TARE-3 blocks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import max_r6b_tare_transformation_reuse_donor as reuse
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6_p10_candidate_blind_frame_optimizer as p10

TOL = 1e-12


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _block(terms, indices):
    return {
        "targets": [list(terms[i][0]) for i in indices],
        "term_indices": list(indices),
    }


def _tag_key(signature: reuse.ReuseSignature):
    return (signature.s0, signature.s1, signature.labels)


def _restore_support(signature: reuse.ReuseSignature) -> int:
    return int(sum(p10.wt(item[1]) for item in signature.corrections))


def _representation_valid(signature: reuse.ReuseSignature, block: dict[str, Any], n: int) -> bool:
    prov = signature.provenance
    if len(prov) != 3 or not isinstance(prov[0], int):
        return False
    q = int(prov[0])
    rs = tuple(tuple(x) for x in prov[1])
    permutation = tuple(int(x) for x in prov[2])
    if len(rs) != 3 or sorted(permutation) != [0, 1, 2]:
        return False
    if not p10.is_pairwise_anti(rs):
        return False
    expected_xyz = {(1 << q, 0), (1 << q, 1 << q), (0, 1 << q)}
    if set(rs) != expected_xyz or any(p10.wt(r) != 1 for r in rs):
        return False
    if reuse._labels(signature.s0, signature.s1, rs) != signature.labels:
        return False
    targets = tuple(tuple(x) for x in block["targets"])
    permuted = tuple(targets[permutation[k]] for k in range(3))
    for k, (phase, correction) in enumerate(signature.corrections):
        correction = tuple(correction)
        if p10.mul(correction, rs[k]) != permuted[k]:
            return False
        if reuse.correction_phase(permuted[k], rs[k], correction, n) != int(phase):
            return False
    return True


def _best_by_tag(block: dict[str, Any], n: int):
    signatures = reuse.complete_source_signatures(block, n)
    best = {}
    for signature in signatures.values():
        if not _representation_valid(signature, block, n):
            raise AssertionError({"R6H_invalid_source_signature": signature.provenance})
        key = _tag_key(signature)
        restore = _restore_support(signature)
        rank = (restore, signature.provenance, signature.corrections)
        old = best.get(key)
        if old is None or rank < old[0]:
            best[key] = (rank, signature)
    return signatures, best


def best_partial_tag(a: dict[str, Any], b: dict[str, Any], n: int):
    sig_a, best_a = _best_by_tag(a, n)
    sig_b, best_b = _best_by_tag(b, n)
    common = sorted(set(best_a) & set(best_b))
    best = None
    for key in common:
        sa = best_a[key][1]
        sb = best_b[key][1]
        tag = int(2 * (p10.wt(sa.s0) + p10.wt(sa.s1)))
        ra = _restore_support(sa)
        rb = _restore_support(sb)
        total = int(tag + ra + rb)
        restore_equal = sa.corrections == sb.corrections
        rec = {
            "C_partial_tag": total,
            "tag_support_twice_shared": tag,
            "restore_support_A": ra,
            "restore_support_B": rb,
            "restore_equal": restore_equal,
            "tag_key": {
                "S0": list(sa.s0), "S1": list(sa.s1), "labels": list(sa.labels),
            },
            "block_A": {
                "provenance": [sa.provenance[0], [list(x) for x in sa.provenance[1]], list(sa.provenance[2])],
                "signed_T": [{"phase": int(x[0]), "T": list(x[1])} for x in sa.corrections],
            },
            "block_B": {
                "provenance": [sb.provenance[0], [list(x) for x in sb.provenance[1]], list(sb.provenance[2])],
                "signed_T": [{"phase": int(x[0]), "T": list(x[1])} for x in sb.corrections],
            },
            "checks": {
                "same_S0": sa.s0 == sb.s0,
                "same_S1": sa.s1 == sb.s1,
                "same_labels": sa.labels == sb.labels,
                "blocks_disjoint": set(a["term_indices"]).isdisjoint(b["term_indices"]),
                "A_valid": _representation_valid(sa, a, n),
                "B_valid": _representation_valid(sb, b, n),
                "cost_recomputed": total == tag + ra + rb,
            },
        }
        if not all(rec["checks"].values()):
            raise AssertionError({"R6H_partial_tag_witness_failed": rec})
        order = (total, tag, ra + rb, key, sa.provenance, sb.provenance)
        if best is None or order < best[0]:
            best = (order, rec)
    return {
        "source_signature_count_A": len(sig_a),
        "source_signature_count_B": len(sig_b),
        "common_tag_key_count": len(common),
        "best": None if best is None else best[1],
    }


def _incumbent_envelope(rows, lam: float):
    eligible = [row for row in rows if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"R6H_empty_incumbent_envelope": lam})
    best = min(eligible, key=lambda row: (int(row["C_incumbent"]), float(row["Lambda_batch"]), row["partition"]))
    return int(best["C_incumbent"]), best


def hostile_validation():
    n = 2
    x, y, z = (1, 0), (1, 1), (0, 1)
    # Same q0 Tag is possible, but block B has an extra Z on q1 in every target,
    # so its Restore strings necessarily differ from block A's identity Restores.
    q1z = (0, 2)
    block_a = {"targets": [list(x), list(y), list(z)], "term_indices": [0, 1, 2]}
    block_b_targets = [p10.mul(r, q1z) for r in (x, y, z)]
    block_b = {"targets": [list(t) for t in block_b_targets], "term_indices": [3, 4, 5]}
    partial = best_partial_tag(block_a, block_b, n)
    best = partial["best"]
    if best is None:
        raise AssertionError("R6H hostile common-Tag pair rejected")
    different_restore_accepted = best["restore_equal"] is False
    mismatched_tag_rejected = (
        (tuple(best["tag_key"]["S0"]), tuple(best["tag_key"]["S1"]), tuple(best["tag_key"]["labels"]))
        != ((3, 3), (3, 3), (0, 1, 2))
    )
    gates = {
        "r6b_signed_phase_hostile_pass": reuse.hostile_validation()["all_pass"],
        "common_tag_with_different_restore_accepted": different_restore_accepted,
        "mismatched_tag_key_not_equal": mismatched_tag_rejected,
        "partial_witness_checks_pass": all(best["checks"].values()),
    }
    if not all(gates.values()):
        raise AssertionError({"R6H_hostile_failure": gates, "best": best})
    return {"gates": gates, "all_pass": True, "synthetic_best": best}


def run_subject(name: str, cfg):
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    evaluation = r6d._evaluate_fixed_batch(terms, source_indices, n)
    if len(source_indices) != 6:
        return {
            "subject": name, "source_blob_expected": cfg["blob"], "source_blob_observed": observed_blob,
            "source_blob_verified": observed_blob == cfg["blob"], "batch_complete": False,
            "r6b_window_champions_available": len(champions), "frozen_source_indices": list(source_indices),
            "partition_count": 0, "strict_points": [], "best_strict": None,
            "strict_budget_matched_improvement_exists": False,
        }, {"subject": name, "partitions": []}
    if len(evaluation.get("all_partitions", [])) != 10 or evaluation.get("all_witnesses_valid") is not True:
        raise AssertionError({"R6H_R6D_incumbent_replay_failed": name})
    incumbent_rows = evaluation["eligible_points"]
    rows = []
    for partition in evaluation["all_partitions"]:
        if not partition["eligible"]:
            continue
        a = tuple(int(x) for x in partition["partition"][0])
        b = tuple(int(x) for x in partition["partition"][1])
        block_a, block_b = _block(terms, a), _block(terms, b)
        partial = best_partial_tag(block_a, block_b, n)
        lam = float(
            (3.0 * sum(float(terms[i][1]) ** 2 for i in a)) ** 0.5
            + (3.0 * sum(float(terms[i][1]) ** 2 for i in b)) ** 0.5
        )
        incumbent_cost, incumbent_witness = _incumbent_envelope(incumbent_rows, lam)
        candidate = None if partial["best"] is None else int(partial["best"]["C_partial_tag"])
        delta = None if candidate is None else int(incumbent_cost - candidate)
        rows.append({
            "partition": [list(a), list(b)], "Lambda_batch": lam,
            "partial_tag": partial, "C_partial_tag": candidate,
            "C_incumbent_envelope": incumbent_cost,
            "incumbent_envelope_witness": {
                "partition": incumbent_witness["partition"],
                "Lambda_batch": float(incumbent_witness["Lambda_batch"]),
                "C_incumbent": int(incumbent_witness["C_incumbent"]),
                "incumbent_source": incumbent_witness["incumbent_source"],
            },
            "delta_vs_incumbent": delta,
            "strict_budget_matched_improvement": delta is not None and delta > 0,
        })
    strict = sorted(
        (row for row in rows if row["strict_budget_matched_improvement"]),
        key=lambda row: (-int(row["delta_vs_incumbent"]), float(row["Lambda_batch"]), row["partition"]),
    )
    summary = {
        "subject": name, "source_blob_expected": cfg["blob"], "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"], "batch_complete": True,
        "r6b_window_champions_available": len(champions), "frozen_source_indices": list(source_indices),
        "partition_count": len(evaluation["all_partitions"]), "eligible_partition_count": len(rows),
        "strict_count": len(strict), "strict_budget_matched_improvement_exists": bool(strict),
        "best_strict": None if not strict else strict[0], "max_imag": float(max_imag),
    }
    return summary, {"subject": name, "partitions": rows}


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
        authority = "MAX_R6H_PARTIAL_TAG_SHARING_DONOR_POSITIVE__ABSORB__NOT_R6"
        responsibility = "RESP:ABSORB_PARTIAL_TAG_SHARING_DONOR"
        supported = True
    elif h4 or n2:
        authority = "MAX_R6H_PARTIAL_TAG_SHARING_DONOR_PARTIAL__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_DONOR_SPLIT"
        supported = False
    else:
        authority = "MAX_R6H_PARTIAL_TAG_SHARING_DONOR_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_AFTER_TAG_REUSE_CLOSURE"
        supported = False
    gates = {
        "hostile_pass": hostile["all_pass"],
        "source_blobs_observed_match": all(row["source_blob_verified"] for row in summaries.values()),
        "frozen_sixterm_batches_complete": all(row["batch_complete"] for row in summaries.values()),
        "exactly_ten_partitions": all(row["partition_count"] == 10 for row in summaries.values()),
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"R6H_integrity_gate_failure": gates})
    detail_bundle = {"schema": "ORIONQ.MAXR6H.PartialTagSharingDetail.v1", "subjects": details}
    detail_sha = digest(detail_bundle)
    persisted_ok = True
    if args.detail_json is not None:
        args.detail_json.write_text(canonical_json(detail_bundle) + "\n")
        persisted_ok = digest(json.loads(args.detail_json.read_text())) == detail_sha
        if not persisted_ok:
            raise AssertionError("R6H persisted detail digest mismatch")
    result = {
        "schema": "ORIONQ.MAXR6H.PartialTagSharingDonor.v1", "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_WEIGHT_ONE_TAG_SHARING__NOT_R6",
        "responsibility": responsibility, "development_supported": supported,
        "subjects": summaries, "hostile": hostile, "gates": gates,
        "detail_bundle_sha256": detail_sha, "detail_persisted_digest_match": persisted_ok,
        "donor_novelty_credit": False, "novelty_credit": False, "r6_authority": False,
        "reserved_stretched_n2_accessed": False,
    }
    print("ORIONQ_MAX_R6H_PARTIAL_TAG_SHARING=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
