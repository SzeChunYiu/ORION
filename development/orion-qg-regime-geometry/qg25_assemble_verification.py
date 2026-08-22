#!/usr/bin/env python3
"""Assemble QG25_GENERIC_VERIFICATION.json: verdict, determinism, tampers.

Validated through the committed `orion_research_harness.falsifiability` gate:
every case names the check that must catch it, and this refuses to write if any
case is caught by a different one.
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
VERIFIER = HERE / "qg25_generic_verify.py"
RECEIPT = REPO / "research" / "extensions" / "orion-qg" / "QG25_NO_SYNDROME_FAMILY_RESULTS.json"
ARTIFACT = HERE / "QG25_GENERIC_VERIFICATION.json"
sys.path.insert(0, str(REPO / "packages" / "orion-research-harness" / "src"))

from orion_research_harness.falsifiability import (  # noqa: E402
    validate_determinism, validate_falsifiability_demonstration,
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
    out = json.loads(p.stdout.split("QG25_GENERIC_VERIFY=")[0])
    return out["verdict"], out["failed_checks"], p.stdout


def t1(r):
    """Make the two witness words NOT permutations -- the argument's whole basis."""
    r["q1_abelian_syndrome_at_any_D"]["1"]["witness"]["word_b"] = ["H(0)", "H(0)"]
    return r


def t2(r):
    """Claim both words reach the same state, which would kill the witness."""
    w = r["q1_abelian_syndrome_at_any_D"]["1"]["witness"]
    w["state_b_paulis"] = list(w["state_a_paulis"])
    return r


def t3(r):
    """Claim both words prepare the target, so nothing is separated."""
    r["q1_abelian_syndrome_at_any_D"]["1"]["witness"]["word_b_prepares_target"] = True
    return r


def t4(r):
    """Inflate the counterexample family's configuration space."""
    r["counterexample_to_qg22s_stated_reason"]["rows"][1]["configuration_space"] = 64
    return r


def t5(r):
    """Claim the counterexample needs a growing syndrome, gutting its point."""
    r["counterexample_to_qg22s_stated_reason"]["rows"][2]["syndrome_dimension_D"] = 9
    return r


def t6(r):
    """Strip the verbatim passage from a donor record."""
    for rec in r["donor_search"]["records"]:
        if str(rec.get("verbatim_passage", "")).strip():
            rec["verbatim_passage"] = ""
            return r
    raise SystemExit("no donor record with a passage")


def t7(r):
    """Claim a passage was verified at document level, against the retrieval ceiling."""
    r["donor_search"]["records"][0]["document_level_verification"] = True
    if "document_level_verification" in r["donor_search"]:
        r["donor_search"]["document_level_verification"] = True
    return r


def t8(r):
    """Break a criterion digest so it no longer matches the frozen protocol text."""
    r["criterion_binding"]["records"][0]["frozen_criterion_digest"] = "0" * 64
    return r


def t9(r):
    """Soften the finding about QG-22 into agreement."""
    r["headline_findings_in_plain_words"]["2_does_qg22s_premise_stand"] = \
        "QG-22's premise stands, reason and all."
    return r


def t10(r):
    """Claim a hardness result the protocol forbids."""
    r["gates"]["G4_no_reduction_or_lower_bound_claimed"] = False
    return r


def t11(r):
    r["gates"]["G9_not_r6_protected_subject_unread_caps_disclosed"] = False
    return r


def t12(r):
    r["criterion_binding"]["records"][0].pop("applied_criterion_digest", None)
    return r


def t13(r):
    r["q1_abelian_syndrome_at_any_D"]["1"]["abelian_syndrome_exists_at_any_D"] = True
    return r


TAMPERS = [
    ("T1_witness_words_not_permutations",
     "the two witness words are edited so they are no longer permutations of each "
     "other, which is the entire basis of the abelian argument", t1),
    ("T2_witness_states_made_equal",
     "the two words are claimed to reach the same stabilizer state", t2),
    ("T3_both_words_prepare_the_target",
     "both words are claimed to prepare the target, separating nothing", t3),
    ("T4_counterexample_space_inflated",
     "the counterexample family's configuration space is inflated at n=2", t4),
    ("T5_counterexample_syndrome_made_to_grow",
     "the counterexample's syndrome dimension is made to grow with n, gutting it", t5),
    ("T6_donor_passage_stripped",
     "the verbatim passage is stripped from a donor record", t6),
    ("T7_document_level_verification_claimed",
     "a donor record claims document-level verification against the measured "
     "retrieval ceiling", t7),
    ("T8_criterion_digest_broken",
     "a criterion digest no longer matches the frozen protocol text", t8),
    ("T9_qg22_finding_softened",
     "the finding that QG-22 was right for a reason it did not give is softened "
     "into agreement", t9),
    ("T10_hardness_gate_flipped",
     "the gate forbidding a reduction or lower bound is flipped to false", t10),
    ("T11_authority_ceiling_dropped",
     "the NOT_R6 / protected-subject-unread gate is flipped to false", t11),
    ("T12_criterion_digest_removed",
     "a criterion record drops its applied digest, so sameness would be inferred "
     "from silence", t12),
    ("T13_abelian_syndrome_claimed_to_exist",
     "the receipt claims an abelian syndrome does exist, contradicting the very "
     "witness it carries", t13),
]

