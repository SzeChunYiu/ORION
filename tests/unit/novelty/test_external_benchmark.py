import json
from pathlib import Path

from orion.novelty.external_benchmark import (
    BenchmarkDisposition,
    BenchmarkPrediction,
    disposition_for_state,
    evaluate_predictions,
)
from orion.novelty.types import NoveltyFinalState


def test_cannot_check_is_abstention_not_positive_novelty() -> None:
    assert disposition_for_state(NoveltyFinalState.CANNOT_CHECK) is BenchmarkDisposition.ABSTAIN


def test_state_mapping_is_non_compensatory() -> None:
    assert disposition_for_state(NoveltyFinalState.ALREADY_SOLVED) is BenchmarkDisposition.NON_NOVEL
    assert disposition_for_state(NoveltyFinalState.NOVELTY_NARROWED) is BenchmarkDisposition.NARROWED
    assert disposition_for_state(NoveltyFinalState.NOVELTY_SUPPORTED) is BenchmarkDisposition.NOVEL


def test_metrics_separate_coverage_accuracy_and_false_positive_novelty() -> None:
    rows = (
        BenchmarkPrediction("a", 1, NoveltyFinalState.ALREADY_SOLVED),
        BenchmarkPrediction("b", 3, NoveltyFinalState.NOVELTY_NARROWED),
        BenchmarkPrediction("c", 5, NoveltyFinalState.NOVELTY_SUPPORTED),
        BenchmarkPrediction("d", 2, NoveltyFinalState.NOVELTY_SUPPORTED),
        BenchmarkPrediction("e", 4, NoveltyFinalState.CANNOT_CHECK),
    )
    metrics = evaluate_predictions(rows)
    assert metrics.n == 5
    assert metrics.covered == 4
    assert metrics.correct_covered == 3
    assert metrics.coverage == 0.8
    assert metrics.selective_accuracy == 0.75
    assert metrics.abstention_rate == 0.2
    assert metrics.false_positive_novelty_rate == 0.5


def test_rinobench_freeze_is_preoutcome_and_pins_official_artifacts() -> None:
    path = Path("research/novelty/benchmark/RINOBENCH_FREEZE_V1.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["official_repository"] == "TimSchopf/RINoBench"
    assert payload["official_commit"] == "d94cd7b3ae8b336cd97e6ae274b3120268dbea82"
    assert payload["artifacts"]["test"]["blob_sha"] == "9e2c335974047475781a8bc0d57299565d658779"
    assert payload["split_policy"]["outcomes_accessed_before_freeze"] is False
    assert payload["split_policy"]["test_labels_used_for_tuning"] is False
    assert payload["evaluator_protocol"]["cannot_check_is_abstention"] is True
    assert payload["authority"]["grants_novelty_authority"] is False
