from dataclasses import replace

import pytest

from orion.study.p9.structural_world import (
    Atom,
    AtomType,
    FailureRecord,
    GluingVerdict,
    GoldKind,
    GoldTarget,
    MechanicView,
    P9StructuralWorld,
    Relation,
    RelationType,
    ViewMode,
    classify_cycle_gluing,
    failure_history_pair,
    relation_semantics_pair,
    transport_gluing_pair,
)


def test_same_surface_and_topology_different_relation_semantics_change_gold():
    supports, defeats = relation_semantics_pair()

    assert supports.fingerprint(ViewMode.SURFACE) == defeats.fingerprint(ViewMode.SURFACE)
    assert supports.fingerprint(ViewMode.TOPOLOGY) == defeats.fingerprint(ViewMode.TOPOLOGY)
    assert supports.fingerprint(ViewMode.TYPED) != defeats.fingerprint(ViewMode.TYPED)

    assert supports.gold == GoldTarget(GoldKind.MECHANIC_SELECTION, "m_integrate")
    assert defeats.gold == GoldTarget(GoldKind.MECHANIC_SELECTION, "m_reopen")


def test_same_typed_graph_different_transport_maps_change_gluing_gold():
    compatible, obstructed = transport_gluing_pair()

    assert compatible.fingerprint(ViewMode.TOPOLOGY) == obstructed.fingerprint(ViewMode.TOPOLOGY)
    assert compatible.fingerprint(ViewMode.TYPED) == obstructed.fingerprint(ViewMode.TYPED)
    assert compatible.fingerprint(ViewMode.SEMANTIC) != obstructed.fingerprint(ViewMode.SEMANTIC)

    cycle = ("chart_a", "chart_b", "chart_c", "chart_a")
    assert classify_cycle_gluing(compatible, cycle) is GluingVerdict.GLUE
    assert classify_cycle_gluing(obstructed, cycle) is GluingVerdict.OBSTRUCTION
    assert compatible.gold == GoldTarget(GoldKind.GLUING, GluingVerdict.GLUE.value)
    assert obstructed.gold == GoldTarget(GoldKind.GLUING, GluingVerdict.OBSTRUCTION.value)


def test_missing_transport_is_unknown_not_obstruction():
    compatible, _ = transport_gluing_pair()
    missing = replace(
        compatible,
        world_id="transport-missing",
        transports=compatible.transports[:-1],
        gold=GoldTarget(GoldKind.GLUING, GluingVerdict.UNKNOWN.value),
    )
    missing.verify()

    assert classify_cycle_gluing(
        missing, ("chart_a", "chart_b", "chart_c", "chart_a")
    ) is GluingVerdict.UNKNOWN


def test_same_current_state_different_negative_history_changes_correct_mechanic():
    clean, learned_failure = failure_history_pair()

    assert clean.fingerprint(ViewMode.CURRENT) == learned_failure.fingerprint(ViewMode.CURRENT)
    assert clean.fingerprint(ViewMode.SEMANTIC) != learned_failure.fingerprint(ViewMode.SEMANTIC)
    assert clean.gold == GoldTarget(GoldKind.MECHANIC_SELECTION, "m_primary")
    assert learned_failure.gold == GoldTarget(GoldKind.MECHANIC_SELECTION, "m_fallback")


def test_surface_permutation_changes_words_not_semantic_identity_or_gold():
    world, _ = relation_semantics_pair()
    permuted = world.permute_surface(seed="p9-hostile-permutation")

    assert permuted.fingerprint(ViewMode.SURFACE) != world.fingerprint(ViewMode.SURFACE)
    assert permuted.fingerprint(ViewMode.SEMANTIC) == world.fingerprint(ViewMode.SEMANTIC)
    assert permuted.gold == world.gold


def test_dangling_relation_target_is_rejected():
    world, _ = relation_semantics_pair()
    bad_relation = Relation(
        relation_id="r_bad",
        source_id="evidence",
        target_id="missing",
        relation_type=RelationType.SUPPORTS,
        surface_label="linked",
    )
    broken = replace(world, relations=world.relations + (bad_relation,))

    with pytest.raises(ValueError, match="unknown target"):
        broken.verify()


def test_duplicate_atom_and_mechanic_ids_are_rejected():
    world, _ = relation_semantics_pair()
    with pytest.raises(ValueError, match="duplicate atom id"):
        replace(world, atoms=world.atoms + (world.atoms[0],)).verify()

    with pytest.raises(ValueError, match="duplicate mechanic id"):
        replace(world, mechanics=world.mechanics + (world.mechanics[0],)).verify()


def test_failure_history_referencing_unknown_mechanic_is_rejected():
    world, _ = failure_history_pair()
    bad = FailureRecord(
        record_id="f_bad",
        mechanic_id="missing",
        reason="precondition_failed",
        context_atom_ids=("problem",),
    )

    with pytest.raises(ValueError, match="unknown mechanic"):
        replace(world, history=(bad,)).verify()


def test_mechanic_cannot_encode_scientific_or_adoption_authority():
    atom = Atom("problem", AtomType.CLAIM, "problem")
    mechanic = MechanicView(
        mechanic_id="m",
        surface_label="do thing",
        read_atom_ids=("problem",),
        write_atom_ids=("problem",),
        preconditions=("evidence_present",),
        effects=("candidate_state_change",),
        failure_modes=("insufficient_evidence",),
        cost=1.0,
        can_authorize=True,
    )
    world = P9StructuralWorld(
        world_id="authority-laundering",
        atoms=(atom,),
        relations=(),
        transports=(),
        mechanics=(mechanic,),
        history=(),
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, "m"),
    )

    with pytest.raises(ValueError, match="cannot authorize"):
        world.verify()


def test_gold_target_is_not_part_of_any_model_view_fingerprint():
    world, _ = relation_semantics_pair()
    alternate_gold = replace(
        world,
        world_id="alternate-gold",
        gold=GoldTarget(GoldKind.MECHANIC_SELECTION, "m_reopen"),
    )
    alternate_gold.verify()

    for mode in ViewMode:
        assert world.fingerprint(mode) == alternate_gold.fingerprint(mode)


def test_topology_collision_is_intentional_on_both_hostile_pair_families():
    relation_left, relation_right = relation_semantics_pair()
    transport_left, transport_right = transport_gluing_pair()

    assert relation_left.fingerprint(ViewMode.TOPOLOGY) == relation_right.fingerprint(
        ViewMode.TOPOLOGY
    )
    assert transport_left.fingerprint(ViewMode.TOPOLOGY) == transport_right.fingerprint(
        ViewMode.TOPOLOGY
    )