EXPECTED_CHECK = {
    "T1_witness_words_not_permutations": "witness_words_are_permutations_of_each_other",
    "T2_witness_states_made_equal": "witness_states_match_the_receipt",
    "T3_both_words_prepare_the_target": "exactly_one_word_prepares_the_target",
    "T4_counterexample_space_inflated": "counterexample_family_reproduces",
    "T5_counterexample_syndrome_made_to_grow": "counterexample_family_reproduces",
    "T6_donor_passage_stripped": "donor_records_validate_with_the_log_passed",
    "T7_document_level_verification_claimed": "document_level_verification_declared_false",
    "T8_criterion_digest_broken": "criterion_digests_match_the_frozen_protocol_text",
    "T9_qg22_finding_softened": "qg22_conclusion_stands_but_its_reason_does_not",
    "T10_hardness_gate_flipped": "no_hardness_or_reduction_claimed",
    "T11_authority_ceiling_dropped": "authority_ceiling_not_r6",
    "T12_criterion_digest_removed": "criterion_binding_records_bind_both_digests",
    "T13_abelian_syndrome_claimed_to_exist": "no_abelian_syndrome_claimed_at_any_D",
}

#: Checks no receipt tamper can exercise, each with its reason.
UNEXERCISED = [
    # resealed by construction, so a tampered copy never trips it
    "result_digest_recomputes",
    # no tamper edits the frozen protocol
    "protocol_sha256_recomputes",
    # this one is computed ENTIRELY by this verifier's own stabilizer simulation and
    # takes no input from the receipt, so no edit to the receipt can make it fail.
    # It is a self-check on the verifier, not a check on the lane, and saying so is
    # more honest than leaving it to look like receipt coverage.
    "witness_words_reach_different_states",
]


def _enforce(art: dict) -> None:
    broken = []
    if art["verdict"] != "ACCEPT" or art["failed_checks"]:
        broken.append(f"clean receipt did not ACCEPT: {art['failed_checks']}")
    try:
        validate_falsifiability_demonstration(
            art["falsifiability_demonstration"], EXPECTED_CHECK,
            all_checks=list(art["checks"].keys()),
            acknowledged_unexercised=UNEXERCISED)
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
    with tempfile.TemporaryDirectory(prefix="qg25-tamper-") as tmp:
        for name, desc, mutate in TAMPERS:
            p = pathlib.Path(tmp) / f"{name}.json"
            m = reseal(mutate(copy.deepcopy(receipt)))
            p.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
            body = {k: v for k, v in m.items() if k != "result_digest"}
            consistent = hashlib.sha256(canonical(body).encode()).hexdigest() == m["result_digest"]
            tv, tf, _ = run(p)
            cases.append({"case": name, "tamper": desc,
                          "result_digest_recomputed_so_copy_is_internally_self_consistent": consistent,
                          "verdict": tv, "failed_checks": tf})

    art = json.loads(out1.split("QG25_GENERIC_VERIFY=")[0])
    art["schema"] = "ORIONQG.QG25.GenericVerification.v1"
    art["verifier_sha256"] = hashlib.sha256(VERIFIER.read_bytes()).hexdigest()
    art["determinism"] = {"double_run": True, "stdout_identical": out1 == out2,
                          "run1_sha256": hashlib.sha256(out1.encode()).hexdigest(),
                          "run2_sha256": hashlib.sha256(out2.encode()).hexdigest()}
    art["falsifiability_demonstration"] = {
        "method": ("each tampered copy has its result_digest RECOMPUTED, so no hash "
                   "mismatch is available; every rejection comes from re-derivation"),
        "tamper_files_kept_outside_the_repository": True,
        "validated_through": "orion_research_harness.falsifiability",
        "all_tampered_copies_internally_self_consistent": all(
            c["result_digest_recomputed_so_copy_is_internally_self_consistent"] for c in cases),
        "all_tampered_copies_rejected": all(c["verdict"] == "REJECT" for c in cases),
        "expected_check_per_case": EXPECTED_CHECK,
        "cases": cases,
    }
    _enforce(art)
    ARTIFACT.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": art["verdict"], "failed_checks": art["failed_checks"],
                      "deterministic": art["determinism"]["stdout_identical"],
                      "tamper_verdicts": {c["case"]: c["verdict"] for c in cases}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
