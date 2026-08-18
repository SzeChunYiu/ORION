import pytest

from orion.study.p9.identifiability import analyze_identifiability
from orion.study.p9.structural_world import (
    ViewMode,
    failure_history_pair,
    relation_semantics_pair,
    transport_gluing_pair,
)


def test_surface_and_topology_are_nonidentifying_for_relation_semantics_pair():
    worlds = relation_semantics_pair()

    surface = analyze_identifiability(worlds, ViewMode.SURFACE)
    topology = analyze_identifiability(worlds, ViewMode.TOPOLOGY)
    typed = analyze_identifiability(worlds, ViewMode.TYPED)

    assert surface.is_identifying is False
    assert topology.is_identifying is False
    assert len(surface.collisions) == 1
    assert len(topology.collisions) == 1
    assert typed.is_identifying is True


def test_typed_graph_is_nonidentifying_when_local_transport_values_change_gold():
    worlds = transport_gluing_pair()

    typed = analyze_identifiability(worlds, ViewMode.TYPED)
    current = analyze_identifiability(worlds, ViewMode.CURRENT)

    assert typed.is_identifying is False
    assert len(typed.collisions) == 1
    assert current.is_identifying is True


def test_current_state_is_nonidentifying_when_admitted_history_changes_gold():
    worlds = failure_history_pair()

    current = analyze_identifiability(worlds, ViewMode.CURRENT)
    semantic = analyze_identifiability(worlds, ViewMode.SEMANTIC)

    assert current.is_identifying is False
    assert len(current.collisions) == 1
    assert semantic.is_identifying is True


def test_semantic_view_identifies_all_bootstrap_hostile_worlds():
    worlds = (
        *relation_semantics_pair(),
        *transport_gluing_pair(),
        *failure_history_pair(),
    )

    report = analyze_identifiability(worlds, ViewMode.SEMANTIC)

    assert report.sample_count == 6
    assert report.is_identifying is True
    assert report.collisions == ()


def test_collision_receipt_exposes_worlds_and_conflicting_targets_not_model_gold():
    report = analyze_identifiability(relation_semantics_pair(), ViewMode.TOPOLOGY)
    collision = report.collisions[0]

    assert collision.world_ids == ("relation-defeat", "relation-support")
    assert collision.targets == (
        "MECHANIC_SELECTION:m_integrate",
        "MECHANIC_SELECTION:m_reopen",
    )
    assert collision.fingerprint.startswith("sha256:")


def test_duplicate_world_identity_is_rejected():
    world, other = relation_semantics_pair()
    duplicate = type(other)(
        world_id=world.world_id,
        atoms=other.atoms,
        relations=other.relations,
        transports=other.transports,
        mechanics=other.mechanics,
        history=other.history,
        gold=other.gold,
    )

    with pytest.raises(ValueError, match="duplicate world id"):
        analyze_identifiability((world, duplicate), ViewMode.SEMANTIC)
