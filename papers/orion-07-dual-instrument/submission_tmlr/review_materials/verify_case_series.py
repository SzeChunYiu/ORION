#!/usr/bin/env python3
"""Verify the anonymous three-question case-series record."""
from __future__ import annotations

import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"verification failed: {message}")


data = json.loads((Path(__file__).parent / "case_series.json").read_text(encoding="utf-8"))
boundary = data["study_boundary"]
cases = data["valid_questions"]

require(boundary["valid_question_count"] == 3, "valid question count must be three")
require(len(cases) == 3, "exactly three valid records are required")
require([record["public_name"] for record in cases] == [
    "regime characterization",
    "support-threshold stress test",
    "reweighted-objective census",
], "the three public question names or their order changed")
require(len(data["retired_candidates"]) == 2, "both contaminated candidates must be retained")
require(all(not record["included_in_valid_question_count"] for record in data["retired_candidates"]),
        "retired candidates must not enter the valid count")
require(all(record["retained"] for record in data["retired_candidates"]),
        "retired candidates must remain visible")

for record in cases:
    require(record["prospective_freeze_verified"], f"{record['public_name']} lacks a verified freeze")
    decisions = record["frozen_decisions"]
    reconstructed_relation = {
        "diagnosis": "agree" if decisions["host"]["diagnosis"] == decisions["controller"]["diagnosis"] else "disagree",
        "experiment": "agree" if decisions["host"]["experiment"] == decisions["controller"]["experiment"] else "disagree",
    }
    require(record["instrument_relations"] == reconstructed_relation,
            f"{record['public_name']} relation is not reconstructable from frozen decisions")
    expected = record["deferred_scoring_map"][record["observed_branch"]]
    reconstructed_alignment = {
        "host_diagnosis": decisions["host"]["diagnosis"] == expected["expected_diagnosis"],
        "controller_diagnosis": decisions["controller"]["diagnosis"] == expected["expected_diagnosis"],
        "host_experiment": decisions["host"]["experiment"] == expected["expected_experiment"],
        "controller_experiment": decisions["controller"]["experiment"] == expected["expected_experiment"],
    }
    require(record["deferred_alignment"] == reconstructed_alignment,
            f"{record['public_name']} deferred alignment is not reconstructable from the frozen map")

support_test = cases[1]["bounded_scientific_observation"]
require(support_test["exact_panel_rows"] == 53, "support-threshold row count")
require(support_test["unrestricted_better_than_support_two_rows"] == 0, "support-threshold gap count")
require(support_test["theorem_sharpness_resolved"] is False, "support-threshold question must leave sharpness open")

reweighted_census = cases[2]
reweighted_observation = reweighted_census["bounded_scientific_observation"]
require(reweighted_observation["ordered_one_object_cases"] + reweighted_observation["reorder_quotiented_two_object_cases"]
        == reweighted_observation["total_cases"] == 39489, "reweighted-census domain arithmetic")
require(reweighted_observation["predicate_label_mismatches"] == 0, "reweighted-census mismatch count")
require(reweighted_census["deferred_alignment"] == {
    "host_diagnosis": False,
    "controller_diagnosis": False,
    "host_experiment": True,
    "controller_experiment": True,
}, "reweighted-census agreement-with-misdiagnosis disposition")

for prohibited in ("reliability_claimed", "calibration_claimed", "generalization_claimed"):
    require(boundary[prohibited] is False, f"prohibited promotion: {prohibited}")
require(boundary["statistical_or_causal_instrument_independence_claimed"] is False,
        "instrument independence must not be promoted")
flow = data["candidate_flow"]
require(flow["registered_candidates"] == flow["valid_questions"] + flow["contaminated_before_freeze"]
        + flow["instrument_invalid"] + flow["cannot_check"] == 5,
        "candidate-flow accounting is incomplete")

for limitation in data["known_instrument_limitations"]:
    require(limitation["repaired_between_valid_cases"] is False,
            "known limitations must not be described as repaired")
    require(limitation["triggered_in_valid_cases"] is False,
            "known limitations did not trigger in valid cases")

print("Verified cases")
for record in cases:
    align = record["deferred_alignment"]
    print(
        f"  {record['public_name']}: diagnosis relation={record['instrument_relations']['diagnosis']}; "
        f"host diagnosis={align['host_diagnosis']}; controller diagnosis={align['controller_diagnosis']}; "
        f"host experiment={align['host_experiment']}; controller experiment={align['controller_experiment']}"
    )
print("Bounded case-series checks passed; no aggregate performance claim was computed.")
