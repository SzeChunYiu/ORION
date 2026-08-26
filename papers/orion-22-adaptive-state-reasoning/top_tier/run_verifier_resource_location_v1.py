#!/usr/bin/env python3
"""Execute the prospectively frozen P12 verifier-backed resource-location study."""

from __future__ import annotations

from collections import defaultdict
from itertools import product
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "P12_VERIFIER_SEARCH_PROTOCOL_V1.md"
CASES = HERE / "sat_resource_location_cases_v1.json"


class BudgetExhausted(Exception):
    pass


class WorkCounter:
    def __init__(self, budget: int):
        self.budget = budget
        self.propagation = 0
        self.search = 0
        self.phase = "search"

    def charge(self) -> None:
        if self.total >= self.budget:
            raise BudgetExhausted
        if self.phase == "propagation":
            self.propagation += 1
        else:
            self.search += 1

    @property
    def total(self) -> int:
        return self.propagation + self.search


def literal_truth(lit: int, assignment: dict[int, bool]) -> bool:
    value = assignment[abs(lit)]
    return value if lit > 0 else not value


def clause_status(clause: list[int], assignment: dict[int, bool], work: WorkCounter):
    unassigned = []
    for lit in clause:
        work.charge()
        var = abs(lit)
        if var not in assignment:
            unassigned.append(lit)
        elif literal_truth(lit, assignment):
            return "SAT", None
    if not unassigned:
        return "CONFLICT", None
    if len(unassigned) == 1:
        return "UNIT", unassigned[0]
    return "OPEN", None


def propagate(clauses: list[list[int]], assignment: dict[int, bool], work: WorkCounter):
    work.phase = "propagation"
    assignment = dict(assignment)
    while True:
        changed = False
        for clause in clauses:
            status, unit = clause_status(clause, assignment, work)
            if status == "CONFLICT":
                return assignment, True
            if status == "UNIT":
                assert unit is not None
                var = abs(unit)
                value = unit > 0
                if var in assignment and assignment[var] != value:
                    return assignment, True
                if var not in assignment:
                    assignment[var] = value
                    changed = True
        if not changed:
            return assignment, False


def verify_assignment(clauses: list[list[int]], assignment: dict[int, bool]) -> bool:
    return all(any(literal_truth(lit, assignment) for lit in clause) for clause in clauses)


def exhaustive_truth(clauses: list[list[int]], n_vars: int) -> tuple[bool, dict[int, bool] | None]:
    for bits in product((False, True), repeat=n_vars):
        assignment = {i + 1: bits[i] for i in range(n_vars)}
        if verify_assignment(clauses, assignment):
            return True, assignment
    return False, None


def search(clauses: list[list[int]], n_vars: int, partial: dict[int, bool], work: WorkCounter):
    work.phase = "search"
    remaining = [v for v in range(1, n_vars + 1) if v not in partial]
    tried = 0
    for bits in product((False, True), repeat=len(remaining)):
        tried += 1
        assignment = dict(partial)
        assignment.update({v: bit for v, bit in zip(remaining, bits)})
        all_sat = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                work.charge()
                if literal_truth(lit, assignment):
                    clause_sat = True
                    break
            if not clause_sat:
                all_sat = False
                break
        if all_sat:
            return "SAT", assignment, tried
    return "UNSAT", None, tried


def execute(case: dict[str, Any], policy: str, budget: int, threshold: int) -> dict[str, Any]:
    clauses = case["clauses"]
    n_vars = case["n_vars"]
    unit_count = sum(len(c) == 1 for c in clauses)
    work = WorkCounter(budget)
    partial: dict[int, bool] = {}
    compiled = False
    contradiction = False
    search_tried = 0

    should_propagate = policy == "PROPAGATE_FIRST" or (policy == "ADAPTIVE_LOCATION" and unit_count >= threshold)

    try:
        if should_propagate:
            compiled = True
            partial, contradiction = propagate(clauses, partial, work)
            if contradiction:
                terminal = "UNSAT"
                assignment = None
            else:
                terminal, assignment, search_tried = search(clauses, n_vars, partial, work)
        else:
            terminal, assignment, search_tried = search(clauses, n_vars, partial, work)
    except BudgetExhausted:
        terminal = "BUDGET_EXHAUSTED"
        assignment = None

    # Independent verifier is outside candidate resource accounting.
    true_sat, _ = exhaustive_truth(clauses, n_vars)
    verifier_correct = False
    if terminal == "SAT":
        assert assignment is not None
        verifier_correct = verify_assignment(clauses, assignment) and true_sat
    elif terminal == "UNSAT":
        verifier_correct = not true_sat
    elif terminal == "BUDGET_EXHAUSTED":
        verifier_correct = True  # correct abstention/non-claim

    return {
        "id": case["id"],
        "family": case["family"],
        "policy": policy,
        "unit_clause_count": unit_count,
        "compiled": compiled,
        "variables_fixed_by_compilation": len(partial),
        "terminal": terminal,
        "verifier_correct": verifier_correct,
        "true_satisfiable": true_sat,
        "propagation_literal_evaluations": work.propagation,
        "search_literal_evaluations": work.search,
        "total_literal_evaluations": work.total,
        "search_assignments_tried": search_tried,
        "assignment": {str(k): v for k, v in sorted(assignment.items())} if assignment else None,
    }


