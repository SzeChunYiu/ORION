#!/usr/bin/env python3
"""MAX-R6D exact six-term TARE partition / representation co-optimization.

Frozen by MAX_R6D_SIXTERM_PARTITION_REPRESENTATION_COOPT_PROTOCOL.md.
Uses only already-open H4 and equilibrium-N2 evidence. A positive is open-subject
method development only and cannot self-authorize R6 or novelty.
"""
from __future__ import annotations

import itertools
import json
import math
from typing import Any

import max_r6_exact_tare3_joint_frame_dp as exact
import max_r6_p10_candidate_blind_frame_optimizer as p10
import max_r6b_tare_transformation_reuse_donor as reuse

TOL = 1e-12


def partitions_3plus3() -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    rows = []
    universe = set(range(6))
    for pair in itertools.combinations(range(1, 6), 2):
        a = tuple(sorted((0, *pair)))
        b = tuple(sorted(universe - set(a)))
        rows.append((a, b))
    result = tuple(rows)
    if len(result) != 10 or len(set(result)) != 10:
        raise AssertionError({"partition_enumerator_not_10_unique": result})
    return result


def _frame_witness_valid(witness: dict[str, Any], targets: tuple[tuple[int, int], ...]) -> bool:
    rs = tuple(tuple(x) for x in witness["R"])
    ss = tuple(tuple(x) for x in witness["S"])
    ts = tuple(tuple(x) for x in witness["T"])
    permutation = tuple(int(x) for x in witness["target_permutation"])
    labels = tuple(int(x) for x in witness["labels"])
    if len(rs) != 3 or len(ss) != 2 or len(ts) != 3 or sorted(permutation) != [0, 1, 2]:
        return False
    if not p10.is_pairwise_anti(rs):
        return False
    got_labels = tuple(2 * p10.symp(ss[0], r) + p10.symp(ss[1], r) for r in rs)
    if got_labels != labels or len(set(labels)) != 3:
        return False
    permuted = tuple(targets[permutation[k]] for k in range(3))
    if not all(p10.mul(ts[k], rs[k]) == permuted[k] for k in range(3)):
        return False
    recomputed = 2 * (p10.wt(ss[0]) + p10.wt(ss[1])) + sum(p10.wt(t) for t in ts)
    return witness.get("uanti_support") == 0 and recomputed == int(witness["C_joint"])


def _triple_payload(terms, source_indices: tuple[int, int, int], n: int) -> dict[str, Any]:
    targets = tuple(terms[i][0] for i in source_indices)
    coefficients = tuple(float(terms[i][1]) for i in source_indices)
    lam = math.sqrt(3.0) * math.sqrt(sum(value * value for value in coefficients))
    candidate = exact.exact_joint(targets, n)
    frame = exact.frame_only_strong(targets, n)
    candidate_valid = all(candidate["checks"].values())
    frame_valid = _frame_witness_valid(frame, targets)
    if not candidate_valid or not frame_valid:
        raise AssertionError(
            {
                "triple_witness_invalid": list(source_indices),
                "candidate_valid": candidate_valid,
                "frame_valid": frame_valid,
            }
        )
    return {
        "source_indices": list(source_indices),
        "targets": [list(x) for x in targets],
        "coefficients": list(coefficients),
        "Lambda_TARE3": float(lam),
        "candidate_exact_joint": candidate,
        "frame_only": frame,
        "candidate_witness_valid": True,
        "frame_witness_valid": True,
    }


def _reuse_block(triple: dict[str, Any]) -> dict[str, Any]:
    return {
        "targets": triple["targets"],
        "term_indices": triple["source_indices"],
        "frame_only": triple["frame_only"],
    }


def _reuse_valid(row: dict[str, Any] | None) -> bool:
    if row is None:
        return True
    best = row.get("best")
    if best is None:
        return True
    checks = best.get("checks")
    return isinstance(checks, dict) and bool(checks) and all(value is True for value in checks.values())


