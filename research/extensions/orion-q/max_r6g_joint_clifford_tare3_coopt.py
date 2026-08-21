#!/usr/bin/env python3
"""MAX-R6G full single-CNOT / partition / exact-TARE3 co-optimization.

Frozen before R6F/R6G outcomes. Uses only already-open H4/equilibrium-N2
six-term batches and cannot self-authorize R6 or novelty.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6e_deep_p10_exact_frame_saturation as r6e
import max_r6e_deep_p10_exact_frame_saturation_fast as r6e_fast
import max_r6f_donor_clifford_preconditioned_tare3 as r6f
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6_p10_candidate_blind_frame_optimizer as p10

TOL = 1e-12


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _donor_envelope(points: list[dict[str, Any]], lam: float):
    eligible = [row for row in points if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"empty_R6G_donor_envelope": lam})
    best = min(
        eligible,
        key=lambda row: (
            int(row["C_donor"]), float(row["Lambda_batch"]), row["donor_kind"],
            row["transform_id"], row["partition"],
        ),
    )
    return int(best["C_donor"]), best


def _lambda3(coefficients) -> float:
    return float((3.0 * sum(float(x) * float(x) for x in coefficients)) ** 0.5)


def _strict_key(row):
    return (
        -int(row["delta_vs_donor_envelope"]), float(row["Lambda_batch"]),
        row["transform_id"], row["partition"],
    )


def run_subject(name: str, cfg):
    terms, source_indices, champions, max_imag, observed_blob = r6f._frozen_batch(cfg)
    n = int(cfg["n_qubits"])
    if len(source_indices) != 6:
        summary = {
            "subject": name, "source_blob_expected": cfg["blob"],
            "source_blob_observed": observed_blob,
            "source_blob_verified": observed_blob == cfg["blob"], "n_qubits": n,
            "max_imag": float(max_imag), "r6b_window_champions_available": len(champions),
            "frozen_source_indices": list(source_indices), "batch_complete": False,
            "transform_grammar_count": 1 + n * (n - 1), "partition_count": 0,
            "donor_point_count": 0, "candidate_point_count": 0, "strict_count": 0,
            "strict_budget_matched_improvement_exists": False, "best_strict": None,
            "all_lambda_invariant": True, "all_frame_witnesses_valid": True,
            "all_strict_original_witnesses_valid": True,
            "identity_frame_reference_all_pass": True,
        }
        return summary, {"subject": name, "donor_points": [], "candidate_points": [], "strict_points": []}

    partitions = r6f._partitions_for_source(source_indices)
    transforms = r6f.transform_grammar(n)
    if len(partitions) != 10:
        raise AssertionError({"R6G_partition_count": len(partitions)})
    if len(transforms) != 1 + n * (n - 1):
        raise AssertionError({"R6G_transform_count": len(transforms), "n": n})

    donor_points = []
    candidate_raw = []
    lambda_checks = []
    frame_reference_checks = []
    frame_witnesses_valid = True
    transformed_cache = {}
    frame_cache = {}
    sparse_cache = {}

    # D1 first: complete frame-only donor over the full transform/partition grammar.
    for transform in transforms:
        tid = r6f.transform_id(transform)
        wrapper = 0 if transform is None else 2
        for a, b in partitions:
            for triple in (a, b):
                key = (tid, tuple(triple))
                if key not in transformed_cache:
                    targets, signs = r6f._transformed_targets(terms, triple, transform)
                    signed_coeff = tuple(
                        float(terms[i][1]) * int(sign)
                        for i, sign in zip(triple, signs, strict=True)
                    )
                    source_lambda = r6f._lambda_for_indices(terms, triple)
                    transformed_lambda = _lambda3(signed_coeff)
                    invariant = abs(source_lambda - transformed_lambda) <= TOL
                    lambda_checks.append({
                        "transform_id": tid, "term_indices": list(triple),
                        "source_lambda": float(source_lambda),
                        "transformed_lambda": transformed_lambda, "signs": list(signs),
                        "pass": invariant,
                    })
                    if not invariant:
                        raise AssertionError({"R6G_lambda_invariance_failed": lambda_checks[-1]})
                    transformed_cache[key] = (targets, signs, signed_coeff)
                    frame = r6e.frame_only_fast(targets, n)
                    valid_frame = r6f._frame_witness_valid(frame, targets)
                    frame_witnesses_valid = frame_witnesses_valid and valid_frame
                    if not valid_frame:
                        raise AssertionError({"R6G_frame_witness_invalid": [name, tid, triple]})
                    frame_cache[key] = frame
                    if transform is None:
                        original = exact.frame_only_strong(targets, n)
                        passed = int(original["C_joint"]) == int(frame["C_joint"])
                        frame_reference_checks.append({
                            "term_indices": list(triple), "fast": int(frame["C_joint"]),
                            "original": int(original["C_joint"]), "pass": passed,
                        })
                        if not passed:
                            raise AssertionError({"R6G_identity_frame_reference_mismatch": triple})
            lam = float(r6f._lambda_for_indices(terms, a) + r6f._lambda_for_indices(terms, b))
            donor_points.append({
                "donor_kind": "FULL_SINGLE_CNOT_FRAME_ONLY", "transform_id": tid,
                "partition": [list(a), list(b)], "Lambda_batch": lam,
                "C_donor": int(frame_cache[(tid, a)]["C_joint"] + frame_cache[(tid, b)]["C_joint"] + wrapper),
                "wrapper_charge": wrapper,
            })

    # D2: absorbed R6B transformation-reuse donor on every untransformed partition.
    r6d_eval = r6d._evaluate_fixed_batch(terms, source_indices, n)
    if len(r6d_eval.get("all_partitions", [])) != 10 or r6d_eval.get("all_witnesses_valid") is not True:
        raise AssertionError("R6G R6B/R6D donor replay failed")
    for row in r6d_eval.get("eligible_points", []):
        if row.get("C_reuse") is not None:
            donor_points.append({
                "donor_kind": "ABSORBED_R6B_REUSE", "transform_id": "IDENTITY_REUSE",
                "partition": row["partition"], "Lambda_batch": float(row["Lambda_batch"]),
                "C_donor": int(row["C_reuse"]), "wrapper_charge": 0,
            })

    # Candidate: exhaustive exact-joint co-optimization on the same full grammar.
    for transform in transforms:
        tid = r6f.transform_id(transform)
        wrapper = 0 if transform is None else 2
        for a, b in partitions:
            for triple in (a, b):
                key = (tid, tuple(triple))
                if key not in sparse_cache:
                    sparse_cache[key] = int(r6e_fast.exact_joint_cost_sparse(transformed_cache[key][0], n))
            lam = float(r6f._lambda_for_indices(terms, a) + r6f._lambda_for_indices(terms, b))
            block_costs = [int(sparse_cache[(tid, a)]), int(sparse_cache[(tid, b)])]
            candidate_cost = int(sum(block_costs) + wrapper)
            donor_cost, witness = _donor_envelope(donor_points, lam)
            delta = int(donor_cost - candidate_cost)
            candidate_raw.append({
                "transform_id": tid,
                "transform": None if transform is None else list(transform),
                "partition": [list(a), list(b)], "Lambda_batch": lam,
                "C_candidate": candidate_cost, "candidate_block_costs": block_costs,
                "wrapper_charge": wrapper, "C_donor_envelope": donor_cost,
                "delta_vs_donor_envelope": delta,
                "strict_budget_matched_improvement": delta > 0,
                "donor_envelope_witness": {
                    "donor_kind": witness["donor_kind"], "transform_id": witness["transform_id"],
                    "partition": witness["partition"], "Lambda_batch": witness["Lambda_batch"],
                    "C_donor": witness["C_donor"],
                },
            })

    strict = sorted(
        (row for row in candidate_raw if row["strict_budget_matched_improvement"]),
        key=_strict_key,
    )
    strict_original_valid = True
    for row in strict:
        tid = row["transform_id"]
        originals = []
        signed_coefficients = []
        for triple_list, sparse_cost in zip(row["partition"], row["candidate_block_costs"], strict=True):
            triple = tuple(int(x) for x in triple_list)
            targets = transformed_cache[(tid, triple)][0]
            original = exact.exact_joint(targets, n)
            valid = int(original["C_joint"]) == int(sparse_cost) and all(
                value is True for value in original.get("checks", {}).values()
            )
            strict_original_valid = strict_original_valid and valid
            if not valid:
                raise AssertionError({"R6G_strict_original_replay_failed": [name, tid, triple]})
            originals.append(original)
            signed_coefficients.append(list(transformed_cache[(tid, triple)][2]))
        row["original_exact_blocks"] = originals
        row["original_witnesses_valid"] = True
        row["signed_transformed_coefficients"] = signed_coefficients

    summary = {
        "subject": name, "source_blob_expected": cfg["blob"],
        "source_blob_observed": observed_blob, "source_blob_verified": observed_blob == cfg["blob"],
        "n_qubits": n, "max_imag": float(max_imag),
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": list(source_indices), "batch_complete": True,
        "transform_grammar_count": len(transforms), "partition_count": len(partitions),
        "donor_point_count": len(donor_points), "candidate_point_count": len(candidate_raw),
        "strict_count": len(strict), "strict_budget_matched_improvement_exists": bool(strict),
        "best_strict": None if not strict else strict[0],
        "all_lambda_invariant": all(row["pass"] for row in lambda_checks),
        "all_frame_witnesses_valid": frame_witnesses_valid,
        "all_strict_original_witnesses_valid": strict_original_valid,
        "identity_frame_reference_count": len(frame_reference_checks),
        "identity_frame_reference_all_pass": bool(frame_reference_checks) and all(
            row["pass"] for row in frame_reference_checks
        ),
    }
    detail = {
        "subject": name, "donor_points": donor_points,
        "candidate_points": candidate_raw, "strict_points": strict,
        "lambda_invariance_checks": lambda_checks,
        "identity_frame_reference_checks": frame_reference_checks,
    }
    return summary, detail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--detail-json", type=Path, default=None)
    args = parser.parse_args()

    cnot_hostile = r6f.hostile_cnot()
    sparse_hostile = r6e_fast.sparse_hostile_equivalence()
    original_hostile = exact.hostile_exactness()
    summaries, details = {}, {}
    for name, cfg in p10.base.SUBJECTS.items():
        summaries[name], details[name] = run_subject(name, cfg)

    h4 = summaries["H4"]["strict_budget_matched_improvement_exists"]
    n2 = summaries["N2"]["strict_budget_matched_improvement_exists"]
    if h4 and n2:
        authority = "MAX_R6G_JOINT_CLIFFORD_TARE3_COOPT_SUPPORTED__NOT_R6"
        responsibility = "RESP:CIRCUIT_RESOURCE_INSTANTIATION_AND_NOVELTY_SUBTRACTION"
        supported = True
    elif h4 or n2:
        authority = "MAX_R6G_PARTIAL_JOINT_CLIFFORD_REOPEN__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_METHOD_SPLIT"
        supported = False
    else:
        authority = "MAX_R6G_JOINT_CLIFFORD_TARE3_COOPT_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_BEYOND_SINGLE_CNOT_TARE3"
        supported = False

    gates = {
        "signed_cnot_table_complete": cnot_hostile["local_pauli_rows"] == 16,
        "signed_cnot_involution_exact": cnot_hostile["involution_all_pass"],
        "signed_cnot_symplectic_exact": cnot_hostile["symplectic_all_pass"],
        "sparse_exact_matches_original_and_brute_hostile": sparse_hostile["all_pass"],
        "original_exact_hostile_pass": original_hostile["all_exact"],
        "source_blobs_observed_match": all(row["source_blob_verified"] for row in summaries.values()),
        "frozen_sixterm_batches_complete": all(row["batch_complete"] for row in summaries.values()),
        "transform_grammar_complete": all(
            row["transform_grammar_count"] == 1 + row["n_qubits"] * (row["n_qubits"] - 1)
            for row in summaries.values()
        ),
        "exactly_ten_partitions": all(row["partition_count"] == 10 for row in summaries.values()),
        "coefficient_lambda_invariance": all(row["all_lambda_invariant"] for row in summaries.values()),
        "frame_witnesses_valid": all(row["all_frame_witnesses_valid"] for row in summaries.values()),
        "frame_fast_original_reference_agreement": all(
            row["identity_frame_reference_all_pass"] for row in summaries.values()
        ),
        "strict_original_witnesses_valid": all(
            row["all_strict_original_witnesses_valid"] for row in summaries.values()
        ),
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"R6G_integrity_gate_failure": gates})

    detail_bundle = {"schema": "ORIONQ.MAXR6G.JointCliffordTARE3CooptDetail.v1", "subjects": details}
    detail_sha = digest(detail_bundle)
    persisted_ok = True
    if args.detail_json is not None:
        args.detail_json.write_text(canonical_json(detail_bundle) + "\n")
        persisted_ok = digest(json.loads(args.detail_json.read_text())) == detail_sha
        if not persisted_ok:
            raise AssertionError("R6G persisted detail digest mismatch")

    result = {
        "schema": "ORIONQ.MAXR6G.JointCliffordTARE3Coopt.v1", "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_SIXTERM_FULL_SINGLE_CNOT_GRAMMAR__NOT_R6",
        "responsibility": responsibility, "development_supported": supported,
        "subjects": summaries,
        "hostile": {"cnot": cnot_hostile, "sparse_exact": sparse_hostile, "original_exact": original_hostile},
        "gates": gates, "detail_bundle_sha256": detail_sha,
        "detail_persisted_digest_match": persisted_ok,
        "donor_novelty_credit": False, "novelty_credit": False,
        "r6_authority": False, "reserved_stretched_n2_accessed": False,
    }
    print("ORIONQ_MAX_R6G_JOINT_CLIFFORD_TARE3=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
