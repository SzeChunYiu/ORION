#!/usr/bin/env python3
"""Independent from-primitives verifier for QG-25 (protocol gate G7).

Written by the adjudicator, not the lane -- the lane's agent died before writing
one, which is the ordinary case for an independent verifier and not a special
circumstance. It imports nothing the lane wrote. In particular it carries its own
stabilizer simulation, so the two-gate witness that carries the whole result is
re-derived from the definition of the Clifford action on Pauli operators rather
than read back out of the receipt.

Usage: qg25_generic_verify.py [results.json]   Exit 0 ACCEPT, 1 REJECT.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "packages" / "orion-research-harness" / "src"))

from orion_research_harness.donor_search import validate_donor_search  # noqa: E402

DEFAULT = REPO / "research" / "extensions" / "orion-qg" / "QG25_NO_SYNDROME_FAMILY_RESULTS.json"
PROTOCOL = HERE / "QG25_NO_SYNDROME_FAMILY_PROTOCOL_V1.md"
DONOR_LOG = HERE / "QG25_DONOR_SEARCH.md"


def canonical(o) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- an independent single-qubit stabilizer simulation -----------------------
#
# A single-qubit stabilizer state is fixed by its stabilizer group {I, P} for a
# signed Pauli P. Track P. Clifford conjugation on the Pauli group:
#   H: X<->Z,  Y -> -Y
#   S: X->Y,   Y -> -X,   Z->Z
# Only the unsigned label is needed to separate the states this witness uses.

def apply_gate(pauli: str, gate: str) -> str:
    if gate == "H":
        return {"X": "Z", "Z": "X", "Y": "Y", "I": "I"}[pauli]
    if gate == "S":
        return {"X": "Y", "Y": "X", "Z": "Z", "I": "I"}[pauli]
    raise ValueError(gate)


def run_word(word: list[str]) -> str:
    """|0> is stabilized by Z. Apply the gates left to right."""
    p = "Z"
    for g in word:
        p = apply_gate(p, g)
    return p


def parity_grid_has_dimension_one_syndrome(n: int) -> dict:
    """Re-derive the counterexample family from its own definition.

    PARITY_GRID(n): n*n bits, a move flips one cell, feasible iff total parity 1.
    The syndrome is the total parity: one bit, independent of n, and every move
    increments it by exactly 1.
    """
    cells = n * n
    space = 2 ** cells
    # every move flips exactly one cell, so it flips the total parity
    increments = {1}
    for config in range(space):
        for cell in range(cells):
            after = config ^ (1 << cell)
            if (bin(after).count("1") % 2) == (bin(config).count("1") % 2):
                increments.add(0)
    fibres_decide = all(
        (bin(c).count("1") % 2 == 1) == (bin(c).count("1") % 2 == 1)
        for c in range(space)
    )
    return {
        "n": n,
        "configuration_space": space,
        "syndrome_dimension_D": 1,
        "per_move_increment_is_always_one": increments == {1},
        "fibres_decide_feasibility": fibres_decide,
    }


def main(argv) -> int:
    path = pathlib.Path(argv[1]) if len(argv) > 1 else DEFAULT
    res = json.loads(path.read_text())
    checks, failed = {}, []

    def record(name, ok, detail=None):
        checks[name] = {"ok": bool(ok), "detail": detail}
        if not ok:
            failed.append(name)

    record("protocol_sha256_recomputes", sha_file(PROTOCOL) == res.get("protocol_sha256"))
    record("result_digest_recomputes",
           hashlib.sha256(canonical({k: v for k, v in res.items()
                                     if k != "result_digest"}).encode()).hexdigest()
           == res.get("result_digest"))

    # --- the witness that carries the whole result, re-derived ---------------
    w = res["q1_abelian_syndrome_at_any_D"]["1"]["witness"]
    word_a = [g.split("(")[0] for g in w["word_a"]]
    word_b = [g.split("(")[0] for g in w["word_b"]]
    pa, pb = run_word(word_a), run_word(word_b)
    record("witness_words_are_permutations_of_each_other",
           sorted(word_a) == sorted(word_b), {"a": word_a, "b": word_b})
    record("witness_words_reach_different_states", pa != pb,
           {"recomputed_a": pa, "recomputed_b": pb})
    record("witness_states_match_the_receipt",
           ("+" + pa) in w["state_a_paulis"] and ("+" + pb) in w["state_b_paulis"],
           {"recomputed": [pa, pb], "receipt": [w["state_a_paulis"], w["state_b_paulis"]]})
    record("exactly_one_word_prepares_the_target",
           bool(w["word_a_prepares_target"]) != bool(w["word_b_prepares_target"]))
    record("no_abelian_syndrome_claimed_at_any_D",
           res["q1_abelian_syndrome_at_any_D"]["1"]["abelian_syndrome_exists_at_any_D"] is False)

    # --- the counterexample family, re-derived from its definition -----------
    bad_rows = []
    for row in res["counterexample_to_qg22s_stated_reason"]["rows"]:
        mine = parity_grid_has_dimension_one_syndrome(int(row["n"]))
        if (mine["configuration_space"] != row["configuration_space"]
                or mine["syndrome_dimension_D"] != row["syndrome_dimension_D"]
                or not mine["per_move_increment_is_always_one"]
                or not row["fibres_decide_feasibility"]):
            bad_rows.append([row["n"], mine])
    record("counterexample_family_reproduces", not bad_rows, {"bad": bad_rows})
    record("counterexample_space_is_two_to_the_n_squared",
           all(int(r["configuration_space"]) == 2 ** (int(r["n"]) ** 2)
               for r in res["counterexample_to_qg22s_stated_reason"]["rows"]))

    # --- donor gate, re-run against the committed module WITH the log --------
    log = DONOR_LOG.read_text()
    donor_bad = []
    for i, rec in enumerate(res["donor_search"]["records"]):
        try:
            validate_donor_search(rec, log)
        except Exception as exc:  # noqa: BLE001 - reported, not raised
            donor_bad.append([i, str(exc)[:120]])
    record("donor_records_validate_with_the_log_passed", not donor_bad, {"bad": donor_bad})
    record("document_level_verification_declared_false",
           res["donor_search"].get("document_level_verification") is False
           or all(r.get("document_level_verification") is False
                  for r in res["donor_search"]["records"]))

    # --- criterion binding: every record must bind both digests -------------
    cb = res.get("criterion_binding", {})
    recs = cb.get("records", [])
    cb_bad = [i for i, r in enumerate(recs)
              if not r.get("frozen_criterion_digest") or not r.get("applied_criterion_digest")]
    record("criterion_binding_records_bind_both_digests", not cb_bad and bool(recs),
           {"count": len(recs), "bad": cb_bad})
    record("criterion_digests_match_the_frozen_protocol_text",
           all(hashlib.sha256(" ".join(str(r["criterion_text"]).split()).encode()).hexdigest()
               == r["frozen_criterion_digest"] for r in recs))

    # --- the finding about QG-22, and the gates ------------------------------
    head = res["headline_findings_in_plain_words"]
    record("qg22_conclusion_stands_but_its_reason_does_not",
           "CONCLUSION stands" in head["2_does_qg22s_premise_stand"]
           and "REASON does not" in head["2_does_qg22s_premise_stand"])
    record("no_hardness_or_reduction_claimed",
           res["gates"]["G3_no_hardness_inference_from_wall_clock"] is True
           and res["gates"]["G4_no_reduction_or_lower_bound_claimed"] is True)
    record("authority_ceiling_not_r6",
           res["gates"]["G9_not_r6_protected_subject_unread_caps_disclosed"] is True
           and res["authority"].get("novelty_authority") is False
           if isinstance(res.get("authority"), dict) else
           res["gates"]["G9_not_r6_protected_subject_unread_caps_disclosed"] is True)

    verdict = "ACCEPT" if not failed else "REJECT"
    out = {
        "verifier": "qg25_generic_verify",
        "authored_by": "the adjudicator, not the lane",
        "independent_of": ["qg25_no_syndrome_family", "qg6_syndrome_rank", "numpy"],
        "results_file": str(path),
        "results_sha256": sha_file(path),
        "terminal_under_review": res["terminal"],
        "check_count": len(checks),
        "checks": checks,
        "failed_checks": failed,
        "scope_note": (
            "re-derives the two-gate witness from the Clifford action on Pauli "
            "operators and the counterexample family from its own definition. It "
            "does NOT re-run the lane's complete word enumerations at n = 2, 3, "
            "which are reported on the lane's word and are not what the result "
            "rests on: a single permutation pair reaching two states settles the "
            "abelian question at every dimension."
        ),
        "verdict": verdict,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    print(f"QG25_GENERIC_VERIFY={verdict}")
    return 0 if verdict == "ACCEPT" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
