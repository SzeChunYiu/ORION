#!/usr/bin/env python3
"""Assemble QG-28's verification record: G7 falsifiability and G8 determinism.

Runs the independent verifier on the real receipt, then on tampered copies whose
digests are recomputed so that no rejection can come from a hash mismatch. Every
case binds the check it is aimed at, and the committed
``orion_research_harness.falsifiability`` gate refuses the demonstration if a
copy is accepted, if a copy is caught by a check other than the one it targets,
or if any of the verifier's checks is left unexercised without being named.

This script REFUSES TO WRITE when the demonstration does not hold. Both of the
wave-3 assemblers recorded G7 and G8 and enforced neither, and that had already
cost this branch one artifact written with ``all_tampered_copies_rejected:
false`` sitting inside it.
"""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_HARNESS_SRC = ROOT / "packages/orion-research-harness/src"

import qg28_generic_verify as gv  # noqa: E402


def _import_harness(module: str):
    import importlib
    import types

    name = "orion_research_harness"
    if name not in sys.modules:
        pkg = types.ModuleType(name)
        pkg.__path__ = [str(_HARNESS_SRC / name)]
        sys.modules[name] = pkg
    if str(_HARNESS_SRC) not in sys.path:
        sys.path.insert(0, str(_HARNESS_SRC))
    return importlib.import_module(name + "." + module)


fals = _import_harness("falsifiability")

RESULTS = ROOT / "research/extensions/orion-qg/QG28_SUPPORT_CAPPED_REALIZATION_RESULTS.json"
LANE = ROOT / "research/extensions/orion-qg/qg28_support_capped_realization.py"
OUT = ROOT / "development/orion-qg-regime-geometry/QG28_GENERIC_VERIFICATION.json"

#: Checks no resealed tamper can exercise, each with the reason it cannot.
#: A false exemption here is worse than no exemption -- QG-25 used this very
#: mechanism to hide a real gap, and the note was struck rather than deleted.
UNEXERCISED: dict[str, str] = {
    "content_digest_recomputes": (
        "every tampered copy is resealed on purpose, so this check passes on all "
        "of them; a copy that could exercise it would be rejected on the hash and "
        "would demonstrate nothing about re-derivation"
    ),
    "protocol_carries_the_same_disclosure": (
        "reads the committed protocol file and nothing from the receipt, so no "
        "edit to a receipt copy can move it"
    ),
    "tag_dp_equals_tag_sweep_under_this_verifier": (
        "the verifier runs its own DP against its own 4^n sweep and reads nothing "
        "from the receipt, so no receipt edit can move it"
    ),
    "definitional_brute_force_agrees_on_declared_n1_sample": (
        "the verifier brute-forces C_D++ from the frozen family definition and "
        "compares against dxx_search directly; it reads nothing from the receipt"
    ),
}


def reseal(rec: dict[str, Any]) -> dict[str, Any]:
    body = {k: v for k, v in rec.items()
            if k not in ("content_digest", "timings_excluded_from_digest",
                         "total_seconds")}
    rec["content_digest"] = hashlib.sha256(
        gv.canonical(body).encode()
    ).hexdigest()
    return rec


def _domain(rec: dict[str, Any], letter: str) -> dict[str, Any]:
    for d in rec["domains"]:
        if str(d.get("domain", "")).startswith(letter):
            return d
    raise KeyError(f"domain {letter} not present")


def t_protocol_digest(r):
    r["protocol_digest"] = "0" * 64


def t_q1_claimed_prospective(r):
    r["prospective_status"]["q1_build_the_capped_search"] = True


def t_q3_not_prospective(r):
    r["prospective_status"]["q3_cell_model_and_crossover"] = False


def t_disclosure_removed(r):
    r["prospective_status"]["disclosure"] = ""


def t_pair_count(r):
    r["frame_pair_counts"]["3"] = 665


def t_ladder_row(r):
    r["q3_cell_model"]["ladder"][6]["N_cap"] *= 2


def t_crossover(r):
    row = r["q3_cell_model"]
    row["crossover_n"] = (row["crossover_n"] or 0) + 1


def t_tag_claim(r):
    r["tag_dp_vs_sweep"]["2"]["disagreement_count"] = 3
    r["tag_dp_vs_sweep"]["2"]["dp_reproduces_sweep"] = True


def t_domain_a_size(r):
    d = _domain(r, "A")
    d["instances"] = 4095
    d["agree"] = 4095
    r["total_instances_compared"] -= 1


