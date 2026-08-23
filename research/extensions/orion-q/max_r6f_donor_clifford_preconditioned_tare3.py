#!/usr/bin/env python3
"""MAX-R6F donor-Clifford-preconditioned exact TARE-3 development.

Frozen by MAX_R6F_DONOR_CLIFFORD_PRECONDITIONED_TARE3_PROTOCOL.md.
Uses only already-open H4/equilibrium-N2 evidence. The full identity/single-CNOT
frame-only donor envelope is computed before the exact-joint candidate is run.
No positive result from this file is R6 or novelty authority.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6b_tare_transformation_reuse_donor as r6b
import max_r6d_sixterm_partition_representation_coopt as r6d
import max_r6e_deep_p10_exact_frame_saturation as r6e

TOL = 1e-12
SHORTLIST_NONIDENTITY = 7


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _load_terms_verified(cfg) -> tuple[list[Any], float, str]:
    p10.base.configure_subject(cfg)
    text = p10.h.fetch_source()
    raw = text.encode()
    observed_blob = git_blob_sha(raw)
    if observed_blob != cfg["blob"]:
        raise AssertionError(
            {
                "observed_source_blob_mismatch": observed_blob,
                "expected": cfg["blob"],
                "path": cfg["path"],
            }
        )
    one, two = p10.h.parse_ducc(text)
    paulis, max_imag = p10.h.jordan_wigner_paulis(one, two)
    paulis.pop((0, 0), None)
    terms = sorted(paulis.items(), key=lambda kv: (-abs(kv[1]), kv[0][0], kv[0][1]))
    return terms, float(max_imag), observed_blob


def _frozen_batch(cfg) -> tuple[list[Any], tuple[int, ...], list[dict[str, Any]], float, str]:
    verified_terms, verified_max_imag, observed_blob = _load_terms_verified(cfg)
    replay_terms, champions, replay_max_imag = r6b.window_champions(cfg)
    if len(replay_terms) != len(verified_terms):
        raise AssertionError("R6B replay term count disagrees with independently verified source")
    for idx, (left, right) in enumerate(zip(verified_terms, replay_terms, strict=True)):
        if left[0] != right[0] or abs(complex(left[1]) - complex(right[1])) > TOL:
            raise AssertionError({"R6B_replay_term_mismatch": idx, "left": left, "right": right})
    if abs(verified_max_imag - float(replay_max_imag)) > TOL:
        raise AssertionError("R6B replay max-imag disagrees with independently verified source")
    if len(champions) < 2:
        return verified_terms, tuple(), champions, verified_max_imag, observed_blob
    chosen = champions[:2]
    source_indices = tuple(sorted(int(i) for row in chosen for i in row["term_indices"]))
    if len(source_indices) != 6 or len(set(source_indices)) != 6:
        raise AssertionError({"frozen_R6B_batch_not_six_unique": source_indices})
    if chosen[0]["window_start"] == chosen[1]["window_start"]:
        raise AssertionError("R6B frozen champions unexpectedly share a window")
    return verified_terms, source_indices, chosen, verified_max_imag, observed_blob


# ---- Exact CNOT Pauli conjugation including Hermitian sign -----------------

_I = np.array([[1, 0], [0, 1]], dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_MATRIX_BY_BITS = {(0, 0): _I, (1, 0): _X, (1, 1): _Y, (0, 1): _Z}
_CNOT = np.array(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
    dtype=complex,
)


def _cnot_local_table():
    table = {}
    for c_bits, c_mat in _MATRIX_BY_BITS.items():
        for t_bits, t_mat in _MATRIX_BY_BITS.items():
            transformed = _CNOT @ np.kron(c_mat, t_mat) @ _CNOT.conj().T
            matches = []
            for oc_bits, oc_mat in _MATRIX_BY_BITS.items():
                for ot_bits, ot_mat in _MATRIX_BY_BITS.items():
                    candidate = np.kron(oc_mat, ot_mat)
                    if np.allclose(transformed, candidate, atol=1e-12):
                        matches.append((1, oc_bits, ot_bits))
                    if np.allclose(transformed, -candidate, atol=1e-12):
                        matches.append((-1, oc_bits, ot_bits))
            if len(matches) != 1:
                raise AssertionError({"CNOT_local_table_nonunique": [c_bits, t_bits, matches]})
            table[(c_bits, t_bits)] = matches[0]
    if len(table) != 16:
        raise AssertionError("CNOT local Pauli table incomplete")
    return table


_CNOT_LOCAL = _cnot_local_table()


def _bit_pair(key: tuple[int, int], q: int) -> tuple[int, int]:
    return ((key[0] >> q) & 1, (key[1] >> q) & 1)


def cnot_conjugate(
    key: tuple[int, int], control: int, target: int
) -> tuple[tuple[int, int], int]:
    if control == target:
        raise ValueError("CNOT control and target must differ")
    c_bits = _bit_pair(key, control)
    t_bits = _bit_pair(key, target)
    sign, out_c, out_t = _CNOT_LOCAL[(c_bits, t_bits)]
    x, z = key
    for q, bits in ((control, out_c), (target, out_t)):
        x &= ~(1 << q)
        z &= ~(1 << q)
        x |= int(bits[0]) << q
        z |= int(bits[1]) << q
    return (int(x), int(z)), int(sign)


def transform_key(key: tuple[int, int], transform: tuple[int, int] | None):
    if transform is None:
        return key, 1
    return cnot_conjugate(key, transform[0], transform[1])


def transform_id(transform: tuple[int, int] | None) -> str:
    return "IDENTITY" if transform is None else f"CNOT:{transform[0]}->{transform[1]}"


def transform_grammar(n: int) -> tuple[tuple[int, int] | None, ...]:
    return (None,) + tuple((c, t) for c in range(n) for t in range(n) if c != t)


def hostile_cnot() -> dict[str, Any]:
    keys = [(x, z) for x in range(4) for z in range(4)]
    involution_rows = []
    for key in keys:
        first, s1 = cnot_conjugate(key, 0, 1)
        second, s2 = cnot_conjugate(first, 0, 1)
        passed = second == key and s1 * s2 == 1
        involution_rows.append({"key": list(key), "pass": passed})
        if not passed:
            raise AssertionError({"CNOT_involution_failed": key, "first": first, "second": second, "sign": s1 * s2})
    symplectic_pass = True
    for a in keys:
        ta, _ = cnot_conjugate(a, 0, 1)
        for b in keys:
            tb, _ = cnot_conjugate(b, 0, 1)
            if p10.symp(a, b) != p10.symp(ta, tb):
                symplectic_pass = False
                raise AssertionError({"CNOT_symplectic_failed": [a, b, ta, tb]})
    return {
        "local_pauli_rows": len(_CNOT_LOCAL),
        "involution_rows": len(involution_rows),
        "involution_all_pass": all(row["pass"] for row in involution_rows),
        "symplectic_pair_rows": len(keys) * len(keys),
        "symplectic_all_pass": symplectic_pass,
    }


def _frame_witness_valid(witness: dict[str, Any], targets) -> bool:
    rs = tuple(tuple(x) for x in witness["R"])
    ss = tuple(tuple(x) for x in witness["S"])
    ts = tuple(tuple(x) for x in witness["T"])
    perm = tuple(int(x) for x in witness["target_permutation"])
    labels = tuple(int(x) for x in witness["labels"])
    if len(rs) != 3 or len(ss) != 2 or len(ts) != 3 or sorted(perm) != [0, 1, 2]:
        return False
    if not p10.is_pairwise_anti(rs) or int(witness["uanti_support"]) != 0:
        return False
    got_labels = tuple(2 * p10.symp(ss[0], r) + p10.symp(ss[1], r) for r in rs)
    if got_labels != labels or len(set(labels)) != 3 or labels[0] ^ labels[1] ^ labels[2] != 0:
        return False
    permuted = tuple(targets[perm[k]] for k in range(3))
    if not all(p10.mul(ts[k], rs[k]) == permuted[k] for k in range(3)):
        return False
    recomputed = 2 * (p10.wt(ss[0]) + p10.wt(ss[1])) + sum(p10.wt(t) for t in ts)
    return recomputed == int(witness["C_joint"])


def _lambda_for_indices(terms, indices: tuple[int, int, int]) -> float:
    coeffs = [float(terms[i][1]) for i in indices]
    return float(math.sqrt(3.0) * math.sqrt(sum(value * value for value in coeffs)))


def _partitions_for_source(source_indices: tuple[int, ...]):
    rows = []
    for positions_a, positions_b in r6d.partitions_3plus3():
        a = tuple(sorted(source_indices[pos] for pos in positions_a))
        b = tuple(sorted(source_indices[pos] for pos in positions_b))
        rows.append((a, b))
    if len(rows) != 10 or len(set(rows)) != 10:
        raise AssertionError({"source_partition_count_not_10": rows})
    return tuple(rows)


def _transformed_targets(terms, indices, transform):
    targets = []
    signs = []
    for index in indices:
        key, sign = transform_key(terms[index][0], transform)
        if transform is not None:
            back, sign2 = transform_key(key, transform)
            if back != terms[index][0] or sign * sign2 != 1:
                raise AssertionError({"chemistry_CNOT_roundtrip_failed": [index, transform_id(transform)]})
        targets.append(key)
        signs.append(sign)
    return tuple(targets), tuple(signs)


def _donor_stage(terms, source_indices: tuple[int, ...], n: int) -> dict[str, Any]:
    if len(source_indices) != 6:
        return {
            "transforms": [],
            "all_points": [],
            "shortlist": [],
            "shortlist_hash": sha256([]),
            "frame_reference_checks": [],
        }
    partitions = _partitions_for_source(source_indices)
    transforms = transform_grammar(n)
    if len(transforms) != 1 + n * (n - 1):
        raise AssertionError("single-CNOT transform grammar cardinality drift")

    all_points = []
    transform_summaries = []
    frame_reference_checks = []
    for transform in transforms:
        tid = transform_id(transform)
        wrapper = 0 if transform is None else 2
        cache: dict[tuple[int, int, int], dict[str, Any]] = {}
        signs_cache: dict[tuple[int, int, int], tuple[int, ...]] = {}
        costs = []
        for a, b in partitions:
            for triple in (a, b):
                if triple not in cache:
                    targets, signs = _transformed_targets(terms, triple, transform)
                    frame = r6e.frame_only_fast(targets, n)
                    if not _frame_witness_valid(frame, targets):
                        raise AssertionError({"R6F_frame_witness_invalid": [tid, triple]})
                    cache[triple] = frame
                    signs_cache[triple] = signs
                    # On the identity transform, independently bind the fast comparator
                    # to the original exact Erratum-3 implementation for every triple.
                    if transform is None:
                        reference = exact.frame_only_strong(targets, n)
                        passed = int(reference["C_joint"]) == int(frame["C_joint"])
                        frame_reference_checks.append(
                            {
                                "term_indices": list(triple),
                                "fast": int(frame["C_joint"]),
                                "reference": int(reference["C_joint"]),
                                "pass": passed,
                            }
                        )
                        if not passed:
                            raise AssertionError({"frame_fast_reference_mismatch": triple})
            lam = _lambda_for_indices(terms, a) + _lambda_for_indices(terms, b)
            cost = int(cache[a]["C_joint"] + cache[b]["C_joint"] + wrapper)
            costs.append(cost)
            all_points.append(
                {
                    "transform_id": tid,
                    "partition": [list(a), list(b)],
                    "Lambda_batch": float(lam),
                    "C_donor": cost,
                    "wrapper_charge": wrapper,
                    "block_costs": [int(cache[a]["C_joint"]), int(cache[b]["C_joint"])],
                    "phase_signs": [list(signs_cache[a]), list(signs_cache[b])],
                }
            )
        transform_summaries.append(
            {
                "transform_id": tid,
                "transform": None if transform is None else list(transform),
                "min_partition_C_donor": min(costs),
                "sum_partition_C_donor": sum(costs),
            }
        )

    identity = next(row for row in transform_summaries if row["transform_id"] == "IDENTITY")
    nonidentity = sorted(
        (row for row in transform_summaries if row["transform_id"] != "IDENTITY"),
        key=lambda row: (
            int(row["min_partition_C_donor"]),
            int(row["sum_partition_C_donor"]),
            row["transform_id"],
        ),
    )
    if len(nonidentity) < SHORTLIST_NONIDENTITY:
        raise AssertionError("not enough non-identity CNOT transforms for frozen shortlist")
    shortlist = [identity, *nonidentity[:SHORTLIST_NONIDENTITY]]
    shortlist_receipt = [
        {
            "transform_id": row["transform_id"],
            "transform": row["transform"],
            "min_partition_C_donor": row["min_partition_C_donor"],
            "sum_partition_C_donor": row["sum_partition_C_donor"],
        }
        for row in shortlist
    ]
    return {
        "transforms": transform_summaries,
        "all_points": all_points,
        "shortlist": shortlist_receipt,
        "shortlist_hash": sha256(shortlist_receipt),
        "frame_reference_checks": frame_reference_checks,
    }


def _donor_envelope(points: list[dict[str, Any]], lam: float) -> tuple[int, dict[str, Any]]:
    eligible = [row for row in points if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"empty_R6F_donor_envelope": lam})
    best = min(
        eligible,
        key=lambda row: (
            int(row["C_donor"]),
            float(row["Lambda_batch"]),
            row["transform_id"],
            row["partition"],
        ),
    )
    return int(best["C_donor"]), best


def _candidate_stage(terms, source_indices, n: int, donor_stage: dict[str, Any]) -> dict[str, Any]:
    if len(source_indices) != 6:
        return {"points": [], "strict_points": [], "all_witnesses_valid": False}
    shortlist_hash_before = donor_stage["shortlist_hash"]
    shortlist = donor_stage["shortlist"]
    if len(shortlist) != 1 + SHORTLIST_NONIDENTITY:
        raise AssertionError({"R6F_shortlist_length": len(shortlist)})
    partitions = _partitions_for_source(source_indices)
    candidate_points = []
    all_valid = True
    for entry in shortlist:
        transform = None if entry["transform"] is None else tuple(int(x) for x in entry["transform"])
        tid = entry["transform_id"]
        wrapper = 0 if transform is None else 2
        cache: dict[tuple[int, int, int], dict[str, Any]] = {}
        signs_cache: dict[tuple[int, int, int], tuple[int, ...]] = {}
        for a, b in partitions:
            for triple in (a, b):
                if triple not in cache:
                    targets, signs = _transformed_targets(terms, triple, transform)
                    joint = exact.exact_joint(targets, n)
                    valid = all(value is True for value in joint.get("checks", {}).values())
                    if not valid:
                        all_valid = False
                        raise AssertionError({"R6F_exact_joint_witness_invalid": [tid, triple, joint.get("checks")]})
                    cache[triple] = joint
                    signs_cache[triple] = signs
            lam = _lambda_for_indices(terms, a) + _lambda_for_indices(terms, b)
            candidate_cost = int(cache[a]["C_joint"] + cache[b]["C_joint"] + wrapper)
            donor_cost, donor_best = _donor_envelope(donor_stage["all_points"], lam)
            delta = int(donor_cost - candidate_cost)
            candidate_points.append(
                {
                    "transform_id": tid,
                    "partition": [list(a), list(b)],
                    "Lambda_batch": float(lam),
                    "C_candidate": candidate_cost,
                    "candidate_block_costs": [int(cache[a]["C_joint"]), int(cache[b]["C_joint"])],
                    "wrapper_charge": wrapper,
                    "phase_signs": [list(signs_cache[a]), list(signs_cache[b])],
                    "C_donor_envelope": donor_cost,
                    "delta_vs_donor_envelope": delta,
                    "strict_budget_matched_improvement": delta > 0,
                    "donor_envelope_witness": {
                        "transform_id": donor_best["transform_id"],
                        "partition": donor_best["partition"],
                        "Lambda_batch": donor_best["Lambda_batch"],
                        "C_donor": donor_best["C_donor"],
                    },
                }
            )
    # Detect any accidental mutation/recomputation of the frozen donor-only shortlist.
    if sha256(shortlist) != shortlist_hash_before:
        raise AssertionError("R6F donor shortlist mutated after candidate evaluation")
    strict = [row for row in candidate_points if row["strict_budget_matched_improvement"]]
    strict.sort(
        key=lambda row: (
            -int(row["delta_vs_donor_envelope"]),
            float(row["Lambda_batch"]),
            row["transform_id"],
            row["partition"],
        )
    )
    return {
        "points": candidate_points,
        "strict_points": strict,
        "strict_count": len(strict),
        "best_strict": None if not strict else strict[0],
        "all_witnesses_valid": all_valid and bool(candidate_points),
    }


def _pareto_donor(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        points,
        key=lambda row: (
            float(row["Lambda_batch"]),
            int(row["C_donor"]),
            row["transform_id"],
            row["partition"],
        ),
    )
    front = []
    best_cost = None
    for row in ordered:
        cost = int(row["C_donor"])
        if best_cost is None or cost < best_cost:
            front.append(
                {
                    "Lambda_batch": float(row["Lambda_batch"]),
                    "C_donor": cost,
                    "transform_id": row["transform_id"],
                    "partition": row["partition"],
                }
            )
            best_cost = cost
    return front


def run_subject(name: str, cfg) -> tuple[dict[str, Any], dict[str, Any]]:
    terms, source_indices, champions, max_imag, observed_blob = _frozen_batch(cfg)
    donor = _donor_stage(terms, source_indices, int(cfg["n_qubits"]))
    # Candidate begins only after the donor-only shortlist exists and has a digest.
    candidate = _candidate_stage(terms, source_indices, int(cfg["n_qubits"]), donor)
    summary = {
        "subject": name,
        "source_blob_expected": cfg["blob"],
        "source_blob_observed": observed_blob,
        "source_blob_verified": observed_blob == cfg["blob"],
        "n_qubits": int(cfg["n_qubits"]),
        "max_imag": max_imag,
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": list(source_indices),
        "transform_grammar_count": len(donor["transforms"]),
        "donor_shortlist": donor["shortlist"],
        "donor_shortlist_sha256": donor["shortlist_hash"],
        "donor_frame_reference_checks": len(donor["frame_reference_checks"]),
        "donor_frame_reference_all_pass": bool(donor["frame_reference_checks"]) and all(
            row["pass"] for row in donor["frame_reference_checks"]
        ),
        "donor_pareto": _pareto_donor(donor["all_points"]) if donor["all_points"] else [],
        "donor_point_count": len(donor["all_points"]),
        "candidate_point_count": len(candidate["points"]),
        "strict_budget_matched_improvement_exists": bool(candidate["strict_points"]),
        "strict_count": candidate.get("strict_count", 0),
        "best_strict": candidate.get("best_strict"),
        "all_candidate_witnesses_valid": candidate["all_witnesses_valid"],
    }
    detail = {
        "subject": name,
        "source_indices": list(source_indices),
        "donor_transforms": donor["transforms"],
        "donor_points": donor["all_points"],
        "donor_shortlist": donor["shortlist"],
        "donor_shortlist_sha256": donor["shortlist_hash"],
        "candidate_points": candidate["points"],
        "strict_points": candidate["strict_points"],
    }
    return summary, detail


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--detail-json", type=Path, default=None)
    args = parser.parse_args()

    hostile = hostile_cnot()
    summaries = {}
    details = {}
    for name, cfg in p10.base.SUBJECTS.items():
        summaries[name], details[name] = run_subject(name, cfg)

    strict_h4 = summaries["H4"]["strict_budget_matched_improvement_exists"]
    strict_n2 = summaries["N2"]["strict_budget_matched_improvement_exists"]
    if strict_h4 and strict_n2:
        authority = "MAX_R6F_CLIFFORD_PRECONDITIONED_TARE3_SUPPORTED__NOT_R6"
        responsibility = "RESP:CIRCUIT_LEVEL_INSTANTIATION_AND_DONOR_REPLAY"
        development_supported = True
    elif strict_h4 or strict_n2:
        authority = "MAX_R6F_PARTIAL_CLIFFORD_REOPEN__NOT_R6"
        responsibility = "RESP:MATCHED_COUNTERFACTUAL_CLIFFORD_METHOD_SPLIT"
        development_supported = False
    else:
        authority = "MAX_R6F_CLIFFORD_PRECONDITIONING_NEGATIVE__NOT_R6"
        responsibility = "RESP:METHOD_LANGUAGE_INADEQUATE_BEYOND_SINGLE_CNOT_PRECONDITIONING"
        development_supported = False

    gates = {
        "cnot_local_table_complete": hostile["local_pauli_rows"] == 16,
        "cnot_involution_phase_exact": hostile["involution_all_pass"],
        "cnot_symplectic_exact": hostile["symplectic_all_pass"],
        "source_blobs_observed_match": all(row["source_blob_verified"] for row in summaries.values()),
        "frozen_sixterm_batches_complete": all(len(row["frozen_source_indices"]) == 6 for row in summaries.values()),
        "transform_grammar_complete": all(
            row["transform_grammar_count"] == 1 + row["n_qubits"] * (row["n_qubits"] - 1)
            for row in summaries.values()
        ),
        "donor_shortlists_exactly_eight": all(len(row["donor_shortlist"]) == 8 for row in summaries.values()),
        "frame_only_independent_reference_agreement": all(
            row["donor_frame_reference_all_pass"] for row in summaries.values()
        ),
        "candidate_witnesses_valid": all(row["all_candidate_witnesses_valid"] for row in summaries.values()),
        "fresh_stretched_n2_unread": True,
    }
    if not all(gates.values()):
        raise AssertionError({"R6F_integrity_gate_failure": gates})

    detail_bundle = {
        "schema": "ORIONQ.MAXR6F.CliffordPreconditionedTARE3Detail.v1",
        "subjects": details,
    }
    detail_sha = sha256(detail_bundle)
    persisted_ok = True
    if args.detail_json is not None:
        args.detail_json.write_text(canonical_json(detail_bundle) + "\n")
        persisted = json.loads(args.detail_json.read_text())
        persisted_ok = sha256(persisted) == detail_sha
        if not persisted_ok:
            raise AssertionError("R6F persisted detail digest mismatch")

    result = {
        "schema": "ORIONQ.MAXR6F.DonorCliffordPreconditionedTARE3.v1",
        "authority": authority,
        "scope": "OPEN_H4_EQ_N2_R6B_FROZEN_SIXTERM_BATCHES__NOT_R6",
        "responsibility": responsibility,
        "donor_novelty_credit": False,
        "novelty_credit": False,
        "r6_authority": False,
        "development_supported": development_supported,
        "hostile": hostile,
        "subjects": summaries,
        "detail_bundle_sha256": detail_sha,
        "detail_persisted_digest_match": persisted_ok,
        "gates": gates,
        "reserved_stretched_n2_accessed": False,
    }
    print("ORIONQ_MAX_R6F_CLIFFORD_TARE3=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
