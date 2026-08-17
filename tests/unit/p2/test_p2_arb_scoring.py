"""Fidelity tests for the vendored official AutoResearchBench Wide scorer.

The question these tests answer is not "does our metric look sensible" but
"is it the same function the official evaluator runs". A metric that is
subtly nicer than the official one produces numbers that cannot be compared
to published AutoResearchBench results, which is the whole reason the scorer
was vendored rather than reimplemented.

Every invariant below is asserted in both directions where that is possible:
the alarm case *and* the no-alarm case. A test that only checks that bad
input is rejected passes just as happily on a scorer that rejects everything.
"""

from __future__ import annotations

import ast
import inspect
import os
import random
from pathlib import Path

import pytest

from orion.study.p2 import arb_scoring
from orion.study.p2.arb_scoring import (
    JinaLookupDisabled,
    compute_iou_recall,
    evaluator_hash,
    get_gt_arxiv_ids,
    get_predicted_arxiv_ids,
    max_iou_at_k_sampling,
    normalize_arxiv_id,
    score_wide_task,
)

VENDORED_FUNCTION_NAMES = (
    "max_iou_at_k_sampling",
    "normalize_arxiv_id",
    "get_gt_arxiv_ids",
    "get_predicted_arxiv_ids",
    "compute_iou_recall",
)


# ---------------------------------------------------------------------------
# Differential fidelity against the real upstream file, when it is reachable.
# ---------------------------------------------------------------------------


def _upstream_path() -> Path | None:
    """Locate a copy of the pinned upstream evaluator, or report that we cannot.

    CI has no copy, so this returns None there and the differential test skips
    with an explicit reason. A skip is recorded as "not checked", never as
    "checked and fine" -- the behavioural tests below stand on their own and do
    not depend on this file being present.
    """

    override = os.environ.get("ORION_ARB_UPSTREAM_WIDE_EVALUATOR", "").strip()
    if override:
        candidate = Path(override)
        return candidate if candidate.is_file() else None
    return None


def _function_sources(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: ast.unparse(node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def test_vendored_functions_match_upstream_source_when_available() -> None:
    path = _upstream_path()
    if path is None:
        pytest.skip(
            "upstream evaluate/evaluate_wide_search.py not reachable; set "
            "ORION_ARB_UPSTREAM_WIDE_EVALUATOR to a copy of "
            f"{arb_scoring.UPSTREAM_REPO}@{arb_scoring.UPSTREAM_COMMIT} :: "
            f"{arb_scoring.UPSTREAM_FILE} to run the differential check. "
            "This is NOT evidence that the vendored code matches."
        )
    upstream = _function_sources(path)
    missing = [name for name in VENDORED_FUNCTION_NAMES if name not in upstream]
    assert not missing, f"upstream file is missing {missing}; wrong file pinned?"

    for name in VENDORED_FUNCTION_NAMES:
        ours = ast.unparse(ast.parse(inspect.getsource(getattr(arb_scoring, name))))
        assert ours == upstream[name], f"vendored {name} drifted from upstream"


# ---------------------------------------------------------------------------
# compute_iou_recall -- the metric itself, including the edge cases upstream
# encodes.
# ---------------------------------------------------------------------------


def test_both_sets_empty_scores_perfect() -> None:
    """Upstream's explicit special case. Nothing asked, nothing missed."""

    assert compute_iou_recall(set(), set()) == (1.0, 1.0, 1.0)


def test_empty_prediction_against_real_gold_scores_zero() -> None:
    """The no-alarm counterpart: emptiness is only perfect when gold is empty too."""

    iou, recall, precision = compute_iou_recall({"2501.00001"}, set())
    assert (iou, recall, precision) == (0.0, 0.0, 0.0)


def test_empty_gold_against_real_prediction_scores_zero() -> None:
    iou, recall, precision = compute_iou_recall(set(), {"2501.00001"})
    assert (iou, recall, precision) == (0.0, 0.0, 0.0)


def test_partial_overlap_arithmetic() -> None:
    gold = {"2501.00001", "2501.00002"}
    pred = {"2501.00002", "2501.00003"}
    iou, recall, precision = compute_iou_recall(gold, pred)
    assert iou == pytest.approx(1 / 3)
    assert recall == pytest.approx(0.5)
    assert precision == pytest.approx(0.5)


def test_exact_match_scores_one() -> None:
    gold = {"2501.00001", "2501.00002"}
    iou, recall, precision = compute_iou_recall(gold, set(gold))
    assert (iou, recall, precision) == (1.0, 1.0, 1.0)


def test_empty_union_branch_is_unreachable_and_is_kept_that_way() -> None:
    """Upstream observation U1, asserted rather than described.

    ``iou = intersection / union if union else 0.0`` can only take its ``else``
    when both sets are empty, and that case returned earlier. We keep the dead
    branch verbatim; this test pins *why* it is dead so a future reader does not
    "fix" the guard and change the metric.
    """

    source = inspect.getsource(compute_iou_recall)
    assert "if union else 0.0" in source, "the upstream dead branch was removed"
    for gold, pred in (({"a"}, set()), (set(), {"a"}), ({"a"}, {"b"})):
        assert len(gold | pred) > 0


# ---------------------------------------------------------------------------
# normalize_arxiv_id -- id normalisation with and without a version suffix.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2501.12345", "2501.12345"),
        ("2501.12345v2", "2501.12345"),
        ("2501.1234", "2501.1234"),
        ("arXiv:2501.12345", "2501.12345"),
        ("ARXIV:2501.12345", "2501.12345"),
        ("arxiv:2501.12345v7", "2501.12345"),
        ("https://arxiv.org/abs/2501.12345", "2501.12345"),
        ("https://arxiv.org/pdf/2501.12345v1", "2501.12345"),
        ("  2501.12345  ", "2501.12345"),
        ("", ""),
    ],
)
def test_normalize_arxiv_id_new_style(raw: str, expected: str) -> None:
    assert normalize_arxiv_id(raw) == expected


