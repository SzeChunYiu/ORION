#!/usr/bin/env python3
"Fail-closed checks of the claims carried by enclosed result objects."
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "results"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main():
    a = load("paired_route_result.json")
    assert a["development"]["candidate_count"] == 99
    assert a["development"]["feasible_candidate_count"] == 0
    assert a["development"]["selected_route"]["metrics"]["route_change_coverage"] == 0
    assert a["terminal"] == "ANON_STUDY_A_NO_PAIRED_ROUTE_VALUE"

    b = load("joint_route_repair_result.json")
    assert b["invalid_STUDY_B_pairing_counterexample"]["original_randomized_value"] == "35"
    assert b["invalid_STUDY_B_pairing_counterexample"]["shortcut_randomized_value"] == "70"
    assert b["same_marginals_different_joint_system"]["full_pair_randomized_value"] == "0"
    assert b["same_marginals_different_joint_system"]["diagonal_pair_randomized_value"] == "50"

    n1 = load("initial_neighbourhood_result.json")
    assert n1["overall_verdict"] == "CERTIFICATE_INVALID"
    official = n1["splits"][0]
    assert official["relations"]["NBR_FULL"]["heldout_coverage"]["epsilon_5000"] == 0.20945945945945946
    assert official["relations"]["NBR_PCA10"]["heldout_coverage"]["epsilon_5000"] == 0.3310810810810811
    assert official["relations"]["NBR_FULL"]["certificate_heldout_violation_rate"] == 0.16891891891891891
    assert official["relations"]["NBR_PCA10"]["certificate_heldout_violation_rate"] == 0.18243243243243243

    n2 = load("corrected_neighbourhood_result.json")
    assert n2["overall_verdict"] == "VALID_WITHOUT_COVERAGE_OR_VALUE"
    for split in n2["splits"]:
        for rec in split["relations"].values():
            assert rec["heldout_coverage"]["epsilon_5000"] == 0.0

    e = load("density_backoff_result.json")
    assert e["coverage"]["backoff_summary"]["certified_coverage"] == 0.727272727273
    assert e["coverage"]["negative_control_summary"]["certified_coverage"] == 0.886363636364
    assert e["coverage"]["target"] == 0.95
    pair = load("density_paired_comparison.json")
    assert pair["geometry_certified"] == 32 and pair["control_certified"] == 39
    assert pair["mcnemar_exact_two_sided_p"] == 0.09228515625
    assert not pair["bootstrap"]["ci_excludes_zero"]

    f = load("arm_conditional_result.json")
    assert f["primary"]["certified_n"] == 44 and f["primary"]["n"] == 44
    assert f["primary"]["violations_strict"] == 20
    assert "per_instance_policy_arm_violation_flags" not in f

    selector = load("selector_diagnostic.json")
    assert selector["n"] == 44
    assert round(selector["selector_signal"]["pearson"], 3) == -0.144
    assert round(selector["selector_signal"]["permutation_p_two_sided"], 3) == 0.353
    print("ENCLOSED_RESULT_RECHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