def _frozen_six_batch(cfg) -> tuple[list[Any], tuple[int, ...], list[dict[str, Any]], float]:
    terms, champions, max_imag = reuse.window_champions(cfg)
    if len(champions) < 2:
        return terms, tuple(), champions, max_imag
    chosen = champions[:2]
    source_indices = tuple(sorted(int(i) for row in chosen for i in row["term_indices"]))
    if len(source_indices) != 6 or len(set(source_indices)) != 6:
        raise AssertionError({"r6b_frozen_batch_not_six_unique": source_indices})
    if chosen[0]["window_start"] == chosen[1]["window_start"]:
        raise AssertionError("R6B window champions unexpectedly share a window")
    return terms, source_indices, chosen, max_imag


def _envelope_direct(rows: list[dict[str, Any]], lam: float) -> int:
    eligible = [int(row["C_incumbent"]) for row in rows if float(row["Lambda_batch"]) <= lam + TOL]
    if not eligible:
        raise AssertionError({"empty_incumbent_envelope": lam})
    return min(eligible)


def _envelope_sorted(rows: list[dict[str, Any]], lam: float) -> int:
    ordered = sorted((float(row["Lambda_batch"]), int(row["C_incumbent"])) for row in rows)
    best = None
    for row_lam, cost in ordered:
        if row_lam > lam + TOL:
            break
        best = cost if best is None else min(best, cost)
    if best is None:
        raise AssertionError({"empty_sorted_incumbent_envelope": lam})
    return int(best)


def _pareto(rows: list[dict[str, Any]], cost_key: str) -> list[dict[str, Any]]:
    keep = []
    for row in rows:
        lam = float(row["Lambda_batch"])
        cost = int(row[cost_key])
        dominated = False
        for other in rows:
            if other is row:
                continue
            olam = float(other["Lambda_batch"])
            ocost = int(other[cost_key])
            if olam <= lam + TOL and ocost <= cost and (olam < lam - TOL or ocost < cost):
                dominated = True
                break
        if not dominated:
            keep.append(
                {
                    "partition": row["partition"],
                    "Lambda_batch": lam,
                    cost_key: cost,
                }
            )
    return sorted(keep, key=lambda item: (item["Lambda_batch"], item[cost_key], item["partition"]))