def test_normalize_arxiv_id_passes_old_style_identifiers_through() -> None:
    """Pre-2007 ids do not match the new-style regex and are returned as-is.

    This matters for us: an old-style id can never equal a new-style one, so a
    prediction carrying one scores zero against new-style gold. Preserved, not
    fixed -- the official evaluator behaves this way and so must we.
    """

    assert normalize_arxiv_id("hep-th/9901001") == "hep-th/9901001"
    assert normalize_arxiv_id("arXiv:hep-th/9901001") == "hep-th/9901001"


def test_normalize_arxiv_id_truncates_over_long_numeric_ids() -> None:
    """Upstream's regex is greedy at 5 digits; a 6-digit tail is dropped."""

    assert normalize_arxiv_id("2501.123456") == "2501.12345"


# ---------------------------------------------------------------------------
# Gold custody entry point.
# ---------------------------------------------------------------------------


def test_get_gt_arxiv_ids_reads_arxiv_id_directly() -> None:
    record = {
        "question": "irrelevant",
        "answer": ["Some Title"],
        "arxiv_id": ["2501.00001", "arXiv:2501.00002v3"],
    }
    assert get_gt_arxiv_ids(record, use_jina=False) == {"2501.00001", "2501.00002"}


def test_get_gt_arxiv_ids_drops_blank_entries() -> None:
    record = {"arxiv_id": ["2501.00001", "", None]}
    assert get_gt_arxiv_ids(record, use_jina=False) == {"2501.00001"}


def test_get_gt_arxiv_ids_without_ids_returns_empty_when_jina_disabled() -> None:
    assert get_gt_arxiv_ids({"answer": ["Title"]}, use_jina=False) == set()


def test_jina_branch_is_inert_because_the_key_is_pinned_empty() -> None:
    """Deviation D1: with no key the branch is not taken, exactly as upstream."""

    assert arb_scoring.JINA_API_KEY == ""
    assert get_gt_arxiv_ids({"answer": ["Title"]}, use_jina=True) == set()


