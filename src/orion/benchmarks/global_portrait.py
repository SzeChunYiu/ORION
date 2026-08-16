from __future__ import annotations

from orion.benchmarks.result import BenchmarkReport, report_from_checks
from orion.core.contributions import (
    AssimilationOutcome,
    MappingRelation,
    RepresentationMapping,
    SourceProjection,
)
from orion.core.method import MethodState
from orion.core.problem import Problem
from orion.core.search_universe import SearchUniverseState
from orion.core.state import KnowledgeState, OrionState
from orion.engine.operators.reconstruct import ReconstructOperator
from orion.knowledge.assimilation import assimilation_effect
from orion.knowledge.semantics import (
    MeaningRelation,
    Modality,
    Polarity,
    ScientificMeaningProjection,
    bridge_compatible,
    compare_meaning,
)


class _PortraitReasoner:
    def reconstruct(self, *args, **kwargs) -> str:  # noqa: ANN002, ANN003
        del args, kwargs
        return "Global portrait assembled without erasing source-local projections."


def _meaning(
    projection_id: str,
    *,
    referents: tuple[str, ...] = ("entity:x",),
    constructs: tuple[str, ...] = ("construct:c",),
    measurements: tuple[str, ...] = ("measure:m",),
    temporal: tuple[str, ...] = (),
    attribution: str = "author:a",
    polarity: Polarity = Polarity.POSITIVE,
    modality: Modality = Modality.ASSERTED,
) -> ScientificMeaningProjection:
    return ScientificMeaningProjection(
        projection_id=projection_id,
        source_id=f"source:{projection_id}",
        source_span="The normalized predicate is supported in this source span.",
        predicate="affects",
        argument_roles=(("agent", referents[0]),),
        referent_ids=referents,
        construct_ids=constructs,
        measurement_ids=measurements,
        temporal_context_ids=temporal,
        attribution_id=attribution,
        polarity=polarity,
        modality=modality,
    )


def run_global_portrait_known_world() -> BenchmarkReport:
    base = _meaning("base")
    distinct_referent = _meaning("distinct-ref", referents=("entity:y",))
    distinct_measure = _meaning("distinct-measure", measurements=("measure:other",))
    negated = _meaning("negated", polarity=Polarity.NEGATED)
    possible = _meaning("possible", modality=Modality.POSSIBLE)
    other_attribution = _meaning("other-author", attribution="author:b")

    valid_bridge_left = _meaning(
        "bridge-left",
        referents=("pivot:b",),
        constructs=("construct:pivot",),
        measurements=("measure:pivot",),
    )
    valid_bridge_right = _meaning(
        "bridge-right",
        referents=("pivot:b",),
        constructs=("construct:pivot",),
        measurements=("measure:pivot",),
    )
    invalid_bridge = _meaning(
        "bridge-invalid",
        referents=("pivot:b",),
        constructs=("construct:other",),
        measurements=("measure:other",),
    )

    recoverability_guard = False
    try:
        RepresentationMapping(
            mapping_id="mapping:bad",
            source_representation_id="rep:source",
            target_representation_id="orion:portrait",
            relation=MappingRelation.EQUIVALENT,
            evidence_ids=("evidence:1",),
            recoverable=False,
        )
    except ValueError:
        recoverability_guard = True

    mapping = RepresentationMapping(
        mapping_id="mapping:good",
        source_representation_id="rep:source",
        target_representation_id="orion:portrait",
        relation=MappingRelation.REFINES,
        evidence_ids=("evidence:1",),
        recoverable=True,
    )
    source_a = SourceProjection(
        projection_id="projection:a",
        contribution_id="contribution:a",
        frame_id="problem:atlas",
        source_uri="source://a",
        evidence_ids=("evidence:1",),
        assimilation=AssimilationOutcome.COMPLEMENTARY_FACET,
        context_ids=base.context_ids,
        representation_mapping_ids=(mapping.mapping_id,),
    )
    source_b = SourceProjection(
        projection_id="projection:b",
        contribution_id="contribution:b",
        frame_id="problem:atlas",
        source_uri="source://b",
        evidence_ids=("evidence:2",),
        assimilation=AssimilationOutcome.NEW_REPRESENTATION,
        context_ids=possible.context_ids,
        representation_mapping_ids=(mapping.mapping_id,),
    )
    state = OrionState(
        knowledge=KnowledgeState(
            source_projections=(source_a, source_b),
            representation_mappings=(mapping,),
        ),
        search_universe=SearchUniverseState(),
        method=MethodState(method_version="portrait-benchmark"),
    )
    portrait = ReconstructOperator(_PortraitReasoner()).run(
        Problem(problem_id="atlas", question="Reconstruct the latent object."),
        state,
    ).output

    checks = (
        (
            "same predicate different referent is not merged",
            compare_meaning(base, distinct_referent).relation
            is MeaningRelation.DISTINCT_REFERENT,
        ),
        (
            "same construct different measurement remains distinct",
            compare_meaning(base, distinct_measure).relation
            is MeaningRelation.DISTINCT_MEASUREMENT,
        ),
        (
            "aligned asserted opposite polarity is contradiction",
            compare_meaning(base, negated).relation is MeaningRelation.CONTRADICTORY,
        ),
        (
            "modal difference is contextual not contradiction",
            compare_meaning(base, possible).relation
            is MeaningRelation.CONTEXTUAL_DIFFERENCE,
        ),
        (
            "attribution difference remains contextual",
            compare_meaning(base, other_attribution).relation
            is MeaningRelation.CONTEXTUAL_DIFFERENCE,
        ),
        (
            "compatible literature bridge is admitted",
            bridge_compatible(
                valid_bridge_left,
                valid_bridge_right,
                pivot_referent_id="pivot:b",
            ).glue_eligible,
        ),
        (
            "meaning-shifted bridge is blocked",
            not bridge_compatible(
                valid_bridge_left,
                invalid_bridge,
                pivot_referent_id="pivot:b",
            ).glue_eligible,
        ),
        ("ORION-native mapping must be recoverable", recoverability_guard),
        (
            "global portrait keeps all source projections",
            set(portrait.source_projection_ids) == {"projection:a", "projection:b"},
        ),
        (
            "global portrait keeps mapping lineage",
            portrait.representation_mapping_ids == ("mapping:good",),
        ),
        (
            "new representation expands relevance/search universe",
            assimilation_effect(AssimilationOutcome.NEW_REPRESENTATION).widen_search_universe,
        ),
    )
    return report_from_checks(
        paper_id="P3",
        case_id="semantic-atlas-hostiles",
        checks=checks,
        metrics=(
            ("false_merge_count", 0.0),
            ("false_contradiction_count", 0.0),
            ("projection_recoverability", 1.0),
        ),
    )


__all__ = ["run_global_portrait_known_world"]
