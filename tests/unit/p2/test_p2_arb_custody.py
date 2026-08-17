"""Gold custody, the identity bridge, and the frozen subsample.

The custody tests are adversarial on purpose. A polite test that simply never
looks at the gold would pass against a completely open object graph, so the
hostile system below actively walks everything reachable from what it is
handed and fails the test if it finds a gold id. The bridge tests are the
mirror image: the failure mode there is a silent zero, so the positive case
(a correct prediction really does score 1.0) is asserted as hard as the
negative one.

No network, no bundle file: every fixture is built inline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from orion.knowledge.identity import SourceIdentity
from orion.study.p2.arb_wide import (
    BUNDLE_ENV_VAR,
    GoldCustody,
    TaskPrompt,
    WideTask,
    achieved_half_width,
    arxiv_predictions_from_identities,
    build_subsample_manifest,
    canonical_manifest_hash,
    derive_task_id,
    load_wide_tasks,
    precision_tier,
    publication_stats,
    select_subsample,
)

GOLD_A = ("2501.00001", "2501.00002", "cs/0409043")
GOLD_B = ("2402.04324", "2412.17042")


def _tasks() -> tuple[WideTask, ...]:
    return (
        WideTask(
            task_id="wide-aaaa000000000000",
            question="Which papers model temporal coherence in video diffusion?",
            gold_arxiv_ids=GOLD_A,
            answer_titles=("A Secret Title", "Another Secret Title"),
        ),
        WideTask(
            task_id="wide-bbbb000000000000",
            question="Which papers analyse neural scaling laws?",
            gold_arxiv_ids=GOLD_B,
            answer_titles=("Scaling Secrets",),
        ),
    )


# ---------------------------------------------------------------------------
# Custody: what a candidate can see.
# ---------------------------------------------------------------------------


def test_prompt_carries_only_task_id_and_question() -> None:
    prompt = _tasks()[0].prompt()
    assert set(vars(prompt)) == {"task_id", "question"}
    assert isinstance(prompt, TaskPrompt)


def _reachable_strings(root: object, budget: int = 20_000) -> set[str]:
    """Collect every string reachable from ``root`` by ordinary attribute walking.

    This is what a hostile-but-not-insane candidate can do: follow attributes,
    dataclass fields, mappings and sequences. It deliberately does not use
    ``gc.get_referrers``; nothing in Python can defend against that, and
    claiming otherwise would be a false assurance. What it does establish is
    that no *reference path* leads from a handed-out object to gold.
    """

    seen: set[int] = set()
    strings: set[str] = set()
    stack: list[object] = [root]
    while stack and len(seen) < budget:
        item = stack.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, str):
            strings.add(item)
            continue
        if isinstance(item, (bytes, int, float, bool, type(None))):
            continue
        if isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())
            continue
        if isinstance(item, (list, tuple, set, frozenset)):
            stack.extend(item)
            continue
        for attribute in ("__dict__", "__slots__"):
            value = getattr(item, attribute, None)
            if isinstance(value, dict):
                stack.extend(value.values())
            elif isinstance(value, (list, tuple)):
                for name in value:
                    stack.append(getattr(item, str(name), None))
    return strings


class HostileSystem:
    """A candidate that tries to read the gold instead of searching for it."""

    def __init__(self) -> None:
        self.harvested: set[str] = set()

    def run(self, prompt: TaskPrompt, custody: GoldCustody) -> tuple[str, ...]:
        self.harvested |= _reachable_strings(prompt)
        # Also try the custody handle itself, in case a candidate is handed one.
        self.harvested |= _reachable_strings(custody.prompts())
        for accessor in ("gold", "gold_arxiv_ids", "answers", "answer_titles", "tasks"):
            value = getattr(custody, accessor, None)
            if value is not None:
                self.harvested |= _reachable_strings(value)
        return ()


def test_hostile_system_cannot_reach_gold_from_a_prompt() -> None:
    tasks = _tasks()
    custody = GoldCustody(tasks)
    hostile = HostileSystem()
    for prompt in custody.prompts():
        hostile.run(prompt, custody)

    leaked_ids = hostile.harvested & set(GOLD_A + GOLD_B)
    assert not leaked_ids, f"gold arXiv ids reachable from candidate view: {leaked_ids}"
    leaked_titles = hostile.harvested & {
        title for task in tasks for title in task.answer_titles
    }
    assert not leaked_titles, f"gold titles reachable: {leaked_titles}"


def test_the_leak_detector_actually_detects_a_leak() -> None:
    """No-alarm assertion for the detector itself.

    If ``_reachable_strings`` simply returned nothing, the custody test above
    would pass against a wide-open object graph. Handing it a real ``WideTask``
    must surface the gold.
    """

    found = _reachable_strings(_tasks()[0])
    assert set(GOLD_A) <= found
    assert "A Secret Title" in found


def test_custody_exposes_counts_but_never_members() -> None:
    custody = GoldCustody(_tasks())
    assert custody.gold_count("wide-aaaa000000000000") == 3
    for attribute in ("gold_arxiv_ids", "answer_titles", "gold"):
        assert not hasattr(custody, attribute)


def test_custody_scores_without_returning_gold_members() -> None:
    custody = GoldCustody(_tasks())
    score = custody.score("wide-aaaa000000000000", ["2501.00001", "9999.99999"])
    assert score.hit_count == 1
    assert score.gold_count == 3
    assert score.predicted_count == 2
    assert set(vars(score)) == {
        "task_id",
        "iou",
        "recall",
        "precision",
        "gold_count",
        "predicted_count",
        "hit_count",
    }
    assert not (_reachable_strings(score) & set(GOLD_A))


def test_custody_copies_the_prediction_before_scoring() -> None:
    """A candidate must not be able to mutate its answer after intersection."""

    custody = GoldCustody(_tasks())
    live = ["2501.00001"]
    score = custody.score("wide-aaaa000000000000", live)
    live.append("2501.00002")
    assert score.hit_count == 1


def test_custody_rejects_an_unknown_task() -> None:
    custody = GoldCustody(_tasks())
    with pytest.raises(KeyError):
        custody.score("wide-not-a-task", [])


def test_custody_rejects_duplicate_task_ids() -> None:
    task = _tasks()[0]
    with pytest.raises(ValueError, match="duplicate task id"):
        GoldCustody((task, task))


def test_wide_task_refuses_an_empty_gold_set() -> None:
    """An empty gold scores 1.0 against an empty prediction. Never allow it."""

    with pytest.raises(ValueError, match="no gold arxiv ids"):
        WideTask(task_id="wide-x", question="q", gold_arxiv_ids=())


# ---------------------------------------------------------------------------
# The identity bridge: the silent-zero failure mode.
# ---------------------------------------------------------------------------


def test_bridge_emits_bare_ids_for_arxiv_primary_identities() -> None:
    identities = (SourceIdentity(source_id="arxiv:2501.00001"),)
    assert arxiv_predictions_from_identities(identities) == ("2501.00001",)


def test_bridge_finds_the_arxiv_alias_of_a_doi_primary_work() -> None:
    """The case the whole bridge exists for.

    ``merge_identities`` sorts by ``source_id``, so a work reached by both DOI
    and arXiv gets a DOI primary key. Wide gold is arXiv-only. Reading the
    primary alone would score a genuine hit as a miss.
    """

    identities = (
        SourceIdentity(
            source_id="doi:10.1234/abcd", aliases=("arxiv:2501.00002",), title="Paper"
        ),
    )
    assert arxiv_predictions_from_identities(identities) == ("2501.00002",)


def test_bridge_handles_old_style_identifiers() -> None:
    identities = (SourceIdentity(source_id="arxiv:cs/0409043"),)
    assert arxiv_predictions_from_identities(identities) == ("cs/0409043",)


def test_bridge_strips_version_suffixes() -> None:
    identities = (SourceIdentity(source_id="arXiv:2501.00001v3"),)
    assert arxiv_predictions_from_identities(identities) == ("2501.00001",)


def test_bridge_drops_works_with_no_arxiv_identity() -> None:
    identities = (SourceIdentity(source_id="doi:10.1234/only-a-doi"),)
    assert arxiv_predictions_from_identities(identities) == ()


def test_bridge_dedupes_across_identities() -> None:
    identities = (
        SourceIdentity(source_id="arxiv:2501.00001"),
        SourceIdentity(source_id="doi:10.9/x", aliases=("arxiv:2501.00001",)),
    )
    assert arxiv_predictions_from_identities(identities) == ("2501.00001",)


def test_bridge_end_to_end_scores_a_perfect_prediction_as_one() -> None:
    """The positive case. A bridge that always returned () passes every test above."""

    custody = GoldCustody(_tasks())
    identities = (
        SourceIdentity(source_id="arxiv:2501.00001"),
        SourceIdentity(source_id="doi:10.1/x", aliases=("arxiv:2501.00002",)),
        SourceIdentity(source_id="arxiv:cs/0409043"),
    )
    predicted = arxiv_predictions_from_identities(identities)
    score = custody.score("wide-aaaa000000000000", predicted)
    assert score.iou == 1.0
    assert score.recall == 1.0
    assert score.precision == 1.0


# ---------------------------------------------------------------------------
# Bundle loading, including the duplicate-row rule.
# ---------------------------------------------------------------------------


def _write_bundle(path: Path, records: list[dict[str, object]]) -> Path:
    path.write_text(
        "\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8"
    )
    return path


def test_load_wide_tasks_ignores_deep_records(tmp_path: Path) -> None:
    bundle = _write_bundle(
        tmp_path / "b.jsonl",
        [
            {"question": "wide q", "answer": ["T"], "arxiv_id": ["2501.1"], "type": "wide"},
            {"question": "deep q", "answer": ["T"], "arxiv_id": ["2501.2"], "type": "deep"},
        ],
    )
    tasks = load_wide_tasks(bundle)
    assert len(tasks) == 1
    assert tasks[0].question == "wide q"


def test_load_wide_tasks_collapses_a_byte_identical_duplicate_row(tmp_path: Path) -> None:
    record = {
        "question": "repeated q",
        "answer": ["T"],
        "arxiv_id": ["2501.1", "2501.2"],
        "type": "wide",
    }
    bundle = _write_bundle(tmp_path / "b.jsonl", [record, dict(record)])
    tasks = load_wide_tasks(bundle)
    assert len(tasks) == 1


def test_load_wide_tasks_keeps_a_repeated_question_with_different_gold(
    tmp_path: Path,
) -> None:
    """No-alarm counterpart: dedup must key on gold too, not on question alone."""

    bundle = _write_bundle(
        tmp_path / "b.jsonl",
        [
            {"question": "same q", "answer": ["T"], "arxiv_id": ["2501.1"], "type": "wide"},
            {"question": "same q", "answer": ["U"], "arxiv_id": ["2501.9"], "type": "wide"},
        ],
    )
    tasks = load_wide_tasks(bundle)
    assert len(tasks) == 2
    assert len({item.task_id for item in tasks}) == 2


def test_load_wide_tasks_is_independent_of_row_order(tmp_path: Path) -> None:
    records = [
        {"question": f"q{i}", "answer": ["T"], "arxiv_id": [f"2501.{i}"], "type": "wide"}
        for i in range(5)
    ]
    forward = load_wide_tasks(_write_bundle(tmp_path / "f.jsonl", records))
    backward = load_wide_tasks(_write_bundle(tmp_path / "r.jsonl", list(reversed(records))))
    assert [item.task_id for item in forward] == [item.task_id for item in backward]


def test_missing_bundle_env_var_names_the_regeneration_recipe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(BUNDLE_ENV_VAR, raising=False)
    with pytest.raises(FileNotFoundError, match="decrypt_benchmark"):
        load_wide_tasks()


def test_derive_task_id_is_stable_and_disambiguates_occurrences() -> None:
    first = derive_task_id("a question")
    assert first == derive_task_id("a question")
    assert first != derive_task_id("a different question")
    assert derive_task_id("a question", 1) == f"{first}-2"


# ---------------------------------------------------------------------------
# Subsample determinism and achieved precision.
# ---------------------------------------------------------------------------


def test_select_subsample_takes_everything_when_size_is_not_binding() -> None:
    ids = ["c", "a", "b"]
    assert select_subsample(ids) == ("a", "b", "c")
    assert select_subsample(ids, 99) == ("a", "b", "c")


def test_select_subsample_is_deterministic_under_a_seed() -> None:
    ids = [f"wide-{i:04d}" for i in range(50)]
    assert select_subsample(ids, 10, seed=7) == select_subsample(ids, 10, seed=7)


def test_select_subsample_is_independent_of_input_order() -> None:
    ids = [f"wide-{i:04d}" for i in range(50)]
    assert select_subsample(ids, 10, seed=7) == select_subsample(
        list(reversed(ids)), 10, seed=7
    )


def test_select_subsample_actually_varies_with_the_seed() -> None:
    """No-alarm assertion: a 'deterministic' selector that ignores the seed
    would pass every determinism test above while silently freezing one sample."""

    ids = [f"wide-{i:04d}" for i in range(200)]
    assert select_subsample(ids, 10, seed=1) != select_subsample(ids, 10, seed=2)


def test_achieved_half_width_inverts_the_frozen_planning_function() -> None:
    stats = publication_stats()
    for n in (97, 171, 385, 399, 400, 1068):
        half_width = achieved_half_width(n)
        assert stats.required_n_for_proportion_half_width(half_width, 0.5) <= n
        assert stats.required_n_for_proportion_half_width(half_width - 1e-6, 0.5) > n


def test_wide_family_precision_is_tier_b_and_underpowered() -> None:
    """The concrete number this lane commits to for N = 399 distinct Wide tasks."""

    half_width = achieved_half_width(399)
    assert half_width == pytest.approx(0.049063, abs=5e-6)
    assert precision_tier(half_width) == "TIER_B_committed"
    assert half_width > 0.03  # mandatory UNDERPOWERED label


def test_precision_tier_ladder_matches_the_frozen_plan() -> None:
    stats = publication_stats()
    expected = {
        "TIER_A_full": (0.03, 1068),
        "TIER_B_committed": (0.05, 385),
        "TIER_C_reduced": (0.075, 171),
        "TIER_D_minimum_inferential": (0.1, 97),
    }
    for tier, (half_width, required_n) in expected.items():
        assert precision_tier(half_width) == tier
        assert stats.required_n_for_proportion_half_width(half_width, 0.5) == required_n
    assert precision_tier(0.5) == "BELOW_TIER_D_DESCRIPTIVE_ONLY"


# ---------------------------------------------------------------------------
# The subsample manifest.
# ---------------------------------------------------------------------------


def test_manifest_contains_no_gold_and_no_question_text() -> None:
    tasks = _tasks()
    manifest = build_subsample_manifest(
        tasks, selected_task_ids=[item.task_id for item in tasks], seed=0, raw_wide_rows=2
    )
    blob = json.dumps(manifest)
    for secret in GOLD_A + GOLD_B:
        assert secret not in blob
    for task in tasks:
        assert task.question not in blob
        for title in task.answer_titles:
            assert title not in blob


def test_manifest_hash_is_reproducible_and_order_independent() -> None:
    tasks = _tasks()
    ids = [item.task_id for item in tasks]
    first = build_subsample_manifest(tasks, selected_task_ids=ids, seed=0, raw_wide_rows=2)
    second = build_subsample_manifest(tasks, selected_task_ids=list(reversed(ids)), seed=0, raw_wide_rows=2)
    assert first["content_hash"] == second["content_hash"]


def test_manifest_hash_changes_when_the_selection_changes() -> None:
    """No-alarm assertion: a constant hash would 'reproduce' perfectly."""

    tasks = _tasks()
    everything = build_subsample_manifest(
        tasks, selected_task_ids=[item.task_id for item in tasks], seed=0, raw_wide_rows=2
    )
    subset = build_subsample_manifest(
        tasks, selected_task_ids=[tasks[0].task_id], seed=0, raw_wide_rows=2
    )
    assert everything["content_hash"] != subset["content_hash"]


def test_manifest_hash_excludes_itself() -> None:
    tasks = _tasks()
    manifest = build_subsample_manifest(
        tasks, selected_task_ids=[item.task_id for item in tasks], seed=0, raw_wide_rows=2
    )
    body = {k: v for k, v in manifest.items() if k != "content_hash"}
    assert canonical_manifest_hash(body) == manifest["content_hash"]


def test_manifest_rejects_task_ids_outside_the_population() -> None:
    with pytest.raises(ValueError, match="not in the population"):
        build_subsample_manifest(
            _tasks(), selected_task_ids=["wide-ghost"], seed=0, raw_wide_rows=2
        )


def test_manifest_records_the_seed_as_inert_when_everything_is_selected() -> None:
    tasks = _tasks()
    manifest = build_subsample_manifest(
        tasks, selected_task_ids=[item.task_id for item in tasks], seed=11, raw_wide_rows=2
    )
    selection = manifest["selection"]
    assert isinstance(selection, dict)
    assert selection["seed_is_inert"] is True
    subset = build_subsample_manifest(
        tasks, selected_task_ids=[tasks[0].task_id], seed=11, raw_wide_rows=2
    )
    subset_selection = subset["selection"]
    assert isinstance(subset_selection, dict)
    assert subset_selection["seed_is_inert"] is False