def test_jina_stub_raises_loudly_if_the_branch_is_ever_reached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deviation D2: a would-be network call fails loudly, never silently empty.

    Forcing a key on makes the unreachable branch reachable. It must raise, not
    return an empty set -- "found nothing" and "did not look" must not collapse
    into the same value.
    """

    monkeypatch.setattr(arb_scoring, "JINA_API_KEY", "forced-for-test")
    with pytest.raises(JinaLookupDisabled):
        get_gt_arxiv_ids({"answer": ["Some Title"]}, use_jina=True)


# ---------------------------------------------------------------------------
# Prediction entry point.
# ---------------------------------------------------------------------------


def test_get_predicted_arxiv_ids_normalises_and_dedupes() -> None:
    candidates = [
        {"arxiv_id": "2501.00001"},
        {"arxiv_id": "arXiv:2501.00001v2"},
        {"arxiv_id": "2501.00002"},
    ]
    assert get_predicted_arxiv_ids(candidates) == {"2501.00001", "2501.00002"}


def test_get_predicted_arxiv_ids_tolerates_empty_and_missing_fields() -> None:
    assert get_predicted_arxiv_ids([]) == set()
    assert get_predicted_arxiv_ids(None) == set()  # type: ignore[arg-type]
    assert get_predicted_arxiv_ids([{"arxiv_id": ""}, {"title": "no id"}]) == set()


# ---------------------------------------------------------------------------
# max_iou_at_k_sampling -- upstream observation U2.
# ---------------------------------------------------------------------------


def test_max_iou_at_k_returns_zero_when_k_exceeds_available_passes() -> None:
    assert max_iou_at_k_sampling([0.1, 0.5], 4) == 0.0


def test_max_iou_at_k_returns_zero_for_non_positive_k() -> None:
    assert max_iou_at_k_sampling([0.1, 0.5], 0) == 0.0
    assert max_iou_at_k_sampling([0.1, 0.5], -1) == 0.0


def test_max_iou_at_k_is_exact_when_k_equals_the_number_of_passes() -> None:
    """Sampling k of k is a permutation, so the max is the true max."""

    ious = [0.1, 0.5, 0.9]
    random.seed(1)
    assert max_iou_at_k_sampling(ious, 3) == 0.9
    random.seed(12345)
    assert max_iou_at_k_sampling(ious, 3) == 0.9


def test_max_iou_at_k_is_reproducible_under_a_fixed_seed() -> None:
    ious = [0.1, 0.5, 0.9]
    random.seed(7)
    first = max_iou_at_k_sampling(ious, 1)
    random.seed(7)
    second = max_iou_at_k_sampling(ious, 1)
    assert first == second


def test_max_iou_at_k_varies_across_seeds_which_is_why_avg_iou_is_the_primary() -> None:
    """Upstream observation U2, asserted.

    This is the reason ``avg_iou`` and not ``avg_max_iou_at_k`` is bound as
    ``wide_official_iou``: the sampled aggregate moves with the global RNG
    state. Five seeds producing one identical value would mean the sampling is
    not actually happening.
    """

    ious = [0.1, 0.5, 0.9]
    observed = set()
    for seed in (1, 2, 3, 4, 5):
        random.seed(seed)
        observed.add(max_iou_at_k_sampling(ious, 1))
    assert len(observed) > 1


# ---------------------------------------------------------------------------
# The thin shape adapter.
# ---------------------------------------------------------------------------


def test_score_wide_task_perfect_prediction_scores_one() -> None:
    """The positive case. A bridge that always returned empty would fail here."""

    gold = ["2501.00001", "2501.00002"]
    assert score_wide_task(gold, ["arXiv:2501.00001v1", "2501.00002"]) == (1.0, 1.0, 1.0)


def test_score_wide_task_matches_the_vendored_path_directly() -> None:
    gold = ["2501.00001", "2501.00002", "2501.00003"]
    pred = ["2501.00002", "2599.99999"]
    expected = compute_iou_recall(
        get_gt_arxiv_ids({"arxiv_id": gold}, use_jina=False),
        get_predicted_arxiv_ids([{"arxiv_id": item} for item in pred]),
    )
    assert score_wide_task(gold, pred) == expected


def test_evaluator_hash_names_the_upstream_file() -> None:
    assert evaluator_hash() == arb_scoring.UPSTREAM_FILE_SHA256
    assert len(evaluator_hash()) == 64
