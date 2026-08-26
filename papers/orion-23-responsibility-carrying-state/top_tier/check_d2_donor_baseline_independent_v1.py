#!/usr/bin/env python3
"""P13 D2 donor-complete baseline INDEPENDENT checker V1.

Second implementation of all five arms plus the gates, written table-driven from
the case file alone, sharing no code with run_d2_donor_baseline_v1.py. Also
re-derives case invariants by brute-force enumeration (model-set sizes, gold
dispositions, digests) and asserts the no-alarm case for arms that must be clean.
"""
from __future__ import annotations
from itertools import product
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "p13_d2_donor_cases_v1.json"
PROTOCOL = HERE / "P13_D2_DONOR_BASELINE_PROTOCOL_V1.md"


def clause_ok(clause, model):
    # model is a full assignment as a ±int literal list over vars 1..n
    return any(l in model for l in clause)


def formula_ok(clauses, model):
    return all(clause_ok(c, model) for c in clauses)


def enumerate_models(clauses, n=5):
    out = []
    for bits in product((0, 1), repeat=n):
        cand = [v + 1 if bits[v] else -(v + 1) for v in range(n)]
        if all(any(l in cand for l in c) for c in clauses):
            out.append(cand)
    return out


def gold_digest(clauses):
    canon = json.dumps([sorted(c) for c in sorted([list(c) for c in clauses], key=lambda c: sorted(c))], separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()[:16]


def expected_behavior(case):
    """Table-driven re-derivation of each arm's (served_compact, answer, reads, solver)."""
    cell = case["cell"]
    supported = case["request"]["obligation_digest"] in case["record"]["registered_support"]
    epoch_current = case["record"]["epoch"] == case["checkpoint_epoch"]
    added_literals = sum(len(c) for c in case["added_clauses"])
    full_literals = sum(len(c) for c in case["world_formula_clauses"])
    stored_ok = formula_ok(case["world_formula_clauses"], case["record"]["model"])
    answer_if_solve = enumerate_models(case["world_formula_clauses"])[0]
    tbl = {}
    # D2_CORE / D2_PLUS: compact exactly when provenance-current (demand is LOW on this grid)
    for arm in ("D2_CORE", "D2_PLUS"):
        if epoch_current:
            tbl[arm] = (True, case["record"]["model"], 6, 0)
        else:
            tbl[arm] = (False, case["record"]["model"] if stored_ok else answer_if_solve, full_literals, 0 if stored_ok else 1)
    # RCS / COMPOSED: obligation gate; epoch mismatch alone -> local added-clause re-verify
    for arm in ("RCS", "COMPOSED"):
        if supported and epoch_current:
            tbl[arm] = (True, case["record"]["model"], 6, 0)
        elif supported and formula_ok(case["added_clauses"], case["record"]["model"]):
            tbl[arm] = (False, case["record"]["model"], added_literals, 0)
        else:
            tbl[arm] = (False, case["record"]["model"] if stored_ok else answer_if_solve, full_literals, 0 if stored_ok else 1)
    # ALWAYS_RAW: full read; solve only when stored fails
    tbl["ALWAYS_RAW"] = (False, case["record"]["model"] if stored_ok else answer_if_solve, full_literals, 0 if stored_ok else 1)
    return tbl


def main():
    spec = json.loads(CASES.read_text())
    cases = spec["cases"]
    ARMS = ["D2_CORE", "D2_PLUS", "RCS", "COMPOSED", "ALWAYS_RAW"]
    reads = {a: 0 for a in ARMS}; solvers = {a: 0 for a in ARMS}
    correct = {a: 0 for a in ARMS}; unsupported = {a: 0 for a in ARMS}
    invariant_failures = []
    for case in cases:
        # --- brute-force case invariants (no generator bookkeeping trusted) ---
        F, W = case["base_formula_clauses"], case["world_formula_clauses"]
        mF, mW = enumerate_models(F), enumerate_models(W)
        if len(mF) != 2:
            invariant_failures.append((case["case_id"], "base_not_2_models"))
        if gold_digest(F) != case["record"]["formula_digest"] or gold_digest(F) != case["base_formula_digest"]:
            invariant_failures.append((case["case_id"], "digest_mismatch"))
        want_supported = case["cell"] in ("A_SUPPORTED_CURRENT", "C_SUPPORTED_STALE")
        if case["gold"]["requested_obligation_supported"] != want_supported:
            invariant_failures.append((case["case_id"], "gold_support_mismatch"))
        if case["gold"]["compact_reuse_verdict"] != ("SOUND" if want_supported else "UNSOUND_OBLIGATION"):
            invariant_failures.append((case["case_id"], "gold_verdict_mismatch"))
        want_stored_ok = want_supported
        if formula_ok(W, case["record"]["model"]) != want_stored_ok:
            invariant_failures.append((case["case_id"], "stored_satisfaction_mismatch"))
        if not formula_ok(W, case["gold"]["correct_model"]):
            invariant_failures.append((case["case_id"], "gold_model_not_model_of_world"))
        if case["cell"] == "C_SUPPORTED_STALE" and sorted(map(tuple, mW)) != sorted(map(tuple, mF)):
            invariant_failures.append((case["case_id"], "cellC_model_set_changed"))
        if case["cell"] in ("B_CHANGED_CURRENT", "D_CHANGED_STALE") and len(mW) != 1:
            invariant_failures.append((case["case_id"], "changed_cell_not_1_model"))
        # --- independent arm derivation ---
        tbl = expected_behavior(case)
        for arm in ARMS:
            served, ans, r, s = tbl[arm]
            reads[arm] += r; solvers[arm] += s
            correct[arm] += int(formula_ok(W, ans))
            if served and not want_supported:
                unsupported[arm] += 1
    n = len(cases)
    mean_reads = {a: reads[a] / n for a in ARMS}
    gates = {
        "gate_1_donor_unsupported_on_changed": unsupported["D2_CORE"] >= 1 and unsupported["D2_PLUS"] >= 1,
        "gate_2_rcs_composed_perfect": correct["RCS"] == n and unsupported["RCS"] == 0 and correct["COMPOSED"] == n and unsupported["COMPOSED"] == 0,
        "gate_3_composed_reads_dominates_donor": mean_reads["COMPOSED"] <= mean_reads["D2_CORE"] and mean_reads["COMPOSED"] <= mean_reads["D2_PLUS"],
        "gate_4_always_raw_ceiling": correct["ALWAYS_RAW"] == n,
    }
    green = (not invariant_failures) and all(gates.values())
    out = {
        "schema": "P13.D2DonorBaselineIndependent.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "case_count": n,
        "invariant_failures": invariant_failures,
        "expected_correct": correct,
        "expected_unsupported_reuse": unsupported,
        "expected_mean_literal_reads": mean_reads,
        "expected_solver_calls": solvers,
        "gates": gates,
        "terminal": "P13_D2_DONOR_BASELINE_SECOND_INDEPENDENT_CHECKER_GREEN" if green else "P13_D2_DONOR_BASELINE_INDEPENDENT_CHECKER_RED",
    }
    raw = json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
    out["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(out, indent=2, sort_keys=True))
    assert green, out
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
