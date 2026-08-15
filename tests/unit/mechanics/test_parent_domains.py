from orion.mechanics import DOMAIN_CATALOG, MechanicCell, apply_parent_domain_hypotheses, candidate_parent_domain_ids, generate_mechanic_questions


def test_scientific_language_parent_domains_include_computational_linguistics_and_data_integration():
    cell = MechanicCell("ABSORB.SCIENTIFIC_LANGUAGE.v0", "Interpret scientific language.", "fixture")
    domain_ids = candidate_parent_domain_ids(cell)
    assert "computational-linguistics" in domain_ids
    assert "data-integration-entity-resolution" in domain_ids
    assert all(domain_id in DOMAIN_CATALOG for domain_id in domain_ids)


def test_reopen_parent_domains_include_truth_maintenance():
    cell = MechanicCell("REOPEN.DEPENDENCY.v0", "Reopen dependent closure.", "fixture")
    assert "truth-maintenance-incremental-reasoning" in candidate_parent_domain_ids(cell)


def test_parent_domain_hypotheses_close_only_seed_question_not_search_coverage():
    cell = MechanicCell("SEARCH.ROUTE.v0", "Select search routes.", "fixture")
    updated = apply_parent_domain_hypotheses(cell)
    dimensions = {item.dimension.value for item in generate_mechanic_questions(updated)}
    assert "PARENT_DISCIPLINE" not in dimensions
    assert "SEARCH_COVERAGE" in dimensions
    assert any("search seeds only" in item for item in updated.empirical_open_coordinates)
