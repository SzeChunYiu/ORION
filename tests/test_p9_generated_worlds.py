import re

import pytest

from orion.study.p9.generated_worlds import (
    CorpusSplit,
    HostileFamily,
    generate_balanced_split,
    generate_corpus,
    generate_pair,
)
from orion.study.p9.identifiability import analyze_identifiability
from orion.study.p9.structural_world import GluingVerdict, ViewMode, classify_cycle_gluing


FORBIDDEN_MODEL_VISIBLE_WORDS = {
    "relation",
    "transport",
    "history",
    "support",
    "defeat",
    "glue",
    "obstruction",
    "primary",
    "fallback",
    "train",
    "dev",
    "test",
}


def _model_visible_identity_and_surface_tokens(pair):
    tokens = []
    for world in pair.worlds:
        tokens.append(world.world_id)
        for atom in world.atoms:
            tokens.extend((atom.atom_id, atom.surface_label))
        for relation in world.relations:
            tokens.extend((relation.relation_id, relation.surface_label))
        for transport in world.transports:
            tokens.append(transport.transport_id)
        for mechanic in world.mechanics:
            tokens.extend((mechanic.mechanic_id, mechanic.surface_label))
        for record in world.history:
            tokens.append(record.record_id)
    return tokens


@pytest.mark.parametrize("family", list(HostileFamily))
def test_generate_pair_is_deterministic_and_remints_on_seed_change(family):
    first = generate_pair(family, "seed-alpha")
    replay = generate_pair(family, "seed-alpha")
    other = generate_pair(family, "seed-beta")

    assert first == replay
    assert first.pair_digest == replay.pair_digest
    assert first.pair_id != other.pair_id
    assert first.pair_digest != other.pair_digest
    assert {world.world_id for world in first.worlds}.isdisjoint(
        {world.world_id for world in other.worlds}
    )


@pytest.mark.parametrize("family", list(HostileFamily))
def test_generated_model_visible_ids_and_surfaces_are_opaque_and_family_neutral(family):
    raw_seed = "super-secret-generator-seed"
    pair = generate_pair(family, raw_seed)

    for token in _model_visible_identity_and_surface_tokens(pair):
        lowered = token.lower()
        assert raw_seed not in lowered
        assert not any(word in lowered for word in FORBIDDEN_MODEL_VISIBLE_WORDS)
        assert re.fullmatch(r"[a-z][0-9a-f]{12,24}", token), token


@pytest.mark.parametrize("family", list(HostileFamily))
def test_every_generated_hostile_pair_requires_different_gold(family):
    pair = generate_pair(family, "different-gold")

    assert pair.worlds[0].gold != pair.worlds[1].gold


def test_relation_family_collides_until_relation_semantics_are_visible():
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "relation-case")
    left, right = pair.worlds

    assert left.fingerprint(ViewMode.SURFACE) == right.fingerprint(ViewMode.SURFACE)
    assert left.fingerprint(ViewMode.TOPOLOGY) == right.fingerprint(ViewMode.TOPOLOGY)
    assert left.fingerprint(ViewMode.TYPED) != right.fingerprint(ViewMode.TYPED)


def test_transport_family_collides_through_typed_view_then_separates_on_transport_values():
    pair = generate_pair(HostileFamily.TRANSPORT_GLUING, "transport-case")
    compatible, obstructed = pair.worlds
    cycle = tuple(atom.atom_id for atom in compatible.atoms) + (compatible.atoms[0].atom_id,)

    assert compatible.fingerprint(ViewMode.TYPED) == obstructed.fingerprint(ViewMode.TYPED)
    assert compatible.fingerprint(ViewMode.CURRENT) != obstructed.fingerprint(ViewMode.CURRENT)
    assert classify_cycle_gluing(compatible, cycle) is GluingVerdict.GLUE
    assert classify_cycle_gluing(obstructed, cycle) is GluingVerdict.OBSTRUCTION


def test_history_family_collides_through_current_then_separates_on_admitted_history():
    pair = generate_pair(HostileFamily.FAILURE_HISTORY, "history-case")
    clean, negative = pair.worlds

    assert clean.fingerprint(ViewMode.CURRENT) == negative.fingerprint(ViewMode.CURRENT)
    assert clean.fingerprint(ViewMode.SEMANTIC) != negative.fingerprint(ViewMode.SEMANTIC)


def test_balanced_generated_split_preserves_analytic_view_accuracy_ceilings():
    split = generate_balanced_split(
        seed="ceiling-seed",
        split=CorpusSplit.TRAIN,
        pairs_per_family=7,
    )
    expected = {
        ViewMode.SURFACE: 1 / 2,
        ViewMode.TOPOLOGY: 1 / 2,
        ViewMode.TYPED: 2 / 3,
        ViewMode.CURRENT: 5 / 6,
        ViewMode.SEMANTIC: 1.0,
    }

    for mode, ceiling in expected.items():
        report = analyze_identifiability(split.worlds, mode)
        assert report.deterministic_accuracy_ceiling == pytest.approx(ceiling)
        assert report.is_identifying is (mode is ViewMode.SEMANTIC)


def test_train_dev_test_are_deterministic_and_identity_disjoint_by_construction():
    corpus = generate_corpus(
        seed="corpus-seed",
        train_pairs_per_family=5,
        dev_pairs_per_family=2,
        test_pairs_per_family=3,
    )
    replay = generate_corpus(
        seed="corpus-seed",
        train_pairs_per_family=5,
        dev_pairs_per_family=2,
        test_pairs_per_family=3,
    )

    assert corpus == replay
    corpus.verify()

    train_ids = corpus.train.identity_tokens
    dev_ids = corpus.dev.identity_tokens
    test_ids = corpus.test.identity_tokens
    assert train_ids.isdisjoint(dev_ids)
    assert train_ids.isdisjoint(test_ids)
    assert dev_ids.isdisjoint(test_ids)


def test_corpus_seed_and_counts_are_content_bound_in_manifest_digest():
    base = generate_corpus(
        seed="manifest-a",
        train_pairs_per_family=2,
        dev_pairs_per_family=1,
        test_pairs_per_family=1,
    )
    changed_seed = generate_corpus(
        seed="manifest-b",
        train_pairs_per_family=2,
        dev_pairs_per_family=1,
        test_pairs_per_family=1,
    )
    changed_count = generate_corpus(
        seed="manifest-a",
        train_pairs_per_family=3,
        dev_pairs_per_family=1,
        test_pairs_per_family=1,
    )

    assert base.manifest_digest != changed_seed.manifest_digest
    assert base.manifest_digest != changed_count.manifest_digest
    assert base.manifest()["schema"] == "P9.GeneratedCorpus.v0"
    assert "gold" not in repr(base.train.model_manifest()).lower()


def test_pair_metadata_is_evaluator_side_and_never_changes_model_view_fingerprints():
    pair = generate_pair(HostileFamily.RELATION_SEMANTICS, "metadata-separation")
    world = pair.worlds[0]

    for mode in ViewMode:
        payload = world.view_payload(mode)
        serialized = repr(payload).lower()
        assert pair.family.value.lower() not in serialized
        assert pair.pair_id.lower() not in serialized
        assert "gold" not in serialized
