#!/usr/bin/env python3
"""Assemble QG26_GENERIC_VERIFICATION.json: verdict, determinism (G8), tampers (G7).

Every tampered copy has its result_digest RECOMPUTED, so it is internally
self-consistent and no hash mismatch is available to the verifier; every rejection
has to come from re-derivation against the committed DP module.

The QG-24 regeneration taught the lesson this file is written against: a tamper case
must name the field it mutates. A case that finds its target heuristically, or that
mutates a field the verifier does not read, produces a demonstration that proves
nothing while looking exactly like one that proves something.
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
VERIFIER = HERE / "qg26_generic_verify.py"
RECEIPT = REPO / "research" / "extensions" / "orion-qg" / "QG26_NERODE_MINIMALITY_RESULTS.json"
ARTIFACT = HERE / "QG26_GENERIC_VERIFICATION.json"


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def reseal(r: dict) -> dict:
    body = {k: v for k, v in r.items() if k != "result_digest"}
    r["result_digest"] = hashlib.sha256(canonical(body).encode()).hexdigest()
    return r


def run(path: pathlib.Path) -> tuple[str, list[str], str]:
    proc = subprocess.run([sys.executable, str(VERIFIER), str(path)],
                          capture_output=True, text=True, cwd=str(REPO))
    out = json.loads(proc.stdout.split("QG26_GENERIC_VERIFY=")[0])
    return out["verdict"], out["failed_checks"], proc.stdout


def t1(r):
    r["terminal"] = "QG26_SYNDROME_IS_LOOSE__FACTOR_MEASURED"
    return r


def t2(r):
    """Rank understated, with the index and factor kept arithmetically coherent."""
    r["structural_method"]["gf2_rank_of_alphabet"] = 9
    r["structural_method"]["nerode_index"] = 512
    r["looseness_factor"] = 2
    return r


def t3(r):
    r["alphabet"]["letters"] = r["alphabet"]["letters"][:-1]
    r["alphabet"]["distinct_letters"] = len(r["alphabet"]["letters"])
    return r


def t4(r):
    r["mechanical_method"]["239"]["blocks"] = 512
    return r


def t5(r):
    r["looseness_factor"] = 2
    return r


def t6(r):
    r["g3_scope_statement"] = "the feasibility state space is minimal, so the DP is optimal"
    return r


def t7(r):
    r["novelty_authority"] = True
    return r


def t8(r):
    """Enumeration silently truncated but still declared complete."""
    r["alphabet"]["option_rows_enumerated"] = 4 ** 5
    return r


def t9(r):
    """Claim a criterion change and flip the verdict, coherently resealed.

    Until the verifier reimplemented the criterion-churn gate, this copy was
    ACCEPTed: the analyzer validated its own criterion_binding block in-run and
    nothing independent re-checked it, which is custody standing in for
    corroboration.
    """
    rec = r["criterion_binding"][0]
    rec["applied_criterion_digest"] = "0" * 64
    rec["reported_verdict"] = "FAIL"
    return r


def t10(r):
    """Drop applied_criterion_digest entirely -- omission must not read as sameness."""
    del r["criterion_binding"][0]["applied_criterion_digest"]
    return r


def t11(r):
    """Bind a frozen digest that is not the digest of the frozen protocol text."""
    r["criterion_binding"][0]["frozen_criterion_digest"] = "1" * 64
    return r


TAMPERS = [
    ("T1_terminal_flipped_to_loose",
     "the headline terminal is flipped to the opposite branch", t1),
    ("T2_rank_understated_coherently",
     "the GF(2) rank is lowered to 9 with the Nerode index and looseness factor "
     "adjusted to stay arithmetically consistent", t2),
    ("T3_alphabet_letter_removed",
     "one letter is dropped from the declared alphabet and the count adjusted", t3),
    ("T4_mechanical_block_count_altered",
     "the Moore refinement block count for target 239 is halved", t4),
    ("T5_looseness_factor_altered",
     "the looseness factor is set to 2 while rank and index stay correct", t5),
    ("T6_g3_scope_statement_replaced_by_a_speed_claim",
     "the gate-G3 scope statement is replaced with the speed claim G3 forbids", t6),
    ("T7_novelty_authority_granted",
     "novelty_authority is flipped to true", t7),
    ("T8_enumeration_truncated_but_declared_complete",
     "the enumerated option-row count is reduced to 4^5 while complete stays true", t8),
    ("T9_criterion_binding_block_incoherent",
     "the criterion_binding record claims a changed criterion and flips its verdict, "
     "with no deviation, counterfactual or exhibited rejection", t9),
    ("T10_applied_criterion_digest_removed",
     "applied_criterion_digest is deleted, so 'unchanged' would have to be inferred "
     "from silence", t10),
    ("T11_frozen_criterion_digest_does_not_match_the_protocol",
     "the bound frozen digest is not the digest of the criterion text in the frozen "
     "protocol", t11),
]



def _enforce(art: dict) -> None:
    """Refuse to write an artifact whose own gates did not hold.

    G7 requires the verifier be DEMONSTRATED capable of failing and G8 requires
    determinism. Both were computed and recorded here and neither was enforced:
    the artifact was written and the script exited 0 whenever the clean receipt
    was ACCEPT, so a demonstration in which some tamper was accepted could have
    landed as a successful verification receipt.

    That is not hypothetical. The first QG-24 regeneration in this session
    produced all_tampered_copies_rejected false -- T6 was ACCEPTed because the
    tamper mutated a field the verifier does not read -- and it wrote its
    artifact and exited 0. It was caught by a human reading the printed summary,
    which is exactly the kind of custody this programme keeps finding insufficient.
    Reported by Cursor Bugbot on PR #892.
    """
    fd = art["falsifiability_demonstration"]
    broken = []
    if art["verdict"] != "ACCEPT" or art["failed_checks"]:
        broken.append(f"clean receipt did not ACCEPT: {art['failed_checks']}")
    if not fd["all_tampered_copies_rejected"]:
        accepted = [c["case"] for c in fd["cases"] if c["verdict"] != "REJECT"]
        broken.append(f"G7: tampered copies not rejected: {accepted}")
    if not fd["all_tampered_copies_internally_self_consistent"]:
        broken.append("G7: some tampered copy was not resealed, so a hash mismatch "
                      "was available and its rejection proves nothing")
    if not art["determinism"]["stdout_identical"]:
        broken.append("G8: double run was not byte-identical")
    if broken:
        raise SystemExit(
            "refusing to write the verification artifact -- its own gates did not "
            "hold: " + "; ".join(broken)
        )


def main() -> int:
    receipt = json.loads(RECEIPT.read_text())
    verdict, failed, out1 = run(RECEIPT)
    _, _, out2 = run(RECEIPT)

    cases = []
    with tempfile.TemporaryDirectory(prefix="qg26-tamper-") as tmp:
        for name, description, mutate in TAMPERS:
            p = pathlib.Path(tmp) / f"{name}.json"
            m = reseal(mutate(copy.deepcopy(receipt)))
            p.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
            body = {k: v for k, v in m.items() if k != "result_digest"}
            consistent = hashlib.sha256(canonical(body).encode()).hexdigest() == m["result_digest"]
            tv, tf, _ = run(p)
            cases.append({
                "case": name,
                "tamper": description,
                "result_digest_recomputed_so_copy_is_internally_self_consistent": consistent,
                "verdict": tv,
                "failed_checks": tf,
            })

    art = json.loads(out1.split("QG26_GENERIC_VERIFY=")[0])
    art["schema"] = "ORIONQG.QG26.GenericVerification.v1"
    art["verifier_sha256"] = sha_file(VERIFIER)
    art["analyzer_sha256"] = sha_file(
        REPO / "research" / "extensions" / "orion-qg" / "qg26_nerode_minimality.py")
    art["determinism"] = {
        "double_run": True,
        "stdout_identical": out1 == out2,
        "run1_sha256": hashlib.sha256(out1.encode()).hexdigest(),
        "run2_sha256": hashlib.sha256(out2.encode()).hexdigest(),
    }
    art["falsifiability_demonstration"] = {
        "method": ("each tampered copy has its result_digest RECOMPUTED, so no hash "
                   "mismatch is available; every rejection comes from re-derivation "
                   "against the committed DP module"),
        "tamper_files_kept_outside_the_repository": True,
        "each_case_names_the_field_it_mutates": True,
        "all_tampered_copies_internally_self_consistent": all(
            c["result_digest_recomputed_so_copy_is_internally_self_consistent"] for c in cases),
        "all_tampered_copies_rejected": all(c["verdict"] == "REJECT" for c in cases),
        "cases": cases,
    }
    _enforce(art)
    ARTIFACT.write_text(json.dumps(art, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": art["verdict"],
        "failed_checks": art["failed_checks"],
        "deterministic": art["determinism"]["stdout_identical"],
        "all_tampered_rejected": art["falsifiability_demonstration"]["all_tampered_copies_rejected"],
        "tamper_verdicts": {c["case"]: c["verdict"] for c in cases},
    }, indent=1))
    return 0 if art["verdict"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
