from __future__ import annotations

from orion.benchmarks.result import BenchmarkReport, BenchmarkStatus, report_from_checks
from orion.core.search import SearchRouteKind
from orion.knowledge.evaluation import (
    GoldTier,
    RecallTask,
    UnsupportedClaim,
    compare_against_baseline,
)
from orion.knowledge.routes import RouteCapture, build_ensemble


def run_discovery_known_world() -> BenchmarkReport:
    """A tiny complete-gold world whose lexical baseline is intentionally strong.

    The ORION ranking is supplied as the output of the discovery system under
    test; this benchmark evaluates the promotion contract rather than pretending
    the fixture proves open-web recall.
    """

    documents = {
        "gold-a": "psychometric latent trait item response differential functioning",
        "gold-b": "multi trait multi method reliability construct validity instrument",
        "distractor-a": "latent construct measurement invariance latent construct measurement invariance",
        "distractor-b": "measurement invariance tutorial latent construct glossary",
        "other-a": "database schema normalization and entity matching",
        "other-b": "semantic parsing modality coreference discourse",
    }
    task = RecallTask(
        task_id="paper2-known-world",
        query="latent construct measurement invariance",
        gold_ids=frozenset({"gold-a", "gold-b"}),
        corpus_ids=tuple(documents),
        tier=GoldTier.T3_PROTOCOL_COMPLETE,
        provenance="orion:frozen-known-world-v1",
    )
    comparison = compare_against_baseline(
        task,
        ("gold-a", "gold-b", "distractor-a", "distractor-b", "other-a", "other-b"),
        documents,
        cutoffs=(1, 2, 4),
        target_recall=1.0,
    )

    same_backend = build_ensemble(
        (
            RouteCapture(
                SearchRouteKind.CURRENT_VOCABULARY,
                "backend:shared",
                "derivation:lexical",
                frozenset({"digest:a", "digest:shared"}),
            ),
            RouteCapture(
                SearchRouteKind.PARENT_DISCIPLINE,
                "backend:shared",
                "derivation:parent",
                frozenset({"digest:b", "digest:shared"}),
            ),
        )
    )
    zero_overlap = build_ensemble(
        (
            RouteCapture(
                SearchRouteKind.FUNCTION_ONLY,
                "backend:function",
                "derivation:function",
                frozenset({"digest:x"}),
            ),
            RouteCapture(
                SearchRouteKind.LITERATURE_BRIDGE,
                "backend:bridge",
                "derivation:bridge",
                frozenset({"digest:y"}),
            ),
        )
    )
    reminted_identity = build_ensemble(
        (
            RouteCapture(
                SearchRouteKind.CURRENT_VOCABULARY,
                "backend:a",
                "derivation:a",
                frozenset({"content:same-paper"}),
            ),
            RouteCapture(
                SearchRouteKind.PARENT_DISCIPLINE,
                "backend:b",
                "derivation:b",
                frozenset({"content:same-paper"}),
            ),
        )
    )

    unsupported_refused = False
    try:
        compare_against_baseline(
            RecallTask(
                task_id="single-target",
                query="one known paper",
                gold_ids=frozenset({"gold-a"}),
                corpus_ids=tuple(documents),
                tier=GoldTier.T1_SINGLE_TARGET,
                provenance="fixture",
            ),
            ("gold-a",),
            documents,
        )
    except UnsupportedClaim:
        unsupported_refused = True

    checks = (
        ("recall-first system beats lexical baseline", comparison.beats_baseline),
        (
            "shared backend receives no independence estimate",
            same_backend.estimate.population_estimate is None
            and same_backend.estimate.independent_pairs == 0,
        ),
        (
            "zero-overlap independent routes refuse bounded population",
            zero_overlap.estimate.population_estimate is None
            and zero_overlap.estimate.independent_pairs == 1,
        ),
        (
            "same content is one capture despite route re-encounter",
            len(reminted_identity.union) == 1,
        ),
        ("single-target pseudo-recall is refused", unsupported_refused),
        (
            "coverage estimate never becomes stopping authority",
            same_backend.estimate.diagnostic_only
            and zero_overlap.estimate.diagnostic_only
            and reminted_identity.estimate.diagnostic_only,
        ),
    )
    baseline_at_2 = comparison.baseline.recall(2) or 0.0
    system_at_2 = comparison.system.recall(2) or 0.0
    return report_from_checks(
        paper_id="P2",
        case_id="complete-gold-and-coverage-hostiles",
        checks=checks,
        metrics=(
            ("system_recall_at_2", system_at_2),
            ("baseline_recall_at_2", baseline_at_2),
            ("recall_margin_at_2", system_at_2 - baseline_at_2),
            ("content_union_after_reencounter", float(len(reminted_identity.union))),
        ),
    )


def external_discovery_gate(
    *,
    benchmark_name: str,
    complete_gold: bool,
    matched_baseline: bool,
    frozen_provider_trace: bool,
    system_beats_baseline: bool | None,
) -> BenchmarkReport:
    """Promotion gate for ResearchArena/AutoResearchBench/MetaSyn-style trials."""

    blockers: list[str] = []
    if not complete_gold:
        blockers.append("benchmark lacks a recall-supporting gold denominator")
    if not matched_baseline:
        blockers.append("matched simple baseline was not run")
    if not frozen_provider_trace:
        blockers.append("search/provider trajectory was not frozen")
    if blockers or system_beats_baseline is None:
        if system_beats_baseline is None:
            blockers.append("system-vs-baseline outcome unavailable")
        return BenchmarkReport(
            paper_id="P2",
            case_id=benchmark_name,
            status=BenchmarkStatus.CANNOT_CHECK,
            blockers=tuple(dict.fromkeys(blockers)),
        )
    return BenchmarkReport(
        paper_id="P2",
        case_id=benchmark_name,
        status=BenchmarkStatus.PASS if system_beats_baseline else BenchmarkStatus.FAIL,
        metrics=(("beats_baseline", float(system_beats_baseline)),),
        blockers=() if system_beats_baseline else ("ORION did not beat matched baseline",),
    )


__all__ = ["external_discovery_gate", "run_discovery_known_world"]
