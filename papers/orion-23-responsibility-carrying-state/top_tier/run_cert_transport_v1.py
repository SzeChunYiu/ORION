#!/usr/bin/env python3
"""P13 drift-bounded certificate transport runner V1 (protocol: P13_CERT_TRANSPORT_PROTOCOL_V1.md).

Arms: UNCONDITIONAL, SIGNATURE_ONLY, CONDITIONAL_DRIFT_BOUNDED, ALWAYS_RE_ISSUE.
Every episode ends with a served certificate payload of 6 literal reads
(5 assignment literals + 1 digest token) in ALL arms; arms differ only in
verification reads: transport-permit adds added-clause literals, re-issue adds
full shifted-formula literals plus a solver invocation.
"""
from __future__ import annotations
from itertools import product
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "p13_cert_transport_cases_v1.json"
PROTOCOL = HERE / "P13_CERT_TRANSPORT_PROTOCOL_V1.md"
ARMS = ["UNCONDITIONAL", "SIGNATURE_ONLY", "CONDITIONAL_DRIFT_BOUNDED", "ALWAYS_RE_ISSUE"]
PAYLOAD = 6


def sat(clauses, model_list):
    m = {abs(l): (l > 0) for l in model_list}
    return all(any((m[abs(l)] if l > 0 else not m[abs(l)]) for l in c) for c in clauses)


def solve(clauses, n=5):
    for bits in product((0, 1), repeat=n):
        cand = [v + 1 if bits[v] else -(v + 1) for v in range(n)]
        if sat(clauses, cand):
            return cand
    return None


def literal_reads(clauses):
    return sum(len(c) for c in clauses)


def justification_units(case):
    """Unit clauses of F fixing variables present in the stored model's certification."""
    model = case["issued_certificate"]["model"]
    fixed_vars = {abs(l) for l in model}
    return [c for c in case["source_formula_clauses"] if len(c) == 1 and abs(c[0]) in fixed_vars]


def transport_predicate(case):
    """Frozen drift bound. Returns (PERMIT|DENY, added_literal_reads)."""
    F = [tuple(c) for c in case["source_formula_clauses"]]
    W = [tuple(c) for c in case["shifted_formula_clauses"]]
    added = [list(c) for c in W if c not in set(F)]
    removed = [list(c) for c in F if c not in set(W)]
    just = [tuple(c) for c in justification_units(case)]
    if not added and not removed:
        return "PERMIT", 0  # identical formula: nothing to verify
    if not removed and added:
        model = case["issued_certificate"]["model"]
        if all(sat([c], model) for c in added):  # MONOTONE_ADD with local verification
            return "PERMIT", literal_reads(added)
        return "DENY", 0
    if not added and removed:
        if all(tuple(c) not in just for c in removed):  # MONOTONE_DROP outside justification
            return "PERMIT", 0
        return "DENY", 0
    return "DENY", 0  # mixture or strengthened clause


def run_arm(arm, case):
    """Return (transported, answer_or_None, unsat_claim, reads, solver_calls)."""
    cert = case["issued_certificate"]
    W = case["shifted_formula_clauses"]
    full = literal_reads(W)
    if arm == "UNCONDITIONAL":
        if cert["epoch"] == case["checkpoint_epoch"]:
            return True, cert["model"], False, PAYLOAD, 0
    elif arm == "SIGNATURE_ONLY":
        if cert["formula_digest"] == case["shifted_formula_digest"]:
            return True, cert["model"], False, PAYLOAD, 0
    elif arm == "CONDITIONAL_DRIFT_BOUNDED":
        verdict, local = transport_predicate(case)
        if verdict == "PERMIT":
            return True, cert["model"], False, PAYLOAD + local, 0
    # re-issue path (all fallbacks + ALWAYS_RE_ISSUE)
    model = solve(W)
    if model is None:
        return False, None, True, PAYLOAD + full, 1
    return False, model, False, PAYLOAD + full, 1


def main():
    spec = json.loads(CASES.read_text())
    cases = spec["cases"]
    reads = {a: 0 for a in ARMS}; solvers = {a: 0 for a in ARMS}
    correct = {a: 0 for a in ARMS}
    unsound = {a: 0 for a in ARMS}; needless = {a: 0 for a in ARMS}
    stratum_reads = {}
    rows = []
    for case in cases:
        W = case["world"] if "world" in case else case["shifted_formula_clauses"]
        gold = case["gold"]
        for arm in ARMS:
            transported, ans, unsat_claim, r, s = run_arm(arm, case)
            reads[arm] += r; solvers[arm] += s
            ok = (unsat_claim == gold["unsat"]) and (unsat_claim or sat(W, ans))
            correct[arm] += int(ok)
            if transported and gold["gold_transport"] == "TRANSPORT_DENY":
                unsound[arm] += 1
            if (not transported) and gold["gold_transport"] == "TRANSPORT_SOUND":
                needless[arm] += 1
            stratum_reads.setdefault((arm, case["stratum"]), []).append(r)
            rows.append({"case_id": case["case_id"], "arm": arm, "transported": transported,
                         "unsat_claim": unsat_claim, "verifier_correct": ok, "literal_reads": r})
    n = len(cases)
    mean_reads = {a: reads[a] / n for a in ARMS}
    stratum_mean = {f"{a}|{s}": sum(v) / len(v) for (a, s), v in stratum_reads.items()}
    t1 = unsound["CONDITIONAL_DRIFT_BOUNDED"] == 0 and needless["CONDITIONAL_DRIFT_BOUNDED"] == 0 and correct["CONDITIONAL_DRIFT_BOUNDED"] == n
    t2 = unsound["UNCONDITIONAL"] >= 1
    t3 = needless["SIGNATURE_ONLY"] >= 1
    t4 = correct["ALWAYS_RE_ISSUE"] == n and stratum_mean["ALWAYS_RE_ISSUE|REDUNDANT"] > stratum_mean["CONDITIONAL_DRIFT_BOUNDED|REDUNDANT"]
    positive = t1 and t2 and t3 and t4
    receipt = {
        "schema": "P13.CertTransportResult.v1",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "case_count": n,
        "arms": ARMS,
        "verifier_correct": correct,
        "unsound_transport": unsound,
        "needless_reissue": needless,
        "total_literal_reads": reads,
        "mean_literal_reads": mean_reads,
        "stratum_mean_literal_reads": stratum_mean,
        "solver_calls": solvers,
        "gate_1_conditional_exact": t1,
        "gate_2_unconditional_unsound": t2,
        "gate_3_signature_needless": t3,
        "gate_4_reissue_cost_ceiling": t4,
        "rows": rows,
        "terminal": "P13_CERT_TRANSPORT_V1_SUPPORTED" if positive else "P13_CERT_TRANSPORT_V1_GATE_NOT_MET",
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    assert positive, receipt
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
