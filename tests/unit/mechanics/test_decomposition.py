from orion.mechanics import RAKL_SURFACE_TO_CHILDREN, expanded_mechanical_backlog, expanded_workflow_cells


_EXPECTED_RAKL_SURFACES = {
    "decomposition",
    "routing",
    "search_query_generation",
    "source_selection_reliability",
    "claim_extraction",
    "ontology_terminology_normalization",
    "mathematical_context_translation",
    "equivalence_similarity",
    "contextual_theory_gluing",
    "contradiction_diagnosis",
    "gap_discovery",
    "experiment_query_selection",
    "synthesis",
    "memory",
    "review",
    "benchmarking",
    "authority_promotion",
    "saturation_stopping",
    "prompting_context_policy",
    "capability_shaping",
    "software_architecture_execution",
    "research_portfolio_tree",
    "objective_evolution",
    "generator_transport",
}


def test_expanded_workflow_recovers_all_historical_rakl_surfaces_as_provenance():
    assert set(RAKL_SURFACE_TO_CHILDREN) == _EXPECTED_RAKL_SURFACES
    known_ids = {item.mechanic_id for item in expanded_workflow_cells()}
    assert all(child in known_ids for children in RAKL_SURFACE_TO_CHILDREN.values() for child in children)


def test_recursive_decomposition_exposes_more_than_a_thousand_open_questions():
    cells = expanded_workflow_cells()
    backlog = expanded_mechanical_backlog()
    assert len(cells) >= 59
    assert len(backlog) >= 1200
    # The point is not raw question count: every question remains typed to a mechanic.
    assert all(item.mechanic_id and item.dimension.value for item in backlog)
