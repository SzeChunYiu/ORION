from __future__ import annotations

from orion.discovery.structural_navigation import (
    NavigationOption,
    StructuralAddress,
    StructuralCorrespondence,
    build_navigation_receipt,
    evaluate_structural_correspondence,
    pareto_navigation_frontier,
)


def _address(address_id: str, domain_id: str) -> StructuralAddress:
    return StructuralAddress(
        address_id=address_id,
        domain_id=domain_id,
        role_ids=("state", "transition", "terminal"),
        relation_signature_ids=("transition-preserves-invariant", "terminal-reachable"),
        invariant_ids=("rank",),
        obstruction_ids=("local-greedy-trap",),
        validation_kind="FORMAL_PROOF",
        interface_ids=("finite-state",),
    )


def test_cross_domain_exactness_depends_on_structure_not_labels() -> None:
    source = _address("source", "algebra")
    target = _address("target", "compiler")
    correspondence = StructuralCorrespondence(
        correspondence_id="map",
        source_address_id="source",
        target_address_id="target",
        mapped_target_role_ids=target.role_ids,
        mapped_target_relation_ids=target.relation_signature_ids,
        mapped_target_invariant_ids=target.invariant_ids,
        mapped_target_obstruction_ids=target.obstruction_ids,
        mapped_target_interface_ids=target.interface_ids,
        validation_correspondence=True,
    )
    result = evaluate_structural_correspondence(source, target, correspondence)
    assert result.exact
    assert result.vector == (0, 0, 0, 0, 0, 0)


def test_surface_similarity_does_not_hide_relation_debt() -> None:
    source = _address("same-words-source", "domain-a")
    target = _address("same-words-target", "domain-b")
    correspondence = StructuralCorrespondence(
        correspondence_id="bad-map",
        source_address_id=source.address_id,
        target_address_id=target.address_id,
        mapped_target_role_ids=target.role_ids,
        mapped_target_relation_ids=("terminal-reachable",),
        mapped_target_invariant_ids=(),
        mapped_target_obstruction_ids=(),
        mapped_target_interface_ids=target.interface_ids,
        validation_correspondence=False,
    )
    result = evaluate_structural_correspondence(source, target, correspondence)
    assert not result.exact
    assert result.missing_relation_ids == ("transition-preserves-invariant",)
    assert result.validation_mismatch


def test_pareto_navigation_keeps_tradeoffs_and_removes_dominated_routes() -> None:
    fast_narrow = NavigationOption(
        option_id="fast-narrow",
        reachable_contract_ids=("t1",),
        distortion_vector=(0, 1),
        resource_vector=(1, 1),
        authority_debt=0,
        origin_trace_id="o1",
    )
    slow_broad = NavigationOption(
        option_id="slow-broad",
        reachable_contract_ids=("t1", "t2"),
        distortion_vector=(0, 0),
        resource_vector=(5, 5),
        authority_debt=0,
        origin_trace_id="o2",
    )
    dominated = NavigationOption(
        option_id="dominated",
        reachable_contract_ids=("t1",),
        distortion_vector=(1, 2),
        resource_vector=(3, 3),
        authority_debt=1,
        origin_trace_id="o3",
    )
    frontier = pareto_navigation_frontier((fast_narrow, slow_broad, dominated))
    assert tuple(row.option_id for row in frontier) == ("fast-narrow", "slow-broad")


def test_navigation_receipt_is_non_authorizing_and_content_bound() -> None:
    source = _address("source", "a")
    target = _address("target", "b")
    correspondence = StructuralCorrespondence(
        correspondence_id="map",
        source_address_id="source",
        target_address_id="target",
        mapped_target_role_ids=target.role_ids,
        mapped_target_relation_ids=target.relation_signature_ids,
        mapped_target_invariant_ids=target.invariant_ids,
        mapped_target_obstruction_ids=target.obstruction_ids,
        mapped_target_interface_ids=target.interface_ids,
        validation_correspondence=True,
    )
    distortion = evaluate_structural_correspondence(source, target, correspondence)
    option = NavigationOption(
        option_id="route",
        reachable_contract_ids=("target",),
        distortion_vector=distortion.vector,
        resource_vector=(2, 3),
        authority_debt=0,
        origin_trace_id="origin",
    )
    receipt = build_navigation_receipt(
        problem_address_id="target",
        options=(option,),
        correspondence_results=(("map", distortion),),
    )
    receipt.verify()
    assert receipt.frontier_option_ids == ("route",)
    assert not receipt.grants_scientific_validity
    assert not receipt.grants_novelty_authority
