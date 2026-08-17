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

from orion.study.p2.cases import (
    PUBLISHED_PROBE_ROUTES,
    PUBLISHED_PROBES_PER_ROUTE,
    CaseFamily,
    build_tasks,
    suite_fingerprint,
)
from orion.study.p2.corpus import (
    TOPIC_COUNT,
    DiscoveryRoute,
    DiscoveryWorld,
    Topic,
    build_world,
    is_relevant,
    validate_generated_vocabulary,
    validate_topic_plans,
)
from orion.study.p2.corpus import (
    _AUTHORED_TOPIC_PLANS,
    _TOPIC_PLANS,
    _TopicPlan,
    _label_tokens,
)
from orion.study.p2.freeze import (
    DEFAULT_ROOT,
    FROZEN_SEED,
    MANIFEST_FILE,
    MAX_FILE_BYTES,
    PROVENANCE,
    TOPICS_FILE,
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
    """If every probe could be tried, allocation and stopping would be free.

    Checked against the probes each task is actually *published*, not against the
    world-wide vocabulary. The world-wide count grew with the corpus, which makes the
    world-wide form of this assertion pass more and more easily while saying nothing
    — the binding constraint is the space a single task must search.
    """

    suite = load_suite()
    for task in suite.tasks:
        published = sum(len(probes) for _, probes in task.public_route_probes)
        assert task.budget.max_route_calls < published, task.task_id


# --------------------------------------------------------------------------
# Scale: the power commitment, and holding difficulty fixed while N moves
# --------------------------------------------------------------------------


def test_the_suite_meets_the_frozen_power_commitment() -> None:
    """`STATISTICAL_PLAN_V1.json` committed this family to TIER_B: n >= 385.

    The family's n is host-owned, so a shortfall is something the world can be made
    to fix rather than a fact to report around. This asserts it was.
    """

    manifest = load_manifest()
    assert manifest["task_count"] >= 385, manifest["task_count"]
    assert manifest["task_count"] == manifest["topic_count"] * len(CaseFamily)
    assert manifest["topic_count"] == TOPIC_COUNT


def test_published_probe_space_stays_the_size_the_superseded_world_had() -> None:
    """Per-route probe space is bounded, and bounded at the value it always had.

    The superseded 20-task world published one key per route per topic over four
    topics: four probes per route, sixteen against a twelve-call budget. Publishing
    all 78 topics' keys would have kept the inequality true while turning the
    semantic route — whose correct key shares no token with the question by
    construction — from a four-way trial into a 78-way lottery, collapsing recall for
    every system for a reason that has nothing to do with route governance. Holding
    the bound at four is what makes this a change of denominator and nothing else.
    """

    suite = load_suite()
    assert PUBLISHED_PROBES_PER_ROUTE == 4
    for task in suite.tasks:
        published = dict(task.public_route_probes)
        assert set(published) == {route.value for route in PUBLISHED_PROBE_ROUTES}
        for route, probes in published.items():
            assert len(probes) == PUBLISHED_PROBES_PER_ROUTE, (task.task_id, route)
            assert len(set(probes)) == len(probes), (task.task_id, route)


def test_every_task_is_published_its_own_key_on_every_published_route() -> None:
    """A bounded probe set is only fair if the answer is inside it."""

    suite = load_suite()
    for task in suite.tasks:
        topic = suite.world.topic(task.topic_id)
        relevant = [item for item in suite.world.documents if is_relevant(item, topic)]
        published = dict(task.public_route_probes)
        for route in PUBLISHED_PROBE_ROUTES:
            own = set()
            for document in relevant:
                own.update(document.keys_for(route))
            assert own, (task.task_id, route.value)
            assert own <= set(published[route.value]), (task.task_id, route.value)


# --------------------------------------------------------------------------
# Topic-plan invariants. Each is checked against the real plan set, where it must
# stay silent, and against a plan set broken in exactly the way it exists to catch.
# --------------------------------------------------------------------------


def _plan_pair() -> tuple[_TopicPlan, _TopicPlan]:
    return _TOPIC_PLANS[0], _TOPIC_PLANS[len(_AUTHORED_TOPIC_PLANS)]


def test_the_plan_validator_is_silent_on_the_real_plan_set() -> None:
    """The no-alarm half. A validator that fires on everything catches nothing."""

    assert validate_topic_plans(_TOPIC_PLANS) == ()
    assert validate_generated_vocabulary(_TOPIC_PLANS[len(_AUTHORED_TOPIC_PLANS):]) == ()


def test_lexical_and_semantic_tokens_are_disjoint_within_every_topic() -> None:
    authored, generated = _plan_pair()
    for plan in _TOPIC_PLANS:
        lexical = set(plan.lexical_key.lower().split())
        semantic = set(plan.semantic_key.lower().split())
        assert not (lexical & semantic), plan.topic_id

    # Alarm: give one topic a semantic key built from its own lexical vocabulary.
    broken = replace(generated, semantic_key=generated.lexical_key)
    problems = validate_topic_plans((authored, broken))
    assert any("shares" in item and "lexical key" in item for item in problems), problems


def test_no_access_key_is_shared_between_topics() -> None:
    """Route lookup is exact-key membership, so a shared key crosses the wires."""

    for field in ("lexical_key", "semantic_key", "reformulation_key", "restricted_key"):
        keys = [getattr(plan, field) for plan in _TOPIC_PLANS]
        assert len(set(keys)) == len(keys), field

    # Alarm: hand a second topic the first topic's lexical key.
    authored, generated = _plan_pair()
    broken = replace(generated, lexical_key=authored.lexical_key)
    problems = validate_topic_plans((authored, broken))
    assert any("shared by topics" in item for item in problems), problems


def test_concept_tokens_are_globally_unique_to_one_topic() -> None:
    """A concept claimed twice would let one topic's gold rule admit another's docs."""

    owners: dict[str, list[str]] = {}
    for plan in _TOPIC_PLANS:
        for concept in plan.required_concepts:
            owners.setdefault(concept, []).append(plan.topic_id)
    duplicated = {k: v for k, v in owners.items() if len(v) > 1}
    assert not duplicated, duplicated

    # And the world agrees: no document satisfies two topics' rules at once.
    world = load_suite().world
    for document in world.documents:
        matching = [t.topic_id for t in world.topics if is_relevant(document, t)]
        assert len(matching) <= 1, (document.doc_id, matching)

    # Alarm: two topics requiring the same concepts.
    authored, generated = _plan_pair()
    broken = replace(generated, required_concepts=authored.required_concepts,
                     partial_concept=authored.partial_concept)
    problems = validate_topic_plans((authored, broken))
    assert any("claimed by topics" in item for item in problems), problems


def test_topic_labels_share_at_most_one_token_so_screening_cannot_cross_topics() -> None:
    """`offline_systems._on_topic` needs two shared tokens; labels must not supply them.

    A record's text embeds its topic label, so two labels sharing two tokens would
    make one topic's records screen as on-topic for another topic's question.
    """

    tokens = [(p.topic_id, _label_tokens(p.label)) for p in _TOPIC_PLANS]
    for outer in range(len(tokens)):
        for inner in range(outer + 1, len(tokens)):
            shared = tokens[outer][1] & tokens[inner][1]
            assert len(shared) <= 1, (tokens[outer][0], tokens[inner][0], sorted(shared))

    # Alarm: two topics sharing a label.
    authored, generated = _plan_pair()
    broken = replace(generated, label=authored.label)
    problems = validate_topic_plans((authored, broken))
    assert any("share" in item and "screen as on-topic" in item for item in problems), problems


def test_generated_paraphrase_keys_carry_no_spelling_shortcut() -> None:
    """The paraphrase routes must be unreachable by characters as well as by tokens.

    The semantic and reformulation keys share no *token* with the question by
    construction, which is what makes them paraphrase-only. But a system orders
    probes with a character-similarity term as well as a token term, so a shared
    spelling — the same syllable in the label and in the semantic key — ranks the
    correct probe without any word in common. This is the invariant that caught a
    real defect: three successive arithmetic token layouts each left such a
    signature, and the correct semantic probe ranked first for 71 of 74 generated
    topics instead of spreading across all four ranks as the authored topics do.
    """

    generated = _TOPIC_PLANS[len(_AUTHORED_TOPIC_PLANS):]
    assert validate_generated_vocabulary(generated) == ()

    # Alarm: rebuild a semantic key from a syllable the label already uses.
    plan = generated[0]
    label_token = sorted(_label_tokens(plan.label))[0]
    broken = replace(plan, semantic_key=f"{label_token[:3]}xyzmos {plan.semantic_key}")
    problems = validate_generated_vocabulary((broken,))
    assert any("opening 3 characters" in item for item in problems), problems


# --------------------------------------------------------------------------
# Sharding
# --------------------------------------------------------------------------


def test_shards_round_trip_and_every_one_stays_under_the_ceiling() -> None:
    """The committed suite is sharded, and the shards reassemble to the same suite."""

    manifest = load_manifest()
    shards = manifest["shards"]
    assert len(shards["world"]) >= 1
    assert len(shards["tasks"]) >= 1
    assert shards["topics"] == [TOPICS_FILE]

    for name, recorded in sorted(manifest["files"].items()):
        path = DEFAULT_ROOT / name
        assert path.is_file(), name
        assert path.stat().st_size == recorded["bytes"] , name
        assert recorded["bytes"] <= MAX_FILE_BYTES, (name, recorded["bytes"])

    # Round trip: the sharded bytes rebuild the object the seed produces.
    loaded = load_suite()
    assert loaded.fingerprint == manifest["suite_fingerprint"]
    assert build_suite(FROZEN_SEED).fingerprint == loaded.fingerprint
    assert len(loaded.world.documents) == manifest["document_count"]
    assert len(loaded.tasks) == manifest["task_count"]
    # Sharding must not reorder or duplicate.
    doc_ids = [item.doc_id for item in loaded.world.documents]
    assert doc_ids == sorted(doc_ids)
    assert len(set(doc_ids)) == len(doc_ids)
    task_ids = [item.task_id for item in loaded.tasks]
    assert task_ids == sorted(task_ids)
    assert len(set(task_ids)) == len(task_ids)


def test_a_missing_shard_is_refused_rather_than_silently_shortening_the_corpus(
    tmp_path: Path,
) -> None:
    """The alarm half. A short corpus with a complete-gold claim is the worst case."""

    for name in sorted(load_manifest()["files"]):
        (tmp_path / name).write_text(
            (DEFAULT_ROOT / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    # No-alarm: the copy loads and matches before anything is removed.
    assert load_suite(tmp_path).fingerprint == load_manifest()["suite_fingerprint"]

    world_shards = sorted(tmp_path.glob("world-*.json"))
    if len(world_shards) < 2:  # pragma: no cover - only if the corpus stops needing shards
        pytest.skip("corpus currently fits in a single world shard")
    world_shards[-1].unlink()
    with pytest.raises(ValueError, match="missing shard indices"):
        load_suite(tmp_path)


def test_verify_notices_a_shard_that_no_hash_covers(tmp_path: Path) -> None:
    """Per-file hashes all match while the loaded suite holds unsigned material."""

    manifest = load_manifest()
    for name in sorted(manifest["files"]):
        (tmp_path / name).write_text(
            (DEFAULT_ROOT / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    (tmp_path / MANIFEST_FILE).write_text(
        (DEFAULT_ROOT / MANIFEST_FILE).read_text(encoding="utf-8"), encoding="utf-8"
    )
    assert verify(tmp_path).ok

    smuggled = tmp_path / "world-900.json"
    smuggled.write_text(
        json.dumps(
            {
                "schema_version": manifest["corpus_schema_version"],
                "seed": manifest["seed"],
                "shard_index": 900,
                "shard_count": 2,
                "documents": [],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="world-.* has 3 shards but declares 2"):
        verify(tmp_path)


def test_gold_completeness_is_recomputed_over_the_whole_corpus_at_scale() -> None:
    """Completeness is asserted document-by-document, both directions, at full size."""

    suite = load_suite()
    assert len(suite.world.documents) >= 1000
    assert len(suite.tasks) >= 385
    checked = 0
    for task in suite.tasks:
        topic = suite.world.topic(task.topic_id)
        gold = frozenset(task.protected_gold.gold_doc_ids)
        assert completeness_violations(suite.world, topic, gold) == (), task.task_id
        checked += len(suite.world.documents)
    assert checked == len(suite.tasks) * len(suite.world.documents)
