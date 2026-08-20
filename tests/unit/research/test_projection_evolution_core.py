from pathlib import Path
import importlib.util
import sys

MODULE = (
    Path(__file__).resolve().parents[3]
    / "research"
    / "extensions"
    / "meta-orion-recursive-scientific-evolution"
    / "projection_evolution_core.py"
)
spec = importlib.util.spec_from_file_location("projection_evolution_core", MODULE)
pe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = pe
spec.loader.exec_module(pe)


def test_f0_cegar_refines_exactly_three_base_coordinate_families():
    train = pe.base_pairs(seed=701, per_family=5)
    result = pe.cegar_refine(train)
    assert result.spec.coordinates == frozenset(
        {
            pe.Coordinate.EVIDENCE_ROUTE,
            pe.Coordinate.NEGATIVE_CAUSE,
            pe.Coordinate.AUTHORITY_ORIGIN,
        }
    )
    assert len(result.steps) == 3
    assert len({step.added_coordinate for step in result.steps}) == 3


def test_f1_generalizes_to_disjoint_base_holdout():
    train = pe.base_pairs(seed=703, per_family=4)
    f1 = pe.cegar_refine(train).spec
    holdout = pe.base_pairs(seed=709, per_family=7)
    result = pe.evaluate_projection(holdout, f1)
    assert result["accuracy"] == 1.0
    assert result["coordinate_count"] == 3


def test_f1_is_insufficient_for_unseen_obligation_provenance_family():
    f1 = pe.cegar_refine(pe.base_pairs(seed=719, per_family=5)).spec
    unseen = pe.obligation_pairs(seed=727, per_family=8)
    result = pe.evaluate_projection(unseen, f1)
    assert result["accuracy"] == 0.5
    assert result["family_accuracy"]["obligation_provenance_debt"] == 0.5
    assert all(pe.pair_is_spuriously_merged(pair, f1) for pair in unseen)


def test_dpair4_counterexample_refines_f1_to_f2_once():
    f1 = pe.cegar_refine(pe.base_pairs(seed=733, per_family=5)).spec
    development = pe.obligation_pairs(seed=739, per_family=6)
    result = pe.cegar_refine(development, initial=f1)
    assert result.spec.coordinates == f1.coordinates | {pe.Coordinate.OBLIGATION_PROVENANCE}
    assert len(result.steps) == 1
    assert result.steps[0].added_coordinate is pe.Coordinate.OBLIGATION_PROVENANCE


def test_f2_generalizes_to_disjoint_obligation_and_base_holdouts():
    f1 = pe.cegar_refine(pe.base_pairs(seed=743, per_family=5)).spec
    f2 = pe.cegar_refine(pe.obligation_pairs(seed=751, per_family=3), initial=f1).spec
    holdout = pe.base_pairs(seed=757, per_family=6) + pe.obligation_pairs(seed=761, per_family=6)
    result = pe.evaluate_projection(holdout, f2)
    assert result["accuracy"] == 1.0
    assert result["coordinate_count"] == 4


def test_full_lineage_is_fidelity_ceiling_across_all_families():
    pairs = pe.base_pairs(seed=769, per_family=7) + pe.obligation_pairs(seed=773, per_family=7)
    result = pe.evaluate_full_lineage(pairs)
    assert result["accuracy"] == 1.0


def test_two_generation_experiment_has_expected_subtraction_pattern():
    result = pe.two_generation_experiment(per_family=5)
    assert result["f0_coordinate_count"] == 0
    assert result["f1_coordinate_count"] == 3
    assert result["f1_holdout_accuracy"] == 1.0
    assert result["f1_new_family_accuracy_before_refinement"] == 0.5
    assert result["f2_coordinate_count"] == 4
    assert result["f2_new_family_holdout_accuracy"] == 1.0
    assert result["f2_all_family_holdout_accuracy"] == 1.0
    assert result["full_lineage_holdout_accuracy"] == 1.0


def test_refinement_witness_is_coordinate_difference_not_family_label():
    pair = pe.obligation_pairs(seed=787, per_family=1)[0]
    assert pe.differing_lineage_coordinates(pair) == (pe.Coordinate.OBLIGATION_PROVENANCE,)
    step = pe.refine_from_counterexample(pe.AbstractionSpec(), pair)
    assert step.added_coordinate is pe.Coordinate.OBLIGATION_PROVENANCE