def _evaluate_fixed_batch(terms, source_indices: tuple[int, ...], n: int) -> dict[str, Any]:
    if len(source_indices) != 6:
        # Fail closed with the same complete shape returned by the normal path.
        # A short frozen batch is a scientific negative, not an implementation crash.
        return {
            "all_partitions": [],
            "eligible_partition_count": 0,
            "eligible_points": [],
            "candidate_pareto": [],
            "incumbent_pareto": [],
            "strict_points": [],
            "best_strict_improvement": None,
            "all_witnesses_valid": False,
        }

    triple_cache: dict[tuple[int, int, int], dict[str, Any]] = {}
    signature_cache: dict[tuple[int, int, int], dict[Any, Any]] = {}

    def triple(position_tuple: tuple[int, int, int]):
        source = tuple(sorted(source_indices[pos] for pos in position_tuple))
        if source not in triple_cache:
            triple_cache[source] = _triple_payload(terms, source, n)
        return triple_cache[source]

    def signatures(payload: dict[str, Any]):
        key = tuple(payload["source_indices"])
        if key not in signature_cache:
            signature_cache[key] = reuse.complete_source_signatures(_reuse_block(payload), n)
        return signature_cache[key]

    rows: list[dict[str, Any]] = []
    all_partitions = []
    for positions_a, positions_b in partitions_3plus3():
        source_a = tuple(sorted(source_indices[pos] for pos in positions_a))
        source_b = tuple(sorted(source_indices[pos] for pos in positions_b))
        targets_a = tuple(terms[i][0] for i in source_a)
        targets_b = tuple(terms[i][0] for i in source_b)
        eligible = not p10.is_direct_triple(targets_a) and not p10.is_direct_triple(targets_b)
        partition_id = [list(source_a), list(source_b)]
        partition_record = {
            "position_partition": [list(positions_a), list(positions_b)],
            "partition": partition_id,
            "eligible": eligible,
            "ineligibility_reason": None if eligible else "DIRECT_ANTICOMMUTING_TRIPLE_PRESENT",
        }
        all_partitions.append(partition_record)
        if not eligible:
            continue

        a = triple(positions_a)
        b = triple(positions_b)
        six = sorted(a["source_indices"] + b["source_indices"])
        if six != sorted(source_indices):
            raise AssertionError({"partition_term_conservation_failed": partition_id})
        coeff_count = len(a["coefficients"]) + len(b["coefficients"])
        if coeff_count != 6:
            raise AssertionError({"partition_coefficient_conservation_failed": partition_id})

        candidate_cost = int(a["candidate_exact_joint"]["C_joint"] + b["candidate_exact_joint"]["C_joint"])
        frame_cost = int(a["frame_only"]["C_joint"] + b["frame_only"]["C_joint"])

        # R6B donor comparator with signature generation cached per triple.
        combined_signatures = dict(signatures(a))
        for key, value in signatures(b).items():
            combined_signatures.setdefault(key, value)
        reuse_best = None
        valid_reuse = 0
        for key in sorted(combined_signatures):
            rec = reuse.signature_shared_cost(combined_signatures[key], _reuse_block(a), _reuse_block(b), n)
            if rec is None:
                continue
            valid_reuse += 1
            rkey = (int(rec["C_reuse"]), tuple(rec["source_signature_provenance"]), tuple(key))
            if reuse_best is None or rkey < reuse_best[0]:
                reuse_best = (rkey, rec)
        reuse_payload = {
            "valid_reuse_signature_count": valid_reuse,
            "best": None if reuse_best is None else reuse_best[1],
        }
        if not _reuse_valid(reuse_payload):
            raise AssertionError({"reuse_witness_invalid": partition_id})
        reuse_cost = None if reuse_payload["best"] is None else int(reuse_payload["best"]["C_reuse"])
        incumbent_cost = min(frame_cost, reuse_cost) if reuse_cost is not None else frame_cost
        incumbent_source = "R6B_REUSE" if reuse_cost is not None and reuse_cost < frame_cost else "FRAME_ONLY"
        lam = float(a["Lambda_TARE3"] + b["Lambda_TARE3"])
        rows.append(
            {
                "partition": partition_id,
                "Lambda_batch": lam,
                "block_A": a,
                "block_B": b,
                "C_candidate": candidate_cost,
                "C_frame_only": frame_cost,
                "reuse": reuse_payload,
                "C_reuse": reuse_cost,
                "C_incumbent": int(incumbent_cost),
                "incumbent_source": incumbent_source,
                "all_witnesses_valid": (
                    a["candidate_witness_valid"]
                    and b["candidate_witness_valid"]
                    and a["frame_witness_valid"]
                    and b["frame_witness_valid"]
                    and _reuse_valid(reuse_payload)
                ),
            }
        )

    for row in rows:
        direct = _envelope_direct(rows, float(row["Lambda_batch"]))
        sorted_scan = _envelope_sorted(rows, float(row["Lambda_batch"]))
        if direct != sorted_scan:
            raise AssertionError({"envelope_implementation_disagreement": row["partition"], "direct": direct, "sorted": sorted_scan})
        row["incumbent_envelope_C_at_candidate_Lambda"] = int(direct)
        row["budget_matched_delta"] = int(direct - int(row["C_candidate"]))
        row["strict_budget_matched_improvement"] = row["budget_matched_delta"] > 0

    strict = [row for row in rows if row["strict_budget_matched_improvement"]]
    strict.sort(
        key=lambda row: (
            -int(row["budget_matched_delta"]),
            float(row["Lambda_batch"]),
            row["partition"],
        )
    )
    return {
        "all_partitions": all_partitions,
        "eligible_partition_count": len(rows),
        "eligible_points": rows,
        "candidate_pareto": _pareto(rows, "C_candidate") if rows else [],
        "incumbent_pareto": _pareto(rows, "C_incumbent") if rows else [],
        "strict_points": strict,
        "best_strict_improvement": None if not strict else strict[0],
        "all_witnesses_valid": bool(rows) and all(row["all_witnesses_valid"] for row in rows),
    }


