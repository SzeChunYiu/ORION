from __future__ import annotations

from dataclasses import dataclass

from orion.benchmarks.result import BenchmarkReport, report_from_checks
from orion.knowledge.ignorance import (
    IgnoranceAction,
    IgnoranceKind,
    IgnoranceProjection,
    deduplicate_ignorance,
    plan_for_ignorance,
)


@dataclass(frozen=True)
class IgnoranceActionCase:
    case_id: str
    kind: IgnoranceKind
    expected_action: IgnoranceAction
    source_span: str
    knowledge_goal: str


def frozen_ignorance_cases() -> tuple[IgnoranceActionCase, ...]:
    return (
        IgnoranceActionCase(
            "insufficient-evidence",
            IgnoranceKind.INCOMPLETE_EVIDENCE,
            IgnoranceAction.SEARCH_EVIDENCE,
            "Evidence remains insufficient to determine whether the association holds.",
            "Obtain independent evidence capable of identifying the association.",
        ),
        IgnoranceActionCase(
            "competing-explanations",
            IgnoranceKind.ALTERNATIVE_OR_CONTROVERSY,
            IgnoranceAction.DESIGN_DISCRIMINATOR,
            "Two mechanisms remain plausible and current evidence does not distinguish them.",
            "Find an observation that separates the competing mechanisms.",
        ),
        IgnoranceActionCase(
            "unexpected-result",
            IgnoranceKind.ANOMALOUS_OBSERVATION,
            IgnoranceAction.REPLICATE_OR_EXPERIMENT,
            "An unexpected response was observed in one experiment.",
            "Determine whether the observation replicates and which mechanism explains it.",
        ),
        IgnoranceActionCase(
            "instrument-barrier",
            IgnoranceKind.RESEARCH_BARRIER,
            IgnoranceAction.REPAIR_RESEARCH_BARRIER,
            "The present assay cannot distinguish the relevant states.",
            "Develop or identify a measurement that separates the states.",
        ),
        IgnoranceActionCase(
            "future-work-proposal",
            IgnoranceKind.FUTURE_RESEARCH,
            IgnoranceAction.RETAIN_FUTURE_WORK_CANDIDATE,
            "Future work should investigate whether this effect persists in adults.",
            "Check whether later evidence has already addressed the proposed question.",
        ),
    )


def _projection(case: IgnoranceActionCase, *, source_id: str | None = None) -> IgnoranceProjection:
    return IgnoranceProjection(
        projection_id=f"ignorance:{case.case_id}:{source_id or 'source-a'}",
        source_id=source_id or "source-a",
        source_span=case.source_span,
        kind=case.kind,
        knowledge_goal=case.knowledge_goal,
        subject_ids=("subject:test",),
        context_ids=("context:frozen",),
        evidence_ids=(f"evidence:{source_id or 'source-a'}",),
        source_taxonomy_label=f"source-label:{case.kind.value.lower()}",
    )


def run_typed_ignorance_known_world() -> BenchmarkReport:
    cases = frozen_ignorance_cases()
    projections = tuple(_projection(case) for case in cases)
    plans = tuple(plan_for_ignorance(item) for item in projections)

    expected = {case.case_id: case.expected_action for case in cases}
    actual = {
        case.case_id: plan.action
        for case, plan in zip(cases, plans, strict=True)
    }

    # A generic "there is a gap -> search" controller is the baseline this
    # benchmark falsifies. It cannot distinguish controversy, anomaly, barrier
    # or source-proposed future work.
    generic_action = IgnoranceAction.SEARCH_EVIDENCE
    generic_correct = sum(
        int(case.expected_action is generic_action) for case in cases
    )
    typed_correct = sum(
        int(actual[case.case_id] is expected[case.case_id]) for case in cases
    )

    future = projections[-1]
    independent_repeat = IgnoranceProjection(
        projection_id="ignorance:future-repeat:source-b",
        source_id="source-b",
        source_span=future.source_span,
        kind=future.kind,
        knowledge_goal=future.knowledge_goal,
        subject_ids=future.subject_ids,
        context_ids=future.context_ids,
        evidence_ids=("evidence:source-b",),
        source_taxonomy_label=future.source_taxonomy_label,
    )
    exact_duplicate = IgnoranceProjection(
        projection_id="ignorance:future-duplicate",
        source_id=future.source_id,
        source_span=future.source_span,
        kind=future.kind,
        knowledge_goal=future.knowledge_goal,
        subject_ids=future.subject_ids,
        context_ids=future.context_ids,
        evidence_ids=future.evidence_ids,
        source_taxonomy_label=future.source_taxonomy_label,
    )
    deduped = deduplicate_ignorance((future, independent_repeat, exact_duplicate))

    checks = (
        ("typed actions match all frozen cases", typed_correct == len(cases)),
        (
            "typed controller beats generic missing-gap action",
            typed_correct > generic_correct,
        ),
        (
            "source ignorance never asserts a global gap",
            all(not item.asserts_global_gap for item in projections),
        ),
        (
            "ignorance plans never mint authority",
            all(not item.creates_scientific_authority for item in plans),
        ),
        (
            "all typed plans require independent confirmation",
            all(item.requires_independent_confirmation for item in plans),
        ),
        (
            "future work is retained/check-freshness rather than promoted as gap",
            plans[-1].action is IgnoranceAction.RETAIN_FUTURE_WORK_CANDIDATE,
        ),
        (
            "independent sources remain distinct while exact duplicate collapses",
            len(deduped) == 2 and {item.source_id for item in deduped} == {"source-a", "source-b"},
        ),
    )
    return report_from_checks(
        paper_id="P3",
        case_id="typed-ignorance-action-discrimination",
        checks=checks,
        metrics=(
            ("typed_action_accuracy", typed_correct / len(cases)),
            ("generic_action_accuracy", generic_correct / len(cases)),
            ("retained_independent_source_count", float(len(deduped))),
        ),
        observations=(
            "The benchmark tests routing value, not NLP extraction quality or global gap truth.",
        ),
    )


__all__ = [
    "IgnoranceActionCase",
    "frozen_ignorance_cases",
    "run_typed_ignorance_known_world",
]
