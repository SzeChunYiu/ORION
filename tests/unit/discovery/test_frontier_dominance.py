from fractions import Fraction

import pytest

from orion.discovery.frontier_dominance import (
    ClosureClass,
    ComparisonContract,
    DonorExplanation,
    IdentifyingExperiment,
    NoveltyLayer,
    ResourceVector,
    SemanticAtom,
    SemanticEdge,
    SystemProfile,
    TaskOutcome,
    assess_frontier_dominance,
    donor_expansion_is_residual_monotone,
    fair_dovetail_schedule,
    minimal_residual_families,
    minimal_superiority_destroying_mutations,
    pareto_minimum_identifying_portfolios,
    select_scalarized_portfolios,
)


def rv(compute: int, memory: int) -> ResourceVector:
    return ResourceVector.from_mapping({"compute": compute, "memory": memory})


def contract(*task_ids: str, matched: bool = True) -> ComparisonContract:
    return ComparisonContract(
        contract_id="C",
        task_ids=tuple(task_ids),
        information_contract_id="I",
        resource_contract_id="R",
        evaluator_id="E",
        same_candidate_visible_information=matched,
        same_tool_access=matched,
        donor_first_refusal=matched,
        frozen_before_outcomes=matched,
    )


def outcome(
    task_id: str,
    closure: ClosureClass,
    *,
    success: bool,
    cost: ResourceVector,
    false_promotion: bool = False,
    held_out: bool = False,
    counterfactual: bool = False,
) -> TaskOutcome:
    return TaskOutcome(
        task_id=task_id,
        closure_class=closure,
        correct=success,
        scientifically_admissible=success,
        false_promotion=false_promotion,
        resources=cost,
        held_out=held_out,
        counterfactual=counterfactual,
    )


def profile(system_id: str, *rows: TaskOutcome) -> SystemProfile:
    return SystemProfile(system_id, {row.task_id: row for row in rows})


def test_strong_frontier_dominance_requires_conservativity_and_strict_expansion():
    tasks = contract("old", "frontier-h", "frontier-c")
    donor = profile(
        "donor",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(4, 4)),
        outcome("frontier-h", ClosureClass.FRONTIER, success=False, cost=rv(4, 4), held_out=True),
        outcome(
            "frontier-c",
            ClosureClass.FRONTIER,
            success=False,
            cost=rv(4, 4),
            counterfactual=True,
        ),
    )
    candidate = profile(
        "candidate",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(3, 4)),
        outcome("frontier-h", ClosureClass.FRONTIER, success=True, cost=rv(3, 4), held_out=True),
        outcome(
            "frontier-c",
            ClosureClass.FRONTIER,
            success=True,
            cost=rv(3, 4),
            counterfactual=True,
        ),
    )
    report = assess_frontier_dominance(candidate, (donor,), contract=tasks)
    assert report.frontier_dominant
    assert report.triangulated_frontier_dominant
    assert report.strict_frontier_win_ids == ("frontier-h", "frontier-c")
    assert not report.grants_external_novelty_authority
    assert not report.grants_paper_authority


def test_frontier_win_cannot_compensate_for_old_closure_regression():
    tasks = contract("old", "new")
    donor = profile(
        "donor",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(1, 1)),
        outcome("new", ClosureClass.FRONTIER, success=False, cost=rv(1, 1)),
    )
    candidate = profile(
        "candidate",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=False, cost=rv(1, 1)),
        outcome("new", ClosureClass.FRONTIER, success=True, cost=rv(1, 1)),
    )
    report = assess_frontier_dominance(candidate, (donor,), contract=tasks)
    assert report.strict_frontier_win_ids == ("new",)
    assert report.donor_conservativity_violations == ("old",)
    assert not report.frontier_dominant


def test_unmatched_information_blocks_dominance_even_when_scores_look_good():
    tasks = contract("old", "new", matched=False)
    donor = profile(
        "donor",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(2, 2)),
        outcome("new", ClosureClass.FRONTIER, success=False, cost=rv(2, 2)),
    )
    candidate = profile(
        "candidate",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(1, 1)),
        outcome("new", ClosureClass.FRONTIER, success=True, cost=rv(1, 1)),
    )
    report = assess_frontier_dominance(candidate, (donor,), contract=tasks)
    assert not report.matched_contract
    assert not report.frontier_dominant


def test_resource_tradeoff_is_not_hidden_scalarized_into_superiority():
    tasks = contract("old", "new")
    donor = profile(
        "donor",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(1, 10)),
        outcome("new", ClosureClass.FRONTIER, success=False, cost=rv(1, 10)),
    )
    candidate = profile(
        "candidate",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(10, 1)),
        outcome("new", ClosureClass.FRONTIER, success=True, cost=rv(10, 1)),
    )
    report = assess_frontier_dominance(candidate, (donor,), contract=tasks)
    assert report.resource_violations == ("old",)
    assert not report.resource_noninferior
    assert not report.frontier_dominant


def test_false_promotion_is_noncompensatory():
    tasks = contract("old", "new")
    donor = profile(
        "donor",
        outcome("old", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(2, 2)),
        outcome("new", ClosureClass.FRONTIER, success=False, cost=rv(2, 2)),
    )
    candidate = profile(
        "candidate",
        outcome(
            "old",
            ClosureClass.DONOR_CLOSURE,
            success=False,
            false_promotion=True,
            cost=rv(1, 1),
        ),
        outcome("new", ClosureClass.FRONTIER, success=True, cost=rv(1, 1)),
    )
    report = assess_frontier_dominance(candidate, (donor,), contract=tasks)
    assert report.calibration_violations == ("old",)
    assert not report.frontier_dominant


