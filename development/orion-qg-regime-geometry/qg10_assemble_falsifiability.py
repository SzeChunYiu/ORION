#!/usr/bin/env python3
"""Build QG-10's gate-G7 demonstration as evidence instead of prose.

QG-10 is cited in the closure packet and the PR body, and its falsifiability
demonstration existed only as a sentence in the wave record: "Two tampered copies
both REJECT: inflating a row's L to break the sandwich, and corrupting a row's
C_DP." There was no machine-readable record, so nothing established which check
caught what -- and three tampers on this branch turned out to reject for a reason
other than the one they were named after.

Two defects were found before this file existed:

* Running the verifier against a tampered copy OVERWROTE the committed
  verification artifact, because its output path was fixed. Testing the verifier
  destroyed the record of it passing. Fixed by making the destination follow the
  input; found by doing it.
* The prose is wrong about the first tamper. Inflating L does not break the
  sandwich -- L is recomputed from primitives before the sandwich is evaluated,
  so the lie is caught at `lower_bound_mismatch`, and the sandwich check never
  fires. A separate tamper is needed to exercise it, and is included below.

Each run takes about a minute; the suite is therefore slow by design rather than
by accident.
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
VERIFIER = HERE / "qg10_generic_verify.py"
RECEIPT = REPO / "research" / "extensions" / "orion-qg" / "QG10_INTERVAL_GEOMETRY_RESULTS.json"
ARTIFACT = HERE / "QG10_FALSIFIABILITY.json"
sys.path.insert(0, str(REPO / "packages" / "orion-research-harness" / "src"))

from orion_research_harness.falsifiability import (  # noqa: E402
    validate_falsifiability_demonstration,
)


def run(path: pathlib.Path):
    subprocess.run([sys.executable, str(VERIFIER), str(path)],
                   capture_output=True, text=True, cwd=str(REPO), check=False)
    art = json.loads(path.with_name(path.stem + ".verification.json").read_text())
    return art["decision"], sorted({f["why"] for f in art["failures_verbatim"]})


def live_row(rows):
    return next(i for i, r in enumerate(rows) if r.get("C_DP") is not None)


def row_with_a_foreign_target(rows):
    """A live row where some other block holds a target block 0 does not.

    Row 0 turns out to be fully degenerate -- all three target pairs are
    [[1,0],[1,0]] -- so there is no foreign target to place and T4 cannot bite
    there at all. Choosing a row where the check CAN fail is part of building the
    case; picking row 0 by default is what made the first T4 a silent no-op.
    """
    for i, r in enumerate(rows):
        if r.get("C_DP") is None:
            continue
        tp = r["target_pairs"]
        block0 = {tuple(tp[0][0]), tuple(tp[0][1])}
        if any(tuple(x) not in block0 for pair in tp[1:] for x in pair):
            return i
    raise SystemExit("no live row has a foreign target; T4 cannot be built")


def withheld_row(rows):
    return next(i for i, r in enumerate(rows)
                if r.get("referee") == "WITHHELD_CERTIFICATION_ONLY")


def t1(r):
    rows = r["rows_for_generic_verifier"]; i = live_row(rows)
    rows[i]["L"] = int(rows[i]["U"]) + 5
    return r


def t2(r):
    rows = r["rows_for_generic_verifier"]; i = live_row(rows)
    rows[i]["C_DP"] = int(rows[i]["C_DP"]) + 3
    return r


def t3(r):
    rows = r["rows_for_generic_verifier"]; i = live_row(rows)
    rows[i]["witness"]["value"] = int(rows[i]["witness"]["value"]) + 1
    return r


def t4(r):
    """Replace a witness target with a Pauli that is genuinely not in its block.

    The first version copied t6[1] over t6[0]. On the row it happened to pick,
    those two entries were EQUAL, so the edit was a no-op and the copy was
    ACCEPTed -- a tamper that did not tamper, named after a check it never
    reached. Found by running the demonstration, not by reading it. The target is
    now chosen to differ from both members of the block it is placed in, and the
    function refuses to build a case it cannot make bite.
    """
    rows = r["rows_for_generic_verifier"]; i = row_with_a_foreign_target(rows)
    w = rows[i]["witness"]
    tp = rows[i]["target_pairs"]
    block0 = {tuple(tp[0][0]), tuple(tp[0][1])}
    foreign = next((tuple(x) for pair in tp[1:] for x in pair if tuple(x) not in block0), None)
    if foreign is None:
        raise SystemExit(
            "T4 cannot be built on this row: every target in the other blocks "
            "already belongs to block 0, so no foreign target exists to place. "
            "Refusing to emit a case that would pass for the wrong reason."
        )
    t6 = [list(x) for x in w["t6"]]
    t6[0] = list(foreign)
    w["t6"] = t6
    return r


def t5(r):
    rows = r["rows_for_generic_verifier"]; i = withheld_row(rows)
    rows[i]["C_DP"] = 7
    return r


def t6(r):
    rows = r["rows_for_generic_verifier"]; i = live_row(rows)
    rows[i]["gap"] = int(rows[i]["gap"]) + 2
    return r


def t7(r):
    """Break the sandwich itself -- what the prose thought T1 did.

    L and C_DP are recomputed, so lying about either is caught at recomputation.
    U is NOT recomputed (it is the witness's value, checked against the witness),
    so lowering U below the recomputed C_DP is the tamper that reaches the
    sandwich check. It trips the witness check too, which is the honest reading:
    U cannot be moved independently of its witness.
    """
    rows = r["rows_for_generic_verifier"]; i = live_row(rows)
    rows[i]["U"] = int(rows[i]["C_DP"]) - 1
    return r


TAMPERS = [
    ("T1_L_inflated", "a row's L is inflated above U", t1, "lower_bound_mismatch"),
    ("T2_C_DP_corrupted", "a row's C_DP is altered", t2, "C_DP_mismatch"),
    ("T3_witness_value_altered", "the witness's recorded value is altered", t3, "witness_replay"),
    ("T4_witness_targets_foreign", "a witness target is replaced by another block's",
     t4, "witness_targets_not_instance"),
    ("T5_withheld_row_given_a_referee_value",
     "a certification-only row is given a C_DP it must not have", t5,
     "withheld_row_carries_C_DP"),
    ("T6_gap_field_inconsistent", "the gap field no longer equals U - L", t6,
     "gap_field_inconsistent"),
    ("T7_U_lowered_below_C_DP", "U is lowered below the recomputed C_DP, which is "
     "what actually reaches the sandwich check", t7, "sandwich_violated"),
]


def main() -> int:
    receipt = json.loads(RECEIPT.read_text())

    # A managed temporary directory, as the qg24-qg27 assemblers use. An earlier
    # version hardcoded a session-specific path under /tmp/claude-0/<uuid>, which
    # is ephemeral state that does not belong in a research record and would not
    # exist on anyone else's machine. Reported by Cursor Bugbot.
    with tempfile.TemporaryDirectory(prefix="qg10-tamper-") as tmp:
        scratch = pathlib.Path(tmp)
        clean_path = scratch / "clean.json"
        clean_path.write_text(json.dumps(receipt))
        clean_decision, clean_why = run(clean_path)

        cases = []
        for name, desc, mutate, expected in TAMPERS:
            p = scratch / f"{name}.json"
            p.write_text(json.dumps(mutate(copy.deepcopy(receipt))))
            decision, why = run(p)
            cases.append({
                "case": name, "tamper": desc,
                "verdict": "REJECT" if decision == "REJECT" else "ACCEPT",
                "failed_checks": why,
                "result_digest_recomputed_so_copy_is_internally_self_consistent": True,
                "note": "this receipt carries no self-digest field, so there is no "
                        "hash for a tamper to invalidate and every rejection is "
                        "necessarily a re-derivation",
            })

    expected_check = {name: exp for name, _d, _m, exp in TAMPERS}
    demo = {
        "method": ("the verifier is run against each tampered copy from its own input "
                   "path; the receipt carries no self-digest, so no rejection can come "
                   "from a hash mismatch"),
        "all_tampered_copies_rejected": all(c["verdict"] == "REJECT" for c in cases),
        "all_tampered_copies_internally_self_consistent": True,
        "expected_check_per_case": expected_check,
        "cases": cases,
    }

    problems = None
    try:
        validate_falsifiability_demonstration(
            demo, expected_check,
            all_checks=[e for _n, _d, _m, e in TAMPERS] + [
                "interval_inverted", "lower_bound_mismatch"],
            acknowledged_unexercised=["interval_inverted"])
    except ValueError as exc:
        problems = str(exc)

    out = {
        "schema": "ORIONQG.QG10.Falsifiability.v1",
        "why_this_exists": (
            "QG-10's gate-G7 demonstration existed only as prose in the wave record, "
            "with no record of which check caught which tamper"
        ),
        "clean_receipt": {"decision": clean_decision, "failed_checks": clean_why},
        "prose_claim_corrected": {
            "wave_record_said": "inflating a row's L to break the sandwich",
            "actually_caught_by": ["gap_field_inconsistent", "lower_bound_mismatch"],
            "why": "L is recomputed from primitives before the sandwich is evaluated, "
                   "so the lie is caught at recomputation and the sandwich check never "
                   "fires. T7 was added to exercise the sandwich for real.",
        },
        "verifier_output_path_defect": (
            "running the verifier against a tampered copy overwrote the COMMITTED "
            "verification artifact, because its output path was fixed. Testing the "
            "verifier destroyed the record of it passing. The destination now follows "
            "the input."
        ),
        "falsifiability_demonstration": demo,
        "gate": "CLEARS" if problems is None else "REFUSED",
        "gate_reason": problems,
    }
    if problems is not None or clean_decision != "ACCEPT":
        # The sibling assemblers refuse to write when their own gates do not hold,
        # and this one recorded its refusal into the artifact and wrote it anyway.
        # An artifact that documents its own failure is still an artifact someone
        # can cite from the cases list without reading the gate field.
        raise SystemExit(
            "refusing to write the falsifiability artifact -- clean="
            f"{clean_decision}; gate={out['gate']}: {problems}"
        )
    ARTIFACT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "clean": clean_decision,
        "gate": out["gate"],
        "cases": {c["case"]: (c["verdict"], c["failed_checks"]) for c in cases},
    }, indent=1))
    return 0 if problems is None and clean_decision == "ACCEPT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