def t_domain_b_incomplete(r):
    _domain(r, "B")["complete_enumeration"] = False


def t_domain_d_claims_enumeration(r):
    _domain(r, "D")["complete_enumeration"] = True


def t_agree_flag(r):
    d = _domain(r, "B")
    d["agree"] = int(d["agree"]) - 1


def t_mismatch_hidden(r):
    _domain(r, "A")["mismatch_count"] = 2


def t_all_domains_agree(r):
    r["all_domains_agree"] = not r["all_domains_agree"]


def t_terminal(r):
    r["terminal"] = "QG28_COROLLARY_REALIZED__NO_WIN_AT_ANY_N"


def t_novelty(r):
    r["novelty_authority"] = True


def t_donor_record(r):
    r["donor_search_records"][1]["asserts_novelty"] = True


def t_panel_row(r):
    _domain(r, "C")["rows"][0]["C_capped"] += 1
    _domain(r, "C")["rows"][0]["agree"] = True


def t_dp_crossover(r):
    q = r["q3_cell_model"]
    q["crossover_n_dp_variant"] = (q["crossover_n_dp_variant"] or 0) - 1


def t_dp_ladder_row(r):
    r["q3_cell_model"]["ladder"][8]["N_cap_dp"] += 1


def t_amendment_undisclosed(r):
    r["q3_cell_model"]["counting_rule_amendment"][
        "added_after_the_protocol_was_frozen"] = False


def t_dp_row_agree_flag(r):
    r["dp_driven_search"]["rows"][0]["agree"] = False


def t_dp_row_value(r):
    r["dp_driven_search"]["rows"][1]["C_dp_driven"] += 1
    r["dp_driven_search"]["rows"][1]["agree"] = True


def t_dp_search_n1_only(r):
    d = r["dp_driven_search"]
    d["rows"] = [x for x in d["rows"] if int(x.get("n", 1)) == 1]
    d["instances"] = len(d["rows"])
    d["agree"] = sum(1 for x in d["rows"] if x["agree"])


def t_dp_scope_removed(r):
    r["dp_driven_search"]["declared_scope_and_obstacle"] = ""


def t_section_33_deviation_hidden(r):
    r["deviation_from_protocol_section_3_3"]["what_licenses_the_claim_anyway"] = ""


def t_dp_sample_disagrees_but_win_kept(r):
    d = r["dp_driven_search"]
    d["rows"][2]["agree"] = False
    d["all_agree"] = False
    d["agree"] = sum(1 for x in d["rows"] if x["agree"])


def t_dp_n2_row_fabricated(r):
    for row in r["dp_driven_search"]["rows"]:
        if int(row.get("n", 0)) == 2:
            for k in ("C_dp_driven", "C_table_driven", "C_Dxx"):
                row[k] = int(row[k]) + 1
            return
    raise AssertionError("no n=2 row to fabricate")


def t_licensing_counts_inflated(r):
    lic = r["deviation_from_protocol_section_3_3"]["what_licenses_the_claim_anyway"]
    lic["instances_agreeing"] = int(lic["instances_agreeing"]) + 3


def t_licensing_soft_reverted_to_prose(r):
    """The field's previous shape. A non-empty string is truthy, so an `or {}`
    guard never fires and `.get` raises -- the verifier aborted instead of
    REJECTing, which is a fail-closed gate failing open. The existing
    `T18e` tamper set the field to "", which IS falsy, so the suite passed
    while the crash path stayed untested. Reported by Cursor Bugbot on 37903dfd.
    """
    r["deviation_from_protocol_section_3_3"]["what_licenses_the_claim_anyway"] = (
        "dp_driven_search above runs the section-3.3 algorithm literally on a "
        "declared sample and gets the same C_D++"
    )


def t_wall_clock_put_back_under_the_digest(r):
    r["q3_cell_model"]["wall_clock_corroboration"] = {
        "1": {"capped_seconds_per_instance": 0.00124}}


def t_model_ratio_altered(r):
    r["q3_cell_model"]["model_ratio_by_n"]["3"] = 1.0


def t_wall_clock_status(r):
    r["q3_cell_model"]["wall_clock_status"] = ""


def t_total_instances(r):
    r["total_instances_compared"] = int(r["total_instances_compared"]) + 7