def test_interaction_novelty_survives_when_all_component_atoms_are_donor_owned():
    atoms = (
        SemanticAtom("a", NoveltyLayer.METHOD, "A"),
        SemanticAtom("b", NoveltyLayer.REPRESENTATION, "B"),
        SemanticAtom("t", NoveltyLayer.MECHANISM, "T"),
    )
    edges = (SemanticEdge("join", ("a", "b"), "t", "COMPOSES", "J"),)
    residuals = minimal_residual_families(
        atoms,
        edges,
        (
            DonorExplanation(("D1", "D2"), ("a", "b", "t"), ()),
        ),
    )
    assert len(residuals) == 1
    assert residuals[0].interaction_only
    assert residuals[0].residual_edge_ids == ("join",)


def test_full_donor_absorption_yields_empty_residual():
    atoms = (SemanticAtom("a", NoveltyLayer.METHOD, "A"),)
    residuals = minimal_residual_families(
        atoms,
        (),
        (DonorExplanation(("D",), ("a",), ()),),
    )
    assert residuals[0].empty


def test_expanding_donor_family_cannot_increase_minimal_residual():
    atoms = (
        SemanticAtom("a", NoveltyLayer.METHOD, "A"),
        SemanticAtom("b", NoveltyLayer.REPRESENTATION, "B"),
        SemanticAtom("c", NoveltyLayer.QUESTION, "C"),
    )
    old = minimal_residual_families(
        atoms,
        (),
        (DonorExplanation(("D1",), ("a",), ()),),
    )
    new = minimal_residual_families(
        atoms,
        (),
        (
            DonorExplanation(("D1",), ("a",), ()),
            DonorExplanation(("D1", "D2"), ("a", "b"), ()),
        ),
    )
    assert donor_expansion_is_residual_monotone(old, new)
    assert new[0].residual_atom_ids == ("c",)


def test_residual_decomposition_remains_set_valued_when_nonunique():
    atoms = (
        SemanticAtom("a", NoveltyLayer.METHOD, "A"),
        SemanticAtom("b", NoveltyLayer.METHOD, "B"),
    )
    residuals = minimal_residual_families(
        atoms,
        (),
        (
            DonorExplanation(("D1",), ("a",), ()),
            DonorExplanation(("D2",), ("b",), ()),
        ),
    )
    assert {row.residual_atom_ids for row in residuals} == {("a",), ("b",)}


def test_pareto_identifying_portfolios_do_not_choose_hidden_scalarization():
    experiments = (
        IdentifyingExperiment("fast", ("p1", "p2"), rv(1, 8)),
        IdentifyingExperiment("small", ("p1", "p2"), rv(8, 1)),
        IdentifyingExperiment("dominated", ("p1", "p2"), rv(9, 9)),
        IdentifyingExperiment("half1", ("p1",), rv(1, 1)),
        IdentifyingExperiment("half2", ("p2",), rv(1, 1)),
    )
    portfolios = pareto_minimum_identifying_portfolios(("p1", "p2"), experiments)
    identities = {row.experiment_ids for row in portfolios}
    assert ("dominated",) not in identities
    assert ("fast",) in identities
    assert ("small",) in identities
    assert ("half1", "half2") in identities

    compute_cheap = select_scalarized_portfolios(
        portfolios, prices={"compute": 1, "memory": 10}
    )
    assert compute_cheap[0].experiment_ids == ("small",)
    assert compute_cheap[0].total_cost.scalar_cost(
        {"compute": 1, "memory": 10}
    ) == Fraction(18)


def test_price_vector_must_be_explicit_and_complete():
    vector = rv(1, 2)
    with pytest.raises(ValueError):
        vector.scalar_cost({"compute": 1})


def test_fair_dovetail_schedule_visits_every_finite_pair_by_finite_stage():
    rows = fair_dovetail_schedule(("g0", "g1", "g2"), max_stage=6)
    assert rows[:6] == (
        ("g0", 0),
        ("g0", 1),
        ("g1", 0),
        ("g0", 2),
        ("g1", 1),
        ("g2", 0),
    )
    assert ("g2", 3) in rows


def test_task_metadata_mismatch_is_rejected():
    tasks = contract("x")
    donor = profile(
        "donor",
        outcome("x", ClosureClass.DONOR_CLOSURE, success=True, cost=rv(1, 1)),
    )
    candidate = profile(
        "candidate",
        outcome("x", ClosureClass.FRONTIER, success=True, cost=rv(1, 1)),
    )
    with pytest.raises(ValueError):
        assess_frontier_dominance(candidate, (donor,), contract=tasks)


def test_minimal_superiority_destroying_mutations_identify_interactions():
    rows = minimal_superiority_destroying_mutations(
        ("w1", "w2"),
        {
            ("a",): ("w2",),
            ("b",): ("w1",),
            ("a", "b"): (),
            ("a", "b", "c"): (),
            ("d",): (),
        },
    )
    assert rows == (("d",), ("a", "b"))
