"""Knowledge-space representation: retrieval, assimilation and source-local meaning."""

from orion.knowledge.ignorance import (
    IgnoranceAction,
    IgnoranceActionPlan,
    IgnoranceKind,
    IgnoranceProjection,
    ScientificIgnoranceInterpreter,
    deduplicate_ignorance,
    plan_for_ignorance,
)
from orion.knowledge.semantics import (
    MeaningComparison,
    MeaningRelation,
    Modality,
    Polarity,
    ScientificLanguageInterpreter,
    ScientificMeaningProjection,
    bridge_compatible,
    compare_meaning,
)

__all__ = [
    "IgnoranceAction",
    "IgnoranceActionPlan",
    "IgnoranceKind",
    "IgnoranceProjection",
    "MeaningComparison",
    "MeaningRelation",
    "Modality",
    "Polarity",
    "ScientificIgnoranceInterpreter",
    "ScientificLanguageInterpreter",
    "ScientificMeaningProjection",
    "bridge_compatible",
    "compare_meaning",
    "deduplicate_ignorance",
    "plan_for_ignorance",
]
