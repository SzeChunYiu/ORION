from __future__ import annotations

import pytest

from orion.discovery.synthesis_modes import (
    CandidateElement,
    CompositionEdge,
    DonorFragment,
    ProvenanceClass,
    SemanticElementKind,
    StructuralTransferMap,
    SynthesisMode,
    SynthesisTerminal,
    TransferStrength,
    assess_candidate_synthesis,
    build_candidate_synthesis_record,
    minimal_semantic_residuals,
    minimal_successful_subsets,
    minimum_separating_panels,
)


def _element(
    element_id: str,
    *,
    local: bool = False,
    donors: tuple[str, ...] = (),
    generated: str | None = None,
    kind: SemanticElementKind = SemanticElementKind.OPERATOR,
) -> CandidateElement:
    return CandidateElement(
        element_id=element_id,
        kind=kind,
        equivalence_class_id=f"eq:{element_id}",
        in_local_closure=local,
        donor_source_ids=donors,
        generated_origin_id=generated,
    )


def _fragment(fragment_id: str, element_id: str, domain: str = "target") -> DonorFragment:
    return DonorFragment(
        fragment_id=fragment_id,
        domain_id=domain,
        element_ids=(element_id,),
        required_interface_ids=(),
        guarantee_ids=(f"g:{fragment_id}",),
    )


def test_a1_b2_c3_is_irreducible_three_way_donor_composition() -> None:
    elements = (
        _element("a1", donors=("donor-a",)),
        _element("b2", donors=("donor-b",)),
        _element("c3", donors=("donor-c",)),
    )
    fragments = (
        _fragment("A", "a1"),
        _fragment("B", "b2"),
        _fragment("C", "c3"),
    )
    edge = CompositionEdge(
        edge_id="compose-abc",
        operator_id="registered-product",
        input_fragment_ids=("A", "B", "C"),
        output_contract_ids=("target",),
        in_registered_product_closure=True,
        required_obligation_ids=("typed",),
        discharged_obligation_ids=("typed",),
        generated_origin_id=None,
    )
    record = build_candidate_synthesis_record(
        candidate_id="abc",
        target_domain_id="target",
        target_contract_id="target",
        elements=elements,
        donor_fragments=fragments,
        composition_edges=(edge,),
        old_regime_reaches_target=False,
        candidate_reaches_target=True,
        hidden_consequence_passed=True,
        independent_validity_passed=True,
        successful_donor_subsets=(("A", "B", "C"),),
    )
    result = assess_candidate_synthesis(record)
    assert result.mode is SynthesisMode.DONOR_COMPOSITION
    assert result.terminal is SynthesisTerminal.DONOR_COMPOSITION_ONLY
    assert result.interaction_order == 3
    assert result.generated_residual_element_ids == ()


def test_novel_bridge_is_residual_even_when_nodes_are_donor_owned() -> None:
    elements = (
        _element("a", donors=("A",)),
        _element("b", donors=("B",)),
    )
    fragments = (_fragment("A", "a"), _fragment("B", "b"))
    edge = CompositionEdge(
        edge_id="new-bridge",
        operator_id="bridge",
        input_fragment_ids=("A", "B"),
        output_contract_ids=("target",),
        in_registered_product_closure=False,
        required_obligation_ids=("scope", "semantics"),
        discharged_obligation_ids=("scope", "semantics"),
        generated_origin_id="origin:new-bridge",
    )
    result = assess_candidate_synthesis(
        build_candidate_synthesis_record(
            candidate_id="bridge-candidate",
            target_domain_id="target",
            target_contract_id="target",
            elements=elements,
            donor_fragments=fragments,
            composition_edges=(edge,),
            old_regime_reaches_target=False,
            candidate_reaches_target=True,
            hidden_consequence_passed=True,
            independent_validity_passed=True,
            successful_donor_subsets=(("A", "B"),),
        )
    )
    assert result.mode is SynthesisMode.HYBRID
    assert result.terminal is SynthesisTerminal.HYBRID_SYNTHESIS_CANDIDATE
    assert result.generated_residual_edge_ids == ("new-bridge",)


def test_exact_cross_domain_structure_transfer() -> None:
    element = _element("source-lemma", donors=("remote-source",))
    fragment = _fragment("remote", "source-lemma", domain="remote-domain")
    transfer = StructuralTransferMap(
        map_id="map-remote-target",
        source_domain_id="remote-domain",
        target_domain_id="target-domain",
        mapped_element_ids=("source-lemma",),
        required_relation_ids=("order", "composition"),
        preserved_relation_ids=("order", "composition"),
        target_obligation_ids=("boundary",),
        discharged_target_obligation_ids=("boundary",),
        validation_correspondence=True,
        negative_twin_id="twin-1",
    )
    assert transfer.strength is TransferStrength.EXACT_INTERPRETATION
    result = assess_candidate_synthesis(
        build_candidate_synthesis_record(
            candidate_id="transfer",
            target_domain_id="target-domain",
            target_contract_id="target",
            elements=(element,),
            donor_fragments=(fragment,),
            transfer_maps=(transfer,),
            old_regime_reaches_target=False,
            candidate_reaches_target=True,
            hidden_consequence_passed=True,
            independent_validity_passed=True,
            successful_donor_subsets=(("remote",),),
        )
    )
    assert result.mode is SynthesisMode.STRUCTURAL_TRANSFER
    assert result.terminal is SynthesisTerminal.STRUCTURAL_TRANSFER_ONLY


