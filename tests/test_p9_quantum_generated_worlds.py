from orion.study.p9.quantum_generated_worlds import (
    QuantumHostileFamily,
    QuantumViewMode,
    deterministic_information_ceiling,
    generate_quantum_hostile_pair,
    generate_quantum_pairs,
    quantum_view_fingerprint,
    quantum_view_payload,
)
from orion.study.p9.quantum_obstruction import QuantumObstructionVerdict


def test_entanglement_pair_collides_until_semantic_target_is_exposed():
    pair = generate_quantum_hostile_pair(
        QuantumHostileFamily.ENTANGLEMENT,
        seed="orion-q-entanglement-hostile",
    )
    left, right = pair.cases

    assert {left.gold, right.gold} == {
        QuantumObstructionVerdict.EXPRESSIVITY_OBSTRUCTION,
        QuantumObstructionVerdict.INVARIANT_COMPATIBLE,
    }
    assert quantum_view_fingerprint(pair, left, QuantumViewMode.SURFACE) == quantum_view_fingerprint(
        pair, right, QuantumViewMode.SURFACE
    )
    assert quantum_view_fingerprint(pair, left, QuantumViewMode.CONTRACT) == quantum_view_fingerprint(
        pair, right, QuantumViewMode.CONTRACT
    )
    assert quantum_view_fingerprint(pair, left, QuantumViewMode.SEMANTIC) != quantum_view_fingerprint(
        pair, right, QuantumViewMode.SEMANTIC
    )


def test_complex_phase_pair_collides_until_semantic_target_is_exposed():
    pair = generate_quantum_hostile_pair(
        QuantumHostileFamily.COMPLEX_PHASE,
        seed="orion-q-phase-hostile",
    )
    left, right = pair.cases

    assert quantum_view_fingerprint(pair, left, QuantumViewMode.SURFACE) == quantum_view_fingerprint(
        pair, right, QuantumViewMode.SURFACE
    )
    assert quantum_view_fingerprint(pair, left, QuantumViewMode.CONTRACT) == quantum_view_fingerprint(
        pair, right, QuantumViewMode.CONTRACT
    )
    assert quantum_view_fingerprint(pair, left, QuantumViewMode.SEMANTIC) != quantum_view_fingerprint(
        pair, right, QuantumViewMode.SEMANTIC
    )


def test_balanced_quantum_information_lattice_has_exact_half_half_one_ceilings():
    pairs = generate_quantum_pairs(seed="orion-q-information-lattice", pairs_per_family=5)

    surface = deterministic_information_ceiling(pairs, mode=QuantumViewMode.SURFACE)
    contract = deterministic_information_ceiling(pairs, mode=QuantumViewMode.CONTRACT)
    semantic = deterministic_information_ceiling(pairs, mode=QuantumViewMode.SEMANTIC)

    assert surface["sample_count"] == 20
    assert surface["distinct_view_count"] == 10
    assert surface["collision_bucket_count"] == 10
    assert surface["max_deterministic_accuracy"] == 0.5

    assert contract["sample_count"] == 20
    assert contract["distinct_view_count"] == 10
    assert contract["collision_bucket_count"] == 10
    assert contract["max_deterministic_accuracy"] == 0.5

    assert semantic["sample_count"] == 20
    assert semantic["distinct_view_count"] == 20
    assert semantic["collision_bucket_count"] == 0
    assert semantic["max_deterministic_accuracy"] == 1.0


def test_generator_is_deterministic_and_pair_identities_are_disjoint():
    first = generate_quantum_pairs(seed="orion-q-determinism", pairs_per_family=4)
    second = generate_quantum_pairs(seed="orion-q-determinism", pairs_per_family=4)

    assert [pair.pair_digest for pair in first] == [pair.pair_digest for pair in second]
    assert len({pair.pair_id for pair in first}) == len(first)
    case_ids = [case.case_id for pair in first for case in pair.cases]
    assert len(set(case_ids)) == len(case_ids)


def test_model_views_exclude_evaluator_family_case_ids_and_gold():
    pair = generate_quantum_hostile_pair(
        QuantumHostileFamily.COMPLEX_PHASE,
        seed="orion-q-no-gold-leakage",
    )
    case = pair.cases[0]

    for mode in QuantumViewMode:
        text = str(quantum_view_payload(pair, case, mode))
        assert pair.family.value not in text
        assert pair.pair_id not in text
        assert case.case_id not in text
        assert case.initial.state_id not in text
        assert case.target.state_id not in text
        assert case.gold.value not in text
