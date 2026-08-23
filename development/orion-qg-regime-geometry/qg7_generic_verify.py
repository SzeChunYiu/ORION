#!/usr/bin/env python3
"""Independent generic-harness verifier for QG-7 B' completeness.

Rebuilds the QG-7 normalization local domains (N1-N5) directly from the
primitive local Pauli operations (p10.h) WITHOUT importing the analyzer or
its tables, replays the stored verification sample through the committed
proof-carrying referees (r6o unrestricted-DP truth, r6p D++/D+ enumerator,
qg5b enlarged borrow family), re-verifies the protocol hash, the result
digest, the gates, and terminal consistency, and prints an ACCEPT/REJECT
token.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
ORION_Q = REPO_ROOT / "research" / "extensions" / "orion-q"
ORION_QG = REPO_ROOT / "research" / "extensions" / "orion-qg"
sys.path.insert(0, str(ORION_Q))
sys.path.insert(0, str(ORION_QG))

import max_r6_p10_candidate_blind_frame_optimizer as p10  # noqa: E402
import max_r6m_exact_three_tare2_shared_factor_dp as r6m  # noqa: E402
import max_r6o_enlarged_tag_donor_closure as r6o  # noqa: E402
import max_r6p_weight2_frame_donor_closure as r6p  # noqa: E402
import max_r6s_all_n_composition as r6s  # noqa: E402
import qg5b_exact_forecaster as qg5b  # noqa: E402

r6p.EXPECTED_PAIR_COUNTS.setdefault(4, r6s.PAIR_COUNTS_SUPPORT2[4])

PROTOCOL_PATH = (REPO_ROOT / "development" / "orion-qg-regime-geometry"
                 / "QG7_BPRIME_COMPLETENESS_PROTOCOL_V1.md")
DEFAULT_INPUT = ORION_QG / "QG7_BPRIME_COMPLETENESS_RESULTS.json"
DEFAULT_OUTPUT = (REPO_ROOT / "artifacts"
                  / "orion-qg-qg7-generic-verification.json")
TOKEN_PREFIX = "ORIONQG_QG7_GENERIC_VERIFY="

TERMINALS = {
    "QG7_FOURTH_SUPPORT2_REGIME_FOUND",
    "QG7_ENLARGED_BORROW_COMPLETENESS_ALL_N_MACHINE_CHECKED",
    "QG7_PARTIAL_NORMALIZATION__HYBRID_SHAPE_OPEN",
    "QG7_DONOR_PARENT_FOUND",
    "QG7_CANNOT_CHECK",
}

sy = p10.h.local_symp
lw = p10.h.local_wt


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def f3(a: int, b: int, c: int) -> int:
    return 1 if a == b == c != 0 else lw(a) + lw(b) + lw(c)


def verify_digest(raw: dict[str, Any]) -> bool:
    unsigned = {k: v for k, v in raw.items()
                if k not in ("result_digest", "timing")}
    return raw.get("result_digest") == hashlib.sha256(
        canonical(unsigned).encode()).hexdigest()


# ---- independent rebuilds of the local domains -------------------------------

def rebuild_n1():
    maxima = {"in_place_change": -99, "removal_new_identity": -99,
              "addition_old_identity": -99}
    domain = 0
    for slot, old, new, b, c in itertools.product(
            range(3), range(4), range(4), range(4), range(4)):
        domain += 1
        env = [b, c]
        d = (f3(*(env[:slot] + [new] + env[slot:]))
             - f3(*(env[:slot] + [old] + env[slot:])))
        if old and new:
            maxima["in_place_change"] = max(maxima["in_place_change"], d)
        if not new:
            maxima["removal_new_identity"] = max(
                maxima["removal_new_identity"], d)
        if not old:
            maxima["addition_old_identity"] = max(
                maxima["addition_old_identity"], d)
    return {"domain_size": domain, "maxima": maxima}


def rebuild_n2():
    violations = 0
    equality_failures = 0
    for a, b, c in itertools.product(range(4), repeat=3):
        v = f3(a, b, c)
        bound = lw(a) + lw(b) + lw(c)
        if v > bound:
            violations += 1
        if (a == b == c != 0) != (bound - v == 2):
            equality_failures += 1
        if not (a == b == c != 0) and v != bound:
            equality_failures += 1
    return {"violations": violations, "equality_failures": equality_failures}


def rebuild_n3():
    irreducible = []
    dichotomy_failures = 0
    for a1, b1, a2, b2 in itertools.product((0, 1), repeat=4):
        if (a1 + a2) % 2 != 1:
            continue
        t = ((a1, b1), (a2, b2))
        if (0, 0) in t:
            continue
        if all(cb[1] == 1 for cb in t if cb[0] == 0):
            irreducible.append([2 * a + b for a, b in t])
        else:
            dichotomy_failures += 1
    codes = sorted(irreducible)
    return {"dichotomy_failures": dichotomy_failures,
            "irreducible_codes": codes,
            "binds_w2_boundary": codes == sorted(
                [[1, 2], [1, 3], [2, 1], [3, 1]])}


def rebuild_n5():
    patterns = [
        ("same_support", (0, 1), (0, 1)),
        ("shared_one_qubit", (0, 1), (1, 2)),
        ("disjoint", (0, 1), (2, 3)),
    ]
    per = {}
    for name, q0s, q1s in patterns:
        union = sorted(set(q0s) | set(q1s))
        counts = {"cases": 0, "infeasible_pair": 0, "infeasible_labels": 0,
                  "reducible_by_zeroing": 0, "replaced": 0, "failures": 0}
        for f0, g0, f1, g1 in itertools.product((1, 2, 3), repeat=4):
            r0 = {q0s[0]: f0, q0s[1]: g0}
            r1 = {q1s[0]: f1, q1s[1]: g1}
            for sig in itertools.product(range(4), repeat=len(union)):
                counts["cases"] += 1
                sigma = dict(zip(union, sig))
                if sum(sy(r0.get(q, 0), r1.get(q, 0)) for q in union) % 2 != 1:
                    counts["infeasible_pair"] += 1
                    continue
                l0 = sum(sy(sigma[q], v) for q, v in r0.items()) % 2
                l1 = sum(sy(sigma[q], v) for q, v in r1.items()) % 2
                if l0 == l1:
                    counts["infeasible_labels"] += 1
                    continue
                if any(sy(v, other.get(q, 0)) == 0 and sy(sigma[q], v) == 0
                       for frame, other in ((r0, r1), (r1, r0))
                       for q, v in frame.items()):
                    counts["reducible_by_zeroing"] += 1
                    continue
                cold = r1 if l0 == 1 else r0
                if any(sy(sigma[qp], w) == 1 and sy(w, cold.get(qp, 0)) == 1
                       for qp in union for w in (1, 2, 3)):
                    counts["replaced"] += 1
                else:
                    counts["failures"] += 1
        per[name] = counts
    return per


# ---- sample replay through committed referees --------------------------------

def replay_sample(rows):
    failures = []
    for row in rows:
        n = int(row["n"])
        tp = tuple((tuple(a), tuple(b)) for a, b in row["target_pairs"])
        r6m._local_table.cache_clear()
        r6o._block_cache.clear()
        qg5b._bprime_block_cache.clear()
        c_dp = int(r6o.dp_cost_frozen_configs(r6m._synthetic_terms(tp), n))
        c_dxx = int(r6p.dxx_search(tp, n)["C_Dxx"])
        c_dplus = int(r6p.dxx_search(tp, n, max_weight=1)["C_Dxx"])
        fbp = qg5b.bprime_family_min(tp, n)[0]
        fbp_eff = r6m.INF if fbp is None else int(fbp)
        got = {"C_DP": c_dp, "C_Dxx": c_dxx, "C_Dplus": c_dplus,
               "f_Bprime": fbp_eff}
        want = {k: int(row[k]) for k in got}
        if got != want:
            failures.append({"panel": row["panel"],
                             "local_index": row["local_index"],
                             "got": got, "want": want})
    r6m._local_table.cache_clear()
    return failures


def run(input_path: Path) -> dict[str, Any]:
    raw = json.loads(input_path.read_text(encoding="utf-8"))
    checks_rec = raw.get("arm2_normalization", {}).get("checks", {})
    arm1 = raw.get("arm1_hostile_search", {})
    gates = raw.get("gates", {})
    obligations = raw.get("arm2_normalization", {}).get("obligations", {})

    n1 = rebuild_n1()
    n2 = rebuild_n2()
    n3 = rebuild_n3()
    n5 = rebuild_n5()
    sample = raw.get("verification_sample", [])
    sample_failures = replay_sample(sample)

    rec_n5 = checks_rec.get("N5", {}).get("per_pattern", {})
    terminal = raw.get("terminal")
    fourth_total = arm1.get("fourth_regime_candidates_total", -1)
    confirmed_total = arm1.get("fourth_regime_confirmed_total", -1)
    statuses = {k: v.get("status") for k, v in obligations.items()}
    all_closed = statuses and all(
        s == "CLOSED_ALL_N" for s in statuses.values())
    if confirmed_total > 0:
        expected_terminal = "QG7_FOURTH_SUPPORT2_REGIME_FOUND"
    elif fourth_total > 0 or arm1.get("r6s_contradictions_verbatim") or \
            not all(gates.values()):
        expected_terminal = "QG7_CANNOT_CHECK"
    elif all_closed:
        expected_terminal = \
            "QG7_ENLARGED_BORROW_COMPLETENESS_ALL_N_MACHINE_CHECKED"
    else:
        expected_terminal = "QG7_PARTIAL_NORMALIZATION__HYBRID_SHAPE_OPEN"

    checks = {
        "schema": raw.get("schema") == "ORIONQG.QG7.BprimeCompleteness.v1",
        "protocol_hash": raw.get("protocol_sha256")
        == hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "result_digest": verify_digest(raw),
        "terminal_in_frozen_set": terminal in TERMINALS,
        "terminal_consistent": terminal == expected_terminal,
        "authority_not_r6": "NOT_R6" in str(raw.get("authority", "")),
        "independent_n1_maxima": n1["maxima"]
        == checks_rec.get("N1", {}).get("maxima")
        and n1["maxima"] == {"in_place_change": 2,
                             "removal_new_identity": 1,
                             "addition_old_identity": 1},
        "independent_n1_domain": n1["domain_size"] == 768
        and checks_rec.get("N1", {}).get("domain_size") == 768,
        "independent_n2": n2["violations"] == 0
        and n2["equality_failures"] == 0
        and checks_rec.get("N2", {}).get("holds") is True,
        "independent_n3": n3["dichotomy_failures"] == 0
        and n3["binds_w2_boundary"]
        and checks_rec.get("N3", {}).get("holds") is True,
        "independent_n5_counts": n5 == rec_n5,
        "independent_n5_no_failures": all(
            c["failures"] == 0 for c in n5.values()),
        "n5_domain_sizes": {k: c["cases"] for k, c in n5.items()}
        == {"same_support": 1296, "shared_one_qubit": 5184,
            "disjoint": 20736},
        "sample_nonempty": len(sample) > 0,
        "sample_replay_pass": not sample_failures,
        "referee_failure_lists_empty": all(
            not raw.get("hostile_referee", {}).get(k, ["x"])
            for k in ("dxx_witness_failures", "bprime_witness_failures",
                      "exact_matcher_failures", "containment_failures",
                      "symmetry_failures", "replay_failures")),
        "gates_all_true_iff_not_cannot_check": (
            all(gates.values()) or terminal == "QG7_CANNOT_CHECK"),
        "no_novelty_authority": raw.get("novelty_credit") is False
        and raw.get("r6_authority") is False,
        "no_physical_advantage": raw.get(
            "physical_quantum_advantage_claim") is False,
        "protected_subject_untouched": raw.get(
            "reserved_stretched_n2_accessed") is False
        and raw.get("chemistry_data_read") is False,
    }
    decision = "ACCEPT" if all(
        v is True for v in checks.values()) else "REJECT"
    return {
        "schema": "ORIONQG.QG7.GenericVerification.v1",
        "decision": decision,
        "checks": checks,
        "independent_rebuilds": {"N1": n1, "N2": n2, "N3": n3, "N5": n5},
        "sample_rows_replayed": len(sample),
        "sample_replay_failures": sample_failures,
        "source_result_digest": raw.get("result_digest"),
        "source_terminal": terminal,
        "novelty_authority": False,
        "physical_quantum_advantage_claim": False,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    result = run(Path(args.input))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(TOKEN_PREFIX + canonical(
        {"decision": result["decision"], "path": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
