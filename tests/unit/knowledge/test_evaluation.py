from __future__ import annotations

import pytest

from orion.knowledge.evaluation import (
    Comparison,
    GoldTier,
    RecallTask,
    UnsupportedClaim,
    compare_against_baseline,
    naive_keyword_ranking,
    recall_at,
    score_ranking,
    screened_to_recall,
    work_saved_over_sampling,
)

_DOCS = {
    "d1": "stopping rules for technology assisted review screening",
    "d2": "capture recapture estimation of unseen species richness",
    "d3": "a cookbook of italian pasta recipes",
    "d4": "screening prioritisation and stopping criteria in systematic reviews",
    "d5": "convolutional networks for image classification",
}


def _task(tier: GoldTier = GoldTier.T3_PROTOCOL_COMPLETE) -> RecallTask:
    return RecallTask(
        task_id="t1",
        query="stopping criteria for screening in systematic reviews",
        gold_ids=frozenset({"d1", "d4"}),
        corpus_ids=tuple(_DOCS),
        tier=tier,
        provenance="hand-built fixture; not a protocol-derived set",
    )


# --- what a gold set may support ----------------------------------------


def test_a_single_target_gold_set_cannot_report_recall() -> None:
    """The central measurement error in this literature: LitSearch-style
    'recall@5' means one known paper was in the top 5."""

    with pytest.raises(UnsupportedClaim):
        compare_against_baseline(
            _task(GoldTier.T1_SINGLE_TARGET), ["d1"], _DOCS
        )


def test_tiers_declare_whether_a_denominator_exists() -> None:
    assert GoldTier.T3_PROTOCOL_COMPLETE.supports_recall
    assert GoldTier.T2_POOLED.supports_recall
    assert not GoldTier.T1_SINGLE_TARGET.supports_recall
    assert not GoldTier.T0_NO_DOCUMENT_GOLD.supports_recall


def test_a_gold_set_must_state_its_provenance() -> None:
    with pytest.raises(ValueError):
        RecallTask("t", "q", frozenset({"d1"}), ("d1",), GoldTier.T2_POOLED, "  ")


def test_gold_documents_outside_the_corpus_make_recall_unmeasurable() -> None:
    with pytest.raises(ValueError):
        RecallTask(
            "t", "q", frozenset({"absent"}), ("d1",), GoldTier.T2_POOLED, "fixture"
        )


def test_prevalence_is_available_because_recall_must_be_read_against_it() -> None:
    assert _task().prevalence == pytest.approx(2 / 5)


# --- metrics -------------------------------------------------------------


def test_recall_counts_against_the_full_gold_set() -> None:
    assert recall_at(["d1", "d3"], frozenset({"d1", "d4"}), 2) == 0.5
    assert recall_at(["d1", "d4"], frozenset({"d1", "d4"}), 2) == 1.0


def test_an_unreachable_target_is_none_not_a_large_number() -> None:
    """Reporting 'screened everything' as a number would let an unreachable
    target average in as a merely-expensive one."""

    assert screened_to_recall(["d3", "d5"], frozenset({"d1", "d4"}), 0.95) is None
    assert work_saved_over_sampling(None, 5, 0.95) is None


def test_work_saved_is_measured_against_chance_not_raw_saving() -> None:
    """WSS subtracts (1 - target), so a random-quality ranking scores ~0."""

    # Perfect ranking: both gold items first, out of 100 documents.
    assert work_saved_over_sampling(2, 100, 0.95) == pytest.approx(0.93)
    # Having to screen 95 of 100 to hit 95% recall is no better than chance.
    assert work_saved_over_sampling(95, 100, 0.95) == pytest.approx(0.0)


def test_a_ranking_that_never_reaches_the_target_reports_no_saving() -> None:
    score = score_ranking("s", _task(), ["d3", "d5"], target_recall=0.95)
    assert score.screened_to_target_recall is None
    assert score.work_saved is None


# --- the baseline --------------------------------------------------------


def test_the_naive_baseline_actually_retrieves() -> None:
    """It must be a real opponent, not a straw man — on ResearchArena a naive
    title query outscored every LLM agent."""

    ranking = naive_keyword_ranking(_task(), _DOCS)
    assert set(ranking[:2]) == {"d1", "d4"}


def test_the_baseline_degrades_gracefully_on_an_empty_query() -> None:
    task = RecallTask(
        "t", "?", frozenset({"d1"}), tuple(_DOCS), GoldTier.T2_POOLED, "fixture"
    )
    assert set(naive_keyword_ranking(task, _DOCS)) == set(_DOCS)


# --- the refusal that matters -------------------------------------------


def test_a_system_score_is_never_produced_without_its_baseline() -> None:
    """The structural point: the baseline is computed in the same call, on the
    same task, so a report omitting it cannot be assembled by accident."""

    comparison = compare_against_baseline(_task(), ["d1", "d4", "d3"], _DOCS)
    assert isinstance(comparison, Comparison)
    assert comparison.baseline.system == "naive_keyword"
    assert comparison.system.system == "orion"


def test_a_system_no_better_than_the_baseline_does_not_beat_it() -> None:
    comparison = compare_against_baseline(
        _task(), list(naive_keyword_ranking(_task(), _DOCS)), _DOCS
    )
    assert not comparison.beats_baseline
    assert comparison.margin_at(10) == 0.0


def test_a_worse_system_is_reported_as_worse() -> None:
    comparison = compare_against_baseline(_task(), ["d3", "d5", "d2"], _DOCS)
    assert not comparison.beats_baseline
    assert comparison.margin_at(10) is not None and comparison.margin_at(10) < 0