#: case name -> (mutation, the check it exists to exercise)
TAMPERS: dict[str, tuple[Callable[[dict], None], str]] = {
    "T1_protocol_digest_swapped": (
        t_protocol_digest, "protocol_digest_matches_committed_protocol"),
    "T2_q1_relabelled_prospective": (
        t_q1_claimed_prospective, "q1_and_q2_declared_not_prospective"),
    "T3_q3_relabelled_retrospective": (
        t_q3_not_prospective, "q3_declared_prospective"),
    "T4_scouting_disclosure_removed": (
        t_disclosure_removed, "scouting_disclosure_present"),
    "T5_frame_pair_count_altered": (t_pair_count, "frame_pair_counts_rederived"),
    "T6_cell_model_row_altered": (t_ladder_row, "cell_model_rows_rederived"),
    "T7_crossover_moved": (t_crossover, "crossover_rederived"),
    "T8_tag_claim_contradicts_its_own_count": (
        t_tag_claim, "tag_dp_claims_are_internally_consistent"),
    "T9_domain_a_shortened": (t_domain_a_size, "domain_a_is_the_complete_4096"),
    "T10_domain_b_marked_incomplete": (
        t_domain_b_incomplete, "domain_b_is_the_complete_9261"),
    "T11_sample_presented_as_enumeration": (
        t_domain_d_claims_enumeration,
        "domain_d_is_declared_a_sample_not_an_enumeration"),
    "T12_agree_count_lowered_flag_left_true": (
        t_agree_flag, "every_domain_agree_flag_matches_its_own_counts"),
    "T13_mismatches_carried_under_an_agreement_claim": (
        t_mismatch_hidden, "no_domain_claims_agreement_while_carrying_mismatches"),
    "T14_top_level_agreement_flipped": (
        t_all_domains_agree, "all_domains_agree_matches_the_domains"),
    "T15_terminal_swapped": (t_terminal, "terminal_follows_from_the_measurements"),
    "T16_novelty_authority_asserted": (t_novelty, "not_r6_and_no_novelty_asserted"),
    "T17_donor_record_asserts_novelty": (
        t_donor_record, "donor_records_assert_no_novelty"),
    "T18_hostile_panel_value_altered": (t_panel_row, "hostile_panel_rows_recomputed"),
    "T19a_dp_variant_crossover_moved": (
        t_dp_crossover, "dp_variant_crossover_rederived"),
    "T19b_dp_variant_cell_count_altered": (
        t_dp_ladder_row, "cell_model_rows_rederived"),
    "T19c_amendment_hidden": (
        t_amendment_undisclosed, "counting_rule_amendment_discloses_itself"),
    "T18a_dp_row_marked_disagreeing_flag_left_true": (
        t_dp_row_agree_flag, "dp_driven_search_flag_matches_its_rows"),
    "T18b_dp_driven_value_altered": (
        t_dp_row_value, "dp_driven_search_rows_recomputed"),
    "T18c_dp_demonstration_reduced_to_n1": (
        t_dp_search_n1_only, "dp_driven_search_is_not_n1_only"),
    "T18d_dp_scope_statement_removed": (
        t_dp_scope_removed, "dp_driven_search_declares_its_scope"),
    "T18e_section_3_3_deviation_hidden": (
        t_section_33_deviation_hidden, "section_3_3_deviation_disclosed"),
    "T18f_dp_sample_disagrees_but_win_terminal_kept": (
        t_dp_sample_disagrees_but_win_kept,
        "dp_disagreement_would_move_the_terminal"),
    "T18g_dp_n2_row_fabricated": (
        t_dp_n2_row_fabricated, "dp_driven_n2_rows_recomputed"),
    "T18h_licensing_counts_inflated": (
        t_licensing_counts_inflated, "licensing_record_matches_the_dp_rows"),
    "T18i_licensing_soft_reverted_to_prose": (
        t_licensing_soft_reverted_to_prose, "section_3_3_deviation_disclosed"),
    "T19a_measured_wall_clock_returned_to_the_digest": (
        t_wall_clock_put_back_under_the_digest,
        "measured_wall_clock_is_not_under_digest_custody"),
    "T19b_model_ratio_altered": (t_model_ratio_altered, "model_ratios_rederived"),
    "T19_wall_clock_caveat_removed": (
        t_wall_clock_status, "gate_g3_wall_clock_carries_no_argument"),
    "T20_instance_total_inflated": (
        t_total_instances, "total_instances_is_the_sum_of_the_domains"),
}


