from __future__ import annotations

from leakage import exact_label_in_visible_text, planted_label_leakage_hits


def test_planted_gold_label_in_visible_text_fires():
    cases = [
        {
            "case_id": "planted",
            "visible": "Logs show RETRIEVAL_MISS as the protected root cause.",
            "gold": "RETRIEVAL_MISS",
        },
        {
            "case_id": "clean",
            "visible": "Search returns no candidates from an active index.",
            "gold": "RETRIEVAL_MISS",
        },
    ]
    hits = planted_label_leakage_hits(cases)
    assert [hit["case_id"] for hit in hits] == ["planted"]
    assert exact_label_in_visible_text(cases[0]["visible"], "RETRIEVAL_MISS")
    assert not exact_label_in_visible_text(cases[1]["visible"], "RETRIEVAL_MISS")


def test_partial_token_is_not_an_exact_label_hit():
    visible = "The retrieval subsystem missed nearby documents."
    assert not exact_label_in_visible_text(visible, "RETRIEVAL_MISS")