def hostile_validation() -> dict[str, Any]:
    parts = partitions_3plus3()
    partition_gate = (
        len(parts) == 10
        and all(0 in a and set(a).isdisjoint(b) and set(a) | set(b) == set(range(6)) for a, b in parts)
    )

    synthetic_rows = [
        {"partition": [[0, 1, 2], [3, 4, 5]], "Lambda_batch": 1.0, "C_incumbent": 12},
        {"partition": [[0, 1, 3], [2, 4, 5]], "Lambda_batch": 1.1, "C_incumbent": 9},
        {"partition": [[0, 1, 4], [2, 3, 5]], "Lambda_batch": 1.4, "C_incumbent": 7},
        {"partition": [[0, 1, 5], [2, 3, 4]], "Lambda_batch": 1.8, "C_incumbent": 5},
    ]
    envelope_checks = {}
    for lam in (1.0, 1.05, 1.1, 1.3, 1.8, 2.0):
        a = _envelope_direct(synthetic_rows, lam)
        b = _envelope_sorted(synthetic_rows, lam)
        envelope_checks[str(lam)] = {"direct": a, "sorted": b, "pass": a == b}
    gates = {
        "exactly_ten_unordered_partitions": partition_gate,
        "independent_envelope_scans_agree": all(row["pass"] for row in envelope_checks.values()),
    }
    if not all(gates.values()):
        raise AssertionError({"hostile_r6d_failure": gates})
    return {"gates": gates, "envelope_checks": envelope_checks, "all_pass": True}


def run_subject(name: str, cfg) -> dict[str, Any]:
    terms, source_indices, champions, max_imag = _frozen_six_batch(cfg)
    evaluation = _evaluate_fixed_batch(terms, source_indices, int(cfg["n_qubits"]))
    return {
        "subject": name,
        "source_blob": cfg["blob"],
        "n_qubits": int(cfg["n_qubits"]),
        "max_imag": float(max_imag),
        "r6b_window_champions_available": len(champions),
        "frozen_source_indices": list(source_indices),
        **evaluation,
        "strict_budget_matched_improvement_exists": bool(evaluation["strict_points"]),
    }


def main() -> dict[str, Any]:
    hostile = hostile_validation()
    subjects = {name: run_subject(name, cfg) for name, cfg in p10.base.SUBJECTS.items()}
    gates = {
        "hostile_verification_pass": hostile["all_pass"],
        "eligible_partition_exists_both": all(row["eligible_partition_count"] > 0 for row in subjects.values()),
        "all_envelope_witnesses_valid": all(row["all_witnesses_valid"] for row in subjects.values()),
        "strict_budget_matched_improvement_h4": subjects["H4"]["strict_budget_matched_improvement_exists"],
        "strict_budget_matched_improvement_eq_n2": subjects["N2"]["strict_budget_matched_improvement_exists"],
        "fresh_stretched_n2_unread": True,
    }
    supported = all(gates.values())
    result = {
        "schema": "ORIONQ.MAXR6D.SixTermPartitionRepresentationCoopt.v1",
        "authority": (
            "MAX_R6D_SIXTERM_PARTITION_REPRESENTATION_COOPT_SUPPORTED__NOT_R6"
            if supported
            else "MAX_R6D_SIXTERM_PARTITION_REPRESENTATION_COOPT_NEGATIVE__NOT_R6"
        ),
        "scope": "OPEN_H4_EQ_N2_FIXED_SIXTERM_BATCHES__NOT_R6",
        "novelty_credit": False,
        "hostile": hostile,
        "subjects": subjects,
        "gates": gates,
        "development_supported": supported,
        "reserved_stretched_n2_accessed": False,
        "r6_authority": False,
    }
    print("ORIONQ_MAX_R6D_SIXTERM_COOPT=" + json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    main()
