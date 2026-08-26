from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(
    "papers/orion-12-open-world-scientific-discovery/scripts/run_metasyn_keyless.py"
)


def _module():
    spec = importlib.util.spec_from_file_location("p2_metasyn_keyless", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sanitize_review_is_strict_allowlist_and_drops_gold() -> None:
    module = _module()
    review = {
        "ID": 42,
        "Research_Question": "Do exercise programmes improve gait after stroke?",
        "Population": "Adults after stroke",
        "Intervention": "Exercise rehabilitation",
        "Exposure": None,
        "Comparison": "Usual care",
        "Outcome": "Gait speed",
        "search_start_date": "2000-01-01",
        "search_end_date": "2024-12-31",
        "inclusion_criteria": "Randomized adult rehabilitation studies",
        "exclusion_criteria": "Animal studies",
        "source_review_corpus_ids": [9],
        "matched_corpus_ids": [101, 102],
        "Effect_Direction": "Positive",
        "Key_Insights": "hidden synthesis label",
    }
    public = module.sanitize_review(review)
    assert set(public) == set(module.PUBLIC_FIELDS)
    assert public["source_review_corpus_ids"] == [9]
    serialized = repr(public).lower()
    assert "matched_corpus_ids" not in serialized
    assert "effect_direction" not in serialized
    assert "hidden synthesis" not in serialized


def test_screening_uses_public_protocol_terms_and_year_ceiling() -> None:
    module = _module()
    review = {
        "ID": 42,
        "Research_Question": "Do exercise rehabilitation programmes improve gait after stroke?",
        "Population": "Adults after stroke",
        "Intervention": "Exercise rehabilitation",
        "Exposure": None,
        "Comparison": "Usual care",
        "Outcome": "Gait speed",
        "search_start_date": "2000-01-01",
        "search_end_date": "2024-12-31",
        "inclusion_criteria": "Randomized adult rehabilitation studies",
        "exclusion_criteria": "Animal studies",
        "source_review_corpus_ids": [9],
    }
    candidates = [
        {
            "corpus_id": 101,
            "rank": 1,
            "score": 10.0,
            "year": 2022,
            "title": "Exercise rehabilitation after stroke",
            "abstract": "Adults receiving rehabilitation improved gait speed compared with usual care.",
        },
        {
            "corpus_id": 102,
            "rank": 2,
            "score": 9.0,
            "year": 2025,
            "title": "Exercise rehabilitation after stroke",
            "abstract": "Adults receiving rehabilitation improved gait speed.",
        },
        {
            "corpus_id": 103,
            "rank": 3,
            "score": 8.0,
            "year": 2021,
            "title": "Unrelated spectroscopy measurement",
            "abstract": "Optical sensor calibration in a laboratory phantom.",
        },
    ]
    selected = module.screen_candidates(review, candidates)
    assert selected == [101]


def test_nr_intervention_falls_back_to_exposure_terms() -> None:
    module = _module()
    review = {
        "Research_Question": "Smoking exposure and pulmonary outcomes",
        "Population": "Adults",
        "Intervention": "NR",
        "Exposure": "Cigarette smoking",
        "Comparison": None,
        "Outcome": "Pulmonary function",
    }
    fields = module._field_sets(review)
    assert {"cigarette", "smoking"} in fields


def test_screening_never_selects_outside_retrieved_pool() -> None:
    module = _module()
    review = {
        "ID": 1,
        "Research_Question": "Hypertension treatment and mortality",
        "Population": "Adults with hypertension",
        "Intervention": "Antihypertensive treatment",
        "Exposure": None,
        "Comparison": "Placebo",
        "Outcome": "Mortality",
        "search_start_date": None,
        "search_end_date": None,
        "inclusion_criteria": "Controlled trials",
        "exclusion_criteria": None,
        "source_review_corpus_ids": [],
    }
    candidates = [
        {
            "corpus_id": 5,
            "rank": 1,
            "score": 1.0,
            "year": 2020,
            "title": "Antihypertensive treatment",
            "abstract": "Hypertension mortality placebo controlled adults",
        }
    ]
    selected = module.screen_candidates(review, candidates)
    assert selected == [5]
    assert set(selected) <= {item["corpus_id"] for item in candidates}
