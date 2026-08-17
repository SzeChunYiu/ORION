from __future__ import annotations

from orion.study.p3_public_reference_analysis import ablated_relation, analyze


def _base_case(
    case_id: str,
    expected: str,
    *,
    right_referent: str = "entity:a",
    right_polarity: str = "POSITIVE",
):
    return {
        "schema_version": "orion.p3.public-reference-case.v1",
        "case_id": case_id,
        "discipline": "physics",
        "case_family": "same_name_different_referent",
        "source_records": [
            {
                "dataset": "fixture",
                "revision": "abc123",
                "locator": f"{case_id}/source",
                "content_hash": "a" * 64,
            }
        ],
        "left_projection": {
            "projection_id": f"{case_id}:left",
            "source_id": "left",
            "source_span": "left#0:1",
            "predicate": "has_property",
            "referent_ids": ["entity:a"],
            "construct_ids": ["construct:x"],
            "measurement_ids": [],
            "temporal_context_ids": [],
            "polarity": "POSITIVE",
            "modality": "ASSERTED",
        },
        "right_projection": {
            "projection_id": f"{case_id}:right",
            "source_id": "right",
            "source_span": "right#0:1",
            "predicate": "has_property",
            "referent_ids": [right_referent],
            "construct_ids": ["construct:x"],
            "measurement_ids": [],
            "temporal_context_ids": [],
            "polarity": right_polarity,
            "modality": "ASSERTED",
        },
        "expected": {
            "meaning_relation": expected,
            "authority": {
                "kind": "UPSTREAM_EXPERT",
                "evidence": [f"fixture:{case_id}"],
            },
        },
    }


def test_remove_referent_exposes_targeted_false_merge():
    case = _base_case("ref", "DISTINCT_REFERENT", right_referent="entity:b")
    assert ablated_relation(case, "remove_referent").value == "COMPATIBLE"


def test_remove_polarity_erases_asserted_contradiction():
    case = _base_case("pol", "CONTRADICTORY", right_polarity="NEGATED")
    assert (
        ablated_relation(case, "remove_modality_polarity_attribution_discourse").value
        == "COMPATIBLE"
    )


def test_analysis_emits_intervals_primary_comparisons_and_ablations():
    cases = [
        _base_case("compatible", "COMPATIBLE"),
        _base_case("distinct", "DISTINCT_REFERENT", right_referent="entity:b"),
        _base_case("contra", "CONTRADICTORY", right_polarity="NEGATED"),
    ]
    report = analyze(cases)
    assert report["case_count"] == 3
    assert report["systems"]["orion"]["accuracy"]["rate"] == 1.0
    assert "false_merge_orion_minus_flat" in report["primary_comparisons"]
    assert "remove_referent" in report["ablation_deltas"]
    assert report["statistics"]["bootstrap_seed"] == 20260817
