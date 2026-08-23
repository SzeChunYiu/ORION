#!/usr/bin/env python3
"""P13 D2 donor-complete baseline runner V1 (protocol: P13_D2_DONOR_BASELINE_PROTOCOL_V1.md).

Arms: D2_CORE, D2_PLUS (donor-complete provenance-tiered memory, strongest form),
RCS (responsibility-carrying state), COMPOSED (D2 tiering + obligation gate),
ALWAYS_RAW (ceiling). Resource accounting = literal reads; solver calls separate.
Compact serve payload = 5 assignment literals + 1 digest token = 6.
"""
from __future__ import annotations
from itertools import product
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "p13_d2_donor_cases_v1.json"
PROTOCOL = HERE / "P13_D2_DONOR_BASELINE_PROTOCOL_V1.md"
ARMS = ["D2_CORE", "D2_PLUS", "RCS", "COMPOSED", "ALWAYS_RAW"]
COMPACT_PAYLOAD = 6  # 5 assignment literals + 1 digest token


def model_map(model_list):
    return {abs(l): (l > 0) for l in model_list}


def sat(clauses, model_list):
    m = model_map(model_list)
    return all(any((m[abs(l)] if l > 0 else not m[abs(l)]) for l in c) for c in clauses)


def solve(clauses, n=5):
    for bits in product((0, 1), repeat=n):
        cand = [v + 1 if bits[v] else -(v + 1) for v in range(n)]
        if sat(clauses, cand):
            return cand
    return None


def literal_reads(clauses):
    return sum(len(c) for c in clauses)


def run_arm(arm, case):
    """Return (answer_model_or_None, reads, solver_calls, served_compact)."""
    rec, world = case["record"], case
    obligation_supported = case["request"]["obligation_digest"] in rec["registered_support"]
    epoch_current = rec["epoch"] == case["checkpoint_epoch"]
    added = case["added_clauses"]
    full = case["world_formula_clauses"]
    # demand grade for D2_PLUS: CERTIFY on a G=MAX verifier-issued record -> LOW
    demand_low = case["request"]["task_type"] == "CERTIFY" and rec["grounding_grade"] == "MAX"
    if arm == "D2_CORE":
        if epoch_current:
            return rec["model"], COMPACT_PAYLOAD, 0, True
    elif arm == "D2_PLUS":
        if epoch_current and demand_low:
            return rec["model"], COMPACT_PAYLOAD, 0, True
    elif arm == "RCS":
        if obligation_supported and epoch_current:
            return rec["model"], COMPACT_PAYLOAD, 0, True
        if obligation_supported:  # epoch mismatch alone -> local re-verification of added clauses
            if sat(added, rec["model"]):
                return rec["model"], literal_reads(added), 0, False
    elif arm == "COMPOSED":
        if epoch_current and obligation_supported:  # D2 tiering, obligation gate substituted for demand gate
            return rec["model"], COMPACT_PAYLOAD, 0, True
        if obligation_supported:
            if sat(added, rec["model"]):
                return rec["model"], literal_reads(added), 0, False
    # raw path (all arms' fallback + ALWAYS_RAW)
    if sat(full, rec["model"]):
        return rec["model"], literal_reads(full), 0, False
    return solve(full), literal_reads(full), 1, False


def main():
    spec = json.loads(CASES.read_text())
    cases = spec["cases"]
    reads = {a: 0 for a in ARMS}; solvers = {a: 0 for a in ARMS}
    correct = {a: 0 for a in ARMS}; unsupported = {a: 0 for a in ARMS}
    compact_serves = {a: 0 for a in ARMS}
    per_cell_reads = {}
    rows = []
    for case in cases:
        world = case["world_formula_clauses"]
        for arm in ARMS:
            ans, r, s, served = run_arm(arm, case)
            reads[arm] += r; solvers[arm] += s
            if served:
                compact_serves[arm] += 1
                if case["gold"]["compact_reuse_verdict"] == "UNSOUND_OBLIGATION":
                    unsupported[arm] += 1
            ok = ans is not None and sat(world, ans)
            correct[arm] += int(ok)
            per_cell_reads.setdefault((arm, case["cell"]), []).append(r)
            rows.append({"case_id": case["case_id"], "arm": arm, "served_compact": served,
                         "answer": ans, "verifier_correct": ok, "literal_reads": r, "solver_calls": s})
    n = len(cases)
    mean_reads = {a: reads[a] / n for a in ARMS}
    cell_mean = {f"{a}|{c}": sum(v) / len(v) for (a, c), v in per_cell_reads.items()}
    # degenerate control: D2 forced raw at every episode (checkpoint interval -> 0) = ALWAYS_RAW cost
    degenerate_d2 = reads["ALWAYS_RAW"]
    t1 = unsupported["D2_CORE"] >= 1 and unsupported["D2_PLUS"] >= 1
    t2 = correct["RCS"] == n and unsupported["RCS"] == 0 and correct["COMPOSED"] == n and unsupported["COMPOSED"] == 0
    t3 = mean_reads["COMPOSED"] <= mean_reads["D2_CORE"] and mean_reads["COMPOSED"] <= mean_reads["D2_PLUS"]
    t4 = correct["ALWAYS_RAW"] == n
    positive = t1 and t2 and t3 and t4
    receipt = {
        "schema": "P13.D2DonorBaselineResult.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "case_count": n,
        "arms": ARMS,
        "verifier_correct": correct,
        "unsupported_reuse": unsupported,
        "compact_serves": compact_serves,
        "total_literal_reads": reads,
        "mean_literal_reads": mean_reads,
        "cell_mean_literal_reads": cell_mean,
        "solver_calls": solvers,
        "degenerate_d2_equals_always_raw_reads": degenerate_d2,
        "gate_1_donor_unsupported_on_changed": t1,
        "gate_2_rcs_composed_perfect": t2,
        "gate_3_composed_reads_dominates_donor": t3,
        "gate_4_always_raw_ceiling": t4,
        "rows": rows,
        "terminal": "P13_D2_DONOR_BASELINE_V1_SUPPORTED" if positive else "P13_D2_DONOR_BASELINE_V1_GATE_NOT_MET",
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert positive, receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
