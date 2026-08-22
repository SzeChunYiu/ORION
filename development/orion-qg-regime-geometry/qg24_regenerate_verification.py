#!/usr/bin/env python3
"""Regenerate QG24_GENERIC_VERIFICATION.json against the verifier that is on disk now.

Why this exists
---------------

Commit `33138868` fixed a real defect in `qg24_generic_verify.py` -- a blockquote
strip written as `lstrip("> ")`, which takes its argument as a character set. The fix
was correct. What was not done is the consequence: the verification artifact had
already been written, and it kept asserting `verifier_sha256` for a file that no
longer had that hash. The verdict was unaffected, but the receipt bound a verifier
that no longer existed.

That is the receipt-churn hazard this programme documented and then committed anyway,
and re-labelling the hash by hand would be the same mistake with better manners: it
would assert that the determinism and tamper demonstrations still hold under the
changed verifier without re-running them. So this re-derives all three -- verdict,
double-run determinism, and the six tampered copies -- under the verifier as it
stands, and writes the artifact from what it measured.

The lane receipt `QG24_ROTATION_REGIME_RESULTS.json` is NOT touched (protocol gate G6).
Tampered copies are written to a temporary directory outside the repository and
deleted; each has its `result_digest` recomputed so no hash mismatch is available and
every rejection must come from re-derivation.
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
VERIFIER = HERE / "qg24_generic_verify.py"
RECEIPT = REPO / "research" / "extensions" / "orion-qg" / "QG24_ROTATION_REGIME_RESULTS.json"
ARTIFACT = HERE / "QG24_GENERIC_VERIFICATION.json"


def sha_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def reseal(receipt: dict) -> dict:
    """Recompute result_digest so a tampered copy is internally self-consistent."""
    body = {k: v for k, v in receipt.items() if k != "result_digest"}
    receipt["result_digest"] = hashlib.sha256(canonical(body).encode()).hexdigest()
    return receipt


def run_verifier(path: pathlib.Path) -> tuple[str, list[str], str]:
    proc = subprocess.run(
        [sys.executable, str(VERIFIER), str(path)],
        capture_output=True, text=True, cwd=str(REPO),
    )
    stdout = proc.stdout
    body = stdout.split("QG24_GENERIC_VERIFY=")[0]
    out = json.loads(body)
    return out["verdict"], out["failed_checks"], stdout


# --- the six tampers, each described exactly as the artifact describes it ------

def t1_ceiling_flipped(r):
    r["q1_ceiling_verdict"] = "CEILING_IS_STRUCTURAL"
    r["terminal"] = "QG24_CEILING_IS_STRUCTURAL__ROTATION_COUNT_INVARIANT_IN_THE_GRAMMAR"
    return r


def t2_n1_distribution_shifted(r):
    block = r["q1_distribution"]["1"]["per_model"]["R6L_RESTORE_IN_PLACE"]["distribution_reduced"]
    block["9"] = int(block["9"]) - 4096
    block["7"] = int(block["7"]) + 4096
    return r


def t3_panel_cost_understated(r):
    for row in r["panel"]:
        if row.get("seven_rotation_min_clifford_factored") is not None:
            row["seven_rotation_min_clifford_factored"] = int(
                row["seven_rotation_min_clifford_factored"]) - 3
            if row.get("clifford_price_factored") is not None:
                row["clifford_price_factored"] = int(row["clifford_price_factored"]) - 3
            return r
    raise SystemExit("T3: no factored panel row to understate")


def t4_subsuming_passage_removed(r):
    for rec in r["donor_search"]["records"]:
        if rec.get("verdict") == "SUBSUMED" and str(rec.get("verbatim_passage", "")).strip():
            rec["verbatim_passage"] = ""
            return r
    raise SystemExit("T4: no SUBSUMED record with a passage")


def t5_forecast_tally_altered(r):
    """Alter exactly the field the verifier reads.

    An earlier draft searched for any key containing "hit". It happened to land
    on the right one, but a tamper case that finds its target heuristically is
    not a demonstration of anything -- it proves the verifier rejects whatever
    the search happened to hit. The field is named here.
    """
    fc = r["q2_regime"]["prospective_forecast"]
    fc["hits"] = int(fc["hits"]) + 1
    return r


def t6_g4_staging_violated(r):
    """Admit three stage-1 referee calls, consistently.

    The receipt carries this count in two places. An earlier draft set only
    `stage1.referee_calls_during_stage1`, which the verifier does not read, and
    the copy was ACCEPTed -- the reconstruction was wrong, not the verifier.
    Both are set here, which is the harder case: a lie with no internal
    inconsistency for the verifier to notice.
    """
    r["stage1"]["referee_calls_during_stage1"] = 3
    r["q2_regime"]["prospective_forecast"]["referee_calls_during_stage1"] = 3
    return r


TAMPERS = [
    ("T1_ceiling_flipped_to_structural",
     "the headline verdict is flipped to the opposite terminal", t1_ceiling_flipped),
    ("T2_n1_distribution_shifted",
     "4096 configurations moved from nine rotations to seven at n=1", t2_n1_distribution_shifted),
    ("T3_panel_cost_understated",
     "one panel row's seven-rotation Clifford cost lowered by three, with its price kept "
     "arithmetically consistent", t3_panel_cost_understated),
    ("T4_subsuming_passage_removed",
     "the verbatim passage is stripped from a SUBSUMED donor record", t4_subsuming_passage_removed),
    ("T5_forecast_tally_altered",
     "the prospective-forecast hit count is altered", t5_forecast_tally_altered),
    ("T6_g4_staging_violated",
     "the receipt admits three referee calls during stage 1", t6_g4_staging_violated),
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

    verdict, failed, stdout1 = run_verifier(RECEIPT)
    _, _, stdout2 = run_verifier(RECEIPT)
    determinism = {
        "double_run": True,
        "stdout_identical": stdout1 == stdout2,
        "run1_sha256": hashlib.sha256(stdout1.encode()).hexdigest(),
        "run2_sha256": hashlib.sha256(stdout2.encode()).hexdigest(),
        "note": "verifier stdout is the compared object; it carries no timing field",
    }

    cases = []
    with tempfile.TemporaryDirectory(prefix="qg24-tamper-") as tmp:
        for name, description, mutate in TAMPERS:
            copy_path = pathlib.Path(tmp) / f"{name}.json"
            mutated = reseal(mutate(copy.deepcopy(receipt)))
            copy_path.write_text(json.dumps(mutated, indent=1, sort_keys=True) + "\n")
            body = {k: v for k, v in mutated.items() if k != "result_digest"}
            self_consistent = (
                hashlib.sha256(canonical(body).encode()).hexdigest() == mutated["result_digest"]
            )
            tverdict, tfailed, _ = run_verifier(copy_path)
            cases.append({
                "case": name,
                "tamper": description,
                "result_digest_recomputed_so_copy_is_internally_self_consistent": self_consistent,
                "verdict": tverdict,
                "failed_checks": tfailed,
            })

    out = json.loads(stdout1.split("QG24_GENERIC_VERIFY=")[0])
    out["verifier_sha256"] = sha_file(VERIFIER)
    out["determinism"] = determinism
    out["falsifiability_demonstration"] = {
        "method": (
            "each tampered copy is an edit to the receipt with its result_digest "
            "RECOMPUTED, so the copy is internally self-consistent and no hash mismatch "
            "is available to the verifier; every rejection below comes from "
            "re-derivation from primitives"
        ),
        "tamper_files_kept_outside_the_repository": True,
        "all_tampered_copies_internally_self_consistent": all(
            c["result_digest_recomputed_so_copy_is_internally_self_consistent"] for c in cases),
        "all_tampered_copies_rejected": all(c["verdict"] == "REJECT" for c in cases),
        "cases": cases,
    }
    out["schema"] = "ORIONQG.QG24.GenericVerification.v1"
    out["regeneration_note"] = (
        "regenerated after commit 33138868 changed the verifier; the previous artifact "
        "bound a verifier_sha256 the file on disk no longer had. Verdict, determinism "
        "and all six tamper cases were re-derived under the current verifier rather "
        "than carried forward. The lane receipt is untouched (gate G6): its "
        "results_sha256 is unchanged."
    )
    _enforce(out)
    ARTIFACT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": out["verdict"],
        "failed_checks": out["failed_checks"],
        "verifier_sha256": out["verifier_sha256"],
        "results_sha256": out["results_sha256"],
        "all_tampered_rejected": out["falsifiability_demonstration"]["all_tampered_copies_rejected"],
        "tamper_verdicts": {c["case"]: c["verdict"] for c in cases},
        "deterministic": determinism["stdout_identical"],
    }, indent=1))
    return 0 if out["verdict"] == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
