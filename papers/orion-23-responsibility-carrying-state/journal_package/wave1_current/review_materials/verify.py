#!/usr/bin/env python3
"""Independently derive all manuscript tables from anonymous review data."""

from __future__ import annotations

from collections import defaultdict
from itertools import product
import json
from pathlib import Path


DATA = json.loads((Path(__file__).with_name("evidence.json")).read_text())


def lit_satisfied(literal, model):
    value = model[abs(literal) - 1]
    if value in (-1, 1, 2, 3, 4, 5, -2, -3, -4, -5):
        truth = value > 0
    else:
        truth = bool(value)
    return truth if literal > 0 else not truth


def sat(formula, model):
    return all(any(lit_satisfied(lit, model) for lit in clause) for clause in formula)


def all_models(formula, variables=5):
    return [list(bits) for bits in product((0, 1), repeat=variables) if sat(formula, bits)]


def mean(values):
    return sum(values) / len(values)


def learned_check():
    study = DATA["learned_data"]
    rows = study["rows"]
    assert study["source_items"] == 1797
    assert study["responsibility_episodes_per_policy"] == 3594
    assert len(rows) == study["policy_evaluations"] == 17970
    summary = {}
    for policy in sorted({row["policy"] for row in rows}):
        selected = [row for row in rows if row["policy"] == policy]
        digits = [row for row in selected if row["responsibility"] == "DIGIT"]
        summary[policy] = {
            "combined_accuracy": mean([row["prediction"] == row["gold"] for row in selected]),
            "digit_accuracy": mean([row["prediction"] == row["gold"] for row in digits]),
            "unsupported_reuse": mean([row["unsupported_reuse"] for row in digits]),
            "mean_values": mean([row["state_values_read"] for row in selected]),
        }
    expected = {
        "RESPONSIBILITY_RELATIVE": (0.9435169727323317, 0.9699499165275459, 0.0, 33.0),
        "ALWAYS_RAW": (0.9435169727323317, 0.9699499165275459, 0.0, 64.0),
        "CONFIDENCE_ONLY": (0.6563717306622148, 0.39565943238731216, 0.7774067890929327, 15.800779076238175),
        "PROVENANCE_ONLY": (0.5773511407902059, 0.2376182526432944, 1.0, 2.0),
        "UNQUALIFIED_REUSE": (0.5773511407902059, 0.2376182526432944, 1.0, 2.0),
    }
    for policy, values in expected.items():
        observed = summary[policy]
        for key, target in zip(("combined_accuracy", "digit_accuracy", "unsupported_reuse", "mean_values"), values):
            assert abs(observed[key] - target) < 1e-12, (policy, key, observed[key], target)
    assert abs(1 - summary["RESPONSIBILITY_RELATIVE"]["mean_values"] / summary["ALWAYS_RAW"]["mean_values"] - 0.484375) < 1e-12
    return summary


def formula_change_check():
    study = DATA["verified_responsibility_change"]
    cases = {case["case"]: case for case in study["cases"]}
    assert len(cases) == 12 and len(study["rows"]) == 96
    correct = defaultdict(int); stale = defaultdict(int); reads = defaultdict(int)
    for case in cases.values():
        assert len(all_models(case["base_formula"], case["variables"])) == 2
        assert len(all_models(case["changed_formula"], case["variables"])) == 1
        assert sat(case["base_formula"], case["old_model"])
        assert not sat(case["changed_formula"], case["old_model"])
    for row in study["rows"]:
        case = cases[row["case"]]
        formula = case["base_formula"] if row["stage"] == "OLD" else case["changed_formula"]
        correct[row["policy"]] += int(sat(formula, row["prediction"]))
        stale[row["policy"]] += int(row["stale_reuse"])
        reads[row["policy"]] += row["literal_reads"]
    assert dict(correct) == {"RESPONSIBILITY_RELATIVE": 24, "ALWAYS_RAW": 24, "CONFIDENCE_ONLY": 12, "PROVENANCE_ONLY": 12}
    assert dict(stale) == {"RESPONSIBILITY_RELATIVE": 0, "ALWAYS_RAW": 0, "CONFIDENCE_ONLY": 12, "PROVENANCE_ONLY": 12}
    assert dict(reads) == {"RESPONSIBILITY_RELATIVE": 60, "ALWAYS_RAW": 108, "CONFIDENCE_ONLY": 0, "PROVENANCE_ONLY": 0}


