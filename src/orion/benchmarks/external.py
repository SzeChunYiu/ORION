from __future__ import annotations

from orion.benchmarks.result import BenchmarkReport, BenchmarkStatus


def external_reconstruction_gate(
    *,
    hidden_representation_or_domain: bool,
    matched_static_workflow_baseline: bool,
    matched_tree_search_baseline: bool,
    resource_matched: bool,
    responsibility_labels_hidden: bool,
    fresh_cases: bool,
    root_success_better_than_baselines: bool | None,
    unnecessary_reframe_not_worse: bool | None,
) -> BenchmarkReport:
    """External Paper I gate for hidden-formulation tasks."""

    missing: list[str] = []
    if not hidden_representation_or_domain:
        missing.append("task does not require a hidden representation/search-universe shift")
    if not matched_static_workflow_baseline:
        missing.append("matched static-workflow baseline not run")
    if not matched_tree_search_baseline:
        missing.append("matched tree-search/agentic baseline not run")
    if not resource_matched:
        missing.append("resources not matched")
    if not responsibility_labels_hidden:
        missing.append("responsibility/domain labels were exposed to the candidate")
    if not fresh_cases:
        missing.append("no fresh hidden-shift cases")
    if root_success_better_than_baselines is None:
        missing.append("root-success comparison unavailable")
    if unnecessary_reframe_not_worse is None:
        missing.append("unnecessary-reframe comparison unavailable")
    if missing:
        return BenchmarkReport(
            paper_id="P1",
            case_id="external-hidden-formulation",
            status=BenchmarkStatus.CANNOT_CHECK,
            blockers=tuple(missing),
        )
    if not root_success_better_than_baselines or not unnecessary_reframe_not_worse:
        return BenchmarkReport(
            paper_id="P1",
            case_id="external-hidden-formulation",
            status=BenchmarkStatus.FAIL,
            blockers=("typed reconstruction did not improve the protected success/reframe tradeoff",),
        )
    return BenchmarkReport(
        paper_id="P1",
        case_id="external-hidden-formulation",
        status=BenchmarkStatus.PASS,
        metrics=(("better_protected_tradeoff", 1.0),),
    )


def external_portrait_gate(
    *,
    at_least_three_domains: bool,
    multiple_operationalizations: bool,
    source_projection_gold: bool,
    mapping_gold: bool,
    long_context_baseline_run: bool,
    rag_translation_baseline_run: bool,
    flat_schema_baseline_run: bool,
    nlp_ablation_run: bool,
    false_integration_better_than_baselines: bool | None,
    source_recoverability_not_worse: bool | None,
) -> BenchmarkReport:
    """External Paper III gate for real cross-domain global-portrait cases."""

    missing: list[str] = []
    if not at_least_three_domains:
        missing.append("case does not span at least three domains")
    if not multiple_operationalizations:
        missing.append("case lacks construct/measurement ambiguity")
    if not source_projection_gold:
        missing.append("source-local projection gold absent")
    if not mapping_gold:
        missing.append("identity/representation mapping gold absent")
    if not long_context_baseline_run:
        missing.append("long-context synthesis baseline not run")
    if not rag_translation_baseline_run:
        missing.append("RAG/translation baseline not run")
    if not flat_schema_baseline_run:
        missing.append("flat-schema/knowledge-graph baseline not run")
    if not nlp_ablation_run:
        missing.append("semantic-coordinate ablation not run")
    if false_integration_better_than_baselines is None:
        missing.append("false-integration comparison unavailable")
    if source_recoverability_not_worse is None:
        missing.append("source-recoverability comparison unavailable")
    if missing:
        return BenchmarkReport(
            paper_id="P3",
            case_id="external-cross-domain-portrait",
            status=BenchmarkStatus.CANNOT_CHECK,
            blockers=tuple(missing),
        )
    if not false_integration_better_than_baselines or not source_recoverability_not_worse:
        return BenchmarkReport(
            paper_id="P3",
            case_id="external-cross-domain-portrait",
            status=BenchmarkStatus.FAIL,
            blockers=("projection atlas did not improve false-integration/recoverability tradeoff",),
        )
    return BenchmarkReport(
        paper_id="P3",
        case_id="external-cross-domain-portrait",
        status=BenchmarkStatus.PASS,
        metrics=(("better_false_integration_tradeoff", 1.0),),
    )


__all__ = ["external_portrait_gate", "external_reconstruction_gate"]
