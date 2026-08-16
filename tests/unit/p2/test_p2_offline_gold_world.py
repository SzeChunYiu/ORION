"""The frozen offline world: determinism, completeness, reachability.

Each invariant is expressed as a checker that returns problems, and each checker
is exercised twice — once against the real world, where it must stay silent, and
once against a world deliberately broken in the way the checker exists to catch.
A checker only ever run against material that fails it has not been validated; it
has been demonstrated. The no-alarm half is the half that catches a checker which
fires on everything.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from orion.study.p2.cases import build_tasks, suite_fingerprint
from orion.study.p2.corpus import (
    DiscoveryRoute,
    DiscoveryWorld,
    Topic,
    build_world,
    is_relevant,
)
from orion.study.p2.freeze import (
    DEFAULT_ROOT,
    FROZEN_SEED,
    PROVENANCE,
    build_suite,
    load_manifest,
    load_suite,
    verify,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


# --------------------------------------------------------------------------
# Invariant checkers
# --------------------------------------------------------------------------


def completeness_violations(world: DiscoveryWorld, topic: Topic, gold: frozenset[str]) -> tuple[str, ...]:
    """No document may satisfy the relevance rule while being absent from gold.

    This is the whole claim of a complete-gold world, so it is asserted over
    every document rather than sampled. The rule is `is_relevant`; the gold is a
    materialized cache of it; the two must agree in both directions.
    """

    problems: list[str] = []
    for document in world.documents:
        relevant = is_relevant(document, topic)
        listed = document.doc_id in gold
        if relevant and not listed:
            problems.append(f"relevant but absent from gold: {document.doc_id}")
        if listed and not relevant:
            problems.append(f"in gold but fails the relevance rule: {document.doc_id}")
    return tuple(problems)


def reachability_violations(world: DiscoveryWorld, topic: Topic, task_map: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    """Every gold work must be reachable, and the map must match the corpus.

    Citation reachability is recomputed from the reference edges rather than
    trusted, because a declared map that has drifted from the graph it describes
    is exactly the kind of quiet inconsistency that makes a route metric wrong
    without making anything fail.
    """

    problems: list[str] = []
    gold_docs = [item for item in world.documents if is_relevant(item, topic)]
    gold_identities = {item.content_identity for item in gold_docs}

    recomputed: dict[str, set[str]] = {route.value: set() for route in DiscoveryRoute}
    for document in gold_docs:
        for route in DiscoveryRoute:
            if route is DiscoveryRoute.CITATION:
                continue
            if document.keys_for(route):
                recomputed[route.value].add(document.content_identity)
    for seed in world.documents:
        for target in world.citation_reachable(seed.doc_id):
            reached = world.by_id.get(target)
            if reached is not None and is_relevant(reached, topic):
                recomputed[DiscoveryRoute.CITATION.value].add(reached.content_identity)

    for route_name, expected in sorted(recomputed.items()):
        declared = set(task_map.get(route_name, ()))
        if declared != expected:
            problems.append(
                f"{route_name}: declared {sorted(declared)} != corpus-derived {sorted(expected)}"
            )

    covered = set().union(*recomputed.values()) if recomputed else set()
    for orphan in sorted(gold_identities - covered):
        problems.append(f"gold work reachable by no route: {orphan}")
    return tuple(problems)


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------


def test_regeneration_reproduces_the_committed_fingerprint() -> None:
    manifest = load_manifest()
    assert build_suite(FROZEN_SEED).fingerprint == manifest["suite_fingerprint"]
    assert verify().ok, verify().problems


@pytest.mark.parametrize("hash_seed", ["0", "1", "12345"])
def test_regeneration_is_deterministic_across_processes(hash_seed: str) -> None:
    """Same-process regeneration proves nothing about `PYTHONHASHSEED`.

    Iterating an unsorted set of strings is stable within one interpreter and
    varies between them, so a suite that only reproduces in-process would still
    break in CI. This runs the generator in a fresh interpreter with the hash
    seed forced to differ.
    """

    env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONPATH=str(REPO_ROOT / "src"))
    result = subprocess.run(
        [sys.executable, "-m", "orion.study.p2.freeze", "--print-fingerprint"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == load_manifest()["suite_fingerprint"]


def test_a_different_seed_yields_a_different_suite() -> None:
    """No-alarm counterpart: the fingerprint tracks the world rather than a constant."""

    other = build_world(FROZEN_SEED + 1)
    assert other.content_hash != build_world(FROZEN_SEED).content_hash
    assert suite_fingerprint(other, build_tasks(other)) != load_manifest()["suite_fingerprint"]


def test_committed_files_match_the_manifest_and_round_trip() -> None:
    manifest = load_manifest()
    loaded = load_suite()
    assert loaded.fingerprint == manifest["suite_fingerprint"]
    assert len(loaded.world.documents) == manifest["document_count"]
    assert len(loaded.tasks) == manifest["task_count"]
    for name, entry in manifest["files"].items():
        assert (DEFAULT_ROOT / name).is_file()
        assert entry["bytes"] < 1_000_000, f"{name} exceeds the shard ceiling"


def test_the_frozen_artifact_states_its_provenance() -> None:
    """Redistribution has to be unambiguous, and the claim has to be on the record."""

    manifest = load_manifest()
    assert manifest["provenance"] == PROVENANCE
    assert "synthetic" in manifest["provenance"].lower()
    assert manifest["frozen_before_any_system_configured"] is True
    assert manifest["seed"] == FROZEN_SEED


# --------------------------------------------------------------------------
# Completeness by construction
# --------------------------------------------------------------------------


def test_gold_is_complete_by_construction_for_every_task() -> None:
    suite = load_suite()
    for task in suite.tasks:
        topic = suite.world.topic(task.topic_id)
        gold = frozenset(task.protected_gold.gold_doc_ids)
        assert completeness_violations(suite.world, topic, gold) == (), task.task_id


def test_the_completeness_checker_fires_on_an_incomplete_gold_set() -> None:
    """No-alarm validation: silence above must mean the world is right, not that
    the checker cannot speak."""

    suite = load_suite()
    task = suite.tasks[0]
    topic = suite.world.topic(task.topic_id)
    full = frozenset(task.protected_gold.gold_doc_ids)

    dropped = frozenset(sorted(full)[1:])
    assert completeness_violations(suite.world, topic, dropped), "dropping a gold id must be caught"

    intruder = full | {"filler:000"}
    assert completeness_violations(suite.world, topic, intruder), "an irrelevant id in gold must be caught"


def test_a_smuggled_relevant_document_is_caught() -> None:
    """The realistic failure: a document that satisfies the rule but was never listed."""

    suite = load_suite()
    task = suite.tasks[0]
    topic = suite.world.topic(task.topic_id)
    smuggled = replace(
        suite.world.documents[-1],
        doc_id="smuggled:001",
        content_identity="work:smuggled:001",
        concept_tags=tuple(sorted(topic.required_concepts)),
        access_keys=(),
        references=(),
    )
    tampered = DiscoveryWorld(
        schema_version=suite.world.schema_version,
        seed=suite.world.seed,
        documents=tuple(sorted((*suite.world.documents, smuggled), key=lambda d: d.doc_id)),
        topics=suite.world.topics,
    )
    problems = completeness_violations(
        tampered, topic, frozenset(task.protected_gold.gold_doc_ids)
    )
    assert any("smuggled:001" in item for item in problems)


def test_recall_denominator_counts_works_not_copies() -> None:
    """Republications and revisions must not inflate the denominator."""

    suite = load_suite()
    task = suite.tasks[0]
    gold = task.protected_gold
    assert len(gold.gold_content_identities) < len(gold.gold_doc_ids)
    assert len(set(gold.gold_content_identities)) == len(gold.gold_content_identities)


# --------------------------------------------------------------------------
# Reachability
# --------------------------------------------------------------------------


def test_every_gold_work_is_reachable_and_the_map_matches_the_corpus() -> None:
    suite = load_suite()
    for task in suite.tasks:
        topic = suite.world.topic(task.topic_id)
        declared = {name: items for name, items in task.protected_gold.route_reachable_identities}
        assert reachability_violations(suite.world, topic, declared) == (), task.task_id
        assert task.protected_gold.unreachable_content_identities == ()


def test_the_reachability_checker_fires_on_a_drifted_map() -> None:
    suite = load_suite()
    task = suite.tasks[0]
    topic = suite.world.topic(task.topic_id)
    declared = {name: items for name, items in task.protected_gold.route_reachable_identities}

    drifted = dict(declared)
    drifted[DiscoveryRoute.CITATION.value] = ()
    assert reachability_violations(suite.world, topic, drifted), "an emptied route must be caught"

    inflated = dict(declared)
    inflated[DiscoveryRoute.LEXICAL.value] = (*declared[DiscoveryRoute.LEXICAL.value], "work:invented")
    assert reachability_violations(suite.world, topic, inflated), "an invented entry must be caught"


def test_gold_is_split_across_routes_so_one_route_cannot_suffice() -> None:
    """If any single route reached all of it, route diversity would be unmeasurable."""

    suite = load_suite()
    for task in suite.tasks:
        gold = frozenset(task.protected_gold.gold_content_identities)
        for route in DiscoveryRoute:
            reachable = frozenset(task.protected_gold.reachable_via(route))
            assert reachable < gold, f"{task.task_id}: {route.value} reaches the whole gold set"


def test_semantic_keys_share_no_token_with_lexical_keys() -> None:
    """Paraphrase-only reachability is only real if the vocabularies are disjoint."""

    world = load_suite().world
    lexical_tokens = {
        token for probe in world.probes_for(DiscoveryRoute.LEXICAL) for token in probe.split()
    }
    semantic_tokens = {
        token for probe in world.probes_for(DiscoveryRoute.SEMANTIC) for token in probe.split()
    }
    assert not (lexical_tokens & semantic_tokens)


def test_citation_probes_are_earned_not_published() -> None:
    """Snowballing means chaining from a document you hold, so seeds are withheld."""

    suite = load_suite()
    for task in suite.tasks:
        view = task.public_view
        assert view.probes_for(DiscoveryRoute.CITATION) == ()
        assert view.probes_for(DiscoveryRoute.LEXICAL)


def test_the_public_view_carries_no_gold() -> None:
    """The access-control boundary, checked as data rather than trusted as a type.

    What must be absent is the answer (gold content identities) and the
    machine-readable rule (the concept-tag tokens relevance is decided by). The
    topic's *natural-language* vocabulary is deliberately present — a system that
    is not told what it is looking for is not doing discovery.
    """

    suite = load_suite()
    for task in suite.tasks:
        serialized = json.dumps(
            {
                "task_id": task.public_view.task_id,
                "question": task.public_view.question,
                "extraction": task.public_view.initial_extraction_question,
                "routes": list(task.public_view.available_routes),
                "probes": [list(item[1]) for item in task.public_view.route_probes],
            }
        )
        for identity in task.protected_gold.gold_content_identities:
            assert identity not in serialized
        for concept in task.protected_gold.relevance_rule_concepts:
            assert concept not in serialized


def test_budgets_do_not_admit_exhaustive_probing() -> None:
    """If every probe could be tried, allocation and stopping would be free."""

    suite = load_suite()
    total_probes = sum(
        len(suite.world.probes_for(route))
        for route in DiscoveryRoute
        if route is not DiscoveryRoute.CITATION
    )
    for task in suite.tasks:
        assert task.budget.max_route_calls < total_probes, task.task_id
