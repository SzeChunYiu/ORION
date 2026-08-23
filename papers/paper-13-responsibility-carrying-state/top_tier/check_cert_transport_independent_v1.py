#!/usr/bin/env python3
"""P13 certificate transport INDEPENDENT checker V1.

Second, table-driven implementation of the four transport arms and gates,
sharing no code with run_cert_transport_v1.py, plus brute-force re-derivation of
case invariants (model-set preservation on REDUNDANT, stored-model violation on
CONFLICTING, gold dispositions, digests).
"""
from __future__ import annotations
from itertools import product
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "p13_cert_transport_cases_v1.json"
PROTOCOL = HERE / "P13_CERT_TRANSPORT_PROTOCOL_V1.md"
ARMS = ["UNCONDITIONAL", "SIGNATURE_ONLY", "CONDITIONAL_DRIFT_BOUNDED", "ALWAYS_RE_ISSUE"]


def ok(clauses, model_list):
    s = set(model_list)
    return all(any(l in s for l in c) for c in clauses)


def all_models(clauses, n=5):
    out = []
    for bits in product((0, 1), repeat=n):
        cand = [v + 1 if bits[v] else -(v + 1) for v in range(n)]
        if all(any(l in cand for l in c) for c in clauses):
            out.append(cand)
    return out


def dg(clauses):
    canon = json.dumps([sorted(c) for c in sorted([list(c) for c in clauses], key=lambda c: sorted(c))], separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()[:16]


def permit(case):
    """Independent drift-bound derivation via set algebra on clause multisets."""
    Fset = {tuple(sorted(c)) for c in case["source_formula_clauses"]}
    Wset = {tuple(sorted(c)) for c in case["shifted_formula_clauses"]}
    add = [list(c) for c in Wset - Fset]
    drop = [list(c) for c in Fset - Wset]
    cert_model = case["issued_certificate"]["model"]
    just_vars = {abs(l) for l in cert_model}
    just = {tuple(sorted(c)) for c in case["source_formula_clauses"]
            if len(c) == 1 and abs(c[0]) in just_vars}
    if add and not drop:
        return all(ok([c], cert_model) for c in add), sum(len(c) for c in add)
    if drop and not add:
        return all(tuple(sorted(c)) not in just for c in drop), 0
    if not add and not drop:
        return True, 0
    return False, 0


def expected(arm, case):
    """Return (transported, final_answer_or_None, unsat_claim, reads, solver)."""
    cert = case["issued_certificate"]
    W = case["shifted_formula_clauses"]
    full = sum(len(c) for c in W)
    if arm == "UNCONDITIONAL" and cert["epoch"] == case["checkpoint_epoch"]:
        return True, cert["model"], False, 6, 0
    if arm == "SIGNATURE_ONLY" and cert["formula_digest"] == case["shifted_formula_digest"]:
        return True, cert["model"], False, 6, 0
    if arm == "CONDITIONAL_DRIFT_BOUNDED":
        p, local = permit(case)
        if p:
            return True, cert["model"], False, 6 + local, 0
    ms = all_models(W)
    if not ms:
        return False, None, True, 6 + full, 1
    return False, ms[0], False, 6 + full, 1


def main():
    spec = json.loads(CASES.read_text())
    cases = spec["cases"]
    reads = {a: 0 for a in ARMS}; solvers = {a: 0 for a in ARMS}
    correct = {a: 0 for a in ARMS}; unsound = {a: 0 for a in ARMS}; needless = {a: 0 for a in ARMS}
    stratum = {}
    failures = []
    for case in cases:
        gold = case["gold"]
        F, W = case["source_formula_clauses"], case["shifted_formula_clauses"]
        mF, mW = all_models(F), all_models(W)
        if dg(F) != case["issued_certificate"]["formula_digest"]:
            failures.append((case["case_id"], "source_digest"))
        if dg(W) != case["shifted_formula_digest"]:
            failures.append((case["case_id"], "shifted_digest"))
        if gold["gold_transport"] != ("TRANSPORT_SOUND" if case["stratum"] == "REDUNDANT" else "TRANSPORT_DENY"):
            failures.append((case["case_id"], "gold_disposition"))
        if gold["stored_model_satisfies_shifted"] != ok(W, case["issued_certificate"]["model"]):
            failures.append((case["case_id"], "stored_satisfaction"))
        if len(mF) != 2:
            failures.append((case["case_id"], "source_not_2_models"))
        if case["stratum"] == "REDUNDANT":
            if sorted(map(tuple, mW)) != sorted(map(tuple, mF)) or not ok(W, case["issued_certificate"]["model"]):
                failures.append((case["case_id"], "redundant_model_set_or_stored"))
        if case["stratum"] == "CONFLICTING":
            if ok(W, case["issued_certificate"]["model"]) or len(mW) != 1:
                failures.append((case["case_id"], "conflicting_invariant"))
        if gold["unsat"]:
            if mW:
                failures.append((case["case_id"], "unsat_gold_but_sat"))
        else:
            if not ok(W, gold["correct_model"]):
                failures.append((case["case_id"], "gold_model_invalid"))
        for arm in ARMS:
            transported, ans, unsat_claim, r, s = expected(arm, case)
            reads[arm] += r; solvers[arm] += s
            good = (unsat_claim == gold["unsat"]) and (unsat_claim or ok(W, ans))
            correct[arm] += int(good)
            if transported and gold["gold_transport"] == "TRANSPORT_DENY":
                unsound[arm] += 1
            if (not transported) and gold["gold_transport"] == "TRANSPORT_SOUND":
                needless[arm] += 1
            stratum.setdefault((arm, case["stratum"]), []).append(r)
    n = len(cases)
    mean_reads = {a: reads[a] / n for a in ARMS}
    smean = {f"{a}|{s}": sum(v) / len(v) for (a, s), v in stratum.items()}
    gates = {
        "gate_1_conditional_exact": unsound["CONDITIONAL_DRIFT_BOUNDED"] == 0 and needless["CONDITIONAL_DRIFT_BOUNDED"] == 0 and correct["CONDITIONAL_DRIFT_BOUNDED"] == n,
        "gate_2_unconditional_unsound": unsound["UNCONDITIONAL"] >= 1,
        "gate_3_signature_needless": needless["SIGNATURE_ONLY"] >= 1,
        "gate_4_reissue_cost_ceiling": correct["ALWAYS_RE_ISSUE"] == n and smean["ALWAYS_RE_ISSUE|REDUNDANT"] > smean["CONDITIONAL_DRIFT_BOUNDED|REDUNDANT"],
    }
    green = (not failures) and all(gates.values())
    out = {
        "schema": "P13.CertTransportIndependent.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "case_count": n,
        "invariant_failures": failures,
        "expected_correct": correct,
        "expected_unsound_transport": unsound,
        "expected_needless_reissue": needless,
        "expected_mean_literal_reads": mean_reads,
        "expected_stratum_mean_literal_reads": smean,
        "expected_solver_calls": solvers,
        "gates": gates,
        "terminal": "P13_CERT_TRANSPORT_SECOND_INDEPENDENT_CHECKER_GREEN" if green else "P13_CERT_TRANSPORT_INDEPENDENT_CHECKER_RED",
    }
    raw = json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
    out["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(out, indent=2, sort_keys=True))
    assert green, out
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