def _run_lane() -> tuple[str, dict[str, Any]]:
    """Run the lane and return its stdout together with the receipt it wrote."""
    proc = subprocess.run(
        [sys.executable, str(LANE)], capture_output=True, text=True,
        cwd=str(ROOT), check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"lane run failed: {proc.stderr[-2000:]}")
    return proc.stdout, json.loads(RESULTS.read_text())


def main() -> int:
    # G8 wants a double run, so this script owns both of them. Reading a receipt
    # somebody else left on disk and calling the re-run "the second" leaves the
    # first run's stdout in nobody's hands, which is how `stdout_identical` came
    # to be a hardcoded True in the version Cursor Bugbot reviewed.
    stdout_a, base = _run_lane()

    live = gv.verify(RESULTS)
    if live["verdict"] != "ACCEPT":
        raise SystemExit(
            "the verifier REJECTS the real receipt on "
            f"{live['failed_checks']}; nothing downstream may be assembled"
        )

    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        for name, (mutate, expected) in TAMPERS.items():
            rec = copy.deepcopy(base)
            mutate(rec)
            reseal(rec)
            path = tmpdir / f"{name}.json"
            path.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
            out = gv.verify(path)
            cases.append({
                "case": name,
                "expected_check": expected,
                "verdict": out["verdict"],
                "failed_checks": out["failed_checks"],
                "result_digest_recomputed_so_copy_is_internally_self_consistent": True,
            })

    demonstration = {
        "verifier": "development/orion-qg-regime-geometry/qg28_generic_verify.py",
        "cases": cases,
        "all_tampered_copies_rejected": all(c["verdict"] == "REJECT" for c in cases),
        "unexercised_checks_and_why": UNEXERCISED,
    }

    # The gate, not a note about the gate. If this raises, nothing is written.
    fals.validate_falsifiability_demonstration(
        demonstration,
        {name: exp for name, (_, exp) in TAMPERS.items()},
        require_resealed=True,
        all_checks=sorted(live["checks"]),
        acknowledged_unexercised=sorted(UNEXERCISED),
    )

    # G8 -- determinism. Both runs belong to this script, so `stdout_identical`
    # is a measurement rather than a claim: the two stdouts are compared byte for
    # byte. The lane prints no wall-clock, precisely so that this comparison is
    # meaningful instead of guaranteed to fail.
    stdout_b, again = _run_lane()
    stripped = [
        {k: v for k, v in r.items()
         if k not in ("timings_excluded_from_digest", "total_seconds")}
        for r in (base, again)
    ]
    determinism = {
        "double_run": True,
        "stdout_identical": stdout_a == stdout_b,
        "stdout_bytes_compared": len(stdout_a.encode()),
        "content_digest_identical": base["content_digest"] == again["content_digest"],
        "all_digest_covered_fields_identical": stripped[0] == stripped[1],
        "excluded_fields": ["timings_excluded_from_digest", "total_seconds"],
        "how_stdout_was_obtained": (
            "both runs were launched by this script with captured stdout and "
            "compared byte for byte; neither flag is asserted"
        ),
    }
    if not (determinism["content_digest_identical"]
            and determinism["all_digest_covered_fields_identical"]):
        raise SystemExit(
            "the second run does not reproduce the first outside timing; G8 fails "
            "and this record must not be written\n"
            f"digest a={base['content_digest'][:12]} b={again['content_digest'][:12]}"
        )
    # Raises when stdout_identical is False, which is now a thing that can happen.
    fals.validate_determinism(determinism)

    record = {
        "schema": "ORIONQG.QG28.GenericVerification.v1",
        "lane": "QG-28",
        "residual": "W9",
        "verification": live,
        "falsifiability_demonstration": demonstration,
        "determinism": determinism,
        "gates": {
            "G7_verifier_demonstrated_capable_of_failing": True,
            "G7_every_case_rejected_by_the_check_it_targets": True,
            "G7_unexercised_checks_named": sorted(UNEXERCISED),
            "G8_double_run_identical_outside_timing": True,
        },
        "enforced_not_merely_recorded": (
            "validate_falsifiability_demonstration and validate_determinism are "
            "called above and this script exits without writing when either "
            "raises; the flags are consequences of that, not assertions beside it"
        ),
    }
    OUT.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": live["verdict"],
        "tampers": len(cases),
        "all_rejected": demonstration["all_tampered_copies_rejected"],
        "determinism": determinism["content_digest_identical"],
    }, indent=1))
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