def solved(row: dict[str, Any]) -> bool:
    return row["terminal"] in ("SAT", "UNSAT") and row["verifier_correct"]


def mean(values):
    return sum(values) / len(values) if values else None


def main() -> int:
    spec = json.loads(CASES.read_text())
    cases = spec["cases"]
    budget = spec["work_budget"]
    threshold = spec["adaptive_unit_threshold"]
    assert budget == 2000 and threshold == 4 and len(cases) == 16
    assert len({c["id"] for c in cases}) == len(cases)

    policies = ("REASON_ONLY", "PROPAGATE_FIRST", "ADAPTIVE_LOCATION")
    rows = []
    for case in cases:
        for policy in policies:
            rows.append(execute(case, policy, budget, threshold))

    # Oracle is a post-hoc diagnostic over the two fixed non-adaptive policies only.
    oracle_rows = []
    for case in cases:
        candidates = [r for r in rows if r["id"] == case["id"] and r["policy"] in ("REASON_ONLY", "PROPAGATE_FIRST")]
        successful = [r for r in candidates if solved(r)]
        if successful:
            best = min(successful, key=lambda r: r["total_literal_evaluations"])
            oracle_rows.append({"id": case["id"], "terminal": best["terminal"], "work": best["total_literal_evaluations"]})
        else:
            oracle_rows.append({"id": case["id"], "terminal": "BUDGET_EXHAUSTED", "work": budget})

    summaries = {}
    for policy in policies:
        rr = [r for r in rows if r["policy"] == policy]
        solved_rows = [r for r in rr if solved(r)]
        summaries[policy] = {
            "solve_count": len(solved_rows),
            "solve_rate": len(solved_rows) / len(rr),
            "mean_work_solved": mean([r["total_literal_evaluations"] for r in solved_rows]),
            "max_work": max(r["total_literal_evaluations"] for r in rr),
            "budget_exhausted": sum(r["terminal"] == "BUDGET_EXHAUSTED" for r in rr),
            "mean_propagation_work": mean([r["propagation_literal_evaluations"] for r in rr]),
            "mean_search_work": mean([r["search_literal_evaluations"] for r in rr]),
            "all_verifier_correct": all(r["verifier_correct"] for r in rr),
        }

    family = defaultdict(dict)
    for fam in sorted({c["family"] for c in cases}):
        for policy in policies:
            rr = [r for r in rows if r["family"] == fam and r["policy"] == policy]
            family[fam][policy] = {
                "solve_count": sum(solved(r) for r in rr),
                "mean_work": mean([r["total_literal_evaluations"] for r in rr]),
            }

    adaptive = {r["id"]: r for r in rows if r["policy"] == "ADAPTIVE_LOCATION"}
    oracle = {r["id"]: r for r in oracle_rows}
    regrets = []
    for case in cases:
        a = adaptive[case["id"]]
        o = oracle[case["id"]]
        if solved(a) and o["terminal"] in ("SAT", "UNSAT"):
            regrets.append(a["total_literal_evaluations"] - o["work"])
        elif not solved(a) and o["terminal"] in ("SAT", "UNSAT"):
            regrets.append(budget - o["work"])
        else:
            regrets.append(0)

    a = summaries["ADAPTIVE_LOCATION"]
    r = summaries["REASON_ONLY"]
    p = summaries["PROPAGATE_FIRST"]
    # The protocol allows strict solve improvement vs one comparator while no more
    # mean work than the other, or lower mean work than both at equal-or-better solve rate.
    allowed_second_disjunct = (
        a["solve_rate"] > r["solve_rate"] and a["mean_work_solved"] <= p["mean_work_solved"]
    ) or (
        a["solve_rate"] > p["solve_rate"] and a["mean_work_solved"] <= r["mean_work_solved"]
    )
    positive = (
        a["solve_rate"] >= r["solve_rate"]
        and a["solve_rate"] >= p["solve_rate"]
        and (
            (a["mean_work_solved"] < r["mean_work_solved"] and a["mean_work_solved"] < p["mean_work_solved"])
            or allowed_second_disjunct
        )
        and all(summaries[policy]["all_verifier_correct"] for policy in policies)
    )

    receipt = {
        "protocol": "P12_VERIFIER_SEARCH_PROTOCOL_V1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "case_count": len(cases),
        "work_budget": budget,
        "adaptive_unit_threshold": threshold,
        "summaries": summaries,
        "family_summaries": family,
        "oracle": oracle_rows,
        "adaptive_regret_vs_oracle": {
            "per_case": regrets,
            "mean": mean(regrets),
            "max": max(regrets),
        },
        "frontier_positive": positive,
        "terminal": (
            "P12_VERIFIER_RESOURCE_LOCATION_V1_SUPPORTED"
            if positive
            else "P12_VERIFIER_RESOURCE_LOCATION_V1_GATE_NOT_MET"
        ),
        "rows": rows,
    }
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
