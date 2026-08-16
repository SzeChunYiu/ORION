from dataclasses import FrozenInstanceError

import pytest

from orion.knowledge.retrieval_benchmark import (
    BenchmarkVerdict,
    CorpusArtifactIdentity,
    GroundTruthFactorization,
    GroundTruthLayer,
    RetrievalRouteTrial,
    RouteComparisonVerdict,
    RouteTrialVerdict,
    compare_retrieval_routes,
    evaluate_retrieval_route_trial,
    validate_corpus_artifact,
    validate_ground_truth_factorization,
)


def _artifact(**overrides) -> CorpusArtifactIdentity:
    values = dict(
        corpus_id="MIR-test",
        source_id="Anikethh/Methodology-Inspiration-Retrieval",
        revision="dc0545adffad7cd15c730f4a7bb9388d6440a47c",
        path="data/test_chronological_df.csv",
        content_sha="ae1d293db3dd755232e527c3f8d58800ba7e06ad",
        size_bytes=5169467,
        identity_observed=True,
    )
    values.update(overrides)
    return CorpusArtifactIdentity(**values)


def _trial(**overrides) -> RetrievalRouteTrial:
    values = dict(
        trial_id="trial-lexical",
        route_id="LEXICAL",
        corpus_id="MIR-test",
        corpus_revision="dc0545adffad7cd15c730f4a7bb9388d6440a47c",
        corpus_artifact_sha="ae1d293db3dd755232e527c3f8d58800ba7e06ad",
        task_packet_id="mir-eval-packet-v1",
        query_packet_id="query-v1",
        top_k=3,
        base_model_id="same-model",
        base_model_config_id="temperature-0",
        output_contract_id="ranked-paper-ids-v1",
        evaluator_id="mir-evaluator-v1",
        resource_ids=("paper-index",),
        resource_delta_declared=False,
        hidden_labels_exposed=False,
        query_frozen_before_labels=True,
        execution_observed=True,
        corpus_candidate_ids=("surface", "gold-A", "gold-B", "other"),
        designated_relevant_ids=("gold-A", "gold-B"),
        retrieved_candidate_ids=("surface", "gold-A", "other"),
    )
    values.update(overrides)
    return RetrievalRouteTrial(**values)


def test_pinned_corpus_artifact_is_valid():
    assert validate_corpus_artifact(_artifact()).verdict is BenchmarkVerdict.VALID


def test_unpinned_revision_cannot_support_benchmark():
    report = validate_corpus_artifact(_artifact(revision=""))
    assert report.verdict is BenchmarkVerdict.CANNOT_CHECK
    assert "revision_missing" in report.reasons


def test_unobserved_pinned_identity_is_cannot_check_not_success():
    assert validate_corpus_artifact(_artifact(identity_observed=False)).verdict is BenchmarkVerdict.CANNOT_CHECK


def test_retrieval_structure_transfer_ground_truth_cannot_be_collapsed():
    report = validate_ground_truth_factorization(GroundTruthFactorization("mir-gold", "mir-gold", "mir-gold", True))
    assert report.verdict is BenchmarkVerdict.REJECT


def test_retrieval_only_ground_truth_is_valid_but_scoped():
    report = validate_ground_truth_factorization(GroundTruthFactorization("mir-gold", None, None, False))
    assert report.verdict is BenchmarkVerdict.VALID
    assert report.available_layers == (GroundTruthLayer.RETRIEVAL_RELEVANCE,)
    assert "structural_ground_truth_unavailable_retrieval_only_scope" in report.reasons


def test_same_label_authority_cannot_cover_retrieval_and_structure():
    report = validate_ground_truth_factorization(GroundTruthFactorization("one-label", "one-label", None, False))
    assert report.verdict is BenchmarkVerdict.REJECT


def test_route_trial_separates_corpus_coverage_from_retrieval_recall():
    report = evaluate_retrieval_route_trial(
        _trial(
            corpus_candidate_ids=("surface", "gold-A", "other"),
            designated_relevant_ids=("gold-A", "gold-B"),
            retrieved_candidate_ids=("surface", "gold-A", "other"),
        )
    )
    assert report.verdict is RouteTrialVerdict.VALID
    assert report.corpus_coverage_rate == 0.5
    assert report.conditional_recall_at_k == 1.0
    assert report.absent_relevant_ids == ("gold-B",)


