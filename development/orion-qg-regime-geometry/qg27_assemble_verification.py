#!/usr/bin/env python3
"""Assemble QG27_GENERIC_VERIFICATION.json: verdict, determinism (G8), tampers (G7, G6).

G6 requires the falsifiability demonstration be validated through the committed
`orion_research_harness.falsifiability` gate: every case declares the check that
must catch it, and this refuses to write if any case is caught by a different one.
"""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
VERIFIER = HERE / "qg27_generic_verify.py"
RECEIPT = REPO / "research" / "extensions" / "orion-qg" / "QG27_COST_MINIMALITY_RESULTS.json"
ARTIFACT = HERE / "QG27_GENERIC_VERIFICATION.json"
sys.path.insert(0, str(REPO / "packages" / "orion-research-harness" / "src"))

from orion_research_harness.falsifiability import (  # noqa: E402
    validate_determinism,
    validate_falsifiability_demonstration,
)


def canonical(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def reseal(r: dict) -> dict:
    body = {k: v for k, v in r.items() if k != "result_digest"}
    r["result_digest"] = hashlib.sha256(canonical(body).encode()).hexdigest()
    return r


def run(path: pathlib.Path):
    p = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                       capture_output=True, text=True, cwd=str(REPO))
    out = json.loads(p.stdout.split("QG27_GENERIC_VERIFY=")[0])
    return out["verdict"], out["failed_checks"], p.stdout


def t1(r):
    r["terminal"] = "QG27_COST_REDUCTION_CANDIDATE__UNPROVEN_BEYOND_HORIZON"
    return r


def t2(r):
    r["cost_mergeability_reduces_to_feasibility"]["letters_span_rank"] = 9
    r["cost_mergeability_reduces_to_feasibility"]["reachable_subgroup_order"] = 512
    return r


def t3(r):
    """The refutation names a pair whose costs are actually equal -- so it refutes nothing."""
    r["frozen_criterion_refutation"]["optimal_cost_to_go_b"] = \
        r["frozen_criterion_refutation"]["optimal_cost_to_go_a"]
    return r


def t4(r):
    """The exhibited rejection claims it separated everything, i.e. did not reject."""
    r["exhibited_rejection"]["every_state_separated"] = True
    return r


def t5(r):
    r["criterion_binding"][0].pop("exhibited_rejection_ref", None)
    return r


def t6(r):
    r["criterion_binding"][0]["applied_criterion_digest"] = \
        r["criterion_binding"][0]["frozen_criterion_digest"]
    return r


def t7(r):
    r["g4_no_efficiency_claim"] = "the quotient DP is smaller, so the algorithm is faster"
    return r


def t8(r):
    r["novelty_authority"] = True
    return r


def t9(r):
    r["letters_with_finite_cost"] = 999
    return r


def t10(r):
    r["scope_limit"] = "this result holds for the full key-varying DP"
    r["frozen_key_is_the_only_key_used"] = False
    return r


TAMPERS = [
    ("T1_terminal_flipped", "the headline terminal is flipped to the opposite branch", t1),
    ("T2_span_rank_understated_coherently",
     "the letter span rank is lowered to 9 with the subgroup order adjusted to match", t2),
    ("T3_refutation_names_an_equal_cost_pair",
     "the counterexample that refutes the lane's own frozen criterion is edited so the "
     "two states have equal cost, refuting nothing", t3),
    ("T4_exhibited_rejection_did_not_reject",
     "the exhibited rejection claims it separated every state, i.e. that the changed "
     "criterion did not fail on the construction built to make it fail", t4),
    ("T5_exhibited_rejection_ref_removed",
     "the criterion record drops its exhibited_rejection_ref while keeping the PASS", t5),
    ("T6_criterion_change_concealed",
     "the applied criterion digest is set equal to the frozen one, hiding the change", t6),
    ("T7_g4_replaced_by_a_speed_claim",
     "the gate-G4 statement is replaced with the efficiency claim G4 forbids", t7),
    ("T8_novelty_authority_granted", "novelty_authority is flipped to true", t8),
    ("T9_letter_count_altered", "the count of finite-cost letters is altered", t9),
    ("T10_scope_limit_widened_to_all_keys",
     "the scope limit is rewritten to claim the full key-varying DP", t10),
]

