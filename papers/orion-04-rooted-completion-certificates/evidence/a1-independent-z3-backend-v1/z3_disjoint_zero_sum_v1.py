#!/usr/bin/env python3
"""Independent SMT backend for k disjoint nonempty zero-sum subsequences.

The mathematical input is only an explicit finite abelian group (coordinate
orders), an explicit sequence of occurrences, and k.  The representation uses
one integer assignment variable per occurrence; it imports no ORION search,
branch, orbit, census, normalization, SAT/CNF, or DP implementation.

Calibration is the only authority exercised by this file in-repository.  A
solver UNSAT decision is not an independently checked proof certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Sequence

from z3 import Bool, If, Int, Solver, Sum, get_version_string, sat, unsat

Elem = tuple[int, ...]


def validate_problem(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> tuple[tuple[int, ...], tuple[Elem, ...]]:
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 4:
        raise ValueError("k must be an integer in 1..4")
    ords = tuple(orders)
    if not ords or any(isinstance(o, bool) or not isinstance(o, int) or o < 2 for o in ords):
        raise ValueError("orders must be integers >=2")
    seq: list[Elem] = []
    for idx, raw in enumerate(sequence):
        if len(raw) != len(ords):
            raise ValueError(f"occurrence {idx} dimension mismatch")
        elem = tuple(raw)
        for c, (x, order) in enumerate(zip(elem, ords)):
            if isinstance(x, bool) or not isinstance(x, int) or not 0 <= x < order:
                raise ValueError(f"occurrence {idx} coordinate {c} outside 0..{order-1}")
        seq.append(elem)
    if len(seq) > 31:
        raise ValueError("calibrated backend limits explicit sequences to <=31 occurrences")
    return ords, tuple(seq)


def build_solver(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> tuple[Solver, list[Any]]:
    ords, seq = validate_problem(orders, sequence, k)
    solver = Solver()
    assignment = [Int(f"occ_{i}_bin") for i in range(len(seq))]
    for a in assignment:
        solver.add(a >= -1, a < k)
    for b in range(k):
        solver.add(Sum([If(a == b, 1, 0) for a in assignment]) >= 1)
        for c, order in enumerate(ords):
            coordinate_sum = Sum([If(assignment[i] == b, seq[i][c], 0) for i in range(len(seq))])
            solver.add(coordinate_sum % order == 0)
    return solver, assignment


def verify_witness(orders: Sequence[int], sequence: Sequence[Sequence[int]], bins: Sequence[Sequence[int]], k: int) -> bool:
    ords, seq = validate_problem(orders, sequence, k)
    if len(bins) != k or any(not b for b in bins):
        return False
    used: set[int] = set()
    for members in bins:
        for idx in members:
            if isinstance(idx, bool) or not isinstance(idx, int) or not 0 <= idx < len(seq) or idx in used:
                return False
            used.add(idx)
        for c, order in enumerate(ords):
            if sum(seq[i][c] for i in members) % order != 0:
                return False
    return True


def solve(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> dict[str, Any]:
    ords, seq = validate_problem(orders, sequence, k)
    solver, assignment = build_solver(ords, seq, k)
    smt2 = solver.to_smt2()
    decision = solver.check()
    base = {
        "schema": "ORION04.A1.IndependentZ3Decision.v1",
        "orders": list(ords),
        "n": len(seq),
        "k": k,
        "z3_version": get_version_string(),
        "smt2_sha256": hashlib.sha256(smt2.encode("utf-8")).hexdigest(),
        "sequence_sha256": hashlib.sha256(json.dumps(seq, separators=(",", ":")).encode("utf-8")).hexdigest(),
        "authority": "SOLVER_DECISION_ONLY__UNSAT_IS_NOT_AN_INDEPENDENT_PROOF_CERTIFICATE",
    }
    if decision == sat:
        model = solver.model()
        bins = [[] for _ in range(k)]
        for i, a in enumerate(assignment):
            value = model.eval(a, model_completion=True).as_long()
            if 0 <= value < k:
                bins[value].append(i)
        if not verify_witness(ords, seq, bins, k):
            raise AssertionError("solver SAT model failed primitive witness verification")
        return {**base, "decision": "SAT", "bins": bins, "witness_verified": True}
    if decision == unsat:
        return {**base, "decision": "UNSAT", "bins": None, "witness_verified": None}
    return {**base, "decision": "UNKNOWN", "bins": None, "witness_verified": None, "reason": solver.reason_unknown()}


def brute_exists(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> bool:
    """Independent small-instance reference: enumerate occurrence assignments."""
    ords, seq = validate_problem(orders, sequence, k)
    for assignment in itertools.product(range(-1, k), repeat=len(seq)):
        good = True
        for b in range(k):
            members = [i for i, value in enumerate(assignment) if value == b]
            if not members:
                good = False
                break
            for c, order in enumerate(ords):
                if sum(seq[i][c] for i in members) % order:
                    good = False
                    break
            if not good:
                break
        if good:
            return True
    return False


def frozen_suite_calibration(path: Path) -> dict[str, Any]:
    suite = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for control in suite["controls"]:
        if control["control_kind"] == "malformed_proof_object":
            reject = control["asserted_value_in_malformed_object"] != control["closed_form_value"]
            rows.append({
                "control_kind": control["control_kind"],
                "expected": "REJECT",
                "observed": "REJECT" if reject else "ACCEPT",
                "z3_executed": False,
                "brute_executed": False,
                "agrees": reject,
            })
            continue
        orders = control["orders"]
        seq = control["sequence"]
        k = control["k"]
        if "expected_max_disjoint_zero_sums" in control:
            expected_exists = control["expected_max_disjoint_zero_sums"] >= k
        else:
            expected_exists = control["expected_min_disjoint_zero_sums"] >= k
        z3_exists = solve(orders, seq, k)["decision"] == "SAT"
        brute = brute_exists(orders, seq, k)
        rows.append({
            "control_kind": control["control_kind"],
            "group": control["group"],
            "k": k,
            "expected_exists_k_disjoint": expected_exists,
            "z3_exists_k_disjoint": z3_exists,
            "brute_exists_k_disjoint": brute,
            "agrees": expected_exists == z3_exists == brute,
        })
    return {
        "schema": "ORION04.A1.IndependentZ3FrozenCalibration.v1",
        "suite_schema": suite["schema"],
        "suite_declared_sha256": suite["suite_sha256"],
        "d4_outcome_accessed": False,
        "rows": rows,
        "all_controls_agree": all(r["agrees"] for r in rows),
    }


def exhaustive_small_crosscheck() -> dict[str, Any]:
    specs = [
        ("C3", (3,), tuple((x,) for x in range(3)), 5),
        ("C2xC2", (2, 2), tuple(itertools.product(range(2), repeat=2)), 4),
    ]
    checked = 0
    disagreements = []
    for name, orders, alphabet, max_len in specs:
        for n in range(1, max_len + 1):
            for seq in itertools.combinations_with_replacement(alphabet, n):
                for k in range(1, min(3, n) + 1):
                    z3_exists = solve(orders, seq, k)["decision"] == "SAT"
                    brute = brute_exists(orders, seq, k)
                    checked += 1
                    if z3_exists != brute:
                        disagreements.append({"group": name, "sequence": seq, "k": k, "z3": z3_exists, "brute": brute})
    return {
        "domains": ["all C3 multisets length 1..5", "all C2xC2 multisets length 1..4"],
        "cases_checked": checked,
        "disagreements": disagreements,
        "all_agree": not disagreements,
    }


def mutant_allow_empty(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> bool:
    ords, seq = validate_problem(orders, sequence, k)
    s = Solver()
    assignment = [Int(f"empty_occ_{i}") for i in range(len(seq))]
    for a in assignment:
        s.add(a >= -1, a < k)
    for b in range(k):
        for c, order in enumerate(ords):
            s.add(Sum([If(assignment[i] == b, seq[i][c], 0) for i in range(len(seq))]) % order == 0)
    return s.check() == sat


def mutant_allow_overlap(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> bool:
    ords, seq = validate_problem(orders, sequence, k)
    s = Solver()
    selected = [[Bool(f"overlap_{i}_{b}") for b in range(k)] for i in range(len(seq))]
    for b in range(k):
        s.add(Sum([If(selected[i][b], 1, 0) for i in range(len(seq))]) >= 1)
        for c, order in enumerate(ords):
            s.add(Sum([If(selected[i][b], seq[i][c], 0) for i in range(len(seq))]) % order == 0)
    return s.check() == sat


def mutant_wrong_modulus(sequence: Sequence[Sequence[int]], k: int) -> bool:
    # Deliberately interprets a C5 input using order 3.
    return solve((3,), sequence, k)["decision"] == "SAT"


def mutant_drop_zero_sum(orders: Sequence[int], sequence: Sequence[Sequence[int]], k: int) -> bool:
    _ords, seq = validate_problem(orders, sequence, k)
    s = Solver()
    assignment = [Int(f"drop_occ_{i}") for i in range(len(seq))]
    for a in assignment:
        s.add(a >= -1, a < k)
    for b in range(k):
        s.add(Sum([If(a == b, 1, 0) for a in assignment]) >= 1)
    return s.check() == sat


def mutation_controls() -> dict[str, Any]:
    controls = []

    seq_empty = [(1,)]
    correct_empty = solve((5,), seq_empty, 2)["decision"] == "SAT"
    mutated_empty = mutant_allow_empty((5,), seq_empty, 2)
    controls.append({"mutation": "allow_empty_bins", "correct_sat": correct_empty, "mutant_sat": mutated_empty, "detected": (not correct_empty) and mutated_empty})

    seq_overlap = [(1,)] * 5
    correct_overlap = solve((5,), seq_overlap, 2)["decision"] == "SAT"
    mutated_overlap = mutant_allow_overlap((5,), seq_overlap, 2)
    controls.append({"mutation": "allow_occurrence_reuse_across_bins", "correct_sat": correct_overlap, "mutant_sat": mutated_overlap, "detected": (not correct_overlap) and mutated_overlap})

    seq_mod = [(1,)] * 3
    correct_mod = solve((5,), seq_mod, 1)["decision"] == "SAT"
    mutated_mod = mutant_wrong_modulus(seq_mod, 1)
    controls.append({"mutation": "change_modulus_5_to_3", "correct_sat": correct_mod, "mutant_sat": mutated_mod, "detected": (not correct_mod) and mutated_mod})

    seq_zero = [(1,)]
    correct_zero = solve((5,), seq_zero, 1)["decision"] == "SAT"
    mutated_zero = mutant_drop_zero_sum((5,), seq_zero, 1)
    controls.append({"mutation": "drop_zero_sum_constraint", "correct_sat": correct_zero, "mutant_sat": mutated_zero, "detected": (not correct_zero) and mutated_zero})

    return {"controls": controls, "all_mutations_detected": all(c["detected"] for c in controls)}


def self_test(calibration_suite: Path) -> dict[str, Any]:
    frozen = frozen_suite_calibration(calibration_suite)
    exhaustive = exhaustive_small_crosscheck()
    mutations = mutation_controls()
    good = frozen["all_controls_agree"] and exhaustive["all_agree"] and mutations["all_mutations_detected"]
    return {
        "schema": "ORION04.A1.IndependentZ3CalibrationResult.v1",
        "decision": "GREEN" if good else "REJECT",
        "z3_version": get_version_string(),
        "target_d4_execution_performed": False,
        "protected_d4_outcome_accessed": False,
        "d4_rounds_consumed": 0,
        "frozen_suite": frozen,
        "exhaustive_small_crosscheck": exhaustive,
        "mutation_controls": mutations,
        "scientific_authority_delta": "NONE__CALIBRATION_ONLY",
    }


def load_problem(path: Path) -> tuple[Sequence[int], Sequence[Sequence[int]], int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if set(payload) != {"orders", "sequence", "k"}:
        raise ValueError("generic problem JSON must contain exactly orders, sequence, k")
    return payload["orders"], payload["sequence"], payload["k"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--calibration-suite", type=Path)
    parser.add_argument("--input", type=Path, help="generic explicit small/problem record; does not grant target authority")
    args = parser.parse_args()
    if args.self_test:
        if args.calibration_suite is None:
            parser.error("--self-test requires --calibration-suite")
        result = self_test(args.calibration_suite)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["decision"] == "GREEN" else 1
    if args.input:
        orders, seq, k = load_problem(args.input)
        print(json.dumps(solve(orders, seq, k), indent=2, sort_keys=True))
        return 0
    parser.error("use --self-test with --calibration-suite or provide --input")


if __name__ == "__main__":
    raise SystemExit(main())
