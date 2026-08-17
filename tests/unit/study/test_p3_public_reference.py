from __future__ import annotations

import copy

import pytest

from orion.study.p3_public_reference import (
    PublicReferenceError,
    evaluate_case,
    flat_predicate_baseline,
    sha256_json,
    summarize,
    validate_case,
)


def _case(*, expected: str = "DISTINCT_REFERENT", authority: str = "UPSTREAM_EXPERT"):
    return {
        "schema_version": "orion.p3.public-reference-case.v1",
        "case_id": "p3-pr-001",
        "discipline": "physics",
        "case_family": "same_name_different_referent",
        "source_records": [
            {
                "dataset": "fixture-upstream",
                "revision": "0123456789abcdef",
                "locator": "record/a",
                "content_hash": "a" * 64,
            },
            {
                "dataset": "fixture-upstream",
                "revision": "0123456789abcdef",
                "locator": "record/b",
                "content_hash": "b" * 64,
            },
        ],
        "left_projection": {
            "projection_id": "left",
            "source_id": "source-a",
            "source_span": "record/a#0:4",
            "predicate": "has_property",
            "referent_ids": ["entity:a"],
            "construct_ids": ["construct:spin"],
            "measurement_ids": [],
            "temporal_context_ids": [],
            "polarity": "POSITIVE",
            "modality": "ASSERTED",
        },
        "right_projection": {
            "projection_id": "right",
            "source_id": "source-b",
            "source_span": "record/b#0:4",
            "predicate": "has_property",
            "referent_ids": ["entity:b"],
            "construct_ids": ["construct:spin"],
            "measurement_ids": [],
            "temporal_context_ids": [],
            "polarity": "POSITIVE",
            "modality": "ASSERTED",
        },
        "expected": {
            "meaning_relation": expected,
            "authority": {
                "kind": authority,
                "evidence": ["fixture-upstream@0123456789abcdef:record/a"],
            },
        },
    }


def test_public_reference_case_rejects_llm_gold():
    with pytest.raises(PublicReferenceError, match="forbidden gold authority"):
        validate_case(_case(authority="LLM_PROPOSAL"))


def test_public_reference_case_rejects_copied_source_text():
    case = _case()
    case["source_records"][0]["text"] = "copied upstream paragraph"
    with pytest.raises(PublicReferenceError, match="may not vendor upstream text"):
        validate_case(case)


def test_orion_blocks_same_predicate_false_merge_on_distinct_referent():
    case = _case()
    outcome = evaluate_case(case)
    assert outcome.predicted == "DISTINCT_REFERENT"
    assert outcome.correct is True
    assert flat_predicate_baseline(case).value == "COMPATIBLE"


def test_derived_gold_requires_machine_readable_nonheuristic_rule():
    case = _case(authority="DERIVED_FROM_ALLOWED")
    with pytest.raises(PublicReferenceError, match="machine-readable derivation"):
        validate_case(case)

    case["expected"]["authority"]["derivation"] = {
        "rule": "heuristic:lexical-match",
        "inputs": ["fixture"],
    }
    with pytest.raises(PublicReferenceError, match="cannot create final gold"):
        validate_case(case)

    case["expected"]["authority"]["derivation"] = {
        "rule": "identity:upstream-coreference-edge",
        "inputs": ["fixture"],
    }
    validate_case(case)


def test_atlas_hash_is_stable_and_empty_summary_fails_closed():
    case = _case()
    same = copy.deepcopy(case)
    assert sha256_json(case) == sha256_json(same)
    result = summarize([case])
    assert result["case_count"] == 1
    assert result["orion"]["accuracy"] == 1.0
    assert result["orion"]["false_merge_rate"] == 0.0
    assert len(result["atlas_sha256"]) == 64

    with pytest.raises(PublicReferenceError, match="atlas is empty"):
        summarize([])