def test_partial_analogy_retains_transfer_debt() -> None:
    element = _element("source", donors=("remote",))
    fragment = _fragment("remote", "source", domain="remote-domain")
    transfer = StructuralTransferMap(
        map_id="partial",
        source_domain_id="remote-domain",
        target_domain_id="target-domain",
        mapped_element_ids=("source",),
        required_relation_ids=("r1", "r2"),
        preserved_relation_ids=("r1",),
        target_obligation_ids=("o1",),
        discharged_target_obligation_ids=(),
        validation_correspondence=False,
        negative_twin_id=None,
    )
    assert transfer.strength is TransferStrength.PARTIAL_ANALOGY
    result = assess_candidate_synthesis(
        build_candidate_synthesis_record(
            candidate_id="partial-transfer",
            target_domain_id="target-domain",
            target_contract_id="target",
            elements=(element,),
            donor_fragments=(fragment,),
            transfer_maps=(transfer,),
            old_regime_reaches_target=False,
            candidate_reaches_target=True,
            hidden_consequence_passed=True,
            independent_validity_passed=True,
            successful_donor_subsets=(("remote",),),
        )
    )
    assert result.mode is SynthesisMode.UNRESOLVED
    assert result.terminal is SynthesisTerminal.CANNOT_CHECK
    assert result.partial_transfer_map_ids == ("partial",)


def test_partial_structure_plus_generated_rest_is_hybrid() -> None:
    elements = (
        _element("known-module", donors=("d",)),
        _element("missing-invariant", generated="origin:invariant", kind=SemanticElementKind.CONSTRAINT),
    )
    fragment = _fragment("d", "known-module")
    result = assess_candidate_synthesis(
        build_candidate_synthesis_record(
            candidate_id="complete-the-rest",
            target_domain_id="math",
            target_contract_id="theorem",
            elements=elements,
            donor_fragments=(fragment,),
            old_regime_reaches_target=False,
            candidate_reaches_target=True,
            hidden_consequence_passed=True,
            independent_validity_passed=True,
            successful_donor_subsets=(("d",),),
        )
    )
    assert result.mode is SynthesisMode.HYBRID
    assert result.terminal is SynthesisTerminal.HYBRID_SYNTHESIS_CANDIDATE
    assert result.generated_residual_element_ids == ("missing-invariant",)


def test_generated_candidate_absorbed_by_donor_is_not_residual() -> None:
    element = _element("x", donors=("prior",), generated="origin:x")
    assert element.provenance is ProvenanceClass.DONOR_MAPPED


def test_old_regime_reach_blocks_jump_credit() -> None:
    result = assess_candidate_synthesis(
        build_candidate_synthesis_record(
            candidate_id="already-reachable",
            target_domain_id="math",
            target_contract_id="t",
            elements=(_element("old", local=True),),
            old_regime_reaches_target=True,
            candidate_reaches_target=True,
            hidden_consequence_passed=True,
            independent_validity_passed=True,
        )
    )
    assert result.mode is SynthesisMode.FIXED_REGIME_SEARCH
    assert result.terminal is SynthesisTerminal.NO_JUMP_SEARCH


def test_minimal_successful_subsets_preserves_plural_solutions() -> None:
    rows = minimal_successful_subsets(
        ("A", "B", "C"),
        (("A", "B"), ("A", "B", "C"), ("B", "C")),
    )
    assert rows == (("A", "B"), ("B", "C"))


def test_minimal_semantic_residuals_can_be_nonunique() -> None:
    residuals = minimal_semantic_residuals(
        ("a", "b", "c"),
        (("a", "b"), ("a", "c")),
    )
    assert residuals == (("b",), ("c",))


def test_minimum_theorem_identifying_panels_is_exact_set_cover() -> None:
    panels = minimum_separating_panels(
        ("theta-vs-constant", "theta-vs-weakened", "theta-vs-leaky"),
        {
            "e1": ("theta-vs-constant", "theta-vs-weakened"),
            "e2": ("theta-vs-leaky",),
            "e3": ("theta-vs-constant",),
        },
    )
    assert panels == (("e1", "e2"),)


def test_uncovered_alternative_pair_is_rejected() -> None:
    with pytest.raises(ValueError, match="do not identify"):
        minimum_separating_panels(("a", "b"), {"e": ("a",)})
