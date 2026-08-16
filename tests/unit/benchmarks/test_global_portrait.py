from orion.benchmarks.global_portrait import run_global_portrait_known_world
from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    compare_meaning,
)


def test_global_portrait_known_world_preserves_context_and_lineage():
    report = run_global_portrait_known_world()
    assert report.passed
    assert report.metric_dict["false_merge_count"] == 0.0
    assert report.metric_dict["projection_recoverability"] == 1.0


def test_unresolved_semantic_projection_fails_closed():
    left = ScientificMeaningProjection(
        projection_id="left",
        source_id="s:left",
        source_span="ambiguous span",
        predicate="causes",
        polarity=Polarity.POSITIVE,
        modality=Modality.ASSERTED,
        unresolved_ambiguities=("referent of it",),
    )
    right = ScientificMeaningProjection(
        projection_id="right",
        source_id="s:right",
        source_span="resolved span",
        predicate="causes",
        polarity=Polarity.POSITIVE,
        modality=Modality.ASSERTED,
    )
    assert compare_meaning(left, right).relation is MeaningRelation.UNRESOLVED
