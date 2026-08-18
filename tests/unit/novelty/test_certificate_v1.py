"""ScientificNoveltyCertificate.v1 schema, hashing, and sealing."""

from orion.novelty import (
    SCHEMA_ID,
    NoveltyFinalState,
    REQUIRED_SEARCH_ROUTES,
    seal_certificate,
)
from orion.novelty.fixtures import example_supported_draft as _draft


def test_schema_id_and_required_routes_are_frozen():
    assert SCHEMA_ID == "ScientificNoveltyCertificate.v1"
    assert tuple(route.value for route in REQUIRED_SEARCH_ROUTES) == (
        "EXACT_TERM",
        "SYNONYM_FUNCTION_ONLY",
        "PROBLEM_DECOMPOSITION",
        "PARENT_DISCIPLINE_HISTORY",
        "BENCHMARK_IMPLEMENTATION",
        "CITED_BY_RELATED",
        "HOSTILE_ALREADY_SOLVED",
    )


def test_sealed_certificate_contains_every_issue_field():
    cert = seal_certificate(_draft())
    assert cert.schema_id == SCHEMA_ID
    assert cert.claim_text
    assert cert.problem_task_definition
    assert cert.claimed_mechanism_decomposition
    assert cert.closest_prior_by_term
    assert cert.closest_prior_by_function
    assert cert.parent_discipline_mechanisms
    assert cert.benchmark_implementation_routes
    assert cert.hostile_already_solved_route is not None
    assert cert.overlap_classifications
    assert cert.absorption_decisions
    assert cert.smallest_residual
    assert cert.residual_implementation_evidence
    assert cert.discriminating_experiment.experiment_id
    assert cert.unresolved_search_routes == ()
    assert cert.final_state in NoveltyFinalState
    assert len(cert.content_hash) == 64
    assert len(cert.snapshot_hash) == 64
    assert cert.search_snapshot.snapshot_date == "2026-08-17"
    payload = cert.to_payload()
    for key in (
        "claim_text",
        "problem_task_definition",
        "claimed_mechanism_decomposition",
        "closest_prior_by_term",
        "closest_prior_by_function",
        "parent_discipline_mechanisms",
        "benchmark_implementation_routes",
        "hostile_already_solved_route",
        "overlap_classifications",
        "absorption_decisions",
        "smallest_residual",
        "residual_implementation_evidence",
        "discriminating_experiment",
        "unresolved_sources",
        "unresolved_search_routes",
        "final_state",
        "content_hash",
        "snapshot_hash",
        "search_snapshot",
    ):
        assert key in payload


def test_content_hash_is_stable_and_excludes_hash_fields():
    first = seal_certificate(_draft())
    second = seal_certificate(_draft())
    assert first.content_hash == second.content_hash
    mutated = seal_certificate(_draft(claim_text="A different claim text."))
    assert mutated.content_hash != first.content_hash
    payload = first.to_payload()
    assert "content_hash" not in first.hash_payload()
    assert payload["content_hash"] == first.content_hash
