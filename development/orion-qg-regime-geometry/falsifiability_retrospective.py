#!/usr/bin/env python3
"""Run the falsifiability gate over the lane demonstrations that predate it.

`orion_research_harness.falsifiability` was written after QG-24 and QG-26 were
found to contain tamper cases that rejected for the wrong reason. QG-23's
demonstration was committed before either, and has never been checked this way.

**What this can and cannot find, stated before the result.**

It reads the *recorded* demonstration and asks whether each case was caught by the
check its name says it exercises. That finds the QG-26-T9 shape: a case rejected
by a real but unrelated check, leaving the named one untested.

It CANNOT find the QG-24-T6 shape -- a mutation that does not do what its name
says, so that the copy is accepted or caught elsewhere for reasons invisible in
the record. Detecting that requires re-running the verifier against freshly
constructed tampers, which is what produced two wrong reconstructions in one
afternoon and is not attempted here.

The expected-check mapping below is the adjudicator's reading of each case name
against QG-23's committed verifier, not something the lane declared. It is stated
as a reading so it can be disputed.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "packages" / "orion-research-harness" / "src"))

from orion_research_harness.falsifiability import (  # noqa: E402
    validate_falsifiability_demonstration,
)

QG23 = REPO / "development" / "orion-qg-regime-geometry" / "QG23_GENERIC_VERIFICATION.json"

#: Adjudicator's reading of which check each QG-23 case exists to exercise.
QG23_EXPECTED = {
    "H1_verdict_flipped_to_BORNE_OUT": "H1_verdict",
    "normalized_box_coverage_inflated": "coverage",
    "lattice_baseline_claimed_perfect": "baselines_recomputed_32_and_3",
    "one_feature_reclassified_as_linear": "census_per_feature_rederived",
    "raw_headline_witness_threshold_shifted": "raw_headline_witness_is_the_qg15c_witness",
    "one_tradeoff_curve_cell_zeroed": "q3_curves_rederived",
    "stage1_digest_replaced": "stage1_digest",
    "H0_census_claims_intensive_features_did_it": "H0_support_census",
}


def adapt(raw: dict) -> dict:
    """QG-23 recorded its cases under different key names. Rename, do not reshape.

    `tamper` -> `case`, `decision` -> `verdict`, `checks_that_caught_it` ->
    `failed_checks`, `self_consistent_digest` -> the resealing flag. No case is
    added, dropped or altered.
    """
    return {
        "cases": [
            {
                "case": c["tamper"],
                "verdict": c["decision"],
                "failed_checks": c["checks_that_caught_it"],
                "result_digest_recomputed_so_copy_is_internally_self_consistent":
                    c["self_consistent_digest"],
            }
            for c in raw["cases"]
        ]
    }


def main() -> int:
    raw = json.loads(QG23.read_text())["falsifiability_demonstration"]
    demo = adapt(raw)
    try:
        validate_falsifiability_demonstration(demo, QG23_EXPECTED)
        verdict, detail = "CLEARS", None
    except ValueError as exc:
        verdict, detail = "REFUSED", str(exc)

    # A gate that clears everything is not a gate, and an adapter that quietly
    # produced something unfaultable would look exactly like a clean result. Show
    # it biting on this very record set before reporting that it did not bite.
    import copy
    probe = copy.deepcopy(demo)
    probe["cases"][0]["failed_checks"] = ["an_unrelated_check"]
    try:
        validate_falsifiability_demonstration(probe, QG23_EXPECTED)
        raise SystemExit(
            "the gate cleared a QG-23 case pointed at an unrelated check; the "
            "adapter or the mapping is wrong and CLEARS above means nothing"
        )
    except ValueError as exc:
        not_vacuous = {"probe": "first case redirected to an unrelated check",
                       "gate": "REFUSED", "gate_reason": str(exc)}

    out = {
        "schema": "ORIONQG.FalsifiabilityRetrospective.v1",
        "gate_is_not_vacuous": not_vacuous,
        "lane": "QG-23",
        "artifact": str(QG23.relative_to(REPO)),
        "cases_examined": len(demo["cases"]),
        "expected_check_is_the_adjudicators_reading_not_a_lane_declaration": True,
        "detects": "a case rejected by a real but unrelated check (the QG-26 T9 shape)",
        "does_not_detect": (
            "a mutation that does not do what its name says (the QG-24 T6 shape); "
            "that needs the verifier re-run against fresh tampers, not the record"
        ),
        "gate": verdict,
        "gate_reason": detail,
    }
    dest = REPO / "development" / "orion-qg-regime-geometry" / "FALSIFIABILITY_RETROSPECTIVE.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("lane", "cases_examined", "gate", "gate_reason")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