def provenance_check():
    study = DATA["provenance_tier_comparison"]
    cases = {case["case"]: case for case in study["cases"]}
    assert len(cases) == 48 and len(study["rows"]) == 240
    correct = defaultdict(int); unsupported = defaultdict(int); reads = defaultdict(int)
    for row in study["rows"]:
        case = cases[row["case"]]
        ok = sat(case["world_formula"], row["prediction"])
        correct[row["policy"]] += int(ok)
        unsupported[row["policy"]] += int(row["served_compact"] and not case["requested_responsibility_supported"])
        reads[row["policy"]] += row["literal_reads"]
    assert dict(correct) == {"PROVENANCE_TIER": 36, "PROVENANCE_TIER_DEMAND": 36, "RESPONSIBILITY_RELATIVE": 48, "COMPOSED_COORDINATES": 48, "ALWAYS_RAW": 48}
    assert dict(unsupported) == {"PROVENANCE_TIER": 12, "PROVENANCE_TIER_DEMAND": 12, "RESPONSIBILITY_RELATIVE": 0, "COMPOSED_COORDINATES": 0, "ALWAYS_RAW": 0}
    assert {policy: value / 48 for policy, value in reads.items()} == {"PROVENANCE_TIER": 6.25, "PROVENANCE_TIER_DEMAND": 6.25, "RESPONSIBILITY_RELATIVE": 5.0, "COMPOSED_COORDINATES": 5.0, "ALWAYS_RAW": 5.5}


def transport_check():
    study = DATA["bounded_drift_transport"]
    cases = {case["case"]: case for case in study["cases"]}
    assert len(cases) == 60 and len(study["rows"]) == 240
    correct = defaultdict(int); unsound = defaultdict(int); needless = defaultdict(int); reads = defaultdict(int)
    for row in study["rows"]:
        case = cases[row["case"]]
        if row["unsatisfiable_claim"]:
            ok = len(all_models(case["shifted_formula"])) == 0
        else:
            ok = row["prediction"] is not None and sat(case["shifted_formula"], row["prediction"])
        sound_transport = case["stratum"] == "REDUNDANT"
        correct[row["policy"]] += int(ok)
        unsound[row["policy"]] += int(row["transported"] and not sound_transport)
        needless[row["policy"]] += int(not row["transported"] and sound_transport)
        reads[row["policy"]] += row["literal_reads"]
    assert dict(correct) == {"UNCONDITIONAL": 40, "SIGNATURE_EQUALITY": 60, "LOCAL_DRIFT_BOUND": 60, "ALWAYS_REISSUE": 60}
    assert dict(unsound) == {"UNCONDITIONAL": 40, "SIGNATURE_EQUALITY": 0, "LOCAL_DRIFT_BOUND": 0, "ALWAYS_REISSUE": 0}
    assert dict(needless) == {"UNCONDITIONAL": 0, "SIGNATURE_EQUALITY": 20, "LOCAL_DRIFT_BOUND": 0, "ALWAYS_REISSUE": 20}
    means = {policy: value / 60 for policy, value in reads.items()}
    expected = {"UNCONDITIONAL": 6.0, "SIGNATURE_EQUALITY": 11.333333333333334, "LOCAL_DRIFT_BOUND": 10.0, "ALWAYS_REISSUE": 11.333333333333334}
    for policy, target in expected.items(): assert abs(means[policy] - target) < 1e-12


def adverse_check():
    adverse = DATA["retained_adverse_measurement"]
    assert adverse["enumerated_points"] == 3840
    assert adverse["policy_action_changes_under_certificate_corruption"] == 2304
    assert adverse["positive_independent_harm_opportunities"] == 0
    assert adverse["disposition"].startswith("excluded_from_positive_evidence")


def main():
    learned_check()
    formula_change_check()
    provenance_check()
    transport_check()
    adverse_check()
    print("review evidence verification: PASS")


if __name__ == "__main__":
    main()