def test_route_trial_computes_conditional_recall_and_mrr():
    report = evaluate_retrieval_route_trial(_trial())
    assert report.verdict is RouteTrialVerdict.VALID
    assert report.corpus_coverage_rate == 1.0
    assert report.conditional_recall_at_k == 0.5
    assert report.mean_reciprocal_rank == pytest.approx(0.25)


def test_hidden_gold_exposure_invalidates_retrieval_trial():
    assert evaluate_retrieval_route_trial(_trial(hidden_labels_exposed=True)).verdict is RouteTrialVerdict.TRIAL_INVALID


def test_posthoc_query_change_invalidates_retrieval_trial():
    assert evaluate_retrieval_route_trial(_trial(query_frozen_before_labels=False)).verdict is RouteTrialVerdict.TRIAL_INVALID


def test_unexecuted_route_is_cannot_check():
    assert evaluate_retrieval_route_trial(_trial(execution_observed=False)).verdict is RouteTrialVerdict.CANNOT_CHECK


def test_route_output_cannot_exceed_frozen_top_k():
    report = evaluate_retrieval_route_trial(_trial(top_k=2, retrieved_candidate_ids=("surface", "gold-A", "other")))
    assert report.verdict is RouteTrialVerdict.TRIAL_INVALID


def test_duplicate_ranked_candidates_are_invalid():
    assert evaluate_retrieval_route_trial(_trial(retrieved_candidate_ids=("gold-A", "gold-A"))).verdict is RouteTrialVerdict.TRIAL_INVALID


def test_matched_same_resource_routes_are_comparable_but_do_not_activate_default():
    lexical = _trial()
    relational = _trial(
        trial_id="trial-relational",
        route_id="DOMAIN_STRIPPED_RELATIONAL",
        retrieved_candidate_ids=("gold-B", "gold-A", "surface"),
    )
    report = compare_retrieval_routes((lexical, relational))
    assert report.verdict is RouteComparisonVerdict.MATCHED_SAME_RESOURCE
    assert report.activates_default is False
    assert report.establishes_model_improvement is False


def test_topk_mismatch_invalidates_route_comparison():
    report = compare_retrieval_routes((_trial(), _trial(trial_id="trial-graph", route_id="GRAPH", top_k=5, retrieved_candidate_ids=("gold-A", "gold-B"))))
    assert report.verdict is RouteComparisonVerdict.TRIAL_INVALID
    assert "matched_contract_mismatch:top_k" in report.reasons


def test_model_mismatch_invalidates_route_comparison():
    report = compare_retrieval_routes((_trial(), _trial(trial_id="trial-embedding", route_id="EMBEDDING", base_model_id="stronger-model")))
    assert report.verdict is RouteComparisonVerdict.TRIAL_INVALID


def test_undeclared_resource_delta_invalidates_comparison():
    report = compare_retrieval_routes((_trial(), _trial(trial_id="trial-graph", route_id="GRAPH", resource_ids=("paper-index", "methodology-graph"), resource_delta_declared=False)))
    assert report.verdict is RouteComparisonVerdict.TRIAL_INVALID
    assert "undeclared_resource_delta_between_routes" in report.reasons


def test_declared_resource_delta_is_system_level_not_model_improvement():
    report = compare_retrieval_routes((
        _trial(resource_delta_declared=True),
        _trial(
            trial_id="trial-graph",
            route_id="GRAPH",
            resource_ids=("paper-index", "methodology-graph"),
            resource_delta_declared=True,
            retrieved_candidate_ids=("gold-A", "gold-B", "surface"),
        ),
    ))
    assert report.verdict is RouteComparisonVerdict.SYSTEM_LEVEL_WITH_RESOURCE_DELTA
    assert report.establishes_model_improvement is False


def test_corpus_artifact_contract_is_immutable():
    artifact = _artifact()
    with pytest.raises(FrozenInstanceError):
        artifact.revision = "changed"  # type: ignore[misc]