EXPECTED_CHECK = {
    "T1_terminal_flipped": "terminal_follows_from_the_recomputed_numbers",
    "T2_span_rank_understated_coherently": "letters_span_rank_recomputed",
    "T3_refutation_names_an_equal_cost_pair": "frozen_criterion_refutation_holds",
    "T4_exhibited_rejection_did_not_reject": "exhibited_rejection_really_rejects",
    "T5_exhibited_rejection_ref_removed": "criterion_binding_gate_reimplemented",
    "T6_criterion_change_concealed": "criterion_binding_gate_reimplemented",
    "T7_g4_replaced_by_a_speed_claim": "no_efficiency_claim_g4",
    "T8_novelty_authority_granted": "authority_ceiling_not_r6",
    "T9_letter_count_altered": "cost_table_rebuilt_from_the_committed_dp",
    "T10_scope_limit_widened_to_all_keys": "scope_limit_declares_the_single_key",
}


def _enforce(art: dict) -> None:
    broken = []
    if art["verdict"] != "ACCEPT" or art["failed_checks"]:
        broken.append(f"clean receipt did not ACCEPT: {art['failed_checks']}")
    try:
        validate_falsifiability_demonstration(art["falsifiability_demonstration"], EXPECTED_CHECK)
    except ValueError as exc:
        broken.append(f"G7: {exc}")
    try:
        validate_determinism(art["determinism"])
    except ValueError as exc:
        broken.append(f"G8: {exc}")
    if broken:
        raise SystemExit("refusing to write the verification artifact -- its own gates "
                         "did not hold: " + "; ".join(broken))


def main() -> int:
    receipt = json.loads(RECEIPT.read_text())
    verdict, failed, out1 = run(RECEIPT)
    _, _, out2 = run(RECEIPT)

    cases = []
    with tempfile.TemporaryDirectory(prefix="qg27-tamper-") as tmp:
        for name, desc, mutate in TAMPERS:
            p = pathlib.Path(tmp) / f"{name}.json"
            m = reseal(mutate(copy.deepcopy(receipt)))
            p.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
            body = {k: v for k, v in m.items() if k != "result_digest"}
            consistent = hashlib.sha256(canonical(body).encode()).hexdigest() == m["result_digest"]
            tv, tf, _ = run(p)
            cases.append({
                "case": name, "tamper": desc,
                "result_digest_recomputed_so_copy_is_internally_self_consistent": consistent,
                "verdict": tv, "failed_checks": tf,
            })

    art = json.loads(out1.split("QG27_GENERIC_VERIFY=")[0])
    art["schema"] = "ORIONQG.QG27.GenericVerification.v1"
    art["verifier_sha256"] = hashlib.sha256(VERIFIER.read_bytes()).hexdigest()
    art["analyzer_sha256"] = hashlib.sha256(
        (REPO / "research" / "extensions" / "orion-qg" / "qg27_cost_minimality.py").read_bytes()
    ).hexdigest()
    art["determinism"] = {
        "double_run": True, "stdout_identical": out1 == out2,
        "run1_sha256": hashlib.sha256(out1.encode()).hexdigest(),
        "run2_sha256": hashlib.sha256(out2.encode()).hexdigest(),
    }
    art["falsifiability_demonstration"] = {
        "method": ("each tampered copy has its result_digest RECOMPUTED, so no hash "
                   "mismatch is available; every rejection comes from re-derivation "
                   "against the committed DP"),
        "tamper_files_kept_outside_the_repository": True,
        "each_case_names_the_field_it_mutates": True,
        "validated_through": "orion_research_harness.falsifiability",
        "all_tampered_copies_internally_self_consistent": all(
            c["result_digest_recomputed_so_copy_is_internally_self_consistent"] for c in cases),
        "all_tampered_copies_rejected": all(c["verdict"] == "REJECT" for c in cases),
        "expected_check_per_case": EXPECTED_CHECK,
        "cases": cases,
    }
    _enforce(art)
    ARTIFACT.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": art["verdict"], "failed_checks": art["failed_checks"],
        "deterministic": art["determinism"]["stdout_identical"],
        "tamper_verdicts": {c["case"]: c["verdict"] for c in cases},
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
